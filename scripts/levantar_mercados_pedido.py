"""Levantamento dos mercados restantes do `Pedido_Paulo_dados.md` (seções 2-4).

Roda contra a API real do Polymarket (Gamma /public-search + /events + CLOB
/prices-history) e mede, para cada família de mercado, o que a seção 4.2 pede:
existe? / 1ª data / última data / volume (do endpoint) / critério de resolução /
dias sem trade. Cobre M1, M3, M4, M6, M7, M8, M9 (M2 e M5 já foram medidos antes).

Também levanta:
  - Nota A: os buckets de um mês real de CPI (rótulos crus).
  - Nota B: o texto de resolução dos mercados de recessão (NBER vs técnico).
  - Nota C: o texto das rules de um mercado de bucket (terminal vs one-touch).

NÃO decide mapeamento mercado→ETF nem escolhe qual mercado usar — só reporta os
candidatos por volume (a seção 4.2 pede "indicar o binário-mãe por liquidez").
Nada é normalizado/interpolado: dado cru, campos crus.

Uso (terminal com rede — VPN ligada):
    python scripts/levantar_mercados_pedido.py
"""

import json
import sys
import time
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_ROOT / "data" / "raw" / "clob_exploracao"

GAMMA_URL = "https://gamma-api.polymarket.com"
CLOB_URL = "https://clob.polymarket.com"
TIMEOUT = 30

# Famílias de mercado do pedido → termos de busca no public-search.
FAMILIES = {
    "M1 CPI mensal (buckets)": ["cpi monthly inflation", "inflation monthly"],
    "M3 Trajetória do Fed": ["how many fed rate cuts 2025", "fed rate december 2025"],
    "M4 Recessão EUA": ["us recession 2025", "us recession nber"],
    "M6 Tarifas EUA x China": ["trump china tariffs", "tariffs on china"],
    "M7 Ação militar EUA/Israel x Irã": ["us strikes iran", "us military action iran"],
    "M8 Tributária (OBBB) / teto da dívida": ["reconciliation bill passed", "debt ceiling suspended"],
    "M9 Presidencial 2022 (midterms)": ["2022 senate control", "republicans win house 2022"],
}


def get(url, params=None):
    return requests.get(url, params=params, timeout=TIMEOUT)


def search_events(query):
    """public-search por tema; devolve lista de eventos (slug, volume)."""
    r = get(f"{GAMMA_URL}/public-search", {"q": query, "limit_per_type": 6})
    if not r.ok:
        return []
    return (r.json() or {}).get("events", []) or []


def fetch_event(slug):
    """Evento completo (com markets, description) — closed=true p/ resolvidos."""
    r = get(f"{GAMMA_URL}/events", {"slug": slug, "closed": "true"})
    ev = r.json() if r.ok else []
    if not ev:
        r = get(f"{GAMMA_URL}/events", {"slug": slug})  # tenta ativo
        ev = r.json() if r.ok else []
    return ev[0] if isinstance(ev, list) and ev else (ev if isinstance(ev, dict) else None)


def yes_token(market):
    raw = market.get("clobTokenIds")
    if not raw:
        return None
    ids = json.loads(raw) if isinstance(raw, str) else raw
    return ids[0] if ids else None


def price_stats(token_id):
    """1ª/última data, nº de pontos e lacunas (proxy de dias sem trade)."""
    r = get(f"{CLOB_URL}/prices-history",
            {"market": token_id, "interval": "all", "fidelity": 720})
    hist = (r.json() or {}).get("history", []) if r.ok else []
    if not hist:
        return None
    ts = sorted(p["t"] for p in hist if "t" in p)
    import datetime as dt
    lo, hi = dt.datetime.utcfromtimestamp(ts[0]), dt.datetime.utcfromtimestamp(ts[-1])
    span_snaps = max(1, int((ts[-1] - ts[0]) / 43200))  # snapshots esperados (12h)
    missing = span_snaps + 1 - len(ts)                  # snapshots ausentes
    steps = [b - a for a, b in zip(ts, ts[1:])]
    max_gap_days = (max(steps) / 86400) if steps else 0
    return {
        "primeira": lo.date().isoformat(),
        "ultima": hi.date().isoformat(),
        "n_pontos": len(ts),
        "snaps_ausentes_12h": max(0, missing),
        "maior_lacuna_dias": round(max_gap_days, 1),
    }


