# RESPOSTA — FOLLOW-UP `Pedido_Paulo_dados.md` (F1–F10)

> Tudo medido ao vivo contra a API real (2026-07-29, VPN ligada). Scripts:
> `scripts/followup_ids_series.py` (+`_extra`), `scripts/followup_trades_dim.py`,
> `scripts/followup_live_price.py`, `scripts/followup_cpi_sweep.py`,
> `scripts/followup_calendars.py`. Séries cruas em `data/raw/clob_exploracao/`;
> calendários em `data/raw/`. Campo não medido = `?`. Nada normalizado/interpolado.

## F1 — Push

Feito no início da sessão. As 7 commits locais da branch `Paulo` (que incluíam
`scripts/explorar_clob_bidask.py`, `scripts/levantar_mercados_pedido.py`,
`data/raw/clob_exploracao/` e a `RESPOSTA_Pedido_Paulo_dados.md`) estavam só na
máquina — `origin/Paulo` ainda estava no commit dos ETFs (`48cb12e`). Push:

```
48cb12e..fe15206  Paulo -> Paulo
```

Nada foi barrado por `.gitignore` nem por tamanho. Único material fora do controle
de versão: `__pycache__/` e `.pyc` (artefato do Python — correto ficar de fora).
O commit final desta sessão (F2–F10) está no bloco `## Commit` no fim.

## F2 — Identificadores dos 9 mercados

| ID | Título exato do mercado | slug do evento | slug do mercado | conditionId | tokenId Yes | tokenId No |
|---|---|---|---|---|---|---|
| M1 | Will monthly inflation increase by 0.0% or less in July? (PMF — ver buckets) | july-inflation-monthly | will-monthly-inflation-increase-by-0pt0-or-less-in-june-345 | 0xa4dfc7605cd7665efd5af6c5e072b93b8658ec5cc884995751d9ba812999dd63 | 42455172071308476405633209064188045455801526188894250672159234283405709289525 | 65296089124845926346131661216877500848267104504940042408732634028752122820569 |
| M2 | Fed decreases interest rates by 50+ bps after January 2026 meeting? | fed-decision-in-january | fed-decreases-interest-rates-by-50-bps-after-january-2026-meeting | 0x17815081230e3b9c78b098162c33b1ffa68c4ec29c123d3d14989599e0c2e113 | 11862165566757345985240476164489718219056735011698825377388402888080786399275 | 71478852790279095447182996049071040792010759617668969799049179229104800573786 |
| M3 | Will 7 Fed rate cuts happen in 2025? (PMF — ver buckets) | how-many-fed-rate-cuts-in-2025 | will-7-fed-rate-cuts-happen-in-2025 | 0xf4d03ce9ce65ea06654f23e26dead828005511d65bb650cd5a9dc77891406d12 | 106637218023173886895550072700357013102189022015797096007920322441434274793343 | 79328870430805014620288089322067795525620481132773427804769291919755554601870 |
| M4 | US recession in 2025? | us-recession-in-2025 | us-recession-in-2025 | 0xfa48a99317daef1654d5b03e30557c4222f276657275628d9475e141c64b545d | 104173557214744537570424345347209544585775842950109756851652855913015295701992 | 44528029102356085806317866371026691780796471200782980570839327755136990994869 |
| M5 | Will Donald Trump win the 2024 US Presidential Election? | (mercado avulso — sem slug de evento) | will-donald-trump-win-the-2024-us-presidential-election | 0xdd22472e552920b8438158ea7238bfadfa4f736aa4cee91a6b86c39ead110917 | 21742633143463906290569050155826241533067272736897614950488156847949938836455 | 48331043336612883890938759509493159234755048973500640148014422747788308965732 |
| M6 | Will Trump lower tariffs on China in April? | will-trump-lower-tariffs-on-china-in-april | will-trump-lower-tariffs-on-china-in-april | 0xbe5219d1c82daaa110a20c0b50dae77f681f05eb43094e05ea24fe833c5ec47f | 113855018188629272815215854048561973882380218497310887470128856217081250720455 | 108211118887905827198085240321612246840377385685588945381741674294231397172455 |
| M7 | US military action against Iran before July? (primário da view C) | us-military-action-against-iran-before-july | us-military-action-against-iran-before-july | 0x6a67b9d828d53862160e470329ffea5246f338ecfffdf2cab45211ec578b0347 | 114122071509644379678018727908709560226618148003371446110114509806601493071694 | 80978028360254936368371673933700302612703837652131035604541509269884038499223 |
| M7' | US strikes Iran by February 28, 2026? (deadline de maior volume da família) | us-strikes-iran-by | us-strikes-iran-by-february-28-2026-... | 0x3488f31e6449f9803f99a8b5dd232c7ad883637f1c86e6953305a2ef19c77f20 | 110790003121442365126855864076707686014650523258783405996925622264696084778807 | 10832696757358093775468120009000761778513405247768868107262967513475277652998 |
| M8 | Will reconciliation bill be passed by July 3? | reconciliation-bill-passed-by | will-reconciliation-bill-be-passed-by-july-3-428-846 | 0x923334328e7d1b86692e84c34101d314c994ff962c82060bfcaecd4451317d29 | 7299211912834219215826016776799095751192443160841207887023578384459238039537 | 104511845220515605520033610690245567181862010746734604573193199227743014438660 |
| M9 | Which party will control the U.S. Senate after the 2022 election? | which-party-will-control-the-us-senate-after-the-2022-election | which-party-will-control-the-us-senate-after-the-2022-election | 0xe0658c4beed2102c181b3987edff5edd578ad2952a6eb5fa8018925e5d7a48fd | 69984203794322070924779554468751071533998686576952069110752844084141678897886 | 111299642775108135148113523472260651188510255643046337855221699185339755388694 |

