# Backtest do v1 — BL com as views ativas (I5)

> Gerado por `scripts/backtest_v1.py`. Benchmark = comprar e segurar SPY (consequência do `w_mkt` do prior CAPM). Custo de **2.0 bps por lado** sobre o giro contra o peso derivado (D8). Uma coluna por teto de alavancagem — **o teto é decisão humana; a varredura mede, não escolhe.**

- janela: **2025-02-10 a 2026-08-06** (374 pregões)
- views ativas: **2.2 inflação** · **2.3 Fed** · **15b incerteza** · **15g B com β próprio**. As duas últimas entraram em 2026-08-10 (D15a/D15b/D15c fechadas + item 4 da D22 medido na D22e); a 15b é **direcional** (`P[SPY] = 2`) e vive só em dia de anúncio
- ⚠️ **a carteira NÃO é neutra em mercado, e nunca foi**: o ΣP mediano das views é +0,96 (2.2), +1,74 (2.3), +1,24 (15g) e +2,00 (15b) — `P[SPY] = 0` significa que a view não toma posição no SPY, não que ela seja neutra (`Dump/analises/Ortogonalidade.md`)
- demeanagem da 2.3: média expansiva **semeada** com 206 pregões anteriores à janela (2024-04 a 2025-02, dado passado — não lookahead). Sem semente o primeiro dia demeana por 0,0; o sinal líquido sai 22% positivo, contra 34% com semente
- duration do breakeven: **medida** no par da própria view, janela expansiva — variou de **8.31 a 8.38** na amostra (a espec supunha "~8"; o dado confirmou, e agora o número é medido em vez de suposto)
- camada tática v2 (sleeves da D28): **LIGADA** (D28.13) — M4 recessão EUA 2025, M9 Câmara. Os números desta tabela **já incluem** o overlay das sleeves
- camada tática antiga (orçamentos de drift, 12c): **desligada** — os orçamentos são parâmetro de reunião

- **duas varreduras de escopo do teto:** `Σ|w| ≤ t` corta a carteira inteira; `tilt ≤ t` corta só `Σ|w − w_mkt|` e deixa a perna de mercado do prior intacta

| métrica | Σ\|w\| ≤ 1 | Σ\|w\| ≤ 2 | Σ\|w\| ≤ 3 | Σ\|w\| ≤ 5 | tilt ≤ 1 | tilt ≤ 2 | tilt ≤ 3 | tilt ≤ 5 |
|---|---|---|---|---|---|---|---|---|
| pregões | 374.0000 | 374.0000 | 374.0000 | 374.0000 | 374.0000 | 374.0000 | 374.0000 | 374.0000 |
| retorno acumulado bruto | 0.1451 | 0.2163 | 0.3105 | 0.4561 | 0.3745 | 0.4597 | 0.5433 | 0.7171 |
| retorno acumulado líquido | 0.1178 | 0.1606 | 0.2235 | 0.3043 | 0.3420 | 0.3926 | 0.4389 | 0.5339 |
| retorno médio diário líquido | 0.0003 | 0.0004 | 0.0006 | 0.0008 | 0.0008 | 0.0010 | 0.0011 | 0.0013 |
| vol anualizada | 0.0507 | 0.0916 | 0.1307 | 0.1996 | 0.1760 | 0.1860 | 0.2070 | 0.2564 |
| sharpe anualizado (excesso zero) | 1.5056 | 1.1411 | 1.1049 | 0.9963 | 1.2136 | 1.2920 | 1.2877 | 1.2520 |
| giro diário médio | 0.3227 | 0.6277 | 0.9196 | 1.4741 | 0.3201 | 0.6297 | 0.9373 | 1.5105 |
| giro desfeito em 1–2 pregões | 0.3951 | 0.3918 | 0.3887 | 0.3812 | 0.3893 | 0.3871 | 0.3875 | 0.3887 |
| custo pago (fração do patrimônio) | 0.0241 | 0.0470 | 0.0688 | 0.1103 | 0.0239 | 0.0471 | 0.0701 | 0.1130 |
| custo de breakeven (bps por lado) | 11.3830 | 8.6095 | 8.2342 | 7.3545 | 28.4727 | 17.1450 | 13.2835 | 10.4337 |
| alavancagem média (Σ|w|) | 1.0000 | 1.9738 | 2.9342 | 4.8061 | 1.9438 | 2.8791 | 3.8147 | 5.6395 |
| views ativas por dia (média) | 2.2353 | 2.2353 | 2.2353 | 2.2353 | 2.2353 | 2.2353 | 2.2353 | 2.2353 |
| perna de mercado (composta) | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 |
| tilt (soma das contribuições diárias) | -0.1494 | -0.0847 | -0.0036 | 0.1186 | 0.0541 | 0.1170 | 0.1788 | 0.3026 |
| benchmark acumulado | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 |
| excesso acumulado (líquido − benchmark) | -0.1834 | -0.1406 | -0.0777 | 0.0031 | 0.0408 | 0.0914 | 0.1377 | 0.2327 |

