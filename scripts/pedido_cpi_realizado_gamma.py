"""PEDIDO (Lia) — coleta na Gamma das regras e resolução dos mercados-mês de CPI.

Para cada evento de CPI mensal dos EUA no clob_exploracao (dez/2024 → jul/2026):
  - mes_referencia   : parseado da própria rule ("increased in <Month Year>")
  - ajuste           : SA / NSA / ? — lido do texto da rule (não decidido aqui)
  - precisao_regra   : casas decimais que a rule diz usar para resolver
  - release_agendada : data de release citada na rule
  - bucket_vencedor  : groupItemTitle do market com outcomePrices Yes==1
  - buckets          : rótulos crus na ordem
  - uma_status       : umaResolutionStatus do market vencedor (ou do evento)
  - volume, closed

NÃO decide, NÃO normaliza. Campo ausente = None. Fonte da verdade da SA/NSA é a
rule do próprio mercado (é o que resolve na prática), conforme o pedido.

Saída: imprime JSON em stdout (consumido pelo passo do FRED) e salva cópia crua
das descrições em data/raw/cpi_rules_gamma.json para auditoria.

Uso: .venv/bin/python scripts/pedido_cpi_realizado_gamma.py
"""

import json
import re
import sys
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW = REPO_ROOT / "data" / "raw"
G = "https://gamma-api.polymarket.com"
TIMEOUT = 30

# União dos slugs da varredura F8 (followup_cpi_sweep) + buracos do G4 achados
# (jan/2026, fev/2026). O ano/mes de referência sai da rule, não do slug.
SLUGS = [
    "december-inflation-monthly",          # dez/2024
    "january-inflation-monthly",           # jan/2025
    "february-inflation-monthly",          # fev/2025
    "march-inflation-monthly",             # mar/2025
    # abril/2025 = buraco real (sem mercado) — G4
    "may-inflation-monthly",               # mai/2025
    "june-inflation-monthly",              # jun/2025
    "july-inflation-monthly",              # jul/2025
    "august-inflation-monthly",            # ago/2025
    "september-inflation-monthly",         # set/2025
    "october-inflation-monthly",           # out/2025 (fantasma)
    "november-inflation-monthly",          # nov/2025
    "december-inflation-us-monthly",       # dez/2025
    "january-inflation-us-monthly",        # jan/2026 (G4)
    "february-inflation-us-monthly",       # fev/2026 (G4)
    "march-inflation-us-monthly",          # mar/2026
    "april-inflation-us-monthly",          # abr/2026
    "may-inflation-us-monthly",            # mai/2026
    "june-inflation-us-monthly-20260610151033433",   # jun/2026
    "july-inflation-us-monthly-20260714151042665",   # jul/2026
]

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
MONTH_RE = "|".join(MONTHS)


def get(url, params=None):
    return requests.get(url, params=params, timeout=TIMEOUT)


def fetch_event(slug):
    for params in ({"slug": slug, "closed": "true"}, {"slug": slug}):
        r = get(f"{G}/events", params)
        if not r.ok:
            continue
        ev = r.json()
        ev = ev[0] if isinstance(ev, list) and ev else (ev if isinstance(ev, dict) and ev.get("slug") else None)
        if ev:
            return ev
    return None


def parse_ref_month(desc):
    """Mês de referência: 'increased in March 2025' / 'for March 2025'."""
    if not desc:
        return None
    m = re.search(rf"increased in ({MONTH_RE})\s+(\d{{4}})", desc)
    if not m:
        m = re.search(rf"released for ({MONTH_RE})\s+(\d{{4}})", desc)
    if not m:
        m = re.search(rf"report(?:ed)? for ({MONTH_RE})\s+(\d{{4}})", desc)
    return f"{m.group(1)} {m.group(2)}" if m else None


def parse_adjustment(desc):
    if not desc:
        return None
    low = desc.lower()
    if "not seasonally adjusted" in low or "non-seasonally adjusted" in low:
        return "NSA"
    if "seasonally adjusted" in low:
        return "SA"
    return "?"


def parse_precision(desc):
    """Casas decimais que a rule declara usar para resolver."""
    if not desc:
        return None
    if re.search(r"one decimal", desc, re.I):
        return "1 casa (rule)"
    m = re.search(r"(\w+) decimal", desc, re.I)
    return m.group(0) if m else "?"


def parse_release(desc):
    if not desc:
        return None
    m = re.search(rf"released on ({MONTH_RE})\s+(\d{{1,2}}),\s+(\d{{4}})", desc)
    return f"{m.group(1)} {m.group(2)}, {m.group(3)}" if m else None


def winning_bucket(markets):
    """Bucket com Yes resolvido em 1. Retorna (label, todos_status)."""
    win = None
    for mk in markets:
        try:
            prices = json.loads(mk.get("outcomePrices") or "[]")
        except Exception:
            prices = mk.get("outcomePrices") or []
        yes = prices[0] if prices else None
        if str(yes) == "1":
            win = mk.get("groupItemTitle") or mk.get("question")
    return win


def process(slug):
    ev = fetch_event(slug)
    if not ev:
        return {"slug": slug, "erro": "evento não abriu na Gamma"}
    desc = ev.get("description")
    markets = ev.get("markets", []) or []
    buckets = [mk.get("groupItemTitle") or mk.get("question") for mk in markets]
    uma = [mk.get("umaResolutionStatus") for mk in markets]
    return {
        "slug": slug,
        "title": ev.get("title"),
        "mes_referencia": parse_ref_month(desc),
        "ajuste_sa_nsa": parse_adjustment(desc),
        "precisao_regra": parse_precision(desc),
        "release_agendada": parse_release(desc),
        "bucket_vencedor": winning_bucket(markets),
        "buckets": buckets,
        "n_buckets": len(markets),
        "uma_status": sorted(set(u for u in uma if u)),
        "closed": ev.get("closed"),
        "volume": ev.get("volume"),
        "description": desc,
    }


def main():
    out = []
    for slug in SLUGS:
        try:
            rec = process(slug)
        except Exception as exc:  # noqa: BLE001
            rec = {"slug": slug, "erro": f"{type(exc).__name__}: {exc}"}
        out.append(rec)
        tag = rec.get("mes_referencia") or rec.get("erro")
        print(f"  {slug}: {tag} | {rec.get('ajuste_sa_nsa')} | venc={rec.get('bucket_vencedor')} | {rec.get('precisao_regra')}", file=sys.stderr)
    (RAW / "cpi_rules_gamma.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
