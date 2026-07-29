"""FOLLOW-UP F2/F3/F9 — identificadores, séries cruas e contagem de lacunas.

Roda contra a API real do Polymarket (VPN ligada). Para cada um dos 9 mercados
do pedido resolve o evento no Gamma, extrai os IDs (conditionId, clobTokenIds
Yes/No, slugs), salva o retorno CRU do /prices-history de cada token em
data/raw/clob_exploracao/ e, para os mercados pedidos (M2, M5, M6, M8), conta as
lacunas da grade de 12h. Para as PMFs (M1 CPI, M3 trajetória do Fed) salva um
arquivo por bucket.

NÃO decide, NÃO normaliza, NÃO interpola. Dado cru, campos crus. Campo não medido
sai como '?'.

Uso:
    .venv/bin/python scripts/followup_ids_series.py
"""

import datetime as dt
import json
import sys
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_ROOT / "data" / "raw" / "clob_exploracao"

GAMMA_URL = "https://gamma-api.polymarket.com"
CLOB_URL = "https://clob.polymarket.com"
TIMEOUT = 30

# Cada entrada: slug do evento (best-guess do RESPOSTA anterior) + fallback de
# busca. is_pmf=True => salva um arquivo por bucket (M1, M3). count_gaps=True =>
# entra na tabela F9 (M2, M5, M6, M8).
MARKETS = {
    "M1_cpi_monthly": {
        "slug": "july-inflation-monthly",
        "search": ["cpi monthly inflation", "inflation monthly"],
        "is_pmf": True, "count_gaps": False,
    },
    "M2_fomc": {
        "slug": None,  # resolvido via evento FOMC de maior volume (ver resolve_m2)
        "search": ["fed decision", "fed interest rates"],
        "is_pmf": False, "count_gaps": True,
    },
    "M3_fed_trajectory": {
        "slug": "how-many-fed-rate-cuts-in-2025",
        "search": ["how many fed rate cuts 2025", "fed rate cuts 2025"],
        "is_pmf": True, "count_gaps": False,
    },
    "M4_recession": {
        "slug": "us-recession-in-2025",
        "search": ["us recession 2025"],
        "is_pmf": False, "count_gaps": False,
    },
    "M5_trump_2024": {
        "slug": "will-donald-trump-win-the-2024-us-presidential-election",
        "search": ["trump win 2024 presidential"],
        "is_pmf": False, "count_gaps": True,
    },
    "M6_china_tariffs": {
        "slug": None,
        "search": ["trump china tariffs", "tariffs on china"],
        "is_pmf": False, "count_gaps": True,
    },
    "M7_iran_strike": {
        "slug": None,
        "search": ["us strikes iran", "us military action iran"],
        "is_pmf": False, "count_gaps": False,
    },
    "M8_obbb_debt": {
        "slug": None,
        "search": ["reconciliation bill passed", "debt ceiling suspended"],
        "is_pmf": False, "count_gaps": True,
    },
    "M9_midterms_2022": {
        "slug": None,
        "search": ["2022 senate control", "republicans win senate 2022"],
        "is_pmf": False, "count_gaps": False,
    },
}


def get(url, params=None):
    return requests.get(url, params=params, timeout=TIMEOUT)


def search_top_slug(queries):
    """public-search: devolve o slug do evento de maior volume."""
    cand = {}
    for q in queries:
        r = get(f"{GAMMA_URL}/public-search", {"q": q, "limit_per_type": 8})
        if not r.ok:
            continue
        for ev in (r.json() or {}).get("events", []) or []:
            s = ev.get("slug")
            if s:
                cand[s] = float(ev.get("volume") or 0)
    if not cand:
        return None, []
    top = sorted(cand.items(), key=lambda kv: kv[1], reverse=True)
    return top[0][0], top[:5]


def fetch_event(slug):
    r = get(f"{GAMMA_URL}/events", {"slug": slug, "closed": "true"})
    ev = r.json() if r.ok else []
    if not ev:
        r = get(f"{GAMMA_URL}/events", {"slug": slug})
        ev = r.json() if r.ok else []
    return ev[0] if isinstance(ev, list) and ev else (ev if isinstance(ev, dict) else None)


def resolve_m2():
    """M2 = mercado FOMC de maior volume (do evento_id no parquet)."""
    import pandas as pd
    df = pd.read_parquet(REPO_ROOT / "data" / "polymarket_fed_reunioes.parquet")
    # mercado de maior volume
    row = df.sort_values("volume", ascending=False).iloc[0]
    ev_id = int(row["evento_id"])
    r = get(f"{GAMMA_URL}/events/{ev_id}")
    ev = r.json() if r.ok else None
    return ev, row["mercado"], ev_id


