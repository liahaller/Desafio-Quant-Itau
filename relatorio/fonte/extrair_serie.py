"""Extrai a série diária da carteira de entrega para os gráficos do relatório.

Não altera nada dos módulos de origem: importa `carregar` e `run_backtest` como
biblioteca e grava as séries em CSV. Configuração da entrega: teto no tilt = 1
(D10a) com a camada tática ligada (D28.13).
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

SAIDA = Path("X:/serie")
SAIDA.mkdir(exist_ok=True)

retornos, montador, datas, w_mkt = carregar(RAIZ)

# A entrega: teto de referência 1, cortando só o tilt.
resultado = run_backtest(retornos, montador, w_mkt, datas=datas, tau=TAU,
                         delta=DELTA, custo_bps=CUSTO_BPS_POR_LADO,
                         teto_alavancagem=1.0, teto_no_tilt=True)
resumo = summary(resultado, benchmark=retornos["SPY"])

diario = resultado.diario.copy()
spy = retornos["SPY"].reindex(diario.index)

# Curvas acumuladas compostas, base 0 no primeiro pregão da janela.
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

# Drawdown das duas curvas — o edital pede leitura crítica, e o pico-a-vale é
# o que falta na tabela de métricas do artefato.
for nome in ("estrategia", "spy"):
    nav = 1 + saida[f"acum_{nome}"]
    saida[f"dd_{nome}"] = nav / nav.cummax() - 1

saida.index.name = "data"
saida.to_csv(SAIDA / "curva_diaria.csv", encoding="utf-8")
resultado.pesos.to_csv(SAIDA / "pesos_diarios.csv", encoding="utf-8")
diario.to_csv(SAIDA / "diario_completo.csv", encoding="utf-8")
resumo.to_csv(SAIDA / "resumo.csv", encoding="utf-8")

print("colunas do diario:", list(diario.columns))
print()
print(resumo.to_string())
print()
print("acum estrategia:", round(saida['acum_estrategia'].iloc[-1], 6))
print("acum spy       :", round(saida['acum_spy'].iloc[-1], 6))
print("excesso        :", round(saida['excesso_acum'].iloc[-1], 6))
print("dd min estrat  :", round(saida['dd_estrategia'].min(), 6))
print("dd min spy     :", round(saida['dd_spy'].min(), 6))
print("pregoes        :", len(saida))
