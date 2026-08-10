# Backtest com as views novas empilhadas — 15b (incerteza) e 15g (B própria)

> Gerado por `scripts/views_novas.py`. **Mede; não decide.** As duas views ENTRARAM na entrega em 2026-08-10 (D15a/D15b/D15c + item 4 na D22e) — este arquivo é o **registro obrigatório da D22** (atribuição 'sem os 3 maiores' + acerto de sinal), não mais uma proposta. Escopo de referência: **teto no tilt = 1**, γ = 1,0 (D1.1), custo de 2.0 bps/lado.

- janela: **2025-02-10 a 2026-08-06** (374 pregões)
- ⚠️ a primeira linha (`views_novas=()`) é o **v1 de DUAS views**, a configuração ANTERIOR — não a entregue. Ela segue sendo o grupo de controle e a base contra a qual o Δ de cada view é medido: se ela não reproduzir o +4,07 pp registrado, o errado é este script
- a configuração ENTREGUE é a linha **`+ as duas (entropia crua)`**

| configuração | dias com a view | excesso × SPY | Δ vs. v1 | líquido | sharpe | Σ\|w\| média | giro/dia |
|---|---|---|---|---|---|---|---|
| v1 anterior (2.2 + 2.3) | — | +4.07 pp | — | +34.2% | 1.19 | 1.93 | 0.229 |
| + incerteza (entropia crua) | incerteza 27 | +7.96 pp | +3.89 pp | +38.1% | 1.33 | 1.91 | 0.269 |
| + incerteza (percentil) | incerteza 27 | +6.39 pp | +2.32 pp | +36.5% | 1.28 | 1.91 | 0.288 |
| + B com β próprio (DGS1) | B 210 | +2.70 pp | -1.38 pp | +32.8% | 1.14 | 1.95 | 0.253 |
| + as duas (entropia crua) | incerteza 27 · B 210 | +6.24 pp | +2.17 pp | +36.4% | 1.27 | 1.94 | 0.274 |
| + as duas (percentil) | incerteza 27 · B 210 | +4.88 pp | +0.81 pp | +35.0% | 1.24 | 1.93 | 0.296 |

## O que cada view fez por dentro

- **+ incerteza (entropia crua)** (27 dias): entropia média +0.6947 · incerteza líquida -0.0699 · Σ P·β +0.08112 · eventos no β +16.96
- **+ incerteza (percentil)** (27 dias): percentil médio +0.427 · incerteza líquida -0.2112 · Σ P·β +0.06262 · eventos no β +16.96
- **+ B com β próprio (DGS1)** (210 dias): E_poly (bps) +367.8 · DGS1 (bps) +390.8 · surpresa crua (bps) -23.07 · surpresa líquida (bps) +16.22 · Σ P·β -0.0003965 · eventos no β +28

## De onde vem o Δ — atribuição e concentração

Soma dos Δ DIÁRIOS de retorno líquido contra o v1 (não composta, por isso não bate exatamente com o acumulado da tabela acima), e o que sobra dela tirando os três pregões de maior |Δ|. **Uma view ativa em poucos dias pode carregar o acumulado inteiro com um pregão só.**

| configuração | Σ dos Δ diários | sem os 3 maiores | acerto de sinal nos dias da view |
|---|---|---|---|
| + incerteza (entropia crua) | +2.74 pp | -0.54 pp | 48% (13/27) |
| + incerteza (percentil) | +1.61 pp | -0.09 pp | 48% (13/27) |
| + B com β próprio (DGS1) | -0.96 pp | +2.93 pp | 49% (102/210) |
| + as duas (entropia crua) | +1.52 pp | +2.51 pp | 49% (109/222) |
| + as duas (percentil) | +0.50 pp | +0.73 pp | 47% (105/222) |

Os três pregões de maior |Δ| em cada configuração:

