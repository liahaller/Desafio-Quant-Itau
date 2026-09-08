# M4 recessão — a contradição com a D19c, em 2×2

> Gerado por `scripts/gate_recessao_2x2.py`. **Mede; não decide.** Nenhuma premissa nova: os dois livros, a discordância, o `Δp`, as pernas `⊥` e a partição em metades são importados por referência dos artefatos anteriores. O que este artefato acrescenta é o **cruzamento** entre o sinal de um e o livro do outro.

- janela: **2025-02-10 a 2026-08-06** (374 pregões); δ e Σ os mesmos do v1 (D7/D8)
- livro da 3.1: `{'SPY': -1, 'TLT': 1}` — *p(recessão) sobe → risco-off: bolsa cai e duração sobe*
- livro da sleeve: `{'XLP⊥': 1, 'XLK⊥': -1}` — *p(recessão) sobe → defensivo (XLP) bate cíclico (XLK)*
- correlação entre as duas séries de `p` (a normalizada que a 3.1 lê × o midpoint cru que a sleeve lê, 245 pregões comuns): **+1.000**

## As quatro células, e as três que faltavam

| | livro: SPY direcional | livro: spread neutro |
|---|---|---|
| **sinal: nível (discordância)** | a **D19c** | ⬅ célula nova |
| **sinal: incremento (Δp)** | ⬅ célula nova | a **D27** |

As parcelas da discordância (`z(poly)` e `z(−spread)` sozinhas) e o `Δ` da própria discordância entram como linhas extras: sem elas não dá para dizer se um giro veio do Polymarket ou da curva de juros.

## Tabela

