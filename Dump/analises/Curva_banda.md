# Curva banda de não-negociação — o giro do H = 1 dia é ruído?

> Gerado por `scripts/curva_banda.py`. **A banda não está ligada no v1** (`banda=None`): o nível é threshold do modelo e vem de decisão humana (regra 6 do `CLAUDE.md`). Esta tabela **mede e reporta** — nenhuma linha é proposta.

- janela: **2025-02-10 a 2026-08-06** (374 pregões)
- configuração de referência: teto **no tilt = 1**, custo **2.0 bps/lado**, views 2.2 e 2.3, camada tática desligada (12c)
- banda **por ativo**: Δw abaixo dela não é executado, e o Δw grande vai inteiro — não é imposto sobre o trade, é filtro de ruído

| banda | giro diário | desfeito em 1–2 pregões | pernas paradas | breakeven | custo pago | excesso × SPY | sharpe | Σ\|w\| |
|---|---|---|---|---|---|---|---|---|
| **0 (v1)** | 0.242 | 0.363 | 1% | 35.89 bps | 1.81% | +2.62 pp | 1.15 | 1.93 |
| 0.10% | 0.241 | 0.363 | 55% | 36.01 bps | 1.81% | +2.61 pp | 1.15 | 1.93 |
| 0.25% | 0.240 | 0.361 | 69% | 36.19 bps | 1.79% | +2.52 pp | 1.15 | 1.93 |
| 0.50% | 0.238 | 0.360 | 77% | 36.52 bps | 1.78% | +2.59 pp | 1.15 | 1.93 |
| 1.00% | 0.235 | 0.357 | 82% | 36.99 bps | 1.76% | +2.68 pp | 1.15 | 1.93 |
| 2.50% | 0.229 | 0.356 | 87% | 37.80 bps | 1.72% | +2.67 pp | 1.15 | 1.93 |
| 5.00% | 0.220 | 0.354 | 90% | 38.48 bps | 1.65% | +1.70 pp | 1.12 | 1.91 |

## Leitura

**Ponto de partida (v1, sem banda):** giro diário **0.242**, com **36.3%** dele desfeito em 1–2 pregões, e custo de breakeven de **35.89 bps por lado** contra os 2.0 bps premissados — **18× de folga**, que é o número a ter em mente antes de discutir banda: o custo teria de subir uma ordem de grandeza para virar o sinal.

**A banda corta giro:** de 0.242 a 0.220 (9% a menos) na ponta da grade, monotonicamente — na maior banda, 90% dos pares (dia × ativo) não negociam.

**O giro está concentrado em poucas pernas grandes.** A banda mais fina da grade (0.10%) já impede **55%** dos pares (dia × ativo) de negociar e ainda assim corta só **0.4%** do giro — ou seja, não existe uma cauda de trade miúdo a filtrar: quase todo o giro do v1 está em poucas pernas grandes, que a banda deixa passar inteiras por construção.

**Mas cortar giro não é o teste — o teste é a reversão.** Ela cai de 0.363 para 0.354 (-0.009). Praticamente não se move: a banda tira giro dos dois tipos na mesma proporção, então não há evidência de que o giro do v1 seja ruído.

**Custo de breakeven:** vai de 35.89 bps a 38.48 bps (+2.59); o máximo da grade é **38.48 bps**, na banda de 5.00%. A folga contra os 2 bps premissados aumenta com a banda.

**Excesso × SPY:** +2.62 pp sem banda, faixa de +1.70 a +2.68 pp na grade (Δ de -0.93 a +0.06 pp). O sinal do resultado não muda em nenhuma banda da grade.

**O que isto NÃO decide:** o nível da banda. O excesso **não** é monótono na grade — ele oscila e o máximo cai numa banda interior (1.00%, +2.68 pp). É exatamente a tabela que tenta o olho a escolher a linha de maior número, e é o que o protocolo anti-overfit da seção 10 proíbe: com a reversão parada, a oscilação do excesso não tem mecanismo por trás. Se a banda entrar, o nível se escolhe pela **reversão e pelo breakeven** — as duas primeiras colunas —, junto com o teto, e uma vez só.

