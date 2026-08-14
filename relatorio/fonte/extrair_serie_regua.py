"""Série diária da entrega COM a régua do Ω ligada no nível 1.

Mesma configuração do `extrair_serie.py` (teto 1 no tilt, camada ligada), mas
passando `regua=` ao `run_backtest`. Não altera nenhum módulo de origem: a régua
entra pelo parâmetro que o `run_backtest` já expõe.
"""
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ = Path("X:/bt")
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "scripts"))

from backtest import run_backtest, summary  # noqa: E402
from backtest_v1 import carregar  # noqa: E402
from config import DELTA, TAU, CUSTO_BPS_POR_LADO  # noqa: E402
from market_inputs import regua_por_decisao  # noqa: E402

NIVEL = 1
SAIDA = Path("X:/serie_regua")
SAIDA.mkdir(exist_ok=True)

retornos, montador, datas, w_mkt = carregar(RAIZ)
regua = regua_por_decisao(str(RAIZ / "lia/c_por_decisao.csv"), NIVEL)

resultado = run_backtest(retornos, montador, w_mkt, datas=datas, tau=TAU,
                         delta=DELTA, custo_bps=CUSTO_BPS_POR_LADO,
                         teto_alavancagem=1.0, teto_no_tilt=True, regua=regua)
resumo = summary(resultado, benchmark=retornos["SPY"])

diario = resultado.diario.copy()
spy = retornos["SPY"].reindex(diario.index)

saida = pd.DataFrame({
    "retorno_liquido": diario["r_liquido"],
    "retorno_bruto": diario["r_bruto"],
    "custo": diario["custo"],
    "giro": diario["giro"],
    "alavancagem": diario["alavancagem"],
    "n_views": diario["n_views"],
    "n_taticas": diario["n_taticas"],
    "benchmark_spy": spy,
})
saida["acum_estrategia"] = (1 + saida["retorno_liquido"]).cumprod() - 1
saida["acum_spy"] = (1 + saida["benchmark_spy"]).cumprod() - 1
saida["excesso_acum"] = saida["acum_estrategia"] - saida["acum_spy"]
for nome in ("estrategia", "spy"):
    nav = 1 + saida[f"acum_{nome}"]
    saida[f"dd_{nome}"] = nav / nav.cummax() - 1

saida.index.name = "data"
saida.to_csv(SAIDA / "curva_diaria.csv", encoding="utf-8")
resumo.to_csv(SAIDA / "resumo.csv", encoding="utf-8")

print(resumo.to_string())
print()
print("acum estrategia:", round(saida["acum_estrategia"].iloc[-1], 6))
print("acum spy       :", round(saida["acum_spy"].iloc[-1], 6))
print("excesso        :", round(saida["excesso_acum"].iloc[-1], 6))
print("dd min estrat  :", round(saida["dd_estrategia"].min(), 6))
print("views/dia      :", round(saida["n_views"].mean(), 4))
