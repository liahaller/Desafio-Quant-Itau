"""PEDIDO (Lia) — valor realizado do CPI (MoM) para os mercados-mês do Polymarket.

Junta o que a Gamma disse (cpi_rules_gamma.json: mês de ref, SA/NSA da rule,
bucket vencedor) com o CPI do FRED/ALFRED, e devolve por mês de referência:

  - CPIAUCSL (SA)  MoM %  revisado (série corrente) — ≥2 casas
  - CPIAUCNS (NSA) MoM %  revisado (série corrente) — ≥2 casas
  - CPIAUCSL (SA)  MoM %  FIRST-PRINT (ALFRED, vintage = dia do release)
  - CPIAUCNS (NSA) MoM %  FIRST-PRINT (ALFRED, vintage = dia do release)
  - bucket vencedor do mercado + checagem: round(first-print SA,1) ∈ bucket?

MoM % = variação percentual mês-a-mês calculada pelo próprio FRED (units=pch)
sobre o índice; para o first-print, aplicada sobre a vintage do dia do release
(ALFRED realtime_start=realtime_end=release_date). NÃO decide nada: SA vs NSA sai
da rule (coluna vinda da Gamma); só reporta os dois de qualquer forma.

Uso: .venv/bin/python scripts/pedido_cpi_realizado_fred.py
"""

import csv
import json
import sys
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW = REPO_ROOT / "data" / "raw"
SECRETS = REPO_ROOT / "config" / "secrets.json"
API = "https://api.stlouisfed.org/fred/series/observations"
TIMEOUT = 30

# Mês de referência (obs_date = 1º do mês) -> slug do mercado no clob.
# Ordem cronológica. abr/2025 e fev/2026 = buracos (sem mercado no Polymarket).
REF = [
    ("2024-12-01", "december-inflation-monthly"),
    ("2025-01-01", "january-inflation-monthly"),
    ("2025-02-01", "february-inflation-monthly"),
    ("2025-03-01", "march-inflation-monthly"),
    ("2025-05-01", "may-inflation-monthly"),
    ("2025-06-01", "june-inflation-monthly"),
    ("2025-07-01", "july-inflation-monthly"),
    ("2025-08-01", "august-inflation-monthly"),
    ("2025-09-01", "september-inflation-monthly"),
    ("2025-10-01", "october-inflation-monthly"),      # fantasma (ver aside)
    ("2025-11-01", "november-inflation-monthly"),
    ("2025-12-01", "december-inflation-us-monthly"),
    ("2026-01-01", "january-inflation-us-monthly"),
    ("2026-03-01", "march-inflation-us-monthly"),
    ("2026-04-01", "april-inflation-us-monthly"),
    ("2026-05-01", "may-inflation-us-monthly"),
    ("2026-06-01", "june-inflation-us-monthly-20260610151033433"),
    ("2026-07-01", "july-inflation-us-monthly-20260714151042665"),
]


def load_key():
    return json.loads(SECRETS.read_text())["fred_api_key"]


def load_release_dates():
    """mes_referencia (YYYY-MM-01) -> release_date, do calendário oficial do FRED."""
    out = {}
    import datetime as dt
    for r in csv.DictReader((RAW / "cpi_release_dates_fred.csv").read_text().splitlines()):
        mes = r["mes_referencia"]  # ex.: "December 2024"
        d = dt.datetime.strptime(mes, "%B %Y").strftime("%Y-%m-01")
        out[d] = r["release_date"]
    return out


def fred_pch(key, series, obs_date, vintage=None):
    """MoM % (units=pch) para obs_date. vintage=data → ALFRED (first-print)."""
    params = {
        "series_id": series, "units": "pch", "file_type": "json", "api_key": key,
        "observation_start": obs_date, "observation_end": obs_date,
    }
    if vintage:
        params["realtime_start"] = vintage
        params["realtime_end"] = vintage
    r = requests.get(API, params, timeout=TIMEOUT)
    if not r.ok:
        return None, f"HTTP {r.status_code}"
    obs = r.json().get("observations", [])
    if not obs:
        return None, "sem observação (não publicado nessa vintage)"
    v = obs[0]["value"]
    if v in (".", "", None):
        return None, "valor ausente"
    return float(v), None


def bucket_lo_hi(label):
    """Interpreta rótulo do bucket em intervalo [lo, hi] de MoM (pp)."""
    if not label:
        return None
    s = label.replace("%", "").replace("≤", "<=").replace("≥", ">=").strip()
    try:
        if s.startswith("<="):
            return (float("-inf"), float(s[2:]))
        if s.startswith(">="):
            return (float(s[2:]), float("inf"))
        v = float(s)
        return (v, v)  # bucket pontual de 0,1 pp (ex.: "0.3%")
    except ValueError:
        return None


def in_bucket(mom1, label):
    rng = bucket_lo_hi(label)
    if rng is None or mom1 is None:
        return None
    lo, hi = rng
    if lo == hi:  # bucket pontual: bate se arredondar ao mesmo décimo
        return abs(mom1 - lo) < 1e-9
    return lo <= mom1 <= hi


def main():
    key = load_key()
    rel = load_release_dates()
    gamma = {r["slug"]: r for r in json.loads((RAW / "cpi_rules_gamma.json").read_text())}
    rows = []
    for obs_date, slug in REF:
        g = gamma.get(slug, {})
        release = rel.get(obs_date)
        rec = {
            "mes_ref": obs_date,
            "slug": slug,
            "ajuste_regra": g.get("ajuste_sa_nsa"),
            "bucket_vencedor": g.get("bucket_vencedor"),
            "release_date": release,
        }
        # revisado (série corrente)
        rec["sa_rev"], rec["sa_rev_err"] = fred_pch(key, "CPIAUCSL", obs_date)
        rec["nsa_rev"], rec["nsa_rev_err"] = fred_pch(key, "CPIAUCNS", obs_date)
        # first-print (ALFRED, vintage = release)
        if release:
            rec["sa_fp"], rec["sa_fp_err"] = fred_pch(key, "CPIAUCSL", obs_date, release)
            rec["nsa_fp"], rec["nsa_fp_err"] = fred_pch(key, "CPIAUCNS", obs_date, release)
        else:
            rec["sa_fp"] = rec["nsa_fp"] = None
            rec["sa_fp_err"] = rec["nsa_fp_err"] = "sem release_date no calendário FRED"
        # checagem de bucket com o first-print SA arredondado a 1 casa
        sa_fp = rec["sa_fp"]
        rec["sa_fp_1dec"] = round(sa_fp, 1) if sa_fp is not None else None
        rec["bate_bucket"] = in_bucket(rec["sa_fp_1dec"], rec["bucket_vencedor"])
        rows.append(rec)
        print(f"  {obs_date} {slug[:34]:34} | SA fp={rec['sa_fp']} rev={rec['sa_rev']} "
              f"| NSA fp={rec['nsa_fp']} | venc={rec['bucket_vencedor']} bate={rec['bate_bucket']}",
              file=sys.stderr)
    (RAW / "cpi_realizado_mom.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(rows, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
