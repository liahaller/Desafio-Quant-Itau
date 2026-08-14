# Curva orçamento → excesso — sensibilidade da camada tática

> Gerado por `scripts/curva_orcamento.py`. A camada tática **não entra no v1** (decisão 12c): esta tabela é sensibilidade para o relatório, **não** proposta de orçamento. Escolher a linha de maior excesso é exatamente o overfit que o protocolo anti-overfit da seção 10 proíbe.

- janela: **2025-02-10 a 2026-08-06** (374 pregões)
- configuração de referência: teto **no tilt = 1**, custo **2.0 bps/lado**
- linha de base (tática desligada): excesso **+3.04 pp**, sharpe 1.18, giro 0.396

| família | orçamento | dias com overlay | excesso | Δ vs. desligada | sharpe | giro diário | custo pago |
|---|---|---|---|---|---|---|---|
| só prêmio | 1% | 329 | +3.04 pp | -0.00 pp | 1.18 | 0.396 | 2.96% |
| só prêmio | 2% | 329 | +3.04 pp | -0.00 pp | 1.18 | 0.396 | 2.96% |
| só prêmio | 5% | 329 | +3.04 pp | -0.00 pp | 1.18 | 0.396 | 2.96% |
| só prêmio | 10% | 329 | +3.04 pp | -0.01 pp | 1.18 | 0.396 | 2.96% |
| só drift | 1% | 346 | +3.08 pp | +0.03 pp | 1.18 | 0.397 | 2.97% |
| só drift | 2% | 346 | +3.11 pp | +0.07 pp | 1.18 | 0.397 | 2.97% |
| só drift | 5% | 346 | +3.21 pp | +0.16 pp | 1.19 | 0.398 | 2.98% |
| só drift | 10% | 346 | +3.37 pp | +0.32 pp | 1.19 | 0.399 | 2.99% |
| prêmio + drift | 1% | 348 | +3.08 pp | +0.03 pp | 1.18 | 0.397 | 2.97% |
| prêmio + drift | 2% | 348 | +3.11 pp | +0.06 pp | 1.18 | 0.397 | 2.97% |
| prêmio + drift | 5% | 348 | +3.20 pp | +0.16 pp | 1.19 | 0.398 | 2.98% |
| prêmio + drift | 10% | 348 | +3.36 pp | +0.31 pp | 1.19 | 0.399 | 2.99% |

## Leitura

**A faixa inteira da grade cabe entre -0.01 pp e +0.32 pp** contra a tática desligada. O extremo favorável é `só drift` com orçamento de 10%, o desfavorável é `só prêmio` com 10%.

**O Δ é monótono no orçamento dentro de cada família — e é esse o argumento para não ligar.** Cada overlay é um deslocamento de peso fixo vezes o orçamento, então o efeito escala com ele e a grade **não tem ótimo interior**: a melhor linha é sempre a da ponta, e a ponta é onde eu parei de varrer, não onde algo mudou. Uma tabela assim não seleciona orçamento — só informa o sinal do overlay na janela. Escolher a linha de cima seria calibrar tamanho contra o resultado de 374 pregões, sem rodada seguinte para desmentir.

**Sinal por família na janela** (o que a tabela de fato mede): `prêmio + drift` ajuda (+0.03 a +0.31 pp); `só drift` ajuda (+0.03 a +0.32 pp); `só prêmio` atrapalha (-0.01 a -0.00 pp). Sinal medido em uma janela e uma configuração de teto não é evidência de que a tática funciona — é o insumo que faltava para decidir sem opinião.

**O que isto NÃO decide:** o orçamento. A decisão registrada (12c) é entregar o v1 com a camada tática desligada; a implementação fica no repositório, testada, para quem retomar depois da entrega.

