# LOG de sessões

## 2026-08-07 (sessão 8) — Felipe

**Contexto da sessão:** o dono enviou o `RESPOSTA3` e o `FOLLOWUP5` da sessão 7
e pediu o mapa do que dá para fazer, decidir e do que está travado. No meio da
sessão entrou o fato que reordenou tudo: **a entrega é 17/08 e o v1 vira a
entrega final** — "decidir depois" deixou de existir. Ordem executada: decidir o
decidível → executar.

**1. `data/` destravado (o bloqueio que valia por todos).** Não existe `data/` no
branch `Felipe`; os parquets e CSVs do FRED estão no `Paulo`. Resolvido sem merge
e sem sujar o branch: `git archive origin/Paulo data | tar -x` + `data/` no
`.git/info/exclude` (local, não é o `.gitignore` compartilhado). Baseline
reproduziu o número da sessão 6 (+2,68 pp no tilt ≤ 1) antes de qualquer
mudança — a régua de que o ambiente estava certo.

**2. Três decisões fechadas pelo dono, registradas como 12a/12b/12c.**

- **12a — semeadura da média expansiva da 2.3.** A lista que demeana a surpresa
  nascia vazia no primeiro pregão (dia 1 demeanava por 0,0). Agora entra
  pré-preenchida com os **206 pregões anteriores** à janela
  (`MontadorV1.semear_2_3`). Medido: sinal líquido de **22%/78% → 34%/66%**;
  excesso no tilt ≤ 1 de +2,68 → **+2,62 pp**, e no tilt ≤ 3 de +10,56 →
  **+13,70 pp**. **Melhora e não conserta** — o resíduo é regime, não artefato
  do zero. A 2.2 não tem semente porque não há pregão anterior à primeira PMF
  de CPI.
- **12b — piso de eventos de FOMC para o β: sem piso adicional.** Na janela o β
  nunca foi estimado com menos de 25 eventos, então qualquer piso abaixo disso
  não desativa pregão nenhum. Cravar 10 ou 20 seria threshold sem medição
  (regra 6). O critério de quando decidir (curva de estabilidade do β) fica
  registrado no lugar do número.
- **12c — camada tática fora do v1.** Varrida antes de decidir
  (`scripts/curva_orcamento.py`, novo): só prêmio −0,34 a −0,03 pp; só drift
  +0,08 a +0,80 pp; os dois +0,05 a +0,45 pp. O que decidiu: o Δ é **monótono no
  orçamento** — a grade não tem ótimo interior, a melhor linha é sempre a ponta
  onde parei de varrer. Tabela assim não seleciona orçamento; escolher por ela
  seria o overfit da seção 10, agora sem rodada seguinte para desmentir.

**3. Bug latente encontrado ao entregar a robustez γ — o pior tipo.** As views
2.2 e 2.3 passavam a `favorite_longshot` **binária** como correção da **PMF**.
Em γ = 1,0 (o v1) as duas são a identidade, então **nunca deu diferença**. Em
γ ≠ 1 a binária devolve `p^γ/(p^γ+(1−p)^γ)` faixa a faixa, o vetor deixa de somar
1 e o `E_poly` sai escalado **sem erro nenhum** — ou seja, o defeito só apareceria
dentro da própria coluna de robustez que a seção 9 prometeu, e como número, não
como falha. Consertado nos dois caminhos (`fl_correction=None` = a correção do
caminho da cascata) e, sobretudo, **na raiz**: `pmf_mean` agora exige que a
correção devolva PMF somando 1, com a mensagem dizendo qual usar. Isso cobre
também a view B e a tática do prêmio, que têm o mesmo default e não foram
tocadas.

**4. Robustez γ entregue, dentro do `Backtest_v1.md`.** γ ∈ {1,0; 1,1; 1,25} no
escopo de referência, com a **semente recalculada em cada γ** (`set_gamma`) — a
surpresa depende de γ, e manter a semente de γ = 1,0 numa rodada de 1,25
demeanaria por uma média que aquele γ nunca produziria, sem dar erro. Resultado:
**+2,62 / +2,88 / +4,02 pp** — o sinal não depende do γ nesta janela.

**5. `Curva_c.md` remedida com as duas views, e a conclusão antiga caiu.** A
varredura anterior rodou só com a 2.2 e concluía "o `c` não muda o resultado, o
teto morde antes". Com a 2.3 ligada o excesso se move até **5,01 pp** ao longo da
grade e **troca de sinal** no escopo de tilt (+2,62 pp em `c = 1`, máximo de
+4,57 pp em `c = 0,25`, −0,44 pp em `c = 0,01`). O texto do script era prosa fixa
afirmando o que a tabela mostrava antes; virou frase **calculada da própria
tabela**. Registrado na seção 10 como medição.

**6. Chegou o `RESPOSTA4` da Lia — e a conferência derrubou um número meu.** Ela
aceita/decide cinco itens (sem `ffill`, buraco descarta o slot, grade de tempo
vira dimensão da calibração, dispensa o `serie_janela_tratada`, não consome o
`dp_variacao_janela`) e escolhe **calibrar sobre a história completa (801 dias)**
— apoiada num número que eu tinha lhe dado. Fui medir para lhe mandar a receita
dos 801 dias e o número não sobreviveu:

| | eu havia dito | medido |
|---|---|---|
| dias degenerados (cru, sem carry) | 27 | **25** (27 = dias com faixa faltando) |
| desses, com soma < 0,5 | 24 | 24 ✔ |
| onde caem | "fora da janela do v1" | **dentro** (30/10/2025 a 21/04/2026) |
| após `carry_missing` (o que a view lê) | — | **0 de 801** (0,953 a 1,143) |

E o achado que muda o plano dela: os 25 são **100% linhas incompletas** (mediana
de 3 faixas ausentes de 4) — nenhum livro completo soma abaixo de 0,9. A soma
baixa mede **buraco**, não desencontro entre books, e buraco ela já penaliza no
canal `n_slots_esperados − n_pontos`. Escrito em
`Dump/trocas/RESPOSTA4_Lia_correcao_801_dias.md` com a receita dos 801 dias
(1 linha/dia, mercado da próxima reunião, pré-abertura, sem carry — ler o parquet
direto dá 3.905, 1.952 ou 804, nunca 801). Correção também na seção 12, e a 6a
ganhou a delimitação que ela pediu (fechou o LUGAR; a forma segue aberta, agora
com 4 candidatas = 2 colapsos × 2 grades).

**Quebrou / aprendido:**
- **Número dito de cabeça vira premissa do outro em uma rodada.** O "27 de 801,
  todos fora da janela" saiu num recado, sem artefato que o reproduzisse — e
  voltou como justificativa de método dela ("os seus 27 dias são o ativo"). Duas
  sessões depois ele estava errado em duas das três partes. Medição que vai para
  fora precisa de script, não de memória.
- **Prosa gerada por script também apodrece — e mente com números certos ao
  lado.** O `curva_c.py` imprimia "o `c` não muda o resultado" acima de uma
  tabela que agora mostra troca de sinal. Número gerado, conclusão escrita à mão:
  a conclusão é que envelhece.
- **O bug que só aparece na coluna de robustez é o pior de achar.** Ficou
  invisível por decisão (γ = 1,0 é identidade) e só sairia no relatório final,
  como número plausível.
- **Semente e parâmetro andam juntos.** Semear é estado derivado do γ; trocar um
  sem refazer o outro é inconsistência silenciosa. Por isso `set_gamma` re-semeia
  em vez de só atribuir.
- **Com o v1 virando entrega, "adiar" mudou de significado.** 12b e 12c não são
  adiamentos disfarçados: são fechamentos com o motivo medido, e o que sobra vai
  ao relatório como limitação, não como pendência.

**Pendente:**

*Resolvido no fim da sessão:*
- **Registro da decisão 8 reposto**, por instrução do dono. Esteve 🔴 vazio de
  09/07 a 07/08: a limpeza da seção duplicada (sessão 3) removeu a cópia COM o
  texto e manteve a vazia. Reposto da ata de 07/07 (Σ amostral + irrestrito),
  que bate com o código desde então. Marcado no arquivo como reposição, não como
  decisão nova; as alternativas B2/B3/B4 citadas pela ata sumiram na mesma
  limpeza e ficam para a reunião confirmar se fazem falta.

*Envio (do dono):*
- `Dump/trocas/RESPOSTA4_Lia_correcao_801_dias.md` — correção medida, receita
  dos 801 dias e o aviso de prazo (ela não sabia que existe data de corte).

*Depende de terceiros (caminho crítico da entrega):*
- `G5 do Paulo` → `régua do c da Lia` → `nível e escopo do teto (grupo)`. Três
  elos, dois fora daqui. O `RESPOSTA4` dela **não** entrega o `c`: sobram quatro
  itens do lado dela, e o portão de volume segue preso na D12 do Paulo.
  **Falta fixar data de corte e plano B pré-registrado** (proposta de 13/08 no
  recado, não fechada): se a régua não chegar, entrega com `c = 1` e teto no
  tilt, nível escolhido pela regra e não pelo resultado.
- **D9 do branch `Paulo`** (overlap dos mercados de FOMC) — segue sem recado.

*Trabalho meu, para a entrega:*
- **Reprodutibilidade:** hoje nenhum branch roda sozinho (o código está aqui, o
  dado no `Paulo`). A entrega exige merge dos três — que eu não faço.
- Banda de não-negociação (introduz threshold novo; se entrar, entra medida).

**Uso de IA:**
- **Modelo:** Claude Code / Opus 5.
- **Contexto consumido:** ~85k tokens (estimativa da sessão).
- **Prompt inicial (verbatim):** "enviei os arquivos que montamos na ultima
  sessão. Agora me fale Tudo que podemos fazer ou decidir agora e também me fale
  o que está travado"
- **Iterações até aceitar:** 1 — sem rodada de correção. Os prompts seguintes
  mudaram de tarefa (decidir → explicar → executar), não corrigiram saída
  anterior.
- **Erros da IA:** nenhum novo apanhado nesta sessão. O bug do `fl_correction` é
  de sessão anterior (mesmo autor, mesmo módulo) e só foi achado por a coluna de
  robustez ter sido finalmente construída. Suíte: **181 testes verdes** (179 +
  o de `reset` preservando a semente + o de `pmf_mean` recusando a correção
  binária).
- **Decisões escaladas:** 3 fechadas pelo dono em sessão (**12a**, **12b**,
  **12c**), todas com medição antes; 1 medição registrada sem fechar (curva do
  `c` com duas views, seção 10); 1 devolvida ao dono (registro da decisão 8).
- **Tags:** `[PROMPT-CHAVE]` — o padrão da sessão é **"a mudança de horizonte
  reclassifica as decisões"**: as mesmas três perguntas tinham resposta "adia" na
  véspera e "fecha com o motivo medido" depois de o v1 virar entrega final.

---

## 2026-08-07 (sessão 7) — Felipe

**Contexto da sessão:** duas partes. (1) Leitura do estado das decisões a pedido
do dono — o "9" citado na sessão 6 era ambíguo (seção 9 do branch `Felipe` × D9
do branch `Paulo`), que é o próprio problema registrado no topo do
`Decisoes_pendentes.md`. (2) Chegou o `RESPOSTA3` da Lia (midpoint + portão de
volume): fechar tudo que ela pede ou corrige.

**1. Os quatro pedidos dela, fechados.**

- **Chaves derivadas em runtime (item 2):** já era o comportamento
  (`aplicar_veto` monta `nomes` a partir de `view_results`). Mas o medo dela
  tinha caso real: `VIEWS_ATIVAS` no `src/config.py` era constante escrita à
  mão, **não lida por ninguém** e **desatualizada** (ainda listava a B, fora do
  v1 desde 07/08). **Apagada**, com o motivo no lugar. Docstring do
  `aplicar_veto` passou a dizer que a derivação é do `view_results`, para
  ninguém "consertar" reintroduzindo constante.
- **Piso × `score_coerencia` (item 3):** aceito o argumento de regimes disjuntos.
  Compromisso escrito dos dois lados do meu: comentário em
  `view_2_3_fed.py::SOMA_MINIMA` (**o piso é degrau e não vira rampa**) e bloco
  na seção 12 do `Decisoes_pendentes.md`, com a contrapartida dela (o único
  portão binário da régua dela continua sendo o volume) e a ressalva de poder
  discriminante.
- **G5 `0` × `NaN` (item 4):** é decisão do **Paulo** (D12 do branch dele), não
  minha. Repassei a decisão dela com o raciocínio do midpoint semeado em
  `Dump/trocas/FOLLOWUP5_Pedido_Paulo_dados.md`. Não fechei nada no módulo dele.
- **Protocolo anti-overfit (item 6):** registrado na seção 10 como **posição
  dela, não fechada** — é de grupo. Concordo e levo assim para a reunião.

**2. Decisão 6a fechada — pela DONA dela, não por mim.** No `RESPOSTA3` a Lia
declara que colapsa PMF→`p` do lado dela, a partir da `serie_janela` (opção 1).
Marcada 🟢 com escopo explícito: fechou **quem calcula** (a pergunta de
interface); a **forma** do colapso segue dela, com duas candidatas em teste.
Nada muda no meu módulo — `dp_variacao_janela` continua `NaN` em multi-bucket.

**3. A correção que motivou o retorno: renormalizar a `serie_janela` crua não
reproduz o `p` da view.** Ela pretende colapsar sobre a série "renormalizada".
Entre a série crua e o que a view consome rodam três passos, e dois mudam o
número:

| Passo | Efeito que ela não vê |
|---|---|
| `carry_missing` (D6.1) | faixa faltante **herda a última leitura**; renormalizar a linha crua espalha a massa da ausente nas presentes — o tratamento que a 6.1 rejeitou |
| piso de 0,9 (seção 12) | linha degenerada **mata o dia**; renormalizada, ela vira PMF de aparência normal e entra na medição de um dia em que não houve view |
| `daily_preopen` | `serie_janela` tem 2 slots/dia (00:00 e 12:00 UTC), a view vê 1 — o `p_t − p_{t−1}` dela é de 12 h, o da view é de 24 h |

Conserto é de uma linha do lado dela (`carry_missing` é `pmf.ffill()`, e ela
pode importar). Ofereci entregar um `serie_janela_tratada` pronto no
`diagnostics` **se ela quiser** — não fiz, porque volta a pôr tratamento meu
dentro do insumo da régua dela, que é de onde ela fugiu no 6a.

**Quebrou / aprendido:**
- **Constante morta é a pior forma do bug que ela descreveu:** `VIEWS_ATIVAS`
  não quebrava nada porque ninguém a lia — e estava errada havia uma sessão
  inteira. O pedido dela ("derive as chaves") era sobre um risco que eu achava
  que não existia no meu código, e existia num arquivo ao lado.
- **Aceitar o pedido não é o mesmo que ele estar completo.** Os quatro itens
  dela fechavam sem trabalho; o que valeu a sessão foi o passo 1 da lista *dela*
  (colapso sobre a série renormalizada), que não era pedido nenhum e teria
  produzido um `p` diferente do da view sem ninguém perceber.
- **Achado operacional:** não existe `data/` na árvore do branch `Felipe` — os
  parquets e os CSVs do FRED estão commitados no branch `Paulo`, e trocar de
  branch os apaga daqui. **O backtest não roda no estado atual** até os dados
  serem restaurados. Não mexi: puxar `data/` do branch dele mistura arquivo de
  outro dono e é decisão do dono da sessão.

**Pendente:**

*Envio (do dono):*
- `RESPOSTA3_Lia_portao_renormalizacao.md` (Lia) e `FOLLOWUP5_Pedido_Paulo_dados.md`
  (Paulo). O FOLLOWUP5 é o **único item que ainda bloqueia a régua dela**.

*Depende de terceiros:*
- **D12 do branch `Paulo`** (`0` × `NaN` do G5) — agora com a resposta dela na mão.
- **D9 do branch `Paulo`** (overlap dos mercados de FOMC) — segue sem recado meu.
- **Régua do `c`** (Lia): colapso, portão, monotonicidade, entrega.

*Reunião (grupo):*
- Protocolo anti-overfit da Lia (seção 10) — forma × nível × teto.
- Nível e escopo do teto; revisão das provisórias 9/10/11/12; esquema de
  numeração das decisões; orçamentos da camada tática.

*Trabalho meu:*
- Restaurar/combinar o acesso ao `data/` (sem isso nada roda).
- Curva do `c` vetorial; semear a média expansiva da 2.3 com histórico
  pré-janela; banda de não-negociação.

**Uso de IA:**
- **Modelo:** Claude Code / Opus 5.
- **Contexto consumido:** ~50k tokens (estimativa da sessão).
- **Prompt inicial (verbatim):** "na ultima sessão você falou de uma decisão 9 e
  de decisões provisórias, me ajude a entender melhor o estado das decisões e do
  projeto agora. O que ja foi feito o que esta congelado, o que ja pode ser feito
  etc. e também me explique por que algumas decisões estão como provisórias"
- **Iterações até aceitar:** 1 — sem rodada de correção. O segundo prompt do dono
  ("feche tudo que ela pede ou corrige") mudou de tarefa, não corrigiu a anterior.
- **Erros da IA:** nenhum apanhado nesta sessão. Suíte re-rodada após as três
  edições de código: **179 verdes**.
- **Decisões escaladas:** 1 marcada 🟢 (**6a**, fechada pela DONA dela no
  `RESPOSTA3` — registrei, não decidi); 2 posições registradas sem fechar
  (protocolo anti-overfit na seção 10; compromisso de interface do piso na seção
  12); 1 repassada ao dono (**D12 do `Paulo`**).
- **Tags:** `[PROMPT-CHAVE]` — o padrão da sessão é **"ler o que o outro lado vai
  FAZER, não só o que ele PEDE"**: os quatro pedidos fechavam sem trabalho, e o
  único erro real da troca estava no plano dela, num passo que não era pergunta.

---

## 2026-08-07 (sessão 6) — Felipe

**Contexto da sessão:** chegaram as duas respostas (Lia — decisão 6a e pedido de
interface; Paulo — G8 `DFF` e G5 volume). Sessão de ler, conferir e usar: quatro
frentes, na ordem que o dono escolheu (1 → 2 → 5 → 3).

**1. Recado à Lia** (`Dump/trocas/RESPOSTA2_Lia_6a_interface.md`, pronto para envio).
A verificação de lookahead que ela pediu tem uma **terceira** resposta, e é a que
vale: o ponto das 12:00 UTC não é agregado do slot, é **snapshot instantâneo** do
midpoint (deriva de 3–9 s; que a série é midpoint foi MEDIDO pelo Paulo, não
inferido). Execução às 13:30 UTC ⇒ a leitura está 1,5–2,5 h antes. `idade = 0.0`
não é lookahead e não há nada a corrigir.

**2. `aplicar_veto` passa a casar por NOME** (`src/bl_integration.py`). Dicts
chaveados por `diagnostics["view"]`; chave que falta, sobra ou está errada vira
`ValueError` com os dois lados listados. **Não mantive a variante posicional** —
manter as duas manteria a armadilha viva. A ressalva que vai no recado: ela
escreveu `'2.2'`, a chave é `"2.2_inflacao"`.

**3. Colisão de numeração das decisões, registrada** (aviso no topo do
`Decisoes_pendentes.md`). É pior do que parecia: diverge **a partir da seção 8**
nos três branches, e "D11/D12" nas nossas próprias análises são os itens da
**seção 10**, não as seções 11/12. Levantado, com opções, sem escolher.

**4. View 2.3 LIGADA — e o diagnóstico que eu tinha dado estava errado.**

Eu havia reportado que a 2.3 degeneraria: perna do poly = um binário de −50 bps,
88 dias, poly explicando 4,6% da variância da surpresa e sinal constante em 100%
dos dias. **O binário é um bucket de um mercado de 4 que o Paulo já tinha
entregue inteiro** (`data/polymarket_fed_reunioes.parquet`, 18 reuniões, 4–5
faixas). Com a PMF completa:

| | binário | PMF completa |
|---|---|---|
| dias com as duas pernas | 88 | 531 |
| variância vinda do poly | 4,6% | **53%** |
| `corr(surpresa, −e_ff)` | 0,982 | 0,138 |
| sinal positivo | 100% dos dias | 83% |

**Decisão 12 (branch `Felipe`) fechada em sessão, provisória:** `E_FF = DTB3 −
DFF` com a surpresa **demeanada** por janela expansiva (mesma construção da D7.4
da 2.2), e **PMF com soma crua < 0,9 desativa a view no dia**. Opções A/C/D/E
descartadas e registradas.

**Resultado medido** (374 pregões): a 2.3 fica ativa em **325 dias (87%)**, as
duas views convivem em **240 (64%)**, β estimado com **25–35 eventos** de FOMC.
Excesso contra o SPY no teto-no-tilt = 1: de **−0,94 pp** (só a 2.2, alavancagem
1,74) para **+2,68 pp** (alavancagem 1,90). Pareando pela alavancagem medida de
1,90: teto de carteira −7,91 pp × teto no tilt +2,68 pp.

**Quebrou / aprendido:**
- **Lookahead entre rodadas da varredura, meu, achado antes de virar entrega.** O
  laço limpava só `divergencias` (2.2); o acumulador da 2.3 atravessava as 8
  rodadas, então da 2ª em diante a média expansiva já continha dias POSTERIORES
  à data montada. Corrigido com um `MontadorV1.reset()` — mora na classe
  justamente para a próxima view não reintroduzir o bug por esquecimento. O
  número contaminado dizia +4,65 pp; o limpo é **+2,68 pp**.
- **Três arquivos de teste mentiam "OK".** O bloco `__main__` do
  `test_bl_integration.py` estava no MEIO do arquivo (4 testes nunca rodavam
  pelo comando padrão) e `test_taticas.py` / `test_view_2_3_fed.py` chamavam nome
  de função anterior a um rename, morrendo em `NameError`. Suíte hoje: **179
  testes verdes**.
- **Conferir o dado antes de opinar salvou a view.** O diagnóstico "a 2.3
  degenerou" estava baseado no arquivo errado e teria mandado a view para fora do
  v1 (opção E) por engano. O que pegou foi olhar a decisão 10 aberta do Paulo,
  que citava um dataset de FOMC que eu não estava usando.
- **A demeanagem não equilibrou o sinal na janela do backtest — inverteu.** 45%/55%
  no levantamento completo, **22%/78%** dentro do backtest, porque a média
  expansiva carrega o regime de 2024–25. Registrado como ressalva, com o
  refinamento mapeado (semear a média com o histórico anterior à janela).

**Pendente:**

*Envio (do dono):*
- **Recado à Lia** pronto. O único item dele que trava alguém é o `NaN` × `0` do
  G5, e a resposta dela vai para o **Paulo**, não para nós.

*Depende de terceiros:*
- **Decisão 9 do branch `Paulo` (overlap dos mercados de FOMC).** Fechei a opção
  (a) — "vale o mercado da próxima reunião" — **só para o consumo da 2.3**. A
  decisão do dataset é dele e precisa de um recado.
- **Régua do `c` (Lia).** A fiação está pronta e agora com k = 2 em 64% dos dias.

*Reunião (grupo):*
- **Revisão da seção 12** (E_FF demeanado, piso de 0,9) e das provisórias 9/10.
- **D12-teto — nível e escopo**, agora com número de duas views.
- Quantos eventos de FOMC bastam para o β (hoje: piso algébrico de 2; na prática
  25–35).
- Orçamentos da camada tática; decisão 11 (view B).

*Trabalho meu:*
- **Curva do `c` vira vetorial** — com 2 views o escalar deixa de representar.
- Semear a média expansiva da 2.3 com o histórico pré-janela (refinamento medido,
  não decidido).
- Banda de não-negociação (giro desfeito segue em ~35%).

**Uso de IA:**
- **Modelo:** Claude Code / Opus 5.
- **Contexto consumido:** ~105k tokens (estimativa da sessão).
- **Prompt inicial (verbatim):** "chegaram as repostas da Lia e do Paulo. Leia
  elas e me fale o que podemos fazer a partir delas"
