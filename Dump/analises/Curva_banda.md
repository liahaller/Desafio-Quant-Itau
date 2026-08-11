# Curva banda de não-negociação — o giro do H = 1 dia é ruído?

> Gerado por `scripts/curva_banda.py`. **A banda não está ligada no v1** (`banda=None`): o nível é threshold do modelo e vem de decisão humana (regra 6 do `CLAUDE.md`). Esta tabela **mede e reporta** — nenhuma linha é proposta.

- janela: **2025-02-10 a 2026-08-06** (374 pregões)
- configuração de referência: teto **no tilt = 1**, custo **2.0 bps/lado**, views 2.2 e 2.3, camada tática desligada (12c)
- banda **por ativo**: Δw abaixo dela não é executado, e o Δw grande vai inteiro — não é imposto sobre o trade, é filtro de ruído

| banda | giro diário | desfeito em 1–2 pregões | pernas paradas | breakeven | custo pago | excesso × SPY | sharpe | Σ\|w\| |
|---|---|---|---|---|---|---|---|---|
| **0 (v1)** | 0.274 | 0.374 | 1% | 34.46 bps | 2.05% | +6.24 pp | 1.27 | 1.94 |
| 0.10% | 0.273 | 0.373 | 40% | 34.56 bps | 2.05% | +6.23 pp | 1.27 | 1.94 |
| 0.25% | 0.272 | 0.372 | 54% | 34.81 bps | 2.03% | +6.30 pp | 1.28 | 1.94 |
| 0.50% | 0.269 | 0.370 | 65% | 35.14 bps | 2.01% | +6.27 pp | 1.28 | 1.94 |
| 1.00% | 0.264 | 0.367 | 73% | 35.96 bps | 1.98% | +6.57 pp | 1.28 | 1.94 |
| 2.50% | 0.252 | 0.357 | 83% | 37.48 bps | 1.88% | +6.28 pp | 1.26 | 1.95 |
| 5.00% | 0.235 | 0.349 | 88% | 38.89 bps | 1.76% | +4.94 pp | 1.23 | 1.93 |

## Leitura

**Ponto de partida (v1, sem banda):** giro diário **0.274**, com **37.4%** dele desfeito em 1–2 pregões, e custo de breakeven de **34.46 bps por lado** contra os 2.0 bps premissados — **17× de folga**, que é o número a ter em mente antes de discutir banda: o custo teria de subir uma ordem de grandeza para virar o sinal.

**A banda corta giro:** de 0.274 a 0.235 (14% a menos) na ponta da grade, monotonicamente — na maior banda, 88% dos pares (dia × ativo) não negociam.

**O giro está concentrado em poucas pernas grandes.** A banda mais fina da grade (0.10%) já impede **40%** dos pares (dia × ativo) de negociar e ainda assim corta só **0.3%** do giro — ou seja, não existe uma cauda de trade miúdo a filtrar: quase todo o giro do v1 está em poucas pernas grandes, que a banda deixa passar inteiras por construção.

**Mas cortar giro não é o teste — o teste é a reversão.** Ela cai de 0.374 para 0.349 (-0.025). O giro que a banda tira é desproporcionalmente o que se desfazia: é ruído sendo pago a 2 bps a volta, e a banda ataca o mecanismo certo.

**Custo de breakeven:** vai de 34.46 bps a 38.89 bps (+4.43); o máximo da grade é **38.89 bps**, na banda de 5.00%. A folga contra os 2 bps premissados aumenta com a banda.

**Excesso × SPY:** +6.24 pp sem banda, faixa de +4.94 a +6.57 pp na grade (Δ de -1.30 a +0.32 pp). O sinal do resultado não muda em nenhuma banda da grade.

**O que isto NÃO decide:** o nível da banda. O excesso **não** é monótono na grade — ele oscila e o máximo cai numa banda interior (1.00%, +6.57 pp). É exatamente a tabela que tenta o olho a escolher a linha de maior número, e é o que o protocolo anti-overfit da seção 10 proíbe: com a reversão parada, a oscilação do excesso não tem mecanismo por trás. Se a banda entrar, o nível se escolhe pela **reversão e pelo breakeven** — as duas primeiras colunas —, junto com o teto, e uma vez só.

