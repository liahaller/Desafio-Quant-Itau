# Candidatos táticos — o que sobrou de pé

> 🟢 **ENCERRADO em 2026-08-11 (sessão 27). A camada tática ENTROU.** As duas
> candidatas que sobraram da maratona — **M4 recessão** (livro setorial neutro,
> bloco k = 3, 5, 10) e **M9 Câmara** (k = 20) — foram **admitidas pela D28** e
> estão **LIGADAS na entrega** (D28.13). Implementação em
> `src/tatica_sleeves.py`, medição em `Dump/analises/Camada_tatica_v2.md`.
>
> A **1.1 PEAD fora do Fed**, que este arquivo listava como bloqueada por dado,
> foi destravada (CSV do `CPIAUCSL`, item 8 da D28) e **medida: reprova**. As
> certidões de óbito abaixo continuam válidas; a do CPI mudou de causa (era
> **DADO**, virou **SEM SINAL/INVERSÃO**) — ver a nota na própria linha.
>
> O que este arquivo descreve daqui em diante é **histórico do processo de
> triagem**, não uma fila de candidatos abertos.

Este arquivo lista **apenas os desenhos da camada tática em estado CANDIDATO**.
Depois da maratona de medição de **2026-08-11 (sessão 26)** sobraram **dois**.

Os que morreram saíram das seções individuais e viraram **certidão de óbito**
na tabela abaixo — o motivo de cada um fica registrado aqui, com o número e o
artefato, para não ser redescoberto. Táticas cortadas em ondas anteriores (gap
de fim de semana, sleeves da D16/D17, drift pós-FOMC) continuam no
`Dump/analises/Retomada_tatica.md`.

Views estruturais candidatas ficam no `Dump/analises/Candidatos.md`. **São
camadas diferentes:** uma view entra em P/Q do Black-Litterman; uma tática é
overlay por cima dos pesos já otimizados. Um candidato tático não compete com
uma view candidata.

**Nada aqui está decidido.** A coluna "o que falta" lista condição, não
recomendação — e nenhum candidato foi movido de estado por conta de número.

---

## 🪦 Certidões de óbito — a maratona de 2026-08-11

Quatro scripts, quatro artefatos, **nenhum módulo em `src/`** (protocolo da
D17). Suíte: **276 testes** (259 + 17 novos).

**Como ler a coluna "causa":** **DADO** = não há observação suficiente (G0) ·
**SEM SINAL** = o efeito é ~zero ou está dentro do tick (G1) · **INVERSÃO** = o
efeito existe mas aponta contra a tese declarada (G2; pela D2b não se inverte) ·
**INSTÁVEL** = passa na amostra inteira e troca de sinal quando ela é partida em
duas · **DUPLICAÇÃO** = já pertence a uma view (G3).

