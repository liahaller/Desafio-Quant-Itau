# Curva orçamento → excesso — sensibilidade da camada tática

> Gerado por `scripts/curva_orcamento.py`. A camada tática **não entra no v1** (decisão 12c): esta tabela é sensibilidade para o relatório, **não** proposta de orçamento. Escolher a linha de maior excesso é exatamente o overfit que o protocolo anti-overfit da seção 10 proíbe.

- janela: **2025-02-10 a 2026-08-06** (374 pregões)
- configuração de referência: teto **no tilt = 1**, custo **2.0 bps/lado**
- linha de base (tática desligada): excesso **+4.07 pp**, sharpe 1.19, giro 0.229

| família | orçamento | dias com overlay | excesso | Δ vs. desligada | sharpe | giro diário | custo pago |
|---|---|---|---|---|---|---|---|
| só prêmio | 1% | 13 | +4.05 pp | -0.02 pp | 1.19 | 0.229 | 1.71% |
| só prêmio | 2% | 13 | +4.02 pp | -0.05 pp | 1.19 | 0.229 | 1.71% |
| só prêmio | 5% | 13 | +3.95 pp | -0.13 pp | 1.19 | 0.230 | 1.72% |
| só prêmio | 10% | 13 | +3.82 pp | -0.25 pp | 1.18 | 0.231 | 1.73% |
| só drift | 1% | 115 | +4.16 pp | +0.08 pp | 1.20 | 0.229 | 1.71% |
| só drift | 2% | 115 | +4.24 pp | +0.16 pp | 1.20 | 0.229 | 1.71% |
| só drift | 5% | 115 | +4.47 pp | +0.40 pp | 1.20 | 0.230 | 1.72% |
| só drift | 10% | 115 | +4.87 pp | +0.79 pp | 1.21 | 0.231 | 1.73% |
| prêmio + drift | 1% | 126 | +4.13 pp | +0.06 pp | 1.19 | 0.229 | 1.71% |
| prêmio + drift | 2% | 126 | +4.19 pp | +0.11 pp | 1.20 | 0.229 | 1.71% |
| prêmio + drift | 5% | 126 | +4.35 pp | +0.27 pp | 1.20 | 0.231 | 1.73% |
| prêmio + drift | 10% | 126 | +4.61 pp | +0.54 pp | 1.20 | 0.233 | 1.74% |

## Leitura

**A faixa inteira da grade cabe entre -0.25 pp e +0.79 pp** contra a tática desligada. O extremo favorável é `só drift` com orçamento de 10%, o desfavorável é `só prêmio` com 10%.

**O Δ é monótono no orçamento dentro de cada família — e é esse o argumento para não ligar.** Cada overlay é um deslocamento de peso fixo vezes o orçamento, então o efeito escala com ele e a grade **não tem ótimo interior**: a melhor linha é sempre a da ponta, e a ponta é onde eu parei de varrer, não onde algo mudou. Uma tabela assim não seleciona orçamento — só informa o sinal do overlay na janela. Escolher a linha de cima seria calibrar tamanho contra o resultado de 374 pregões, sem rodada seguinte para desmentir.

**Sinal por família na janela** (o que a tabela de fato mede): `prêmio + drift` ajuda (+0.06 a +0.54 pp); `só drift` ajuda (+0.08 a +0.79 pp); `só prêmio` atrapalha (-0.25 a -0.02 pp). Sinal medido em uma janela e uma configuração de teto não é evidência de que a tática funciona — é o insumo que faltava para decidir sem opinião.

**O que isto NÃO decide:** o orçamento. A decisão registrada (12c) é entregar o v1 com a camada tática desligada; a implementação fica no repositório, testada, para quem retomar depois da entrega.

