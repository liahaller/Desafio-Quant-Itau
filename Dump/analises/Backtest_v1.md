# Backtest do v1 — BL com as views ativas (I5)

> Gerado por `scripts/backtest_v1.py`. Benchmark = comprar e segurar SPY (consequência do `w_mkt` do prior CAPM). Custo de **2.0 bps por lado** sobre o giro contra o peso derivado (D8). Uma coluna por teto de alavancagem — **o teto é decisão humana; a varredura mede, não escolhe.**

- janela: **2025-02-10 a 2026-08-06** (374 pregões)
- views ativas: **2.2 inflação** e **2.3 Fed** (esta desde 2026-08-07: PMF de decisão por reunião + `DTB3 − DFF` demeanado). A B fica fora por decisão 11, não por cascata
- duration do breakeven: **medida** no par da própria view, janela expansiva — variou de **8.31 a 8.38** na amostra (a espec supunha "~8"; o dado confirmou, e agora o número é medido em vez de suposto)
- camada tática: **desligada** — os orçamentos são parâmetro de reunião

- **duas varreduras de escopo do teto:** `Σ|w| ≤ t` corta a carteira inteira; `tilt ≤ t` corta só `Σ|w − w_mkt|` e deixa a perna de mercado do prior intacta

| métrica | Σ\|w\| ≤ 1 | Σ\|w\| ≤ 2 | Σ\|w\| ≤ 3 | Σ\|w\| ≤ 5 | tilt ≤ 1 | tilt ≤ 2 | tilt ≤ 3 | tilt ≤ 5 |
|---|---|---|---|---|---|---|---|---|
| pregões | 374.0000 | 374.0000 | 374.0000 | 374.0000 | 374.0000 | 374.0000 | 374.0000 | 374.0000 |
| retorno acumulado bruto | 0.2063 | 0.2681 | 0.3181 | 0.3944 | 0.3523 | 0.4174 | 0.4755 | 0.5341 |
| retorno acumulado líquido | 0.1808 | 0.2221 | 0.2526 | 0.2919 | 0.3280 | 0.3705 | 0.4068 | 0.4273 |
| retorno médio diário líquido | 0.0005 | 0.0006 | 0.0006 | 0.0007 | 0.0008 | 0.0009 | 0.0010 | 0.0010 |
| vol anualizada | 0.0646 | 0.0970 | 0.1126 | 0.1379 | 0.1838 | 0.1892 | 0.1958 | 0.2092 |
| sharpe anualizado (excesso zero) | 1.7669 | 1.4417 | 1.4049 | 1.3207 | 1.1315 | 1.2168 | 1.2723 | 1.2503 |
| giro diário médio | 0.2853 | 0.4939 | 0.6800 | 1.0200 | 0.2421 | 0.4498 | 0.6369 | 0.9630 |
| giro desfeito em 1–2 pregões | 0.3639 | 0.3528 | 0.3487 | 0.3440 | 0.3500 | 0.3536 | 0.3492 | 0.3446 |
| custo pago (fração do patrimônio) | 0.0213 | 0.0369 | 0.0509 | 0.0763 | 0.0181 | 0.0336 | 0.0476 | 0.0720 |
| custo de breakeven (bps por lado) | 17.8726 | 13.2404 | 11.2309 | 9.0855 | 36.0873 | 22.3073 | 17.5173 | 12.7796 |
| alavancagem média (Σ|w|) | 1.0000 | 1.9040 | 2.7334 | 4.2803 | 1.9040 | 2.7334 | 3.5213 | 5.0267 |
| views ativas por dia (média) | 1.6070 | 1.6070 | 1.6070 | 1.6070 | 1.6070 | 1.6070 | 1.6070 | 1.6070 |
| perna de mercado (composta) | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 |
| tilt (soma das contribuições diárias) | -0.0962 | -0.0423 | -0.0012 | 0.0598 | 0.0399 | 0.0885 | 0.1305 | 0.1734 |
| benchmark acumulado | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 |
| excesso acumulado (líquido − benchmark) | -0.1204 | -0.0791 | -0.0486 | -0.0093 | 0.0268 | 0.0693 | 0.1056 | 0.1261 |

## Giro — as duas checagens obrigatórias do D8

O custo não vem de negociar muito, vem de negociar contra si mesmo: **giro desfeito em 1–2 pregões** é o mecanismo que destruiu a GTAA diária citada na pesquisa do D8. Se ele for alto, a saída prevista **não** é abandonar o H = 1 dia — é banda de não-negociação.

