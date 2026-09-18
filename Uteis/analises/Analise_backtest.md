# Análise estatística do backtest — o número e a sua incerteza

> Gerado por `scripts/analise_backtest.py` sobre `Uteis/dados/backtest_diario.csv` (cenário `tilt ≤ 1`, 374 pregões) e as grades já gravadas. **Mede; não decide.** Escolhas pré-registradas na D33. Bootstrap estacionário (bloco médio 10, B = 2000, semente 20260918); Newey-West 5 lags; nível 95%.

## A. Inferência do número-título

| métrica | valor | nota |
|---|---|---|
| pregões (T) | 374 |  |
| Sharpe Kairós | 1.181 | anualizado, taxa livre zero |
| Sharpe Kairós · IC95 Lo (iid) | [-0.43; 2.79] | Lo (2002) |
| Sharpe Kairós · IC95 bootstrap | [-0.23; 3.04] | estacionário |
| Sharpe SPY | 1.081 |  |
| ΔSharpe (K − SPY) | 0.101 |  |
| ΔSharpe · IC95 bootstrap | [-0.42; 0.63] | Ledoit-Wolf (2008) |
| P(ΔSharpe > 0) | 0.664 | bootstrap |
| excesso acumulado (pp) | 3.045 | líquido − SPY, composto |
| excesso · IC95 bootstrap (pp) | [-12.9; 20.6] |  |
| P(excesso > 0) | 0.639 | bootstrap |
| alpha anualizado | 0.026 | vs SPY, taxa livre zero |
| t do alpha (Newey-West) | 0.616 | 5 lags · régua de Harvey-Liu: 3 |
| beta vs SPY | 0.945 |  |
| information ratio | 0.295 | excesso / tracking error |
| tracking error | 0.051 | anualizado |
| t do tilt líquido | 0.360 | r_tilt − custo |
| assimetria | 1.364 | retornos diários |
| curtose | 25.961 | não excedente |
| ACF(1) dos retornos | -0.072 |  |
| PSR(SR* = 0) | 0.932 | Bailey-LdP (2012) |
| MinTRL a 95 % (pregões) | 456.724 | temos 374 |

**Leitura.** O excesso de +3.04 pp tem IC95 [-12.9; 20.6] e P(> 0) = 64%; o Sharpe 1.18 tem IC95 [-0.23; 3.04]; o alpha tem t = 0.62 contra a régua de 3 de Harvey-Liu. Faltam 83 pregões para o track record mínimo a 95 %. **Em 374 pregões o número não separa habilidade de sorte** — o que sustenta a estratégia é o mecanismo medido fora do resultado (calibração do Polymarket, β por event-study, Ω julgado pelo erro da probabilidade), não o p-valor.

### Deflated Sharpe Ratio — grade de tentativas

Nenhuma linha é 'a' correção. `V medido` é a variância dos Sharpe das configurações gravadas (tetos, γ, bandas) — tentativas correlacionadas, logo V subestima; `V independente` é o SE² de Lo de uma tentativa de ruído do mesmo comprimento — cota superior. A verdade está entre as duas.

| tentativas | N | variância | σ(SR) anual | E[max SR] anual | DSR |
|---|---|---|---|---|---|
| configurações com Sharpe gravado | 18 | V medido nas configurações | 0.139 | 0.257 | 0.878 |
| configurações com Sharpe gravado | 18 | V de tentativas independentes | 0.822 | 1.524 | 0.333 |
| hipóteses medidas (LOG) | 31 | V medido nas configurações | 0.139 | 0.290 | 0.869 |
| hipóteses medidas (LOG) | 31 | V de tentativas independentes | 0.822 | 1.715 | 0.251 |
| + células da busca tática (D27) | 231 | V medido nas configurações | 0.139 | 0.391 | 0.840 |
| + células da busca tática (D27) | 231 | V de tentativas independentes | 0.822 | 2.312 | 0.077 |

## B. De onde vem o resultado

| métrica | valor | nota |
|---|---|---|
| dias com tilt ≠ 0 | 364.000 |  |
| hit ratio do tilt | 0.500 | dias com tilt > 0 |
| ganho médio nos dias + (bps) | 20.414 |  |
| perda média nos dias − (bps) | -17.548 |  |
| payoff (ganho / |perda|) | 1.163 |  |
| HHI dos dias positivos | 0.009 | López de Prado (2018) |
| HHI dos dias negativos | 0.013 |  |
| soma do tilt (pp) | 5.215 | perna das views, bruta |
| 3 maiores dias (pp) | 3.520 |  |
| sem os 3 maiores (pp) | 1.695 |  |
| 3 piores dias (pp) | -4.501 |  |
| sem os 3 piores (pp) | 9.717 |  |
| 10 maiores dias (pp) | 10.109 |  |

