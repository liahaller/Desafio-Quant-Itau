# PEDIDO `G10` — `DGS1`, rótulo dos baldes de payrolls, calendário oficial do CPI

> **Para o Claude do Paulo:** três pedidos independentes entre si. Nenhum baixa série
> de preço nova, nenhum regenera parquet, nenhum toca no universo de ativos.
> O **G10a é uma série só do FRED** (minutos); o G10b é **metadado do que você já baixou**;
> o G10c é **uma chamada de API igual à do G9a**.
>
> Regras de sempre: **você levanta e reporta, não decide nada**; campo não medido vai como `?`;
> dado cru não se normaliza. **Push com hash** no fim.
>
> **Aviso honesto, porque a premissa mudou desde o G9.** O G9 dizia "não vira view —
> payrolls entra só como mais linhas na mesma medição". **Isto aqui vira view.** O dono
> reabriu o escopo em 08/08 (seção 14 do `Decisoes_pendentes.md` do `Felipe`) e pediu uma
> **quarta view** na carteira. Do meu lado já existe uma pronta (incerteza de anúncio, que
> não precisa de nada seu) e a quarta depende do **G10a**. Nada está fechado — a entrada de
> view é decisão do grupo, registrada como candidata na seção 15 — mas você tem direito de
> saber para que o dado vai.

---

## Prioridade e prazo

**Ordem: G10a → G10b → G10c.**

Entrega em **17/08**. A régua do `c` da Lia corta em **13/08**.

**Se você fizer uma coisa só, faça o G10a.** É uma série do FRED, leva minutos, e é o único
insumo que falta para a quarta view existir. O G10b destrava payrolls como família de view.
O G10c é melhoria de um insumo que já funciona.

---

## G10a — `DGS1` do FRED (o menor pedido, e o que destrava a quarta view)

Uma série só: **`DGS1`** — *1-Year Treasury Constant Maturity Rate*, diária. Mesma API, mesma
chave e mesmo script do G9a.

```
=== G10a — DGS1 ===
Fonte usada:            https://api.stlouisfed.org/fred/series/observations?series_id=DGS1
Arquivo salvo:          data/raw/fred_DGS1.csv
Nº de linhas:           <n>
Janela:                 <primeira data> → <última>
Formato:                idêntico aos fred_DTB3.csv / fred_DGS10.csv que já existem
Dias sem leitura:       <feriados/buracos, ou "nenhum">
```

**Para que é:** a **view B (trajetória do Fed)** pergunta *"onde a taxa termina o ano?"*.
O benchmark tem de ser do MESMO horizonte, e nenhum dos dois que temos serve: o `DTB3` é de
3 meses (curto demais) e o `DGS10` é de 10 anos (longo demais). O `DGS1` é o vértice certo.

**É o único insumo que falta.** O mercado de trajetória já está no `data/`
(`M3_fed_trajectory_*`, 9 baldes, 2024-12-30 → 2025-12-10, cobrindo 237 dos 374 pregões da
janela), o módulo da view já existe e as `fomc_dates` também.

**Nada a decidir da sua parte**, e nada muda de formato: é mais um arquivo irmão dos dois
`fred_*.csv` que você já entrega.

---

## G10b — Rótulo dos baldes dos mercados de payrolls

**O problema, medido aqui em 08/08:** os 234 arquivos que você salvou no G9b
(`data/raw/clob_exploracao/G9_payrolls_<slug-do-mercado>_<token>.json`) contêm **só preço**:

```json
{"history": [{"t": 1775347226, "p": 0.23}, ...]}
```

O nome do arquivo traz o slug do MERCADO (`how-many-jobs-added-in-april-296`) e o **token id**,
mas **não traz o slug do DESFECHO**. Compare com o CPI, que você entregou no G4 e que funciona:

```
CPI_april-inflation-us-monthly_will-monthly-inflation-increase-by-0pt3_678205....json
                               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                               este pedaço é o que falta nos payrolls
```

