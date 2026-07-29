"""FOLLOW-UP F8 — varredura do CPI mensal (US) dos últimos ~18 meses.

Para cada evento de CPI mensal dos EUA: nº de buckets, rótulos crus na ordem,
volume do evento, 1ª/última data (da série do bucket primário) e o mês de
referência inferido pelas datas. Salva a série CRUA de cada bucket em
data/raw/clob_exploracao/ (junto com o F3). Anota mudanças de formato.

NÃO decide, NÃO normaliza. Campo indisponível = '?'.

Uso: .venv/bin/python scripts/followup_cpi_sweep.py
"""

import datetime as dt
import json
import sys
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_ROOT / "data" / "raw" / "clob_exploracao"
G = "https://gamma-api.polymarket.com"
CLOB = "https://clob.polymarket.com"
TIMEOUT = 30

# Candidatos US do public-search (exclui argentina/china/uk/eu/canada).
SLUGS = [
    "january-inflation-monthly", "february-inflation-monthly",
    "march-inflation-monthly", "march-inflation-us-monthly",
    "april-inflation-us-monthly", "may-inflation-monthly", "may-inflation-us-monthly",
    "june-inflation-monthly", "june-inflation-us-monthly-20260610151033433",
    "july-inflation-monthly", "july-inflation-us-monthly-20260714151042665",
    "august-inflation-monthly", "september-inflation-monthly",
    "october-inflation-monthly", "november-inflation-monthly",
    "december-inflation-monthly", "december-inflation-us-monthly",
]


def get(url, params=None):
    return requests.get(url, params=params, timeout=TIMEOUT)


def fetch_event(slug):
    r = get(f"{G}/events", {"slug": slug, "closed": "true"})
    ev = r.json() if r.ok else []
    if not ev:
        r = get(f"{G}/events", {"slug": slug})
        ev = r.json() if r.ok else []
    return ev[0] if isinstance(ev, list) and ev else (ev if isinstance(ev, dict) else None)


def tokens(m):
    raw = m.get("clobTokenIds")
    if not raw:
        return []
    return json.loads(raw) if isinstance(raw, str) else raw


def hist(tok):
    r = get(f"{CLOB}/prices-history", {"market": tok, "interval": "all", "fidelity": 720})
    return ((r.json() or {}).get("history", []) if r.ok else []), (r.text if r.ok else "")


def slugify(s):
    return "".join(c if c.isalnum() else "-" for c in (s or "").lower())[:40].strip("-")


def process(slug, rows):
    ev = fetch_event(slug)
    if not ev:
        print(f"  {slug}: NÃO abriu")
        return
    markets = ev.get("markets", []) or []
    labels = [m.get("question") for m in markets]
    vol = ev.get("volume")
    # data pela série do 1º bucket com token
    first = last = "?"
    for m in markets:
        toks = tokens(m)
        if not toks:
            continue
        h, raw = hist(toks[0])
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        fname = f"CPI_{slug}_{slugify(m.get('slug') or m.get('question'))}_{toks[0]}.json"
        (RAW_DIR / fname).write_text(raw, encoding="utf-8")
        ts = sorted(p["t"] for p in h if "t" in p)
        if ts and first == "?":
            first = dt.datetime.utcfromtimestamp(ts[0]).date().isoformat()
            last = dt.datetime.utcfromtimestamp(ts[-1]).date().isoformat()
    rows.append({
        "slug": slug, "title": ev.get("title"), "n_buckets": len(markets),
        "labels": labels, "vol": vol, "first": first, "last": last,
    })
    print(f"  {slug}: {len(markets)} buckets | vol {vol} | {first} → {last}")


def main():
    rows = []
    for slug in SLUGS:
        try:
            process(slug, rows)
        except Exception as exc:  # noqa: BLE001
            print(f"  ERRO {slug}: {type(exc).__name__}: {exc}")
    # ordena por 1ª data
    rows.sort(key=lambda r: (r["first"] == "?", r["first"]))
    print("\n\n===== TABELA F8 (ordenada por 1ª data) =====")
    for r in rows:
        print(f"\n### {r['title']}  [{r['slug']}]")
        print(f"  buckets: {r['n_buckets']} | volume: {r['vol']} | {r['first']} → {r['last']}")
        for lab in r["labels"]:
            print(f"    - {lab}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