- + incerteza (entropia crua): **2025-04-10** +3.21 pp (SPY -4.38%) · **2025-10-24** +0.60 pp (SPY +0.82%) · **2025-12-18** -0.52 pp (SPY +0.76%)
- + incerteza (percentil): **2025-04-10** +3.24 pp (SPY -4.38%) · **2026-03-06** -0.89 pp (SPY -1.31%) · **2025-12-18** -0.64 pp (SPY +0.76%)
- + B com β próprio (DGS1): **2025-04-10** -1.59 pp (SPY -4.38%) · **2025-05-12** -1.31 pp (SPY +3.30%) · **2025-03-12** -1.00 pp (SPY +0.53%)
- + as duas (entropia crua): **2025-04-10** +1.32 pp (SPY -4.38%) · **2025-05-12** -1.31 pp (SPY +3.30%) · **2025-03-12** -1.00 pp (SPY +0.53%)
- + as duas (percentil): **2025-04-10** +2.08 pp (SPY -4.38%) · **2025-05-12** -1.31 pp (SPY +3.30%) · **2025-03-12** -1.00 pp (SPY +0.53%)

**P da B no fim da janela** (β expansivo contra o ΔDGS1) — a 15g mediu 95,6° de ângulo contra o P da 2.3 usando o DGS10 como proxy; esta linha é o vértice CERTO:

| view | SPY | TIP | TLT | XLE | XLF | XLK | XLP | XLU | XLV |
|---|---|---|---|---|---|---|---|---|---|
| B_trajetoria_propria | +0.00 | +0.02 | -0.05 | +1.04 | +0.29 | +0.15 | -0.20 | -0.19 | -0.06 |

A view de incerteza é **direcional por construção** (15b): P[SPY] = +2 e 0 no resto, Σ|P| = 2. **Ela não é a única view com ΣP ≠ 0** — a obrigação 5a foi finalmente executada em 2026-08-10 (`Dump/analises/Ortogonalidade.md`) e mediu ΣP mediano de +0,96 na 2.2, +1,74 na 2.3 e +1,24 na 15g. As views ditas neutras são líquidas COMPRADAS nos 8 ativos que não são o SPY; a 15b declara o direcional, não o introduz.


## Leitura

- **+ incerteza (entropia crua)**: excesso +7.96 pp contra +4.07 pp do v1 (+3.89 pp). O Δ **NÃO sobrevive** à retirada dos três pregões extremos (+2.74 pp → -0.54 pp), e o acerto de sinal nos dias da view é de 48%.
- **+ incerteza (percentil)**: excesso +6.39 pp contra +4.07 pp do v1 (+2.32 pp). O Δ **NÃO sobrevive** à retirada dos três pregões extremos (+1.61 pp → -0.09 pp), e o acerto de sinal nos dias da view é de 48%.
- **+ B com β próprio (DGS1)**: excesso +2.70 pp contra +4.07 pp do v1 (-1.38 pp). O Δ **NÃO sobrevive** à retirada dos três pregões extremos (-0.96 pp → +2.93 pp), e o acerto de sinal nos dias da view é de 49%.
- **+ as duas (entropia crua)**: excesso +6.24 pp contra +4.07 pp do v1 (+2.17 pp). O Δ **sobrevive** à retirada dos três pregões extremos (+1.52 pp → +2.51 pp), e o acerto de sinal nos dias da view é de 49%.
- **+ as duas (percentil)**: excesso +4.88 pp contra +4.07 pp do v1 (+0.81 pp). O Δ **sobrevive** à retirada dos três pregões extremos (+0.50 pp → +0.73 pp), e o acerto de sinal nos dias da view é de 47%.

**Pendência de protocolo PAGA (D21b):** a 15g exigia a ordem `DGS1 chegou → refazer o teste de sinal no vértice certo → só então empilhar`. Quando este script rodou pela primeira vez, a etapa do meio estava pulada. Ela rodou depois (`scripts/teste_sinal.py`, `Dump/analises/Teste_sinal.md`): a B dá **t +0,33 · 51%** em h = 1 e **não sai invertida** — passa o veto do item 3 da D22.

**O que este arquivo não faz:** não decide. A entrega roda com as duas ligadas por decisão registrada (D15a/D15b/D15c/D22e), e os números acima existem para que o Δ de cada uma seja lido como contribuição medida, não como desempenho prometido.