| desenho | causa | por quê, em uma frase | artefato |
|---|---|---|---|
| **1.1 PEAD** · Fed | **SEM SINAL** | Surpresa mediana de **0,52 bps** contra um tick de 1 bp — o poly acerta o Fed quase na mosca, e no sweep de janela o `h = 15` sai `SPY +4.91 ❌ · TLT +1.37 ❌`, **dígito por dígito a sleeve reprovada da D16**: é o mesmo experimento com outro nome. | `Gate_PEAD.md` |
| **1.1 PEAD** · CPI | ~~DADO~~ → **SEM SINAL** | ⚠️ **Causa de morte CORRIGIDA em 2026-08-11 (sessão 27).** O bloqueio era o valor realizado, não a série do poly — a véspera é justamente o lado que a surpresa usa. Com o `CPIAUCSL` no `data/raw` (item 8 da D28), **12 divulgações ficaram pareadas** e a família foi medida: **G1 de 0,6×** (mediana da surpresa **0,06 p.p.** contra uma grade de baldes de 0,1 p.p.), **nenhuma das 5 janelas passa no G2**, e **G3 de +0,58** com a divergência da 2.2. Mesmo diagnóstico do Fed: o poly erra o CPI por menos que a granularidade com que ele próprio pergunta. | `Gate_PEAD.md` |
| **1.1 PEAD** · binários | **DADO** | Um evento de resolução por mercado; com n = 1 não há μ. | `Gate_PEAD.md` |
| **3.2 event-driven** | **SEM SINAL** | Do movimento em volta do salto, o que sobra depois do fechamento tem **mediana −1%** e vira moeda (4 de 8 mercados na direção certa) — a informação aterrissa antes de a tática poder operar. | `Gate_event_driven.md` |
| **3.2** · as 2 que passaram G2 | **DADO** | M7 Irã tem **5 eventos**; M5 Trump tem **G3 imensurável** (mercado de 2024, não sobrepõe as views) — e as duas são mercados de views já cortadas (C e 2.4). | `Gate_event_driven.md` |
| **Notícia** · M6, M8, M7 | **DADO** | Dispersão de sobra (44×, 66× o tick) contra **2, 8, 28 e 58 pregões** de cobertura — um mercado de 8 pregões não sustenta overlay, por mais que se mexa. | `Gate_noticia.md` |
| **Notícia** · M5, M9 | **SEM SINAL** | G1 de 0,5× e **0,0×** o tick em k = 1: o Δp diário desses mercados é menor que um centavo de movimento. | `Gate_noticia.md` |
| **Velocidade de ajuste** | **SEM SINAL** | Variance ratio 0,97–1,18 e nenhuma autocorrelação com \|t\| ≥ 2 — **o encadeamento que ela negocia não existe**. Medida na sessão 25; não re-medida na maratona. | `Premissa_tendencia.md` |
| **1.2 momentum** | **SEM SINAL** + **DUPLICAÇÃO** | Mesmo VR ≈ 1, e o G3 degrada de −0,19 para −0,42 conforme acumula: quanto mais horizonte soma para sair do tick, mais vira a view 15b com outro nome. | `Premissa_tendencia.md` · `Gate_M3_acumulado.md` |

**O que a coluna "causa" diz quando se olha de cima, e é insumo de relatório:**

- **Ninguém morreu por inversão pura.** Inversão foi o que matou a maioria das 13
  tentativas anteriores (C2a, drift CPI, M3 acumulado nos seis lookbacks). Nesta
  rodada ela aparece só como acompanhante, em cima de sinal que já era ruído.
- **A causa dominante virou DADO** — e não é falta de histórico: é que
  **cobertura e dispersão são quase disjuntas** no dado entregue. O que se mexe
  dura 8 pregões; o que dura um ano não se mexe.
- **O modo de falha novo é INSTÁVEL**, e não existia no repertório da camada
  antes desta sessão (veio da **D19c**, que era sobre uma view). Das **10
  aprovações de G2** da maratona, **8 não sobrevivem a ele**.

### ⚠️ Duas destas mortes têm condição de reabertura registrada

Não estão vivas, e não são candidatas — mas o caminho de volta existe e é
específico, no mesmo espírito da coluna "o que reabriria" do
`Retomada_tatica.md`:

- **1.1 PEAD fora do Fed** — o que a mata nas outras duas famílias é G0, não
  tese. Reabre com **(a)** a **decisão 5** fechada (definição operacional de
  "surpresa", 🔴 aberta e vazia) e **(b)** dado de resolução: o print realizado
  do CPI, ou leituras do poly **depois** da resolução. Pedido ao Paulo.
- **Notícia** — reabre com **mais mercados de evento com fluxo de notícia**, não
  com mais histórico dos mesmos. Nenhum horizonte de grade conserta um mercado
  de 8 pregões. ⚠️ E a **D24 🔴** pega esta em cheio: mercado de notícia curto é
  exatamente o de PMF degenerada, e o portão de qualidade do poly vale para
  views e **não** para overlays.

