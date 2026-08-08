"""Testes sintéticos do drift pós-anúncio dimensionado por mean-variance.

Casos com resultado conhecido a mão (regra CLAUDE.md §5). O que precisa ficar
provado aqui é o que a decisão 12c cobrava: o tamanho sai de δ e Σ, não de um
orçamento; e o μ que dimensiona nunca enxerga o futuro.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tatica_drift_anuncio import build_overlay, estimate_drift_mu  # noqa: E402

ASSETS = ["SPY", "TIP", "TLT", "XLK"]


def _retornos(n=60, semente=0):
    """Grade de pregões com retorno zero — o teste planta o que quer medir."""
    idx = pd.bdate_range("2025-01-01", periods=n)
    return pd.DataFrame(0.0, index=idx, columns=ASSETS)


# Σ e τ do encolhimento. Σ diagonal e τ generoso -> fator ~1, para os testes de
# recuperação medirem o μ e não o desconto (que tem teste próprio).
SIGMA_FROUXA = np.eye(len(ASSETS))
TAU_FROUXO = 1.0


# --- estimate_drift_mu ------------------------------------------------------

def _planta_drift(r, eventos, ativo, retorno, janela=5):
    for data, _ in eventos:
        pos = r.index.searchsorted(data, side="right")
        r.iloc[pos:pos + janela, r.columns.get_loc(ativo)] = retorno
    return r


def test_mu_recupera_drift_plantado_liquido_da_linha_de_base():
    """Drift de −0,2%/dia no SPY após dois eventos dovish (direção −1).

    O μ é o EXCESSO sobre o retorno médio da amostra, então o valor esperado
    desconta a linha de base — que os próprios dias plantados contaminam.
    """
    r = _retornos()
    eventos = [(r.index[10], -1.0), (r.index[30], -1.0)]
    _planta_drift(r, eventos, "SPY", -0.002)
    mu, n = estimate_drift_mu(r, eventos, janela=5, ativos_livro=["SPY"],
                              ate_data=r.index[-1], sigma=SIGMA_FROUXA,
                              tau=TAU_FROUXO)
    base = r["SPY"][r.index < r.index[-1]].mean()
    assert n == 2
    assert mu[ASSETS.index("SPY")] == pytest.approx(-1.0 * (-0.002 - base))
    # ativo fora do livro entra zerado mesmo tendo retorno na janela
    assert mu[ASSETS.index("TLT")] == 0.0


def test_mu_ignora_deriva_constante_do_mercado():
    """Somar retorno igual a TODOS os dias não muda o μ.

    É o que separa drift de anúncio de prêmio de risco: sem a linha de base, uma
    sleeve com direção quase sempre +1 mediria o bull market e o compraria.
    """
    idx = pd.bdate_range("2025-01-01", periods=60)
    eventos = [(idx[10], 1.0), (idx[30], 1.0)]
    sem, com = _retornos(), _retornos()
    for r in (sem, com):
        _planta_drift(r, eventos, "SPY", 0.003)
    com += 0.0005  # deriva constante em todos os ativos e todos os dias
    mu_sem, _ = estimate_drift_mu(sem, eventos, 5, ["SPY"], sem.index[-1], SIGMA_FROUXA, TAU_FROUXO)
    mu_com, _ = estimate_drift_mu(com, eventos, 5, ["SPY"], com.index[-1], SIGMA_FROUXA, TAU_FROUXO)
    assert np.allclose(mu_sem, mu_com)


def test_encolhimento_pune_dispersao_entre_eventos():
    """Dois eventos discordando encolhem o μ; dois concordando, não.

    É o que substitui a confiança infinita: μ curto e disperso não pede tamanho.
    """
    idx = pd.bdate_range("2025-01-01", periods=60)
    concordam, discordam = _retornos(), _retornos()
    _planta_drift(concordam, [(idx[10], 1.0), (idx[30], 1.0)], "SPY", 0.003)
    _planta_drift(discordam, [(idx[10], 1.0)], "SPY", 0.03)
    _planta_drift(discordam, [(idx[30], 1.0)], "SPY", -0.024)
    sigma = np.eye(len(ASSETS)) * 0.0001
    args = (5, ["SPY"], idx[-1], sigma, 1.0 / 504)
    mu_ok, _ = estimate_drift_mu(concordam, [(idx[10], 1.0), (idx[30], 1.0)], *args)
    mu_ruim, _ = estimate_drift_mu(discordam, [(idx[10], 1.0), (idx[30], 1.0)], *args)
    i = ASSETS.index("SPY")
    # as duas amostras têm média parecida; só a dispersão entre eventos difere
    assert abs(mu_ruim[i]) < abs(mu_ok[i]) / 10


def test_mu_ignora_evento_cuja_janela_nao_fechou():
    """Sem lookahead: janela que invade `ate_data` não entra no μ."""
    r = _retornos()
    eventos = [(r.index[10], 1.0), (r.index[40], 1.0)]
    for data, _ in eventos:
        pos = r.index.searchsorted(data, side="right")
        r.iloc[pos:pos + 5, r.columns.get_loc("SPY")] = 0.01
    _, n_cedo = estimate_drift_mu(r, eventos, 5, ["SPY"], r.index[42], SIGMA_FROUXA, TAU_FROUXO)
    _, n_tarde = estimate_drift_mu(r, eventos, 5, ["SPY"], r.index[50], SIGMA_FROUXA, TAU_FROUXO)
    assert (n_cedo, n_tarde) == (1, 2)


def test_mu_none_quando_nenhum_evento_fechou():
    r = _retornos()
    mu, n = estimate_drift_mu(r, [(r.index[10], 1.0)], 5, ["SPY"],
                              r.index[11], SIGMA_FROUXA, TAU_FROUXO)
    assert mu is None and n == 0


# --- build_overlay ----------------------------------------------------------

def _sigma_diagonal(var=0.0001):
    return np.eye(len(ASSETS)) * var


def test_dw_e_o_passo_mean_variance():
    """Σ diagonal: dw[i] = μ[i] / (δ·σ²) — o tamanho vem de δ e Σ, só."""
    mu = np.array([0.002, 0.0, 0.0, 0.0])
    r = build_overlay(ASSETS, "fomc", dias_desde_evento=3, direcao=-1.0, mu=mu,
                      sigma=_sigma_diagonal(), delta=3.0, janela=15)
    esperado = -0.002 / (3.0 * 0.0001)
    assert r.dw[ASSETS.index("SPY")] == pytest.approx(esperado)
    assert np.allclose(r.dw[1:], 0.0)
    assert r.diagnostics["soma_abs_dw"] == pytest.approx(abs(esperado))


def test_dobrar_delta_corta_o_tilt_pela_metade():
    """Não há orçamento: quem escala é δ, e ele é observável (D7)."""
    mu = np.array([0.002, 0.0, 0.0, 0.0])
    args = dict(assets=ASSETS, familia="fomc", dias_desde_evento=1, direcao=1.0,
                mu=mu, sigma=_sigma_diagonal(), janela=15)
    assert np.allclose(build_overlay(delta=6.0, **args).dw,
                       build_overlay(delta=3.0, **args).dw / 2.0)


def test_dormente_fora_da_janela_e_sem_direcao():
    mu = np.array([0.002, 0.0, 0.0, 0.0])
    args = dict(assets=ASSETS, familia="fomc", mu=mu, sigma=_sigma_diagonal(),
                delta=3.0, janela=15)
    assert build_overlay(dias_desde_evento=0, direcao=1.0, **args) is None
    assert build_overlay(dias_desde_evento=16, direcao=1.0, **args) is None
    assert build_overlay(dias_desde_evento=3, direcao=0.0, **args) is None
    assert build_overlay(dias_desde_evento=3, direcao=None, **args) is None
    assert build_overlay(dias_desde_evento=None, direcao=1.0, **args) is None


def test_dormente_sem_mu_estimado():
    """Antes do primeiro evento fechado a sleeve não opera (cascata, não erro)."""
    assert build_overlay(ASSETS, "cpi", 3, 1.0, None, _sigma_diagonal(), 3.0, 15) is None


def test_direcao_inverte_o_tilt_inteiro():
    mu = np.array([0.002, 0.0, -0.001, 0.0])
    args = dict(assets=ASSETS, familia="cpi", dias_desde_evento=2,
                mu=mu, sigma=_sigma_diagonal(), delta=3.0, janela=15)
    assert np.allclose(build_overlay(direcao=+1.0, **args).dw,
                       -build_overlay(direcao=-1.0, **args).dw)


def test_shapes_incompativeis_estouram():
    with pytest.raises(ValueError):
        build_overlay(ASSETS, "fomc", 1, 1.0, np.zeros(3), _sigma_diagonal(), 3.0, 15)
    with pytest.raises(ValueError):
        build_overlay(ASSETS, "fomc", 1, 1.0, np.zeros(4), _sigma_diagonal(), 0.0, 15)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
