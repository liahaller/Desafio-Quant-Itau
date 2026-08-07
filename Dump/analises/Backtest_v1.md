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
| retorno acumulado bruto | 0.1638 | 0.2734 | 0.3447 | 0.4451 | 0.3517 | 0.4372 | 0.5092 | 0.5909 |
| retorno acumulado líquido | 0.1395 | 0.2269 | 0.2772 | 0.3372 | 0.3274 | 0.3889 | 0.4382 | 0.4786 |
| retorno médio diário líquido | 0.0004 | 0.0006 | 0.0007 | 0.0008 | 0.0008 | 0.0009 | 0.0010 | 0.0011 |
| vol anualizada | 0.0605 | 0.0902 | 0.1062 | 0.1356 | 0.1798 | 0.1852 | 0.1925 | 0.2078 |
| sharpe anualizado (excesso zero) | 1.4851 | 1.5724 | 1.6063 | 1.5118 | 1.1506 | 1.2873 | 1.3681 | 1.3719 |
| giro diário médio | 0.2815 | 0.4971 | 0.6884 | 1.0370 | 0.2423 | 0.4568 | 0.6438 | 0.9784 |
| giro desfeito em 1–2 pregões | 0.3645 | 0.3576 | 0.3540 | 0.3466 | 0.3634 | 0.3629 | 0.3541 | 0.3465 |
| custo pago (fração do patrimônio) | 0.0211 | 0.0372 | 0.0515 | 0.0776 | 0.0181 | 0.0342 | 0.0482 | 0.0732 |
| custo de breakeven (bps por lado) | 14.6670 | 13.3273 | 11.8309 | 9.8448 | 35.8905 | 22.7121 | 18.2288 | 13.5623 |
| alavancagem média (Σ|w|) | 1.0000 | 1.9265 | 2.7689 | 4.3423 | 1.9265 | 2.7689 | 3.5683 | 5.0907 |
| views ativas por dia (média) | 1.6070 | 1.6070 | 1.6070 | 1.6070 | 1.6070 | 1.6070 | 1.6070 | 1.6070 |
| perna de mercado (composta) | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 |
| tilt (soma das contribuições diárias) | -0.1324 | -0.0390 | 0.0178 | 0.0950 | 0.0384 | 0.1011 | 0.1521 | 0.2094 |
| benchmark acumulado | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 |
| excesso acumulado (líquido − benchmark) | -0.1617 | -0.0743 | -0.0240 | 0.0360 | 0.0262 | 0.0877 | 0.1370 | 0.1774 |

## Giro — as duas checagens obrigatórias do D8

O custo não vem de negociar muito, vem de negociar contra si mesmo: **giro desfeito em 1–2 pregões** é o mecanismo que destruiu a GTAA diária citada na pesquisa do D8. Se ele for alto, a saída prevista **não** é abandonar o H = 1 dia — é banda de não-negociação.

- **Σ\|w\| ≤ 1:** giro diário médio 0.281 · desfeito em 1–2 pregões 0.364 · custo de breakeven 14.67 bps/lado (premissa: 2.0)
- **Σ\|w\| ≤ 2:** giro diário médio 0.497 · desfeito em 1–2 pregões 0.358 · custo de breakeven 13.33 bps/lado (premissa: 2.0)
- **Σ\|w\| ≤ 3:** giro diário médio 0.688 · desfeito em 1–2 pregões 0.354 · custo de breakeven 11.83 bps/lado (premissa: 2.0)
- **Σ\|w\| ≤ 5:** giro diário médio 1.037 · desfeito em 1–2 pregões 0.347 · custo de breakeven 9.84 bps/lado (premissa: 2.0)
- **tilt ≤ 1:** giro diário médio 0.242 · desfeito em 1–2 pregões 0.363 · custo de breakeven 35.89 bps/lado (premissa: 2.0)
- **tilt ≤ 2:** giro diário médio 0.457 · desfeito em 1–2 pregões 0.363 · custo de breakeven 22.71 bps/lado (premissa: 2.0)
- **tilt ≤ 3:** giro diário médio 0.644 · desfeito em 1–2 pregões 0.354 · custo de breakeven 18.23 bps/lado (premissa: 2.0)
- **tilt ≤ 5:** giro diário médio 0.978 · desfeito em 1–2 pregões 0.346 · custo de breakeven 13.56 bps/lado (premissa: 2.0)

## Leitura

**A carteira perde do comprar-e-segurar SPY** no teto de carteira mais apertado: +14.0% contra +30.1% do benchmark (-16.17 pp).

**Folga de custo.** O retorno BRUTO é +16.4% e o custo de breakeven (14.7 bps/lado) é 7.3× a premissa de 2 bps — o resultado não está sendo decidido pelo custo.

