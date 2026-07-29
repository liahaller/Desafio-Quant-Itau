"""FOLLOW-UP F5/F10 — que preço é a série + granularidade em mercado VIVO.

Só mercados VIVOS servem (o book some na resolução). O script acha um mercado
líquido e um fino, ambos ativos, e no MESMO instante puxa /prices-history (último
ponto), /last-trade-price, /midpoint e /book (melhor bid/ask) — é o F5. Depois,
no líquido, varre fidelity 1/10/60/180/720 — é o F10.

NÃO decide, NÃO normaliza. Dado cru. Campo indisponível sai como '?'.

Uso: .venv/bin/python scripts/followup_live_price.py
"""

import datetime as dt
import json
import sys

import requests

GAMMA_URL = "https://gamma-api.polymarket.com"
CLOB_URL = "https://clob.polymarket.com"
TIMEOUT = 30


def get(url, params=None):
    return requests.get(url, params=params, timeout=TIMEOUT)


def tokens(m):
    raw = m.get("clobTokenIds")
    if not raw:
        return []
    return json.loads(raw) if isinstance(raw, str) else raw


def find_live_markets():
    """Devolve (liquido, fino): mercados ativos, não fechados, com clobTokenIds."""
    r = get(f"{GAMMA_URL}/markets",
            {"active": "true", "closed": "false", "order": "volumeNum",
             "ascending": "false", "limit": 200})
    ms = r.json() if r.ok else []
    ms = [m for m in ms if tokens(m) and float(m.get("volumeNum") or 0) > 0]
    ms.sort(key=lambda m: float(m.get("volumeNum") or 0), reverse=True)
    if not ms:
        return None, None
    liquido = ms[0]
    # fino: menor volume > 0 que ainda tenha book (testamos abaixo)
    fino = None
    for m in reversed(ms):
        tok = tokens(m)[0]
        b = get(f"{CLOB_URL}/book", {"token_id": tok})
        if b.ok and (b.json() or {}).get("bids") is not None:
            fino = m
            break
    return liquido, fino


def snapshot(m, rotulo):
    tok = tokens(m)[0]
    now = dt.datetime.utcnow().isoformat() + "Z"
    print(f"\n=== QUE PREÇO É A SÉRIE ({rotulo}) ===")
    print(f"Mercado vivo usado:  {m.get('slug')} | tokenYes {tok}")
    print(f"volumeNum:           {m.get('volumeNum')}")
    print(f"Timestamp da coleta: {now}")

    ph = get(f"{CLOB_URL}/prices-history", {"market": tok, "interval": "1d", "fidelity": 1})
    hist = (ph.json() or {}).get("history", []) if ph.ok else []
    ph_last = hist[-1]["p"] if hist else "?"
    ltp = get(f"{CLOB_URL}/last-trade-price", {"token_id": tok})
    ltp_v = (ltp.json() or {}).get("price", "?") if ltp.ok else f"HTTP{ltp.status_code}"
    mid = get(f"{CLOB_URL}/midpoint", {"token_id": tok})
    mid_v = (mid.json() or {}).get("mid", "?") if mid.ok else f"HTTP{mid.status_code}"
    book = get(f"{CLOB_URL}/book", {"token_id": tok})
    bid = ask = "?"
    if book.ok:
        bk = book.json() or {}
        bids, asks = bk.get("bids") or [], bk.get("asks") or []
        # a API devolve bids/asks; melhor bid = maior price, melhor ask = menor price
        if bids:
            bid = max(bids, key=lambda x: float(x["price"]))["price"]
        if asks:
            ask = min(asks, key=lambda x: float(x["price"]))["price"]
    print(f"prices-history (último ponto): {ph_last}")
    print(f"last-trade-price:              {ltp_v}")
    print(f"midpoint:                      {mid_v}")
    print(f"book: melhor bid / melhor ask: {bid} / {ask}")


def fidelity_sweep(m):
    tok = tokens(m)[0]
    print(f"\n=== GRANULARIDADE EM MERCADO VIVO ===")
    print(f"Mercado: {m.get('slug')} | tokenYes {tok}")
    for fid in (1, 10, 60, 180, 720):
        r = get(f"{CLOB_URL}/prices-history", {"market": tok, "interval": "all", "fidelity": fid})
        hist = (r.json() or {}).get("history", []) if r.ok else []
        ts = sorted(p["t"] for p in hist if "t" in p)
        if not ts:
            print(f"fidelity={fid:<3} → 0 pontos (HTTP {r.status_code})")
            continue
        steps = [b - a for a, b in zip(ts, ts[1:])]
        passo = sorted(steps)[len(steps) // 2] if steps else "?"
        lo = dt.datetime.utcfromtimestamp(ts[0]).isoformat()
        hi = dt.datetime.utcfromtimestamp(ts[-1]).isoformat()
        print(f"fidelity={fid:<3} → {len(ts)} pontos | passo mediano {passo}s | {lo} → {hi}")


def main():
    liquido, fino = find_live_markets()
    if not liquido:
        print("Nenhum mercado vivo encontrado.")
        return 1
    snapshot(liquido, "LÍQUIDO")
    if fino:
        snapshot(fino, "FINO")
    else:
        print("\n(FINO: nenhum mercado fino com book encontrado)")
    fidelity_sweep(liquido)
    return 0


if __name__ == "__main__":
    sys.exit(main())
