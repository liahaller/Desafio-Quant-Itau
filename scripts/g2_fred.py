"""G2 — Entrega física das 3 séries do FRED (CSV público, sem chave).

Baixa o CSV CRU do FRED (fredgraph.csv?id=<ID>) para T10YIE, DGS10 e DTB3 e
salva EXATAMENTE como o endpoint devolve em data/raw/ — sem renomear coluna,
sem reindexar, sem preencher feriado. Reporta linhas, primeira/última data,
como vem o valor ausente e quantos ausentes há.

NÃO trata nada. O FRED marca feriado com um caractere (tipicamente "."),
não com linha faltando — isso é reportado, não corrigido.

Uso:
    .venv/bin/python scripts/g2_fred.py
"""

import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_ROOT / "data" / "raw"

BASE = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}"
SERIES = ["T10YIE", "DGS10", "DTB3"]
TIMEOUT = 60


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    print("Serie | arquivo | URL | linhas | primeira->ultima | marca ausente | n ausentes")
    for sid in SERIES:
        url = BASE.format(sid=sid)
        r = requests.get(url, timeout=TIMEOUT)
        if not r.ok:
            print(f"{sid}: ERRO HTTP {r.status_code}")
            continue
        text = r.text
        fname = f"fred_{sid}.csv"
        (RAW_DIR / fname).write_text(text, encoding="utf-8")

        df = pd.read_csv(io.StringIO(text))
        col_date, col_val = df.columns[0], df.columns[1]
        n = len(df)
        first, last = df[col_date].iloc[0], df[col_date].iloc[-1]
        # o FRED devolve valores como texto; ausência costuma ser "."
        vals = df[col_val].astype(str).str.strip()
        # detecta o marcador de ausente: qualquer valor não numérico
        nonnum = vals[~vals.str.match(r"^-?\d+(\.\d+)?$")]
        markers = sorted(nonnum.unique().tolist())
        n_missing = int(len(nonnum))
        marker_repr = markers if markers else ["(nenhum)"]
        print(f"{sid} | {fname} | {url} | {n} | {first} -> {last} | "
              f"colunas={list(df.columns)} | marca_ausente={marker_repr} | ausentes={n_missing}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
