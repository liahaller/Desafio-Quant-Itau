# LOG

Histórico de sessões. Cada entrada: data, dono da sessão, o que foi feito, o
que quebrou, o que ficou pendente. Ver ritual de sessão em `CLAUDE.md`,
seção 3.

---

## 2026-07-04 — Lia

**Feito:**
- Criados `Decisoes_pendentes.md` e `LOG.md` (não existiam no repositório
  até agora).
- Registradas em `Decisoes_pendentes.md` as Decisões 3, 4 e 5 (definição de
  "surpresa"/PEAD, forma funcional do Ω reativo, tratamento de conflito
  entre fontes), com contexto, perguntas e trade-offs — para servir de
  pauta na reunião de 07/jul/2026. Também registradas, com numeração
  provisória, as Decisões 6 e 7 (gatilho de salto event-driven e forma de
  cálculo da velocidade de ajuste), que apareciam descritas no norte geral
  mas sem decisão fechada.
- Criado esqueleto do módulo de código (`lia/`): `omega.py`
  (`SinaisOmega`, `calcular_omega`) e `camada_tatica.py`
  (`detectar_surpresa_pead`, `detectar_salto_event_driven`,
  `calcular_velocidade_ajuste`), todas as funções matemáticas levantando
  `NotImplementedError` com referência à decisão pendente correspondente —
  nenhum valor numérico ou fórmula foi inventado. Testes mínimos em
  `lia/tests/` que hoje só verificam esse comportamento.

**Quebrou:** nada.

**Pendente:**
- Fechar Decisões 3, 4, 5, 6 e 7 na reunião de 07/jul/2026.
- Reconciliar `Decisoes_pendentes.md` com decisões de Felipe/Paulo (a
  numeração em `LIA_risco_relatorio.md` sugere que já existem Decisões 1 e
  2 fora do escopo de Lia).
- Depois da reunião: escrever o doc formal de especificações da Semana 1
  (deadline 13/jul) e implementar de fato `calcular_omega` e as funções da
  camada tática (deadline 20/jul), substituindo os placeholders.

## 2026-07-04 — Lia (correção)

**Feito:**
- O `Decisoes_pendentes.md` criado antes nesta mesma data foi montado do
  zero, sem base no arquivo real da equipe — numeração e conteúdo eram só
  uma extrapolação do `LIA_risco_relatorio.md`. A Lia recebeu do Felipe,
  via WhatsApp, o `Decisoes_pendentes.md` oficial do grupo (com decisões
  numeradas 1–7 e a Decisão 1, universo de ativos, já fechada 🟢).
- `Decisoes_pendentes.md` substituído pelo conteúdo oficial do Felipe.
  Decisões 1–4 (dele/Paulo) mantidas exatamente como recebidas, sem
  edição. Nas decisões 5 (surpresa/PEAD), 6 (Ω reativo) e 7 (convergência
  entre fontes) — que são do escopo de Lia — adicionado um bloco "Contexto
  para a reunião" com as perguntas/trade-offs já levantados, sem propor
  resposta. Adicionadas as Decisões 8 (gatilho de salto event-driven) e 9
  (forma de cálculo da velocidade de ajuste), que não estavam neste doc.
- Referências `TODO(DECISAO-N)` em `lia/omega.py`, `lia/camada_tatica.py`
  e nos testes atualizadas pra numeração oficial (6 = Ω, 7 = convergência
  de fontes, 5 = surpresa, 8 = event-driven, 9 = velocidade de ajuste).

**Quebrou:** nada — só renumeração de referências, nenhuma função tinha
  sido implementada ainda.

**Pendente:** mesmo da entrada anterior; numeração agora alinhada com o
  doc oficial do time.

## 2026-07-06 — Lia

**Feito:**
- Criada a base da matriz de relação tridimensional da camada tática
  (`lia/matriz_relacao.py`): ativos × mercados do Polymarket × tempo,
  com **distance correlation** por célula, seguindo a referência do
  relatório NEXUS (Desafio Quant AI 2025) indicada pela Lia. Contém
  `distance_correlation`, a estrutura `MatrizRelacao3D` (com `consultar`
  e `fatia_em`) e `calcular_matriz_relacao` (janelas móveis; `janela`
  obrigatória por argumento, sem default — o valor é decisão pendente).
- Testes sintéticos com resultado conhecido em
  `lia/tests/test_matriz_relacao.py`: dcor(x,x)=1, invariância afim,
  série constante → 0, captura de relação não-linear (y=x² com Pearson
  ≈ 0), NaN propagado, dimensões/alinhamento de datas da matriz 3D.
- Registrada a Decisão 10 em `Decisoes_pendentes.md` (status 🟡): a
  direção metodológica (estrutura 3D + dcor) foi dada pela Lia; janela,
  passo, série do Polymarket e a fronteira com a Decisão 3 (Camada 2 do
  Felipe) ficam para confirmar em reunião.

