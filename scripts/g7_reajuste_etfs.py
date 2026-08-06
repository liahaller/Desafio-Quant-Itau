"""G7 — Re-gera os DOIS parquets de ETF (abertura e fechamento) do MESMO pull.

Motivo (follow-up 3): `etf_prices_daily.parquet` (close, baixado 2026-07-09) e
`etf_open_daily.parquet` (open, baixado 2026-08-02) saíram de downloads em datas
diferentes. Como `auto_adjust=True` reescala TODA a história a cada novo
ex-dividendo, os dois arquivos ficaram em bases de ajuste diferentes. Assinatura:
a razão abertura/fechamento de TIP e TLT (os dois ETFs de distribuição MENSAL)
fica num degrau (~-1,15% e ~-0,41%) em vez do ruído intradiário (± 0,1%) dos
outros sete.

Conserto: um único `yf.download(..., auto_adjust=True)` e salvar Open e Close a
partir do MESMO objeto retornado — não existe janela entre pulls onde um dividendo
possa entrar em só um dos arquivos.

Fonte, universo e janela NÃO mudam (Decisão 1: yfinance, mesmos 9, período máximo
comum). Só a base de ajuste passa a ser compartilhada. Formato mantido: dois
arquivos irmãos em formato longo, como já estavam.

NÃO normaliza, NÃO interpola, NÃO converte fuso. Ausência sai como ausência.

Uso:
    .venv/bin/python scripts/g7_reajuste_etfs.py
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yfinance as yf

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "config" / "data_config.json"
CLOSE_PARQUET = REPO_ROOT / "data" / "etf_prices_daily.parquet"
OPEN_PARQUET = REPO_ROOT / "data" / "etf_open_daily.parquet"


def download_ohlc(tickers, start, end):
    """Baixa Open e Close diários (auto_adjust=True) de UM único yf.download.

    Devolve (open_wide, close_wide, chamada_str, timestamp_utc): os dois wide
    DataFrames vêm do MESMO objeto `raw`, garantindo base de ajuste idêntica.
    """
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    chamada = (
        f"yf.download({tickers}, start={start!r}, end={end!r}, "
        f"period={None if start else 'max'!r}, interval='1d', "
        "auto_adjust=True, progress=False, threads=False)"
    )
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
    open_wide = raw["Open"][tickers].copy()
    close_wide = raw["Close"][tickers].copy()
    for wide in (open_wide, close_wide):
        wide.index = pd.to_datetime(wide.index).tz_localize(None).normalize()
    return open_wide, close_wide, chamada, timestamp


def common_window(close_wide):
    """Janela comum aos 9 tickers no close (mesma regra do pipeline original)."""
    coverage = {}
    for ticker in close_wide.columns:
        series = close_wide[ticker].dropna()
        coverage[ticker] = (series.index.min(), series.index.max())
    common_start = max(first for first, _ in coverage.values())
    common_end = min(last for _, last in coverage.values())
    return common_start, common_end


def to_long(wide, value_name):
    """Wide -> longo [data, ticker, <value_name>], ordenado."""
    return (
        wide.rename_axis(index="data", columns="ticker")
        .reset_index()
        .melt(id_vars="data", var_name="ticker", value_name=value_name)
        .sort_values(["data", "ticker"])
        .reset_index(drop=True)
    )


def compare_close_to_old(new_close_wide):
    """Compara o novo close com o arquivo antigo nas datas em comum.

    Devolve dict ticker -> (max_abs_desloc_relativo, data_do_maior). Se um novo
    fator de ajuste entrou, o NÍVEL de fechamento de toda a história desloca.
    """
    if not CLOSE_PARQUET.exists():
        return None
    old_long = pd.read_parquet(CLOSE_PARQUET)
    old_wide = old_long.pivot(index="data", columns="ticker", values="preco_ajustado")
    old_wide.index = pd.to_datetime(old_wide.index).tz_localize(None).normalize()

    result = {}
    common_dates = new_close_wide.index.intersection(old_wide.index)
    for ticker in new_close_wide.columns:
        if ticker not in old_wide.columns:
            result[ticker] = None
            continue
        a = new_close_wide.loc[common_dates, ticker]
        b = old_wide.loc[common_dates, ticker]
        rel = (a / b - 1.0).dropna()
        if rel.empty:
            result[ticker] = (float("nan"), None)
            continue
        idx = rel.abs().idxmax()
        result[ticker] = (float(rel.loc[idx]), idx)
    return result


def main():
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    tickers = config["tickers"]

    print(f"Baixando Open+Close de {len(tickers)} tickers num único pull: {', '.join(tickers)}")
    open_wide, close_wide, chamada, timestamp = download_ohlc(
        tickers, config["start"], config["end"]
    )

    # comparação com o close antigo ANTES de sobrescrever
    close_diff = compare_close_to_old(close_wide)

    # janela comum (regra do pipeline: interseção dos 9 no close)
    c0, c1 = common_window(close_wide)
    aligned_close = close_wide.loc[c0:c1]
    aligned_open = open_wide.reindex(aligned_close.index)

    n_nan_close = int(aligned_close.isna().sum().sum())
    n_nan_open = int(aligned_open.isna().sum().sum())

    # razão abertura/fechamento por ticker (teste do G7)
    ratio = (aligned_open / aligned_close - 1.0)
    med_ratio = ratio.median()

    if n_nan_close > 0:
        print(f"\nERRO: {n_nan_close} NaN no close na janela comum — nada salvo.")
        return 1

    # salva os dois a partir do MESMO pull
    close_long = to_long(aligned_close, "preco_ajustado")
    open_long = to_long(aligned_open, "preco_abertura")
    close_long.to_parquet(CLOSE_PARQUET, index=False)
    open_long.to_parquet(OPEN_PARQUET, index=False)

    # ---- relatório no formato pedido ----
    print("\n=== G7 — BASE DE AJUSTE ===")
    print(f"Arquivos gerados:            {CLOSE_PARQUET.relative_to(REPO_ROOT)} + "
          f"{OPEN_PARQUET.relative_to(REPO_ROOT)}  (um pull só? SIM)")
    print(f"Data/hora do download:       {timestamp} (UTC)")
    print(f"Chamada usada:               {chamada}")
    print(f"Nº de linhas / tickers:      close {len(close_long)} / open {len(open_long)}"
          f"  |  {len(tickers)} tickers: {', '.join(tickers)}")
    print(f"Janela:                      {c0.date()} -> {c1.date()}  "
          f"({aligned_close.index.nunique()} datas)")
    print(f"NaN na janela (close/open):  {n_nan_close} / {n_nan_open}")
    print("Mediana de abertura/fechamento - 1, por ticker:")
    linha = "  " + "  ".join(f"{t} {med_ratio[t]*100:+.3f}%" for t in tickers)
    print(linha)
    fora = [t for t in tickers if abs(med_ratio[t]) > 0.001]
    print(f"  (esperado: todos dentro de ± 0,1%; TIP e TLT são o teste)")
    print(f"  Fora de ± 0,1%: {fora if fora else 'NENHUM'}")

    print("Mudou algum fechamento em relação ao arquivo antigo?  ", end="")
    if close_diff is None:
        print("N/A — arquivo antigo ausente.")
    else:
        mudou = {t: v for t, v in close_diff.items()
                 if v and v[0] == v[0] and abs(v[0]) > 1e-4}
        if not mudou:
            print("NÃO — nenhum ticker deslocou mais de 0,01% em nenhuma data comum.")
        else:
            print("SIM — deslocamento de nível (novo fator de ajuste desde o pull antigo):")
            for t in tickers:
                v = close_diff.get(t)
                if v and v[0] == v[0]:
                    flag = "  <-- deslocou" if abs(v[0]) > 1e-4 else ""
                    print(f"    {t}: max |Δ| {v[0]*100:+.3f}% em {v[1].date()}{flag}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
