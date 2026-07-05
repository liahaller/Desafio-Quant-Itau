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
