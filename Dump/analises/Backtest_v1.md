# Backtest do v1 — BL com as views ativas (I5)

> Gerado por `scripts/backtest_v1.py`. Benchmark = comprar e segurar SPY (consequência do `w_mkt` do prior CAPM). Custo de **2.0 bps por lado** sobre o giro contra o peso derivado (D8). Uma coluna por teto de alavancagem — **o teto é decisão humana; a varredura mede, não escolhe.**

- janela: **2025-02-10 a 2026-08-06** (374 pregões)
- views ativas: **2.2 inflação** · **2.3 Fed** · **15b incerteza** · **15g B com β próprio**. As duas últimas entraram em 2026-08-10 (D15a/D15b/D15c fechadas + item 4 da D22 medido na D22e); a 15b é **direcional** (`P[SPY] = 2`) e vive só em dia de anúncio
- ⚠️ **a carteira NÃO é neutra em mercado, e nunca foi**: o ΣP mediano das views é +0,96 (2.2), +1,74 (2.3), +1,24 (15g) e +2,00 (15b) — `P[SPY] = 0` significa que a view não toma posição no SPY, não que ela seja neutra (`Dump/analises/Ortogonalidade.md`)
- demeanagem da 2.3: média expansiva **semeada** com 206 pregões anteriores à janela (2024-04 a 2025-02, dado passado — não lookahead). Sem semente o primeiro dia demeana por 0,0; o sinal líquido sai 22% positivo, contra 34% com semente
- duration do breakeven: **medida** no par da própria view, janela expansiva — variou de **8.31 a 8.38** na amostra (a espec supunha "~8"; o dado confirmou, e agora o número é medido em vez de suposto)
- camada tática: **desligada** — os orçamentos são parâmetro de reunião

- **duas varreduras de escopo do teto:** `Σ|w| ≤ t` corta a carteira inteira; `tilt ≤ t` corta só `Σ|w − w_mkt|` e deixa a perna de mercado do prior intacta

| métrica | Σ\|w\| ≤ 1 | Σ\|w\| ≤ 2 | Σ\|w\| ≤ 3 | Σ\|w\| ≤ 5 | tilt ≤ 1 | tilt ≤ 2 | tilt ≤ 3 | tilt ≤ 5 |
|---|---|---|---|---|---|---|---|---|
| pregões | 374.0000 | 374.0000 | 374.0000 | 374.0000 | 374.0000 | 374.0000 | 374.0000 | 374.0000 |
| retorno acumulado bruto | 0.1470 | 0.2115 | 0.2994 | 0.4845 | 0.3919 | 0.5045 | 0.6203 | 0.7415 |
| retorno acumulado líquido | 0.1223 | 0.1628 | 0.2249 | 0.3504 | 0.3636 | 0.4454 | 0.5282 | 0.5834 |
| retorno médio diário líquido | 0.0003 | 0.0004 | 0.0006 | 0.0009 | 0.0009 | 0.0010 | 0.0012 | 0.0013 |
| vol anualizada | 0.0461 | 0.0761 | 0.1046 | 0.1597 | 0.1762 | 0.1815 | 0.1929 | 0.2241 |
| sharpe anualizado (excesso zero) | 1.7078 | 1.3732 | 1.3593 | 1.3473 | 1.2736 | 1.4575 | 1.5777 | 1.4935 |
| giro diário médio | 0.2916 | 0.5484 | 0.7900 | 1.2664 | 0.2743 | 0.5364 | 0.7821 | 1.2727 |
| giro desfeito em 1–2 pregões | 0.3723 | 0.3678 | 0.3652 | 0.3630 | 0.3737 | 0.3716 | 0.3686 | 0.3683 |
| custo pago (fração do patrimônio) | 0.0218 | 0.0410 | 0.0591 | 0.0947 | 0.0205 | 0.0401 | 0.0585 | 0.0952 |
| custo de breakeven (bps por lado) | 12.7225 | 9.5641 | 9.1407 | 8.7407 | 34.4646 | 21.5749 | 17.4383 | 12.4341 |
| alavancagem média (Σ|w|) | 0.9986 | 1.9515 | 2.8637 | 4.6052 | 1.9376 | 2.8410 | 3.7193 | 5.4038 |
| views ativas por dia (média) | 2.2353 | 2.2353 | 2.2353 | 2.2353 | 2.2353 | 2.2353 | 2.2353 | 2.2353 |
| perna de mercado (composta) | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 |
| tilt (soma das contribuições diárias) | -0.1481 | -0.0907 | -0.0168 | 0.1272 | 0.0667 | 0.1460 | 0.2232 | 0.3050 |
| benchmark acumulado | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 |
| excesso acumulado (líquido − benchmark) | -0.1789 | -0.1384 | -0.0763 | 0.0492 | 0.0624 | 0.1442 | 0.2270 | 0.2822 |