---

## Régua de admissão em vigor — **D22, fechada pelo dono em 2026-08-10**

A mesma régua das views estruturais vale aqui:

1. **Lê o Polymarket** — o sinal vem de preço/PMF de mercado do poly.
2. **Atua na bolsa** — se expressa em ETFs do universo decidido (D1).
3. **Teoria não desprovada por teste** — nenhuma medição contradiz a tese.
4. **Ortogonal ao que já está dentro** — ângulo alto entre os sinais, sem ρ alto
   no sinal-fonte.

**Sinal fraco não é impedimento.** O que reprova é a tese ser contrariada pelo
dado (precedente D2b, "não se inverte").

⚠️ **Ao que a maratona acrescentou, na prática, um quinto item:** a
**estabilidade no corte da amostra**. Ele não está na D22 e **não estou
tratando como se estivesse** — mas foi o que separou 2 aprovações de 10, e um
G2 que troca de sinal no meio da amostra é a média de dois regimes, não um
sinal. Formalizá-lo ou não é decisão do dono.

### Três condições de camada, todas já registradas e nenhuma nova

Valem para as duas candidatas que sobraram, e nenhuma se resolve em script:

- **Escopo.** A camada saiu em reunião. Reabri-la é reabrir escopo — decisão do
  grupo. ⚠️ O ponteiro "decisão 10" que este arquivo citava **não existe**: o
  número foi reutilizado numa reorganização, e o corte real está no `LOG.md`
  (apontado no `DOSSIE_limitacoes_v1.md`).
- **Tamanho com âncora (12c).** A camada foi desligada porque o dimensionamento
  era parâmetro livre (Δ monótono no orçamento, sem ótimo interior). Nenhuma das
  duas tem âncora própria. ⚠️ Mas o motivo que matou a 12c **não precisa se
  repetir**: a âncora `inv(δΣ)·μ` da D16 tem **zero parâmetro livre**,
  sobreviveu ao teste e segue sem uso. **Não volte a introduzir `orcamento`.**
- **Sinal acima do tick da fonte (G1, D17).** ⚠️ A leitura mudou na D26: o
  veredito vale para o `k` medido, não para a série — o tick é fixo e o sinal
  acumula (M3: 0,5× em k = 1 → 3,7× em k = 20). Rodar o G1 é rodar a **grade de
  horizontes**, não um ponto.

## O bloqueio de terceiro CAIU — e o registro estava desatualizado

A D17e e o `Retomada_tatica.md` registram que o `etf_open_daily.parquet` está em
outra base de ajuste que o `etf_prices_daily.parquet`, e que por isso nenhuma
tática mede o retorno do próprio dia do evento. **Isso não vale mais.** A
conferência foi re-rodada dentro da maratona, antes de qualquer número: maior
desvio de `abertura/fechamento − 1` é **0,059%**, dentro do ruído intradiário.
As janelas intradiárias valem, **inclusive no dia do próprio evento**.

---

# As duas que sobraram

## 🟢 M4 recessão, k = 5 — a única célula que limpou os quatro critérios

**O que é:** overlay que lê a **probabilidade de recessão nos EUA** no
Polymarket, acumulada sobre **5 pregões**, e tilta SPY e TLT na direção de
risco-off. Nasceu como uma linha da tabela do gate da candidata *notícia* — não
foi desenhada, foi encontrada.

**Status:** 🟢 **candidata MEDIDA e aprovada nos quatro critérios**, a primeira
da história do projeto. Nas 13 tentativas anteriores o placar foi 0 de 5 no
`Gate_sleeves.md` e 0 de 6 no `Gate_M3_acumulado.md`.

**Régua (D22):**

