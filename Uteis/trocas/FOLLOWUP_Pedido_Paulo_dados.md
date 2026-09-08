# FOLLOW-UP — `Pedido_Paulo_dados.md` (o que ficou faltando)

> **Para o Claude do Paulo:** a resposta anterior (`RESPOSTA_Pedido_Paulo_dados.md`) foi boa e fechou o item mais
> importante (bid/ask). Ficaram **10 pendências**, listadas abaixo em ordem de prioridade. A sessão anterior
> aparentemente travou no fim — vários itens da seção 3 do pedido original e a **entrega física** não saíram.
>
> Regras iguais às do pedido original, repetidas porque valem: **você levanta e reporta, não decide nada**;
> campo não medido vai como `?` — **nunca** preenchido por plausibilidade; **não** sugira mapeamento mercado → ETF;
> **não** normalize, interpole nem converta fuso em dado cru (o tratamento é a jusante, em módulo do Felipe).
>
> Lembrete operacional: os hosts do Polymarket só resolvem **com VPN** (achado da sessão passada).

---

## Prioridade

| # | Pendência | Por que trava |
|---|---|---|
| **F1** | **Dar push** do que já foi feito | Nada da sessão passada chegou no `origin/Paulo` — do meu lado o dado não existe |
| **F2** | **Identificadores** dos 9 mercados | Sem `conditionId`/`tokenId` ninguém consegue repuxar nada |
| **F3** | **Séries cruas dos 9** salvas em arquivo | O pedido pedia um arquivo por mercado; só o mercado-âncora saiu |
| **F4** | **Dimensionar `/trades`** | É a opção (b) da decisão de reunião — está sendo escalada sem custo medido |
| **F5** | **Qual preço o `/prices-history` entrega** | Pergunta 1 do pedido foi inferida, não medida |
| **F6** | **Contrato ZQ específico** | Trava as views 2.3 e B e a tática de drift pós-FOMC |
| **F7** | **Calendários FOMC e CPI** | Trava as 3 táticas e o alinhamento de evento das views |
| **F8** | **Varredura do CPI mês a mês (~18 meses)** | A view 2.2 precisa da série inteira, não de um mês-amostra |
| **F9** | **Contagem real de "dias sem trade"** (M2, M5, M6, M8) | Coluna do pedido ficou com descrição da grade no lugar da contagem |
| **F10** | **Granularidade em mercado VIVO** | Sabemos que resolvido só dá 12h; vivo é desconhecido |

Se o tempo acabar, **F1–F3 completos valem mais que os dez pela metade** — sem eles não consigo tocar nada do
meu lado.

---

## F1 — Push (fazer primeiro, e de novo no fim da sessão)

A resposta cita `data/raw/clob_exploracao/` e `scripts/explorar_clob_bidask.py` / `scripts/levantar_mercados_pedido.py`.
**Nenhum dos dois está no `origin/Paulo`** — o último commit da branch ainda é o dos ETFs (`48cb12e`). Ou seja: os
retornos crus existem só na máquina do Paulo.

Faça:
1. Commit + push de `scripts/` e `data/raw/` na branch `Paulo`.
2. Se algum arquivo estiver sendo barrado por `.gitignore` ou por tamanho, **diga qual e por quê** — não force.
3. Reporte o **hash do commit** no bloco de devolução.

---

## F2 — Identificadores dos 9 mercados

A tabela da resposta anterior não trouxe nenhum ID. Preencher **uma linha por mercado** (e, no caso das famílias,
a linha do mercado primário que você mediu):

| ID | Título exato do mercado | `slug` do evento | `slug` do mercado | `conditionId` | `tokenId` Yes | `tokenId` No |
|---|---|---|---|---|---|---|

Para M1 (CPI) e M3 (trajetória do Fed), que são PMFs de buckets, some a isto **uma linha por bucket** do mês/ano
que você mediu, com o rótulo original e o `tokenId` de cada bucket.

---

## F3 — Séries cruas dos 9 (entrega física)

