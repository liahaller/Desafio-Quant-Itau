"""Testes das duas medidas novas do teste de tendência (casos sintéticos).

Piso do CLAUDE.md §5. Cada caso tem resultado conhecido de cabeça: passeio
aleatório dá VR ~1 e ρ ~0; série que se encadeia dá VR > 1 e ρ > 0; série que
reverte dá VR < 1 e ρ < 0. O que importa é a medida SEPARAR os três — é essa
separação que decide se o crescimento do G1 é tendência ou convergência.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from premissa_tendencia import (incrementos_nao_sobrepostos,  # noqa: E402
                                rho_com_t, variance_ratio)


def passeio(n=4000, semente=0):
    """Passeio aleatório puro: incrementos i.i.d., VR = 1 por construção."""
    rng = np.random.default_rng(semente)
    return pd.Series(np.cumsum(rng.normal(size=n)))


def encadeada(n=4000, phi=0.5, semente=0):
    """Incrementos AR(1) com phi > 0 — o que "tendência" quer dizer aqui."""
    rng = np.random.default_rng(semente)
    ruido = rng.normal(size=n)
    inc = np.zeros(n)
    for i in range(1, n):
        inc[i] = phi * inc[i - 1] + ruido[i]
    return pd.Series(np.cumsum(inc))


def test_variance_ratio_passeio_aleatorio_fica_em_um():
    for k in (2, 5, 10):
        assert variance_ratio(passeio(), k) == pytest.approx(1.0, abs=0.15)


def test_variance_ratio_separa_persistencia_de_reversao():
    """Incremento que se encadeia soma > 1; o que alterna cancela < 1."""
    assert variance_ratio(encadeada(phi=0.5), 5) > 1.5
    assert variance_ratio(encadeada(phi=-0.5), 5) < 1.0


def test_variance_ratio_sem_variancia_ou_serie_curta():
    assert np.isnan(variance_ratio([1.0, 1.0, 1.0, 1.0], 2))  # constante
    assert np.isnan(variance_ratio([1.0, 2.0], 5))            # curta demais


def test_rho_separa_encadeada_de_passeio():
    """A medida que decide: ρ ~0 no passeio, ρ > 0 e |t| alto na encadeada."""
    rho_passeio, t_passeio, n = rho_com_t(incrementos_nao_sobrepostos(passeio(), 1))
    assert n > 100
    assert rho_passeio == pytest.approx(0.0, abs=0.1)
    assert abs(t_passeio) < 2.0

    rho_enc, t_enc, _ = rho_com_t(incrementos_nao_sobrepostos(encadeada(phi=0.5), 1))
    assert rho_enc > 0.3
    assert t_enc > 2.0


def test_rho_com_poucos_pares_nao_inventa_t():
    """n pequeno é o caso do horizonte longo — a medida devolve NaN, não número."""
    rho, t, n = rho_com_t(pd.Series([1.0, -1.0, 1.0]))
    assert n == 2 and np.isnan(rho) and np.isnan(t)


def test_incrementos_nao_sobrepostos_nao_compartilham_pregao():
    """[0,k], [k,2k], ... — sobrepor inventaria autocorrelação positiva."""
    serie = pd.Series([0.0, 1.0, 3.0, 6.0, 10.0, 15.0, 21.0])
    assert list(incrementos_nao_sobrepostos(serie, 2)) == [3.0, 7.0, 11.0]
    assert list(incrementos_nao_sobrepostos(serie, 3)) == [6.0, 15.0]
