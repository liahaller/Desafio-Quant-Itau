# RESPOSTA — FOLLOW-UP 4 · foco no `G8` (`DFF` do FRED)

> Medido ao vivo contra o FRED em 2026-08-07. Dado salvo **cru**, sem tratar:
> sem renomear coluna, sem reindexar, sem preencher buraco, sem converter
> unidade. Mesmo caminho `fredgraph.csv` do G2, com um ID a mais.

---

## G8 — `DFF` (Effective Federal Funds Rate)

Baixado de:

```
https://fred.stlouisfed.org/graph/fredgraph.csv?id=DFF
```

Salvo em `data/raw/fred_DFF.csv`, mesmo formato dos outros três do G2
(`observation_date,DFF`), cru. Script: `scripts/g8_fred_dff.py`.

```
=== G8 — DFF ===
linhas:         26334
primeira data:  1954-07-01
última data:    2026-08-05
campos vazios:  0
```

**Detalhe medido (não pedido, mas para não gerar dúvida no cruzamento):**

- Colunas exatas do cabeçalho: `['observation_date', 'DFF']` — idênticas ao
  padrão dos três CSVs do G2.
- **0 campos vazios** em 26.334 linhas. Diferente do `DTB3`/`DGS10`, o `DFF`
  **não tem buraco de feriado**: é uma taxa diária de calendário (repete o
  valor em fim de semana/feriado), então cobre todo dia corrido de
  1954-07-01 a 2026-08-05 sem ausência. A varredura de marcador de ausente
  (mesma do G2) não encontrou nenhum não-numérico — `marca ausente: (nenhum)`.
- Nada foi normalizado. Se o Felipe quiser alinhar `DFF` ao índice de pregões
  do `DTB3` para a subtração `e_ff_bps = DTB3 − DFF` (view 2.3), esse recorte
  é tratamento — fica do lado dele, não meu.

Com isso a view 2.3 tem os dois lados da subtração disponíveis crus.

---

## Sobre o ponto de processo (registrado, uma vez)

Aceito: o `G8` era a segunda metade do FOLLOWUP3 e **não foi entregue nem
sinalizado** na resposta do G7 — o `## Bloqueios` dizia "Nenhum" quando devia
constar o `DFF` como não-entregue. Foi falha de sinalização, não de esforço.
Corrigido aqui, e daqui pra frente item não entregue entra em **Bloqueios**,
nunca some.

---

## G5 — volume no tempo (spec da Lia)

Série 12h derivada do `data-api /trades`, só para os mercados das views ativas
(2.2/2.3/B) que já estão em `data/raw/clob_exploracao/`. Para cada mercado
(um `conditionId` por bucket): pagino o `/trades` até o teto da API
(offset≤10000 → ~20.000 trades mais recentes, achado do F4), agrego por slot de
12h e marco o `t_cobertura_min` (trade mais antigo alcançado, **um por
mercado**). O grid de 12h de cada mercado é o da própria série
`/prices-history` já baixada — não re-baixei preço.

Script: `scripts/g5_volume_no_tempo.py`. **Nada normalizado.** Entrego os dois
medidores no mesmo varrimento (`notional_usd` **e** `n_trades`), como pedido.

```
=== G5 — VOLUME NO TEMPO ===
Arquivo salvo:        data/raw/g5_volume_no_tempo.csv   (série longa)
                      data/raw/g5_volume_cobertura.csv  (1 linha por mercado: t_cobertura_min etc.)
Colunas:              ['view', 'mercado', 'conditionId', 'slot_utc', 'notional_usd', 'n_trades']
Nº de linhas:         12928   (slots × mercados)
Nº de mercados:       121     (2.2 = 111 [105 CPI_* + 6 M1_cpi_monthly] · 2.3 = 1 [M2_fomc] · B = 9 [M3_fed_trajectory])
Passo:                12h (43200s; = prices-history fidelity=720)
Janela:               2024-12-30 00:00 → 2026-07-29 12:00 (UTC)
Mercados que bateram no cap de 20k:  3
    - M2_fomc_fed-decreases-interest-rates-by-50-bps-a       (t_cobertura_min = 2025-09-05 16:13:54)
    - M3_fed_trajectory_will-4-fed-rate-cuts-happen-in-2025  (t_cobertura_min = 2025-06-02 22:47:43)
    - M3_fed_trajectory_will-5-fed-rate-cuts-happen-in-2025  (t_cobertura_min = 2025-01-17 19:00:00)
Slots sem trade:      2403  (volume 0 legítimo, DEPOIS do t_cobertura_min)
Slots NaN:            424   (antes do t_cobertura_min, sem alcance do /trades)
```

**Colunas exatas dos dois arquivos:**

- `g5_volume_no_tempo.csv` (long): `view, mercado, conditionId, slot_utc,
  notional_usd, n_trades`. `notional_usd = Σ(size × price)`; `n_trades` =
  contagem. **`NaN` = os dois campos vazios** (antes do `t_cobertura_min`);
  **`0` = slot existiu e ninguém negociou** (`notional_usd=0.000000`,
  `n_trades=0`), sempre DEPOIS do `t_cobertura_min`.
- `g5_volume_cobertura.csv` (1 linha/mercado): `view, mercado, conditionId,
  n_trades_total, bateu_cap_20k, t_cobertura_min, primeiro_slot, ultimo_slot`.

**Breakdown do `NaN` (levanto, não decido — é ponto p/ a Lia):** apliquei a
regra literal da spec ("antes de `t_cobertura_min` = NaN, nunca 0") para
**todos** os mercados. Dos 424 slots NaN:

- **346 são de truncamento do cap** — os 2 mercados M3 capados (4-cuts: 309;
  5-cuts: 37). É exatamente o caso que o `t_cobertura_min` existe para proteger:
  sem ele viravam "0" nos mercados mais líquidos. (O M2 também capou, mas o
  `/trades` alcançou 2025-09-05, ANTES do 1º slot da série 2025-09-18 → 0 slots
  NaN nele.)
- **78 são "pré-primeiro-trade" em 19 mercados NÃO capados** — slots de 12h em
  que a série `/prices-history` já tinha ponto (midpoint semeado na criação do
  mercado) mas ainda **não houve nenhum trade**. Como o mercado não foi
  truncado, dava para lê-los como `0` legítimo em vez de `NaN`. Segui a spec ao
  pé da letra (NaN), mas **sinalizo**: se a Lia quiser que só o truncamento vire
  NaN e o pré-trade vire 0, é troca de uma linha no script — não decido sozinho.

Detalhe de acesso (não altera dado): 21 dos 121 mercados são famílias que o
filtro `clob_token_ids` do Gamma não indexa; resolvi o `conditionId` desses
pelo **evento** (casando o tokenId em `clobTokenIds`) — famílias
`*-inflation-monthly`, `CPI_G4_janeiro`, `M1`, `M3` — e o `M2` pelo slug de
mercado com `closed=true`. **Zero mercado ficou sem resolver.**

---

## Bloqueios

- **Nenhum item pedido no FOLLOWUP4 ficou de fora:** G8 e G5 entregues, ao vivo,
  crus.
- **G6 (CPI 2022–2024):** segue condicional à reunião. Sem mudança (não é item
  do FOLLOWUP4).
- Opcional do Nasdaq Data Link (teto 15 min) do G8: não abordado — o caminho do
  FRED já resolve o `DFF`.

## Commit

<preenchido após o push>