| régua                             | sinal                              | livro                           | inteira   | 1ª metade   | 2ª metade   | gira (fraco)   | gira (D19c: |t| > 2 nas duas)   |   n (inteira) |
|:----------------------------------|:-----------------------------------|:--------------------------------|:----------|:------------|:------------|:---------------|:--------------------------------|--------------:|
| G2 (μ encolhido, janela 1 pregão) | discordância (o sinal da 3.1)      | SPY direcional (livro da 3.1)   | ❌        | ❌          | ❌          | 🛑 SIM         | —                               |           186 |
| G2 (μ encolhido, janela 1 pregão) | discordância (o sinal da 3.1)      | spread neutro (livro da sleeve) | ✅        | ❌          | ✅          | 🛑 SIM         | —                               |           186 |
| G2 (μ encolhido, janela 1 pregão) | z(poly) — só a perna do Polymarket | SPY direcional (livro da 3.1)   | ❌        | ❌          | ❌          | 🛑 SIM         | —                               |           186 |
| G2 (μ encolhido, janela 1 pregão) | z(poly) — só a perna do Polymarket | spread neutro (livro da sleeve) | ❌        | ❌          | ✅          | 🛑 SIM         | —                               |           186 |
| G2 (μ encolhido, janela 1 pregão) | z(−spread) — só a perna do mercado | SPY direcional (livro da 3.1)   | ❌        | ❌          | ❌          | 🛑 SIM         | —                               |           186 |
| G2 (μ encolhido, janela 1 pregão) | z(−spread) — só a perna do mercado | spread neutro (livro da sleeve) | ❌        | ❌          | ❌          | não            | —                               |           186 |
| G2 (μ encolhido, janela 1 pregão) | Δ discordância (k = 5)             | SPY direcional (livro da 3.1)   | ✅        | ✅          | ✅          | não            | —                               |           181 |
| G2 (μ encolhido, janela 1 pregão) | Δ discordância (k = 5)             | spread neutro (livro da sleeve) | ❌        | ✅          | ❌          | 🛑 SIM         | —                               |           181 |
| G2 (μ encolhido, janela 1 pregão) | Δp k = 3 (o sinal da sleeve)       | SPY direcional (livro da 3.1)   | ✅        | ❌          | ✅          | 🛑 SIM         | —                               |           220 |
| G2 (μ encolhido, janela 1 pregão) | Δp k = 3 (o sinal da sleeve)       | spread neutro (livro da sleeve) | ✅        | ✅          | ✅          | não            | —                               |           220 |
| G2 (μ encolhido, janela 1 pregão) | Δp k = 5 (o sinal da sleeve)       | SPY direcional (livro da 3.1)   | ✅        | ✅          | ✅          | não            | —                               |           227 |
| G2 (μ encolhido, janela 1 pregão) | Δp k = 5 (o sinal da sleeve)       | spread neutro (livro da sleeve) | ✅        | ✅          | ✅          | não            | —                               |           227 |
| G2 (μ encolhido, janela 1 pregão) | Δp k = 10 (o sinal da sleeve)      | SPY direcional (livro da 3.1)   | ❌        | ❌          | ❌          | não            | —                               |           229 |
| G2 (μ encolhido, janela 1 pregão) | Δp k = 10 (o sinal da sleeve)      | spread neutro (livro da sleeve) | ✅        | ✅          | ✅          | não            | —                               |           229 |
| OLS (h = 10, a régua da D19c)     | discordância (o sinal da 3.1)      | SPY direcional (livro da 3.1)   | ❌        | ❌          | ❌          | 🛑 SIM         | 🛑 SIM                          |           186 |
| OLS (h = 10, a régua da D19c)     | discordância (o sinal da 3.1)      | spread neutro (livro da sleeve) | ❌        | ❌          | ✅          | 🛑 SIM         | 🛑 SIM                          |           186 |
| OLS (h = 10, a régua da D19c)     | z(poly) — só a perna do Polymarket | SPY direcional (livro da 3.1)   | ❌        | ❌          | ❌          | 🛑 SIM         | não                             |           186 |
| OLS (h = 10, a régua da D19c)     | z(poly) — só a perna do Polymarket | spread neutro (livro da sleeve) | ❌        | ❌          | ✅          | 🛑 SIM         | 🛑 SIM                          |           186 |
| OLS (h = 10, a régua da D19c)     | z(−spread) — só a perna do mercado | SPY direcional (livro da 3.1)   | ❌        | ❌          | ❌          | 🛑 SIM         | não                             |           186 |
| OLS (h = 10, a régua da D19c)     | z(−spread) — só a perna do mercado | spread neutro (livro da sleeve) | ❌        | ❌          | ❌          | 🛑 SIM         | não                             |           186 |
| OLS (h = 10, a régua da D19c)     | Δ discordância (k = 5)             | SPY direcional (livro da 3.1)   | ✅        | ✅          | ❌          | 🛑 SIM         | não                             |           181 |
| OLS (h = 10, a régua da D19c)     | Δ discordância (k = 5)             | spread neutro (livro da sleeve) | ✅        | ❌          | ✅          | 🛑 SIM         | não                             |           181 |
| OLS (h = 10, a régua da D19c)     | Δp k = 3 (o sinal da sleeve)       | SPY direcional (livro da 3.1)   | ❌        | ❌          | ❌          | 🛑 SIM         | não                             |           251 |
| OLS (h = 10, a régua da D19c)     | Δp k = 3 (o sinal da sleeve)       | spread neutro (livro da sleeve) | ❌        | ❌          | ✅          | 🛑 SIM         | não                             |           251 |
| OLS (h = 10, a régua da D19c)     | Δp k = 5 (o sinal da sleeve)       | SPY direcional (livro da 3.1)   | ❌        | ❌          | ✅          | 🛑 SIM         | não                             |           249 |
| OLS (h = 10, a régua da D19c)     | Δp k = 5 (o sinal da sleeve)       | spread neutro (livro da sleeve) | ❌        | ❌          | ❌          | 🛑 SIM         | não                             |           249 |
| OLS (h = 10, a régua da D19c)     | Δp k = 10 (o sinal da sleeve)      | SPY direcional (livro da 3.1)   | ❌        | ❌          | ❌          | 🛑 SIM         | não                             |           244 |
| OLS (h = 10, a régua da D19c)     | Δp k = 10 (o sinal da sleeve)      | spread neutro (livro da sleeve) | ❌        | ❌          | ❌          | não            | não                             |           244 |