**O escopo do teto é mecânico, não da view.** O teto de carteira escala TODAS as pontas pelo mesmo fator, inclusive a de SPY que vem do prior. Com 1.61 view(s) ativa(s) por pregão em média, parte do orçamento de Σ|w| sai do SPY para os pares das views — numa janela em que o SPY fez +30.1%, reduzir exposição a ele custa caro por si só. A seção seguinte mede o tamanho disso.

**Giro desfeito em 1–2 pregões: 36%.** Um terço do que se negocia é desfeito em dois pregões. É material, mas com a folga de custo acima não é o que está segurando o resultado — entra como insumo da revisão condicional do D1 (banda de não-negociação), não como veredito sobre o H.


## Onde o teto corta — carteira inteira × só o tilt

Mesma varredura, dois escopos. `Σ|w| ≤ t` escala tudo; `tilt ≤ t` corta só `Σ|w − w_mkt|` e entrega a perna de mercado inteira. **Isto mede, não decide:** a D12 (nível do teto) segue esperando o `c` da Lia, na ordem que ela propôs — entra o `c`, mede-se Σ|w| de novo, aí se decide o teto.

> Os rótulos NÃO são comparáveis entre si. `tilt ≤ t` limita o desvio, não a carteira: com w_mkt = 100% SPY, Σ|w| pode chegar a 1 + t. Compare pela **alavancagem medida**, que é a coluna ao lado.

| escopo | teto | Σ\|w\| medida | líquido | excesso | tilt (soma diária) | giro/dia |
|---|---|---|---|---|---|---|
| carteira | 1 | 1.00 | +13.95% | -16.17 pp | -13.24% | 0.281 |
| só o tilt | 1 | 1.93 | +32.74% | +2.62 pp | +3.84% | 0.242 |
| carteira | 2 | 1.93 | +22.69% | -7.43 pp | -3.90% | 0.497 |
| só o tilt | 2 | 2.77 | +38.89% | +8.77 pp | +10.11% | 0.457 |
| carteira | 3 | 2.77 | +27.72% | -2.40 pp | +1.78% | 0.688 |
| só o tilt | 3 | 3.57 | +43.82% | +13.70 pp | +15.21% | 0.644 |
| carteira | 5 | 4.34 | +33.72% | +3.60 pp | +9.50% | 1.037 |
| só o tilt | 5 | 5.09 | +47.86% | +17.74 pp | +20.94% | 0.978 |

**No teto 1, preservar a perna de mercado muda o excesso em +18.79 pp** (-16.17 pp → +2.62 pp), a um custo de alavancagem de 1.00 → 1.93 de Σ|w| médio. Com o escopo no tilt a carteira **passa a bater** o comprar-e-segurar SPY.


**A mesma comparação com Σ|w| IGUAL** (o rótulo engana, a alavancagem medida não):

- Σ|w| = **1.93**: `Σ\|w\| ≤ 2` dá -7.43 pp de excesso, `tilt ≤ 1` dá +2.62 pp — diferença de **+10.05 pp** só por causa de ONDE o teto corta, com o mesmo tamanho de carteira.
- Σ|w| = **2.77**: `Σ\|w\| ≤ 3` dá -2.40 pp de excesso, `tilt ≤ 2` dá +8.77 pp — diferença de **+11.17 pp** só por causa de ONDE o teto corta, com o mesmo tamanho de carteira.

A parcela de tilt é o que separa os dois desenhos: -13.24% no corte de carteira contra +3.84% no corte de tilt. No corte de carteira essa parcela mistura duas coisas — o tilt da view **e** o pedaço da perna de mercado que o corte tirou; no corte de tilt ela é só a view. A diferença entre as duas é a conta do que o escopo do teto cobra por si só.


## Robustez γ (favorite-longshot) — promessa da seção 9

O v1 roda em **γ = 1** (D1.1: sem correção — 9 mercados resolvidos não calibram curva própria, e importar γ de aposta esportiva mexeria a mediana sem âncora no nosso dado). A coluna existe para **reportar**, não para escolher: se o resultado só sobrevive em um γ, isso tem de aparecer.

Medido no escopo de referência (**tilt ≤ 1**), com a semente da 2.3 recalculada em cada γ — a surpresa depende dele.

| γ | excesso × SPY | líquido | sharpe | Σ\|w\| média | giro diário |
|---|---|---|---|---|---|
| 1 | +2.62 pp | +32.7% | 1.15 | 1.93 | 0.242 |
| 1.1 | +2.88 pp | +33.0% | 1.16 | 1.93 | 0.244 |
| 1.25 | +4.02 pp | +34.1% | 1.20 | 1.93 | 0.250 |

**Faixa do excesso na varredura: +2.62 pp a +4.02 pp** — o sinal do resultado **não** depende do γ nesta janela.

