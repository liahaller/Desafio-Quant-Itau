# Notícia — o gate completo nos mercados nunca lidos por sleeve

> Gerado por `scripts/gate_noticia.py`. **Mede; não decide.** Nenhum corte cravado, mesma regra do `Gate_sleeves.md`.

- janela do backtest: **2025-02-10 a 2026-08-06** (374 pregões), δ e Σ os mesmos do v1 (D7/D8)
- **G1** = mediana |Δ do sinal em k pregões| ÷ 1 centavo. Num binário o sinal É a probabilidade, então o tick é o centavo
- **G2** = μ do `tatica_drift_anuncio.estimate_drift_mu` contra o sinal DECLARADO. **k é lookback**, não prazo de posição: a sleeve é reassinada todo dia (janela do event-study = 1)
- **G3** = correlação com o sinal que as quatro views vivas já leem

⚠️ **O G0 está na tabela de propósito.** Nos mercados de notícia ele é o critério mordaz, não a formalidade: dispersão e cobertura andam em direções opostas no dado entregue.

| mercado                        | lookback   |   G0 dias |   eventos no μ | G1 razão / tick   | G2 μ (bps/dia)              | G2 bate?   | G3 maior \|corr\|           |
|:-------------------------------|:-----------|----------:|---------------:|:------------------|:----------------------------|:-----------|:----------------------------|
| M4 recessão EUA 2025           | k = 1      |       253 |            193 | 0.7×              | SPY -4.44 ✅ · TLT -1.87 ❌ | ❌         | +0.09 (entropia FOMC (15b)) |
| M4 recessão EUA 2025           | k = 2      |       252 |            211 | 1.0×              | SPY -3.84 ✅ · TLT -2.03 ❌ | ❌         | -0.14 (entropia CPI (15b))  |
| M4 recessão EUA 2025           | k = 3      |       251 |            220 | 1.0×              | SPY -2.84 ✅ · TLT +0.12 ✅ | ✅         | -0.17 (entropia CPI (15b))  |
| M4 recessão EUA 2025           | k = 5      |       249 |            227 | 2.0×              | SPY -1.11 ✅ · TLT +2.70 ✅ | ✅         | -0.20 (entropia CPI (15b))  |
| M4 recessão EUA 2025           | k = 10     |       244 |            229 | 2.5×              | SPY -3.63 ✅ · TLT -1.53 ❌ | ❌         | -0.24 (entropia CPI (15b))  |
| M4 recessão EUA 2025           | k = 20     |       234 |            232 | 5.5×              | SPY -2.09 ✅ · TLT -2.13 ❌ | ❌         | -0.33 (entropia CPI (15b))  |
| M5 Trump 2024                  | k = 1      |       218 |            136 | 0.5×              | SPY -2.13 ❌ · TLT +0.12 ❌ | ❌         | —                           |
| M5 Trump 2024                  | k = 2      |       217 |            163 | 1.0×              | SPY -2.95 ❌ · TLT -0.34 ✅ | ❌         | —                           |
| M5 Trump 2024                  | k = 3      |       216 |            179 | 1.2×              | SPY -2.19 ❌ · TLT -0.20 ✅ | ❌         | —                           |
| M5 Trump 2024                  | k = 5      |       214 |            193 | 2.0×              | SPY -0.42 ❌ · TLT +0.82 ❌ | ❌         | —                           |
| M5 Trump 2024                  | k = 10     |       209 |            194 | 3.0×              | SPY -0.60 ❌ · TLT +0.94 ❌ | ❌         | —                           |
| M5 Trump 2024                  | k = 20     |       199 |            192 | 5.0×              | SPY +1.54 ✅ · TLT +0.09 ❌ | ❌         | —                           |
| M6 tarifas China               | k = 1      |         8 |              8 | 3.5×              | SPY +0.03 ❌ · TLT -0.29 ❌ | ❌         | +0.70 (entropia CPI (15b))  |
| M6 tarifas China               | k = 2      |         7 |              7 | 5.0×              | SPY +0.04 ❌ · TLT -0.11 ❌ | ❌         | -0.73 (entropia FOMC (15b)) |
| M6 tarifas China               | k = 3      |         6 |              6 | 12.8×             | SPY +0.05 ❌ · TLT -0.01 ❌ | ❌         | +0.83 (entropia CPI (15b))  |
| M6 tarifas China               | k = 5      |         4 |              4 | 44.0×             | SPY +0.00 ❌ · TLT +8.92 ✅ | ❌         | +0.82 (divergência da 2.3)  |
| M7 ação militar Irã (jun/2025) | k = 1      |        58 |             50 | 1.2×              | XLE +0.88 ✅ · SPY +0.14 ❌ | ❌         | -0.28 (entropia FOMC (15b)) |
| M7 ação militar Irã (jun/2025) | k = 2      |        57 |             52 | 2.5×              | XLE +0.74 ✅ · SPY +0.29 ❌ | ❌         | +0.42 (divergência da 2.2)  |
| M7 ação militar Irã (jun/2025) | k = 3      |        56 |             53 | 3.3×              | XLE -1.71 ❌ · SPY -1.17 ✅ | ❌         | +0.67 (divergência da 2.2)  |
| M7 ação militar Irã (jun/2025) | k = 5      |        54 |             54 | 4.8×              | XLE -0.75 ❌ · SPY -0.15 ✅ | ❌         | +0.73 (divergência da 2.2)  |
| M7 ação militar Irã (jun/2025) | k = 10     |        49 |             47 | 5.5×              | XLE -1.09 ❌ · SPY +0.22 ❌ | ❌         | +0.82 (divergência da 2.2)  |
| M7 ação militar Irã (jun/2025) | k = 20     |        39 |             39 | 9.0×              | XLE -0.58 ❌ · SPY -2.25 ✅ | ❌         | +0.79 (divergência da 2.2)  |
| M7 ataque ao Irã (fev/2026)    | k = 1      |        28 |             28 | 4.0×              | XLE -1.41 ❌ · SPY +3.09 ❌ | ❌         | -0.12 (divergência da 2.3)  |
| M7 ataque ao Irã (fev/2026)    | k = 2      |        27 |             27 | 6.0×              | XLE +0.11 ✅ · SPY +3.33 ❌ | ❌         | -0.12 (entropia FOMC (15b)) |
| M7 ataque ao Irã (fev/2026)    | k = 3      |        26 |             24 | 7.7×              | XLE -0.69 ❌ · SPY +1.17 ❌ | ❌         | -0.16 (entropia FOMC (15b)) |
| M7 ataque ao Irã (fev/2026)    | k = 5      |        24 |             23 | 10.5×             | XLE -1.96 ❌ · SPY +0.78 ❌ | ❌         | -0.27 (entropia FOMC (15b)) |
| M7 ataque ao Irã (fev/2026)    | k = 10     |        19 |             18 | 11.0×             | XLE -0.68 ❌ · SPY +0.39 ❌ | ❌         | -0.52 (entropia FOMC (15b)) |
| M7 ataque ao Irã (fev/2026)    | k = 20     |         9 |              9 | 26.0×             | XLE -2.41 ❌ · SPY -0.04 ✅ | ❌         | +0.87 (entropia FOMC (15b)) |
| M8 reconciliação fiscal        | k = 1      |         2 |              2 | 33.0×             | TLT -5.25 ✅ · SPY -0.01 ❌ | ❌         | —                           |
| M8 reconciliação fiscal        | k = 2      |         1 |              1 | 66.0×             | μ ausente                   | ❌         | —                           |
| M9 Câmara                      | k = 1      |       244 |             98 | 0.0×              | SPY +2.82 ❌ · TLT +2.95 ✅ | ❌         | -0.13 (divergência da 2.3)  |
| M9 Câmara                      | k = 2      |       243 |            126 | 0.5×              | SPY -0.03 ✅ · TLT +1.47 ✅ | ✅         | -0.21 (divergência da 2.3)  |
| M9 Câmara                      | k = 3      |       242 |            147 | 1.0×              | SPY +2.66 ❌ · TLT +0.70 ✅ | ❌         | -0.20 (divergência da 2.3)  |
| M9 Câmara                      | k = 5      |       238 |            164 | 1.0×              | SPY +3.58 ❌ · TLT +1.52 ✅ | ❌         | -0.27 (entropia CPI (15b))  |
| M9 Câmara                      | k = 10     |       233 |            194 | 1.0×              | SPY +1.43 ❌ · TLT +0.11 ✅ | ❌         | -0.36 (divergência da 2.3)  |
| M9 Câmara                      | k = 20     |       219 |            204 | 3.0×              | SPY -0.41 ✅ · TLT -1.12 ❌ | ❌         | -0.33 (divergência da 2.3)  |

