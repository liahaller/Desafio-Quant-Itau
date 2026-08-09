# Teste de sinal das views — VETO, não certificado

> Gerado por `scripts/teste_sinal.py`. **Mede; não decide.** Regressão de `r_P(D→D+h)` contra o `Q(D)` da própria view. As views 2.2 e 2.3 são **controle embutido**: se elas não reproduzirem o registrado na 15f, o errado é o script.

| view | n | h = 1: coef · t · acerto | h = 5: coef · t · acerto | h = divulgação: coef · t · acerto |
|---|---|---|---|---|
| 2.2 | 274 | +0.0015 · t +0.57 · 53% | +0.0049 · t +0.85 · 50% | +0.0032 · t +0.50 · 58% |
| 2.3 | 325 | +0.1191 · t +0.26 · 51% | +0.2280 · t +0.23 · 56% | +nan · t +nan · nan% |
| transversal (β cru) | 274 | -0.0071 · t -1.08 · 49% | -0.0128 · t -0.86 · 43% | **-0.0460 · t -2.72 · 36%** |
| transversal (β ⊥ risk-on) | 274 | -0.0086 · t -0.90 · 49% | **-0.0524 · t -2.36 · 47%** | -0.0332 · t -1.12 · 37% |

## Elo 2 — o transporte do β (foi ele que matou a 15f)

corr entre o coeficiente PREDITIVO de cada ativo e o β contemporâneo usado para montar o P. A 15f mediu **+0,06**.

| variante | h = 1 | h = 5 | h = divulgação |
|---|---|---|---|
| transversal (β cru) | -0.35 | +0.04 | -0.48 |
| transversal (β ⊥ risk-on) | -0.81 | -0.50 | -0.84 |

## P do último pregão (onde cada variante fica posicionada)

| variante | SPY | TIP | TLT | XLE | XLF | XLK | XLP | XLU | XLV |
|---|---|---|---|---|---|---|---|---|---|
| transversal (β cru) | +0.00 | -0.29 | -0.70 | +0.31 | +0.15 | -0.02 | -0.21 | -0.18 | -0.15 |
| transversal (β ⊥ risk-on) | +0.00 | +0.67 | -0.02 | +0.84 | +0.00 | -0.16 | -0.15 | +0.02 | -0.14 |
