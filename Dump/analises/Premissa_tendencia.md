# Premissa da tendência — o sinal acumulado é negociável?

> Gerado por `scripts/premissa_tendencia.py`. **Mede; não decide.**

O `Premissa_G1.md` mostrou o sinal do poly crescendo com o horizonte e derrubou o veredito da D17 como regra geral. Crescer, porém, não é bastar: **tendência** (movimentos se encadeiam, informação disponível antes) e **convergência** (a probabilidade caminha para o desfecho à medida que a data chega) produzem exatamente a mesma acumulação, e só a primeira vira sleeve.

- **VR** = Var(Δk) ÷ (k · Var(Δ1)). Passeio aleatório = 1. Acima de 1 os incrementos se somam; não diz se por tendência ou por deriva.
- **ρ demeanado** = autocorrelação de lag 1 dos incrementos NÃO sobrepostos, com a deriva tirada pela média expansiva do próprio sinal (D9/D7.4, só passado). **É a parte ex-ante — a única negociável.**
- **ρ bruto** = a mesma coisa com a deriva dentro. A distância entre os dois é o tamanho da convergência.
- `n` = pares de incrementos que sobraram. Em k grande ele desaba (210 pregões ÷ 20 = 10 janelas), e sem ele o ρ é ilegível.

## Variance ratio — os incrementos se somam?

| mercado                                 | família                |   k=1 | k=2   | k=3   | k=5   | k=10   | k=20   |
|:----------------------------------------|:-----------------------|------:|:------|:------|:------|:-------|:-------|
| C1a M3 trajetória do Fed (nº de cortes) | Fed · controle D17     |     1 | 1.05  | 1.12  | 1.11  | 1.18   | 0.97   |
| C1b reunião do FOMC (E_poly em bps)     | Fed · controle D17     |     1 | 0.96  | 0.96  | 0.94  | 0.94   | 0.71   |
| CPI mensal (E_poly)                     | CPI                    |     1 | 0.89  | 0.88  | 0.85  | 0.90   | 0.98   |
| M4 recessão EUA 2025                    | binário (nunca medido) |     1 | 0.74  | 0.84  | 0.88  | 0.89   | 0.84   |
| M5 Trump 2024                           | binário (nunca medido) |     1 | 0.74  | 0.51  | 0.38  | 0.37   | 0.40   |
| M6 tarifas China                        | binário (nunca medido) |     1 | 0.63  | 0.47  | 0.39  | —      | —      |
| M7 ação militar Irã (jun/2025)          | binário (nunca medido) |     1 | 1.10  | 1.09  | 1.38  | 1.13   | 0.56   |
| M7 ataque ao Irã (fev/2026)             | binário (nunca medido) |     1 | 0.97  | 0.77  | 0.51  | 0.29   | 0.08   |
| M8 reconciliação fiscal                 | binário (nunca medido) |     1 | —     | —     | —     | —      | —      |
| M9 Câmara                               | binário (nunca medido) |     1 | 0.79  | 0.76  | 0.68  | 0.76   | 0.84   |

## ρ demeanado — sobra previsibilidade depois de tirar a deriva?

| mercado                                 | k=1                   | k=2                   | k=3                   | k=5                  | k=10                 | k=20                 |
|:----------------------------------------|:----------------------|:----------------------|:----------------------|:---------------------|:---------------------|:---------------------|
| C1a M3 trajetória do Fed (nº de cortes) | +0.02 (t +0.2, n 199) | +0.12 (t +1.2, n 102) | +0.19 (t +1.6, n 66)  | -0.12 (t -0.7, n 35) | -0.22 (t -0.9, n 19) | +0.13 (t +0.3, n 8)  |
| C1b reunião do FOMC (E_poly em bps)     | -0.08 (t -1.3, n 315) | +0.02 (t +0.3, n 166) | +0.09 (t +0.9, n 103) | -0.03 (t -0.2, n 54) | -0.22 (t -1.2, n 33) | -0.13 (t -0.5, n 15) |
| CPI mensal (E_poly)                     | -0.09 (t -1.4, n 267) | -0.09 (t -1.0, n 133) | -0.15 (t -1.4, n 82)  | +0.14 (t +0.9, n 45) | +0.10 (t +0.5, n 26) | -0.16 (t -0.5, n 12) |
| M4 recessão EUA 2025                    | -0.27 (t -4.4, n 251) | +0.06 (t +0.7, n 123) | -0.06 (t -0.5, n 81)  | -0.05 (t -0.3, n 47) | -0.07 (t -0.3, n 21) | -0.10 (t -0.3, n 10) |
| M5 Trump 2024                           | +0.20 (t +3.1, n 216) | -0.22 (t -2.4, n 107) | +0.05 (t +0.4, n 70)  | +0.15 (t +1.0, n 41) | +0.34 (t +1.5, n 19) | -0.21 (t -0.5, n 8)  |
| M6 tarifas China                        | -0.59 (t -1.5, n 6)   | — (n 2)               | — (n 0)               | — (n 0)              | — (n 0)              | — (n 0)              |
| M7 ação militar Irã (jun/2025)          | +0.28 (t +2.1, n 56)  | -0.00 (t -0.0, n 27)  | +0.65 (t +3.3, n 17)  | +0.09 (t +0.2, n 9)  | — (n 3)              | — (n 0)              |
| M7 ataque ao Irã (fev/2026)             | -0.05 (t -0.3, n 26)  | -0.58 (t -2.3, n 12)  | -0.06 (t -0.1, n 7)   | — (n 3)              | — (n 0)              | — (n 0)              |
| M8 reconciliação fiscal                 | — (n 0)               | — (n 0)               | — (n 0)               | — (n 0)              | — (n 0)              | — (n 0)              |
| M9 Câmara                               | -0.21 (t -3.3, n 242) | -0.06 (t -0.7, n 114) | +0.18 (t +1.6, n 81)  | +0.13 (t +0.9, n 49) | -0.09 (t -0.4, n 22) | +0.16 (t +0.5, n 11) |

