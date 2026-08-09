# Convergência da view 2.2 — horizonte do repricing (7.2 / 7.4)

> Gerado por `scripts/convergencia_2_2.py`. **Mede; não fecha o horizonte.** Divergência = inflação mensal anualizada implícita na PMF − breakeven de 10 anos. Repricing medido em `log(TIP) − log(TLT)`.

- meses utilizáveis: **13** · observações diárias: 277
- **viés estrutural (7.4):** divergência média = **+1.87 pp**, desvio 2.32 pp — a média é o descasamento 1 mês × 10 anos, não sinal. É ela que a view precisa remover.

**Regressão empilhada** (janelas sobrepostas — |t| otimista): retorno TIP−TLT de t até a divulgação contra a divergência em t

- coeficiente **-0.1136** · t -2.76 · n 277

**Teste mais limpo — o próprio breakeven anda na direção do poly?** `log(TIP) − log(TLT)` mistura durations muito diferentes (TIP ~7 anos, TLT ~26), então o movimento do TLT abafa o sinal de inflação. Δbreakeven mede a convergência direto, sem esse ruído:

- Δ do breakeven de t até a divulgação contra a divergência em t: coeficiente **+0.00460** · t +2.67 · n 277
- (a view prevê coeficiente **positivo**: poly mais inflacionista que o título ⇒ o breakeven sobe até a divulgação)

**O coeficiente é estável ao longo da contagem regressiva?** (se o gap total é o mesmo, deve ser)

| dias até a divulgação | n | coef. Δbreakeven | t |
|---|---|---|---|
| mais de 15 | 83 | +0.00547 | +1.35 |
| 6 a 15 | 129 | +0.00605 | +2.28 |
| 1 a 5 | 65 | +0.00198 | +1.31 |

**Um ponto por mês** (episódios independentes — é a leitura honesta do tamanho de amostra):

| mês | slots | divergência média | retorno TIP−TLT na janela |
|---|---|---|---|
| February 2025 | 31 | +1.54 pp | -0.33% |
| March 2025 | 29 | -0.77 pp | +3.45% |
| May 2025 | 29 | -0.12 pp | -1.01% |
| June 2025 | 34 | +0.63 pp | +2.80% |
| July 2025 | 28 | +0.65 pp | -1.64% |
| August 2025 | 30 | +1.68 pp | -1.89% |
| September 2025 | 43 | +2.41 pp | -1.58% |
| November 2025 | 35 | +1.47 pp | +0.44% |
| December 2025 | 37 | +1.07 pp | +0.04% |
| March 2026 | 30 | +7.68 pp | +0.24% |
| April 2026 | 30 | +4.89 pp | +2.04% |
| May 2026 | 28 | +4.08 pp | -1.06% |
| June 2026 | 34 | -0.91 pp | +1.38% |

- correlação entre os dois: coeficiente -0.1106 · t -0.52 · n 13 episódios
