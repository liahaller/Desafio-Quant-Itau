"""Gráficos da página 4 do relatório — curva, atribuição e sensibilidade.

O `backtest_v1.py` publica escalares em markdown; a página 4 pede três imagens
que só existem em série. Este script **não mede nada novo**: lê os CSV gravados
por `backtest_v1.py`, `curva_c.py` e `curva_banda.py`, lê as tabelas já
publicadas em `Dump/analises/`, e desenha.

Três coisas que ele não faz, de propósito:

  - **não escolhe cenário** — o default é o escopo de referência que o próprio
    backtest declara (`tilt ≤ 1`, o mesmo da varredura de γ). A D12 (nível e
    escopo do teto) segue aberta; trocar `--cenario` troca a figura inteira.
  - **não copia número** — a atribuição sai lida do markdown que a mede, não
    transcrita. Número copiado à mão envelhece calado, que é um dos erros que a
    própria página 4 lista.
  - **não inventa métrica** — drawdown, alpha e beta são calculados aqui porque
    não existem no `summary()` do backtest, e acrescentá-los lá obrigaria a
    regerar todos os artefatos por causa de três linhas.

Estilo: paleta da capa do v1 (âmbar da ampulheta sobre fundo escuro), figura de
fundo transparente para cair em cima do slide. `--tema claro` inverte, se a
página mudar de fundo.

Uso:

    python scripts/graficos_p4.py                 # Dump/dados → Dump/graficos
    python scripts/graficos_p4.py --demo          # auto-teste em dado sintético
"""

import argparse
import re
import sys
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")   # sem display: o script só grava arquivo
import matplotlib.dates as mdates          # noqa: E402
import matplotlib.pyplot as plt            # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from config import PREGOES_POR_ANO         # noqa: E402

# Cenário de referência: o mesmo rótulo que o `rotulo_teto` do backtest gera e
# que a seção de γ já usa. Não é escolha deste script — a D12 segue aberta.
CENARIO_REF = "tilt ≤ 1"
PONTOS_PERCENTUAIS = 100.0

PALETAS = {
    # âmbar da ampulheta e ciano dos reflexos, da arte da capa do v1
    "escuro": {"texto": "#E6EAF0", "suave": "#8B97A8", "grade": "#2A3444",
               "kairos": "#F5A623", "bench": "#7A8798", "apoio": "#4FC3D9",
               "negativo": "#C25B54"},
    "claro": {"texto": "#1B2430", "suave": "#5C6B7A", "grade": "#D5DCE4",
              "kairos": "#C97A05", "bench": "#8A97A6", "apoio": "#1E7F97",
              "negativo": "#A83A33"},
}


def aplicar_estilo(p):
    """rcParams da paleta. Fundo transparente: quem pinta é o slide."""
    plt.rcParams.update({
        "figure.facecolor": "none", "axes.facecolor": "none",
        "savefig.facecolor": "none", "savefig.transparent": True,
        "text.color": p["texto"], "axes.labelcolor": p["suave"],
        "xtick.color": p["suave"], "ytick.color": p["suave"],
        "axes.edgecolor": p["grade"], "grid.color": p["grade"],
        "font.size": 9, "axes.titlesize": 10, "legend.fontsize": 8.5,
        "axes.spines.top": False, "axes.spines.right": False,
        "figure.autolayout": True,
    })


def _celulas(linha):
    """Células de uma linha markdown, com o `|` de `Σ|w|` protegido.

    `Backtest_v1.md` escapa o nome como `Σ\\|w\\|`, o `Camada_tatica_v2.md` sai
    do `to_markdown()` sem escapar — nos dois casos aquele `|` é nome de coluna,
    não separador, e sem isto o cabeçalho conta duas células a mais que o corpo.
    """
    linha = re.sub(r"Σ\\?\|w\\?\|", "Σ‖w‖", linha.strip())
    return [c.strip() for c in linha.strip("|").split("|")]


def ler_tabela_md(caminho, chave):
    """Primeira tabela markdown do arquivo cujo cabeçalho contém `chave`.

    Lê o artefato em vez de transcrever o número: se a medida for re-gerada, o
    gráfico acompanha em vez de mentir calado.
    """
    linhas = Path(caminho).read_text(encoding="utf-8").splitlines()
    for i, linha in enumerate(linhas):
        if linha.lstrip().startswith("|") and chave in linha:
            cabecalho = _celulas(linha)
            corpo = []
            for seguinte in linhas[i + 2:]:      # +2 pula a linha de alinhamento
                if not seguinte.lstrip().startswith("|"):
                    break
                celulas = _celulas(seguinte)
                if len(celulas) != len(cabecalho):
                    raise ValueError(
                        f"{Path(caminho).name}: linha com {len(celulas)} células "
                        f"sob cabeçalho de {len(cabecalho)} — {seguinte!r}")
                corpo.append(celulas)
            return pd.DataFrame(corpo, columns=cabecalho)
    raise KeyError(f"tabela com '{chave}' não encontrada em {caminho}")


