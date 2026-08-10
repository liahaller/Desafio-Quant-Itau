"""G5 — Série de volume no tempo (spec da Lia), derivada do data-api /trades.

Escopo: os mercados das views ATIVAS (2.2 inflação, 2.3 Fed reunião, B
trajetória do Fed).
  - 2.2: famílias CPI_* e M1_cpi_monthly_* (em data/raw/clob_exploracao/)
  - B  : M3_fed_trajectory_* (as faixas de cortes em 2025, em clob_exploracao/)
  - 2.3: as 76 faixas × reunião do FOMC, lidas do
         data/polymarket_fed_reunioes.parquet (grid de 12h e conditionId vêm do
         próprio parquet que a view 2.3 consome — garante alinhamento de slot 1:1
         com a probabilidade). Requer o conditionId já no parquet (rodar antes o
         scripts/g5b_fomc_conditionid.py). A família CPI/M1/M3 continua vindo dos
         .json de clob_exploracao; os arquivos M2_fomc_* NÃO são mais lidos (o
         parquet cobre o FOMC inteiro, sem duplicar).

Para cada mercado (um conditionId por bucket):
  1. resolve o conditionId a partir do tokenId do nome do arquivo (Gamma
     ?clob_token_ids=), com cache em disco;
  2. pagina o data-api /trades até o TETO da API (offset<=10000, limit 10000 =>
     no máximo os ~20.000 trades MAIS RECENTES — achado do F4);
  3. agrega por slot de 12h (passo nativo, = prices-history fidelity=720):
       notional_usd = Σ (size × price) dos trades no slot
       n_trades     = contagem de trades no slot
  4. t_cobertura_min = timestamp do trade MAIS ANTIGO alcançado (um por mercado).
     Regra do slot ANTES do t_cobertura_min (Decisão 12 do Paulo, respondida pela
     Lia no FOLLOWUP5 — separar os dois casos):
       - mercado CAPADO (bateu_cap): NaN — o dado existe mas o /trades não alcança
         lá; é ignorância nossa, propaga como "sem dado" (não vira 0 falso);
       - mercado NÃO capado: 0 — o /trades alcançou o 1º trade real; antes dele
         sabe-se que ninguém negociou, é fato do mercado (volume zero legítimo).
     DEPOIS do t_cobertura_min, slot sem trade é sempre 0 legítimo.

O grid de 12h de cada mercado vem da própria série /prices-history já baixada
(os arquivos .json em clob_exploracao) — não re-baixa preço.

NÃO decide nada, NÃO normaliza: entrega notional E contagem crus, os dois.

Saídas:
  data/raw/g5_volume_no_tempo.csv    — long: view, mercado, conditionId, slot_utc,
                                        notional_usd, n_trades (vazio = NaN)
  data/raw/g5_volume_cobertura.csv   — por mercado: t_cobertura_min, bateu_cap_20k, ...

Uso: .venv/bin/python scripts/g5_volume_no_tempo.py
"""

import csv
import datetime as dt
import json
import re
import sys
import time
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parents[1]
CLOB_DIR = REPO_ROOT / "data" / "raw" / "clob_exploracao"
RAW_DIR = REPO_ROOT / "data" / "raw"
CACHE = RAW_DIR / "g5_cache"  # conditionId + agregação por mercado (retomável)
REUNIOES_PATH = REPO_ROOT / "data" / "polymarket_fed_reunioes.parquet"  # view 2.3

GAMMA = "https://gamma-api.polymarket.com/markets"
DATA_API = "https://data-api.polymarket.com/trades"
TIMEOUT = 90
DELAY = 0.2
SLOT = 43200  # 12h em segundos (boundaries 00:00 e 12:00 UTC)
CAP = 20000   # teto do /trades (2 páginas de 10000)


def scope_view(fname):
    if fname.startswith("CPI_") or fname.startswith("M1_"):
        return "2.2"
    if fname.startswith("M2_"):
        return "2.3"
    if fname.startswith("M3_"):
        return "B"
    return None


def market_name(fname):
    """Nome legível: tira o tokenId final e a extensão."""
    return re.sub(r"_\d{40,}(_NO)?\.json$", "", fname)


