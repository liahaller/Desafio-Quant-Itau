# RESPOSTA — `PEDIDO_G9` payrolls (calendário + mercados no Polymarket)

> **Do Paulo (pipeline de dados) para o Felipe.** Levantamento, não decisão. Campo não
> medido vai como `?`; dado cru não normalizado. Sessão de 2026-08-06, VPN ligada,
> medido ao vivo contra as APIs reais.
>
> **Resumo em uma linha:** o Polymarket **tem** mercado mensal de emprego dos EUA de 2025
> em diante (duas famílias, ambas multi-bucket) — a amostra pode de fato crescer. E o
> **calendário oficial de release (G9a) foi destravado** via FRED API (chave gratuita) —
> 23 datas, dez/2024→nov/2026. As 5 datas que os dois lados têm em comum batem 100%.

---

## G9a — Calendário de divulgação dos payrolls

**Resolvido via FRED API** (a 2ª fonte do pedido), com uma chave gratuita. O BLS continuou
403 e a *página* do FRED continua bloqueada por esta rede — mas a **API** do FRED
(`api.stlouisfed.org`) é alcançável e, com chave, entrega o `release_id=50` inteiro.

```
=== G9a — CALENDÁRIO DE PAYROLLS ===
Fonte usada:            https://api.stlouisfed.org/fred/release/dates?release_id=50   (precisa de chave? SIM — FRED API key gratuita)
Arquivo salvo:          data/raw/payrolls_release_dates.csv
Nº de linhas:           23
Janela:                 December 2024 → November 2026  (mês de referência)
Colunas:                release_date, time_et, mes_referencia, fonte
Hora de divulgação:     8:30 AM ET  (o FRED não declara; hora padrão do BLS, confirmada pela regra dos mercados no G9b)
Meses faltando no meio:  1 buraco real — nenhum release entre 2025-09-05 e 2025-11-20 (76 dias; shutdown de 2025)
```

**Script:** `scripts/g9a_payrolls_calendar.py` (chave lida de `config/secrets.json`, que está
no `.gitignore` — a chave **não** vai para o repositório).

**O que é medido vs. derivado (honestidade):**
- `release_date` = **MEDIDO** (data que o FRED lista para o release id 50).
- `mes_referencia` = **DERIVADO** por `mês(release) − 1` (o Employment Situation sai no início
  do mês seguinte). Regra determinística — **exceto na janela do shutdown de 2025**, onde o BLS
  remanejou o cronograma e a derivação **não bate 1:1**. Marquei isso **cru** no CSV (coluna
  `fonte` da linha 2025-11-20 traz `[ATENCAO: gap de 76 dias … shutdown …]`) — **a correção é
  sua**, no tratamento, como combinado.
- `time_et` = "8:30 AM": o FRED não declara hora; é a hora padrão do BLS, **confirmada** pela
  regra dos mercados do Polymarket (G9b). Sinalizado na coluna `fonte`.

**Tentativas, ao vivo (2026-08-06, VPN ligada):**

| Fonte candidata | URL exata | Chave? | Resultado |
|---|---|---|---|
| (1) BLS — schedule | `www.bls.gov/schedule/news_release/empsit.htm` | NÃO | **403** (bot-block do servidor; independe de VPN) |
| (2a) FRED — página | `fred.stlouisfed.org/release/dates?rid=50` | NÃO | **000** (Akamai recusa a conexão por esta rede, mesmo com VPN) |
| **(2b) FRED — API** ✅ | `api.stlouisfed.org/fred/release/dates?release_id=50` | **SIM** | **200 — USADA** (chave FRED gratuita) |

- `api.bls.gov/publicAPI/v2` responde 200 mas só dá **valores** da série, não datas de release — não serve.

**Validação cruzada (dois lados independentes batem 100%):** as 5 datas que a regra dos mercados
do Polymarket declara (G9b) são idênticas às do FRED:

| Mês de referência | FRED (G9a) | Regra do mercado (G9b) |
|---|---|---|
| February 2026 | 2026-03-06 | 2026-03-06 ✓ |
| April 2026 | 2026-05-08 | 2026-05-08 ✓ |
| May 2026 | 2026-06-05 | 2026-06-05 ✓ |
| June 2026 | 2026-07-02 | 2026-07-02 ✓ |
| July 2026 | 2026-08-07 | 2026-08-07 ✓ |

---

## G9b — Varredura dos mercados de payrolls no Polymarket

**Achado principal: SIM, existe mercado mensal de emprego dos EUA de 2025 em diante — e em duas
famílias, ambas multi-bucket.** Isso é exatamente o "mais linhas na mesma medição" que você pediu.

