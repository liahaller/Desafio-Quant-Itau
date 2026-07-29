# Guia rápido — como puxar os dados

Mini-guia para o grupo carregar os datasets do pipeline do Paulo. Para o
esquema completo de cada coluna, ver [`README.md`](README.md).

> Todos os caminhos são relativos à raiz do repositório
> (`Desafio-Quant-Itau/`). Nos scripts, prefira montar o caminho a partir da
> raiz para não depender de onde o Python foi chamado.

## 0. Ambiente

```bash
source .venv/bin/activate      # o projeto usa .venv, não venv
pip install pandas pyarrow     # já devem estar instalados
```

## 1. Preços dos ETFs — `etf_prices_daily.parquet`

Histórico diário (adjusted close) dos 9 ativos da camada estrutural.
Formato **longo**: uma linha por (data, ticker).

```python
import pandas as pd

precos = pd.read_parquet("data/etf_prices_daily.parquet")
# colunas: data | ticker | preco_ajustado
```

Padrão de uso mais comum — pivotar para formato **largo** (uma coluna por
ticker), que é o que o otimizador/covariância geralmente espera:

```python
wide = precos.pivot(index="data", columns="ticker", values="preco_ajustado")
# wide["SPY"], wide[["XLK", "TLT"]], etc.

retornos = wide.pct_change().dropna()      # retornos diários simples
log_ret  = (wide / wide.shift(1)).apply("log").dropna()
```

Tickers disponíveis: `XLK XLU XLP XLF XLE XLV TIP TLT SPY`.
Período: 2003-12-05 → data do último download (janela comum aos 9, sem NaN).

## 2. Probabilidades do FOMC — `polymarket_fed_reunioes.parquet`

Probabilidades implícitas do Polymarket para o desfecho de cada reunião do
FOMC. Formato **longo**: uma linha por (data, mercado).

```python
fed = pd.read_parquet("data/polymarket_fed_reunioes.parquet")
# colunas: data | mercado | probabilidade | volume | evento_id
```

`probabilidade` é o preço do token "Yes" ∈ [0, 1]. Cada reunião tem vários
mercados (corte/alta de 25/50/75 bps, sem mudança), agrupados por `evento_id`.

Séries de uma reunião específica (todos os desfechos de um evento):

```python
uma_reuniao = fed[fed["evento_id"] == "<id>"]
serie = uma_reuniao.pivot(index="data", columns="mercado", values="probabilidade")
```

Snapshot mais recente por mercado (última probabilidade conhecida):

```python
ultimo = fed.sort_values("data").groupby("mercado").tail(1)
```

Notas:
- Granularidade de ~12h (00:00 e 12:00 UTC); alguns gaps de 24-48h são
  leituras faltantes, não outra frequência.
- `volume` é o volume lifetime em USD do mercado (constante, repetido em cada
  linha) — serve para ponderar/filtrar mercados por liquidez.
- Cobertura: 18 reuniões, May/2024 → Jun/2026.

## 3. Ver sem código — dashboard

Abra no navegador (não precisa de servidor):

```bash
open data/dashboard_reunioes_fed.html
```

Lista as reuniões por data; ao clicar, mostra o gráfico das probabilidades de
cada desfecho ao longo do tempo.

## 4. Regenerar os dados (só o Paulo, no branch dele)

```bash
python src/data_pipeline/download_prices.py            # ETFs (config/data_config.json)
python src/data_pipeline/download_polymarket_fed.py    # baixa da API + cache
python src/data_pipeline/separar_mercados_fed.py       # separa reuniões
python scripts/gerar_dashboard_reunioes.py             # regera o HTML
```

Validação:

```bash
pytest tests/test_etf_prices.py tests/test_polymarket_fed.py
```

## Regras de convivência

- **Não regenere** os parquets nos outros branches — consuma o arquivo que já
  está no repo. Mudança de fonte, universo de ativos ou esquema de coluna só
  com decisão registrada em `Decisoes_pendentes.md`.
- Precisa de outro formato de saída (nova coluna, outro recorte)? Peça ao
  Paulo — não edite o pipeline de dados fora do módulo dele.