def token_of(fname):
    m = re.search(r"_(\d{40,})(?:_NO)?\.json$", fname)
    return m.group(1) if m else None


def slot_start(ts):
    return ts - (ts % SLOT)


GAMMA_EVENTS = "https://gamma-api.polymarket.com/events"
_EVENT_CACHE = {}  # event_slug -> [markets] (evita re-chamar /events por bucket do mesmo mês)

# Override de resolução para a série M (nomes que não carregam slug de evento).
# ("event", slug) => casa o tokenId nos markets do evento;
# ("market", slug) => conditionId direto do market.
M_OVERRIDE = {
    "M1_cpi_monthly": ("event", "july-inflation-monthly"),
    "M3_fed_trajectory": ("event", "how-many-fed-rate-cuts-in-2025"),
    "M2_fomc": ("market",
                "fed-decreases-interest-rates-by-50-bps-after-september-2025-meeting"),
}


def event_slug_of(fname):
    """Slug do EVENTO no nome do arquivo CPI: o segmento imediatamente antes de
    '_will' (cobre tanto CPI_<ev>_will... quanto CPI_G4_<mes>_<ev>_will...)."""
    if not fname.startswith("CPI_"):
        return None
    head = fname.split("_will", 1)[0]
    return head.split("_")[-1] or None


def _event_markets(slug, sess):
    if slug not in _EVENT_CACHE:
        time.sleep(DELAY)
        re_ = sess.get(GAMMA_EVENTS, params={"slug": slug}, timeout=TIMEOUT)
        _EVENT_CACHE[slug] = (re_.json()[0].get("markets", [])
                              if re_.ok and re_.json() else [])
    return _EVENT_CACHE[slug]


def _match_token_in_event(slug, token, sess):
    for m in _event_markets(slug, sess):
        if token in (m.get("clobTokenIds") or ""):
            return m.get("conditionId")
    return None


def resolve_condition_id(token, fname, sess):
    """Tier 1: Gamma ?clob_token_ids (mercados novos). Tier 2: resolve pelo
    EVENTO e casa o tokenId em clobTokenIds — via slug no nome (CPI) ou via
    M_OVERRIDE (série M)."""
    r = sess.get(GAMMA, params={"clob_token_ids": token}, timeout=TIMEOUT)
    if r.ok:
        j = r.json()
        if isinstance(j, list) and j:
            return j[0].get("conditionId")

    # Tier 2 — série M com override explícito
    for prefix, (kind, slug) in M_OVERRIDE.items():
        if fname.startswith(prefix):
            if kind == "market":
                for extra in ({}, {"closed": "true"}):
                    time.sleep(DELAY)
                    p = {"slug": slug}
                    p.update(extra)
                    rm = sess.get(GAMMA, params=p, timeout=TIMEOUT)
                    if rm.ok and rm.json():
                        return rm.json()[0].get("conditionId")
                return None
            return _match_token_in_event(slug, token, sess)

    # Tier 2 — CPI (slug do evento vem do nome)
    ev_slug = event_slug_of(fname)
    if not ev_slug:
        return None
    return _match_token_in_event(ev_slug, token, sess)


def pull_trades(cid, sess):
    """Pagina /trades até o teto. Devolve (lista_trades, bateu_cap)."""
    trades = []
    offset = 0
    LIMIT = 10000
    while offset <= 10000:
        for attempt in range(3):
            try:
                r = sess.get(DATA_API, params={"market": cid, "limit": LIMIT,
                                               "offset": offset}, timeout=TIMEOUT)
                break
            except requests.RequestException:
                if attempt == 2:
                    raise
                time.sleep(1.0 * (attempt + 1))
        if not r.ok:
            break
        batch = r.json()
        if not batch:
            break
        trades.extend(batch)
        if len(batch) < LIMIT:
            break
        offset += LIMIT
        time.sleep(DELAY)
    bateu_cap = len(trades) >= CAP
    return trades, bateu_cap


