"""Exploração da API do Polymarket — a rota histórica entrega bid/ask?

Tarefa 1 do `docs/Pedido_Paulo_dados.md` (seção 1, prioridade máxima). NÃO é
pipeline de produção: é um levantamento que **roda contra a API real** e reporta
o que cada endpoint devolve, com amostra CRUA (nomes de campo originais).

Perguntas que este script responde (colar a saída no relatório da seção 4.1):
  1. /prices-history retorna qual preço? (último trade | midpoint | mid do book)
  2. Existe endpoint com bid e ask HISTÓRICOS (não só snapshot atual)?
  3. Os endpoints de book (/book, /midpoint, /price, /spread) são só tempo real?
  4. Existe histórico de TRADES individuais (timestamp+preço+tamanho+lado)?
  + granularidade temporal máxima e profundidade de histórico do /prices-history.

Estratégia: usa um mercado real, grande e resolvido — presidencial EUA 2024
(perna Trump) — que tem histórico longo. O token pode vir de três formas, nesta
ordem: --token na linha de comando; slug via Gamma; ou fallback interativo.

Uso (no seu terminal, que tem rede — o sandbox do Claude Code não tem):
    python scripts/explorar_clob_bidask.py
    python scripts/explorar_clob_bidask.py --token <clob_token_id>
    python scripts/explorar_clob_bidask.py --slug <market-slug>

Nada é normalizado, interpolado ou convertido de fuso. Dado cru, campos crus.
"""

import argparse
import json
import sys
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_ROOT / "data" / "raw" / "clob_exploracao"

GAMMA_URL = "https://gamma-api.polymarket.com"
CLOB_URL = "https://clob.polymarket.com"
DATA_URL = "https://data-api.polymarket.com"

# Mercado-âncora: presidencial EUA 2024, "Trump vence?" — grande e resolvido.
DEFAULT_SLUG = "will-donald-trump-win-the-2024-us-presidential-election"

TIMEOUT = 30


def get(url: str, params: dict | None = None) -> requests.Response:
    """GET simples; devolve o Response cru (o chamador decide o que fazer)."""
    return requests.get(url, params=params, timeout=TIMEOUT)


def dump(label: str, obj) -> None:
    """Imprime rótulo + JSON identado (para o relatório)."""
    print(f"\n----- {label} -----")
    print(json.dumps(obj, ensure_ascii=False, indent=2)[:4000])


# ---------------------------------------------------------------------------
# Resolução do token do mercado-âncora
# ---------------------------------------------------------------------------

def resolve_market(slug: str) -> dict:
    """Busca o mercado no Gamma pelo slug e devolve o dict cru do mercado."""
    # closed=true é obrigatório para mercados já resolvidos — sem isso o Gamma
    # filtra só mercados ativos e devolve lista vazia para o presidencial 2024.
    resp = get(f"{GAMMA_URL}/markets", {"slug": slug, "closed": "true"})
    resp.raise_for_status()
    data = resp.json()
    markets = data if isinstance(data, list) else data.get("markets", [data])
    if not markets:
        raise RuntimeError(f"Nenhum mercado no Gamma para slug={slug}")
    return markets[0]


def token_ids_from_market(market: dict) -> list[str]:
    """Extrai a lista de clobTokenIds (Yes primeiro, por convenção do Polymarket)."""
    raw = market.get("clobTokenIds")
    if not raw:
        return []
    return json.loads(raw) if isinstance(raw, str) else raw


# ---------------------------------------------------------------------------
# 1. /prices-history — o que ele entrega e com que resolução/profundidade
# ---------------------------------------------------------------------------

