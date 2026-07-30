"""Testes sintéticos do perfil de defasagem (caso com resultado conhecido)."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from perfil_defasagem_k import alinhar, correlacao_bidirecional, perfil_com_t

ATIVOS = ["SPY", "TLT"]


def _dados_com_defasagem_conhecida(k_real=2, n=200, coef=0.5, semente=0):
    """r(t) = coef * Δp(t − k_real), exato. O perfil TEM que achar k_real."""
    rng = np.random.default_rng(semente)
    datas = pd.bdate_range("2025-01-01", periods=n)
    p = pd.Series(np.cumsum(rng.normal(0, 0.01, n)) + 0.5, index=datas)
    dp = p.diff()
    retornos = pd.DataFrame({a: coef * dp.shift(k_real) for a in ATIVOS}).dropna()
    return dp.loc[retornos.index], retornos


def test_perfil_encontra_o_lag_plantado():
    dp, retornos = _dados_com_defasagem_conhecida(k_real=2, coef=0.5)
    coefs, ts, _ = perfil_com_t(dp, retornos, k_max=5)
    for ativo in ATIVOS:
        assert coefs[ativo].abs().idxmax() == 2
        assert np.isclose(coefs.loc[2, ativo], 0.5)
        # os demais lags são zero exato (relação determinística)
        assert coefs[ativo].drop(2).abs().max() < 1e-9


def test_correlacao_bidirecional_aponta_o_lado_certo():
    dp, retornos = _dados_com_defasagem_conhecida(k_real=2)
    corr = correlacao_bidirecional(dp, retornos)
    for ativo in ATIVOS:
        assert corr[ativo].idxmax() == 2          # poly lidera em +2
        assert corr.loc[-1, ativo] < corr.loc[2, ativo]


def test_correlacao_pega_bolsa_liderando():
    """Sinal invertido: o poly é que segue a bolsa -> pico em k negativo."""
    dp, retornos = _dados_com_defasagem_conhecida(k_real=2)
    retornos_adiantados = retornos.shift(-3).dropna()
    corr = correlacao_bidirecional(dp.loc[retornos_adiantados.index], retornos_adiantados)
    assert corr["SPY"].idxmax() == -1


def test_alinhar_usa_so_o_calendario_de_pregao():
    """Dias de poly sem pregão (fim de semana) não entram; Δp da segunda
    carrega o fim de semana inteiro."""
    p = pd.Series([0.10, 0.20, 0.30, 0.40, 0.55],
                  index=pd.to_datetime(["2025-01-03", "2025-01-04", "2025-01-05",
                                        "2025-01-06", "2025-01-07"]))  # 4 e 5 = fds
    retornos = pd.DataFrame({"SPY": [0.01, 0.02, 0.03]},
                            index=pd.to_datetime(["2025-01-03", "2025-01-06", "2025-01-07"]))
    dp, r = alinhar(p, retornos)
    assert list(r.index) == list(pd.to_datetime(["2025-01-06", "2025-01-07"]))
    np.testing.assert_allclose(dp.tolist(), [0.30, 0.15])  # sexta->segunda = 0.40-0.10
