# Curva orçamento → excesso — sensibilidade da camada tática

> Gerado por `scripts/curva_orcamento.py`. A camada tática **não entra no v1** (decisão 12c): esta tabela é sensibilidade para o relatório, **não** proposta de orçamento. Escolher a linha de maior excesso é exatamente o overfit que o protocolo anti-overfit da seção 10 proíbe.

- janela: **2025-02-10 a 2026-08-06** (374 pregões)
- configuração de referência: teto **no tilt = 1**, custo **2.0 bps/lado**
- linha de base (tática desligada): excesso **+6.24 pp**, sharpe 1.27, giro 0.274

| família | orçamento | dias com overlay | excesso | Δ vs. desligada | sharpe | giro diário | custo pago |
|---|---|---|---|---|---|---|---|
| só prêmio | 1% | 13 | +6.24 pp | -0.00 pp | 1.27 | 0.274 | 2.05% |
| só prêmio | 2% | 13 | +6.23 pp | -0.01 pp | 1.27 | 0.274 | 2.05% |
| só prêmio | 5% | 13 | +6.22 pp | -0.02 pp | 1.27 | 0.274 | 2.05% |
| só prêmio | 10% | 13 | +6.21 pp | -0.04 pp | 1.27 | 0.274 | 2.05% |
| só drift | 1% | 115 | +6.32 pp | +0.07 pp | 1.28 | 0.274 | 2.05% |
| só drift | 2% | 115 | +6.39 pp | +0.15 pp | 1.28 | 0.274 | 2.05% |
| só drift | 5% | 115 | +6.61 pp | +0.37 pp | 1.28 | 0.275 | 2.06% |
| só drift | 10% | 115 | +6.98 pp | +0.74 pp | 1.29 | 0.276 | 2.06% |
| prêmio + drift | 1% | 126 | +6.31 pp | +0.07 pp | 1.28 | 0.274 | 2.05% |
| prêmio + drift | 2% | 126 | +6.38 pp | +0.14 pp | 1.28 | 0.274 | 2.05% |
| prêmio + drift | 5% | 126 | +6.59 pp | +0.35 pp | 1.28 | 0.275 | 2.06% |
| prêmio + drift | 10% | 126 | +6.94 pp | +0.70 pp | 1.29 | 0.276 | 2.06% |

## Leitura

**A faixa inteira da grade cabe entre -0.04 pp e +0.74 pp** contra a tática desligada. O extremo favorável é `só drift` com orçamento de 10%, o desfavorável é `só prêmio` com 10%.

**O Δ é monótono no orçamento dentro de cada família — e é esse o argumento para não ligar.** Cada overlay é um deslocamento de peso fixo vezes o orçamento, então o efeito escala com ele e a grade **não tem ótimo interior**: a melhor linha é sempre a da ponta, e a ponta é onde eu parei de varrer, não onde algo mudou. Uma tabela assim não seleciona orçamento — só informa o sinal do overlay na janela. Escolher a linha de cima seria calibrar tamanho contra o resultado de 374 pregões, sem rodada seguinte para desmentir.

**Sinal por família na janela** (o que a tabela de fato mede): `prêmio + drift` ajuda (+0.07 a +0.70 pp); `só drift` ajuda (+0.07 a +0.74 pp); `só prêmio` atrapalha (-0.04 a -0.00 pp). Sinal medido em uma janela e uma configuração de teto não é evidência de que a tática funciona — é o insumo que faltava para decidir sem opinião.

**O que isto NÃO decide:** o orçamento. A decisão registrada (12c) é entregar o v1 com a camada tática desligada; a implementação fica no repositório, testada, para quem retomar depois da entrega.

