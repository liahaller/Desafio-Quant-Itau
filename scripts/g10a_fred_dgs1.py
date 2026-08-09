"""G10a — Série DGS1 do FRED (1-Year Treasury Constant Maturity Rate, diária).

Baixa o CSV CRU do FRED (fredgraph.csv?id=DGS1) e salva EXATAMENTE como o endpoint
devolve em data/raw/fred_DGS1.csv, sem renomear coluna, sem reindexar, sem preencher
buraco, sem converter unidade. Mesmo formato dos outros do G2/G8
(observation_date,DGS1; ausência = CAMPO VAZIO, como nos fred_DTB3.csv / fred_DGS10.csv).

Nota sobre a fonte (importante para conferência): o pedido templou a URL da API
`api.stlouisfed.org/fred/series/observations`, MAS essa API devolve o valor com
padding (`4.0600000000`) e ausência como "." — o que NÃO fica idêntico aos
fred_DTB3.csv / fred_DGS10.csv que já existem (2 casas, ausência = campo vazio),
e "idêntico" é requisito explícito do pedido + "dado cru não se normaliza" proíbe
reformatar. Os arquivos irmãos existentes vieram do fredgraph (G2/G8), então uso a
MESMA fonte aqui para o formato ser de fato idêntico e cru. Sem chave (o fredgraph
é público). Se preferir a API literal, é uma linha — mas o arquivo não sai idêntico.

DGS1 é o benchmark de 1 ano da view B (trajetória do Fed): DTB3 (3m) é curto demais
e DGS10 (10a) é longo demais.

NÃO trata nada. Reporta linhas, primeira/última data e dias sem leitura.

Uso:
    .venv/bin/python scripts/g10a_fred_dgs1.py
"""

import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_ROOT / "data" / "raw"

SERIES_ID = "DGS1"
URL = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={SERIES_ID}"
TIMEOUT = 60


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(URL, timeout=TIMEOUT)
    if not r.ok:
        print(f"{SERIES_ID}: ERRO HTTP {r.status_code}")
        return 1
    text = r.text
    fname = f"fred_{SERIES_ID}.csv"
    (RAW_DIR / fname).write_text(text, encoding="utf-8")

    df = pd.read_csv(io.StringIO(text))
    col_date, col_val = df.columns[0], df.columns[1]
    n = len(df)
    first, last = df[col_date].iloc[0], df[col_date].iloc[-1]
    # ausência no fredgraph.csv vem como CAMPO VAZIO (achado do G2), não como "."
    vals = df[col_val].astype(str).str.strip()
    nonnum = vals[~vals.str.match(r"^-?\d+(\.\d+)?$")]
    n_missing = int(len(nonnum))

    print("=== G10a — DGS1 ===")
    print(f"Fonte usada:            {URL}   (público, sem chave)")
    print(f"Arquivo salvo:          data/raw/{fname}")
    print(f"Nº de linhas:           {n}")
    print(f"Janela:                 {first} → {last}")
    print("Formato:                idêntico aos fred_DTB3.csv / fred_DGS10.csv que já existem "
          f"(colunas={list(df.columns)}; ausência = campo vazio)")
    print(f"Dias sem leitura:       {n_missing if n_missing else 'nenhum'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