### Tilt por nº de views ativas no dia

| views ativas | dias | tilt médio (bps) | hit |
|---|---|---|---|
| 0 | 28 | -1.75 | 0.36 |
| 1 | 83 | 2.64 | 0.51 |
| 2 | 130 | 1.65 | 0.47 |
| 3 | 130 | 0.73 | 0.52 |
| 4 | 3 | 14.39 | 0.33 |

## C. Estabilidade

### Metades da janela

| metade | retorno K | retorno SPY | excesso (pp) | Sharpe K | Sharpe SPY | pregões |
|---|---|---|---|---|---|---|
| 1ª metade | 17.05 | 13.77 | 3.27 | 1.11 | 0.92 | 187.00 |
| 2ª metade | 13.77 | 14.37 | -0.60 | 1.37 | 1.40 | 187.00 |

### Regime do SPY

| regime | dias | K médio (bps) | SPY médio (bps) | excesso médio (bps) | hit do excesso |
|---|---|---|---|---|---|
| SPY em alta | 208 | 67.84 | 71.72 | -3.88 | 0.43 |
| SPY em queda | 166 | -66.37 | -72.59 | 6.22 | 0.52 |

### Drawdown, meses e janelas móveis

| métrica | valor | nota |
|---|---|---|
| máx. drawdown Kairós (%) | -19.650 |  |
| máx. drawdown SPY (%) | -18.755 |  |
| time under water Kairós (pregões) | 87 | maior sequência abaixo do pico |
| time under water SPY (pregões) | 87 |  |
| meses K > SPY | 11 de 19 |  |
| rolling IR 63d > 0 (fração) | 0.772 |  |
| rolling IR 63d mín / máx | -2.64 / 3.83 |  |
| rolling beta 63d mín / máx | 0.75 / 1.06 |  |

### Os 3 maiores drawdowns

| início | fundo | recuperação | profundidade (%) | pregões |
|---|---|---|---|---|
| 2025-02-20 | 2025-04-08 | 2025-06-26 | -19.6 | 88 |
| 2026-03-02 | 2026-03-30 | 2026-04-24 | -10.3 | 39 |
| 2026-06-03 | 2026-07-30 | em aberto | -6.0 | 45 |

### Retornos mensais

| mês | Kairós | SPY | K > SPY |
|---|---|---|---|
| 2025-02 | -0.59 | -1.10 | True |
| 2025-03 | -6.85 | -5.57 | False |
| 2025-04 | 0.71 | -0.87 | True |
| 2025-05 | 5.42 | 6.28 | False |
| 2025-06 | 5.68 | 5.14 | True |
| 2025-07 | 2.94 | 2.30 | True |
| 2025-08 | 2.46 | 2.05 | True |
| 2025-09 | 2.77 | 3.56 | False |
| 2025-10 | 5.01 | 2.38 | True |
| 2025-11 | 0.95 | 0.20 | True |
| 2025-12 | -0.79 | 0.08 | False |
| 2026-01 | 2.92 | 1.47 | True |
| 2026-02 | 3.52 | -0.86 | True |
| 2026-03 | -8.51 | -4.94 | False |
| 2026-04 | 10.63 | 10.51 | True |
| 2026-05 | 6.71 | 5.26 | True |
| 2026-06 | -2.09 | -1.03 | False |
| 2026-07 | -3.00 | 0.03 | False |
| 2026-08 | 2.88 | 2.88 | False |

## D. Implementação

| métrica | valor | nota |
|---|---|---|
| giro diário médio | 0.396 | fração do patrimônio |
| giro desfeito em 1–2 pregões | 0.419 | backtest_v1 |
| custo pago (pp) | 2.965 | 2 bps por lado |
| breakeven (bps por lado) | 22.869 | backtest_v1 |
| Σ|w| média | 1.915 |  |
| views ativas por dia | 1.992 |  |

## Referências

Lo (2002) FAJ · Bailey & López de Prado (2012) *Sharpe Ratio Efficient Frontier* · Bailey & López de Prado (2014) *Deflated Sharpe Ratio*, JPM · Ledoit & Wolf (2008) JEF · Politis & Romano (1994) JASA · Harvey & Liu (2015) *Backtesting*, JPM · López de Prado (2018) *Advances in Financial ML*, cap. 14 · Grinold & Kahn (2000). Detalhe em `Final/analise/Pesquisa_avaliacao_estrategia.md`.