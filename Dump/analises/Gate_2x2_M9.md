# M4 recessão — a contradição com a D19c, em 2×2

> Gerado por `scripts/gate_recessao_2x2.py`. **Mede; não decide.** Nenhuma premissa nova: os dois livros, a discordância, o `Δp`, as pernas `⊥` e a partição em metades são importados por referência dos artefatos anteriores. O que este artefato acrescenta é o **cruzamento** entre o sinal de um e o livro do outro.

- janela: **2025-02-10 a 2026-08-06** (374 pregões); δ e Σ os mesmos do v1 (D7/D8)
- livro da 3.1: `{'SPY': -1, 'TLT': 1}` — *mecanismo partidário, espelho do M5. ⚠️ é exatamente o mecanismo que a 2.4 mediu como NÃO reproduzindo fora da amostra*
- livro da sleeve: `{'XLP⊥': 1, 'XLK⊥': -1}` — *mecanismo partidário, espelho do M5. ⚠️ é o mecanismo que a 2.4 mediu como NÃO reproduzindo fora da amostra*
- correlação entre as duas séries de `p` (a normalizada que a 3.1 lê × o midpoint cru que a sleeve lê, 268 pregões comuns): **+1.000**

## As quatro células, e as três que faltavam

| | livro: SPY direcional | livro: spread neutro |
|---|---|---|
| **sinal: nível (discordância)** | a **D19c** | ⬅ célula nova |
| **sinal: incremento (Δp)** | ⬅ célula nova | a **D27** |

As parcelas da discordância (`z(poly)` e `z(−spread)` sozinhas) e o `Δ` da própria discordância entram como linhas extras: sem elas não dá para dizer se um giro veio do Polymarket ou da curva de juros.

## Tabela

| régua                             | sinal                         | livro                           | inteira   | 1ª metade   | 2ª metade   | gira (fraco)   | gira (D19c: |t| > 2 nas duas)   |   n (inteira) |
|:----------------------------------|:------------------------------|:--------------------------------|:----------|:------------|:------------|:---------------|:--------------------------------|--------------:|
| G2 (μ encolhido, janela 1 pregão) | z(p) — o NÍVEL da crença      | SPY direcional (livro da 3.1)   | ❌        | ✅          | ❌          | 🛑 SIM         | —                               |           194 |
| G2 (μ encolhido, janela 1 pregão) | z(p) — o NÍVEL da crença      | spread neutro (livro da sleeve) | ✅        | ✅          | ❌          | 🛑 SIM         | —                               |           194 |
| G2 (μ encolhido, janela 1 pregão) | Δp k = 20 (o sinal da sleeve) | SPY direcional (livro da 3.1)   | ❌        | ❌          | ❌          | não            | —                               |           204 |
| G2 (μ encolhido, janela 1 pregão) | Δp k = 20 (o sinal da sleeve) | spread neutro (livro da sleeve) | ✅        | ✅          | ✅          | não            | —                               |           204 |
| OLS (h = 10, a régua da D19c)     | z(p) — o NÍVEL da crença      | SPY direcional (livro da 3.1)   | ✅        | ✅          | ❌          | 🛑 SIM         | 🛑 SIM                          |           190 |
| OLS (h = 10, a régua da D19c)     | z(p) — o NÍVEL da crença      | spread neutro (livro da sleeve) | ✅        | ✅          | ❌          | 🛑 SIM         | 🛑 SIM                          |           190 |
| OLS (h = 10, a régua da D19c)     | Δp k = 20 (o sinal da sleeve) | SPY direcional (livro da 3.1)   | ❌        | ❌          | ❌          | não            | não                             |           215 |
| OLS (h = 10, a régua da D19c)     | Δp k = 20 (o sinal da sleeve) | spread neutro (livro da sleeve) | ✅        | ✅          | ❌          | 🛑 SIM         | não                             |           215 |

**Duas colunas de giro, e a diferença entre elas é o ponto.** O critério FRACO é só a troca de sinal; o FORTE é o da D19c palavra por palavra — *as duas metades significantes e apontando para lados opostos*. No G2 só existe o fraco: o μ encolhido não publica `t` em artefato nenhum deste projeto, e inventar um aqui daria à célula nova um critério que as células já publicadas não tiveram.

### Detalhe por perna

- **G2 (μ encolhido, janela 1 pregão)** · z(p) — o NÍVEL da crença · SPY direcional (livro da 3.1)
    - inteira: `SPY -1.69 ✅ · TLT -1.97 ❌` (❌, n = 194)
    - 1ª metade: `SPY -1.79 ✅ · TLT +0.02 ✅` (✅, n = 97)
    - 2ª metade: `SPY -0.47 ✅ · TLT -2.18 ❌` (❌, n = 97)
- **G2 (μ encolhido, janela 1 pregão)** · z(p) — o NÍVEL da crença · spread neutro (livro da sleeve)
    - inteira: `XLP⊥ +1.57 ✅ · XLK⊥ -0.18 ✅` (✅, n = 194)
    - 1ª metade: `XLP⊥ +3.38 ✅ · XLK⊥ -1.80 ✅` (✅, n = 97)
    - 2ª metade: `XLP⊥ -0.69 ❌ · XLK⊥ +0.54 ❌` (❌, n = 97)
- **G2 (μ encolhido, janela 1 pregão)** · Δp k = 20 (o sinal da sleeve) · SPY direcional (livro da 3.1)
    - inteira: `SPY -0.40 ✅ · TLT -1.12 ❌` (❌, n = 204)
    - 1ª metade: `SPY -0.52 ✅ · TLT -0.24 ❌` (❌, n = 108)
    - 2ª metade: `SPY -0.05 ✅ · TLT -1.10 ❌` (❌, n = 96)