## Premissa declarada ANTES de medir

Herdadas **por referência** do `gate_event_driven.py` — o mesmo dicionário, não uma cópia. A 3.2 e a notícia julgam a mesma tese em cada mercado; o que muda entre os dois artefatos é só o gatilho.

- **M4 recessão EUA 2025** — p(recessão) sobe → risco-off: bolsa cai e duração sobe
- **M5 Trump 2024** — "Trump trade": p(Trump) sobe → bolsa sobe e duração cai (premissa da view 2.4)
- **M6 tarifas China** — p(tarifa) sobe → guerra comercial: bolsa cai e duração sobe
- **M7 ação militar Irã (jun/2025)** — p(ação militar) sobe → petróleo sobe (XLE) e bolsa cai (premissa da view C)
- **M7 ataque ao Irã (fev/2026)** — idem, segundo episódio
- **M8 reconciliação fiscal** — p(aprovação) sobe → mais emissão: duração cai e bolsa sobe
- **M9 Câmara** — mecanismo partidário, espelho do M5. ⚠️ é exatamente o mecanismo que a 2.4 mediu como NÃO reproduzindo fora da amostra

## Leitura

**Cobertura × dispersão, mercado a mercado** (dias em k = 1 · melhor G1 da grade): **M8 reconciliação fiscal** 2 dias, 66.0× em k = 2 · **M6 tarifas China** 8 dias, 44.0× em k = 5 · **M7 ataque ao Irã (fev/2026)** 28 dias, 26.0× em k = 20 · **M7 ação militar Irã (jun/2025)** 58 dias, 9.0× em k = 20 · **M4 recessão EUA 2025** 253 dias, 5.5× em k = 20 · **M5 Trump 2024** 218 dias, 5.0× em k = 20 · **M9 Câmara** 244 dias, 3.0× em k = 20. O de maior dispersão é **M8 reconciliação fiscal**, com **2 pregões** de cobertura. Sleeve precisa das duas coisas ao mesmo tempo, e no dado entregue elas quase não coexistem.

