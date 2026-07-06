# Decisões pendentes — mock do projeto

Decisões de implementação que faltam fechar antes/durante o mock. À medida
que resolvemos, registramos a decisão na própria seção (status: 🔴 aberta ·
🟡 em discussão · 🟢 fechada).

---

## 1. Universo de ativos e fonte de preços 🟢
Lista fechada de instrumentos negociáveis que formam o vetor de pesos.

**Decisão:**

Critério de divisão por **horizonte** (não por tamanho de ativo):
- **Camada estrutural** (posições lentas) → setores + classes de ativos.
- **Camada tática** (trades rápidos) → ações individuais, definidas depois.

Universo da camada estrutural (cobre as 5 views: Fed 2.3, inflação 2.2, eleitoral 2.4, momentum 1.2, sentimento macro 3.1):

| Ticker | O que é | Views que atende |
|--------|---------|------------------|
| XLK | Tecnologia | Fed (long-duration), eleitoral, momentum |
| XLU | Utilities (defensivo) | Fed (defensivo/duration), eleitoral |
| XLP | Consumo defensivo | Fed (defensivo) |
| XLF | Financeiro | Fed (sensível a juros), eleitoral |
| XLE | Energia | Eleitoral/regulatória |
| XLV | Saúde | Eleitoral/regulatória |
| TIP | Títulos protegidos contra inflação (TIPS) | Inflação |
| TLT | Treasuries nominais longos | Inflação (par), Fed |
| SPY | Ações EUA amplo | Âncora de mercado (prior do BL), macro |

- Granularidade: setores + classes de ativos (sem ação individual na estrutural).
- Treasuries nominais: **TLT** (longos, mais sensível a juros — amplifica as views de juros).
- Fonte de preços: yfinance · frequência diária.

**Em aberto:** incluir proxy de Brasil (EWZ) para cobrir a transmissão EUA→BR da view 3.1 — decidir depois.

## 2. Acesso ao Polymarket 🔴
De onde vêm os dados do poly no mock: API real · snapshot histórico · dados sintéticos.

**Decisão:** _(a registrar)_

## 3. Mapeamento cenário → ativos (Camada 2) 🔴
Como estimar a matriz de retornos condicionais. Regredir retorno do ativo contra o quê (mudança de probabilidade? dummy de resolução?).

**Decisão:** _(a registrar)_

## 4. Tradução probabilidade → vetor Q 🔴
Como converter probabilidade do poly em retorno esperado (unidade que o BL exige). Ponte entre "65% de corte" e um número de retorno por ativo.

**Decisão:** _(a registrar)_

## 5. Definição operacional de "surpresa" (PEAD, 1.1) 🔴
Fórmula da surpresa. `1 − prob_atribuída`? Contínua ou por threshold?

**Decisão:** _(a registrar)_

**Contexto para a reunião (Lia):**
- Além da fórmula em si, falta definir a janela de holding do trade de
  drift pós-evento e quais ativos/mercados são elegíveis (todos os
  mapeados no Polymarket, ou só com liquidez mínima?).
- Se for por threshold: existe mais de um nível (ex.: surpresa moderada vs.
  grande)?
- Trade-off conhecido: threshold mais permissivo → mais trades/mais ruído;
  mais restritivo → sinal mais raro, potencialmente mais robusto.
- Depende da Decisão 2 (fonte dos dados do Polymarket), pra saber com que
  granularidade a probabilidade da véspera fica disponível.

## 6. Forma funcional do Ω reativo 🔴
Como volume, estabilidade, convergência e proximidade de evento viram um número de confiança. Versão mínima para o mock vs. versão completa.

**Decisão:** _(a registrar)_

**Contexto para a reunião (Lia):**
- Combinação linear (soma ponderada) vs. não-linear (produto, mínimo,
  logística)?
- Cada fator entra normalizado (ex.: em [0,1])? Como normalizar
  volume/liquidez — percentil histórico ou corte absoluto?
- Intervalo de saída de Ω (ex.: [0,1], onde 0 = recolhe para o prior, 1 =
  confiança máxima)?
- Granularidade de recálculo: a cada período (diário?) ou por evento?
- Trade-off conhecido: forma linear é mais simples/interpretável (bom para
  o relatório); não-linear captura interação entre fatores, mas é mais
  difícil de calibrar e justificar.
- Depende da Decisão 7 (como a convergência entre fontes entra como
  fator).

## 7. Convergência entre fontes (polls, casas de aposta) 🔴
Se entra no Ω já no v1 ou fica como stub (adiciona dependências de dados).

**Decisão:** _(a registrar)_

**Contexto para a reunião (Lia):**
- Se entrar no v1: divergência entre fontes reduz Ω proporcionalmente à
  distância entre elas, ou é um corte binário (diverge acima de X → Ω cai
  para um piso mínimo)?
- Depende de confirmação do Paulo sobre quais fontes o pipeline
  disponibiliza de fato hoje.

## 8. Gatilho de salto (event-driven) 🔴
Sinal da camada tática que dispara com um salto de nível na probabilidade
antes da resolução do evento (ex.: fusão 40% → 70%). Não estava registrado
neste doc — adicionado a partir do norte geral da Lia.

**Decisão:** _(a registrar)_

**Contexto para a reunião (Lia):**
- Tamanho mínimo do salto que caracteriza o gatilho.
- Unidade de medida (pontos percentuais vs. log-odds).
- Janela de tempo em que o salto precisa ocorrer para contar.

## 9. Forma de cálculo da velocidade de ajuste 🔴
Sinal da camada tática que usa a derivada da probabilidade durante um
movimento como gatilho. Não estava registrado neste doc — adicionado a
partir do norte geral da Lia.

**Decisão:** _(a registrar)_

**Contexto para a reunião (Lia):**
- Como estimar a derivada — diferença simples entre períodos consecutivos
  vs. regressão local numa janela.
- Limiar de velocidade que caracteriza o gatilho.

## 10. Matriz de relação 3D ações × mercados Polymarket × tempo (camada tática) 🟡
Como medir a relação entre cada ação e cada previsão macro do Polymarket
para selecionar os ativos elegíveis dos trades táticos.

**Decisão (em discussão — direção dada pela Lia em 06/jul, confirmar com o grupo):**
- Estrutura tridimensional: ativos × mercados do Polymarket × tempo
  (janelas móveis), inspirada na matriz de dependência do relatório NEXUS
  (Desafio Quant AI 2025).
- Métrica por célula: **distance correlation** (dcor, Fórmula 1 do
  NEXUS) — captura relação linear e não-linear; nula só sob independência
  estatística.
- Base implementada em `lia/matriz_relacao.py` com testes sintéticos.

**Em aberto (para a reunião):**
- Tamanho da janela móvel e passo de recálculo (a função exige `janela`
  como argumento explícito, sem default, até isso ser fechado).
- Série do Polymarket a usar: variação da probabilidade ou nível.
- Fronteira com a Decisão 3 (mapeamento cenário → ativos, Camada 2 do
  Felipe): esta matriz é da camada tática (seleção de elegíveis para
  trades curtos), não substitui a matriz de retornos condicionais da
  estrutural — confirmar com o Felipe que não há sobreposição de
  interface.

---

**Próximo passo:** voltar para a Decisão 1.