def numero(texto):
    """'+2.74 pp' → 2.74 · '48% (13/27)' → 48.0 · '—' → nan."""
    achado = re.search(r"[-+]?\d+[.,]?\d*", str(texto).replace("−", "-"))
    return float(achado.group().replace(",", ".")) if achado else float("nan")


def drawdown(retornos):
    """Série de drawdown (fração, ≤ 0) a partir dos retornos diários."""
    patrimonio = (1.0 + retornos).cumprod()
    return patrimonio / patrimonio.cummax() - 1.0


def metricas(diario, pregoes_por_ano=PREGOES_POR_ANO):
    """Tabela Kairós × SPY, com o que o `summary()` do backtest não calcula.

    `alpha` e `beta` saem de regressão dos retornos diários contra o benchmark
    com taxa livre de risco zero — a mesma convenção do "sharpe (excesso zero)"
    que o backtest já reporta.
    """
    r, b = diario["r_liquido"], diario["r_benchmark"]
    beta = float(np.cov(r, b, ddof=1)[0, 1] / np.var(b, ddof=1))
    alpha = float((r.mean() - beta * b.mean()) * pregoes_por_ano)
    anual = np.sqrt(pregoes_por_ano)
    linhas = {
        "Retorno líquido": (float((1 + r).prod() - 1), float((1 + b).prod() - 1)),
        "Vol. anualizada": (float(r.std(ddof=1) * anual), float(b.std(ddof=1) * anual)),
        "Sharpe (excesso zero)": (float(r.mean() / r.std(ddof=1) * anual),
                                  float(b.mean() / b.std(ddof=1) * anual)),
        "Máx. drawdown": (float(drawdown(r).min()), float(drawdown(b).min())),
        "Alpha anualizado": (alpha, 0.0),
        "Beta vs SPY": (beta, 1.0),
        "Σ|w| média": (float(diario["alavancagem"].mean()), 1.0),
        "Giro diário": (float(diario["giro"].mean()), float("nan")),
    }
    return pd.DataFrame(linhas, index=["Kairós", "SPY"]).T


def grafico_curva(diario, p, destino):
    """Curva acumulada × SPY com o drawdown no painel de baixo."""
    fig, (ax, axd) = plt.subplots(
        2, 1, figsize=(7.4, 4.6), sharex=True, gridspec_kw={"height_ratios": [2.5, 1]})
    acum_k = ((1 + diario["r_liquido"]).cumprod() - 1) * PONTOS_PERCENTUAIS
    acum_b = ((1 + diario["r_benchmark"]).cumprod() - 1) * PONTOS_PERCENTUAIS

    ax.plot(acum_k.index, acum_k, color=p["kairos"], lw=1.9, label="Kairós (líquido)")
    ax.plot(acum_b.index, acum_b, color=p["bench"], lw=1.4, label="SPY comprar-e-segurar")
    ax.axhline(0, color=p["grade"], lw=0.8)
    ax.set_ylabel("retorno acumulado (%)")
    ax.legend(frameon=False, loc="upper left")
    ax.grid(axis="y", lw=0.5, alpha=0.5)
    for serie, cor in ((acum_k, p["kairos"]), (acum_b, p["bench"])):
        ax.annotate(f"{serie.iloc[-1]:+.1f}%", (serie.index[-1], serie.iloc[-1]),
                    xytext=(6, 0), textcoords="offset points", color=cor,
                    fontsize=9, fontweight="bold", va="center")

    dd_k, dd_b = (drawdown(diario["r_liquido"]) * PONTOS_PERCENTUAIS,
                  drawdown(diario["r_benchmark"]) * PONTOS_PERCENTUAIS)
    axd.fill_between(dd_k.index, dd_k, 0, color=p["kairos"], alpha=0.35, lw=0)
    axd.plot(dd_k.index, dd_k, color=p["kairos"], lw=1.0)
    axd.plot(dd_b.index, dd_b, color=p["bench"], lw=1.0, ls="--")
    axd.set_ylabel("drawdown (%)")
    axd.grid(axis="y", lw=0.5, alpha=0.5)
    # o pior ponto vai anotado: a página assume que ele é pior que o do benchmark
    axd.annotate(f"mín. {dd_k.min():.1f}%", (dd_k.idxmin(), dd_k.min()),
                 xytext=(12, 4), textcoords="offset points", color=p["kairos"],
                 fontsize=8.5, ha="left", va="bottom")   # ao lado do vale, sem cobrir
    axd.xaxis.set_major_formatter(mdates.ConciseDateFormatter(
        mdates.AutoDateLocator()))
    return salvar(fig, destino, "p4_curva")


