# Dados

## `etf_prices_daily.parquet`

Histórico diário de preços ajustados dos 9 ativos da camada estrutural
(Decisão 1, fechada em `Decisoes_pendentes.md`).

- **Gerado por:** `src/data_pipeline/download_prices.py` (parâmetros em `config/data_config.json`)
- **Fonte:** Yahoo Finance via `yfinance`, frequência diária
- **Preço:** adjusted close (splits e dividendos já incorporados — `auto_adjust=True`)
- **Formato:** tabela única, formato longo

| Coluna | Tipo | Descrição |
|---|---|---|
| `data` | datetime | Data do pregão (sem timezone) |
| `ticker` | string | Um de: XLK, XLU, XLP, XLF, XLE, XLV, TIP, TLT, SPY |
| `preco_ajustado` | float | Preço de fechamento ajustado |

- **Período coberto:** 2003-12-05 → 2026-07-08 (janela comum aos 9 tickers;
  o limite inferior é a estreia do TIP, o ETF mais novo do universo).
  O histórico anterior dos demais tickers (SPY desde 1993, setoriais desde
  1998, TLT desde 2002) é descartado no recorte para garantir datas 100%
  alinhadas entre os 9 tickers, sem NaN.
- **Linhas:** 51.129 (5.681 datas × 9 tickers)
- **Validação:** `pytest tests/test_etf_prices.py`

## `polymarket_fed_probabilities.parquet`

Histórico de probabilidades dos mercados de decisão do Fed/FOMC no Polymarket
(Decisão 2, fechada: Path B — Gamma API + CLOB API, sem provedores pagos).

- **Gerado por:** `src/data_pipeline/download_polymarket_fed.py`
- **Fonte:** Polymarket — Gamma API (catálogo, tag "Fed Rates", id 100196) +
  CLOB API `/prices-history` (`interval=all`, `fidelity=720`)
- **Granularidade:** pontos a cada ~12h — é a mais fina que a API gratuita
  devolve para mercados já resolvidos (720 min; 180/60/10 voltam vazios)
- **Probabilidade:** preço do token "Yes" de cada mercado (0 a 1)
- **Formato:** tabela única, formato longo

| Coluna | Tipo | Descrição |
|---|---|---|
| `data` | datetime | Timestamp do ponto de preço (UTC) |
| `mercado` | string | Pergunta do mercado (ex. "Fed rate cut by March 20?") |
| `probabilidade` | float | Preço do token Yes ∈ [0, 1] |
| `evento_id` | string | ID do evento Polymarket (agrupa mercados da mesma reunião) |

- **Cobertura real (descoberta em 2026-07-08):** primeiro evento em
  **2023-12-06**; primeiro ponto de preço em **2023-12-07**; último ponto em
  2026-06-17. Sem lacunas > 6 meses entre eventos consecutivos.
- **Volume:** 85 eventos Fed/FOMC filtrados (título com "fed"/"fomc"), dos
  quais 83 com dados de preço; 385 mercados percorridos, 331 com histórico
  (54 voltaram vazios); 65.606 linhas.
- **Atenção — overlap:** mercados de reuniões diferentes do FOMC negociam
  simultaneamente (82 de 82 pares de eventos consecutivos com overlap de
  datas). A regra de encadeamento/recorte está em aberto em
  `Decisoes_pendentes.md`.
- **Cache:** respostas brutas das APIs em `cache/` (tags.json,
  fed_events.json, prices_history/{token_id}.json) — reexecutar o script não
  refaz chamadas já cacheadas.
- **Validação:** `pytest tests/test_polymarket_fed.py`
