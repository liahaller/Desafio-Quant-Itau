# PEDIDO DE DADOS — Paulo (pipeline Polymarket)

> **Para o Claude do Paulo:** este arquivo é uma encomenda de **levantamento**, não de implementação de views.
> Você não precisa entender a metodologia do Black-Litterman para executá-lo. Leia a seção 0, execute as
> seções 1–3 na ordem, e devolva **exatamente** o formato da seção 4. Não improvise formato de saída.

---

## 0. O que este pedido é (e o que NÃO é)

**É:** verificar, no CLOB do Polymarket, se **9 mercados específicos** existem, com que histórico, com que
liquidez, e — o mais importante — **se a API entrega bid e ask históricos**.

**NÃO é:**
- ❌ Catalogar todos os mercados do Polymarket. Já temos um catálogo (mensagem do Paulo no grupo, 30 mercados).
  O gargalo agora não é *quais mercados existem*, é *que dado bruto dá pra extrair de um mercado específico*.
- ❌ Sugerir mapeamento mercado → ETF. Esse mapeamento sai de **regressão de β** no módulo do Felipe, não de
  atribuição manual. Se aparecer a tentação de listar "mercado X → ETF Y", ignore: não é usado.
- ❌ Estimar volume "por conhecimento geral". Volume estimado não serve. Ou vem do endpoint, ou o campo fica `?`.
- ❌ Fazer decisão nenhuma. Você levanta e reporta; a decisão volta pro Felipe.

**Regra de ouro do pedido:** campo que você não conseguiu medir vai como `?` — **nunca** preenchido por
plausibilidade. Um `?` honesto é útil; um número inventado contamina uma decisão metodológica.

---

## 1. TAREFA CRÍTICA — a API entrega bid/ask histórico?

**Faça isto primeiro. Se a resposta for "não", ela sozinha muda o desenho de cinco views e vale mais que todo o resto do documento.**

### Por que importa

Cinco views precisam da série de preço do mercado como **midpoint entre bid e ask**, nunca como **último trade
negociado**. Motivo: em mercado fino, o último trade fica *stale* — a série vira uma escada de degraus, e essas
views medem justamente a **defasagem temporal** entre o movimento do Polymarket e o movimento da bolsa. Série em
degraus fabrica defasagem que não existe. O sinal viraria ruído de microestrutura.

### O que descobrir

O endpoint histórico de preços do CLOB (algo como `clob.polymarket.com/prices-history`, com parâmetros de token
id / intervalo / fidelidade — **confirme o nome e a assinatura reais na doc, não assuma os meus**) devolve o quê?

Responda literalmente estas quatro perguntas:

1. O `/prices-history` retorna **qual preço**? Último trade executado, midpoint, mid do book, ou não está documentado?
2. Existe **algum** endpoint que devolva bid e ask **históricos** (não só o snapshot atual)? Se sim, qual, e com que granularidade e profundidade de histórico?
3. Os endpoints de book (`/book`, `/midpoint`, `/spread` ou equivalentes) são **só tempo real**? Confirme.
4. Se não há bid/ask histórico: existe histórico de **trades individuais** (timestamp + preço + tamanho + lado)? Com lado (buy/sell) dá pra reconstruir um proxy de bid/ask.

### Como responder

Não responda pela documentação sozinha — **rode**. Puxe a série de um mercado real e resolvido (sugestão: o
presidencial 2024, que é grande e tem histórico longo) e **cole no relatório as primeiras 5 linhas do retorno
cru**, com os nomes de campo originais. O formato bruto responde mais do que a doc.

Registre também: qual **granularidade temporal** dá pra obter (1min? 1h? diário?) e **quantos dias de histórico**
o endpoint aceita antes de truncar.

---

## 2. Os 9 mercados-alvo

Para **cada** um, preencher as 6 colunas da seção 4. Nada além desses nove — se sobrar tempo, use pra aprofundar
a seção 1, não pra ampliar a lista.

| # | Mercado | Como identificar | Tipo esperado |
|---|---|---|---|
| M1 | **CPI mensal** | mercados de release do CPI dos EUA | ⚠️ ver nota A |
| M2 | **Decisão do FOMC por reunião** | "Fed decision in <mês>", faixas de −50bp/−25bp/manutenção/+25bp | PMF de buckets |
| M3 | **Trajetória do Fed** | "quantos cortes em <ano>?" / "taxa do Fed em dez/<ano>" | PMF de buckets |
| M4 | **Recessão nos EUA** | binário de recessão | ⚠️ ver nota B |
| M5 | **Presidencial EUA 2024 — vencedor** | binário; queremos a perna **Trump** | Binário |
| M6 | **Tarifas EUA × China** | imposição/escalada de tarifas; + "recíprocas"/"Liberation Day" 2025 | Binário |
| M7 | **Ação militar EUA/Israel × Irã (2025)** | "US military action against Iran before...", "US strikes Iran by..." | Binário |
| M8 | **Legislação tributária 2025 (OBBB)** | "passa até <data>?"; + teto da dívida / X-date (2023 e 2025) | Binário |
| M9 | **Presidencial EUA 2022 (midterms)** | robustness do M5 — liquidez fraca esperada, tudo bem | Binário |

### Nota A — o formato do M1 (CPI) é uma pergunta em si

Precisamos do CPI em **buckets exatos e mutuamente exclusivos** (≤3.6% / 3.7% / 3.8% / …), que formam uma
distribuição de probabilidade. O catálogo anterior listou "CPI mensal **vs consensus**", que é **binário** —
formato diferente, e que degrada a view.

**Responda explicitamente:** o que existe no CLOB é bucket, é binário vs consensus, ou existem os dois? Se
existirem buckets, **cole a lista completa dos buckets de um mês real**, com os rótulos originais.

