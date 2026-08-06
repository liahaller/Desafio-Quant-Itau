"""G9b — Varredura dos mercados de payrolls no Polymarket.

Mesmo procedimento do G4: a busca escrita ao lado é parte da resposta, e um
negativo é resposta completa (o Polymarket não abriu mercado daquele mês).

Para cada termo de busca (`payrolls`, `nonfarm`, `jobs report`, `unemployment
rate`) chama o /public-search da Gamma, junta os eventos, e para cada evento
candidato de "relatório mensal de empregos" inspeciona: nº de buckets (ou
binário), volume, 1ª/última data da série (salvando a série crua), e tenta
extrair o mês de referência + a data de release do texto da regra.

NÃO decide, NÃO normaliza. Campo não medido vai como '?'.

Uso: .venv/bin/python scripts/g9b_payrolls_polymarket.py
"""

import csv
import datetime as dt
import json
import re
import sys
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_ROOT / "data" / "raw" / "clob_exploracao"
SUMMARY_CSV = REPO_ROOT / "data" / "raw" / "payrolls_polymarket_markets.csv"
G = "https://gamma-api.polymarket.com"
CLOB = "https://clob.polymarket.com"
TIMEOUT = 30

# Termos sugeridos no pedido — a busca faz parte da resposta.
SEARCH_TERMS = ["payrolls", "nonfarm", "jobs report", "unemployment rate"]

# Janela de referência a cobrir (era da PMF do Polymarket: 2025 em diante).
FIRST_REF = (2025, 1)
LAST_REF = (2026, 8)

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]

# Palavras que indicam um mercado de relatório MENSAL de emprego (não meta-
# mercados tipo "BLS vai parar de reportar?").
JOB_HINTS = ("payroll", "nonfarm", "jobs report", "jobs added", "jobs number",
             "unemployment rate", "employment situation", "jobs created")
META_HINTS = ("stop reporting", "fire ", "fired", "commissioner", "revision")
# Mercados de emprego de OUTROS países — não são o Employment Situation dos EUA.
FOREIGN_HINTS = ("japan", "mexico", "brazil", "u.k", "uk", "canada",
                 "india", "indian", "german", "euro", "china")


def get(url, params=None):
    return requests.get(url, params=params, timeout=TIMEOUT)


def public_search(q):
    r = get(f"{G}/public-search", {"q": q, "limit_per_type": 20})
    if not r.ok:
        return []
    evs = (r.json() or {}).get("events", []) or []
    return [(e.get("slug"), e.get("title"), e.get("volume")) for e in evs]


def fetch_event(slug):
    r = get(f"{G}/events", {"slug": slug, "closed": "true"})
    ev = r.json() if r.ok else []
    if not ev:
        r = get(f"{G}/events", {"slug": slug})
        ev = r.json() if r.ok else []
    if isinstance(ev, list) and ev:
        return ev[0]
    return ev if isinstance(ev, dict) and ev else None


def tokens(m):
    raw = m.get("clobTokenIds")
    if not raw:
        return []
    return json.loads(raw) if isinstance(raw, str) else raw


def hist(tok, cache_path=None):
    """Série crua do token. Usa cache em disco se já existir (re-run rápido)."""
    if cache_path is not None and cache_path.exists():
        raw = cache_path.read_text(encoding="utf-8")
        try:
            h = (json.loads(raw) or {}).get("history", [])
        except json.JSONDecodeError:
            h = []
        return h, raw
    r = get(f"{CLOB}/prices-history", {"market": tok, "interval": "all", "fidelity": 720})
    return ((r.json() or {}).get("history", []) if r.ok else []), (r.text if r.ok else "")


def slugify(s):
    return "".join(c if c.isalnum() else "-" for c in (s or "").lower())[:50].strip("-")


