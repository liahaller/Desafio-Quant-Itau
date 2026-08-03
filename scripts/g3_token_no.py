"""G3 — Série do token No de M4 (recessão) e M5 (Trump 2024).

Puxa o /prices-history do tokenId No dos dois mercados, salva CRU (sufixo _NO),
e compara com a série Yes já conhecida: mesmo grid de 12h? soma p_yes+p_no nos
instantes em que os dois existem (mínimo/mediana/máximo) e quantos instantes há.

NÃO normaliza, NÃO interpola. Campo não medido = '?'.

Uso:
    .venv/bin/python scripts/g3_token_no.py
"""

import datetime as dt
import json
import statistics as st
import sys
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_ROOT / "data" / "raw" / "clob_exploracao"
GAMMA_URL = "https://gamma-api.polymarket.com"
CLOB_URL = "https://clob.polymarket.com"
TIMEOUT = 30

# kind: "event" => resolve via /events e pega o mercado de maior volume.
# kind: "market" => resolve o mercado direto no /markets (caso do M5).
MARKETS = {
    "M4_recession": {"slug": "us-recession-in-2025", "kind": "event"},
    "M5_trump_2024": {
        "slug": "will-donald-trump-win-the-2024-us-presidential-election",
        "kind": "market",
    },
}


def get(url, params=None):
    return requests.get(url, params=params, timeout=TIMEOUT)


def fetch_event(slug):
    r = get(f"{GAMMA_URL}/events", {"slug": slug, "closed": "true"})
    ev = r.json() if r.ok else []
    if not ev:
        r = get(f"{GAMMA_URL}/events", {"slug": slug})
        ev = r.json() if r.ok else []
    return ev[0] if isinstance(ev, list) and ev else (ev if isinstance(ev, dict) else None)


def fetch_market(slug):
    r = get(f"{GAMMA_URL}/markets", {"slug": slug, "closed": "true"})
    data = r.json() if r.ok else []
    ms = data if isinstance(data, list) else data.get("markets", [])
    return ms[0] if ms else None


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


def as_map(hist):
    return {p["t"]: p["p"] for p in (hist or []) if "t" in p and "p" in p}


def slugify(s):
    return "".join(c if c.isalnum() else "-" for c in (s or "").lower())[:40].strip("-")


def process(mid, cfg):
    slug, kind = cfg["slug"], cfg["kind"]
    print(f"\n{'='*70}\n### {mid}  (slug: {slug} | {kind})\n{'='*70}")
    if kind == "market":
        m = fetch_market(slug)
        if not m:
            print("  NAO resolveu no /markets.")
            return
    else:
        ev = fetch_event(slug)
        if not ev:
            print("  NAO abriu evento.")
            return
        markets = sorted(ev.get("markets", []) or [],
                         key=lambda m: float(m.get("volumeNum") or 0), reverse=True)
        if not markets:
            print("  evento sem mercados.")
            return
        m = markets[0]
    toks = token_ids(m)
    yes = toks[0] if len(toks) > 0 else "?"
    no = toks[1] if len(toks) > 1 else "?"
    print(f"  mercado     : {m.get('question')}")
    print(f"  tokenId Yes : {yes}")
    print(f"  tokenId No  : {no}")
    if no == "?":
        print("  sem tokenId No.")
        return

    hist_no, raw_no = fetch_history(no)
    hist_yes, _ = fetch_history(yes)
    fname = f"{mid}_{slugify(m.get('slug') or m.get('question'))}_{no}_NO.json"
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    (RAW_DIR / fname).write_text(raw_no, encoding="utf-8")

    map_no = as_map(hist_no)
    map_yes = as_map(hist_yes)
    n_no, n_yes = len(map_no), len(map_yes)
    ts_no = sorted(map_no)
    ts_yes = sorted(map_yes)

    def fmt_range(ts):
        if not ts:
            return "vazia"
        return (f"{dt.datetime.utcfromtimestamp(ts[0]).date()} -> "
                f"{dt.datetime.utcfromtimestamp(ts[-1]).date()}")

    same_grid = (ts_no == ts_yes)
    common = sorted(set(map_no) & set(map_yes))
    sums = [map_yes[t] + map_no[t] for t in common]
    # os timestamps caem no mesmo slot de 12h mesmo quando o segundo exato difere?
    slots_no = {t // 43200 for t in ts_no}
    slots_yes = {t // 43200 for t in ts_yes}
    same_slots = (slots_no == slots_yes)

    print(f"  arquivo No salvo : {fname}")
    print(f"  n(No) / n(Yes)   : {n_no} / {n_yes}")
    print(f"  range No         : {fmt_range(ts_no)}")
    print(f"  range Yes        : {fmt_range(ts_yes)}")
    print(f"  mesmo grid 12h (timestamp exato)? : {'SIM' if same_grid else 'NAO'}")
    print(f"  mesmos slots de 12h (floor 43200)? : {'SIM' if same_slots else 'NAO'}")
    if not same_grid:
        so_no = sorted(set(ts_no) - set(ts_yes))
        so_yes = sorted(set(ts_yes) - set(ts_no))
        print(f"     ts so no No: {len(so_no)} | ts so no Yes: {len(so_yes)}")
    print(f"  n instantes com os dois: {len(common)}")
    if sums:
        print(f"  soma p_yes+p_no  min/mediana/max: "
              f"{min(sums):.4f} / {st.median(sums):.4f} / {max(sums):.4f}")


def main():
    for mid, cfg in MARKETS.items():
        try:
            process(mid, cfg)
        except Exception as exc:  # noqa: BLE001
            print(f"  ERRO {mid}: {type(exc).__name__}: {exc}")
    print("\nConcluido — G3.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
