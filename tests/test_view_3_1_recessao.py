"""Testes sintéticos da view 3.1 (regra CLAUDE.md §5: caso com resultado
conhecido). Inclui o sanity check de sinal OBRIGATÓRIO da espec (item 6),
com os números do exemplo da própria espec."""

import sys
from pathlib import Path

import numpy as np
from scipy.stats import norm

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from view_3_1_recessao import build_view, p_curve_probit

# Números do exemplo da espec (item 6), β em fração/ponto de probabilidade.
ASSETS = ["SPY", "XLK", "XLP", "TLT"]
BETAS = np.array([-0.30, -0.45, -0.10, 0.15])
# excess = [0, −0.15, +0.20, +0.45]; Σ|excess| = 0.80
# P = 2·excess/0.8 = [0, −0.375, 0.5, 1.125]; Σ P·β = 0.2875
P_ESPERADO = np.array([0.0, -0.375, 0.5, 1.125])
SUM_P_BETA = 0.2875


def test_probit_curva():
    """Spread 0 -> Phi(alpha); mais inclinação (spread maior) -> menos recessão."""
    assert np.isclose(p_curve_probit(0.0, alpha=-0.5, beta_spread=-1.0), norm.cdf(-0.5))
    p_invertida = p_curve_probit(-1.0, alpha=-0.5, beta_spread=-1.0)
    p_inclinada = p_curve_probit(2.0, alpha=-0.5, beta_spread=-1.0)
    assert p_invertida > p_inclinada  # curva invertida = mais recessão


def test_sanity_check_de_sinal_espec_item_6():
    """OBRIGATÓRIO (espec item 6): p_poly = 0.35, p_curva = 0.20 ->
    divergência +0.15 (poly mais pessimista) -> long defensivos/bonds
    (P[XLP] > 0, P[TLT] > 0), short cíclicos (P[XLK] < 0), Q > 0."""
    r = build_view(ASSETS, BETAS, k=2, p_poly=0.35, p_curva=0.20)
    assert np.allclose(r.P, P_ESPERADO)
    assert np.isclose(np.abs(r.P).sum(), 2.0)
    assert r.P[1] < 0 and r.P[2] > 0 and r.P[3] > 0
    assert r.diagnostics["sum_P_beta"] > 0  # dominado pelo termo quadrático
    assert np.isclose(r.Q, SUM_P_BETA * 0.15) and r.Q > 0


def test_divergencia_zero_q_zero():
    """Poly e curva de acordo -> Q = 0 (sem tilt)."""
    r = build_view(ASSETS, BETAS, k=2, p_poly=0.20, p_curva=0.20)
    assert np.isclose(r.Q, 0.0)


def test_sem_mercado_view_desativada():
    """Cascata item 0: sem mercado de recessão -> None (não é falha).
    Sem a curva a view falha alto (benchmark obrigatório quando ativa)."""
    assert build_view(ASSETS, BETAS, k=2) is None
    try:
        build_view(ASSETS, BETAS, k=2, p_poly=0.35)
        assert False, "p_curva ausente com view ativa deveria falhar"
    except ValueError:
        pass


def test_probabilidades_invalidas_rejeitadas():
    """p fora de [0, 1] é dado corrompido, não view."""
    try:
        build_view(ASSETS, BETAS, k=2, p_poly=1.35, p_curva=0.20)
        assert False, "deveria rejeitar p fora de [0, 1]"
    except ValueError:
        pass


if __name__ == "__main__":
    test_probit_curva()
    test_sanity_check_de_sinal_espec_item_6()
    test_divergencia_zero_q_zero()
    test_sem_mercado_view_desativada()
    test_probabilidades_invalidas_rejeitadas()
    print("view_3_1_recessao: 5 testes OK")