Notas: M5 é mercado avulso (resolvido pelo `/markets`, não tem evento-PMF). M7 tem
duas linhas: o episódio jun/2025 (primário da view C) e o deadline de maior volume
da família `us-strikes-iran-by` ($529M no total do evento). O slug de mercado do M1
carrega "in-june" no texto por herança do template do Polymarket, mas o mercado é o
de **julho/2025** (o `question` diz "in July").

### M1 (CPI julho/2025) — um bucket por linha

| rótulo original | tokenId Yes |
|---|---|
| Will monthly inflation increase by 0.0% or less in July? | 42455172071308476405633209064188045455801526188894250672159234283405709289525 |
| Will monthly inflation increase by 0.1% in July? | 64821303263690399903732594539688595805452590843162622040707961845723088940732 |
| Will monthly inflation increase by 0.2% in July? | 15684375191314473267535792118422695910270113185664678474039068400072774179090 |
| Will monthly inflation increase by 0.3% in July? | 10377324574899342046402769562393519344031078028986853698616515589461145799432 |
| Will monthly inflation increase by 0.4% in July? | 29459483225514843783068333233905037381826189647252018970423378292386710025277 |
| Will monthly inflation increase by 0.5% or more in July? | 94518448370307403168819189335389581152402213055337205316245871884733378099372 |

### M3 (nº de cortes do Fed em 2025) — um bucket por linha

| rótulo original | tokenId Yes |
|---|---|
| Will no Fed rate cuts happen in 2025? | 18020161444416260195750543688224692006431301166904957549340226313298366177208 |
| Will 1 Fed rate cut happen in 2025? | 15353185604353847122370324954202969073036867278400776447048296624042585335546 |
| Will 2 Fed rate cuts happen in 2025? | 11661882248425579028730127122226588074844109517532906275870117904036267401870 |
| Will 3 Fed rate cuts happen in 2025? | 17601770442239563289082275181138749951422899442850916335476881677007065139739 |
| Will 4 Fed rate cuts happen in 2025? | 89004595068776945908481855030043950109477136860300352348370395226706216458498 |
| Will 5 Fed rate cuts happen in 2025? | 302273160494790559492931429044277112497487176914839291053945756072421867571 |
| Will 6 Fed rate cuts happen in 2025? | 35428628589990747181456921610814206632405028717182760412162159083085892664954 |
| Will 7 Fed rate cuts happen in 2025? | 106637218023173886895550072700357013102189022015797096007920322441434274793343 |
| Will 8+ Fed rate cuts happen in 2025? | 61673387045681238454585997121170806826401631642653090831500827557099057497566 |