def probe_prices_history(token_id: str) -> None:
    print("\n########## 1. /prices-history ##########")
    # Varre fidelidades para achar a mais fina que a API devolve para este
    # mercado resolvido (o pedido quer a granularidade máxima real, não a doc).
    for fidelity in (1, 10, 60, 180, 720):
        url = f"{CLOB_URL}/prices-history"
        params = {"market": token_id, "interval": "all", "fidelity": fidelity}
        resp = get(url, params)
        try:
            payload = resp.json()
        except ValueError:
            print(f"fidelity={fidelity}: HTTP {resp.status_code}, corpo não-JSON: {resp.text[:200]}")
            continue
        history = payload.get("history", []) if isinstance(payload, dict) else []
        print(f"\nfidelity={fidelity} | HTTP {resp.status_code} | URL {resp.url}")
        print(f"  chaves do payload: {list(payload) if isinstance(payload, dict) else type(payload)}")
        print(f"  nº de pontos: {len(history)}")
        if history:
            print(f"  campos de um ponto: {list(history[0])}")
            print("  primeiras 5 linhas CRUAS:")
            for row in history[:5]:
                print(f"    {json.dumps(row, ensure_ascii=False)}")
            # profundidade: intervalo temporal coberto
            ts = [p.get("t") for p in history if "t" in p]
            if ts:
                import datetime as dt
                lo = dt.datetime.utcfromtimestamp(min(ts))
                hi = dt.datetime.utcfromtimestamp(max(ts))
                print(f"  cobertura: {lo} → {hi} (UTC) | {(hi - lo).days} dias")
                # passo temporal típico entre pontos consecutivos (segundos)
                ts_sorted = sorted(ts)
                steps = [b - a for a, b in zip(ts_sorted, ts_sorted[1:])]
                if steps:
                    steps.sort()
                    print(f"  passo mediano entre pontos: {steps[len(steps)//2]}s")


# ---------------------------------------------------------------------------
# 2-3. Endpoints de book — só tempo real? há variante histórica?
# ---------------------------------------------------------------------------

def probe_book_endpoints(token_id: str) -> None:
    print("\n########## 2-3. Endpoints de book (bid/ask) ##########")
    # Snapshot atual do book: /book, /midpoint, /price (buy/sell), /spread.
    # O objetivo é documentar que TÊM bid/ask mas SÓ do estado atual (sem t).
    probes = [
        ("/book", {"token_id": token_id}),
        ("/midpoint", {"token_id": token_id}),
        ("/price (side=BUY = melhor ask)", {"token_id": token_id, "side": "BUY"}),
        ("/price (side=SELL = melhor bid)", {"token_id": token_id, "side": "SELL"}),
        ("/spread", {"token_id": token_id}),
        ("/last-trade-price", {"token_id": token_id}),
    ]
    endpoint_map = {
        "/book": "/book",
        "/midpoint": "/midpoint",
        "/price (side=BUY = melhor ask)": "/price",
        "/price (side=SELL = melhor bid)": "/price",
        "/spread": "/spread",
        "/last-trade-price": "/last-trade-price",
    }
    for label, params in probes:
        endpoint = endpoint_map[label]
        try:
            resp = get(f"{CLOB_URL}{endpoint}", params)
            payload = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else resp.text
        except Exception as exc:  # noqa: BLE001 — levantamento, queremos ver a falha
            print(f"\n{label}: ERRO {exc}")
            continue
        dump(f"{label}  [HTTP {resp.status_code}]", payload)
    print("\n>> Nenhum destes aceita parâmetro de tempo/timestamp — confirmar na doc "
          "que são todos snapshot do estado atual (sem histórico).")


def probe_orderbook_history(token_id: str) -> None:
    """Testa o /orderbook-history — ÚNICO candidato a bid/ask HISTÓRICO.

    A doc indica parâmetros asset_id/token_id + startTs/endTs/limit/offset, mas
    há relato (issue nautilus_trader #3635) de que devolve {"count":0,"data":[]}.
    Este teste confirma no dado real se ele entrega book histórico ou não — é a
    resposta direta à pergunta 2 da seção 1.
    """
    import time as _time
    print("\n########## 2b. /orderbook-history (bid/ask HISTÓRICO?) ##########")
    now = int(_time.time())
    start = now - 365 * 24 * 3600  # último ano
    # Tenta as duas grafias de parâmetro de asset que aparecem na doc/clientes.
    for asset_param in ("asset_id", "token_id", "market"):
        params = {asset_param: token_id, "startTs": start, "endTs": now, "limit": 5}
        try:
            resp = get(f"{CLOB_URL}/orderbook-history", params)
            ctype = resp.headers.get("content-type", "")
            payload = resp.json() if ctype.startswith("application/json") else resp.text[:500]
        except Exception as exc:  # noqa: BLE001
            print(f"\n{asset_param}=...: ERRO {exc}")
            continue
        print(f"\n/orderbook-history?{asset_param}=... | HTTP {resp.status_code} | URL {resp.url}")
        dump("retorno cru", payload)
        if isinstance(payload, dict) and payload.get("count") == 0:
            print("  >> count=0: endpoint responde mas SEM dados (bate com a issue #3635).")


