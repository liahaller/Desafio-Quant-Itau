# Cristalização da PMF por distância ao evento — e o que ela faz com a 1.3

> Gerado por `scripts/cristalizacao_entropia.py`. Traduz o achado (b) da Lia (2026-08-10) para o sinal da tática 1.3. **Mede; não decide** — nem entrada da sleeve, nem orçamento (CLAUDE.md §6).

- `entropia` = o sinal da 1.3, no slot pré-abertura (12:00 UTC) do dia;
- `variação total` = `Σ|p(d) − p(d−1)|` entre dias corridos ADJACENTES — a mesma grandeza do ingrediente que entrou na régua da Lia;
- `baldes vivos` é CONTROLE: a entropia é normalizada por log(nº de baldes com leitura > 0), e balde morre perto do evento. Queda de entropia com essa coluna caindo junto pode ser artefato de denominador.


## FOMC (PMF de trajetória)

- eventos com leitura: **24** · observações diárias: **7054**

| faixa | n | entropia média | entropia desvio | variação total média | baldes vivos (mediana) |
|---|---|---|---|---|---|
| d = 0 | 7 | 0.713 | 0.305 | 0.0610 | 9.0 |
| 1–2 dias | 16 | 0.663 | 0.295 | 0.0376 | 9.0 |
| 3–5 dias | 24 | 0.676 | 0.279 | 0.0401 | 9.0 |
| 6–10 dias | 40 | 0.680 | 0.274 | 0.0422 | 9.0 |
| 11–20 dias | 80 | 0.706 | 0.218 | 0.0809 | 9.0 |
| 21–60 dias | 301 | 0.723 | 0.218 | 0.0559 | 9.0 |

## CPI (PMF do mês)

- eventos com leitura: **14** · observações diárias: **439**

| faixa | n | entropia média | entropia desvio | variação total média | baldes vivos (mediana) |
|---|---|---|---|---|---|
| d = 0 | 12 | 0.585 | 0.202 | 0.1717 | 5.0 |
| 1–2 dias | 25 | 0.571 | 0.249 | 0.0709 | 5.0 |
| 3–5 dias | 36 | 0.617 | 0.243 | 0.0838 | 5.0 |
| 6–10 dias | 62 | 0.663 | 0.205 | 0.0640 | 5.0 |
| 11–20 dias | 135 | 0.645 | 0.226 | 0.0680 | 5.0 |
| 21–60 dias | 154 | 0.747 | 0.185 | 0.1439 | 5.0 |

## Payrolls (PMF do Employment Situation)

- eventos com leitura: **13** · observações diárias: **373**

| faixa | n | entropia média | entropia desvio | variação total média | baldes vivos (mediana) |
|---|---|---|---|---|---|
| d = 0 | 13 | 0.819 | 0.098 | 0.3270 | 6.0 |
| 1–2 dias | 26 | 0.862 | 0.075 | 0.2000 | 6.0 |
| 3–5 dias | 39 | 0.891 | 0.058 | 0.1620 | 6.0 |
| 6–10 dias | 59 | 0.901 | 0.043 | 0.1367 | 6.0 |
| 11–20 dias | 117 | 0.904 | 0.050 | 0.1363 | 6.0 |
| 21–60 dias | 106 | 0.909 | 0.068 | 0.1549 | 6.0 |

## O que isto diz do desenho da 1.3

**FOMC (PMF de trajetória)** — no slot que a sleeve lê (d = 0) a entropia média é 0.713 com desvio 0.305, contra 0.680 / 0.274 a 6–10 dias. A variação total média vai de 0.0422 (6–10 dias) para 0.0610 em d = 0, com a mediana de baldes vivos indo de 9.0 para 9.0.

↳ o mínimo de variação está em **1–2 dias**, não em d = 0: a cristalização anda até ali e **reverte no último slot** (0.0376 → 0.0610). Amostra do slot lido: **n = 7** — o desvio de d = 0 é a estatística mais frágil da tabela.

**CPI (PMF do mês)** — no slot que a sleeve lê (d = 0) a entropia média é 0.585 com desvio 0.202, contra 0.663 / 0.205 a 6–10 dias. A variação total média vai de 0.0640 (6–10 dias) para 0.1717 em d = 0, com a mediana de baldes vivos indo de 5.0 para 5.0.

↳ o mínimo de variação está em **6–10 dias**, não em d = 0: a cristalização anda até ali e **reverte no último slot** (0.0640 → 0.1717). Amostra do slot lido: **n = 12** — o desvio de d = 0 é a estatística mais frágil da tabela.

**Payrolls (PMF do Employment Situation)** — no slot que a sleeve lê (d = 0) a entropia média é 0.819 com desvio 0.098, contra 0.901 / 0.043 a 6–10 dias. A variação total média vai de 0.1367 (6–10 dias) para 0.3270 em d = 0, com a mediana de baldes vivos indo de 6.0 para 6.0.

↳ o mínimo de variação está em **11–20 dias**, não em d = 0: a cristalização anda até ali e **reverte no último slot** (0.1363 → 0.3270). Amostra do slot lido: **n = 13** — o desvio de d = 0 é a estatística mais frágil da tabela.

A leitura que decide o desenho é o **desvio da entropia em d = 0**, não a média: `dw[SPY] = orcamento_max · sinal` só é modulação se o sinal diferir entre anúncios no slot em que é lido. Desvio que sobrevive à cristalização = a sleeve continua dimensionando. Desvio que colapsa = a sleeve vira long SPY constante em dia de anúncio, que é outra tática e precisaria de outra justificativa.

**O que isto NÃO decide:** a entrada da 1.3 na carteira e o `orcamento_max` seguem pendentes de reunião. O número aqui é insumo dessa conversa.

