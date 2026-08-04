# Surpresa de FOMC sem o ZQ — proxy pelo T-bill de 3 meses (6.2)

> Gerado por `scripts/surpresa_fomc.py`. **Mede; não escolhe fonte.** Surpresa = ΔDTB3 do dia do anúncio, em bps, no lugar da variação do fed funds future.

- reuniões de FOMC com ΔDTB3 disponível: **36** (2022-01-26 a 2026-06-17)
- surpresa: mediana +0.0 bps · desvio 3.3 bps · mín -11.0 · máx +4.0
- reuniões com |surpresa| > 5 bps: 3 de 36

β do event-study (fração de retorno por bp de surpresa de ALTA):

| ativo | β | t | sinal esperado | bate? |
|---|---|---|---|---|
| SPY | -0.001359 | -2.09 | - | ✅ |
| TIP | -0.000459 | -1.65 | - | ✅ |
| TLT | -0.000241 | -0.50 | - | ✅ |
| XLE | -0.000530 | -0.69 | ? | — |
| XLF | -0.001237 | -1.90 | ? | — |
| XLK | -0.001488 | -1.60 | - | ✅ |
| XLP | -0.001282 | -2.70 | - | ✅ |
| XLU | -0.000203 | -0.36 | - | ✅ |
| XLV | -0.001058 | -2.28 | - | ✅ |

- sinais coerentes com Bernanke-Kuttner: **7 de 7** (XLE e XLF não têm sinal previsto pela literatura)
- β com |t| > 2: **3** de 9
- dispersão dos β em torno do SPY (é ela que dá conteúdo ao P): 0.004632

## O que este teste NÃO resolve

O proxy serve para estimar β (surpresa realizada no dia). Ele **não** entrega o `e_ff_bps` — a expectativa de Δtaxa da PRÓXIMA reunião, que é o benchmark contra o qual o E_poly é comparado. Para isso falta a taxa efetiva corrente (`DFF` no FRED, mesmo formato dos três CSVs já entregues): o excesso do T-bill de 3 meses sobre a taxa efetiva é a expectativa embutida de mudança nos próximos ~3 meses.

