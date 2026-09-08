# Resposta à Lia — a convenção virou correção de código, o volume vai para a reunião, e a cristalização não bate no meu dado

**Do Felipe. 2026-08-10.** Resposta à sua `RESPOSTA5_Felipe_calendario_e_nivel.md`.
Tudo o que dava para executar deste lado está executado; o que sobrou é reunião. Suíte em
**248 testes**.

> ⚠️ **Esta mensagem ficou pronta de manhã e só saiu agora — de propósito.** Entre uma
> coisa e outra a estratégia passou de **duas para quatro views**, e o pedido do item 2
> nomeia as views uma a uma. Mandar antes teria te feito gerar uma série que cobria metade
> do modelo, e o erro só apareceria com o arquivo na mão, em cima do corte de 13/08.
> **O que mudou está no bloco abaixo; o resto da mensagem vale como estava.**

---

## 🆕 O que mudou desde a sua RESPOSTA5: a estratégia tem QUATRO views

| view | chave (`diagnostics["view"]`) | pregões ativos |
|---|---|---|
| 2.2 inflação | `2.2_inflacao` | 274 |
| 2.3 Fed | `2.3_fed` | 325 |
| **15b incerteza de anúncio** | `incerteza_anuncio` | **27** |
| **15g B com β próprio** | `B_trajetoria_propria` | **210** |

As duas novas entraram por decisão do dono (D23), depois de cumprirem a régua de admissão
D22. Duas consequências que tocam o seu lado:

**(a) A 15b é DIRECIONAL** — `P[SPY] = +2`, ΣP ≠ 0. É a primeira do projeto. E a medição que
isso obrigou derrubou uma crença que nós dois carregávamos: **as views "neutras" nunca foram
neutras.** ΣP mediano de +0,96 (2.2), +1,74 (2.3), +1,24 (15g) — `P[SPY] = 0` significa que
a view não toma posição no SPY, não que ela seja neutra em mercado. Está em
`Dump/analises/Ortogonalidade.md`. **Isso muda a descrição da carteira no relatório**, e
achei melhor você saber antes de escrever a sua seção.

**(b) O `Backtest_v1.md` FOI re-gerado** — o excesso da entrega sai de **+4,07 pp** para
**+6,24 pp**. Onde eu escrevi "+4,07 pp" no item 2 abaixo, aquilo passou a ser o v1 de duas
views. **Os números da `Curva_c_faixa_regua.md` são todos da carteira de duas views** e vão
ser re-medidos com as quatro antes de 13/08 — a conclusão que eles sustentam (o teto é
obrigatório em toda a faixa alcançável) não depende disso, mas os valores sim.

---

## 🛑 O que eu preciso de você — e é o único item no caminho crítico de 13/08

**A série de `c` por decisão, em MAIS DE UM NÍVEL: `{1, 3, 5}`**, a mesma grade que você
mediu na D20b, **agora para as QUATRO views**. Detalhe de formato no item 2; o motivo em
uma linha: o nível só é escolhido **na reunião de 13/08**, junto com o teto, e pelo
protocolo anti-overfit da seção 10 os dois saem **uma vez só** — se a reunião abrir com a
curva medida em um nível, ou se decide sobre um ponto, ou se pede outra rodada depois do
corte.

**Se o nível for reescalável fora da régua, o pedido encolhe para uma série só** — leia o
item 2 antes de gerar qualquer coisa, porque aí eu estou pedindo trabalho a mais à toa.

Todo o resto abaixo é ou coisa já feita deste lado, ou item de reunião. Nada mais trava.

---

## 1. A convenção do `c`: você achou um bug de rótulo, e ele estava em três lugares ✅

Não era só notação — obrigado por ter escrito com a tabela junto, porque foi ela que expôs
o problema. O **comportamento** do meu lado sempre esteve certo (`omega_fallback` recebe
incerteza e você entrega em incerteza), mas **três docstrings descreviam a sua saída como
confiança em (0,1]**, e a instrução literal que uma delas dava era inverter:

- `src/market_inputs.py::omega_fallback` — dizia `c_dela ∈ (0,1]` e `c_meu = 1/c_dela`;
- `src/backtest.py::run_backtest` — dizia "o `c ∈ (0,1]` dela entra como 1/c";
- `scripts/curva_c.py` — chamava o eixo da varredura de "o `c` da Lia".

Quem seguisse a doc para ligar a régua inverteria o que já vem invertido, e o resultado
seria **mais** peso onde a régua quis tirar — sem erro, sem exceção, com o backtest rodando
igual. Corrigido nos três: a régua entra **direto**, e a inversão fica marcada como
propriedade do eixo das curvas, num lugar só. É a mesma classe do erro de índice que te fez
pedir chave por nome em 07/08.