def grafico_atribuicao(views_md, tatica_md, p, destino, teto_ref=1.0):
    """De onde vem o excesso: Δ por view e o Δ da camada, com e sem os 3 maiores.

    Os números não são digitados aqui: saem das tabelas de `Views_novas.md`
    (atribuição por view) e `Camada_tatica_v2.md` (a camada na entrega).
    """
    atrib = ler_tabela_md(views_md, "sem os 3 maiores").set_index("configuração")
    # a linha da entrega está declarada no próprio artefato: entropia crua
    rotulos = {"+ incerteza (entropia crua)": "15b · incerteza",
               "+ B com β próprio (DGS1)": "15g · trajetória",
               "+ as duas (entropia crua)": "as duas, empilhadas"}
    itens = [(nome, numero(atrib.loc[chave, "Σ dos Δ diários"]),
              numero(atrib.loc[chave, "sem os 3 maiores"]))
             for chave, nome in rotulos.items() if chave in atrib.index]

    camada = ler_tabela_md(tatica_md, "excesso × SPY (com)")
    coluna_teto = camada.columns[0]
    linha = camada[camada[coluna_teto].map(numero) == teto_ref]
    if not linha.empty:
        itens.append(("camada tática v2", numero(linha.iloc[0]["Δ"]), float("nan")))

    fig, ax = plt.subplots(figsize=(6.6, 3.4))
    y = np.arange(len(itens))
    largura = 0.38
    total = [i[1] for i in itens]
    sem3 = [i[2] for i in itens]
    ax.barh(y + largura / 2, total, largura, color=p["kairos"], label="Δ no excesso")
    ax.barh(y - largura / 2, sem3, largura, color=p["apoio"],
            label="sem os 3 maiores dias")
    ax.axvline(0, color=p["grade"], lw=0.9)
    ax.set_yticks(y, [i[0] for i in itens])
    ax.set_xlabel("pontos percentuais de excesso × SPY")
    ax.invert_yaxis()
    # legenda acima: dentro do painel ela cai em cima da barra da camada tática
    ax.legend(frameon=False, ncol=2, loc="lower left",
              bbox_to_anchor=(0, 1.0, 1, 0.1))
    ax.margins(x=0.16)      # respiro para o rótulo das barras negativas
    ax.grid(axis="x", lw=0.5, alpha=0.5)
    for yi, (_, t, s) in zip(y, itens):
        for valor, deslocamento in ((t, largura / 2), (s, -largura / 2)):
            if not np.isnan(valor):
                ax.annotate(f"{valor:+.2f}", (valor, yi + deslocamento),
                            xytext=(4 if valor >= 0 else -4, 0),
                            textcoords="offset points", fontsize=8,
                            va="center", ha="left" if valor >= 0 else "right",
                            color=p["texto"])
    return salvar(fig, destino, "p4_atribuicao")


def _painel(ax, x, y, p, titulo, eixo_x, decidido=None):
    """Um mini-gráfico da varredura. `decidido` marca o valor já fechado."""
    ax.plot(x, y, color=p["kairos"], lw=1.6, marker="o", ms=3.5)
    ax.axhline(0, color=p["grade"], lw=0.8)
    ax.set_title(titulo, color=p["texto"], loc="left")
    ax.set_xlabel(eixo_x)
    ax.grid(lw=0.5, alpha=0.4)
    if decidido is not None and decidido in list(x):
        i = list(x).index(decidido)
        ax.plot([decidido], [y[i]], marker="o", ms=8, mfc="none",
                mec=p["apoio"], mew=1.6)


