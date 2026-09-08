# Curva banda de não-negociação — o giro do H = 1 dia é ruído?

> Gerado por `scripts/curva_banda.py`. **A banda não está ligada no v1** (`banda=None`): o nível é threshold do modelo e vem de decisão humana (regra 6 do `CLAUDE.md`). Esta tabela **mede e reporta** — nenhuma linha é proposta.

- janela: **2025-02-10 a 2026-08-06** (374 pregões)
- configuração de referência: teto **no tilt = 1**, custo **2.0 bps/lado**, camada tática v2 **ligada**, régua do Ω **ligada no nível 1** (6q). As views são as do `backtest_v1.carregar` e **não são redeclaradas aqui** — foi assim que este artefato ficou anunciando "2.2 e 2.3" depois da D23 (mesmo erro da D25g)
- banda **por ativo**: Δw abaixo dela não é executado, e o Δw grande vai inteiro — não é imposto sobre o trade, é filtro de ruído

| banda | giro diário | desfeito em 1–2 pregões | pernas paradas | breakeven | custo pago | excesso × SPY | sharpe | Σ\|w\| |
|---|---|---|---|---|---|---|---|---|
| **0 (v1)** | 0.396 | 0.419 | 1% | 22.87 bps | 2.96% | +3.04 pp | 1.18 | 1.91 |
| 0.10% | 0.396 | 0.419 | 33% | 22.91 bps | 2.96% | +3.05 pp | 1.18 | 1.91 |
| 0.25% | 0.394 | 0.418 | 46% | 23.02 bps | 2.95% | +3.12 pp | 1.18 | 1.92 |
| 0.50% | 0.391 | 0.417 | 56% | 23.15 bps | 2.93% | +3.04 pp | 1.18 | 1.92 |
| 1.00% | 0.386 | 0.415 | 64% | 23.47 bps | 2.89% | +3.16 pp | 1.18 | 1.92 |
| 2.50% | 0.372 | 0.411 | 76% | 24.33 bps | 2.78% | +3.16 pp | 1.18 | 1.92 |
| 5.00% | 0.348 | 0.410 | 83% | 25.45 bps | 2.60% | +2.47 pp | 1.17 | 1.94 |

## Leitura

**Ponto de partida (v1, sem banda):** giro diário **0.396**, com **41.9%** dele desfeito em 1–2 pregões, e custo de breakeven de **22.87 bps por lado** contra os 2.0 bps premissados — **11× de folga**, que é o número a ter em mente antes de discutir banda: o custo teria de subir uma ordem de grandeza para virar o sinal.

**A banda corta giro:** de 0.396 a 0.348 (12% a menos) na ponta da grade, monotonicamente — na maior banda, 83% dos pares (dia × ativo) não negociam.

**O giro está concentrado em poucas pernas grandes.** A banda mais fina da grade (0.10%) já impede **33%** dos pares (dia × ativo) de negociar e ainda assim corta só **0.2%** do giro — ou seja, não existe uma cauda de trade miúdo a filtrar: quase todo o giro do v1 está em poucas pernas grandes, que a banda deixa passar inteiras por construção.

**Mas cortar giro não é o teste — o teste é a reversão.** Ela cai de 0.419 para 0.410 (-0.009). Praticamente não se move: a banda tira giro dos dois tipos na mesma proporção, então não há evidência de que o giro do v1 seja ruído.

**Custo de breakeven:** vai de 22.87 bps a 25.45 bps (+2.58); o máximo da grade é **25.45 bps**, na banda de 5.00%. A folga contra os 2 bps premissados aumenta com a banda.

**Excesso × SPY:** +3.04 pp sem banda, faixa de +2.47 a +3.16 pp na grade (Δ de -0.58 a +0.11 pp). O sinal do resultado não muda em nenhuma banda da grade.

**O que isto NÃO decide:** o nível da banda. O excesso **não** é monótono na grade — ele oscila e o máximo cai numa banda interior (1.00%, +3.16 pp). É exatamente a tabela que tenta o olho a escolher a linha de maior número, e é o que o protocolo anti-overfit da seção 10 proíbe: com a reversão parada, a oscilação do excesso não tem mecanismo por trás. Se a banda entrar, o nível se escolhe pela **reversão e pelo breakeven** — as duas primeiras colunas —, junto com o teto, e uma vez só.