- Lê o poly ✅ — o sinal é o Δ de 5 pregões da probabilidade do mercado M4.
- Atua na bolsa ✅ — SPY e TLT, universo da D1.
- Teoria não desprovada ✅ — **medido**, não por vacuidade: `SPY −1,11 ✅ ·
  TLT +2,70 ✅` contra a premissa declarada *"p(recessão) sobe → risco-off:
  bolsa cai e duração sobe"*.
- Ortogonal ✅ — G3 **−0,20** (entropia CPI da 15b), o menor de toda a maratona.

**Os números, de `Dump/analises/Gate_noticia.md`:**

| critério | valor |
|---|---|
| **G0** cobertura | **249 pregões** |
| **G1** dispersão ÷ tick | **2,0×** |
| **G2** μ contra premissa declarada | `SPY −1,11 ✅ · TLT +2,70 ✅` |
| **G3** maior \|corr\| com as views vivas | **−0,20** |
| **estabilidade** 1ª metade | `SPY −0,66 ✅ · TLT +1,36 ✅` (n = 116) |
| **estabilidade** 2ª metade | `SPY −0,56 ✅ · TLT +2,06 ✅` (n = 111) |

**O que falta — e o item 1 vem antes de tudo:**

1. 🛑 **Explicar a contradição com a D19c.** A **view 3.1** leu **este mesmo
   mercado**, e a D19c mediu que o coeficiente **troca de sinal dentro da
   própria amostra** (SPY em h = 10: +0,97% t +6,52 na 1ª metade, **−0,35%
   t −2,27** na 2ª). A sleeve **passa** exatamente o teste de metades que a view
   **reprovou**. Ou existe diferença real de horizonte e montagem que explica, ou
   uma das duas medições está lendo ruído. **É análise, não script, e nada deve
   ser construído em cima disto antes.**
2. **Reabrir escopo da camada** — decisão do grupo.
3. **Âncora de tamanho** (12c). Candidata natural: o `inv(δΣ)·μ` da D16, zero
   parâmetro livre, de pé e sem uso.
4. **G4 (P&L da sleeve sozinha)** — é o primeiro critério que exige escrever
   módulo, e por protocolo ele só vem depois de 1.

> ⚠️ **Contra o próprio candidato, três coisas:**
>
> - **M4 não é um mercado de fluxo de notícia** — é pergunta permanente, G1 de
>   **0,7×** em k = 1. Ele só sai do tick **acumulando**, e é por isso que
>   aparece em k = 5. A candidata *notícia* foi desenhada para o outro grupo; o
>   que passou foi o vizinho de tabela.
> - **`k = 5` é uma célula de uma grade de seis.** Em k = 3 passa mas não
>   sobrevive ao corte; em k = 1, 2, 10 e 20 não passa. Uma célula isolada numa
>   grade é o padrão de quem achou o horizonte que funcionou — cravar k = 5 por
>   ter sido o que passou seria escolher parâmetro contra o resultado, que é
>   exatamente o que a 12c e a D13 mataram.
> - **Não há segundo mercado de recessão**, então o corte em metades é o único
>   teste fora da amostra que existe (a própria D18d já registra isso).

## 🟡 Transversal — o eixo do INSTRUMENTO, medido e ainda não conclusivo

**O que é:** o mesmo gatilho de qualquer candidata, expresso em **long/short de
setores** em vez de SPY/TLT direcional. Não é um gatilho novo — é a constatação
de que as 13 tentativas escolheram todas o **mesmo livro**, e que esse livro
nunca foi variável.

**Status:** 🟡 **candidata MEDIDA, resultado dividido.** O eixo existe; quase
nada sobrevive ao teste fora da amostra; e metade dos livros que declarei falha
a própria premissa de ortogonalidade.

**Por que ela existe:** é a única direção que **sobrevive ao poly estar certo**.
Toda tática direcional precisa que ele esteja errado (D16: 0,52 bps em 17
reuniões) ou que ele ajuste **em rampa**, dando tempo de entrar no meio do
movimento (D26: VR ≈ 1, ρ ex-ante ≈ 0 — ele reprecifica de uma vez), e as duas
premissas estão
medidas contra. Um spread entre setores não pede que o Fed surpreenda — pede que
os setores respondam de forma diferente ao mesmo choque.

