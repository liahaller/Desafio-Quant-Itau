# View 3.1 — Recessão (risk-on/off, poly vs curva de juros)

**Status:** 🟢 fechada condicionalmente em sessão com Felipe (2026-07-10) · Família A (divergência + sensibilidade **estimada** por regressão) · fecha as decisões 3 e 4 para esta view · condições: mercado de recessão com histórico (e bid/ask) no CLOB — checagem do Paulo — e pendência de reunião sobre o horizonte (abaixo).

**Origem:** reframe da ideia original "índice de sentimento macro" (3.1 do banco de ideias). O índice agregado foi descartado (dupla contagem com 2.2/2.3, sem benchmark único, receita cheia de parâmetros arbitrários); ficou só o pedaço com dois termômetros de verdade: **recessão**.

## A ideia

A curva de juros americana precifica recessão há décadas: inclinação 10a−3m invertida antecipa recessões (Estrella-Mishkin; modelo usado pelo NY Fed). O Polymarket também precifica recessão, num mercado binário. Quando as duas probabilidades divergem, existe uma reprecificação risk-on/off que o mercado acionário ainda não pagou — a view aposta na reprecificação cross-sectional (cíclicos vs defensivos, SPY vs TLT).

Diferente da 2.3 (onde do ZQ sai esperança em bps, não probabilidade), aqui **os dois lados são probabilidades do mesmo evento** — a divergência direta em pontos de probabilidade é legítima.

## Como funciona (decidido)

0. **Fórmula geral (nunca muda):** `divergencia = p_poly − p_curva`, em pontos de probabilidade. Cascata de degradação (padrão das views fechadas):
   - Mercado binário de recessão disponível → caminho principal (item 1).
   - Nenhum mercado de recessão no período → **view 3.1 desativada**; Ω → ∞; o BL fica no prior. Não é falha, é comportamento correto.
   - Sem bid/ask histórico para reconstruir o midpoint → pendência crítica (mesma condição da 2.4).
1. **De onde vem `p_poly`:** mercado binário de recessão EUA. Critério de resolução: **preferência pela definição técnica** (2 trimestres de PIB negativo — resolve mecanicamente com dado do BEA); mercado NBER só se for o único com liquidez (a declaração atrasada do NBER contamina o preço com incerteza de resolução). Escolha final condicionada ao levantamento do Paulo. Preço da série = **midpoint bid/ask** (nunca último trade — lição da 2.4); pré-processamento pelo módulo da decisão 9: normalização `p_sim + p_não ≠ 1` e correção de favorite-longshot — **relevante aqui**: mercados de recessão vivem em probabilidade baixa, região onde o viés é maior.
2. **De onde vem `p_curva`:** **probit clássico com coeficientes publicados** (Estrella-Mishkin / NY Fed) sobre o spread 10a−3m diário do FRED (`DGS10 − DTB3`). Nenhuma estimação nossa — fórmula publicada, como a duration na 2.2. Frequência diária (casa com o backtest). ⚠️ Adiciona `DGS10`/`DTB3` ao pipeline do Paulo (FRED já entra pela 2.2 via `T10YIE`).
3. **β por ativo (= decisão 3 desta view):** **regressão própria** — retorno diário do ETF vs `Δp_poly`, com a maquinaria da 2.4: **teste de defasagem** `Δp(t−1)→retorno(t)` obrigatório e **β de absorção plena** (soma dos coeficientes dos lags 0…k); janela expandida encerrada antes de cada rebalanceamento, sem lookahead. O benchmark (curva) **entra só no Q, não na regressão**. Sinal do β vem do dado; literatura de ciclo (setores defensivos vs cíclicos) só como sanity check a posteriori, nunca inverte o β.
4. **P (uma única linha sobre os 9 ETFs):** espelha a 2.3 — `P[i] = 2·(β_i − β_SPY) / Σ_j |β_j − β_SPY|`, centro = β_SPY estimado na mesma regressão (`P[SPY] = 0` exato), convenção **Σ|P| = 2**. TIP/TLT entram pelo excesso deles sobre o mercado (coerente: recessão move bonds). ⚠️ Mesmo acoplamento da 2.3: se a origem do β mudar, P muda junto.
5. **Q da linha:** `Q = (Σ_i P[i]·β_i) × (p_poly − p_curva)`. Unidades: divergência em pontos de probabilidade, β em %/ponto → Q em %. Mesma leitura de spread das outras views (retorno do lado comprado − lado vendido) e mesma propriedade da 2.3: `|Q|` cresce com a dispersão dos βs. Como o β é de absorção plena sobre k dias, **Q herda o horizonte de k dias** — mesma pendência transversal de reconciliação com Σ/π da 2.4.
6. **Sanity check de sinal (⚠️ teste obrigatório na implementação):** números inventados, só para fixar o sinal. `p_poly = 0.35`, `p_curva = 0.20` → divergência `+0.15` (poly mais pessimista). β em %/pp: `β_SPY = −0.30`, `β_XLK = −0.45`, `β_XLP = −0.10`, `β_TLT = +0.15`. Então `P ∝ β_i − β_SPY`: XLK `< 0` (short), XLP e TLT `> 0` (long) → **long defensivos/bonds, short cíclicos**, e `Σ P·β > 0` (dominado pelo termo quadrático) → `Q > 0`. Erro de sinal só apareceria no backtest — teste obrigatório.
7. **Ativação/desligamento (herda a regra da 2.4):** existe mercado de recessão → view ativa (liquidez é papel do Ω, sem limiar próprio); **desliga no último dia antes do primeiro tick de resolução** (ex.: o release de PIB que resolve o mercado) — senão o salto de resolução fabrica alfa, mesma lição de 5–6/nov na 2.4.

