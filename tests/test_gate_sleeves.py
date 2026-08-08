"""Testes das quatro medidas do gate de sleeves (casos sintéticos).

Cada uma tem resultado conhecido de cabeça — é o piso do CLAUDE.md §5 para
função matemática nova. O que interessa aqui é o gate REPRODUZIR a morte
conhecida: sinal do tamanho do tick dá razão ~1, e μ contra a premissa reprova.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gate_sleeves import (bate_premissa, corr_comum, demeanar_expansivo,  # noqa: E402
                          eventos_diarios, massa_de_cauda, razao_dispersao)


def test_razao_dispersao_sinal_do_tamanho_do_tick():
    """O caso que matou a sleeve do FOMC: sinal da ordem do tick -> razão ~1."""
    assert razao_dispersao([0.01, -0.01, 0.01], 0.01) == pytest.approx(1.0)
    assert razao_dispersao([1.0, -1.0, 1.0], 0.01) == pytest.approx(100.0)


def test_razao_dispersao_sem_sinal_ou_sem_tick():
    assert np.isnan(razao_dispersao([], 0.01))
    assert np.isnan(razao_dispersao([1.0, 2.0], 0.0))


def test_massa_de_cauda_renormaliza_e_soma_as_pontas():
    # PMF que não soma 1 (é o caso do poly): 0,2 + 0,2 sobre um total de 1,0.
    assert massa_de_cauda([0.2, 0.6, 0.2]) == pytest.approx(0.4)
    assert massa_de_cauda([0.1, 0.3, 0.1]) == pytest.approx(0.4)  # soma 0,5
    assert massa_de_cauda([0.0, 1.0, 0.0]) == pytest.approx(0.0)


def test_massa_de_cauda_precisa_de_tres_baldes():
    """Com 2 baldes tudo é ponta e a medida não distingue nada."""
    assert np.isnan(massa_de_cauda([0.5, 0.5]))
    assert np.isnan(massa_de_cauda([0.0, 0.0, 0.0]))


def test_corr_comum_serie_identica_da_um():
    datas = pd.date_range("2026-01-01", periods=10)
    a = pd.Series(np.arange(10.0), index=datas)
    assert corr_comum(a, a) == pytest.approx(1.0)
    assert corr_comum(a, -a) == pytest.approx(-1.0)
    # Transformação afim não muda ρ — é o que autoriza usar o NÍVEL da
    # divergência no lugar do Q da view na coluna do G3.
    assert corr_comum(a, 3.0 * a + 7.0) == pytest.approx(1.0)


def test_corr_comum_pouco_dado_ou_constante():
    datas = pd.date_range("2026-01-01", periods=10)
    assert np.isnan(corr_comum([1.0, 2.0], [1.0, 2.0]))
    assert np.isnan(corr_comum(pd.Series(np.ones(10), index=datas),
                               pd.Series(np.arange(10.0), index=datas)))


def test_bate_premissa_reprova_o_sinal_invertido():
    """Reproduz a morte da sleeve de CPI da D16: TLT anda mais que TIP."""
    assets = ("TIP", "TLT")
    mu_certo = np.array([1e-4, -1e-4])
    mu_invertido = np.array([0.21e-4, 1.31e-4])   # os números medidos na D16
    declarado = {"TIP": +1, "TLT": -1}
    assert bate_premissa(mu_certo, assets, declarado)[0] is True
    ok, detalhe = bate_premissa(mu_invertido, assets, declarado)
    assert ok is False
    assert "TLT" in detalhe and "❌" in detalhe


def test_bate_premissa_sem_mu():
    assert bate_premissa(None, ("SPY",), {"SPY": +1}) == (False, "μ ausente")


def test_demeanar_expansivo_nao_olha_o_futuro():
    datas = pd.date_range("2026-01-01", periods=4)
    s = pd.Series([1.0, 3.0, 5.0, 7.0], index=datas)
    saida = demeanar_expansivo(s)
    # O 1º ponto some (não há passado); depois: 3−1, 5−2, 7−3.
    assert list(saida.index) == list(datas[1:])
    assert saida.to_numpy() == pytest.approx([2.0, 3.0, 4.0])


def test_eventos_diarios_descarta_sinal_zero():
    datas = pd.date_range("2026-01-01", periods=3)
    eventos = eventos_diarios(pd.Series([2.0, 0.0, -5.0], index=datas))
    assert [d for d, _ in eventos] == [datas[0], datas[2]]
    assert [s for _, s in eventos] == [1.0, -1.0]