def market_volume(market, event):
    for k in ("volumeNum", "volume"):
        v = market.get(k) or event.get(k)
        if v not in (None, ""):
            try:
                return float(v)
            except (TypeError, ValueError):
                pass
    return None


def describe(text, n=280):
    t = (text or "").strip().replace("\n", " ")
    return (t[:n] + "…") if len(t) > n else t


def levantar_familia(nome, queries):
    print(f"\n{'='*70}\n### {nome}\n{'='*70}")
    # 1) coleta candidatos por volume (dedup por slug)
    cand = {}
    for q in queries:
        for ev in search_events(q):
            slug = ev.get("slug")
            if slug and slug not in cand:
                cand[slug] = float(ev.get("volume") or 0)
        time.sleep(0.2)
    if not cand:
        print("  NENHUM candidato encontrado.")
        return
    top = sorted(cand.items(), key=lambda kv: kv[1], reverse=True)[:5]
    print("Candidatos (por volume do evento, desc):")
    for slug, vol in top:
        print(f"  ${vol:>14,.0f}  {slug}")

    # 2) mede o de maior volume (o "binário-mãe" por liquidez)
    slug_primary = top[0][0]
    ev = fetch_event(slug_primary)
    if not ev:
        print(f"  (não consegui abrir o evento {slug_primary})")
        return
    print(f"\nMEDIÇÃO do primário: {slug_primary}")
    print(f"  título: {ev.get('title')}")
    print(f"  resolução (rules/description): {describe(ev.get('description'))}")
    print(f"  resolutionSource: {ev.get('resolutionSource') or '—'}")
    markets = ev.get("markets", [])
    # mercado com maior volume dentro do evento
    markets = sorted(markets, key=lambda m: float(m.get("volumeNum") or 0), reverse=True)
    for m in markets[:1]:
        tok = yes_token(m)
        vol = market_volume(m, ev)
        print(f"  mercado: {describe(m.get('question'), 90)}")
        print(f"    volume (endpoint): ${vol:,.0f}" if vol is not None else "    volume: ?")
        if tok:
            st = price_stats(tok)
            print(f"    série: {st}" if st else "    série: VAZIA")
    # lista dos demais mercados do evento (buckets, se houver)
    if len(markets) > 1:
        print(f"  ({len(markets)} mercados no evento — possível PMF/família)")


def nota_a_cpi():
    print(f"\n{'='*70}\n### NOTA A — buckets de um mês real de CPI\n{'='*70}")
    for slug in ("august-inflation-monthly", "july-inflation-monthly"):
        ev = fetch_event(slug)
        if ev and ev.get("markets"):
            print(f"Evento: {slug} | título: {ev.get('title')}")
            print(f"  resolução: {describe(ev.get('description'))}")
            print("  buckets (rótulos crus dos mercados):")
            for m in ev["markets"]:
                print(f"    - {m.get('question')}")
            return
    print("  (não achei um mês mensal aberto; ajustar slug)")


def nota_b_recessao():
    print(f"\n{'='*70}\n### NOTA B — critério de resolução dos mercados de recessão\n{'='*70}")
    for slug in ("us-recession-in-2025", "us-recession-announced-by-nber-before-june-2025"):
        ev = fetch_event(slug)
        if ev:
            print(f"\n{slug}:")
            print(f"  resolução: {describe(ev.get('description'), 500)}")
            print(f"  resolutionSource: {ev.get('resolutionSource') or '—'}")


def nota_c_onetouch():
    print(f"\n{'='*70}\n### NOTA C — terminal vs one-touch (mercado de bucket)\n{'='*70}")
    ev = fetch_event("august-inflation-monthly")
    if ev and ev.get("markets"):
        m = ev["markets"][0]
        print(f"Exemplo (CPI bucket): {m.get('question')}")
        print(f"  rules/description: {describe(m.get('description') or ev.get('description'), 500)}")
        txt = ((m.get("description") or ev.get("description")) or "").lower()
        print(f"  contém 'touch'? {'SIM' if 'touch' in txt else 'não'} | "
              f"'at any time'? {'SIM' if 'at any time' in txt else 'não'}")


def main():
    for nome, queries in FAMILIES.items():
        try:
            levantar_familia(nome, queries)
        except Exception as exc:  # noqa: BLE001
            print(f"  ERRO em {nome}: {type(exc).__name__}: {exc}")
    nota_a_cpi()
    nota_b_recessao()
    nota_c_onetouch()
    print("\n\nConcluído — transcrever para docs/RESPOSTA_Pedido_Paulo_dados.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
