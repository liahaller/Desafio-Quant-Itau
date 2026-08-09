# Backtest do v1 — BL com as views ativas (I5)

> Gerado por `scripts/backtest_v1.py`. Benchmark = comprar e segurar SPY (consequência do `w_mkt` do prior CAPM). Custo de **2.0 bps por lado** sobre o giro contra o peso derivado (D8). Uma coluna por teto de alavancagem — **o teto é decisão humana; a varredura mede, não escolhe.**

- janela: **2025-02-10 a 2026-08-06** (374 pregões)
- views ativas: **2.2 inflação** e **2.3 Fed** (esta desde 2026-08-07: PMF de decisão por reunião + `DTB3 − DFF` demeanado). A B fica fora por decisão 11, não por cascata
- demeanagem da 2.3: média expansiva **semeada** com 206 pregões anteriores à janela (2024-04 a 2025-02, dado passado — não lookahead). Sem semente o primeiro dia demeana por 0,0; o sinal líquido sai 22% positivo, contra 34% com semente
- duration do breakeven: **medida** no par da própria view, janela expansiva — variou de **8.31 a 8.38** na amostra (a espec supunha "~8"; o dado confirmou, e agora o número é medido em vez de suposto)
- camada tática: **desligada** — os orçamentos são parâmetro de reunião

- **duas varreduras de escopo do teto:** `Σ|w| ≤ t` corta a carteira inteira; `tilt ≤ t` corta só `Σ|w − w_mkt|` e deixa a perna de mercado do prior intacta

| métrica | Σ\|w\| ≤ 1 | Σ\|w\| ≤ 2 | Σ\|w\| ≤ 3 | Σ\|w\| ≤ 5 | tilt ≤ 1 | tilt ≤ 2 | tilt ≤ 3 | tilt ≤ 5 |
|---|---|---|---|---|---|---|---|---|
| pregões | 374.0000 | 374.0000 | 374.0000 | 374.0000 | 374.0000 | 374.0000 | 374.0000 | 374.0000 |
| retorno acumulado bruto | 0.1727 | 0.2891 | 0.3727 | 0.5143 | 0.3651 | 0.4680 | 0.5642 | 0.6905 |
| retorno acumulado líquido | 0.1492 | 0.2441 | 0.3073 | 0.4075 | 0.3419 | 0.4215 | 0.4951 | 0.5781 |
| retorno médio diário líquido | 0.0004 | 0.0006 | 0.0007 | 0.0010 | 0.0008 | 0.0010 | 0.0011 | 0.0013 |
| vol anualizada | 0.0604 | 0.0901 | 0.1066 | 0.1386 | 0.1795 | 0.1849 | 0.1927 | 0.2102 |
| sharpe anualizado (excesso zero) | 1.5821 | 1.6791 | 1.7473 | 1.7316 | 1.1933 | 1.3735 | 1.5026 | 1.5676 |
| giro diário médio | 0.2712 | 0.4744 | 0.6521 | 0.9783 | 0.2286 | 0.4303 | 0.6038 | 0.9200 |
| giro desfeito em 1–2 pregões | 0.3640 | 0.3600 | 0.3559 | 0.3459 | 0.3672 | 0.3671 | 0.3546 | 0.3444 |
| custo pago (fração do patrimônio) | 0.0203 | 0.0355 | 0.0488 | 0.0732 | 0.0171 | 0.0322 | 0.0452 | 0.0688 |
| custo de breakeven (bps por lado) | 15.9790 | 14.6544 | 13.3359 | 11.7330 | 39.1774 | 25.4250 | 21.0251 | 16.2109 |
| alavancagem média (Σ|w|) | 1.0000 | 1.9288 | 2.7782 | 4.3787 | 1.9288 | 2.7782 | 3.5890 | 5.1431 |
| views ativas por dia (média) | 1.6016 | 1.6016 | 1.6016 | 1.6016 | 1.6016 | 1.6016 | 1.6016 | 1.6016 |
| perna de mercado (composta) | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 |
| tilt (soma das contribuições diárias) | -0.1248 | -0.0268 | 0.0384 | 0.1424 | 0.0481 | 0.1223 | 0.1880 | 0.2709 |
| benchmark acumulado | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 |
| excesso acumulado (líquido − benchmark) | -0.1520 | -0.0571 | 0.0061 | 0.1063 | 0.0407 | 0.1203 | 0.1939 | 0.2769 |

## Giro — as duas checagens obrigatórias do D8

O custo não vem de negociar muito, vem de negociar contra si mesmo: **giro desfeito em 1–2 pregões** é o mecanismo que destruiu a GTAA diária citada na pesquisa do D8. Se ele for alto, a saída prevista **não** é abandonar o H = 1 dia — é banda de não-negociação.

- **Σ\|w\| ≤ 1:** giro diário médio 0.271 · desfeito em 1–2 pregões 0.364 · custo de breakeven 15.98 bps/lado (premissa: 2.0)
- **Σ\|w\| ≤ 2:** giro diário médio 0.474 · desfeito em 1–2 pregões 0.360 · custo de breakeven 14.65 bps/lado (premissa: 2.0)
- **Σ\|w\| ≤ 3:** giro diário médio 0.652 · desfeito em 1–2 pregões 0.356 · custo de breakeven 13.34 bps/lado (premissa: 2.0)
- **Σ\|w\| ≤ 5:** giro diário médio 0.978 · desfeito em 1–2 pregões 0.346 · custo de breakeven 11.73 bps/lado (premissa: 2.0)
- **tilt ≤ 1:** giro diário médio 0.229 · desfeito em 1–2 pregões 0.367 · custo de breakeven 39.18 bps/lado (premissa: 2.0)
- **tilt ≤ 2:** giro diário médio 0.430 · desfeito em 1–2 pregões 0.367 · custo de breakeven 25.42 bps/lado (premissa: 2.0)
- **tilt ≤ 3:** giro diário médio 0.604 · desfeito em 1–2 pregões 0.355 · custo de breakeven 21.03 bps/lado (premissa: 2.0)
- **tilt ≤ 5:** giro diário médio 0.920 · desfeito em 1–2 pregões 0.344 · custo de breakeven 16.21 bps/lado (premissa: 2.0)

