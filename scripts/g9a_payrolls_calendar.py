"""G9a — Calendário de divulgação dos payrolls (Employment Situation do BLS).

Fonte: FRED release/dates para o release id **50** (Employment Situation), via API
oficial `api.stlouisfed.org` (a página web `fred.stlouisfed.org` está bloqueada por
Akamai nesta rede; o BLS dá 403). A API **exige uma chave gratuita**.

A chave é lida de (nesta ordem) — NUNCA hardcoded, NUNCA versionada:
  1. variável de ambiente FRED_API_KEY
  2. arquivo config/secrets.json  ->  {"fred_api_key": "..."}   (git-ignored)

Sai um CSV com o MESMO cabeçalho do cpi_release_dates.csv:
  release_date, time_et, mes_referencia, fonte

Observações honestas (o que é medido vs. derivado):
  - `release_date`      : MEDIDO (data que o FRED declara para o release id 50).
  - `mes_referencia`    : DERIVADO — o Employment Situation de um mês sai no início do
                          mês seguinte, então mês_ref = mês(release) − 1. Regra
                          determinística e documentada, não uma escolha metodológica.
  - `time_et`           : o FRED **não** declara a hora. Preenchido "8:30 AM" (hora
                          padrão do BLS, confirmada pela regra dos mercados de payrolls
                          do Polymarket no G9b). Sinalizado na coluna `fonte`.
  - typo de ano         : se aparecer, mantém cru e sinaliza (não corrige).

Uso:
  export FRED_API_KEY=...        # ou config/secrets.json
  .venv/bin/python scripts/g9a_payrolls_calendar.py
"""

import csv
import json
import os
import sys
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW = REPO_ROOT / "data" / "raw"
SECRETS = REPO_ROOT / "config" / "secrets.json"
OUT = RAW / "payrolls_release_dates.csv"

API = "https://api.stlouisfed.org/fred/release/dates"
RELEASE_ID = 50  # Employment Situation (traz o nonfarm payrolls)
# Só interessa a era da PMF do Polymarket (2025+); pega desde dez/2024 para cobrir
# o mês de referência nov/2024 e ter margem. Ajustável.
FROM_RELEASE_DATE = "2025-01-01"

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]


def load_key():
    key = os.environ.get("FRED_API_KEY", "").strip()
    if key:
        return key, "env FRED_API_KEY"
    if SECRETS.exists():
        try:
            key = (json.loads(SECRETS.read_text()) or {}).get("fred_api_key", "").strip()
            if key:
                return key, "config/secrets.json"
        except json.JSONDecodeError:
            pass
    return None, None


def ref_month(release_iso):
    """Mês de referência = mês do release − 1 (Employment Situation reporta o mês anterior)."""
    y, m = int(release_iso[:4]), int(release_iso[5:7])
    m -= 1
    if m == 0:
        m, y = 12, y - 1
    return f"{MONTHS[m - 1]} {y}"


def main():
    key, origem = load_key()
    if not key:
        print("=== G9a — BLOQUEADO: falta a FRED API key ===")
        print("Como obter (grátis, ~2 min):")
        print("  1. Abra  https://fredaccount.stlouisfed.org/apikeys")
        print("  2. Crie a conta / faça login e clique em 'Request API Key'.")
        print("  3. Copie a chave (32 caracteres).")
        print("Depois, uma das duas opções:")
        print("  a) export FRED_API_KEY=<sua_chave>   e rode de novo; ou")
        print(f"  b) crie {SECRETS.relative_to(REPO_ROOT)} com "
              '{"fred_api_key": "<sua_chave>"}')
        return 2

    print(f"Chave carregada de: {origem}")
    params = {
        "release_id": RELEASE_ID,
        "api_key": key,
        "file_type": "json",
        "include_release_dates_with_no_data": "true",  # inclui datas futuras agendadas
        "sort_order": "asc",
        "limit": 10000,
    }
    r = requests.get(API, params=params, timeout=30)
    if not r.ok:
        print(f"ERRO {r.status_code} na API do FRED: {r.text[:300]}")
        return 1

    dates = [d["date"] for d in (r.json() or {}).get("release_dates", [])]
    dates = [d for d in dates if d >= FROM_RELEASE_DATE]

    import datetime as _dt

    def _d(s):
        return _dt.date.fromisoformat(s)

    rows = []
    seen_ref = {}
    prev = None
    for d in dates:
        ref = ref_month(d)
        base_fonte = (f"FRED release/dates id={RELEASE_ID} (Employment Situation); "
                      "hora=padrão BLS 8:30 ET")
        row = {"release_date": d, "time_et": "8:30 AM", "mes_referencia": ref,
               "fonte": base_fonte}
        # sinaliza colisão de mês de referência (possível typo de ano na fonte)
        if ref in seen_ref:
            row["fonte"] += "  [ATENCAO: mes_referencia duplicado — conferir typo]"
        # sinaliza buraco no calendário (gap > 45 dias = mês pulado; ex.: shutdown 2025).
        # Nesse caso a derivação mes_ref = mes(release)-1 NAO bate 1:1 — Felipe corrige.
        if prev is not None and (_d(d) - _d(prev)).days > 45:
            row["fonte"] += (f"  [ATENCAO: gap de {(_d(d) - _d(prev)).days} dias desde "
                             f"{prev} (mes de referencia pulado/remanejado — provavel "
                             "shutdown 2025; mes_referencia DERIVADO pode nao bater, CRU)]")
        seen_ref[ref] = d
        prev = d
        rows.append(row)

    RAW.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["release_date", "time_et",
                                          "mes_referencia", "fonte"])
        w.writeheader()
        w.writerows(rows)

    print("\n=== G9a — CALENDÁRIO DE PAYROLLS ===")
    print(f"Fonte usada:            {API}?release_id={RELEASE_ID}   (precisa de chave? SIM)")
    print(f"Arquivo salvo:          {OUT.relative_to(REPO_ROOT)}")
    print(f"Nº de linhas:           {len(rows)}")
    if rows:
        print(f"Janela:                 {rows[0]['mes_referencia']} → {rows[-1]['mes_referencia']}")
    print("Colunas:                release_date, time_et, mes_referencia, fonte")
    print("Hora de divulgação:     8:30 AM ET (padrão BLS; FRED não declara — confirmado via G9b)")
    dups = [k for k, v in seen_ref.items() if list(r["mes_referencia"] for r in rows).count(k) > 1]
    print(f"Meses faltando no meio:  (checar contra o calendário mensal; typos sinalizados: "
          f"{dups or 'nenhum'})")
    print()
    for row in rows:
        print(f"  {row['release_date']}  {row['time_et']}  | ref {row['mes_referencia']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