O `payrolls_polymarket_markets.csv` também não tem: ele tem uma linha por MERCADO
(33 linhas, com `n_buckets`), não uma linha por BALDE.

**Consequência exata:** `src/poly_loader.py::bucket_value` lê o valor do balde do slug. Sem
slug de desfecho não existe `E_poly[payrolls]` — e sem esperança não há surpresa, não há view.
Hoje payrolls só serve para **entropia**, que é invariante a rótulo e por isso já roda: a
medição de `premio_condicional.py` usa os 12 eventos de payrolls sem nenhum rótulo. Com
rótulo, payrolls vira a terceira família de view do projeto.

**O que preciso — uma linha por (mercado, balde):**

```
=== G10b — RÓTULO DOS BALDES DE PAYROLLS ===
Fonte usada:            <URL exata do endpoint>   (precisa de chave? SIM / NÃO)
Arquivo salvo:          <caminho>
Nº de linhas:           <n>   (esperado: soma dos n_buckets do CSV do G9b)
Colunas:                slug_mercado, token_id, outcome, slug_desfecho, familia
Mercados sem rótulo:    <lista, ou "nenhum">
Grades com ponta aberta: <em quais mercados o balde extremo é "X ou mais" / "X ou menos">
```

- **`token_id` é a chave que casa com o nome do arquivo** que você já salvou — é ele que amarra
  o rótulo à série. Sem essa coluna o resto não serve.
- **`outcome`** = o texto como o mercado escreve (ex.: `"150k-199k"`, `"4.3%"`), **cru, sem
  normalizar**. Eu converto para número aqui, como faço com o CPI.
- **Não rebaixe as séries.** Os 234 JSONs estão bons; isto é só o metadado que ficou de fora.

**Onde deve estar** (você mediu esses endpoints no G9b, então confira em vez de aceitar minha
sugestão): o `GET gamma-api.polymarket.com/events?slug=<slug>` devolve os `markets` do evento,
e cada market traz `clobTokenIds` junto de `outcomes`/`groupItemTitle`. Se o campo tiver outro
nome na resposta real, **use o que existe e reporte o nome verdadeiro** — não force o meu.

**Uma armadilha que você já pagou uma vez, no G9b:** a busca por `unemployment rate` traz
mercado de outros países. Se o levantamento partir de busca de novo, o filtro de EUA que você
aplicou lá vale aqui igual. Se partir do `payrolls_polymarket_markets.csv` (33 linhas, já
filtrado), não tem esse risco — e é o caminho que eu tomaria.

**As duas famílias, e por que quero as duas:** `nfp_jobs_added` (nº de vagas) e
`unemployment_rate` (taxa). Elas saem do MESMO Employment Situation, e no
`premio_condicional.py` conto **um evento por release** (jobs ganha da taxa quando as duas
existem) justamente para não contar o mesmo pregão duas vezes. Mas para a view a taxa pode ser
o melhor instrumento em alguns meses — quero o rótulo das duas e decido depois, medindo.

---

## G10c — Calendário OFICIAL de divulgação do CPI

**O que existe hoje:** `data/raw/cpi_release_dates.csv`, **15 linhas**, jan/2025 → ago/2026, e a
coluna `fonte` diz de onde veio cada data: **as regras dos mercados do Polymarket**
(`Polymarket rules (december-inflation-us-monthly)`). Funciona, e agradeço — mas tem dois limites:

1. **Só existe onde existe mercado.** O calendário do CPI é público desde sempre; o nosso começa
   em 2025 porque o Polymarket começa em 2025. Uma limitação do dado de PREÇO contaminou o dado
   de CALENDÁRIO, que não precisava ter esse limite.
2. **É derivado de regra de mercado, não da fonte oficial.** Vai ao relatório como ressalva, e é
   ressalva evitável.

**Por que vale agora:** uma das views novas tem uma variante que estima o β por **event-study
nos dias de divulgação**. Com 15 datas não roda de forma defensável; com o calendário completo
(~250 divulgações desde 2003) roda.

