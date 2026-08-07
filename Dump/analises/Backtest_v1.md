# Backtest do v1 — BL com as views ativas (I5)

> Gerado por `scripts/backtest_v1.py`. Benchmark = comprar e segurar SPY (consequência do `w_mkt` do prior CAPM). Custo de **2.0 bps por lado** sobre o giro contra o peso derivado (D8). Uma coluna por teto de alavancagem — **o teto é decisão humana; a varredura mede, não escolhe.**

- janela: **2025-02-10 a 2026-08-06** (374 pregões)
- views ativas: **2.2 inflação**. A 2.3 e a B ficam fora por insumo que não chegou (DFF/G8 e ZQ de dezembro), não por cascata
- duration do breakeven: **medida** no par da própria view, janela expansiva — variou de **8.31 a 8.38** na amostra (a espec supunha "~8"; o dado confirmou, e agora o número é medido em vez de suposto)
- camada tática: **desligada** — os orçamentos são parâmetro de reunião

- **duas varreduras de escopo do teto:** `Σ|w| ≤ t` corta a carteira inteira; `tilt ≤ t` corta só `Σ|w − w_mkt|` e deixa a perna de mercado do prior intacta

| métrica | Σ\|w\| ≤ 1 | Σ\|w\| ≤ 2 | Σ\|w\| ≤ 3 | Σ\|w\| ≤ 5 | tilt ≤ 1 | tilt ≤ 2 | tilt ≤ 3 | tilt ≤ 5 |
|---|---|---|---|---|---|---|---|---|
| pregões | 374.0000 | 374.0000 | 374.0000 | 374.0000 | 374.0000 | 374.0000 | 374.0000 | 374.0000 |
| retorno acumulado bruto | 0.1764 | 0.1809 | 0.1850 | 0.1917 | 0.3055 | 0.3093 | 0.3126 | 0.3199 |
| retorno acumulado líquido | 0.1572 | 0.1498 | 0.1420 | 0.1248 | 0.2918 | 0.2821 | 0.2720 | 0.2525 |
| retorno médio diário líquido | 0.0004 | 0.0004 | 0.0004 | 0.0003 | 0.0007 | 0.0007 | 0.0007 | 0.0007 |
| vol anualizada | 0.0897 | 0.0939 | 0.1006 | 0.1194 | 0.1796 | 0.1818 | 0.1854 | 0.1963 |
| sharpe anualizado (excesso zero) | 1.1423 | 1.0485 | 0.9395 | 0.7232 | 1.0495 | 1.0113 | 0.9665 | 0.8702 |
| giro diário médio | 0.2192 | 0.3559 | 0.4933 | 0.7710 | 0.1413 | 0.2803 | 0.4197 | 0.7004 |
| giro desfeito em 1–2 pregões | 0.3346 | 0.3296 | 0.3272 | 0.3249 | 0.3176 | 0.3203 | 0.3211 | 0.3214 |
| custo pago (fração do patrimônio) | 0.0164 | 0.0266 | 0.0369 | 0.0577 | 0.0106 | 0.0210 | 0.0314 | 0.0524 |
| custo de breakeven (bps por lado) | 20.5437 | 12.9831 | 9.6035 | 6.4455 | 54.9298 | 28.0313 | 18.9416 | 11.6791 |
| alavancagem média (Σ|w|) | 1.0000 | 1.7380 | 2.4759 | 3.9501 | 1.7380 | 2.4759 | 3.2139 | 4.6854 |
| views ativas por dia (média) | 0.7380 | 0.7380 | 0.7380 | 0.7380 | 0.7380 | 0.7380 | 0.7380 | 0.7380 |
| perna de mercado (composta) | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 |
| tilt (soma das contribuições diárias) | -0.1184 | -0.1140 | -0.1096 | -0.1010 | 0.0035 | 0.0070 | 0.0105 | 0.0191 |
| benchmark acumulado | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 |
| excesso acumulado (líquido − benchmark) | -0.1439 | -0.1514 | -0.1592 | -0.1764 | -0.0094 | -0.0191 | -0.0292 | -0.0487 |

## Giro — as duas checagens obrigatórias do D8

O custo não vem de negociar muito, vem de negociar contra si mesmo: **giro desfeito em 1–2 pregões** é o mecanismo que destruiu a GTAA diária citada na pesquisa do D8. Se ele for alto, a saída prevista **não** é abandonar o H = 1 dia — é banda de não-negociação.