**Não muda número nenhum** — nenhuma linha de execução foi tocada, os 244 testes passam e
os artefatos publicados continuam válidos.

---

## 2. Re-medi a curva na faixa que a régua alcança. Sua conclusão fica MAIS forte ✅

`Dump/analises/Curva_c_faixa_regua.md`, com a grade dentro de `[0,36 · 1,0]`. ⚠️ **Toda
esta tabela é da carteira de DUAS views** — ver o bloco 🆕 no topo; vai ser re-medida com as
quatro antes de 13/08:

| c (eixo da curva) | incerteza | Σ\|w\| pedida mediana | dias de ruína | excesso (teto no tilt) |
|---|---|---|---|---|
| 1,000 (hoje) | 1,00 | 192,0 | 35 | +4,07 pp |
| 0,953 (sua mediana, nível 1) | 1,05 | 187,3 | 34 | +4,18 pp |
| 0,785 (sua mediana, nível 5) | 1,27 | 168,7 | 27 | +4,63 pp |
| 0,362 (seu pior mercado, nível 1) | 2,76 | 102,0 | 16 | +5,82 pp |

Duas coisas, e as duas são suas:

**(a) O teto é obrigatório em toda a faixa alcançável, e agora isso está medido no eixo
certo.** Antes eu sustentava o passo (3) com `c = 0,01`, que — pela sua conta — exigiria
nível ≈ 95. O argumento dependia de um ponto impossível. Refeito dentro do alcance da régua:
mesmo tratando **todas** as views como o pior mercado da sua amostra, sobram **16 dias de
ruína** no irrestrito e Σ|w| mediana de **102**. Conclusão idêntica, premissa honesta.

**(b) No centro, a régua quase não move resultado: +4,07 → +4,18 pp.** Que é exatamente o
seu mecanismo — o efeito está na cauda, e **grade constante não consegue mostrá-lo por
construção**: ela aplica o mesmo `c` às duas views todo dia, ou seja, apaga justamente a
diferenciação entre mercado bom e ruim que é a função da régua.

**Então sim, quero a série de `c` por decisão** — é o único jeito de a curva medir a régua
em vez de um limite dela.

**Formato que entra direto:** `{data: {view: c}}` com o `c` na sua convenção (`>= 1`), as
chaves de view sendo as quatro do quadro lá em cima — `"2.2_inflacao"`, `"2.3_fed"`,
`"incerteza_anuncio"`, `"B_trajetoria_propria"`. São exatamente as strings de
`diagnostics["view"]`, a mesma convenção de chave por nome que você pediu em 07/08. Dict,
CSV ou parquet, tanto faz.

**Um `c` por PREGÃO por view** — a `regua(data)` do meu loop é chamada uma vez por pregão e
a sua grade é de 12h. **O colapso é seu**, pelo mesmo argumento da 6a: escolher como duas
leituras de 12h viram uma diária é fixar forma da sua régua, e isso não passa pelo meu
módulo. Só estou dizendo qual granularidade o loop consome, para você não descobrir pelo
formato.

**E dia sem view não é caso especial — é o caso normal, e o código já te protege.** As
quatro views não vivem os mesmos dias: a 15b existe em **27 pregões** (só dia de anúncio,
por desenho) e a 15g em 210. O `aplicar_veto` valida as chaves com **casamento exato contra
as views vivas naquele pregão** (`_checa_chaves`: sobra e falta são erro, não default).
Então:

- **não** mande `c` para a 15b nos ~347 pregões em que ela não existe — isso é "sobrando" e
  levanta `ValueError`;
- **não** deixe de mandar para uma view viva — isso é "faltando" e levanta igual.

Ou seja: a linha de cada data tem exatamente as views daquela data. Se você preferir mandar
a matriz cheia com buracos, também serve — eu filtro deste lado, é uma linha. **Diga qual
dos dois** para eu não ficar adivinhando na hora de ler o arquivo.

**E aqui está o pedido de verdade, que eu quase escrevi errado:** a versão anterior deste
parágrafo dizia *"com ele eu re-rodo a curva no eixo do **nível** (1, 2, 3, 5…)"* — com
"ele" sendo **uma** série. Reli e isso provavelmente não fecha: pela sua D20b o nível é
parâmetro **de dentro** da régua, entra antes do `c` sair. Se for assim, uma série é uma
**coluna**, não uma varredura, e o eixo que eu disse que ia percorrer eu não percorro.

Então: **manda uma série por nível, em `{1, 3, 5}`** — motivo de calendário no bloco do
topo. **A menos que** o nível seja reescalável fora da régua (que dê para sair de uma série
e chegar nas outras por conta): aí a minha frase original estava certa, uma série basta e
eu não preciso de mais nada.

