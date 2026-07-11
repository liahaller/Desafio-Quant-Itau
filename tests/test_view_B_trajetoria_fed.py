"""Testes sintéticos da view B — candidata (regra CLAUDE.md §5).
Inclui o sanity check de sinal obrigatório (espec item 6)."""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from view_B_trajetoria_fed import build_view, rates_from_cut_buckets

# Mesmos βs sintéticos da 2.3 (a view B REUSA os β da 2.3 por espec).
ASSETS = ["SPY", "XLK", "XLU", "TIP"]
BETAS = np.array([-0.0004, -0.0008, -0.0001, -0.0003])
P_ESPERADO = np.array([0.0, -1.0, 0.75, 0.25])  # idêntico ao da 2.3, por construção
SUM_P_BETA = 6.5e-4


def _fl_identidade(p):
    return np.asarray(p, dtype=float)


def test_conversao_buckets_de_cortes():
    """Taxa vigente 450bp: [0, 1, 2] cortes -> [450, 425, 400] bps."""
    assert np.allclose(rates_from_cut_buckets(450.0, [0, 1, 2]), [450.0, 425.0, 400.0])


def test_pmf_caso_conhecido():
    """Buckets de taxa [400, 425] com probs iguais -> E_poly = 412.5;
    ZQ dez = 430 -> surpresa = −17.5 bps; P idêntico ao da 2.3."""
    r = build_view(ASSETS, e_zq_dez_bps=430.0, betas=BETAS,
                   bucket_probs=[0.45, 0.45], bucket_rates_bps=[400.0, 425.0],
                   fl_correction=_fl_identidade)
    assert np.isclose(r.diagnostics["surpresa_bps"], -17.5)
    assert np.allclose(r.P, P_ESPERADO)
    assert np.isclose(r.Q, -17.5 * SUM_P_BETA)
    assert r.diagnostics["caminho"] == "pmf"


def test_sanity_check_de_sinal_espec_item_6():
    """OBRIGATÓRIO (espec item 6): poly mais dovish que o ZQ dez.
    E_poly = 400, E_ZQdez = 430 -> surpresa = −30 bps; β_XLK = −0.08%/bp ->
    retorno esperado de XLK = +2.4% -> XLK no lado LONG (P[XLK] < 0 e Q < 0)."""
    r = build_view(ASSETS, e_zq_dez_bps=430.0, betas=BETAS,
                   bucket_probs=[1.0], bucket_rates_bps=[400.0],
                   fl_correction=_fl_identidade)
    surpresa = r.diagnostics["surpresa_bps"]
    assert np.isclose(surpresa, -30.0)
    retorno_xlk = BETAS[1] * surpresa  # (−0.0008)·(−30) = +0.024
    assert np.isclose(retorno_xlk, 0.024) and retorno_xlk > 0
    assert r.P[1] < 0 and r.Q < 0  # tilt líquido compra XLK


def test_fallback_binario():
    """Taxa vigente 450, p(corte até dez) = 0.6 -> E_poly = 435 bps."""
    r = build_view(ASSETS, e_zq_dez_bps=430.0, betas=BETAS,
                   binary_prob=(0.6, 0.4), taxa_atual_bps=450.0,
                   fl_correction=_fl_identidade)
    assert np.isclose(r.diagnostics["e_poly_bps"], 435.0)
    assert r.diagnostics["caminho"] == "binario"
    # fallback sem taxa vigente é rejeitado
    try:
        build_view(ASSETS, 430.0, BETAS, binary_prob=(0.6, 0.4), fl_correction=_fl_identidade)
        assert False, "deveria exigir taxa_atual_bps"
    except ValueError:
        pass


def test_sem_mercado_view_desativada():
    """Cascata item 0: sem mercado de trajetória -> None (não é falha)."""
    assert build_view(ASSETS, e_zq_dez_bps=430.0, betas=BETAS) is None


if __name__ == "__main__":
    test_conversao_buckets_de_cortes()
    test_pmf_caso_conhecido()
    test_sanity_check_de_sinal_espec_item_6()
    test_fallback_binario()
    test_sem_mercado_view_desativada()
    print("view_B_trajetoria_fed: 5 testes OK")