## ρ bruto — a mesma medida com a deriva dentro

| mercado                                 | k=1   | k=2   | k=3   | k=5   | k=10   | k=20   |
|:----------------------------------------|:------|:------|:------|:------|:-------|:-------|
| C1a M3 trajetória do Fed (nº de cortes) | +0.01 | +0.12 | +0.08 | -0.21 | -0.19  | +0.07  |
| C1b reunião do FOMC (E_poly em bps)     | -0.07 | +0.02 | +0.09 | -0.03 | -0.22  | -0.07  |
| CPI mensal (E_poly)                     | -0.09 | -0.09 | -0.16 | +0.13 | +0.09  | -0.09  |
| M4 recessão EUA 2025                    | -0.26 | +0.07 | -0.05 | -0.02 | -0.02  | +0.06  |
| M5 Trump 2024                           | +0.18 | -0.26 | +0.05 | +0.14 | +0.28  | -0.32  |
| M6 tarifas China                        | -0.45 | —     | —     | —     | —      | —      |
| M7 ação militar Irã (jun/2025)          | +0.30 | +0.08 | +0.71 | +0.22 | -0.97  | —      |
| M7 ataque ao Irã (fev/2026)             | -0.04 | -0.55 | -0.35 | -0.68 | —      | —      |
| M8 reconciliação fiscal                 | —     | —     | —     | —     | —      | —      |
| M9 Câmara                               | -0.21 | -0.06 | +0.18 | +0.13 | -0.10  | +0.13  |

## Leitura

**A linha que decide é a do C1a M3 trajetória do Fed (nº de cortes)** — a única série com cobertura e dispersão ao mesmo tempo, e a única não consumida por nenhuma das quatro views vivas.

- VR: k=1: 1.00, k=2: 1.05, k=3: 1.12, k=5: 1.11, k=10: 1.18, k=20: 0.97
- ρ demeanado: k=1: ρ +0.02 (t +0.2, n 199), k=2: ρ +0.12 (t +1.2, n 102), k=3: ρ +0.19 (t +1.6, n 66), k=5: ρ -0.12 (t -0.7, n 35), k=10: ρ -0.22 (t -0.9, n 19), k=20: ρ +0.13 (t +0.3, n 8)

**Não sobra previsibilidade ex-ante em nenhum horizonte da grade** (nenhum |t| ≥ 2), e o VR fica colado em 1. Tirada a deriva, o incremento passado não informa o próximo: a série de crença do poly se comporta como passeio aleatório.

**O que isto mata: a hipótese de MOMENTUM.** A *1.2 momentum* existia por supor que a tendência sustentada da crença se encadeia — não se encadeia. Ela perde a razão de ser, e junto com a *velocidade de ajuste* (já morta em k = 1) fecha a família inteira de "ler o movimento da crença para prever o próximo movimento da crença".

**O que isto NÃO mata: o G2.** Ele pergunta outra coisa — se o sinal prevê o RETORNO dos ativos, não se ele prevê a si mesmo. Um passeio aleatório pode perfeitamente antecipar preço. E a razão de rodar o G2 num horizonte acumulado continua de pé pelo argumento do G1, que VR = 1 não desfaz: o erro de discretização no incremento fica limitado a ~1 tick por mais que `k` cresça, enquanto o movimento verdadeiro acumula. Em k ≥ 3 o G2 deixa de condicionar em arredondamento — que era exatamente o vício que matou C1a e C1b em k = 1. **O que caiu foi o motivo para ESPERAR que o G2 passe, não a legitimidade de rodá-lo.**

**Fora do M3, 7 pares chegam a |t| ≥ 2 — 4 negativos e 3 positivos**, sem sinal dominante: M4 recessão EUA 2025 k = 1 (ρ -0.27, t -4.4, n 251) · M9 Câmara k = 1 (ρ -0.21, t -3.3, n 242) · M5 Trump 2024 k = 1 (ρ +0.20, t +3.1, n 216) · M5 Trump 2024 k = 2 (ρ -0.22, t -2.4, n 107) · M7 ação militar Irã (jun/2025) k = 1 (ρ +0.28, t +2.1, n 56) · M7 ação militar Irã (jun/2025) k = 3 (ρ +0.65, t +3.3, n 17) · M7 ataque ao Irã (fev/2026) k = 2 (ρ -0.58, t -2.3, n 12).

**Onde a deriva mais pesa** (maior distância entre ρ bruto e ρ demeanado): M7 ataque ao Irã (fev/2026) em k = 3 (-0.35 → -0.06) · M4 recessão EUA 2025 em k = 20 (+0.06 → -0.10) · M6 tarifas China em k = 1 (-0.45 → -0.59). É a convergência aparecendo como se fosse tendência — e é exatamente por isso que a leitura acima usa a coluna demeanada.

**O que isto NÃO diz:** que existe (ou não) sleeve. Diz se o crescimento do sinal com o horizonte contém parte negociável. G2 (μ contra premissa declarada) e G3 (duplicação com as views vivas) continuam sendo os critérios seguintes, e nenhum módulo se escreve antes deles.

