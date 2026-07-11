"""Testes sintéticos da view 2.3 (regra CLAUDE.md §5: caso com resultado conhecido).

Inclui o sanity check de sinal OBRIGATÓRIO da espec (item 6 de
`view_2.3_fed.md`), com os números do exemplo da própria espec.
`_fl_identidade` é SINTÉTICO — injeta identidade no lugar do stub da
decisão 11a; em produção o default falha alto.
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from view_2_3_fed import build_view, estimate_betas, P_from_betas

ASSETS = ["SPY", "XLK", "XLU", "TIP"]
# βs sintéticos em fração/bp: XLK long-duration (mais negativo), XLU defensivo.
BETAS = np.array([-0.0004, -0.0008, -0.0001, -0.0003])
# excess = β − β_SPY = [0, −4e−4, +3e−4, +1e−4]; Σ|excess| = 8e−4
# P = 2·excess/8e−4 = [0, −1, 0.75, 0.25]; Σ P·β = 6.5e−4
P_ESPERADO = np.array([0.0, -1.0, 0.75, 0.25])
SUM_P_BETA = 6.5e-4


def _fl_identidade(p):
    return np.asarray(p, dtype=float)


def test_estimate_betas_recupera_beta_exato():
    """Dados exatamente lineares (r = a + β·s) devolvem o β plantado."""
    s = np.array([10.0, -20.0, 5.0, 0.0, 15.0])
    betas_true = np.array([-0.0008, 0.0002])
    R = 0.001 + np.outer(s, betas_true)  # intercepto comum não contamina o β
    assert np.allclose(estimate_betas(R, s), betas_true)


def test_P_from_betas():
    """P determinístico: P[SPY] = 0 exato, Σ|P| = 2, proporcional ao excesso."""
    P = P_from_betas(BETAS, ASSETS)
    assert np.allclose(P, P_ESPERADO)
    assert P[0] == 0.0
    assert np.isclose(np.abs(P).sum(), 2.0)
    try:
        P_from_betas(np.full(4, -0.0004), ASSETS)
        assert False, "βs sem dispersão deveriam ser rejeitados"
    except ValueError:
        pass


def test_pmf_caso_conhecido():
    """Probs cruas [0.6, 0.3] nos buckets [−25, 0] → E_poly = −50/3 bps;
    e_ff = −10 → surpresa = −20/3; Q = surpresa · Σ P·β."""
    r = build_view(ASSETS, e_ff_bps=-10.0, betas=BETAS,
                   bucket_probs=[0.6, 0.3], bucket_deltas_bps=[-25.0, 0.0],
                   fl_correction=_fl_identidade)
    assert np.isclose(r.diagnostics["e_poly_bps"], -50.0 / 3.0)
    assert np.isclose(r.Q, (-50.0 / 3.0 + 10.0) * SUM_P_BETA)
    assert np.allclose(r.P, P_ESPERADO)
    assert r.diagnostics["caminho"] == "pmf"


def test_fallback_binario():
    """Binário cru (0.72, 0.24) → p = 0.75; Δ = −25 → E_poly = −18.75 bps."""
    r = build_view(ASSETS, e_ff_bps=-10.0, betas=BETAS,
                   binary_prob=(0.72, 0.24), binary_delta_bps=-25.0,
                   fl_correction=_fl_identidade)
    assert np.isclose(r.diagnostics["e_poly_bps"], -18.75)
    assert np.isclose(r.Q, -8.75 * SUM_P_BETA)
    assert r.diagnostics["caminho"] == "binario"


def test_sanity_check_de_sinal_espec_item_6():
    """OBRIGATÓRIO (espec item 6): poly precifica corte maior que o ZQ.
    E_poly = −20, E_FF = −10 → surpresa = −10 bps; β_XLK = −0.08%/bp →
    retorno esperado de XLK = +0.8% → XLK tem que sair no lado LONG do tilt
    (aqui: P[XLK] < 0 e Q < 0 → o BL vende o portfólio P → compra XLK)."""
    r = build_view(ASSETS, e_ff_bps=-10.0, betas=BETAS,
                   bucket_probs=[0.8, 0.2], bucket_deltas_bps=[-25.0, 0.0],
                   fl_correction=_fl_identidade)
    surpresa = r.diagnostics["surpresa_bps"]
    assert np.isclose(surpresa, -10.0)
    retorno_xlk = BETAS[1] * surpresa  # (−0.0008)·(−10) = +0.008
    assert np.isclose(retorno_xlk, 0.008) and retorno_xlk > 0
    assert r.P[1] < 0 and r.Q < 0  # sinais coerentes: tilt líquido compra XLK
    assert np.isclose(r.Q, surpresa * SUM_P_BETA)


def test_sem_mercado_view_desativada():
    """Cascata item 0: nenhum mercado de FOMC -> None (não é falha)."""
    assert build_view(ASSETS, e_ff_bps=-10.0, betas=BETAS) is None


def test_default_falha_alto_ate_decisao_11():
    """Sem fl_correction injetada, o stub da decisão 11a deve estourar."""
    try:
        build_view(ASSETS, e_ff_bps=-10.0, betas=BETAS,
                   bucket_probs=[0.5, 0.5], bucket_deltas_bps=[-25.0, 0.0])
        assert False, "deveria levantar NotImplementedError (TODO DECISAO-11a)"
    except NotImplementedError:
        pass


if __name__ == "__main__":
    test_estimate_betas_recupera_beta_exato()
    test_P_from_betas()
    test_pmf_caso_conhecido()
    test_fallback_binario()
    test_sanity_check_de_sinal_espec_item_6()
    test_sem_mercado_view_desativada()
    test_default_falha_alto_ate_decisao_11()
    print("view_2_3_fed: 7 testes OK")
