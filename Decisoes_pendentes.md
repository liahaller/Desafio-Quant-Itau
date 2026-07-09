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

## 2. Acesso ao Polymarket 🟢
De onde vêm os dados do poly no mock: API real · snapshot histórico · dados sintéticos.

**Decisão:** Path B — APIs gratuitas do Polymarket: Gamma API
(gamma-api.polymarket.com, catálogo/metadados) + CLOB API
(clob.polymarket.com, `/prices-history`), sem provedores pagos.
_(Registrada por instrução explícita do Paulo na sessão de 2026-07-08 —
prompt da Tarefa 2.)_

Limitações observadas na implementação (2026-07-08):
- Granularidade mínima para mercados já resolvidos: **12h** (`fidelity=720`;
  valores mais finos voltam vazios) — confirma a limitação já conhecida.
- Cobertura real dos mercados Fed/FOMC (tag "Fed Rates"): primeiro evento em
  **2023-12-06** — ver decisões 8 e 9 abaixo.

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

## 8. Reconciliação de cobertura: Polymarket × preços dos ETFs 🔴
A série de preços dos ETFs começa em 2003-12-05 (janela comum dos 9 tickers),
mas a cobertura real dos mercados Fed/FOMC no Polymarket começa em
**2023-12-06** (primeiro ponto de preço em 2023-12-07) — ~20 anos mais curta.
Afeta a Decisão 3 (mapeamento cenário→ativos: com ~2,5 anos de dados, a
estimação da matriz de retornos condicionais tem poucas reuniões do FOMC
para regredir).

Opções levantadas (trade-offs a discutir em reunião):
- Restringir o backtest à janela 2023-12 em diante (dados reais, amostra curta).
- Usar a série longa dos ETFs só para estimar prior/covariância e a janela
  curta para as views (janelas diferentes por componente).
- Complementar o período pré-2023 com outra fonte de probabilidades
  (reabriria a Decisão 2).

**Decisão:** _(a registrar)_

## 9. Encadeamento dos mercados FOMC — tratamento do overlap 🔴
Mercados de reuniões diferentes do FOMC negociam simultaneamente no
Polymarket (ex.: o mercado da reunião de dezembro/2024 abre em abril/2024).
No dataset baixado, 82 de 82 pares de eventos consecutivos têm overlap de
datas — o teste de "sem overlap" está marcado como xfail documentado em
`tests/test_polymarket_fed.py`. Para o dataset unificado (Tarefa 3), é
preciso uma regra de qual probabilidade vale em cada data.

Opções levantadas (trade-offs a discutir em reunião):
- Em cada data, usar só o mercado da **próxima** reunião do FOMC (recorte
  por janela entre reuniões).
- Manter todos os mercados ativos por data (dataset mais rico; a Camada 2
  decide o que consumir).
- Recortar cada mercado a uma janela fixa antes da reunião (ex.: últimos
  N dias).

**Decisão:** _(a registrar)_

---

**Próximo passo:** voltar para a Decisão 1.