## Giro — as duas checagens obrigatórias do D8

O custo não vem de negociar muito, vem de negociar contra si mesmo: **giro desfeito em 1–2 pregões** é o mecanismo que destruiu a GTAA diária citada na pesquisa do D8. Se ele for alto, a saída prevista **não** é abandonar o H = 1 dia — é banda de não-negociação.

- **Σ\|w\| ≤ 1:** giro diário médio 0.292 · desfeito em 1–2 pregões 0.372 · custo de breakeven 12.72 bps/lado (premissa: 2.0)
- **Σ\|w\| ≤ 2:** giro diário médio 0.548 · desfeito em 1–2 pregões 0.368 · custo de breakeven 9.56 bps/lado (premissa: 2.0)
- **Σ\|w\| ≤ 3:** giro diário médio 0.790 · desfeito em 1–2 pregões 0.365 · custo de breakeven 9.14 bps/lado (premissa: 2.0)
- **Σ\|w\| ≤ 5:** giro diário médio 1.266 · desfeito em 1–2 pregões 0.363 · custo de breakeven 8.74 bps/lado (premissa: 2.0)
- **tilt ≤ 1:** giro diário médio 0.274 · desfeito em 1–2 pregões 0.374 · custo de breakeven 34.46 bps/lado (premissa: 2.0)
- **tilt ≤ 2:** giro diário médio 0.536 · desfeito em 1–2 pregões 0.372 · custo de breakeven 21.57 bps/lado (premissa: 2.0)
- **tilt ≤ 3:** giro diário médio 0.782 · desfeito em 1–2 pregões 0.369 · custo de breakeven 17.44 bps/lado (premissa: 2.0)
- **tilt ≤ 5:** giro diário médio 1.273 · desfeito em 1–2 pregões 0.368 · custo de breakeven 12.43 bps/lado (premissa: 2.0)

## Leitura

**A carteira perde do comprar-e-segurar SPY** no teto de carteira mais apertado: +12.2% contra +30.1% do benchmark (-17.89 pp).

**Folga de custo.** O retorno BRUTO é +14.7% e o custo de breakeven (12.7 bps/lado) é 6.4× a premissa de 2 bps — o resultado não está sendo decidido pelo custo.

**O escopo do teto é mecânico, não da view.** O teto de carteira escala TODAS as pontas pelo mesmo fator, inclusive a de SPY que vem do prior. Com 2.24 view(s) ativa(s) por pregão em média, parte do orçamento de Σ|w| sai do SPY para os pares das views — numa janela em que o SPY fez +30.1%, reduzir exposição a ele custa caro por si só. A seção seguinte mede o tamanho disso.

**Giro desfeito em 1–2 pregões: 37%.** Um terço do que se negocia é desfeito em dois pregões. É material, mas com a folga de custo acima não é o que está segurando o resultado — entra como insumo da revisão condicional do D1 (banda de não-negociação), não como veredito sobre o H.


## Onde o teto corta — carteira inteira × só o tilt

Mesma varredura, dois escopos. `Σ|w| ≤ t` escala tudo; `tilt ≤ t` corta só `Σ|w − w_mkt|` e entrega a perna de mercado inteira. **Isto mede, não decide:** a D12 (nível do teto) segue esperando o `c` da Lia, na ordem que ela propôs — entra o `c`, mede-se Σ|w| de novo, aí se decide o teto.

> Os rótulos NÃO são comparáveis entre si. `tilt ≤ t` limita o desvio, não a carteira: com w_mkt = 100% SPY, Σ|w| pode chegar a 1 + t. Compare pela **alavancagem medida**, que é a coluna ao lado.

| escopo | teto | Σ\|w\| medida | líquido | excesso | tilt (soma diária) | giro/dia |
|---|---|---|---|---|---|---|
| carteira | 1 | 1.00 | +12.23% | -17.89 pp | -14.81% | 0.292 |
| só o tilt | 1 | 1.94 | +36.36% | +6.24 pp | +6.67% | 0.274 |
| carteira | 2 | 1.95 | +16.28% | -13.84 pp | -9.07% | 0.548 |
| só o tilt | 2 | 2.84 | +44.54% | +14.42 pp | +14.60% | 0.536 |
| carteira | 3 | 2.86 | +22.49% | -7.63 pp | -1.68% | 0.790 |
| só o tilt | 3 | 3.72 | +52.82% | +22.70 pp | +22.32% | 0.782 |
| carteira | 5 | 4.61 | +35.04% | +4.92 pp | +12.72% | 1.266 |
| só o tilt | 5 | 5.40 | +58.34% | +28.22 pp | +30.50% | 1.273 |

