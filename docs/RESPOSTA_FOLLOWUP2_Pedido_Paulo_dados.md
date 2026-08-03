## G1 — `Open` diário dos 9 ETFs

```
=== OPEN DOS ETFs ===
Arquivo:                data/etf_open_daily.parquet   (arquivo irmão do etf_prices_daily.parquet)
Coluna(s) nova(s):      preco_abertura   (formato longo: data, ticker, preco_abertura)
Base do Open:           ajustado — auto_adjust=True (a MESMA base do close que já está no etf_prices_daily.parquet)
Nº de linhas:           51.129   (bate com o esperado; 5.681 datas × 9 tickers)
Tickers:                SPY, TIP, TLT, XLE, XLF, XLK, XLP, XLU, XLV
Janela:                 2003-12-05 → 2026-07-08
Alinhado ao close?      SIM — reindexado às datas EXATAS do arquivo de close; 0 datas de Open fora do grid do close
Dias com Open ausente:  0  (nenhum ticker; alinhamento 100%)
```

Gerado por `scripts/g1_open_etfs.py`. `data/README.md` atualizado com a seção do
arquivo novo. Escolhi `auto_adjust=True` para não misturar close ajustado com
open cru (o que geraria retorno intradiário falso em dia de dividendo, como você
mesmo apontou) — a decisão metodológica final continua sendo do grupo; aqui é só
consistência interna e está escrito. Se preferirem o Open **cru** (não ajustado),
é trocar um parâmetro e re-rodar; me digam.

---

## G2 — Séries do FRED salvas em arquivo

```
=== FRED (entrega física) ===
Série  | arquivo             | URL exata                                                        | nº de linhas | primeira → última       | como vem o valor ausente | nº de ausentes
T10YIE | data/raw/fred_T10YIE.csv | https://fred.stlouisfed.org/graph/fredgraph.csv?id=T10YIE  | 6.152        | 2003-01-02 → 2026-07-31 | CAMPO VAZIO (ver nota)   | 253
DGS10  | data/raw/fred_DGS10.csv  | https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10   | 16.848       | 1962-01-02 → 2026-07-30 | CAMPO VAZIO (ver nota)   | 719
DTB3   | data/raw/fred_DTB3.csv   | https://fred.stlouisfed.org/graph/fredgraph.csv?id=DTB3    | 18.934       | 1954-01-04 → 2026-07-30 | CAMPO VAZIO (ver nota)   | 799
```

Salvas **cruas**, sem renomear coluna, sem reindexar, sem preencher feriado.
Gerado por `scripts/g2_fred.py`.

**NOTA — como vem o valor ausente (o item que você marcou como o mais importante):**
o endpoint `fredgraph.csv` **não** usa `"."`. Ele devolve o feriado/dia sem dado
como **campo vazio** — a linha existe, mas o valor depois da vírgula é string
vazia. Exemplo real do `fred_T10YIE.csv`:

```
observation_date,T10YIE
2003-01-17,1.71
2003-01-20,          ← feriado (MLK): linha presente, valor VAZIO, não "."
2003-01-21,1.70
```

O cabeçalho é `observation_date,<ID>` (ex. `observation_date,T10YIE`). Então o
join com o calendário de pregão não quebra por linha faltando — a data está lá;
o que quebra é ler o campo vazio como número. (O `"."` é o marcador da API JSON
antiga do FRED; **este** CSV público usa vazio. Registrando porque a sua nota
assumia `"."`.)

Contagens levemente maiores que as de 27/07 (T10YIE 6.148→6.152, DGS10
16.844→16.848, DTB3 18.930→18.934): são os pregões novos desde então; as
primeiras datas são idênticas.

---

## G3 — Série do token No (M4 e M5)

Resultado central: **em ambos, No = 1 − Yes exatamente** (soma = 1,000 em todos os
instantes compartilhados). O No é redundante em valor. A única diferença é de
**grelha de amostragem**, e ela difere entre os dois mercados — detalhe abaixo.

