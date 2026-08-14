"""Custo da camada tática COM a régua no nível 1 — as duas pontas na mesma config."""
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
RAIZ = Path("X:/bt")
sys.path.insert(0, str(RAIZ / "src")); sys.path.insert(0, str(RAIZ / "scripts"))
from backtest import run_backtest, summary
from backtest_v1 import carregar
from config import DELTA, TAU, CUSTO_BPS_POR_LADO
from market_inputs import regua_por_decisao

regua = regua_por_decisao(str(RAIZ / "lia/c_por_decisao.csv"), 1)
for sleeves in (False, True):
    retornos, montador, datas, w_mkt = carregar(RAIZ, sleeves=sleeves)
    r = run_backtest(retornos, montador, w_mkt, datas=datas, tau=TAU, delta=DELTA,
                     custo_bps=CUSTO_BPS_POR_LADO, teto_alavancagem=1.0,
                     teto_no_tilt=True, regua=regua)
    s = summary(r, benchmark=retornos["SPY"])
    print(f"camada={'LIGADA ' if sleeves else 'DESLIGADA'}: "
          f"excesso={s['excesso acumulado (líquido − benchmark)']*100:+.2f}pp", flush=True)
