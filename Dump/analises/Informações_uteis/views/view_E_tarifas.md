# View E (candidata) — Tarifas / política comercial (template poly-defasado)

**Status:** 🟡 **candidata — entrada na carteira em aberto** (entra ou não é decisão de reunião). Desenho fechado em sessão com Felipe (2026-07-10): mercado designado = família **EUA×China** (Q1-A), β aceito com fragilidade documentada (Q2). Condições (mesmas da 2.4/C): **bid/ask histórico no CLOB** para reconstruir o midpoint; cobertura dos mercados na janela do backtest — checagem do Paulo. Embasamento completo da pesquisa: `Informações_uteis/Pesquisa_embasamento_novas_ideias.md`.

## A ideia

Tarifas mudam o valor dos setores de forma heterogênea: quem depende de cadeia global (tech) sofre; domésticos/defensivos quase não sentem; e anúncios tarifários derrubam yields de Treasuries (flight to safety → **TLT sobe**). O Polymarket precifica eventos tarifários em tempo real com alto volume (2025 inteiro); a bolsa absorve com defasagem — a mesma tese da 2.4.

**Não existe instrumento tradicional precificando "probabilidade de tarifa"** → benchmark = **próprio poly defasado**, template da 2.4: `divergência = p_t − p_{t−k}`.

**Âncoras acadêmicas (papel = sanity check a posteriori, nunca invertem o β — padrão do projeto):**
- **Amiti, Gomez, Kong & Weinstein — "Trade Protection, Stock-Market Returns, and Welfare" (WP, NBER/RBA 2024)** — event-study da guerra comercial EUA-China: 11 anúncios somam −11,5% no mercado; cross-section por exposição à China com piora real subsequente (lucro, emprego, produtividade); **flight to safety em Treasuries**. É o mapa de sinais esperados do vetor β (incluindo TLT positivo).
- **Caldara, Iacoviello, Molligo, Prestipino & Raffo (2020, *Journal of Monetary Economics*, índice TPU)** — a *incerteza* de política comercial já contrai investimento e atividade antes de qualquer tarifa vigorar. Legitima usar a **probabilidade** (ameaça, não o ato) como sinal — mesmo papel do GPR na view C.
- **Benchmark dos episódios da janela:** event-studies de 2025 já publicados (ex.: "Tariffs announcement as a global stress test", *Finance Research Letters* 2025) para conferir os β estimados.

## Eventos e mercados (decisão do Felipe, sessão 2026-07-10)

- **Evento primário do v1: família EUA×China** (imposição/escalada de tarifas sobre a China) — canal mais estudado na literatura (toda a âncora AGKW é EUA×China) e volume alto na janela. Mercados específicos e binário-mãe por período a validar pelo Paulo no CLOB (critério de liquidez, como nas demais).
- **Robustness check: família de tarifas recíprocas/"Liberation Day" (2025)** — episódio com maior movimento de mercado da janela; sinal esperado igual (tarifa ↑ = risco ↑).
- **Um evento por vez:** a view roda sobre **um** mercado designado por período (regra herdada da 2.4/C); eventos tarifários são episódicos e recorrentes — a cascata liga/desliga várias vezes na janela, como na C.

## Como funciona (herda a maquinaria da 2.4 — diferenças anotadas)