def grid_slots(fname):
    """Slots de 12h da série /prices-history já baixada (grid do mercado)."""
    try:
        hist = json.loads((CLOB_DIR / fname).read_text()).get("history", [])
    except Exception:
        return []
    slots = sorted({slot_start(p["t"]) for p in hist if "t" in p})
    return slots


def process_market(fname, sess):
    """Devolve dict com agregação por slot + metadados. Usa cache em disco."""
    CACHE.mkdir(parents=True, exist_ok=True)
    cache_f = CACHE / (fname.replace(".json", "") + ".g5.json")
    if cache_f.exists():
        return json.loads(cache_f.read_text())

    token = token_of(fname)
    cid = resolve_condition_id(token, fname, sess)
    if not cid:
        result = {"fname": fname, "erro": "conditionId não resolvido", "conditionId": None}
        cache_f.write_text(json.dumps(result))
        return result

    time.sleep(DELAY)
    trades, bateu_cap = pull_trades(cid, sess)

    # agrega por slot
    agg = {}  # slot -> [notional, count]
    ts_all = []
    for t in trades:
        ts = t["timestamp"]
        ts_all.append(ts)
        s = slot_start(ts)
        a = agg.setdefault(s, [0.0, 0])
        a[0] += float(t["size"]) * float(t["price"])
        a[1] += 1

    t_cov = min(ts_all) if ts_all else None
    result = {
        "fname": fname,
        "conditionId": cid,
        "n_trades_total": len(trades),
        "bateu_cap": bateu_cap,
        "t_cobertura_min": t_cov,
        "agg": {str(k): v for k, v in agg.items()},
    }
    cache_f.write_text(json.dumps(result))
    return result


def process_fomc(cid, sess):
    """Igual ao process_market, mas para um mercado do FOMC identificado direto
    pelo conditionId (vindo do parquet) — sem resolver token/slug. Cacheado em
    disco por conditionId."""
    CACHE.mkdir(parents=True, exist_ok=True)
    cache_f = CACHE / (f"fomc_{cid}.g5.json")
    if cache_f.exists():
        return json.loads(cache_f.read_text())

    time.sleep(DELAY)
    trades, bateu_cap = pull_trades(cid, sess)

    agg = {}  # slot -> [notional, count]
    ts_all = []
    for t in trades:
        ts = t["timestamp"]
        ts_all.append(ts)
        s = slot_start(ts)
        a = agg.setdefault(s, [0.0, 0])
        a[0] += float(t["size"]) * float(t["price"])
        a[1] += 1

    result = {
        "conditionId": cid,
        "n_trades_total": len(trades),
        "bateu_cap": bateu_cap,
        "t_cobertura_min": min(ts_all) if ts_all else None,
        "agg": {str(k): v for k, v in agg.items()},
    }
    cache_f.write_text(json.dumps(result))
    return result


def fomc_grid(sub):
    """Grid de 12h de um mercado do FOMC = slots distintos da série do parquet
    (o mesmo grid que a view 2.3 consome)."""
    # datetime64[ms] UTC -> epoch em SEGUNDOS (trunca p/ segundo antes do int64,
    # robusto à unidade do parquet; NÃO usar //10**9 direto sobre [ms]).
    ts = sub["data"].astype("datetime64[s]").astype("int64").tolist()
    return sorted({slot_start(int(t)) for t in ts})