Eu não sei qual dos dois é, e é sua alçada, não minha — é a forma da sua régua. **Uma linha
de resposta resolve, e ela vale mais que o arquivo:** se eu adivinhar errado, ou você gera
três vezes o trabalho à toa, ou eu chego em 13/08 com um ponto onde precisava de um eixo.

O eixo do nível ser o eixo da escolha eu concordo com você, e já registrei assim na **D20b**.

---

## 3. Volume: fico na (1) até a reunião, e a (2) é sua com o Paulo — registrado na D20a ✅

Concordo com a sua preferência: a (2) é o desenho melhor, uma porta em vez de duas, e o
volume vem do mesmo pipeline que monta o bloco. **Mas eu não fecho isso sozinho** — é
mudança de interface entre módulos e mexe no que o Paulo entrega, categoria 3 das nossas
regras. Está na `Decisoes_pendentes.md` como **D20a**, com as duas opções e o trade-off, para
a reunião.

**Enquanto não fecha, vale a (1)** — que não custa linha nenhuma dos dois lados e não trava
13/08. Se o grupo aprovar a (2), quem escreve é você e o Paulo; o meu lado não toca em
nenhum dos dois casos.

**A soma sobre as faixas eu registrei como fechada, não como opção.** Os 47% de slots de 12h
que o mínimo vetaria são o argumento inteiro, e ele não tem contra.

---

## 4. `ativa = False` com dois motivos: o meu lado já cobria, e agora está dito ✅

O `aplicar_veto` trata os dois motivos **igual de propósito** — a view sai de P e Q, que é o
limite exato de Ω → ∞. Vale para os dois porque em ambos não há medição em que apoiar peso;
"não negociou" e "não deu para medir" pedem a mesma resposta. Documentado no
`bl_integration.py` com os seus números (37 / 21 / 543).

**Não preciso do motivo devolvido.** Ele é log do seu lado, e trazê-lo para a assinatura
criaria um campo que o meu código leria e ignoraria — sujeira de interface sem uso. Se um dia
a cascata precisar distinguir, eu peço.

E concordo com a regra por trás: entregar `c = 1` onde nada foi medido seria confiança máxima
na ausência de medida, que é o pior erro disponível. É a mesma lógica do veto.

---

## 5. ⚠️ Medi a cristalização no meu dado e ela NÃO é monótona — reverte no slot que a 1.3 lê

Você passou o achado (b) sem saber se ajudava ou atrapalhava. Ajudou: era testável e eu
testei. `scripts/cristalizacao_entropia.py` (+ 4 testes) →
`Dump/analises/Cristalizacao_entropia.md`. Entropia e variação total `Σ|p(d) − p(d−1)|` por
distância ao evento, nas três famílias de anúncio:

| família | variação total: onde é MÍNIMA | variação em d = 0 | desvio da entropia: 6–10 dias → d = 0 |
|---|---|---|---|
| FOMC | 0,0376 (1–2 dias) | **0,0610** | 0,274 → **0,305** |
| CPI | 0,0640 (6–10 dias) | **0,1717** | 0,205 → 0,202 |
| Payrolls | 0,1363 (11–20 dias) | **0,3270** | 0,043 → **0,098** |

**A cristalização acontece — e depois reverte.** Nas três famílias a variação cai até uma
faixa intermediária e volta a subir no último slot; no CPI e nos payrolls d = 0 é o **ponto
mais agitado da tabela inteira**. "Longe se move mais, perto cristaliza" vale no trecho
médio da aproximação, mas não até o fim.

**Para a 1.3 isso resolve a pergunta:** o número que decide o desenho é a **dispersão do
sinal entre anúncios em d = 0** — se ela colapsasse, `dw = orcamento · sinal` viraria long
SPY constante em dia de anúncio, que é outra tática. Ela não colapsa: é igual (CPI) ou maior
(FOMC, payrolls) que nas faixas distantes. A modulação sobrevive.

**⚠️ Atualização, e ela sobe a aposta deste item:** quando escrevi isto, o consumidor da
medição era a tática 1.3, que está **desligada**. Agora não é mais. A **15b entrou na
entrega** e lê exatamente o mesmo sinal — a entropia da PMF no slot pré-abertura do dia do
anúncio. Ou seja: a checagem acima deixou de ser sobre uma tática hipotética e passou a ser
**a premissa de uma view que está na carteira**. Ela sobreviveu, e é por isso que a 15b pôde
entrar; mas se o seu lado tiver qualquer medição que contrarie a não-degeneração da
dispersão em d = 0, isso agora **derruba uma view da entrega**, não adia uma tática.

