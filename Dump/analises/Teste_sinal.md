# Teste de sinal das views — VETO, não certificado

> Gerado por `scripts/teste_sinal.py`. **Mede; não decide.** Regressão de `r_P(D→D+h)` contra o `Q(D)` da própria view. As views 2.2 e 2.3 são **controle embutido**: se elas não reproduzirem o registrado na 15f, o errado é o script.

**`h = 0` é o próprio pregão de D** — o que o backtest de fato ganha (a montagem de D só olha dado anterior à abertura de D) e o ÚNICO horizonte da 15b, cujo Q é o close-to-close do dia do anúncio. O controle reproduz no `h = 1`, que é a convenção em que 15f e 15g registraram os números.

As linhas **incerteza (15b)** e **B com β próprio (15g)** entraram em 2026-08-10: as duas tinham sido medidas no BACKTEST (15h) e nunca aqui, e a B com o `DGS1` era pendência de protocolo aberta na 15h (`o teste de sinal no vértice certo segue não rodado`). Rodam com `views_novas=("incerteza", "B")`; a entrega segue `views_novas=()`.

| view | n | h = 0: coef · t · acerto | h = 1: coef · t · acerto | h = 5: coef · t · acerto | h = divulgação: coef · t · acerto |
|---|---|---|---|---|---|
| 2.2 | 274 | +0.0008 · t +0.29 · 50% | +0.0015 · t +0.57 · 53% | +0.0049 · t +0.85 · 50% | +0.0032 · t +0.50 · 58% |
| 2.3 | 325 | +0.2767 · t +0.59 · 50% | +0.1191 · t +0.26 · 51% | +0.2280 · t +0.23 · 56% | +nan · t +nan · nan% |
| transversal (β cru) | 274 | -0.0098 · t -1.47 · 49% | -0.0071 · t -1.08 · 49% | -0.0128 · t -0.86 · 43% | **-0.0460 · t -2.72 · 36%** |
| transversal (β ⊥ risk-on) | 274 | **-0.0187 · t -2.02 · 51%** | -0.0086 · t -0.90 · 49% | **-0.0524 · t -2.36 · 47%** | -0.0332 · t -1.12 · 37% |
| incerteza (15b) | 27 | +0.0244 · t +0.06 · 44% | -0.0388 · t -0.17 · 41% | +0.4241 · t +0.93 · 41% | +nan · t +nan · nan% |
| B com β próprio (15g) | 210 | +0.0061 · t +0.05 · 51% | +0.0383 · t +0.33 · 51% | +0.1560 · t +0.65 · 53% | +nan · t +nan · nan% |
| C geopolítica (k = 1) | 72 | -0.0501 · t -0.43 · 44% | -0.0735 · t -0.68 · 53% | -0.3541 · t -1.63 · 47% | +nan · t +nan · nan% |
| C geopolítica (k = 2) | 68 | -0.0297 · t -0.75 · 53% | -0.0195 · t -0.50 · 53% | -0.0270 · t -0.42 · 44% | +nan · t +nan · nan% |
| C geopolítica (k = 3) | 64 | +0.0251 · t +1.29 · 55% | +0.0288 · t +1.44 · 56% | -0.0627 · t -1.59 · 48% | +nan · t +nan · nan% |
| C geopolítica (k = 4) | 60 | +0.0083 · t +0.41 · 47% | +0.0020 · t +0.10 · 53% | +0.0022 · t +0.05 · 50% | +nan · t +nan · nan% |
| C geopolítica (k = 5) | 56 | +0.0170 · t +0.56 · 55% | -0.0184 · t -0.62 · 45% | +0.0822 · t +1.47 · 50% | +nan · t +nan · nan% |
| C iran_jun2025 (k = 1) | 50 | -0.1757 · t -0.75 · 38% | **+0.4015 · t +2.13 · 52%** | -0.1073 · t -0.27 · 46% | +nan · t +nan · nan% |
| C iran_jun2025 (k = 2) | 48 | -0.0171 · t -0.31 · 50% | -0.0344 · t -0.61 · 50% | -0.0092 · t -0.10 · 42% | +nan · t +nan · nan% |
| C iran_jun2025 (k = 3) | 46 | -0.0465 · t -0.66 · 50% | +0.0988 · t +1.39 · 54% | +0.0616 · t +0.47 · 57% | +nan · t +nan · nan% |
| C iran_jun2025 (k = 4) | 44 | +0.0300 · t +0.47 · 45% | -0.0110 · t -0.17 · 52% | -0.1077 · t -0.98 · 55% | +nan · t +nan · nan% |
| C iran_jun2025 (k = 5) | 42 | +0.0211 · t +0.68 · 60% | -0.0150 · t -0.52 · 48% | +0.1065 · t +1.94 · 57% | +nan · t +nan · nan% |
| C iran_2026 (k = 1) | 22 | -0.0586 · t -0.44 · 59% | -0.2385 · t -1.60 · 55% | -0.5166 · t -1.70 · 50% | +nan · t +nan · nan% |
| C iran_2026 (k = 2) | 20 | -0.0696 · t -1.20 · 60% | -0.0123 · t -0.23 · 60% | -0.0796 · t -0.84 · 50% | +nan · t +nan · nan% |
| C iran_2026 (k = 3) | 18 | +0.0284 · t +1.52 · 67% | +0.0228 · t +1.11 · 61% | -0.0641 · t -1.33 · 28% | +nan · t +nan · nan% |
| C iran_2026 (k = 4) | 16 | +0.0013 · t +0.09 · 50% | +0.0033 · t +0.22 · 56% | +0.0184 · t +0.30 · 38% | +nan · t +nan · nan% |
| C iran_2026 (k = 5) | 14 | -0.1004 · t -0.53 · 43% | -0.1194 · t -0.56 · 36% | -0.4340 · t -1.28 · 29% | +nan · t +nan · nan% |

**Como ler as linhas por episódio da C, e é o ponto todo:** as linhas `C geopolítica (k = …)` juntam os dois episódios do Irã, e por isso **não servem para escolher o k** — o k de melhor t nelas é o k ajustado à amostra inteira. As linhas `C iran_jun2025` e `C iran_2026` são os dois episódios SEPARADOS, que não se sobrepõem em data. Um k escolhido no primeiro é pré-registro para o segundo, e a comparação de SINAL entre os dois é o único teste aqui que distingue tese de ajuste de amostra.


## Elo 2 — o transporte do β (foi ele que matou a 15f)

corr entre o coeficiente PREDITIVO de cada ativo e o β contemporâneo usado para montar o P. A 15f mediu **+0,06**.

| variante | h = 0 | h = 1 | h = 5 | h = divulgação |
|---|---|---|---|---|
| transversal (β cru) | -0.38 | -0.35 | +0.04 | -0.48 |
| transversal (β ⊥ risk-on) | -0.69 | -0.81 | -0.50 | -0.84 |

## P do último pregão (onde cada variante fica posicionada)

| variante | SPY | TIP | TLT | XLE | XLF | XLK | XLP | XLU | XLV |
|---|---|---|---|---|---|---|---|---|---|
| transversal (β cru) | +0.00 | -0.29 | -0.70 | +0.31 | +0.15 | -0.02 | -0.21 | -0.18 | -0.15 |
| transversal (β ⊥ risk-on) | +0.00 | +0.67 | -0.02 | +0.84 | +0.00 | -0.16 | -0.15 | +0.02 | -0.14 |