def parse_rule(desc):
    """Extrai (mes_referencia, release_date, hora_et) do texto da regra, se houver."""
    ref = re.search(r"for ([A-Za-z]+ \d{4})", desc or "")
    if not ref:
        ref = re.search(r"in ([A-Za-z]+ \d{4})", desc or "")
    rel = re.search(r"released on ([A-Za-z]+ \d{1,2}, \d{4}),? at ([\d:]+ ?[AP]M) ?ET", desc or "")
    rel_iso, hora = "?", "?"
    if rel:
        mo, day, yr = re.match(r"([A-Za-z]+) (\d{1,2}), (\d{4})", rel.group(1)).groups()
        rel_iso = f"{yr}-{MONTHS.index(mo) + 1:02d}-{int(day):02d}"
        hora = rel.group(2)
    return (ref.group(1) if ref else "?"), rel_iso, hora


def slug_month(slug, title):
    """Nome do mês de referência a partir do slug/título (o ano vem da série)."""
    text = f"{slug} {title}".lower()
    for i, name in enumerate(MONTHS):
        if name.lower() in text:
            return i + 1  # 1..12
    return None


def ref_from_series(mo, first_iso):
    """Mês de referência = nome-do-mês (do slug) + ano (inferido da 1ª data da
    série). Escolhe o ano tal que o mês de referência caia por volta do início
    da negociação — o mercado negocia durante o mês de referência e resolve no
    release (início do mês seguinte)."""
    if not mo or first_iso in ("?", None):
        return "?"
    fy, fm = int(first_iso[:4]), int(first_iso[5:7])
    year = fy
    # série que começa em jan p/ um mercado de dezembro => dezembro do ano anterior
    if mo == 12 and fm == 1:
        year = fy - 1
    # série que começa em dez p/ um mercado de janeiro => janeiro do ano seguinte
    elif mo == 1 and fm == 12:
        year = fy + 1
    return f"{MONTHS[mo - 1]} {year}"


def inspect_event(slug, title, vol):
    ev = fetch_event(slug)
    if not ev:
        print(f"       (evento {slug} não abriu no /events)")
        return None
    desc = ev.get("description") or ""
    markets = ev.get("markets", []) or []
    n_buckets = len(markets)
    estrutura = "binário (Yes/No)" if n_buckets == 1 else f"{n_buckets} buckets"
    _, rel_iso, hora = parse_rule(desc)  # release/hora do texto da regra (se houver)

    # série crua do 1º bucket -> 1ª/última data (com cache em disco)
    first = last = "?"
    for m in markets:
        toks = tokens(m)
        if not toks:
            continue
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        cache = RAW_DIR / f"G9_payrolls_{slugify(slug)}_{toks[0]}.json"
        h, raw = hist(toks[0], cache_path=cache)
        cache.write_text(raw, encoding="utf-8")
        ts = sorted(p["t"] for p in h if "t" in p)
        if ts and first == "?":
            first = dt.datetime.utcfromtimestamp(ts[0]).date().isoformat()
            last = dt.datetime.utcfromtimestamp(ts[-1]).date().isoformat()

    # mês de referência: nome do slug + ano da série (robusto ao ano do CPI/G4)
    ref = ref_from_series(slug_month(slug, title), first)

    print(f"     >>> slug        : {slug}")
    print(f"         title       : {title}")
    print(f"         estrutura   : {estrutura}")
    print(f"         volume      : {vol}  (evento: {ev.get('volume')})")
    print(f"         mês ref     : {ref}")
    print(f"         release     : {rel_iso}  {hora} ET")
    print(f"         série datas : {first} -> {last}")
    return {"slug": slug, "title": title, "estrutura": estrutura, "n_buckets": n_buckets,
            "volume": ev.get("volume"), "mes_ref": ref, "release": rel_iso,
            "hora": hora, "first": first, "last": last}


