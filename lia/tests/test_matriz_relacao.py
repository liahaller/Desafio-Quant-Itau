"""Testes da matriz de relação 3D (ações × mercados Polymarket × tempo).

Casos sintéticos com resultado conhecido para a distance correlation:
- dcor(x, x) = 1 (dependência perfeita);
- dcor(x, a + b·x) = 1 para b ≠ 0 (invariância a transformação afim);
- dcor(x, constante) = 0 (sem dependência mensurável);
- dcor(x, x²) > 0 em domínio simétrico (captura relação não-linear que a
  correlação de Pearson zeraria).
"""

import numpy as np
import pandas as pd
import pytest

from lia.matriz_relacao import (
    MatrizRelacao3D,
    calcular_matriz_relacao,
    distance_correlation,
)


def test_dcor_identidade_e_um():
    x = np.array([1.0, 2.0, 4.0, 8.0, 16.0])
    assert distance_correlation(x, x) == pytest.approx(1.0)


def test_dcor_transformacao_afim_e_um():
    x = np.array([0.5, 1.0, -2.0, 3.0, 0.0])
    y = 3.0 * x - 7.0
    assert distance_correlation(x, y) == pytest.approx(1.0)
    y_negativo = -2.0 * x + 1.0
    assert distance_correlation(x, y_negativo) == pytest.approx(1.0)


def test_dcor_serie_constante_e_zero():
    x = np.array([1.0, 2.0, 3.0, 4.0])
    y = np.full(4, 5.0)
    assert distance_correlation(x, y) == 0.0


def test_dcor_captura_relacao_nao_linear():
    # y = x² em domínio simétrico: Pearson ≈ 0, mas dcor > 0
    x = np.linspace(-1.0, 1.0, 21)
    y = x**2
    pearson = np.corrcoef(x, y)[0, 1]
    assert abs(pearson) == pytest.approx(0.0, abs=1e-10)
    assert distance_correlation(x, y) > 0.4


def test_dcor_com_nan_devolve_nan():
    x = np.array([1.0, np.nan, 3.0])
    y = np.array([1.0, 2.0, 3.0])
    assert np.isnan(distance_correlation(x, y))


def test_matriz_3d_dimensoes_e_consulta():
    datas = pd.date_range("2026-01-01", periods=10, freq="D")
    x = np.linspace(-1.0, 1.0, 10)
    retornos = pd.DataFrame(
        {"XLK": x, "TLT": -2.0 * x + 1.0}, index=datas
    )
    polymarket = pd.DataFrame({"corte_fed": x}, index=datas)

    matriz = calcular_matriz_relacao(retornos, polymarket, janela=5, passo=1)

    assert isinstance(matriz, MatrizRelacao3D)
    # 10 períodos, janela 5, passo 1 → 6 janelas
    assert matriz.valores.shape == (6, 2, 1)
    assert matriz.ativos == ["XLK", "TLT"]
    assert matriz.mercados == ["corte_fed"]
    # XLK é o próprio sinal e TLT é transformação afim → dcor = 1 em toda janela
    ultima_data = matriz.datas[-1]
    assert matriz.consultar(ultima_data, "XLK", "corte_fed") == pytest.approx(1.0)
    assert matriz.consultar(ultima_data, "TLT", "corte_fed") == pytest.approx(1.0)
    fatia = matriz.fatia_em(ultima_data)
    assert fatia.loc["XLK", "corte_fed"] == pytest.approx(1.0)


def test_matriz_3d_alinha_datas_e_valida_janela():
    datas_a = pd.date_range("2026-01-01", periods=8, freq="D")
    datas_b = pd.date_range("2026-01-03", periods=8, freq="D")  # interseção = 6 dias
    retornos = pd.DataFrame({"SPY": np.arange(8.0)}, index=datas_a)
    polymarket = pd.DataFrame({"eleicao": np.arange(8.0)}, index=datas_b)

    matriz = calcular_matriz_relacao(retornos, polymarket, janela=3, passo=1)
    assert matriz.valores.shape == (4, 1, 1)  # 6 datas comuns, janela 3 → 4 janelas

    with pytest.raises(ValueError):
        calcular_matriz_relacao(retornos, polymarket, janela=7)  # > datas comuns
    with pytest.raises(ValueError):
        calcular_matriz_relacao(retornos, polymarket, janela=1)  # janela mínima