## F3 — Séries cruas dos 9 (entrega física)

Um arquivo por mercado (por bucket nas PMFs) em `data/raw/clob_exploracao/`, retorno
CRU do `/prices-history` (chaves `history`/`t`/`p`). Tabela arquivo → nº de linhas →
1ª/última data (mercados primários; os 125 arquivos de bucket do CPI estão no F8):

| arquivo | linhas | primeira → última |
|---|---|---|
| M1_cpi_monthly_..._4245517207...289525.json (bucket 0.0%) | 56 | 2025-07-16 → 2025-08-12 |
| M2_fomc_fed-decreases-...-50-bps-a_1186216556...399275.json | 266 | 2025-09-18 → 2026-01-28 |
| M3_fed_trajectory_will-7-fed-rate-cuts-..._1066372180...793343.json (bucket "7") | 691 | 2024-12-30 → 2025-12-10 |
| M4_recession_us-recession-in-2025_1041735572...701992.json | 716 | 2025-01-08 → 2026-01-01 |
| M5_trump_2024_..._2174263314...836455.json | 614 | 2024-01-05 → 2024-11-06 |
| M6_china_tariffs_..._1138550181...720455.json | 26 | 2025-04-03 → 2025-04-16 |
| M7_iran_jun2025_..._1141220715...071694.json (episódio jun/2025) | 165 | 2025-04-01 → 2025-06-22 |
| M7_iran_strike_..._1107900031...778807.json (deadline fev/2026) | 79 | 2026-01-20 → 2026-02-28 |
| M8_obbb_debt_..._7299211912...039537.json | 6 | 2025-07-01 → 2025-07-03 |
| M9_midterms_2022_...senate...a_6998420379...897886.json | 0 | **VAZIO** (salvo mesmo assim) |

M1 e M3 têm um arquivo por bucket (6 e 9 arquivos); todos com a mesma janela do
primário. M9 (Senado 2022): série vazia confirmada — arquivo com `{"history":[]}`
salvo, como pedido. (Existe também um `M9_midterms_2022_..._8324778103...625563.json`
com 713 linhas: é o mercado da Câmara **2026** que a busca por volume pegou por
engano na 1ª passada; **não é** o M9 — deixado no diretório apenas por transparência.)

## F4 — Dimensionamento do `data-api /trades`

**Achado que decide tudo:** a data-api capa **`limit=10000` E `offset=10000`** →
só dá para alcançar, no máximo, os **~20.000 trades MAIS RECENTES** de cada mercado.
`offset>10000` → HTTP 400 `"max historical trades offset of 10000 exceeded"`. Os
parâmetros de tempo (`before`/`after`/`start_ts`/`end_ts`/`from`/`to`) são **ignorados**
(não filtram). Ou seja: para mercado grande, `/trades` **não** cobre a vida inteira.