def token_ids(market):
    raw = market.get("clobTokenIds")
    if not raw:
        return []
    return json.loads(raw) if isinstance(raw, str) else raw


def fetch_history(token_id, fidelity=720):
    r = get(f"{CLOB_URL}/prices-history",
            {"market": token_id, "interval": "all", "fidelity": fidelity})
    if not r.ok:
        return None, r.text
    return (r.json() or {}).get("history", []), r.text


def series_stats(hist):
    ts = sorted(p["t"] for p in hist if "t" in p)
    if not ts:
        return None
    lo = dt.datetime.utcfromtimestamp(ts[0]).date().isoformat()
    hi = dt.datetime.utcfromtimestamp(ts[-1]).date().isoformat()
    return {"n": len(ts), "primeira": lo, "ultima": hi, "ts": ts}


def gap_analysis(ts):
    """F9: slots de 12h esperados, ausentes, %, maior buraco (h)."""
    span_s = ts[-1] - ts[0]
    esperados = int(round(span_s / 43200)) + 1
    ausentes = max(0, esperados - len(ts))
    steps = [b - a for a, b in zip(ts, ts[1:])]
    maior_h = round(max(steps) / 3600, 1) if steps else 0.0
    pct = round(100 * ausentes / esperados, 1) if esperados else 0.0
    return {"esperados_12h": esperados, "ausentes": ausentes, "pct": pct, "maior_buraco_h": maior_h}


def save_raw(fname, text):
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    (RAW_DIR / fname).write_text(text, encoding="utf-8")


def slugify(s):
    return "".join(c if c.isalnum() else "-" for c in (s or "").lower())[:40].strip("-")


def process(mid, cfg):
    print(f"\n{'='*75}\n### {mid}\n{'='*75}")
    slug = cfg["slug"]
    if mid == "M2_fomc":
        ev, mname, ev_id = resolve_m2()
        if not ev:
            print("  M2: não abriu o evento FOMC.")
            return
        slug = ev.get("slug")
        print(f"  (M2 = mercado FOMC de maior volume: {mname!r}, evento_id {ev_id})")
    else:
        if slug is None:
            slug, top = search_top_slug(cfg["search"])
            print(f"  slug resolvido por busca: {slug}")
            for s, v in top:
                print(f"    ${v:>13,.0f}  {s}")
        ev = fetch_event(slug)
    if not ev:
        print(f"  NÃO abriu evento (slug={slug}).")
        return

    print(f"  evento.title : {ev.get('title')}")
    print(f"  evento.slug  : {ev.get('slug')}")
    print(f"  evento.volume: {ev.get('volume')}")
    markets = ev.get("markets", []) or []
    markets = sorted(markets, key=lambda m: float(m.get("volumeNum") or 0), reverse=True)

    if cfg["is_pmf"]:
        targets = markets  # todos os buckets
    elif mid == "M2_fomc":
        # o mercado específico de maior volume já é o alvo; casa o nome do parquet
        targets = markets[:1]
    else:
        targets = markets[:1]  # binário-mãe por liquidez

    print(f"  nº de mercados no evento: {len(markets)} | medindo {len(targets)}")
    for m in targets:
        toks = token_ids(m)
        cid = m.get("conditionId")
        yes = toks[0] if len(toks) > 0 else "?"
        no = toks[1] if len(toks) > 1 else "?"
        print(f"\n  --- mercado: {m.get('question')}")
        print(f"      market.slug : {m.get('slug')}")
        print(f"      conditionId : {cid}")
        print(f"      tokenId Yes : {yes}")
        print(f"      tokenId No  : {no}")
        print(f"      volumeNum   : {m.get('volumeNum')}")
        if yes == "?":
            print("      (sem clobTokenIds — não dá para puxar série)")
            continue
        hist, raw = fetch_history(yes, 720)
        fname = f"{mid}_{slugify(m.get('slug') or m.get('question'))}_{yes}.json"
        save_raw(fname, raw)
        st = series_stats(hist or [])
        if not st:
            print(f"      série: VAZIA (salvo mesmo assim: {fname})")
            continue
        print(f"      série: n={st['n']} | {st['primeira']} → {st['ultima']} | arquivo={fname}")
        if cfg["count_gaps"]:
            g = gap_analysis(st["ts"])
            print(f"      [F9] esperados_12h={g['esperados_12h']} ausentes={g['ausentes']} "
                  f"({g['pct']}%) maior_buraco={g['maior_buraco_h']}h")


def main():
    for mid, cfg in MARKETS.items():
        try:
            process(mid, cfg)
        except Exception as exc:  # noqa: BLE001
            print(f"  ERRO {mid}: {type(exc).__name__}: {exc}")
    print("\n\nConcluído — F2/F3/F9.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
