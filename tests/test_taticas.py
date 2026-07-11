"""Testes sintéticos da camada tática (regra CLAUDE.md §5: caso conhecido).

Cobre o contrato comum (apply_overlays) e as 3 táticas candidatas.
`_fl_identidade` é SINTÉTICO — injeta identidade no lugar do stub da
decisão 11a só para exercitar a matemática; em produção o default falha alto.
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import tatica_drift_pos_fomc
import tatica_gap_fds
import tatica_premio_anuncios
from taticas_common import OverlayResult, apply_overlays

ASSETS = ["SPY", "TIP", "TLT", "XLK"]


def _fl_identidade(p):
    return np.asarray(p, dtype=float)


# --- taticas_common ---------------------------------------------------------

def test_apply_overlays_soma_e_ignora_dormentes():
    """w_final = w_bl + Σ dw; None (dormente) não entra na soma."""
    w_bl = np.array([0.5, 0.2, 0.2, 0.1])
    r1 = OverlayResult(dw=np.array([0.1, 0.0, 0.0, 0.0]), diagnostics={"tatica": "a"})
    r2 = OverlayResult(dw=np.array([0.0, 0.0, -0.05, 0.0]), diagnostics={"tatica": "b"})
    w, diags = apply_overlays(w_bl, [r1, None, r2])
    assert np.allclose(w, [0.6, 0.2, 0.15, 0.1])
    assert [d["tatica"] for d in diags] == ["a", "b"]
    # sem tática ativa, w_final = w_bl exato
    w0, d0 = apply_overlays(w_bl, [None, None])
    assert np.allclose(w0, w_bl) and d0 == []


def test_apply_overlays_rejeita_dw_desalinhado():
    try:
        apply_overlays(np.zeros(4), [OverlayResult(dw=np.zeros(3), diagnostics={})])
        assert False, "deveria rejeitar dw com shape errado"
    except ValueError:
        pass


# --- 1.3 prêmio de anúncios --------------------------------------------------

def test_premio_pmf_uniforme_entropia_1():
    """PMF uniforme -> entropia normalizada = 1 -> dw[SPY] = orçamento cheio.
    Probs cruas com spread (soma 0.9) dão o mesmo resultado (normalização)."""
    r = tatica_premio_anuncios.build_overlay(
        ASSETS, orcamento_max=0.2, announcement_pmf=[0.3, 0.3, 0.3],
        fl_correction=_fl_identidade)
    assert np.allclose(r.dw, [0.2, 0.0, 0.0, 0.0])
    assert np.isclose(r.diagnostics["entropia_normalizada"], 1.0)


def test_premio_certeza_total_posicao_zero():
    """PMF degenerada (certeza) -> entropia 0 -> posição 0 (modulado, não
    liga/desliga); PMF concentrada tem sinal menor que a uniforme."""
    r = tatica_premio_anuncios.build_overlay(
        ASSETS, 0.2, announcement_pmf=[1.0, 0.0, 0.0], fl_correction=_fl_identidade)
    assert np.allclose(r.dw, 0.0)
    conc = tatica_premio_anuncios.build_overlay(
        ASSETS, 0.2, announcement_pmf=[0.9, 0.05, 0.05], fl_correction=_fl_identidade)
    assert 0.0 < conc.diagnostics["entropia_normalizada"] < 1.0


def test_premio_dia_sem_anuncio_dormente():
    """Cascata: sem anúncio / sem PMF utilizável -> None (não é falha)."""
    assert tatica_premio_anuncios.build_overlay(ASSETS, 0.2) is None


def test_premio_default_falha_alto_ate_decisao_11():
    """Sem fl_correction injetada, o stub da decisão 11a deve estourar."""
    try:
        tatica_premio_anuncios.build_overlay(ASSETS, 0.2, announcement_pmf=[0.5, 0.5])
        assert False, "deveria levantar NotImplementedError (TODO DECISAO-11a)"
    except NotImplementedError:
        pass


# --- drift pós-FOMC ----------------------------------------------------------

def test_drift_dovish_long_dois_livros():
    """Surpresa dovish (-10 bps) no dia 5: long SPY e long TLT, orçamento cheio."""
    r = tatica_drift_pos_fomc.build_overlay(
        ASSETS, dias_desde_fomc=5, surpresa_bps=-10.0,
        orcamento_acoes=0.1, orcamento_rf=0.05, janela_acoes=15, janela_rf=50)
    assert np.allclose(r.dw, [0.1, 0.0, 0.05, 0.0])
    assert r.diagnostics["direcao"] == 1.0
    # hawkish (+10 bps) espelha: short nos dois livros
    r2 = tatica_drift_pos_fomc.build_overlay(
        ASSETS, 5, +10.0, 0.1, 0.05, 15, 50)
    assert np.allclose(r2.dw, [-0.1, 0.0, -0.05, 0.0])


def test_drift_janela_acoes_fecha_antes_da_rf():
    """Dia 20 (> 15, <= 50): só o livro de renda fixa segue ativo."""
    r = tatica_drift_pos_fomc.build_overlay(
        ASSETS, 20, -10.0, 0.1, 0.05, janela_acoes=15, janela_rf=50)
    assert np.allclose(r.dw, [0.0, 0.0, 0.05, 0.0])
    assert not r.diagnostics["livro_acoes_ativo"]


def test_drift_truncagem_no_fomc_seguinte():
    """Dia do FOMC seguinte (dias_ate=0): livro de RF truncado -> dormente."""
    r = tatica_drift_pos_fomc.build_overlay(
        ASSETS, 42, -10.0, 0.1, 0.05, 15, 50, dias_ate_proximo_fomc=0)
    assert r is None
    # véspera do FOMC seguinte (dias_ate=1) ainda carrega
    r2 = tatica_drift_pos_fomc.build_overlay(
        ASSETS, 41, -10.0, 0.1, 0.05, 15, 50, dias_ate_proximo_fomc=1)
    assert np.isclose(r2.dw[ASSETS.index("TLT")], 0.05)


def test_drift_dormente_sem_drift_a_carregar():
    """Dia do anúncio (posição abre no close -> vale a partir do dia 1),
    surpresa zero (sign-based) e sem evento/surpresa -> None."""
    f = tatica_drift_pos_fomc.build_overlay
    assert f(ASSETS, 0, -10.0, 0.1, 0.05, 15, 50) is None
    assert f(ASSETS, 5, 0.0, 0.1, 0.05, 15, 50) is None
    assert f(ASSETS, None, -10.0, 0.1, 0.05, 15, 50) is None
    assert f(ASSETS, 5, None, 0.1, 0.05, 15, 50) is None


# --- gap de fim de semana ----------------------------------------------------

def test_gap_caso_conhecido():
    """Uma view: dw = lam * beta * dp — caso com números conhecidos."""
    betas = [0.0, 0.0, 1.0, -1.0]  # alinhado a ASSETS
    r = tatica_gap_fds.build_overlay(ASSETS, lam=0.5,
                                     view_signals=[("3.1_recessao", betas, 0.1)])
    assert np.allclose(r.dw, [0.0, 0.0, 0.05, -0.05])
    assert r.diagnostics["sinais"][0]["dp_fds"] == 0.1


def test_gap_multiplas_views_somam():
    """Tilts de views distintas somam (mesma lógica do empilhamento no BL)."""
    r = tatica_gap_fds.build_overlay(ASSETS, 1.0, [
        ("a", [1.0, 0.0, 0.0, 0.0], 0.1),
        ("b", [1.0, 0.0, 0.0, 0.0], -0.04),
    ])
    assert np.isclose(r.dw[0], 0.06)


def test_gap_dormente_e_beta_desalinhado():
    """Sem sinal (dia comum / sem snapshot) -> None; beta errado -> erro."""
    assert tatica_gap_fds.build_overlay(ASSETS, 1.0, []) is None
    assert tatica_gap_fds.build_overlay(ASSETS, 1.0, None) is None
    try:
        tatica_gap_fds.build_overlay(ASSETS, 1.0, [("a", [1.0, 2.0], 0.1)])
        assert False, "deveria rejeitar betas desalinhados"
    except ValueError:
        pass


if __name__ == "__main__":
    test_apply_overlays_soma_e_ignora_dormentes()
    test_apply_overlays_rejeita_dw_desalinhado()
    test_premio_pmf_uniforme_entropia_1()
    test_premio_certeza_total_posicao_zero()
    test_premio_dia_sem_anuncio_dormente()
    test_premio_default_falha_alto_ate_decisao_11()
    test_drift_dovish_long_dois_livros()
    test_drift_janela_acoes_fecha_antes_da_rf()
    test_drift_truncagem_no_fomc_seguinte()
    test_drift_dormente_sem_drift_a_carregar()
    test_gap_caso_conhecido()
    test_gap_multiplas_views_somam()
    test_gap_dormente_e_beta_desalinhado()
    print("taticas (common + 1.3 + drift + gap_fds): 13 testes OK")