**O que a maratona mediu, de `Dump/analises/Gate_transversal.md`:**

**1. O eixo é real, e o placar é assimétrico.** Mesmo sinal, mesma grade, mesma
janela — trocando só o livro:

| | pares (mercado, k) |
|---|---|
| passam **só** com livro setorial | **8** |
| passam **só** com livro direcional | **0** |
| passam nos dois | 3 |
| não passam em nenhum | 43 |

Oito contra zero não é ruído de amostragem: quando o livro muda o veredito, ele
muda **sempre no mesmo sentido**. Inclusive na família do FOMC, que reprova com
SPY/TLT em toda a grade e passa com `−XLK +XLF` em k = 5, 10 e 20.

**2. Mas 6 das 8 morrem no corte da amostra.** Sobram duas, e nenhuma credita a
transversal de forma limpa:

- **M4 recessão k = 5** sobrevive — **e passa igual com o livro direcional**.
  Ali quem funciona é o gatilho; o livro setorial não acrescentou nada.
- **M9 Câmara k = 20** é o **único caso com crédito próprio** (o direcional
  falha, o setorial passa). ⚠️ E cai justamente no mecanismo partidário que a
  **view 2.4 reprovou fora da amostra**.

**3. "Ortogonal por construção" é falso para metade dos livros — medido.** Dos 6
livros distintos declarados, 3 ficam abaixo de |0,20| de correlação com o SPY
(`+XLK −XLF` −0,16 · `−XLK +XLF` +0,16 · `+XLE −XLK` +0,01) e **3 não**
(`+XLP −XLK` −0,56 · `+XLF −XLP` **+0,59** · `+XLF −XLU` +0,48). Os três sujos
são **beta disfarçado**. Isso derruba metade da razão de ser da transversal — a
de não competir com as views vivas pelo mesmo risco. Os pares com **energia** são
os genuinamente neutros.

**Régua (D22):**

- Lê o poly ⚠️ — **depende do gatilho a que for acoplada.** Sozinha ela não lê
  nada: é escolha de instrumento.
- Atua na bolsa ✅ — XLE/XLF/XLK/XLP/XLU/XLV, universo da D1.
- Teoria não desprovada 🟡 — **evidência dos dois lados, e agora medida.** A
  favor: 8 × 0. Contra: 6 de 8 instáveis. ⚠️ A **15f** e a **19b** reprovaram uma
  transversal, mas eram *view estrutural* de inflação com P montado por β contra
  breakeven, e o elo que falhou lá foi o **transporte** β → retorno (corr −0,84).
  Aqui não há β: o livro é declarado a priori. **São coisas diferentes**, e
  herdar aquele veredito sem reescrever a premissa é a armadilha da D26.
- Ortogonal ⚠️ — **3 de 6 livros reprovam**, e isso é falha de **desenho do
  livro**, não do eixo. Consertável.

**O que falta:**

1. **Neutralidade vira critério de desenho do livro.** Três dos seis livros
   declarados carregam meio índice dentro. Barato de consertar, e muda o que
   "ortogonal por construção" quer dizer neste projeto.
2. **Escolher o gatilho a que se acopla** — sem isso o item 1 da D22 não passa.
   É decisão, não medição. ⚠️ E a maratona estreitou as opções: a 1.1 e a 3.2
   morreram, então o estoque de gatilhos vivos é o **M4 recessão k = 5** — que
   já passa sozinho no livro direcional.
3. **Reabrir escopo da camada** — decisão do grupo.
4. **Âncora de tamanho** (12c).

### 🔬 SEGUNDA RODADA — `Dump/analises/Gate_transversal_neutro.md`

