"""G4 — Os três buracos da varredura de CPI: abr/2025, jan/2026, fev/2026.

Para cada mês de referência tenta uma lista de slugs candidatos no /events e,
em paralelo, o public-search com o termo exato. Reporta, por mês: cada busca
feita (endpoint + termo), se achou mercado, e — se achou — slug, nº de buckets,
volume, 1ª/última data (salvando as séries cruas). Se não achou após todas as
buscas, é lacuna real do Polymarket.

O ano é desambiguado pelas datas da série (o slug sozinho não distingue
jan/2025 de jan/2026). NÃO decide, NÃO normaliza.

Uso: .venv/bin/python scripts/g4_cpi_holes.py
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

TARGETS = {
    "abril/2025": {
        "slugs": ["april-inflation-monthly", "april-inflation-us-monthly",
                  "april-2025-inflation-monthly"],
        "search": ["april inflation", "april 2025 inflation cpi"],
        "expect_year": 2025,
    },
    "janeiro/2026": {
        "slugs": ["january-inflation-us-monthly", "january-inflation-monthly",
                  "january-2026-inflation-monthly"],
        "search": ["january inflation", "january 2026 inflation cpi"],
        "expect_year": 2026,
    },
    "fevereiro/2026": {
        "slugs": ["february-inflation-us-monthly", "february-inflation-monthly",
                  "february-2026-inflation-monthly"],
        "search": ["february inflation", "february 2026 inflation cpi"],
        "expect_year": 2026,
    },
}


def get(url, params=None):
    return requests.get(url, params=params, timeout=TIMEOUT)


def fetch_event(slug):
    r = get(f"{G}/events", {"slug": slug, "closed": "true"})
    ev = r.json() if r.ok else []
    if not ev:
        r = get(f"{G}/events", {"slug": slug})
        ev = r.json() if r.ok else []
    return ev[0] if isinstance(ev, list) and ev else (ev if isinstance(ev, dict) else None)


def search_events(q):
    r = get(f"{G}/public-search", {"q": q, "limit_per_type": 10})
    if not r.ok:
        return []
    return [(ev.get("slug"), ev.get("title"), ev.get("volume"))
            for ev in (r.json() or {}).get("events", []) or []]


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


def event_span(ev, save_prefix):
    """Salva séries cruas dos buckets e devolve (n_buckets, first, last)."""
    markets = ev.get("markets", []) or []
    first = last = "?"
    for m in markets:
        toks = tokens(m)
        if not toks:
            continue
        h, raw = hist(toks[0])
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        fname = f"{save_prefix}_{slugify(m.get('slug') or m.get('question'))}_{toks[0]}.json"
        (RAW_DIR / fname).write_text(raw, encoding="utf-8")
        ts = sorted(p["t"] for p in h if "t" in p)
        if ts and first == "?":
            first = dt.datetime.utcfromtimestamp(ts[0]).date().isoformat()
            last = dt.datetime.utcfromtimestamp(ts[-1]).date().isoformat()
    return len(markets), first, last


def process(mes, cfg):
    print(f"\n{'='*70}\n### {mes}\n{'='*70}")
    achou = None
    # 1) slugs candidatos
    for slug in cfg["slugs"]:
        ev = fetch_event(slug)
        status = "achou evento" if ev else "vazio"
        print(f"  [/events slug={slug}] -> {status}")
        if ev and achou is None:
            achou = (slug, ev)
    # 2) public-search
    for q in cfg["search"]:
        hits = search_events(q)
        print(f"  [/public-search q='{q}'] -> {len(hits)} eventos:")
        for s, title, vol in hits[:8]:
            print(f"       {s}  | {title}  | vol={vol}")
        if achou is None:
            for s, title, vol in hits:
                if "inflation" in (s or ""):
                    ev2 = fetch_event(s)
                    if ev2:
                        achou = (s, ev2)
                        break

    if not achou:
        print(f"\n  RESULTADO {mes}: NAO encontrado -> lacuna real do Polymarket "
              f"(nenhum mercado US de inflação para esse mês de referência).")
        return

    slug, ev = achou
    n, first, last = event_span(ev, save_prefix=f"CPI_G4_{slugify(mes)}_{slug}")
    print(f"\n  RESULTADO {mes}: SIM")
    print(f"     slug     : {slug}")
    print(f"     title    : {ev.get('title')}")
    print(f"     buckets  : {n}")
    print(f"     volume   : {ev.get('volume')}")
    print(f"     datas    : {first} -> {last}  (ano confirma {cfg['expect_year']}? "
          f"{'SIM' if str(cfg['expect_year']) in (first + last) else 'CONFERIR'})")


def main():
    for mes, cfg in TARGETS.items():
        try:
            process(mes, cfg)
        except Exception as exc:  # noqa: BLE001
            print(f"  ERRO {mes}: {type(exc).__name__}: {exc}")
    print("\nConcluido — G4.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
