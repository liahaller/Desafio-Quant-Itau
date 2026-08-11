# O Ω reativo — confiança medida, não arbitrada

> Seção do relatório final referente ao módulo de confiança do Black-Litterman.
> Escrita em 09/08/2026 sobre a calibração das views 2.2 (CPI) e 2.3 (FOMC).
> Os resultados de carteira ficam na seção de backtest; aqui trata-se de como a
> confiança é construída e por que se pode confiar nela.

---

## 1. O problema: Ω é o elo subjetivo do Black-Litterman

O modelo de Black-Litterman combina o equilíbrio de mercado com as visões do
gestor. A matriz **Ω** é o peso relativo entre as duas coisas: ela declara
quanta incerteza há em cada view. Na formulação de He & Litterman,

```
Ω_ii = c_i · diag( P τ Σ Pᵀ )_ii
```

onde `c_i = 1` recupera o BL clássico e `c_i > 1` encolhe a view em direção ao
prior.

A crítica clássica ao BL não é sobre a álgebra — é sobre de onde saem `Q` e
`Ω`. Na prática usual, ambos são declarados pelo gestor: "estou 60% confiante
nesta view". O modelo herda a subjetividade inteira e a esconde atrás de uma
matriz. É o elo em que qualquer resultado pode ser produzido escolhendo os
números certos depois de ver o backtest.

**A proposta deste trabalho é remover a arbitrariedade dos dois lados.** As
views vêm de probabilidades negociadas com dinheiro real no Polymarket — não
de opinião. E o `Ω` vem de uma régua cuja **forma foi escolhida por um teste
estatístico definido antes de ver o resultado**, sobre uma grandeza que não é
o retorno da carteira.

Restou exatamente **um** número livre no Ω, e ele é declarado como parâmetro
de risco, não de régua (§9).

---

## 2. A régua

```
c = ( (1 + v̄) · (1 + |Σp − 1|) ) ^ nível
```

Dois fatores, cada um a medida de um defeito da leitura do mercado. Cada
defeito **multiplica** a incerteza por (1 + o tamanho do defeito).

| Fator | O que mede | Definição |
|---|---|---|
| `1 + v̄` | **Instabilidade.** Quanto a distribuição de probabilidade se moveu nas últimas leituras | `v̄` = média da variação total, `0,5·Σ_b \|p_{t,b} − p_{t−1,b}\|`, nas 5 variações que terminam na decisão |
| `1 + \|Σp − 1\|` | **Desarranjo do livro.** Quanto as faixas do mercado deixam de descrever uma distribuição | soma das faixas na leitura da decisão, medida **crua** |

Mais um portão, que não é fator e sim **veto**: mercado sem nenhuma
negociação no slot sai da carteira (`ativa = False`), em vez de receber `c`
grande.

Três propriedades que a forma garante por construção, sem truncamento, piso
ou teto:

- **`c ≥ 1` sempre.** O baseline de He-Litterman é o *teto* de confiança: o Ω
  só tira peso da view, nunca adiciona. Não existe estado do mercado em que o
  modelo fique mais confiante do que o BL padrão já estaria.
- **`nível = 0` devolve `c = 1`** para toda view, recuperando o BL clássico.
  O nível é um botão contínuo entre "ignorar a qualidade do sinal" e "levá-la
  a sério".
- **Sem divisão por zero e sem descontinuidade.** Os dois fatores são ≥ 1 em
  qualquer entrada válida.

### Por que multiplicativa, e não uma soma ponderada

Uma soma ponderada permitiria compensação indevida: um mercado com o livro
completamente desarranjado poderia ser "salvo" por estar estável. Os dois
fatores medem condições necessárias distintas, e a falha de qualquer uma
degrada a leitura independentemente da outra.

### Por que a coerência é medida no livro cru e a estabilidade no renormalizado

As faixas de um mercado de buckets são livros separados, e elas se
desencontram: medimos somas de **0,92 a 1,33** no mercado de cortes do Fed e
de **0,75 a 2,73** nos mercados de CPI (mediana 1,02). Isso é informação sobre
a saúde do mercado.

