# Pauta da reunião — em português claro

Todas as decisões que estão travadas esperando a reunião, explicadas sem jargão.
Ordem: da que trava mais coisa para a que trava menos.

> Nota: a lista foi montada da versão de `Decisoes_pendentes.md` do commit `7b9d036`. A versão que está hoje
> na pasta é mais curta (não traz as decisões 9 a 12) **por decisão do grupo** — não é perda acidental de merge,
> e não deve ser "restaurada".
>
> Atualizada em 30/07 com a segunda entrega do Paulo (`RESPOSTA_FOLLOWUP_Pedido_Paulo_dados.md`, F1–F10,
> medida ao vivo em 29/07). As seções marcadas **ATUALIZADA** mudaram por causa dela.
>
> **Segunda atualização em 30/07 (sessão da tarde), agora com o dado RODANDO.** Três documentos novos medem
> o que antes era opinião: `Sensibilidade_decisoes_1.1_1.2_6.1.md`, `Perfil_defasagem_k.md` e
> `Proposta_4.1_horizontes.md`. As seções marcadas **MEDIDA** mudaram por causa deles — em dois casos a
> medição **inverte** o que esta pauta dizia. Nada foi decidido: só deixou de ser achismo.

---

# 🔴 BLOCO 1 — Trava tudo

## 1.1 Como corrigir o "otimismo" dos preços do Polymarket ⚠️ MEDIDA

**O que é.** Em qualquer mercado de apostas, as pessoas pagam caro demais por coisas improváveis — é o
mesmo efeito de quem compra bilhete de loteria. Isso é conhecido na literatura como *favorite-longshot
bias*. Na prática: quando o Polymarket diz "10% de chance de recessão", a chance real costuma ser menor,
talvez 6%. O preço tem uma gordura embutida.

**Por que importa.** A gente usa esses números como se fossem probabilidades honestas. Se não corrigir, todo
sinal sai um pouco torto — e torto de forma sistemática, sempre na mesma direção. O efeito é pior justamente
na view de recessão, porque mercados de recessão vivem na faixa de probabilidade baixa, que é onde a
distorção é máxima.

**As opções.**
- **Calibrar por conta própria** — pegar mercados do Polymarket que já resolveram, comparar "o que o preço
  dizia" com "o que de fato aconteceu", e montar a curva de correção com o nosso próprio dado. Mais honesto,
  dá trabalho, e depende de ter mercados resolvidos suficientes.
- **Usar uma curva pronta da literatura** — existe correção publicada e citável. Rápido e defensável, mas foi
  calibrada em outro tipo de mercado (apostas esportivas), não no Polymarket.
- **Não corrigir no v1** — assumir o viés e escrever no relatório que ele existe. É uma escolha legítima
  desde que documentada, e tem a vantagem de não inventar número nenhum.

**O que a medição mostrou (30/07).** O efeito é **muito menor do que se supunha nos mercados de faixas e
grande onde ninguém estava olhando**. Varrendo uma família de correção de força crescente sobre os 17 meses
de CPI, a inflação esperada quase não se move (o deslocamento fica em no máximo 30% do que o próprio número
varia no tempo — ou seja, dentro do ruído). Já no mercado **binário de recessão**, que vive em probabilidade
baixa, a mesma correção derruba a mediana de 20,5% para 15,5% e o primeiro decil de 3,0% para **1,3%** — mais
da metade. Tradução: **esta decisão é da view de recessão (3.1) e da eleitoral (2.4), não da de inflação.**

**Se não decidir.** Nada roda. O código tem um buraco proposital nesse ponto — ele **falha na hora** em vez
de usar um valor chutado. Foi feito assim de propósito, pra ninguém rodar o modelo com um número inventado
sem perceber.

---

## 1.2 Que número vale o "balde aberto" ⚠️ ATUALIZADA · MEDIDA

**O que é.** Os mercados de CPI no Polymarket são divididos em faixas: "3,7%", "3,8%", "3,9%"… e uma faixa
final aberta, tipo **"3,6% ou menos"**. Pra calcular a inflação média que o mercado está esperando, cada
faixa precisa virar um número. "3,7%" vira 3,7 — fácil. Mas "3,6% ou menos" vira o quê? 3,6? 3,4? 3,0?

**Por que importa.** É literalmente uma multiplicação: cada faixa entra na média pelo seu número. Se a
faixa aberta tem probabilidade alta, o número escolhido move a resposta inteira da view de inflação.

