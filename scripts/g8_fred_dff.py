"""G8 — Entrega física da série DFF do FRED (CSV público, sem chave).

Baixa o CSV CRU do FRED (fredgraph.csv?id=DFF) — a Effective Federal Funds
Rate — e salva EXATAMENTE como o endpoint devolve em data/raw/fred_DFF.csv,
sem renomear coluna, sem reindexar, sem preencher buraco, sem converter
unidade. Mesmo formato dos outros três do G2 (observation_date,DFF).

DFF é o outro lado da subtracao e_ff_bps = DTB3 - DFF (view 2.3 do Felipe).

NAO trata nada. Reporta linhas, primeira/ultima data e campos vazios.

Uso:
    .venv/bin/python scripts/g8_fred_dff.py
"""

import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_ROOT / "data" / "raw"

URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DFF"
TIMEOUT = 60


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(URL, timeout=TIMEOUT)
    if not r.ok:
        print(f"DFF: ERRO HTTP {r.status_code}")
        return 1
    text = r.text
    fname = "fred_DFF.csv"
    (RAW_DIR / fname).write_text(text, encoding="utf-8")

    df = pd.read_csv(io.StringIO(text))
    col_date, col_val = df.columns[0], df.columns[1]
    n = len(df)
    first, last = df[col_date].iloc[0], df[col_date].iloc[-1]
    # ausencia no fredgraph.csv vem como CAMPO VAZIO (achado do G2), nao como "."
    vals = df[col_val].astype(str).str.strip()
    nonnum = vals[~vals.str.match(r"^-?\d+(\.\d+)?$")]
    markers = sorted(nonnum.unique().tolist())
    n_missing = int(len(nonnum))
    marker_repr = markers if markers else ["(nenhum)"]

    print("=== G8 — DFF ===")
    print(f"arquivo:        data/raw/{fname}")
    print(f"colunas:        {list(df.columns)}")
    print(f"linhas:         {n}")
    print(f"primeira data:  {first}")
    print(f"última data:    {last}")
    print(f"marca ausente:  {marker_repr}")
    print(f"campos vazios:  {n_missing}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