- **Script:** `scripts/g9b_payrolls_polymarket.py`
- **Buscas (endpoint):** `GET gamma-api.polymarket.com/public-search?q=<termo>` para os 4 termos
  sugeridos: `payrolls`, `nonfarm`, `jobs report`, `unemployment rate`.
- **Séries cruas salvas:** `data/raw/clob_exploracao/G9_payrolls_<slug>_<token>.json` (234 arquivos,
  todos os buckets de todos os eventos US) via `clob.polymarket.com/prices-history` (`fidelity=720` = 12h).
- **Resumo tabular (medido):** `data/raw/payrolls_polymarket_markets.csv` (33 linhas).

### As três perguntas específicas de payrolls

**1) Buckets ou binário?** As duas famílias úteis são **multi-bucket** (mesmo caminho do CPI):

| Família | Slug típico | Estrutura | O que é |
|---|---|---|---|
| `nfp_jobs_added` | `how-many-jobs-added-in-<mês>` | **multi-bucket (5–8)** | nº de nonfarm payrolls por faixa — **análogo direto ao CPI** |
| `unemployment_rate` | `<mês>-unemployment-rate` | **multi-bucket (4–9)** | taxa de desemprego por faixa — **mesmo relatório** (Employment Situation) |
| `nfp_prints_negative` | `<mês>-jobs-report-prints-negative` | **binário (Yes/No)** | só o sinal do payroll — jun/jul 2025 (ponte antes dos buckets) |
| `release_timing_meta` | `…report-be-released-by-…` / `…during-government-shutdown` | binário | **não é PMF do número** — mede se/quando o relatório sai |

- **A grade de buckets muda de tamanho ao longo do tempo, igual ao CPI.** `nfp_jobs_added` varia de
  **5 a 8** buckets; `unemployment_rate` varia de **4 a 9**. A cascata precisa tratar grade variável.
- **Cuidado (importante):** `unemployment rate` traz muito mercado de **outros países** (Japão, México,
  Brasil, Reino Unido, Índia, Canadá) — **filtrei fora** (só EUA). O CSV/tabela abaixo é só EUA.

**2) A série chega até o dia da divulgação?** **Sim, para os mercados multi-bucket resolvidos** — a
última data da série bate com o dia do release, então o **slot de 12h imediatamente anterior à
abertura existe**. Exemplos (resolvidos): abr/2026 série→2026-05-08 (release 05-08); mai/2026→2026-06-05
(06-05); jun/2026→2026-07-02 (07-02); fev/2026→2026-03-06 (03-06). **Exceções a vigiar:**
- `nfp_prints_negative` (jun/jul 2025): série **degenerada** (jun/2025 tem 1 ponto só, 2025-07-03) —
  não dá PMF utilizável.
- Meses do **shutdown** de 2025 (set/2025 e nov/2025): séries com cauda estranha/atrasada (set/2025
  negocia até 2025-11-07; nov/2025 só 2025-11-19→2025-12-16). O release atrasou; a série reflete isso.

**3) Termos de busca — a busca é parte da resposta.** Cada termo achou coisas diferentes:
- `payrolls` e `nonfarm` → pegam a família `how-many-jobs-added-in-*` (e nada de `unemployment-rate` puro).
- `jobs report` → pega `how-many-jobs-added`, os binários `*-prints-negative` e os meta de shutdown/release-timing.
- `unemployment rate` → pega os `*-unemployment-rate` (US **e** estrangeiros — filtrados).
- Nenhum termo, sozinho, pega tudo; por isso rodei os quatro e uni.

### Cobertura mês a mês — janela de referência 2025-01 → 2026-08

Legenda: **✅ multi-bucket US** (útil p/ entropia) · **◑ só binário/meta** (PMF pobre ou não é do número) · **❌ sem mercado**.

