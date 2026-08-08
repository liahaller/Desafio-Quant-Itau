# Dossiê de limitações do v1 — insumo para o relatório

> **O que é:** consolidação, num lugar só, de tudo que ficou **fora** do v1 e de
> tudo que entrou **com ressalva**. Cada linha traz o número da decisão que a
> fechou e o ponteiro para o artefato que a mede — o relatório não deve repetir
> número que não tenha origem rastreável aqui.
>
> **O que NÃO é:** decisão. Nada neste arquivo fecha, reabre ou revisa nada. É
> matéria-prima; o relatório é módulo da Lia.
>
> **Escrito por:** Felipe (sessão 11, 2026-08-08). **Estado do v1 na data:**
> 2 views ativas, camada tática desligada, sem banda, régua do `c` pendente
> (corte 13/08, decisão 10a), entrega 17/08.

---

## 0. Como ler os números de decisão neste projeto

Antes de qualquer coisa, porque é a armadilha mais fácil de cair ao redigir o
relatório: **existem três numerações diferentes em circulação.**

| Numeração | Onde vive | Exemplo |
|---|---|---|
| **Seções do `Decisoes_pendentes.md`** | por branch, e **divergem a partir da 8** | "seção 12 do `Felipe`" = `E_FF` sem ZQ; "12 do `Paulo`" = slot pré-primeiro-trade |
| **Itens da pauta / espec** | citados no código como `DECISAO-N.N` | `DECISAO-6.1` (`poly_preprocessing.py:111`) = faixa faltante; **não** é a seção 6 |
| **D1–D10 da maratona de 04/08** | `LOG.md`, sessão 2 de 04/08 | "D2c" = corte revisado das views |

**Regra ao citar:** sempre dizer a origem — "D2c da maratona", "seção 12 do
`Felipe`", "item 6.1 da pauta". O aviso de colisão está no topo do
`Decisoes_pendentes.md` e segue **sem decisão** (opções a–d listadas lá).

**Nota de referência velha:** o `CLAUDE.md` diz que a camada tática original foi
adiada "pela decisão 10 em `Decisoes_pendentes.md`". A seção 10 atual é o
backtest — a referência aponta para o lugar errado desde a reorganização do
arquivo. O fato (adiamento em reunião) está certo; o ponteiro não.

---

## 1. Escopo cortado — views

**Das oito views desenhadas, duas estão ativas: 2.2 (inflação) e 2.3 (Fed).**
Verificável no código, não só no registro: `scripts/backtest_v1.py:395` monta a
lista de views com essas duas e nada mais. Convivência medida na janela de 374
pregões: a 2.3 fica ativa em **325 dias (87%)** e as duas rodam juntas em
**240 dias (64%)**.

| View | Onde foi cortada | Motivo medido | Artefato |
|---|---|---|---|
| **2.4 eleitoral** | D2 + D2c (04/08) | O efeito **aterrissa no gap de abertura**, que não é negociável: sobra **23%** na janela abertura→fechamento, só XLF significante, e o TLT — o "Trump trade" mais forte — **some inteiro** (−0,072 no gap → +0,010 no negociável). Depois **reprovou fora da amostra**: no mercado da Câmara 2026 os sinais deveriam inverter contra 2024 se o mecanismo fosse partidário; o TLT cai nos **dois** mercados (−0,072 e −0,075, ambos significantes). | `Dump/analises/Janela_negociavel.md`, `scripts/janela_negociavel.py` |
| **3.1 recessão** | D2b (04/08) | No par que a view monta (defensivo − cíclico) **não há sinal**: t entre −0,46 e −1,05. Existe efeito **direcional** e significante (SPY +0,59% em 10 pregões), que a view **não consegue expressar** porque o P dela é neutro em mercado (`P[SPY] = 0`). Não foi redesenhada para direcional: sinal contrário à própria tese, 245 pregões, um ano só, z-score in-sample. | `Dump/analises/Nivel_divergencia_3_1.md`, `scripts/nivel_divergencia_3_1.py` |
| **C geopolítica/energia** | D2c (04/08) | O mecanismo é real e é a **correlação mais forte da maratona** (XLE com r = +0,54 no gap), mas **nada sobra na janela negociável**, com 27 observações. | `Dump/analises/Janela_negociavel.md` |
| **E tarifas** | D2c (04/08) | Dado: **13 dias** de cobertura. | idem |
| **G fiscal** | D2c (04/08) | Dado: **3 dias** de cobertura. | idem |
| **B trajetória do Fed** | Seção 11 do `Felipe` (07/08) | Três motivos somados: (1) **duplica a 2.3** — β e P são os mesmos por desenho da espec, muda só a surpresa; (2) **cobre metade da janela** — o M3 é só de 2025, ~210 dos 374 pregões; (3) **o benchmark não existe de graça** — o F6 do Paulo testou todas as sintaxes do ZQ de dezembro no yfinance (`ZQZ25`, `ZQZ25.CME`, `ZQ=Z25`, `ZQZ2025`, `ZQF26`…), todas vazias; só o contínuo `ZQ=F` funciona e é o contrato da frente. | Espec preservada em `Dump/analises/Informações_uteis/views/view_B_trajetoria_fed.md` |

