"""Teste mínimo do OLS univariado de `scripts/janela_negociavel.py`."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from janela_negociavel import ols_simples  # noqa: E402


def test_recupera_coeficiente_plantado():
    """y = 3·x + ruído pequeno -> coef ~ 3, |t| grande, corr ~ 1."""
    rng = np.random.default_rng(0)
    x = pd.Series(rng.normal(size=300))
    y = 3.0 * x + pd.Series(rng.normal(scale=0.01, size=300))
    coef, t, corr, n = ols_simples(y, x)
    assert abs(coef - 3.0) < 0.01
    assert abs(t) > 50
    assert corr > 0.99
    assert n == 300


def test_sem_relacao_da_coeficiente_nulo():
    """x e y independentes -> coef ~ 0 e |t| < 2."""
    rng = np.random.default_rng(1)
    x = pd.Series(rng.normal(size=300))
    y = pd.Series(rng.normal(size=300))
    coef, t, _, _ = ols_simples(y, x)
    assert abs(coef) < 0.15
    assert abs(t) < 2


def test_amostra_curta_devolve_nan():
    """Menos de 10 pares utilizáveis -> NaN, nunca número inventado."""
    x = pd.Series([1.0, 2.0, 3.0])
    y = pd.Series([1.0, 2.0, 3.0])
    coef, t, corr, n = ols_simples(y, x)
    assert np.isnan(coef) and np.isnan(t) and np.isnan(corr)
    assert n == 3


def test_ignora_nan_do_par():
    """NaN em qualquer um dos lados sai do par, não contamina o coeficiente."""
    rng = np.random.default_rng(2)
    x = pd.Series(rng.normal(size=100))
    y = 2.0 * x
    x_com_buraco = x.copy()
    x_com_buraco.iloc[:5] = np.nan
    coef, _, _, n = ols_simples(y, x_com_buraco)
    assert abs(coef - 2.0) < 1e-8
    assert n == 95
