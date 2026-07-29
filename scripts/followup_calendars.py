"""FOLLOW-UP F7 — calendários FOMC e CPI (salva dois CSVs em data/raw/).

FOMC: raspa federalreserve.gov/monetarypolicy/fomccalendars.htm. A data exata do
anúncio vem do nome do PDF do statement (monetaryYYYYMMDD...) — medida, não
inferida. Reuniões futuras (sem statement) entram com a data = último dia do
intervalo do mês.

CPI: as datas de release do BLS estão bloqueadas por bot (HTTP 403). Rota usada =
as *rules* dos próprios mercados de CPI (fallback autorizado pelo pedido): o texto
traz "scheduled to be released on <data>, at <hora> ET" e o mês de referência.

NÃO decide fonte — só lista as candidatas (impressas no fim) e puxa pela que
funcionou. Campo indisponível = vazio.

Uso: .venv/bin/python scripts/followup_calendars.py
"""

import csv
import re
import sys
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW = REPO_ROOT / "data" / "raw"
G = "https://gamma-api.polymarket.com"
UA = {"User-Agent": "Mozilla/5.0"}
FOMC_URL = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"

MONTHS = {m: i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"], 1)}

CPI_SLUGS = [
    "january-inflation-monthly", "february-inflation-monthly",
    "march-inflation-monthly", "march-inflation-us-monthly",
    "april-inflation-us-monthly", "may-inflation-monthly", "may-inflation-us-monthly",
    "june-inflation-monthly", "june-inflation-us-monthly-20260610151033433",
    "july-inflation-monthly", "july-inflation-us-monthly-20260714151042665",
    "august-inflation-monthly", "september-inflation-monthly",
    "october-inflation-monthly", "november-inflation-monthly",
    "december-inflation-monthly", "december-inflation-us-monthly",
]


def scrape_fomc():
    html = requests.get(FOMC_URL, headers=UA, timeout=30).text
    rows = []
    # blocos por ano
    year_blocks = list(re.finditer(r"(\d{4})\s+FOMC Meetings", html))
    for i, ym in enumerate(year_blocks):
        year = int(ym.group(1))
        start = ym.end()
        end = year_blocks[i + 1].start() if i + 1 < len(year_blocks) else len(html)
        block = html[start:end]
        for mt in re.finditer(
                r'fomc-meeting__month[^>]*>(?:<strong>)?\s*([A-Za-z/]+)\s*'
                r'(?:</strong>)?</div>\s*<div class="fomc-meeting__date[^>]*>\s*'
                r'([^<]+?)\s*</div>(.*?)(?=fomc-meeting__month|$)', block, re.S):
            month_txt, date_txt, tail = mt.group(1), mt.group(2), mt.group(3)
            # "notation vote" não é reunião de decisão de juros (ex.: 22/08/2025
            # foi voto sobre o framework de longo prazo) — fora do calendário.
            if "notation" in date_txt.lower():
                continue
            # "*" na página do Fed = "Meeting associated with a Summary of
            # Economic Projections" (reunião com SEP + coletiva), NÃO reunião
            # extraordinária. Só marcamos esse detalhe; todas são regulares.
            com_sep = "*" in date_txt
            # data exata via PDF do statement (monetaryYYYYMMDD)
            pdf = re.search(r"monetary(\d{8})", tail)
            if pdf:
                d = pdf.group(1)
                date_iso = f"{d[:4]}-{d[4:6]}-{d[6:8]}"
            else:
                # sem statement (futuro): usa último dia do intervalo do mês
                nums = re.findall(r"\d+", date_txt)
                # meses podem vir como "Jan/Feb"; usa o último mês citado
                mo_name = re.split(r"[/-]", month_txt)[-1].strip()
                mo = MONTHS.get(mo_name.capitalize())
                if not (nums and mo):
                    continue
                date_iso = f"{year}-{mo:02d}-{int(nums[-1]):02d}"
            rows.append({
                "date": date_iso, "time_et": "",  # não consta no HTML
                "tipo": "reunião regular (SEP+coletiva)" if com_sep else "reunião regular",
                "fonte": FOMC_URL,
            })
    # filtra 2022+ e ordena/dedup
    rows = [r for r in rows if r["date"] >= "2022-01-01"]
    rows = sorted({r["date"]: r for r in rows}.values(), key=lambda r: r["date"])
    return rows


def scrape_cpi():
    rows = []
    for slug in CPI_SLUGS:
        r = requests.get(f"{G}/events", {"slug": slug, "closed": "true"}, timeout=30)
        ev = r.json() if r.ok else []
        if not ev:  # mercado vivo (ex.: jul/2026) não vem com closed=true
            ev = requests.get(f"{G}/events", {"slug": slug}, timeout=30).json() or []
        if not ev:
            continue
        desc = ev[0].get("description") or ""
        if len(desc) < 100:  # descrição vazia/curta: sem data para extrair
            print(f"  (aviso) {slug}: descrição sem regra de release ({len(desc)} chars) — pulado")
            continue
        rel = re.search(r"released on ([A-Za-z]+ \d{1,2}, \d{4}),? at ([\d:]+ ?[AP]M) ?ET", desc)
        ref = re.search(r"increased in ([A-Za-z]+ \d{4})", desc)
        if not ref:
            ref = re.search(r"report released for ([A-Za-z]+ \d{4})", desc)
        release_date = ""
        if rel:
            mo, day, yr = re.match(r"([A-Za-z]+) (\d{1,2}), (\d{4})", rel.group(1)).groups()
            release_date = f"{yr}-{MONTHS[mo]:02d}-{int(day):02d}"
        rows.append({
            "release_date": release_date,
            "time_et": rel.group(2) if rel else "",
            "mes_referencia": ref.group(1) if ref else "",
            "fonte": f"Polymarket rules ({slug})",
        })
    rows = [r for r in rows if r["release_date"]]
    return sorted(rows, key=lambda r: r["release_date"])


def write_csv(path, fields, rows):
    RAW.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def main():
    fomc = scrape_fomc()
    write_csv(RAW / "fomc_dates.csv", ["date", "time_et", "tipo", "fonte"], fomc)
    print(f"fomc_dates.csv: {len(fomc)} linhas ({fomc[0]['date']} → {fomc[-1]['date']})")
    for r in fomc:
        print(f"  {r['date']} | {r['tipo']}")

    cpi = scrape_cpi()
    write_csv(RAW / "cpi_release_dates.csv",
              ["release_date", "time_et", "mes_referencia", "fonte"], cpi)
    print(f"\ncpi_release_dates.csv: {len(cpi)} linhas ({cpi[0]['release_date']} → {cpi[-1]['release_date']})")
    for r in cpi:
        print(f"  {r['release_date']} {r['time_et']} | ref {r['mes_referencia']} | {r['fonte']}")

    print("\n=== FONTES CANDIDATAS (listadas, NÃO escolhidas) ===")
    print("FOMC: (1) federalreserve.gov/monetarypolicy/fomccalendars.htm — HTML, sem chave, raspagem [USADA];")
    print("      (2) statement PDFs monetaryYYYYMMDD — data exata do anúncio [usada p/ preencher];")
    print("      (3) FRED (não tem série pronta de datas do FOMC).")
    print("CPI:  (1) bls.gov/schedule/news_release/cpi.htm — HTML estruturado, sem chave, mas HTTP 403 (bot-block) [FALHOU];")
    print("      (2) rules dos mercados de CPI no Polymarket — traz data+hora ET+mês ref [USADA];")
    print("      (3) FRED release calendar (API, exige chave).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
