"""Pipeline de probabilidades do Polymarket — mercados de decisão do Fed/FOMC.

Tarefa 2 — Paulo. Decisão 2 (fechada): Path B — APIs gratuitas do Polymarket,
Gamma API (catálogo) + CLOB API (preços históricos), sem provedores pagos.

Etapas:
1. Descoberta: /tags (Gamma) para achar o tag de Fed Rates; /events paginado
   (tag_id, closed=true) para listar eventos; filtro local por "fed"/"fomc".
2. Download: /prices-history (CLOB) uma vez por token, com cache local por
   token para permitir reexecução sem rebaixar tudo.
3. Consolidação: tabela longa [data, mercado, probabilidade, evento_id] em
   parquet, eventos encadeados em ordem cronológica de reunião.

Todas as respostas brutas ficam em cache/ — o script nunca repete uma chamada
cujo resultado já está salvo.

Uso:
    python src/data_pipeline/download_polymarket_fed.py
"""

import json
import sys
import time
from pathlib import Path

import pandas as pd
import requests

# Raiz do repositório (este arquivo fica em src/data_pipeline/)
REPO_ROOT = Path(__file__).resolve().parents[2]
CACHE_DIR = REPO_ROOT / "cache"
TAGS_CACHE = CACHE_DIR / "tags.json"
EVENTS_CACHE = CACHE_DIR / "fed_events.json"
PRICES_CACHE_DIR = CACHE_DIR / "prices_history"
OUTPUT_PATH = REPO_ROOT / "data" / "polymarket_fed_probabilities.parquet"

GAMMA_URL = "https://gamma-api.polymarket.com"
CLOB_URL = "https://clob.polymarket.com"
PAGE_LIMIT = 500
REQUEST_DELAY_S = 0.2
MAX_RETRIES = 3
# Granularidade em minutos do /prices-history. 720 (12h) é a mais fina que a
# API gratuita devolve para mercados já resolvidos (testado: 180/60/10 voltam
# vazios) — limitação documentada na Decisão 2.
FIDELITY_MINUTES = 720

# Contador de chamadas de API realmente feitas na execução (cache hits não contam)
api_calls = {"n": 0}


