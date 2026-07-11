"""Testes sintéticos da integração (regra CLAUDE.md §5). τ/δ sintéticos,
marcados como tal — os reais vêm de decisão registrada."""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bl_integration import bl_weights_from_views, stack_views
from views_common import ViewResult

SIGMA = np.array([[0.04, 0.01, 0.00],
                  [0.01, 0.03, 0.01],
                  [0.00, 0.01, 0.02]])
W_MKT = np.array([0.5, 0.3, 0.2])
TAU, DELTA = 0.05, 2.5  # sintéticos


def _view(P, Q, nome):
    return ViewResult(P=np.asarray(P, dtype=float), Q=Q, diagnostics={"view": nome})


def test_stack_filtra_none_e_preserva_ordem():
    """None (view desativada) sai; ordem e diagnostics preservados."""
    v1 = _view([1.0, -1.0, 0.0], 0.02, "a")
    v2 = _view([0.0, 1.0, -1.0], -0.01, "b")
    P, Q, diags = stack_views([None, v1, None, v2], n_assets=3)
    assert P.shape == (2, 3) and np.allclose(Q, [0.02, -0.01])
    assert [d["view"] for d in diags] == ["a", "b"]
    # P desalinhado com o universo é rejeitado
    try:
        stack_views([_view([1.0, -1.0], 0.02, "c")], n_assets=3)
        assert False, "deveria rejeitar P de tamanho errado"
    except ValueError:
        pass


def test_sem_view_ativa_volta_w_mkt():
    """Caso neutro da decisão 8: todas desativadas -> w = w_mkt exato."""
    w, info = bl_weights_from_views(SIGMA, W_MKT, TAU, DELTA, [None, None])
    assert np.allclose(w, W_MKT)
    assert info["P"] is None and info["diagnostics"] == []


def test_confianca_zero_encosta_no_prior():
    """Ω enorme (confiança ~0) -> pesos ~ w_mkt (a view desbota)."""
    v = _view([1.0, -1.0, 0.0], 0.05, "a")
    w, _ = bl_weights_from_views(SIGMA, W_MKT, TAU, DELTA, [v], omega=np.array([[1e9]]))
    assert np.allclose(w, W_MKT, atol=1e-4)


def test_view_altista_tilta_na_direcao_certa():
    """View long ativo 0 / short ativo 1 com Q acima do prior -> w0 sobe, w1 cai."""
    v = _view([1.0, -1.0, 0.0], 0.05, "a")
    w, info = bl_weights_from_views(SIGMA, W_MKT, TAU, DELTA, [v], omega=np.array([[1e-4]]))
    assert info["P"].shape == (1, 3)
    assert w[0] > W_MKT[0] and w[1] < W_MKT[1]


def test_omega_obrigatorio_com_view_ativa():
    """View ativa sem Ω da Lia -> falha alto (nunca inventar confiança)."""
    v = _view([1.0, -1.0, 0.0], 0.05, "a")
    try:
        bl_weights_from_views(SIGMA, W_MKT, TAU, DELTA, [v])
        assert False, "deveria exigir omega"
    except ValueError:
        pass


if __name__ == "__main__":
    test_stack_filtra_none_e_preserva_ordem()
    test_sem_view_ativa_volta_w_mkt()
    test_confianca_zero_encosta_no_prior()
    test_view_altista_tilta_na_direcao_certa()
    test_omega_obrigatorio_com_view_ativa()
    print("bl_integration: 5 testes OK")