0. **Ativação e cascata (zero parâmetros):** existe mercado designado ativo → view ativa; sem mercado → view desativada, Ω → ∞, BL no prior. Liquidez baixa não desliga (papel do Ω). ⚠️ **Desligamento no último dia antes do primeiro tick de resolução** (o salto de resolução não vira alfa — lição de 5–6/nov da 2.4).
1. **Sinal do poly:** p(evento tarifário) do binário designado, série diária, preço = **midpoint bid/ask** (nunca último trade), em fração [0,1].
2. **Pré-processamento (módulo da decisão 9):** (a) normalização `p_sim + p_não ≠ 1`; (b) favorite-longshot — mercados de tarifa viveram em faixas amplas de p em 2025 (registrar o nível observado na validação; ver achado transversal do "Yes bias" na pesquisa); (c) midpoint bid/ask + reportar dias sem trade.
3. **β por ativo:** regressão própria — retorno diário de cada um dos 9 ETFs contra Δp(evento), com as três obrigações da 2.4: **janela expandida sem lookahead** (fim = t−1 do rebalanceamento), **teste de defasagem obrigatório** (Δp(t−1)→retorno(t), varredura de k) e **β de absorção plena** (soma dos coeficientes dos lags 0…k). β estimado **por mercado/família** (o sinal de "tarifa nova" é oposto ao de "acordo comercial" — a regressão resolve sem regra manual). AGKW entra só como sanity check de sinal a posteriori.
4. **Benchmark e divergência:** poly defasado — `divergência = p_t − p_{t−k}`, k da varredura de defasagem. Herda da 2.4: acoplamento **k ↔ frequência de rebalance** e a condição permanente **k ≈ 0 → view nunca liga** (pendência de reunião compartilhada).
5. **P (cross-sectional, padrão 2.4/3.1/C):** `P[i] ∝ (β_i − β_SPY)`, convenção **Σ|P| = 2**, `P[SPY] = 0` exato. TLT participa do cross-section como qualquer ativo (flight to safety documentado — nada de caminho especial).
6. **Q da linha:** `Q = (Σ_i P[i]·β_i) × (p_t − p_{t−k})` — o mesmo β define P e Q, sem parâmetro livre. Unidades: p em fração, β em %/unidade de probabilidade → **Q em %, acumulado em k dias** (herda a pendência de horizonte do Q vs Σ/π).
7. **Sanity check de sinal (⚠️ teste obrigatório na implementação):** números inventados, só para fixar o sinal. p(tarifa EUA×China) sobe de 0,30 para 0,50 em k dias → divergência +0,20. β em %/unidade: `β_XLK = −2,5`, `β_SPY = −1,0`, `β_XLP = +0,5`, `β_TLT = +1,0` → P: XLK short (β_XLK − β_SPY = −1,5), XLP long (+1,5), TLT long (+2,0) → `Σ P·β > 0` → `Q > 0`: **long defensivos/TLT, short tech** com risco tarifário subindo — bate com AGKW (expostos à China sofrem; flight to safety). No mercado de "acordo comercial" os β saem com sinais trocados e a mesma fórmula funciona.

## Decisões fechadas nesta view (sessão 2026-07-10)

- **Q1-A — família fixa de evento** (EUA×China primário, recíprocas como robustness), espelhando a C (Irã primário, Rússia robustness).
- **Q2 — β aceito com fragilidade documentada:** episódios concentrados em 2025 (janela curta, saltos correlacionados); sem condição extra de amostra mínima — herda o limiar de volume p/ estimabilidade já pendente da 2.4 (parâmetro humano).

## Decisões rejeitadas (referência)

- **Herdadas da 2.4** (mesma maquinaria, valem igual): último trade como preço; interruptor binário por liquidez; janela de ativação "N dias antes"; β da literatura como fonte de valores; prob implícita por inversão de regressão.
- **Q1-B — mercado de maior volume do tema a cada período:** a série troca de mercado no meio e quebra a estimação de k e β.
- **Índice agregado de vários mercados de tarifa:** pilha de pesos arbitrários — o defeito que matou a 3.1 original; um evento designado por vez.
- **Condição extra de amostra mínima para o β:** mais um parâmetro para defender; a fragilidade fica documentada e o limiar de volume da 2.4 cobre a estimabilidade.

## Pendências desta view

- ⚠️ **Reunião — entra ou não.** O desenho está fechado; a entrada na carteira, não (discutir junto com B/C e demais candidatas).
- **Paulo:** confirmar no CLOB os mercados da família EUA×China (2024–25) e recíprocas/"Liberation Day" — cobertura na janela do backtest, volume, critério de resolução e **bid/ask histórico** (condição da view); indicar o binário-mãe por período pelo critério de liquidez.
- **k ≈ 0 (herdada da 2.4):** fallback contemporâneo vs view fora do v1 — decisão de reunião compartilhada.
- **Horizonte do Q** (acumulado de k dias) vs Σ/π — pendência transversal compartilhada (2.4/3.1/C/E).
- **Parâmetros numéricos por decisão humana:** limiar de volume para estimabilidade do β (herdado da 2.4); frequência de rebalance (acoplada ao k).
- **Medir ΣP empiricamente** (centragem em β_SPY) — decisão conjunta com 2.3/2.4/3.1/C, nunca de uma view só.
- **Sanity check do TLT:** conferir na estimação o sinal positivo esperado (flight to safety) — se a regressão der TLT negativo, reportar antes de usar (o β manda, mas a divergência com a âncora precisa estar registrada).