- **G2 (μ encolhido, janela 1 pregão)** · Δp k = 20 (o sinal da sleeve) · spread neutro (livro da sleeve)
    - inteira: `XLP⊥ +2.23 ✅ · XLK⊥ -2.62 ✅` (✅, n = 204)
    - 1ª metade: `XLP⊥ +2.83 ✅ · XLK⊥ -2.85 ✅` (✅, n = 108)
    - 2ª metade: `XLP⊥ +0.38 ✅ · XLK⊥ -0.98 ✅` (✅, n = 96)
- **OLS (h = 10, a régua da D19c)** · z(p) — o NÍVEL da crença · SPY direcional (livro da 3.1)
    - inteira: `SPY -0.24% t -1.57 ✅ · TLT +0.11% t +1.07 ✅` (✅, n = 190)
    - 1ª metade: `SPY -0.26% t -2.45 ✅ · TLT +0.25% t +2.81 ✅` (✅, n = 97)
    - 2ª metade: `SPY -0.30% t -0.38 ✅ · TLT -1.63% t -3.87 ❌` (❌, n = 93)
- **OLS (h = 10, a régua da D19c)** · z(p) — o NÍVEL da crença · spread neutro (livro da sleeve)
    - inteira: `XLP⊥ +0.71% t +3.71 ✅ · XLK⊥ -0.08% t -0.43 ✅` (✅, n = 190)
    - 1ª metade: `XLP⊥ +0.99% t +4.93 ✅ · XLK⊥ -0.26% t -2.01 ✅` (✅, n = 97)
    - 2ª metade: `XLP⊥ -1.91% t -2.97 ❌ · XLK⊥ +1.16% t +1.21 ❌` (❌, n = 93)
- **OLS (h = 10, a régua da D19c)** · Δp k = 20 (o sinal da sleeve) · SPY direcional (livro da 3.1)
    - inteira: `SPY -3.22% t -1.01 ✅ · TLT -5.96% t -2.40 ❌` (❌, n = 215)
    - 1ª metade: `SPY -1.35% t -0.56 ✅ · TLT -5.84% t -2.22 ❌` (❌, n = 109)
    - 2ª metade: `SPY -13.00% t -1.35 ✅ · TLT -6.88% t -1.10 ❌` (❌, n = 106)
- **OLS (h = 10, a régua da D19c)** · Δp k = 20 (o sinal da sleeve) · spread neutro (livro da sleeve)
    - inteira: `XLP⊥ +9.25% t +2.19 ✅ · XLK⊥ -10.20% t -2.83 ✅` (✅, n = 215)
    - 1ª metade: `XLP⊥ +15.08% t +3.50 ✅ · XLK⊥ -8.65% t -3.14 ✅` (✅, n = 109)
    - 2ª metade: `XLP⊥ -20.11% t -1.87 ❌ · XLK⊥ -18.06% t -1.64 ✅` (❌, n = 106)

## Leitura

**Antes de ler qualquer célula: em h = 10 o critério fraco marca 3 das 4 células, e o da D19c marca 2.** Com janelas sobrepostas e n ~ 200, trocar de sinal entre as metades é barato — um teste que reprova quase todo mundo não separa candidato de ruído. **Só o critério forte é lido abaixo nessa régua.**

**O NÍVEL (`z(p) — o NÍVEL da crença`) contra o livro NEUTRO** — a célula que separa as duas explicações — G2: 🛑 gira · OLS: 🛑 gira.


**As marginais do 2×2 — quantas células giram, por régua:**

| corte | G2 (fraco) | OLS (forte) |
|---|---|---|
| nível | **2 de 2** | **2 de 2** |
| incremento | **0 de 2** | **0 de 2** |
| SPY direcional (livro da 3.1) | **1 de 2** | **1 de 2** |
| spread neutro (livro da sleeve) | **1 de 2** | **1 de 2** |

➡ **Nenhuma das duas explicações pré-registradas.** O giro não se concentra num livro (aparece nos dois), logo não é o canal de direção — cai a explicação (1). E não aparece no sinal de INCREMENTO em livro nenhum, logo não é "o mercado M9 Câmara é instável" — cai a explicação (2), que exigiria a sleeve girando também.

**O eixo é a TRANSFORMAÇÃO do sinal.** O NÍVEL da crença tem relação instável com os retornos; o INCREMENTO não. Isso tem mecanismo, e ele é banal: um nível que sobe e desce ao longo da amostra fica correlacionado com o que o mercado fez em cada regime, e o coeficiente ajustado vira uma afirmação sobre o regime, não sobre o mecanismo. Diferenciar remove isso por construção.

**Consequência para a candidata M9 Câmara:** a objeção publicada contra este mercado mede o NÍVEL e a sleeve lê o INCREMENTO — as duas medições estão certas e não se contradizem. A objeção deixa de valer contra a sleeve e passa a ser uma **limitação a declarar**: neste mercado, qualquer view que leia NÍVEL está medindo regime.


**A sleeve (Δp k = 20, livro neutro) fora da régua em que foi aprovada:** no G2 as metades saem ✅✅ (giro: não); na régua da D19c (h = 10) o veredito da amostra inteira é ✅ e o giro forte é não.

**O que isto NÃO diz:** nada sobre P&L (o G4 continua sem rodar para nada), e nada sobre comparações múltiplas — as ~200 células da D27 seguem sem correção. O teste de **mercado irmão** deste mercado é assunto do `Gate_mercados_irmaos.md`, não deste artefato.

