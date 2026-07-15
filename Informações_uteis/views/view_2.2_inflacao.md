# View 2.2 — Inflação (TIP vs TLT)

**Status:** 🟢 fechada em reunião (2026-07-09) · **Exceção à Família A**: não usa o template `Q = sensibilidade × divergência` com sensibilidade estimada — é tradução mecânica (`Q = duration × Δinflação`, sem regressão) · fecha as decisões 3 e 4 para esta view.

## A ideia

O mercado embute uma inflação esperada no **breakeven** (yield nominal − yield real dos TIPS). O Polymarket dá probabilidades sobre o CPI. Quando a inflação implícita no poly diverge do breakeven, existe uma reprecificação esperada que o mercado de títulos ainda não pagou: poly acima do breakeven → long TIP / short TLT; abaixo → o inverso.

A âncora acadêmica é Fisher/breakeven: a sensibilidade é renda fixa básica (`retorno ≈ duration × Δinflação`), **sem regressão** — por isso a decisão 3 (β da view) se resolve mecanicamente aqui: **β = duration**.

## Como funciona (decidido)

0. **Cascata de degradação (fallback):**
   - Buckets de CPI disponíveis → média da PMF (caminho principal, item 1).
   - Apenas mercado binário disponível → normal deslocada com vol histórica do CPI: encontra a média que faz `P(CPI > X) = prob_poly`.
   - Nenhum mercado de CPI no período → **view 2.2 desativada**; Ω → ∞; o BL fica no prior. Não é falha, é comportamento correto.
1. **Sinal do poly:** os mercados de CPI do Polymarket são **buckets exatos** (≤3.6%, 3.7%, 3.8%, 3.9%, 4.0%…) — uma **PMF**, não uma CDF de thresholds. A inflação esperada sai direto: `E[CPI] = Σ pᵢ · xᵢ`.
2. **Pré-processamento das probabilidades** (antes de calcular a média):
   - **Normalizar** — as probabilidades não somam 1 por causa do spread bid/ask.
   - **Correção de favorite-longshot bias** (Camada 4) — morde na cauda direita: buckets de 4.2%+ com volume baixo e preço <1%.
   - **Bucket aberto ≤3.6%** precisa de um valor atribuído (ex. 3.55%) para entrar na média.
3. **Benchmark de mercado + duration (acoplados):** **breakeven de 10 anos** — série `T10YIE` do FRED — com **duration = a do breakeven de 10 anos (~8)**. Benchmark e duration são acoplados; alterar um exige alterar o outro. ⚠️ Adiciona FRED como fonte no pipeline do Paulo (precisa de acordo com ele).
4. **Divergência:** em **pontos de inflação**: `Δinflação = inflação_poly − breakeven_10a`.
5. **Q (retorno esperado do par TIP − TLT):** `Q = duration × Δinflação`.
6. **P:** linha relativa `TIP − TLT` (par +1/−1, dentro do universo da decisão 1) — já na convenção padrão entre views **Σ|P| = 2** (reunião 2026-07-10; registro na decisão 4).

## Decisões rejeitadas (referência)

- **Unidade da divergência em probabilidade** (converter breakeven em prob do evento do poly assumindo distribuição do CPI): exigia premissa distribucional + uma sensibilidade prob→retorno extra.
- **Prob→inflação linear no threshold** (`X + k×(prob−0.5)`): parâmetro `k` arbitrário a mais.
- **Duration do TLT (~17a)** e **duration do TIP (~7a)** como conversor: escolhida a do benchmark (10a, ~8) por consistência com a série usada na divergência.
- **Proxy de breakeven via ETFs (TIP/IEF no yfinance)**: ruidoso, exigia calibração própria.
- **Breakeven casado com o horizonte do mercado do poly** (5a/1a): mais coerente conceitualmente, dados curtos mais difíceis.

_Nota:_ a "normal deslocada com vol histórica" não foi descartada — virou o **fallback** do item 0 quando só houver mercado binário.

## Pendências desta view

- **Paulo: levantar a cobertura histórica dos mercados de CPI no Polymarket nos últimos ~18 meses** (quantos meses têm mercado listado e líquido). É a única pendência que pode invalidar a view inteira.
- Valor exato da duration (~8) confirmar com dado real na implementação — parâmetro numérico registrado, não inventado em código.
- Acordo com Paulo para incluir FRED (`T10YIE`) no pipeline.