**Quebrou:** nada. Ressalva: Python não está instalado nesta máquina, os
  testes não puderam ser executados localmente — rodar `pytest lia/tests`
  num ambiente com numpy/pandas/pytest antes de considerar pronto.

**Pendente:**
- Fechar em reunião os itens em aberto da Decisão 10 (janela, passo,
  série do Polymarket, fronteira com Camada 2).
- Demais pendências das entradas anteriores (Decisões 5–9).

## 2026-07-08 — Lia

**Feito:**
- Merge da `main` no branch `Lia` concluído (commit `17470e3`). Conflitos
  em `Decisoes_pendentes.md` resolvidos por instrução da Lia: o arquivo
  ficou **idêntico ao da main** (Decisões 1, 2 e 7 fechadas; Decisão 8
  agora é o passo final do otimizador, do Felipe). Consequência: as
  antigas seções 8 (gatilho de salto), 9 (velocidade de ajuste) e 10
  (matriz 3D) saíram do doc.
- Decisão 6 (Ω reativo): a reunião do grupo delegou a decisão à Lia.
  Registrado no doc (status 🟡) o protocolo proposto para fechá-la:
  estrutura multiplicativa com volume como veto, confiança escalando o
  baseline de He-Litterman, e parâmetros (janela, decaimento, threshold)
  escolhidos por teste de monotonicidade confiança → erro realizado.
- Criado o harness de calibração (`lia/calibracao_omega.py`): definições
  de erro realizado (`erro_realizado_futuro`, `erro_vs_resolucao`),
  scores candidatos (`score_estabilidade`, `score_proximidade`
  linear/exponencial, `portao_volume`, `combinar_por_rank`) e o critério
  de escolha (`avaliar_monotonicidade`, `comparar_candidatas`). Funções
  puras, sem acesso a dados, sem defaults nos parâmetros do modelo.
  Testes sintéticos em `lia/tests/test_calibracao_omega.py`.
- Python 3.12.10 instalado nesta máquina (winget, em
  `%LOCALAPPDATA%\Programs\Python\Python312`, fora do PATH) com
  numpy/pandas/pytest. A suíte completa (24 testes) rodou pela primeira
  vez: **todos passaram** — resolvida a ressalva da entrada de 06/07.

**Quebrou:** primeira execução do pytest teve 4 falhas + 1 erro, todos no
  código novo: (a) `pandas.corr(method="spearman")` depende de scipy —
  trocado por Pearson sobre ranks, equivalente e sem dependência nova;
  (b) o nome `teste_monotonicidade` colidia com o padrão de coleta do
  pytest — renomeado para `avaliar_monotonicidade`; (c) asserção com
  direção invertida num teste da forma exponencial. Corrigido na sessão.

**Pendente:**
- Lia ratificar a estrutura proposta da Decisão 6, escolher a definição
  de erro realizado e, após a calibração, a normalização final para
  (0,1].
- Rodar a calibração de verdade: depende do histórico do Polymarket via
  pipeline do Paulo (confirmar com ele se **volume** vem junto — o
  `/prices-history` só entrega preço).
- Os `TODO(DECISAO-8/9/10)` em `lia/camada_tatica.py` e
  `lia/matriz_relacao.py` apontam para seções que saíram do doc no merge
  (e o nº 8 agora é outra decisão, do Felipe) — decidir se os itens
  táticos voltam ao doc e com que numeração.
- Python fora do PATH — usar caminho completo ou ajustar o PATH.

**Uso de IA:**
- **Modelo:** Claude Code / Sonnet 5 (início da sessão) e Fable 5 (da
  discussão da Decisão 6 em diante, troca via `/model`).
- **Contexto consumido:** ~35% da janela (~70k tokens, estimativa).
- **Prompt inicial (verbatim):** `git merge main`
- **Iterações até aceitar:** merge: 2 (a primeira proposta de resolução
  fundia conteúdo das duas versões; a Lia corrigiu para "igual ao da
  main"). Harness: 1 (aceito de primeira; houve 1 rodada interna de
  correção após a primeira execução dos testes).
- **Erros da IA:** (1) supôs que o Spearman do pandas não dependia de
  scipy — 3 testes quebraram; (2) nomeou função com prefixo que o pytest
  coleta como teste; (3) asserção invertida num teste; (4) na resolução
  do merge, a primeira proposta assumiu que era para preservar conteúdo
  das duas versões, quando a intenção era manter só o da main.
- **Decisões escaladas:** 6 (contexto e protocolo de calibração
  registrados; decisão segue aberta, delegada à Lia).
- **Tags:** —

## 2026-07-20 — Lia

