# Pesquisa — embasamento teórico das novas candidatas (views E–H, táticas T1–T4)

**Data:** 2026-07-10 · **Sessão:** Felipe + Claude (levantamento web).
**Status:** material de pesquisa, **nada aqui é decisão**. Cada candidata ainda passa pela avaliação em sessão (bateria de perguntas, padrão 2.2–3.1) e a entrada na carteira é decisão de reunião. Papers seguem a regra do projeto: âncora é *sanity check a posteriori* — o β de cada view/tática vem de regressão própria, a literatura nunca inverte o β.

**Veredito geral da pesquisa:** nenhuma das 6 candidatas originais morreu. Uma foi **reorientada** (G: de "fiscal genérico/shutdown" para legislação tributária + teto da dívida — shutdown puro não mexe em bolsa), uma foi **reancorada** (T2: âncora principal passa a ser a evidência direta de prediction market → futuros de equity), e a pesquisa revelou **2 candidatas novas** (view H — nomeação do Fed; tática T4 — ciclo FOMC) e **4 achados transversais** que interessam a módulos já existentes (decisão 9, Ω da Lia, template poly-defasado).

---

## Views candidatas

### View E — Tarifas / política comercial (template poly-defasado)

**Tese:** o poly precifica eventos tarifários em tempo real; a bolsa digere em dias; o movimento recente de p(tarifa) ainda não absorvido vira tilt setorial cross-section (`Q = (Σ P·β) × (p_t − p_{t−k})`, maquinaria da 2.4).

