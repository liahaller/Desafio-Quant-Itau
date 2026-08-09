# RESPOSTA `G10` — `DGS1`, rótulo dos baldes de payrolls, calendário oficial do CPI

**Do Paulo (pipeline de dados). Sessão de 2026-08-08.** Os três entregues, na ordem
pedida (G10a → G10b → G10c). Levantei e reportei — não decidi nada. Nenhuma série de
preço nova, nenhum parquet regenerado, universo de ativos intocado.

Scripts: `scripts/g10a_fred_dgs1.py`, `scripts/g10b_payrolls_bucket_labels.py`,
`scripts/g10c_cpi_calendar.py`.

---

## G10a — `DGS1` do FRED

```
=== G10a — DGS1 ===
Fonte usada:            https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS1   (público, sem chave)
Arquivo salvo:          data/raw/fred_DGS1.csv
Nº de linhas:           16853
Janela:                 1962-01-02 → 2026-08-06
Formato:                idêntico aos fred_DTB3.csv / fred_DGS10.csv que já existem
                        (colunas=['observation_date','DGS1']; ausência = CAMPO VAZIO)
Dias sem leitura:       719  (campos vazios; feriados/buracos do calendário)
```

**Uma escolha de fonte que preciso reportar — porque diverge do que você templou, e
"idêntico" é requisito seu.** Você escreveu a URL da **API** `series/observations`. Medi
as duas fontes ao vivo antes de gravar:

| | valor recente | ausência | idêntico aos `fred_*.csv` existentes? |
|---|---|---|---|
| `api.stlouisfed.org/.../observations` (a que você templou) | `4.0600000000` (padding) | `"."` | **não** |
| `fredgraph.csv?id=DGS1` (a que fez o DTB3/DGS10/DFF, G2/G8) | `4.06` | campo vazio | **sim** |

A API devolve o número com padding e ausência como `"."`; isso **não** fica idêntico aos
irmãos (2 casas, ausência = campo vazio), e eu não posso reformatar (regra: dado cru não
se normaliza). Os `fred_DTB3.csv`/`DGS10`/`DFF` vieram todos do **fredgraph** (G2/G8),
então usei a **mesma fonte** — é o único jeito de o arquivo sair de fato idêntico e cru.
Os valores são a mesma série; muda só a formatação. **Se você preferir a API literal, é
uma linha no script** — mas aí o arquivo não sai idêntico aos existentes. Reportei a URL
real usada, como você pede.

Confere: `DGS1` termina `2026-08-05,4.03 / 2026-08-06,4.06` — mesma cara de
`DGS10` (`...,4.68`). Ausência é campo vazio (ex.: `1962-02-12,`).

**Para que é:** benchmark de 1 ano da view B (trajetória do Fed). `DTB3` (3m) curto
demais, `DGS10` (10a) longo demais. É o vértice que faltava.

---

## G10b — Rótulo dos baldes dos mercados de payrolls

```
=== G10b — RÓTULO DOS BALDES DE PAYROLLS ===
Fonte usada:            https://gamma-api.polymarket.com/events?slug=<slug>   (precisa de chave? NÃO)
Arquivo salvo:          data/raw/payrolls_bucket_labels.csv
Nº de linhas:           182   (esperado: soma dos n_buckets do CSV do G9b = 182 — bate)
Colunas:                slug_mercado, token_id, outcome, slug_desfecho, familia
Rótulo lido do campo:   groupItemTitle (baldes) + outcomes (só nos binários sem groupItemTitle)
Mercados sem rótulo:    nenhum
Grades com ponta aberta: sim — todos os multi-bucket (ver abaixo)
```

**Caminho:** parti do `payrolls_polymarket_markets.csv` (33 linhas, **já filtrado para
EUA** no G9b — sem risco de mercado estrangeiro, como você previu). Para cada slug de
evento, `GET gamma-api.polymarket.com/events?slug=<slug>` (com fallback `closed=true`,
igual ao G9b), e uma linha por `market` (balde) do evento.

**Campos, como pedido:**
- **`token_id` = `clobTokenIds[0]`** de cada balde — é o token que **casa com o nome do
  JSON** que você já salvou (`G9_payrolls_<slug-evento>_<token>.json`). Conferi ao vivo:
  **182/182 baldes casam** com um JSON existente em `data/raw/clob_exploracao/`.
- **`outcome` = `groupItemTitle`**, **cru** (ex.: `<-50k`, `-50k – 0`, `250k+`, `≤3.9%`,
  `≥4.7%`). Nos 6 mercados binários (`n_buckets=1`, sem `groupItemTitle`) reportei os
  `outcomes` crus (`Yes/No`) e sinalizei que veio de outro campo. Nada normalizado — você
  converte para número aí, como faz com o CPI.
- **`slug_desfecho` = `slug` do market-balde** (ex.: `will-the-us-lose-more-than-50k-jobs-in-april`).
- **`familia`** = a do CSV do G9b (por evento): `nfp_jobs_added` (12), `unemployment_rate`
  (16), `nfp_prints_negative` (3), `release_timing_meta` (1), `outro` (1).

