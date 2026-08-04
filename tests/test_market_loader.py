"""Testes da leitura de ETFs e FRED (casos sintéticos).

O formato dos arquivos e os casos-limite (campo vazio no FRED, abertura e
fechamento no mesmo grid) vêm do que foi CONFERIDO no dado do Paulo
(`origin/Paulo` @ a9be92b), mas o dado aqui é sintético: o teste não pode
depender de arquivo de outro branch.
"""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from market_loader import load_etf_prices, load_fred

DATAS = pd.to_datetime(["2026-07-06", "2026-07-07", "2026-07-08"])


def escrever_parquet(caminho, coluna, valores):
    longo = pd.DataFrame(
        [(d, t, v) for d, linha in zip(DATAS, valores) for t, v in zip(["SPY", "TLT"], linha)],
        columns=["data", "ticker", coluna],
    )
    longo.sample(frac=1, random_state=0).to_parquet(caminho)  # fora de ordem de propósito
    return caminho


def test_etf_longo_vira_largo_ordenado(tmp_path):
    caminho = escrever_parquet(tmp_path / "close.parquet", "preco_ajustado",
                               [[100.0, 90.0], [101.0, 89.0], [102.0, 88.5]])
    largo = load_etf_prices(caminho)
    assert list(largo.columns) == ["SPY", "TLT"]
    assert largo.index.tolist() == list(DATAS)
    assert largo.loc[DATAS[2], "SPY"] == 102.0


def test_abertura_e_fechamento_no_mesmo_grid(tmp_path):
    """G1: os dois arquivos alinham data a data — é o que faz o retorno
    intradiário (abertura → fechamento do mesmo dia) existir."""
    fechamento = load_etf_prices(escrever_parquet(
        tmp_path / "close.parquet", "preco_ajustado",
        [[100.0, 90.0], [101.0, 89.0], [102.0, 88.5]]))
    abertura = load_etf_prices(escrever_parquet(
        tmp_path / "open.parquet", "preco_abertura",
        [[99.0, 90.5], [100.5, 89.5], [101.0, 88.0]]))
    assert fechamento.index.equals(abertura.index)
    assert list(fechamento.columns) == list(abertura.columns)
    intradiario = fechamento / abertura - 1
    assert intradiario.loc[DATAS[0], "SPY"] == pytest.approx(100.0 / 99.0 - 1)


def test_etf_rejeita_duas_colunas_de_valor(tmp_path):
    caminho = tmp_path / "duas.parquet"
    pd.DataFrame({"data": DATAS, "ticker": "SPY", "a": 1.0, "b": 2.0}).to_parquet(caminho)
    with pytest.raises(ValueError, match="coluna de valor"):
        load_etf_prices(caminho)


def test_fred_campo_vazio_vira_nan_e_nao_e_preenchido(tmp_path):
    # feriado (MLK) exatamente como o fredgraph.csv entrega: linha presente,
    # valor vazio depois da vírgula — não é "." nem linha faltando.
    caminho = tmp_path / "fred_T10YIE.csv"
    caminho.write_text(
        "observation_date,T10YIE\n"
        "2003-01-17,1.71\n"
        "2003-01-20,\n"
        "2003-01-21,1.70\n",
        encoding="utf-8",
    )
    serie = load_fred(caminho)
    assert serie.name == "T10YIE"
    assert len(serie) == 3 and serie.isna().sum() == 1
    assert serie.iloc[0] == 1.71 and serie.iloc[2] == 1.70
    assert pd.isna(serie.loc[pd.Timestamp("2003-01-20")])


def test_fred_mantem_unidade_do_arquivo(tmp_path):
    """Pontos percentuais, sem conversão silenciosa: 4.25 é 4,25%, não 0,0425.
    (A 2.2 pede fração decimal — a divisão é de quem chama.)"""
    caminho = tmp_path / "fred_DGS10.csv"
    caminho.write_text("observation_date,DGS10\n2026-07-08,4.25\n", encoding="utf-8")
    assert load_fred(caminho).iloc[0] == 4.25


def test_fred_marcador_desconhecido_falha_alto(tmp_path):
    """Se algum dia a fonte voltar a usar '.', o erro aparece na leitura em
    vez de virar coluna de texto silenciosamente."""
    caminho = tmp_path / "fred_DTB3.csv"
    caminho.write_text("observation_date,DTB3\n2026-07-07,4.10\n2026-07-08,.\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_fred(caminho)