- **Σ\|w\| ≤ 1:** giro diário médio 0.219 · desfeito em 1–2 pregões 0.335 · custo de breakeven 20.54 bps/lado (premissa: 2.0)
- **Σ\|w\| ≤ 2:** giro diário médio 0.356 · desfeito em 1–2 pregões 0.330 · custo de breakeven 12.98 bps/lado (premissa: 2.0)
- **Σ\|w\| ≤ 3:** giro diário médio 0.493 · desfeito em 1–2 pregões 0.327 · custo de breakeven 9.60 bps/lado (premissa: 2.0)
- **Σ\|w\| ≤ 5:** giro diário médio 0.771 · desfeito em 1–2 pregões 0.325 · custo de breakeven 6.45 bps/lado (premissa: 2.0)
- **tilt ≤ 1:** giro diário médio 0.141 · desfeito em 1–2 pregões 0.318 · custo de breakeven 54.93 bps/lado (premissa: 2.0)
- **tilt ≤ 2:** giro diário médio 0.280 · desfeito em 1–2 pregões 0.320 · custo de breakeven 28.03 bps/lado (premissa: 2.0)
- **tilt ≤ 3:** giro diário médio 0.420 · desfeito em 1–2 pregões 0.321 · custo de breakeven 18.94 bps/lado (premissa: 2.0)
- **tilt ≤ 5:** giro diário médio 0.700 · desfeito em 1–2 pregões 0.321 · custo de breakeven 11.68 bps/lado (premissa: 2.0)

## Leitura

**A carteira perde do comprar-e-segurar SPY**: +15.7% contra +30.1% do benchmark no teto mais apertado, e a distância AUMENTA conforme o teto afrouxa.

**O custo não é o culpado.** O retorno BRUTO já é +17.6%, muito abaixo do benchmark, e o custo de breakeven (20.5 bps/lado) é 10.3× a premissa de 2 bps. Há folga larga de custo; o problema é o retorno bruto.

**O mecanismo suspeito era mecânico, não da view.** O teto de carteira escala TODAS as pontas pelo mesmo fator, inclusive a de SPY que vem do prior. Com a view ativa em 74% dos pregões, parte do orçamento de Σ|w| sai do SPY para o par TIP/TLT — numa janela em que o SPY fez +30.1%, reduzir exposição a ele custa caro por si só. A seção seguinte mede o tamanho disso.

**Giro desfeito em 1–2 pregões: 33%.** Um terço do que se negocia é desfeito em dois pregões. É material, mas com a folga de custo acima não é o que está segurando o resultado — entra como insumo da revisão condicional do D1 (banda de não-negociação), não como veredito sobre o H.


## Onde o teto corta — carteira inteira × só o tilt

Mesma varredura, dois escopos. `Σ|w| ≤ t` escala tudo; `tilt ≤ t` corta só `Σ|w − w_mkt|` e entrega a perna de mercado inteira. **Isto mede, não decide:** a D12 (nível do teto) segue esperando o `c` da Lia, na ordem que ela propôs — entra o `c`, mede-se Σ|w| de novo, aí se decide o teto.

> Os rótulos NÃO são comparáveis entre si. `tilt ≤ t` limita o desvio, não a carteira: com w_mkt = 100% SPY, Σ|w| pode chegar a 1 + t. Compare pela **alavancagem medida**, que é a coluna ao lado.

| escopo | teto | Σ\|w\| medida | líquido | excesso | tilt (soma diária) | giro/dia |
|---|---|---|---|---|---|---|
| carteira | 1 | 1.00 | +15.72% | -14.39 pp | -11.84% | 0.219 |
| só o tilt | 1 | 1.74 | +29.18% | -0.94 pp | +0.35% | 0.141 |
| carteira | 2 | 1.74 | +14.98% | -15.14 pp | -11.40% | 0.356 |
| só o tilt | 2 | 2.48 | +28.21% | -1.91 pp | +0.70% | 0.280 |
| carteira | 3 | 2.48 | +14.20% | -15.92 pp | -10.96% | 0.493 |
| só o tilt | 3 | 3.21 | +27.20% | -2.92 pp | +1.05% | 0.420 |
| carteira | 5 | 3.95 | +12.48% | -17.64 pp | -10.10% | 0.771 |
| só o tilt | 5 | 4.69 | +25.25% | -4.87 pp | +1.91% | 0.700 |