**O caminho é o mesmo que destravou o G9a:** a **API do FRED** (`api.stlouisfed.org`), com a
chave gratuita que você já tem em `config/secrets.json` — foi ela que resolveu os payrolls
quando o BLS deu 403 e a página do FRED deu 000 nessa rede.

```
=== G10c — CALENDÁRIO OFICIAL DO CPI ===
Fonte usada:            https://api.stlouisfed.org/fred/release/dates?release_id=<id>
release_id usado:       <id>   (+ como você confirmou que é o do CPI)
Arquivo salvo:          <caminho>
Nº de linhas:           <n>
Janela:                 <primeira data> → <última>
Colunas:                release_date, time_et, mes_referencia, fonte
Bate com o CSV atual?:  <quantas das 15 datas atuais são idênticas; quais divergem>
```

- **Não chute o `release_id`.** No G9a o de payrolls era o **50**; o do CPI é outro. Liste
  `/fred/releases` e ache o do Consumer Price Index — e **reporte como confirmou**.
- **`mes_referencia` derivado é aceitável** pela mesma regra do G9a (mês do release − 1), desde
  que venha **marcado como derivado** na coluna `fonte`. A correção fica comigo, como sempre.
- **A conferência que mais me interessa é a última linha do bloco:** as 15 datas que já temos
  batem com o FRED? Se alguma divergir, quero saber **antes** de trocar o arquivo — divergência
  ali muda o dia do evento em medições que já estão feitas e publicadas.
- **Não sobrescreva o `cpi_release_dates.csv`.** Salve ao lado (ex.: `cpi_release_dates_fred.csv`).
  Trocar o arquivo que o backtest lê é mudança de insumo de coisa já medida, e isso é decisão do
  grupo, não efeito colateral de um pedido meu.

---

## O que eu NÃO estou pedindo

- **ZQ**: morto e enterrado. A caça apareceu em três pedidos seus (F6, FOLLOWUP2, FOLLOWUP3) e
  **não tem mais consumidor** — a view B agora usa o `DGS1` do G10a como benchmark. Pode parar
  de procurar de vez.
- **Trocar o benchmark da view 2.2.** Existe uma candidata melhor que o breakeven de 10 anos
  (`EXPINF1YR`, do Cleveland Fed, no FRED), mas isso é reforma de decisão registrada e não entra
  neste pedido. **Não puxe.**
- **Mercado de evento novo** (eleição, geopolítica, tarifas, fiscal): não. Os que morreram,
  morreram por cobertura medida (E com 13 dias, G com 3) e por a informação aterrissar no gap de
  abertura. Não quero repetir.
- **Re-download das séries de payrolls**: não. Os 234 JSONs estão bons.
- **Mercado de trajetória de 2026**: não neste pedido. O M3 (2025) cobre 63% da janela e isso é
  limitação a declarar, não impedimento — e não quero pedido grande no seu caminho crítico.
- **G6 (CPI 2022–2024)**: continua condicional à reunião, sem mudança da minha parte.

---

## Se você não conseguir

Diga cru e siga. Os três têm plano B, então nenhum trava a entrega:

- **Sem o G10a**: a quarta view não existe. A carteira entrega com três (2.2, 2.3 e a de
  incerteza, que não depende de você). É a perda mais concreta da lista, e é por isso que ele
  está em primeiro.
- **Sem o G10b**: payrolls continua entrando só pela entropia (12 eventos já contribuindo hoje) e
  a view direcional de emprego não existe no v1. Vai ao relatório como limitação **de dado**, com
  este pedido citado — atribuída ao formato do arquivo, não a uma escolha de modelo.
- **Sem o G10c**: o β fica na estimação diária, que é a construção da 2.2 e está justificada no
  módulo. Perde-se a comparação entre variantes, não a view.

---

**Do Felipe (otimizador, bridge, integração, camada tática).** Sessão de 2026-08-08.
Contexto no `Decisoes_pendentes.md` do `Felipe`: seção 14 (reabertura de escopo) e seção 15
(views candidatas; a B reformulada é a **15g**, que depende do G10a). Nada fechado.