**No teto 1, preservar a perna de mercado muda o excesso em +24.14 pp** (-17.89 pp → +6.24 pp), a um custo de alavancagem de 1.00 → 1.94 de Σ|w| médio. Com o escopo no tilt a carteira **passa a bater** o comprar-e-segurar SPY.

A parcela de tilt é o que separa os dois desenhos: -14.81% no corte de carteira contra +6.67% no corte de tilt. No corte de carteira essa parcela mistura duas coisas — o tilt da view **e** o pedaço da perna de mercado que o corte tirou; no corte de tilt ela é só a view. A diferença entre as duas é a conta do que o escopo do teto cobra por si só.


## Robustez γ (favorite-longshot) — promessa da seção 9

O v1 roda em **γ = 1** (D1.1: sem correção — 9 mercados resolvidos não calibram curva própria, e importar γ de aposta esportiva mexeria a mediana sem âncora no nosso dado). A coluna existe para **reportar**, não para escolher: se o resultado só sobrevive em um γ, isso tem de aparecer.

Medido no escopo de referência (**tilt ≤ 1**), com a semente da 2.3 recalculada em cada γ — a surpresa depende dele.

| γ | excesso × SPY | líquido | sharpe | Σ\|w\| média | giro diário |
|---|---|---|---|---|---|
| 1 | +6.24 pp | +36.4% | 1.27 | 1.94 | 0.274 |
| 1.1 | +6.59 pp | +36.7% | 1.28 | 1.94 | 0.278 |
| 1.25 | +6.96 pp | +37.1% | 1.29 | 1.94 | 0.282 |

**Faixa do excesso na varredura: +6.24 pp a +6.96 pp** — o sinal do resultado **não** depende do γ nesta janela.


## Limitações declaradas — leia antes de citar o número

> Obrigatório pela **D22/D23b**, e escrito aqui porque o lugar de uma limitação é o artefato que produz o número, não a seção de quem o cita.

**1. O excesso da entrega NÃO é desempenho das views novas.** Medida uma a uma contra o v1 anterior de duas views (`Dump/analises/Views_novas.md`), a **15b** entrega quase tudo num único pregão — tirados os três maiores dias, o Δ dela vira **negativo** — e a **15g** mede **negativo** no backtest. As duas têm acerto de sinal de ~49%, ou seja cara ou coroa. Pela D22 sinal fraco **não reprova** (a régua de admissão é mecanismo, não performance), mas o número-título não pode ser lido como se as duas o tivessem carregado.

**2. Cobertura desigual — cada view vive num número diferente de pregões:**

- `2.3_fed`: **325 de 374** pregões (87%)
- `2.2_inflacao`: **274 de 374** pregões (73%)
- `B_trajetoria_propria`: **210 de 374** pregões (56%)
- `incerteza_anuncio`: **27 de 374** pregões (7%)

A 15b vive só em dia de anúncio, **por desenho**; a 15g acaba junto com o mercado de trajetória (não há mercado de 2026 no `data/`). Média de views por pregão: **2.24** de 4.

**3. O Ω é diagonal e não enxerga correlação entre views.** Com ρ +0,673 entre o sinal-fonte da 15g e o da 2.2 (`Dump/analises/Ortogonalidade.md`), isso deixou de ser hipotético: duas views correlacionadas entram como se fossem informação independente, e o BL soma confiança que não existe. É **limitação de modelo declarada** (D15a, D22e), não bug — o Ω da Lia dosa cada view, não o par.

**4. Horizonte do Q (D4.1) segue aberto, fora do caminho crítico.** Nenhuma das quatro views tem `horizonte_q_dias ≠ 1`, então o empilhamento é homogêneo aqui. O caso concreto medido está na view C, que o `stack_views` **recusou** empilhar por Q acumulado em k dias — ela ficou fora do v1 (D23f), e é o exemplo de que a limitação morde de verdade.

**5. O conjunto de views está FECHADO em quatro** (D23e) e a **camada tática está desligada** (12c). Nada nesta tabela mede sleeve.

