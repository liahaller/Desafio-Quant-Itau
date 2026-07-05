"""Testes sintéticos do otimizador BL — validam a mecânica exigida na Semana 1:
confiança alta -> carteira segue as views; confiança baixa -> fica no prior.

Todos os números aqui são SINTÉTICOS, só para o teste (tau/delta reais
virão de decisão registrada em Decisoes_pendentes.md).
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bl_optimizer import bl_posterior, implied_equilibrium_returns, optimal_weights

# --- caso sintético: 3 ativos, 1 view relativa (ativo 0 supera ativo 1 em 2%) ---
SIGMA = np.array([
    [0.040, 0.010, 0.005],
    [0.010, 0.030, 0.008],
    [0.005, 0.008, 0.020],
])
W_MKT = np.array([0.5, 0.3, 0.2])
DELTA = 2.5   # sintético
TAU = 0.05    # sintético
P = np.array([[1.0, -1.0, 0.0]])
Q = np.array([0.02])


def test_reverse_optimization_roundtrip():
    """pi vem de w_mkt; otimizar com pi deve devolver exatamente w_mkt."""
    pi_prior = implied_equilibrium_returns(SIGMA, W_MKT, DELTA)
    w = optimal_weights(pi_prior, SIGMA, DELTA)
    assert np.allclose(w, W_MKT), f"{w} != {W_MKT}"


def test_low_confidence_returns_prior():
    """omega enorme (confiança ~zero) -> posterior colapsa no prior."""
    pi_prior = implied_equilibrium_returns(SIGMA, W_MKT, DELTA)
    omega = np.array([[1e9]])
    mu_bl, sigma_bl = bl_posterior(pi_prior, SIGMA, TAU, P, Q, omega)
    assert np.allclose(mu_bl, pi_prior, atol=1e-8)
    # sem informação nas views, Sigma_bl -> (1 + tau) * Sigma (He & Litterman)
    assert np.allclose(sigma_bl, (1 + TAU) * SIGMA, atol=1e-8)


def test_high_confidence_matches_view():
    """omega ~zero (confiança total) -> a view é satisfeita: P @ mu_bl = Q."""
    pi_prior = implied_equilibrium_returns(SIGMA, W_MKT, DELTA)
    omega = np.array([[1e-12]])
    mu_bl, _ = bl_posterior(pi_prior, SIGMA, TAU, P, Q, omega)
    assert np.allclose(P @ mu_bl, Q, atol=1e-6), f"{P @ mu_bl} != {Q}"


def test_confidence_tilts_weights_monotonically():
    """Quanto maior a confiança, mais a carteira se inclina na direção da view.

    Nota: o prior de equilíbrio já implica P @ pi = 2.1% de spread; usamos
    uma view bem acima disso (5%) para o tilt ser positivo e crescente.
    """
    pi_prior = implied_equilibrium_returns(SIGMA, W_MKT, DELTA)
    q_bullish = np.array([0.05])
    tilt_prev = -np.inf
    for omega_scalar in (1e-2, 1e-3, 1e-4):
        mu_bl, sigma_bl = bl_posterior(pi_prior, SIGMA, TAU, P, q_bullish,
                                       np.array([[omega_scalar]]))
        w = optimal_weights(mu_bl, sigma_bl, DELTA)
        tilt = (w - W_MKT) @ P[0]  # exposição na direção da view (long 0, short 1)
        assert tilt > tilt_prev, f"tilt nao cresceu: {tilt} <= {tilt_prev}"
        tilt_prev = tilt
    assert tilt_prev > 0, f"tilt final deveria ser positivo: {tilt_prev}"


if __name__ == "__main__":
    test_reverse_optimization_roundtrip()
    test_low_confidence_returns_prior()
    test_high_confidence_matches_view()
    test_confidence_tilts_weights_monotonically()
    print("OK — 4 testes passaram")

    # demo ponta a ponta com dados sintéticos: view "ativo 0 supera ativo 1
    # em 5%" (bem acima do spread de equilibrio, 2.1%) em 3 niveis de confianca
    pi_prior = implied_equilibrium_returns(SIGMA, W_MKT, DELTA)
    q_demo = np.array([0.05])
    print(f"\npi_prior (equilibrio): {np.round(pi_prior, 4)}")
    print(f"pesos de mercado:      {W_MKT}")
    for label, omega_scalar in (("baixa", 1.0), ("media", 1e-3), ("alta", 1e-6)):
        mu_bl, sigma_bl = bl_posterior(pi_prior, SIGMA, TAU, P, q_demo,
                                       np.array([[omega_scalar]]))
        w = optimal_weights(mu_bl, sigma_bl, DELTA)
        print(f"confianca {label:5s} (omega={omega_scalar:g}): w = {np.round(w, 4)}")