| Mês ref. | Status | Mercados US encontrados (estrutura · vol · série) |
|---|---|---|
| **Jan 2025** | ✅ | `how-many-jobs-added-in-january` (6 bkt · 138k · 2025-01-14→02-07); `january-unemployment-rate` (4 bkt · 48k · 01-14→02-07) |
| **Feb 2025** | ✅ | `february-unemployment-rate` (5 bkt · 225k · 2025-02-09→03-07) — *só a família taxa* |
| **Mar 2025** | ✅ | `march-unemployment-rate` (5 bkt · 57k · 2025-03-08→04-04) — *só a família taxa* |
| **Apr 2025** | ❌ | **lacuna real** (nenhuma família) |
| **May 2025** | ❌ | **lacuna real** (nenhuma família) |
| **Jun 2025** | ◑ | `june-jobs-report-prints-negative` (binário · 31k · série degenerada 1 ponto) |
| **Jul 2025** | ◑ | `july-jobs-report-prints-negative` (binário · 4k · 2025-07-04→08-01) |
| **Aug 2025** | ✅ | `how-many-jobs-added-in-august-643` (5 bkt · 342k); `august-unemployment-rate` (6 bkt · 206k); `august-jobs-report-prints-negative` (binário · 32k) |
| **Sep 2025** | ✅⚠ | `how-many-jobs-added-in-september-522` (7 bkt · 393k · série 09-07→**11-07**); `september-unemployment-rate` (6 bkt · 347k) — *shutdown: série atrasada* |
| **Oct 2025** | ◑ | **só meta**: `will-the-next-bls-employment-situation-report-be-released-by-october-3-2025-…` (binário · 73k · 1 ponto). **Não há mercado do número** (shutdown) |
| **Nov 2025** | ✅⚠ | `how-many-jobs-added-in-november-693` (7 bkt · 22k · série **12-11→12-16**); `november-unemployment-rate-765` (6 bkt · 182k) — *shutdown: série curta/tardia* |
| **Dec 2025** | ✅ | `how-many-jobs-added-in-december-853` (7 bkt · 18k); `december-unemployment-rate-938` (6 bkt · 74k) |
| **Jan 2026** | ✅ | `how-many-jobs-added-in-january-321` (7 bkt · 308k); `january-unemployment-rate-333` (6 bkt · 101k) |
| **Feb 2026** | ✅ | `how-many-jobs-added-in-february-246` (8 bkt · vol `?`); *(release 2026-03-06 8:30 ET pela regra)* |
| **Mar 2026** | ✅ | `march-unemployment-rate-561` (9 bkt · 308k · 2026-02-14→03-28) |
| **Apr 2026** | ✅ | `how-many-jobs-added-in-april-296` (8 bkt · 28k); `april-unemployment-rate-372` (9 bkt · 90k) |
| **May 2026** | ✅ | `how-many-jobs-added-in-may-945` (6 bkt · 13k); `may-unemployment-rate-168` (9 bkt · 23k) |
| **Jun 2026** | ✅ | `how-many-jobs-added-in-june-…` (6 bkt · 16k); `june-unemployment-rate-734` (9 bkt · 39k) |
| **Jul 2026** | ✅ | `how-many-jobs-added-in-july-…` (6 bkt · 27k · 2026-07-03→**08-06**); `july-unemployment-rate-…` (9 bkt · 41k) — *ainda vivo; release 2026-08-07* |
| **Aug 2026** | ❌ | sem mercado — **esperado** (é o mês corrente; o relatório de ago/2026 só sai em set/2026) |

**Contagem (janela 2025-01→2026-08, 20 meses):**
- Com mercado multi-bucket US (✅): **15 meses** — desses, **2 marcados ⚠** (set/nov 2025, séries perturbadas pelo *shutdown*).
- Só binário/meta (◑): **3 meses** (jun, jul, out 2025).
- Lacuna real / esperada (❌): **2** reais (abr, mai 2025) + **1** esperado (ago/2026, mês corrente).

**Fora da janela pedida (mas existem, 2024):** `how-many-jobs-added-in-december` (dez/2024, 6 bkt),
`december/november/october-2024 unemployment-rate` — atribuí o ano pela data da série (o slug sozinho
não distingue dez/2024 de dez/2025, mesmo problema do CPI no G4).

### Leitura para o seu denominador (sem eu decidir)

Meses com **PMF multi-bucket US que chega ao release** (candidatos "limpos" à sua medição de entropia,
família `nfp_jobs_added`): **jan/2025, ago, dez/2025, jan, fev, abr, mai, jun, jul/2026** — mais
set e nov/2025 se você aceitar as séries perturbadas pelo shutdown. A família `unemployment_rate`
adiciona meses (ex.: fev, mar/2025) e é do **mesmo relatório**. **Quantos desses "contam" é decisão
sua** — eu só reporto estrutura, volume e se a série alcança o dia do anúncio. Confirmo o formato:
é a mesma estrutura de buckets do CPI, então entra na cascata que já existe.

---

## Bloqueios

- **G9a: destravado** com FRED API key gratuita (o BLS segue 403 e a *página* do FRED segue
  bloqueada por esta rede, mas a **API** do FRED resolve). Único resíduo, **sinalizado e cru**: a
  janela do **shutdown de 2025** (set–nov/2025) tem 1 release remanejado — o `mes_referencia`
  derivado ali não bate 1:1; correção fica com o Felipe no tratamento.
- **Sem relação com G9 (continuam parados):** G5 (volume no tempo) espera a spec do Ω com a Lia; G6
  (CPI 2022–2024) segue condicional à reunião.

## Commit

- **Branch:** `Paulo`
- **Hash:** `6daebbf` (G9a via FRED API; G9b em `5c72edb`)