**Duas colunas de giro, e a diferença entre elas é o ponto.** O critério FRACO é só a troca de sinal; o FORTE é o da D19c palavra por palavra — *as duas metades significantes e apontando para lados opostos*. No G2 só existe o fraco: o μ encolhido não publica `t` em artefato nenhum deste projeto, e inventar um aqui daria à célula nova um critério que as células já publicadas não tiveram.

### Detalhe por perna

- **G2 (μ encolhido, janela 1 pregão)** · discordância (o sinal da 3.1) · SPY direcional (livro da 3.1)
    - inteira: `SPY -0.21 ✅ · TLT -1.91 ❌` (❌, n = 186)
    - 1ª metade: `SPY +0.78 ❌ · TLT -0.96 ❌` (❌, n = 93)
    - 2ª metade: `SPY -3.23 ✅ · TLT -1.41 ❌` (❌, n = 93)
- **G2 (μ encolhido, janela 1 pregão)** · discordância (o sinal da 3.1) · spread neutro (livro da sleeve)
    - inteira: `XLP⊥ +3.29 ✅ · XLK⊥ -2.07 ✅` (✅, n = 186)
    - 1ª metade: `XLP⊥ +0.07 ✅ · XLK⊥ +1.54 ❌` (❌, n = 93)
    - 2ª metade: `XLP⊥ +3.94 ✅ · XLK⊥ -3.83 ✅` (✅, n = 93)
- **G2 (μ encolhido, janela 1 pregão)** · z(poly) — só a perna do Polymarket · SPY direcional (livro da 3.1)
    - inteira: `SPY +0.73 ❌ · TLT -1.66 ❌` (❌, n = 186)
    - 1ª metade: `SPY +0.91 ❌ · TLT -1.23 ❌` (❌, n = 93)
    - 2ª metade: `SPY -1.28 ✅ · TLT -0.40 ❌` (❌, n = 93)
- **G2 (μ encolhido, janela 1 pregão)** · z(poly) — só a perna do Polymarket · spread neutro (livro da sleeve)
    - inteira: `XLP⊥ +1.42 ✅ · XLK⊥ +1.04 ❌` (❌, n = 186)
    - 1ª metade: `XLP⊥ -0.43 ❌ · XLK⊥ +1.85 ❌` (❌, n = 93)
    - 2ª metade: `XLP⊥ +2.11 ✅ · XLK⊥ -0.32 ✅` (✅, n = 93)
- **G2 (μ encolhido, janela 1 pregão)** · z(−spread) — só a perna do mercado · SPY direcional (livro da 3.1)
    - inteira: `SPY +3.01 ❌ · TLT -3.22 ❌` (❌, n = 186)
    - 1ª metade: `SPY +1.81 ❌ · TLT -3.06 ❌` (❌, n = 93)
    - 2ª metade: `SPY +1.38 ❌ · TLT +0.33 ✅` (❌, n = 93)
- **G2 (μ encolhido, janela 1 pregão)** · z(−spread) — só a perna do mercado · spread neutro (livro da sleeve)
    - inteira: `XLP⊥ -2.13 ❌ · XLK⊥ +2.53 ❌` (❌, n = 186)
    - 1ª metade: `XLP⊥ -2.23 ❌ · XLK⊥ +2.70 ❌` (❌, n = 93)
    - 2ª metade: `XLP⊥ -0.35 ❌ · XLK⊥ +0.71 ❌` (❌, n = 93)
- **G2 (μ encolhido, janela 1 pregão)** · Δ discordância (k = 5) · SPY direcional (livro da 3.1)
    - inteira: `SPY -4.07 ✅ · TLT +0.28 ✅` (✅, n = 181)
    - 1ª metade: `SPY -3.28 ✅ · TLT +0.12 ✅` (✅, n = 90)
    - 2ª metade: `SPY -1.50 ✅ · TLT +0.24 ✅` (✅, n = 91)
