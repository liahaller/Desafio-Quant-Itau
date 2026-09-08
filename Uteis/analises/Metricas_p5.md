# Métricas da página 5 — uso de IA

> Gerado por `scripts/graficos_p5.py` a partir dos três `LOG.md` (branch atual + `origin/Lia` + `origin/Paulo`). Não editar à mão.

| indicador | valor | nota |
|---|---|---|
| Sessões de IA | 91 | Felipe 55 · Lia 18 · Paulo 18 |
| Tokens por sessão | 232k | média · 19,7M no total |
| Decisões registradas | 81 | escaladas para decisão humana |
| Taxa de recorreção | 37% | das sessões pediram 2ª rodada (87 medidas) |

## Qualidade do dado de contexto

- **58 de 91 sessões** registram tokens direto no LOG.
- As outras **33** registram só "% da janela" e foram convertidas pela regra declarada em `JANELA_POR_DATA` (200k até 2026-07-08, 1M depois) — decisão do dono, não do script.

## Decisões, por sessão que as registrou

| data | dono | decisões |
|---|---|---|
| 2026-07-07 | Felipe | 8 |
| 2026-07-08 | Felipe | 4 |
| 2026-07-08 | Felipe | 3 |
| 2026-07-08 | Paulo | 2 8 9 |
| 2026-07-09 | Felipe | 9 |
| 2026-07-09 | Felipe | 10 |
| 2026-07-10 | Felipe | 11 |
| 2026-07-11 | Felipe | 12 |
| 2026-07-14 | Felipe | 6 |
| 2026-07-27 | Paulo | 10 |
| 2026-07-29 | Paulo | 11 |
| 2026-08-07 | Felipe | 6a |
| 2026-08-07 | Felipe | 12a 12b 12c |
| 2026-08-07 | Felipe | 10a 13 |
| 2026-08-07 | Lia | 6a |
| 2026-08-07 | Lia | 6 6b 6c 6d |
| 2026-08-07 | Paulo | 12 |
| 2026-08-08 | Felipe | 14 |
| 2026-08-08 | Felipe | 15 15a 15b 15c 15d 15f 15g 15e |
| 2026-08-08 | Felipe | 16 |
| 2026-08-08 | Felipe | 17 |
| 2026-08-08 | Paulo | 13 14 |
| 2026-08-09 | Felipe | 14a 15h |
| 2026-08-09 | Felipe | 18 18a 18d |
| 2026-08-09 | Felipe | 19 19a 19b 19c |
| 2026-08-09 | Lia | 6f |
| 2026-08-09 | Lia | 6g 6h 6i 6j |
| 2026-08-10 | Felipe | 20 20a 20b 20c |
| 2026-08-10 | Felipe | 21 21a 21d |
| 2026-08-10 | Felipe | 22 |
| 2026-08-10 | Felipe | 22e 23 23f 23e |
| 2026-08-10 | Lia | 6k 6l |
| 2026-08-10 | Lia | 6m 6n 6o |
| 2026-08-10 | Lia | 6p |
| 2026-08-10 | Paulo | 15 |
| 2026-08-11 | Felipe | 25 25a 25b 25c 25g |
| 2026-08-11 | Felipe | 27 |
| 2026-08-11 | Felipe | 5 28 |
| 2026-08-12 | Lia | 6q |
| 2026-08-14 | Felipe | 29 |

## Decisões sem data de registro

Existem no `Decisoes_pendentes.md` mas nenhum campo "Decisões escaladas" as cita de forma inequívoca (ver `cita()`), então ficam fora da curva acumulada: **43** ao todo.

- **Felipe:** 1 2 7 16a 16b 16c 17a 17b 17c 17d 17e 18b 18c 21b 21c 22a 22b 22c 22d 24 23a 23b 23c 23d 25d 25f 25e 26
- **Lia:** 1 2 3 4 5 6e 7 8 9
- **Paulo:** 1 3 4 5 6 7

## Tipo de sessão

> Classificado à mão pela regra declarada antes da contagem: vale o que a sessão DEIXOU, e no desempate a medição ganha do código (o script era o meio, a medição era o fim).

| tipo | sessões | % das sessões | % dos tokens |
|---|---|---|---|
| pesquisa e decisão | 28 | 31% | 25% |
| análise e medição | 49 | 54% | 71% |
| código | 14 | 15% | 4% |

## Erros da IA — tipo × mecanismo que pegou

| tipo | execução / teste | auto-correção na sessão | conferência humana | só pego em sessão posterior | total |
|---|---|---|---|---|---|
| código quebrado | 40 | 19 | 4 | 9 | **72** |
| alucinação numérica | 2 | 13 | 6 | 4 | **25** |
| generalização além do teste | 6 | 2 | 2 | 3 | **13** |
| texto impreciso ou contraditório | 0 | 3 | 10 | 0 | **13** |
| premissa herdada | 2 | 6 | 3 | 1 | **12** |
| escopo ou condução errada | 0 | 3 | 7 | 0 | **10** |
| **total** | **50** | **46** | **32** | **17** | **145** |
