"""Testes sintéticos das views candidatas C, E e G (regra CLAUDE.md §5).

As três delegam ao template compartilhado (views_common.lagged_poly_view),
já coberto pelos testes da 2.4 — aqui ficam os sanity checks de sinal
OBRIGATÓRIOS de cada espec (item 7) e a cascata de desativação."""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from view_C_geopolitica_energia import build_view as build_C
from view_E_tarifas import build_view as build_E
from view_G_fiscal import build_view as build_G


def test_sanity_C_espec_item_7():
    """p(ataque) 0.20 -> 0.35 (div +0.15); β: XLE +4, SPY −1, XLK −2 ->
    long XLE, short XLK, Q > 0 (Kilian & Park)."""
    assets = ["SPY", "XLE", "XLK"]
    betas = np.array([-1.0, 4.0, -2.0])
    p = np.array([0.20, 0.25, 0.35])
    r = build_C(assets, betas, k=2, p_series=p)
    assert r.diagnostics["view"] == "C_geopolitica_energia"
    assert r.P[1] > 0 and r.P[2] < 0 and r.P[0] == 0.0
    assert np.isclose(np.abs(r.P).sum(), 2.0)
    # excess = [0, 5, −1] -> P = [0, 5/3, −1/3]; ΣP·β = 22/3; Q = 22/3 · 0.15
    assert np.isclose(r.Q, (22.0 / 3.0) * 0.15) and r.Q > 0


def test_sanity_E_espec_item_7():
    """p(tarifa EUA×China) 0.30 -> 0.50 (div +0.20); β: XLK −2.5, SPY −1,
    XLP +0.5, TLT +1 -> long defensivos/TLT, short tech, Q > 0 (AGKW)."""
    assets = ["SPY", "XLK", "XLP", "TLT"]
    betas = np.array([-1.0, -2.5, 0.5, 1.0])
    p = np.array([0.30, 0.40, 0.50])
    r = build_E(assets, betas, k=2, p_series=p)
    assert r.diagnostics["view"] == "E_tarifas"
    # excess = [0, −1.5, 1.5, 2] -> P = [0, −0.6, 0.6, 0.8]; ΣP·β = 2.6
    assert np.allclose(r.P, [0.0, -0.6, 0.6, 0.8])
    assert np.isclose(r.Q, 2.6 * 0.20) and r.Q > 0


def test_sanity_G_espec_item_7():
    """p(pacote tributário passa) 0.40 -> 0.60 (div +0.20); β: XLF +2,
    SPY +0.5, XLK −1 -> long XLF, short XLK, Q > 0 (WZZ)."""
    assets = ["SPY", "XLF", "XLK"]
    betas = np.array([0.5, 2.0, -1.0])
    p = np.array([0.40, 0.50, 0.60])
    r = build_G(assets, betas, k=2, p_series=p)
    assert r.diagnostics["view"] == "G_fiscal"
    # excess = [0, 1.5, −1.5] -> P = [0, 1, −1]; ΣP·β = 3
    assert np.allclose(r.P, [0.0, 1.0, -1.0])
    assert np.isclose(r.Q, 3.0 * 0.20) and r.Q > 0


def test_cascata_e_k_zero_no_template():
    """Sem mercado designado -> None; k ~ 0 falha alto (herdado do template)."""
    assets = ["SPY", "XLE"]
    betas = np.array([-1.0, 4.0])
    for build in (build_C, build_E, build_G):
        assert build(assets, betas, k=2) is None
        try:
            build(assets, betas, k=0, p_series=np.array([0.2, 0.3]))
            assert False, "k=0 deveria falhar alto"
        except NotImplementedError:
            pass


if __name__ == "__main__":
    test_sanity_C_espec_item_7()
    test_sanity_E_espec_item_7()
    test_sanity_G_espec_item_7()
    test_cascata_e_k_zero_no_template()
    print("views candidatas C/E/G: 4 testes OK")