- **G2 (μ encolhido, janela 1 pregão)** · Δ discordância (k = 5) · spread neutro (livro da sleeve)
    - inteira: `XLP⊥ -0.09 ❌ · XLK⊥ -1.70 ✅` (❌, n = 181)
    - 1ª metade: `XLP⊥ +0.97 ✅ · XLK⊥ -1.85 ✅` (✅, n = 90)
    - 2ª metade: `XLP⊥ -0.92 ❌ · XLK⊥ -0.53 ✅` (❌, n = 91)
- **G2 (μ encolhido, janela 1 pregão)** · Δp k = 3 (o sinal da sleeve) · SPY direcional (livro da 3.1)
    - inteira: `SPY -2.84 ✅ · TLT +0.12 ✅` (✅, n = 220)
    - 1ª metade: `SPY -1.77 ✅ · TLT -0.39 ❌` (❌, n = 112)
    - 2ª metade: `SPY -1.01 ✅ · TLT +0.94 ✅` (✅, n = 108)
- **G2 (μ encolhido, janela 1 pregão)** · Δp k = 3 (o sinal da sleeve) · spread neutro (livro da sleeve)
    - inteira: `XLP⊥ +4.92 ✅ · XLK⊥ -3.02 ✅` (✅, n = 220)
    - 1ª metade: `XLP⊥ +2.03 ✅ · XLK⊥ -2.75 ✅` (✅, n = 112)
    - 2ª metade: `XLP⊥ +4.34 ✅ · XLK⊥ -1.01 ✅` (✅, n = 108)
- **G2 (μ encolhido, janela 1 pregão)** · Δp k = 5 (o sinal da sleeve) · SPY direcional (livro da 3.1)
    - inteira: `SPY -1.12 ✅ · TLT +2.70 ✅` (✅, n = 227)
    - 1ª metade: `SPY -0.66 ✅ · TLT +1.36 ✅` (✅, n = 116)
    - 2ª metade: `SPY -0.58 ✅ · TLT +2.05 ✅` (✅, n = 111)
- **G2 (μ encolhido, janela 1 pregão)** · Δp k = 5 (o sinal da sleeve) · spread neutro (livro da sleeve)
    - inteira: `XLP⊥ +3.62 ✅ · XLK⊥ -3.39 ✅` (✅, n = 227)
    - 1ª metade: `XLP⊥ +1.77 ✅ · XLK⊥ -2.07 ✅` (✅, n = 116)
    - 2ª metade: `XLP⊥ +2.78 ✅ · XLK⊥ -2.30 ✅` (✅, n = 111)
- **G2 (μ encolhido, janela 1 pregão)** · Δp k = 10 (o sinal da sleeve) · SPY direcional (livro da 3.1)
    - inteira: `SPY -3.64 ✅ · TLT -1.53 ❌` (❌, n = 229)
    - 1ª metade: `SPY -1.86 ✅ · TLT -1.13 ❌` (❌, n = 116)
    - 2ª metade: `SPY -3.06 ✅ · TLT -0.42 ❌` (❌, n = 113)
- **G2 (μ encolhido, janela 1 pregão)** · Δp k = 10 (o sinal da sleeve) · spread neutro (livro da sleeve)
    - inteira: `XLP⊥ +2.39 ✅ · XLK⊥ -2.47 ✅` (✅, n = 229)
    - 1ª metade: `XLP⊥ +0.86 ✅ · XLK⊥ -2.11 ✅` (✅, n = 116)
    - 2ª metade: `XLP⊥ +2.29 ✅ · XLK⊥ -0.88 ✅` (✅, n = 113)
- **OLS (h = 10, a régua da D19c)** · discordância (o sinal da 3.1) · SPY direcional (livro da 3.1)
    - inteira: `SPY +0.40% t +3.22 ❌ · TLT -0.11% t -0.84 ❌` (❌, n = 186)
    - 1ª metade: `SPY +0.97% t +6.52 ❌ · TLT -0.01% t -0.04 ❌` (❌, n = 93)
    - 2ª metade: `SPY -0.35% t -2.27 ✅ · TLT -0.24% t -1.42 ❌` (❌, n = 93)
