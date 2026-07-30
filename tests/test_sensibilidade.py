"""Testes sintéticos das regras varridas no pacote de sensibilidade."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sensibilidade_reuniao import e_poly, fl_power, valores_com_ponta


def test_valores_com_ponta_desloca_as_duas_pontas():
    grade = np.array([0.0, 0.1, 0.2, 0.3])
    assert valores_com_ponta(grade, 0.0).tolist() == [0.0, 0.1, 0.2, 0.3]
    np.testing.assert_allclose(valores_com_ponta(grade, 0.5), [-0.05, 0.1, 0.2, 0.35])
    np.testing.assert_allclose(valores_com_ponta(grade, 1.0), [-0.1, 0.1, 0.2, 0.4])


def test_valores_com_ponta_so_a_alta_e_resolve_nan():
    # caso do M3: "no cuts" = 0 é exato; a ponta alta vem NaN (slug "8plus")
    grade = np.array([0.0, 1.0, 2.0, np.nan])
    resolvida = valores_com_ponta(grade, 0.5, abertas=("alta",))
    np.testing.assert_allclose(resolvida, [0.0, 1.0, 2.0, 3.5])


def test_fl_power_identidade_e_encolhimento_do_longshot():
    np.testing.assert_allclose(fl_power(1.0)([0.2, 0.8]), [0.2, 0.8])
    # gamma > 1 encolhe o longshot: 0.2^2 / (0.2^2 + 0.8^2) = 0.04/0.68
    np.testing.assert_allclose(fl_power(2.0)([0.2, 0.8]), [0.04 / 0.68, 0.64 / 0.68])


def _pmf_com_buraco():
    """2 buckets (valores 0.0 e 1.0) e 3 slots; o bucket 'a' some no slot 2."""
    return pd.DataFrame({"a": [0.5, 0.4, np.nan], "b": [0.5, 0.6, 0.7]},
                        index=pd.date_range("2025-01-01", periods=3, freq="12h"))


def test_e_poly_regras_de_faixa_faltante():
    pmf, values, fl = _pmf_com_buraco(), np.array([0.0, 1.0]), fl_power(1.0)

    # renormalizar: no slot 2 só sobra 'b' -> E = 1.0
    renorm = e_poly(pmf, values, fl, "renormalizar")
    np.testing.assert_allclose(renorm.tolist(), [0.5, 0.6, 1.0])

    # carregar: 'a' entra com o último preço (0.4) -> 0.7/(0.4+0.7)
    carregar = e_poly(pmf, values, fl, "carregar")
    np.testing.assert_allclose(carregar.tolist(), [0.5, 0.6, 0.7 / 1.1])

    # slot completo: o slot 2 sai da conta
    completo = e_poly(pmf, values, fl, "slot completo")
    assert len(completo) == 2
    np.testing.assert_allclose(completo.tolist(), [0.5, 0.6])


def test_e_poly_normaliza_soma_diferente_de_um():
    # PMF crua não soma 1 (medido: 0,92 a 1,33) — a média tem que normalizar
    pmf = pd.DataFrame({"a": [0.6], "b": [0.6]}, index=pd.date_range("2025-01-01", periods=1))
    resultado = e_poly(pmf, np.array([0.0, 1.0]), fl_power(1.0), "renormalizar")
    np.testing.assert_allclose(resultado.tolist(), [0.5])
