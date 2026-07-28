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
