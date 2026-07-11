"""Testes sintéticos da view 2.4 e da maquinaria de defasagem compartilhada
(regra CLAUDE.md §5: caso com resultado conhecido)."""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from view_2_4_eleitoral import build_view
from views_common import full_absorption_beta, lag_regression

ASSETS = ["SPY", "XLK", "XLU", "TIP"]
# βs sintéticos em fração de retorno por unidade de probabilidade.
BETAS = np.array([0.02, 0.08, -0.02, 0.00])
# excess = β − β_SPY = [0, 0.06, −0.04, −0.02]; Σ|excess| = 0.12
# P = 2·excess/0.12 = [0, 1, −2/3, −1/3]; Σ P·β = 0.08 + 2/3·0.02 = 0.28/3
P_ESPERADO = np.array([0.0, 1.0, -2.0 / 3.0, -1.0 / 3.0])
SUM_P_BETA = 0.28 / 3.0


def test_lag_regression_recupera_perfil_plantado():
    """r(t) = a + β·Δp(t−2) exato -> coeficiente β no lag 2, ~0 nos demais;
    β de absorção plena até k=2 devolve o próprio β."""
    rng = np.random.default_rng(0)
    dp = rng.normal(0.0, 0.02, size=40)
    betas_true = np.array([0.05, -0.02])
    R = np.zeros((40, 2))
    R[2:] = 0.001 + np.outer(dp[:-2], betas_true)  # r(t) responde a dp(t−2)
    coefs = lag_regression(R, dp, k_max=3)
    assert coefs.shape == (4, 2)
    assert np.allclose(coefs[2], betas_true)
    assert np.allclose(np.delete(coefs, 2, axis=0), 0.0, atol=1e-10)
    assert np.allclose(full_absorption_beta(coefs, 2), betas_true)
    # amostra curta demais para os parâmetros -> falha alto
    try:
        lag_regression(R[:6], dp[:6], k_max=3)
        assert False, "deveria rejeitar amostra insuficiente"
    except ValueError:
        pass


def test_caso_conhecido():
    """p_t = 0.60, p_{t−2} = 0.55 -> divergência 0.05; Q = ΣP·β × 0.05."""
    p_series = np.array([0.50, 0.52, 0.55, 0.58, 0.60])
    r = build_view(ASSETS, BETAS, k=2, p_series=p_series)
    assert np.allclose(r.P, P_ESPERADO)
    assert np.isclose(np.abs(r.P).sum(), 2.0)
    assert np.isclose(r.diagnostics["divergencia"], 0.05)
    assert np.isclose(r.Q, SUM_P_BETA * 0.05)
    assert r.diagnostics["horizonte_q_dias"] == 2  # Q acumulado em k dias


def test_sem_mercado_view_desativada():
    """Cascata item 0: sem mercado de vencedor -> None (não é falha)."""
    assert build_view(ASSETS, BETAS, k=2) is None


def test_k_zero_falha_alto():
    """k ~ 0 é condição permanente (tese cai) — pendência de reunião, falha alto."""
    try:
        build_view(ASSETS, BETAS, k=0, p_series=np.array([0.5, 0.6]))
        assert False, "k=0 deveria falhar alto (decisão de reunião pendente)"
    except NotImplementedError:
        pass


def test_serie_curta_rejeitada():
    """Série com menos de k+1 pontos não permite p_{t−k}."""
    try:
        build_view(ASSETS, BETAS, k=3, p_series=np.array([0.5, 0.6]))
        assert False, "deveria rejeitar série mais curta que k+1"
    except ValueError:
        pass


if __name__ == "__main__":
    test_lag_regression_recupera_perfil_plantado()
    test_caso_conhecido()
    test_sem_mercado_view_desativada()
    test_k_zero_falha_alto()
    test_serie_curta_rejeitada()
    print("view_2_4_eleitoral: 5 testes OK")
