# Backtest do v1 — BL com as views ativas (I5)

> Gerado por `scripts/backtest_v1.py`. Benchmark = comprar e segurar SPY (consequência do `w_mkt` do prior CAPM). Custo de **2.0 bps por lado** sobre o giro contra o peso derivado (D8). Uma coluna por teto de alavancagem — **o teto é decisão humana; a varredura mede, não escolhe.**

- janela: **2025-02-10 a 2026-08-06** (374 pregões)
- views ativas: **2.2 inflação** · **2.3 Fed** · **15b incerteza** · **15g B com β próprio**. As duas últimas entraram em 2026-08-10 (D15a/D15b/D15c fechadas + item 4 da D22 medido na D22e); a 15b é **direcional** (`P[SPY] = 2`) e vive só em dia de anúncio
- ⚠️ **a carteira NÃO é neutra em mercado, e nunca foi**: o ΣP mediano das views é +0,96 (2.2), +1,74 (2.3), +1,24 (15g) e +2,00 (15b) — `P[SPY] = 0` significa que a view não toma posição no SPY, não que ela seja neutra (`Dump/analises/Ortogonalidade.md`)
- demeanagem da 2.3: média expansiva **semeada** com 206 pregões anteriores à janela (2024-04 a 2025-02, dado passado — não lookahead). Sem semente o primeiro dia demeana por 0,0; o sinal líquido sai 22% positivo, contra 34% com semente
- duration do breakeven: **medida** no par da própria view, janela expansiva — variou de **8.31 a 8.38** na amostra (a espec supunha "~8"; o dado confirmou, e agora o número é medido em vez de suposto)
- camada tática v2 (sleeves da D28): **LIGADA** (D28.13) — M4 recessão EUA 2025, M9 Câmara. Os números desta tabela **já incluem** o overlay das sleeves
- régua do Ω (Lia): **LIGADA**, nível **1** (decisão 6q, 13/08) — o `c` por view e por pregão dosa a confiança de cada view antes do teto, e o veto de liquidez dela desativa view sem negociação no slot
- camada tática antiga (orçamentos de drift, 12c): **desligada** — os orçamentos são parâmetro de reunião

- **duas varreduras de escopo do teto:** `Σ|w| ≤ t` corta a carteira inteira; `tilt ≤ t` corta só `Σ|w − w_mkt|` e deixa a perna de mercado do prior intacta

| métrica | Σ\|w\| ≤ 1 | Σ\|w\| ≤ 2 | Σ\|w\| ≤ 3 | Σ\|w\| ≤ 5 | tilt ≤ 1 | tilt ≤ 2 | tilt ≤ 3 | tilt ≤ 5 |
|---|---|---|---|---|---|---|---|---|
| pregões | 374.0000 | 374.0000 | 374.0000 | 374.0000 | 374.0000 | 374.0000 | 374.0000 | 374.0000 |
| retorno acumulado bruto | 0.1881 | 0.2587 | 0.3488 | 0.4713 | 0.3717 | 0.4475 | 0.5159 | 0.6734 |
| retorno acumulado líquido | 0.1526 | 0.1876 | 0.2376 | 0.2831 | 0.3316 | 0.3649 | 0.3894 | 0.4582 |
| retorno médio diário líquido | 0.0004 | 0.0005 | 0.0006 | 0.0008 | 0.0008 | 0.0009 | 0.0010 | 0.0011 |
| vol anualizada | 0.0584 | 0.0988 | 0.1391 | 0.2093 | 0.1764 | 0.1884 | 0.2115 | 0.2625 |
| sharpe anualizado (excesso zero) | 1.6673 | 1.2221 | 1.1020 | 0.9071 | 1.1815 | 1.2062 | 1.1531 | 1.0990 |
| giro diário médio | 0.4058 | 0.7776 | 1.1508 | 1.8308 | 0.3963 | 0.7862 | 1.1653 | 1.8415 |
| giro desfeito em 1–2 pregões | 0.4268 | 0.4232 | 0.4230 | 0.4149 | 0.4188 | 0.4210 | 0.4210 | 0.4173 |
| custo pago (fração do patrimônio) | 0.0304 | 0.0582 | 0.0861 | 0.1369 | 0.0296 | 0.0588 | 0.0872 | 0.1377 |
| custo de breakeven (bps por lado) | 11.5280 | 8.1618 | 7.2868 | 6.1152 | 22.8685 | 13.4705 | 10.3041 | 8.2173 |
| alavancagem média (Σ|w|) | 1.0000 | 1.9471 | 2.8834 | 4.6866 | 1.9146 | 2.8232 | 3.7261 | 5.4737 |
| views ativas por dia (média) | 1.9920 | 1.9920 | 1.9920 | 1.9920 | 1.9920 | 1.9920 | 1.9920 | 1.9920 |
| perna de mercado (composta) | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 |
| tilt (soma das contribuições diárias) | -0.1119 | -0.0495 | 0.0268 | 0.1319 | 0.0522 | 0.1092 | 0.1622 | 0.2791 |
| benchmark acumulado | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 | 0.3012 |
| excesso acumulado (líquido − benchmark) | -0.1486 | -0.1136 | -0.0636 | -0.0181 | 0.0304 | 0.0637 | 0.0882 | 0.1570 |