Os dois buracos que a rodada anterior deixou foram fechados, e **os dois vieram
positivos**. Livros hedgeados contra o SPY por β **expansivo defasado em 1 dia**,
semeado em `MINIMO_PREGOES = 60` (a constante que a 15f e a 3.1 direcional já
usam). Nenhuma premissa nova: livros, grades e teses são importados dos
artefatos anteriores.

**1. O hedge funcionou.** A maior |correlação| com o SPY cai de **0,59** para
**0,17**. Os três livros que eram beta disfarçado (`+XLP −XLK` −0,56 ·
`+XLF −XLP` +0,59 · `+XLF −XLU` +0,48) vão todos para ~|0,1|.

**2. A vantagem do livro setorial NÃO era beta disfarçado — ela CRESCE quando o
índice sai.** O placar vai de **8 × 0** (livro cru) para **14 × 0** (livro
neutro). Isso derruba a hipótese alternativa que a primeira rodada não
conseguia excluir: o que estava sendo medido é **spread**, não alavancagem
direcional disfarçada.

**3. O cruzamento salto × setorial, que não existia em artefato nenhum, dá 6 × 1**
a favor do livro neutro.

**4. E o que sobrevive ao corte da amostra deixou de ser célula isolada.**
7 de 26 aprovações sobrevivem, e a distribuição delas é o achado:

> ## 🟢 **M4 recessão, livro `+XLP⊥ −XLK⊥`, em k = 3, 5 e 10**
>
> **Três colunas contíguas da grade de seis**, todas passando o G2 e todas
> sobrevivendo às duas metades. Isso responde diretamente a ressalva que este
> arquivo levantava contra o M4 direcional: *"k = 5 é uma célula isolada, o
> padrão de quem garimpou o horizonte que funcionou"*. **Um bloco de horizontes
> vizinhos é bem mais difícil de conseguir por sorte que uma célula.**
>
> É a candidata mais forte que a camada tática já produziu — e continua presa à
> mesma pendência: **a contradição com a D19c**, que mediu inversão dentro da
> amostra neste mesmo mercado.

Os outros sobreviventes, todos com uma ressalva que os enfraquece:
**M7 Irã k = 20** (mercado da view C, que não entrou pela D23f) · **M9 Câmara
k = 20** e **M5 Trump q0.00** (o mecanismo partidário que a 2.4 reprovou fora da
amostra) · **M4 q0.75** — o **único corte de salto de verdade** que sobrevive,
já que o `q0.00` do M5 é a linha de base, não um salto.

### 🔬 TERCEIRA RODADA — `Dump/analises/Gate_mercados_irmaos.md`

O teste fora-da-amostra **de verdade**: partir a amostra em duas metades usa o
mesmo mercado, o mesmo ano e o mesmo regime. O teste forte é *o mecanismo se
repete num segundo mercado que deveria ter o mesmo mecanismo?* — e foi assim que
a **view 2.4** morreu (o TLT caiu nos dois mercados partidários quando deveria
inverter).

Dois pares existem no dado, com relação **declarada antes de medir**:
**partidário** (M5 Trump ↔ M9 Câmara, relação **espelho** — o μ cru tem de
inverter) e **geopolítico** (M7 Irã jun/2025 ↔ fev/2026, relação **igual** — o μ
cru tem de repetir). O teste é sobre o **μ cru**, sem alinhar premissa: alinhar
embutiria a resposta, já que as premissas partidárias são espelhadas por
declaração.

**O cruzamento célula a célula liquidou o nível 2 — mas não como eu previa:**