**Feito:**
- Lidos `Para_Paulo_e_Lia.md` e `pauta_reuniao_outros.md` (adicionados
  pela Lia nesta sessão). Confirmado que a Decisão 10 já registrada
  (camada tática reformulada realocada ao Felipe; módulo da Lia
  reduzido a "Ω reativo · Relatório") bate com o combinado em reunião.
  Sinalizados dois pontos que ficam para a Lia decidir, sem ação
  tomada: (a) destino de `lia/camada_tatica.py` e
  `lia/matriz_relacao.py` — código da camada tática antiga, que o
  desenho novo do Felipe não parece reaproveitar; (b) a tabela de posse
  no `CLAUDE.md` ainda lista a camada tática como módulo da Lia,
  desatualizada frente à Decisão 10.
- Levantamento da API do Polymarket (CLOB, Gamma, Data API) para checar
  se dá pra obter volume histórico por mercado — dependência da
  calibração da Decisão 6. Resultado: não há endpoint pronto de volume
  histórico; `/prices-history` (CLOB) só dá preço; Gamma só dá volume
  agregado atual/24h; o caminho viável é agregar trades individuais do
  `/trades`/`/activity` da Data API. Registrado em
  `Decisoes_pendentes.md`, seção 6.
- Avaliado se esse levantamento permite fechar a Decisão 6: **não**. A
  fonte de volume é tecnicamente acessível, mas o protocolo da Decisão
  6 amarra os parâmetros numéricos (janela, decaimento, threshold) a um
  teste de monotonicidade sobre dado histórico real, que ainda não
  existe no pipeline (o Paulo precisa implementar a agregação de trades
  primeiro). Fechar agora exigiria inventar esses números — proibido
  pela regra 1 do `CLAUDE.md`. Decisão 6 segue 🟡, sem fechamento.

**Quebrou:** nada.

- Destino de `lia/matriz_relacao.py` esclarecido pela Lia: apoiar a
  Decisão 3 (Camada 2 do Felipe) como evidência exploratória de "qual
  mercado do Polymarket tem mais relação com qual ativo" — registrada
  a Decisão 9 em `Decisoes_pendentes.md` (janela, passo e série do
  Polymarket ainda em aberto, sem default inventado).
- Testada a API do Polymarket na prática (Bash local): `clob.polymarket.com`
  e `gamma-api.polymarket.com` **não resolvem pelo DNS padrão desta
  rede** (NXDOMAIN), mas resolvem normalmente via DNS público (8.8.8.8)
  — bloqueio/filtro do resolver local, não domínio fora do ar.
  Contorno funcional: `curl --resolve <host>:443:<ip>` (ou configurar
  DNS público). Achado relevante pro Paulo montar o pipeline.
- Confirmado que `/prices-history` (CLOB) funciona normalmente para
  mercados **ativos** (testado com dado real de um mercado do Fed,
  jul/2026 — série diária de ~120 pontos). Para o mercado presidencial
  de 2024 (resolvido), o mesmo endpoint devolveu histórico **vazio**
  em várias combinações de parâmetros (`interval=max`, `1d`, `1w`,
  `1m`; `startTs`/`endTs` explícitos deram erro "interval too long").
  Indício de que mercados resolvidos/antigos podem não ficar
  disponíveis por esse endpoint do jeito testado — bate com a
  "condição crítica" já sinalizada em `Para_Paulo_e_Lia.md` (bid/ask
  histórico das views 2.4/3.1/C/E/G). Investigação aprofundada é
  mandato do Paulo; não insisti além disso pra não duplicar o
  trabalho dele.
- Rodado um demo exploratório (`scratchpad`, fora do repositório —
  não é pipeline oficial nem calibração final) com dado 100% real:
  retornos das 9 ETFs via yfinance × série do mercado ativo do Fed via
  CLOB, `calcular_matriz_relacao` com duas janelas candidatas (10 e 20
  dias). Resultado: o ranking de relação muda de forma relevante entre
  as duas janelas (XLF lidera com janela 10, XLV com janela 20) —
  evidência concreta de por que o parâmetro não pode ser chutado
  (reforça a Decisão 9).

**Pendente:**
- Passar o levantamento de API (DNS + comportamento de mercados
  resolvidos) para o Paulo — ele decide como resolver.
- Depois que o volume histórico estiver disponível: rodar
  `lia/calibracao_omega.py` com dado real e só então fechar a Decisão
  6.
- Fechar a Decisão 9 (janela/passo/série do Polymarket da matriz de
  relação) em reunião ou com critério de dado, como foi feito na
  Decisão 6.
- Avaliar se/quando atualizar a tabela de posse no `CLAUDE.md`.
- Itens 2–5 da lista "LIA" em `Para_Paulo_e_Lia.md`: validar
  `diagnostics`, nota de interação Ω ↔ camada tática, SWZ no
  relatório.