A estabilidade, porém, precisa medir **movimento de opinião**, não
desarranjo. Se a PMF não fosse renormalizada antes do colapso, uma variação
na soma total entraria como "o mercado se moveu", e os dois fatores estariam
punindo a mesma coisa duas vezes — num produto, isso seria dupla contagem
disfarçada de confirmação mútua. A renormalização deixa o desarranjo
inteiramente com o segundo fator.

---

## 3. O protocolo: quem decide o quê

A régua foi construída sob uma disciplina declarada **antes** da calibração,
justamente para que a escolha das formas não pudesse ser feita olhando o
resultado da carteira.

**1. O que a matemática determina.** A relação entre `c` e `Ω` sai de He &
Litterman. Não é escolha.

**2. O que a semântica determina.** A estrutura multiplicativa e o papel do
volume como veto, não como fator. Um mercado sem liquidez não tem um preço
que seja probabilidade; isso não é uma questão de grau.

**3. O que o dado determina.** Tudo o que sobrou: quais ingredientes entram,
a janela da estabilidade, a grade temporal, a forma do decaimento.

O critério do item 3 é um **teste de monotonicidade**: faixas de confiança
maiores devem apresentar **erro realizado da probabilidade** menor. Reporta-se
a correlação de Spearman entre score e erro futuro e a média do erro por
tercil de confiança. Empates resolvem-se pela forma com menos parâmetros.

> **O alvo é o erro da probabilidade, não o retorno da carteira.** Esta é a
> trava central contra o overfit. Se a forma da régua fosse escolhida por
> resultado de backtest, todo o argumento de objetividade cairia — seria
> apenas subjetividade com mais passos. A consequência é assumida: a forma
> **não é revisitada** se o backtest desagradar. O que se ajusta, nesse caso,
> é o teto de alavancagem, que é um parâmetro de risco declarado.

---

## 4. Os dados

| | View 2.3 (FOMC) | View 2.2 (CPI) |
|---|---|---|
| Mercados | 18 reuniões (76 faixas) | 18 mercados-mês (111 faixas) |
| Slots (grade 12h) | 3.905 | 1.142 |
| Slots (grade 24h) | 1.952 | 534 |
| Volume por slot | 76/76 faixas, 1.242 slots julgáveis | 111/111 faixas, 1.142 slots julgáveis |

Preço: endpoint `/prices-history` do CLOB do Polymarket, passo nativo de 12h.
Volume: reconstruído trade a trade pela Data API (`/trades`), agregado em
`notional_usd` por slot — não existe endpoint de volume histórico pronto.

A calibração roda sobre a **história completa dos mercados**, e não sobre a
janela do backtest. O alvo do teste é o erro da probabilidade, que existe
mesmo nos dias em que a view não seria negociada; e os dias de livro
degenerado são justamente a condição que deve produzir score baixo. Excluí-los
removeria o poder discriminante do teste.

Cada mercado é uma série própria: nem as variações nem o alvo cruzam a
fronteira entre eventos. Sem esse cuidado, um `.diff()` sobre o painel
empilhado compararia a PMF de uma reunião com a da seguinte.

---

## 5. Resultados

Correlação de Spearman entre score e erro realizado da probabilidade. **Mais
negativo é melhor** — significa que confiança alta antecede erro pequeno.

| Ingrediente | 2.3 (FOMC) | 2.2 (CPI) | Monotônica | Veredito |
|---|---|---|---|---|
| Estabilidade (variação total) | **−0,40** | **−0,47** | ✅ | **entra** |
| Estabilidade (\|ΔE\|) | −0,38 | −0,43 | ✅ | perde no desempate |
| Coerência do livro | −0,15 a −0,18 | **−0,23 a −0,32** | ✅ | **entra** |
| Portão de volume (como score) | −0,10 a +0,19 | −0,11 a +0,14 | — | reprovado |
| Proximidade do evento | +0,07 a +0,22 | +0,11 a +0,37 | ✗ | **reprovado** |

Cada faixa cobre as combinações testadas (2 grades temporais × 2 horizontes de
erro × 3 janelas); os valores em destaque são a melhor configuração de cada
ingrediente, com o alvo em variação total. A escolha entre as duas formas de
estabilidade é sensível ao alvo, e isso está tratado na §9.