def grafico_sensibilidade(dados, p, destino):
    """As quatro varreduras num painel — o valor entregue não veio do resultado.

    Só marca o ponto das varreduras cujo valor JÁ está fechado por decisão
    (nível 1 = 6q, γ = 1 = D1.1, banda desligada no v1). O teto fica sem marca:
    a D12 está aberta e marcar um ponto seria escolher por gráfico.
    """
    excesso = "excesso acumulado (líquido − benchmark)"
    fig, eixos = plt.subplots(2, 2, figsize=(7.4, 4.6))

    met = pd.read_csv(dados / "backtest_metricas.csv", index_col=0)
    tetos = [c for c in met.columns if c.startswith("tilt")]
    _painel(eixos[0, 0], [numero(c) for c in tetos],
            [met.loc[excesso, c] * PONTOS_PERCENTUAIS for c in tetos], p,
            "Teto de risco (no tilt)", "teto de Σ|w − w_mkt|")

    nivel = pd.read_csv(dados / "curva_c_nivel.csv", index_col=0)
    nivel = nivel[nivel.index.map(lambda i: bool(re.match(r"^[\d.]+$", str(i))))]
    _painel(eixos[0, 1], [float(i) for i in nivel.index],
            list(nivel["excesso — teto no tilt"] * PONTOS_PERCENTUAIS), p,
            "Nível da régua do Ω", "nível (0 = He-Litterman)", decidido=1.0)

    banda = pd.read_csv(dados / "curva_banda.csv")
    _painel(eixos[1, 0], list(banda["banda"]),
            list(banda["excesso"] * PONTOS_PERCENTUAIS), p,
            "Banda de não-negociação", "banda (0 = desligada)", decidido=0.0)

    gama = pd.read_csv(dados / "backtest_gamma.csv", index_col=0)
    _painel(eixos[1, 1], [float(c) for c in gama.columns],
            [gama.loc[excesso, c] * PONTOS_PERCENTUAIS for c in gama.columns], p,
            "Correção favorite-longshot", "γ", decidido=1.0)

    for ax in eixos[:, 0]:
        ax.set_ylabel("excesso × SPY (pp)")
    return salvar(fig, destino, "p4_sensibilidade")


def salvar(fig, destino, nome):
    """SVG para o slide (vetor, não borra no projetor) e PNG como reserva."""
    destino.mkdir(parents=True, exist_ok=True)
    caminhos = []
    for extensao, dpi in (("svg", None), ("png", 300)):
        alvo = destino / f"{nome}.{extensao}"
        fig.savefig(alvo, dpi=dpi, bbox_inches="tight", transparent=True)
        caminhos.append(alvo)
    plt.close(fig)
    return caminhos


def escrever_metricas(tabela, caminho, cenario):
    """Tabela de métricas em markdown, pronta para colar no slide."""
    formato = {"Retorno líquido": "{:+.1%}", "Vol. anualizada": "{:.1%}",
               "Sharpe (excesso zero)": "{:.2f}", "Máx. drawdown": "{:.1%}",
               "Alpha anualizado": "{:+.2%}", "Beta vs SPY": "{:.2f}",
               "Σ|w| média": "{:.2f}", "Giro diário": "{:.2f}"}
    linhas = [f"# Métricas da página 4 — cenário `{cenario}`\n",
              "> Gerado por `scripts/graficos_p4.py` a partir de "
              "`Dump/dados/backtest_diario.csv`. Alpha e beta por regressão dos "
              "retornos diários contra o SPY, taxa livre de risco zero — mesma "
              "convenção do sharpe do backtest.\n",
              "| métrica | Kairós | SPY |", "|---|---|---|"]
    for nome, linha in tabela.iterrows():
        celulas = ["—" if pd.isna(v) else formato[nome].format(v) for v in linha]
        linhas.append(f"| {nome} | " + " | ".join(celulas) + " |")
    Path(caminho).write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return caminho


def gerar(dados, analises, destino, cenario, tema):
    p = PALETAS[tema]
    aplicar_estilo(p)
    diario = pd.read_csv(dados / "backtest_diario.csv", parse_dates=["data"],
                         index_col="data")
    if cenario not in set(diario["cenario"]):
        raise SystemExit(f"cenário '{cenario}' não está no CSV — há: "
                         + ", ".join(sorted(set(diario['cenario']))))
    recorte = diario[diario["cenario"] == cenario]
    saidas = grafico_curva(recorte, p, destino)
    saidas += grafico_atribuicao(analises / "Views_novas.md",
                                 analises / "Camada_tatica_v2.md", p, destino,
                                 teto_ref=numero(cenario))
    saidas += grafico_sensibilidade(dados, p, destino)
    saidas.append(escrever_metricas(metricas(recorte),
                                    analises / "Metricas_p4.md", cenario))
    return saidas


