# Camada tática reconstruída — duas sleeves de drift, sem orçamento

> Gerado por `scripts/tatica_reconstruida.py`. **Mede; não decide** — a entrada da camada é decisão do grupo. Sem grade de orçamento **de propósito**: o tamanho sai de `inv(δΣ)·μ`, então não existe parâmetro para escolher olhando a coluna de excesso (era a armadilha da 12c).

- janela: **2025-02-10 a 2026-08-06** (374 pregões)
- teto **no tilt = 1**, custo **2.0 bps/lado**, δ = 3 (D7, observável), janela do drift = 15 dias úteis (Neuhierl-Weber)

| configuração | dias com sleeve | excesso | Δ vs. desligada | sharpe | giro diário | Σ\|dw\| mediano | P&L da sleeve sozinha |
|---|---|---|---|---|---|---|---|
| desligada (v1, 12c) | 0 | +2.62 pp | +0.00 pp | 1.15 | 0.242 | — | — |
| só drift FOMC (poly) | 158 | -3.06 pp | -5.68 pp | 0.99 | 0.266 | 72.72 | -35.23 pp |
| só drift CPI | 150 | +0.39 pp | -2.23 pp | 1.09 | 0.240 | 6.42 | -5.31 pp |
| as duas sleeves | 260 | -4.18 pp | -6.80 pp | 0.96 | 0.264 | 40.05 | -40.55 pp |

## A surpresa que as sleeves condicionam

Distribuição do sinal que dá a DIREÇÃO do tilt. É aqui que a sleeve do FOMC morre, e o motivo não é de modelagem.

| sleeve | eventos | mediana \|surpresa\| | máx \|surpresa\| | positivas | negativas |
|---|---|---|---|---|---|
| fomc | 17 | 0.52 bps | 5.34 bps | 13 | 4 |
| cpi | 14 | 1.00 bps | 8.00 bps | 6 | 6 |

## O μ que dimensiona cada sleeve

Retorno diário médio da janela do drift, por unidade de direção da surpresa, estimado com TODOS os eventos fechados da amostra. É o sanity check de sinal: o backtest reestima este μ a cada dia, só com o que já fechou.

| sleeve | eventos com surpresa | eventos no μ | livro | μ (bps/dia) |
|---|---|---|---|---|
| fomc | 17 | 17 | SPY + TLT | SPY +4.91 · TLT +1.37 |
| cpi | 12 | 12 | TIP + TLT | TIP +0.21 · TLT +1.31 |

## Leitura

**As duas sleeves perdem dinheiro por conta própria, e não é o teto.** A coluna `P&L da sleeve sozinha` soma `dw · r` no dw PEDIDO, antes de qualquer corte — se ela é negativa, a sleeve não está sendo espremida pelo teto, está errando. Ela é negativa nas duas (pior: -40.55 pp).

**Mecanismo da sleeve do FOMC, e ele é uma descoberta sobre o dado, não sobre o modelo:** o Polymarket ACERTA a decisão do Fed quase na mosca. A surpresa é a decisão realizada menos o `E_poly` da véspera, e a tabela acima mostra que ela vive na casa de 1 bp — ordem de grandeza do ruído de discretização da própria PMF. Uma sleeve que toma direção pelo SINAL desse resíduo está condicionando em ruído, e nenhum ajuste de tamanho conserta isso. É o oposto do problema da 12c: lá faltava âncora para o tamanho, aqui falta sinal para a direção.

**Mecanismo da sleeve do CPI:** a surpresa (Δ breakeven no dia) é balanceada em sinal, mas o μ estimado diz que depois de surpresa inflacionária o TLT (nominal) anda MAIS que o TIP (indexado) — contrário à premissa que justifica o livro. Mesma classe de inversão da view transversal (15f) e da B em proxy (15g).

**O que isto NÃO diz:** que a camada tática é inviável. Diz que estas duas sleeves, com este dado, não pagam o espaço que ocupam. A âncora de tamanho sem parâmetro (`inv(δΣ)·μ` com encolhimento pela dispersão) sobrevive ao teste e fica disponível para qualquer sleeve futura — foi ela que permitiu medir sem calibrar nada contra o resultado.