```
=== DIMENSIONAMENTO /trades ===
Mercado:                M5 (Trump 2024) — 0xdd22472e552920b8438158ea7238bfadfa4f736aa4cee91a6b86c39ead110917
URL exata:              https://data-api.polymarket.com/trades?market=<conditionId>&limit=10000&offset=<0 e 10000>
Nº total de trades:     20000 alcançáveis (o total real é muito maior — o mercado tem $1,53bi de volume)
Limite por página:      10000 (param limit; pedir mais devolve 10000 mesmo)
Como pagina:            offset (passo 10000). offset>10000 => HTTP 400
Span coberto:           2024-11-06 04:07:47 → 2024-11-06 15:20:35 (UTC)  ← só o dia da eleição
Cobre a vida inteira?   NÃO — a série /prices-history começa 2024-01-05; os 20k trades alcançáveis são todos de 2024-11-06
Nº de requests / tempo: 2 requests / 7,1s
Rate limit encontrado:  não encontrado (nenhum 429)
Trades por dia (mediana): 20000 (janela alcançável = 1 dia)
Dias sem NENHUM trade:  0 (na janela alcançável de 1 dia)
Campos crus:            proxyWallet, side, asset, conditionId, size, price, timestamp, title, slug, icon, eventSlug, outcome, outcomeIndex, name, pseudonym, bio, profileImage, profileImageOptimized, transactionHash
Amostra (3 linhas cruas):
  {side:SELL, price:0.998, size:94.37,  ts:1730906435, tx:0xcef4b27fdb...}
  {side:SELL, price:0.998, size:5.4,    ts:1730906435, tx:0x11bce3547a...}
  {side:BUY,  price:0.999, size:0.35,   ts:1730906433, tx:0x2b6365ceac...}

=== DIMENSIONAMENTO /trades ===
Mercado:                M4 (recessão) — 0xfa48a99317daef1654d5b03e30557c4222f276657275628d9475e141c64b545d
URL exata:              https://data-api.polymarket.com/trades?market=<conditionId>&limit=10000&offset=<0 e 10000>
Nº total de trades:     20000 alcançáveis (bate no teto; total real > 20000)
Limite por página:      10000
Como pagina:            offset (passo 10000). offset>10000 => HTTP 400
Span coberto:           2025-05-11 15:16:50 → 2026-01-01 08:46:33 (UTC)
Cobre a vida inteira?   NÃO — série começa 2025-01-08; os trades alcançáveis só vão até 2025-05-11 (trunca ~4 meses iniciais)
Nº de requests / tempo: 2 requests / 10,0s
Rate limit encontrado:  não encontrado (nenhum 429)
Trades por dia (mediana): 60
Dias sem NENHUM trade:  0 (na janela alcançável de 236 dias)
Campos crus:            (idênticos ao M5)
Amostra (3 linhas cruas):
  {side:SELL, price:0.999, size:62.16,    ts:1767257193, tx:0xf5ff1da175...}
  {side:SELL, price:0.001, size:10,       ts:1767251233, tx:0xe0c1b58dbb...}
  {side:BUY,  price:0.999, size:92646.61, ts:1767251117, tx:0xbe49593a22...}
```

**BUY/SELL por janela de 12h** (o que decide se dá para reconstruir proxy de bid/ask):

- **M4 (liquidez normal — 236 dias):**
  ```
  Janelas de 12h na amostra:            470 (com >=1 trade; de 472 slots do span)
  Janelas com BUY e SELL (ambos):       469 (99,8%)
  Janelas com um lado só:               1  (0,2%)
  Janelas vazias:                       2  (0,4%)
  ```
- **M5 (só cobre o dia da eleição — liquidez anormalmente alta):**
  ```
  Janelas de 12h na amostra:            2
  Janelas com BUY e SELL (ambos):       2 (100%)
  Janelas com um lado só / vazias:      0
  ```
  (Aviso: para M5 a janela alcançável **não** é "um dia normal" — é o pico da
  eleição; por isso o M4 é a medida representativa.)

**Extra — `/trades` cobre 2022 (M9)?** **NÃO.** `data-api /trades?market=<conditionId
do Senado 2022>` devolve **0 trades** (mesmo o mercado tendo $1,77M de volume no
Gamma). Ou seja, o M9 continua sem série por **as duas** vias (`/prices-history` vazio
e `/trades` vazio).

## F5 — Que preço é a série do `/prices-history`

Medido em mercado VIVO (2026-07-29 ~22:50 UTC). Em ambos, o último ponto da série
**bate com o `midpoint`**, não com o `last-trade-price`:

```
=== QUE PREÇO É A SÉRIE ===  (LÍQUIDO)
Mercado vivo usado:  will-jesus-christ-return-before-2027 | tokenYes 6932431735...608517 | volume $64,8M
Timestamp da coleta: 2026-07-29T22:50:03Z
prices-history (último ponto): 0.0195
last-trade-price:              0.02
midpoint:                      0.0195
book: melhor bid / melhor ask: 0.019 / 0.02
Conclusão medida: a série bate com MIDPOINT (0.0195 = midpoint; ≠ last-trade 0.02)

=== QUE PREÇO É A SÉRIE ===  (mais fino disponível)
Mercado vivo usado:  will-jb-pritzker-win-the-2028-us-presidential-election | tokenYes 7094873140...444076 | volume $12,4M
Timestamp da coleta: 2026-07-29T22:50:07Z
prices-history (último ponto): 0.0055
last-trade-price:              0.005
midpoint:                      0.0055
book: melhor bid / melhor ask: 0.005 / 0.006
Conclusão medida: a série bate com MIDPOINT (0.0055 = midpoint; ≠ last-trade 0.005)
```