def family(slug, title):
    """Classifica a família do mercado de emprego dos EUA."""
    text = f"{slug} {title}".lower()
    if "jobs added" in text or "how-many-jobs-added" in text:
        return "nfp_jobs_added"      # nº de payrolls (buckets) — análogo direto ao CPI
    if "prints negative" in text:
        return "nfp_prints_negative"  # binário sobre o sinal do payroll
    if "unemployment rate" in text:
        return "unemployment_rate"    # taxa de desemprego (buckets), mesmo relatório
    if "released by" in text or "employment situation report be released" in text \
            or "during government shutdown" in text:
        return "release_timing_meta"  # meta: se/quando o relatório sai (não é PMF do número)
    return "outro"


def is_job_market(slug, title):
    text = f"{slug} {title}".lower()
    if any(h in text for h in META_HINTS):
        return False
    if any(h in text for h in FOREIGN_HINTS):  # emprego de outros países: fora
        return False
    return any(h in text for h in JOB_HINTS)


def main():
    print("=" * 72)
    print("G9b — VARREDURA DE MERCADOS DE PAYROLLS NO POLYMARKET")
    print("=" * 72)

    discovered = {}  # slug -> (title, vol, termos_que_acharam)
    for term in SEARCH_TERMS:
        hits = public_search(term)
        print(f"\n[/public-search q='{term}'] -> {len(hits)} eventos:")
        for slug, title, vol in hits:
            flag = "JOBS" if is_job_market(slug, title) else "    "
            print(f"   [{flag}] {slug}  | {title}  | vol={vol}")
            if slug:
                if slug not in discovered:
                    discovered[slug] = [title, vol, []]
                discovered[slug][2].append(term)

    job_events = {s: v for s, v in discovered.items() if is_job_market(s, v[0])}
    print(f"\n{'=' * 72}\nEVENTOS DE RELATÓRIO DE EMPREGO (filtrados): {len(job_events)}")
    print("=" * 72)

    results = []
    for slug, (title, vol, terms) in job_events.items():
        print(f"\n--- {slug}  (achado por: {', '.join(terms)}) ---")
        r = inspect_event(slug, title, vol)
        if r:
            r["found_by"] = ";".join(terms)
            r["familia"] = family(slug, title)
            results.append(r)

    # CSV-resumo (dado medido cru; ano/mês inferido da série, sinalizado no doc)
    fields = ["mes_referencia", "familia", "slug", "title", "estrutura", "n_buckets",
              "volume", "release_regra", "hora_et_regra", "serie_first", "serie_last",
              "found_by"]
    with open(SUMMARY_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(fields)
        for r in sorted(results, key=lambda x: (x["mes_ref"], x["familia"])):
            w.writerow([r["mes_ref"], r["familia"], r["slug"], r["title"], r["estrutura"],
                        r["n_buckets"], r["volume"], r["release"], r["hora"],
                        r["first"], r["last"], r["found_by"]])
    print(f"\nCSV-resumo salvo: {SUMMARY_CSV.relative_to(REPO_ROOT)} ({len(results)} linhas)")

    # Cobertura mês a mês da janela de referência
    print(f"\n{'=' * 72}\nCOBERTURA POR MÊS DE REFERÊNCIA ({FIRST_REF} -> {LAST_REF})")
    print("=" * 72)
    by_ref = {}
    for r in results:
        by_ref.setdefault(r["mes_ref"], []).append(r)
    y, mth = FIRST_REF
    while (y, mth) <= LAST_REF:
        label = f"{MONTHS[mth - 1]} {y}"
        hits = by_ref.get(label, [])
        status = "SIM" if hits else "NAO"
        extra = ""
        if hits:
            extra = " | " + "; ".join(f"{h['slug']} ({h['estrutura']}, vol={h['volume']}, "
                                      f"série {h['first']}->{h['last']})" for h in hits)
        print(f"   {label:<16} {status}{extra}")
        mth += 1
        if mth > 12:
            mth, y = 1, y + 1

    print("\nConcluído — G9b.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
