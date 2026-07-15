# Guia rápido de ideias (pessoal do Felipe)

> Arquivo pessoal de organização — **Claude não lê nem mantém este arquivo** (pasta claude_ignore). Fonte da verdade continua sendo `Decisoes_pendentes.md` + `Informações_uteis/views/` e `/táticas/`.

## Views (BL)

| View | O que é (1 linha) | Estado |
|------|-------------------|--------|
| **2.2 Inflação** | Poly de CPI vs breakeven TIPS → par TIP−TLT (Q via duration, sem regressão) | 🟢 Ativa (desenho fechado; falta implementar) |
| **2.3 Fed** | Surpresa da próxima reunião: E_poly vs futuro ZQ, em bps → tilt duration (tech vs defensivos) | 🟢 Ativa (desenho fechado; falta implementar) |
| **2.4 Eleitoral** | Poly presidencial defasado (p_t − p_{t−k}) → tilt cross-section pelos β | 🟢 Ativa condicional (bid/ask histórico no CLOB — Paulo) |
| **3.1 Recessão** | Poly de recessão vs prob da curva de juros (probit 10a−3m) → cíclicos vs defensivos | 🟢 Ativa condicional (mercado no CLOB — Paulo; horizonte — reunião) |
| **B Trajetória do Fed** | Taxa de fim de ano: poly vs ZQ de dezembro; reusa β/P da 2.3 | 🟡 Candidata (reunião decide; dupla exposição com 2.3 é a questão) |
| **C Geopolítica→energia** | Mercados de guerra/cessar-fogo (Irã primário) defasados → XLE e cross-section | 🟡 Candidata (desenho fechado; reunião decide entrada) |
| **E Tarifas** | Poly de tarifas EUA×China defasado → cross-section (tech sofre, defensivos/TLT ganham) | 🟡 Candidata (desenho fechado 10/jul; reunião decide) |
| **G Fiscal** | Poly de aprovação de pacote tributário (OBBB) defasado; teto da dívida como robustness | 🟠 Reserva (desenho fechado 10/jul; só sobe se cair outra) |
| **F Petróleo** | E_poly[WTI] vs curva futura → XLE | ❌ Descartada (dupla exposição com a C; e mercados do poly são one-touch) |
| **H Chair do Fed** | Poly de nomeação do chair defasado → duration | ❌ Descartada (tripla exposição Fed com 2.3+B; evento único) |

## Táticas (camada reformulada — paralela ao BL, gatilho de calendário)

| Tática | O que é (1 linha) | Estado |
|--------|-------------------|--------|
| **1.3 Prêmio de anúncios** | Long SPY em todo dia de FOMC/CPI, tamanho = entropia da PMF do poly na véspera | 🟡 Candidata-fundadora (reunião precisa reabrir a camada — decisão 10) |
| **Drift pós-FOMC** | Depois do anúncio, tilt na direção da surpresa realizada: SPY ~15d + TLT ~50d | 🟡 Candidata (desenho fechado 10/jul; reunião) |
| **Gap de fim de semana** | Δp do poly no fim de semana × β das views → tilt na segunda, desmonta no fechamento | 🟡 Candidata (desenho fechado 10/jul; reunião) |
| **T4 Ciclo FOMC** | Prêmio de ações nas semanas pares do ciclo FOMC (calendário puro) | ❌ Descartada (sem conexão com o poly; evidência enfraquecendo) |

## Camada tática antiga (congelada — decisão 10)

| Ideia | O que era | Estado |
|-------|-----------|--------|
| **1.1 PEAD** | Drift pós-resolução pelo tamanho da surpresa | 🧊 Congelada (volta se a tática antiga for retomada) |
| **1.2 Momentum** | Seguir a tendência/velocidade da probabilidade | 🧊 Congelada (reclassificada tática em 10/jul) |
| **3.2 Event-driven** | Agir antes da resolução no salto de probabilidade | 🧊 Congelada |
| **Velocidade de ajuste** | Operar durante o movimento (derivada) | 🧊 Congelada |

## Outros (não são views nem táticas)

- **Ω reativo (Lia):** confiança móvel das views — decisão 6 aberta.
- **Módulo PMF compartilhado (decisão 9):** normalização + favorite-longshot + midpoint — aberto.
- **3.4 detector de insider / 3.5 anti-narrativa:** reserva especulativa / filtro do Ω (banco antigo).

*Snapshot de 2026-07-10 — estados mudam na reunião (decisão 11 foi removida; entrada das candidatas é pauta de reunião).*