As duas views rodam com **os quatro ingredientes**. Até 10/08 a 2.3 rodava com
dois, porque a reconstrução de volume não alcançava os mercados do FOMC; a
entrega da chave de junção e das 76 faixas fechou essa lacuna, e a rodada
completa **confirmou a régua sem alterar nenhuma escolha**. A regra que
decidiria o contrário foi registrada e versionada *antes* de a rodada existir:
concordância confirmaria, discordância seria declarada como limitação e não
mudaria a forma — porque trocar a régua ao ver a segunda view é escolher depois
do dado, e é exatamente o que a trava do §3 proíbe.

Parâmetros que o dado escolheu: **janela de 5 variações** (vence 10 e 20 em
todos os cortes das duas views) e **grade de 12h** (vence a de 24h em todos).

### O teste que sustenta o ingrediente principal

O ingrediente mais forte esteve sob suspeita de ser um artefato de medição
(§7.1), e o resultado só passou a valer depois de essa suspeita ser testada
diretamente. Medindo a estabilidade **apenas nos slots que passam pelo veto de
liquidez**:

| | Spearman | n |
|---|---|---|
| Todos os slots | −0,4615 | 996 |
| Somente slots com negociação | −0,4531 | 932 |

O sinal sobrevive: o veto custa 6% da amostra e move a correlação em 0,008. O
ingrediente **não vivia do artefato**.

O diagnóstico direto confirma pelo outro lado — comparando slots com e sem
negociação:

| | Variação exatamente zero | Erro futuro médio |
|---|---|---|
| Sem negociação | 4,4% dos pares | 0,0318 |
| Com negociação | 1,2% dos pares | 0,0346 |

O congelamento existe (é 3,7× mais frequente sem negociação, exatamente como
previsto), mas é raro demais em termos absolutos para explicar uma correlação
de −0,46.

**O mesmo teste, repetido na segunda view.** Com o volume do FOMC disponível, a
verificação que sustentava o ingrediente numa view só foi repetida na outra, e
dá o mesmo veredito: −0,4005 em todos os slots contra −0,3960 apenas nos slots
com negociação — um movimento de 0,005. A suspeita da §7.1 está encerrada nas
duas views, e não por analogia.

Vale registrar o que **não** se sustentaria sem esse teste. Na 2.3, os slots
sem negociação têm erro futuro médio quatro vezes menor que os demais (0,0037
contra 0,0147), que é precisamente a assinatura do artefato temido: mercado
parado prevê mercado parado. O que desarma a objeção não é a ausência do
mecanismo — é a raridade dele: são 24 slots contra 1.139. O mecanismo é real e
irrelevante em volume, e essas são coisas diferentes que só a medição separa.

### Robustez: os vereditos dependem do corte escolhido?

Duas verificações, porque um teste que só funciona com os parâmetros em que
foi rodado não é evidência.

**Número de faixas.** O teste roda com 2, 3, 4 e 5 faixas. O `spearman` é
idêntico nas quatro — e isso não é um resultado, é uma identidade: ele é
calculado sobre postos, e as faixas existem só para a leitura de
monotonicidade. Registramos a distinção porque apresentá-la como robustez
seria vender uma tautologia. O que de fato varia é a **flag de
monotonicidade**, e ela se mantém em todas as contagens para os dois
ingredientes que entraram na régua, nas configurações escolhidas. Onde ela
oscila é nas janelas longas (20 variações) e na grade de 24h — ambas já
descartadas por outros critérios.

**Alvo alternativo, independente das candidatas.** A calibração usou a
variação futura da probabilidade, o que é circular para comparar as duas
formas de colapso: cada uma tende a vencer no alvo medido por ela mesma. O
segundo alvo é o **erro contra o desfecho real**: a massa de probabilidade que
o mercado alocou fora do bucket que resolveu.

> O desfecho **não pode** sair do próprio mercado. Tomar como resultado o
> bucket mais provável no último slot assumiria que o mercado acertou, e o
> erro contra ele seria pequeno por construção justamente onde o mercado
> estava confiante — circularidade pior que a original. O desfecho é derivado
> da **taxa efetiva dos fed funds** (DFF, FRED): a variação da taxa em torno
> da reunião, arredondada à grade de 25 bps. A derivação foi validada contra
> as 16 reuniões em que o mercado terminou inequívoco (acima de 0,9 num
> bucket): **concorda em 16 de 16**, e resolve as 2 reuniões que o mercado não
> resolveu — incluindo o corte surpresa de 50 bps de setembro de 2024, em que
> o mercado terminou dividido em 0,517 contra 0,468.

