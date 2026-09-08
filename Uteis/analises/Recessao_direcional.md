# View 3.1 — P direcional × P neutro (D18d)

> Gerado por `scripts/view_3_1_direcional.py`. **Mede; não decide — e a entrada desta view está BLOQUEADA pela D2b/D18d.** Régua do `teste_sinal.py`: `r_P(D→D+h)` contra o `Q(D)` da própria montagem, com `r_P` começando em D+1.

- pregões medidos: **126** (discordância expansiva disponível em 186 dias)
- padronização e β **expansivos** — sem o z in sample que o `Nivel_divergencia_3_1.md` declarou como ressalva

| montagem | h = 1: coef · t · acerto | h = 5: coef · t · acerto | h = 10: coef · t · acerto | h = 21: coef · t · acerto |
|---|---|---|---|---|
| 3.1 P neutro (módulo) | -0.757 · t -1.31 · 45% | **-3.829 · t -3.37 · 51%** | **-7.442 · t -5.13 · 47%** | **-12.821 · t -6.59 · 55%** |
| 3.1 P direcional (candidata) | -0.725 · t -1.28 · 45% | **-2.805 · t -2.50 · 36%** | **-3.937 · t -3.40 · 33%** | **-2.617 · t -2.22 · 31%** |

## O que a escolha de TESE faz com o mesmo número

O Q é linear no β, então trocar o sinal do β espelha o t. A linha de cima é o β **medido no dado** ("prêmio de medo pago"); a de baixo é a **tese original** da espec (mais recessão → cíclico cai). Nenhuma das duas é recomendação — a D18d pergunta ao grupo qual tese vale, e ela tem de ser declarada **antes**.

| tese | h = 1 | h = 5 | h = 10 | h = 21 |
|---|---|---|---|---|
| β medido (prêmio de medo pago) | t -1.28 · 45% | **t -2.50 · 36%** | **t -3.40 · 33%** | **t -2.22 · 31%** |
| tese original da espec (β invertido) | t +1.28 · 55% | **t +2.50 · 64%** | **t +3.40 · 67%** | **t +2.22 · 69%** |

## Retorno do mercado contra a discordância (o sinal cru)

Sem view no meio: retorno de cada ativo em D+1..D+h contra a discordância expansiva de D. É a tabela do `Nivel_divergencia_3_1.md` refeita sem o z in sample.

| h | SPY | TIP | TLT | XLE | XLF | XLK | XLP | XLU | XLV |
|---|---|---|---|---|---|---|---|---|---|
| 1 | -0.05% | -0.01% | -0.02% | -0.03% | +0.04% | -0.12% | +0.03% | -0.02% | +0.06% |
| 5 | -0.20% | -0.04% | -0.05% | +0.00% | +0.25% | **-0.54%** | +0.17% | -0.08% | **+0.40%** |
| 10 | **-0.30%** | -0.06% | -0.05% | +0.22% | +0.17% | **-0.78%** | **+0.59%** | -0.26% | +0.39% |
| 21 | -0.20% | **-0.22%** | **-0.54%** | **+1.62%** | -0.04% | **-0.74%** | **+1.86%** | **-0.79%** | -0.17% |

> Janelas sobrepostas para h > 1: o |t| segue otimista, como no artefato original. O que muda aqui é só o z e o β, que deixaram de olhar o futuro.


## 🛑 Estabilidade do coeficiente dentro da própria amostra

**É a linha que a D18d precisa antes de discutir tese.** O mesmo coeficiente de SPY em h = 10, medido em pedaços da única amostra que existe (não há segundo mercado de recessão, então não há teste fora da amostra possível):

| recorte | pregões | período | coef SPY (h = 10) | t |
|---|---|---|---|---|
| amostra inteira | 186 | 2025-04-04 a 2025-12-31 | **+0.40%** | +3.22 |
| 1ª metade | 93 | 2025-04-04 a 2025-08-18 | **+0.97%** | +6.52 |
| 2ª metade | 93 | 2025-08-19 a 2025-12-31 | **-0.35%** | -2.27 |
| dias com β (tabela acima) | 126 | 2025-07-02 a 2025-12-31 | **-0.30%** | -2.53 |

> O sinal que a re-declaração de tese da D18d se apoiaria é o coeficiente desta coluna. Se ele **troca de sinal entre as metades**, a pergunta "qual tese vale" fica sem base medida — não porque a tese seja errada, mas porque a amostra não a sustenta em nenhuma direção.

