# View C (candidata) — Geopolítica → energia (template poly-defasado)

**Status:** 🟡 **candidata — entrada na carteira em aberto** (entra ou não é decisão de reunião). Desenho fechado em 2026-07-10 **por delegação explícita do Felipe ao Claude na sessão** (escolha de âncora acadêmica, mercados e forma do P — registrado aqui para a trilha de auditoria; demais peças herdam a maquinaria da 2.4 sem decisão nova). Condições (mesmas da 2.4/3.1): **bid/ask histórico no CLOB** para reconstruir o midpoint; cobertura dos mercados na janela do backtest — checagem do Paulo. **Terceira view do template poly-defasado** (com a 2.4; a 3.1 usa a maquinaria de β mas tem benchmark externo).

## A ideia

Eventos geopolíticos (guerra, cessar-fogo, sanções) movem o risco de oferta de petróleo, e o setor de energia reage de forma **oposta** ao resto do mercado: risco de oferta ↑ → petróleo ↑ → XLE sobe enquanto os setores consumidores de energia sofrem (Kilian & Park, 2009). O Polymarket precifica esses eventos em tempo real com alto volume; o mercado acionário absorve com defasagem — a mesma tese da 2.4.

**Não existe instrumento tradicional precificando "probabilidade de ataque/cessar-fogo"** (o petróleo embute, mas não se extrai probabilidade dele) → benchmark = **próprio poly defasado**, template da 2.4: `divergência = p_t − p_{t−k}`.

**Âncoras acadêmicas (escolhidas por delegação; papel = sanity check a posteriori, nunca invertem o β — padrão do projeto):**
- **Kilian & Park (2009, *International Economic Review*)** — a resposta das ações americanas a choques de petróleo depende da origem do choque, e a resposta **setorial** é heterogênea; choques de oferta/risco de oferta beneficiam energia e penalizam setores dependentes de demanda final. É o mapa de sinais esperados do vetor β.
- **Caldara & Iacoviello (2022, *American Economic Review*, índice GPR)** — risco geopolítico medido por eventos E **ameaças** antecipa queda de atividade/investimento e maior downside risk. Legitima usar a **probabilidade** (ameaça, não o ato) como sinal: o risco age antes de o evento acontecer.

## Eventos e mercados (escolhidos por delegação — levantamento web de 2026-07-10; volumes a validar pelo Paulo no CLOB)

- **Evento primário do v1: ação militar EUA/Israel × Irã (2025)** — ex.: "US military action against Iran before July?" (lançado mar/2025, ~$29,9M) e família subsequente ("US strikes Iran by...?", ~$529M, lançado dez/2025). Racional: maior volume da janela do backtest e **canal de petróleo mais limpo** do menu (risco direto sobre oferta — Estreito de Ormuz), episódio de jun/2025 com movimento real de preços para a regressão.
- **Robustness check: família cessar-fogo Rússia × Ucrânia** — mercados por deadline ("before July", "by August 31"…), ~$4,5–17M cada, série mais longa da categoria. Sinal invertido (cessar-fogo ↑ = risco de oferta ↓) — o β estimado por mercado captura o sinal sozinho, sem regra manual.
- **Fora do v1: Israel × Hamas** — volumes menores (~$1–7M) e canal de petróleo indireto (Gaza não é oferta; o canal é escalada regional, que o evento Irã já cobre melhor).
- **Um evento por vez:** a view roda sobre **um** mercado designado por período (como a 2.4 roda sobre p(Trump)) — agregar vários eventos num índice reabriria o defeito que matou a 3.1 original. Mercados com estrutura de deadline ("before X") herdam a pendência de **rolagem entre mercados** da 3.1/B.

## Como funciona (herda a maquinaria da 2.4 — diferenças anotadas)