## Leitura

**A carteira perde do comprar-e-segurar SPY** no teto de carteira mais apertado: +14.9% contra +30.1% do benchmark (-15.20 pp).

**Folga de custo.** O retorno BRUTO é +17.3% e o custo de breakeven (16.0 bps/lado) é 8.0× a premissa de 2 bps — o resultado não está sendo decidido pelo custo.

**O escopo do teto é mecânico, não da view.** O teto de carteira escala TODAS as pontas pelo mesmo fator, inclusive a de SPY que vem do prior. Com 1.60 view(s) ativa(s) por pregão em média, parte do orçamento de Σ|w| sai do SPY para os pares das views — numa janela em que o SPY fez +30.1%, reduzir exposição a ele custa caro por si só. A seção seguinte mede o tamanho disso.

**Giro desfeito em 1–2 pregões: 36%.** Um terço do que se negocia é desfeito em dois pregões. É material, mas com a folga de custo acima não é o que está segurando o resultado — entra como insumo da revisão condicional do D1 (banda de não-negociação), não como veredito sobre o H.


## Onde o teto corta — carteira inteira × só o tilt

Mesma varredura, dois escopos. `Σ|w| ≤ t` escala tudo; `tilt ≤ t` corta só `Σ|w − w_mkt|` e entrega a perna de mercado inteira. **Isto mede, não decide:** a D12 (nível do teto) segue esperando o `c` da Lia, na ordem que ela propôs — entra o `c`, mede-se Σ|w| de novo, aí se decide o teto.

> Os rótulos NÃO são comparáveis entre si. `tilt ≤ t` limita o desvio, não a carteira: com w_mkt = 100% SPY, Σ|w| pode chegar a 1 + t. Compare pela **alavancagem medida**, que é a coluna ao lado.

| escopo | teto | Σ\|w\| medida | líquido | excesso | tilt (soma diária) | giro/dia |
|---|---|---|---|---|---|---|
| carteira | 1 | 1.00 | +14.92% | -15.20 pp | -12.48% | 0.271 |
| só o tilt | 1 | 1.93 | +34.19% | +4.07 pp | +4.81% | 0.229 |
| carteira | 2 | 1.93 | +24.41% | -5.71 pp | -2.68% | 0.474 |
| só o tilt | 2 | 2.78 | +42.15% | +12.03 pp | +12.23% | 0.430 |
| carteira | 3 | 2.78 | +30.73% | +0.61 pp | +3.84% | 0.652 |
| só o tilt | 3 | 3.59 | +49.51% | +19.39 pp | +18.80% | 0.604 |
| carteira | 5 | 4.38 | +40.75% | +10.63 pp | +14.24% | 0.978 |
| só o tilt | 5 | 5.14 | +57.81% | +27.69 pp | +27.09% | 0.920 |

**No teto 1, preservar a perna de mercado muda o excesso em +19.28 pp** (-15.20 pp → +4.07 pp), a um custo de alavancagem de 1.00 → 1.93 de Σ|w| médio. Com o escopo no tilt a carteira **passa a bater** o comprar-e-segurar SPY.


**A mesma comparação com Σ|w| IGUAL** (o rótulo engana, a alavancagem medida não):

- Σ|w| = **1.93**: `Σ\|w\| ≤ 2` dá -5.71 pp de excesso, `tilt ≤ 1` dá +4.07 pp — diferença de **+9.78 pp** só por causa de ONDE o teto corta, com o mesmo tamanho de carteira.
- Σ|w| = **2.78**: `Σ\|w\| ≤ 3` dá +0.61 pp de excesso, `tilt ≤ 2` dá +12.03 pp — diferença de **+11.42 pp** só por causa de ONDE o teto corta, com o mesmo tamanho de carteira.

A parcela de tilt é o que separa os dois desenhos: -12.48% no corte de carteira contra +4.81% no corte de tilt. No corte de carteira essa parcela mistura duas coisas — o tilt da view **e** o pedaço da perna de mercado que o corte tirou; no corte de tilt ela é só a view. A diferença entre as duas é a conta do que o escopo do teto cobra por si só.


## Robustez γ (favorite-longshot) — promessa da seção 9

O v1 roda em **γ = 1** (D1.1: sem correção — 9 mercados resolvidos não calibram curva própria, e importar γ de aposta esportiva mexeria a mediana sem âncora no nosso dado). A coluna existe para **reportar**, não para escolher: se o resultado só sobrevive em um γ, isso tem de aparecer.

Medido no escopo de referência (**tilt ≤ 1**), com a semente da 2.3 recalculada em cada γ — a surpresa depende dele.

| γ | excesso × SPY | líquido | sharpe | Σ\|w\| média | giro diário |
|---|---|---|---|---|---|
| 1 | +4.07 pp | +34.2% | 1.19 | 1.93 | 0.229 |
| 1.1 | +4.35 pp | +34.5% | 1.20 | 1.93 | 0.230 |
| 1.25 | +5.51 pp | +35.6% | 1.24 | 1.93 | 0.236 |

**Faixa do excesso na varredura: +4.07 pp a +5.51 pp** — o sinal do resultado **não** depende do γ nesta janela.