def fomc_stage(sess):
    """Produz as linhas da view 2.3 (FOMC) a partir do parquet enriquecido.
    Devolve (long_rows, cov_rows, n_mercados, mercados_cap, n_nan, n_zero_slots)."""
    if not REUNIOES_PATH.exists():
        print("FOMC: parquet não encontrado — pulando view 2.3.", file=sys.stderr)
        return [], [], 0, [], 0, 0
    df = pd.read_parquet(REUNIOES_PATH)
    if "conditionId" not in df.columns:
        print("FOMC: parquet sem coluna conditionId — rode scripts/g5b_fomc_conditionid.py "
              "antes. Pulando view 2.3.", file=sys.stderr)
        return [], [], 0, [], 0, 0

    # Um mercado por conditionId; rótulo = slug (chave de junção legível).
    meta = (df[["conditionId", "slug"]].drop_duplicates()
            .set_index("conditionId")["slug"].to_dict())
    cids = sorted(meta, key=lambda c: meta[c])

    long_rows, cov_rows, mercados_cap = [], [], []
    n_nan = n_zero = 0
    for i, cid in enumerate(cids, 1):
        slug = meta[cid]
        sub = df[df["conditionId"] == cid]
        grid = fomc_grid(sub)
        try:
            res = process_fomc(cid, sess)
        except Exception as exc:  # noqa: BLE001
            print(f"  [FOMC {i}/{len(cids)}] ERRO {slug}: {type(exc).__name__}: {exc}",
                  file=sys.stderr)
            cov_rows.append(["2.3", slug, cid, "", "ERRO", "", "", ""])
            continue

        t_cov = res["t_cobertura_min"]
        agg = {int(k): v for k, v in res["agg"].items()}
        cov_slot = slot_start(t_cov) if t_cov is not None else None

        primeiro = last = None
        for s in grid:
            slot_iso = dt.datetime.utcfromtimestamp(s).strftime("%Y-%m-%d %H:%M")
            if primeiro is None:
                primeiro = slot_iso
            last = slot_iso
            if res["bateu_cap"] and (cov_slot is None or s < cov_slot):
                long_rows.append(["2.3", slug, cid, slot_iso, "", ""])  # NaN (truncamento)
                n_nan += 1
            else:
                notional, cnt = agg.get(s, (0.0, 0))
                long_rows.append(["2.3", slug, cid, slot_iso, f"{notional:.6f}", cnt])
                if cnt == 0:
                    n_zero += 1

        t_cov_iso = (dt.datetime.utcfromtimestamp(t_cov).strftime("%Y-%m-%d %H:%M:%S")
                     if t_cov is not None else "")
        cov_rows.append(["2.3", slug, cid, res["n_trades_total"],
                         "SIM" if res["bateu_cap"] else "não",
                         t_cov_iso, primeiro or "", last or ""])
        if res["bateu_cap"]:
            mercados_cap.append((slug, t_cov_iso))
        print(f"  [FOMC {i}/{len(cids)}] {slug}: {res['n_trades_total']} trades, "
              f"cap={'SIM' if res['bateu_cap'] else 'não'}, slots={len(grid)}",
              file=sys.stderr)

    return long_rows, cov_rows, len(cids), mercados_cap, n_nan, n_zero


