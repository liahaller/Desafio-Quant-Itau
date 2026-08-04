# View 3.1 — o sinal de NÍVEL prevê retorno? (D2b)

> Gerado por `scripts/nivel_divergencia_3_1.py`. **Mede; não decide.** Discordância padronizada entre a probabilidade de recessão do Polymarket e a curva de juros (`z(p_poly) − z(−spread)`), contra o retorno dos pregões seguintes, entrando na abertura.

- pregões com os dois termômetros: **245** (2025-01-08 a 2025-12-31)
- discordância: mediana -0.18 desvios · mín -1.62 · máx +2.21
- correlação entre os dois termômetros (nível): **+0.56**

Coeficiente do retorno futuro contra a discordância (**|t| > 2 em negrito**); a view prevê **negativo** para ativo cíclico — mais risco de recessão do que a curva reconhece:

| N pregões | SPY | TIP | TLT | XLE | XLF | XLK | XLP | XLU | XLV |
|---|---|---|---|---|---|---|---|---|---|
| 1 | +0.11% | +0.02% | +0.02% | +0.05% | **+0.15%** | +0.14% | +0.07% | +0.11% | +0.02% |
| 5 | **+0.35%** | **+0.12%** | **+0.24%** | +0.21% | **+0.76%** | +0.33% | **+0.37%** | **+0.48%** | +0.15% |
| 10 | **+0.59%** | **+0.18%** | **+0.32%** | +0.11% | **+1.09%** | +0.60% | **+0.81%** | **+0.39%** | +0.14% |
| 21 | **+0.82%** | **+0.14%** | +0.14% | +0.66% | **+0.97%** | **+1.34%** | **+1.59%** | +0.41% | **-0.85%** |

- (coeficiente = retorno por 1 desvio de discordância; n ≈ 245)

Mesma conta no par que a view realmente monta — **defensivo menos cíclico** (XLP+XLU contra XLK+XLF), que é onde o P da 3.1 concentra peso. A view prevê coeficiente **positivo** aqui:

| N pregões | coeficiente | t | n |
|---|---|---|---|
| 1 | -0.05% | -0.71 | 245 |
| 5 | -0.12% | -0.71 | 245 |
| 10 | -0.24% | -1.05 | 245 |
| 21 | -0.15% | -0.46 | 245 |

> Janelas sobrepostas para N > 1 e z-score in sample: o |t| é otimista e o coeficiente não é retorno realizável. O que a tabela responde é **se existe sinal**, não quanto ele rende.