```
=== TOKEN NO ===
Mercado:                      M4 — "US recession in 2025?"
Arquivo salvo:                data/raw/clob_exploracao/M4_recession_us-recession-in-2025_44528029...4869_NO.json
Nº de linhas (No) / (Yes):    716 / 716
Mesmo grid de 12h que o Yes?  PARCIAL — mesmos SLOTS de 12h (floor 43200) SIM; timestamp exato NÃO.
                              Cada lado tem 244 timestamps que o outro não tem; 472 instantes com timestamp idêntico.
                              (O endpoint amostra o No em segundos ligeiramente diferentes dentro do mesmo slot de 12h.
                               Join por slot de 12h alinha 100%; join por timestamp exato alinha 472/716.)
Soma p_yes + p_no (nos 472 instantes com timestamp idêntico):
  mínimo / mediana / máximo:  1,0000 / 1,0000 / 1,0000
Nº de instantes com os dois:  472  (por timestamp exato)  |  716 slots de 12h coincidem
```

```
=== TOKEN NO ===
Mercado:                      M5 — "Will Donald Trump win the 2024 US Presidential Election?"
Arquivo salvo:                data/raw/clob_exploracao/M5_trump_2024_will-donald-trump-win-the-2024-us-presid_48331043...5732_NO.json
Nº de linhas (No) / (Yes):    614 / 614
Mesmo grid de 12h que o Yes?  SIM — timestamp exato idêntico ponto a ponto (614/614).
Soma p_yes + p_no:
  mínimo / mediana / máximo:  1,0000 / 1,0000 / 1,0000
Nº de instantes com os dois:  614
```

Conclusão para você decidir: **o No é redundante** (é o complemento exato do Yes).
Em M5 dá pra usar direto (grelha idêntica); em M4 o valor também é redundante, mas
se quiser casar ponto a ponto por timestamp exato só 472/716 batem — casando por
slot de 12h, batem todos. Gerado por `scripts/g3_token_no.py`.

---

## G4 — Os três buracos da varredura de CPI

```
Mês de referência:   abril/2025
Buscas feitas:       /events slug=april-inflation-monthly → vazio
                     /events slug=april-inflation-us-monthly → achou, MAS é ABRIL/2026 (série 2026-04-12→2026-05-12)
                     /events slug=april-2025-inflation-monthly → vazio
                     /public-search q="april inflation" → só annual, argentina, powell e mercados 2022-2024 "from X to Y"; nenhum US monthly de 2025
                     /public-search q="april 2025 inflation cpi" → 0 relevante (só fed-rate-hike-by)
Achou mercado?       NÃO
Resultado:           LACUNA REAL do Polymarket — não abriram mercado mensal-por-bucket para o CPI de referência abr/2025.
                     (Consistente com o F8, que já sinalizava abril/2025 como furo.)
```

```
Mês de referência:   janeiro/2026
Buscas feitas:       /events slug=january-inflation-us-monthly → ACHOU (série 2025-12-20→2026-02-13, ano confirma 2026)
                     /events slug=january-inflation-monthly → achou, MAS é JANEIRO/2025 (série 2025-01-16→2025-02-12)
Achou mercado?       SIM
Slug:                january-inflation-us-monthly   | título: "January Inflation US - Monthly"
Nº de buckets:       5   | volume: 260.605,12   | 1ª/última: 2025-12-20 → 2026-02-13
Séries cruas:        salvas (5 arquivos CPI_G4_janeiro-2026_january-inflation-us-monthly_*.json em data/raw/clob_exploracao/)
Resultado:           BURACO DA BUSCA, não do Polymarket. O mercado existe; o F8 tinha usado o slug
                     "january-inflation-monthly" (que é jan/2025) e por isso não o pegou. O de 2026 usa o sufixo "-us-monthly".
```

```
Mês de referência:   fevereiro/2026
Buscas feitas:       /events slug=february-inflation-us-monthly → vazio
                     /events slug=february-inflation-monthly → achou, MAS é FEVEREIRO/2025 (série 2025-02-08→2025-03-12)
                     /events slug=february-inflation-us-monthly-2026 / february-2026-inflation-us-monthly /
                              february-inflation-monthly-us / february-inflation-us → todos vazios
                     /public-search q="february inflation" / "february inflation us monthly" / "february us cpi 2026" /
                              "february 2026 cpi" → nenhum mercado US de CPI mensal de 2026 (só annual 2026, preços de ações,
                              mercados de strikes, e os "from X to Y" de 2022-2023)
Achou mercado?       NÃO (após ~9 buscas)
Resultado:           LACUNA REAL do Polymarket — jan/2026 (us-monthly) e mar/2026 (us-monthly) existem, mas fev/2026
                     não foi aberto como mercado mensal-por-bucket (nem via slug direto nem via public-search).
```