| Ingrediente | Alvo: variação futura | Alvo: desfecho (DFF) |
|---|---|---|
| Estabilidade (variação total) | −0,31 a −0,40 | −0,44 a −0,46 |
| Estabilidade (\|ΔE\|) | −0,29 a −0,38 | −0,43 a −0,47 |
| **Coerência do livro** | −0,15 a −0,18 | **−0,45 a −0,46** |
| Proximidade do evento | +0,07 a +0,22 | **+0,29 a +0,72** |

Três leituras, todas favoráveis à régua escolhida:

1. **A coerência é muito mais forte do que a primeira calibração sugeria.**
   Contra o desfecho ela triplica e passa a competir de igual para igual com a
   estabilidade — na grade de 24h é a melhor candidata isolada. O desarranjo
   do livro prevê mal o movimento de curto prazo e prevê bem o erro contra o
   resultado, o que é coerente com o que ele mede: um livro que não fecha é um
   mercado que não está processando informação, não um mercado agitado.
2. **A rejeição da proximidade fica mais forte, não mais fraca.** No alvo
   independente ela chega a +0,72 — o sinal invertido não era artefato do alvo
   original.
3. **As duas formas de colapso empatam no alvo neutro** (diferenças de 0,002 a
   0,017, com a ordem trocando entre grades). Isso **confirma** que o
   desempate por parcimônia foi a decisão certa, e não um recurso para
   escapar de uma comparação inconclusiva: quando o alvo deixa de favorecer
   qualquer uma delas, não há vencedora.

**O mesmo alvo na segunda view — e o que ele revela sobre o próprio alvo.** O
desfecho da 2.2 é o **CPI mensal realizado** (variação mensal com ajuste
sazonal, na versão publicada no dia do anúncio, do ALFRED — não a série
revisada, que em dois meses cairia no bucket errado). A derivação foi validada
como a do DFF: o valor publicado cai no bucket que o mercado resolveu em **15
de 15** meses, incluindo as três pontas abertas.

| Ingrediente | 2.3: desfecho (DFF) | 2.2: desfecho (CPI) |
|---|---|---|
| Estabilidade (variação total) | −0,44 a −0,46 | −0,05 a −0,13 |
| Estabilidade (\|ΔE\|) | −0,43 a −0,47 | **+0,11 a +0,26** |
| Coerência do livro | −0,45 a −0,46 | −0,02 a +0,01 |
| Proximidade do evento | +0,29 a +0,72 | +0,16 a +0,25 |

A leitura honesta tem duas partes, e a segunda é mais importante que a primeira.

**A magnitude despenca — e a causa é medível, não especulativa.** No FOMC o
mercado converge: no último slot, a probabilidade no bucket que de fato
resolveu tem mediana **0,97**, e 83% das reuniões terminam acima de 0,90. No
CPI o mercado não converge: mediana **0,39**, e apenas 7% dos meses passam de
0,90. Onde o desfecho é antecipável, "quanta massa ficou fora do resultado"
decai ao longo da vida do mercado e discrimina bem; onde a incerteza é
irredutível até a publicação, esse alvo é dominado pelo tamanho da surpresa do
mês — uma propriedade do evento, não da qualidade do livro naquele instante.
O alvo perde poder na 2.2, e isso é uma limitação **do alvo**, não da régua.

**O que sobrevive é uma distinção, e ela desempata o que faltava.** A variação
total mantém o sinal correto nos quatro cortes da 2.2; a \|ΔE\| **inverte** o
sinal nos quatro. Na 2.3 as duas empatavam, e a escolha da régua foi feita por
parcimônia, explicitamente sem evidência estatística (§9). Num alvo
independente e numa view diferente, a candidata escolhida é a única que não
inverte. É pouca magnitude e é evidência fraca — mas aponta na direção da
escolha já registrada, e não contra ela.

