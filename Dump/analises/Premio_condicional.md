# Prêmio de anúncio condicionado à incerteza (tática 1.3)

> Gerado por `scripts/premio_condicional.py`. **Mede; não decide.** Incerteza = entropia normalizada da PMF do Polymarket no slot pré-abertura do dia do anúncio (não usa valor de balde nem renormalização — independe das decisões 1.2 e 6.1).


## FOMC (PMF de cortes 2025)

- anúncios com PMF na véspera: **7** (2025-01-29 a 2025-12-10)
- entropia: mín 0.08 · mediana 0.83 · máx 0.93

| grupo | n | retorno médio do SPY | mediana | t |
|---|---|---|---|---|
| evento INCERTO (entropia alta) | 3 | +0.354% | +0.421% | +0.79 |
| evento previsível (entropia baixa) | 4 | +0.099% | -0.070% | +0.52 |

- diferença (incerto − previsível): **+0.254%** (t de Welch +0.53) · nas medianas: +0.490%

## CPI (PMF do mês)

- anúncios com PMF na véspera: **13** (2025-03-12 a 2026-07-14)
- entropia: mín 0.07 · mediana 0.62 · máx 0.78

| grupo | n | retorno médio do SPY | mediana | t |
|---|---|---|---|---|
| evento INCERTO (entropia alta) | 6 | +0.398% | +0.487% | +1.79 |
| evento previsível (entropia baixa) | 7 | -1.012% | -0.427% | -1.54 |

- diferença (incerto − previsível): **+1.410%** (t de Welch +2.03) · nas medianas: +0.915%

## Payrolls (PMF do Employment Situation)

- anúncios com PMF na véspera: **12** (2025-01-10 a 2026-07-02)
- entropia: mín 0.68 · mediana 0.83 · máx 0.96

| grupo | n | retorno médio do SPY | mediana | t |
|---|---|---|---|---|
| evento INCERTO (entropia alta) | 6 | -0.217% | -0.148% | -0.67 |
| evento previsível (entropia baixa) | 6 | -1.593% | -0.908% | -1.63 |

- diferença (incerto − previsível): **+1.376%** (t de Welch +1.33) · nas medianas: +0.760%

## As famílias de anúncio juntas

| grupo | n | retorno médio do SPY | mediana | t |
|---|---|---|---|---|
| evento INCERTO | 15 | +0.143% | +0.421% | +0.78 |
| evento previsível | 17 | -0.956% | -0.151% | -2.14 |

- diferença (incerto − previsível): **+1.099%** (t de Welch +2.27) · nas medianas: +0.572%
- referência: dias SEM anúncio entre 2025-01-10 e 2026-07-14 — 345 pregões, média +0.123%, mediana +0.145%
- robustez: tirando o pregão mais extremo do grupo incerto (2026-03-06), a média dele vai de +0.143% para +0.247%
- robustez (simétrica): tirando o extremo dos DOIS grupos (2026-03-06 e 2025-04-04, este último 5.9% em módulo), a diferença vai de +1.099% para **+0.896%** e o t de Welch de +2.27 para **+2.34**

## Limite de leitura

**A entropia não vive na mesma faixa em toda família** — o corte é a mediana DE CADA UMA, então cada split é interno, mas o rótulo não é comparável entre elas:

- FOMC (PMF de cortes 2025): entropia de **0.08 a 0.93**
- CPI (PMF do mês): entropia de **0.07 a 0.78**
- Payrolls (PMF do Employment Situation): entropia de **0.68 a 0.96**

Onde a faixa inteira é alta, o grupo "previsível" é apenas o *menos incerto* da família — não um anúncio que o mercado dava como resolvido. A leitura de Savor-Wilson (prêmio = compensação por risco de evento) se aplica ao CONTRASTE dentro da família, não ao nível absoluto.

A PMF do Polymarket só existe de 2025 em diante, então a versão condicional tem **muito menos eventos** que a incondicional (que usava o calendário de FOMC desde 2022). Diferença sem significância aqui não é evidência de ausência — é amostra curta. O que a medição entrega é a ORDEM DE GRANDEZA e o sinal.