Um arquivo por mercado, **sem tratamento nenhum**, nomes de coluna originais da API, em `data/raw/clob_exploracao/`:

- Formato: JSON ou CSV, tanto faz — desde que seja o retorno cru.
- Nome do arquivo: `M<n>_<slug>_<tokenId>.json` (ou `.csv`).
- Para as PMFs (M1, M3): **um arquivo por bucket**, não um agregado.
- M9 (série vazia): salve o retorno vazio mesmo assim — vazio medido também é dado.
- Reporte, na devolução, a **tabela arquivo → nº de linhas → primeira e última data**.

---

## F4 — Dimensionar o `data-api /trades` (o mais importante depois da entrega física)

A resposta escalou a decisão "(a) série única do `/prices-history` vs (b) proxy de midpoint reconstruído de
`/trades`" **sem medir o custo da opção (b)**. Não dá para levar isso à reunião assim: o grupo precisa saber se (b)
é viável antes de escolher.

Meça em **dois** mercados — **M5** (Trump 2024, grande) e **M4** (recessão, médio) — e responda:

```
=== DIMENSIONAMENTO /trades ===
Mercado:                <M5 | M4> — conditionId
URL exata:              <cole a URL com todos os parâmetros de paginação>
Nº total de trades:     <número; se paginou, some as páginas>
Limite por página:      <quantos trades vieram por request; qual parâmetro controla>
Como pagina:            <offset? cursor? timestamp? — qual parâmetro funcionou>
Span coberto:           <primeiro timestamp> → <último timestamp>
Cobre a vida inteira?   SIM / NÃO — <se NÃO, onde trunca>
Nº de requests / tempo: <quantas chamadas e quantos minutos para baixar tudo>
Rate limit encontrado:  <HTTP 429? a partir de quantas req/s? ou "não encontrado">
Trades por dia (mediana): <número>
Dias sem NENHUM trade:  <número de dias-calendário sem trade na janela>
Campos crus:            <lista>
Amostra (3 linhas cruas): <cole>
```

E mais uma medida, que é a que decide de verdade: pegue **um dia qualquer com liquidez normal** e conte
**quantos trades de BUY e de SELL** existem por janela de 12h. Se houver os dois lados na mesma janela, dá para
reconstruir um proxy de bid/ask; se em muitas janelas só aparecer um lado, não dá. Reporte:

```
Janelas de 12h na amostra:            <N>
Janelas com BUY e SELL (ambos):       <N e %>
Janelas com um lado só:               <N e %>
Janelas vazias:                       <N e %>
```

**Extra (só se sobrar tempo):** o `/trades` cobre 2022? Se cobrir, o M9 (midterms) volta a ser possível pela via
de trades, mesmo com o `/prices-history` vazio. Responda SIM/NÃO com a evidência.

---

## F5 — Qual preço o `/prices-history` entrega (medir, não inferir)

A resposta disse que a série "se comporta como último trade", mas isso foi inferência. Meça:

Escolha um mercado **VIVO** (resolvido não serve — o book some na resolução), e no **mesmo instante** puxe:

- `/prices-history` (último ponto da série)
- `/last-trade-price`
- `/midpoint`
- `/book` (melhor bid e melhor ask)

```
=== QUE PREÇO É A SÉRIE ===
Mercado vivo usado:  <slug + tokenId>
Timestamp da coleta: <ISO>
prices-history (último ponto): <valor>
last-trade-price:              <valor>
midpoint:                      <valor>
book: melhor bid / melhor ask: <valor> / <valor>
Conclusão medida: a série bate com <last-trade | midpoint | nenhum dos dois>
```

Repita em **2 mercados** (um líquido, um fino) — é no mercado fino que a diferença aparece.

---

## F6 — Contrato ZQ específico no yfinance

`ZQ=F` (contínuo) **não serve**: as views 2.3/B precisam do contrato do **mês seguinte a cada reunião do FOMC** e do
contrato de **dezembro** de cada ano. Falta a sintaxe do ticker mensal.

Teste as variantes e diga **qual funcionou** (as que falharem, reporte como falha — falha medida é resultado):

