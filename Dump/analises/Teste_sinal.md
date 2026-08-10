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