## Decisões rejeitadas (referência)

- **Índice de sentimento agregado (3.1 original):** dupla contagem com 2.2/2.3; não existe instrumento único precificando "sentimento macro"; pesos/normalização do índice = pilha de parâmetros arbitrários.
- **3.1 como contexto/prior (modulador do Ω):** redundante — o Ω reativo já embute leitura de regime (decisão do Felipe, 2026-07-10). A variante de inclinar o prior brigaria com a decisão 8 (confiança zero → `w_mkt`).
- **Série mensal do NY Fed como benchmark:** oficial, mas mensal (sinal em degraus no backtest diário) e fonte nova fora do FRED/yfinance.
- **Probit estimado por nós:** mais trabalho, parâmetros nossos para defender, risco de lookahead na janela de estimação.
- **Event-study em releases macro para o β:** amostra pequena; Δp_poly em dia de release mistura várias causas.
- **Regressão vs Δdivergência:** mistura o ruído das duas séries e acopla o β à escolha do benchmark.
- **P como par simples SPY−TLT:** descarta a informação cross-sectional (cíclicos vs defensivos) que diferencia recessão de um tilt de juros.
- **Limiar próprio de volume na ativação:** duplica o papel do Ω e cria mais um número para defender.
- **Fallback "só curva" quando não há mercado no poly:** sem poly não há view — a curva sozinha não é sinal do Polymarket.

## Pendências desta view

- ⚠️ **Reunião — horizonte (única decisão de desenho em aberto):** o poly pergunta "recessão até dez/ANO" (janela que encolhe) e a curva enxerga ~12 meses rolantes. Opções mapeadas: (a) aceitar e documentar (divergência mais fiel no início do ano; penalização de fim de ano a cargo do Ω); (b) view ativa só com janela restante ≥ N meses (N humano); (c) reescalar p_poly para equivalente 12m (premissa de modelo extra). Inclui a **rolagem entre mercados anuais** (2024 → 2025): qual mercado usar em cada data.
- **Paulo:** quais mercados de recessão existem no CLOB (2023–25), critério de resolução de cada um (preferência: técnica GDP), volume e **se há bid/ask histórico** para o midpoint — condição da view, como na 2.4.
- **Referência exata dos coeficientes do probit** (paper/tabela do NY Fed) a fixar antes de implementar — publicada, não inventada.
- Parâmetros numéricos por decisão humana: janela amostral da regressão do β; k da defasagem (estimado, mas **acoplado à frequência de rebalance** — pendência transversal compartilhada com a 2.4).
- **Horizonte do Q** (retorno acumulado de k dias) — reconciliar com Σ e π; pendência transversal compartilhada com a 2.4.
