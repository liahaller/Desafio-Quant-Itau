"""Matriz de relação tridimensional ações × mercados do Polymarket × tempo.

Base inspirada no relatório NEXUS (Desafio Quant AI 2025): lá, a
dependência entre ações era medida por distance correlation (dcor),
métrica que captura relações lineares e não-lineares e que só é nula
quando as variáveis são estatisticamente independentes. Aqui a mesma
métrica é aplicada entre séries de retorno dos ativos e séries de
variação de probabilidade dos mercados do Polymarket ligados ao cenário
macroeconômico, recalculada em janelas móveis — o eixo do tempo é a
terceira dimensão da matriz.

Uso na camada tática: identificar, a cada data, quais ações respondem
mais a cada previsão macro, para selecionar os ativos elegíveis dos
trades curtos (PEAD, event-driven, velocidade).

Este módulo não acessa dados externos: recebe DataFrames já preparados
pelo pipeline do Paulo (Decisão 2 em aberto define a fonte).

TODO(DECISAO-10): métrica (dcor), tamanho da janela e série usada para o
Polymarket (variação de probabilidade vs. nível) precisam ser
confirmados com o grupo — ver Decisoes_pendentes.md.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd


def distance_correlation(x: np.ndarray, y: np.ndarray) -> float:
    """Distance correlation entre duas séries unidimensionais.

    Implementa a Fórmula 1 do relatório NEXUS:
        dcor(x, y) = dcov(x, y) / sqrt(dcov(x, x) * dcov(y, y))

    Resultado em [0, 1]; 0 só quando as variáveis são estatisticamente
    independentes. Se alguma série for constante (variância de distância
    nula), retorna 0.0 — não há dependência mensurável.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.shape != y.shape or x.ndim != 1:
        raise ValueError("x e y devem ser vetores 1D do mesmo tamanho")
    if np.isnan(x).any() or np.isnan(y).any():
        return float("nan")

    # matrizes de distância duplamente centradas
    a = np.abs(x[:, None] - x[None, :])
    b = np.abs(y[:, None] - y[None, :])
    A = a - a.mean(axis=0)[None, :] - a.mean(axis=1)[:, None] + a.mean()
    B = b - b.mean(axis=0)[None, :] - b.mean(axis=1)[:, None] + b.mean()

    dcov2_xy = (A * B).mean()
    dcov2_xx = (A * A).mean()
    dcov2_yy = (B * B).mean()
    if dcov2_xx <= 0.0 or dcov2_yy <= 0.0:
        return 0.0
    return float(np.sqrt(max(dcov2_xy, 0.0) / np.sqrt(dcov2_xx * dcov2_yy)))


@dataclass
class MatrizRelacao3D:
    """Matriz ações × mercados × tempo.

    `valores[t, i, j]` = dependência entre o ativo `ativos[i]` e o
    mercado `mercados[j]`, medida na janela que termina em `datas[t]`.
    """

    valores: np.ndarray  # shape (n_janelas, n_ativos, n_mercados)
    datas: list
    ativos: list
    mercados: list

    def consultar(self, data, ativo: str, mercado: str) -> float:
        """Devolve a relação de um par ativo×mercado na janela que
        termina em `data`."""
        t = self.datas.index(data)
        i = self.ativos.index(ativo)
        j = self.mercados.index(mercado)
        return float(self.valores[t, i, j])

    def fatia_em(self, data) -> pd.DataFrame:
        """Matriz 2D (ativos × mercados) da janela que termina em `data`."""
        t = self.datas.index(data)
        return pd.DataFrame(
            self.valores[t], index=self.ativos, columns=self.mercados
        )


def calcular_matriz_relacao(
    retornos_ativos: pd.DataFrame,
    series_polymarket: pd.DataFrame,
    janela: int,
    passo: int = 1,
) -> MatrizRelacao3D:
    """Constrói a matriz de relação 3D por janelas móveis.

    Parâmetros
    ----------
    retornos_ativos : DataFrame (índice = datas, colunas = tickers)
        Retornos dos ativos, vindos do pipeline do Paulo.
    series_polymarket : DataFrame (índice = datas, colunas = mercados)
        Séries dos mercados do Polymarket ligados ao cenário macro.
        TODO(DECISAO-10): variação de probabilidade ou nível — a definir.
    janela : int
        Número de períodos de cada janela móvel. Sem valor padrão de
        propósito: o tamanho é parâmetro do modelo e vem de decisão
        registrada (Decisão 10), não de default no código.
    passo : int
        Deslocamento entre janelas consecutivas (1 = recalcula a cada
        período).

    As duas séries são alinhadas pela interseção das datas. Janelas que
    contenham NaN em algum par produzem NaN naquela célula.
    """
    if janela < 2:
        raise ValueError("janela deve ter pelo menos 2 períodos")

    datas_comuns = retornos_ativos.index.intersection(series_polymarket.index)
    if len(datas_comuns) < janela:
        raise ValueError(
            "menos períodos em comum entre as séries do que o tamanho da janela"
        )
    r = retornos_ativos.loc[datas_comuns]
    p = series_polymarket.loc[datas_comuns]

    ativos = list(r.columns)
    mercados = list(p.columns)
    fins_de_janela = range(janela - 1, len(datas_comuns), passo)

    valores = np.full((len(fins_de_janela), len(ativos), len(mercados)), np.nan)
    datas = []
    for t, fim in enumerate(fins_de_janela):
        inicio = fim - janela + 1
        datas.append(datas_comuns[fim])
        for i, ativo in enumerate(ativos):
            x = r[ativo].iloc[inicio : fim + 1].to_numpy()
            for j, mercado in enumerate(mercados):
                y = p[mercado].iloc[inicio : fim + 1].to_numpy()
                valores[t, i, j] = distance_correlation(x, y)

    return MatrizRelacao3D(
        valores=valores, datas=datas, ativos=ativos, mercados=mercados
    )