**Achado transversal, e é o que derruba a tese de defasagem inteira:** a
informação do Polymarket **aterrissa no gap de abertura**. O mesmo padrão
apareceu na tática de fim de semana, na eleição 2024, na recessão 2025 e no Irã
2026. Não é propriedade de uma view — é característica do dado.

**Condições de reabertura registradas:** a **B** reabre se aparecer fonte
gratuita do ZQ de dezembro **ou** se o grupo aprovar benchmark substituto (o
forward de dezembro extraído da curva de bills do FRED está **mapeado e não
decidido**; tem precedente na troca do ZQ por ΔDTB3, com a ressalva de que um
forward de 1 mês tirado de dois vértices interpolados é ruidoso e **ninguém
mediu esse ruído**).

**Consequência operacional já comunicada:** o Paulo pode parar de procurar o ZQ
— a caça aparece em três pedidos (F6, FOLLOWUP2, FOLLOWUP3) e não tem mais
consumidor no v1.

---

## 2. Escopo cortado — camada tática

São **dois cortes distintos**, em momentos e por motivos diferentes. O relatório
não deve tratá-los como um só.

### 2.1 A tática ORIGINAL saiu por escopo, sem medição

PEAD (1.1), event-driven (3.2) e velocidade de ajuste eram módulo da Lia e
foram **adiadas em reunião** por estarem fora do escopo do projeto. Nenhuma foi
medida — foi decisão de prioridade, não de dado. (Ver nota de referência velha
na seção 0 deste dossiê.)

### 2.2 A tática REFORMULADA foi medida, e saiu por não haver como escolher o tamanho

Três candidatas foram desenhadas e realocadas ao Felipe em 2026-07-11.

**O gap de fim de semana morreu antes das outras (D3b, 04/08).** Condicionar a
|Δp| grande **funcionou como método** — achou significância onde a versão
incondicional não achava (SPY t +2,22, XLF t +3,21 no M4) — mas o **sinal é de
reversão, não de continuação**: a tática compraria a direção do poly e perderia.
Não foi invertida para operar a reversão: seriam 25 observações de um mercado,
num ano em que a reversão intradiária foi o regime.
→ `Dump/analises/Gap_fds_condicionado.md`, `scripts/gap_fds_condicionado.py`

**As outras duas entraram no D3 e foram desligadas na seção 12c (07/08).** O
motivo não é o tamanho do efeito — é a impossibilidade de escolher o parâmetro
sem olhar o resultado:

| família | Δ vs. desligada |
|---|---|
| só prêmio de anúncios (1.3) | **−0,34 a −0,03 pp** |
| só drift pós-FOMC | +0,08 a +0,80 pp |
| prêmio + drift | +0,05 a +0,45 pp |

Ligar exige um `orcamento` (fração do patrimônio), que é **parâmetro do modelo**
e não sai de teoria nenhuma. A varredura mostrou que o Δ é **monótono no
orçamento** dentro de cada família — cada overlay é um deslocamento de peso fixo
vezes o orçamento, logo a grade **não tem ótimo interior**. A melhor linha é
sempre a da ponta, e a ponta é onde a varredura parou: a tabela não seleciona o
orçamento, ela devolve a pergunta. Escolher a linha de cima seria calibrar
tamanho contra o resultado de 374 pregões — o overfit em dois passos do
protocolo da seção 10, agora **sem rodada seguinte para desmentir**, porque o v1
virou a entrega final.
→ `Dump/analises/Curva_orcamento.md`, `scripts/curva_orcamento.py`

**Estado no repositório:** os três overlays estão **implementados e testados**
(`src/tatica_premio_anuncios.py`, `src/tatica_drift_pos_fomc.py`,
`src/tatica_gap_fds.py`), com os orçamentos em `None`. Vão ao relatório como
**análise de sensibilidade**, não como configuração entregue.

