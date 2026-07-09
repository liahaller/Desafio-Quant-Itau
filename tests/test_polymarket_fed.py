"""Testes de validação do dataset de probabilidades do Polymarket (Fed/FOMC).

Valida o arquivo gerado por src/data_pipeline/download_polymarket_fed.py.

Rodar: pytest tests/test_polymarket_fed.py
"""

from pathlib import Path

import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = REPO_ROOT / "data" / "polymarket_fed_probabilities.parquet"

# Cobertura real observada na descoberta (Etapa 1, 2026-07-08):
# evento mais antigo com dados começa em 2023-12-07.
EXPECTED_MAX_START = pd.Timestamp("2023-12-31")
EXPECTED_MIN_END = pd.Timestamp("2026-06-01")


@pytest.fixture(scope="module")
def dataset() -> pd.DataFrame:
    assert DATASET_PATH.exists(), (
        f"Arquivo não encontrado: {DATASET_PATH} — rodar o pipeline antes."
    )
    return pd.read_parquet(DATASET_PATH)


def test_columns(dataset):
    """A tabela longa tem exatamente as colunas do formato acordado."""
    assert list(dataset.columns) == ["data", "mercado", "probabilidade", "evento_id"]


def test_no_nan(dataset):
    """Sem NaN em nenhuma coluna."""
    assert not dataset.isna().any().any()


def test_probabilities_in_unit_interval(dataset):
    """Nenhuma probabilidade fora de [0, 1]."""
    assert dataset["probabilidade"].between(0, 1).all()


def test_date_coverage(dataset):
    """Cobertura conforme observado na descoberta (início dez/2023)."""
    dates = pd.to_datetime(dataset["data"])
    assert dates.min() <= EXPECTED_MAX_START
    assert dates.max() >= EXPECTED_MIN_END


@pytest.mark.xfail(
    reason=(
        "Overlap é intrínseco aos mercados do Fed no Polymarket: mercados de "
        "reuniões diferentes do FOMC negociam simultaneamente (82 de 82 pares "
        "consecutivos com overlap em 2026-07-08). A regra de encadeamento/"
        "recorte é decisão metodológica em aberto — ver Decisoes_pendentes.md."
    ),
    strict=True,
)
def test_no_overlap_between_consecutive_events(dataset):
    """Sem overlap de datas entre eventos (reuniões FOMC) consecutivos."""
    spans = dataset.groupby("evento_id")["data"].agg(["min", "max"]).sort_values("min")
    prev_max = None
    for _, row in spans.iterrows():
        if prev_max is not None:
            assert row["min"] >= prev_max, "overlap entre eventos consecutivos"
        prev_max = row["max"] if prev_max is None else max(prev_max, row["max"])