**No teto 1, preservar a perna de mercado muda o excesso em +13.45 pp** (-14.39 pp → -0.94 pp), a um custo de alavancagem de 1.00 → 1.74 de Σ|w| médio. Com o escopo no tilt a carteira **continua perdendo** do comprar-e-segurar SPY.


**A mesma comparação com Σ|w| IGUAL** (o rótulo engana, a alavancagem medida não):

- Σ|w| = **1.74**: `Σ\|w\| ≤ 2` dá -15.14 pp de excesso, `tilt ≤ 1` dá -0.94 pp — diferença de **+14.19 pp** só por causa de ONDE o teto corta, com o mesmo tamanho de carteira.
- Σ|w| = **2.48**: `Σ\|w\| ≤ 3` dá -15.92 pp de excesso, `tilt ≤ 2` dá -1.91 pp — diferença de **+14.02 pp** só por causa de ONDE o teto corta, com o mesmo tamanho de carteira.

A parcela de tilt é o que separa os dois desenhos: -11.84% no corte de carteira contra +0.35% no corte de tilt. No corte de carteira essa parcela mistura duas coisas — o tilt da view **e** o pedaço da perna de mercado que o corte tirou; no corte de tilt ela é só a view. A diferença entre as duas é a conta do que o escopo do teto cobra por si só.


## De onde veio a mudança contra a rodada de 05/08 — atribuição medida

> **Seção escrita à mão** (o resto do arquivo é gerado pelo script; re-rodar
> `backtest_v1.py` apaga esta parte). Existe uma vez só: é a atribuição da
> troca de dado do G7, não uma métrica recorrente. Todos os números abaixo são
> do **escopo de carteira** (`Σ|w| ≤ 1`), que era o único que existia quando
> foram medidos.

A rodada anterior deu **+8,6%** no teto ≤ 1 contra **+26,2%** do benchmark. Esta
dá **+15,7%** contra **+30,1%**. Duas coisas mudaram no dado ao mesmo tempo — o
re-pull do G7 corrigiu o nível de TIP e TLT **e** esticou a janela em 21 pregões
— então rodei as três combinações para não atribuir no chute:

| Rodada (teto ≤ 1) | Pregões | Líquido | Benchmark | Excesso |
|---|---|---|---|---|
| parquet antigo (05/08) | 353 | +8,61% | +26,20% | −17,59 pp |
| parquet novo, **truncado** em 2026-07-08 | 353 | +9,43% | +26,20% | −16,77 pp |
| parquet novo, janela cheia | 374 | +15,72% | +30,12% | −14,39 pp |

- **A correção do dado vale +0,82 pp** (linha 1 → 2), com o benchmark **idêntico**
  até a 4ª casa. Era esperado que só mexesse na estratégia: o deslocamento de
  nível atingiu só TIP e TLT, e o retorno close-a-close deles é igual ao antigo
  em todos os pregões **menos um** — 2026-06-01, o ex-dividendo que entrou no
  pull novo (TIP +115 bps, TLT +39 bps de diferença nesse dia). O par TIP/TLT é
  exatamente o que a view 2.2 monta, então um dia errado nele passa direto para
  o resultado. Efeito cresce com o teto: **+4,03 pp** no teto ≤ 5.
- **Os 21 pregões novos valem +6,29 pp** de retorno acumulado (linha 2 → 3),
  contra +3,92 pp do benchmark. Descontando a base, o retorno **do sub-período**
  é de **+5,75% da estratégia contra +3,11% do SPY**: **na amostra nova a
  estratégia bateu o benchmark**, e o excesso encolheu de −17,59 pp para
  −14,39 pp.

**O que isso NÃO muda:** o veredito da rodada anterior continua de pé. A carteira
segue perdendo do comprar-e-segurar SPY em toda a varredura de teto, e a
distância segue aumentando conforme o teto afrouxa — o mecanismo levantado em
05/08 (o teto escala a perna de SPY junto com o tilt) não foi tocado por dado
nenhum. 21 pregões bons não são evidência contra 374. **Ele agora está medido**
na seção "Onde o teto corta", desta sessão: com o teto no tilt o excesso vai de
−14,39 pp a −0,94 pp, e a parcela de tilt sai de −11,84% para +0,35%.

**A duration medida (D11) não se moveu:** 8,31 a 8,38, os mesmos valores da
rodada anterior. A correção do G7 é multiplicativa e constante, então some na
regressão de retorno contra Δbreakeven — como previsto ao conferir o G7.