**Âncoras encontradas:**
- **Amiti, Gomez, Kong & Weinstein — "Trade Protection, Stock-Market Returns, and Welfare" (working paper; NBER/RBA 2024).** Event-study dos anúncios tarifários da guerra comercial EUA-China: 11 eventos-chave somam **−11,5%** no mercado americano; firmas expostas à China caem mais **e** têm piora real subsequente (lucro, emprego, produtividade); anúncios derrubam yields de Treasuries (flight to safety → o TLT também é ativo da view, não só os setores). É exatamente o cross-section heterogêneo que o nosso β por regressão deve capturar. [PDF](https://www.rba.gov.au/publications/workshops/research/2024/pdf/rba-workshop-2024-amiti-gomez-kong-weinstein.pdf) · [paper irmão sobre investimento](https://deweinst.github.io/weinstein_website/Trade_War_Investment_Paper.pdf)
- **Caldara, Iacoviello, Molligo, Prestipino & Raffo (2020), "The economic effects of trade policy uncertainty", *Journal of Monetary Economics* 109, 38–59.** A *incerteza* tarifária (índice TPU) já reduz investimento e atividade antes de qualquer tarifa sair do papel — legitima usar a **probabilidade** (não o ato) como sinal, mesmo papel que o GPR de Caldara-Iacoviello faz na view C. [PDF](https://www.matteoiacoviello.com/research_files/JME2020.pdf) · [índice TPU](https://www.matteoiacoviello.com/tpu.htm)
- **Literatura 2025 já existe sobre os episódios da janela do backtest:** ex. "Tariffs announcement as a global stress test" (*Finance Research Letters*, 2025) sobre os anúncios recíprocos ("Liberation Day"). Útil como benchmark dos sinais estimados. [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S1544612325013376)

**Implicação de desenho:** incluir TLT no cross-section (flight to safety documentado); episódios concentrados em 2025 → janela curta e saltos correlacionados para o β (mesma fragilidade já aceita na 2.4, documentar).

**Pergunta aberta específica:** havia *muitos* mercados de tarifa simultâneos no poly (China, recíprocas, acordo) — o critério de "mercado designado por período" é menos óbvio que na eleição; decidir na avaliação.

**Veredito: sustentada e reforçada.**

---

### View F — Petróleo: nível do poly vs curva futura (Família A com benchmark externo)

**Tese:** buckets de preço do WTI no poly dão uma esperança `E_poly[WTI]`; o futuro de WTI (CL, yfinance) dá o benchmark tradicional do mesmo objeto; a divergência entre os dois, multiplicada pelos β setoriais a petróleo, vira Q. Única candidata **Família A genuína** (dois termômetros externos, como 2.2/2.3).

**Âncoras encontradas:**
- **Kilian & Park (2009), "The impact of oil price shocks on the U.S. stock market", *International Economic Review* 50, 1267–1287.** Confirmada: resposta setorial heterogênea; choques de demanda vs oferta têm efeitos opostos; oferta/demanda do petróleo explicam 22% da variação de longo prazo dos retornos. **Ressalva relevante:** a resposta depende da *origem* do choque — o β médio estimado por regressão mistura regimes (documentar como limitação, igual fizemos na C). [Wiley](https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1468-2354.2009.00568.x)
- **Leigh, Wolfers & Zitzewitz (2003), "What do financial markets think of war in Iraq?" (NBER WP 9587) e Wolfers & Zitzewitz (2009), *Economica*.** O "Saddam Security" (prediction market) movia o preço spot do petróleo: +10 p.p. de probabilidade de guerra ≈ +$1/barril. É a ponte quantitativa probabilidade→petróleo mais antiga e limpa da literatura — serve à F e à C. [NBER](https://www.nber.org/papers/w9587) · [Economica](https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1468-0335.2008.00750.x)
- **Alquist & Kilian (2010), "What do we learn from the price of crude oil futures?", *Journal of Applied Econometrics*.** ⚠️ O futuro de petróleo **não é um previsor não-viesado** do spot: embute prêmio de risco variável no tempo e historicamente não bate um no-change forecast. A divergência `E_poly − F_WTI` contém (expectativa do poly − expectativa do mercado) **+ prêmio de risco**. Mesma natureza do term premium que já aceitamos no ZQ da 2.3 — aceitável, mas tem que estar escrito. Contraponto recente: **Ellwanger & Snudden (2023, *The Energy Journal*)** reabilitam os futuros como previsores mensais. [ECB WP sobre risk-adjusted forecasts](https://www.ecb.europa.eu/pub/pdf/scpwps/ecbwp999.pdf) · [Ellwanger-Snudden](https://journals.sagepub.com/doi/10.5547/01956574.44.4.rell)

**⚠️ Gotcha descoberto na pesquisa (muda o desenho):** os mercados mensais de WTI do Polymarket ("What price will WTI hit in April 2026?") resolvem por **one-touch**: "Yes" se *qualquer candle de 1 minuto tocar* o nível durante o período — ou seja, precificam `P(máximo do período ≥ X)`, **não** uma PMF do preço terminal. A média da PMF (receita da 2.2) **não se aplica diretamente**: a distribuição do máximo enviesa `E_poly` para cima. Caminhos possíveis (decisão de avaliação/reunião): (a) localizar mercados de *fechamento/settle* no CLOB, se existirem; (b) usar as probabilidades touch como CDF do máximo e derivar um sinal alternativo, com viés documentado; (c) restringir a view a mercados binários direcionais de fim de ano ("Oil above $X on Dec 31"), se houver histórico. Checagem do Paulo: quais estruturas existem no CLOB e desde quando. [Polymarket oil](https://polymarket.com/predictions/oil) · [exemplo de mercado mensal](https://polymarket.com/event/what-price-will-wti-hit-in-april-2026)

**Implicação de desenho:** β estimável com amostra longa (regressão dos ETFs contra retornos do petróleo — não precisa de event-study), o que a torna a candidata com o β mais bem-estimado do lote; dupla exposição com a C (mesmo canal XLE) — discutir como 2.3↔B.

**Veredito: sustentada, com gotcha de desenho (one-touch) que precisa ser resolvido antes de fechar.**

> **❌ Rejeitada em sessão (2026-07-10, decisão do Felipe):** dupla exposição com a view C — as duas empurram XLE pelo mesmo canal de petróleo. A C (já desenhada) fica; a F não entra. Registro mantido aqui como referência.

---

### View G — Legislação fiscal: tributária + teto da dívida (reorientada pela pesquisa)

**Tese original:** "pacote fiscal passa até X?" → template poly-defasado → cross-section setorial + TLT.
**O que a pesquisa mudou:** shutdown **não** sustenta uma view de equities — S&P flat/positivo em 10 dos 13 shutdowns; efeito médio em Treasuries de ~2 bps (ruído). O conteúdo com efeito real está em (i) **legislação tributária** e (ii) **teto da dívida/default técnico**. A view reorientada: mercados do poly sobre aprovação de legislação fiscal relevante (ex.: OBBB 2025) e sobre teto da dívida/X-date, um designado por período.

**Âncoras encontradas:**
- **Wagner, Zeckhauser & Ziegler (2018), "Company stock price reactions to the 2016 election shock: Trump, taxes, and trade", *Journal of Financial Economics* + "Unequal Rewards to Firms" (*AEA P&P* 2018).** Cross-section exato do canal tributário: firmas de alta carga tributária e domésticas ganham com corte de imposto; internacionais perdem (repatriação); e a *velocidade* de precificação varia com a complexidade do item — ou seja, existe defasagem a explorar, que é justamente o que o template poly-defasado mede. [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2909835) · [JFE](https://www.sciencedirect.com/science/article/abs/pii/S0304405X18301739) · [AEA P&P](https://www.aeaweb.org/articles?id=10.1257%2Fpandp.20181091)
- **Teto da dívida:** 2011 (downgrade S&P) teve queda de bolsa, salto de vol e spreads de crédito **persistentes por meses** — diferente de shutdown; estudo recente sobre o standoff de 2023/2025: "The U.S. debt ceiling standoff and financial markets' reactions" (*Journal of Applied Economics*, 2025). Paradoxo documentado: flight-to-quality **para dentro** dos próprios Treasuries (TLT sobe com yields caindo, exceto bills curtos) — o sinal do TLT na view não é óbvio e o β por regressão resolve. [Tandfonline](https://www.tandfonline.com/doi/full/10.1080/15140326.2025.2609025) · [Treasury sobre 2011](https://home.treasury.gov/system/files/276/POTENTIAL-MACROECONOMIC-IMPACT-OF-DEBT-CEILING-BRINKMANSHIP.pdf)
- **Evidência negativa (motivo da reorientação):** "Do the Markets Care about the 2025 U.S. Government Shutdown?" e séries históricas de shutdowns (S&P positivo/flat em ~77% dos casos). Shutdown só entra, se entrar, como robustness — não como evento primário. [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S1059056026006416)

**Implicação de desenho:** poucos episódios na janela (OBBB, teto 2023/2025) → β frágil, mesma classe de fragilidade da 2.4; candidata natural a "reserva" se E e F forem aprovadas.

**Veredito: reorientada (tributária + teto da dívida; shutdown descartado como evento primário).**

---

### View H — Nomeação do presidente do Fed (nova candidata, descoberta na pesquisa)

**Tese:** o poly negociou com volume alto "quem será o próximo chair do Fed" (2025–26); a literatura mostra que anúncios de nomeação de chair mexem de forma **desproporcional** em juros e ações. Binário designado por candidato nomeável (ex.: p(Warsh)); β por regressão própria dos ETFs contra Δp — o sinal "hawkish/dovish" sai da regressão, sem dove-score manual (mesmo truque que resolve ataque/cessar-fogo na C). Template poly-defasado (não há instrumento externo precificando a nomeação).

**Âncoras encontradas:**
- **Kuttner & Posen (2010), "Do markets care who chairs the central bank?", *Journal of Money, Credit and Banking* (NBER WP 13101).** Event-study de nomeações em 15 países: câmbio e yields reagem significativamente a nomeações inesperadas, e **nomeações de chair do Fed se destacam com efeitos anormalmente pronunciados**. É âncora direta e específica. [NBER](https://www.nber.org/papers/w13101)
- Cobertura de mercado 2025–26 confirma o canal operando em tempo real (precificação de Warsh/candidatos em bonds). [CNBC](https://www.cnbc.com/2026/05/02/kevin-warsh-federal-reserve-interest-rates-bonds-fixed-income.html)

**Riscos/pendências:** terceira view no tema "Fed" (2.3 + B + H = tripla exposição — a discussão de dupla exposição da B fica mais aguda); evento raro (uma nomeação por ciclo) → β estimado num episódio só; mercado multi-candidato exige regra de designação (um binário por vez). Condição padrão: histórico/bid-ask no CLOB (Paulo).

**Veredito: candidata nova, entra na fila de avaliação atrás de E/F/G.**

> **❌ Descartada em sessão (2026-07-10, decisão do Felipe):** tripla exposição ao tema Fed (2.3 + B + H) — mesmo critério que derrubou a F — agravada pelo evento único na janela (β estimado num episódio só). Registro mantido aqui como referência.

---

## Táticas candidatas (camada reformulada: paralela ao BL, ~12h, gatilho de calendário/sinal lento)

### T1 — Momentum monetário pós-FOMC

**Tese:** tilt SPY (ou duration) por N dias após cada FOMC, na direção da surpresa — que a view 2.3 **já calcula** (E_poly − ZQ, realizada no dia). Custo de dado zero.

**Âncora:** **Neuhierl & Weber, "Monetary Momentum" (NBER WP 24748).** Drift de ~25 dias antes e **15 dias depois** do FOMC na direção da surpresa; diferença acumulada expansionista−contracionista chega a **+4,5%** 15 dias após a reunião; o drift não é explicado por fatores padrão nem por time-series momentum; estratégia simples multiplica o Sharpe de buy-and-hold por ~4. A parte *negociável* para nós é o pós-anúncio (a surpresa só é conhecida no dia). [NBER](https://www.nber.org/papers/w24748) · [resumo NBER Digest](https://nber.org/digest/sep18/w24748.shtml)

**Encaixe:** gatilho = calendário FOMC (dado já pendente da 2.3); janela D→D+N dias (N da literatura ≈ 15, valor final = decisão humana); marca posição diária como a 1.3 (mesmo requisito de backtest já pedido ao Paulo).

**Veredito: sustentada — âncora forte.**

### T2 — Gap de fim de semana (reancorada)

**Tese:** o poly opera 24/7; a bolsa fecha de sexta a segunda. O Δp acumulado no fim de semana nos mercados designados, vezes os β já estimados pelas views, vira um tilt na abertura de segunda (desmontado em 1–2 dias). É a defasagem k da 2.4 aplicada à janela em que a bolsa não pode reagir.

**Âncoras (novas, da pesquisa):**
- **Snowberg, Wolfers & Zitzewitz (2007), "Partisan impacts on the economy: evidence from prediction markets and close elections", *QJE*.** Evidência direta do mecanismo: na noite da eleição de 2004 (bolsa fechada), os movimentos do prediction market moviam os **futuros** de equity em frequência intradiária. Prediction market se move fora do pregão → equities reprecificam depois. É a âncora principal. [PDF](https://eriksnowberg.com/papers/Snowberg-Wolfers-Zitzewitz%20-%20Partisan%20Impacts.pdf)
- **Lou, Polk & Skouras (2019), "A tug of war: overnight versus intraday expected returns", *JFE*.** Retornos overnight e intradiários têm estrutura sistematicamente diferente — suporte de que "o que acontece com o mercado fechado" é um objeto real de estudo. Âncora secundária. [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0304405X19300650)
- ⚠️ **Ressalva da literatura nova do Polymarket:** binários do poly exibem **mean-reversion** de curto prazo (estudo QuantPedia sobre contratos binários do Polymarket) — parte do Δp de fim de semana pode reverter em vez de ser absorvida pela bolsa. Implicação de desenho: filtrar o sinal (magnitude mínima e/ou confirmação por volume) — parâmetros humanos. [QuantPedia](https://quantpedia.com/exploiting-mean-reversion-in-decentralized-prediction-markets-evidence-from-polymarket-binary-contracts/)

**Veredito: sustentada com reancoragem (SWZ 2007 como âncora principal) e ressalva de mean-reversion incorporada.**

### T3 — Drift pós-anúncio em renda fixa

**Tese:** tilt TLT/TIP por dias após FOMC na direção da surpresa (dovish → long TLT; hawkish → short/evita), usando a surpresa da 2.3.

**Âncora:** **Brooks, Katz & Lustig, "Post-FOMC announcement drift in U.S. bond markets" (NBER WP 25127).** Yields de 10 anos continuam se movendo por ~50 dias: +10 bps de surpresa → +1,7 bps no dia vs **+14 bps acumulados em 50 dias**; mecanismo documentado (fluxo lento de fundos mútuos + demanda inelástica). Explica time-series momentum em bonds. [NBER](https://www.nber.org/papers/w25127) · [Stanford GSB](https://www.gsb.stanford.edu/faculty-research/working-papers/post-fomc-announcement-drift-us-bond-markets)

**Encaixe/observação:** irmã da T1 (mesmo gatilho, livro diferente — ações vs renda fixa; horizontes diferentes: 15 vs 50 dias). Avaliar juntas e decidir se viram **uma** camada de drift pós-FOMC com dois livros, ou duas, ou uma só. Extensão a CPI: sem âncora própria encontrada — fica como sub-questão.

**Veredito: sustentada — âncora forte.**

### T4 — Ciclo FOMC / semanas pares (nova candidata, descoberta na pesquisa)

**Tese:** desde 1994, o prêmio de risco de ações é ganho **inteiramente nas semanas pares** do ciclo FOMC (semanas 0, 2, 4, 6 contadas da última reunião). Overlay de calendário puro: exposição extra a SPY nas semanas pares (ou redução nas ímpares).

**Âncora:** **Cieslak, Morse & Vissing-Jorgensen (2019), "Stock returns over the FOMC cycle", *Journal of Finance* 74(5), 2201–2248.** Retornos médios positivos nas semanas pares, ~zero/negativos nas ímpares; ligação causal com o Fed (mudanças intermeeting, fed funds futures, atas do Board); canal = comunicação informal. [Wiley](https://onlinelibrary.wiley.com/doi/abs/10.1111/jofi.12818) · [PDF](https://faculty.haas.berkeley.edu/morse/research/papers/cycle_paper_cieslak_morse_vissingjorgensen.pdf)

**⚠️ Fraqueza honesta:** é a única candidata **sem nenhuma conexão com o Polymarket** — calendário puro. Encaixa no contrato da camada (gatilho de calendário, granularidade diária), mas pode ser considerada fora do tema do desafio. Decisão de reunião: entra como está, entra modulada pelo poly (ex.: entropia, como a 1.3 — mas seria enxerto sem âncora), ou fica de fora. Há também evidência de enfraquecimento pós-amostra (replicações recentes discutem se o padrão persiste — ver [Uppal, WP](https://aliuppal.me/files/Ali_Uppal_CB_Cycles.pdf)).

**Veredito: candidata nova com âncora de topo, mas com risco de "fora do tema" — reunião decide.**

> **❌ Descartada em sessão (2026-07-10, decisão do Felipe):** zero conexão com o Polymarket (fora do tema do desafio) e evidência pós-amostra enfraquecendo. Registro mantido aqui como referência.

---

## Achados transversais (interessam a módulos já existentes)

1. **Favorite-longshot atualizado para o Polymarket (→ decisão 9 / Camada 4):** a literatura nova (tick-level, Kalshi + Polymarket) encontra o viés com forma específica: em grande parte é um **"Yes bias"** (compradores pagam caro pelo lado afirmativo); no Polymarket, favoritos acima de ~55% ficam **subprecificados**; em horizontes longos os preços comprimem na direção de 50%. Isso refina a correção da decisão 9 (hoje descrita genericamente): a correção ideal depende do lado (Yes/No), do nível de p e do horizonte. [Gupta, SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6858200) · [Whelan, UCD WP 2025](https://www.ucd.ie/economics/t4media/WP2025_19.pdf) · [QuantPedia — systematic edges](https://quantpedia.com/systematic-edges-in-prediction-markets/)
2. **Price discovery no Polymarket é de minoria informada (→ Ω da Lia):** Gómez-Cram, Guo, Jensen & Kung (WP 2026, ~1,7M contas, 2023–25): ~**3% dos traders** respondem pela maior parte do price discovery. Implicação: volume *total* é proxy imperfeita de qualidade de sinal — volume pode subir com fluxo desinformado. Registrar como observação para o desenho do Ω (não muda nada automaticamente). [Coindesk sobre o paper](https://www.coindesk.com/markets/2026/04/26/only-3-of-traders-drive-prediction-markets-accuracy-not-the-crowd-study-finds) · [Ng, Peng, Tao & Zhou, SSRN — price discovery cross-plataforma](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5331995)
3. **Mean-reversion nos binários do poly (→ ressalva ao template poly-defasado: 2.4, C, E, G, H):** se o próprio poly reverte no curto prazo, parte do Δp que o template trata como "informação a ser absorvida pela bolsa" é ruído que desfaz. O teste de defasagem k já mitiga (só liga se a bolsa historicamente segue o poly), mas vale checar na estimação se Δp grandes revertem — item novo para a bateria de validação das views poly-defasadas. [QuantPedia](https://quantpedia.com/exploiting-mean-reversion-in-decentralized-prediction-markets-evidence-from-polymarket-binary-contracts/)
4. **Guarda-chuva metodológico do bridge inteiro:** Snowberg, Wolfers & Zitzewitz têm dois textos que justificam academicamente o nosso desenho geral — **"How prediction markets can save event studies"** (usar Δp como medida contínua do evento em event-studies, que é literalmente a nossa regressão de β) e **"Prediction markets for economic forecasting" (NBER WP 18222)**. Bons para o relatório final do desafio. [Event studies PDF](https://eriksnowberg.com/papers/Snowberg%20Wolfers%20Zitzewitz%20event%20studies.pdf) · [NBER 18222](https://www.nber.org/system/files/working_papers/w18222/w18222.pdf)
5. **Academia recente sobre o Polymarket na eleição de 2024** (anatomia do mercado, choques políticos e price discovery): úteis para o relatório e para validar escolhas da 2.4 (midpoint, liquidez). [arXiv 2603.03136](https://arxiv.org/html/2603.03136v2) · [arXiv 2603.03152](https://arxiv.org/html/2603.03152v2)

---

## Fila sugerida para a revisão (a decidir com o Felipe)

1. **F** (única Família A; tem o gotcha one-touch para resolver cedo — se não houver mercado utilizável, morre rápido e barato).
2. **E** (âncora mais forte do lote entre as poly-defasadas; muitos episódios em 2025).
3. **T1 + T3 juntas** (mesmo gatilho; decidir se fundem).
4. **G** (reorientada; candidata a reserva).
5. **T2** (depende de decisão sobre o filtro anti-mean-reversion).
6. **H e T4** (novas; H esbarra na tripla exposição Fed, T4 no tema).

**Condição comum a todas as views:** Paulo confirmar no CLOB cobertura histórica, volume e bid/ask dos mercados (tarifas, WTI — estrutura de resolução!, fiscal/teto, nomeação do Fed). T1/T3/T4 não precisam de dado novo do poly; T2 usa os mercados que as views já contratam.