- **OLS (h = 10, a régua da D19c)** · discordância (o sinal da 3.1) · spread neutro (livro da sleeve)
    - inteira: `XLP⊥ +0.33% t +2.43 ✅ · XLK⊥ +0.07% t +0.60 ❌` (❌, n = 186)
    - 1ª metade: `XLP⊥ -0.27% t -1.78 ❌ · XLK⊥ +0.79% t +7.21 ❌` (❌, n = 93)
    - 2ª metade: `XLP⊥ +1.14% t +5.39 ✅ · XLK⊥ -0.90% t -5.45 ✅` (✅, n = 93)
- **OLS (h = 10, a régua da D19c)** · z(poly) — só a perna do Polymarket · SPY direcional (livro da 3.1)
    - inteira: `SPY +1.07% t +10.31 ❌ · TLT -0.43% t -3.54 ❌` (❌, n = 186)
    - 1ª metade: `SPY +1.05% t +8.33 ❌ · TLT -0.47% t -2.92 ❌` (❌, n = 93)
    - 2ª metade: `SPY -1.04% t -0.53 ✅ · TLT -8.68% t -4.38 ❌` (❌, n = 93)
- **OLS (h = 10, a régua da D19c)** · z(poly) — só a perna do Polymarket · spread neutro (livro da sleeve)
    - inteira: `XLP⊥ -0.20% t -1.40 ❌ · XLK⊥ +0.64% t +5.98 ❌` (❌, n = 186)
    - 1ª metade: `XLP⊥ -0.20% t -1.39 ❌ · XLK⊥ +0.74% t +7.39 ❌` (❌, n = 93)
    - 2ª metade: `XLP⊥ +6.45% t +2.16 ✅ · XLK⊥ -8.49% t -3.84 ✅` (✅, n = 93)
- **OLS (h = 10, a régua da D19c)** · z(−spread) — só a perna do mercado · SPY direcional (livro da 3.1)
    - inteira: `SPY +0.77% t +5.98 ❌ · TLT -0.38% t -2.86 ❌` (❌, n = 186)
    - 1ª metade: `SPY +1.26% t +3.24 ❌ · TLT -2.76% t -9.52 ❌` (❌, n = 93)
    - 2ª metade: `SPY +0.37% t +2.32 ❌ · TLT +0.20% t +1.14 ✅` (❌, n = 93)
- **OLS (h = 10, a régua da D19c)** · z(−spread) — só a perna do mercado · spread neutro (livro da sleeve)
    - inteira: `XLP⊥ -0.63% t -4.34 ❌ · XLK⊥ +0.67% t +5.74 ❌` (❌, n = 186)
    - 1ª metade: `XLP⊥ +0.21% t +0.62 ✅ · XLK⊥ +0.36% t +1.18 ❌` (❌, n = 93)
    - 2ª metade: `XLP⊥ -1.19% t -5.41 ❌ · XLK⊥ +0.91% t +5.28 ❌` (❌, n = 93)
- **OLS (h = 10, a régua da D19c)** · Δ discordância (k = 5) · SPY direcional (livro da 3.1)
    - inteira: `SPY -0.74% t -3.54 ✅ · TLT +0.34% t +1.65 ✅` (✅, n = 181)
    - 1ª metade: `SPY -0.22% t -0.68 ✅ · TLT +0.82% t +2.73 ✅` (✅, n = 90)
    - 2ª metade: `SPY -0.90% t -3.61 ✅ · TLT -0.21% t -0.71 ❌` (❌, n = 91)
- **OLS (h = 10, a régua da D19c)** · Δ discordância (k = 5) · spread neutro (livro da sleeve)
    - inteira: `XLP⊥ +0.37% t +1.55 ✅ · XLK⊥ -0.93% t -4.81 ✅` (✅, n = 181)
    - 1ª metade: `XLP⊥ -0.08% t -0.29 ❌ · XLK⊥ -0.63% t -2.43 ✅` (❌, n = 90)
    - 2ª metade: `XLP⊥ +0.68% t +1.68 ✅ · XLK⊥ -1.14% t -3.84 ✅` (✅, n = 91)