**As opções.**
- **Ponto médio extrapolado** — fingir que a faixa aberta tem a mesma largura da vizinha e pegar o meio dela.
- **Valor fixo escolhido** — cravar um número e justificar.
- **Truncar no limite** — usar o próprio 3,6.

**O que mudou (varredura de 17 meses de CPI, F8).** A grade de faixas **não é fixa** — ela muda ao longo do
histórico: 3 faixas em dez/2024, 4 em jan/2025, 5 no padrão de 2025, 6 em jul/2025 e mar/2026, e **9** a
partir de abr/2026. Em mar/2026 a grade inteira desloca pra cima (começa em "0,3% ou menos" em vez de
"0,0%"), e em jul/2026 os rótulos **invertem o sinal** — passam a falar em inflação **caindo** ("cair 0,7% ou
mais", "ficar em 0,0%"). Ou seja: a regra do balde aberto tem que valer **mês a mês**, não pode ser um número
só cravado uma vez; e o mês de jul/2026 precisa de tratamento próprio, senão entra com o sinal trocado.

**O que a medição mostrou (30/07) — esta é a que morde.** Em 4 dos 19 mercados de faixas, trocar a regra do
balde aberto move a inflação esperada **mais do que ela varia no tempo inteiro**. No pior caso (março/2025) o
deslocamento é o dobro da variação natural do sinal; nos meses de 2026, que têm 9 faixas, é do mesmo tamanho.
Ou seja: **a regra escolhida pesa tanto quanto a informação que o mercado está dando.** Não dá para deixar
implícita.

**Se não decidir.** Mesma coisa da 1.1: o código para com erro.

> ⚠️ **Correção do que esta pauta dizia.** Estava escrito aqui que "1.1 e 1.2 são a mesma decisão e as duas
> mais urgentes". A medição separa as duas: **a 1.2 é a que move a view de inflação; a 1.1 é a que move as
> views de recessão e eleitoral.** Elas travam coisas diferentes e **podem ser decididas em separado** — se a
> reunião só tiver fôlego para uma, a 1.2 destrava a 2.2 sozinha. (No registro formal as duas ainda são a
> "decisão 11"; a separação é do efeito medido, não da numeração.)

---

# 🟠 BLOCO 2 — Define o tamanho do projeto

## 2.1 Quais views entram de verdade na carteira

**O que é.** Além das 4 views já fechadas, existem 4 extras **com código pronto e testado**: trajetória do
Fed (B), geopolítica→energia (C), tarifas (E) e fiscal (G). Estar pronto não é estar dentro — a reunião
decide quais efetivamente vão pro backtest.

**Por que importa.** Cada view a mais é mais um sinal disputando espaço na carteira. Duas views que apostam
na mesma coisa por caminhos diferentes viram, na prática, uma aposta dobrada sem ninguém ter decidido dobrar.

**O risco de cada uma.**
- **B (trajetória do Fed):** ela e a view 2.3 apostam as duas em juros — 2.3 na próxima reunião do Fed, B em
  onde a taxa termina o ano. Risco de exposição dobrada ao mesmo fator. Pergunta extra: B pode reaproveitar
  as sensibilidades já estimadas pela 2.3, ou precisa estimar as suas?
- **C (geopolítica→energia):** mexe em XLE (energia), que outras views também mexem — mesma questão de
  sobreposição.
- **E (tarifas):** a estimativa de sensibilidade dela é reconhecidamente frágil, está documentado.
- **G (fiscal):** já nasceu marcada como reserva — poucos episódios históricos pra estimar em cima.

**Se não decidir.** Não dá pra montar o backtest: a lista de views é literalmente um argumento de entrada da
função que calcula os pesos.

---

## 2.2 A camada tática entra?

**O que é.** Três estratégias curtas que rodam **por cima** da carteira principal, sem substituí-la:
(a) comprar SPY na véspera de anúncio macro, porque dia de anúncio historicamente paga um prêmio;
(b) surfar o movimento que continua por semanas depois de uma decisão do Fed; (c) aproveitar que o
Polymarket funciona no fim de semana e a bolsa não — se a probabilidade andou no sábado, entrar na abertura
de segunda.

**Por que importa.** É uma camada inteira a mais no projeto. Muda o que precisa ser testado, muda o
relatório, e o item (b) em particular obriga o backtest a acompanhar posições dia a dia por semanas seguidas
— bem mais pesado de programar do que o resto.

**Se não decidir.** O código existe, mas fica inerte. Sem prejuízo pro resto.

---

## 2.3 Qual o tamanho de cada aposta tática

**O que é.** Decidido que a camada entra, falta o número: quanto do dinheiro vai em cada tilt. Três botões
sem valor — o teto da compra de SPY em dia de anúncio, o tamanho dos livros de ações e de renda fixa da
estratégia pós-Fed, e o ganho da estratégia de fim de semana.

**Por que importa.** Regra do projeto: parâmetro numérico não se inventa, vem de decisão humana registrada.
Com zero, as táticas não fazem nada; com valor alto demais, elas dominam a carteira e o Black-Litterman
vira decoração.

**Miudezas que vêm junto.** Quantos dias dura cada surfada pós-Fed (15 e 50 são as propostas); se a
expectativa da véspera sai do futuro de juros ou do próprio Polymarket; se surpresa pequena entra com
posição cheia ou proporcional; se a posição de fim de semana desmonta no mesmo dia ou ao longo de vários; e
quem manda quando um tilt tático e um rebalanceamento caem no mesmo dia.

---

## 2.4 Os dois botões do Black-Litterman (τ e δ)

**O que é.** O modelo tem dois parâmetros globais sem valor definido:
- **τ ("tau")** — o quanto a gente admite que a carteira de mercado padrão pode estar errada. É o que decide
  se as nossas views empurram muito ou pouco a carteira pra longe do neutro.
- **δ ("delta")** — aversão a risco. Quanto maior, menor a posição total.

**Por que importa.** São os dois botões que mais mexem no resultado final e nenhum tem valor decidido — os
testes atuais rodam com números sintéticos só pra provar que a matemática fecha.

**Ressalva.** O δ tem um pé fora do meu módulo: ele é dimensionamento de risco, e o módulo de risco (Ω) é da
Lia. **Precisa de alinhamento com ela antes de cravar**, senão os dois mexem no mesmo botão sem saber.

---

# 🟡 BLOCO 3 — Só fecha com o dado do Paulo na mesa

## 3.1 Quantos dias a bolsa demora pra reagir (o "k") ⚠️ ATUALIZADA · MEDIDA — resultado adverso

**O que é.** A tese de várias views é: o Polymarket percebe a notícia primeiro e a bolsa demora alguns dias
pra absorver. Esse atraso é o **k**. Se o k for 3, a gente compara a probabilidade de hoje com a de 3 dias
atrás e aposta que a bolsa ainda vai andar essa diferença.

**Por que importa.** Nas views defasadas, o k **é** a view — não é um detalhe de calibração. Escolher errado
é apostar num atraso que não existe.

**As opções.** (a) rodar a regressão com o dado real, olhar o gráfico de atraso e decidir com ele na mesa;
(b) regra estatística automática, que exige escolher mais um limiar; (c) escolher o k que melhor explica os
dados, com o risco de pegar um k grande por puro ruído.

**O que mudou (F5 e F10).** Duas notícias boas. Primeira: a série do Polymarket **é o preço médio do livro de
ofertas**, não o último negócio fechado (foi medido, não inferido) — então ela não fica parada entre negócios,
e o k que a regressão medir é atraso de verdade, não artefato de preço velho. Segunda: o histórico vem em
passo de **12 horas** — dá dois pontos por dia, o suficiente pra medir atraso em dias. O passo fino (10 min)
existe, mas só nos últimos ~30 dias de mercado vivo, então não serve pro backtest.

**⚠️ A regressão RODOU (30/07) e o resultado é ruim para a tese.** Não era preciso esperar a 1.1: a correção
de viés é uma transformação que preserva a ordem, então ela mexe no tamanho do coeficiente, não no dia em que
a reação aparece — e isso foi checado rodando com e sem correção, com o mesmo resultado.

- **Eleição 2024 (view 2.4):** a reação da bolsa está **no mesmo dia** (SPY, financeiro, tecnologia e títulos
  longos, todos com o sinal esperado do "Trump trade"). Nos dias seguintes não sobra nada além do que se
  esperaria por acaso. **k ≈ 0.**
- **Recessão (view 3.1):** a regressão *parecia* mostrar uma reação no dia seguinte, forte e em todos os 9
  ativos. Mas uma checagem que não estava prevista — perguntar se **a bolsa é que anda antes do Polymarket** —
  mostrou que a associação mais forte está do **outro lado**: o poly se move depois do pregão, não antes.
- **Irã (view C):** só 45 dias de dados. Não dá para concluir nada.

**A ressalva honesta, que vale para os três.** A janela de 12 horas do Polymarket **contém o pregão do dia
anterior**. Então parte dessa inversão é mecânica: os dois estão lendo a mesma notícia dentro da mesma
janela. O que dá para afirmar é mais fraco e mais importante do que "a tese está errada": **com o dado que
existe, não dá para mostrar que o Polymarket antecipa a bolsa.** Para separar de verdade seria preciso passo
intradiário, que o Paulo mediu existir só nos ~30 dias mais recentes de mercado vivo — não serve para
backtest. Para efeito de decisão dá no mesmo: não há como ligar as views defasadas com base nisso.

**Encaminhamento.** A opção (a) da lista acima já foi executada — o gráfico está na mesa
(`Dump/Perfil_defasagem_k.md`). O que a reunião decide agora não é mais "qual critério de k", e sim **o que
fazer com views cuja premissa o dado não sustentou** (ver 3.2 e a nova 7.3).

---

## 3.2 E se o atraso for zero? ⚠️ MEDIDA — deixou de ser hipótese

**O que é.** Pode acontecer de a regressão dizer que a bolsa reage no mesmo dia (k = 0). Nesse caso a view
eleitoral **nunca liga**, por construção — ela não tem o que apostar, porque não sobrou defasagem.

**As opções.** Ou vira uma aposta contemporânea (segue a probabilidade no mesmo dia, sem esperar), ou sai do
v1. Não dá pra decidir antes de ver o número.

**⚠️ O número chegou (30/07): é esse o caso.** No episódio de 2024 a reação está toda no lag 0. Esta decisão
saiu da categoria "se acontecer" e entrou na categoria "precisa ser tomada nesta reunião". Um agravante que
já estava registrado: a view eleitoral tem **um único episódio** (o mercado de 2022 não tem série
recuperável), então não há um segundo caso para desempatar.

---

## 3.3 Prazos que não batem entre poly e curva de juros

**O que é.** A view de recessão compara duas fontes que respondem perguntas diferentes. O Polymarket
pergunta "vai ter recessão **até dezembro**?" — e essa janela vai encolhendo conforme o ano passa. A curva
de juros estima "recessão nos **próximos 12 meses**" — janela sempre do mesmo tamanho, rolando. Em janeiro
as duas quase coincidem; em novembro, uma pergunta sobre 1 mês e a outra sobre 12.

**Por que importa.** A view é a diferença entre as duas. Se as perguntas não são a mesma, a diferença mede
em parte o desalinhamento de prazo, não desacordo de verdade.

**Junto vem:** o que fazer quando o mercado de um ano acaba e começa o do ano seguinte (a "rolagem"). Vale
igual pra view B.

---

# ⚠️ BLOCO 4 — ~~Sem dono definido~~ → 4.1 tem dono desde 30/07

## 4.1 Misturar retornos de prazos diferentes ✅ DONO: FELIPE · proposta pronta

**O que é.** Umas views dizem "esperamos +2% **acumulados em 3 dias**". Outras dizem "+0,1% **por dia**".
Hoje o código empilha as duas na mesma matriz. É somar km/h com km — o número sai, mas não significa nada.

**Por que importa.** Contamina o resultado silenciosamente: não dá erro, não trava, só devolve peso errado.
E precisa estar resolvido **antes** de escrever o loop de rebalanceamento, senão o backtest inteiro nasce
com o vício embutido.

**Precisa de duas coisas:** ~~alguém assumir~~ (**Felipe assumiu em 30/07** — a ponte probabilidade→retorno já
é módulo dele) e a escolha de como converter.

**O que já foi feito (30/07).** Levantamento de em que prazo cada view responde — a de inflação **não tem
prazo definido** (é o repricing total, sem dizer em quantos dias); as de Fed respondem **em 1 dia**; as
defasadas respondem **em k dias**; e a matriz de risco que entra no modelo é **diária**. Ou seja, hoje o
modelo soma quatro prazos diferentes. No código, cada view passou a **declarar** o seu prazo e a integração
**recusa juntar prazos diferentes** — antes ela somava em silêncio. A proposta completa está em
`Dump/Proposta_4.1_horizontes.md`.

**O que sobrou para a reunião:** duas perguntas, e nenhum número foi proposto (regra do projeto).
Viraram os itens **7.1 e 7.2** do bloco novo.

---

## 4.2 O medidor de confiança das views (Ω) — com a Lia

**O que é.** O Black-Litterman precisa saber **o quanto confiar** em cada view. Uma view baseada num mercado
grande, líquido e estável merece mais peso que uma baseada num mercado fininho de dois participantes. O Ω é
esse número de confiança, e é módulo da Lia.

**Por que importa.** Trava a integração final. Uma view ligada sem Ω faz o sistema **falhar na hora** — de
propósito, pra ninguém rodar com confiança inventada.

**Estado.** Foi delegada à Lia na reunião de 08/07 e ela já propôs um protocolo. A reunião confirma o
protocolo ou só acompanha o prazo? Depende do Paulo entregar volume histórico do Polymarket — e a segunda
entrega trouxe **volume total por mercado**, não volume **dia a dia**. Se o Ω da Lia precisa de volume variando
no tempo, esse pedido ainda não foi feito.

---

# 🆕 BLOCO 5 — Nasceram da mensagem do Paulo (ainda não registradas)

## 5.1 A lista "mercado → ETF" dele é o quê?

**O que é.** O Paulo mandou os 30 mercados com uma sugestão de quais ETFs cada um afeta ("CPI → TIP, TLT").
No nosso desenho, **quem decide qual ETF responde a qual evento é a regressão**, não atribuição manual — a
gente olha o histórico e mede.

**Por que importa.** Se a lista dele for entendida como proposta de carteira, atropela a metodologia inteira.
Se for entendida como "quais mercados vale a pena baixar primeiro", é útil. Precisa ficar explícito qual das
duas.

**Recomendação:** heurística de priorização do download, não input do modelo.

---

## 5.2 Os ~20 mercados novos viram views?

**O que é.** O catálogo dele tem muita coisa que a gente não usa: payrolls, VIX, dólar, petróleo, antitruste,
regulação de IA, semicondutores, preço de remédio, quebra de banco, spread de crédito.

**Por que importa.** Nenhum tem view, nem sensibilidade estimada, nem âncora acadêmica. Cada um que entrar
custa uma regressão nova e uma decisão de como virar retorno esperado.

**Recomendação:** fora do v1. O projeto já tem 8 views e uma camada tática esperando decisão.

---

## 5.3 Petróleo como termômetro externo da view C

**O que é.** Esse é o achado útil da mensagem dele. Hoje a view de geopolítica compara o Polymarket **com ele
mesmo alguns dias atrás**, porque não existia nada de fora precificando "os EUA vão atacar o Irã?". Mas se o
Polymarket tem mercado de **preço do petróleo**, e o petróleo tem futuro negociado em bolsa, dá pra comparar
uma coisa com outra coisa — que é bem mais sólido do que comparar com o passado de si mesmo.

**O risco.** Mercado de commodity costuma resolver por "**tocou** o preço em algum momento", não por "**terminou**
no preço". São coisas diferentes, e a nossa receita de calcular média só vale pro segundo caso. Tem que
checar antes de comemorar.

---

## 5.4 Shutdown volta?

**O que é.** Paralisação do governo americano. Tem volume alto no Polymarket (~US$ 25M, pela estimativa
dele), mas a gente tirou de propósito da view fiscal, porque não achamos efeito documentado de shutdown em
bolsa — a bolsa historicamente ignora.

**A decisão.** Reafirmar a exclusão ou reabrir por causa do volume. Volume alto é bom pro dado; não é
argumento de que o evento move preço de ação.

---

## 5.5 O Polymarket não tem "preço de compra e de venda" no histórico ⚠️ ATUALIZADA — deixou de ser escolha

**O que é.** A gente queria, pra cada dia, os dois preços do mercado: o que quem compra oferece e o que quem
vende pede. O Paulo mediu na API (27/07) e **esse dado não existe no histórico**. Existe só **uma** série de
preço, e os preços de compra/venda só aparecem **ao vivo** (e somem quando o mercado é encerrado).

**O que a medição de 29/07 mudou — as duas coisas importantes:**
- **A série única já é o preço médio do livro** (o tal "preço justo"), não o último negócio fechado. Foi medido
  no mesmo instante em dois mercados vivos: a série bate com o preço médio, não com o último negócio. Isso
  **derruba a preocupação da escada de degraus** — o preço não fica velho entre um negócio e outro. A condição
  que as cinco views pediam era, no fundo, "queremos o preço médio"; ela está atendida por outro caminho.
- **A opção (b) morreu.** A lista de negócios individuais existe, mas a API só entrega os **20 mil mais
  recentes** de cada mercado (10 mil por página, duas páginas, e os filtros de data são ignorados). No Trump
  2024 isso cobre **só o dia da eleição**; na recessão, faltam os 4 primeiros meses. Não dá pra reconstruir a
  série da vida inteira do mercado. Detalhe: **não é falta de negócio** — 99,8% das janelas de 12h têm compra
  e venda. É teto da API.

**O que sobra pra decidir.** Não é mais "qual fonte de preço" — é uma só, a série de preço médio, e ela serve.
O que fica em aberto é o **custo de negociar**: sem livro de ofertas histórico, a diferença entre comprar e
vender **não é observável**. Então o desconto de custo do backtest é um número que o grupo arbitra (hoje não
existe nenhum) ou que se assume como zero, declarado no relatório.

**Se não decidir:** o backtest roda com custo zero implícito e o resultado sai melhor do que a realidade.

---

## 5.6 A recessão só existe com o critério "sujo" ⚠️ NOVA

**O que é.** A view 3.1 queria o mercado de recessão que resolve **mecanicamente** (dois trimestres de PIB
negativo, dado do governo). O Paulo mediu: esse mercado **não existe sozinho**. O que existe é um mercado que
resolve por **duas portas** — ou o PIB negativo, **ou** o NBER (um comitê de economistas) declarar recessão.

**Por que importa.** O NBER anuncia com meses de atraso. Isso significa que parte do preço do mercado reflete
"quando o comitê vai se pronunciar", não "a economia está em recessão" — e é justamente esse ruído que a view
3.1 queria evitar.

**A decisão.** Usar o mercado de duas portas assim mesmo (e assumir o ruído), trocar o desenho da view 3.1, ou
tirar a 3.1 do v1.

*(Sem mudança na segunda entrega — continua como estava.)*

---

# 🆕 BLOCO 6 — Nasceram da segunda entrega do Paulo (30/07)

## 6.1 As probabilidades das faixas não somam 100% ⚠️ MEDIDA · a pergunta cresceu

**O que é.** Num mercado de faixas (CPI, número de cortes do Fed), as faixas deveriam somar 100% — ou acontece
uma, ou acontece outra. Medi no dado cru que ele entregou: **não somam**. No CPI de julho/2025 a soma varia
entre 97,8% e 106%; no mercado de cortes do Fed, entre 92,3% e **132,5%**. Cada faixa é negociada num livro
separado, então elas se desencontram.

**Por que importa.** Toda a view de inflação é uma média ponderada por essas probabilidades. Com a soma
errada, a média sai errada — pra mais ou pra menos, dependendo do dia.

**A decisão.** Dividir tudo pela soma (é o que o código já faz hoje) é o caminho óbvio, mas tem uma pergunta
junto: **faixa que morre no meio do caminho conta como quê?** No mercado de cortes do Fed, a faixa "nenhum
corte" para de ter preço em set/2025 (virou impossível) e a de "1 corte" em out/2025. Some da conta ou entra
como zero? As duas escolhas dão médias diferentes, e nenhuma é obviamente certa.

**⚠️ Faltava um caso, e ele é maior que o previsto (medido em 30/07).** Não existe só "faixa que morre":
existe **faixa que some e volta**. Nos meses de grade nova de 2026 os buracos são internos e não coincidem
entre faixas — em **março/2026 só 24 dos 60 momentos têm todas as 6 faixas com preço** (abril/2026: 42 de 63).
Nos meses de 2025, de grade estável, isso não acontece. Como está escrita, a decisão não cobre esse caso — e
ele atinge mais da metade dos momentos de março/2026.

**Quanto isso muda o número (medido).** Nos meses de 2025: **zero**, escolha o que escolher. Em março/2026:
0,13 ponto na inflação esperada. No mercado de cortes do Fed: **0,18 corte**, que é muito. Ou seja: **é
decisão dos meses de grade nova e do mercado de cortes**, não de todos.

**Relação com a 1.1.** Estava escrito aqui que é a mesma família e que deveria fechar junto. **A medição
separa:** a 6.1 quase não interage com a 1.1 — quem convive com ela de perto é a **1.2**, porque as duas
mexem em como a faixa entra na média. Fechar 1.2 e 6.1 na mesma conversa faz mais sentido do que 1.1 e 6.1.

---

## 6.2 De onde vem o futuro de juros do mês (ZQ)

**O que é.** Duas views (2.3 e B) e a tática pós-Fed precisam do contrato de juros **de um mês específico** —
o mês seguinte a cada reunião do Fed. O Paulo testou 8 formas de pedir isso ao yfinance (a fonte grátis que a
gente usa pra tudo): **nenhuma funciona**. Só sai o contrato "contínuo", que é uma colagem de vários meses e
não serve pra medir o que a reunião mudou.

**As opções (nenhuma escolhida — é decisão do grupo).** CME (fonte oficial, parte paga), Nasdaq Data Link
(exige conta e chave), Barchart (parte paga). O FRED não tem o contrato — só a taxa efetiva.

**Se não decidir.** As views 2.3 e B e a tática de drift pós-Fed ficam sem insumo, mesmo com o código pronto.

---

## 6.3 O calendário de datas do CPI só começa em 2025

**O que é.** Pra saber quando cada número de inflação foi divulgado, o Paulo tentou o site do órgão americano
(BLS) e **levou bloqueio de robô**. O plano B funcionou: as datas estão escritas nas regras dos próprios
mercados do Polymarket. Só que aí o calendário só existe **onde existe mercado** — ou seja, de jan/2025 pra
frente. O calendário do Fed, esse sim, está completo desde 2022.

**Por que importa.** Define até onde o backtest das táticas pode voltar no tempo. Com CPI só de 2025, a
tática de "prêmio de véspera de anúncio" perde os anos de 2022 a 2024.

**A decisão.** Aceitar backtest curto (2025 em diante), ou alguém buscar as datas antigas em outra fonte.

**Três buracos medidos, pra ninguém tropeçar depois:** abr/2025, jan/2026 e fev/2026 não têm mercado mensal de
CPI. E uma linha do calendário veio com **erro de digitação da própria fonte** — o CPI de dez/2025 aparece com
divulgação em "13/01/**2025**" quando o certo é 2026 (confirmei pela data em que a série do mercado termina).
O Paulo deixou cru e sinalizou, que é o certo; a correção é do meu lado, no tratamento.

---

## 6.4 O teste de 2022 da view eleitoral acabou

**O que é.** A ideia era testar a view eleitoral também na eleição de meio de mandato de 2022, pra não depender
só de 2024. O mercado de 2022 existe e teve US$ 1,77M negociados, mas **não tem histórico recuperável**: a série
volta vazia e a lista de negócios volta zerada. Morreu pelas duas portas.

**A consequência.** A view eleitoral fica com **um único episódio** (2024) pra sustentar a estimativa. Não é
decisão a tomar — é uma limitação a declarar no relatório, e um argumento a mais na hora de decidir quanto peso
essa view merece.

---

# 🆕 BLOCO 7 — Nasceram da sessão de código de 30/07 (dado rodando)

## 7.1 Qual é o prazo da carteira (o "H")

**O que é.** De quanto em quanto tempo a carteira é recalculada: todo dia, toda semana, todo mês. Não é
pergunta nova — o backtest precisa disso de qualquer jeito — mas descobrimos que ela decide **outra coisa**
junto: é o prazo para o qual todas as views e a matriz de risco têm que ser convertidas (decisão 4.1).

**Por que importa.** Uma view que promete "+2% em 3 dias" não entrega isso numa carteira que é recalculada
todo dia. Com H definido, a conversão de cada view vira conta mecânica; sem ele, não existe conversão possível.

## 7.2 Em quantos dias o mercado de títulos fecha o gap da view de inflação

**O que é.** A view 2.2 diz "o Polymarket está vendo mais inflação do que os títulos estão pagando, logo há um
repricing de X% a acontecer". Ela **não diz em quanto tempo**. As outras views todas dizem.

**Por que importa.** Sem um prazo, o número dela é o repricing inteiro, o que a faz **gritar mais alto que
todas as outras** quando entram na mesma carteira — não porque o sinal é melhor, mas porque está medido numa
régua maior.

**Quem decide.** É premissa de convergência, não parâmetro de código: vem da reunião.

## 7.3 As views defasadas sobrevivem? ⚠️ a mais dura

**O que é.** Quatro das oito views (2.4 eleitoral, 3.1 recessão, C geopolítica, E tarifas — e G, que já era
reserva) se apoiam na mesma tese: **o Polymarket anda primeiro e a bolsa demora k dias**. O perfil medido em
30/07 não sustenta essa tese em nenhum dos mercados que dava para testar (ver 3.1 e 3.2).

**Por que é uma decisão, e não um resultado.** O dado disponível é de 12 em 12 horas, e essa janela se
sobrepõe ao pregão — então o teste não é conclusivo *contra* a tese; ele é **inconclusivo a favor**. As
opções são: (a) tirar as views defasadas do v1 e concentrar nas de evento (2.3, B) e na de inflação (2.2);
(b) mantê-las como contemporâneas, assumindo que é co-movimento e não previsão — o que muda a natureza da
aposta e precisa estar escrito no relatório; (c) mantê-las como estão e declarar a fragilidade.

**Ligação com a 2.1** ("quais views entram"): esta decisão praticamente responde aquela. Faz sentido tratar as
duas na mesma conversa.

## 7.4 A view de inflação compara 1 mês com 10 anos

**O que é.** Descobrimos ao ligar o dado real na view: os mercados de CPI do Polymarket são sobre a inflação
**de um mês**, e o benchmark de títulos que a view usa é a inflação média esperada para **dez anos**.

**O que já foi corrigido (não precisa de reunião).** A parte de **unidade** — estava comparando 0,3% ao mês
com 2,3% ao ano, o que deixava a view apostando na direção errada o tempo todo, por aritmética. O código
agora anualiza antes de comparar, e não roda sem que se declare qual é a unidade do mercado.

**O que sobra para a reunião.** O descasamento de **prazo**, que a correção de unidade não resolve: um mês
anualizado é um número **nervoso** (um errinho de 0,1 ponto no mês vira 1,2 ponto no ano), e ele está sendo
comparado com a média de uma década. É a mesma família da decisão 3.3. Amortecer isso — suavizar, escalar,
usar um breakeven de prazo mais curto — é decisão do grupo.

---

# Resumo em uma tela

| # | Decisão | Trava o quê |
|---|---|---|
| **1.2** | **Valor do balde aberto** — a que mais move o número na view de inflação (chega a valer mais que o próprio sinal) | **View 2.2.** Fechar junto com a 6.1 |
| **1.1** | **Correção do viés** — quase irrelevante na inflação, decisiva em recessão/eleitoral (mediana 20,5% → 15,5%) | **Views 3.1 e 2.4.** Pode ser decidida separada da 1.2 |
| 2.1 | Quais das 4 views extras entram | Montagem do backtest — **ver 7.3, que praticamente responde esta** |
| 2.2 | Camada tática entra? | Escopo do projeto |
| 2.3 | Tamanho das apostas táticas | Táticas ficam inertes |
| 2.4 | τ e δ | Resultado final (alinhar δ com a Lia) |
| ~~3.1~~ | ~~Critério do atraso k~~ → **medido: k ≈ 0 na eleitoral; na recessão o dado não sustenta a tese** | Virou a 7.3 |
| **3.2** | **Fallback com k = 0** — deixou de ser hipótese, é o caso real | **View eleitoral — decidir nesta reunião** |
| 3.3 | Prazo da view de recessão | Views 3.1 e B (fecha com dado) |
| 4.1 | Mistura de horizontes | Backtest inteiro — ✅ **dono: Felipe**; proposta pronta, faltam 7.1 e 7.2 |
| 4.2 | Ω (confiança das views) | Integração final — Lia |
| 5.1–5.4 | Itens novos do catálogo do Paulo | Escopo — ainda não registradas |
| ~~5.5~~ | ~~Série única ou reconstruir~~ → **resolvido pela medição:** a série já é o preço médio e não há alternativa. Sobra **quanto descontar de custo** | Backtest sai otimista se ficar em zero sem declarar |
| **5.6** | **Recessão só existe com critério NBER embutido** | **View 3.1 — desenho** |
| **6.1** | **Faixas não somam 100% + faixa que morre + (novo) faixa que some e volta** | **Views 2.2 e 2.3.** Zero em 2025, material só em 2026 e no mercado de cortes. **Fechar junto com a 1.2**, não com a 1.1 |
| **6.2** | **Fonte do futuro de juros mensal (ZQ)** | **Views 2.3 e B + tática pós-Fed — sem insumo** |
| **6.3** | **Calendário de CPI só de 2025 em diante** | **Até onde o backtest tático pode voltar** |
| 6.4 | Teste de 2022 da view eleitoral morreu | Nada trava — limitação a declarar (agrava a 3.2: episódio único) |
| **7.1** | **Qual é o prazo da carteira (H)** | **Backtest + a conversão de horizonte da 4.1** |
| **7.2** | **Em quantos dias o breakeven fecha o gap da 2.2** | **View 2.2 não entra em carteira multi-view sem isso** |
| **7.3** | **As views defasadas sobrevivem?** (2.4, 3.1, C, E) | **Metade das views. A mais dura da reunião** |
| **7.4** | **Prazo da 2.2: 1 mês anualizado vs 10 anos** (a unidade já foi corrigida no código) | **Magnitude da view 2.2 — mesma família da 3.3** |
