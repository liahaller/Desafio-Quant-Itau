"""FOLLOW-UP F4 — dimensionamento do data-api /trades (M5 e M4) + extra M9/2022.

Mede, sem decidir, se dá para reconstruir um proxy de midpoint a partir do fluxo
de trades: quantos trades existem, como pagina, até onde cobre, rate limit, e —
o que decide de verdade — quantas janelas de 12h têm BUY e SELL simultâneos.

Achado da fase de sondagem (documentado no cabeçalho da devolução): a data-api
capa limit=10000 E offset=10000 → no máximo os ~20.000 trades MAIS RECENTES.
Este script confirma isso ao vivo e mede o resto.

Uso: .venv/bin/python scripts/followup_trades_dim.py
"""

import datetime as dt
import statistics
import sys
import time
from collections import Counter, defaultdict

import requests

D = "https://data-api.polymarket.com"
CLOB = "https://clob.polymarket.com"
TIMEOUT = 90

MARKETS = {
    "M5_trump_2024": {
        "conditionId": "0xdd22472e552920b8438158ea7238bfadfa4f736aa4cee91a6b86c39ead110917",
        "tokenYes": "21742633143463906290569050155826241533067272736897614950488156847949938836455",
    },
    "M4_recession": {
        "conditionId": "0xfa48a99317daef1654d5b03e30557c4222f276657275628d9475e141c64b545d",
        "tokenYes": "104173557214744537570424345347209544585775842950109756851652855913015295701992",
    },
    "M9_midterms_2022": {  # extra: /trades alcança 2022?
        "conditionId": "0xe0658c4beed2102c181b3987edff5edd578ad2952a6eb5fa8018925e5d7a48fd",
        "tokenYes": "69984203794322070924779554468751071533998686576952069110752844084141678897886",
    },
}


def prices_history_first(token):
    """1ª data da série do /prices-history (para comparar cobertura)."""
    r = requests.get(f"{CLOB}/prices-history",
                     {"market": token, "interval": "all", "fidelity": 720}, timeout=TIMEOUT)
    hist = (r.json() or {}).get("history", []) if r.ok else []
    ts = sorted(p["t"] for p in hist if "t" in p)
    if not ts:
        return None, 0
    return dt.datetime.utcfromtimestamp(ts[0]), len(ts)


def pull_all(cid):
    """Pagina /trades até o teto (offset<=10000). Devolve (trades, n_req, seg, rate_429, page_limit)."""
    trades = []
    n_req = 0
    t0 = time.time()
    rate_429 = "não encontrado"
    page_limit = None
    offset = 0
    LIMIT = 10000
    while offset <= 10000:
        r = requests.get(f"{D}/trades", {"market": cid, "limit": LIMIT, "offset": offset}, timeout=TIMEOUT)
        n_req += 1
        if r.status_code == 429:
            rate_429 = f"HTTP 429 na req {n_req} (offset {offset})"
            break
        if not r.ok:
            break
        batch = r.json()
        if page_limit is None:
            page_limit = len(batch)
        if not batch:
            break
        trades.extend(batch)
        if len(batch) < LIMIT:
            break
        offset += LIMIT
    return trades, n_req, time.time() - t0, rate_429, page_limit


def analyze(mid, cid, token):
    print(f"\n{'='*72}\n=== DIMENSIONAMENTO /trades — {mid} ===\n{'='*72}")
    ph_first, ph_n = prices_history_first(token)
    trades, n_req, secs, rate_429, page_limit = pull_all(cid)
    print(f"Mercado:                {mid} — {cid}")
    print(f"URL exata:              {D}/trades?market={cid}&limit=10000&offset=<0,10000>")
    print(f"Nº total de trades:     {len(trades)}  (alcançáveis; teto da API = 20000)")
    print(f"Limite por página:      {page_limit} (parâmetro limit; capado em 10000 pela API)")
    print(f"Como pagina:            offset (passo 10000); offset>10000 => HTTP 400 'max offset 10000'")
    if not trades:
        print("Span coberto:           — (sem trades)")
        print(f"Rate limit encontrado:  {rate_429}")
        return
    ts = sorted(t["timestamp"] for t in trades)
    lo, hi = dt.datetime.utcfromtimestamp(ts[0]), dt.datetime.utcfromtimestamp(ts[-1])
    print(f"Span coberto:           {lo} → {hi} (UTC)")
    if ph_first:
        cobre = "SIM" if lo <= ph_first + dt.timedelta(days=1) else "NÃO"
        extra = "" if cobre == "SIM" else f" — trunca; série começa {ph_first.date()}, trades só desde {lo.date()}"
        print(f"Cobre a vida inteira?   {cobre} (1ª data da série /prices-history: {ph_first.date()}){extra}")
    else:
        print(f"Cobre a vida inteira?   ? (série /prices-history vazia; trades cobrem {lo.date()}→{hi.date()})")
    print(f"Nº de requests / tempo: {n_req} requests / {secs:.1f}s")
    print(f"Rate limit encontrado:  {rate_429}")

    # trades por dia (mediana) e dias sem trade na janela alcançável
    por_dia = Counter(dt.datetime.utcfromtimestamp(t["timestamp"]).date() for t in trades)
    dias_span = (hi.date() - lo.date()).days + 1
    dias_com = len(por_dia)
    dias_sem = dias_span - dias_com
    print(f"Trades por dia (mediana): {int(statistics.median(por_dia.values()))}")
    print(f"Dias sem NENHUM trade:  {dias_sem} (na janela alcançável de {dias_span} dias-calendário)")
    print(f"Campos crus:            {list(trades[0].keys())}")
    print("Amostra (3 linhas cruas):")
    for t in trades[:3]:
        print(f"  {{side:{t['side']}, price:{t['price']}, size:{t['size']}, ts:{t['timestamp']}, tx:{t['transactionHash'][:12]}...}}")

    # BUY/SELL por janela de 12h — só num DIA de liquidez normal (mediana)
    janelas = defaultdict(lambda: Counter())
    for t in trades:
        d = dt.datetime.utcfromtimestamp(t["timestamp"])
        slot = (d.date(), 0 if d.hour < 12 else 1)
        janelas[slot][t["side"]] += 1
    n_jan = len(janelas)
    ambos = sum(1 for c in janelas.values() if c["BUY"] > 0 and c["SELL"] > 0)
    um_lado = sum(1 for c in janelas.values() if (c["BUY"] > 0) ^ (c["SELL"] > 0))
    vazias = 0  # janelas sem trade não aparecem no dict; contamos os slots ausentes
    total_slots = dias_span * 2
    vazias = total_slots - n_jan
    print(f"\nJanelas de 12h na amostra:            {n_jan} (com >=1 trade; de {total_slots} slots no span)")
    print(f"Janelas com BUY e SELL (ambos):       {ambos} ({round(100*ambos/n_jan,1)}%)")
    print(f"Janelas com um lado só:               {um_lado} ({round(100*um_lado/n_jan,1)}%)")
    print(f"Janelas vazias (slot sem trade):      {vazias} ({round(100*vazias/total_slots,1)}%)")


def main():
    for mid, info in MARKETS.items():
        try:
            analyze(mid, info["conditionId"], info["tokenYes"])
        except Exception as exc:  # noqa: BLE001
            print(f"  ERRO {mid}: {type(exc).__name__}: {exc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
