"""G10c — Calendário OFICIAL de divulgação do CPI (FRED release/dates).

Substitui a origem do calendário do CPI: hoje o `cpi_release_dates.csv` (15 linhas,
2025→2026) vem das REGRAS dos mercados do Polymarket, então só existe onde existe
mercado. Aqui o calendário vem da fonte oficial via API do FRED (a mesma que
destravou o G9a), cobrindo toda a história pública do CPI.

O `release_id` do CPI NÃO é chutado: o script lista `/fred/releases` e acha o release
cujo nome é exatamente "Consumer Price Index" (reporta como confirmou). No G9a o de
payrolls era 50; o do CPI é outro.

Sai um CSV com o MESMO cabeçalho do cpi_release_dates.csv:
  release_date, time_et, mes_referencia, fonte

O que é MEDIDO vs. DERIVADO:
  - release_date   : MEDIDO (data que o FRED declara para o release do CPI).
  - mes_referencia : DERIVADO — o CPI de um mês sai no mês seguinte, então
                     mês_ref = mês(release) − 1. Regra determinística e marcada
                     como DERIVADA na coluna `fonte`.
  - time_et        : o FRED NÃO declara a hora. Preenchido "8:30 AM" (padrão BLS),
                     sinalizado na coluna `fonte`.

NÃO sobrescreve o cpi_release_dates.csv — salva ao lado (cpi_release_dates_fred.csv).
Troca do arquivo que o backtest lê é decisão do grupo, não efeito colateral daqui.

A chave é lida de (nesta ordem): env FRED_API_KEY  ->  config/secrets.json.

Uso: .venv/bin/python scripts/g10c_cpi_calendar.py
"""

import csv
import datetime as dt
import json
import os
import sys
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW = REPO_ROOT / "data" / "raw"
SECRETS = REPO_ROOT / "config" / "secrets.json"
CURRENT = RAW / "cpi_release_dates.csv"          # 15 linhas, origem Polymarket
OUT = RAW / "cpi_release_dates_fred.csv"          # ao lado, NÃO sobrescreve

RELEASES = "https://api.stlouisfed.org/fred/releases"
RELEASE_DATES = "https://api.stlouisfed.org/fred/release/dates"
CPI_NAME = "Consumer Price Index"                 # nome exato a casar em /fred/releases

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
    """Mês de referência = mês do release − 1 (o CPI reporta o mês anterior)."""
    y, m = int(release_iso[:4]), int(release_iso[5:7])
    m -= 1
    if m == 0:
        m, y = 12, y - 1
    return f"{MONTHS[m - 1]} {y}"


def find_cpi_release_id(key):
    """Lista /fred/releases e acha o release cujo nome é exatamente CPI_NAME."""
    params = {"api_key": key, "file_type": "json", "limit": 1000}
    r = requests.get(RELEASES, params=params, timeout=60)
    if not r.ok:
        return None, f"ERRO {r.status_code}: {r.text[:200]}", []
    releases = (r.json() or {}).get("releases", []) or []
    exatos = [rel for rel in releases if (rel.get("name") or "").strip() == CPI_NAME]
    candidatos = [(rel["id"], rel["name"]) for rel in releases
                  if "consumer price index" in (rel.get("name") or "").lower()]
    if exatos:
        return exatos[0]["id"], "nome exato 'Consumer Price Index' em /fred/releases", candidatos
    return None, "nenhum release com nome exato 'Consumer Price Index'", candidatos


def main():
    key, origem = load_key()
    if not key:
        print("=== G10c — BLOQUEADO: falta a FRED API key ===")
        print("Ver config/secrets.json  ->  {\"fred_api_key\": \"...\"}  (git-ignored)")
        return 2
    print(f"Chave carregada de: {origem}")

    rid, como, candidatos = find_cpi_release_id(key)
    if rid is None:
        print(f"Não achei o release_id do CPI: {como}")
        print(f"Candidatos (contêm 'consumer price index'): {candidatos}")
        return 1
    print(f"release_id do CPI: {rid}  ({como}; candidatos={candidatos})")

    params = {
        "release_id": rid,
        "api_key": key,
        "file_type": "json",
        "include_release_dates_with_no_data": "true",  # inclui datas futuras agendadas
        "sort_order": "asc",
        "limit": 10000,
    }
    r = requests.get(RELEASE_DATES, params=params, timeout=60)
    if not r.ok:
        print(f"ERRO {r.status_code} em release/dates: {r.text[:300]}")
        return 1
    dates = [d["date"] for d in (r.json() or {}).get("release_dates", [])]
    dates = sorted(set(dates))

    base_fonte = (f"FRED release/dates id={rid} (Consumer Price Index); "
                  "hora=padrão BLS 8:30 ET (nao declarada pelo FRED); "
                  "mes_referencia DERIVADO (mes do release - 1)")
    rows = [{"release_date": d, "time_et": "8:30 AM",
             "mes_referencia": ref_month(d), "fonte": base_fonte} for d in dates]

    RAW.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["release_date", "time_et",
                                          "mes_referencia", "fonte"])
        w.writeheader()
        w.writerows(rows)

    # Conferência com o CSV atual (15 linhas): quantas datas batem, quais divergem.
    fred_dates = {d for d in dates}
    atual = []
    if CURRENT.exists():
        with open(CURRENT, encoding="utf-8") as f:
            atual = list(csv.DictReader(f))
    iguais, divergem = [], []
    for a in atual:
        rd = a["release_date"]
        if rd in fred_dates:
            iguais.append(rd)
        else:
            divergem.append(rd)

    print("\n=== G10c — CALENDÁRIO OFICIAL DO CPI ===")
    print(f"Fonte usada:            {RELEASE_DATES}?release_id={rid}")
    print(f"release_id usado:       {rid}   (confirmado: {como})")
    print(f"Arquivo salvo:          {OUT.relative_to(REPO_ROOT)}")
    print(f"Nº de linhas:           {len(rows)}")
    if rows:
        print(f"Janela:                 {rows[0]['release_date']} → {rows[-1]['release_date']}")
    print("Colunas:                release_date, time_et, mes_referencia, fonte")
    print(f"Bate com o CSV atual?:  {len(iguais)}/{len(atual)} datas idênticas ao FRED"
          + (f"; DIVERGEM: {divergem}" if divergem else "; nenhuma diverge"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
