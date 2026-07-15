# Pauta de reunião — itens de outros donos (Paulo / Lia) e calibração

O que falta que **não é meu** — depende do Paulo (dado), da Lia (Ω/relatório) ou de decisão metodológica de calibração. Estes travam o backtest rodar com dado real.

---

## PAULO — dados

**Condição crítica (trava 2.4/3.1/C/E/G e a decisão 9):**
- Fonte do poly com **bid/ask histórico** no CLOB. `poly_preprocessing.midpoint_price` precisa de bid e ask crus. ⚠️ O mandato do Paulo não inclui limpeza de Polymarket; se a fonte final só der último trade, o midpoint some e as views defasadas perdem a condição de fechamento.

**Cobertura de mercados no CLOB:**
- CPI (buckets/PMF) e FOMC (buckets/PMF) — views 2.2 e 2.3.
- Recessão (preferência: resolução técnica GDP) — view 3.1.
- Presidencial 2024, binário p(Trump) — view 2.4.
- Tarifas EUA×China + recíprocas — condição da E.
- Fiscal OBBB + teto/X-date — condição da G.
- Geopolítica Irã 2025 + Rússia×Ucrânia — condição da C.
- ⚠️ **Critério de resolução dos mercados de bucket** (terminal vs one-touch): mercados de commodities do poly podem resolver por one-touch; a receita "média da PMF" não transfere sem checar isso.

**Outras fontes:**
- FRED: T10YIE (breakeven 10a → 2.2); DGS10 e DTB3 → spread 10a−3m (3.1).
- ZQ (Fed Funds futures) no yfinance — E_FF da 2.3 e ZQ dezembro da B; a conversão preço → E_FF em bps fica a montante da view (de qual taxa corrente subtrair a implícita).
- Coeficientes exatos do probit (Estrella-Mishkin/NY Fed) — referência a fixar antes de implementar a 3.1.

**Requisitos do backtest:**
- **Marcação diária contínua** das posições táticas (o livro TLT do drift ≈ 42 dias úteis por reunião — bem mais pesado que os ~20 dias/ano da 1.3).
- Calendário de releases do CPI (dado novo).
- Preço de **abertura de segunda** dos ETFs (gap de fim de semana).
- Snapshots de fim de semana do poly.

## LIA — Ω reativo + relatório

- **Decisão 6 🟡 — forma funcional do Ω reativo** (Camada 4): como volume, estabilidade, convergência e proximidade de evento viram um número de confiança. **Delegada à Lia (reunião 08/07)**; protocolo de calibração proposto por ela já registrado na seção 6 de `Decisoes_pendentes.md` (baseline He-Litterman escalado por confiança c; forma multiplicativa com volume como veto; parâmetros por teste de monotonicidade no histórico). **Trava a integração:** view ativa sem Ω falha alto de propósito (`bl_integration.py` não inventa confiança). Dependência nova → Paulo: disponibilidade de **volume histórico** do poly no pipeline.
- **Validar o campo `diagnostics`** do `ViewResult` como insumo do Ω (formato não travado — decisão 6 aberta).
- **Nota de interação Ω ↔ camada tática:** a mesma incerteza entra com sinais opostos nos dois módulos — documentar para o Ω não neutralizar a tática por construção. Hoje **4 módulos leem o calendário FOMC**: 2.3 (antes), 1.3 prêmio de anúncios (no dia), drift (depois), gap (nas segundas).
- **Relatório:** SWZ como guarda-chuva metodológico do bridge probabilidade→Q (achado da pesquisa, para embasar o relatório).

## CALIBRAÇÃO (decisão de reunião — Camada 4, sem dono fixo)

- **Decisão 11 🔴 — pré-processamento das probabilidades** (`poly_preprocessing.py`, stubs que falham alto):
  - **(11a) Forma do favorite-longshot bias:** calibração própria sobre mercados resolvidos vs curva da literatura (Page & Clemen) vs sem correção no v1. Relevância máxima na 3.1 (p baixa), segunda ordem na 2.4.
  - **(11b) Valor do bucket aberto** das PMFs (ex. "≤3.6%"): ponto médio extrapolado vs valor fixo vs truncar no limite.
  - **Trava TODAS as views com dado real** — os stubs levantam `NotImplementedError` de propósito.

---

## Avisos pendentes do Felipe → Paulo/Lia (mudanças no branch Felipe, valem após merge)
- Decisão 10 (camada tática adiada e reformulada; módulo da Lia reduzido a "Ω reativo · Relatório" no CLAUDE.md).
- Deleções de arquivos `.md` (Cronograma, Mapa, FELIPE_arquitetura, Ideias_consolidadas).
- Felipe assumiu **alinhar a fonte do poly com bid/ask** diretamente com o Paulo.
