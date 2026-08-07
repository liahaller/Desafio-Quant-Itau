# Backtest do v1 — BL com as views ativas (I5)

> Gerado por `scripts/backtest_v1.py`. Benchmark = comprar e segurar SPY (consequência do `w_mkt` do prior CAPM). Custo de **2.0 bps por lado** sobre o giro contra o peso derivado (D8). Uma coluna por teto de alavancagem — **o teto é decisão humana; a varredura mede, não escolhe.**

- janela: **2025-02-10 a 2026-08-06** (374 pregões)
- views ativas: **2.2 inflação**. A 2.3 e a B ficam fora por insumo que não chegou (DFF/G8 e ZQ de dezembro), não por cascata
- duration do breakeven: **medida** no par da própria view, janela expansiva — variou de **8.31 a 8.38** na amostra (a espec supunha "~8"; o dado confirmou, e agora o número é medido em vez de suposto)
- camada tática: **desligada** — os orçamentos são parâmetro de reunião

| métrica | Σ\|w\| ≤ 1 | Σ\|w\| ≤ 2 | Σ\|w\| ≤ 3 | Σ\|w\| ≤ 5 |
|---|---|---|---|---|
| pregões | 374.0000 | 374.0000 | 374.0000 | 374.0000 |
| retorno acumulado bruto | 0.1764 | 0.1809 | 0.1850 | 0.1917 |
| retorno acumulado líquido | 0.1572 | 0.1498 | 0.1420 | 0.1248 |
| retorno médio diário líquido | 0.0004 | 0.0004 | 0.0004 | 0.0003 |
| vol anualizada | 0.0897 | 0.0939 | 0.1006 | 0.1194 |
| sharpe anualizado (excesso zero) | 1.1423 | 1.0485 | 0.9395 | 0.7232 |
| giro diário médio | 0.2192 | 0.3559 | 0.4933 | 0.7710 |
| giro desfeito em 1–2 pregões | 0.3346 | 0.3296 | 0.3272 | 0.3249 |
| custo pago (fração do patrimônio) | 0.0164 | 0.0266 | 0.0369 | 0.0577 |
| custo de breakeven (bps por lado) | 20.5437 | 12.9831 | 9.6035 | 6.4455 |
| alavancagem média (Σ|w|) | 1.0000 | 1.7380 | 2.4759 | 3.9501 |
| views ativas por dia (média) | 0.7380 | 0.7380 | 0.7380 | 0.7380 |
| benchmark acumulado | 0.3012 | 0.3012 | 0.3012 | 0.3012 |
| excesso acumulado (líquido − benchmark) | -0.1439 | -0.1514 | -0.1592 | -0.1764 |

## Giro — as duas checagens obrigatórias do D8

O custo não vem de negociar muito, vem de negociar contra si mesmo: **giro desfeito em 1–2 pregões** é o mecanismo que destruiu a GTAA diária citada na pesquisa do D8. Se ele for alto, a saída prevista **não** é abandonar o H = 1 dia — é banda de não-negociação.

- **Σ\|w\| ≤ 1:** giro diário médio 0.219 · desfeito em 1–2 pregões 0.335 · custo de breakeven 20.54 bps/lado (premissa: 2.0)
- **Σ\|w\| ≤ 2:** giro diário médio 0.356 · desfeito em 1–2 pregões 0.330 · custo de breakeven 12.98 bps/lado (premissa: 2.0)
- **Σ\|w\| ≤ 3:** giro diário médio 0.493 · desfeito em 1–2 pregões 0.327 · custo de breakeven 9.60 bps/lado (premissa: 2.0)
- **Σ\|w\| ≤ 5:** giro diário médio 0.771 · desfeito em 1–2 pregões 0.325 · custo de breakeven 6.45 bps/lado (premissa: 2.0)

## Leitura

**A carteira perde do comprar-e-segurar SPY**: +15.7% contra +30.1% do benchmark no teto mais apertado, e a distância AUMENTA conforme o teto afrouxa.

**O custo não é o culpado.** O retorno BRUTO já é +17.6%, muito abaixo do benchmark, e o custo de breakeven (20.5 bps/lado) é 10.3× a premissa de 2 bps. Há folga larga de custo; o problema é o retorno bruto.

**O mecanismo mais provável é mecânico, não da view.** O teto escala TODAS as pontas pelo mesmo fator, inclusive a de SPY que vem do prior. Com a view ativa em 74% dos pregões, parte do orçamento de Σ|w| sai do SPY para o par TIP/TLT — numa janela em que o SPY fez +30.1%, reduzir exposição a ele custa caro por si só. **Questão de desenho em aberto (não decidida aqui):** o teto deve cortar a carteira inteira ou só o TILT da view, deixando a perna de mercado intacta?

**Giro desfeito em 1–2 pregões: 33%.** Um terço do que se negocia é desfeito em dois pregões. É material, mas com a folga de custo acima não é o que está segurando o resultado — entra como insumo da revisão condicional do D1 (banda de não-negociação), não como veredito sobre o H.


## De onde veio a mudança contra a rodada de 05/08 — atribuição medida

> **Seção escrita à mão** (o resto do arquivo é gerado pelo script; re-rodar
> `backtest_v1.py` apaga esta parte). Existe uma vez só: é a atribuição da
> troca de dado do G7, não uma métrica recorrente.

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
nenhum. 21 pregões bons não são evidência contra 374.

**A duration medida (D11) não se moveu:** 8,31 a 8,38, os mesmos valores da
rodada anterior. A correção do G7 é multiplicativa e constante, então some na
regressão de retorno contra Δbreakeven — como previsto ao conferir o G7.
