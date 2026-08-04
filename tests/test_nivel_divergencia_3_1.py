"""Teste mínimo do sinal de nível da 3.1 (`scripts/nivel_divergencia_3_1.py`)."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from nivel_divergencia_3_1 import spread_defasado, z  # noqa: E402


def test_z_padroniza():
    s = pd.Series([1.0, 2.0, 3.0, 4.0])
    out = z(s)
    assert abs(float(out.mean())) < 1e-12
    assert abs(float(out.std()) - 1.0) < 1e-12


def test_spread_usa_leitura_estritamente_anterior():
    """Regra de lookahead da 3.1: a leitura do próprio dia D não pode entrar —
    o H.15 publica a taxa de D depois do fechamento de D."""
    idx = pd.to_datetime(["2025-01-02", "2025-01-03", "2025-01-06"])
    dgs10 = pd.Series([4.0, 4.0, 99.0], index=idx)   # armadilha no dia 06
    dtb3 = pd.Series([3.0, 3.2, 3.0], index=idx)
    out = spread_defasado(dgs10, dtb3, pd.DatetimeIndex(["2025-01-06"]))
    assert abs(float(out.iloc[0]) - 0.8) < 1e-12  # usou 03/01, não o 99 do dia 06


def test_sem_leitura_anterior_da_nan():
    idx = pd.to_datetime(["2025-01-02"])
    out = spread_defasado(pd.Series([4.0], index=idx), pd.Series([3.0], index=idx),
                          pd.DatetimeIndex(["2025-01-02"]))
    assert np.isnan(float(out.iloc[0]))
