# RESPOSTA — `PEDIDO_G9` payrolls (calendário + mercados no Polymarket)

> **Do Paulo (pipeline de dados) para o Felipe.** Levantamento, não decisão. Campo não
> medido vai como `?`; dado cru não normalizado. Sessão de 2026-08-06, VPN ligada,
> medido ao vivo contra a API real do Polymarket.
>
> **Resumo em uma linha:** o Polymarket **tem** mercado mensal de emprego dos EUA de 2025
> em diante (em duas famílias, ambas multi-bucket) — a amostra pode de fato crescer. **Mas
> o calendário oficial de release (G9a) ficou bloqueado**: BLS segue 403 e o FRED está
> inalcançável por esta rede (detalhe em Bloqueios).

---

## G9a — Calendário de divulgação dos payrolls

**Bloqueado nas duas fontes nomeadas (BLS e FRED).** Reporto qual falhou e como, conforme pedido.

```
=== G9a — CALENDÁRIO DE PAYROLLS ===
Fonte usada:            NENHUMA das duas funcionou (ver abaixo)   (precisa de chave? ver abaixo)
Arquivo salvo:          — (não gerado; não invento datas sem fonte)
Nº de linhas:           ?
Janela:                 ?
Colunas:                (alvo, igual ao cpi_release_dates.csv: release_date, time_et, mes_referencia, fonte)
Hora de divulgação:     8:30 AM ET   (declarada pela regra dos próprios mercados do Polymarket — ver G9b)
Meses faltando no meio: ?  (não há calendário para medir buracos)
```

**Tentativas, ao vivo (2026-08-06, VPN ligada):**

| Fonte candidata | URL exata | Precisa de chave? | Resultado |
|---|---|---|---|
| **(1) BLS — schedule** | `https://www.bls.gov/schedule/news_release/empsit.htm` | NÃO | **HTTP 403** (bot-block do servidor; independe de VPN — igual ao G6 do follow-up 2) |
| **(2a) FRED — página de release dates** | `https://fred.stlouisfed.org/release/dates?rid=50` (Employment Situation = release id 50) | NÃO | **Conexão falha (000)**: o DNS resolve para o Akamai, mas o handshake é recusado por esta rede, mesmo com VPN e User-Agent de browser |
| **(2b) FRED — API** | `https://api.stlouisfed.org/fred/release/dates?release_id=50&file_type=json` | **SIM (api_key)** | **HTTP 400** = alcançável, mas exige `api_key` (não temos chave no projeto) |

- O `api.bls.gov/publicAPI/v2` (API pública de séries do BLS) responde **200**, mas devolve os
  **valores** da série (ex.: `CES0000000001`), **não as datas de divulgação** — não serve para o calendário.
- **Não fabriquei o calendário por regra** (ex.: "primeira sexta-feira do mês"): a regra tem
  exceções reais (feriados; e em 2025 os atrasos do *shutdown* — ver G9b), então uma data derivada
  contaminaria a medição. Um `?` honesto aqui é melhor que um número inventado.

**Byproduto parcial (não é o calendário oficial):** o texto da *regra* de alguns mercados de
payrolls do Polymarket declara a data e hora do release. Consegui extrair **5** datas (as recentes),
todas **8:30 AM ET** — batendo com a convenção do Employment Situation:

| Mês de referência | Release (da regra do mercado) | Hora |
|---|---|---|
| February 2026 | 2026-03-06 | 8:30 AM ET |
| April 2026 | 2026-05-08 | 8:30 AM ET |
| May 2026 | 2026-06-05 | 8:30 AM ET |
| June 2026 | 2026-07-02 | 8:30 AM ET |
| July 2026 | 2026-08-07 | 8:30 AM ET |

A maioria das descrições **não** traz a frase "released on … at … ET", então isso **não** reconstrói
a janela inteira — fica como confirmação da hora (8:30 ET) e de 5 datas, não como o calendário.

**Como destravar o G9a (decisão sua):** (a) uma **FRED API key** (grátis, registro no site do FRED)
— destrava o `release_id=50` inteiro; ou (b) rodar o scrape do BLS/FRED de uma rede sem o bloqueio
do Akamai. Fora isso, o G9a permanece `?`.

> Script pronto que já tenta as duas fontes na ordem certa: `scripts/followup_calendars.py` (rota
> FOMC/CPI) — o payroll seguiria o mesmo padrão assim que uma das fontes abrir.

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

- **G9a (calendário oficial): bloqueado.** BLS = **403** (bloqueio de bot do servidor, independe de
  VPN); FRED página = **conexão recusada (000)** por esta rede (Akamai), mesmo com VPN; FRED API =
  alcançável mas exige **api_key** (não temos). Não fabriquei datas por regra. **Destrava com uma FRED
  API key** ou rodando de uma rede sem o bloqueio do Akamai. Byproduto: 5 datas + a hora 8:30 ET
  confirmadas pela regra dos mercados (não é o calendário completo).
- **Sem relação com G9 (continuam parados):** G5 (volume no tempo) espera a spec do Ω com a Lia; G6
  (CPI 2022–2024) segue condicional à reunião.

## Commit

- **Branch:** `Paulo`
- **Hash:** `<PREENCHER_APOS_COMMIT>`
