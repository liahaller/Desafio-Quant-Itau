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

## 9. Encadeamento dos mercados FOMC — tratamento do overlap 🟢
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

**Decisão (Paulo, 2026-08-08 — via recado do `Felipe` `RECADO_Paulo_G5_recebido_e_D9.md`):**
**opção 1** — em cada data, usar só o mercado da **próxima** reunião do FOMC (recorte
por janela entre reuniões).

Razões (a metodológica pesa mais que o custo):
- **Metodológica:** mercados de reuniões diferentes do FOMC **não são estimativas
  redundantes da mesma probabilidade** — são probabilidades de **eventos distintos**
  (a decisão de setembro ≠ a de dezembro). Agregar os dois num mesmo dia não é "usar
  mais informação"; sem regra de seleção, qualquer estatística por dia fica ponderada
  pelo **número de mercados abertos** naquele dia, que não é propriedade nenhuma do
  mercado. A opção 1 escolhe o instrumento que corresponde à decisão iminente.
- **Consistência:** já é o que o código do `Felipe` (view 2.3) e o arquivo da Lia
  (`Dump/trocas/dias_801_fomc.csv`, script `scripts/dias_801_lia.py`) rodam — os 801
  dias batem 1 a 1 com o v1. Registrar a opção 1 **documenta o que já roda**; nada muda.
- **Custo/prazo:** a opção 2 exigiria refazer a 2.3 e o arquivo da Lia (corte 13/08,
  entrega 17/08) sem ganho metodológico — pelo argumento acima, seria mais frágil.

Número que quantifica o overlap (medido pelo `Felipe` em 2026-08-08 no
`data/polymarket_fed_reunioes.parquet`, 18 reuniões): 1.952 linhas reunião×dia no slot
pré-abertura vs. **801 datas distintas** → o overlap infla a contagem em **2,44×**.

A opção 2 só faria sentido como **escopo novo** (usar reuniões mais distantes como um
segundo sinal, com regra própria — ex.: view de trajetória de juros), o que não é o que
a D9 pergunta. Interliga com a Decisão 8 (janela de backtest) e a 11 (midpoint).

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

## 12. G5 volume no tempo — tratamento de slot pré-primeiro-trade: `NaN` ou `0`? 🟢
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
`scripts/g5_volume_no_tempo.py`.

**Decisão (Lia, via FOLLOWUP5, 2026-08-08 — dona da régua Ω):** **separar os
dois casos**.
- Truncamento do cap (346 slots): `NaN` — ignorância nossa (o dado existe, a API
  não entrega); propaga como "sem dado", não veta o portão de volume.
- Pré-primeiro-trade (78 slots, 19 mercados não capados): `0` — fato do mercado
  (ninguém negociou); é `0` legítimo e **veta** o portão.

Argumento que decidiu: a série de preço do Polymarket é **midpoint** (não último
trade), logo nunca fica vazia por falta de negociação; midpoint parado leria como
estabilidade perfeita e, sem portão de volume, daria confiança máxima ao mercado
mais ilíquido (inversão de sinal). Os 78 slots são midpoint semeado na criação do
book — o caso puro que o portão existe para vetar. A Lia também revogou o "entrego
o `c` sem portão se o G5 atrasar" (05/08): o G5 virou **pré-condição** da régua,
não um dos quatro insumos.

**Implementado e conferido (Paulo, 2026-08-08):** condição do `NaN` no
`scripts/g5_volume_no_tempo.py` passou a exigir `bateu_cap`. `g5_volume_no_tempo.csv`:
`NaN` 424→346, `0` 2403→2481 (+78), positivos 10101 inalterados, total 12928.
`t_cobertura_min` por mercado inalterado (`g5_volume_cobertura.csv` sem mudança).
Entregável `docs/RESPOSTA_FOLLOWUP5_Pedido_Paulo_dados.md`.

