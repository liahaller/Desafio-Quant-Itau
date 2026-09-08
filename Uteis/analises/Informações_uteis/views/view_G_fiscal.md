# View G (candidata-reserva) — Legislação fiscal: tributária + teto da dívida (template poly-defasado)

**Status:** 🟡 **candidata-RESERVA — entrada na carteira em aberto** (decisão de reunião; por decisão do Felipe em sessão 2026-07-10, G entra na fila já marcada como reserva: só sobe se a reunião derrubar outra candidata ou quiser mais amplitude — é o β mais frágil do lote, poucos episódios na janela). Desenho fechado em sessão (2026-07-10): evento primário = **legislação tributária** (Q1-A), reserva (Q2). Condições (mesmas da 2.4/C/E): **bid/ask histórico no CLOB**; cobertura na janela do backtest — Paulo. Embasamento: `Informações_uteis/Pesquisa_embasamento_novas_ideias.md`.

**⚠️ Reorientação registrada (pesquisa 2026-07-10):** a ideia nasceu como "shutdown/fiscal" (antiga candidata D). A literatura derrubou o pedaço shutdown — S&P flat/positivo em 10 dos 13 shutdowns, ~2 bps em Treasuries — e sustentou dois pedaços com efeito real: **legislação tributária** e **teto da dívida**. Shutdown está fora como evento (ver rejeitadas).

## A ideia

Legislação fiscal grande redistribui valor entre setores: corte de imposto corporativo beneficia firmas de alta carga tributária e domésticas, penaliza internacionais (repatriação); o déficit implícito mexe em Treasuries. O Polymarket precifica "o pacote passa até X?" em tempo real; a bolsa digere devagar — e a âncora documenta exatamente isso: os itens *complexos* da reforma de 2017 foram precificados **lentamente**, que é a defasagem que o template poly-defasado mede.

**Não existe instrumento tradicional precificando "probabilidade de aprovação"** → benchmark = **próprio poly defasado**, template da 2.4: `divergência = p_t − p_{t−k}`.

**Âncoras acadêmicas (papel = sanity check a posteriori, nunca invertem o β):**
- **Wagner, Zeckhauser & Ziegler (2018), "Company stock price reactions to the 2016 election shock: Trump, taxes, and trade" (*Journal of Financial Economics*) + "Unequal Rewards to Firms" (*AEA P&P* 2018)** — cross-section do canal tributário (alta carga/domésticas ganham; internacionais perdem) e evidência de precificação lenta nos itens complexos. Mapa de sinais esperados do β no evento tributário.
- **Teto da dívida:** episódio de 2011 (downgrade S&P) com queda de bolsa, salto de vol e spreads persistentes por meses; estudo do standoff 2023/2025 (*Journal of Applied Economics*, 2025). ⚠️ **Paradoxo documentado:** flight-to-quality *para dentro* dos próprios Treasuries (TLT sobe apesar de ser o ativo "em risco", exceto bills curtos) — o sinal do TLT é empírico; **o sanity check não exige sinal a priori do TLT neste evento** (o β manda; registrar o que sair).

## Eventos e mercados (decisão do Felipe, sessão 2026-07-10)

- **Evento primário do v1: legislação tributária** — mercados de aprovação do pacote fiscal (ex.: família OBBB 2025, "passa até X?"). Cross-section mais limpo (âncora WZZ) e volume alto na janela.
- **Robustness check: teto da dívida / X-date** (episódios 2023 e 2025) — efeito mais violento, mas raro e com o paradoxo do TLT.
- **Fora como evento: shutdown** — sem efeito documentado em equities (ver rejeitadas).
- **Um evento por vez:** um mercado designado por período (regra herdada da 2.4/C/E); eventos episódicos — a cascata liga/desliga na janela.

## Como funciona (herda a maquinaria da 2.4/E — diferenças anotadas)

