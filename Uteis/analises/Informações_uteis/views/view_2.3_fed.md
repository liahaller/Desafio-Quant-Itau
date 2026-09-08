# View 2.3 — Fed (surpresa de juros, Bernanke-Kuttner)

**Status:** 🟢 fechada em reunião (2026-07-09) · Família A (divergência + sensibilidade **estimada** por regressão) · fecha as decisões 3 e 4 para esta view.

## A ideia

Bernanke-Kuttner: só a parte **surpresa** de uma decisão de juros move ações, e setores long-duration (tech) reagem mais que defensivos. O Polymarket precifica a decisão do FOMC; os Fed Funds futures também. Quando as duas expectativas divergem, existe uma surpresa esperada que o mercado acionário ainda não pagou — a view aposta na reprecificação cross-sectional (quem é mais sensível a juros se move mais).

## Como funciona (decidido)

0. **Fórmula geral (nunca muda):** `surpresa = E_poly[Δtaxa] − E_FF[Δtaxa]`, em bps. `E_FF` **nunca degrada** — sai sempre do ZQ, sempre como esperança em bps (item 2). O que degrada é apenas **como se calcula `E_poly`**:
   - PMF de buckets disponível → caminho principal (item 1).
   - Apenas mercado binário → `E_poly = p_poly × 25bp` (fallback).
   - Nenhum mercado de FOMC no período → **view 2.3 desativada**; Ω → ∞; o BL fica no prior. Não é falha, é comportamento correto.
   (Sub-decisão análoga ao item 0 da view 2.2.)
1. **De onde vem `E_poly`:** os mercados de FOMC são buckets de decisão (−50bp, −25bp, manutenção, +25bp…) — uma PMF. `E_poly[Δtaxa] = Σ pᵢ · Δtaxaᵢ`, em bps.
2. **De onde vem `E_FF`:** extraído do preço do **Fed Funds future (ZQ, yfinance)**. Registrar: o que sai do ZQ é uma **esperança em bps, não uma probabilidade**; usar o **contrato do mês posterior à reunião** para evitar o ajuste de média de dias dentro do mês da reunião.
3. **β por ativo (= decisão 3 desta view):** **regressão própria** — event-study nos dias de FOMC, retorno do ativo contra a **surpresa à la Kuttner** (variação do FF future no dia do anúncio), **não** contra o Δtaxa bruto. A literatura (B-K e extensões) entra como **sanity check de sinal e magnitude, não como fonte de valores**.
4. **P (uma única linha sobre os 9 ETFs):** `P[i] = 2·(β_i − β_SPY) / Σ_j |β_j − β_SPY|`.
   - **Escala (reunião 2026-07-10):** fator 2 = convenção única **Σ|P| = 2** entre todas as views (2.2 e 2.4 já estavam nela). A convenção original desta view (Σ|P| = 1, leitura de média ponderada) foi substituída para que os Q e o Ω fiquem comparáveis entre views.
   - **Sub-decisão:** a linha de P **não é construída à mão** — é função determinística do vetor β estimado.
   - Centro = **β_SPY estimado na mesma regressão** (β_SPY ≈ média cap-weighted por construção) → `P[SPY] = 0` exato; cada peso é a sensibilidade **em excesso** ao mercado.
   - TIP/TLT entram pelo excesso deles sobre o mercado — a view também tilta os bonds (coerente: são sensíveis a juros), a linha não é puramente setorial.
   - ⚠️ **Acoplamento:** origem do β (regressão própria) → centro (β_SPY estimado). Se o β passasse a vir da literatura, não haveria β_SPY estimado e a construção de P quebraria — decisões co-documentadas aqui de propósito. Se a origem do β mudar, P muda junto.
5. **Q da linha:** `Q = Σ_i P[i] · β_i · surpresa = surpresa · Σ_i P[i] · β_i` — determinístico dado o vetor β e a surpresa esperada. Unidades: surpresa em bps, β em %/bp → Q em %. `Q` é o **retorno esperado do portfólio long-short definido por P**: como `Σ|P[i]| = 2` (≈1 unidade comprada e 1 vendida; aproximado porque ΣP ≠ 0 pela centragem em β_SPY), lê-se como **retorno do lado comprado menos o do lado vendido** (retorno do spread) — não o retorno de nenhum ativo específico. O fator 2 do P dobra o Q automaticamente pela própria fórmula; ninguém ajusta Q à mão.
   - **Propriedade do desenho (não é bug):** como `P[i] ∝ (β_i − β_SPY)`, o termo `Σ_i P[i] · β_i` é proporcional à **dispersão** dos βs em torno de β_SPY. Consequência: `|Q|` cresce quando os ativos discordam mais entre si quanto à sensibilidade a juros, e tende a zero quando todos têm β parecido.
6. **Sanity check de sinal (⚠️ teste obrigatório na implementação):** poly precifica corte maior que o ZQ → `E_poly < E_FF` → `surpresa < 0`. Exemplo numérico (números inventados, só para fixar o sinal): `E_poly = −20bp` (80% de chance de corte de 25bp), `E_FF = −10bp` → `surpresa = −10bp`. `β_XLK = −0.08%/bp` (long-duration sobe quando juros caem, β < 0) → retorno esperado de XLK = `(−0.08) × (−10) = +0.8%` → **XLK entra long**. Erro de sinal aqui só apareceria no backtest — por isso o teste é obrigatório.

## Decisões rejeitadas (referência)

- **Divergência direta em probabilidade** (`Q = β′ × (p_poly − p_FF)` sem converter para bps): mistura tamanho do movimento com probabilidade, o β′ perde a comparação com a literatura — e pressupõe um `p_FF` que não existe (do ZQ sai esperança, não probabilidade). No caso binário o que degrada é só o lado do poly: `E_poly = p_poly × 25bp` (item 0).
- **β da literatura como fonte de valores:** amostra antiga (1989–2002), não casa 1:1 com os ETFs do universo. Mantida só como sanity check.
- **Regressão própria sem sanity check:** preterida pela versão com validação contra a literatura.
- **FedWatch (scrape/manual)** como benchmark: sem API oficial, frágil para backtest.
- **Proxy por yield curto (SHY/IRX):** não entrega uma esperança comparável à do poly.
- **P como par simples (ex. XLK−XLU) ou cesta vs cesta:** casos particulares que descartam a informação cross-sectional da regressão.
- **Centro β̄ = média simples dos 9:** contaminada pelos βs de duration de TIP/TLT; SPY sobraria com peso residual arbitrário.
- **Centro β̄ = média cap-weighted dos setores do universo:** só 6 dos 11 setores do S&P estão no universo (aproximação pior que β_SPY) e exigiria pesos de capitalização como dado extra.

## Pendências desta view

- **Paulo: cobertura histórica dos mercados de FOMC no Polymarket** (buckets por reunião, liquidez) — análoga à pendência crítica da 2.2.
- **Paulo: profundidade/qualidade do histórico do ZQ no yfinance** (contratos mensais para o backtest).
- Dados da regressão: datas de FOMC + variação do FF future no dia do anúncio (a surpresa à la Kuttner) — fonte a acordar.
- Pré-processamento das probs dos buckets: virou **decisão 9** em `Decisoes_pendentes.md` (módulo compartilhado de PMF entre views 2.2 e 2.3 — verificar antes se se comporta igual nas duas).
- Parâmetros numéricos da regressão (janela amostral, frequência diária vs intradiária) — decisão humana antes de implementar, não inventar em código.