**Premissa que sustenta a família do prêmio, para o registro:** separando os
anúncios por **entropia normalizada da PMF na véspera**, anúncio incerto rende
+0,383% de média (mediana +0,444%) contra −0,704%/−0,139% do previsível e
+0,079% do dia sem anúncio (t de Welch +2,10, n = 9 vs 10), com a mesma direção
nas duas famílias (FOMC e CPI) separadas. **A premissa passou; o dimensionamento
é que não tem âncora.**
→ `Dump/analises/Premio_condicional.md`, `Dump/analises/Premissa_taticas.md`

---

## 3. Escopo cortado — banda de não-negociação (seção 13 do `Felipe`, 07/08)

O v1 entrega **sem banda** (`banda=None`): a carteira negocia todo `Δw` que o
modelo pede. A banda era a saída **pré-registrada no D8** para o caso de o giro
do H = 1 dia ser ruído — e a nossa estratégia tem **36% do giro desfeito em 1–2
pregões**, exatamente o mecanismo que a pesquisa aponta como matador de
estratégia diária.

| banda | giro diário | desfeito em 1–2 pregões | pernas paradas | breakeven | excesso × SPY |
|---|---|---|---|---|---|
| 0 (v1) | 0,242 | 0,363 | 1% | 35,89 bps | +2,62 pp |
| 0,10% | 0,241 | 0,363 | 55% | 36,01 bps | +2,61 pp |
| 1,00% | 0,235 | 0,357 | 82% | 36,99 bps | +2,68 pp |
| 5,00% | 0,220 | 0,354 | 90% | 38,48 bps | +1,70 pp |

**Os três motivos, e nenhum deles é o excesso:**

1. **O ruído não está nas pernas pequenas.** A banda mais fina já impede 55% dos
   pares (dia × ativo) de negociar e corta **0,4%** do giro. Não existe cauda de
   trade miúdo a filtrar — quase todo o giro está em poucas pernas grandes, que a
   banda deixa passar por construção. Para cortar giro de verdade ela teria de
   bloquear trade grande, e aí não é filtro de ruído: é deixar de seguir o modelo.
2. **A reversão quase não se move** (0,363 → 0,354). O remédio não morde o
   mecanismo que o motivou.
3. **O custo não é o que aperta:** breakeven de **35,89 bps por lado contra os
   2 bps premissados — 18× de folga**. O custo teria de subir uma ordem de
   grandeza para virar o sinal.

**Armadilha registrada:** o excesso tem **máximo interior** (1,00%, +2,68 pp).
Com a reversão parada, essa oscilação não tem mecanismo por trás — escolher a
banda por ela seria o mesmo overfit da 12c.
→ `Dump/analises/Curva_banda.md`, `scripts/curva_banda.py`

---

## 4. Limitações de dado (o que entrou com ressalva)

