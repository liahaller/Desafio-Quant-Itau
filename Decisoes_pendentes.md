# Decisões pendentes — mock do projeto

Decisões de implementação que faltam fechar antes/durante o mock. À medida que resolvemos, registramos a decisão na própria seção (status: 🔴 aberta · 🟡 em discussão · 🟢 fechada).

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

## 6. Forma funcional do Ω reativo 🔴
Como volume, estabilidade, convergência e proximidade de evento viram um número de confiança. Versão mínima para o mock vs. versão completa.

**Decisão:** _(a registrar)_

## 7. Convergência entre fontes (polls, casas de aposta) 🔴
Se entra no Ω já no v1 ou fica como stub (adiciona dependências de dados).

**Decisão:** _(a registrar)_

---

**Próximo passo:** voltar para a Decisão 1.