## Giro — as duas checagens obrigatórias do D8

O custo não vem de negociar muito, vem de negociar contra si mesmo: **giro desfeito em 1–2 pregões** é o mecanismo que destruiu a GTAA diária citada na pesquisa do D8. Se ele for alto, a saída prevista **não** é abandonar o H = 1 dia — é banda de não-negociação.

- **Σ\|w\| ≤ 1:** giro diário médio 0.323 · desfeito em 1–2 pregões 0.395 · custo de breakeven 11.38 bps/lado (premissa: 2.0)
- **Σ\|w\| ≤ 2:** giro diário médio 0.628 · desfeito em 1–2 pregões 0.392 · custo de breakeven 8.61 bps/lado (premissa: 2.0)
- **Σ\|w\| ≤ 3:** giro diário médio 0.920 · desfeito em 1–2 pregões 0.389 · custo de breakeven 8.23 bps/lado (premissa: 2.0)
- **Σ\|w\| ≤ 5:** giro diário médio 1.474 · desfeito em 1–2 pregões 0.381 · custo de breakeven 7.35 bps/lado (premissa: 2.0)
- **tilt ≤ 1:** giro diário médio 0.320 · desfeito em 1–2 pregões 0.389 · custo de breakeven 28.47 bps/lado (premissa: 2.0)
- **tilt ≤ 2:** giro diário médio 0.630 · desfeito em 1–2 pregões 0.387 · custo de breakeven 17.14 bps/lado (premissa: 2.0)
- **tilt ≤ 3:** giro diário médio 0.937 · desfeito em 1–2 pregões 0.387 · custo de breakeven 13.28 bps/lado (premissa: 2.0)
- **tilt ≤ 5:** giro diário médio 1.511 · desfeito em 1–2 pregões 0.389 · custo de breakeven 10.43 bps/lado (premissa: 2.0)

## Leitura

**A carteira perde do comprar-e-segurar SPY** no teto de carteira mais apertado: +11.8% contra +30.1% do benchmark (-18.34 pp).

**Folga de custo.** O retorno BRUTO é +14.5% e o custo de breakeven (11.4 bps/lado) é 5.7× a premissa de 2 bps — o resultado não está sendo decidido pelo custo.

**O escopo do teto é mecânico, não da view.** O teto de carteira escala TODAS as pontas pelo mesmo fator, inclusive a de SPY que vem do prior. Com 2.24 view(s) ativa(s) por pregão em média, parte do orçamento de Σ|w| sai do SPY para os pares das views — numa janela em que o SPY fez +30.1%, reduzir exposição a ele custa caro por si só. A seção seguinte mede o tamanho disso.