def get_json(url: str, params: dict | None = None):
    """GET com retry e backoff (mesmo padrão do retry do script de ETFs)."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(url, params=params, timeout=30)
            api_calls["n"] += 1
            resp.raise_for_status()
            return resp.json()
        except (requests.RequestException, ValueError) as exc:
            if attempt == MAX_RETRIES:
                raise
            wait = 2**attempt
            print(f"  retry {attempt}/{MAX_RETRIES} em {wait}s ({url}): {exc}")
            time.sleep(wait)


# ---------------------------------------------------------------------------
# Etapa 1 — Descoberta
# ---------------------------------------------------------------------------

def fetch_tags() -> list[dict]:
    """Baixa o catálogo de tags da Gamma API (cache-first)."""
    if TAGS_CACHE.exists():
        print(f"[cache] tags: {TAGS_CACHE}")
        return json.loads(TAGS_CACHE.read_text(encoding="utf-8"))

    # A Gamma API ignora limit > 100 em /tags — paginar pelo tamanho real do
    # batch e parar somente quando vier página vazia.
    tags: list[dict] = []
    offset = 0
    while True:
        batch = get_json(f"{GAMMA_URL}/tags", {"limit": PAGE_LIMIT, "offset": offset})
        if not batch:
            break
        tags.extend(batch)
        offset += len(batch)
        time.sleep(REQUEST_DELAY_S)
    TAGS_CACHE.parent.mkdir(parents=True, exist_ok=True)
    TAGS_CACHE.write_text(json.dumps(tags, ensure_ascii=False), encoding="utf-8")
    print(f"Tags baixadas: {len(tags)} → {TAGS_CACHE}")
    return tags


def find_fed_tag(tags: list[dict]) -> dict:
    """Localiza o tag de Fed Rates (candidatos: fed / economy / finance)."""
    candidates = [
        t
        for t in tags
        if any(
            key in str(t.get("label", "")).lower() or key in str(t.get("slug", "")).lower()
            for key in ("fed", "fomc", "econom", "financ", "interest rate")
        )
    ]
    print("Tags candidatos (fed/fomc/economy/finance/interest rate):")
    for t in candidates:
        print(f"  id={t.get('id')} slug={t.get('slug')} label={t.get('label')}")

    # Preferência: tag específico de Fed Rates; senão, um tag com 'fed'+'rate'
    # ou 'fomc' no slug/label (evita falsos positivos como 'federal government').
    for t in candidates:
        if str(t.get("slug", "")).lower() == "fed-rates" or str(t.get("label", "")).lower() == "fed rates":
            print(f"Tag escolhido: id={t['id']} ({t.get('label')})")
            return t
    specific = [
        t
        for t in candidates
        if "fomc" in (str(t.get("slug", "")) + str(t.get("label", ""))).lower()
        or (
            "fed" in str(t.get("slug", "")).lower()
            and "rate" in str(t.get("slug", "")).lower()
        )
    ]
    if len(specific) == 1:
        print(f"Tag escolhido: id={specific[0]['id']} ({specific[0].get('label')})")
        return specific[0]
    raise RuntimeError(
        "Não foi possível identificar o tag de Fed Rates de forma inequívoca — "
        "escolher manualmente entre os candidatos acima."
    )


def fetch_fed_events(tag_id) -> list[dict]:
    """Baixa todos os eventos fechados do tag, paginando por offset (cache-first)."""
    if EVENTS_CACHE.exists():
        print(f"[cache] eventos: {EVENTS_CACHE}")
        return json.loads(EVENTS_CACHE.read_text(encoding="utf-8"))

    # A Gamma API ignora limit > 100 em /events — paginar pelo tamanho real do
    # batch e parar somente quando vier página vazia.
    events: list[dict] = []
    offset = 0
    while True:
        batch = get_json(
            f"{GAMMA_URL}/events",
            {
                "tag_id": tag_id,
                "closed": "true",
                "order": "startDate",
                "ascending": "true",
                "limit": PAGE_LIMIT,
                "offset": offset,
            },
        )
        if not batch:
            break
        events.extend(batch)
        print(f"  offset={offset}: +{len(batch)} eventos")
        offset += len(batch)
        time.sleep(REQUEST_DELAY_S)
    EVENTS_CACHE.parent.mkdir(parents=True, exist_ok=True)
    EVENTS_CACHE.write_text(json.dumps(events, ensure_ascii=False), encoding="utf-8")
    print(f"Eventos baixados: {len(events)} → {EVENTS_CACHE}")
    return events


def filter_fed_events(events: list[dict]) -> list[dict]:
    """Filtra localmente eventos cujo título contém 'fed' ou 'fomc'."""
    filtered = [
        e
        for e in events
        if "fed" in str(e.get("title", "")).lower() or "fomc" in str(e.get("title", "")).lower()
    ]
    print(f"Eventos filtrados (título com fed/fomc): {len(filtered)} de {len(events)}")
    return filtered


def report_discovery(events: list[dict]) -> None:
    """Reporta cobertura: evento mais antigo, total e lacunas > 6 meses."""
    dates = sorted(
        pd.to_datetime(e["startDate"]).tz_localize(None)
        for e in events
        if e.get("startDate")
    )
    print("\n=== Descoberta — cobertura dos eventos Fed/FOMC ===")
    print(f"Total de eventos: {len(events)} (com startDate: {len(dates)})")
    print(f"Evento mais antigo: {dates[0].date()} | mais recente: {dates[-1].date()}")
    gaps = [
        (prev, curr)
        for prev, curr in zip(dates, dates[1:])
        if (curr - prev).days > 183
    ]
    if gaps:
        print("Lacunas > 6 meses entre eventos consecutivos:")
        for prev, curr in gaps:
            print(f"  {prev.date()} → {curr.date()} ({(curr - prev).days} dias)")
    else:
        print("Sem lacunas > 6 meses entre eventos consecutivos.")


# ---------------------------------------------------------------------------
# Etapa 2 — Download de preços (CLOB /prices-history)
# ---------------------------------------------------------------------------

def fetch_price_history(token_id: str) -> list[dict]:
    """Baixa o histórico de preços de um token (cache-first, 1 chamada/token)."""
    cache_file = PRICES_CACHE_DIR / f"{token_id}.json"
    if cache_file.exists():
        return json.loads(cache_file.read_text(encoding="utf-8"))

    # interval=max volta vazio para mercados resolvidos antigos; interval=all
    # com fidelity=720 devolve a vida inteira do mercado em passos de 12h.
    payload = get_json(
        f"{CLOB_URL}/prices-history",
        {"market": token_id, "interval": "all", "fidelity": FIDELITY_MINUTES},
    )
    history = payload.get("history", [])
    PRICES_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(json.dumps(history, ensure_ascii=False), encoding="utf-8")
    time.sleep(REQUEST_DELAY_S)
    return history


def yes_token_id(market: dict) -> str | None:
    """Extrai o token do desfecho 'Yes' (primeiro da lista clobTokenIds)."""
    raw = market.get("clobTokenIds")
    if not raw:
        return None
    token_ids = json.loads(raw) if isinstance(raw, str) else raw
    return token_ids[0] if token_ids else None


# ---------------------------------------------------------------------------
# Etapa 3 — Consolidação
# ---------------------------------------------------------------------------

def meeting_date(event: dict) -> pd.Timestamp:
    """Data de reunião do FOMC — proxy: endDate do evento (data de resolução)."""
    return pd.to_datetime(event.get("endDate") or event.get("startDate")).tz_localize(None)


def build_table(events: list[dict]) -> pd.DataFrame:
    """Monta a tabela longa [data, mercado, probabilidade, evento_id]."""
    rows = []
    n_markets = 0
    n_no_token = 0
    n_empty_history = 0
    for event in sorted(events, key=meeting_date):
        for market in event.get("markets", []):
            n_markets += 1
            token = yes_token_id(market)
            if token is None:
                n_no_token += 1
                continue
            history = fetch_price_history(token)
            if not history:
                n_empty_history += 1
                continue
            mercado = market.get("question") or market.get("slug")
            for point in history:
                rows.append(
                    {
                        "data": pd.Timestamp(point["t"], unit="s"),
                        "mercado": mercado,
                        "probabilidade": float(point["p"]),
                        "evento_id": str(event["id"]),
                    }
                )
    print(f"\n=== Consolidação ===")
    print(f"Mercados percorridos: {n_markets} | sem clobTokenIds: {n_no_token} | histórico vazio: {n_empty_history}")
    return pd.DataFrame(rows)


def main() -> int:
    # Etapa 1 — descoberta
    tags = fetch_tags()
    fed_tag = find_fed_tag(tags)
    events = fetch_fed_events(fed_tag["id"])
    fed_events = filter_fed_events(events)
    if not fed_events:
        print("ERRO: nenhum evento Fed/FOMC encontrado — nada a fazer.")
        return 1
    report_discovery(fed_events)

    # Etapas 2 e 3 — download por token (com cache) e consolidação
    table = build_table(fed_events)
    if table.empty:
        print("ERRO: nenhuma série de preços obtida — arquivo NÃO salvo.")
        return 1

    out_of_range = table[(table["probabilidade"] < 0) | (table["probabilidade"] > 1)]
    if len(out_of_range) > 0:
        print(f"ATENÇÃO: {len(out_of_range)} pontos com probabilidade fora de [0,1].")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    table.to_parquet(OUTPUT_PATH, index=False)
    print(f"Salvo: {OUTPUT_PATH}")
    print(f"Linhas: {len(table)} | Colunas: {list(table.columns)}")
    print(f"Período: {table['data'].min()} → {table['data'].max()}")
    print(f"Eventos com dados: {table['evento_id'].nunique()} | Mercados com dados: {table['mercado'].nunique()}")
    print(f"\nChamadas de API feitas nesta execução: {api_calls['n']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
