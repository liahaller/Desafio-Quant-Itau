# Tática — Drift pós-FOMC (momentum monetário; dois livros: ações e renda fixa)

**Status:** 🟡 candidata da **camada tática reformulada** (contrato definido em `tatica_1.3_premio_anuncios.md`: paralela ao BL, granularidade ~12h, gatilho de calendário, sinal lento) — desenho fechado em sessão com Felipe (2026-07-10), **condicionado à reunião** (reabrir a camada mexe na decisão 10). Fusão das candidatas T1 (ações) e T3 (renda fixa) da pesquisa — decisão Q1-A da sessão.

**Origem:** pesquisa de 2026-07-10 (`Informações_uteis/Pesquisa_embasamento_novas_ideias.md`) — não é do banco de ideias original. Âncoras:
- **Neuhierl & Weber, "Monetary Momentum" (NBER WP 24748):** ações continuam andando na direção da surpresa de política monetária por ~15 dias após o FOMC (diferença acumulada dovish−hawkish > +4,5%); o drift **não é explicado por fatores padrão nem por time-series momentum** (⚠️ importante: não é a tática 1.2 adiada disfarçada — objeto distinto).
- **Brooks, Katz & Lustig, "Post-FOMC Announcement Drift in U.S. Bond Markets" (NBER WP 25127):** +10 bps de surpresa → +1,7 bps no yield de 10a no dia, **+14 bps acumulados em ~50 dias**; mecanismo documentado (fluxo lento de fundos mútuos + demanda inelástica).

## A ideia

No dia do FOMC a surpresa vira pública — mas o mercado não termina de reagir no dia: ações e Treasuries continuam andando na mesma direção por semanas. A tática entra **depois** do anúncio, na direção da surpresa realizada, e carrega por uma janela fixa. Gatilho = calendário FOMC (conhecido); sinal = número publicado no próprio dia; nada aqui exige intradiário.

**Por que não é view do BL:** mesma lógica da 1.3 — afirma *quando e para que lado estar exposto* depois de um evento, não um retorno esperado no horizonte do rebalance; e a view do evento FOMC **já existe** (2.3, que opera a divergência *antes* da reunião e desliga na resolução). O drift pega exatamente o pedaço que a 2.3 solta: o *depois*.

## Como funciona (decidido)

1. **Formato: sleeve overlay com dois livros, por cima do BL intocado** (mesmo formato da 1.3):
   - **Livro de ações:** SPY vs caixa, janela D close → D+15 dias úteis (âncora NW).
   - **Livro de renda fixa:** TLT vs caixa, janela D close → D+50 dias úteis, **truncada no dia anterior ao FOMC seguinte** (~42 dias úteis típicos — evita carregar o drift de uma reunião para dentro da próxima).
2. **Sinal = surpresa realizada do anúncio**, em bps: `surpresa = Δtaxa_decidida − E[Δtaxa na véspera]`. Fonte da expectativa da véspera: **futuro ZQ (D−1 close)** — leitura direta da âncora (é a surpresa à la Kuttner, o mesmo objeto contra o qual a 2.3 já estima os β; dado já contratado). ⚠️ Sub-questão registrada para reunião: variante com `E_poly(D−1)` no lugar do ZQ (mais "tema do projeto", mas sem âncora própria — NW/BKL medem contra o mercado de futuros).
3. **Direção: simétrica** — surpresa dovish (corte além do esperado) → long SPY e long TLT; hawkish → short SPY e short TLT. É o que as âncoras documentam (os dois lados).
4. **Tamanho: binário por sinal (v1):** `posição = ±orçamento_máx_drift × sinal(surpresa)`, por livro. Um parâmetro humano por livro (ou um comum — reunião). **Upgrade registrado** (mesmo padrão normativo→regressão da 1.3): tamanho proporcional a |surpresa| com escala estimada, quando a amostra permitir (~8 FOMCs/ano → ruidoso hoje). ⚠️ Ressalva: por construção da âncora o sinal é o classificador (sign-based); micro-surpresas (ex.: 1 bp) tomam posição cheia — registrado como sub-questão de calibração para a reunião (um threshold seria parâmetro novo a defender).
5. **Eventos: só FOMC no v1.** Extensão a CPI rejeitada por ora — não foi encontrada âncora própria de drift pós-CPI (a de bonds é específica de FOMC).
6. **Cascata de degradação:** sem ZQ utilizável na véspera ou sem decisão publicada → aquele evento **não opera** (camada dormente; não é falha). A camada nunca bloqueia o BL.

## Relação com os módulos vizinhos (registro, sem decisão)

- **View 2.3:** complementaridade temporal exata — a 2.3 opera a divergência esperada *antes* da reunião e desliga na resolução; o drift liga *no close do dia do anúncio* com a surpresa realizada. Sem sobreposição de janela.
- **Tática 1.3:** janelas se encostam sem colidir (1.3 fecha no close de D; drift abre no close de D). Sinais distintos (1.3 lê *incerteza* na véspera; drift lê *surpresa realizada*).
- **Ω (Lia):** três módulos leem o mesmo calendário FOMC (2.3 antes, 1.3 no dia, drift depois) — documentar para o Ω não neutralizar nenhum por construção (soma-se à nota já pendente da 1.3).

## Decisões rejeitadas (referência)

- **Duas táticas separadas (T1 e T3):** mesmo gatilho e mesma surpresa — duplicaria estrutura e orçamento para um evento só (Q1).
- **Operar só o lado long:** assimetria sem âncora — a literatura documenta os dois lados (Q2).
- **Tamanho proporcional a |surpresa| já no v1:** cria o parâmetro "escala" com ~8 obs/ano; fica como upgrade (Q3).
- **TIP no livro de renda fixa:** BKL é sobre Treasuries nominais; TIP sem âncora própria aqui.
- **Extensão a CPI no v1:** sem âncora de drift pós-CPI encontrada na pesquisa.
- **Virar view do BL:** horizonte condicional ao evento, irreconciliável com o rebalance; a view do FOMC é a 2.3.

## Pendências

- ⚠️ **Reunião:** (a) reabrir a camada tática reformulada (decisão 10; junto com a 1.3); (b) `orçamento_máx_drift` (por livro ou comum); (c) janelas finais (defaults da literatura: 15d ações / 50d bonds truncado); (d) sub-questão da fonte da expectativa (ZQ vs E_poly); (e) micro-surpresas (posição cheia por sinal vs threshold).
- **Backtest (Paulo):** ⚠️ requisito mais pesado que o da 1.3 — as janelas de drift cobrem boa parte do ano (8 reuniões × ~42d úteis no livro de TLT ≈ cobertura quase contínua): na prática o motor precisa de **marcação diária contínua** das posições da camada tática, não só ~20 dias/ano. Dados: nenhum novo (ZQ e calendário FOMC já eram pendências da 2.3/1.3).
- **Lia:** nota de interação Ω ↔ camada (três módulos no calendário FOMC).