def main():
    files = sorted(f for f in (p.name for p in CLOB_DIR.glob("*.json"))
                   if scope_view(f) and not f.endswith("_NO.json")
                   and not f.startswith("M2_"))  # 2.3 vem do parquet, não dos .json
    print(f"Mercados no escopo (2.2/2.3/B): {len(files)}", file=sys.stderr)

    sess = requests.Session()
    sess.headers.update({"User-Agent": "quant-itau-g5/1.0"})

    long_rows = []      # (view, mercado, conditionId, slot_utc, notional, n_trades|NaN)
    cov_rows = []       # por mercado
    slots_sem_trade = 0
    slots_nan = 0
    mercados_cap = []

    for i, fname in enumerate(files, 1):
        view = scope_view(fname)
        name = market_name(fname)
        try:
            res = process_market(fname, sess)
        except Exception as exc:  # noqa: BLE001
            print(f"  [{i}/{len(files)}] ERRO {name}: {type(exc).__name__}: {exc}", file=sys.stderr)
            cov_rows.append([view, name, "", "", "", "ERRO", "", ""])
            continue

        cid = res.get("conditionId")
        if res.get("erro"):
            print(f"  [{i}/{len(files)}] {name}: {res['erro']}", file=sys.stderr)
            cov_rows.append([view, name, cid or "", "", "", res["erro"], "", ""])
            continue

        t_cov = res["t_cobertura_min"]
        agg = {int(k): v for k, v in res["agg"].items()}
        grid = grid_slots(fname)
        # slot que contém t_cov (fronteira do NaN)
        cov_slot = slot_start(t_cov) if t_cov is not None else None

        primeiro = last = None
        for s in grid:
            slot_iso = dt.datetime.utcfromtimestamp(s).strftime("%Y-%m-%d %H:%M")
            if primeiro is None:
                primeiro = slot_iso
            last = slot_iso
            if res["bateu_cap"] and (cov_slot is None or s < cov_slot):
                # capado E antes do alcance do /trades -> NaN (dado existe, o
                # /trades não alcança lá). Mercado NÃO capado antes do 1º trade
                # cai no else e vira 0 legítimo — Decisão 12 do Paulo / FOLLOWUP5.
                long_rows.append([view, name, cid, slot_iso, "", ""])
                slots_nan += 1
            else:
                notional, cnt = agg.get(s, (0.0, 0))
                long_rows.append([view, name, cid, slot_iso,
                                  f"{notional:.6f}", cnt])
                if cnt == 0:
                    slots_sem_trade += 1

        t_cov_iso = (dt.datetime.utcfromtimestamp(t_cov).strftime("%Y-%m-%d %H:%M:%S")
                     if t_cov is not None else "")
        cov_rows.append([view, name, cid, res["n_trades_total"],
                         "SIM" if res["bateu_cap"] else "não",
                         t_cov_iso, primeiro or "", last or ""])
        if res["bateu_cap"]:
            mercados_cap.append((name, t_cov_iso))
        print(f"  [{i}/{len(files)}] {name}: {res['n_trades_total']} trades, "
              f"cap={'SIM' if res['bateu_cap'] else 'não'}, slots={len(grid)}",
              file=sys.stderr)

    # ---- view 2.3 (FOMC), a partir do parquet enriquecido ----
    fomc_long, fomc_cov, n_fomc, fomc_cap, fomc_nan, fomc_zero = fomc_stage(sess)
    long_rows.extend(fomc_long)
    cov_rows.extend(fomc_cov)
    mercados_cap.extend(fomc_cap)
    slots_nan += fomc_nan
    slots_sem_trade += fomc_zero

    # ---- grava CSVs ----
    long_path = RAW_DIR / "g5_volume_no_tempo.csv"
    with long_path.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["view", "mercado", "conditionId", "slot_utc",
                    "notional_usd", "n_trades"])
        w.writerows(long_rows)

    cov_path = RAW_DIR / "g5_volume_cobertura.csv"
    with cov_path.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["view", "mercado", "conditionId", "n_trades_total",
                    "bateu_cap_20k", "t_cobertura_min", "primeiro_slot", "ultimo_slot"])
        w.writerows(cov_rows)

    # ---- bloco de report ----
    todos_slots = [r[3] for r in long_rows]
    janela = (min(todos_slots), max(todos_slots)) if todos_slots else ("—", "—")
    print("\n=== G5 — VOLUME NO TEMPO ===")
    print(f"Arquivo salvo:        {long_path.relative_to(REPO_ROOT)}")
    print(f"                      {cov_path.relative_to(REPO_ROOT)} (cobertura por mercado)")
    print("Colunas:              ['view', 'mercado', 'conditionId', 'slot_utc', "
          "'notional_usd', 'n_trades']")
    print(f"Nº de linhas:         {len(long_rows)}  (slots × mercados)")
    print(f"Nº de mercados:       {len(files) + n_fomc}  "
          f"(2.2={sum(1 for f in files if scope_view(f)=='2.2')}, "
          f"2.3={n_fomc}, "
          f"B={sum(1 for f in files if scope_view(f)=='B')})")
    print("Passo:                12h (43200s; = prices-history fidelity=720)")
    print(f"Janela:               {janela[0]} → {janela[1]} (UTC)")
    print(f"Mercados que bateram no cap de 20k:  {len(mercados_cap)}")
    for name, tcov in mercados_cap:
        print(f"    - {name}  (t_cobertura_min={tcov})")
    print(f"Slots com volume 0 legítimo (slot sem trade; inclui pré-1º-trade de mercado não capado):  {slots_sem_trade}")
    print(f"Slots NaN (só truncamento do cap: mercado capado antes do t_cobertura_min):  {slots_nan}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