def demo():
    """Auto-teste em dado sintético: a matemática e os três desenhos."""
    import tempfile

    b = pd.Series(np.tile([0.01, -0.005], 60),
                  index=pd.bdate_range("2025-01-01", periods=120))
    # carteira = 2× o benchmark + 10 bps/dia: beta 2 e alpha 0,10%·252 conhecidos
    diario = pd.DataFrame({"r_liquido": 2 * b + 0.001, "r_benchmark": b,
                           "alavancagem": 2.0, "giro": 0.3}, index=b.index)
    diario.index.name = "data"
    m = metricas(diario)
    assert abs(m.loc["Beta vs SPY", "Kairós"] - 2.0) < 1e-9, m
    assert abs(m.loc["Alpha anualizado", "Kairós"] - 0.001 * PREGOES_POR_ANO) < 1e-9, m
    assert m.loc["Máx. drawdown", "Kairós"] < 0, m
    # drawdown de uma queda isolada de 10%: exatamente -10%
    assert abs(drawdown(pd.Series([0.0, -0.10, 0.0])).min() + 0.10) < 1e-12
    assert numero("+2.74 pp") == 2.74 and numero("48% (13/27)") == 48.0
    assert np.isnan(numero("—"))

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "Views_novas.md").write_text(
            "| configuração | Σ dos Δ diários | sem os 3 maiores |\n|---|---|---|\n"
            "| + incerteza (entropia crua) | +2.74 pp | -0.54 pp |\n"
            "| + B com β próprio (DGS1) | -0.96 pp | +2.93 pp |\n", encoding="utf-8")
        (tmp / "Camada_tatica_v2.md").write_text(
            "| teto no tilt | excesso × SPY (com) | Δ |\n|---|---|---|\n"
            "| 1 | +3.04 pp | -2.94 pp |\n", encoding="utf-8")
        lido = ler_tabela_md(tmp / "Views_novas.md", "sem os 3 maiores")
        assert list(lido["configuração"])[0] == "+ incerteza (entropia crua)", lido
        for cenario in ("tilt ≤ 1",):
            diario.assign(cenario=cenario).to_csv(tmp / "backtest_diario.csv")
        pd.DataFrame({"tilt ≤ 1": {"excesso acumulado (líquido − benchmark)": 0.03},
                      "tilt ≤ 2": {"excesso acumulado (líquido − benchmark)": 0.06}}
                     ).to_csv(tmp / "backtest_metricas.csv")
        pd.DataFrame({1.0: {"excesso acumulado (líquido − benchmark)": 0.03},
                      1.25: {"excesso acumulado (líquido − benchmark)": 0.04}}
                     ).to_csv(tmp / "backtest_gamma.csv")
        pd.DataFrame({"nível": ["sem régua", "0", "1"],
                      "excesso — teto no tilt": [0.01, 0.02, 0.03]}
                     ).set_index("nível").to_csv(tmp / "curva_c_nivel.csv")
        pd.DataFrame({"banda": [0.0, 0.001], "excesso": [0.03, 0.02]}
                     ).to_csv(tmp / "curva_banda.csv", index=False)
        saidas = gerar(tmp, tmp, tmp / "fig", "tilt ≤ 1", "escuro")
        assert all(Path(s).exists() for s in saidas), saidas
        assert "Beta vs SPY | 2.00" in (tmp / "Metricas_p4.md").read_text(
            encoding="utf-8")
    print(f"demo ok — {len(saidas)} arquivos gerados e conferidos")


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dados", default="Dump/dados",
                        help="pasta dos CSV gravados pelos scripts de medida")
    parser.add_argument("--analises", default="Dump/analises",
                        help="pasta dos artefatos markdown já publicados")
    parser.add_argument("--destino", default="Dump/graficos")
    parser.add_argument("--cenario", default=CENARIO_REF,
                        help="coluna do backtest a desenhar. O default é o "
                             "escopo de REFERÊNCIA do próprio backtest — a D12 "
                             "(nível e escopo do teto) segue aberta")
    parser.add_argument("--tema", choices=sorted(PALETAS), default="escuro")
    parser.add_argument("--demo", action="store_true",
                        help="auto-teste em dado sintético, sem tocar no Dump")
    args = parser.parse_args()

    if args.demo:
        return demo()
    for caminho in gerar(Path(args.dados), Path(args.analises),
                         Path(args.destino), args.cenario, args.tema):
        sys.stdout.write(f"escrito: {caminho}\n")


if __name__ == "__main__":
    main()