| # | Limitação | Origem | O que ela custa, medido |
|---|---|---|---|
| L1 | **ΔDTB3 no lugar do ZQ** na surpresa de juros | D6 (04/08) + seção 12 do `Felipe` | Horizonte de **~3 meses contra uma reunião**. Ganho: 36 reuniões (contra 8 pelo poly) e **7 de 7** sinais coerentes com Bernanke-Kuttner. Ressalvas: a **ordem das magnitudes não bate** (XLU e TLT, que deveriam ser os mais sensíveis, dão os β mais fracos) e a surpresa é pequena (σ = 3,3 bps). A demeanagem trata o viés de **nível**, não o descasamento de horizonte. |
| L2 | **Midpoint sem bid/ask** | D11 do `Paulo` | **Não existe bid/ask histórico no CLOB** — medido: `/orderbook-history` volta vazio; `/book`, `/midpoint` e `/spread` são só tempo real e dão 404 em mercado resolvido. Duas consequências: **o spread não é observável** (o haircut de custo vira **premissa, não estimativa**), e midpoint parado em mercado sem negociação **lê como estabilidade perfeita** — é a razão de os 78 slots pré-primeiro-trade terem de sair como `0` no G5, e não `NaN`. |
| L3 | **Truncamento do cap de 20k no `/trades`** | F4 do `Paulo`, G5 | O endpoint capa em 20k (limit 10000 + offset 10000, filtros de tempo ignorados). **346 slots** de volume saem `NaN` **por truncamento** — ausência de medição, não ausência de mercado. A distinção `NaN` (não medido) × `0` (medido, sem trade) é decisão da Lia e é a régua do G5. |
| L4 | **Granularidade de 12h** | F4 do `Paulo` | Teto do backtest histórico. A granularidade fina (10 min) só existe nos últimos ~30 dias de mercado vivo. Dois pontos por dia bastam para o desenho atual, mas fecham a porta para qualquer coisa intradiária. |
| L5 | **Ponta aberta extrapolada** | D4 (04/08) / item 1.2 da pauta | Balde aberto vira **ponto médio a meia largura da grade**. Regra sem parâmetro e sem lookahead, mas é extrapolação — e a grade **muda de 3 a 9 faixas** ao longo da amostra, com deslocamento em mar/2026 e **inversão de sinal em jul/2026** (`bucket_values_with_open`). |
| L6 | **`carry_missing`** | D4 (04/08) / item 6.1 da pauta | Faixa sem preço num slot **herda a última leitura**, e só depois renormaliza. Justificativa medida: a faixa que morre já decaiu para ~zero antes de parar de negociar ("nenhum corte" morreu valendo 0,0045; "1 corte", 0,0030), então carregar ≡ zerar; e para a faixa que some e volta (mar/2026: 24 de 60 slots completos) carregar bate renormalizar sobre as presentes. **Efeito de interface, e importa para o relatório: a view NUNCA vê o buraco** que o `diagnostics` reporta. Medido: 25 dias degenerados na leitura crua viram **0 de 801** depois do carry (somas entre 0,953 e 1,143) — é por isso que o piso de 0,9 da 2.3 **não morde um único dia**, nem na janela do v1 nem no histórico completo. |
| L7 | **Sem correção de favorite-longshot** (γ = 1,0) | D5 (04/08) | 9 mercados resolvidos não calibram curva própria, e um γ de aposta esportiva mexeria **25% na mediana** de um mercado de p baixa, sem âncora no nosso dado. Reportado com γ ∈ {1,0; 1,1; 1,25} como **coluna de robustez**. |
| L8 | **Lista mercado → ETF é heurística de download** | D10, item 5.1 | O mapeamento foi feito para saber o que baixar, não como afirmação de que aquele ETF é o canal do mercado. |
| L9 | **Shutdown segue excluído** | D10, item 5.4 | — |
| L10 | **CPI só de 2025** | D10, item 6.3 | Limita a janela da 2.2 pela ponta esquerda: a semeadura da média expansiva **não existe** para a 2.2 (não há pregão anterior à primeira PMF de CPI, 2025-02-08), ao contrário da 2.3. |
| L11 | **Custo de transação é premissa, não medição** | D8 (04/08) | 2 bps/lado sobre `Σ\|Δw\|` + financiamento e aluguel declarados em separado. A pesquisa confirmou que 2 bps é **conservador** (spread cotado desses 9 ETFs é 1–2 bps cheios; all-in medido do SPY em ordem de US$ 25 M é 0,30 bp), mas com L2 o número não é observável no nosso dado. Por isso a métrica do relatório é o **custo de breakeven**, não o retorno líquido de um custo escolhido. |

---

## 5. Limitações de parâmetro e de processo

### 5.1 As 13 decisões da maratona seguem PROVISÓRIAS e nunca foram revistas pelo grupo

Fechadas pelo Felipe em 2026-08-04 **com autorização do grupo**, para não travar
a entrega, e marcadas para revisão desde então. **A revisão nunca aconteceu.**
Prioridade declarada na época: **D7 (τ e δ)**, por encostar no módulo de risco da
Lia.

Lista: H = 1 dia · views ativas · views fora · camada tática · tática fora ·
balde aberto · faixa faltante · favorite-longshot · surpresa de juros · δ = 3,0 ·
τ = 1/T · custo de transação · horizonte da 2.2.
→ seção 9 do `Decisoes_pendentes.md`; justificativas no `LOG.md` (sessão 2 de
04/08); medições em `Dump/analises/`.

**Mesmo regime, mesma pendência:** as 2 decisões do backtest (seção 10 — duration
medida e teto de alavancagem), a saída da view B (seção 11) e o `E_FF` da 2.3
(seção 12). **Nenhuma foi revista pelo grupo.**

### 5.2 Cinco seções seguem sem decisão registrada

