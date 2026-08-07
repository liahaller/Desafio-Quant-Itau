# Curva orçamento → excesso — sensibilidade da camada tática

> Gerado por `scripts/curva_orcamento.py`. A camada tática **não entra no v1** (decisão 12c): esta tabela é sensibilidade para o relatório, **não** proposta de orçamento. Escolher a linha de maior excesso é exatamente o overfit que o protocolo anti-overfit da seção 10 proíbe.

- janela: **2025-02-10 a 2026-08-06** (374 pregões)
- configuração de referência: teto **no tilt = 1**, custo **2.0 bps/lado**
- linha de base (tática desligada): excesso **+2.62 pp**, sharpe 1.15, giro 0.242

| família | orçamento | dias com overlay | excesso | Δ vs. desligada | sharpe | giro diário | custo pago |
|---|---|---|---|---|---|---|---|
| só prêmio | 1% | 14 | +2.59 pp | -0.03 pp | 1.15 | 0.242 | 1.81% |
| só prêmio | 2% | 14 | +2.56 pp | -0.07 pp | 1.15 | 0.243 | 1.81% |
| só prêmio | 5% | 14 | +2.46 pp | -0.17 pp | 1.14 | 0.243 | 1.82% |
| só prêmio | 10% | 14 | +2.29 pp | -0.34 pp | 1.14 | 0.244 | 1.83% |
| só drift | 1% | 115 | +2.71 pp | +0.08 pp | 1.15 | 0.242 | 1.81% |
| só drift | 2% | 115 | +2.79 pp | +0.16 pp | 1.15 | 0.242 | 1.81% |
| só drift | 5% | 115 | +3.03 pp | +0.40 pp | 1.16 | 0.243 | 1.82% |
| só drift | 10% | 115 | +3.42 pp | +0.80 pp | 1.17 | 0.244 | 1.83% |
| prêmio + drift | 1% | 126 | +2.67 pp | +0.05 pp | 1.15 | 0.242 | 1.81% |
| prêmio + drift | 2% | 126 | +2.72 pp | +0.09 pp | 1.15 | 0.243 | 1.82% |
| prêmio + drift | 5% | 126 | +2.85 pp | +0.23 pp | 1.16 | 0.244 | 1.82% |
| prêmio + drift | 10% | 126 | +3.07 pp | +0.45 pp | 1.16 | 0.246 | 1.84% |

## Leitura

**A faixa inteira da grade cabe entre -0.34 pp e +0.80 pp** contra a tática desligada. O extremo favorável é `só drift` com orçamento de 10%, o desfavorável é `só prêmio` com 10%.

**O Δ é monótono no orçamento dentro de cada família — e é esse o argumento para não ligar.** Cada overlay é um deslocamento de peso fixo vezes o orçamento, então o efeito escala com ele e a grade **não tem ótimo interior**: a melhor linha é sempre a da ponta, e a ponta é onde eu parei de varrer, não onde algo mudou. Uma tabela assim não seleciona orçamento — só informa o sinal do overlay na janela. Escolher a linha de cima seria calibrar tamanho contra o resultado de 374 pregões, sem rodada seguinte para desmentir.

**Sinal por família na janela** (o que a tabela de fato mede): `prêmio + drift` ajuda (+0.05 a +0.45 pp); `só drift` ajuda (+0.08 a +0.80 pp); `só prêmio` atrapalha (-0.34 a -0.03 pp). Sinal medido em uma janela e uma configuração de teto não é evidência de que a tática funciona — é o insumo que faltava para decidir sem opinião.

**O que isto NÃO decide:** o orçamento. A decisão registrada (12c) é entregar o v1 com a camada tática desligada; a implementação fica no repositório, testada, para quem retomar depois da entrega.

