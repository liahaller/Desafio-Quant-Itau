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

- anúncios com PMF na véspera: **12** (2025-03-12 a 2026-06-10)
- entropia: mín 0.33 · mediana 0.62 · máx 0.78

| grupo | n | retorno médio do SPY | mediana | t |
|---|---|---|---|---|
| evento INCERTO (entropia alta) | 6 | +0.398% | +0.487% | +1.79 |
| evento previsível (entropia baixa) | 6 | -1.240% | -1.002% | -1.70 |

- diferença (incerto − previsível): **+1.638%** (t de Welch +2.15) · nas medianas: +1.489%

## Os dois tipos de anúncio juntos

| grupo | n | retorno médio do SPY | mediana | t |
|---|---|---|---|---|
| evento INCERTO | 9 | +0.383% | +0.444% | +1.99 |
| evento previsível | 10 | -0.704% | -0.139% | -1.47 |

- diferença (incerto − previsível): **+1.087%** (t de Welch +2.10) · nas medianas: +0.583%
- referência: dias SEM anúncio entre 2025-01-29 e 2026-06-10 — 324 pregões, média +0.079%, mediana +0.121%
- robustez: tirando o pregão mais extremo do grupo incerto (2025-03-19), a média dele vai de +0.383% para +0.295%

## Limite de leitura

A PMF do Polymarket só existe de 2025 em diante, então a versão condicional tem **muito menos eventos** que a incondicional (que usava o calendário de FOMC desde 2022). Diferença sem significância aqui não é evidência de ausência — é amostra curta. O que a medição entrega é a ORDEM DE GRANDEZA e o sinal.

