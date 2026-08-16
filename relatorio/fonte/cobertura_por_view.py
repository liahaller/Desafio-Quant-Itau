"""Cobertura por view na janela do backtest: calendário × depois do veto.

A tabela da página 3 do relatório mostra em quantos pregões cada view existe.
O número precisa sair da MESMA rodada que os demais números da entrega, e a
série diária (`curva_diaria*.csv`) só guarda o total de views do dia — daí este
script, que lê a quebra por view do `diagnostics` do `run_backtest`.

Duas rodadas, de propósito:

- **sem régua** — nenhuma view é vetada, então o `diagnostics` devolve o
  CALENDÁRIO puro. Serve também de controle: o resumo tem de bater com o
  `Dump/analises/Backtest_v1.md` do Felipe (sharpe 1,2136 · excesso +4,08 pp).
- **com régua no nível 1** (decisão 6q) — a view vetada vira `None` antes do
  `stack_views` e não aparece no `diagnostics`, que passa a ser a cobertura
  EFETIVA da entrega.

⚠️ **`montador.reset()` entre as rodadas é obrigatório.** O `MontadorV1` guarda
estado de propósito (a média da divergência da D9 é expansiva), então a segunda
rodada com o mesmo objeto começa com a janela inteira já vista e devolve outro
resultado — aqui deu excesso −0,29 pp no lugar de +3,04 pp. É a mesma chamada
que o `curva_c.py` do Felipe faz ao fim de cada rodada da grade.

Nenhum módulo alheio é tocado: a régua entra pelo parâmetro `regua=` que o
`run_backtest` já expõe. Depende do diretório de trabalho montado em `X:`
(código do branch `Felipe` + `data/` do branch `Paulo`) — ver `README.md`.
"""
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ = Path("X:/")
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "scripts"))

from backtest import run_backtest, summary  # noqa: E402
from backtest_v1 import carregar  # noqa: E402
from config import CUSTO_BPS_POR_LADO, DELTA, TAU  # noqa: E402
from market_inputs import regua_por_decisao  # noqa: E402

NIVEL = 1
SAIDA = Path(__file__).parent / "dados"

ROTULOS = {
    "2.3_fed": "2.3 · decisão do FOMC",
    "2.2_inflacao": "2.2 · inflação mensal",
    "B_trajetoria_propria": "B · trajetória de juros do ano",
    "incerteza_anuncio": "15b · incerteza no dia do anúncio",
}


def contar_por_view(resultado):
    """Pregões em que cada view entrou no P do BL, pelo `diagnostics` do dia."""
    contagem = Counter()
    for _, dia in resultado.diagnostics.items():
        for bloco in dia["views"]:
            contagem[bloco["view"]] += 1
    return contagem


retornos, montador, datas, w_mkt = carregar(RAIZ)
comum = dict(datas=datas, tau=TAU, delta=DELTA, custo_bps=CUSTO_BPS_POR_LADO,
             teto_alavancagem=1.0, teto_no_tilt=True)

print("rodando SEM régua (calendário + controle contra o Backtest_v1.md)...")
sem = run_backtest(retornos, montador, w_mkt, **comum)
resumo_sem = summary(sem, benchmark=retornos["SPY"])
montador.reset()   # sem isto a rodada seguinte herda as médias expansivas

print("rodando COM régua no nível 1...")
regua = regua_por_decisao(str(RAIZ / "lia/c_por_decisao.csv"), NIVEL)
com = run_backtest(retornos, montador, w_mkt, regua=regua, **comum)
resumo_com = summary(com, benchmark=retornos["SPY"])

cal, efetiva = contar_por_view(sem), contar_por_view(com)
n_pregoes = len(sem.diario)

tabela = pd.DataFrame(
    [{"view": v, "rotulo": ROTULOS.get(v, v), "pregoes": n_pregoes,
      "calendario": cal.get(v, 0), "apos_veto": efetiva.get(v, 0),
      "perda_pct": 100 * (1 - efetiva.get(v, 0) / cal[v]) if cal.get(v) else float("nan")}
     for v in sorted(cal, key=lambda k: -cal[k])])

SAIDA.mkdir(exist_ok=True)
tabela.to_csv(SAIDA / "cobertura_por_view.csv", index=False, encoding="utf-8")

print()
print(tabela.to_string(index=False))
print()
print(f"pregões                : {n_pregoes}")
print(f"views/dia sem régua    : {sem.diario['n_views'].mean():.4f}")
print(f"views/dia com régua    : {com.diario['n_views'].mean():.4f}")
print()
print("--- controle: a rodada sem régua tem de bater com o Backtest_v1.md ---")
for chave in ("sharpe anualizado (excesso zero)", "custo de breakeven (bps por lado)",
              "excesso acumulado (líquido − benchmark)"):
    print(f"{chave:45s} sem={resumo_sem[chave]:.4f}  com={resumo_com[chave]:.4f}")
