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

## `etf_open_daily.parquet`

Arquivo **irmão** do `etf_prices_daily.parquet` com o **preço de abertura**
(`Open`) diário dos mesmos 9 ativos, na mesma janela e no **mesmo alinhamento
de datas** — para as táticas que operam na abertura (gap de fim de semana,
prêmio de anúncio na véspera → saída na abertura).

- **Gerado por:** `scripts/g1_open_etfs.py`
- **Fonte:** Yahoo Finance via `yfinance`, frequência diária
- **Base do Open:** ajustado (`auto_adjust=True`) — **a mesma base do close** que
  está no `etf_prices_daily.parquet`. Escolhido para consistência interna (não
  misturar close ajustado com open cru, o que geraria retorno intradiário falso
  em dia de dividendo); a decisão metodológica final é do grupo.
- **Formato:** tabela única, formato longo

| Coluna | Tipo | Descrição |
|---|---|---|
| `data` | datetime | Data do pregão (sem timezone) |
| `ticker` | string | Um de: XLK, XLU, XLP, XLF, XLE, XLV, TIP, TLT, SPY |
| `preco_abertura` | float | Preço de **abertura** ajustado (`auto_adjust=True`) |

- **Período coberto:** 2003-12-05 → 2026-07-08 (idêntico ao arquivo de close).
- **Linhas:** 51.129 (5.681 datas × 9 tickers) — reindexado às datas EXATAS do
  arquivo de close; **0 dias com Open ausente**, alinhamento 100%.

## `polymarket_fed_reunioes.parquet`

Histórico de probabilidades dos mercados de **decisão direta por reunião** do
FOMC no Polymarket (Decisão 2, fechada: Gamma API + CLOB API, sem provedores
pagos). Contém apenas os mercados de desfecho de cada reunião (corte/alta de
25/50/75 bps, sem mudança); mercados acessórios (Fed Chair, dissidência,
cortes acumulados) foram descartados.

- **Fonte:** Polymarket — Gamma API (catálogo, tag "Fed Rates", id 100196) +
  CLOB API `/prices-history` (`interval=all`, `fidelity=720`)
- **Granularidade:** 1 ponto a cada 12h (00:00 e 12:00 UTC) — é a mais fina
  que a API gratuita devolve para mercados já resolvidos. Alguns intervalos de
  24/36/48h são leituras faltantes pontuais, não outra granularidade.
- **Probabilidade:** preço do token "Yes" de cada mercado (0 a 1)
- **Formato:** tabela única, formato longo

| Coluna | Tipo | Descrição |
|---|---|---|
| `data` | datetime | Timestamp do ponto de preço (UTC) |
| `mercado` | string | Pergunta do mercado (ex. "Fed decreases interest rates by 25 bps after March 2025 meeting?") |
| `probabilidade` | float | Preço do token Yes ∈ [0, 1] |
| `volume` | float | Volume total (lifetime) do mercado em USD, do Gamma — constante por mercado, repetido em cada ponto |
| `evento_id` | string | ID do evento Polymarket (agrupa os desfechos da mesma reunião) |

- **Cobertura:** 18 reuniões do FOMC, de **May 2024** a **June 2026**; 76
  mercados de desfecho; 16.338 linhas. Range de datas: 2024-04-04 → 2026-06-17.
  As reuniões antigas (dez/2023, jan/2024, mar/2024) foram testadas e removidas
  — ver Decisão 10 em `Decisoes_pendentes.md`.
- **Regeneração:** `src/data_pipeline/download_polymarket_fed.py` (baixa da API
  e recria o cache local) → `src/data_pipeline/separar_mercados_fed.py` (separa
  reuniões dos demais mercados). O cache bruto e os datasets intermediários
  (`polymarket_fed_probabilities.parquet`, `polymarket_fed_outros.parquet`)
  foram removidos por serem regeneráveis por esses scripts.

## `dashboard_reunioes_fed.html`

Dashboard estático (arquivo único, abre no navegador sem servidor) com a lista
das 18 reuniões do FOMC por data; ao selecionar uma reunião, mostra o gráfico
das probabilidades de cada desfecho ao longo do tempo.

- **Gerado por:** `scripts/gerar_dashboard_reunioes.py`
- **Entrada:** `polymarket_fed_reunioes.parquet`
- **Regeneração:** `python scripts/gerar_dashboard_reunioes.py`