Nenhum dos dois meses em que o resultado existe apenas como resolução do
mercado (o CPI que o *shutdown* de 2025 impediu de ser publicado, e o mês
seguinte, sem base de comparação) foi usado. Ambos têm desfecho declarado pelo
oráculo do Polymarket e nenhum número independente, e aceitá-los reintroduziria
por uma porta lateral a circularidade que este alvo existe para remover — nos
dois meses mais anômalos da amostra, ainda por cima.

### Um teste não planejado: o calendário estava errado

Durante a redação desta seção, o calendário oficial do CPI (FRED) revelou dois
erros no calendário que vínhamos usando, ambos na janela do *shutdown* de
2025: uma divulgação atrasada em nove dias e uma que **nunca ocorreu** —
um evento fantasma no arquivo.

Recalculada a calibração com o calendário corrigido, **um único número mudou**:
o da proximidade do evento, que passou de +0,09/+0,31 para +0,10/+0,37 na 2.2
(mais reprovada do que antes). Estabilidade, coerência e portão saíram
idênticos.

Não é coincidência, e é o argumento mais forte disponível a favor da régua
escolhida: **os dois ingredientes que entraram não consultam o calendário.**
Eles medem propriedades da leitura do mercado — quanto a distribuição se moveu
e se o livro fecha —, e não propriedades da agenda. O único candidato que
dependia de saber quando o evento aconteceria é justamente o que foi
descartado. Uma régua construída sobre "faltam N dias para o anúncio" teria
herdado o erro inteiro, silenciosamente, e sem nenhum sintoma que a
calibração pudesse detectar.

A lição geral, que vale além do Ω: numa janela histórica curta, um erro de
calendário pode pesar mais que boa parte das escolhas de modelo. O que ele
sustenta não é "o resultado melhorou" — é que dado de calendário deve vir de
fonte oficial em tudo que for medido.

---

## 6. O que foi rejeitado

Esta seção é parte do resultado, não um apêndice. Uma régua que só registra o
que entrou não permite avaliar se a escolha foi disciplinada.

**Proximidade do evento — reprovada com o sinal invertido.** A hipótese
inicial era que a incerteza aumenta perto de uma decisão agendada. O dado diz
o contrário, nas duas views, em 16 cortes independentes: **longe do evento o
mercado se move mais**, não menos — a probabilidade se cristaliza à medida que
a decisão chega. A rejeição sobrevive à troca do alvo, e com folga maior
(§5). O ingrediente saiu da régua pelo protocolo. Entrar com o
sinal trocado seria escolher o sinal depois de ver o dado, que é precisamente
o que a trava do §3 existe para impedir. O achado fica registrado como
resultado e como candidato para uma versão futura, com hipótese declarada
antes do teste.

**Volume como ingrediente gradual — reprovado.** Não pontua sozinho (−0,03 a
+0,14, sinal predominantemente invertido: mais volume antecede *mais*
movimento, o que é econômicamente sensato — volume chega com notícia). E
nenhum threshold calibrado melhora a régua: exigir liquidez acima do 1º, 2º ou
3º quartil piora o Spearman em até 0,14 e consome amostra. Sobrevive apenas o
veto do slot sem **nenhuma** negociação, que é gratuito e tem justificativa
semântica independente.

**Agregação de volume pelo mínimo entre faixas — rejeitada por medição.** Era
a opção conservadora, mas veta 47% dos slots de 12h: é comum que uma faixa de
um mercado de buckets não negocie em meio dia. A agregação por soma é a que
mede atividade do mercado, não da faixa menos ativa.