**Uso de IA:**
- **Modelo:** Claude Code / Fable 5.
- **Contexto consumido:** ~35% da janela, estimativa.
- **Prompt inicial (verbatim):** "esses arquivos que eu adicionei devem
  ser levados em consideração antes de fazer qualquer coisa. Decidimos
  passar a camada tática para o felipe. o que da minha parte eu posso
  fazer agora?"
- **Iterações até aceitar:** 1 (levantamento de API aceito de primeira;
  a IA recusou fechar a Decisão 6 por falta de dado real e a recusa foi
  mantida, sem repetição de pedido); demo da matriz aceito de primeira
  após a Lia esclarecer o objetivo via pergunta de esclarecimento.
- **Erros da IA:** nenhum.
- **Decisões escaladas:** 6 (dependência de volume tornada concreta;
  decisão segue aberta) e 9 (nova — matriz de relação; contexto e
  achados registrados, decisão aberta).
- **Tags:** —

## 2026-07-30 — Lia

**Feito:**
- Commit das mudanças pendentes da branch Lia (commit `124d478`):
  `Decisoes_pendentes.md`, `LOG.md`, `Para_Paulo_e_Lia.md`,
  `pauta_reuniao_outros.md`. Os diretórios `lia/__pycache__/` e
  `lia/tests/__pycache__/` ficaram de fora de propósito (bytecode
  gerado; não versionar). O repo não tem `.gitignore`.
