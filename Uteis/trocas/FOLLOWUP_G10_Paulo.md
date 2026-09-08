# Para o Felipe — G10 entregue, e uma decisão de grupo no calendário do CPI

Felipe, o G10 está entregue e no push (`origin/Paulo`, commit `b19c440`, detalhe em
`docs/RESPOSTA_G10_Paulo.md`). Os três rodaram: `DGS1` (G10a), rótulo dos baldes de
payrolls (G10b, 182 linhas, `token_id` casando 182/182 com os JSONs) e o calendário
oficial do CPI (G10c). Só uma coisa te devolve uma decisão, e uma confirmação rápida.

## 1. Decisão de grupo: trocamos o `cpi_release_dates.csv` pelo do FRED?

Você pediu para saber **antes de trocar** se as 15 datas atuais batem com o FRED. Rodei:
o `release_id` do CPI é o **10** (confirmado por nome exato em `/fred/releases`), e o
calendário oficial tem 953 datas (1949→2026, ~250 desde 2003), salvo **ao lado** em
`data/raw/cpi_release_dates_fred.csv` — **não** sobrescrevi o atual.

**12 das 15 batem. 3 divergem** — e as 3 são exatamente as tocadas pelo shutdown de 2025:

| data no CSV atual | o que o FRED tem | natureza |
|---|---|---|
| `2025-01-13` | `2025-01-15` | dez/2024, diferença de **2 dias** |
| `2025-10-15` | `2025-10-24` | set/2025, **atraso +9 dias** (shutdown) |
| `2025-11-13` | **nenhuma em nov/2025** | out/2025 não sai em nov no FRED — pula de `10-24` direto p/ `12-18` (shutdown) |

Como você mesmo apontou, **divergência aí muda o dia do evento** em medições já feitas e
publicadas (a variante de β por event-study nos dias de divulgação). Por isso não troquei
nada — é decisão do grupo. As perguntas concretas:

- **(a)** Adotamos o calendário do FRED como fonte do `cpi_release_dates.csv`? Isso
  destrava a variante de event-study com ~250 divulgações em vez de 15, mas **muda 3 dias
  de evento** já usados.
- **(b)** Se sim, o que fazer com as medições já publicadas que usaram `2025-10-15` e
  `2025-11-13`? Refazer com as datas do FRED, ou congelar o que está publicado e usar o
  FRED só daqui pra frente?
- **(c)** O caso de `2025-11-13` (CPI de out/2025 que o FRED não lista em nov) — trato o
  mês de referência out/2025 como remanejado para dez/2025, ou como buraco declarado?

Não fecho nenhuma — é sua régua de backtest. Me diz o rumo e eu executo do lado dos dados.

## 2. Confirmação rápida (não é decisão): fonte do `DGS1`

Você templou a API `series/observations`, mas medi que ela devolve valor com padding
(`4.0600000000`) e ausência `"."` — o que **não** fica idêntico aos `fred_DTB3/DGS10`
(2 casas, ausência = campo vazio), e "idêntico" era requisito. Usei o **fredgraph** (a
mesma fonte que fez o DTB3/DGS10/DFF), então o arquivo saiu de fato idêntico e cru. Mesma
série, muda só a formatação. Se por algum motivo você precisa da API literal, é uma linha
— mas aí ele não sai idêntico aos irmãos. **Só confirma que o fredgraph serve.**

— Paulo