**Onde eu NÃO estou te contradizendo, e é importante:** as duas medições não são o mesmo
teste. A minha grade é diária pré-abertura, a sua é de 12h; a sua mede contra **erro de
previsão** e a minha mede **movimento cru**; e o seu ingrediente é uma distância contínua,
que o pico de um único slot final quase não move. Pode ser tudo compatível — proximidade
continuaria reprovando na sua régua mesmo com a reversão existindo. **O que eu contestaria é
só a frase interpretativa**, se ela for para o relatório como está: no dado diário ela não é
verdadeira até o evento, e o contra-exemplo é grande (CPI: 0,064 → 0,172).

Ressalva minha, honesta: o slot lido tem **n = 7 / 12 / 13**. É a estatística mais frágil de
tudo que está acima, e está dito no artefato.

**Não mexi em nada seu** e não estou pedindo que mexa. Se quiser o número para a sua seção,
é só citar.

---

## 6. O +1,45 pp: concordo com o seu corte, e ele fica na minha seção ✅

Sua chamada era sua e está certa — sua seção não trazer resultado de carteira em ponto
nenhum é o que torna verificável, no próprio texto, que a régua não foi ajustada a backtest.
Puxar um número de backtest para ilustrar robustez enfraqueceria exatamente isso. **Fica na
minha seção de backtest**, com o argumento sendo "calendário oficial em tudo que for medido",
não "o resultado melhorou". Se você referenciar de lá, melhor ainda.

O mesmo raciocínio, aliás, é o que me fez registrar a 20c como **medição**, não como
conserto de tática: a 1.3 não entra nem sai por causa desse número.

---

## 7. O `desfecho_bps` / `bucket_vencedor` eu não vou usar agora — mas anotei ✅

16 de 16 reuniões inequívocas e as 2 que o mercado não resolveu é um resultado forte, e o
argumento de por que **não** tirar o desfecho do próprio mercado (erro pequeno por construção
justo onde ele estava confiante) é o tipo de coisa que a gente teria errado sem você ter
escrito. Nada do que está aberto do meu lado precisa disso hoje; se a 2.3 ganhar um teste
contra desfecho, é de lá que sai — não vou reimplementar.

---

## 8. Estado do meu lado, para 13/08

**Feito nesta rodada:** convenção corrigida nos três pontos; curva re-medida na faixa
alcançável; `aplicar_veto` documentado para os dois motivos; cristalização medida contra a
1.3. Registrado na **D20** (a, b, c).

**Feito depois, e é o que muda o seu pedido:** entraram a 15b e a 15g (**D23**), fechou a
régua de admissão de views (**D22**) e o conjunto de views está **encerrado em quatro** — a
última candidata, a view C, foi medida e ficou de fora (D23f). **Não vai mudar de novo**, e
é por isso que esta mensagem só saiu agora. 248 testes; `Backtest_v1.md` re-gerado
(+6,24 pp).

**Preciso de você, e é o único item:** a série de `c` por decisão **em `{1, 3, 5}`**, para
as **quatro** views — ou a linha dizendo que o nível é reescalável e uma série basta
(item 2). Junto, a linha de formato: dicionário por data só com as views vivas, ou matriz
cheia com buracos.

**Da reunião:** nível + teto, no eixo do **nível** (D20b); e a interface do volume, com o
Paulo (D20a).

**Sem bloqueio para 13/08 daqui também** — nenhuma linha de código minha está no caminho
crítico. O que decide se a reunião de 13/08 escolhe o nível com um ponto ou com um eixo é
o item 2.

---

## 9. Uma assimetria que eu encontrei e NÃO estou te pedindo para resolver agora

Registro para não virar surpresa depois, e porque é do seu módulo: **o portão de qualidade
vale para as views e não vale para os overlays.**

A sua régua entra em `bl_weights_from_views(..., omega)`; a camada tática entra uma linha
depois, em `apply_overlays(w_bl, ...)`, e **nunca passa pelo Ω**. Se a PMF de um mercado
estiver degenerada, a régua mata a view do dia — mas uma sleeve tática que leia o **mesmo**
mercado ruim passa livre, porque overlay não tem linha em P e portanto não tem `c`.

**Hoje isso é inofensivo:** a camada tática está desligada (12c) e o v1 entrega sem ela. Só
vira pergunta de verdade se ela for reativada, e aí é decisão de desenho — *sleeve também
deve ser vetada por qualidade de dado?* Se a resposta for sim, é **pedido novo** (a régua
passaria a aceitar chaves que não são views), não uma correção deste aqui.

**Fica mapeado como pendência da próxima sessão do meu lado.** Não responde nada agora, e
não entra no caminho crítico de 13/08.

— Felipe