Ressalva honesta: não achei um mercado **realmente fino** (volume baixo) que ainda
exponha `/book` — os mercados de baixo volume ativos devolvem **book vazio** (sem
bid/ask nem em tempo real). Então o teste "líquido vs fino" ficou entre um mercado
de $64,8M e um de $12,4M; nos dois a série = midpoint. Corrige a inferência anterior
(que dizia "comporta-se como último trade"): **medido, é o midpoint.**

## F6 — Contrato ZQ específico no yfinance

**Nenhuma** sintaxe de contrato mensal específico funcionou no yfinance — só o
contínuo `ZQ=F` puxa.

```
=== ZQ CONTRATO ESPECÍFICO ===
Sintaxe testada | Puxou? | Nº de obs | Desde       | Tem Open? | Observação
ZQZ25.CME       | NÃO    | 0         | —           | —         | vazio
ZQZ25           | NÃO    | 0         | —           | —         | vazio
ZQ=Z25          | NÃO    | 0         | —           | —         | vazio
ZQZ2025         | NÃO    | 0         | —           | —         | vazio
ZQZ25.NYB       | NÃO    | 0         | —           | —         | vazio
ZQF26           | NÃO    | 0         | —           | —         | vazio
ZQF26.CME       | NÃO    | 0         | —           | —         | vazio
ZQF2026         | NÃO    | 0         | —           | —         | vazio
ZQ=F (contínuo) | SIM    | 252       | 2025-07-29  | sim       | único que funciona; NÃO é contrato específico
```

Como **nenhuma** sintaxe de contrato específico funciona no yfinance, as fontes
alternativas que existem (listadas, **sem escolher** — decisão do grupo):
- **CME** (dados oficiais 30-Day Fed Funds ZQ; via CME DataMine ou site, alguns pagos);
- **Nasdaq Data Link / Quandl** (datasets CME de futuros — historicamente `CME/ZQ...`, exige conta/chave);
- **Barchart** (tem os contratos mensais ZQ por símbolo, parte paga);
- **FRED** não tem o **contrato** ZQ (só a taxa efetiva `DFF`/`EFFR` e futuros implícitos indiretos).

## F7 — Calendários FOMC e CPI

**Fontes candidatas (listadas, NÃO escolhidas):**
- FOMC: (1) `federalreserve.gov/monetarypolicy/fomccalendars.htm` — HTML, sem chave,
  raspagem **[USADA]**; (2) PDFs de statement `monetaryYYYYMMDD...` — dão a data exata
  do anúncio **[usada para preencher a data]**; (3) FRED — não tem série pronta de datas do FOMC.
- CPI: (1) `bls.gov/schedule/news_release/cpi.htm` — HTML estruturado, sem chave, mas
  respondeu **HTTP 403 (bot-block)** **[FALHOU]**; (2) as *rules* dos mercados de CPI
  no Polymarket — trazem data + hora ET + mês de referência **[USADA — fallback do pedido]**;
  (3) FRED release calendar (API, exige chave).

Salvos:
- `data/raw/fomc_dates.csv` → **48 linhas**, 2022-01-26 → 2027-12-08. 8 reuniões/ano.
  Colunas `date, time_et, tipo, fonte`. `time_et` fica vazio (não consta no HTML).
  `tipo` = "reunião regular" ou "reunião regular (SEP+coletiva)" (o "*" da página do
  Fed marca reunião com Summary of Economic Projections, **não** extraordinária).
  Excluído o "notation vote" de 22/08/2025 (voto de framework, não decisão de juros).
- `data/raw/cpi_release_dates.csv` → **15 linhas**, ref dez/2024→jul/2026 (release
  2025-01-13 → 2026-08-12). Colunas `release_date, time_et, mes_referencia, fonte`.
  Todas via rules do Polymarket, todas 8:30 AM ET.