**2 de 7 mercados passam no G2 em pelo menos um lookback:** **M4 recessão EUA 2025** (k = 3, k = 5) · **M9 Câmara** (k = 2). Passar no G2 **não é aprovação** — o gate mede, e o destino é decisão do dono.

**Quem passa G1 e G2 ao mesmo tempo** (o G1 acima de 1× e o μ na direção declarada): **M4 recessão EUA 2025** em k = 3 (G1 1.0×, 251 dias, G3 -0.17) · **M4 recessão EUA 2025** em k = 5 (G1 2.0×, 249 dias, G3 -0.20).

### As aprovações sobrevivem às duas metades da amostra?

A **D19c** derrubou a view 3.1 direcional partindo a amostra do mercado de recessão em duas: +0,97% (t +6,52) na 1ª metade, **−0,35% (t −2,27)** na 2ª. Como não há segundo mercado de recessão, partir a amostra é o único teste fora da amostra que existe. Mesmo teste, aplicado a cada aprovação:

- **M4 recessão EUA 2025**, k = 3 — 1ª metade: `SPY -1.77 ✅ · TLT -0.39 ❌` (❌, n = 112) · 2ª metade: `SPY -0.99 ✅ · TLT +0.94 ✅` (✅, n = 108). 🛑 **NÃO sobrevive** — o veredito da amostra inteira é a média de dois regimes, não um sinal.
- **M4 recessão EUA 2025**, k = 5 — 1ª metade: `SPY -0.66 ✅ · TLT +1.36 ✅` (✅, n = 116) · 2ª metade: `SPY -0.56 ✅ · TLT +2.06 ✅` (✅, n = 111). **Sobrevive nas duas metades.**

**1 de 2** aprovações sobrevivem ao corte da amostra: **M4 recessão EUA 2025** k = 5.

⚠️ **O que o projeto já mediu sobre esses mercados, em outra camada:**

- **M4 recessão EUA 2025** — a **view 3.1** leu este mercado, e a D19c mediu que o coeficiente **troca de sinal dentro da própria amostra** (SPY em h = 10: +0,97% t +6,52 na 1ª metade, **−0,35% t −2,27** na 2ª). Não há segundo mercado de recessão, então não existe teste fora da amostra — e agora se sabe que não existe nem dentro dela.

**O que trava esta candidata, e não é nenhum veredito acima:** o **pedido de dado**. Mercados de evento com fluxo de notícia têm dispersão de sobra e duram poucos pregões; o que dura um ano é pergunta permanente e não se mexe. O pedido ao Paulo é *mais mercados de evento com notícia*, não mais histórico dos mesmos — nenhum horizonte desta grade conserta um mercado de 9 pregões.

⚠️ **A D24 pega esta candidata em cheio** e continua 🔴: o portão de qualidade do poly vale para views e **não** para overlays. Mercado de notícia curto é exatamente o de PMF degenerada — uma sleeve aqui passaria livre pelo veto que mata a view equivalente.

**O que isto NÃO diz:** nada sobre P&L (G4 exige backtest, backtest exige o módulo que este protocolo se recusa a escrever antes de a linha passar), e nada sobre o gatilho de SALTO nesses mesmos mercados — isso está em `Gate_event_driven.md`.

