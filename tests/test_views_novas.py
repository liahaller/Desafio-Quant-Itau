"""Testes do wiring das views novas no montador (casos sintéticos).

Piso do CLAUDE.md §5 para a matemática nova desta rodada, que é pouca de
propósito: a conta das duas views mora em `src/` e já é testada lá. O que
entrou de novo é (a) a escala de PERCENTIL da incerteza, que a 15c deixa em
aberto, e (b) a base do M3 ser a taxa do fim de 2024, não a de hoje.
"""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from backtest_v1 import percentil_expansivo  # noqa: E402
from view_B_trajetoria_propria import rates_from_cut_buckets  # noqa: E402


def test_percentil_expansivo_conhecido_de_cabeca():
    """Fração dos passados ≤ valor. Nada de interpolação escondida."""
    assert percentil_expansivo(0.5, [0.1, 0.2, 0.9, 1.0]) == pytest.approx(0.5)
    assert percentil_expansivo(0.0, [0.1, 0.2]) == pytest.approx(0.0)
    assert percentil_expansivo(2.0, [0.1, 0.2]) == pytest.approx(1.0)


def test_percentil_expansivo_sem_passado_e_NaN_nunca_meio():
    """Amostra vazia -> NaN. 0,5 inventado seria a view rodando sem histórico."""
    assert np.isnan(percentil_expansivo(0.5, []))


def test_base_do_M3_e_a_taxa_do_inicio_do_ano():
    """O M3 conta cortes DENTRO de 2025 — a base é o fim de 2024.

    Com 2 cortes já entregues no ano, usar a taxa de hoje (3,90%) em vez da de
    fim de 2024 (4,40%) desloca a grade inteira em 50 bps, e a "surpresa" da
    view vira prêmio de prazo com nome errado.
    """
    grade = rates_from_cut_buckets(440.0, [0, 1, 2])
    assert np.allclose(grade, [440.0, 415.0, 390.0])
    # a leitura errada, para o teste dizer o que está sendo evitado
    assert not np.allclose(rates_from_cut_buckets(390.0, [0, 1, 2]), grade)
