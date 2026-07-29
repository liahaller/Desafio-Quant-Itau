"""FOLLOW-UP F2/F3/F9 — casos especiais (M5, M9, M7 episódio jun/2025).

M5 (presidencial 2024) é resolvido por slug de MERCADO no /markets (não é evento).
M9 (midterms 2022) precisa do slug fixo do Senado 2022 (a busca por volume pega
o mercado de 2026). M7 acrescenta o episódio jun/2025 (primário da view C, além
do que já foi medido pela família us-strikes-iran-by).

Uso: .venv/bin/python scripts/followup_ids_series_extra.py
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


def get(url, params=None):
    return requests.get(url, params=params, timeout=TIMEOUT)


def market_by_slug(slug):
    """M5: mercado direto no /markets (closed=true p/ resolvido)."""
    r = get(f"{GAMMA_URL}/markets", {"slug": slug, "closed": "true"})
    data = r.json() if r.ok else []
    ms = data if isinstance(data, list) else data.get("markets", [])
    return ms[0] if ms else None


def event_market_by_slug(ev_slug, mkt_match=None):
    """M9/M7: abre evento e devolve (evento, mercado alvo)."""
    r = get(f"{GAMMA_URL}/events", {"slug": ev_slug, "closed": "true"})
    ev = r.json() if r.ok else []
    if not ev:
        r = get(f"{GAMMA_URL}/events", {"slug": ev_slug})
        ev = r.json() if r.ok else []
    ev = ev[0] if isinstance(ev, list) and ev else ev if isinstance(ev, dict) else None
    if not ev:
        return None, None
    markets = sorted(ev.get("markets", []) or [],
                     key=lambda m: float(m.get("volumeNum") or 0), reverse=True)
    if mkt_match:
        for m in markets:
            if mkt_match.lower() in (m.get("question") or "").lower():
                return ev, m
    return ev, (markets[0] if markets else None)


def tokens(m):
    raw = m.get("clobTokenIds")
    if not raw:
        return []
    return json.loads(raw) if isinstance(raw, str) else raw


def hist(tok, fid=720):
    r = get(f"{CLOB_URL}/prices-history", {"market": tok, "interval": "all", "fidelity": fid})
    return ((r.json() or {}).get("history", []) if r.ok else []), (r.text if r.ok else r.text)


def stats_and_gaps(h, gaps=False):
    ts = sorted(p["t"] for p in h if "t" in p)
    if not ts:
        return None
    lo = dt.datetime.utcfromtimestamp(ts[0]).date().isoformat()
    hi = dt.datetime.utcfromtimestamp(ts[-1]).date().isoformat()
    out = {"n": len(ts), "primeira": lo, "ultima": hi}
    if gaps:
        esperados = int(round((ts[-1] - ts[0]) / 43200)) + 1
        ausentes = max(0, esperados - len(ts))
        steps = [b - a for a, b in zip(ts, ts[1:])]
        out["gap"] = {"esperados_12h": esperados, "ausentes": ausentes,
                      "pct": round(100 * ausentes / esperados, 1) if esperados else 0,
                      "maior_buraco_h": round(max(steps) / 3600, 1) if steps else 0}
    return out


def slugify(s):
    return "".join(c if c.isalnum() else "-" for c in (s or "").lower())[:40].strip("-")


def report(mid, m, ev=None, gaps=False):
    toks = tokens(m)
    yes = toks[0] if toks else "?"
    no = toks[1] if len(toks) > 1 else "?"
    print(f"\n### {mid}")
    if ev:
        print(f"  evento.slug : {ev.get('slug')} | evento.volume {ev.get('volume')}")
    print(f"  question    : {m.get('question')}")
    print(f"  market.slug : {m.get('slug')}")
    print(f"  conditionId : {m.get('conditionId')}")
    print(f"  tokenId Yes : {yes}")
    print(f"  tokenId No  : {no}")
    print(f"  volumeNum   : {m.get('volumeNum')}")
    if yes == "?":
        print("  (sem clobTokenIds)")
        return
    h, raw = hist(yes)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    fname = f"{mid}_{slugify(m.get('slug') or m.get('question'))}_{yes}.json"
    (RAW_DIR / fname).write_text(raw, encoding="utf-8")
    st = stats_and_gaps(h, gaps)
    if not st:
        print(f"  série: VAZIA (salvo mesmo assim: {fname})")
        return
    print(f"  série: n={st['n']} | {st['primeira']} → {st['ultima']} | arquivo={fname}")
    if gaps and "gap" in st:
        g = st["gap"]
        print(f"  [F9] esperados_12h={g['esperados_12h']} ausentes={g['ausentes']} "
              f"({g['pct']}%) maior_buraco={g['maior_buraco_h']}h")


def main():
    # M5 — presidencial 2024 (slug de mercado, não evento)
    m5 = market_by_slug("will-donald-trump-win-the-2024-us-presidential-election")
    if m5:
        report("M5_trump_2024", m5, gaps=True)
    else:
        print("\n### M5_trump_2024\n  NÃO resolveu no /markets.")

    # M9 — midterms 2022 (slug fixo do Senado 2022)
    ev9, m9 = event_market_by_slug(
        "which-party-will-control-the-us-senate-after-the-2022-election")
    if m9:
        report("M9_midterms_2022", m9, ev9)
    else:
        print("\n### M9_midterms_2022\n  NÃO resolveu o evento do Senado 2022.")

    # M7 — episódio jun/2025 (primário da view C)
    ev7, m7 = event_market_by_slug("us-military-action-against-iran-before-july")
    if m7:
        report("M7_iran_jun2025", m7, ev7)
    else:
        print("\n### M7_iran_jun2025\n  NÃO resolveu o episódio jun/2025.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
