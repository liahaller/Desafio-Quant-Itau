"""Gera um dashboard HTML simples das reunioes do Fed (Polymarket).

Lista todas as reunioes por data; ao clicar em uma reuniao, mostra o grafico
das probabilidades de cada mercado (desfecho) ao longo do tempo.

Saida: data/dashboard_reunioes_fed.html (arquivo unico, sem servidor).
"""

import json
import re
from pathlib import Path

import pandas as pd

# Caminhos
RAIZ = Path(__file__).resolve().parent.parent
ENTRADA = RAIZ / "data" / "polymarket_fed_reunioes.parquet"
SAIDA = RAIZ / "data" / "dashboard_reunioes_fed.html"

# Ordem dos meses para normalizar rotulos "2024 May" / "the March 2026"
MESES = {
    "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
    "July": 7, "August": 8, "September": 9, "October": 10, "November": 11,
    "December": 12,
}


def rotulo_reuniao(mercado: str) -> str:
    """Extrai 'Month Year' do nome do mercado, normalizando a ordem."""
    x = re.search(r"after (?:the )?(.+?) meeting", mercado)
    bruto = x.group(1) if x else mercado
    # Normaliza "2024 May" -> "May 2024"
    partes = bruto.split()
    mes = next((p for p in partes if p in MESES), None)
    ano = next((p for p in partes if p.isdigit()), None)
    if mes and ano:
        return f"{mes} {ano}"
    return bruto


def desfecho(mercado: str) -> str:
    """Rotulo curto do desfecho (ex.: '-25 bps', '+25 bps')."""
    m = mercado.lower()
    bps = re.search(r"(\d+)\s*bps", m)
    n = bps.group(1) if bps else "?"
    if "decreases" in m:
        return f"-{n} bps"
    if "increases" in m:
        return f"+{n} bps"
    if "no change" in m or "unchanged" in m:
        return "sem mudanca"
    return mercado


def main() -> None:
    df = pd.read_parquet(ENTRADA)
    df["reuniao"] = df["mercado"].apply(rotulo_reuniao)
    df["desfecho"] = df["mercado"].apply(desfecho)
    df["data"] = pd.to_datetime(df["data"])

    reunioes = []
    for evento_id, g in df.groupby("evento_id"):
        rotulo = g["reuniao"].mode().iloc[0]
        data_reuniao = g["data"].max()
        series = []
        for desf, gg in g.groupby("desfecho"):
            gg = gg.sort_values("data")
            # Volume total (lifetime) do mercado — constante na coluna, pega o 1o.
            vol = float(gg["volume"].iloc[0]) if "volume" in gg else 0.0
            series.append({
                "nome": desf,
                "volume": round(vol, 2),
                "x": gg["data"].dt.strftime("%Y-%m-%d").tolist(),
                "y": gg["probabilidade"].round(4).tolist(),
            })
        volume_total = round(sum(s["volume"] for s in series), 2)
        reunioes.append({
            "id": str(evento_id),
            "rotulo": rotulo,
            "data": data_reuniao.strftime("%Y-%m-%d"),
            "ordem": data_reuniao.value,
            "volume_total": volume_total,
            "series": series,
        })

    reunioes.sort(key=lambda r: r["ordem"])
    dados_json = json.dumps(reunioes, ensure_ascii=False)

    html = _TEMPLATE.replace("__DADOS__", dados_json)
    SAIDA.write_text(html, encoding="utf-8")
    print(f"Dashboard gerado: {SAIDA}")
    print(f"Reunioes: {len(reunioes)}")


_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<title>Reunioes do Fed - Polymarket</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
  * { box-sizing: border-box; }
  body { margin: 0; font-family: -apple-system, Segoe UI, Roboto, sans-serif;
         color: #1a1a1a; background: #f5f6f8; }
  header { padding: 16px 24px; background: #0b1f3a; color: #fff; }
  header h1 { margin: 0; font-size: 18px; font-weight: 600; }
  header p { margin: 4px 0 0; font-size: 12px; opacity: .7; }
  .wrap { display: flex; height: calc(100vh - 66px); }
  .lista { width: 240px; overflow-y: auto; background: #fff;
           border-right: 1px solid #e2e5ea; }
  .item { padding: 12px 16px; cursor: pointer; border-bottom: 1px solid #f0f1f4;
          font-size: 14px; }
  .item:hover { background: #eef2f8; }
  .item.ativo { background: #0b1f3a; color: #fff; }
  .item .data { font-size: 11px; opacity: .6; }
  .item.ativo .data { opacity: .8; }
  .painel { flex: 1; padding: 16px 24px; overflow-y: auto; }
  #grafico { width: 100%; height: 100%; }
  .vazio { color: #888; font-size: 14px; margin-top: 40px; text-align: center; }
</style>
</head>
<body>
<header>
  <h1>Reunioes do Fed &middot; Polymarket</h1>
  <p>Selecione uma reuniao na lista para ver as probabilidades ao longo do tempo.</p>
</header>
<div class="wrap">
  <div class="lista" id="lista"></div>
  <div class="painel"><div id="grafico"><div class="vazio">Selecione uma reuniao</div></div></div>
</div>
<script>
const REUNIOES = __DADOS__;
const lista = document.getElementById('lista');

function fmtVol(v) {
  if (v >= 1e6) return '$' + (v / 1e6).toFixed(2) + 'M';
  if (v >= 1e3) return '$' + (v / 1e3).toFixed(1) + 'k';
  return '$' + v.toFixed(0);
}

REUNIOES.forEach((r, i) => {
  const el = document.createElement('div');
  el.className = 'item';
  el.innerHTML = `<div>${r.rotulo}</div>` +
    `<div class="data">${r.data} &middot; vol ${fmtVol(r.volume_total)}</div>`;
  el.onclick = () => selecionar(i, el);
  lista.appendChild(el);
});

function selecionar(i, el) {
  document.querySelectorAll('.item').forEach(x => x.classList.remove('ativo'));
  el.classList.add('ativo');
  const r = REUNIOES[i];
  const traces = r.series.map(s => ({
    x: s.x, y: s.y, name: `${s.nome} · ${fmtVol(s.volume)}`,
    type: 'scatter', mode: 'lines'
  }));
  Plotly.newPlot('grafico', traces, {
    title: `Reuniao ${r.rotulo} (${r.data}) — volume total ${fmtVol(r.volume_total)}`,
    yaxis: { title: 'Probabilidade', tickformat: '.0%', range: [0, 1] },
    xaxis: { title: 'Data' },
    legend: { orientation: 'h' },
    margin: { t: 50, r: 20, b: 50, l: 55 }
  }, { responsive: true });
}
</script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