- `ZQZ25.CME`, `ZQZ25`, `ZQ=Z25`, `ZQZ2025`, e o equivalente para janeiro (`ZQF26`…).

```
=== ZQ CONTRATO ESPECÍFICO ===
Sintaxe testada          | Puxou? | Nº de obs | Desde | Tem Open? | Observação
```

Se **nenhuma** sintaxe funcionar no yfinance, diga isso claramente e liste as fontes alternativas que existem
(CME, Quandl/Nasdaq Data Link, FRED) **sem escolher nenhuma** — a escolha de fonte é decisão do grupo.

---

## F7 — Calendários FOMC e CPI (2022–2025)

Não foram puxados e a fonte não foi escolhida. Duas coisas separadas:

1. **Levante as fontes candidatas** (URL exata, formato, se precisa de chave, se é raspagem ou arquivo estruturado)
   para: (a) datas de anúncio do FOMC, (b) datas de release do CPI. **Não escolha** — só liste.
2. **Puxe pela fonte que funcionar mais rápido** e salve dois CSVs em `data/raw/`:
   - `fomc_dates.csv` → colunas: `date`, `time_et` (se disponível), `tipo` (reunião regular / extraordinária), `fonte`.
   - `cpi_release_dates.csv` → colunas: `release_date`, `time_et`, `mes_referencia`, `fonte`.

A resposta anterior notou que a data de release do CPI aparece nas *rules* dos próprios mercados de CPI — se essa
for a rota mais fácil, use, mas **diga qual rota usou** em cada linha (coluna `fonte`).

---

## F8 — Varredura do CPI mês a mês (~18 meses)

A resposta mediu **um** mês (julho/2025) como amostra, e a view 2.2 precisa da série inteira. Varra os eventos de
CPI mensal dos **últimos ~18 meses** e devolva:

| Mês de referência | `slug` do evento | Nº de buckets | Rótulos (originais, na ordem) | Volume do evento (USD) | 1ª data c/ dado | Última data |
|---|---|---|---|---|---|---|

Anote explicitamente: **em que mês o formato muda** (nº de buckets varia, rótulo muda de redação, some algum mês).
Salve as séries cruas de cada bucket junto com as do F3.

---

## F9 — "Dias sem trade": contar, não descrever

Na tabela anterior, M2, M5, M6 e M8 vieram com "grade 12h", que descreve a grade e não conta os buracos. Para os
quatro, conte de verdade sobre a série do `/prices-history`:

| ID | Nº de pontos na série | Nº de slots de 12h esperados na janela | Slots ausentes | % ausente | Maior buraco consecutivo (h) |
|---|---|---|---|---|---|

---

## F10 — Granularidade em mercado VIVO

Sabemos que em mercado **resolvido** só `fidelity=720` (12h) retorna dados. Falta saber o que um mercado **vivo**
entrega — isso muda o teto de granularidade do projeto inteiro.

Teste, num mercado vivo e líquido, `fidelity` = 1, 10, 60, 180, 720:

```
=== GRANULARIDADE EM MERCADO VIVO ===
Mercado: <slug>
fidelity=1    → <nº de pontos> | passo mediano <s> | janela coberta <de → até>
fidelity=10   → ...
fidelity=60   → ...
fidelity=180  → ...
fidelity=720  → ...
Observação: <a fidelidade fina tem janela limitada? trunca? etc.>
```

---

## Formato da devolução

Um bloco só, colável, nesta ordem — **F1, F2, F3, F4, F5, F6, F7, F8, F9, F10**, cada um com o cabeçalho
`## F<n> — <título>` e exatamente o formato pedido na seção correspondente. Sem introdução, sem resumo executivo,
sem recomendação, sem sugestão de decisão.

Fecha com:

```
## Bloqueios
<lista do que não deu, com o motivo: rate limit, endpoint fora, precisa de chave, rede, não encontrado após N buscas>

## Commit
<hash + branch do push do F1>
```

E, como no pedido original: **um `?` honesto é útil; um número inventado contamina uma decisão metodológica.**