## Giro — as duas checagens obrigatórias do D8

O custo não vem de negociar muito, vem de negociar contra si mesmo: **giro desfeito em 1–2 pregões** é o mecanismo que destruiu a GTAA diária citada na pesquisa do D8. Se ele for alto, a saída prevista **não** é abandonar o H = 1 dia — é banda de não-negociação.

- **Σ\|w\| ≤ 1:** giro diário médio 0.406 · desfeito em 1–2 pregões 0.427 · custo de breakeven 11.53 bps/lado (premissa: 2.0)
- **Σ\|w\| ≤ 2:** giro diário médio 0.778 · desfeito em 1–2 pregões 0.423 · custo de breakeven 8.16 bps/lado (premissa: 2.0)
- **Σ\|w\| ≤ 3:** giro diário médio 1.151 · desfeito em 1–2 pregões 0.423 · custo de breakeven 7.29 bps/lado (premissa: 2.0)
- **Σ\|w\| ≤ 5:** giro diário médio 1.831 · desfeito em 1–2 pregões 0.415 · custo de breakeven 6.12 bps/lado (premissa: 2.0)
- **tilt ≤ 1:** giro diário médio 0.396 · desfeito em 1–2 pregões 0.419 · custo de breakeven 22.87 bps/lado (premissa: 2.0)
- **tilt ≤ 2:** giro diário médio 0.786 · desfeito em 1–2 pregões 0.421 · custo de breakeven 13.47 bps/lado (premissa: 2.0)
- **tilt ≤ 3:** giro diário médio 1.165 · desfeito em 1–2 pregões 0.421 · custo de breakeven 10.30 bps/lado (premissa: 2.0)
- **tilt ≤ 5:** giro diário médio 1.842 · desfeito em 1–2 pregões 0.417 · custo de breakeven 8.22 bps/lado (premissa: 2.0)

## Leitura

**A carteira perde do comprar-e-segurar SPY** no teto de carteira mais apertado: +15.3% contra +30.1% do benchmark (-14.86 pp).

**Folga de custo.** O retorno BRUTO é +18.8% e o custo de breakeven (11.5 bps/lado) é 5.8× a premissa de 2 bps — o resultado não está sendo decidido pelo custo.

**O escopo do teto é mecânico, não da view.** O teto de carteira escala TODAS as pontas pelo mesmo fator, inclusive a de SPY que vem do prior. Com 1.99 view(s) ativa(s) por pregão em média, parte do orçamento de Σ|w| sai do SPY para os pares das views — numa janela em que o SPY fez +30.1%, reduzir exposição a ele custa caro por si só. A seção seguinte mede o tamanho disso.

**Giro desfeito em 1–2 pregões: 43%.** Essa fração do que se negocia é desfeita em dois pregões. É material, mas com a folga de custo acima não é o que está segurando o resultado — entra como insumo da revisão condicional do D1 (banda de não-negociação), não como veredito sobre o H.


## Onde o teto corta — carteira inteira × só o tilt

Mesma varredura, dois escopos. `Σ|w| ≤ t` escala tudo; `tilt ≤ t` corta só `Σ|w − w_mkt|` e entrega a perna de mercado inteira. **Isto mede, não decide:** a D12 (nível do teto) segue aberta. O `c` da Lia já entrou (6q, nível 1), que era o passo 1 da ordem proposta por ela; esta tabela é o passo 2 — a Σ|w| medida COM a régua —, e o passo 3, escolher o teto, é da reunião.

> Os rótulos NÃO são comparáveis entre si. `tilt ≤ t` limita o desvio, não a carteira: com w_mkt = 100% SPY, Σ|w| pode chegar a 1 + t. Compare pela **alavancagem medida**, que é a coluna ao lado.