0. **Ativação e cascata (zero parâmetros):** existe mercado designado ativo → view ativa; sem mercado → desativada, Ω → ∞, BL no prior. ⚠️ **Desligamento no último dia antes do primeiro tick de resolução** (votação final resolve o mercado — o salto não vira alfa).
1. **Sinal do poly:** p(aprovação) do binário designado, série diária, **midpoint bid/ask**, em fração [0,1].
2. **Pré-processamento (módulo da decisão 9):** (a) normalização; (b) favorite-longshot (registrar o nível de p observado na validação — mercados legislativos costumam viver em faixas medianas); (c) midpoint + reportar dias sem trade.
3. **β por ativo:** regressão própria — retorno diário dos 9 ETFs contra Δp(evento), com as três obrigações da 2.4 (janela expandida sem lookahead; teste de defasagem obrigatório; β de absorção plena). β **por mercado/evento** (aprovação de corte de imposto é "boa" para uns setores; risco de default é outro bicho — a regressão resolve por evento, sem regra manual). WZZ entra só como sanity check no evento tributário; no teto, sem sinal a priori para o TLT.
4. **Benchmark e divergência:** poly defasado — `divergência = p_t − p_{t−k}`. Herda: acoplamento k ↔ rebalance; **k ≈ 0 → view nunca liga** (pendência compartilhada).
5. **P (cross-sectional padrão):** `P[i] ∝ (β_i − β_SPY)`, **Σ|P| = 2**, `P[SPY] = 0` exato.
6. **Q da linha:** `Q = (Σ_i P[i]·β_i) × (p_t − p_{t−k})` — **Q em %, acumulado em k dias** (herda a pendência de horizonte).
7. **Sanity check de sinal (⚠️ teste obrigatório):** números inventados. p(pacote tributário passa) sobe de 0,40 para 0,60 em k dias → divergência +0,20. β em %/unidade: `β_XLF = +2,0` (doméstico/alta carga), `β_SPY = +0,5`, `β_XLK = −1,0` (internacional/repatriação) → P: XLF long (+1,5), XLK short (−1,5) → `Σ P·β > 0` → `Q > 0`: **long domésticos de alta carga, short internacionais** com aprovação ficando mais provável — bate com WZZ.

## Decisões fechadas nesta view (sessão 2026-07-10)

- **Q1-A — legislação tributária primário; teto da dívida robustness.**
- **Q2 — nasce como reserva:** poucos episódios → β mais frágil do lote; a marcação é honesta e barata (a reunião pode promovê-la).

## Decisões rejeitadas (referência)

- **Shutdown como evento:** sem efeito documentado em equities (S&P flat/positivo em ~77% dos episódios; ~2 bps em Treasuries) — foi a reorientação da pesquisa; reabrir só se surgir literatura nova.
- **Teto da dívida como primário (Q1-B):** episódios mais raros e âncora de sinal fraca (paradoxo do TLT); fica como robustness.
- **Herdadas da 2.4** (mesma maquinaria): último trade como preço; interruptor por liquidez; janela "N dias antes"; β da literatura como valores; prob implícita por inversão.
- **Índice agregado de eventos fiscais:** defeito da 3.1 original; um designado por vez.

## Pendências desta view

- ⚠️ **Reunião — entra ou não** (como reserva; junto com as demais candidatas).
- **Paulo:** mercados de aprovação fiscal (OBBB 2025) e teto/X-date (2023, 2025) no CLOB — cobertura, volume, critério de resolução, **bid/ask histórico**.
- **Herdadas transversais (2.4/3.1/C/E):** k ≈ 0; horizonte do Q vs Σ/π; limiar de volume p/ estimabilidade (parâmetro humano); frequência de rebalance ↔ k; medir ΣP empiricamente (decisão conjunta).
- **Registro do TLT no evento de teto:** reportar o sinal que a regressão der (sem expectativa a priori) — insumo para a reunião avaliar se o robustness fica.