**Nome de campo verdadeiro (você pediu para reportar, não forçar o seu):** o rótulo do
balde está em **`groupItemTitle`** e o slug do desfecho em **`slug`** — os dois nomes que
você sugeriu existem na resposta real. `clobTokenIds` vem como **string JSON** (fiz
`json.loads`).

**Grades com ponta aberta** — **todos** os multi-bucket têm as duas extremidades abertas
(`<X`/`≤X` embaixo, `>X`/`X+`/`≥X` em cima). Exemplos medidos:

| mercado | balde de baixo | balde de cima |
|---|---|---|
| `how-many-jobs-added-in-april-296` | `<-50k` | `250k+` |
| `how-many-jobs-added-in-august-643` | `<50k` | `>200k` |
| `how-many-jobs-added-in-december` | `<100k` | `>300k` |
| `april-unemployment-rate-372` | `≤3.9%` | `≥4.7%` |
| `august-unemployment-rate` | `≤3.9%` | `≥4.4%` |
| `december-unemployment-rate-938` | `≤4.4%` | `≥4.9%` |

(o padrão vale para os 26 mercados multi-bucket; lista completa impressa pelo script). Os
6 binários (`*-prints-negative`, meta de release-timing, `unemployment-rate-over-4pt1-in-october`)
não têm grade de baldes. **Você decide como tratar a ponta aberta aí** — só reportei.

---

## G10c — Calendário OFICIAL de divulgação do CPI

```
=== G10c — CALENDÁRIO OFICIAL DO CPI ===
Fonte usada:            https://api.stlouisfed.org/fred/release/dates?release_id=10   (precisa de chave? SIM)
release_id usado:       10   (confirmado: nome EXATO "Consumer Price Index" em /fred/releases;
                        único candidato exato — o outro com "consumer price index" é
                        345 "Research Consumer Price Index", descartado)
Arquivo salvo:          data/raw/cpi_release_dates_fred.csv   (NÃO sobrescrevi o cpi_release_dates.csv)
Nº de linhas:           953
Janela:                 1949-03-24 → 2026-12-10
Colunas:                release_date, time_et, mes_referencia, fonte
Bate com o CSV atual?:  12/15 datas idênticas ao FRED; 3 DIVERGEM (detalhe abaixo)
```

- **`release_id` confirmado por nome exato**, não chutado: listei `/fred/releases` e o
  único com nome exatamente `"Consumer Price Index"` é o **10**. (No G9a payrolls era 50.)
- **`mes_referencia`** = mês do release − 1 (**DERIVADO**, marcado na coluna `fonte`).
  **`time_et`** = `8:30 AM`, padrão BLS — o FRED **não** declara hora (marcado em `fonte`).
- **Não sobrescrevi** o `cpi_release_dates.csv` — salvei ao lado como
  `cpi_release_dates_fred.csv`. Trocar o arquivo que o backtest lê é decisão do grupo.
- **~250 divulgações desde 2003** confirmado dentro das 953 (a série vai até 1949).

### As 3 divergências — você pediu para saber ANTES de trocar o arquivo

Todas são do CSV atual (origem: regras do Polymarket) contra o FRED oficial. Nas três, o
FRED **não** tem a data que está hoje no arquivo:

| data no CSV atual | ref (atual) | o que o FRED tem | natureza |
|---|---|---|---|
| `2025-01-13` | December (2024)¹ | **`2025-01-15`** | data do release de dez/2024 diverge em **2 dias** |
| `2025-10-15` | September 2025 | **`2025-10-24`** | CPI de set/2025 **atrasado +9 dias** pelo shutdown de 2025 |
| `2025-11-13` | October 2025 | **nenhuma em nov/2025** | CPI de out/2025 **não sai em nov** no FRED — pula de `2025-10-24` direto p/ `2025-12-18` (shutdown) |

¹ O CSV atual escreve `December 2025` nessa linha (aparente typo de ano; o release de
jan/2025 cobre o CPI de **dezembro de 2024**). Não mexi no arquivo atual — só reporto.

**Leitura:** as 12 que batem são o miolo estável. As 3 que divergem são exatamente as
tocadas pelo **shutdown de 2025** (set→dez) e uma diferença de 2 dias numa data antiga.
**Divergência muda o dia do evento** — por isso está aqui como aviso, não como troca.
Trocar `cpi_release_dates.csv` pelo `_fred.csv` é decisão do grupo.

---

## O que eu NÃO fiz (respeitando o pedido)

- **ZQ**: não procurei — morto e enterrado, a view B agora usa o `DGS1`.
- **Não troquei o benchmark da 2.2** (`EXPINF1YR`): fora do escopo, não puxei.
- **Nenhum mercado de evento novo**, nenhum re-download das séries de payrolls (os 234
  JSONs seguem intactos), nenhum mercado de trajetória de 2026, G6 segue condicional à reunião.
- **Não sobrescrevi** `cpi_release_dates.csv`.

## Bloqueios

Nenhum. Os três rodaram ao vivo. Único ponto de atenção (não bloqueio): a fonte do G10a
(fredgraph vs. API `observations`) — usei o fredgraph para o formato sair idêntico aos
irmãos; se preferir a API literal, troca de uma linha.

## Commit

`0a0daea` no branch `Paulo`.