**A forma simétrica `(1 − x)` para os fatores — rejeitada por medição.** Seria
a escolha natural ("fração da massa que ficou parada" × "quanto o livro
fecha"), mas o fator de coerência **fica negativo em 7 de 1.139 leituras**
completas do CPI, onde a soma do livro chega a 2,73. Corrigir isso exigiria
truncar o fator em zero, o que criaria um segundo veto binário — e o
compromisso metodológico assumido é que o **único** veto binário da régua é o
de liquidez, para que nenhum defeito seja cobrado duas vezes.

**Normalização por posto histórico — rejeitada por argumento.** Tornaria o `c`
relativo à história em vez de absoluto: o mercado em bom estado receberia
confiança baixa no seu pior dia, e o mesmo estado do mercado produziria `c`
diferente em datas diferentes.

**Convergência entre fontes (polls, casas de aposta) — fora do escopo.**
Adicionaria dependências de dados que não caberiam no prazo; fica como stub.

---

## 7. Três achados de medição que mudaram a régua

Os três surgiram de conferir o que o dado era, e não do que se supunha que
fosse. Cada um teria produzido uma inversão de sinal silenciosa.

### 7.1 A série é midpoint amostrado, não último trade

O `/prices-history` devolve o **midpoint do book no instante t**, não o preço
do último negócio nem um agregado do intervalo. A consequência é grave para o
ingrediente de estabilidade: um mercado sem nenhuma negociação **continua
reportando o mesmo número**, e midpoint parado é lido como estabilidade
perfeita. Sem o veto de liquidez, a régua daria confiança **máxima** ao
mercado mais ilíquido — uma inversão sistemática de sinal, não ruído. Foi este
achado que transformou o volume de "quarto ingrediente" em pré-condição, e é a
razão pela qual a §5 gasta um teste inteiro para verificar se o ingrediente
sobreviveu.

### 7.2 Preencher buracos para a frente (`ffill`) injeta estabilidade falsa

A série tem leituras faltantes. O tratamento usual — repetir a última leitura
— é inutilizável aqui: leitura repetida entra na conta como **variação zero**,
de modo que quanto mais esburacado o mercado, mais estável ele pareceria. É a
mesma inversão da §7.1 por outro caminho, e pior que ruído: o `ffill` é
determinístico e erra num sentido só (nunca aumenta a variação medida), o que
é **viés**, e o teste de monotonicidade não distingue viés de sinal.

Regra adotada: slot com qualquer faixa sem leitura **não entra** no cálculo de
variação, e o par deixa de ser adjacente. O buraco continua custando confiança,
mas por um canal só.

Corolário de método: **o score não deve reproduzir a série que a view
consome.** A série tratada é suave por construção; medir a estabilidade nela
seria medir a estabilidade do tratamento. O score mede se o mercado que gerou
o insumo estava funcionando.

### 7.3 A janela entregue não vem na grade completa

O bloco de diagnóstico entrega apenas as leituras existentes, omitindo os
slots inteiramente vazios. Duas linhas vizinhas na lista podem, portanto,
estar a mais de um slot de distância — e uma diferença calculada entre elas
leria como *uma* variação o que são duas ou três, contaminando exatamente os
pares que a regra da §7.2 manda descartar. A implementação reconstrói a grade
de 12h antes de qualquer diferença, e há teste dedicado a esse caso.

---

## 8. Implementação e validação

A régua está implementada em `lia/omega.py`, com **55 testes** na suíte do
módulo. Toda função matemática tem caso sintético com resultado conhecido:
PMF parada devolve fator 1,0; massa movida conhecida devolve o valor exato; o
fator de coerência é bilateral; `nível = 0` recupera He-Litterman.

Testes sintéticos, porém, não provam que o contrato com o pipeline funciona.
A régua foi executada de ponta a ponta sobre o bloco de diagnóstico **real**,
em 573 decisões da view 2.2:

| | |
|---|---|
| Views ativas | 515 (89,9%) |
| Inativas por veto de liquidez | 37 |
| Inativas por ausência de leitura mensurável | 21 |
| `c` mínimo · mediana · p95 · máximo (nível = 1) | 1,0016 · 1,0496 · 1,2488 · 2,7653 |

Nenhum `c` abaixo de 1 e nenhum `NaN` em view ativa, como a forma garante.

**Uma regra de borda vale registro:** view sem nenhum par adjacente completo
na janela sai como **inativa**, não com `c = 1`. Sem par não há como
qualificar a leitura, e atribuir confiança máxima onde nada foi medido é o
pior erro disponível — é o caso em que a régua estaria mais errada e menos
capaz de perceber.

### Dois defeitos encontrados por revisão cruzada

Ambos foram medidos por outro membro da equipe sobre o código já escrito, e
ambos invertiam o sinal da régua em silêncio:

1. O portão convertia `NaN` em `0,0`, de modo que **346 slots** em que o
   volume era desconhecido (por truncamento do limite de coleta) vetavam o
   mercado — o oposto da regra, que separa "ninguém negociou" (veta) de "não
   sabemos" (não veta).
2. A combinação de scores inferia veto de `score == 0,0`, o que invertia dois
   ingredientes: o score de estabilidade era `−desvio`, e portanto `0,0` era o
   **melhor** valor possível.

Um terceiro apareceu por um caminho diferente, e vale registrar o caminho. Ao
conciliar com o pipeline quantos mercados de CPI existiam, sobrou um: nós
contávamos 19 e o dado tinha 18. A divergência era pequena o bastante para ser
tratada como detalhe de contagem — e era o sintoma de um mês (julho de 2025)
entrando **duas vezes** na calibração, sob dois rótulos diferentes, com os
mesmos identificadores de mercado, os mesmos 56 instantes e diferença máxima
zero entre as leituras. A identidade de um mercado passou a ser o identificador
do contrato, não o nome do arquivo. Removida a duplicata, todos os coeficientes
melhoram ligeiramente (o principal vai de −0,4615 a −0,4717) e **nenhuma
ordenação muda** — o efeito era pequeno, mas a lição não é sobre o tamanho do
efeito: uma discrepância de contagem entre duas pessoas olhando a mesma base é
barata de investigar e cara de ignorar.

---

## 9. Limitações declaradas

**O portão de liquidez julga menos slots na 2.3 do que na 2.2.** A lacuna
anterior — a reconstrução de volume não alcançava os mercados do FOMC — foi
fechada, e as duas views rodam com os quatro ingredientes. O que resta é
desigual: 42 das 76 faixas do FOMC atingiram o limite de coleta da API, e um
slot com qualquer faixa truncada sai como volume desconhecido, que **não veta**
(§7.1). Na prática, o portão desativa 4,0% das decisões da 2.2 e 1,2% das da
2.3. O truncamento morde os slots antigos e não a janela de decisão de cada
reunião, o que limita o dano; ainda assim, o veto de liquidez é uma verificação
mais fraca na 2.3.

**Os dois ingredientes que entraram correlacionam +0,37 a +0,40 entre si.**
Não é a dupla contagem mecânica que a renormalização eliminou (§2), mas também
não são medidas ortogonais: parte da penalidade é cobrada duas vezes no
produto. Registrado e não resolvido — separá-los exigiria uma reformulação que
não caberia no prazo.

**O empate entre as duas formas de colapso foi resolvido por parcimônia, não
por evidência.** Na view 2.3 a variação total vencia em todos os cortes; na
2.2 cada candidata vence no alvo medido por ela mesma. O alvo independente
(§5) mostra que o empate é real e não um artefato da comparação: sem um alvo
que favoreça qualquer das duas, elas ficam a 0,002–0,017 uma da outra e a
ordem troca entre grades. A escolha continua sendo do critério de parcimônia
do protocolo — o que mudou é que agora se sabe que não havia vencedora a ser
encontrada. O alvo por desfecho na 2.2 é o único corte em que as duas se
separam de forma consistente, e separa a favor da escolhida; é evidência fraca
em magnitude, e está registrada como tal, não como confirmação.

**A janela ideal difere entre os dois alvos.** A régua usa 5 variações, que
vence com folga no alvo de variação futura nas duas views. No alvo por
desfecho, a janela de 10 fica ligeiramente à frente na 2.3 (−0,458 contra
−0,443), e na 2.2 a de 20 fica à frente na grade de 24h. As diferenças são
pequenas e não apontam todas para a mesma alternativa; a janela de 5 foi
mantida por ser o critério declarado antes do teste. Fica registrado — e
declarado agora, não depois de olhar o backtest, justamente porque a regra é
que a forma não se ajusta a resultado de carteira.

**O alvo por desfecho tem pouco poder discriminante na 2.2.** A verificação de
não circularidade existe hoje nas duas views, o que não era o caso até
10/08/2026. Mas os coeficientes na 2.2 são pequenos (−0,05 a −0,13 para o
ingrediente principal), pela razão medida na §5: o mercado de CPI não converge
antes da publicação, então a massa alocada fora do resultado mede sobretudo o
tamanho da surpresa do mês. A conclusão que essa verificação sustenta na 2.2 é
de **sinal** — qual candidata não inverte —, não de magnitude.

**Dois meses de CPI ficam fora dessa verificação, e um mercado do universo tem
resolução sem número.** O *shutdown* de 2025 impediu a publicação de um CPI que
o mercado mesmo assim resolveu, e deixou o mês seguinte sem base para a
variação mensal. Os dois foram excluídos do alvo por desfecho por não terem
número independente. Vale notar o que isso implica para o projeto além do Ω: há
mercado no universo cujo desfecho existe apenas como decisão de um oráculo, sem
contrapartida verificável em série oficial.

**Duas views, não vinte.** A replicação entre 2.2 e 2.3 é o que dá alguma
confiança de que os resultados não são propriedade de um mercado específico —
particularmente no caso da proximidade, reprovada com o mesmo sinal invertido
nas duas. Ainda assim, são dois mercados.

**O nível global ainda não está fechado.** É o único parâmetro livre da régua,
e será cravado uma única vez, junto com o teto de alavancagem, por decisão de
risco declarada. A ordem importa: hoje o teto de alavancagem faz parte do
trabalho que caberia ao Ω, então o `c` entra primeiro, mede-se a alavancagem
resultante, e só então se decide o teto. O botão existe justamente porque a
escala apropriada é uma decisão de apetite a risco, não de estatística.

O que já se pode dizer sobre ele, medido: **a régua discrimina, mas não
encolhe a carteira.** Expressa como confiança relativa (o inverso do
multiplicador), com `nível = 1` ela vai de 0,95 na mediana a 0,36 no pior
mercado; com `nível = 5`, de 0,79 na mediana a 0,006 no pior. A cauda desaba
muito antes do centro — e para levar a *mediana* ao ponto em que o
dimensionamento pedido cairia de fato seria preciso um nível da ordem de 95,
o que não é uma escolha, é uma impossibilidade. Ou seja: o Ω separa mercado
confiável de mercado ruim, e não substitui o limitador de tamanho da
carteira. Os dois têm de conviver, e é por isso que o nível e o teto se
decidem na mesma conversa.

**E o efeito é muito desigual entre as duas views**, o que importa para essa
decisão. Em confiança relativa, por view (decisões ativas):

| Nível | 2.2 mediana | 2.2 pior | 2.3 mediana | 2.3 pior |
|---|---|---|---|---|
| 1 | 0,950 | 0,362 | 0,988 | 0,817 |
| 3 | 0,858 | 0,047 | 0,965 | 0,545 |
| 5 | 0,775 | 0,006 | 0,942 | 0,364 |

O mercado de decisão do Fed tem livro que fecha e distribuição que se move
pouco, então a régua quase não o modula: com `nível = 5`, o pior dia da 2.3
ainda está onde a 2.2 já se encontra com `nível = 1`. Isso **não** é defeito —
é a régua dizendo que aquele mercado é bom —, mas implica que escolher o nível
pelo efeito agregado subestima quanto ele morde a view de inflação, porque a
outra dilui a média. A recomendação é que a curva de decisão seja lida por
view; um nível **por** view seria outra coisa, e criaria dois botões onde o
protocolo pediu um.

Diferentemente da versão anterior desta tabela, os números acima já incluem o
veto de liquidez nas duas views. A suavidade da 2.3 não era efeito da falta do
portão: com ele, apenas 1,2% das decisões saem por liquidez.

---

## 10. Síntese

O Ω deste trabalho não pergunta ao gestor quanta confiança ele tem. Ele mede
três coisas verificáveis no mercado que gerou a view — se houve negociação, o
quanto a distribuição se moveu, e se o livro fecha — e converte isso num
multiplicador de incerteza cuja forma foi escolhida por um teste contra o erro
realizado da probabilidade, não contra o retorno da carteira.

Dos quatro ingredientes candidatos, **dois entraram, um virou veto e um foi
reprovado** — inclusive um que a intuição inicial dava como certo. É esse
saldo, e não a régua final, que sustenta a afirmação de que a confiança aqui
foi medida e não arbitrada.