- **OLS (h = 10, a régua da D19c)** · Δp k = 3 (o sinal da sleeve) · SPY direcional (livro da 3.1)
    - inteira: `SPY +3.75% t +0.81 ❌ · TLT -9.70% t -3.14 ❌` (❌, n = 251)
    - 1ª metade: `SPY +4.94% t +0.77 ❌ · TLT -9.66% t -2.69 ❌` (❌, n = 125)
    - 2ª metade: `SPY -7.09% t -0.85 ✅ · TLT -7.67% t -0.74 ❌` (❌, n = 126)
- **OLS (h = 10, a régua da D19c)** · Δp k = 3 (o sinal da sleeve) · spread neutro (livro da sleeve)
    - inteira: `XLP⊥ +0.84% t +0.22 ✅ · XLK⊥ +1.04% t +0.34 ❌` (❌, n = 251)
    - 1ª metade: `XLP⊥ -0.34% t -0.08 ❌ · XLK⊥ +1.09% t +0.31 ❌` (❌, n = 125)
    - 2ª metade: `XLP⊥ +4.61% t +0.35 ✅ · XLK⊥ -3.76% t -0.36 ✅` (✅, n = 126)
- **OLS (h = 10, a régua da D19c)** · Δp k = 5 (o sinal da sleeve) · SPY direcional (livro da 3.1)
    - inteira: `SPY +5.57% t +1.59 ❌ · TLT -5.86% t -2.49 ❌` (❌, n = 249)
    - 1ª metade: `SPY +6.79% t +1.41 ❌ · TLT -5.98% t -2.21 ❌` (❌, n = 124)
    - 2ª metade: `SPY -8.19% t -1.14 ✅ · TLT +0.24% t +0.03 ✅` (✅, n = 125)
- **OLS (h = 10, a régua da D19c)** · Δp k = 5 (o sinal da sleeve) · spread neutro (livro da sleeve)
    - inteira: `XLP⊥ -0.75% t -0.25 ❌ · XLK⊥ +1.40% t +0.60 ❌` (❌, n = 249)
    - 1ª metade: `XLP⊥ -1.24% t -0.37 ❌ · XLK⊥ +1.28% t +0.49 ❌` (❌, n = 124)
    - 2ª metade: `XLP⊥ -5.79% t -0.51 ❌ · XLK⊥ -1.96% t -0.22 ✅` (❌, n = 125)
- **OLS (h = 10, a régua da D19c)** · Δp k = 10 (o sinal da sleeve) · SPY direcional (livro da 3.1)
    - inteira: `SPY +4.77% t +1.91 ❌ · TLT -4.26% t -2.54 ❌` (❌, n = 244)
    - 1ª metade: `SPY +5.53% t +1.62 ❌ · TLT -3.90% t -2.04 ❌` (❌, n = 122)
    - 2ª metade: `SPY -5.92% t -0.90 ✅ · TLT -6.80% t -0.86 ❌` (❌, n = 122)
- **OLS (h = 10, a régua da D19c)** · Δp k = 10 (o sinal da sleeve) · spread neutro (livro da sleeve)
    - inteira: `XLP⊥ -0.94% t -0.45 ❌ · XLK⊥ +1.05% t +0.64 ❌` (❌, n = 244)
    - 1ª metade: `XLP⊥ -1.55% t -0.66 ❌ · XLK⊥ +0.50% t +0.28 ❌` (❌, n = 122)
    - 2ª metade: `XLP⊥ -1.28% t -0.13 ❌ · XLK⊥ +7.05% t +0.87 ❌` (❌, n = 122)

## Leitura

**Antes de ler qualquer célula: em h = 10 o critério fraco marca 13 das 14 células, e o da D19c marca 3.** Com janelas sobrepostas e n ~ 200, trocar de sinal entre as metades é barato — um teste que reprova quase todo mundo não separa candidato de ruído. **Só o critério forte é lido abaixo nessa régua.**

**A D19c se reproduz aqui?** Na régua dela (OLS h = 10, critério forte), a discordância contra o livro direcional **gira de sinal** entre as metades — é o achado da D19c, reencontrado com o livro de duas pernas em vez de só o SPY.

