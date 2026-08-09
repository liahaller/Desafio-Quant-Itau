# Para o Paulo — o G5 não alcança os mercados do FOMC (achado ao ligar o portão)

Paulo, o G5 chegou certo e a separação `0` × `NaN` está exatamente como eu pedi — obrigada. O
problema apareceu quando fui **ligar** o portão de volume na série do FOMC: o arquivo não casa com
o parquet. Isto não é defeito do seu trabalho; o pedido saiu antes de a calibração rodar sobre o
FOMC, e só dá para ver isso tentando usar.

Medido hoje (09/08), com `g5_volume_no_tempo.csv` e `polymarket_fed_reunioes.parquet` do
`origin/Paulo` em `033e0d8`:

| | mercados |
|---|---:|
| Parquet do FOMC (o que a view 2.3 consome) | **76** (18 reuniões × 4–5 faixas) |
| G5, linhas com `view = 2.3` | **1** |
| Chaves em comum entre os dois arquivos | **0** |

São dois problemas somados, e nenhum se resolve sem você:

**1. Não há chave para juntar as tabelas.** O G5 identifica mercado por slug
(`M2_fomc_fed-decreases-interest-rates-by-50-bps-a`) e por `conditionId`. O parquet do FOMC tem só
`data, mercado, probabilidade, volume, evento_id`, e o `mercado` é o **título**
(`"Fed decreases interest rates by 50 bps after December 2024 meeting?"`). Não existe coluna comum.

**2. Cobertura.** Mesmo com a chave resolvida, o G5 traz **um** mercado da família FOMC contra os
76 que a série percorre. O portão não teria o que julgar.

## O que eu preciso

1. **`conditionId` no parquet do FOMC** — uma coluna a mais no `polymarket_fed_reunioes.parquet`,
   com o `conditionId` de cada mercado. É a chave; o slug também serve, desde que seja o mesmo
   string do G5. **Sem isso, nada do resto encaixa.**
2. **G5 estendido aos mercados do FOMC**, mesmo formato de hoje (`notional_usd`, `n_trades`,
   `slot_utc` de 12h, `t_cobertura_min` por mercado, e a separação que você já aplicou:
   truncamento = `NaN`, pré-primeiro-trade = `0`).

**Se não der tudo até 13/08** (é a data de corte da régua), a ordem de prioridade:

- **por reunião, não por faixa.** Reunião com faixa faltando não me serve: o volume do slot é a
  soma das faixas daquele evento, e faltando uma a soma subestima — e o meu tratamento descarta
  linha incompleta, então a reunião pela metade vira reunião fora. **Prefiro 6 reuniões inteiras a
  18 pela metade.**
- **das mais recentes para as mais antigas.** O backtest do v1 roda de 2025-02 em diante; as
  reuniões de 2025–2026 valem mais que as de 2024.
- se der só o item 1 (a chave) e mais nada, ainda ganho o único mercado que existe hoje — pouco,
  mas verificável.

## O que não muda

- Não preciso de granularidade nova: 12h continua bom.
- Não preciso de reprocessar o que já está lá — a parte de CPI (`view = 2.2`, 111 mercados) está
  íntegra e eu não mexo nela.
- O cap de 20k segue valendo, com a mesma consequência de sempre: onde ele morder, `NaN` e
  `t_cobertura_min`, nunca `0`.

## Enquanto isso, do meu lado

Não fico parada esperando: calibro com **proximidade + coerência**, sem o ingrediente de
estabilidade. É a saída que a decisão 6b já previa — sem volume, o que cai é a estabilidade (que o
midpoint congelado engana: mercado sem negociação nenhuma aparece como perfeitamente estável), não
o portão. Entrego um `c` de dois ingredientes calibrados, que é melhor que o plano B de `c = 1`, e
o terceiro entra depois sem mudar interface, porque a régua é multiplicativa.

Um `?` honesto sobre o que não dá para levantar até 13/08 me ajuda mais do que a tentativa —
prefiro saber hoje que só vêm 4 reuniões do que descobrir na véspera.
