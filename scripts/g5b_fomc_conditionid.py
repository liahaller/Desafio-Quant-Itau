"""G5b — Chave de junção no parquet do FOMC: acrescenta conditionId + slug.

Pedido da Lia (PEDIDO_Paulo_G5_fomc): o `polymarket_fed_reunioes.parquet` tinha
só [data, mercado, probabilidade, volume, evento_id], onde `mercado` é o TÍTULO
da pergunta — não há coluna que case com a saída do G5 (que identifica mercado
por `conditionId` e por slug). Sem chave, os dois arquivos não se juntam.

Este script acrescenta DUAS colunas ao parquet, sem tocar nas linhas nem nas
colunas existentes (operação puramente aditiva):
  - conditionId — id canônico do mercado no Polymarket (chave robusta de junção);
  - slug        — slug do mercado (a chave alternativa que a Lia também aceita).

Como resolve: para cada `evento_id` do parquet (18 reuniões), chama a Gamma
`/events?id=<id>` uma vez e casa `question` → (conditionId, slug) dentro do evento
(question é única por evento). Não re-baixa preço, não re-descobre eventos: usa os
evento_id que já estão no parquet, então NÃO há risco de o universo mudar.

Fonte da chave é a mesma Gamma que gerou o parquet (Decisão 2) — não é troca de
fonte de dado. A mudança de esquema foi PEDIDA pela Lia (dona do consumidor);
é aditiva e retrocompatível.

Uso: .venv/bin/python scripts/g5b_fomc_conditionid.py
"""

import sys
import time
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parents[1]
REUNIOES_PATH = REPO_ROOT / "data" / "polymarket_fed_reunioes.parquet"

GAMMA_EVENTS = "https://gamma-api.polymarket.com/events"
TIMEOUT = 30
DELAY = 0.15


def build_map(evento_ids, sess):
    """(evento_id, question) -> (conditionId, slug), via /events?id= por evento."""
    mp = {}
    for eid in evento_ids:
        r = sess.get(GAMMA_EVENTS, params={"id": eid}, timeout=TIMEOUT)
        r.raise_for_status()
        j = r.json()
        markets = j[0].get("markets", []) if j else []
        for m in markets:
            mp[(eid, m.get("question"))] = (m.get("conditionId"), m.get("slug"))
        print(f"  evento {eid}: {len(markets)} mercados", file=sys.stderr)
        time.sleep(DELAY)
    return mp


def main():
    df = pd.read_parquet(REUNIOES_PATH)
    evento_ids = sorted(df["evento_id"].unique(), key=int)
    print(f"Parquet: {len(df)} linhas, {df['mercado'].nunique()} mercados, "
          f"{len(evento_ids)} eventos", file=sys.stderr)

    sess = requests.Session()
    sess.headers.update({"User-Agent": "quant-itau-g5b/1.0"})
    mp = build_map(evento_ids, sess)

    # Casa cada linha por (evento_id, mercado). question é única por evento.
    keys = list(zip(df["evento_id"], df["mercado"]))
    cond = [mp.get(k, (None, None))[0] for k in keys]
    slug = [mp.get(k, (None, None))[1] for k in keys]

    faltando = sorted({k for k, c in zip(keys, cond) if c is None})
    if faltando:
        print("ERRO: mercados sem conditionId (parquet NÃO reescrito):", file=sys.stderr)
        for eid, q in faltando:
            print(f"  evento {eid}: {q}", file=sys.stderr)
        return 1

    # Insere as colunas logo após evento_id, preservando o resto intacto.
    df["conditionId"] = cond
    df["slug"] = slug
    cols = list(df.columns)
    for c in ("conditionId", "slug"):
        cols.remove(c)
    i = cols.index("evento_id") + 1
    cols = cols[:i] + ["conditionId", "slug"] + cols[i:]
    df = df[cols]

    df.to_parquet(REUNIOES_PATH, index=False)

    n_cid = df["conditionId"].nunique()
    print("\n=== G5b — chave de junção no parquet do FOMC ===")
    print(f"Arquivo:            {REUNIOES_PATH.relative_to(REPO_ROOT)}")
    print(f"Colunas:            {list(df.columns)}")
    print(f"Linhas:             {len(df)} (inalterado)")
    print(f"Mercados:           {df['mercado'].nunique()} | conditionId distintos: {n_cid}")
    print(f"Cobertura:          {sum(c is not None for c in cond)}/{len(cond)} linhas com chave")
    return 0


if __name__ == "__main__":
    sys.exit(main())
