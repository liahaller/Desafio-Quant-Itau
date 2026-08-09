# Curva banda de não-negociação — o giro do H = 1 dia é ruído?

> Gerado por `scripts/curva_banda.py`. **A banda não está ligada no v1** (`banda=None`): o nível é threshold do modelo e vem de decisão humana (regra 6 do `CLAUDE.md`). Esta tabela **mede e reporta** — nenhuma linha é proposta.

- janela: **2025-02-10 a 2026-08-06** (374 pregões)
- configuração de referência: teto **no tilt = 1**, custo **2.0 bps/lado**, views 2.2 e 2.3, camada tática desligada (12c)
- banda **por ativo**: Δw abaixo dela não é executado, e o Δw grande vai inteiro — não é imposto sobre o trade, é filtro de ruído

| banda | giro diário | desfeito em 1–2 pregões | pernas paradas | breakeven | custo pago | excesso × SPY | sharpe | Σ\|w\| |
|---|---|---|---|---|---|---|---|---|
| **0 (v1)** | 0.229 | 0.367 | 1% | 39.18 bps | 1.71% | +4.07 pp | 1.19 | 1.93 |
| 0.10% | 0.228 | 0.366 | 56% | 39.32 bps | 1.70% | +4.06 pp | 1.19 | 1.93 |
| 0.25% | 0.226 | 0.365 | 69% | 39.53 bps | 1.69% | +3.99 pp | 1.19 | 1.93 |
| 0.50% | 0.224 | 0.363 | 78% | 39.97 bps | 1.68% | +4.10 pp | 1.19 | 1.93 |
| 1.00% | 0.221 | 0.360 | 83% | 40.48 bps | 1.66% | +4.16 pp | 1.20 | 1.93 |
| 2.50% | 0.216 | 0.358 | 88% | 41.38 bps | 1.61% | +4.07 pp | 1.20 | 1.93 |
| 5.00% | 0.207 | 0.356 | 91% | 41.94 bps | 1.55% | +2.92 pp | 1.16 | 1.92 |

## Leitura

**Ponto de partida (v1, sem banda):** giro diário **0.229**, com **36.7%** dele desfeito em 1–2 pregões, e custo de breakeven de **39.18 bps por lado** contra os 2.0 bps premissados — **20× de folga**, que é o número a ter em mente antes de discutir banda: o custo teria de subir uma ordem de grandeza para virar o sinal.

**A banda corta giro:** de 0.229 a 0.207 (9% a menos) na ponta da grade, monotonicamente — na maior banda, 91% dos pares (dia × ativo) não negociam.

**O giro está concentrado em poucas pernas grandes.** A banda mais fina da grade (0.10%) já impede **56%** dos pares (dia × ativo) de negociar e ainda assim corta só **0.4%** do giro — ou seja, não existe uma cauda de trade miúdo a filtrar: quase todo o giro do v1 está em poucas pernas grandes, que a banda deixa passar inteiras por construção.

**Mas cortar giro não é o teste — o teste é a reversão.** Ela cai de 0.367 para 0.356 (-0.011). O giro que a banda tira é desproporcionalmente o que se desfazia: é ruído sendo pago a 2 bps a volta, e a banda ataca o mecanismo certo.

**Custo de breakeven:** vai de 39.18 bps a 41.94 bps (+2.76); o máximo da grade é **41.94 bps**, na banda de 5.00%. A folga contra os 2 bps premissados aumenta com a banda.

**Excesso × SPY:** +4.07 pp sem banda, faixa de +2.92 a +4.16 pp na grade (Δ de -1.15 a +0.09 pp). O sinal do resultado não muda em nenhuma banda da grade.

**O que isto NÃO decide:** o nível da banda. O excesso **não** é monótono na grade — ele oscila e o máximo cai numa banda interior (1.00%, +4.16 pp). É exatamente a tabela que tenta o olho a escolher a linha de maior número, e é o que o protocolo anti-overfit da seção 10 proíbe: com a reversão parada, a oscilação do excesso não tem mecanismo por trás. Se a banda entrar, o nível se escolhe pela **reversão e pelo breakeven** — as duas primeiras colunas —, junto com o teto, e uma vez só.