0. **Ativação e cascata (zero parâmetros):** existe mercado designado ativo → view ativa; sem mercado → **view desativada**, Ω → ∞, BL no prior. Liquidez baixa não desliga (papel do Ω). ⚠️ **Desligamento no último dia antes do primeiro tick de resolução** (o salto de resolução não vira alfa — lição de 5–6/nov da 2.4). Diferença vs 2.4: eventos geopolíticos são **episódicos e recorrentes** — a cascata liga/desliga várias vezes na janela, não uma só.
1. **Sinal do poly:** p(evento) do mercado binário designado, série diária, preço = **midpoint bid/ask** (nunca último trade — série stale infla k), em fração [0,1].
2. **Pré-processamento (módulo da decisão 9):** (a) normalização `p_sim + p_não ≠ 1`; (b) **favorite-longshot relevante** — mercados de ação militar vivem em p baixa (~0,1–0,4), região de viés máximo, como na 3.1 (não como na 2.4); (c) midpoint bid/ask + reportar dias sem trade.
3. **β por ativo:** regressão própria — retorno diário de cada um dos 9 ETFs contra Δp(evento), com as três obrigações da 2.4: **janela expandida sem lookahead** (fim = t−1 do rebalanceamento), **teste de defasagem obrigatório** (Δp(t−1)→retorno(t), varredura de k) e **β de absorção plena** (soma dos coeficientes dos lags 0…k). β estimado **por mercado/evento** (o sinal de "ataque" é oposto ao de "cessar-fogo" — a regressão resolve sem regra manual). Kilian & Park entra só como sanity check de sinal a posteriori.
4. **Benchmark e divergência:** poly defasado — `divergência = p_t − p_{t−k}`, k da varredura de defasagem. Herda da 2.4: acoplamento **k ↔ frequência de rebalance** e a condição permanente **k ≈ 0 → view nunca liga** (pendência de reunião compartilhada).
5. **P (cross-sectional, padrão 2.4/3.1 — decisão por delegação):** `P[i] ∝ (β_i − β_SPY)`, convenção **Σ|P| = 2**, `P[SPY] = 0` exato. O esboço inicial "XLE vs SPY concentrado" foi **substituído**: o par simples é caso particular que descarta a informação cross-sectional (mesma rejeição da 2.4/3.1) — se o β do XLE dominar, o P concentra em XLE **sozinho**, sem regra manual; e defensivos/TLT também reagem a geopolítica (Caldara-Iacoviello: downside risk). Legibilidade recuperada de graça: reportar a "cesta implícita" (β ordenado) no slide.
6. **Q da linha:** `Q = (Σ_i P[i]·β_i) × (p_t − p_{t−k})` — o mesmo β define P e Q, sem parâmetro livre. Unidades: p em fração, β em %/unidade de probabilidade → **Q em %, acumulado em k dias** (herda a pendência de horizonte do Q vs Σ/π da 2.4). Herda também a checagem do perfil de lags (spike vs resposta distribuída).
7. **Sanity check de sinal (⚠️ teste obrigatório na implementação):** números inventados, só para fixar o sinal. Mercado "ação militar contra o Irã": p sobe de 0,20 para 0,35 em k dias → divergência `+0,15`. β em %/unidade: `β_XLE = +4,0`, `β_SPY = −1,0`, `β_XLK = −2,0` → P: XLE long (β_XLE − β_SPY = +5), XLK short (−1) → `Σ P·β > 0` → `Q > 0`: **long XLE, short cíclicos** com risco de oferta subindo — bate com Kilian & Park. No mercado de cessar-fogo os β saem com sinais trocados e a mesma fórmula funciona.

## Decisões rejeitadas (referência)

- **Herdadas da 2.4** (mesma maquinaria, valem igual): último trade como preço; interruptor binário por liquidez; janela de ativação "N dias antes"; β da literatura como fonte de valores; prob implícita por inversão de regressão.
- **Par simples XLE − SPY** (o esboço inicial): caso particular do P cross-sectional que joga fora informação já estimada; mesma rejeição de "par simples/cesta" das views 2.4 e 3.1.
- **Índice agregado de vários eventos geopolíticos:** pilha de pesos arbitrários — o defeito que matou a 3.1 original; um evento designado por vez.
- **Israel × Hamas no v1:** volume menor e canal de petróleo indireto; coberto pelo robustness só se a reunião pedir.
- **Petróleo (USO/WTI) como benchmark externo:** o preço do petróleo embute a probabilidade mas não a revela (mistura estoque, demanda, dólar) — não existe divergência extraível; foi exatamente isso que empurrou a view para o template poly-defasado.
- **XLE como ativo novo dedicado + opções de energia:** fora do universo fechado (decisão 1) — o XLE já está no universo; nada a adicionar.

## Pendências desta view

- ⚠️ **Reunião — entra ou não.** O desenho está fechado; a entrada na carteira, não.
- **Paulo:** confirmar no CLOB os mercados Irã 2025 (e família) e Rússia×Ucrânia — cobertura na janela do backtest, volume, critério de resolução e **bid/ask histórico** (condição da view, como na 2.4/3.1). Os volumes citados acima vieram de levantamento web (páginas públicas do Polymarket, 2026-07-10) e precisam ser validados no dado.
- **Rolagem entre mercados de deadline** ("before July" → "by August 31"…): mesma pendência de horizonte da 3.1/B — decidir as três juntas na reunião.
- **k ≈ 0 (herdada da 2.4):** fallback contemporâneo vs view fora do v1 — decisão de reunião compartilhada.
- **Horizonte do Q** (acumulado de k dias) vs Σ/π — pendência transversal compartilhada (2.4/3.1/C).
- **Parâmetros numéricos por decisão humana:** limiar de volume para estimabilidade do β; frequência de rebalance (acoplada ao k).
- **Medir ΣP empiricamente** (centragem em β_SPY) — decisão conjunta com 2.3/2.4/3.1, nunca de uma view só.