Gerado por `scripts/g4_cpi_holes.py` (+ probe manual para fev/2026 e confirmação de
ano). Removi do `data/raw/` os arquivos que o script tinha salvo por engano nos
matches de ano errado (abril→2026 e fevereiro→2025); mantive só a série real de
jan/2026.

---

## G5 — Volume dia a dia por mercado ⚠️ (só levantamento de disponibilidade)

**Ainda não medi a série de volume no tempo — isso espera o alinhamento com a Lia**
(o que o Ω precisa: volume por dia? por 12h? notional em USD ou nº de trades?).
Abaixo só a disponibilidade dos endpoints, que independe da escolha dela.

```
=== VOLUME NO TEMPO ===
Existe endpoint que devolve volume por dia (ou por 12h) de um mercado?  NÃO
Endpoint(s) testado(s):
  - CLOB   /prices-history?market=<token>&interval=all&fidelity=720  → devolve só {t, p}; SEM campo de volume
  - CLOB   /volume-history                                           → HTTP 404
  - CLOB   /volume                                                   → HTTP 404
  - Gamma  /volume-history                                           → HTTP 404
  - Gamma  /series?slug=<market>                                     → HTTP 200 mas corpo VAZIO ([])
  - data-api /volume                                                 → HTTP 404
  - Gamma  /markets?slug=<market>  → só AGREGADOS-snapshot, não série:
             volume, volumeClob, volume1wk, volume1wkClob, volume1mo, volume1moClob, volume1yr, volume1yrClob, volumeNum
             (janelas móveis "a partir de agora"; para mercado resolvido ficam constantes — não é série temporal)
Se NÃO:  dá pra derivar do /trades?  SIM (parcial) —
             data-api /trades traz por trade os campos: size, price, timestamp, side, outcome, conditionId, transactionHash, ...
             → somando size (ou size×price) por bucket de dia/12h dá volume no tempo.
         Evidência da limitação: o /trades é capado em ~20.000 trades mais recentes (F4: limit 10000 + offset 10000;
             offset>10000 → HTTP 400; filtros de tempo ignorados). Logo:
             - mercado grande (ex. M5/Trump, milhões de trades): só cobre a cauda recente → volume/dia histórico incompleto;
             - mercado médio (ex. M4/recessão): cobre a maior parte da vida do mercado (ver F4, 99,8% das janelas 12h com trade).
```

Ou seja: **não há série de volume pronta na API**; o único caminho é reconstruir do
`/trades`, com o mesmo teto de 20k que limita mercado grande. Antes de eu levantar
a série de fato, preciso da spec do Ω com a Lia (granularidade e se é notional ou
contagem).

---

## G6 — Datas de release do CPI de 2022–2024 (condicional)

**NÃO medido** — conforme instruído, depende de a reunião decidir se o backtest
tático volta antes de 2025. Deixei o levantamento de fontes pendente de gatilho:

```
Fonte testada          | Devolve 2022–2024? | Precisa de chave? | Formato | Observação
FRED release calendar  | não medido         | não medido        | —       | aguarda decisão da reunião (G6 é condicional)
BLS (retry do 403)     | não medido         | não medido        | —       | aguarda decisão; BLS bloqueou bot (403) no F7
```

**Typo de dez/2025 — qual das duas eu fiz:** MANTIVE O CSV CRU. A linha continua
`release_date = 2025-01-13` para "December 2025" (é o que a rule do mercado
`december-inflation-us-monthly` traz, transcrito sem alterar). **Não corrigi** —
segui a disciplina de dado cru; **a correção para `2026-01-13` fica com você no
tratamento**. Só existe essa uma linha (não há duplicata).

---

## Bloqueios

- **G5 (série de volume no tempo):** não medida por dependência de processo, não por
  falha técnica — precisa da spec do Ω com a Lia antes (granularidade + notional vs.
  contagem). Disponibilidade de endpoint: reportada acima.
- **G6:** não medido por ser condicional (aguarda decisão de reunião sobre janela do
  backtest). Sem bloqueio técnico.
- Nenhum rate limit, endpoint fora do ar (além dos 404 esperados testados no G5) ou
  problema de rede nesta sessão. VPN ligada; Gamma/CLOB/data-api/FRED/yfinance todos
  responderam.

## Commit
<preenchido no push — ver rodapé>
