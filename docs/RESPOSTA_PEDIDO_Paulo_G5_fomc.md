# Para a Lia — G5 agora alcança o FOMC (chave + as 76 faixas)

Lia, resolvi os dois problemas que você levantou. Os dois arquivos agora casam por
`conditionId`, e a view 2.3 saiu do único mercado de antes para **as 76 faixas × reunião**,
no mesmo formato do resto do G5. Abaixo, item por item do que você pediu, mais um `?` honesto
no fim sobre o que o cap de 20k trunca.

Medido hoje (10/08) sobre `origin/Paulo`.

---

## Item 1 — a chave: `conditionId` (e `slug`) no parquet do FOMC ✅

Acrescentei **duas** colunas ao `data/polymarket_fed_reunioes.parquet`, sem tocar em nenhuma
linha nem nas colunas que já existiam (operação puramente aditiva):

| coluna | o que é |
|---|---|
| `conditionId` | id canônico do mercado no Polymarket — **a chave**, o mesmo string que sai no G5 |
| `slug` | a chave alternativa que você disse também servir (slug completo, não truncado) |

**Esquema novo:** `['data', 'mercado', 'probabilidade', 'volume', 'evento_id', 'conditionId', 'slug']`
→ as duas colunas novas entram no fim, depois de `evento_id`; as anteriores ficam na mesma ordem.
Mesmas 16.338 linhas, mesmos 76 mercados, mesmos 18 eventos. `mercado` (o título) continua lá,
intocado.

**Como foi feito:** para cada um dos 18 `evento_id` já no parquet, chamei a Gamma `/events?id=`
uma vez e casei `question → (conditionId, slug)` dentro do evento. Não re-baixei preço nem
re-descobri eventos — parti dos `evento_id` que já estavam no arquivo, então **não há risco de o
universo mudar**. Mesma fonte (Gamma, Decisão 2); não é troca de fonte de dado.

**Teste de junção (o número que estava em 0):**

| | antes | agora |
|---|---:|---:|
| `conditionId` em comum entre G5 (view 2.3) e o parquet | **0** | **76** |

Cobertura: **76/76** faixas mapeadas, 0 sem chave.

Script: `scripts/g5b_fomc_conditionid.py` (idempotente; re-rodar só reconfirma a chave). Deixei o
`src/data_pipeline/download_polymarket_fed.py` também emitindo `conditionId`+`slug`, para um rebuild
completo já sair com a chave — mas o parquet que está em disco foi enriquecido pelo g5b (não precisei
reconstruir do zero, então nada derivou do que você mediu).

---

## Item 2 — G5 estendido às 76 faixas do FOMC ✅

A view 2.3 agora tem **as 76 faixas das 18 reuniões**, no mesmo formato de sempre
(`notional_usd`, `n_trades`, `slot_utc` de 12h, `conditionId`, `t_cobertura_min` por mercado, e a
separação `NaN`/`0` da Decisão 12 do jeito que você fechou no FOLLOWUP5).

**Detalhe que te interessa diretamente:** o grid de 12h de cada faixa **vem do próprio parquet que
a view 2.3 consome** (a série `data`), não de um download paralelo. Consequência conferida:

> **slot-a-slot, 76/76 faixas batem 1 a 1 com o parquet — 0 divergência de conjunto de slots.**

Ou seja, o portão de volume e a probabilidade ficam no mesmo slot por construção; você soma as faixas
de um evento num slot e o volume cai exatamente no slot da probabilidade daquela reunião.

Números da view 2.3 no `data/raw/g5_volume_no_tempo.csv`:

| | valor |
|---|---:|
| Faixas (mercados) | **76** |
| Linhas (slot × faixa) | 16.321 |
| Células com volume > 0 | 6.803 |
| Células com `0` legítimo | 445 |
| Células `NaN` (truncamento do cap) | 9.073 |
| Faixas que bateram o cap de 20k | 42 de 76 |

Arquivos (agora com as três views):
- `data/raw/g5_volume_no_tempo.csv` — long: `view, mercado, conditionId, slot_utc, notional_usd, n_trades`
  (2.2=111, **2.3=76**, B=9 mercados).
- `data/raw/g5_volume_cobertura.csv` — por mercado: `t_cobertura_min, bateu_cap_20k, ...` (2.3 incluído).

Junção do seu lado (a única sutileza: o `data` do parquet tem segundos — `00:00:03` — e o
`slot_utc` do G5 é o slot de 12h já arredondado — `00:00`; então piso o `data` no slot de 12h antes de
casar):
```python
g23 = g5[g5.view == "2.3"].copy()                        # slot_utc + notional_usd + n_trades
par = parquet_fomc.copy()
par["slot_utc"] = par["data"].dt.floor("12h").dt.strftime("%Y-%m-%d %H:%M")
merged = par.merge(g23, on=["conditionId", "slot_utc"])  # 1:1, 0 slot órfão
```
(Conferido: com esse piso, o conjunto de slots das 76 faixas bate exatamente com o do G5 — 0
divergência.)

---

## O `?` honesto — o que o cap de 20k trunca (leia antes de somar faixas)

Você foi explícita: *"reunião com faixa faltando não me serve … faltando uma a soma subestima"* e
*"prefiro saber hoje do que descobrir na véspera"*. Então o mapa exato:

**Nível mercado:** nenhuma reunião tem faixa faltando. **As 76 faixas das 18 reuniões estão todas
presentes**, cada uma com o grid inteiro de slots. Não caí em nenhum plano de fallback — entreguei
tudo, não um recorte.

**Nível slot:** o cap de 20k trades do `/trades` morde as faixas mais líquidas. Onde ele morde,
os slots **iniciais** daquela faixa saem `NaN` (a regra que você fechou: truncamento = `NaN`, não
`0`). Isso não some com a faixa — some com os slots **antigos** dela. Então, num slot inicial de uma
reunião capada, a sua soma de faixas fica incompleta (algumas faixas `NaN` ali). **É o único ponto em
que a soma subestima, e ela subestima nos slots antigos, não no run-up da reunião.**

Cobertura por reunião (`full%` = slots em que **todas** as faixas têm volume real; `1º slot 100%` =
a partir de quando a reunião fica inteira):

| reunião | faixas | slots | full% | 1º slot 100% | último slot |
|---|---:|---:|---:|---|---|
| May/2024 | 4 | 56 | 100% | 2024-04-04 | 2024-05-01 |
| Jun/2024 | 4 | 84 | 100% | 2024-05-02 | 2024-06-12 |
| Jul/2024 | 4 | 98 | 100% | 2024-06-13 | 2024-07-31 |
| Sep/2024 | 4 | 110 | 100% | 2024-07-26 | 2024-09-18 |
| **Nov/2024** | 5 | 194 | **14%** | 2024-10-25 | 2024-11-07 |
| **Dec/2024** | 5 | 268 | **24%** | 2024-11-17 | 2024-12-18 |
| **Jan/2025** | 5 | 166 | **20%** | 2025-01-13 | 2025-01-29 |
| **Mar/2025** | 4 | 182 | **46%** | 2025-02-06 | 2025-03-19 |
| May/2025 | 4 | 208 | 100% | 2025-01-24 | 2025-05-07 |
| Jun/2025 | 4 | 263 | 100% | 2025-02-07 | 2025-06-18 |
| **Jul/2025** | 4 | 266 | **22%** | 2025-07-02 | 2025-07-30 |
| **Sep/2025** | 4 | 266 | **9%** | 2025-09-05 | 2025-09-17 |
| Oct/2025 | 4 | 266 | 100% | 2025-06-20 | 2025-10-31 |
| Dec/2025 | 4 | 263 | 100% | 2025-08-01 | 2025-12-10 |
| Jan/2026 | 4 | 265 | 100% | 2025-09-18 | 2026-01-28 |
| Mar/2026 | 4 | 280 | 100% | 2025-10-30 | 2026-03-18 |
| Apr/2026 | 4 | 328 | 100% | 2025-11-13 | 2026-04-29 |
| Jun/2026 | 5 | 342 | 100% | 2025-12-11 | 2026-06-17 |

Leitura para as suas duas prioridades:

- **"por reunião, não por faixa":** **12 das 18 reuniões estão 100% cobertas** em todos os slots. As
  6 truncadas (Nov/2024, Dec/2024, Jan/2025, Mar/2025, Jul/2025, Sep/2025) têm **todas as faixas
  presentes**, só com os slots iniciais `NaN`. Em todas elas o **run-up** (as semanas coladas na
  reunião — o `1º slot 100%` até o último slot) está inteiro: p.ex. Dec/2024 fecha 100% de 17/11 até
  a reunião; Sep/2025, de 05/09 até 17/09. O que falta é histórico antigo, não a janela de decisão.
- **"das mais recentes para as mais antigas":** **todas as reuniões de Oct/2025 em diante (6) estão
  100%.** O truncamento é todo em 2024–meados de 2025. Pela sua régua de recência, é o melhor arranjo
  possível: onde o v1 mais pesa, a cobertura é cheia.

Se a sua soma de faixas por slot tratar `NaN` como "sem dado" (propaga, não veta — que é a Decisão 12),
os slots iniciais das 6 reuniões truncadas caem como "sem dado" e o portão simplesmente não julga ali,
sem subestimar nada. O único cuidado é **não** somar `NaN` como `0` nesses slots.

---

## O que **não** mudou (como você pediu)

- **CPI (view 2.2, 111 mercados): idêntico byte a byte ao que já estava** — conferi contra o `HEAD`,
  as 6.699 linhas da 2.2 não mudaram. Não reprocessei, não toquei.
- **View B (M3, 9 mercados): idêntica** (5.964 linhas, conferido contra o `HEAD`).
- Granularidade: **12h**, sem grão novo.
- Cap de 20k: continua valendo, com a consequência de sempre — onde morde, `NaN` + `t_cobertura_min`,
  nunca `0`.

---

## Como reproduzir (ordem)

```bash
.venv/bin/python scripts/g5b_fomc_conditionid.py   # 1) põe conditionId+slug no parquet
.venv/bin/python scripts/g5_volume_no_tempo.py      # 2) G5 c/ a view 2.3 (FOMC) vinda do parquet
```

O passo 2 tem cache retomável em `data/raw/g5_cache/` (git-ignored) — os `/trades` das 76 faixas já
estão cacheados, então re-rodar é rápido e offline.

Qualquer ajuste de rótulo (hoje uso o `slug` completo na coluna `mercado` da view 2.3, porque é a chave
legível) eu troco numa linha — é só avisar.