- **Σ\|w\| ≤ 1:** giro diário médio 0.285 · desfeito em 1–2 pregões 0.364 · custo de breakeven 17.87 bps/lado (premissa: 2.0)
- **Σ\|w\| ≤ 2:** giro diário médio 0.494 · desfeito em 1–2 pregões 0.353 · custo de breakeven 13.24 bps/lado (premissa: 2.0)
- **Σ\|w\| ≤ 3:** giro diário médio 0.680 · desfeito em 1–2 pregões 0.349 · custo de breakeven 11.23 bps/lado (premissa: 2.0)
- **Σ\|w\| ≤ 5:** giro diário médio 1.020 · desfeito em 1–2 pregões 0.344 · custo de breakeven 9.09 bps/lado (premissa: 2.0)
- **tilt ≤ 1:** giro diário médio 0.242 · desfeito em 1–2 pregões 0.350 · custo de breakeven 36.09 bps/lado (premissa: 2.0)
- **tilt ≤ 2:** giro diário médio 0.450 · desfeito em 1–2 pregões 0.354 · custo de breakeven 22.31 bps/lado (premissa: 2.0)
- **tilt ≤ 3:** giro diário médio 0.637 · desfeito em 1–2 pregões 0.349 · custo de breakeven 17.52 bps/lado (premissa: 2.0)
- **tilt ≤ 5:** giro diário médio 0.963 · desfeito em 1–2 pregões 0.345 · custo de breakeven 12.78 bps/lado (premissa: 2.0)

## Leitura

**A carteira perde do comprar-e-segurar SPY** no teto de carteira mais apertado: +18.1% contra +30.1% do benchmark (-12.04 pp).

**Folga de custo.** O retorno BRUTO é +20.6% e o custo de breakeven (17.9 bps/lado) é 8.9× a premissa de 2 bps — o resultado não está sendo decidido pelo custo.

**O escopo do teto é mecânico, não da view.** O teto de carteira escala TODAS as pontas pelo mesmo fator, inclusive a de SPY que vem do prior. Com 1.61 view(s) ativa(s) por pregão em média, parte do orçamento de Σ|w| sai do SPY para os pares das views — numa janela em que o SPY fez +30.1%, reduzir exposição a ele custa caro por si só. A seção seguinte mede o tamanho disso.

**Giro desfeito em 1–2 pregões: 36%.** Um terço do que se negocia é desfeito em dois pregões. É material, mas com a folga de custo acima não é o que está segurando o resultado — entra como insumo da revisão condicional do D1 (banda de não-negociação), não como veredito sobre o H.


## Onde o teto corta — carteira inteira × só o tilt

Mesma varredura, dois escopos. `Σ|w| ≤ t` escala tudo; `tilt ≤ t` corta só `Σ|w − w_mkt|` e entrega a perna de mercado inteira. **Isto mede, não decide:** a D12 (nível do teto) segue esperando o `c` da Lia, na ordem que ela propôs — entra o `c`, mede-se Σ|w| de novo, aí se decide o teto.

> Os rótulos NÃO são comparáveis entre si. `tilt ≤ t` limita o desvio, não a carteira: com w_mkt = 100% SPY, Σ|w| pode chegar a 1 + t. Compare pela **alavancagem medida**, que é a coluna ao lado.

| escopo | teto | Σ\|w\| medida | líquido | excesso | tilt (soma diária) | giro/dia |
|---|---|---|---|---|---|---|
| carteira | 1 | 1.00 | +18.08% | -12.04 pp | -9.62% | 0.285 |
| só o tilt | 1 | 1.90 | +32.80% | +2.68 pp | +3.99% | 0.242 |
| carteira | 2 | 1.90 | +22.21% | -7.91 pp | -4.23% | 0.494 |
| só o tilt | 2 | 2.73 | +37.05% | +6.93 pp | +8.85% | 0.450 |
| carteira | 3 | 2.73 | +25.26% | -4.86 pp | -0.12% | 0.680 |
| só o tilt | 3 | 3.52 | +40.68% | +10.56 pp | +13.05% | 0.637 |
| carteira | 5 | 4.28 | +29.19% | -0.93 pp | +5.98% | 1.020 |
| só o tilt | 5 | 5.03 | +42.73% | +12.61 pp | +17.34% | 0.963 |

**No teto 1, preservar a perna de mercado muda o excesso em +14.72 pp** (-12.04 pp → +2.68 pp), a um custo de alavancagem de 1.00 → 1.90 de Σ|w| médio. Com o escopo no tilt a carteira **passa a bater** o comprar-e-segurar SPY.


**A mesma comparação com Σ|w| IGUAL** (o rótulo engana, a alavancagem medida não):

- Σ|w| = **1.90**: `Σ\|w\| ≤ 2` dá -7.91 pp de excesso, `tilt ≤ 1` dá +2.68 pp — diferença de **+10.59 pp** só por causa de ONDE o teto corta, com o mesmo tamanho de carteira.
- Σ|w| = **2.73**: `Σ\|w\| ≤ 3` dá -4.86 pp de excesso, `tilt ≤ 2` dá +6.93 pp — diferença de **+11.79 pp** só por causa de ONDE o teto corta, com o mesmo tamanho de carteira.

A parcela de tilt é o que separa os dois desenhos: -9.62% no corte de carteira contra +3.99% no corte de tilt. No corte de carteira essa parcela mistura duas coisas — o tilt da view **e** o pedaço da perna de mercado que o corte tirou; no corte de tilt ela é só a view. A diferença entre as duas é a conta do que o escopo do teto cobra por si só.

