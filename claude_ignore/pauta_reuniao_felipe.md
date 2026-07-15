# Pauta de reunião — itens do Felipe (Camadas 1 e 2)

Itens 100% dentro do meu escopo (views + integração + tática). Não dependem da Lia (Ω) nem da calibração (favorite-longshot/bucket aberto) nem de dado do Paulo — são decisões de **desenho e escala**, fecháveis na reunião sem esperar ninguém.

---

## 1. Entrada das views candidatas B/C/E/G na carteira — Camada 1
Código pronto e testado; falta decidir **quais entram de fato** na lista que vai pro backtest.

- **B (trajetória do Fed):** entra? E o **reuso do β da 2.3** é aceito? → risco de exposição dupla ao fator juros (2.3 + B).
- **C (geopolítica→energia):** entra? → risco de dupla exposição a XLE.
- **E (tarifas):** entra? → β com fragilidade documentada no doc da view.
- **G (fiscal):** entra ou fica reserva? → nasceu como reserva; paradoxo do TLT no teto sem sinal a priori.

**Trava:** define o universo de views do backtest (argumento de `bl_weights_from_views`).

## 2. Orçamentos da camada tática — Camada 2
3 táticas implementadas (somam `dw` por cima do BL via `apply_overlays`). Falta o **tamanho da aposta** de cada uma (número — CLAUDE.md §6):

- `orcamento_max` — teto do tilt long SPY no dia de anúncio (`dw[SPY] = orcamento_max × H(p)/H_max`).
- `orcamento_acoes` / `orcamento_rf` — livros SPY e TLT do drift (por livro ou comum?).
- `lam` (λ) — ganho do gap de fim de semana (`dw = λ × Σ β·Δp`).
- Sub-questões: janelas `15/50` dias do drift; expectativa da véspera = **ZQ vs E_poly**; micro-surpresas (posição cheia por sinal vs proporcional); desmonte do gap em 1 vs k dias; precedência tilt × rebalance no mesmo dia.

**Trava:** sem os orçamentos as táticas ficam inertes.

## 3. Critério de escolha do k (defasagem) — Camada 1 · decisão 12 🟡
Views defasadas (2.4/3.1/C/E/G): `lag_regression` devolve o perfil de coeficientes; o Q usa o β de absorção plena (soma dos lags 0…k). Falta o **critério que escolhe o k**.

- Opções: (a) inspeção do perfil real na reunião · (b) último lag significativo (exige limiar de t-stat) · (c) máximo R² ajustado (pode pegar k grande por ruído).
- **Encaminhamento (Felipe):** opção (a) — fecha com o perfil real na mesa quando o dado do Paulo chegar.

**Trava:** hoje `k` entra como argumento humano; sem ele os `build_view` das defasadas não rodam.

## 4. Horizonte das views 3.1/B + fallback k≈0 da 2.4 — Camada 1
- **Horizonte 3.1/B:** poly "recessão até dez" (janela que encolhe) **vs** curva 12m rolante + rolagem entre mercados anuais. Decidir qual.
- **k≈0 na 2.4:** se a defasagem ~0, a view **nunca ativa** (por construção). Fallback: tilt contemporâneo `Q = β·Δp` **vs** tirar a 2.4 do v1.

## 5. Reconciliação do horizonte do Q — Camada 1 (integração) ⚠️ sem dono
As views defasadas produzem `Q` = **retorno acumulado de k dias** (`horizonte_q_dias = k`); a prior π e o Σ são **diários**. Empilhar view de k dias com view diária no mesmo `stack_views` **mistura unidades de horizonte** → resultado errado.

**Decidir:** como reconciliar (converter o Q pra diário? anualizar tudo?) **antes** de escrever o loop de rebalanceamento. Trava o backtest misturar defasadas com diárias.

## 6. Valores de τ e δ — Camada 1 (otimizador)
Dois botões do BL sem valor decidido (testes usam sintéticos):

- **τ (tau):** escala a incerteza da prior (`τΣ`) — quanto as views deslocam do `w_mkt`. Puro otimizador → Camada 1.
- **δ (delta):** aversão a risco no passo `w = inv(δΣ)μ`. ⚠️ **Ressalva:** δ = dimensionamento de risco, que o mapa coloca na Camada 3 (pode viver dentro do Ω). Tem um pé fora de 1/2 — alinhar com a Lia se o Ω vai mexer nisso.

---

**Fora desta lista (não são meus / travam dado real):** decisão 11 (favorite-longshot + bucket aberto — Camada 4), decisão 6 (Ω reativo — Lia, Camada 4), dado com bid/ask do Paulo.
