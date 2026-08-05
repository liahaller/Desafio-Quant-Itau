"""Testes sintéticos de Σ, w_mkt e Ω de fallback (CLAUDE.md §5)."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bl_integration import bl_weights_from_views  # noqa: E402
from market_inputs import (  # noqa: E402
    breakeven_duration, equal_weights, market_weights, omega_fallback,
    sample_covariance)

ATIVOS = ["SPY", "TIP", "TLT"]


def _retornos(n=600, seed=0):
    rng = np.random.default_rng(seed)
    return pd.DataFrame(rng.normal(scale=0.01, size=(n, 3)), columns=ATIVOS,
                        index=pd.bdate_range("2023-01-02", periods=n))


def test_sigma_recupera_covariancia_plantada():
    """Ativos independentes com vol conhecida -> Σ ~ diagonal de 1e-4."""
    sigma = sample_covariance(_retornos(), janela=500)
    assert sigma.shape == (3, 3)
    assert np.allclose(np.diag(sigma), 1e-4, rtol=0.15)
    assert abs(sigma[0, 1]) < 2e-5  # fora da diagonal ~ zero


def test_sigma_nao_olha_o_futuro():
    """Com `data`, só entram pregões ANTERIORES a ela."""
    r = _retornos()
    corte = r.index[300]
    r.loc[r.index >= corte] = 99.0  # armadilha: lixo depois do corte
    sigma = sample_covariance(r, data=corte, janela=200)
    assert np.all(np.diag(sigma) < 1e-3)  # não pegou o 99


def test_sigma_rejeita_janela_curta():
    try:
        sample_covariance(_retornos(n=10), janela=500)
        assert False, "deveria rejeitar janela curta"
    except ValueError:
        pass


def test_sigma_rejeita_mal_condicionada():
    """Dois ativos idênticos -> Σ singular -> falha alto em vez de devolver lixo."""
    r = _retornos()
    r["TLT"] = r["TIP"]
    try:
        sample_covariance(r, janela=500)
        assert False, "deveria rejeitar Σ mal condicionada"
    except ValueError as e:
        assert "condicionada" in str(e)


def test_w_mkt_e_capm():
    w = market_weights(ATIVOS)
    assert np.allclose(w, [1.0, 0.0, 0.0])
    assert np.isclose(w.sum(), 1.0)
    assert np.allclose(equal_weights(ATIVOS), 1 / 3)


def test_w_mkt_exige_ativo_de_mercado_no_universo():
    try:
        market_weights(["TIP", "TLT"])
        assert False, "deveria rejeitar universo sem SPY"
    except ValueError:
        pass


def test_omega_fallback_e_a_variancia_do_prior():
    """Com confiança 1, Ω[i,i] = P_i·τΣ·P_iᵀ exatamente."""
    sigma = np.diag([1e-4, 4e-4, 9e-4])
    P = np.array([[1.0, -1.0, 0.0], [0.0, 0.0, 1.0]])
    tau = 0.002
    omega = omega_fallback(P, sigma, tau)
    assert np.allclose(np.diag(omega), [tau * 5e-4, tau * 9e-4])
    assert np.allclose(omega - np.diag(np.diag(omega)), 0.0)  # diagonal


def test_omega_confianca_escala_a_diagonal():
    sigma = np.diag([1e-4, 4e-4, 9e-4])
    P = np.array([[1.0, -1.0, 0.0]])
    base = omega_fallback(P, sigma, 0.002)
    dobro = omega_fallback(P, sigma, 0.002, confianca=[2.0])
    assert np.allclose(np.diag(dobro), 2 * np.diag(base))
    for ruim in ([0.0], [-1.0], [1.0, 1.0]):
        try:
            omega_fallback(P, sigma, 0.002, confianca=ruim)
            assert False, f"deveria rejeitar confiança {ruim}"
        except ValueError:
            pass


def test_sem_view_a_carteira_e_o_benchmark():
    """Fecha o circuito: com w_mkt do CAPM e nenhuma view ativa, o otimizador
    devolve exatamente comprar e segurar SPY (caso neutro da decisão 8)."""
    sigma = sample_covariance(_retornos(), janela=500)
    w_mkt = market_weights(ATIVOS)
    w, _ = bl_weights_from_views(sigma, w_mkt, tau=0.002, delta=3.0,
                                 view_results=[None, None])
    assert np.allclose(w, w_mkt)


def test_breakeven_duration_recupera_o_coeficiente_plantado():
    """Par que rende 6x o Δbreakeven mais ruído -> duration medida ~ 6."""
    rng = np.random.default_rng(1)
    dbe = pd.Series(rng.normal(scale=0.0005, size=400),
                    index=pd.bdate_range("2024-01-01", periods=400))
    par = 6.0 * dbe + rng.normal(scale=1e-5, size=400)
    assert breakeven_duration(par, dbe) == pytest.approx(6.0, rel=0.05)


def test_breakeven_duration_exige_amostra():
    curta = pd.Series(np.zeros(30), index=pd.bdate_range("2024-01-01", periods=30))
    with pytest.raises(ValueError, match="amostra curta"):
        breakeven_duration(curta, curta)