- **Iterações até aceitar:** 1 — sem rodada de correção de conteúdo pelo dono. As
  intervenções foram de condução ("vamos de 1,2 e 5 primeiro", "vamos para o item
  3") e duas escolhas de opção (demeanar; view desativada na PMF ruim).
- **Erros da IA:** 2, os dois apanhados pela própria medição antes de virar
  entrega. (1) Diagnóstico da 2.3 baseado no arquivo errado (binário de um bucket
  em vez da PMF completa) — a conclusão "a view degenerou" chegou a ser escrita no
  recado à Lia e foi corrigida antes do envio. (2) Lookahead entre rodadas da
  varredura, por só metade do estado expansivo ser limpo no laço.
- **Decisões escaladas:** 1 fechada (**12 do branch `Felipe`**, provisória, por
  escolha explícita do dono); 1 registrada sem fechar (aviso de numeração); 1
  marcada como dependente de terceiro (Decisão 9 do `Paulo`).
- **Tags:** `[PROMPT-CHAVE]` — o padrão da sessão é **"conferir o insumo no
  repositório antes de concluir sobre ele"**: as duas conclusões erradas da sessão
  vieram de ler o arquivo errado e de supor que o estado era limpo, e as duas
  caíram quando o número foi medido.

---

## 2026-08-07 (sessão 2) — Felipe

**Contexto da sessão:** os dois recados da sessão 4 (`FOLLOWUP4` ao Paulo e
`RESPOSTA_Lia_omega_diagnostics`) **foram enviados pelo dono** — a pendência de
envio da sessão 4 está fechada. Sessão de fazer o que **não** depende das
respostas: três frentes escolhidas por não terem dono externo no caminho.

**1. Escopo do teto medido — a questão de desenho aberta da seção 10 virou número.**

`cap_leverage(w, teto, w_ref)`: com `w_ref` o corte incide sobre `w − w_ref`.
Sem ele, comportamento idêntico ao anterior. `run_backtest(..., teto_no_tilt=)`
liga a variante, e o `backtest_v1.py` passou a varrer os **dois escopos**.

Comparando a Σ|w| **medido igual** (a única comparação honesta — `tilt ≤ t`
limita o desvio, não a carteira, e deixa Σ|w| chegar a 1 + t):

| Σ\|w\| medida | teto na carteira | teto só no tilt | diferença |
|---|---|---|---|
| 1,74 | −15,14 pp | −0,94 pp | **+14,19 pp** |
| 2,48 | −15,92 pp | −1,91 pp | **+14,02 pp** |

- **O buraco de ~14 pp contra o SPY era o escopo do teto, não a view.** A
  parcela de tilt sai de **−11,84% para +0,35%**: no corte de carteira ela
  misturava o tilt da view com o pedaço da perna de SPY que o corte arrancava.
  A view 2.2 sozinha fica **perto de zero** na janela — nem heroína nem vilã.
- A carteira segue perdendo do SPY nos dois escopos, mas por −0,94 pp em vez de
  −14,39 pp. O giro cai junto (0,219 → 0,141/dia).
- **Atribuição saiu para o script** (`r_mercado`, `r_tilt` no diário, exatas por
  linearidade). Era a seção escrita à mão que a re-rodada apagava.

**2. Curva do `c` — o passo (2) da ordem da Lia, pré-executado** (`scripts/curva_c.py`
→ `Dump/analises/Curva_c.md`; `run_backtest(..., incerteza=)` como ferramenta de
**varredura**, o vetor de verdade continua vindo dela pelo `aplicar_veto`).

| c | Σ\|w\| pedida (mediana) | teto 1 morde | ruína sem teto | excesso (carteira) |
|---|---|---|---|---|
| 1 | 195 | 74% | 36 dias | −14,39 pp |
| 0,25 | 79 | 74% | 16 dias | −14,33 pp |
| 0,05 | 19,5 | 74% | 3 dias | −14,33 pp |
| 0,01 | 4,8 | 74% | 0 | −14,12 pp |

- **O `c` encolhe menos do que parece:** com Ω = (1/c)·diag(P·τΣ·Pᵀ) o tilt
  escala como **c/(1+c)**, não como `c`. Perto de `c = 1` metade do peso já vem
  do prior. Dividir o `c` por 100 corta a Σ|w| por 40.
- **O `c` não substitui o limitador de tamanho.** O teto morde em 74% dos
  pregões em TODA a grade, e por isso o excesso quase não se move. É a resposta
  ao passo (3) dela, com número. **Não contradiz a Lia** — o `c` de fato só tira
  peso e a ordem dela segue certa; refina: os dois convivem, o teto não é só
  remendo esperando o Ω.
- **Correção de registro:** o "Σ|w| mediana 24, máx 264" da seção 10 subestima.
  Sem teto o backtest morre no primeiro dia de ruína (2025-03-19 no dado de
  hoje), então aquela estatística só cobria os 26 pregões até lá. Na carteira
  **pedida** — que existe todo dia, por não depender de trajetória — é **195 de
  mediana e 34.481 de máximo**. A conclusão que o número sustentava fica mais
  forte, não mais fraca.

**3. View B fora do v1 (decisão 11, provisória).** Estava registrada como
"bloqueada esperando dado", o que não descrevia a situação:

- **A perna do poly já estava entregue** e ninguém tinha visto:
  `M3_fed_trajectory_*`, 9 faixas ("nenhum corte" a "8+ cortes em 2025"), ~690
  leituras por faixa, 2024-12-29 a 2025-12-10.
- **A perna do mercado não existe de graça, e isso já estava medido** no F6: todas
  as sintaxes do contrato de dezembro voltam vazias no yfinance; só o contínuo
  `ZQ=F` funciona e ele é o da frente. Alternativas são pagas.
- Sai porque **duplica a 2.3** (β e P são os mesmos por desenho), **cobre metade
  da janela** (~210 de 374 pregões) e **a view irmã está travada por um CSV
  grátis** (o `DFF`). Comprar dado para a B enquanto a 2.3 espera o G8 inverte a
  prioridade.
- Substituto **mapeado e não decidido** (é metodológico, do grupo): forward de
  dezembro extraído da curva de bills do FRED — tem precedente na seção 9
  (`ΔDTB3` no lugar do ZQ), com a ressalva de que ninguém mediu o ruído de um
  forward de 1 mês tirado de dois vértices interpolados.
- **Libera a fila do Paulo:** a caça ao ZQ aparece em três pedidos (F6,
  FOLLOWUP2, FOLLOWUP3) e agora não tem consumidor no v1.

**Quebrou / aprendido:**
- **Média de views ativas denunciou um artefato de float.** A coluna "dias acima
  do teto" saiu 94% quando a view só existe em 74% dos pregões. Causa: nos dias
  sem view o BL devolve `w_mkt` com erro de arredondamento (`inv(δΣ)π` não fecha
  em 1,0 exato), e um `> teto` seco contava esses dias como se o teto mordesse.
  Só apareceu porque havia um segundo número medindo a mesma coisa.
- **Conferir número antigo contra medição nova rendeu a correção do 24/264** —
  mesmo padrão da sessão 4, agora aplicado ao registro do próprio time.
- A comparação entre escopos de teto **não pode ser feita pelo rótulo**: `tilt ≤ 1`
  e `Σ|w| ≤ 1` são carteiras de tamanhos diferentes. Sem parear pela alavancagem
  medida, o ganho de 14 pp seria lido como se viesse de graça.

**Pendente:**

*Bloqueado em terceiros (nada a fazer além de esperar):*
- **G8 (`fred_DFF.csv`) — Paulo.** É o gargalo: sem ele o backtest roda com 1
  view de 2. Já cobrado no FOLLOWUP4.
- **G5 (spec do volume) — Paulo**, passado no FOLLOWUP4.
- **Decisão 6a — Lia** (colapso da PMF no `p` do `score_estabilidade`). Não
  bloqueia: o fallback `c = 1` roda.
- **Régua do `c` — Lia.** A fiação está pronta (`aplicar_veto` +
  `omega_fallback(incerteza=)`) e a curva já está medida: quando o vetor chegar,
  é plugar e reportar.

*Reunião (grupo):*
- **D12 — nível E escopo do teto**, agora com número dos dois lados.
- **Orçamentos da camada tática** (`--orcamento-premio`, `--orcamento-drift-*`).
  Sem eles a camada não entra no backtest, apesar dos 32 eventos medidos na
  sessão 4.
- **Decisão 11** — confirmar a saída da B; se reabrir, decidir sobre o proxy de
  forward da curva.
- **Revisão das provisórias** das seções 9 e 10 (τ, δ, H = 1, custo, γ).

*Trabalho meu, destravado quando o dado chegar:*
- **Ligar a 2.3** e re-rodar as duas análises. Com 2 views o escalar de `c` deixa
  de ser o `c` da view e vira média grosseira — a curva teria de virar vetorial.
- **Banda de não-negociação** (revisão condicional do D1): o giro desfeito em
  1–2 pregões está em 32–33% e continua não medido como banda.
- **Seção manual do `Backtest_v1.md`**: a atribuição das 3 rodadas de 05/08
  segue escrita à mão e é apagada a cada re-rodada. Menos crítica agora (a
  atribuição corrente saiu para o script), mas ainda manual.
- **DECISAO-4.1 (horizonte do Q) está dormente, não resolvida:** 2.2, 2.3 e B
  declaram todas `horizonte_q_dias = 1`, então ligar a 2.3 **não** dispara o
  `raise` do `stack_views`. Volta a morder se alguma view defasada (2.4) entrar.

**Uso de IA:**
- **Modelo:** Claude Code / Opus 5.
- **Contexto consumido:** ~90k tokens (estimativa da sessão).
- **Prompt inicial (verbatim):** "Na ultima sessão usamos as respostas que
  recebbemos pra progredir no projeto, escrevemos uns recados para o paulo e Lia
  que eu já mandei pra eles. Queria saber o que podemos fazer ou decidir enquanto
  esperamos pela resposta"
- **Iterações até aceitar:** 1 — nenhuma rodada de correção de conteúdo. As
  intervenções do dono foram de condução ("sim, vamos lá", "vamos atacar o item
  4", "me explique o problema e sua recomendação") e uma escolha de opção (B fora
  do v1).
- **Erros da IA:** 4, todos apanhados antes de virar entrega. (1) Contagem de
  dias acima do teto poluída por erro de float — pega ao cruzar com a média de
  views ativas. (2) `|` sem escape no cabeçalho da tabela gerada, que partia as
  colunas em duas. (3) Afirmação imprecisa de que a fórmula `c/(1+c)` previa a
  queda de **Σ|w|**, quando prevê a do **tilt** (Σ|w| carrega a perna de mercado
  junto) — reescrita em vez de maquiada. (4) Data e estatísticas da primeira
  ruína cravadas à mão no texto gerado; trocadas por valores calculados.
- **Decisões escaladas:** 1 nova (**11**, view B fora do v1 — fechada por escolha
  explícita do dono, provisória). Seção 10 ganhou duas medições e uma correção de
  número; seção 9 teve a linha "Views ativas" anotada. Nenhuma outra fechada.
- **Tags:** `[PROMPT-CHAVE]` — o padrão da sessão é **"medir a pergunta em aberto
  em vez de esperar a reunião respondê-la"**. As três frentes eram itens que
  estavam parados esperando terceiros; nenhuma precisava de fato da resposta, e
  duas mudaram o que a reunião vai discutir.

---

## 2026-08-07  — Felipe

**Contexto da sessão:** chegaram as **três respostas** dos recados enviados em 05/08 (G9 payrolls e
FOLLOWUP3 do Paulo, régua do Ω da Lia). Sessão de ler, conferir, responder e implementar o que as
respostas destravaram. Ordem definida com o dono depois da leitura: recado ao Paulo → `diagnostics`
da Lia → re-rodar o backtest → tratar payrolls.

**Leitura das respostas — o que a conferência achou:**
- **G7 (base de ajuste dos parquets): confere, número por número.** Não aceitei o relatório: extraí os
  dois parquets de `origin/Paulo` e o close antigo (`87721ae~1`) e refiz as medições. Bate exato
  (TIP +0,0000% e TLT −0,0230% na razão abertura/fechamento; close novo/antigo −1,8692% e −0,7914%;
  os outros 7 em 0,0000% nas 5.681 datas comuns). **O alfa fabricado de +1,15%/dia no TIP sumiu.**
- **E o retrabalho que o Paulo anunciou é ~zero — medido.** Ele avisou que eu teria de refazer as
  medições de `k`/sensibilidade porque o nível de TIP/TLT desceu. Medi nos **retornos** (que é o que
  essas medições usam): média de |Δ| de 0,024 bps (TIP) e 0,011 bps (TLT), correlação 0,9992 e
  0,99998. O deslocamento é constante em **todos os 5.680 dias menos um** — 2026-06-01, o
  ex-dividendo que entrou no pull novo. Nada a refazer.
- **⚠️ G8 (`DFF`) não veio e não foi declarado.** A resposta do `FOLLOWUP3` cobre só o G7; o arquivo
  não existe em `origin/Paulo`; o commit se chama `followup3 (G7)` e **dois commits de G9 vieram
  depois**. Pior: o `## Bloqueios` diz **"Nenhum"**. Só descobri cruzando a árvore do git.
- **G9 (payrolls): entregue e útil.** O remap do shutdown é meu, como combinado.
- **Lia:** destravou o G5 (spec do volume) e fechou o formato do `diagnostics`. Me corrigiu em duas
  coisas, nas duas ela está certa (ver "Erros meus").

**Recados escritos (2, commitados, ainda NÃO enviados):**
- **`Dump/trocas/FOLLOWUP4_Pedido_Paulo_dados.md`** — cobra o **G8** (com a nota de processo: item
  não entregue vai como `?` ou como bloqueio, nunca silêncio) e passa o **G5** com a spec da Lia
  transcrita, amarrando o `t_cobertura_min` ao F4 dele (o cap de 20k que ele mesmo mediu) e com a
  lista dos arquivos dos mercados das views ativas, para ele não adivinhar.
- **`Dump/trocas/RESPOSTA_Lia_omega_diagnostics.md`** — `diagnostics` no ar, a pergunta da 6a, o fato
  de interface do `carry_missing`, e o aceite da ordem dela em δ/teto.

**`diagnostics` do Ω implementado** (`poly_loader.diagnostics_qualidade`, `poly_preprocessing.soma_faixas`,
os campos nas 8 views, fusão no `MontadorV1`):
- **Medido na série CRUA**, antes do `carry_missing` e do `daily_preopen`. Foi o ponto que quase passou
  batido e é o que faz o campo valer algo: depois do tratamento não existe mais buraco para contar, e
  sobra 1 ponto por dia em vez de 2.
- **`janela_slots = None`** (vida inteira do mercado até a decisão): o tamanho da janela é output da
  calibração da Lia — não inventei número (CLAUDE.md §6).
- **`n_slots_esperados` truncado pelo nascimento do mercado**, para não confundir "buraco de leitura"
  com "mercado não existia" e ligar o veto dela em cima de mercado íntegro.
- **`omega_fallback(..., confianca=)` → `incerteza=`** a pedido da Lia. O nome dizia o oposto do que o
  número faz — era a própria armadilha que eu descrevi no pedido original.
- **`bl_integration.aplicar_veto`**: veto = view que SAI de P e Q (item 4c dela), reusando o filtro de
  `None` que o `stack_views` já tinha. A função devolve o `incerteza` já reduzido aos sobreviventes,
  porque a armadilha ali é o índice (os vetores dela vêm na ordem das views ATIVAS; a lista tem os
  `None` da cascata intercalados).

**Backtest re-rodado no dado do G7 — com atribuição, em 3 rodadas** (`Dump/analises/Backtest_v1.md`):

| Rodada (teto ≤ 1) | Pregões | Líquido | Benchmark | Excesso |
|---|---|---|---|---|
| parquet antigo (05/08) | 353 | +8,61% | +26,20% | −17,59 pp |
| parquet novo, **truncado** em 2026-07-08 | 353 | +9,43% | +26,20% | −16,77 pp |
| parquet novo, janela cheia | 374 | +15,72% | +30,12% | −14,39 pp |

- A linha 1 **reproduz o LOG de 05/08 exato** — checagem feita de propósito antes de sobrescrever o
  relatório: confirma que o `diagnostics` não mexeu em número nenhum.
- **Correção do dado: +0,82 pp** (com benchmark idêntico à 4ª casa, como tinha de ser). Cresce para
  **+4,03 pp** no teto ≤ 5 — o par TIP/TLT é justamente o que a view 2.2 monta.
- **21 pregões novos: +6,29 pp.** No sub-período a estratégia fez **+5,75% contra +3,11% do SPY**.
- **O veredito de 05/08 continua de pé:** a carteira perde do SPY em toda a varredura e a distância
  cresce com o teto. 21 pregões bons não são evidência contra 374 — anotado no próprio relatório.
- **A duration medida (D11) não se moveu** (8,31 a 8,38): a correção é multiplicativa e some na
  regressão, como previsto ao conferir o G7.

**Payrolls tratados — a amostra da tática 1.3 quase dobrou (19 → 32 eventos):**
- `poly_loader.load_payroll_releases`: remap do shutdown como **exceção declarada com validação** (não
  é regra derivável como o typo de ano do CPI — é fato histórico). `2025-11-20` é o release de
  **setembro**; `2025-12-16` é **combinado out+nov**; **outubro não ganha linha inventada**.
- `premio_condicional.mercados_de_payroll`: **o casamento mercado→release é pela data em que a série
  TERMINA**, não pelo nome do mês. Resolve três problemas de uma vez — a ambiguidade de ano que o
  Paulo sinalizou (dez/2024 vs dez/2025), o desalinhamento do shutdown, e é o próprio critério que a
  tática exige (série que não alcança o release não tem PMF pré-abertura). Set/2025 sai sozinho.
- `load_pmf(..., ordenar=False)`: os arquivos de payrolls vêm **sem slug de balde** (só o tokenId),
  então `bucket_value` quebraria. A entropia não usa valor de balde — por isso a tática foi escrita
  em cima dela.
- **Resultado: 7 FOMC + 13 CPI + 12 payrolls = 32 eventos.** Diferença incerto−previsível
  **+1,099%** com **t de Welch subindo de +2,10 para +2,27**. Payrolls é família **independente**, não
  usada para desenhar a tática — é a evidência mais forte que a 1.3 tem.

**Duas ressalvas que a própria medição levantou, registradas no relatório:**
- **O grupo "previsível" ganhou o choque tarifário** (2025-04-04, −5,9%). A checagem de robustez que
  existia tirava o extremo só do grupo *incerto* — trabalha a favor da tese. Fiz a **simétrica**:
  tirando o extremo dos dois lados a diferença cai para +0,896% mas o **t sobe para +2,34**.
- **A entropia de payrolls vive numa faixa alta e estreita** (0,68–0,96) contra 0,07–0,78 do CPI: um
  payroll "previsível" é mais incerto que um CPI "incerto". O corte é a mediana **de cada família**,
  então cada split é interno e válido, mas o rótulo não é comparável entre elas. E, honestamente: nos
  payrolls **os dois grupos são negativos** — o contraste está na direção certa, o nível não.

**Quebrou / aprendido:**
- **O teste unitário não pega fiação.** O `diagnostics` passou em 167 testes e o backtest quebrou na
  primeira linha real (`pmfs.values()` desempacotado em 2 onde virou 3-tupla). Só o smoke run contra
  o dado do Paulo achou. Lição para o resto da entrega: mudança de shape exige rodar no dado real.
- **Conferir o dado do outro rendeu 3 achados** que o relatório não trazia: o G8 faltando, o
  retrabalho do G7 sendo zero, e a data errada do `march-unemployment-rate-561`.

**Observações para o dono do módulo do Paulo** (não toquei em nada dele):
1. **`data/raw/fred_DFF.csv` não existe** e o `## Bloqueios` do `FOLLOWUP3` diz "Nenhum" — item não
   entregue virou silêncio. Cobrado no `FOLLOWUP4`.
2. **Erro de reporte no G9b:** o entregável diz que a série do `march-unemployment-rate-561` vai até
   2026-03-28; o arquivo vai até **2026-04-03**, que é a data de release do G9a dele. **O dado está
   certo, o entregável não.** Isso restaura o padrão "toda série resolvida termina no dia do release",
   sem exceção — e foi esse padrão que virou a chave de casamento do tratamento.

**Organização dos arquivos (fim da sessão):** a raiz do repo tinha material solto que já não era de
raiz. Agora só sobram os arquivos de governança (`CLAUDE.md`, `LOG.md`, `Decisoes_pendentes.md`,
`README.md`) e as pastas de código.

- `Informações_uteis/` (13 arquivos de espec das views e táticas) → **`Dump/analises/Informações_uteis/`**.
  O git detectou os 13 como rename, então o histórico segue.
- As **três respostas recebidas** foram versionadas em `Dump/trocas/`, junto dos pedidos que as
  originaram: `RESPOSTA_FOLLOWUP3_Pedido_Paulo_dados.md`, `RESPOSTA_PEDIDO_G9_payrolls_Paulo.md` e
  `RESPOSTA_Pergunta_Lia_omega_volume.md`. Estavam fora do rastreio, e o LOG as cita.
- **Renomeado:** o arquivo da Lia veio como `Reposta Lia.md` (typo + espaço no nome, fora da convenção
  `RESPOSTA_*` que todas as outras seguem) → `RESPOSTA_Pergunta_Lia_omega_volume.md`, espelhando o
  `Pergunta_Lia_omega_volume.md` que o originou.
- **Deletado: `leaveoff.md`** (o da sessão 3). É nota de retomada, consumida por construção — o
  próprio arquivo dizia "leia também o `LOG.md`, que traz os números; este é o resumo operacional".
  Com as sessões 3 e 4 registradas, o conteúdo está superado. **Recuperável em `abadefe:leaveoff.md`**
  se alguém precisar.
- **Nada mais foi deletado, de propósito.** Os scripts de medição de decisão reprovada
  (`gap_fds_condicionado.py`, `nivel_divergencia_3_1.py`) e as views cortadas do v1 (2.4, 3.1, C, E, G)
  **não são código morto**: são a trilha de auditoria das decisões D2/D2b/D2c/D3b que o relatório cita,
  e estão cobertos por teste. Apagá-los destruiria a reprodutibilidade do que já foi decidido.

**Pendente:**
- **Os dois recados estão escritos e commitados, mas NÃO enviados** — o envio é do dono.
- **G8 é o gargalo:** sem `DFF` o backtest segue com 1 view de 3. A view B continua sem caminho (ZQ de
  dezembro, sem fonte grátis, não pedido a ninguém).
- **Decisão 6a aberta** (colapso da PMF no `p` do `score_estabilidade`) — depende da Lia; não bloqueia,
  o fallback `c = 1` roda.
- **Teto de alavancagem (D12):** posição da Lia registrada na seção 10; a ordem dela (c → medir Σ|w| →
  decidir teto) vai para a reunião.
- **Camada tática segue desligada** por falta dos orçamentos (parâmetro de reunião). O ganho de
  amostra do G9 é da **medição**, não do backtest.
- **Seção manual em `Backtest_v1.md`:** a atribuição das 3 rodadas é escrita à mão e re-rodar o script
  a apaga. Avisado no topo da própria seção.

**Uso de IA**
- **Modelo:** Claude Code / Opus 5.
- **Contexto consumido:** ~150k tokens (estimativa da sessão inteira).
- **Prompt inicial (verbatim):** "chegaram as respostas do paulo e da Lia. Vamos começar lendo a do G9
  RESPOSTA_PEDIDO_G9_payrolls_Paulo.md. ela veio com o seguinte texto: Buraco real no calendário: não
  há release entre 2025-09-05 e 2025-11-20 (76 dias) — é o shutdown de 2025. Como o BLS remanejou o
  cronograma, a coluna mes_referencia (que eu derivo por "mês do release − 1") não bate 1:1 nessa
  janela. Deixei isso marcado cru no próprio CSV ([ATENCAO: gap de 76 dias… shutdown…]) — a correção
  fica com o Felipe no tratamento, como o pedido pediu."
- **Iterações até aceitar:** nenhuma correção de conteúdo do dono. As intervenções dele foram de
  enquadramento (perguntar o que era o passo 2, se as decisões de desenho estavam abertas, de onde vem
  o dado do backtest) — e a de "as decisões estão em aberto?" **mudou a entrega**: gerou o registro da
  6a, que eu tinha tratado só como nota de conversa.
- **Erros da IA:** 5, todos apanhados antes de virar entrega. (1) Chamei `_soma_faixas` antes de
  existir, ao mover a função para o módulo compartilhado. (2) **O grave:** deixei um `pmfs.values()`
  desempacotado em 2 quando virou 3-tupla — passou em 167 testes unitários e só quebrou no dado real.
  (3) Escrevi o arquivo de teste por heredoc e os escapes colapsaram (`\n` virou quebra de linha),
  SyntaxError. (4) Igualdade de float num teste (0,92). (5) A nota do release combinado de 2025-12-16
  não era gravada porque o mês derivado já saía certo — achado ao inspecionar a saída, não por teste.
  Além disso, uma correção de rumo: comecei a implementar `janela_slots` com valor cravado e voltei
  atrás — é parâmetro da Lia, não meu.
- **Decisões escaladas:** 1 (**6a**, subitem da decisão 6). Nenhuma fechada.
- **Tags:** `[PROMPT-CHAVE]` — o padrão desta sessão é **"conferir o dado do outro em vez de aceitar o
  relatório"**. Re-medir o G7 em vez de confiar no resumo rendeu três achados que o entregável não
  trazia (o G8 faltando, o retrabalho anunciado sendo zero, a data errada do G9b), e um deles mudou o
  desenho do tratamento de payrolls.

---

## 2026-08-05 (sessão 3) — Felipe

**Contexto da sessão:** retomada pelo `leaveoff.md` da sessão 2. Três frentes, na ordem em que o leaveoff mandava: destravar o push, despachar os recados, implementar o I5.

**Push destravado.** O 403 era de conta: o `git` local está com `menusoids-p`, mas a credencial do push vem do `gh auth`, que estava na `Gruppy-FelipeM` (sem escrita no repo da Lia). O `gh auth login --web` trava sem terminal interativo, então rodei o **device flow do GitHub por curl** e o dono autorizou o código no browser. Conta ativa agora é `menusoids-p`, com `push: true` confirmado pela API. **24 commits empurrados** (`a4edcb6..1faa09b`) — a maratona inteira chegou ao repo compartilhado. A `Gruppy-FelipeM` continua no keyring, inativa.

**Dois recados escritos** (o `FOLLOWUP3` já estava pronto e segue sem enviar):
- **`Dump/trocas/PEDIDO_G9_payrolls_Paulo.md`** (novo) — G9a calendário de divulgação do Employment Situation (com o 403 do BLS já sinalizado e o release calendar do FRED como plano B) e G9b varredura dos mercados de payrolls no Polymarket, mesmo procedimento do G4. Justificativa nos números reais: a tática de prêmio roda com **19 eventos** (7 FOMC + 12 CPI) e a PMF do poly só existe de 2025, então esticar a janela para trás não traz evento nenhum — payrolls é o único jeito barato de aumentar a amostra. Três itens específicos pedidos: buckets ou binário, se a série chega ao slot pré-abertura, e quais termos de busca acharam.
- **Régua do Ω anexada ao `Pergunta_Lia_omega_volume.md`** (seção 4) — o Ω vem como **multiplicador de confiança** sobre `diag(P·τΣ·Pᵀ)`, não variância absoluta. Três argumentos: o τ se cancela na razão `τΣ/Ω` (revisão futura do τ não recalibra o módulo dela), sobra confiança relativa (que é o que o protocolo dela produz), e some a armadilha de escala. Cita o encaixe exato — `omega_fallback(P, sigma, tau, confianca=None)` — e a conversão caso ela já tenha algo em escala absoluta.

**I5 implementado — a entrega final roda ponta a ponta:**
- **`src/backtest.py`** (novo) — motor puro, sem plumbing de dado: `derived_weights` (o drift do dia, contra o qual o giro é medido — D8), `transaction_cost`, `carry_cost` (financiamento e aluguel declarados, hoje 0,0), `cap_leverage`, `reversal_share`, `run_backtest` e `summary` com o **custo de breakeven** como métrica do relatório.
- **`scripts/backtest_v1.py`** (novo) — liga no dado real do Paulo, com as três regras de não-lookahead aplicadas por dia (PMF no slot das 12:00 UTC; breakeven e curva da última leitura estritamente anterior; média da divergência e durations em janela expansiva).
- **`tests/test_backtest.py`** (novo, 24 testes) — inclui o **obrigatório do D8**: ir de `w = 0` a `w = 1` cobra exatamente `c`. **Suíte: 158 testes verdes** (153 → 158).

**Resultado do backtest** (`Dump/analises/Backtest_v1.md`) — 353 pregões, 2025-02-10 a 2026-07-08, **só a view 2.2 ativa** (a 2.3 e a B ficam fora por insumo que não chegou: DFF/G8 e ZQ de dezembro — não é cascata, é dado ausente), camada tática desligada por falta de orçamento:

| | Σ\|w\| ≤ 1 | ≤ 2 | ≤ 3 | ≤ 5 |
|---|---|---|---|---|
| retorno líquido | +8,6% | +7,4% | +6,1% | +3,5% |
| sharpe | 0,71 | 0,59 | 0,47 | 0,26 |
| giro diário médio | 0,22 | 0,36 | 0,50 | 0,78 |
| giro desfeito em 1–2 pregões | 33% | 32% | 32% | 32% |
| custo de breakeven | 13,3 bps | 8,1 | 5,8 | 3,6 |

**Benchmark (comprar e segurar SPY): +26,2%.** A carteira **perde por 17,6 pp** no teto mais apertado, e a distância cresce conforme o teto afrouxa.

**Achado central: o custo não é o culpado.** O retorno **bruto** já é +10,3%, e o breakeven de 13,3 bps é **6,7× a premissa de 2 bps** — há folga larga de custo. O mecanismo mais provável é mecânico: o teto escala TODAS as pontas junto, inclusive a de SPY que vem do prior, e com a view ativa em 74% dos pregões parte do orçamento sai do SPY numa janela em que o SPY fez +26%. **Questão de desenho registrada e não decidida:** o teto corta a carteira inteira ou só o tilt da view?

**As duas checagens obrigatórias do D8, respondidas:** giro diário médio de 0,22 (teto 1) e **33% dele desfeito em 1–2 pregões**. É material, mas com 6,7× de folga de custo **não é o que está segurando o resultado** — entra como insumo da revisão condicional do D1 (banda de não-negociação), não como veredito sobre o H = 1 dia.

**Duas decisões escaladas** (registradas na **seção 10** do `Decisoes_pendentes.md`, provisórias):
- **D11 — duration do breakeven MEDIDA**, não cravada. Regressão do retorno do par (o mesmo `pair_P` da view) contra o Δbreakeven, janela expansiva: **8,31 a 8,38** na amostra. O dado confirmou o "~8" da espec — o palpite estava certo e agora é medição.
- **D12 — teto de alavancagem.** Sem teto o backtest vai à **ruína** dentro da amostra: Σ|w| mediana **24**, máximo **264**. Causa estrutural, não numérica — o I3b casou a duration do par TIP/TLT justamente para cancelar o movimento de juros, e `w ∝ Δμ/(δσ²)` numa direção de variância pequena explode por construção. ⚠️ **Encosta no módulo da Lia** (teto é dimensionamento de risco, mesma família do δ) e é **remendo no lugar do Ω**: com `c = 1` a view é confiada tanto quanto o prior, e é daí que vem a alavancagem.

**Observação para o dono do módulo do Paulo:** nenhuma nova. O G7 não afeta este backtest (é fechamento contra fechamento; o G7 só contamina `abertura→fechamento`, janela das táticas).

**Pendente:**
- **Os três recados foram ENVIADOS pelo dono em 05/08** (`FOLLOWUP3` com G7+G8 e `PEDIDO_G9` ao Paulo, régua do Ω à Lia). Aguardando resposta — nada a despachar.
- **O que cada resposta muda no backtest:** o **G8/`DFF`** destrava a view 2.3 e o backtest deixa de rodar com uma view só; o **Ω da Lia** é o que mexe direto na alavancagem (um `c > 1` encolhe o tilt e dispensaria o teto); o **G7** não muda nada aqui; o **G9/payrolls** não muda nada enquanto a camada tática estiver desligada.
- **Camada tática desligada** por falta dos orçamentos (`orcamento_max`, `orcamento_acoes`, `orcamento_rf`) — parâmetros de reunião, não inventados. O script já está ligado neles: passar `--orcamento-*` liga a camada sem tocar em código.
- **View B sem caminho:** precisa do ZQ de dezembro, que não tem fonte grátis (F6) e **não está pedido a ninguém**.
- **I6 inalterado** e `e_ff_bps` da 2.3 incompleto até o `DFF` chegar.

**Uso de IA**
- **Modelo:** Claude Code / Opus 5.
- **Contexto consumido:** ~135k tokens.
- **Prompt inicial (verbatim):** "A ultima sessão foi longa e levantou varias coisas para fazer. Quero retomar de onde parei nela. Fiz ele montar leaveoff.md. Leia e me fale de onde retomamos"
- **Iterações até aceitar:** nenhuma correção do dono sobre o conteúdo. 3 correções minhas apanhadas pela execução: teste de breakeven escrito com retornos aleatórios (a estratégia sintética perdia no bruto e o breakeven saía negativo — trocado por retornos determinísticos), crash de cp1252 no print do console (o arquivo já saía em utf-8), e o `|` do rótulo `Σ|w|` quebrando a tabela markdown.
- **Erros da IA:** nenhum de conteúdo. Um número herdado errado: o `leaveoff.md` dizia 23 commits à frente e eram 24 (o commit do próprio leaveoff), corrigido na leitura do git.
- **Decisões escaladas:** 2 (seção 10 do `Decisoes_pendentes.md`: duration medida e teto de alavancagem).
- **Tags:** `[PROMPT-CHAVE]` — o padrão desta sessão é **"implementar até rodar revela o parâmetro que ninguém tinha decidido"**: o I5 não descobriu um bug, descobriu que duas decisões numéricas (duration da 2.2, teto de risco) tinham passado despercebidas por nunca terem sido exercitadas. Escrever o loop foi o que forçou as duas à superfície.

---

## 2026-08-04 (sessão 2) — Felipe

**Contexto da sessão:** o grupo liberou o Felipe a fechar sozinho as decisões que estavam travadas em reunião, por causa da proximidade da entrega. Sessão inteira dedicada a isso — uma maratona de decisões, cada uma apresentada com explicação leiga, o que afeta, recomendação e consequência, e **medida antes de fechar sempre que havia dado para medir**. Todas as decisões desta sessão são **provisórias e marcadas para revisão do grupo** (instrução explícita do dono).

**Decisões fechadas (13):**
- **D1 — H = 1 dia.** Σ e π já são diários (zero conversão), as views de evento já entregam em 1 dia, e o dado do poly tem 2 pontos/dia. Fecha a 4.1 como conta mecânica.
- **D2 — views defasadas fora do v1** (2.4 eleitoral, C geopolítica, E tarifas, G fiscal). Base: `scripts/janela_negociavel.py` — parti o retorno do dia em gap (não negociável) e abertura→fechamento (negociável) e medi contra o Δp do poly. Na eleição 2024 sobra **23%** do efeito na janela negociável (só XLF significante); TLT, o "Trump trade" mais forte, **some inteiro** (−0,072 no gap → +0,010 no negociável).
- **D2b — 3.1 recessão fora, pelo motivo certo.** Ver "Erro meu". `scripts/nivel_divergencia_3_1.py` testou o sinal de NÍVEL (`z(p_poly) − z(−spread)`, que contorna a falta de α/β do probit por monotonicidade): no par que a view monta (defensivo − cíclico) **nada** (t entre −0,46 e −1,05); ativo a ativo aparece efeito **direcional** e significante (SPY +0,59% em 10 pregões), que a view **não consegue expressar** porque o P dela é neutro em mercado (`P[SPY] = 0`). Não redesenhei para direcional: sinal contrário à própria tese, 245 pregões, um ano só, z-score in sample.
- **D2c — corte revisado, redesenho tentado nas quatro.** **Achado grande:** o arquivo `M9_midterms_2022_will-the-democratic-party*` que o Paulo puxou por engano é o mercado da **Câmara 2026** (355 dias, jul/2025→jul/2026) — a decisão 6.4 dava a view eleitoral como tendo **um único episódio**, e não tinha. Primeiro teste **fora da amostra** do projeto: se o mecanismo fosse partidário, os sinais de 2026 ("democratas controlam a Câmara") deveriam **inverter** contra 2024 ("Trump vence"). XLF inverteu o sinal mas perdeu a significância; **TLT cai nos dois mercados** (−0,072 e −0,075, ambos significantes), o que nenhuma leitura partidária sustenta. A view **reprova fora da amostra** — argumento muito mais forte que "amostra curta". Na C, o mercado do Irã de 2026 mostra **XLE com r = +0,54 no gap** (o mecanismo é real e é a correlação mais forte da maratona) mas nada na janela negociável, com 27 observações. E e G morrem por dado: **13 e 3 dias** de cobertura.
- **D3 — camada tática ENTRA, redesenhada.** `scripts/premio_condicional.py`: a âncora de Savor-Wilson diz que o prêmio é compensação por **risco de evento**, logo só deveria existir em anúncio incerto. Separando por **entropia normalizada da PMF na véspera** (medida escolhida por não depender das decisões 1.2 nem 6.1): anúncio incerto **+0,383%** de média e +0,444% de mediana contra **−0,704%/−0,139%** do previsível, e +0,079% do dia sem anúncio na mesma janela (t de Welch +2,10, n 9 vs 10). Mesma direção nas duas famílias (FOMC e CPI) separadas. Tirando o pregão mais extremo, a média do grupo incerto ainda fica ~4× um dia normal.
- **D3b — gap de fim de semana FORA.** `scripts/gap_fds_condicionado.py`: condicionar a |Δp| grande **funcionou como método** (achou significância onde a versão incondicional não achava: SPY t +2,22, XLF t +3,21 no M4), mas o **sinal é de reversão, não de continuação** — a tática compraria a direção do poly e perderia. Não inverti a tática para operar a reversão: seriam 25 observações de um mercado num ano em que a reversão intradiária foi o regime.
- **D4 — balde aberto = ponto médio extrapolado (meia largura da grade); faixa faltante = carrega a última leitura e depois renormaliza.** Uma regra cobre os dois casos medidos, sem parâmetro e sem lookahead: medi que a faixa que morre já decaiu para ~zero antes de parar de negociar ("nenhum corte" morreu valendo **0,0045**; "1 corte", **0,0030**), então carregar ≡ zerar; e para a faixa que some e volta (mar/2026: 24 de 60 slots completos) carregar é melhor que renormalizar sobre as presentes.
- **D5 — sem correção de favorite-longshot no v1** (γ = 1,0), com o resultado final reportado também em γ = 1,1 e 1,25 como coluna de robustez. 9 mercados resolvidos não calibram curva própria; γ de aposta esportiva mexeria 25% na mediana de um mercado de p baixa sem âncora no nosso dado.
- **D6 — não pagar por ZQ; substituto medido.** `scripts/surpresa_fomc.py`: ΔDTB3 do dia do FOMC no lugar da variação do fed funds future dá **36 reuniões** (contra 8 se fosse pelo poly) e **7 de 7** sinais coerentes com Bernanke-Kuttner. Ressalva medida: a ORDEM das magnitudes não bate (XLU e TLT, que deveriam ser os mais sensíveis, dão os β mais fracos) e a surpresa é pequena (σ 3,3 bps). A expectativa (`e_ff_bps`) sai de DTB3 − DFF; **DFF pedido como G8** no `FOLLOWUP3`.
- **D7 — δ = 3,0 e τ = 1/T.** δ **medido no nosso SPY** com DTB3 como taxa livre de risco: 3,01 na história inteira (janelas curtas dão 3,4–4,9, infladas pelo bull recente) — não é número de livro. τ pela regra 1/T (T = janela de estimação do Σ), **com o Ω da Lia ancorado em `diag(P·τΣ·Pᵀ)`**, o que faz o valor absoluto de τ sair da conta e deixa sobrar a confiança relativa, que é o que o módulo dela mede. Interface a comunicar à Lia — não é decisão dela.
- **D8 — custo = 2 bps/lado sobre `Σ|Δw|`, mais financiamento e aluguel declarados em separado; a métrica do relatório é o custo de BREAKEVEN.** Disparei subagente de pesquisa a pedido do dono. Confirmou a forma (`c·Σ|Δw|` é o consenso, idêntica à de paper de BL verificado) e que 2 bps é **conservador** (spread cotado desses 9 ETFs é 1–2 bps cheios; all-in medido do SPY em ordem de US$ 25 M é 0,30 bp). Corrigiu três coisas minhas: faltavam as parcelas de **financiamento da alavancagem e aluguel dos shorts** (pesos irrestritos), a varredura devia virar **custo de breakeven**, e o Δw tem de ser contra o peso **derivado** (pós-drift), não contra o alvo anterior.
- **D9 — divergência demeanada (7.4) e horizonte = pregões até a divulgação do CPI (7.2).** `scripts/convergencia_2_2.py`: o viés estrutural é **+2,03 pp de média com 2,26 pp de desvio** — do tamanho de toda a variação do sinal, logo a view ficaria comprada em inflação por aritmética. E o breakeven **realmente anda** na direção do poly até a divulgação (+0,0063, t +3,42), com o padrão certo na contagem regressiva (faltando 1–5 dias o coeficiente cai para +0,0022: sobra pouco gap a fechar).
- **D10 — quatro limitações declaradas** (5.1 lista mercado→ETF é heurística de download; 5.4 shutdown segue excluído; 6.3 CPI só de 2025; 6.4 substituída pelo achado do D2c). **5.3 (petróleo como termômetro da C) saiu da lista de limitações e virou munição do D2c** — é o mesmo desenho das views que sobreviveram. **5.2 mantida fora**, com uma exceção que não custa modelo: payrolls não vira view, vira **mais eventos** para a tática de prêmio (que hoje roda com 19).

**Código:**
- **`src/poly_preprocessing.py` destravado** (era o `TODO(DECISAO-11a/11b)`): `favorite_longshot` e `favorite_longshot_pmf` com γ = 1,0 = identidade, `carry_missing` (6.1) e `bucket_values_with_open` (1.2). `open_bucket_value(bound, side)` foi **substituída** — a regra da 1.2 é sobre a GRADE do mês, não sobre um bucket isolado, e a largura sai da própria grade (que muda de 3 a 9 faixas e inverte de sinal em jul/2026).
- **6 scripts de medição novos** + **4 arquivos de teste novos**, mais 4 testes de módulo reescritos (os que exigiam o stub falhar alto agora conferem o comportamento decidido). **Suíte: 121 testes verdes** (98 → 121).
- `scripts/convergencia_2_2.py` e os outros reusam o OLS de `janela_negociavel.py` em vez de duplicar.

**Quebrou / aprendido:**
- **Erro meu de classificação, corrigido em sessão:** no D2 tirei a **3.1 junto com as views defasadas**, e ela não é defasada — o sinal dela é divergência de NÍVEL entre dois termômetros lidos no mesmo dia (`p_poly − p_curva`), mesma família da 2.2, que sobreviveu. O dono apanhou isso ao perguntar quantas views tinham sobrado. Reabri como D2b e rodei o teste do sinal certo; a conclusão não mudou, mas passou a ter fundamento medido em vez de emprestado. **Aprendizado: medir a coisa certa e medir bem são falhas independentes — a segunda é visível, a primeira não.**
- **O instrumento da view 2.2 está errado, e só apareceu porque o teste falhou.** `log(TIP) − log(TLT)` deu coeficiente **negativo** (−0,077) contra a divergência, enquanto o Δbreakeven deu **+0,0063 com t +3,42**. Causa: TIP tem duration de ~7 anos e TLT de ~26 — a oscilação de juros do TLT abafa o sinal de inflação. **A tese da view está certa e o par que ela monta está errado.** Virou o item I3b.
- **Condicionar é um método, não um salvador.** A mesma receita (separar por incerteza/tamanho do Δp) salvou a tática de anúncios e **condenou** a de fim de semana — nesta ela achou significância com o sinal invertido. Quem decide é o dado, não a receita.
- **O padrão que se repete em tudo:** a informação do Polymarket **aterrissa no gap de abertura**. Apareceu na tática de fim de semana (04/08 manhã), na eleição 2024, na recessão 2025 e no Irã 2026 (XLE com r = +0,54 no gap e nada depois). Não é achado de uma view — é característica do dado, e é o que derruba a tese de defasagem inteira.
- **Arquivo puxado por engano não é arquivo inútil.** O `M9_midterms_2022_*` de 711 slots é o mercado da Câmara 2026 e virou o único teste fora da amostra do projeto. A armadilha de nome estava registrada no LOG de 30/07 como curiosidade; era dado.

**Pendente:**
- **`Decisoes_pendentes.md` segue intocado** (instrução vigente desde 27/07 e não revogada). As 13 decisões desta sessão estão registradas **aqui** e na lista de tarefas, com um item explícito de **revisão pelo grupo** — o dono pediu para construir com elas e revisar com calma depois. **Prioridade de revisão: D7 (τ e δ), que encosta no módulo de risco da Lia.**
- **Recado à Lia ainda não enviado:** o Ω precisa vir como **multiplicador de confiança** sobre `diag(P·τΣ·Pᵀ)`, não como variância absoluta. É régua de interface, não mudança de metodologia dela. Vai junto com o `Pergunta_Lia_omega_volume.md`.
- **`FOLLOWUP3` ganhou o G8** (série `DFF` do FRED) e um item opcional com teto de 15 min (testar se o Nasdaq Data Link grátis tem futuros do CME). **Ainda não enviado ao Paulo.**
- **D3c aberta e bloqueada por dado:** payrolls como terceiro tipo de anúncio da tática de prêmio — precisa de pedido novo ao Paulo (calendário + mercados), mesmo procedimento do G4.
- **Implementação, na ordem:** I1 config, I3 Σ e w_mkt (nada no repo os constrói), I3b duration no P da 2.2, I4 plano B do Ω, I5 loop de backtest. O I5 carrega duas checagens obrigatórias vindas do D8: reportar o giro diário e decompor quanto dele é reversão em 1–2 dias.
- **O D1 fica sob revisão condicional:** se o giro medido for alto e o custo de breakeven baixo, a resposta não é abandonar H = 1 dia — é banda de não-negociação, que a pesquisa aponta como a mitigação simples mais eficaz.
- **I6 inalterado:** janelas de TIP/TLT seguem contaminadas até o G7 chegar. Nenhuma medição desta sessão depende disso (as janelas medidas terminam antes do degrau de ~2026-06-01, e deslocamento constante não move covariância nem coeficiente).

**Uso de IA:**
- **Modelo:** Claude Code / Opus 5 (mais um subagente de pesquisa para o D8).
- **Contexto consumido:** ~120k tokens (~60% de janela de 200k).
- **Prompt inicial (verbatim):** "Com a aproximação da entrega final o grupo me liberou fazer as escolhas sozinho. O que ainda precisa ser decidido e/ou implementado? Enquanto o follouwup 3 não chega"
- **Iterações até aceitar:** 1 por decisão — as 13 foram aceitas na primeira apresentação. Quatro intervenções do dono mudaram o rumo sem serem correção de erro: (1) "quantas views temos agora?", que expôs a classificação errada da 3.1; (2) "essa parte não seria da Lia?", checagem de propriedade de módulo no D7; (3) a instrução de princípio "cortar views é ruim, é melhor fazer algo mais complexo para mantê-la", que gerou o D2b e o D2c; (4) o pedido de disparar subagente de pesquisa no D8 em vez de aceitar a minha preconcepção.
- **Erros da IA:** 1 de conteúdo — classifiquei a view 3.1 como defasada e a cortei no D2 com base na medição errada (Δp em vez do nível). Detectado pelo dono, reaberto como D2b e remedido; a conclusão sobreviveu, o fundamento não. Um erro de premissa apanhado por mim antes da pesquisa: a minha recomendação inicial de custo (2 bps) ignorava financiamento e aluguel, que os pesos irrestritos exigem.
- **Decisões escaladas:** — (nenhuma para `Decisoes_pendentes.md`; as 13 foram fechadas em sessão pelo dono com autorização do grupo, e todas estão marcadas para revisão posterior). 3 pedidos novos gerados: G8 ao Paulo, payrolls ao Paulo (D3c) e a régua do Ω à Lia.
- **Tags:** `[PROMPT-CHAVE]` — dois padrões desta sessão são candidatos: (1) **"antes de fechar a decisão, medir a premissa dela"** — foi o que inverteu o D3 (a tática fundadora estava condenada e voltou condicionada) e o que deu fundamento novo ao D2b; (2) **"testar fora da amostra quando aparecer um segundo episódio"** — o mercado da Câmara 2026 transformou "amostra curta" em "reprovou fora da amostra", que é a diferença entre uma desculpa e um resultado.

## 2026-08-04 — Felipe

**Feito:**
- **Resposta do `FOLLOWUP2` (G1–G6) recebida e auditada** arquivo por arquivo contra `origin/Paulo` @ `a9be92b` (extraído com `git archive` para scratchpad, **sem merge**). Tudo bate: G1 (51.129 linhas, 9 tickers, 2003-12-05 → 2026-07-08, merge com o close sem sobra dos dois lados, zero abertura ausente); G2 (6.152 / 16.848 / 18.934 linhas, 253 / 719 / 799 ausentes, cabeçalho `observation_date,<ID>`, **zero** ocorrências de `"."` — o ausente é campo vazio, como ele reportou); G3 (soma Yes+No = 1,0000 min/mediana/máx nos dois mercados); G4 (5 arquivos de jan/2026); G6 (linha crua de dez/2025 presente — o `load_cpi_releases` já corrige por regra geral). Única divergência, irrelevante: no M4 os slots de 12h com os dois lados são 715, não 716. Arquivo arquivado em `Dump/trocas/RESPOSTA_FOLLOWUP2_Pedido_Paulo_dados.md` (`c123470`).
- **`src/market_loader.py` criado** — a leitura do dado que não é do Polymarket não existia (o `poly_loader` só cobre o poly, e o pivot do parquet estava duplicado dentro de um script). Funções puras: `load_etf_prices` (parquet longo → largo, serve aos dois arquivos porque deduz a coluna de valor), `load_fred` (CSV cru → Series, vazio → NaN) e `check_same_grid`. `scripts/perfil_defasagem_k.py` passou a reusar o leitor (`3dd8b36`).
- **Três decisões de módulo (escopo próprio, categoria 2 do CLAUDE.md §1):** (a) o FRED sai **na unidade do arquivo** (pontos percentuais), sem conversão silenciosa — a 3.1 usa assim, a 2.2 divide por 100 no chamador, e está escrito no docstring porque foi esse tipo de descasamento que quebrou a 2.2 em 30/07; (b) **feriado não é preenchido** (NaN), igual ao `poly_loader` — join com calendário de pregão é do backtest; (c) marcador `"."` (que o F1 supunha) **derruba a leitura** em vez de virar coluna de texto.
- **View 3.1 ligada ao FRED** (`6217959`): `curve_spread` (DGS10 − DTB3 em pp, data sem uma das pontas cai fora) e `p_curve_at` (probit na **última leitura estritamente anterior a D**). **Regra de lookahead decidida na sessão:** o H.15 publica a taxa de D depois do fechamento de D, então o rebalanceamento de D só enxerga D−1 — contraparte da regra das 12:00 UTC do `poly_loader`. Fim de semana e feriado caem por consequência. Teste com armadilha plantada (spread absurdo em D) garante que a leitura do próprio dia não entra. Rodado na janela do M4: 357 datas, spread D−1 disponível em todas, mediana +0,19 pp, **10 dias de curva invertida**.
- **`src/taticas_common.py`** ganhou as duas janelas de retorno que as táticas declaram: `intraday_returns` (abertura → fechamento, gap de fim de semana) e `close_to_close_returns` (1.3 e passo diário do drift).
- **`scripts/premissa_taticas.py` + `Dump/analises/Premissa_taticas.md`** (`56ec954`) — mede a premissa das 3 táticas **sem nenhum parâmetro humano** (o `dw` é linear nos orçamentos, então o que se mede é retorno por unidade de orçamento).
- **Suíte: 98 testes verdes** (85 no início da sessão → +6 do `market_loader`, +4 da 3.1, +3 das janelas).
- **`Dump/trocas/FOLLOWUP3_Pedido_Paulo_dados.md`** escrito: um item só (G7), com a evidência, a causa e o formato de devolução.
- **`Dump/reuniao/Pauta_reuniao_explicada.md` atualizada com os três achados** (`d7d7239`): nota de terceira atualização no cabeçalho; **2.2 marcada ⚠️ MEDIDA** (os três resultados, com o limite de leitura de cada um, a ressalva do TIP/TLT contaminado e a decisão reformulada — deixou de ser "vale uma camada a mais?" e virou "vale uma camada cuja âncora principal não se reproduziu no nosso período?", com três saídas listadas); **2.3 marcada ⚠️ ATUALIZADA** (a janela de 50 dias do livro de RF não cabe entre dois FOMCs — ou vira "até a véspera do próximo FOMC", que é o que o código já faz, ou um número ≤ 29); linhas 2.2 e 2.3 do resumo refeitas. **Nada fechado** e `Decisoes_pendentes.md` intocado.

**Quebrou / aprendido:**
- **ACHADO QUE INVALIDA UMA JANELA — os dois parquets de preço não estão na mesma base de ajuste.** Mediana de `abertura/fechamento − 1`: **TIP −1,15%** e **TLT −0,41%** contra −0,03% a −0,06% nos outros sete. O degrau tem data (0,9878 até ~2026-06-01, 1,0000 depois) e a causa está no git: o `etf_prices_daily.parquet` é de **2026-07-09** (`48cb12e`) e o `etf_open_daily.parquet` de **2026-08-02** (`7ea4e86`) — um ex-dividendo entre os dois pulls, e o `auto_adjust=True` reescala toda a história anterior à data-ex de **um** dos arquivos. Os dois deslocados são justamente os de distribuição **mensal**. Efeito: `abertura(D) → fechamento(D)` de TIP e TLT ganha **+1,15% e +0,40% fabricados por dia** na amostra antiga. Fechamento contra fechamento não sofre; **correlações também não** (deslocamento constante não muda covariância). **Observação para o dono do módulo (CLAUDE.md §2): nada foi tocado no pipeline do Paulo** — o conserto é re-baixar os dois no mesmo pull, e foi para o `FOLLOWUP3`. No meu lado ficou o detector `market_loader.adjustment_gap()`, sem número mágico (devolve a medida, quem lê decide).
- **Erro meu de método, corrigido no meio da sessão:** escrevi no docstring do `market_loader` e no cabeçalho do relatório que "os dois arquivos estão na mesma base ajustada" — copiando a declaração do Paulo — e só medi depois. A primeira versão do `Premissa_taticas.md` saiu com as médias de TIP/TLT como se fossem válidas. Aprendizado: **base de ajuste declarada não é base de ajuste conferida**; "mesmo método" não implica "mesma base" quando os downloads são de datas diferentes. A conferência custa uma linha (`adjustment_gap`) e agora roda antes de qualquer número de janela intradiária.
- **Prêmio de anúncios (1.3) não aparece na amostra.** SPY de fechamento(D−1) a fechamento(D): FOMC **+0,062%** contra **+0,060%** dos demais dias da mesma janela (t 0,28, n 36); CPI **−0,394%** (t −0,97, n 13). A âncora Savor-Wilson não se materializa em 2022–2026 — evidência **adversa** à candidata-fundadora da camada tática, e o oposto do que a espec supõe. Amostra do CPI é curta por construção (calendário só de 2025 em diante).
- **Gap de fim de semana: a continuação intradiária existe, mas não tem sinal uniforme.** corr(salto do fim de semana, intradiário da reabertura): SPY **+0,128** (t 4,4), XLE +0,106, XLF +0,090 — mas XLP **−0,252** (t −8,9) e XLK −0,100, que é **reversão**. E o intradiário do SPY em dia de reabertura (+0,015%) é **idêntico** ao dos demais pregões (+0,015%, t 0,57): sem o Δp do poly não há nada na janela. A tática vive inteira do sinal, não do dia.
- **Drift pós-FOMC: o livro de RF nunca roda inteiro.** O intervalo entre FOMCs é de **29 a 40 dias úteis** (mediana 30), então a janela de 50 dias da literatura (Brooks-Katz-Lustig) é truncada pelo FOMC seguinte em **47 de 47** intervalos do calendário entregue — na prática é um livro de ~29 dias com outro nome. O livro de ações (15 dias) nunca trunca. A **direção** do drift não é testável: depende da surpresa do ZQ, que segue sem fonte definida.

**Pendente:**
- **`FOLLOWUP3` (G7) a enviar** ao Paulo. Enquanto não vier, qualquer janela `abertura → fechamento` de TIP e TLT está contaminada — o `adjustment_gap` denuncia, mas não conserta.
- **View 3.1 destravada de dado, travada de parâmetro:** faltam α e β do probit (Estrella-Mishkin / NY Fed — publicados, pendência da própria espec) e o k / janela do β (decisão 3.1, com o agravante medido em 30/07 de que o pico do M4 está em k = −1).
- **Três achados novos para a reunião**, todos em `Dump/analises/Premissa_taticas.md`: a âncora da 1.3 não aparece na amostra; o gap de fim de semana troca de sinal entre setores; o livro de RF do drift é truncado sempre. **Já levados para a `Pauta_reuniao_explicada.md`** (ver "Feito") — o que falta é a reunião decidir.
- `Decisoes_pendentes.md` intocado, como nas últimas sessões.

**Uso de IA:**
- **Modelo:** Claude Code / Opus 5.
- **Contexto consumido:** ~95k tokens (~48% de janela de 200k).
- **Prompt inicial (verbatim):** "resposta do followup 2 chegou"
- **Iterações até aceitar:** 1 — nenhuma rodada de correção do usuário; as três instruções seguintes ("segue por ai", "segue com a 3.1", "segue pras táticas") foram continuação, não correção.
- **Erros da IA:** 1 — afirmou, copiando a declaração do Paulo, que os dois parquets estavam na mesma base de ajuste, e gerou uma primeira versão do relatório com as médias de TIP/TLT contaminadas apresentadas como válidas. Detectado pela própria implausibilidade do número (−1,14% de overnight médio com σ de 0,23%), investigado até a causa (datas de download diferentes, via `git log` dos dois arquivos) e corrigido antes de qualquer commit do relatório.
- **Decisões escaladas:** — (nenhuma nova em `Decisoes_pendentes.md`; 3 decisões de módulo tomadas na sessão e registradas acima, 1 observação sobre módulo do Paulo registrada aqui conforme §2, 1 pedido novo ao Paulo em `Dump/trocas/FOLLOWUP3_Pedido_Paulo_dados.md`).
- **Tags:** —

## 2026-07-31 — Felipe

**Feito:**
- **`Dump/` organizado em 3 subpastas** (9 arquivos, nenhum criado nem apagado): `trocas/` (5 — pedidos e respostas com o Paulo: `FOLLOWUP`, `FOLLOWUP2`, `RESPOSTA`, `RESPOSTA_FOLLOWUP`; mais `Pergunta_Lia_omega_volume.md`), `analises/` (2 saídas de script — `Perfil_defasagem_k.md`, `Sensibilidade_decisoes_1.1_1.2_6.1.md`) e `reuniao/` (2 — `Pauta_reuniao_explicada.md`, `Proposta_4.1_horizontes.md`).
- Movido com `git mv`: o git detectou os 9 como rename, **histórico preservado** em todos.
- **5 referências de path atualizadas** para não quebrar: `--saida` default de `scripts/perfil_defasagem_k.py` e `scripts/sensibilidade_reuniao.py` (agora apontam para `Dump/analises/`), e 3 citações internas nos dois docs de `reuniao/`.
- Commit `e50a35c` no branch `Felipe`; branch empurrada para `origin/Felipe` (estava 17 commits à frente).

**Quebrou / aprendido:**
- Nada quebrou. Um tropeço de processo: o primeiro commit saiu com os renames e os scripts, mas **sem** as edições de path dentro dos dois `.md` de `reuniao/` (o `git mv` deixa a modificação de conteúdo unstaged). Corrigido por `--amend` antes do push — o commit publicado está completo.
- Escolha deliberada: **os 7 `Dump/...` citados em entradas antigas do `LOG.md` não foram reescritos**. É registro histórico e os caminhos valiam na data da entrada; reescrever seria mexer no passado do log.

**Pendente:**
- Nada aberto por esta sessão. Nenhuma decisão nova, nenhuma alteração em `Decisoes_pendentes.md` — sessão puramente organizacional, sem toque em metodologia ou módulo de outro membro.

**Uso de IA:**
- **Modelo:** Claude Code / Opus 5.
- **Contexto consumido:** ~40k tokens (~20% de janela de 200k).
- **Prompt inicial (verbatim):** "da uma organizada no dump, com pastas pra separar os arquivos"
- **Iterações até aceitar:** 1 (agrupamento aceito de primeira; as duas instruções seguintes foram commit e push, não correção).
- **Erros da IA:** 1 — staging incompleto no primeiro commit (edições de conteúdo dos `.md` renomeados ficaram de fora); detectado pelo próprio `git status` e corrigido por amend antes de qualquer push.
- **Decisões escaladas:** —
- **Tags:** —

## 2026-07-30 (sessão 2) — Felipe

**Feito:**
- **Mapa do que dá para avançar enquanto o Paulo roda o `FOLLOWUP2`** apresentado ao usuário em 3 blocos: travado por reunião (1.1/1.2, 6.1, 6.2, 2.1–2.4, 5.6, 4.1), travado por G1/G2 (as 3 táticas sem `Open`; 3.1 e benchmark da 2.2 sem FRED) e **livre agora** (camada de leitura, pacote de sensibilidade para a reunião, perfil de defasagem k, miudezas, alinhamento com a Lia). Escolhido começar pela camada de leitura.
- **`src/poly_loader.py` criado** — a leitura do dado cru do Polymarket não existia: `poly_preprocessing.py` só opera sobre arrays, e os JSONs entregues pelo Paulo (`/prices-history`, um por tokenId) não tinham quem os abrisse. Funções puras: `load_history` (JSON cru → arrays), `to_slots` (timestamp → índice do slot de 12h), `series_by_slot`, `load_pmf` (matriz slots × buckets), `daily_preopen` (regra de alinhamento diário) e `bucket_value` (slug → número).
- **Regra de alinhamento diário decidida pelo Felipe em sessão** (escopo do próprio módulo, categoria 2 do CLAUDE.md §1): o valor do pregão D é o **slot das 12:00 UTC da data D** — 07:00/08:00 em Nova York, o ponto mais recente que fecha ANTES da abertura, sem lookahead por construção. O slot das 00:00 UTC (19:00/20:00 ET do dia anterior) segue disponível na série completa para quem precisar (ex.: gap de fim de semana). Buraco de leitura **não é preenchido** e o join com o calendário de pregão fica no backtest — o loader devolve toda data corrida, inclusive fim de semana e feriado.
- **Nenhuma decisão metodológica entrou no loader:** faixa sem leitura vira **NaN, nunca zero** (6.1 é de quem consome), e `bucket_value` devolve **NaN para bucket aberto** (`8plus`), que é exatamente o que `pmf_mean` já rejeita citando a 11b. O parser lê o valor do **slug de cada arquivo**, nunca de tabela fixa — a grade do CPI varia de 3 a 9 buckets e inverte o sinal em jul/2026.
- **Validado contra o dado real** (`origin/Paulo` @ `90c7574`, extraído para scratchpad via `git archive`, **sem merge**): reproduz exatamente os números da auditoria de ontem — M1 56/56 slots completos com soma 0,978–1,060; M3 524/691 com soma 0,923–1,325; "no cuts" morrendo em 2025-09-17 e "1 cut" em 2025-10-29. Os **17 meses de CPI** parseiam, incluindo os 9 buckets negativos de jul/2026 (−0,7 a +0,1) e os 3 buckets de dez/2024.
- **`tests/test_poly_loader.py`** — 11 testes sintéticos (deriva de segundos, granularidade fina rejeitada, alinhamento de buckets com deriva diferente, NaN de faixa morta, regra das 12:00 UTC, buraco não preenchido, as duas grades de slug, bucket aberto, slug desconhecido). **Suíte inteira verde: 71 testes.**
- **`pytest` e `pyarrow` instalados** no ambiente (o `pyarrow` era pendência declarada ontem; o parquet dos ETFs deixa de estar fechado para mim).
- **`scripts/sensibilidade_reuniao.py` + `Dump/Sensibilidade_decisoes_1.1_1.2_6.1.md`** — varre as opções das decisões 1.2 (balde aberto: truncar / ponto médio / largura inteira), 6.1 (faixa faltante: renormalizar / carregar / só slot completo) e 1.1 (FL, família `p^γ` com γ ∈ {1,0; 1,1; 1,25}) sobre os 17 meses de CPI + M3, e mede o Δ de E_poly contra **σ do próprio sinal no tempo**. **Resultado inverte a urgência da pauta:** quem move a PMF é a **1.2** (Δ/σ até 1,99; > 1 em 4 dos 19 mercados), não a 1.1 (Δ/σ ≤ 0,3 em todo CPI) — mas a 1.1 é decisiva no **binário em p baixa** (recessão: mediana 0,205 → 0,155; 1º decil 0,030 → 0,013). **1.1 e 1.2 travam views diferentes e podem ser decididas separadamente**, ao contrário do que a pauta afirma. A 6.1 é zero em 2025 e material só em 2026 (0,126 pp em mar/2026; 0,184 corte no M3). 6 testes sintéticos.
- **Correção de unidade da view 2.2 (autorizada pelo usuário em sessão):** os mercados entregues são de CPI **mensal** (Nota A do Paulo) e o breakeven é **anual** — a fórmula comparava 0,3% com 2,3% e produzia divergência negativa permanente de ~2 pp, deixando a view comprada em TLT contra TIP por erro de unidade. `cpi_frequencia` vira argumento **obrigatório** (keyword-only) e a anualização `(1+π)^12−1` entra nos **valores dos buckets**, não na média (Jensen). `diagnostics` passa a levar `e_poly` (anual) e `e_poly_declarado` (como veio). 3 testes novos + os 7 antigos atualizados; nota datada na espec `view_2.2_inflacao.md`.
- **`scripts/perfil_defasagem_k.py` + `Dump/Perfil_defasagem_k.md`** — regressão de lags (reusa `views_common.lag_regression`, com as SEs recalculadas no script e `assert` de que o perfil bate com o caminho de produção) nos 3 mercados designados, mais **checagem de lead-lag com lags negativos**, que a regressão sozinha não faz. 4 testes sintéticos com defasagem plantada.
- **`Dump/Proposta_4.1_horizontes.md` + código:** assumi a decisão 4.1 (era o único item que travava o backtest inteiro e não tinha dono; sou dono do bridge prob→Q). Levantamento de em que horizonte cada view devolve Q (2.2 indefinido · 2.3 e B 1 dia · defasadas k dias · Σ/π diários) e proposta de horizonte-alvo H = intervalo de rebalanceamento, com as conversões por tipo de view. **No código:** toda view declara `horizonte_q_dias` no `diagnostics` e `bl_integration.stack_views` **recusa empilhar horizontes diferentes**, citando a 4.1 — antes passava silencioso. Duas perguntas ficam para a reunião (qual é H; qual o prazo de convergência do breakeven na 2.2) e **nenhum valor foi proposto**.
- **`load_cpi_releases` no `poly_loader`** — corrige o erro de ano da fonte (CPI de dez/2025 com divulgação em 2025-01-13) por **regra geral** ("divulgação nunca precede o mês de referência"), não por data cravada, e reordena o arquivo. Validado no CSV real.
- **`Dump/Pergunta_Lia_omega_volume.md`** — o G5 do Paulo está parado esperando a especificação do Ω; pergunta objetiva (volume por dia vs acumulado vs total), mais o fechamento do formato do `diagnostics` (lista do que as views já entregam) e o alinhamento do δ. Inclui um achado que pode servir de régua pronta para ela: **o desvio da soma da PMF em relação a 1 é medida direta de desarranjo do mercado**, disponível slot a slot, sem dado novo.
- **`Dump/` limpo** (por instrução do usuário): removidos os 5 docs superados — todos recuperáveis do histórico (`HEAD:claude_ignore/...` e `origin/Paulo:docs/Pedido_Paulo_dados.md`). A `Pauta_reuniao_explicada.md` **não** foi apagada: tinha **zero commits em qualquer branch** (apagar seria perda definitiva) e é o arquivo que os três documentos novos alimentam — agora está versionada.
- **`Pauta_reuniao_explicada.md` atualizada com o efeito da medição** (as decisões seguem em `Decisoes_pendentes.md` intocado, por instrução vigente): 1.1 e 1.2 **separadas** (travam views diferentes, podem ser decididas em separado); 3.1 marcada como **medida com resultado adverso**; 3.2 promovida de hipótese a caso real; 6.1 ganhou o caso "faixa some e volta" + a medida de quanto muda; 4.1 com dono e proposta. **Bloco 7 novo (4 decisões):** 7.1 qual é o H, 7.2 prazo de convergência do breakeven, 7.3 **as views defasadas sobrevivem?**, 7.4 prazo da 2.2 (1 mês anualizado vs 10 anos). Tabela-resumo refeita.
- **Commitado também o trabalho pendente da sessão da manhã** (`poly_preprocessing` ajustado ao midpoint + testes), que estava sem commit desde ontem. **Worktree limpa ao fim da sessão**; nada empurrado para o `origin` (não foi pedido).
- **13 commits no branch `Felipe`** (+ o desta linha), um por mudança lógica. **Suíte: 85 testes verdes.**

**Quebrou / aprendido:**
- **Achado novo no dado cru (1):** em mercado ainda **vivo**, a API acrescenta um último ponto **fora da grade de 12h** — o "agora" do instante do download. Acontece em 8 arquivos (os 7 buckets do CPI de jul/2026 e o mercado da Câmara 2026), com 3.410 a 4.431 s de desvio, **sempre no último ponto**. O loader descarta esse ponto e mantém erro alto para ponto fora da grade no meio da série (que seria outra granularidade).
- **Achado novo no dado cru (2), que muda a decisão 6.1:** faixa que **some e volta** existe, além da faixa que morre. Nos meses de grade nova os buracos são **internos e não coincidem entre buckets** — mar/2026 tem só **24 de 60** slots com todos os 6 buckets precificados; abr/2026, **42 de 63**. Nos meses de 2025 (5/6 buckets) isso não aparece. A 6.1, como está redigida, cobre só "faixa que morre" — precisa cobrir também "slot com faixa faltando no meio", senão mais da metade dos slots de mar/2026 fica sem regra.
- **Armadilha de nome de arquivo:** existem dois arquivos `M9_midterms_2022_*`; o de 713 linhas é o mercado da **Câmara 2026**, que a busca do Paulo pegou por engano e ele deixou no diretório por transparência (está escrito no F3 dele). Quem varrer por prefixo `M9_` mistura os dois. **M9 segue morto** — a série do Senado 2022 é `{"history":[]}`, a 6.4 não muda.
- Confirmado por caminho independente que o alinhamento por **slot** (e não por timestamp cru) é o que junta as colunas da PMF: as derivas diferem entre buckets do mesmo mercado.
- **Achado que muda o desenho de duas views — a defasagem não aparece no dado.** No episódio eleitoral 2024 a associação Δp↔retorno se concentra no **lag 0** (SPY, XLF, XLK, TLT com os sinais do "Trump trade"); em lag ≥ 1 os coeficientes fortes são compatíveis com acaso (7 de 99 a 5%). **k ≈ 0 ⇒ dispara a decisão 3.2.** No mercado de recessão a regressão mostra lag 1 forte nos 9 ativos, mas a checagem bidirecional revela que **a maior correlação está em k = −1** (−0,52 no SPY) — e a janela de 12h do poly **contém o pregão anterior**, então esse pico é em boa parte mecânico. Conclusão honesta: **nessa granularidade não dá para separar "o poly antecipa" de "os dois leem a mesma notícia na janela sobreposta"** — o que, para efeito de decisão, dá no mesmo: o dado não sustenta ligar a view. Separar exigiria passo intradiário, que só existe nos ~30 dias recentes de mercado vivo. A view C tem 45 observações: amostra curta demais para concluir.
- **A regressão sozinha teria dado a resposta errada.** O perfil de lags do mercado de recessão, lido isolado, parecia um k = 1 de manual (9 de 9 ativos significantes, robusto à correção FL). Só a checagem de lags negativos — que não estava planejada — mostrou que o pico está do outro lado. Aprendizado: **em lead-lag, medir só o lado da tese confirma a tese**.
- **Descasamento de unidade encontrado ao propagar a sensibilidade para o Q:** a espec da 2.2 supunha CPI anual, o mercado entregue é mensal. Não apareceu em nenhuma das duas auditorias anteriores porque as duas leram *o relatório do Paulo* e *o código* separadamente — o erro só existe na junção dos dois. O usuário autorizou resolver na sessão em vez de mandar para a pauta.

**Pendente:**
- Segue aguardando o `FOLLOWUP2` do Paulo (G1–G6); **G1 + G2 continuam sendo o que importa**.
- **Três documentos novos para a reunião**, todos em `Dump/`: `Sensibilidade_decisoes_1.1_1.2_6.1.md`, `Perfil_defasagem_k.md`, `Proposta_4.1_horizontes.md`. Os dois primeiros substituem opinião por número; o terceiro é proposta com dono.
- **`Dump/Pergunta_Lia_omega_volume.md` a enviar** — enquanto ela não responder, o G5 do Paulo fica parado e o formato do `diagnostics` segue em aberto.
- **A 6.1 precisa ser reescrita antes da reunião** para incluir o caso "faixa faltando no meio". Registrado aqui e a levar para a pauta — `Decisoes_pendentes.md` segue intocado por instrução vigente.
- **Item novo para a pauta, saído da correção de unidade:** a 2.2 compara expectativa de **1 mês** com breakeven de **10 anos**; a unidade foi corrigida, o descasamento de PRAZO não (mesma família da decisão 3.3). Anualizar um mês multiplica o ruído por ~12. Amortecer isso é decisão do grupo.
- **A 3.2 deixou de ser hipotética:** o k ≈ 0 medido no episódio eleitoral é exatamente o cenário que ela antecipava. Precisa de decisão (view contemporânea vs sair do v1), agora com número na mesa.
- **4.1 deixou de estar sem dono** (Felipe). Faltam as duas escolhas do grupo: qual é H e qual o prazo de convergência do breakeven da 2.2.
- Decisões de reunião inalteradas: 1.1/1.2 (11), 6.1, 6.2 (ZQ), 2.1–2.4, 5.6, 3.3, 6 (Ω — Lia).

**Uso de IA:**
- **Modelo:** Claude Code / Opus 5.
- **Contexto consumido:** ~85k tokens (leitura dos docs de estado, inspeção do dado do `origin/Paulo`, 4 módulos/scripts novos, 3 documentos de reunião e validações).
- **Prompt inicial (verbatim):** "na ultima sessão escrevemos um followup2 pro paulo. Mas enquanto esperamos esse queria saber que outras coisas podemos ir fazendo. O que esta travado por reuniões e o que com base na primeira e segunda resposta dele podemos mudar, avançar?"
- **Iterações até aceitar:** 1 por entregável (mapa dos 3 blocos, loader, pacote de sensibilidade, correção de unidade, perfil de k, 4.1 e carta para a Lia — todos aceitos na primeira versão). Correções minhas durante a validação, não pedidas pelo usuário: tolerância do slot, ponto "agora" de mercado vivo, coluna σ no pacote de sensibilidade e a checagem de lags negativos.
- **Erros da IA:** nenhum de conteúdo. Três ajustes apanhados pela própria validação: tolerância inicial do slot larga demais (1h → 5 min), ponto fora da grade em mercado vivo não previsto, e — o mais relevante — a **primeira versão do perfil de k media só lags ≥ 0**, o que teria reportado "k = 1" no mercado de recessão como se fosse previsibilidade. Os três só apareceram por rodar contra o dado real.
- **Decisões escaladas:** — (nenhuma em `Decisoes_pendentes.md`, por instrução vigente). Decididas em sessão pelo Felipe, categoria 2: regra de alinhamento diário (slot pré-abertura), correção de unidade da 2.2 (autorizada explicitamente pelo usuário) e assunção da dona da 4.1. Nenhum parâmetro numérico do modelo foi escolhido.
- **Tags:** `[PROMPT-CHAVE]` — dois padrões desta sessão são candidatos: (1) "validar módulo novo contra o dado real do outro branch, sem merge (`git archive` para scratchpad)"; (2) **"transformar decisão de reunião em número antes da reunião"** — varrer as opções em aberto e medir o efeito de cada uma contra o tamanho do sinal, em vez de listar prós e contras. Foi o que inverteu a ordem de urgência da pauta e o que derrubou a tese de defasagem.

## 2026-07-30 — Felipe

**Feito:**
- **Auditoria da segunda entrega do Paulo** (`RESPOSTA_FOLLOWUP_Pedido_Paulo_dados.md`, F1–F10, medida ao vivo em 29/07) **verificada contra o repositório**, não só contra o texto: `git fetch` + `origin/Paulo` @ `90c7574`. Conferi arquivo por arquivo — **todos os counts e datas da tabela do F3 batem**, M9 salvo com `{"history":[]}`, os dois CSVs de calendário existem (FOMC 48 linhas 2022→2027; CPI 15 linhas). Fechado pela entrega: IDs completos dos 9 + buckets; entrega física real (F1 empurrado); `/trades` capado em **20k** (limit 10000 + offset 10000, filtros de tempo ignorados) com **99,8%** das janelas de 12h do M4 tendo BUY e SELL; **a série do `/prices-history` É o midpoint** (medido em 2 mercados vivos, corrige a inferência "último trade"); nenhuma sintaxe de ZQ mensal no yfinance; 17 meses de CPI varridos; granularidade fina (10 min) só nos últimos ~30 dias de mercado vivo ⇒ **teto do backtest histórico = 12h, fechado**.
- **5 achados meus no dado cru, além do que ele reportou:** (1) calendário de CPI só cobre de jan/2025 (o F7 pedia 2022–2025; FOMC cobre); (2) o typo de dez/2025 põe a linha **fora de ordem** no CSV e o valor certo é 2026-01-13 — confirmado pela série do próprio mercado, que termina nessa data; (3) **dois buracos de CPI não sinalizados** (jan/2026 e fev/2026, além do abr/2025 que ele sinalizou); (4) a nota do F3 "todos os buckets com a mesma janela do primário" está **errada para o M3** — `no cuts` morre em 2025-09-17 (524 pts), `1 cut` em 2025-10-29 (607), os demais vão a 2025-12-10 (690/691); M1 está certo (56 em todos); (5) **a PMF não soma 1** — alinhando ao slot de 12h (os timestamps dos buckets diferem em segundos entre arquivos), M1 fecha 56/56 slots completos e M3 524/691, com somas de **0,978–1,060** (M1) e **0,923–1,325** (M3).
- **`src/poly_preprocessing.py` ajustado ao midpoint (F5):** `midpoint_price(bid, ask)` **deletada** — não existe bid/ask histórico e a série já vem em midpoint; nada mais a chamava. `binary_prob_series` passa a receber as séries dos dois tokenIds, com `p_no=None` cobrindo a entrega atual (só o token Yes dos 9). Docstrings passam a registrar o medido: série = midpoint, **spread não observável** (haircut de custo vira premissa, não estimativa) e as somas reais das PMFs. Testes atualizados (`test_midpoint` removido, `test_binary_prob_series` reescrito com os três casos: par, só-Yes, shapes desalinhados). **10 arquivos de teste rodados, todos verdes.**
- **`claude_ignore/Pauta_reuniao_explicada.md` atualizada:** §5.5 deixou de ser escolha de três — a série já é o midpoint (a condição das 5 views está atendida por outro caminho) e a opção (b) morreu pelo cap do `/trades`; sobra decidir **custo de transação**. §3.1 (k) ganhou as duas notícias boas (midpoint ⇒ k não é artefato de série stale; 12h ⇒ dois pontos/dia bastam). §1.2 ganhou a grade variável do CPI (3→4→5→6→9 buckets, deslocamento em mar/2026, **inversão de sinal em jul/2026**). §4.2 registrou que veio volume **total**, não diário (insumo do Ω da Lia). **Bloco 6 novo:** 6.1 PMF não soma 1 + faixa que morre, 6.2 fonte do ZQ, 6.3 CPI só de 2025 + 3 buracos + typo, 6.4 robustness de 2022 morto. Corrigida também a nota do topo: o `Decisoes_pendentes.md` curto é **decisão do grupo**, não perda de merge (estava escrito errado desde 27/07).
- **Criado `claude_ignore/FOLLOWUP2_Pedido_Paulo_dados.md`** (G1–G6): G1 `Open` diário dos 9 ETFs e G2 as 3 séries do FRED em arquivo como prioridade máxima — **ambos já medidos por ele em 27/07 e nunca salvos**, mesmo padrão do F1; G3 token No de 2 binários, G4 os 3 buracos de CPI, G5 volume no tempo (com aviso de alinhar com a Lia antes, a especificação do Ω é dela), G6 CPI 2022–2024 marcado **não faça ainda** (depende da reunião). Inclui seção **"o que NÃO precisa mais ser feito"** (ZQ = decisão do grupo, M9 morto, `/trades` encerrado, séries já conferidas) para não gastar sessão dele em retrabalho.
- **`Decisoes_pendentes.md` NÃO tocado** (mesma instrução vigente desde 27/07).

**Quebrou / aprendido:**
- Nada quebrou. A suíte inteira (10 arquivos) roda verde após a mudança do `poly_preprocessing`.
- **Não deu para abrir o `etf_prices_daily.parquet`:** `pyarrow`/`fastparquet` não estão no ambiente. A cobertura foi verificada pelo `data/README.md` dele (2003-12-05 → 2026-07-08, 51.129 linhas, 9 tickers) — foi ali que apareceu o **G1**: o parquet tem só `preco_ajustado`, sem `Open`. Instalar `pyarrow` é pendência minha, não mudança de formato a pedir.
- **Padrão que se repetiu pela segunda vez:** dado **medido** não é dado **entregue**. Na primeira entrega faltou o push; nesta, FRED e `Open` foram medidos em 27/07, reportados como ✅ e nunca salvos em arquivo. Aprendizado para as ordens de serviço: "confirmar que a fonte existe" e "salvar o arquivo" têm que ser **itens numerados separados**, senão o ✅ do primeiro é lido como conclusão do segundo.
- **Auditar o dado cru rende achado que a leitura do relatório não rende:** as 5 observações novas (PMF não somar 1, buckets com janelas diferentes, os dois meses faltantes) só apareceram porque abri os JSONs e somei, não porque li a tabela dele. O relatório estava honesto — só incompleto.

**Pendente:**
- Aguardando o Paulo rodar o `FOLLOWUP2_Pedido_Paulo_dados.md`. **G1 + G2 são o que importa** — sem eles as 3 táticas e as views 3.1/2.2 são código pronto sem insumo.
- **Nenhum dos itens do G1–G6 fecha decisão** — todos destravam código. As decisões (1.1/1.2 viés + balde aberto, 6.1 normalização da PMF, 6.2 fonte do ZQ, custo de transação, τ e δ) já têm o que precisam para serem tomadas e dependem só da reunião. **A única decisão que o dado fecharia é o k (3.1), e esse dado já chegou** — está travada em 1.1/1.2, não no Paulo.
- **Não é pergunta para o Paulo, é instrução pós-reunião:** a regra de alinhamento do dataset de backtest (qual dos dois pontos de 12h vale como "o dia", fim de semana, fuso) é decisão metodológica minha/do grupo. Pedir agora convida ele a decidir sozinho — que foi o que deu errado no primeiro pedido.
- Questões novas estacionadas em `Pauta_reuniao_explicada.md` bloco 6 (6.1–6.4), fora do `Decisoes_pendentes.md` por instrução vigente.
- Decisões de reunião inalteradas: 11 (favorite-longshot + bucket aberto), entrada das views B/C/E/G, entrada e orçamentos da camada tática, τ e δ, 12 (critério do k), k≈0 na 2.4, horizonte 3.1/B, reconciliação do horizonte do Q (⚠️ sem dono), 6 (Ω — Lia).
- Observação para o grupo, sem ação: a dessincronização da numeração do `Decisoes_pendentes.md` entre branches segue como estava.

**Uso de IA:**
- **Modelo:** Claude Code / Opus 5.
- **Contexto consumido:** ~85k tokens (estimativa; leitura da entrega + docs, verificação por `git ls-tree`/`git show` sobre o `origin/Paulo`, scripts de conferência das PMFs, e redação).
- **Prompt inicial (verbatim):** "chegou a resposta do followup do paulo. também chegou veio com: Duas ressalvas honestas do enunciado: não achei mercado
  realmente fino com book (baixo volume devolve book vazio),
  então o F5 ficou entre dois mercados líquidos; e o release
  de dez/2025 tem um typo na própria fonte do Polymarket
  ("2025" em vez de 2026) — mantido cru e sinalizado."
- **Iterações até aceitar:** 1 por entregável (auditoria, ajuste do `poly_preprocessing`, atualização da pauta, `FOLLOWUP2` — os quatro aceitos na primeira versão), mais 2 rodadas de esclarecimento pedidas pelo usuário ("o que é a opção b" e "que proveito você tira dessas informações / o que fecha decisão").
- **Erros da IA:** nenhum. As afirmações sobre o que a entrega fechou foram checadas contra os arquivos do `origin/Paulo` (counts, datas, somas de PMF) antes de entrarem no relatório — as 5 divergências reportadas são achados no dado, não suposições. Limitação declarada: o parquet não pôde ser aberto localmente (sem `pyarrow`).
- **Decisões escaladas:** — (nenhuma em `Decisoes_pendentes.md`, por instrução vigente; as novas foram para `claude_ignore/Pauta_reuniao_explicada.md` bloco 6).
- **Tags:** `[PROMPT-CHAVE]` — terceira volta do padrão "auditar entrega recebida contra o pedido e gerar follow-up com formato fechado", agora com o diferencial de **auditar o dado cru** (abrir os JSONs e recomputar) em vez de só conferir o repositório. Foi o que produziu os 5 achados que o relatório não trazia.

## 2026-07-28 — Felipe

**Feito:**
- **Auditoria da resposta do Paulo** (`claude_ignore/RESPOSTA_Pedido_Paulo_dados.md`, medida ao vivo em 27/07 com VPN) contra o `Pedido_Paulo_dados.md`. Fechado pela resposta: **não existe bid/ask histórico no CLOB** (medido: `/orderbook-history` volta vazio, `/book`/`/midpoint`/`/spread` são só tempo real e dão 404 em mercado resolvido); existência/datas/volume/critério dos 9 mercados; Nota A = **bucket** (PMF confirmada para a 2.2, com buckets abertos nos extremos); Nota B = resolução técnica pura **não existe isolada**, só a *two-pronged* (NBER **ou** PIB do BEA); Nota C = **terminal** (a receita `E = Σ pᵢ·xᵢ` vale); FRED `T10YIE`/`DGS10`/`DTB3` via CSV público **sem API key**; `Open` diário confirmado para os 9 ETFs; Polymarket exige **VPN** nesta rede.
- **10 pendências identificadas** e verificadas contra o repositório: (1) o trabalho da sessão dele **não foi empurrado** — `origin/Paulo` ainda está em `48cb12e` (ETFs), sem `scripts/` nem `data/raw/clob_exploracao/`; (2) nenhum identificador (`conditionId`/`tokenId`/slug) na tabela dos 9; (3) séries cruas dos 9 não entregues (só o mercado-âncora citado); (4) `/trades` **não dimensionado** — profundidade, paginação e densidade de lados, que é o que decide a viabilidade da opção (b) da decisão escalada; (5) pergunta 1 da seção 1 (que preço a série entrega) **inferida, não medida**; (6) contrato ZQ específico ⏳ (trava 2.3, B e drift pós-FOMC); (7) calendários FOMC/CPI ⏳ (travam as 3 táticas); (8) varredura de ~18 meses de CPI não feita (só jul/2025 como amostra); (9) coluna "dias sem trade" descrita e não contada em M2/M5/M6/M8; (10) granularidade em mercado **vivo** não testada (só resolvido, que trava em 12h).
- **Criado `claude_ignore/FOLLOWUP_Pedido_Paulo_dados.md`** — segunda ordem de serviço para o Claude do Paulo, com as 10 pendências como F1–F10 em ordem de prioridade (F1–F3 = entrega física, sem a qual nada chega do lado do Felipe), cada uma com formato de devolução fechado. Inclui a medida decisiva do F4 (contagem de janelas de 12h com BUY **e** SELL, que diz se o proxy de midpoint é reconstruível) e repete as regras do pedido original (`?` honesto, não decidir, não mapear mercado→ETF, dado cru sem tratamento).
- **`Pauta_reuniao_explicada.md`:** adicionadas §5.5 (sem bid/ask histórico — série única vs reconstruir de `/trades` vs adiar) e §5.6 (recessão só existe com o critério NBER embutido), mais as duas linhas no resumo em uma tela.
- **Nenhum código tocado. `Decisoes_pendentes.md` NÃO tocado** (mesma instrução da sessão de 27/07).

**Quebrou / aprendido:**
- Nada quebrou (sessão sem código).
- **Padrão observado na resposta do Paulo:** o relatório é honesto e bem medido, mas a **entrega física ficou fora** — o texto descreve arquivos que não existem no repositório compartilhado. Aprendizado para as próximas ordens de serviço: pedir o **push com hash de commit** como item numerado e prioritário, não como parágrafo final ("entrega física"). Relatório sem push é relatório sem dado.
- **Escalar decisão sem medir o custo de uma das opções trava a reunião:** ele escalou "(a) série única vs (b) proxy de `/trades`" sem dimensionar o `/trades`. O grupo não tem como escolher (b) sem saber se ela é viável. Vira o F4 do follow-up.

**Pendente:**
- Aguardando o Paulo rodar o `FOLLOWUP_Pedido_Paulo_dados.md` (F1–F10). Sem F1–F3 nenhum módulo do Felipe roda com dado real.
- **Duas questões novas de reunião, sem registro em `Decisoes_pendentes.md`** (arquivo intocado por instrução): §5.5 (bid/ask — condição de fechamento das views 2.4/3.1/C/E/G **falhou**; as duas views trazem a condição escrita em `src/view_2_4_eleitoral.py:3` e `src/view_3_1_recessao.py:4`) e §5.6 (critério da recessão contamina a 3.1). Estacionadas em `Pauta_reuniao_explicada.md`.
- Consequência direta: `src/poly_preprocessing.py` (`midpoint_price`, `binary_prob_series`) está sem insumo até a §5.5 fechar — a assinatura atual pede `bid` e `ask` separados.
- M9 (midterms 2022) sem série no `/prices-history`: o robustness de 2022 da view 2.4 cai, salvo se o `/trades` cobrir 2022 (perguntado no F4).
- Decisões de reunião inalteradas: 11 (favorite-longshot + bucket aberto), entrada das views B/C/E/G, entrada e orçamentos da camada tática, τ e δ, 12 (critério do k), k≈0 na 2.4, horizonte 3.1/B, reconciliação do horizonte do Q (⚠️ sem dono), 6 (Ω — Lia).
- Observação para o grupo (sem ação): a numeração do `Decisoes_pendentes.md` está **dessincronizada entre branches** — o `origin/Paulo` tem 7/8/9 com conteúdo diferente do `Felipe`/`main`, e as decisões 9–12 citadas nos docs e nos `# TODO(DECISAO-N)` do `src/` não existem em nenhuma versão vigente do arquivo.

**Uso de IA:**
- **Modelo:** Claude Code / Opus 5.
- **Contexto consumido:** ~60k tokens (estimativa; sessão sem código, dominada por leitura de docs, `git ls-tree` entre branches e redação).
- **Prompt inicial (verbatim):** "enviei o pedidos pro paulo e ele retornou isso aqui: c:\Users\felip\Documents\Pessoal\Desafio-Quant-Itau\claude_ignore\RESPOSTA_Pedido_Paulo_dados.md. O que falta e foi fechado com a resposta? Ele falou que a sessão travou então pode ter faltado algo"
- **Iterações até aceitar:** 1 por entregável (auditoria fechado × falta e o `FOLLOWUP_Pedido_Paulo_dados.md`, ambos aceitos na primeira versão).
- **Erros da IA:** nenhum. As afirmações sobre o que falta foram checadas contra o repositório (`git ls-tree origin/Paulo`) antes de entrar no follow-up, e não por leitura só do texto da resposta.
- **Decisões escaladas:** — (nenhuma em `Decisoes_pendentes.md`, por instrução vigente; as duas novas foram para `claude_ignore/Pauta_reuniao_explicada.md` §5.5 e §5.6).
- **Tags:** `[PROMPT-CHAVE]` — "auditar entrega recebida contra o pedido, checando as afirmações contra o repositório, e gerar follow-up com formato fechado" é candidato ao teste de reprodutibilidade (é a segunda volta do mesmo padrão da sessão de 27/07, agora com a verificação por `git` como diferencial).

## 2026-07-27 — Felipe

**Feito:**
- **Análise da resposta do Paulo** (`prompt.txt` — catálogo de 30 mercados do Polymarket com volume, recorrência e mapeamento mercado→ETF) contra o que o `Para_Paulo_e_Lia.md` pediu. Diagnóstico: das 5 dimensões pedidas por mercado (existe? desde quando? volume? critério de resolução? bid/ask?), a resposta cobre só volume — e estimado, não medido (ele mesmo registra isso no fim da mensagem). Não menciona bid/ask histórico (condição crítica), critério de resolução, cobertura histórica nem estrutura de buckets. Ausentes do catálogo: presidencial 2024 (view 2.4), geopolítica Irã/Rússia-Ucrânia (view C), trajetória do Fed (view B) e OBBB (view G primário). Flag: o item "CPI mensal vs consensus" dele é **binário**, e a view 2.2 precisa de **PMF de buckets**.
- **Criado `claude_ignore/Pedido_Paulo_dados.md`** — ordem de serviço operacional para o Claude do Paulo, substituindo o briefing explicativo como documento de trabalho. Diferenças de desenho: seção "o que NÃO é" no topo (o formato anterior induziu catálogo + mapeamento ETF); bid/ask isolado como tarefa 1 com pedido de **colar 5 linhas do JSON cru** em vez de responder pela doc; escopo travado em 9 mercados; `?` declarado resposta válida e estimativa declarada inválida; formato de devolução fechado (blocos + tabelas de colunas fixas); ordem de prioridade explícita. Notas A/B/C embutidas: formato do CPI (bucket vs vs-consensus), critério de resolução da recessão (técnica GDP vs NBER), e terminal vs one-touch nos mercados de bucket.
- **Criado `claude_ignore/Pauta_reuniao_explicada.md`** — as 14 decisões de reunião em linguagem leiga, agrupadas por quanto travam (bloco 1 trava tudo → bloco 5 novas), cada uma com o que é / por que importa / opções / o que acontece se não decidir, + tabela-resumo de uma tela.
- **Nenhum código tocado. `Decisoes_pendentes.md` NÃO tocado** (ver "Quebrou / aprendido").

**Quebrou / aprendido:**
- **Erro de diagnóstico meu:** ao ler o `Decisoes_pendentes.md` no início da sessão, encontrei-o com 79 linhas e sem as decisões 9–12 (com 3/4/5/8 marcadas como abertas), comparei com a versão de 181 linhas do commit `7b9d036` e classifiquei como regressão acidental do merge `b1d31bf`. Propus restaurar via `git checkout 7b9d036 -- Decisoes_pendentes.md`. **O usuário informou que o arquivo está nesse estado por decisão do grupo** — não é acidente, e nada deve ser restaurado. Aprendizado: diferença entre branches num arquivo compartilhado não é evidência de acidente; a explicação "o grupo decidiu" tem precedência sobre a reconstrução por git e deve ser perguntada antes de ser tratada como bug.
- Consequência prática registrada, sem ação: o código em `src/` referencia `# TODO(DECISAO-11)`, cuja descrição não está na versão vigente do arquivo. Fica como observação para o grupo, não como problema a corrigir.
- Sobre a resposta do Paulo: um briefing explicativo (metodologia → dado necessário) faz o executor inferir a tarefa e entregar outra coisa. Pedido de levantamento precisa de formato de devolução fechado e de uma lista explícita do que não fazer.

**Pendente:**
- Aguardando o Paulo rodar o `Pedido_Paulo_dados.md` e devolver: bloco bid/ask, tabela dos 9 mercados, notas A/B/C, fontes externas, bloqueios. Prioridade 1 é bid/ask — trava as views 2.4/3.1/C/E/G e a decisão 9.
- **4 questões novas, saídas do catálogo do Paulo, sem registro em `Decisoes_pendentes.md`** (por instrução explícita do usuário de não tocar o arquivo). Ficam estacionadas em `Pauta_reuniao_explicada.md` §5: (a) o mapeamento mercado→ETF dele é heurística de priorização ou proposta de P? — hoje P sai de β; (b) os ~20 mercados novos do catálogo entram como views no v1? — recomendação: não; (c) WTI/gás natural como benchmark externo da view C, substituindo o poly-defasado — ⚠️ checar antes se commodity resolve por one-touch; (d) shutdown volta pra view G? — foi excluído por falta de efeito documentado em equities; volume alto não é argumento de que move preço de ação.
- Decisões de reunião inalteradas: 11 (🔴 favorite-longshot + bucket aberto — trava toda view com dado real), entrada das views B/C/E/G, entrada e orçamentos da camada tática, τ e δ (δ a alinhar com a Lia), 12 (critério do k), k≈0 na 2.4, horizonte 3.1/B, reconciliação do horizonte do Q (⚠️ sem dono), 6 (Ω — Lia).
- Distribuição combinada dos documentos: `Pedido_Paulo_dados.md` → Claude do Paulo; `Para_Paulo_e_Lia.md` → Paulo e Lia pessoas (carrega os itens de engenharia do backtest que o Pedido não cobre: marcação diária contínua, snapshots de fim de semana, conversão ZQ→bps).

**Uso de IA:**
- **Modelo:** Claude Code / Opus 5.
- **Contexto consumido:** ~75k tokens (estimativa; sessão sem código, dominada por leitura de docs e git).
- **Prompt inicial (verbatim):** "leia o c:\Users\felip\Documents\Pessoal\Desafio-Quant-Itau\prompt.txt. Essa foi uma mensagem que o paulo mandou no grupo com o mapeamento dos mercados do polymerket. leia o c:\Users\felip\Documents\Pessoal\Desafio-Quant-Itau\claude_ignore\Para_Paulo_e_Lia.md e me fale o que ele responde, o que precisamos decidir dele"
- **Iterações até aceitar:** 1 por entregável (análise, `Pedido_Paulo_dados.md`, `Pauta_reuniao_explicada.md` — os três aceitos na primeira versão), mais 1 rodada de esclarecimento ("não entendi o que está pendente") e 1 proposta rejeitada (restaurar o `Decisoes_pendentes.md`).
- **Erros da IA:** 1 — classifiquei o estado do `Decisoes_pendentes.md` como regressão acidental de merge quando é decisão do grupo; propus restaurar de commit anterior. Nenhuma edição chegou a ser feita (a regra CLAUDE.md §6 exige instrução humana para mexer nesse arquivo, então a proposta parou em pergunta). Nenhuma alucinação de dado ou de código.
- **Decisões escaladas:** — (nenhuma registrada em `Decisoes_pendentes.md`, por instrução explícita do usuário; as 4 questões novas ficaram em `claude_ignore/Pauta_reuniao_explicada.md` §5).
- **Tags:** `[PROMPT-CHAVE]` — o padrão "confrontar entrega recebida contra o que foi pedido → gerar ordem de serviço com formato de devolução fechado" é candidato ao teste de reprodutibilidade.

## 2026-07-14 — Felipe

**Feito:**
- Criado `Para_Paulo_e_Lia.md` (raiz): briefing consolidado para os outros donos. Parte 1 = como funcionam TODAS as views (2.2/2.3/2.4/3.1 fechadas + candidatas B/C/E/G) e as 3 táticas reformuladas, com os mercados do Polymarket e dados que cada uma exige (inclui colinha-tabela de dados para o Paulo). Parte 2 = pendências deles (fonte: `pauta_reuniao_outros.md`): condição crítica bid/ask no CLOB, cobertura de mercados, fontes FRED/ZQ/probit, requisitos do backtest (Paulo); decisão 6, validação do `diagnostics`, nota Ω↔tática, SWZ no relatório (Lia); decisão 11a/11b (calibração); avisos de merge.
- **Decisão 6 sincronizada do branch da Lia:** incorporado ao `Decisoes_pendentes.md` o bloco de contexto que a Lia registrou em `Decisoes_pendentes_LIA.md` (08/07/2026) — delegação da decisão à Lia + protocolo de calibração proposto (baseline He-Litterman escalado por confiança c; estrutura multiplicativa com volume como veto; parâmetros por teste de monotonicidade no histórico) + dependência de volume do poly (confirmar com Paulo). Status da 6: 🔴 → 🟡 (segue ABERTA — nada fechado; o resto do arquivo da Lia é fork defasado, nada mais era novo).
- Nenhum código tocado; nenhuma decisão fechada.

**Quebrou / aprendido:**
- `Decisoes_pendentes_LIA.md` é um fork antigo do arquivo principal (anterior ao fechamento das decisões 1/3/4/5/8 e sem as 9–12) — só a seção 6 tinha conteúdo novo. Consolidar branches de decisões exige diff manual, não substituição.

**Pendente:**
- Inalterado (decisões 6 — agora 🟡 —, 11, 12; entrada B/C/E/G e da camada tática; condições de dado do Paulo; τ/δ). O briefing só consolida — as fontes da verdade seguem `Decisoes_pendentes.md` e os docs de views/táticas.
- ~~`pauta_reuniao_outros.md` e `Para_Paulo_e_Lia.md` ainda citam a decisão 6 como 🔴~~ — atualizados na mesma sessão (6 → 🟡, delegação + protocolo + dependência de volume do poly referenciados; item de volume adicionado como dependência ao Paulo).
- ~~Destino do `Decisoes_pendentes_LIA.md`~~ — arquivo removido pelo Felipe na mesma sessão (conteúdo já incorporado).

**Uso de IA:**
- **Modelo:** Claude Code / Fable 5.
- **Contexto consumido:** ~120k tokens (~12% de janela de 1M; sessão passou por sumarização de contexto).
- **Prompt inicial (verbatim):** "Passe por todas as Views que montamos e decisões que fizemos quero que você monte um arquivo para a lia e o paulo. O arquivo deve ter duas partes: Informações impotantes sobre TODAS as views e mercados quer precisamos usar (eles precisarão saber como funciona as views, o que elas precisam para poder levantar os dados do polymarket). A segunda parte é com as pendencias(decisões que eles precisam fazer) que eu não entro. use principalmente c:\Users\felip\Documents\Pessoal\Desafio-Quant-Itau\pauta_reuniao_outros.md como fonte para essa parte. Sea completo."
- **Iterações até aceitar:** 1 em todas as entregas (briefing `Para_Paulo_e_Lia.md`, sincronização da decisão 6 do branch da Lia, atualização de status na pauta/briefing — nenhuma rodada de correção).
- **Erros da IA:** nenhum do modelo (2 Edits falharam por perda de estado de arquivo no harness após a sumarização de contexto — reaplicados após releitura, sem mudança de conteúdo).
- **Decisões escaladas:** — (nenhuma fechada; decisão 6 apenas sincronizada 🔴→🟡 com registro da Lia, segue aberta).
- **Tags:** —

## 2026-07-11 (sessão 3) — Felipe

**Feito:**
- Abertura: confirmado que views + integração já estavam prontas (sessão 2); bateria completa re-executada — 48 testes OK.
- **Dono do módulo da camada tática reformulada: Felipe** (decisão do Felipe em sessão — a camada não volta à Lia). Registrado na decisão 10 (`Decisoes_pendentes.md`) e na tabela de propriedade do `CLAUDE.md`.
- **Interface da camada tática fechada em sessão (Felipe, 3 escolhas):** (i) contrato de CHAMADA DIÁRIA `build_overlay(insumos do dia) → OverlayResult(dw, diagnostics) | None` — `dw` (n,) de pesos EXTRAS alinhado a `assets`, mesma unidade de w; `None` = dormente (não é falha); janelas são lógica interna da tática; (ii) layout espelho das views — um módulo por tática + `src/taticas_common.py`; (iii) soma `w_final = w_bl + Σ dw` em `taticas_common.apply_overlays` (`bl_integration.py` intocado — BL fica limpa, camada por cima).
- **3 táticas candidatas implementadas** (código pronto; **entrada na carteira e orçamentos seguem pendentes de reunião** — mesmo precedente das views B/C/E/G, docstrings marcam o status):
  - **1.3 prêmio de anúncios** (`src/tatica_premio_anuncios.py`): `dw[SPY] = orcamento_max × H(p)/H_max` no dia do anúncio (FOMC+CPI), entropia da PMF de D−1 (sem lookahead) via pré-processamento da decisão 9 (stub FL falha alto — 11a bloqueia; 11b NÃO bloqueia: entropia não usa valores de bucket). Sempre ligado, modulado.
  - **Drift pós-FOMC** (`src/tatica_drift_pos_fomc.py`): dois livros, `direção = −sign(surpresa_bps)`; SPY dias 1..janela_acoes, TLT dias 1..janela_rf truncado no dia anterior ao FOMC seguinte; surpresa zero/dia 0/sem evento → dormente. Janelas da literatura (15/50) entram como ARGUMENTO (confirmação de reunião pendente).
  - **Gap de fim de semana** (`src/tatica_gap_fds.py`): `dw = λ × Σ β_view × Δp_fds` — β reusados das views designadas ativas (tática não estima nada); sinais somam; lista vazia → dormente. Δp sobre a mesma série pré-processada da view (quem monta é o backtest).
- Testes: `tests/test_taticas.py` — **13 testes OK** (contrato/soma, entropia com caso conhecido, direção dovish/hawkish, janelas e truncagem, caso conhecido do gap, dormências, falha alta do stub 11a). Total do projeto: 61.
- **Mapa "o que falta" apresentado** (fechamento da sessão): todo o código escrevível sem dado real existe; falta só o **backtest** (dá para esqueletar com dado sintético); decisões abertas 6/11/12 + pauta de reunião (entrada B/C/E/G, entrada+orçamentos da tática, horizonte 3.1/B, k≈0, τ/δ) + dependências Paulo/Lia. Gotcha sem dono destacado: **reconciliação do Q acumulado (k dias) com Σ/π diários** — trava o backtest misturar views defasadas com as diárias.

**Quebrou / aprendido:**
- Nada quebrou (testes passaram de primeira).

**Pendente:**
- **Reunião (camada tática):** entrada da camada na carteira; orçamentos (`orcamento_max`, `orcamento_acoes`/`orcamento_rf` — por livro ou comum —, `λ`); janelas finais (15/50); fonte da expectativa do drift (ZQ vs E_poly); micro-surpresas (posição cheia por sinal); desmonte do gap em k dias; precedência tilt × rebalance no mesmo dia.
- **Paulo (backtest):** marcação diária contínua das posições táticas (o drift cobre boa parte do ano); calendário de releases do CPI (dado novo); preço de ABERTURA de segunda dos ETFs; snapshots de fim de semana do poly.
- **Lia:** nota de interação Ω ↔ camada tática (incerteza entra com sinais opostos nos dois módulos; três módulos leem o calendário FOMC).
- Anteriores seguem: decisões 6, 11, 12; entrada das views B/C/E/G; condições de dado do Paulo; τ/δ reais.

**Uso de IA:**
- **Modelo:** Claude Code / Fable 5.
- **Contexto consumido:** ~60k tokens (~6% de janela de 1M).
- **Prompt inicial (verbatim):** "montei as views do Black litterman, precisa montar o integração agora né?"
- **Iterações até aceitar:** 1 (levantamento das pendências pré-código aceito; interface fechada pelo Felipe em 3 escolhas estruturadas; código das 3 táticas aceito sem rodada de correção).
- **Erros da IA:** nenhum.
- **Decisões escaladas:** dono do módulo tático e interface da camada fechados pelo Felipe em sessão (registrados na decisão 10, não numerados); nenhuma decisão numerada fechada.
- **Tags:** —

## 2026-07-11 (sessão 2) — Felipe

**Feito:**
- **Interface das views fechada em sessão (Felipe, 3 escolhas):** entrada livre por view, saída uniforme `build_view(...) → ViewResult | None` — (i) view desativada retorna `None` (a integração não empilha); (ii) `ViewResult(P, Q, diagnostics)` com `diagnostics` dict livre para o Ω da Lia (formato não travado — decisão 6 aberta; **a confirmar com a Lia**, mesmo modelo do "a confirmar" do `bl_optimizer.py`); (iii) um módulo por view + `src/views_common.py` com o contrato. Convenções: `P` alinhado a `assets` com Σ|P| = 2; `Q` em fração decimal.
- **View 2.2 Inflação implementada** (`src/view_2_2_inflacao.py`): cascata completa da espec (PMF → fallback binário via normal deslocada com `scipy.stats.norm.ppf` → `None`); `Q = duration × (E_poly − breakeven_10a)`, `P = +1 TIP/−1 TLT`; duration e breakeven como argumentos (nada hardcoded); sem `fl_correction` decidida (decisão 11a) a view falha alto, e `bucket_values` com bucket aberto não resolvido (NaN, 11b) é rejeitado. 7 testes sintéticos (`tests/test_view_2_2_inflacao.py`).
- **Regra nova (por instrução do Felipe): a 2.2 é o template estrutural das demais views** — registrado no mapa de camadas (`Informações_uteis/Black-Litterman_com_Polymarket.md`, seção da camada 1).
- **View 2.3 Fed implementada** (`src/view_2_3_fed.py`) no mesmo molde: `estimate_betas` (OLS event-study com intercepto, retorno vs surpresa Kuttner — janela/frequência são decisão humana, entram como dado), `P_from_betas` determinístico (`P[i] = 2·(β_i−β_SPY)/Σ|β_j−β_SPY|`, P[SPY]=0, Σ|P|=2, rejeita βs sem dispersão), `Q = surpresa · ΣP·β`; cascata PMF → binário (`E_poly = p × Δtaxa do evento`, Δ como argumento sem default de sinal) → `None`; `E_FF` entra pronto em bps (extração do ZQ fica a montante). 7 testes (`tests/test_view_2_3_fed.py`), incluindo o **sanity check de sinal obrigatório do item 6 da espec** com os números do exemplo (surpresa −10bp → XLK no lado long: P[XLK]<0 e Q<0).
- **Consolidação na decisão 9:** a média de PMF com pré-processamento (normaliza → favorite-longshot → Σp·x) era idêntica nas 2.2/2.3 → virou `poly_preprocessing.pmf_mean` (com teste); a 2.2 foi ajustada para usá-la.
- **Views 2.4 Eleitoral e 3.1 Recessão implementadas** (`src/view_2_4_eleitoral.py`, `src/view_3_1_recessao.py`) no mesmo molde, por instrução do Felipe ("mesma hierarquia e estrutura"):
  - Matemática compartilhada movida para `views_common.py`: `P_from_betas` (era da 2.3; mesma construção nas 2.3/2.4/3.1) + maquinaria de defasagem da 2.4 (`lag_regression` — regressão de lags distribuídos, devolve o perfil completo; `full_absorption_beta` — soma dos coeficientes 0…k), reusada pela 3.1.
  - `poly_preprocessing.binary_prob_series` (decisão 9): midpoint de cada lado → normaliza o par → favorite-longshot; construída UMA vez a montante e usada tanto na regressão do β quanto no `build_view` (é o que faz o β absorver a parte linear da correção FL — espec 2.4 item 2b).
  - **2.4:** `Q = (ΣP·β) × (p_t − p_{t−k})`, benchmark = poly defasado; **k ≈ 0 falha alto** (`NotImplementedError` — fallback contemporâneo vs sair do v1 é pendência de reunião); desligamento antes do 1º tick de resolução e "dias sem trade" documentados como responsabilidade do backtest; `horizonte_q_dias = k` nos diagnostics (pendência transversal Q acumulado × Σ/π diários).
  - **3.1:** `Q = (ΣP·β) × (p_poly − p_curva)`; `p_curve_probit` = Φ(α + β·spread) com coeficientes publicados **como argumento** (referência exata do NY Fed = pendência, não inventada em código); sem curva com view ativa → falha alto; sanity check de sinal obrigatório (espec item 6) virou teste com os números do exemplo (divergência +0.15 → long defensivos/TLT, short XLK, Q > 0).
  - Teste com dado real segue bloqueado pelas condições do Paulo (bid/ask histórico; mercados de CPI/FOMC/recessão/presidencial no CLOB).
- **Views candidatas B/C/E/G implementadas por instrução do Felipe** ("monte as views BCEG… quero ter tudo feito") — **registro importante: o código existe, mas a ENTRADA delas na carteira segue pendente de reunião** (docstrings de todos os módulos marcam o status; implementar não fecha a decisão do rodapé de `Decisoes_pendentes.md`):
  - C/E/G são matematicamente idênticas à 2.4 (só muda o mercado designado) → o corpo virou `views_common.lagged_poly_view` e a 2.4 passou a delegar; `view_C_geopolitica_energia.py`, `view_E_tarifas.py` e `view_G_fiscal.py` são módulos finos (docstring com específicos da espec + delegação). Sanity checks de sinal obrigatórios (item 7 de cada espec) viraram testes com os números dos exemplos.
  - **B** (`view_B_trajetoria_fed.py`) espelha a 2.3: `surpresa_caminho = E_poly[taxa_fim_de_ano] − E_ZQdez` (nível em bps), β/P **reusados da 2.3** (premissa da espec, confirmação de reunião pendente), cascata PMF → binário (`E_poly = taxa_atual + p·(−25bp)`) → None; helper `rates_from_cut_buckets` (25bp/corte, convenção da espec); sanity check item 6 como teste.
- **Integração implementada** (`src/bl_integration.py`): `stack_views` (filtra None, empilha P (k,n)/Q (k,), preserva diagnostics na ordem — é o alinhamento do Ω da Lia) e `bl_weights_from_views` (prior → posterior → pesos com Σ amostral irrestrita, decisão 8; **sem view ativa devolve w_mkt exato**; view ativa sem Ω falha alto — nunca inventar confiança). Quais views entram na lista é decisão do chamador/backtest — é aí que a pendência B/C/E/G se materializa.
- Bateria completa: 6 + 7 + 7 + 5 + 5 + 5 + 4 + 5 + 4 = **48 testes OK**.

**Quebrou / aprendido:**
- Nada quebrou (testes passaram de primeira nas duas views). Convenção de unidades explicitada para evitar erro silencioso %-vs-decimal: tudo que é retorno/inflação em fração decimal; na 2.3, taxas em bps → β em fração/bp.

**Pendente:**
- Decisão 11 (favorite-longshot + bucket aberto) segue bloqueio para qualquer view rodar com dado real (os stubs falham alto em todas).
- **Decisão 12 (nova, 🟡):** o CRITÉRIO de escolha do k a partir do perfil de lags não está especificado nas especs 2.4/3.1 ("varrer k" não diz como escolher). Encaminhamento do Felipe em sessão: **opção (a) — decidir com o perfil real na mesa** quando o dado do Paulo chegar; até lá `lag_regression` devolve o perfil completo e k entra como argumento humano. Registrada com opções/trade-offs em `Decisoes_pendentes.md`.
- **Lia:** validar o campo `diagnostics` do `ViewResult` como insumo do Ω.
- **Paulo:** condições já registradas (cobertura CPI/FOMC/recessão/presidencial no poly, bid/ask histórico no CLOB, T10YIE + DGS10/DTB3 do FRED, ZQ no yfinance). Detalhe novo a acordar quando o dado chegar: a conversão preço do ZQ → `E_FF` em bps (de qual taxa corrente subtrair a implícita 100−preço) fica a montante da view (já coberto pela pendência "fonte a acordar" da espec da 2.3).
- Pendências de desenho já registradas nas especs seguem: horizonte da 3.1/B (reunião), k≈0 (2.4/C/E/G), reconciliação do horizonte do Q (k dias) com Σ/π — **agora bloqueia o backtest misturar views poly-defasadas com as diárias** (aviso no docstring da integração) —, coeficientes exatos do probit, ΣP empírico (decisão conjunta), reuso do β da 2.3 na B, rolagem entre mercados anuais/deadline (3.1/B/C).
- **Reunião: entrada das candidatas B/C/E/G** — código pronto, decisão em aberto (rodapé de `Decisoes_pendentes.md` inalterado).
- τ e δ reais: seguem sem decisão registrada (testes usam sintéticos marcados).
- Próximo código: backtest (loop de rebalanceamento sobre o dataset do Paulo) — depende do dado e das decisões 11/12.

**Uso de IA:**
- **Modelo:** Claude Code / Fable 5.
- **Contexto consumido:** ~190k tokens (~19% de janela de 1M).
- **Prompt inicial (verbatim):** "quero começar a montar o código das views. fechamos a decisão 9 e agora vamos montando as views, por qual começamos"
- **Iterações até aceitar:** 1 (todas as entregas — interface, 8 views, maquinaria compartilhada e integração — aceitas sem rodada de correção; interface fechada pelo Felipe em 3 escolhas estruturadas; critério do k encaminhado em 1 escolha).
- **Erros da IA:** 1, auto-corrigido no mesmo turno — um Edit em `views_common.py` inseriu texto de docstring fora das aspas (seria SyntaxError); detectado e corrigido antes de rodar qualquer teste.
- **Decisões escaladas:** decisão 12 criada (🟡, critério do k — encaminhamento: fecha com o dado real); interface das views e regra do template fechadas pelo Felipe em sessão (não numeradas); implementação das candidatas B/C/E/G autorizada pelo Felipe SEM fechar a entrada delas na carteira (segue de reunião).
- **Tags:** `[PROMPT-CHAVE]` (candidato: a camada de views inteira — 8 views + maquinaria + integração, 48 testes — nasceu desta sequência curta de prompts; bom caso para o teste de reprodutibilidade).

## 2026-07-11 — Felipe

**Feito:**
- Pergunta de abertura ("dá para começar o código das views direto?") respondida com levantamento de dependências: o único código-fundação faltante era o pré-processamento das probabilidades do poly — exatamente a decisão 9, então ela foi resolvida antes de codar.
- **Decisão 9 fechada (por instrução do Felipe): Opção A** — módulo compartilhado único `src/poly_preprocessing.py` (módulo do Felipe), caixa de ferramentas de funções puras, sem `preprocess()` monolítico. O midpoint fica no módulo (não no pipeline do Paulo); implicação de interface registrada: o dataset do Paulo entrega bid/ask cru — Felipe vai alinhar com Paulo o uso da API com bid/ask histórico (mesma condição de fechamento das views 2.4/3.1). Alternativas B (por view) e C (midpoint no Paulo) documentadas como descartadas.
- **Nova decisão 11 registrada** (🔴): (a) forma da correção de favorite-longshot e (b) valor do bucket aberto das PMFs — as duas peças do módulo sem forma/valor decididos, com opções mapeadas para reunião. ⚠️ Nota de numeração: o nº 11 já existiu (entrada das candidatas B/C) e foi removido por completo em 2026-07-10; o número foi reutilizado para tema totalmente diferente — sem colisão no arquivo atual, mas atas antigas que citem "decisão 11" referem-se ao tema antigo.
- **Código novo:** `src/poly_preprocessing.py` — `midpoint_price` ((bid+ask)/2, rejeita bid>ask), `normalize_probs` (divide pela soma; binários e matriz datas×buckets), `favorite_longshot` e `open_bucket_value` como stubs que levantam `NotImplementedError` com `TODO(DECISAO-11)` (falham alto de propósito: identidade silenciosa esconderia a ausência da correção no backtest). Testes sintéticos em `tests/test_poly_preprocessing.py` — 4/4 OK.
- Achado no caminho (leitura de `PAULO_dados.md` a pedido): o mandato do Paulo não inclui limpeza de Polymarket e recomenda proxies (FedWatch) / PolymarketData.co — se a fonte final não tiver bid/ask, o midpoint deixa de existir para qualquer opção e as views 2.4/3.1 perdem a condição de fechamento. Felipe assumiu alinhar a fonte com o Paulo.

**Quebrou / aprendido:**
- Nada quebrou (testes passaram de primeira). Aprendizado: a checagem "se comporta igual nas views?" (que derrubou a tabela de sensibilidades) passou desta vez — normalização é idêntica em todas e o favorite-longshot é a mesma função elemento a elemento (muda calibração, não código).

**Pendente:**
- **Decisão 11** (favorite-longshot + bucket aberto) — reunião; até lá as views que dependem delas usam os stubs.
- **Felipe → Paulo:** alinhar fonte de dados do poly com bid/ask histórico (condição da decisão 9 e das views 2.4/3.1).
- Próxima sessão de código: **view 2.2 (inflação)** — a mais mecânica, já destravada pelo módulo novo.
- Anteriores seguem: reunião (candidatas B/C/E/G, tática reformulada, horizonte 3.1, k≈0, decisão 6), condições do Paulo.

**Uso de IA:**
- **Modelo:** Claude Code / Fable 5.
- **Contexto consumido:** ~55k tokens (~5% de janela de 1M).
- **Prompt inicial (verbatim):** "quero começar a montar o código das views. Podemos começar direto com eles ou teria outro código que teriamos que montar antes?"
- **Iterações até aceitar:** 1 (explicações da decisão 9, leitura do PAULO_dados.md e código aceitos sem rodada de correção).
- **Erros da IA:** nenhum.
- **Decisões escaladas:** decisão 9 fechada por instrução humana explícita; decisão 11 criada (aberta).
- **Tags:** —

## 2026-07-10 (sessão 3) — Felipe

**Feito:**
- **Decisão 11 removida por completo** de `Decisoes_pendentes.md` por instrução do Felipe; referências nos docs das views B e C ajustadas para texto neutro ("entrada na carteira em aberto"); rodapé atualizado. As candidatas passam a viver só nos próprios arquivos (mesmo modelo da 1.3).
- **Geração de 6 ideias novas** (views E tarifas / F petróleo / G fiscal + táticas T1 momentum monetário / T2 gap de fim de semana / T3 drift em renda fixa) e **pesquisa web de embasamento teórico** → `Informações_uteis/Pesquisa_embasamento_novas_ideias.md` (âncoras com citação e link, gotchas de desenho, 2 candidatas extras descobertas — view H chair do Fed, tática T4 ciclo FOMC — e 4 achados transversais: favorite-longshot/"Yes bias" p/ decisão 9; minoria informada ~3% p/ o Ω; mean-reversion dos binários como ressalva ao template poly-defasado; SWZ como guarda-chuva metodológico do bridge p/ o relatório).
- **Avaliação uma a uma (to-do), decisões do Felipe em cada:**
  - **F descartada** — dupla exposição com a C (mesmo canal XLE); agravante documentado: mercados de WTI do poly resolvem one-touch (precificam o máximo, não o preço terminal).
  - **E fechada como candidata** → `views/view_E_tarifas.md` (família EUA×China primário + recíprocas robustness; β aceito com fragilidade documentada; TLT no cross-section via flight-to-safety do AGKW; template poly-defasado da 2.4).
  - **T1+T3 fundidas** numa tática → `táticas/tatica_drift_pos_fomc.md` (dois livros: SPY ~15d e TLT ~50d truncado no FOMC seguinte; direção simétrica; tamanho binário por sinal com upgrade proporcional; sub-decisão marcada no arquivo: expectativa da véspera = ZQ à la Kuttner, variante E_poly registrada p/ reunião).
  - **G fechada como candidata-RESERVA** → `views/view_G_fiscal.md` (reorientada pela literatura: tributária primário/OBBB + teto da dívida robustness; **shutdown descartado como evento** — S&P flat/positivo em 10 de 13; paradoxo do TLT no teto registrado sem sinal a priori).
  - **T2 fechada como candidata** → `táticas/tatica_gap_fds.md` (sinal = Δp de fim de semana dos mercados das views ativas × β já estimados; tilt contínuo sem threshold; desmonte em 1 dia útil; mean-reversion como risco documentado).
  - **H descartada** — tripla exposição ao tema Fed (2.3+B+H) + evento único na janela.
  - **T4 descartada** — zero conexão com o poly (fora do tema) + evidência pós-amostra enfraquecendo.
- Criado `claude_ignore/guia_ideias.md` (guia pessoal do Felipe, uma linha por ideia com estado — fora da leitura/manutenção do Claude).

**Quebrou / aprendido:**
- Nada de código. Aprendizados: (i) shutdown puro não mexe em equities — a candidata fiscal só sobreviveu reorientada para tributária+teto; (ii) mercados de commodities do poly podem resolver por one-touch — a receita "média da PMF" da 2.2 não transfere sem checar o critério de resolução (item novo para validar em qualquer mercado de buckets); (iii) exposição repetida ao mesmo tema virou o filtro de corte na prática — derrubou F (×C) e H (×2.3×B); (iv) a camada tática reformulada comporta ideias sem sinal do poly no dia (drift usa ZQ), mas não ideias sem conexão nenhuma com o projeto (T4).
- **Observação (não resolvida):** `Informações_uteis/Ideias_consolidadas.md` consta como **deletado** no working tree, mas o mapa de camadas ainda aponta para ele (descrições de 1.1/1.2/3.2 ficariam sem lar) — confirmar se a deleção foi intencional.

**Pendente:**
- **Reunião:** entrada das candidatas B/C/E/G (sem número de decisão — decisão 11 removida); reabrir a camada tática reformulada (decisão 10) agora com 3 táticas e seus orçamentos (`orçamento_máx` da 1.3, `orçamento_máx_drift`, `λ` do gap); sub-questões novas: fonte da expectativa do drift (ZQ vs E_poly), micro-surpresas, janelas 15/50d, desmonte do gap (1d vs k), precedência gap × rebalance; antigas: horizonte 3.1, k≈0, decisões 6 e 9.
- **Paulo:** mercados no CLOB — tarifas EUA×China + recíprocas (condição da E), aprovação fiscal OBBB + teto/X-date (condição da G); preço de **abertura** de segunda dos ETFs (gap); ⚠️ marcação diária **contínua** no backtest (livro TLT do drift ≈ 42 dias úteis por reunião — mais pesado que os ~20 dias/ano da 1.3); condições anteriores seguem.
- **Lia:** nota Ω ↔ camada tática agora cobre 4 módulos (2.3 antes do FOMC, 1.3 no dia, drift depois, gap nas segundas).

**Uso de IA:**
- **Modelo:** Claude Code / Fable 5 (effort max a partir do pedido de pesquisa).
- **Contexto consumido:** ~130k tokens (~13% de janela de 1M).
- **Prompt inicial (verbatim):** "veja onde estamos do projeto agora, o que falta para fazer"
- **Iterações até aceitar:** 1 (todos os arquivos aceitos de primeira — "pode seguir sua leitura" em E/G/drift/gap; a primeira to-do foi desfeita e refeita por mudança de escopo do humano — pesquisa antes de avaliar —, não por erro).
- **Erros da IA:** 1 de imprecisão, auto-apontado: na abertura da bateria T1+T3 descreveu a surpresa do drift como "a que a 2.3 já calcula" (a 2.3 calcula divergência pré-reunião; o drift usa surpresa realizada) — corrigido no próprio arquivo com a sub-decisão marcada e a variante E_poly escalada para reunião. Publicações não verificadas foram citadas como working paper (sem status de journal inventado).
- **Decisões escaladas:** nenhuma decisão numerada criada/fechada. Decisão 11 removida por instrução explícita. Desenhos de E/G/drift/gap fechados por decisão do humano em sessão (registrados nos arquivos das ideias); F/H/T4 descartadas por decisão do humano.
- **Tags:** [PROMPT-CHAVE] candidato — terceira sessão consecutiva com a mesma abertura, desdobramento reprodutível (status → ideias → pesquisa → avaliação um a um → arquivos).

## 2026-07-10 (sessão 2) — Felipe

**Feito:**
- Sessão de expansão da estratégia (sem código): to-do de 4 candidatas discutidas uma a uma — 1.3, 3.3, B e C (motivação: carteira só com views macro e 2.4 em risco no backtest).
  - **1.3 Prêmio de anúncios (Savor-Wilson):** decidido (Felipe) que **não é view do BL** (afirma "quando estar exposto", não retorno esperado; prêmio de 1 dia, ~20 eventos/ano) → vira **candidata-fundadora da camada tática reformulada** ("ideias paralelas ao BL compatíveis com granularidade ~12h"; gatilho = calendário, sinal lento). Desenho fechado em 2 baterias de perguntas: sleeve overlay long SPY vs caixa por cima do BL (alavanca temporária, BL intocado), sempre ligado em dia de anúncio FOMC+CPI, tamanho = orçamento_máx × entropia normalizada da PMF (snapshot ≤ D−1 close, sem lookahead; módulo da decisão 9), janela D−1→D close, calibração normativa no v1 com regressão como upgrade. Criado `Informações_uteis/táticas/tatica_1.3_premio_anuncios.md`; por escolha do Felipe, **registrada só no arquivo por ora** (sem nova decisão em `Decisoes_pendentes.md` — reabrir a camada mexe na decisão 10 e vai à reunião).
  - **3.3 Proxy de vol: descartada** (Felipe) — forma original exige opções/VIX (fora do universo); adaptada, usa o mesmo sinal da 1.3 com trade oposto (contradição) e o espírito defensivo já é papel do Ω. Menções removidas de `Black-Litterman_com_Polymarket.md` (bullet da camada de risco) e `Decisoes_pendentes.md` (linha da decisão 10); `Ideias_consolidadas.md` preservado (retrato histórico) e LOG antigo intacto (histórico não se reescreve).
  - **B Trajetória do Fed:** doc de candidata criado espelhando a 2.3 → `Informações_uteis/views/view_B_trajetoria_fed.md` (surpresa = E_poly[taxa fim de ano] − ZQ dez; β/P reusados da 2.3 com premissa explícita; pendências de reunião: dupla exposição com a 2.3, confirmação do reuso do β, horizonte/rolagem anual junto com a 3.1). Status 🟡 candidata — não fecha as decisões 3/4.
  - **C Geopolítica→energia: desenho fechado por delegação explícita do Felipe ao Claude** ("vou te dar controle sobre essas decisões") → `Informações_uteis/views/view_C_geopolitica_energia.md`. Decisões delegadas: âncoras Kilian & Park (2009) + Caldara & Iacoviello (2022) como sanity check; evento primário = ação militar EUA/Israel×Irã 2025 (~$29,9M + família; volumes de levantamento web, Paulo valida), robustness = cessar-fogo Rússia×Ucrânia, Israel×Hamas fora; **P cross-sectional** substituindo o esboço "XLE vs SPY" da decisão 11. Resto herda a maquinaria da 2.4. Entrada na carteira segue na decisão 11 (reunião).
- Decisão 11 atualizada com ponteiros para os docs de B e C (decisão em si segue aberta); rodapé de `Decisoes_pendentes.md` atualizado.

**Quebrou / aprendido:**
- Nada de código. Aprendizados: (i) o critério que separa view de tática não é o tema, é o objeto da afirmação — retorno esperado num horizonte de rebalance (view) vs quando/quanto estar exposto (camada); (ii) a granularidade de 12h não mata ideias de calendário (anúncios agendados) — matou a tática antiga porque lá o gatilho era salto intradiário; (iii) a 3.3 e a 1.3 eram o mesmo sinal com conclusões opostas — só uma podia existir.

**Pendente:**
- **Reunião:** decisão 11 (B e C, docs prontos); reabrir a camada tática no formato reformulado (1.3: orçamento_máx, dono do módulo — era da Lia); pendências compartilhadas: horizonte/rolagem anual (3.1 + B + C juntas), k≈0 (2.4 + C), decisões 6 e 9.
- **Paulo:** mercados Irã 2025 e Rússia×Ucrânia no CLOB (cobertura, volume, bid/ask — condição da C); mercados de trajetória do Fed + ZQ de dezembro no yfinance (condição da B); requisito novo do backtest: **marcar posições diariamente nos dias de anúncio** (~20/ano) para a camada da 1.3; calendário de releases do CPI como dado novo.
- **Lia:** nota de interação Ω ↔ camada da 1.3 (a mesma incerteza entra com sinais opostos nos dois módulos — documentar para o Ω não neutralizar a camada por construção).
- Avisos a Paulo/Lia das sessões anteriores seguem pendentes.

**Uso de IA:**
- **Modelo:** Claude Code / Fable 5.
- **Contexto consumido:** ~95k tokens (~9% de janela de 1M).
- **Prompt inicial (verbatim):** "veja onde estamos do projeto agora, o que falta para fazer"
- **Iterações até aceitar:** 1 (nenhuma rodada de correção de conteúdo; docs aceitos de primeira).
- **Erros da IA:** de conteúdo, nenhum. De condução, 1: avançou a análise completa da 1.3 sem esperar o usuário ("para, calma ai") — corrigido no ritmo da sessão.
- **Decisões escaladas:** nenhuma fechada em `Decisoes_pendentes.md`. Decisão 11 atualizada (ponteiros B/C); 3.3 removida por instrução explícita; desenho da C fechado **por delegação explícita** do Felipe (registrada no doc da view); camada tática reformulada registrada só em arquivo por escolha do Felipe.
- **Tags:** [PROMPT-CHAVE] candidato — mesma abertura da sessão anterior, com desdobramento reprodutível (status → candidatas → docs).

## 2026-07-10 — Felipe

**Feito:**
- Revisão do estado do projeto (mapa decidido × em aberto) e sessão de decisão sobre as duas views paradas — **os problemas da 1.2 e da 3.1 foram resolvidos**:
  - **1.2 Momentum: fechada** — reclassificada como **camada tática** (gatilho = tendência/velocidade da probabilidade; sem âncora de magnitude para o template estrutural) → adiada junto com a camada (decisão 10); reabre com a retomada da tática. Registrada nas decisões 1, 3, 4 e 10; removida da Camada 1 do mapa (`Black-Litterman_com_Polymarket.md`) e anotada no aviso do retrato histórico.
  - **3.1 Sentimento: fechada condicionalmente** — reframe para **view de recessão** (caminhos "índice agregado" e "contexto/Ω" rejeitados; o Ω reativo já cobre leitura de regime). Desenho fechado em 2 baterias de perguntas: `Q = (Σ P·β) × (p_poly − p_curva)`; p_poly de binário de recessão (preferência: resolução técnica GDP, condicional ao levantamento do Paulo; midpoint bid/ask + decisão 9); p_curva de probit clássico com coeficientes publicados (Estrella-Mishkin/NY Fed) sobre spread 10a−3m do FRED; β por regressão própria vs Δp_poly com teste de defasagem e absorção plena (maquinaria da 2.4); P espelha a 2.3 (Σ|P| = 2); ativação/desligamento herdados da 2.4. Criado `Informações_uteis/views/view_3.1_recessao.md` (fórmulas, cascata, 9 rejeitadas, pendências).
- Decisão 9 ganhou os itens do binário de recessão (favorite-longshot é **relevante** nesta view — p baixa, ao contrário da 2.4).
- **Decisão 11 criada (🔴 aberta):** views adicionais candidatas para reunião — B (trajetória do Fed vs ZQ de dezembro; reusa β/P da 2.3), C (geopolítica→energia; template poly-defasado da 2.4, XLE) e D (shutdown/fiscal, reserva). A candidata A (recessão) virou a 3.1 na mesma sessão.

**Quebrou / aprendido:**
- Nada de código. Aprendizado: a 3.1 original tinha 3 defeitos (dupla contagem com 2.2/2.3, sem benchmark único, índice = pilha de parâmetros arbitrários) — estreitar para o único pedaço com dois termômetros reais (recessão: poly vs curva) resolve os três de uma vez.

**Pendente:**
- **Reunião:** horizonte da 3.1 (poly "até dez" vs curva 12m rolante + rolagem entre mercados anuais — única decisão de desenho adiada pelo Felipe na sessão; opções mapeadas na view); decisão 11 (views B/C/D); decisões 6 e 9 seguem abertas.
- **Paulo:** mercados de recessão no CLOB (2023–25), critério de resolução, volume e bid/ask histórico (condição da 3.1, como na 2.4); referência exata dos coeficientes do probit a fixar antes de implementar.
- Pendências transversais inalteradas (horizonte do Q, k ↔ rebalance, k≈0 da 2.4, bid/ask histórico); avisos a Paulo/Lia das sessões anteriores seguem pendentes.

**Uso de IA:**
- **Modelo:** Claude Code / Fable 5.
- **Contexto consumido:** ~65k tokens (~6% de janela de 1M).
- **Prompt inicial (verbatim):** "veja onde estamos do projeto agora, o que falta para fazer"
- **Iterações até aceitar:** 1 (explicações leigas da 1.2 e 3.1 e registros aceitos sem rodada de correção; o horizonte da 3.1 foi adiado por escolha do humano, não por erro).
- **Erros da IA:** nenhum.
- **Decisões escaladas:** 11 (nova, aberta). Fechadas por instrução explícita do humano: 1.2 (reclassificação tática, nas decisões 3/4/10) e 3.1 (reframe para recessão, decisões 3/4 — condicional).
- **Tags:** —

## 2026-07-09 (sessão 4) — Felipe

**Feito:**
- Execução documental de decisão de time reportada pelo Felipe: **camada tática (velocidade de ajuste, event-driven 3.2, PEAD 1.1) adiada — removida do escopo do projeto**, fica para retomada futura. Registrada como **decisão 10 (🟢)** em `Decisoes_pendentes.md`; os demais documentos apontam para ela (regra "aponte, não copie").
- Edições por arquivo:
  - `Decisoes_pendentes.md`: decisão 10 criada; **decisão 5 (surpresa do PEAD) fechada sem objeto** (PEAD é inteiramente tático — reabre com a retomada); notas de adiamento nas decisões 1 (universo tático sem efeito), 3 (nota de nomenclatura) e 4 (escopo; pergunta da 1.2 vira "estrutural ou adiada junto com a tática"); rodapé atualizado.
  - `Black-Litterman_com_Polymarket.md`: seção "2. Camada tática" do mapa condensada em nota de adiamento — preserva a descrição de 1 linha da "velocidade de ajuste" (única no repositório; 1.1 e 3.2 têm lar no retrato histórico); numeração das camadas 3/4 mantida para não quebrar referências (ex.: decisão 9 cita "Camada 4"); linha "Atenção" (2.4/firm-specific) atualizada; removida a frase "mesmo sinal roda como view ou tático".
  - `CLAUDE.md`: módulos da Lia viram "Ω reativo · Relatório"; nota de adiamento abaixo da tabela (a tática volta a ser módulo dela se retomada).
  - `Ideias_consolidadas.md`: só o aviso do topo ganhou a menção do adiamento (conteúdo congelado intocado).
  - `views/view_2.4_eleitoral.md`: 3 referências à tática anotadas como adiada (status, item 0, decisões rejeitadas).
  - Inalterados: `README.md` e views 2.2/2.3 (sem menção à tática); entradas antigas do LOG (histórico não se reescreve). Camada de risco (1.3, 3.3), Ω reativo e reserva (3.4) **não** foram tocados — não são tática.

**Quebrou / aprendido:**
- Nada de código. Ponto de atenção: a "velocidade de ajuste" não tinha lar fora do mapa de camadas — deletar a seção seca apagaria a ideia do repositório, contrariando o "fica para depois"; ficou preservada na nota compacta.

**Pendente:**
- **Avisar Paulo/Lia:** decisão 10 + módulo da Lia reduzido no `CLAUDE.md` (mudanças no branch Felipe, valem após merge) — soma-se ao aviso pendente da sessão 3 (deleções de arquivos).
- Decisões abertas: 3/4 para 3.1 e 1.2; 6 e 9. Pendências transversais inalteradas (Σ|P|, horizonte do Q, k≈0, bid/ask histórico no CLOB).

**Uso de IA:**
- **Modelo:** Claude Code / Fable 5 (effort max).
- **Contexto consumido:** ~50k tokens (~5% de janela de 1M).
- **Prompt inicial (verbatim):** "Leia c:\Users\felip\Documents\Pessoal\Desafio-Quant-Itau\Informações_uteis\Black-Litterman_com_Polymarket.md. c:\Users\felip\Documents\Pessoal\Desafio-Quant-Itau\Informações_uteis\Ideias_consolidadas.md, c:\Users\felip\Documents\Pessoal\Desafio-Quant-Itau\Decisoes_pendentes.md, c:\Users\felip\Documents\Pessoal\Desafio-Quant-Itau\LOG.md, c:\Users\felip\Documents\Pessoal\Desafio-Quant-Itau\CLAUDE.md. Saiba que o Log pode ter informações desatualizadas por ser uma memoria de dump."
- **Iterações até aceitar:** 1 (a confirmar pelo humano).
- **Erros da IA:** nenhum.
- **Decisões escaladas:** 10 (nova, registrada como fechada por decisão de reunião reportada pelo humano); 5 fechada sem objeto como consequência direta da 10.
- **Tags:** —

## 2026-07-09 (sessão 3) — Felipe

**Feito:**
- **Limpeza de divergências** (sem código): auditoria dos 11 `.md` do repositório; 22 edições em 9 arquivos, todas por decisão do humano (3 baterias de perguntas):
  - `Ideias_consolidadas.md` congelado como retrato histórico (aviso no topo); Mapa/BL doc atualizados às views fechadas (2.4 sem cestas/cross-section de β; exemplo da 2.3 em bps — não probabilidade; "real estate" fora dos exemplos; convergência entre fontes anotada como stub fora do v1 — decisão 7).
  - **"Camada 2 (cenário→ativo)" absorvida no bridge:** módulos do Felipe no `CLAUDE.md` viram "Otimizador BL · Bridge probabilidade→Q (P, Q e β por view) · Integração final"; "Camada 2" volta a ter significado único (camada tática).
  - Decisão 4 compactada: linhas 2.2/2.3/2.4 da tabela da Família A apontam "fechada → `views/`"; perguntas de reunião reduzidas às restantes (3.1 e 1.2); rodapé com o próximo passo real.
  - LOG: cabeçalho faltante "2026-07-09 (sessão 1)" inserido no bloco órfão do fechamento 2.2/2.3; data da view_2.2 corrigida (08 → 09/jul).
- **Reestruturação do repositório** (decisão do humano): `CRONOGRAMA_GERAL.md` (deadlines não usados; regras duplicavam CLAUDE.md), `FELIPE_arquitetura_BL.md` (duplicava CLAUDE.md/views) e `Mapa_de_camadas.md` **deletados**; mapa de camadas + norte geral **fundidos** em `Black-Litterman_com_Polymarket.md` (nenhum conteúdo perdido; seção "Sinais táticos" deduplicada dentro da Camada tática). 11 → 8 arquivos `.md`.
- README de índice ("onde cada informação vive" + regra "aponte, não copie") proposto no chat — Felipe comita na main.

**Quebrou / aprendido:**
- Nada de código. Aprendizado: a desorganização vinha de **sobreposição de lares** (a view 2.4 estava descrita em 6 lugares), não do número de arquivos. Regra adotada: um arquivo-lar por tipo de informação; os demais apontam, não copiam.

**Pendente:**
- Felipe: comitar o README na main; **avisar Paulo/Lia** das deleções (Cronograma, Mapa, FELIPE_arquitetura) — mudanças no branch Felipe, valem após merge.
- Estado das decisões inalterado: 3/4 abertas para 3.1 e 1.2; 5, 6 e 9 abertas; pendências transversais (Σ|P|, horizonte do Q, k≈0, bid/ask histórico no CLOB) seguem como estavam.

**Uso de IA:**
- **Modelo:** Claude Code / Opus 4.8 e Fable 5 (troca via `/model` no início; effort max).
- **Contexto consumido:** ~90k tokens (~9% de janela de 1M).
- **Prompt inicial (verbatim):** "Tenho um problema de organização. Tenho varios documentos de informações sobre a minha parte/as ideias/ a estratégia em geral. Acredito que tem informações conflitantes e um excesso de documentos. Vamos começar fazendo uma limpeza de informações. preciso que você leia todos os documentos md do repositório e vá me perguntando como resolver cada divergencia de informação que encontrar" (um prompt anterior na mesma sessão veio cortado e foi abortado com "stop").
- **Iterações até aceitar:** 1 (nenhuma rodada de correção; todas as escolhas coletadas em 3 baterias de perguntas estruturadas antes de editar).
- **Erros da IA:** nenhum.
- **Decisões escaladas:** — (nenhuma nova/fechada em `Decisoes_pendentes.md`; as escolhas foram de organização documental, sem impacto metodológico).
- **Tags:** —

## 2026-07-09 (sessão 2) — Felipe

**Feito:**
- Sessão de decisão (sem código): desenho da **view 2.4 Eleitoral** fechado, no mesmo processo das 2.2/2.3 (7 perguntas levantadas pela IA a partir de `Ideias_consolidadas.md` + `Mapa_de_camadas.md`; respostas/decisões do humano). Criado `Informações_uteis/views/view_2.4_eleitoral.md`.
- Decisões principais registradas:
  - Escopo só eleitoral ("regulatória" saiu do nome; firm-specific → tática 3.2). Evento: presidencial EUA 2024, binário de vencedor sobre p(Trump) (p(democrata) tem quebra de identidade em 21/jul/2024); 2022 = robustness check; Senado/Câmara/sweep fora (distribuição conjunta).
  - β por regressão própria (retorno diário do ETF vs Δp(Trump)), híbrida: β manda sempre, literatura só sanity check a posteriori (nunca inverte β); janela expandida sem lookahead; teste de defasagem Δp(t−1)→retorno(t) obrigatório.
  - **Segunda exceção à Família A:** sem instrumento externo precificando o evento, o benchmark é o **próprio poly defasado** — `Q = (Σ P[i]·β_i) × (p_t − p_{t−k})`, k estimado pela varredura de defasagem, β de absorção plena = soma dos coeficientes dos lags 0…k; **Q é retorno acumulado de k dias**. k ≈ 0 → view nunca liga (condição permanente; o que fazer é pendência). Acoplamento k ↔ frequência de rebalance co-documentado.
  - P cross-sectional `P[i] ∝ (β_i − β_SPY)` com Σ|P| = 2; centragem em β_SPY mantida por consistência com a 2.3, com obrigação de medir ΣP e decidir sobre o componente direcional (trocar 2.3 e 2.4 juntas, se for o caso).
  - Ativação sem parâmetros (existe mercado → ativa; liquidez é papel do Ω); **desligamento no último dia antes do primeiro tick de resolução** (senão o salto de 5–6/nov fabrica alfa).
  - Pré-processamento: midpoint bid/ask (nunca último trade — série stale infla k); itens (a)/(b)/(c) registrados na decisão 9.
- `Decisoes_pendentes.md` atualizado: decisões 3 e 4 agora fechadas para 2.2, 2.3 **e 2.4** (em aberto: 3.1 e 1.2); decisão 9 ganhou os itens da 2.4, incluindo o novo item "qual preço da série".

**Quebrou / aprendido:**
- Nada de código. Aprendizados: 2.2/2.3 têm benchmark porque existe um segundo instrumento precificando a mesma variável — na eleição não existe, e o benchmark correto é o poly defasado; TIP−TLT é identidade, não cesta escolhida (o argumento "par é mais legível" não transfere para a eleição); a escolha do preço da série (midpoint vs último trade) pode fabricar a defasagem k inteira.
- **Inconsistência detectada entre views:** 2.3 normaliza Σ|P| = 1; 2.2 (par +1/−1) e 2.4 usam Σ|P| = 2 — Q das views em escalas diferentes. Registrada como pendência transversal (reconciliar mudando as views juntas).

**Pendente:**
- Paulo: histórico do mercado presidencial 2024 no CLOB — **se há bid/ask histórico para reconstruir o midpoint** (a view está "fechada condicionalmente" a isso); idem 2022.
- Parâmetros numéricos por decisão humana: limiar de volume p/ estimabilidade do β; frequência de rebalanceamento (acoplada ao k).
- **k ≈ 0 (decisão de reunião não tomada):** fallback para tilt contemporâneo `Q = β·Δp` ou 2.4 fora do v1.
- **Horizonte do Q** (acumulado de k dias) a reconciliar com Σ e π antes da implementação.
- Reconciliar Σ|P| entre 2.3 e 2.4 (e 2.2) — juntas.
- Views 3.1 (Sentimento) e 1.2 (Momentum) — próximas da fila; decisão 9 (módulo PMF compartilhado) segue aberta.

**Uso de IA:**
- **Modelo:** Claude Code / Fable 5.
- **Contexto consumido:** ~90k tokens (~9% de janela de 1M).
- **Prompt inicial (verbatim):** "Fechei o desenho das views 2.2 e 2.3. agora quero seguir para a 2.4 Leia a descrição dela em c:\Users\felip\Documents\Pessoal\Desafio-Quant-Itau\Informações_uteis\Ideias_consolidadas.md e c:\Users\felip\Documents\Pessoal\Desafio-Quant-Itau\Informações_uteis\Mapa_de_camadas.md Com base nisso monte perguntas para decidirmos o que falta do seu desenho. No final vamos montar um documento simples com o que foi decidido/ rejeitado e o que a ideia deve fazer"
- **Iterações até aceitar:** 2 (perguntas aceitas de primeira; doc da 2.4 passou por 1 rodada de revisão do humano com 7 correções, todas aplicadas).
- **Erros da IA:** nas perguntas — as opções da Q4 partiam de premissa errada (exigir benchmark externo, que não existe para eleição; o humano propôs a opção D, poly defasado); Q4-B descreveu `β × Δp` incorretamente como momentum; Q6 ofereceu parâmetro desnecessário ("N meses antes") e fundiu ativação/peso/estimação; Q7 não listou a sub-decisão mais grave (qual preço da série). No doc (pegos na revisão do humano) — contradição interna Σ|P| = 2 rotulado "long 1/short 1" quando ΣP ≠ 0; Q sem declarar que é retorno acumulado de k dias nem a premissa de spike no lag k, e "β de absorção plena" usado sem definição; colisão de janelas no item 3 (fim da amostra "até a resolução" reintroduzia lookahead); k ≈ 0 tratado como a mesma cascata do item 0, escondendo decisão não tomada; unidade de p ambígua (%/fração); consequência do limiar de amostra ausente; status "🟢 fechada" incompatível com pendência declarada como invalidante.
- **Decisões escaladas:** 3 e 4 fechadas para a view 2.4 por instrução humana explícita; decisão 9 expandida (itens a/b/c da 2.4); nova pendência transversal Σ|P|.
- **Tags:** —

## 2026-07-09 (sessão 1) — Felipe

**Feito:**
- Sessão de decisão (sem código): fechamento das decisões 3 e 4 **por view**, ideia por ideia, para as duas primeiras views estruturais:
  - **View 2.2 Inflação (fechada):** divergência em pontos de inflação (E_poly[CPI] via média da PMF dos buckets do poly vs breakeven T10YIE/FRED); Q = duration do breakeven 10a (~8) × Δinflação, par TIP−TLT; β = duration (exceção à Família A, sem regressão); cascata de degradação (PMF → binário via normal deslocada → view desativada com Ω→∞); pré-processamento das probs (normalização bid/ask, favorite-longshot, bucket aberto).
  - **View 2.3 Fed (fechada):** surpresa = E_poly[Δtaxa] − E_FF[Δtaxa] em bps (E_poly da PMF dos buckets de FOMC; E_FF do futuro ZQ via yfinance, contrato do mês posterior à reunião); β por regressão própria event-study contra surpresa à la Kuttner (literatura B-K só como sanity check); P = função determinística do vetor β, centrado em β_SPY (P[SPY]=0 exato); Q = surpresa · Σ P[i]·β_i (retorno do portfólio long-short definido por P); sanity check de sinal marcado como teste obrigatório.
- Criados `Informações_uteis/views/view_2.2_inflacao.md` e `view_2.3_fed.md` (resumo da ideia, decisões fechadas e rejeitadas, pendências por view).
- **Decisão 9 registrada** em `Decisoes_pendentes.md`: pré-processamento de PMFs como módulo compartilhado entre 2.2 e 2.3 (aberta — verificar se se comporta igual nas duas antes de compartilhar).
- Decisões 3 e 4 atualizadas para 🟡 com registro parcial (2.2 e 2.3 fechadas; 2.4, 3.1 e 1.2 em aberto).

**Quebrou / aprendido:**
- Nada de código. Aprendizados registrados nos docs das views: mercados de CPI/FOMC do poly são **buckets exatos (PMF)**, não thresholds (CDF); do ZQ sai **esperança em bps, não probabilidade** (não existe p_FF); benchmark e duration da 2.2 são acoplados; origem do β e construção de P na 2.3 são acopladas (β da literatura quebraria o centro β_SPY).

**Pendente:**
- Views 2.4 (Eleitoral), 3.1 (Sentimento) e 1.2 (Momentum) — próximas da fila para fechar 3/4 por completo.
- Decisão 9 aberta (módulo de PMF compartilhado).
- Pendências críticas de dados (Paulo): cobertura histórica dos mercados de CPI e de FOMC no poly (~18 meses), inclusão do FRED (T10YIE) no pipeline, qualidade do histórico do ZQ no yfinance.
- Fonte das datas de FOMC + variação do FF future no dia (para a regressão da 2.3) a acordar; parâmetros numéricos (janela da regressão, valor exato da duration) por decisão humana.

**Uso de IA:**
- **Modelo:** Claude Code / Fable 5.
- **Contexto consumido:** ~65k tokens (~6.5% de janela de 1M).
- **Prompt inicial (verbatim):** "vamos fechar as decisões 3 e 4 juntas como falado. quero passar ideia por idea e decidir o que precisa"
- **Iterações até aceitar:** 4 (doc da 2.2: 1 rodada de correção com 6 pontos; doc da 2.3: 2 rodadas — unificação da fórmula/notação do Q/sinal, depois colapso de itens duplicados e interpretação do Q).
- **Erros da IA:** descreveu os mercados de CPI do poly como thresholds (">X%") quando são buckets exatos (PMF); introduziu um `p_FF` inexistente no fallback binário da 2.3 (do ZQ sai esperança, não probabilidade); duplicou a fórmula da surpresa em dois itens do doc; notação do Q imprecisa (`P · (β × surpresa)`) e sem interpretação do portfólio long-short.
- **Decisões escaladas:** 9 (nova, aberta); 3 e 4 parcialmente fechadas (views 2.2 e 2.3) por instrução humana explícita.
- **Tags:** —

## 2026-07-08 (sessão 3) — Felipe

**Feito:**
- Sessão de discussão (sem código). Explicada a Decisão 3 (mapeamento cenário→ativo): o que é, opções da forma da regressão (Δprob vs. dummy de resolução vs. surpresa macro realizada), trade-offs, onde entra no BL (alimenta a magnitude de Q, não P/Ω) e que partes toca.
- **Reframe conceitual da Decisão 3 registrado (decisão do Felipe):** descartada como objeto a **tabela central de sensibilidades** (grade única cenários × ativos que traduziria prob crua). É redundante — nunca alimentamos prob crua ao BL para uma tabela central traduzir. Na arquitetura real cada view da Camada 1 monta P e Q sozinha a partir do histórico do seu próprio mercado poly. A conta de sensibilidade (β) **não some**, mas passa a ser interna a cada view/família.
- **Colapso Decisão 3 ↔ Decisão 4 registrado:** "estimar magnitude" (3) e "fabricar Q da probabilidade" (4) viram quase a mesma operação por família; devem ser fechadas juntas, por família. Adicionadas notas cruzadas nas duas seções.
- Ajustada a frase da "Consequência p/ o planejamento" (Decisão 4) que dizia que o β vinha de um "mapeamento cenário→ativo" central — agora reflete que a sensibilidade é interna a cada view.

**Quebrou / aprendido:**
- Nada de código. Aprendizado: a tabela central de sensibilidades era incompatível com a arquitetura "cada view monta seu P/Q"; Decisões 3 e 4 não são independentes — colapsam por família.

**Pendente:**
- Decisão 3 segue 🔴: descarte da tabela central está registrado, mas a **forma da regressão por família** (Δprob vs. dummy de resolução) segue aberta — fecha junto com a Decisão 4.
- Decisão 4 segue 🔴 — fechar view a view / por família (próximo passo sugerido: 2.2 Inflação).
- Decisões 5 e 6 seguem abertas.

**Uso de IA:**
- **Modelo:** Claude Code / Opus 4.8.
- **Contexto consumido:** ~75k tokens (~38% de janela de 200k).
- **Prompt inicial (verbatim):** "preciso fechar as decisões 3 e 4. comece me explicando a 3, as opções que tenho, seus trade offs, onde ela entra do black littermann e que partes do projeto ela engloba?"
- **Iterações até aceitar:** 1 (explicação da Decisão 3 aceita; registro do reframe feito conforme decisão conceitual passada pelo Felipe).
- **Erros da IA:** nenhum.
- **Decisões escaladas:** reframe da Decisão 3 (descarte da tabela central) e colapso 3↔4 registrados; nenhuma fechada como 🟢.
- **Tags:** —

## 2026-07-08 (sessão 2) — Felipe

**Feito:**
- Sessão de discussão sobre a Decisão 4 (sem código). Explicada a decisão como um todo (ponte prob→Q, template por view, Famílias A/B).
- **Correção de nomenclatura + registro:** identificada colisão do termo "Camada 2" nos documentos. No `Mapa_de_camadas.md`, **Camada 2 = camada tática**; no `FELIPE_arquitetura_BL.md` e na Decisão 3, "Camada 2" = mapeamento cenário→ativo. O que o grupo congelou (por exigir dados de alta frequência que a granularidade da API não dá) é a **camada tática**, não o mapeamento de sensibilidades — que **segue de pé**.
- Correções aplicadas no `Decisoes_pendentes.md`: título da Decisão 3 sem o "(Camada 2)" ambíguo; nota de status deixando claro que o mapeamento não está congelado (é fonte das β da Família A); célula do Fed ajustada; **parágrafo "Consequência p/ o planejamento" da Decisão 4 reescrito** com a premissa certa (congelado = tática; mapeamento vivo → magnitudes das views estruturais não bloqueadas).
- Implicação registrada: com o mapeamento vivo, a Família A inteira tem fonte de β; o que separa as views é o trabalho próprio de cada uma (cestas na 2.4, view-vs-prior na 3.1, magnitude frágil na 1.2).

**Quebrou / aprendido:**
- Nada de código. Aprendizado: as entradas anteriores do LOG (07/07 e 07/08 sessão 1) atribuíram o congelamento à "Camada 2 (decisão 3)" por causa da colisão de nomes — o correto é **camada tática congelada**. Histórico das entradas antigas preservado; correção fica registrada aqui.

**Pendente:**
- Decisão 4 segue aberta — próximo passo: fechar view a view, começando pela **2.2 Inflação**.
- Decisão 3 (mapeamento cenário→ativo) segue aberta (forma da regressão), mas **não congelada**.
- Decisões 5 e 6 seguem abertas.

**Uso de IA:**
- **Modelo:** Claude Code / Opus 4.8.
- **Contexto consumido:** ~70k tokens (~35% de janela de 200k).
- **Prompt inicial (verbatim):** "preciso fechar a decisão 4. Acho bom passarmos por cada uma das ideias para também relembrar como elas funcionam e decidir juntos como as views serão formadas por elas. Comece explicando de forma rápida e consisa a decisão 4 como um todo"
- **Iterações até aceitar:** 3 (explicação da Decisão 4 aceita; depois 2 rodadas de correção sobre qual camada estava congelada, até a IA acertar que é a tática e reescrever o registro).
- **Erros da IA:** 1 — inverteu inicialmente o que estava congelado (afirmou que o mapeamento de sensibilidades estava frozen; na verdade é a camada tática). Corrigido após o usuário apontar.
- **Decisões escaladas:** nenhuma fechada. Correção de registro nas Decisões 3 e 4 (nomenclatura + parágrafo de consequência).
- **Tags:** —

## 2026-07-08 — Felipe

**Feito:**
- Sessão de discussão sobre a Decisão 4 (probabilidade → Q). Insight-chave do usuário: a Camada 1 tem múltiplas views, cada uma com a própria análise/âncora, então a Decisão 4 **não é uma fórmula única** — é um template por view.
- Reescrita da seção 4 do `Decisoes_pendentes.md` com o reframe (status segue 🔴 aberta): 5 views estruturais agrupadas em 2 famílias.
  - **Família A (divergência + sensibilidade):** 2.3 Fed, 2.2 inflação, 2.4 eleitoral, 3.1 sentimento macro — esqueleto comum `Q = sens × (prob_poly − prob_mercado)`, forma relativa.
  - **Família B (série temporal):** 1.2 momentum — não encaixa no template de divergência.
  - Tabelas por view (âncora, sinal do poly, Q natural, o que falta decidir) + 3 perguntas de reunião.
- Consequência registrada: o "Camada 2 congelada" só bloqueia parte das views — **2.2 (mecânica via duration) e 2.3 (beta estreita) destravam sem a Camada 2**.

**Quebrou / aprendido:**
- Nada quebrou (sessão sem código). Aprendizado: a Decisão 4 deve ser especializada por view, não global.

**Pendente:**
- Decisão 4 segue aberta — agora estruturada como template por view; falta a reunião responder as 3 perguntas (adotar template Família A? quais views no v1? 1.2 estrutural ou tático?).
- Parâmetros numéricos por view (β, duration, valor justo da cesta) ainda dependem de decisão humana.
- Decisões 3, 5 e 6 seguem abertas (3 congelada até a reformulação da Camada 2).

**Uso de IA:**
- **Modelo:** Claude Code / Opus 4.8.
- **Contexto consumido:** ~50k tokens (~25% de janela de 200k).
- **Prompt inicial (verbatim):** "Das decisões pendentes quero resolver a 4 agora. me explique o que tenho que escolher, as opções e trade-offs"
- **Iterações até aceitar:** 2 (explicação inicial das opções; usuário reformulou com o insight de "template por view" e a explicação foi refeita e aceita).
- **Erros da IA:** nenhum.
- **Decisões escaladas:** Decisão 4 reescrita/reestruturada (mantida em aberto; nenhuma fechada).
- **Tags:** —

## 2026-07-07 — Felipe

**Feito:**
- Sessão de discussão (sem código novo): explicação detalhada das decisões 4 e 8, do cálculo completo do Black-Litterman (π, P, Q, Ω, posterior, pesos) e dos trade-offs de cada opção.
- **Decisão 8 fechada em reunião** e registrada em `Decisoes_pendentes.md`:
  - Parte A: **Σ amostral** no passo final (caso neutro limpo: confiança zero → `w_mkt`; encolhimento por incerteza fica a cargo do Ω reativo).
  - Parte B: **B1 — irrestrito** (fórmula fechada, aceita short/desvio de soma = 1; reavaliar se o backtest mostrar pesos extremos). Alternativas B2/B3/B4 mantidas no arquivo como referência.
- Docstring de `optimal_weights` em `src/bl_optimizer.py` atualizado: TODO(DECISAO-8) → decisão fechada.
- Limpeza: seção 8 estava duplicada em `Decisoes_pendentes.md` (usuário removeu a duplicata; sobra de linha "Decisão" consolidada na edição).

**Quebrou / aprendido:**
- Nada quebrou. Alinhamento do time: Camada 2 (decisão 3) fica de fora por ora — vai passar por reformulação; foco apenas na camada estrutural.

**Pendente:**
- Decisão 4 (probabilidade → Q) segue aberta — é a única que bloqueia o bridge e agora deve ser discutida sem depender da Camada 2 (magnitudes não virão da regressão da decisão 3 por enquanto).
- Decisões 3, 5 e 6 seguem abertas (3 congelada até a reformulação da Camada 2).

**Uso de IA:**
- **Modelo:** Claude Code / Fable 5.
- **Contexto consumido:** ~55k tokens (~25% de janela de 200k).
- **Prompt inicial (verbatim):** "Sentei e discuti com o meu grupo sobre o que iriamos fazer com as decisões pendentes. Olhando o que faltava, decidimos que eu iria ficar responsável por entender e fechar as decisões 4 e 8, por que fazem parte das minhas responsabilidades. Me explique de forma consisa e rápida o que precisamos decidir na 4."
- **Iterações até aceitar:** 1 (explicações aceitas sem rodada de correção; uma iteração extra a pedido do usuário para aprofundar o cálculo do BL).
- **Erros da IA:** nenhum (um Edit falhou por edição concorrente do usuário no arquivo, não por erro do modelo).
- **Decisões escaladas:** — (nenhuma nova; decisão 8 foi fechada por instrução humana explícita).
- **Tags:** —

## 2026-07-05 — Felipe

**Feito:**
- Esqueleto do otimizador BL (`src/bl_optimizer.py`): reverse optimization (`implied_equilibrium_returns`), posterior He & Litterman (`bl_posterior` → μ_bl e Σ_bl) e pesos mean-variance irrestritos (`optimal_weights`). Funções puras, validação de shapes, sem dados/parâmetros hardcoded.
- Testes sintéticos (`tests/test_bl_optimizer.py`, 4 testes, todos passando): round-trip da reverse optimization, confiança ~0 → posterior = prior (e Σ_bl → (1+τ)Σ), confiança total → P·μ_bl = Q, tilt monotônico com a confiança. `python tests/test_bl_optimizer.py` roda testes + demo ponta a ponta.

**Quebrou / aprendido:**
- Primeira versão do teste de monotonicidade assumia tilt positivo, mas o prior de equilíbrio já implicava spread (2,1%) maior que a view (2%) — view era baixista em relação ao prior. Corrigido usando view de 5% no teste/demo.

**Pendente:**
- Interface proposta (arrays numpy com shapes documentados no docstring de `bl_optimizer.py`, ordem de ativos definida pelo dataset) precisa de ok do Paulo e da Lia.
- Nova decisão registrada: item 8 em `Decisoes_pendentes.md` (Σ amostral vs Σ_bl no passo de pesos + restrições da carteira).
- τ e δ reais dependem de decisão; os dos testes são sintéticos e marcados como tal.