**O NÍVEL (`discordância (o sinal da 3.1)`) contra o livro NEUTRO** — a célula que separa as duas explicações — G2: 🛑 gira · OLS: 🛑 gira.


**As marginais do 2×2 — quantas células giram, por régua:**

| corte | G2 (fraco) | OLS (forte) |
|---|---|---|
| nível | **5 de 6** | **3 de 6** |
| incremento | **2 de 8** | **0 de 8** |
| SPY direcional (livro da 3.1) | **4 de 7** | **1 de 7** |
| spread neutro (livro da sleeve) | **3 de 7** | **2 de 7** |

⚠️ **As exceções, nomeadas:** no G2 (critério fraco) o grupo de incremento não sai limpo — giram `Δ discordância (k = 5) × spread neutro` · `Δp k = 3 (o sinal da sleeve) × SPY direcional`. Nenhuma delas é a sleeve no livro dela, mas o total da marginal não deve ser lido como zero.

➡ **Nenhuma das duas explicações pré-registradas.** O giro não se concentra num livro (aparece nos dois), logo não é o canal de direção — cai a explicação (1). E não aparece no sinal de INCREMENTO em livro nenhum, logo não é "o mercado M4 recessão EUA 2025 é instável" — cai a explicação (2), que exigiria a sleeve girando também.

**O eixo é a TRANSFORMAÇÃO do sinal.** O NÍVEL da crença tem relação instável com os retornos; o INCREMENTO não. Isso tem mecanismo, e ele é banal: um nível que sobe e desce ao longo da amostra fica correlacionado com o que o mercado fez em cada regime, e o coeficiente ajustado vira uma afirmação sobre o regime, não sobre o mecanismo. Diferenciar remove isso por construção.

**Consequência para a candidata M4 recessão EUA 2025:** a objeção publicada contra este mercado mede o NÍVEL e a sleeve lê o INCREMENTO — as duas medições estão certas e não se contradizem. A objeção deixa de valer contra a sleeve e passa a ser uma **limitação a declarar**: neste mercado, qualquer view que leia NÍVEL está medindo regime.

**De onde vem o giro do nível — o Polymarket:** SPY direcional — G2: 🛑 gira, OLS: não gira · spread neutro — G2: 🛑 gira, OLS: 🛑 gira.
**De onde vem o giro do nível — a curva de juros:** SPY direcional — G2: 🛑 gira, OLS: não gira · spread neutro — G2: não gira, OLS: não gira.

**A sleeve (Δp k = 3, livro neutro) fora da régua em que foi aprovada:** no G2 as metades saem ✅✅ (giro: não); na régua da D19c (h = 10) o veredito da amostra inteira é ❌ e o giro forte é não.
**A sleeve (Δp k = 5, livro neutro) fora da régua em que foi aprovada:** no G2 as metades saem ✅✅ (giro: não); na régua da D19c (h = 10) o veredito da amostra inteira é ❌ e o giro forte é não.
**A sleeve (Δp k = 10, livro neutro) fora da régua em que foi aprovada:** no G2 as metades saem ✅✅ (giro: não); na régua da D19c (h = 10) o veredito da amostra inteira é ❌ e o giro forte é não.

⚠️ **Limitação que sai junto, e não é pequena:** em k = 3, 5, 10 a sleeve **reprova a premissa em h = 10** na amostra inteira. Ela é estável, mas a vantagem que o G2 mede vive na janela de **1 pregão** e não se estende a dez. Estabilidade não é o mesmo que alcance, e o G4 — quando rodar — vai medir a segunda coisa, não a primeira.

**O que isto NÃO diz:** nada sobre P&L (o G4 continua sem rodar para nada), e nada sobre comparações múltiplas — as ~200 células da D27 seguem sem correção. **Este mercado não tem irmão** (D18d), então o corte em metades é o único fora-da-amostra que ele pode ter.

A correlação de **+1.000** entre as duas séries de `p` **confirma** que a escolha da construção do `p` não é o que separa as duas medições.

