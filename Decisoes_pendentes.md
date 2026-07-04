# Decisões Pendentes

Fonte da verdade sobre o que já foi decidido e o que ainda está em aberto no
projeto. Nenhuma decisão aqui é fechada por uma sessão de Claude Code — só
por acordo do time em reunião. Ver `CLAUDE.md`, seção 1.

Formato de cada entrada: contexto, perguntas a responder, opções levantadas
(sem recomendação unilateral) e trade-offs. Status muda só com instrução
explícita de um humano.

> Nota: a numeração usada em `LIA_risco_relatorio.md` já pressupõe a
> existência de Decisões 1 e 2 (provavelmente escolha de fonte de dados e
> universo de ativos, dono: Paulo/Felipe). Este arquivo ainda não tem essas
> entradas porque a sessão de Lia não tem contexto sobre elas — precisa ser
> reconciliado quando Felipe e/ou Paulo registrarem as próprias decisões
> pendentes aqui.

---

## Decisão 3 — Definição de "surpresa" (gatilho do PEAD)

- **Status:** EM ABERTO — pauta da reunião de 07/jul/2026.
- **Dono do módulo afetado:** Lia (camada tática).
- **Contexto:** o sinal de PEAD (drift pós-evento) precisa de um critério
  operacional para decidir quando um desfecho conta como "surpresa" grande
  o suficiente para disparar o trade. `LIA_risco_relatorio.md` cita como
  exemplo ilustrativo "desfecho com prob. < 30% = surpresa grande", mas isso
  não está fechado como decisão.
- **Perguntas a responder na reunião:**
  - Qual o limiar de divergência entre a probabilidade da véspera e o
    desfecho real que caracteriza "surpresa"? Existe mais de um nível
    (ex.: moderada vs. grande)?
  - A divergência é medida em pontos percentuais absolutos, em razão, ou em
    log-odds?
  - Qual a janela de holding do trade de drift pós-evento?
  - Quais ativos/mercados são elegíveis para esse sinal (todos os mercados
    do Polymarket mapeados, ou só os com liquidez mínima)?
- **Opções levantadas até agora:** nenhuma fechada.
- **Trade-offs conhecidos:** limiar mais permissivo → mais trades, mais
  ruído; limiar mais restritivo → sinal mais raro, potencialmente mais
  robusto.
- **Depende de:** dataset de backtest (Paulo), para calibrar limiares com
  dados reais em vez de "achismo".

## Decisão 4 — Forma funcional do Ω reativo

- **Status:** EM ABERTO — pauta da reunião de 07/jul/2026.
- **Dono do módulo afetado:** Lia (Ω reativo).
- **Contexto:** Ω é a confiança que modula o quanto a carteira se inclina
  para as views do Black-Litterman. Precisa reagir a quatro fatores:
  volume/liquidez do mercado, estabilidade da probabilidade ao longo do
  tempo, convergência entre fontes, e proximidade da data de resolução do
  evento.
- **Perguntas a responder na reunião:**
  - Ω combina os 4 fatores de forma linear (soma ponderada) ou não-linear
    (produto, mínimo, função logística, etc.)?
  - Cada fator entra normalizado (ex.: em [0,1])? Como normalizar
    volume/liquidez — percentil histórico? corte absoluto?
  - Qual o intervalo de saída de Ω (ex.: [0,1], onde 0 = ignora a view e
    recolhe para o prior, 1 = confiança máxima)?
  - Ω é recalculado em qual granularidade — a cada período (diário?) ou por
    evento?
- **Opções levantadas até agora:** nenhuma fechada.
- **Trade-offs conhecidos:** forma linear é simples e interpretável (bom
  para o relatório), mas pode não capturar interação entre fatores (ex.:
  baixa liquidez *e* alta volatilidade sendo pior que a soma das partes);
  forma não-linear é mais expressiva, porém mais difícil de calibrar e de
  explicar/justificar na avaliação da competição.
- **Depende de:** Decisão 5 (como o conflito entre fontes entra como um dos
  fatores de Ω).

## Decisão 5 — Tratamento de conflito entre fontes de probabilidade

- **Status:** EM ABERTO — pauta da reunião de 07/jul/2026.
- **Dono do módulo afetado:** Lia (Ω reativo), depende do pipeline do
  Paulo.
- **Contexto:** quando existe mais de uma fonte de probabilidade para o
  mesmo evento e elas divergem, é preciso definir como isso entra no fator
  "convergência entre fontes" da Decisão 4.
- **Perguntas a responder na reunião:**
  - O pipeline de dados do Paulo de fato disponibiliza mais de uma fonte
    por evento hoje, ou isso é um cenário futuro/hipotético?
  - Se sim: a divergência reduz Ω proporcionalmente à distância entre as
    fontes, ou é um corte binário (diverge acima de X → Ω cai para um piso
    mínimo)?
- **Opções levantadas até agora:** nenhuma fechada.
- **Depende de:** confirmação do Paulo sobre quais fontes estão realmente
  disponíveis no pipeline.

## Decisão 6 — Gatilho de salto (event-driven)

- **Status:** EM ABERTO — numeração provisória (não estava explícita em
  `LIA_risco_relatorio.md`; ajustar se colidir com decisão já numerada por
  Felipe ou Paulo).
- **Dono do módulo afetado:** Lia (camada tática).
- **Contexto:** o sinal event-driven dispara com um salto de nível na
  probabilidade antes da resolução do evento (ex.: fusão 40% → 70%).
- **Perguntas a responder:**
  - Qual o tamanho mínimo do salto que caracteriza o gatilho?
  - O salto é medido em pontos percentuais, ou em log-odds?
  - Em qual janela de tempo o salto precisa ocorrer para contar?
- **Opções levantadas até agora:** nenhuma fechada.

## Decisão 7 — Forma de cálculo da velocidade de ajuste

- **Status:** EM ABERTO — numeração provisória (mesma ressalva da Decisão
  6).
- **Dono do módulo afetado:** Lia (camada tática).
- **Contexto:** o sinal de velocidade usa a derivada da probabilidade
  durante um movimento como gatilho.
- **Perguntas a responder:**
  - Como estimar a derivada — diferença simples entre períodos consecutivos,
    regressão local em uma janela, outro método?
  - Qual o limiar de velocidade que caracteriza o gatilho?
- **Opções levantadas até agora:** nenhuma fechada.
