# Paulo — Dados

## Norte geral

Sua missão é montar a matéria-prima histórica que alimenta todo o modelo. O modelo precisa de duas séries temporais alinhadas: preços dos ativos e probabilidades do Polymarket. Se os dados estiverem errados ou desalinhados, o modelo inteiro dá resultado errado — você é a fundação. O seu entregável final é **um dataset unificado de backtest**: uma tabela onde cada dia tem os preços dos ETFs e as probabilidades correspondentes.

## O que fazer

### 1. Pipeline de preços dos ETFs (Semana 1)

**O quê:** baixar e validar o histórico diário dos 9 ativos já decididos (Decisão 1, fechada): XLK, XLU, XLP, XLF, XLE, XLV, TIP, TLT, SPY.

**Como:**
- Usar yfinance, frequência diária.
- Validar: sem buracos nas séries, datas alinhadas entre os tickers, splits/dividendos ajustados (usar preço ajustado).
- Salvar em formato padronizado (ex. um CSV/parquet por ticker ou tabela única longa) e documentar o formato no repositório.

**Deadline:** 13/jul.

### 2. Fonte de probabilidades do Polymarket (Semana 1) — Decisão 2

**O quê:** resolver o gargalo do projeto. A API gratuita do Polymarket (CLOB, endpoint `/prices-history`) só entrega granularidade de 12h+ para mercados já resolvidos — insuficiente para backtest fino.

**Como:** implementar o caminho já recomendado nas discussões:
- **Path B:** proxies de mercado tradicional (ex. CME FedWatch para probabilidades de decisão do Fed) — mais defensável para a competição.
- **Path B+D:** combinar com PolymarketData.co (fonte paga, dados a partir de meados de 2025) se o orçamento permitir.
- Registrar a decisão final e a justificativa em `Decisoes_pendentes.md`.

**Deadline:** 13/jul.

### 3. Dataset unificado de backtest (Semana 2)

**O quê:** juntar as duas pernas numa tabela única: cada data casa preço de ETF com probabilidade daquele mesmo dia.

**Como:**
- Alinhar calendários (dias úteis dos ETFs vs. dados contínuos das probabilidades — definir regra de junção, ex. última probabilidade disponível até o fechamento do pregão).
- Tratar dados faltantes com regra explícita e documentada (forward-fill, exclusão, etc.).
- Entregar com um script de validação que qualquer membro consiga rodar.

**Deadline:** 20/jul.

### 4. Backtest com Felipe (Semana 3)

Rodar o backtest completo junto com Felipe, validar resultados e iterar em bugs. **Deadline: 25/jul.**

### 5. Fechamento (Semana 4)

Revisar e limpar o código/repositório com Felipe. **Deadline: 30/jul.**

## Organização com Claude Code

- Trabalhe no seu branch; você é dono dos módulos de dados (ninguém mais edita sem avisar).
- Toda sessão: começar lendo `Decisoes_pendentes.md`, terminar atualizando-o + entrada no `LOG.md`.
- Delegue ao Claude Code o mecânico (baixar dados, checar buracos, validar cobertura); as decisões de fonte e regra de junção são suas.