## 13. Calendário do CPI — adotar o oficial do FRED (G10c) no lugar do derivado de mercado? 🔴
Levantado em 2026-08-08 (entrega do G10c, pedido do `Felipe`). O
`data/raw/cpi_release_dates.csv` (15 linhas, 2025→2026) tem as datas de divulgação do
CPI derivadas das **regras dos mercados do Polymarket** — só existe onde existe mercado.
O G10c baixou o calendário **oficial do FRED** (release_id=10, confirmado por nome exato),
**953 datas** (1949→2026, ~250 desde 2003), salvo **ao lado** em
`data/raw/cpi_release_dates_fred.csv` (o atual NÃO foi sobrescrito). Motiva a variante de
β por **event-study nos dias de divulgação**, que com 15 datas não roda de forma
defensável e com o calendário completo roda.

Conferência das 15 datas atuais contra o FRED: **12 batem, 3 divergem** — e as 3 são as
tocadas pelo **shutdown de 2025**:
- `2025-01-13` → FRED `2025-01-15` (dez/2024, +2 dias).
- `2025-10-15` → FRED `2025-10-24` (set/2025, atraso +9 dias).
- `2025-11-13` → FRED **não tem** nov/2025 (out/2025 pula de `10-24` p/ `12-18`).

Divergência muda o **dia do evento** em medições já feitas/publicadas — por isso é decisão
de grupo, não efeito colateral do pedido (o próprio `Felipe` marcou assim). Perguntas em
aberto (trade-offs a decidir — NÃO decidido):
- Adotar o FRED como fonte do `cpi_release_dates.csv` (troca de insumo do backtest)?
- Se sim, refazer as medições que usaram `2025-10-15`/`2025-11-13`, ou congelar o
  publicado e usar o FRED só daqui pra frente?
- Tratar out/2025 (que o FRED não lista em nov) como remanejado p/ dez/2025 ou como buraco
  declarado?

Reportado ao `Felipe` em `docs/FOLLOWUP_G10_Paulo.md`. Lado dos dados (trocar arquivo /
tratar mês de referência) é do `Paulo`; refazer o event-study é módulo do `Felipe`.
**Decisão:** _(a registrar — grupo)_

## 14. Fonte do `DGS1` (G10a) — fredgraph vs. API `series/observations` 🟡
Levantado em 2026-08-08 (G10a). O pedido templou a URL da API
`api.stlouisfed.org/fred/series/observations`, mas ela devolve valor com padding
(`4.0600000000`) e ausência `"."` — **não** idêntico aos `fred_DTB3.csv`/`DGS10` (2 casas,
ausência = campo vazio). Como "formato idêntico" é requisito e "dado cru não se normaliza",
o `DGS1` foi baixado do **fredgraph** (a mesma fonte do G2/G8 que gerou os irmãos), saindo
de fato idêntico. Mesma série, muda só a formatação. Confirmação pendente do `Felipe`:
fredgraph serve, ou ele precisa da API literal (aí o arquivo não fica idêntico)? Não é
troca de fonte de dado (é o mesmo FRED, mesma série) — é detalhe de formato. Reportado em
`docs/FOLLOWUP_G10_Paulo.md`. **Decisão:** _(confirmação do `Felipe` — não bloqueia)_

---

## Notas de interface (mudanças de formato acordadas — não são decisões metodológicas)

- **2026-08-10 — `polymarket_fed_reunioes.parquet` ganhou `conditionId` + `slug`.** Mudança
  **aditiva** (as colunas antigas e as 16.338 linhas / 76 mercados / 18 eventos ficam intactas),
  **pedida pela consumidora (Lia)** no `Downloads/PEDIDO_Paulo_G5_fomc.md` — é a chave que faltava
  para juntar o parquet com a saída do G5 (antes: 0 chaves em comum; agora: 76). Esquema novo:
  `[data, mercado, probabilidade, volume, evento_id, conditionId, slug]`. Fonte da chave: a mesma
  Gamma da Decisão 2 (`/events?id=`), sem re-baixar preço. Aplicada por
  `scripts/g5b_fomc_conditionid.py`; o `download_polymarket_fed.py` também já emite a chave num
  rebuild completo. A view 2.3 do G5 (`g5_volume_no_tempo.csv`) passou a cobrir as 76 faixas do FOMC
  a partir deste parquet. Entregável: `docs/RESPOSTA_PEDIDO_Paulo_G5_fomc.md`.

---

**Próximo passo:** voltar para a Decisão 1.