| célula viva | reproduz no irmão? | μ cru A/B |
|---|---|---|
| **M9 Câmara** `+XLP⊥ −XLK⊥` k = 20 | **✅** | `XLP⊥ −1,39/+2,23 ✅ · XLK⊥ +0,08/−2,62 ✅` |
| **M7 Irã jun/2025** `+XLE⊥ −XLK⊥` k = 20 | **❌** | `XLE⊥ +2,01/−1,23 ❌ · XLK⊥ −2,54/+0,18 ❌` |
| **M5 Trump** `+XLF⊥ −XLP⊥` (≈ k = 1) | **❌** | `XLF⊥ +2,11/+0,77 ❌ · XLP⊥ −0,14/+0,29 ✅` |

- **M7 Irã morre.** Sobrevive ao corte dentro do próprio mercado e falha quando
  o mercado muda — exatamente o padrão da **view C** (D23f), agora medido também
  na camada tática.
- **M5 Trump morre.** Idem, e com a ressalva de que a célula viva dele é um
  corte de salto (`q0.00`) que não existe na grade de lookbacks; a
  correspondência com k = 1 é aproximada.
- **M9 Câmara SOBREVIVE**, e isso é inesperado: é a única célula do projeto
  inteiro que passa G0, G1, G2, G3, o corte da amostra **e** a reprodução em
  mercado irmão. ⚠️ E está em tensão com a **2.4**: no livro direcional SPY/TLT
  o par partidário reproduz em só 2 de 6 células (consistente com o veredito da
  2.4), mas no **livro setorial neutro** reproduz em 3 de 6, incluindo a célula
  viva. **O que a 2.4 mediu foi o livro direcional.** Se isso reabilita o
  mecanismo partidário ou se é o livro achando estrutura onde não há, é decisão
  que precede qualquer módulo.

> ⚠️ **A taxa de reprodução do par NÃO é teste estatístico.** Partidário 43%,
> geopolítico 28%, contra 25% de acaso (livro de 2 pernas, exigindo acerto nas
> duas). As células **não são independentes** — k = 3 e k = 5 leem quase os
> mesmos dias, e os livros compartilham perna —, então o `n` efetivo é muito
> menor que 30 e a distância até 25% não sustenta significância. A taxa serve
> só para dizer se reprodução é rara ou comum no par; **quem decide candidata é
> o cruzamento célula a célula.**

> 🛑 **E o M4 recessão não tem irmão — limite estrutural, não omissão.** Não
> existe segundo mercado de recessão no dado (a própria D18d registra). A
> candidata mais forte da camada é justamente a que **nunca** poderá receber
> este teste. Ela depende para sempre do corte em metades (que passa, em três
> horizontes contíguos) **mais** a explicação da contradição com a D19c.

> ⚠️ **A pergunta desconfortável continua de pé, com outra redação.** O eixo
> está agora demonstrado com força (14 × 0, hedge conferido) — mas **o único
> bloco que sobrevive é no mesmo mercado que já passa no livro direcional**. A
> transversal melhora o resultado do M4 (3 horizontes contíguos em vez de 1
> célula) sem ainda ter um gatilho que **só** funcione com ela. Segue como
> **eixo comprovado que reforça um gatilho existente**, e não como candidata
> independente.

> ⚠️ **O que a segunda rodada NÃO fez:** varrer os 15 pares setoriais possíveis.
> Continua **um par por mercado, declarado pelo mecanismo**. Varrer atrás do que
> funciona é pescaria, e é o vício que a D2b existe para barrar.

---

## Fora deste arquivo

- **1.3 prêmio de anúncios** e **drift pós-FOMC (T1+T3)** são táticas **medidas**
  e desligadas pela 12c — não são candidatas por vacuidade. Ficam na D12c e no
  `Retomada_tatica.md`. Nota registrada: o drift foi a **única tática do projeto
  que mediu positivo** (+0,08 a +0,80 pp).
- **Os quatro artefatos da maratona** ficam em `Dump/analises/`:
  `Gate_event_driven.md` · `Gate_PEAD.md` · `Gate_noticia.md` ·
  `Gate_transversal.md`, gerados por `scripts/gate_*.py` e cobertos por 17
  testes em `tests/test_gate_*.py`.