### Nota B — o critério de resolução do M4 (recessão) muda a view

Existem duas famílias de mercado de recessão:
- **Resolução técnica** (2 trimestres consecutivos de PIB negativo, dado do BEA) — resolve mecanicamente. **É a que queremos.**
- **Resolução por declaração do NBER** — o NBER declara com meses de atraso, o que contamina o preço do mercado.

**Descubra qual critério cada mercado de recessão usa** e diga quais existem. Se só houver NBER, diga isso
claramente — é uma restrição, não um detalhe.

### Nota C — mercados que resolvem por "one-touch"

Para os mercados de bucket (M1, M2, M3): a resolução é **terminal** (vale o valor **na data final**) ou
**one-touch** (dispara se o valor **tocar** o nível a qualquer momento)? Isso decide se a receita de extrair a
média da distribuição vale ou não. Se a regra não estiver explícita nas *rules* do mercado, diga "não explícito"
— e **cole o texto das rules**.

---

## 3. Fontes fora do Polymarket (mesmo levantamento, mais curto)

Para cada uma: consegue puxar? desde quando? com que frequência? qual o nome/ticker exato que funcionou?

1. **FRED `T10YIE`** — breakeven de inflação 10 anos.
2. **FRED `DGS10`** e **`DTB3`** — juros 10 anos e 3 meses (o spread entra num probit).
3. **ZQ (Fed Funds futures) no yfinance** — duas coisas distintas: (a) o contrato do **mês seguinte a cada reunião do FOMC**, e (b) o contrato de **dezembro** de cada ano. Diga qual sintaxe de ticker funcionou (`ZQ=F`? contrato específico?) e quanto histórico veio.
4. **Calendário de datas do FOMC** — datas de anúncio, 2022–2025. Qual fonte?
5. **Calendário de releases do CPI** — datas de divulgação, 2022–2025. Qual fonte?
6. **Preço de ABERTURA (open)** dos 9 ETFs — XLK, XLU, XLP, XLF, XLE, XLV, TIP, TLT, SPY. Confirmar que o yfinance entrega `Open` diário confiável (não só `Close`).

---

## 4. FORMATO DA DEVOLUÇÃO

Devolva **um bloco só**, nesta estrutura, pra ser colado inteiro. Sem introdução, sem resumo executivo, sem
recomendações.

### 4.1 Bloco bid/ask (o mais importante)

```
=== BID/ASK HISTÓRICO ===
Endpoint testado: <url completa com parâmetros>
Retorna:          <último trade | midpoint | outro | indefinido>
Campos crus:      <lista de nomes de campo do JSON>
Amostra (5 linhas cruas):
  <cole aqui>
Bid/ask histórico disponível?  SIM / NÃO / PARCIAL — <onde, se sim>
Histórico de trades individuais? SIM / NÃO — <tem campo de lado buy/sell?>
Granularidade máxima:  <1min | 1h | diário | ...>
Profundidade máxima:   <quantos dias/meses antes de truncar>
```

### 4.2 Tabela dos 9 mercados

Uma linha por mercado. `?` onde não mediu.

| ID | Existe? | Primeira data com dado | Última data | Volume (USD, **do endpoint**) | Critério de resolução | Bid/ask? | Nº de dias sem trade na janela |
|---|---|---|---|---|---|---|---|
| M1 | | | | | | | |
| … | | | | | | | |

Abaixo da tabela, um parágrafo curto por mercado **só se houver surpresa** (formato diferente do esperado, o
mercado é uma família de vários em vez de um, mudou de regra no meio, etc.). Se não houve surpresa, não escreva
nada — a linha da tabela basta.

### 4.3 Respostas às notas A, B e C

```
NOTA A (formato do CPI):  <bucket | binário vs consensus | ambos>
  Buckets de um mês real: <cole os rótulos>
NOTA B (recessão):        <mercados encontrados e o critério de resolução de cada um>
NOTA C (one-touch):       <por mercado de bucket: terminal | one-touch | não explícito + texto das rules>
```

### 4.4 Fontes externas

| Fonte | Puxou? | Ticker/ID que funcionou | Desde | Frequência | Observação |
|---|---|---|---|---|---|

### 4.5 Bloqueios

Lista do que **não** deu pra levantar e por quê (rate limit, endpoint fora do ar, precisa de chave de API, rede
bloqueada, mercado não encontrado depois de N buscas). Um bloqueio explícito é resultado válido — some no
relatório é que não pode.

---

## 5. Ordem de prioridade

Se o tempo acabar, esta é a ordem de valor. Entregar 1 e 2 completos vale mais que os cinco pela metade.

1. **Seção 1 (bid/ask)** — trava cinco views e uma decisão de arquitetura.
2. **M5, M4, M1, M2** — as quatro views já fechadas. Sem esses, o v1 não roda.
3. **Notas A, B, C** — condicionam a matemática de quem usa esses mercados.
4. **M6, M7, M8, M3, M9** — views candidatas, entram por decisão de reunião.
5. **Seção 3** — fontes externas.

---

## 6. Entrega física

Além do relatório em texto:
- Salve os CSVs crus que conseguir puxar (um por mercado) no diretório de dados brutos do pipeline — série
  temporal completa, **sem tratamento**, com os nomes de coluna originais da API.
- Não normalize, não preencha buraco, não interpole, não converta fuso. O tratamento é a jusante, em módulo do
  Felipe (`src/poly_preprocessing.py`), e precisa receber o dado cru pra decidir o que fazer com ele.
- Um `?` no relatório **não** deve ser resolvido com estimativa. Deixe `?`.
