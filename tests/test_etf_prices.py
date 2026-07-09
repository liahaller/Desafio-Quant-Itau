"""Testes de validação do dataset de preços dos ETFs (Tarefa 1 — Paulo).

Valida o arquivo gerado por src/data_pipeline/download_prices.py:
sem NaN, datas alinhadas entre todos os tickers e intervalo de datas
conforme esperado (janela comum começa na estreia do TIP, 2003-12-05).

Rodar: pytest tests/test_etf_prices.py
"""

import json
from pathlib import Path

import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "config" / "data_config.json"

# Início esperado da janela comum: primeira data do TIP (ticker mais novo),
# observada no download de 2026-07-08.
EXPECTED_START = pd.Timestamp("2003-12-05")
# O dataset deve cobrir pelo menos até esta data (cresce a cada re-download).
EXPECTED_MIN_END = pd.Timestamp("2026-07-01")


@pytest.fixture(scope="module")
def config() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def dataset(config) -> pd.DataFrame:
    path = REPO_ROOT / config["output_path"]
    assert path.exists(), f"Arquivo não encontrado: {path} — rodar o pipeline antes."
    return pd.read_parquet(path)


def test_columns(dataset):
    """A tabela longa tem exatamente as colunas do formato acordado."""
    assert list(dataset.columns) == ["data", "ticker", "preco_ajustado"]


def test_no_nan(dataset):
    """Nenhum ticker com NaN em nenhuma coluna."""
    assert not dataset.isna().any().any()


def test_all_tickers_present(dataset, config):
    """Todos os 9 tickers da Decisão 1 estão no arquivo, sem extras."""
    assert set(dataset["ticker"].unique()) == set(config["tickers"])


def test_dates_aligned_across_tickers(dataset, config):
    """Toda data tem preço para todos os tickers (datas 100% alinhadas)."""
    counts = dataset.groupby("data")["ticker"].nunique()
    assert (counts == len(config["tickers"])).all(), (
        f"Datas com tickers faltando: {counts[counts < len(config['tickers'])].index.tolist()}"
    )


def test_date_range(dataset):
    """Intervalo de datas conforme esperado (janela comum dos 9 tickers)."""
    dates = pd.to_datetime(dataset["data"])
    assert dates.min() == EXPECTED_START
    assert dates.max() >= EXPECTED_MIN_END


def test_prices_positive(dataset):
    """Preços ajustados estritamente positivos."""
    assert (dataset["preco_ajustado"] > 0).all()
