"""Pipeline de preços dos ETFs (Tarefa 1 — Paulo).

Baixa via yfinance o histórico diário de preço ajustado (splits e
dividendos incorporados) dos 9 ativos da Decisão 1 (fechada), valida as
séries e salva uma tabela única em formato longo (parquet).

Uso:
    python src/data_pipeline/download_prices.py

Parâmetros (tickers, período, caminho de saída) em config/data_config.json.
`start`/`end` nulos = histórico máximo disponível.
"""

import json
import sys
import time
from pathlib import Path

import pandas as pd
import yfinance as yf

# Raiz do repositório (este arquivo fica em src/data_pipeline/)
REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / "config" / "data_config.json"


def load_config(config_path: Path = CONFIG_PATH) -> dict:
    """Lê o arquivo de configuração do pipeline de dados."""
    with open(config_path, encoding="utf-8") as f:
        return json.load(f)


def download_prices(tickers: list[str], start: str | None, end: str | None) -> pd.DataFrame:
    """Baixa preços ajustados diários via yfinance.

    Com auto_adjust=True a coluna Close já vem ajustada por splits e
    dividendos. Retorna DataFrame wide: índice = datas, colunas = tickers.
    """
    raw = yf.download(
        tickers,
        start=start,
        end=end,
        period=None if start else "max",
        interval="1d",
        auto_adjust=True,
        progress=False,
        threads=False,
    )
    prices = raw["Close"][tickers]
    prices.index = pd.to_datetime(prices.index).tz_localize(None).normalize()

    # Retry individual para tickers que voltaram vazios (falha transitória
    # do yfinance, ex. "database is locked" no cache local).
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        empty = [t for t in tickers if prices[t].dropna().empty]
        if not empty:
            break
        print(f"Retry {attempt}/{max_retries} para tickers vazios: {', '.join(empty)}")
        time.sleep(2 * attempt)
        for ticker in empty:
            retry_raw = yf.download(
                ticker,
                start=start,
                end=end,
                period=None if start else "max",
                interval="1d",
                auto_adjust=True,
                progress=False,
                threads=False,
            )
            if not retry_raw.empty:
                series = retry_raw["Close"][ticker]
                series.index = pd.to_datetime(series.index).tz_localize(None).normalize()
                prices = prices.reindex(prices.index.union(series.index))
                prices[ticker] = series

    still_empty = [t for t in tickers if prices[t].dropna().empty]
    if still_empty:
        raise RuntimeError(
            f"Download falhou após {max_retries} tentativas para: {', '.join(still_empty)}"
        )
    return prices


def validate_prices(prices: pd.DataFrame) -> pd.DataFrame:
    """Valida as séries e reporta inconsistências no console.

    Checagens:
    1. Cobertura por ticker (primeira/última data, nº de observações).
    2. Buracos: datas em que outros tickers negociaram mas o ticker não,
       dentro da janela de cobertura do próprio ticker.
    3. Alinhamento: se todos os tickers têm exatamente as mesmas datas
       dentro da janela comum [maior primeira data, menor última data].
    4. NaN dentro da janela de cobertura de cada ticker.

    Retorna o DataFrame recortado à janela comum (datas alinhadas entre
    os 9 tickers), pronto para salvar.
    """
    print("=== Cobertura por ticker ===")
    coverage = {}
    for ticker in prices.columns:
        series = prices[ticker].dropna()
        coverage[ticker] = (series.index.min(), series.index.max())
        print(
            f"{ticker}: {series.index.min().date()} → {series.index.max().date()}"
            f" ({len(series)} observações)"
        )

    print("\n=== Buracos por ticker (dentro da própria cobertura) ===")
    any_gap = False
    for ticker in prices.columns:
        first, last = coverage[ticker]
        window = prices.loc[first:last, ticker]
        gaps = window[window.isna()]
        if len(gaps) > 0:
            any_gap = True
            print(f"{ticker}: {len(gaps)} data(s) sem preço enquanto outros negociaram:")
            for date in gaps.index:
                print(f"  - {date.date()}")
        else:
            print(f"{ticker}: sem buracos.")
    if not any_gap:
        print("Nenhum buraco encontrado em nenhum ticker.")

    common_start = max(first for first, _ in coverage.values())
    common_end = min(last for _, last in coverage.values())
    print(f"\n=== Janela comum (datas alinhadas entre os 9 tickers) ===")
    print(f"{common_start.date()} → {common_end.date()}")
    starts = {t: c[0] for t, c in coverage.items()}
    late_starters = {t: d for t, d in starts.items() if d > min(starts.values())}
    if late_starters:
        print("Tickers com histórico mais curto (início depois dos demais):")
        for ticker, date in sorted(late_starters.items(), key=lambda kv: kv[1]):
            print(f"  - {ticker}: começa em {date.date()}")

    aligned = prices.loc[common_start:common_end]
    n_nan = int(aligned.isna().sum().sum())
    if n_nan > 0:
        print(f"\nATENÇÃO: {n_nan} NaN dentro da janela comum:")
        print(aligned.isna().sum()[aligned.isna().sum() > 0])
    else:
        print("\nSem NaN na janela comum — datas 100% alinhadas entre os 9 tickers.")

    return aligned


def build_long_table(prices: pd.DataFrame) -> pd.DataFrame:
    """Converte a tabela wide em formato longo: [data, ticker, preco_ajustado]."""
    long_table = (
        prices.rename_axis(index="data", columns="ticker")
        .stack()
        .rename("preco_ajustado")
        .reset_index()
        .sort_values(["data", "ticker"])
        .reset_index(drop=True)
    )
    return long_table


def main() -> int:
    config = load_config()
    tickers = config["tickers"]
    output_path = REPO_ROOT / config["output_path"]

    print(f"Baixando {len(tickers)} tickers via yfinance: {', '.join(tickers)}")
    prices = download_prices(tickers, config["start"], config["end"])
    aligned = validate_prices(prices)

    if aligned.empty:
        print("\nERRO: janela comum vazia — arquivo NÃO salvo.")
        return 1

    if aligned.isna().any().any():
        print("\nERRO: NaN remanescente na janela comum — arquivo NÃO salvo.")
        return 1

    long_table = build_long_table(aligned)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    long_table.to_parquet(output_path, index=False)
    print(f"\nSalvo: {output_path}")
    print(f"Linhas: {len(long_table)} | Colunas: {list(long_table.columns)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