**Giro desfeito em 1–2 pregões: 40%.** Um terço do que se negocia é desfeito em dois pregões. É material, mas com a folga de custo acima não é o que está segurando o resultado — entra como insumo da revisão condicional do D1 (banda de não-negociação), não como veredito sobre o H.


## Onde o teto corta — carteira inteira × só o tilt

Mesma varredura, dois escopos. `Σ|w| ≤ t` escala tudo; `tilt ≤ t` corta só `Σ|w − w_mkt|` e entrega a perna de mercado inteira. **Isto mede, não decide:** a D12 (nível do teto) segue esperando o `c` da Lia, na ordem que ela propôs — entra o `c`, mede-se Σ|w| de novo, aí se decide o teto.

> Os rótulos NÃO são comparáveis entre si. `tilt ≤ t` limita o desvio, não a carteira: com w_mkt = 100% SPY, Σ|w| pode chegar a 1 + t. Compare pela **alavancagem medida**, que é a coluna ao lado.

| escopo | teto | Σ\|w\| medida | líquido | excesso | tilt (soma diária) | giro/dia |
|---|---|---|---|---|---|---|
| carteira | 1 | 1.00 | +11.78% | -18.34 pp | -14.94% | 0.323 |
| só o tilt | 1 | 1.94 | +34.20% | +4.08 pp | +5.41% | 0.320 |
| carteira | 2 | 1.97 | +16.06% | -14.06 pp | -8.47% | 0.628 |
| só o tilt | 2 | 2.88 | +39.26% | +9.14 pp | +11.70% | 0.630 |
| carteira | 3 | 2.93 | +22.35% | -7.77 pp | -0.36% | 0.920 |
| só o tilt | 3 | 3.81 | +43.89% | +13.77 pp | +17.88% | 0.937 |
| carteira | 5 | 4.81 | +30.43% | +0.31 pp | +11.86% | 1.474 |
| só o tilt | 5 | 5.64 | +53.39% | +23.27 pp | +30.26% | 1.511 |

**No teto 1, preservar a perna de mercado muda o excesso em +22.42 pp** (-18.34 pp → +4.08 pp), a um custo de alavancagem de 1.00 → 1.94 de Σ|w| médio. Com o escopo no tilt a carteira **passa a bater** o comprar-e-segurar SPY.

A parcela de tilt é o que separa os dois desenhos: -14.94% no corte de carteira contra +5.41% no corte de tilt. No corte de carteira essa parcela mistura duas coisas — o tilt da view **e** o pedaço da perna de mercado que o corte tirou; no corte de tilt ela é só a view. A diferença entre as duas é a conta do que o escopo do teto cobra por si só.


## Robustez γ (favorite-longshot) — promessa da seção 9

O v1 roda em **γ = 1** (D1.1: sem correção — 9 mercados resolvidos não calibram curva própria, e importar γ de aposta esportiva mexeria a mediana sem âncora no nosso dado). A coluna existe para **reportar**, não para escolher: se o resultado só sobrevive em um γ, isso tem de aparecer.

Medido no escopo de referência (**tilt ≤ 1**), com a semente da 2.3 recalculada em cada γ — a surpresa depende dele.

| γ | excesso × SPY | líquido | sharpe | Σ\|w\| média | giro diário |
|---|---|---|---|---|---|
| 1 | +4.08 pp | +34.2% | 1.21 | 1.94 | 0.320 |
| 1.1 | +4.38 pp | +34.5% | 1.22 | 1.94 | 0.323 |
| 1.25 | +4.41 pp | +34.5% | 1.22 | 1.94 | 0.325 |

**Faixa do excesso na varredura: +4.08 pp a +4.41 pp** — o sinal do resultado **não** depende do γ nesta janela.


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

**5. O conjunto de views está FECHADO em quatro** (D23e). A camada tática ANTIGA (orçamentos de drift, 12c) segue desligada; a camada v2 está **LIGADA** (D28.13) e o overlay das sleeves entra nos números acima.