- Merge da `origin/main` na branch Lia (commit `f473297`), autorizado
  explicitamente pela Lia sobrepondo a regra 6 do `CLAUDE.md` ("nunca
  faz merge entre branches"). A IA sinalizou o conflito com a regra e
  só prosseguiu após confirmação. Merge limpo, sem conflitos: trouxe a
  atualização do `CLAUDE.md` (regra 1 agora tria decisões em 3
  categorias em vez de parar em qualquer dúvida; tabela de posse reduz
  o módulo da Lia a "Ω reativo · Relatório", com a camada tática
  realocada ao Felipe; regra 4 pede respostas concisas). O
  `Decisoes_pendentes.md` da Lia foi preservado — a main não o tocou
  desde o ancestral comum.

**Quebrou:** nada.

**Pendente:**
- `git push` da branch Lia não foi feito — commit e merge estão só
  locais.
- `__pycache__` seguem untracked; sem `.gitignore` (sugerida a criação,
  não executada — fica a critério da Lia).
- Continuam as pendências da sessão de 20/07 (Decisão 6 esperando
  volume real do Paulo; Decisão 9 aberta; itens 2–5 da lista "LIA" em
  `Para_Paulo_e_Lia.md`).

**Uso de IA:**
- **Modelo:** Claude Code / Opus 4.8 (sessão iniciou em Sonnet 5,
  trocada para Opus 4.8 logo no começo).
- **Contexto consumido:** ~15% da janela, estimativa.
- **Prompt inicial (verbatim):** "faz o commit das minhas mudanças na
  minha branch Lia"
- **Iterações até aceitar:** 1 (commit aceito de primeira; o merge
  exigiu uma confirmação de override da regra 6, não uma correção de
  resultado).
- **Erros da IA:** nenhum.
- **Decisões escaladas:** — (nenhuma decisão nova em
  `Decisoes_pendentes.md`; a autorização de merge foi pontual, não
  metodológica).
- **Tags:** —

## 2026-07-30 — Lia (fechamento da sessão de 20/07)

**Feito:**
- Sessão de 20/07 (levantamento de API, Decisão 9, demo da matriz de
  relação, mensagem de achados preparada para o Paulo) retomada e
  encerrada. Lia confirmou que já conversou com o Paulo sobre os
  achados — conteúdo/resultado da conversa não relatado nesta sessão.
- Revisado estado atual de `Decisoes_pendentes.md` e `LOG.md` antes de
  fechar: nenhuma decisão nova surgiu.

**Quebrou:** nada.

**Pendente:** as mesmas da entrada de 20/07 (Decisão 6 esperando volume
  real do Paulo; Decisão 9 aberta; itens 2–5 da lista "LIA" em
  `Para_Paulo_e_Lia.md`).

**Uso de IA:**
- **Modelo:** Claude Code / Fable 5.
- **Contexto consumido:** ~40% da janela, estimativa (sessão contínua
  desde 20/07).
- **Prompt inicial (verbatim):** "ja conversamos. finalizar sessao"
- **Iterações até aceitar:** 1.
- **Erros da IA:** nenhum.
- **Decisões escaladas:** —.
- **Tags:** —

## 2026-08-05 — Lia

**Feito:**
- Respondidas as quatro perguntas do Felipe em
  `Dump/trocas/Pergunta_Lia_omega_volume.md` (branch `Felipe`) — resposta
  em `RESPOSTA_Pergunta_Lia_omega_volume.md` (raiz, branch `Lia`):
  1. **Volume (destrava o G5 do Paulo):** série em passo de 12h com
     `notional_usd` + `n_trades` por slot e `t_cobertura_min` por mercado,
     escopo nas views ativas (2.2, 2.3, B). Total lifetime recusado por
     lookahead (contém volume posterior à data da decisão) e por ser
     constante no tempo.
  2. **`diagnostics`:** lista de campos fechada do meu lado — série crua da
     janela + escalares de qualidade + `dias_ate_evento` + `soma_faixas`;
     desconhecido = NaN, nunca 0.
  3. **δ:** aceito fechar junto com a escala do Ω, com correção de alvo —
     δ = 3,0 é medido, não é parâmetro livre; o que precisa fechar junto é
     o **teto de alavancagem**, que hoje faz o trabalho do Ω.
  4. **Régua `Ω = c·diag(P·τΣ·Pᵀ)`:** aceita — é a mesma âncora do
     protocolo de 08/07. Sinalizada a **convenção invertida** (`c_felipe =
     1/c_lia`) e proposta a entrega como vetor `c` + máscara `ativa`, com
     veto removendo a view em vez de virar `c` grande.
- Achado do Felipe (faixas de mercados de buckets não somam 1) aceito como
  **quarto ingrediente candidato** (`score_coerencia = −|soma_faixas − 1|`),
  sujeito ao mesmo teste de monotonicidade dos outros — sem exceção ao
  protocolo.
- `Decisoes_pendentes.md`: Decisão 6 ganhou o bloco de especificação de
  interface e insumos. **A decisão continua aberta** — o que foi
  especificado são entradas e saída, não a forma funcional.

**Quebrou:** nada.

**Observações para os donos:**
- **Felipe:** o argumento `confianca` de `omega_fallback` (`src/market_inputs.py`)
  tem nome invertido em relação ao que o número faz (>1 = *menos* confiança).
  Sugerida a renomeação para `incerteza`/`mult_incerteza`; módulo dele,
  decisão dele — não editado.
- A numeração de `Decisoes_pendentes.md` **divergiu entre branches**: as
  seções 9 e 10 da branch `Felipe` (maratona de 04/08 e decisões do
  backtest de 05/08) não são as mesmas da branch `Lia` (9 = matriz de
  relação). Por isso o registro desta sessão entrou como contexto na
  Decisão 6, sem criar seção nova — reconciliar a numeração é tarefa de
  merge, não desta sessão.

**Pendente:**
- Enviar `RESPOSTA_Pergunta_Lia_omega_volume.md` ao Felipe e ao Paulo
  (o item 1 é o que destrava o G5).
- `c_i` real continua dependendo do volume histórico (G5). Se atrasar,
  entregar o `c` sem o portão de volume — a estrutura multiplicativa
  permite acrescentar o portão depois sem mudar a interface.
- Reunião: escala do `c` + teto de alavancagem na mesma conversa.
- Decisão 9 (matriz de relação) segue aberta.
- `git push` da branch `Lia` continua não feito (pendência desde 30/07).

**Uso de IA:**
- **Modelo:** Claude Code / Opus 5.
- **Contexto consumido:** ~25% da janela, estimativa.
- **Prompt inicial (verbatim):** "responda a pergunta desse arquivo"
  (seguido do conteúdo de `Pergunta_Lia_omega_volume.md` colado).
- **Iterações até aceitar:** 1 — a IA levantou o contexto (arquivo do
  Felipe, `market_inputs.py`, G5 do Paulo, protocolo de 08/07), apresentou
  três escolhas com recomendação (granularidade do volume, tratamento do
  veto, formato do `diagnostics`), a Lia confirmou as três e a resposta foi
  escrita de uma vez.
- **Erros da IA:** nenhum.
- **Decisões escaladas:** 6 (especificação de interface e insumos
  registrada; forma funcional segue aberta). Teto de alavancagem e escala
  do `c` remetidos à reunião, sem seção nova por causa da divergência de
  numeração entre branches.
- **Tags:** `[PROMPT-CHAVE]` — a resposta depende de a IA reconstruir o
  contexto cruzando três branches (`Felipe`, `Paulo`, `Lia`); bom candidato
  ao teste de reprodutibilidade.

## 2026-08-07 — Lia (segunda rodada com o Felipe)

**Feito:**
- Respondido o retorno do Felipe ("o `diagnostics` está no ar") em
  `RESPOSTA2_Felipe_diagnostics_6a.md` (raiz, branch `Lia`):
  1. **Decisão 6a (colapso PMF→p):** aceita a saída 1 — o colapso é
     calculado do lado da Lia a partir de `serie_janela`;
     `dp_variacao_janela` fica `NaN` de propósito. Forma funcional **não**
     fechada: grade de duas candidatas (variação total entre PMFs
     consecutivas · desvio-padrão das diferenças de `E[·]`), decidida pelo
     teste de monotonicidade.
  2. **Premissa nova e não óbvia:** o colapso roda sobre a PMF
     **renormalizada**. Sobre a PMF crua, ele misturaria movimento de
     opinião com desarranjo do livro, e a régua multiplicativa puniria a
     mesma coisa duas vezes — `score_estabilidade` e `score_coerencia`
     ficariam correlacionados e isso apareceria no teste como confirmação
     mútua, não como erro. Era esse o motivo de pedir `soma_faixas` cru
     junto da série crua.
  3. **Pedido de interface:** `c` e `ativa` entregues como `dict[str, ...]`
     chaveados pela view, em vez de vetores posicionais — a
     `aplicar_veto` casa os índices contra uma lista com `None`
     intercalados da cascata, e deslocamento de índice não levanta
     exceção, produz carteira plausível e errada. Decisão dele (módulo
     dele); alternativa oferecida: manter vetor + validação por nomes.
  4. **Verificação pedida a ele:** com `idade_ultimo_ponto_h = 0.0`,
     confirmar que o último ponto da `serie_janela` é o último slot
     **fechado antes** do timestamp de decisão, não o slot que o contém —
     no segundo caso há lookahead de meio slot, invisível no retorno e
     capaz de inflar a estabilidade medida.
  5. **Dimensionamento com k = 1 view:** o teste de monotonicidade
     continua válido (é sobre slots no tempo, não entre views); o que fica
     sem amostra é a ordenação *entre* views. Com uma view, `c` e teto de
     alavancagem são a mesma alavanca — reforça a ordem já acordada.
  6. **Ressalva registrada antes do resultado:** como `c ≥ 1`, o Ω só
     melhora o backtest por subtração (no limite a carteira vira o
     benchmark). Se depois do `c` a carteira ainda perder do SPY, o
     problema é a view 2.2, não o dimensionamento de risco.
- Confirmados sem ressalva os pontos 1a (medição na série crua, antes do
  `carry_missing`/`daily_preopen`), 1b (truncar `n_slots_esperados` pelo
  nascimento do mercado) e 1c (`janela_slots = None`).
- Registrada a semântica corrigida do campo de buracos: mede **quanta
  imputação houve**, não quanto dado faltou ao modelo — o `carry_missing`
  roda entre a série crua e a view.
- `Decisoes_pendentes.md`: nova subseção **6a** dentro da Decisão 6 (lugar
  resolvido, forma funcional aberta).

**Quebrou:** nada.

**Aceito pelo Felipe nesta rodada** (do que a Lia pediu em 05/08):
`omega_fallback(..., confianca=)` renomeado para `incerteza=`; veto
implementado como view que sai (`bl_integration.aplicar_veto`), não como Ω
gigante; G5 despachado ao Paulo com a spec de volume transcrita; ordem
"entra o `c` → mede Σ|w| → decide o teto" aceita para a reunião.

**Pendente:**
- Implementar o colapso PMF→p (duas candidatas) e rodar o teste de
  monotonicidade nos três ingredientes com dado (estabilidade,
  proximidade, coerência) — a 2.2 é a única view com dado hoje.
- Entregar `c` + `ativa` sem o portão de volume se o G5 demorar.
- `c_i` completo segue dependendo do G5 (volume) com o Paulo.
- Reunião: escala do `c` + teto de alavancagem; forma funcional da 6a
  depende da calibração, não de reunião.
- Decisão 9 (matriz de relação) segue aberta; `git push` da branch `Lia`
  continua não feito.

**Uso de IA:**
- **Modelo:** Claude Code / Opus 5.
- **Contexto consumido:** ~40% da janela, estimativa (sessão contínua com
  a rodada de 05/08).
- **Prompt inicial (verbatim):** "o felipe me respondeu com essa mensagem:"
  (seguido da mensagem dele colada).
- **Iterações até aceitar:** 1 — duas escolhas apresentadas com
  recomendação (onde calcular o colapso · qual regra), ambas confirmadas,
  resposta escrita de uma vez.
- **Erros da IA:** nenhum.
- **Decisões escaladas:** 6a (nova subseção; lugar resolvido, forma
  funcional aberta).
- **Tags:** `[PROMPT-CHAVE]` — a resposta depende de perceber que colapsar
  a PMF crua correlaciona dois ingredientes da régua multiplicativa; é o
  tipo de achado que decide se o teste de monotonicidade mede o que
  promete.

## 2026-08-07 — Lia (terceira rodada com o Felipe)

**Feito:**
- Respondido o retorno do Felipe (verificação do lookahead + dict
  implementado + G5/DFF chegando) em
  `RESPOSTA3_Felipe_midpoint_portao.md` (raiz, branch `Lia`).
- **Achado principal, e não estava na lista de nenhum dos dois:** a série
  do `/prices-history` é **midpoint amostrado no instante t**, não último
  trade nem agregado. Logo a série de preço nunca fica vazia por falta de
  negociação — mercado sem trade segue reportando midpoint, e midpoint
  parado é lido pelo `score_estabilidade` como **estabilidade perfeita**.
  Sem o portão de volume, o ingrediente daria confiança **máxima** ao
  mercado mais ilíquido: inversão sistemática de sinal, não ruído.
  Consequência: **o portão de volume vira pré-condição do
  `score_estabilidade`**, e fica **revogado** o registro de 05/08 de que o
  `c` poderia ser entregue sem o portão se o G5 atrasasse (o certo seria
  entregar sem o ingrediente de estabilidade).
- Verificação do lookahead encerrada sem ação: leitura das 12:00 UTC,
  execução na abertura de NY (13:30/14:30 UTC) — a leitura é 1,5–2,5 h
  anterior à execução.
- **6c (fronteira com a cascata do Felipe):** o piso "soma crua < 0,9
  desativa a view" (D12 do `Felipe`) e o `score_coerencia` **não** são
  dupla contagem — os regimes são disjuntos (view desativada nem chega ao
  Ω). Compromisso registrado dos dois lados: o piso não vira rampa e o
  score não ganha portão binário. Assimetria a favor: o corte dele é só
  por baixo, o score é bilateral, então soma 1,32 só é pega pelo score.
- **G5:** pedida a separação — truncamento do cap = `NaN` (não veta),
  pré-primeiro-trade = `0` (veta). O item do midpoint é o que decide: nos
  slots pré-trade o preço é o midpoint semeado na criação, valor inicial
  do book e não probabilidade negociada.
- **Chave do dict:** aceito o identificador longo (`"2.2_inflacao"` etc.),
  que sai de `diagnostics["view"]`. O apelido curto do exemplo de 07/08
  foi descuido de escrita, não pedido de renomeação — um segundo nome para
  a mesma coisa recriaria a classe de erro que o dict fechou.
- **6d (disciplina de calibração):** proposta a separação forma × nível
  para evitar overfit em dois passos, agora que o backtest ficou positivo
  (+2,68 pp) e um `c` alto passou a ser custo em vez de conserto.
- `Decisoes_pendentes.md`: novas subseções **6b**, **6c**, **6d** e a nota
  de numeração divergente entre branches.

**Quebrou:** nada.

**Notícias recebidas nesta rodada** (contexto que muda dimensionamento):
`DFF` entregue e view 2.3 ligada — k = 2 em 64% dos pregões e 2.3 ativa em
87%, então a calibração *entre* views passa a ter amostra (ressalva de
07/08 retirada, com nota de que são dois mercados, não vinte). G5 entregue:
121 mercados, 12.928 slots, `notional_usd` + `n_trades` + `t_cobertura_min`.
Backtest reancorado: +2,68 pp de excesso sobre o SPY com teto no tilt
(contra −7,91 pp do teto de carteira, mesma alavancagem 1,90) — o número
+15,7% × +30,1% que motivou o parágrafo de honestidade de 07/08 está duas
medições atrás.

**Observação para o Felipe (módulo dele, não editado):** pedido que a lista
de chaves válidas da `aplicar_veto` seja derivada de `view_results` em
runtime, não de constante escrita à mão — senão o nome da view passa a
viver em três lugares e a validação cobre dois. Registrada também a
implicação do achado dele sobre os testes que nunca rodavam: "suíte verde"
naqueles arquivos não era evidência antes do conserto.

**Pendente:**
- Implementar o colapso PMF→p (duas candidatas) sobre a `serie_janela`
  renormalizada.
- Portão de volume com o G5, assim que a separação `0` × `NaN` estiver no
  arquivo do Paulo.
- Rodar o teste de monotonicidade nos quatro ingredientes, agora com duas
  views.
- Entregar `c` + `ativa` (dicts chaveados por `diagnostics["view"]`).
- Reunião: nível global do `c` + teto de alavancagem (uma vez só, ver 6d);
  forma do `c` não entra nessa conversa.
- Decisão 9 (matriz de relação) segue aberta; `git push` da branch `Lia`
  continua não feito.

**Uso de IA:**
- **Modelo:** Claude Code / Opus 5.
- **Contexto consumido:** ~55% da janela, estimativa (sessão contínua desde
  05/08).
- **Prompt inicial (verbatim):** "o felipe me respondeu com essa mensagem:"
  (seguido da mensagem dele colada).
- **Iterações até aceitar:** 1, com um percalço de processo: a primeira
  chamada de escolhas foi rejeitada por engano e a Lia confirmou em
  seguida a opção recomendada nas duas perguntas.
- **Erros da IA:** nenhum.
- **Decisões escaladas:** 6b, 6c e 6d (novas subseções da Decisão 6).
- **Tags:** `[PROMPT-CHAVE]` — a rodada depende de perceber que "a série é
  midpoint" implica que mercado ilíquido parece perfeitamente estável; é
  uma inversão de sinal que nenhuma das duas partes tinha na lista e que o
  teste de monotonicidade não pegaria sozinho.

## 2026-08-07 — Lia (quarta rodada com o Felipe)

**Feito:**
- Respondida a correção do Felipe
  (`RESPOSTA3_Lia_portao_renormalizacao.md`, recebido por fora do repo) em
  `RESPOSTA4_Felipe_buracos_calibracao.md` (raiz, branch `Lia`).
- **A correção dele estava certa no diagnóstico:** a `serie_janela` crua
  não reproduz o `p` da view (entre as duas rodam `carry_missing` e
  `daily_preopen`). Das três consequências que ele listou, duas
  incorporadas e uma resolvida pelo caminho oposto ao proposto:
  - **`ffill` recusado.** Repetir a última leitura injeta **variação zero**
    — mercado esburacado pareceria mais estável. Mesma inversão de sinal do
    midpoint (6b) por outro caminho, e pior: `ffill` só erra num sentido, o
    que é viés, não imprecisão, e a monotonicidade não distingue viés de
    sinal. Regra adotada: **linha incompleta não entra** no cálculo de
    variação; o buraco segue custando confiança pelo canal próprio.
  - **Passo de tempo:** aceito que 12 h e 24 h são réguas diferentes;
    entram como dimensão da grade (2 formas × 2 grades).
  - **Dias degenerados:** aceito o recorte em produção (é automático),
    **recusado na calibração** — o alvo do teste é o erro da probabilidade,
    que existe mesmo sem view, e livro degenerado é a condição que deve
    gerar score baixo. O artefato é o sinal.
- **Consequência do número que ele mandou** (27 dias degenerados de 801, 24
  com soma < 0,5, todos fora da janela do v1): a calibração passa a rodar
  sobre a **história completa dos mercados (801 dias)**, não sobre os 374
  pregões do backtest — legítimo pela trava do 6d, e é o que dá poder
  discriminante ao `score_coerencia`. A faixa estreita da 2.3 era
  propriedade do recorte, não do mercado.
- Dispensada a oferta de `serie_janela_tratada`: a série tratada é
  inutilizável para o que o score mede.
- `dp_variacao_janela` não será consumido nem nas views binárias — mesma
  quantidade calculada por um único caminho.
- `Decisoes_pendentes.md`: nova subseção **6e**; delimitação registrada de
  que o 6a fechou o **lugar**, não a **forma**.

**Quebrou:** nada.

**Fechado pelo Felipe nesta rodada:** chaves derivadas de `view_results` em
runtime (já era assim) + `VIEWS_ATIVAS` desatualizada apagada do
`src/config.py` (constante escrita à mão que ninguém lia e ainda listava a
view B); compromisso do 6c escrito em dois lugares do lado dele; G5
repassado ao Paulo como D12 do branch `Paulo`; protocolo anti-overfit
registrado como posição da Lia, não fechado (é decisão de grupo).

**Pendente:**
- Implementar o colapso (linha incompleta fora, sem `ffill`, PMF
  renormalizada) e rodar a monotonicidade nas quatro candidatas sobre os
  801 dias.
- Portão de volume quando o Paulo aplicar a separação `0` × `NaN`.
- Entregar `c` + `ativa`.
- Confirmar com o Felipe/Paulo se `polymarket_fed_reunioes.parquet` é o
  caminho certo para os 801 dias.
- Reunião: nível global do `c` + nível e escopo do teto (6d).
- Decisão 9 (matriz de relação) aberta; `git push` da branch `Lia` ainda
  não feito.

**Uso de IA:**
- **Modelo:** Claude Code / Opus 5.
- **Contexto consumido:** ~70% da janela, estimativa (sessão contínua desde
  05/08).
- **Prompt inicial (verbatim):** caminho do arquivo recebido por WhatsApp
  (`.../transfers/2026-32/RESPOSTA3_Lia_portao_renormalizacao.md`), sem
  texto adicional.
- **Iterações até aceitar:** 1 (uma escolha apresentada — imputar ×
  descartar linha incompleta — confirmada na recomendação).
- **Erros da IA:** nenhum.
- **Decisões escaladas:** 6e.
- **Tags:** `[PROMPT-CHAVE]` — a rodada depende de reconhecer que a
  correção do Felipe estava certa no diagnóstico e errada no remédio, e que
  o remédio proposto reintroduzia por outra porta a mesma inversão de sinal
  identificada na rodada anterior.
