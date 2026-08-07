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

## G5 — volume no tempo (NÃO abordado nesta sessão)

Esta sessão foi escopada só ao `G8` (instrução do Paulo: focar no G8). O `G5`
com a spec nova da Lia (série 12h derivada do `/trades`: `notional_usd`,
`n_trades`, `t_cobertura_min` com `NaN` antes do alcance do cap de 20k, escopo
só views 2.2/2.3/B) **não foi executado** — fica declarado como pendente
abaixo, não some.

---

## Bloqueios

- **G5 (volume no tempo):** **não executado nesta sessão** — escopo fechado no
  G8 por instrução. A spec da Lia está entendida e é executável (varredura do
  `data-api /trades` por bucket de 12h, com `t_cobertura_min`/`NaN` para o
  truncamento do cap de 20k já medido no F4). Fica para a próxima sessão.
- **G6 (CPI 2022–2024):** segue condicional à reunião. Sem mudança.
- Opcional do Nasdaq Data Link (teto 15 min): não abordado — o caminho do FRED
  já resolve o G8.

## Commit

- **Hash:** `2f3a3eb67861524431e2a621e50d9afea6db4def`
- **Branch:** `Paulo` (push para `origin/Paulo`: `8dd635d..2f3a3eb`)