| Seção | Assunto | Estado real |
|---|---|---|
| 3 🔴 | mapeamento cenário → ativos | O código responde (β por event-study), mas **a seção nunca foi escrita** |
| 4 🔴 | tradução probabilidade → vetor Q | idem (bridge do Felipe) |
| 5 🔴 | definição de "surpresa" do PEAD | **Morreu junto com a tática original** — não há o que registrar |
| 6 🔴 | forma funcional do Ω reativo | Só a **6a** fechou (quem colapsa a PMF multi-bucket); a **forma** continua aberta, com 4 candidatas (2 colapsos × 2 grades de tempo) |
| 7 🟡 | convergência entre fontes | Declarada **fora do v1 como stub** — é a única das cinco cujo estado está escrito |

**Leitura honesta para o relatório:** as seções 3, 4 e 6 não são buracos de
metodologia — são buracos de **registro**. O que o código faz está documentado
nos módulos e no `LOG.md`; o que falta é a ata. Isso é uma limitação de processo
e deve ser declarada como tal, não escondida.

### 5.3 A régua do `c` da Lia pode não chegar

**Corte fechado em 13/08** (seção 10a, entrega 17/08). Se não chegar, o v1
entrega com **`c = 1`** (fallback neutro do `omega_fallback`) e **teto no tilt,
nível 1** — o ponto mais conservador da grade `{1, 2, 3, 5}`.

**O critério do fallback é deliberadamente independente do backtest:** *o ponto
mais conservador da grade*. Qualquer um confere que 1 é o menor de `{1, 2, 3, 5}`
sem abrir o `Backtest_v1.md`. Foi pré-registrado justamente para não escolher o
teto com a tabela de excesso na tela.

**O que continua aberto mesmo com a régua entregue:** o **nível e o escopo do
teto** são decisão do grupo, e a ordem da Lia (c → medir Σ|w| → decidir teto)
vale até 13/08.

**Por que o teto existe, e por que ele é uma limitação e não um recurso:** sem
limitador o backtest vai à ruína — Σ|w| **mediana 195, máximo 34.481** na
carteira pedida. Isso vem de o v1 rodar com `c = 1`, isto é, **confiando na view
tanto quanto no prior**. O teto está hoje fazendo o trabalho do Ω. Medido: com
`c ≤ 0,02` a ruína do irrestrito some, mas **algum** limitador segue obrigatório
em toda a grade.
→ `Dump/analises/Curva_c.md`, `scripts/curva_c.py`

### 5.4 O escopo do teto vale 14 pp, e não foi decidido

Comparando na **mesma Σ|w| medida** (única comparação honesta):

| Σ\|w\| medida | teto na carteira | teto só no tilt | diferença |
|---|---|---|---|
| 1,74 | −15,14 pp | −0,94 pp | **+14,19 pp** |
| 2,48 | −15,92 pp | −1,91 pp | **+14,02 pp** |

O buraco de ~14 pp contra o SPY **era o escopo do teto, não a view**: no corte de
carteira o teto misturava o tilt da view com o pedaço da perna de SPY que ele
tirava. **Isto mede, não decide** — o escopo continua sendo do grupo.

### 5.5 O protocolo anti-overfit, e por que ele aparece três vezes neste dossiê

Proposta da Lia (`RESPOSTA3`), aceita pelo Felipe, **não fechada pelo grupo**:

1. a **forma** do `c` sai do teste de monotonicidade e **não é revisitada por
   resultado de backtest**;
2. o **nível** global é escolhido **uma única vez**, na conversa de risco, junto
   com o teto;
3. se o resultado depois desagradar, mexe-se no **teto**, não na régua.

