# RESPOSTA — FOLLOW-UP 3 · G7 (base de ajuste dos dois parquets de ETF)

**Para o Felipe.** Consertado. Os dois arquivos (`etf_open_daily.parquet` e
`etf_prices_daily.parquet`) foram **re-gerados de um único `yf.download`**, então
agora estão na **mesma base de ajuste**. O teste que você apontou (razão
abertura/fechamento de TIP e TLT) passou: os dois voltaram para o ruído
intradiário. Fonte, universo e janela **não** mudaram (segue yfinance, mesmos 9,
período máximo comum) — só a base de ajuste passou a ser compartilhada.

Script: `scripts/g7_reajuste_etfs.py` (baixa Open e Close do mesmo objeto `raw` e
salva os dois a partir dele — não existe janela entre pulls onde um dividendo
entre em só um dos arquivos). Formato mantido: dois arquivos irmãos em formato
longo, como já estavam.

---

## `=== G7 — BASE DE AJUSTE ===`

```
Arquivos gerados:            data/etf_prices_daily.parquet + data/etf_open_daily.parquet   (um pull só? SIM)
Data/hora do download:       2026-08-06T20:56:33+00:00 (UTC)
Chamada usada:               yf.download(['XLK','XLU','XLP','XLF','XLE','XLV','TIP','TLT','SPY'],
                               start=None, end=None, period='max', interval='1d',
                               auto_adjust=True, progress=False, threads=False)
                             -> Open  = raw["Open"][tickers]
                             -> Close = raw["Close"][tickers]   (mesmo objeto raw)
Nº de linhas / tickers:      51.318 (cada arquivo) / 9  [XLK, XLU, XLP, XLF, XLE, XLV, TIP, TLT, SPY]
Janela:                      2003-12-05 -> 2026-08-06   (5.702 datas; 0 NaN em close e open)
Mediana de abertura/fechamento - 1, por ticker:
  SPY -0,059%  TIP +0,000%  TLT -0,023%  XLE -0,046%  XLF -0,038%
  XLK -0,064%  XLP -0,042%  XLU -0,034%  XLV -0,027%
  -> todos dentro de ± 0,1%; TIP e TLT (o teste) ZERARAM o degrau. Fora de ± 0,1%: NENHUM.
Mudou algum fechamento em relação ao arquivo antigo?  SIM — só TIP e TLT (deslocamento de NÍVEL).
  TIP:  -1,869% (mediana/mín nas 5.681 datas comuns; afina para -0,728% perto do fim)
  TLT:  -0,791% (mediana; afina para -0,401% perto do fim)
  Outros 7 (SPY, XLE, XLF, XLK, XLP, XLU, XLV):  0,000% em todas as datas comuns — NÃO mudaram.
```

### Antes × depois (razão abertura/fechamento − 1, o teste do G7)

| | SPY | **TIP** | **TLT** | XLE | XLF | XLK | XLP | XLU | XLV |
|---|---|---|---|---|---|---|---|---|---|
| **antes** (bases diferentes) | −0,06% | **−1,15%** | **−0,41%** | −0,05% | −0,04% | −0,06% | −0,04% | −0,04% | −0,03% |
| **depois** (mesmo pull) | −0,06% | **+0,00%** | **−0,02%** | −0,05% | −0,04% | −0,06% | −0,04% | −0,03% | −0,03% |

TIP e TLT saíram do degrau e entraram no ruído dos outros sete. O alfa fabricado
na janela `abertura(D)→fechamento(D)` (+1,15% TIP / +0,40% TLT) sumiu.

---

## O campo que importa pra você: **o fechamento mudou (só TIP e TLT)**

Você pediu para eu marcar isso porque suas medições em cima do close (perfil de
defasagem `k`, sensibilidade) dependem do nível. **Resposta: SIM, para TIP e TLT.**

- É um **deslocamento de nível de toda a história**, não de datas isoladas: a
  diferença `novo/antigo − 1` é praticamente constante (**TIP ≈ −1,869%**,
  **TLT ≈ −0,791%** na maior parte das 5.681 datas comuns), afinando perto do fim
  (−0,728% / −0,401%) porque as datas recentes carregam menos ex-dividendos novos.
- **Causa:** o arquivo de close antigo foi baixado em **2026-07-09**. TIP e TLT
  distribuem **mensalmente**; entre 09/jul e hoje (06/ago) entraram ex-dividendos
  novos, e o `auto_adjust=True` reescala **toda** a história a cada um. Ou seja: o
  degrau que você viu no par open/close era o **espelho** disso — o open (pull de
  02/ago) já tinha um fator a mais que o close (pull de 09/jul) não tinha.
- **Os outros 7 não mudaram** (0,000% em todas as datas comuns): não tiveram
  ex-dividendo novo com efeito material nessa janela de ~1 mês.

**O que isso te custa:** refazer as medições de `k`/sensibilidade **só para TIP e
TLT** (o nível deles desceu ~1,87% / ~0,79% em bloco). Os outros 7 ficam como
estão. Correlações e retornos close-a-close **não** mudam de forma (é fator
multiplicativo constante) — o que muda é o nível absoluto de TIP/TLT.

---

## Duas coisas que você pediu para evitar repetir

1. **Data/hora do download agora está registrada.** Anotei no `data/README.md` o
   timestamp do pull de cada arquivo (e que ambos saíram do **mesmo** pull), para
   qualquer um ver se dois arquivos são comparáveis sem ter que medir a razão.
2. **A janela esticou** de `2026-07-08` para **`2026-08-06`** (pull fresco de hoje):
   **+21 pregões**, 5.681 → 5.702 datas, 51.129 → 51.318 linhas por arquivo. O
   limite inferior segue `2003-12-05` (estreia do TIP). Como você disse que seu
   alinhamento com o poly usa o grid de datas do close: **o grid novo vai até
   2026-08-06**, mesmas datas nos dois arquivos, 0 NaN.

---

## Bloqueios

Nenhum. G7 rodou de ponta a ponta ao vivo, os dois arquivos saíram do mesmo pull,
0 NaN, teste do open/close passou.

## O que continua parado (sem ação minha, como no follow-up 2)

- **G5 (série de volume no tempo):** espera a spec do Ω com a Lia
  (`Dump/trocas/Pergunta_Lia_omega_volume.md`).
- **G6 (CPI 2022–2024):** condicional à reunião.
- *(Detalhe sem ação, do G3: os slots de 12h com os dois lados no M4 dão 715, não
  716 — um slot tem só um lado. Não muda a conclusão de que o No é redundante.)*

## Commit

```
<preenchido no push>  (branch Paulo)
```
