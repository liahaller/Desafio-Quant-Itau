"""Slide 4 da final — o que cada fonte espera para cada ETF, dia a dia.

Grava `Uteis/dados/s4_comparacao.csv`: para cada pregão do backtest, o retorno
esperado por ETF segundo o MERCADO e segundo o POLYMARKET, na view 2.3 (decisão
do Fed) — a única que a fala percorre inteira.

  - `pi_<ETF>`   : equilíbrio π = δ·Σ·w_mkt, o retorno diário que justifica os
                   pesos que o mercado carrega. É o "não espero surpresa".
  - `poly_<ETF>` : π + β_i × surpresa líquida — o mesmo dia, se o Fed fizer o que
                   o Polymarket precifica em vez do que os juros embutem. O β é o
                   do event-study expansivo do próprio backtest (`_betas_fomc`).
  - `e_poly_bps`, `e_ff_bps`, `surpresa_liquida`, `dias_ate_evento`: o que a
                   view 2.3 registrou no dia (diagnostics), para a legenda.

Nada aqui é conta nova: é o `MontadorV1` de `backtest_v1.py` com a régua da Lia
ligada (nível 1, decisão 6q), lido dia a dia e gravado em forma larga. Em dia
sem a 2.3 ativa as colunas `poly_*` ficam vazias.

Uso:

    python scripts/comparacao_etf_s4.py          # mede e grava o CSV
    python scripts/comparacao_etf_s4.py --demo   # auto-teste (dia sintético)
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "scripts"))

import backtest_v1 as bv                                          # noqa: E402
from bl_integration import aplicar_veto, nomes_ativos             # noqa: E402
from bl_optimizer import implied_equilibrium_returns              # noqa: E402
from config import ASSETS, DELTA                                  # noqa: E402
from market_inputs import regua_por_decisao                       # noqa: E402

SAIDA = RAIZ / "Uteis" / "dados" / "s4_comparacao.csv"


def linha_do_dia(pi, betas, diag):
    """Uma linha larga: π por ETF e, se a 2.3 está ativa, π + β·surpresa."""
    linha = {f"pi_{a}": float(pi[i]) for i, a in enumerate(ASSETS)}
    if diag is None:
        return linha
    s = diag["surpresa_liquida"]
    linha.update({f"poly_{a}": float(pi[i] + betas[i] * s) for i, a in enumerate(ASSETS)})
    linha.update(e_poly_bps=diag["e_poly_bps"], e_ff_bps=diag["e_ff_bps"],
                 surpresa_bps=diag["surpresa_bps"], surpresa_liquida=s,
                 dias_ate_evento=diag["dias_ate_evento"])
    return linha


def medir(raiz=RAIZ):
    retornos, montador, datas, w_mkt = bv.carregar(raiz)
    regua = regua_por_decisao(str(raiz / "data/lia/c_por_decisao.csv"), nivel=1.0)
    linhas = {}
    for data in datas:
        sigma, views, _ = montador(data)
        views, _ = aplicar_veto(views, *regua(data, nomes_ativos(views)))
        v23 = next((v for v in views if v is not None
                    and v.diagnostics["view"] == "2.3_fed"), None)
        pi = implied_equilibrium_returns(np.asarray(sigma, float), w_mkt, DELTA)
        betas = montador._betas_fomc(data)[0] if v23 is not None else None
        linhas[data] = linha_do_dia(pi, betas, None if v23 is None else v23.diagnostics)
    return pd.DataFrame.from_dict(linhas, orient="index").rename_axis("data")


def demo():
    pi = np.full(len(ASSETS), 0.0003)
    betas = np.full(len(ASSETS), -0.001)
    diag = {"surpresa_liquida": 10.0, "e_poly_bps": -20.0, "e_ff_bps": -35.0,
            "surpresa_bps": 15.0, "dias_ate_evento": 1}
    linha = linha_do_dia(pi, betas, diag)
    # 10 bps de surpresa × −0,001/bp = −1 % em cima do prêmio de 3 bps
    assert abs(linha["poly_SPY"] - (0.0003 - 0.010)) < 1e-12
    assert "poly_SPY" not in linha_do_dia(pi, None, None)
    print("demo ok")


if __name__ == "__main__":
    if "--demo" in sys.argv:
        demo()
    else:
        df = medir()
        SAIDA.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(SAIDA)
        ativos = df["surpresa_liquida"].notna().sum()
        print(f"{SAIDA.relative_to(RAIZ)}: {len(df)} pregões, 2.3 ativa em {ativos}")