# ---------------------------------------------------------------------------
# 4. Histórico de trades individuais (data-api) — tem lado buy/sell?
# ---------------------------------------------------------------------------

def probe_trades(market: dict, token_id: str) -> None:
    print("\n########## 4. Trades individuais (data-api) ##########")
    condition_id = market.get("conditionId") or market.get("condition_id")
    print(f"conditionId do mercado: {condition_id}")
    # A data-api expõe trades por mercado (condition id) e/ou por asset (token).
    attempts = [
        ("data-api /trades?market=<conditionId>", f"{DATA_URL}/trades", {"market": condition_id, "limit": 5}),
        ("data-api /trades?asset=<tokenId>", f"{DATA_URL}/trades", {"asset": token_id, "limit": 5}),
        ("clob /trades (pode exigir auth)", f"{CLOB_URL}/trades", {"market": condition_id}),
    ]
    for label, url, params in attempts:
        try:
            resp = get(url, params)
            ctype = resp.headers.get("content-type", "")
            payload = resp.json() if ctype.startswith("application/json") else resp.text[:500]
        except Exception as exc:  # noqa: BLE001
            print(f"\n{label}: ERRO {exc}")
            continue
        n = len(payload) if isinstance(payload, list) else "n/a"
        print(f"\n{label} | HTTP {resp.status_code} | itens: {n}")
        if isinstance(payload, list) and payload:
            print(f"  campos de um trade: {list(payload[0])}")
            print("  primeiras linhas CRUAS:")
            for row in payload[:5]:
                print(f"    {json.dumps(row, ensure_ascii=False)}")
            print("  >> Verificar se há campo de LADO (side/taker/maker) para reconstruir bid/ask proxy.")
        else:
            dump(label, payload)


def save_raw(market: dict, token_id: str) -> None:
    """Salva o retorno cru do /prices-history do mercado-âncora (entrega física)."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    resp = get(f"{CLOB_URL}/prices-history",
               {"market": token_id, "interval": "all", "fidelity": 1})
    if resp.ok:
        out = RAW_DIR / f"prices_history_{token_id}.json"
        out.write_text(resp.text, encoding="utf-8")
        print(f"\n[entrega física] retorno cru salvo em {out}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--token", help="clob token id direto (pula a resolução por slug)")
    parser.add_argument("--slug", default=DEFAULT_SLUG, help="slug do mercado no Gamma")
    args = parser.parse_args()

    if args.token:
        token_id = args.token
        market = {"conditionId": None, "question": "(token informado direto)"}
    else:
        print(f"Resolvendo mercado por slug: {args.slug}")
        market = resolve_market(args.slug)
        print(f"Mercado: {market.get('question')!r}")
        tokens = token_ids_from_market(market)
        print(f"clobTokenIds: {tokens}")
        if not tokens:
            print("ERRO: mercado sem clobTokenIds — informe --token manualmente.")
            return 1
        token_id = tokens[0]  # Yes
        print(f"Token usado (Yes): {token_id}")

    probe_prices_history(token_id)
    probe_book_endpoints(token_id)
    probe_orderbook_history(token_id)
    probe_trades(market, token_id)
    save_raw(market, token_id)

    print("\n\n==================================================")
    print("Concluído. Cole a saída acima na seção 4.1 do relatório.")
    print("==================================================")
    return 0


if __name__ == "__main__":
    sys.exit(main())
