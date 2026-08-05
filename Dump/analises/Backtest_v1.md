# Backtest do v1 — BL com as views ativas (I5)

> Gerado por `scripts/backtest_v1.py`. Benchmark = comprar e segurar SPY (consequência do `w_mkt` do prior CAPM). Custo de **2.0 bps por lado** sobre o giro contra o peso derivado (D8). Uma coluna por teto de alavancagem — **o teto é decisão humana; a varredura mede, não escolhe.**

- janela: **2025-02-10 a 2026-07-08** (353 pregões)
- views ativas: **2.2 inflação**. A 2.3 e a B ficam fora por insumo que não chegou (DFF/G8 e ZQ de dezembro), não por cascata
- duration do breakeven: **medida** no par da própria view, janela expansiva — variou de **8.31 a 8.38** na amostra (a espec supunha "~8"; o dado confirmou, e agora o número é medido em vez de suposto)
- camada tática: **desligada** — os orçamentos são parâmetro de reunião

| métrica | Σ\|w\| ≤ 1 | Σ\|w\| ≤ 2 | Σ\|w\| ≤ 3 | Σ\|w\| ≤ 5 |
|---|---|---|---|---|
| pregões | 353.0000 | 353.0000 | 353.0000 | 353.0000 |
| retorno acumulado bruto | 0.1032 | 0.1015 | 0.0993 | 0.0936 |
| retorno acumulado líquido | 0.0861 | 0.0738 | 0.0611 | 0.0347 |
| retorno médio diário líquido | 0.0002 | 0.0002 | 0.0002 | 0.0001 |
| vol anualizada | 0.0892 | 0.0941 | 0.1015 | 0.1223 |
| sharpe anualizado (excesso zero) | 0.7058 | 0.5876 | 0.4680 | 0.2601 |
| giro diário médio | 0.2208 | 0.3599 | 0.4997 | 0.7822 |
| giro desfeito em 1–2 pregões | 0.3261 | 0.3216 | 0.3193 | 0.3172 |
| custo pago (fração do patrimônio) | 0.0156 | 0.0254 | 0.0353 | 0.0552 |
| custo de breakeven (bps por lado) | 13.3146 | 8.0942 | 5.7740 | 3.6143 |
| alavancagem média (Σ|w|) | 1.0000 | 1.7394 | 2.4788 | 3.9557 |
| views ativas por dia (média) | 0.7394 | 0.7394 | 0.7394 | 0.7394 |
| benchmark acumulado | 0.2620 | 0.2620 | 0.2620 | 0.2620 |
| excesso acumulado (líquido − benchmark) | -0.1759 | -0.1882 | -0.2008 | -0.2273 |

## Giro — as duas checagens obrigatórias do D8

O custo não vem de negociar muito, vem de negociar contra si mesmo: **giro desfeito em 1–2 pregões** é o mecanismo que destruiu a GTAA diária citada na pesquisa do D8. Se ele for alto, a saída prevista **não** é abandonar o H = 1 dia — é banda de não-negociação.

- **Σ\|w\| ≤ 1:** giro diário médio 0.221 · desfeito em 1–2 pregões 0.326 · custo de breakeven 13.31 bps/lado (premissa: 2.0)
- **Σ\|w\| ≤ 2:** giro diário médio 0.360 · desfeito em 1–2 pregões 0.322 · custo de breakeven 8.09 bps/lado (premissa: 2.0)
- **Σ\|w\| ≤ 3:** giro diário médio 0.500 · desfeito em 1–2 pregões 0.319 · custo de breakeven 5.77 bps/lado (premissa: 2.0)
- **Σ\|w\| ≤ 5:** giro diário médio 0.782 · desfeito em 1–2 pregões 0.317 · custo de breakeven 3.61 bps/lado (premissa: 2.0)

## Leitura

**A carteira perde do comprar-e-segurar SPY**: +8.6% contra +26.2% do benchmark no teto mais apertado, e a distância AUMENTA conforme o teto afrouxa.

**O custo não é o culpado.** O retorno BRUTO já é +10.3%, muito abaixo do benchmark, e o custo de breakeven (13.3 bps/lado) é 6.7× a premissa de 2 bps. Há folga larga de custo; o problema é o retorno bruto.

**O mecanismo mais provável é mecânico, não da view.** O teto escala TODAS as pontas pelo mesmo fator, inclusive a de SPY que vem do prior. Com a view ativa em 74% dos pregões, parte do orçamento de Σ|w| sai do SPY para o par TIP/TLT — numa janela em que o SPY fez +26.2%, reduzir exposição a ele custa caro por si só. **Questão de desenho em aberto (não decidida aqui):** o teto deve cortar a carteira inteira ou só o TILT da view, deixando a perna de mercado intacta?

**Giro desfeito em 1–2 pregões: 33%.** Um terço do que se negocia é desfeito em dois pregões. É material, mas com a folga de custo acima não é o que está segurando o resultado — entra como insumo da revisão condicional do D1 (banda de não-negociação), não como veredito sobre o H.