| escopo | teto | Σ\|w\| medida | líquido | excesso | tilt (soma diária) | giro/dia |
|---|---|---|---|---|---|---|
| carteira | 1 | 1.00 | +15.26% | -14.86 pp | -11.19% | 0.406 |
| só o tilt | 1 | 1.91 | +33.16% | +3.04 pp | +5.22% | 0.396 |
| carteira | 2 | 1.95 | +18.76% | -11.36 pp | -4.95% | 0.778 |
| só o tilt | 2 | 2.82 | +36.49% | +6.37 pp | +10.92% | 0.786 |
| carteira | 3 | 2.88 | +23.76% | -6.36 pp | +2.68% | 1.151 |
| só o tilt | 3 | 3.73 | +38.94% | +8.82 pp | +16.22% | 1.165 |
| carteira | 5 | 4.69 | +28.31% | -1.81 pp | +13.19% | 1.831 |
| só o tilt | 5 | 5.47 | +45.82% | +15.70 pp | +27.91% | 1.842 |

**No teto 1, preservar a perna de mercado muda o excesso em +17.90 pp** (-14.86 pp → +3.04 pp), a um custo de alavancagem de 1.00 → 1.91 de Σ|w| médio. Com o escopo no tilt a carteira **passa a bater** o comprar-e-segurar SPY.

A parcela de tilt é o que separa os dois desenhos: -11.19% no corte de carteira contra +5.22% no corte de tilt. No corte de carteira essa parcela mistura duas coisas — o tilt da view **e** o pedaço da perna de mercado que o corte tirou; no corte de tilt ela é só a view. A diferença entre as duas é a conta do que o escopo do teto cobra por si só.


## Robustez γ (favorite-longshot) — promessa da seção 9

O v1 roda em **γ = 1** (D1.1: sem correção — 9 mercados resolvidos não calibram curva própria, e importar γ de aposta esportiva mexeria a mediana sem âncora no nosso dado). A coluna existe para **reportar**, não para escolher: se o resultado só sobrevive em um γ, isso tem de aparecer.

Medido no escopo de referência (**tilt ≤ 1**), com a semente da 2.3 recalculada em cada γ — a surpresa depende dele.

| γ | excesso × SPY | líquido | sharpe | Σ\|w\| média | giro diário |
|---|---|---|---|---|---|
| 1 | +3.04 pp | +33.2% | 1.18 | 1.91 | 0.396 |
| 1.1 | +3.60 pp | +33.7% | 1.20 | 1.91 | 0.399 |
| 1.25 | +3.89 pp | +34.0% | 1.21 | 1.91 | 0.401 |

**Faixa do excesso na varredura: +3.04 pp a +3.89 pp** — o sinal do resultado **não** depende do γ nesta janela.


## Limitações declaradas — leia antes de citar o número

> Obrigatório pela **D22/D23b**, e escrito aqui porque o lugar de uma limitação é o artefato que produz o número, não a seção de quem o cita.

**1. O excesso da entrega NÃO é desempenho das views novas.** Medida uma a uma contra o v1 anterior de duas views (`Dump/analises/Views_novas.md`), a **15b** entrega quase tudo num único pregão — tirados os três maiores dias, o Δ dela vira **negativo** — e a **15g** mede **negativo** no backtest. As duas têm acerto de sinal de ~49%, ou seja cara ou coroa. Pela D22 sinal fraco **não reprova** (a régua de admissão é mecanismo, não performance), mas o número-título não pode ser lido como se as duas o tivessem carregado.

**2. Cobertura desigual — cada view vive num número diferente de pregões:**

- `2.3_fed`: **312 de 374** pregões (83%)
- `2.2_inflacao`: **253 de 374** pregões (68%)
- `B_trajetoria_propria`: **154 de 374** pregões (41%)
- `incerteza_anuncio`: **26 de 374** pregões (7%)

A 15b vive só em dia de anúncio, **por desenho**; a 15g acaba junto com o mercado de trajetória (não há mercado de 2026 no `data/`). Média de views por pregão: **1.99** de 4.

**3. O Ω é diagonal e não enxerga correlação entre views.** Com ρ +0,673 entre o sinal-fonte da 15g e o da 2.2 (`Dump/analises/Ortogonalidade.md`), isso deixou de ser hipotético: duas views correlacionadas entram como se fossem informação independente, e o BL soma confiança que não existe. É **limitação de modelo declarada** (D15a, D22e), não bug — o Ω da Lia dosa cada view, não o par.

**4. Horizonte do Q (D4.1) segue aberto, fora do caminho crítico.** Nenhuma das quatro views tem `horizonte_q_dias ≠ 1`, então o empilhamento é homogêneo aqui. O caso concreto medido está na view C, que o `stack_views` **recusou** empilhar por Q acumulado em k dias — ela ficou fora do v1 (D23f), e é o exemplo de que a limitação morde de verdade.

**5. O conjunto de views está FECHADO em quatro** (D23e). A camada tática ANTIGA (orçamentos de drift, 12c) segue desligada; a camada v2 está **LIGADA** (D28.13) e o overlay das sleeves entra nos números acima.