Ressalvas medidas (não corrigidas — dado cru):
- `january-inflation-monthly` (CPI jan/2025) tem **descrição vazia** (70 chars) — sem
  data de release para extrair; ficou de fora do CSV.
- `december-inflation-us-monthly` (ref **dezembro/2025**) traz nas próprias rules
  "released on **January 13, 2025**" — **typo na fonte** (o release do CPI de dez/2025
  é em jan/**2026**). Mantido como veio; sinalizado aqui.

## F8 — Varredura do CPI mês a mês (US, ~18 meses)

| Mês de referência | slug do evento | Nº de buckets | Rótulos (originais, na ordem) | Volume (USD) | 1ª data | Última data |
|---|---|---|---|---|---|---|
| dez/2024 | december-inflation-monthly | 3 | 0.3% or less / 0.4% / 0.5% or more | 15.186 | 2025-01-14 | 2025-01-15 |
| jan/2025 | january-inflation-monthly | 4 | 0.1% or less / 0.2% / 0.3% / 0.4% or more | 384.583 | 2025-01-16 | 2025-02-12 |
| fev/2025 | february-inflation-monthly | 5 | 0.1% or less … 0.5% or more | 103.829 | 2025-02-08 | 2025-03-12 |
| mar/2025 | march-inflation-monthly | 5 | 0.1% or less … 0.5% or more | 304.092 | 2025-03-13 | 2025-04-10 |
| mai/2025 | may-inflation-monthly | 5 | 0.0% or less … 0.4% or more | 764.230 | 2025-05-14 | 2025-06-11 |
| jun/2025 | june-inflation-monthly | 5 | 0.0% or less … 0.4% or more | 847.992 | 2025-06-12 | 2025-07-15 |
| jul/2025 | july-inflation-monthly | 6 | 0.0% or less … 0.5% or more | 1.089.178 | 2025-07-16 | 2025-08-12 |
| ago/2025 | august-inflation-monthly | 5 | 0.0% or less … 0.4% or more | 628.822 | 2025-08-13 | 2025-09-11 |
| set/2025 | september-inflation-monthly | 5 | 0.1% or less … 0.5% or more | 385.912 | 2025-09-12 | 2025-10-24 |
| out/2025 | october-inflation-monthly | 5 | 0.1% or less … 0.5% or more | 257.539 | 2025-10-31 | 2025-11-22 |
| nov/2025 | november-inflation-monthly | 5 | 0.1% or less … 0.5% or more | 301.955 | 2025-11-14 | 2026-01-13 |
| dez/2025 | december-inflation-us-monthly | 5 | 0.1% or less … 0.5% or more | 480.241 | 2025-12-06 | 2026-01-13 |
| mar/2026 | march-inflation-us-monthly | 6 | 0.3% or less / 0.4% / 0.5% / 0.6% / 0.7% / 0.8% or more | 703.745 | 2026-03-12 | 2026-04-09 |
| abr/2026 | april-inflation-us-monthly | 9 | 0.3% or less … 1.0% / ≥1.1% | 128.201 | 2026-04-12 | 2026-05-12 |
| mai/2026 | may-inflation-us-monthly | 9 | 0.1% or less … 0.9% or more | 127.500 | 2026-05-13 | 2026-06-10 |
| jun/2026 | june-inflation-us-monthly-20260610151033433 | 9 | 0.1% or less … 0.9% or more | 52.283 | 2026-06-11 | 2026-07-14 |
| jul/2026 | july-inflation-us-monthly-20260714151042665 | 9 | **decrease** 0.7% or more … flat 0.0% / increase 0.1% or more | 65.657 (vivo) | 2026-07-15 | 2026-07-29 |

**Onde o formato muda (medido):**
- **nº de buckets:** 3 (dez/24) → 4 (jan/25) → 5 (padrão fev–dez/25) → 6 em jul/25 e
  mar/26 → **9** a partir de abr/26.
- **abril/2025** não existe como evento US mensal separado (não achei `april-inflation-monthly`
  de 2025 no public-search — só o de 2026); é uma lacuna real da série de 2025.
- **grade desloca para cima em mar/2026:** os buckets vão de "0.3% or less" a "0.8% or
  more" (regime de inflação mais alta), em vez de "0.0/0.1% or less".
- **jul/2026 inverte o sinal:** os buckets viram **queda** ("decrease by 0.7%…", "stay
  flat 0.0%", "increase by 0.1% or more") — cenário de deflação mensal; redação
  totalmente diferente dos demais.
- **naming:** 2025 usa `<mês>-inflation-monthly`; 2026 usa `<mês>-inflation-us-monthly`
  (alguns com sufixo de timestamp no slug). Há colisão de nome de mês entre anos —
  o ano só se resolve pelas datas da série.

Séries cruas de cada bucket salvas em `data/raw/clob_exploracao/` com prefixo `CPI_`.

## F9 — "Dias sem trade": contagem (grade de 12h, sobre o `/prices-history`)

| ID | Nº de pontos na série | Slots de 12h esperados na janela | Slots ausentes | % ausente | Maior buraco consecutivo (h) |
|---|---|---|---|---|---|
| M2 (Fed jan/2026) | 266 | 266 | 0 | 0,0% | 24,0 |
| M5 (Trump 2024) | 614 | 614 | 0 | 0,0% | 12,0 |
| M6 (tarifas China abr/2025) | 26 | 26 | 0 | 0,0% | 12,0 |
| M8 (reconciliation jul/3) | 6 | 6 | 0 | 0,0% | 12,0 |

Nota: no M2 o total de pontos casa com o esperado (0 ausentes), mas há um passo de
24h no meio (um ponto fora da grade exata de 12h compensa outro) — por isso "maior
buraco" = 24h com "ausentes" = 0. São séries limpas, sem buracos relevantes.

## F10 — Granularidade em mercado VIVO

```
=== GRANULARIDADE EM MERCADO VIVO ===
Mercado: will-jesus-christ-return-before-2027 (tokenYes 6932431735...608517)
fidelity=1    → 4288 pontos | passo mediano 600s  | 2026-06-29T23:00 → 2026-07-29T22:49
fidelity=10   → 4288 pontos | passo mediano 600s  | 2026-06-29T23:00 → 2026-07-29T22:49
fidelity=60   → 712  pontos | passo mediano 3600s | 2026-06-29T23:00 → 2026-07-29T22:49
fidelity=180  → 236  pontos | passo mediano 10800s| 2026-06-30T00:00 → 2026-07-29T22:49
fidelity=720  → 472  pontos | passo mediano 43200s| 2025-11-26T00:00 → 2026-07-29T22:50
Observação: em mercado VIVO a série fina existe, mas com JANELA LIMITADA. fidelity=1
e 10 dão o mesmo passo real de 600s (10 min) — o "1 min" não é entregue; o piso
efetivo com interval=all é 10 min. As fidelidades finas (1/10/60/180) cobrem só os
~últimos 30 dias; só fidelity=720 (12h) traz a vida inteira (desde 2025-11-26).
Ou seja: granularidade fina ⇒ janela curta; janela longa ⇒ só 12h. (Contraste com
mercado RESOLVIDO, onde só fidelity=720 devolve qualquer dado.)
```

## Bloqueios

- **BLS bloqueado por bot** (`bls.gov/schedule/...` → HTTP 403). Datas de release do
  CPI vieram das *rules* dos mercados (fallback autorizado). `january-inflation-monthly`
  não entrou por ter descrição vazia.
- **`/trades` capado em 20k trades** (limit 10000 + offset 10000; timestamp ignorado).
  Para mercado grande não cobre a vida inteira — só a cauda mais recente. Não é rede,
  é limite da API.
- **M9 (Senado 2022):** morto pelas duas vias — `/prices-history` vazio e `/trades` = 0.
- **ZQ contrato específico:** nenhuma sintaxe funciona no yfinance (só o contínuo `ZQ=F`).
  Fonte alternativa é decisão do grupo.
- **Mercado realmente fino com book:** não encontrado — mercados de baixo volume
  devolvem `/book` vazio. O teste do F5 ficou entre dois mercados líquidos.
- **abril/2025 CPI:** não existe evento US mensal separado (lacuna real na série de 2025).

## Commit

```
<preenchido no push final desta sessão — ver LOG.md>
```
