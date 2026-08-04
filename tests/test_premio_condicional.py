"""Teste mínimo da medida de incerteza de `scripts/premio_condicional.py`."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from premio_condicional import diferenca_de_medias, entropia_normalizada  # noqa: E402


def test_uniforme_da_entropia_um():
    assert entropia_normalizada([0.25, 0.25, 0.25, 0.25]) == 1.0


def test_concentrada_da_entropia_zero():
    """Toda a massa num balde -> 0 (os zeros não contam como balde vivo)."""
    assert entropia_normalizada([1.0, 0.0, 0.0]) != entropia_normalizada([0.5, 0.5, 0.0])
    assert entropia_normalizada([0.9, 0.05, 0.05]) < entropia_normalizada([0.4, 0.3, 0.3])


def test_invariante_a_renormalizacao():
    """PMF que soma 1,2 dá a mesma incerteza da mesma PMF normalizada —
    é o que torna a medida independente da decisão 6.1."""
    crua = [0.6, 0.3, 0.3]
    normalizada = [v / 1.2 for v in crua]
    assert abs(entropia_normalizada(crua) - entropia_normalizada(normalizada)) < 1e-12


def test_comparavel_entre_grades_de_tamanhos_diferentes():
    """Uniforme de 3 baldes e uniforme de 9 baldes dão o mesmo 1,0 — a grade
    do CPI muda de tamanho ao longo do histórico."""
    assert abs(entropia_normalizada([1 / 3] * 3)
               - entropia_normalizada([1 / 9] * 9)) < 1e-12


def test_bucket_sem_leitura_nao_conta():
    """NaN sai da conta em vez de virar zero (decisão 6.1 é de quem consome)."""
    assert entropia_normalizada([0.5, 0.5, np.nan]) == 1.0


def test_menos_de_dois_baldes_vivos_da_nan():
    assert np.isnan(entropia_normalizada([1.0]))
    assert np.isnan(entropia_normalizada([np.nan, np.nan]))


def test_diferenca_de_medias_recupera_deslocamento():
    rng = np.random.default_rng(0)
    a = pd.Series(rng.normal(loc=1.0, scale=0.1, size=200))
    b = pd.Series(rng.normal(loc=0.0, scale=0.1, size=200))
    dif, t = diferenca_de_medias(a, b)
    assert abs(dif - 1.0) < 0.05
    assert t > 10
