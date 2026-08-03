"""G1 — Abertura (Open) diária dos 9 ETFs da camada estrutural.

Baixa via yfinance o Open diário dos mesmos 9 tickers da Decisão 1 e o
ENTREGA como arquivo irmão do etf_prices_daily.parquet, no mesmo formato
longo, reindexado EXATAMENTE às mesmas datas do arquivo de close (mesma
janela, mesmo alinhamento). Reporta divergências de alinhamento e ausências.

Base do Open: auto_adjust=True (a MESMA base do close que já está no
etf_prices_daily.parquet). Escolha registrada só para consistência interna
(não misturar close ajustado com open cru); a decisão metodológica final é
do grupo/Felipe.

NÃO normaliza, NÃO interpola, NÃO converte fuso. Ausência sai como ausência.

Uso:
    .venv/bin/python scripts/g1_open_etfs.py
"""

import sys
from pathlib import Path

import pandas as pd
import yfinance as yf

REPO_ROOT = Path(__file__).resolve().parents[1]
CLOSE_PARQUET = REPO_ROOT / "data" / "etf_prices_daily.parquet"
OUT_PARQUET = REPO_ROOT / "data" / "etf_open_daily.parquet"

TICKERS = ["XLK", "XLU", "XLP", "XLF", "XLE", "XLV", "TIP", "TLT", "SPY"]


def download_open(tickers, start, end):
    """Baixa o Open diário (auto_adjust=True) e devolve DataFrame wide."""
    raw = yf.download(
        tickers,
        start=start,
        end=end,
        interval="1d",
        auto_adjust=True,
        progress=False,
        threads=False,
    )
    opens = raw["Open"][tickers]
    opens.index = pd.to_datetime(opens.index).tz_localize(None).normalize()
    return opens


def main():
    close = pd.read_parquet(CLOSE_PARQUET)
    ref_dates = pd.DatetimeIndex(sorted(close["data"].unique()))
    d0, d1 = ref_dates.min(), ref_dates.max()
    print(f"Referência (close): {d0.date()} -> {d1.date()} | {len(ref_dates)} datas x {len(TICKERS)} tickers")

    # baixa com folga de 1 dia no fim para garantir o último pregão
    opens = download_open(TICKERS, d0.strftime("%Y-%m-%d"),
                          (d1 + pd.Timedelta(days=1)).strftime("%Y-%m-%d"))

    # reindexa às datas EXATAS do arquivo de close (mesmo alinhamento)
    opens_aligned = opens.reindex(ref_dates)

    # relatório de ausências por ticker (datas de close sem Open)
    missing = {}
    for t in TICKERS:
        na = opens_aligned[t].isna()
        missing[t] = int(na.sum())
    total_missing = sum(missing.values())

    # datas que o yfinance trouxe FORA do grid de close (divergência de calendário)
    extra_dates = opens.index.difference(ref_dates)

    # monta formato longo (mantém ausências como NaN, sem dropar linha)
    long_df = opens_aligned.reset_index(names="data").melt(
        id_vars="data", var_name="ticker", value_name="preco_abertura"
    )
    long_df = long_df.sort_values(["data", "ticker"]).reset_index(drop=True)
    long_df.to_parquet(OUT_PARQUET, index=False)

    print("\n=== RESULTADO G1 ===")
    print(f"Arquivo salvo:        {OUT_PARQUET.relative_to(REPO_ROOT)}")
    print(f"Nº de linhas:         {len(long_df)}  (esperado 51129)")
    print(f"Tickers:              {', '.join(sorted(long_df['ticker'].unique()))}")
    print(f"Janela:               {long_df['data'].min().date()} -> {long_df['data'].max().date()}")
    print(f"Datas x tickers:      {long_df['data'].nunique()} x {long_df['ticker'].nunique()}")
    print(f"Alinhado ao close:    {'SIM' if len(extra_dates) == 0 else 'NAO'}"
          f"  (datas de Open fora do grid de close: {len(extra_dates)})")
    if len(extra_dates) > 0:
        print(f"  datas extras (amostra): {[d.date().isoformat() for d in extra_dates[:10]]}")
    print(f"Dias com Open ausente: {total_missing}")
    for t, n in missing.items():
        if n:
            dts = opens_aligned.index[opens_aligned[t].isna()]
            print(f"  {t}: {n} -> {[d.date().isoformat() for d in dts[:10]]}"
                  f"{' ...' if n > 10 else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
