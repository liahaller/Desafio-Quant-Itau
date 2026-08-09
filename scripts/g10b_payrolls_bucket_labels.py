"""G10b — Rótulo dos baldes dos mercados de payrolls (metadado que ficou de fora
do G9b).

Os 234 JSONs do G9b (`data/raw/clob_exploracao/G9_payrolls_<slug-do-mercado>_<token>.json`)
têm só preço; o nome do arquivo traz o slug do EVENTO e o token, mas não o slug do
DESFECHO nem o rótulo do balde. Este script preenche esse metadado — uma linha por
(mercado, balde) — para que o `bucket_value` do Felipe consiga ler o desfecho.

Caminho: parte do `payrolls_polymarket_markets.csv` (33 linhas, JÁ filtrado para EUA
no G9b — sem risco de mercado estrangeiro). Para cada slug de evento, chama
`gamma-api.polymarket.com/events?slug=<slug>` (sem chave) e, para cada `market`
(balde) do evento, extrai:
  - token_id      = clobTokenIds[0]  (o token que CASA com o nome do JSON do G9b)
  - outcome       = groupItemTitle   (rótulo do balde, CRU, sem normalizar)
  - slug_desfecho = slug do market-balde
  - familia       = a do CSV do G9b (por evento)

NÃO decide, NÃO normaliza. Campo ausente vai como '?'. Não rebaixa as séries.

Uso: .venv/bin/python scripts/g10b_payrolls_bucket_labels.py
"""

import csv
import json
import sys
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parents[1]
SUMMARY_CSV = REPO_ROOT / "data" / "raw" / "payrolls_polymarket_markets.csv"
OUT = REPO_ROOT / "data" / "raw" / "payrolls_bucket_labels.csv"
G = "https://gamma-api.polymarket.com"
TIMEOUT = 30

# Marcadores de balde com ponta aberta ("X ou mais" / "X ou menos").
OPEN_END = ("<", ">", "≤", "≥", "+", "or more", "or fewer", "or less", "more than",
            "less than", "under", "over", "above", "below")


def get(url, params=None):
    return requests.get(url, params=params, timeout=TIMEOUT)


def fetch_event(slug):
    """Mesmo padrão do G9b: tenta com closed=true, cai para sem filtro."""
    r = get(f"{G}/events", {"slug": slug, "closed": "true"})
    ev = r.json() if r.ok else []
    if not ev:
        r = get(f"{G}/events", {"slug": slug})
        ev = r.json() if r.ok else []
    if isinstance(ev, list) and ev:
        return ev[0]
    return ev if isinstance(ev, dict) and ev else None


def as_list(raw):
    if raw is None:
        return []
    return json.loads(raw) if isinstance(raw, str) else raw


def is_open_ended(label):
    t = (label or "").lower()
    return any(m in t for m in OPEN_END)


def main():
    fam_by_slug = {}
    with open(SUMMARY_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            fam_by_slug[row["slug"]] = row["familia"]

    print("=" * 72)
    print("G10b — RÓTULO DOS BALDES DE PAYROLLS")
    print("=" * 72)

    rows = []
    sem_rotulo = []      # mercados que não abriram no /events ou sem markets
    ponta_aberta = {}    # slug_mercado -> [rótulos de ponta aberta]
    campo_rotulo_usado = set()

    for slug in fam_by_slug:
        ev = fetch_event(slug)
        if not ev:
            print(f"  [SEM ROTULO] {slug} — não abriu no /events")
            sem_rotulo.append(slug)
            continue
        markets = ev.get("markets", []) or []
        if not markets:
            print(f"  [SEM ROTULO] {slug} — evento sem markets")
            sem_rotulo.append(slug)
            continue
        fam = fam_by_slug[slug]
        for m in markets:
            toks = as_list(m.get("clobTokenIds"))
            token_id = toks[0] if toks else "?"   # tok[0] casa com o nome do JSON G9b
            git = m.get("groupItemTitle")
            if git not in (None, ""):
                outcome = git
                campo_rotulo_usado.add("groupItemTitle")
            else:
                # balde binário sem groupItemTitle: reporta os outcomes CRUS
                oc = as_list(m.get("outcomes"))
                outcome = "/".join(oc) if oc else "?"
                campo_rotulo_usado.add("outcomes" if oc else "?")
            slug_desfecho = m.get("slug") or "?"
            rows.append({"slug_mercado": slug, "token_id": token_id,
                         "outcome": outcome, "slug_desfecho": slug_desfecho,
                         "familia": fam})
            if is_open_ended(outcome):
                ponta_aberta.setdefault(slug, []).append(outcome)
        print(f"  [OK] {slug} — {len(markets)} baldes ({fam})")

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["slug_mercado", "token_id", "outcome",
                                          "slug_desfecho", "familia"])
        w.writeheader()
        w.writerows(rows)

    print("\n=== G10b — RÓTULO DOS BALDES DE PAYROLLS ===")
    print(f"Fonte usada:            {G}/events?slug=<slug>   (precisa de chave? NÃO)")
    print(f"Arquivo salvo:          {OUT.relative_to(REPO_ROOT)}")
    exp = sum(1 for _ in rows)
    esperado = None
    with open(SUMMARY_CSV, encoding="utf-8") as f:
        esperado = sum(int(r["n_buckets"]) for r in csv.DictReader(f))
    print(f"Nº de linhas:           {len(rows)}   (esperado: soma dos n_buckets do CSV do G9b = {esperado})")
    print(f"Colunas:                slug_mercado, token_id, outcome, slug_desfecho, familia")
    print(f"Rótulo lido do campo:   {sorted(campo_rotulo_usado)}")
    print(f"Mercados sem rótulo:    {sem_rotulo or 'nenhum'}")
    if ponta_aberta:
        print("Grades com ponta aberta:")
        for s, labs in ponta_aberta.items():
            print(f"   {s}: {labs}")
    else:
        print("Grades com ponta aberta: nenhum")
    return 0


if __name__ == "__main__":
    sys.exit(main())
