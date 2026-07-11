"""Testes sintéticos do pré-processamento (regra CLAUDE.md §5: caso com resultado conhecido)."""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from poly_preprocessing import (
    midpoint_price,
    normalize_probs,
    favorite_longshot,
    open_bucket_value,
    pmf_mean,
    binary_prob_series,
)


def test_midpoint():
    """Midpoint é a média simples de bid e ask; bid > ask é rejeitado."""
    mid = midpoint_price([0.40, 0.50], [0.44, 0.52])
    assert np.allclose(mid, [0.42, 0.51])
    try:
        midpoint_price([0.60], [0.55])
        assert False, "deveria rejeitar bid > ask"
    except ValueError:
        pass


def test_normalize_binario():
    """Binário com spread: 0.62 + 0.36 -> normaliza para somar 1."""
    p = normalize_probs([0.62, 0.36])
    assert np.isclose(p.sum(), 1.0)
    assert np.isclose(p[0], 0.62 / 0.98)


def test_normalize_pmf_por_linha():
    """Matriz (datas x buckets) normaliza cada linha independentemente."""
    pmf = np.array([[0.10, 0.30, 0.50], [0.20, 0.20, 0.20]])
    out = normalize_probs(pmf, axis=1)
    assert np.allclose(out.sum(axis=1), 1.0)
    assert np.allclose(out[1], [1 / 3, 1 / 3, 1 / 3])


def test_pmf_mean():
    """Probs cruas [0.6, 0.3] normalizam para [2/3, 1/3]; média conhecida.
    NaN em values (bucket aberto não resolvido) e o stub default falham alto."""
    identidade = lambda p: np.asarray(p, dtype=float)  # sintético (decisão 11a pendente)
    m = pmf_mean([0.6, 0.3], [3.0, 6.0], fl_correction=identidade)
    assert np.isclose(m, 4.0)
    for probs, values in [([0.5, 0.5], [np.nan, 6.0])]:
        try:
            pmf_mean(probs, values, fl_correction=identidade)
            assert False, "deveria rejeitar NaN em values"
        except ValueError:
            pass
    try:
        pmf_mean([0.6, 0.3], [3.0, 6.0])  # default = stub da 11a
        assert False, "deveria levantar NotImplementedError"
    except NotImplementedError:
        pass


def test_binary_prob_series():
    """Midpoints (0.60, 0.30) normalizam para p_sim = 2/3; default (stub 11a) falha alto."""
    identidade = lambda p: np.asarray(p, dtype=float)  # sintético (decisão 11a pendente)
    p = binary_prob_series(
        bid_yes=[0.58, 0.40], ask_yes=[0.62, 0.44],
        bid_no=[0.28, 0.48], ask_no=[0.32, 0.52],
        fl_correction=identidade,
    )
    assert np.allclose(p, [0.6 / 0.9, 0.42 / 0.92])
    try:
        binary_prob_series([0.58], [0.62], [0.28], [0.32])  # default = stub da 11a
        assert False, "deveria levantar NotImplementedError"
    except NotImplementedError:
        pass


def test_stubs_falham_alto():
    """Stubs das pendências (decisão 11) devem falhar, nunca passar dado adiante."""
    for fn, args in [(favorite_longshot, ([0.1],)), (open_bucket_value, (3.6, "lower"))]:
        try:
            fn(*args)
            assert False, f"{fn.__name__} deveria levantar NotImplementedError"
        except NotImplementedError:
            pass


if __name__ == "__main__":
    test_midpoint()
    test_normalize_binario()
    test_normalize_pmf_por_linha()
    test_pmf_mean()
    test_binary_prob_series()
    test_stubs_falham_alto()
    print("poly_preprocessing: 6 testes OK")
