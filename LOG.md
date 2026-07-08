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