O risco que ele previne é de processo, não de código: eu e ela alternarmos
ajustes olhando o resultado ("ela calibra o `c`, o grupo mexe o teto vendo o
número, ela recalibra vendo o número"), que vira overfit em dois passos sem
nenhum dos lados perceber. **É o mesmo argumento que cortou a camada tática
(12c) e a banda (13)** — em ambas a tabela tinha um número tentador sem mecanismo
por trás.

### 5.6 Ressalvas de medição que precisam ir junto do número

- **A demeanagem da 2.3 não equilibrou o sinal na janela — inverteu o lado.** No
  levantamento completo (2024-04 → 2026-06, 533 dias) a surpresa líquida fica
  45%/55%; **dentro do backtest**, 22% positiva / 78% negativa, porque a média
  expansiva carrega o regime de 2024–25. Com a semeadura da 12a melhora para
  **34%/66%** e não volta ao equilíbrio: **o resíduo é regime, não artefato**.
- **O piso de eventos do β foi deliberadamente não fixado** (12b): na janela do v1
  o β foi estimado com **25 a 35 eventos todos os dias**, então qualquer piso
  abaixo de 25 não desativa um único pregão. Escolher 10 ou 20 seria inventar
  threshold sem medição. **Vira limitação do relatório, não pendência.** O
  critério para quem retomar: curva de estabilidade (β com os primeiros *n*
  eventos contra o β final), e o piso é onde a diferença deixa de virar o sinal
  de `P`.
- **O ingrediente de coerência da Lia tem pouco poder discriminante na 2.3**: com
  a soma entre 0,969 e 1,013 na janela do v1, se ele reprovar no teste de
  monotonicidade pode ser **falta de variação, não sinal errado**. Ela vai
  reportar a distinção — o relatório **não deve** concluir que "o desarranjo não
  prevê erro".
- **Os 25 dias degenerados são 100% linhas incompletas** (mediana de 3 faixas
  ausentes de 4): **não existe um único livro completo somando abaixo de 0,9**. A
  soma baixa mede **buraco**, não desencontro entre books.
- **Correção de registro sobre a alavancagem:** o "Σ|w| mediana 24, máx 264" que
  circulou até 07/08 **subestima** — só cobria os pregões até a ruína. Na carteira
  pedida, mediana **195** e máximo **34.481**.

### 5.7 Reprodutibilidade

- **O repositório não roda sozinho.** O `data/` vive no branch do Paulo e o
  módulo do Ω no da Lia; o merge dos três branches é o único caminho, e não é
  feito do branch `Felipe`.
- **Os quatro artefatos do v1 reproduzem byte a byte sob dois ambientes**
  (pandas 2.3.3 e 3.0.4) — os números atravessam uma major sem se mover.
  Tabela dos dois ambientes no `README.md`.
- **A restauração do `data/` está documentada no `README`** (`git archive
  origin/Paulo data`), e foi exercitada em 08/08 do zero.

---

## 6. Índice de artefatos

| Assunto | Análise | Script |
|---|---|---|
| Views defasadas, gap × janela negociável, teste fora da amostra | `Dump/analises/Janela_negociavel.md` | `scripts/janela_negociavel.py` |
| View 3.1, sinal de nível | `Dump/analises/Nivel_divergencia_3_1.md` | `scripts/nivel_divergencia_3_1.py` |
| Tática de prêmio, premissa condicionada | `Dump/analises/Premio_condicional.md`, `Premissa_taticas.md` | `scripts/premio_condicional.py`, `premissa_taticas.py` |
| Tática de fim de semana | `Dump/analises/Gap_fds_condicionado.md` | `scripts/gap_fds_condicionado.py` |
| Surpresa de FOMC sem ZQ | `Dump/analises/Surpresa_fomc_sem_ZQ.md` | `scripts/surpresa_fomc.py` |
| Convergência e horizonte da 2.2 | `Dump/analises/Convergencia_2_2.md` | `scripts/convergencia_2_2.py` |
| Defasagem k | `Dump/analises/Perfil_defasagem_k.md` | `scripts/perfil_defasagem_k.py` |
| Sensibilidade das decisões 1.1/1.2/6.1 | `Dump/analises/Sensibilidade_decisoes_1.1_1.2_6.1.md` | `scripts/sensibilidade_reuniao.py` |
| Backtest, atribuição, escopo do teto | `Dump/analises/Backtest_v1.md` | `scripts/backtest_v1.py` |
| Varredura do `c` | `Dump/analises/Curva_c.md` | `scripts/curva_c.py` |
| Varredura de orçamento da tática | `Dump/analises/Curva_orcamento.md` | `scripts/curva_orcamento.py` |
| Varredura de banda | `Dump/analises/Curva_banda.md` | `scripts/curva_banda.py` |
| Especs das 8 views | `Dump/analises/Informações_uteis/views/` | — |
| Especs das 3 táticas | `Dump/analises/Informações_uteis/táticas/` | — |

---

## 7. Aviso ao relatório: este dossiê descreve o v1, e o escopo vai ser reaberto

Em **2026-08-08 o dono determinou** que a próxima sessão desenha **views novas** e
depois tenta **reativar a camada tática** com estratégias novas (registrado como
seção 14 do `Decisoes_pendentes.md`). Se isso entrar antes de 17/08, as seções 1
e 2 deste dossiê mudam.

**O que NÃO muda em nenhuma hipótese**, porque é medição e não escolha: a seção 4
inteira (limitações de dado), as ressalvas da 5.6, e o motivo de cada corte já
consumado. Uma view nova não desfaz o achado de que o efeito eleitoral aterrissa
no gap — no máximo evita repeti-lo.
