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

## 10. Extensão do universo de eventos FOMC — reuniões antigas e mercados "cut by date" 🟡
Descoberta em 2026-07-27: as reuniões antigas do FOMC (dez/2023, jan/2024,
mar/2024) **não** têm o tag "Fed Rates" (id 100196) que o pipeline usava — só
tags gerais (interest-rates=131, fed=159). Por isso o dataset começa em
mai/2024.

**Testado e revertido (por instrução do Paulo, 2026-07-27):** as 3 reuniões
antigas (December 2023, January 2024, March 2024) foram incluídas via padrão
de slug `fed-interest-rates-<mês>-<ano>` nas tags gerais, mas **não deram certo**
(dados de baixa qualidade / volume muito baixo). Foram **removidas** — o
dataset permanece com 18 reuniões, de mai/2024 em diante. A extensão da
descoberta foi revertida no `download_polymarket_fed.py`.

**Mantido:** coluna `volume` (volume total lifetime por mercado, do Gamma) no
`reunioes.parquet`, exibida no dashboard.

**Em aberto (NÃO decidido):** os mercados **cumulativos** "Fed rate cut by
<data>?" (ex.: evento 903089, dez/2023) são estrutura diferente — medem se
houve corte *até* a reunião, não o desfecho *da* reunião. Continuam em
`outros`/ambíguos. Ver também a Decisão 9 (overlap) e a 8 (janela de backtest).

## 11. Fonte da série de preço do Polymarket — não há bid/ask histórico 🔴
Levantado em 2026-07-29 (resposta ao `docs/Pedido_Paulo_dados.md`, medido ao
vivo). A API gratuita do Polymarket **não entrega bid/ask histórico**:
- `/prices-history` (CLOB) devolve **uma série única** `{t, p}` — sem bid nem ask.
- `/orderbook-history` responde `{"count":0,"data":[]}` (vazio) para os tokens
  testados.
- `/book`, `/midpoint`, `/price`, `/spread` só existem em tempo real e retornam
  **404** para mercados já resolvidos (o book é apagado na resolução).
- Há histórico de **trades individuais com lado** (`data-api /trades`, campo
  `side` BUY/SELL) — dá para reconstruir um **proxy** de midpoint/bid-ask.

Isso afeta as views que exigem midpoint (o doc do Felipe cita 2.4, 3.1, C, E, G).
Opções levantadas (trade-offs a discutir em reunião — NÃO decidido):
- Usar a série única do `/prices-history` como está (comporta-se como último
  trade; em mercado fino a série fica em degraus/stale).
- Reconstruir um proxy de midpoint a partir do fluxo de `data-api /trades`
  (tem `side` e `size`) — mais trabalho de pipeline, decisão de forma.
- Desligar as views defasadas que dependem de midpoint.

**Novos fatos medidos (2026-07-29, follow-up do pedido — NÃO alteram a decisão,
só informam o trade-off):**
- A série do `/prices-history`, medida ao vivo em 2 mercados vivos, **bate com o
  `midpoint`**, não com o último trade (corrige a inferência anterior). Em mercado
  fino de baixo volume o `/book` volta **vazio** (sem bid/ask nem em tempo real).
- O fallback `data-api /trades` é **capado em ~20.000 trades** (limit 10000 +
  offset 10000; `offset>10000` → HTTP 400; params de tempo ignorados). Para
  mercado grande (ex.: M5/Trump) isso cobre só a cauda recente, **não** a vida
  inteira → o proxy de midpoint via trades **não** é viável para mercados grandes;
  para médios (ex.: M4/recessão) 99,8% das janelas de 12h têm BUY e SELL (proxy
  viável dentro da janela alcançável, que trunca os ~4 meses iniciais).
- M9 (Senado 2022) está morto pelas **duas** vias (`/prices-history` vazio e
  `/trades` = 0 trades).

Interliga com a Decisão 9 (overlap) e com o `poly_preprocessing` do Felipe
(midpoint bid/ask). **Decisão:** _(a registrar)_

## 12. G5 volume no tempo — tratamento de slot pré-primeiro-trade: `NaN` ou `0`? 🔴
Levantado em 2026-08-07 (entrega do G5 do FOLLOWUP4, spec do Ω da Lia). A spec
diz "antes do `t_cobertura_min` = `NaN`, nunca `0`", regra criada para o
**truncamento do cap de 20k** do `/trades` (sem ela, os mercados mais líquidos
leriam volume 0 falso nas datas antigas que a API não alcança). Apliquei a regra
**literal a todos os mercados**.

Consequência medida: dos 424 slots `NaN` no `g5_volume_no_tempo.csv`, **346 são
de truncamento** (2 mercados M3 capados — o caso que a regra protege) e **78 são
"pré-primeiro-trade" em 19 mercados NÃO capados** — slots de 12h em que a série
`/prices-history` já tinha ponto (midpoint semeado na criação do mercado) mas
ainda não houve nenhum trade. Como esses mercados **não** foram truncados,
sabe-se que o volume ali é genuinamente zero.

Opções (trade-off a decidir — dona da regra é a Lia, é o Ω dela):
- Manter `NaN` literal em tudo antes do `t_cobertura_min` (conservador; trata
  pré-trade como "sem dado").
- `NaN` só quando houve truncamento (mercado bateu o cap); nos não-capados, os
  slots antes do 1º trade viram `0` legítimo (informação que existe, não se
  perde).

Não fechei sozinho (CLAUDE.md §1). Sinalizado no entregável
`docs/RESPOSTA_FOLLOWUP4_Pedido_Paulo_dados.md`. É troca de uma linha no
`scripts/g5_volume_no_tempo.py`. **Decisão:** _(a registrar)_

---

**Próximo passo:** voltar para a Decisão 1.
