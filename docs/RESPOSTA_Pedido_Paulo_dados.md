# RESPOSTA — `Pedido_Paulo_dados.md` (levantamento de dados, Paulo)

> **Como ler este documento.** As seções 1–4 foram **medidas ao vivo** contra a API
> real (2026-07-27, com VPN), rodando `scripts/explorar_clob_bidask.py` (bid/ask) e
> `scripts/levantar_mercados_pedido.py` (9 mercados + notas), mais FRED/yfinance. A
> regra de ouro do pedido foi respeitada — nada preenchido por plausibilidade:
>
> - **valores sem marca** = medidos ao vivo (datas, volume, séries, buckets, rules).
> - **[DOC]** = afirmação da documentação/issues oficiais (só onde não há o que medir).
> - **⏳ / 🟡** = ainda não medido (poucas pontas: contrato ZQ específico, calendários).
>
> Retornos crus salvos em `data/raw/clob_exploracao/`. Scripts em `scripts/`.

---

## 4.1 Bloco bid/ask (o mais importante)

**Resumo [MEDIDO 2026-07-27]:** **NÃO existe bid/ask histórico na API.** O
`/prices-history` do CLOB entrega **uma série de preço única** (`{t, p}`), **sem
bid/ask**. O endpoint candidato a bid/ask histórico (`/orderbook-history`) responde
**vazio** (`count=0`). Os endpoints de book (`/book`, `/price`, `/midpoint`,
`/spread`) só existem em **tempo real** — e, para mercado **resolvido**, retornam
**404 "No orderbook exists"** (o book é apagado na resolução; nem snapshot sobra).
Há, porém, **histórico de trades individuais com lado** (`data-api /trades`), do qual
dá para reconstruir um **proxy** de midpoint/bid-ask. **Isso trava a condição de
fechamento das views 2.4, 3.1, C, E e G** e exige decisão de reunião:
**(a)** aceitar a série única do `/prices-history` (comporta-se como último trade —
stale em mercado fino), ou **(b)** reconstruir proxy de midpoint a partir do fluxo de
`/trades` (tem `side` + `size`). Escalar.

```
=== BID/ASK HISTÓRICO ===  [MEDIDO 2026-07-27 — âncora: "Will Donald Trump win the
                            2024 US Presidential Election?", token Yes 217426...836455]
Endpoint testado: https://clob.polymarket.com/prices-history?market=<tokenYes>&interval=all&fidelity=720
Retorna:          série única {t, p} — um preço por instante, SEM bid/ask.
Campos crus:      ["t", "p"]
Amostra (5 linhas cruas):
  {"t": 1704412803, "p": 0.5}
  {"t": 1704456003, "p": 0.405}
  {"t": 1704499202, "p": 0.405}
  {"t": 1704542402, "p": 0.405}
  {"t": 1704585602, "p": 0.405}
Bid/ask histórico disponível?  NÃO.
  - /orderbook-history?asset_id=<token>  → HTTP 200  {"count":0,"data":[]}  (vazio; confirma issue #3635)
  - /orderbook-history?token_id / market → HTTP 400  "either market or asset_id must be provided"
  - /book /midpoint /price /spread       → HTTP 404  "No orderbook exists for the requested token id"
                                           (mercado RESOLVIDO: o book some na resolução)
  - /last-trade-price                    → HTTP 200  {"price":"0.998","side":"SELL"}  (só o último trade, sem série)
Histórico de trades individuais? SIM — data-api /trades?market=<conditionId> → HTTP 200.
  Campos crus do trade: proxyWallet, side (BUY/SELL), asset, conditionId, size, price,
  timestamp, title, slug, outcome, outcomeIndex, transactionHash, ...
  ⚠️ o parâmetro ?asset=<tokenId> NÃO filtra (devolve trades globais recentes) — usar market=<conditionId>.
  ⚠️ clob.polymarket.com/trades → HTTP 401 (exige API key); usar a data-api (pública).
Granularidade máxima:  12h. fidelity 1/10/60/180 devolvem 0 pontos para mercado
                       resolvido; só fidelity=720 traz dados (614 pontos; passo mediano 43200s = 12h).
Profundidade máxima:   vida inteira do mercado (interval=all). Âncora: 2024-01-05 → 2024-11-06 (306 dias).
```

Retorno cru salvo em `data/raw/clob_exploracao/prices_history_<token>.json` (entrega física).

---

## 4.2 Tabela dos 9 mercados

Todos os 9 medidos ao vivo (2026-07-27, VPN). Coluna **Bid/ask?** é a limitação
global do bloco 4.1 (sem book histórico) — uniforme `NÃO*`. Volume e datas vêm do
endpoint (Gamma `volumeNum` / CLOB `/prices-history` fidelity=720). Onde a família
tem vários mercados, medi o **de maior liquidez** (o "binário-mãe" que o pedido pede).

| ID | Existe? | 1ª data c/ dado | Última data | Volume (USD, do endpoint) | Critério de resolução | Bid/ask? | Dias sem trade (grade 12h) |
|---|---|---|---|---|---|---|---|
| **M1** CPI mensal | SIM — buckets (5–6/mês, recorrente) | 2025-07-16¹ | 2025-08-12¹ | evento ~$1,09M; bucket medido ~$205k | terminal — print mensal SA CPI-U do BLS | NÃO* | 0 ausentes (série limpa) |
| **M2** FOMC por reunião | SIM | 2024-04-04 | 2026-06-17 | por mercado, até ~$235M | terminal — decisão da reunião | NÃO* | grade 12h |
| **M3** Trajetória do Fed | SIM — PMF 9 buckets (nº de cortes) | 2024-12-30 | 2025-12-10 | evento $31,4M; bucket "7 cortes" $6,0M | terminal — nº de cortes no ano | NÃO* | 1 snapshot ausente |
| **M4** Recessão EUA | SIM (+ variante NBER-only) | 2025-01-08 | 2026-01-01 | $11,7M | two-pronged: NBER **ou** 2T de PIB<0 (BEA advance) — ver Nota B | NÃO* | 0 ausentes |
| **M5** Presidencial 2024 (Trump) | SIM | 2024-01-05 | 2024-11-06 | **$1,53 bi** | terminal — vencedor certificado | NÃO* | grade 12h (614 pts) |
| **M6** Tarifas EUA×China | SIM — família episódica | 2025-04-03 | 2025-04-16 | evento $11,0M (episódio abril "Liberation Day") | terminal — por deadline | NÃO* | episódio curto (~13 dias) |
| **M7** Ação militar EUA/Israel×Irã | SIM — família (65 deadlines) | 2025-04-01² | 2025-06-22² | episódio jun/2025 $29,9M; família `us-strikes-iran-by` **$529M** | terminal — ataque por deadline | NÃO* | 0 ausentes |
| **M8** Tributária (OBBB) / teto | SIM — família curta | 2025-07-01 | 2025-07-03 | evento reconciliation $1,75M; teto da dívida sep. ~$0,49M | terminal — aprovação por deadline | NÃO* | episódio curto (~3 dias) |
| **M9** Presidencial 2022 (midterms) | SIM, mas **`/prices-history` VAZIO** | — | — | $1,77M (volume existe no Gamma) | terminal — controle do Senado | NÃO* | sem série utilizável |

`NÃO*` = `/prices-history` não dá bid/ask; `/orderbook-history` volta **vazio** (medido);
**proxy** possível via `data-api /trades` (tem `side`). Limitação da API, uniforme a todos.
¹ M1 é **recorrente mensal** — cada mês é um evento próprio; as datas são de **um** mês
(julho/2025) como amostra. ² M7: medi o episódio jun/2025 (primário da view C); a família
`us-strikes-iran-by` tem 65 mercados por deadline.

**Parágrafos por surpresa (só onde há):**

- **M1 (CPI):** um evento **por mês**, com 5–6 buckets cada (ver Nota A). A "cobertura
  ~18 meses" que a view 2.2 pede exige varrer os eventos mês a mês — cada mês tem
  ~$0,4–1,1M de volume. Estrutura sólida de PMF.
- **M6 e M8 (tarifas / fiscal):** o "binário-mãe" por liquidez é **episódico e curto** —
  o de tarifas de abril/2025 vive ~13 dias; o "reconciliation by July 3", ~3 dias. A
  família cobre vários deadlines, então a view liga/desliga várias vezes (como o doc previa).
- **M7 (Irã):** liquidez enorme — a família `us-strikes-iran-by` soma **$529M** (65
  deadlines). O episódio jun/2025 (primário da view C) tem $29,9M e série de ~2,5 meses.
- **M9 (midterms 2022):** o mercado **existe** e tem volume ($1,77M), mas o
  `/prices-history` devolve **série vazia** — mercado de 2022, provavelmente anterior à
  cobertura do endpoint de série do CLOB. Confirma o "liquidez fraca / robustness" do
  doc: **sem série, a view 2.4 não roda no episódio 2022.**
- **M4 (recessão):** é uma **família** com dois critérios convivendo (Nota B); a escolha
  muda a view 3.1.

---

## 4.3 Respostas às notas A, B e C

```
NOTA A (formato do CPI):  [MEDIDO] BUCKET (faixas), não binário vs consensus.
  Resolve pela variação mensal do CPI-U com ajuste sazonal do BLS (1 casa
  decimal). Buckets crus de um mês real (August Inflation - Monthly, 5 buckets):
    - Will monthly inflation increase by 0.0% or less in August?
    - Will monthly inflation increase by 0.1% in August?
    - Will monthly inflation increase by 0.2% in August?
    - Will monthly inflation increase by 0.3% in August?
    - Will monthly inflation increase by 0.4% or more in August?
  (Julho teve 6 buckets — o nº varia por mês.) Extremos são buckets ABERTOS
  ("0.0% or less", "0.4% or more") → precisam de valor atribuído (decisão 11b).

NOTA B (recessão):        [MEDIDO] DUAS famílias coexistem —
  (1) NBER-only ("us-recession-announced-by-nber-before-june-2025"): rules crus —
      "resolve to Yes if the NBER publicly announces that a recession has occurred
      ... The resolution source will be the official announcements from the NBER."
      (a que o pedido NÃO quer: atraso do NBER contamina o preço.)
  (2) Two-pronged ("us-recession-in-2025", $11,7M): rules crus — "resolve to Yes
      if either: 1. NBER announces a recession ... by Dec 31, 2025; OR 2. the
      seasonally adjusted annualized % change in quarterly US real GDP ... is < 0.0
      for two consecutive quarters between Q4 2024 and Q4 2025, as reported by [BEA]."
  → A "resolução técnica" pura que o pedido prefere NÃO existe isolada: vem embutida
    como UMA das duas pernas do two-pronged. Restrição real, não detalhe.

NOTA C (one-touch):       [MEDIDO] TERMINAL, não one-touch (para M1/M2/M3).
  As rules do bucket de CPI NÃO contêm "touch" nem "at any time" — resolve pelo
  valor do print mensal do BLS (terminal). FOMC resolve pela decisão da reunião
  (terminal). Logo a receita "média da PMF" (E = Σ pᵢ·xᵢ) se aplica sem ressalva
  a M1/M2/M3. (O alerta de one-touch do pedido é para mercados de COMMODITIES, que
  não estão no nosso universo.)
```

---

## 4.4 Fontes externas

Medidas ao vivo (2026-07-27). **FRED via CSV público** (`fredgraph.csv?id=<ID>`) —
**sem API key**, achado que simplifica o pipeline.

| Fonte | Puxou? | Ticker/ID que funcionou | Desde | Frequência | Observação |
|---|---|---|---|---|---|
| FRED `T10YIE` (breakeven 10a) | ✅ SIM | `T10YIE` (fredgraph CSV) | 2003-01-02 | diária | 6.148 obs; sem chave |
| FRED `DGS10` (juros 10a) | ✅ SIM | `DGS10` (fredgraph CSV) | 1962-01-02 | diária | 16.844 obs |
| FRED `DTB3` (T-bill 3m) | ✅ SIM | `DTB3` (fredgraph CSV) | 1954-01-04 | diária | 18.930 obs; par do spread 10a−3m |
| ZQ mês pós-reunião | 🟡 PARCIAL | `ZQ=F` (contínuo) via yfinance | ~1 ano no teste | diária | tem `Open`; **contrato específico do mês** (ex. `ZQF26`) ainda a confirmar |
| ZQ de dezembro (contrato fixo) | ⏳ | contrato de dez (ex. `ZQZ25`) a confirmar | — | diária | idem: sintaxe do contrato específico no yfinance |
| Calendário FOMC 2022–2025 | ⏳ | fonte Federal Reserve (a fixar) | — | eventos | não puxado ainda — decisão de fonte |
| Calendário releases CPI 2022–2025 | ⏳ | fonte BLS (a fixar) | — | eventos | a data de release aparece nas *rules* dos mercados de CPI (fallback) |
| Abertura (Open) dos 9 ETFs | ✅ SIM | yfinance `download(...)['Open']` | igual ao Close | diária | campo `Open` confirmado disponível para os 9 |

> **Nota sobre ZQ:** `ZQ=F` (contrato contínuo) puxa com `Open/High/Low/Close`, mas as
> views 2.3/B precisam do **contrato específico** (mês pós-reunião / dezembro), não do
> contínuo. A sintaxe do contrato mensal no yfinance é a única peça da seção 3 que
> falta confirmar. O **Close ajustado** dos 9 ETFs já está em
> `data/etf_prices_daily.parquet`; agora o **Open** também está confirmado disponível.

---

## 4.5 Bloqueios

- **Bloqueio de rede resolvido com VPN (2026-07-27).** Antes da VPN, o DNS não
  resolvia `gamma-api.polymarket.com` / `clob.polymarket.com` nem na máquina do Paulo
  nem no Claude Code (`NameResolutionError`). **Com a VPN, tudo rodou** (seções 1–4
  medidas). Achado a registrar: os hosts do Polymarket estão bloqueados na rede local
  — **a VPN é necessária** para rodar o pipeline daqui.
- **M9 (midterms 2022): `/prices-history` vazio.** O mercado existe e tem volume, mas
  o endpoint de série não cobre 2022. Se a view 2.4 quiser usar 2022 como robustness,
  a série teria de vir de outra rota (ex. reconstruir de `data-api /trades`).
- **`clob/trades`** exige API key (HTTP 401) → usar a **data-api** pública
  (`data-api.polymarket.com/trades?market=<conditionId>`, filtra por `market`, não `asset`).
- **Pendências pequenas** (não bloqueiam, faltou rodar): sintaxe do **contrato ZQ
  específico** (mês/dezembro) no yfinance; **calendários FOMC/CPI** (decisão de fonte);
  varredura da **cobertura ~18 meses de CPI** mês a mês.

---

## Prioridade (seção 5) — estado

1. **Seção 1 (bid/ask)** — **MEDIDA e fechada.** Não há bid/ask histórico; decisão
   (série única vs proxy de `/trades`) escalada para reunião. 🟢
2. **M5, M4, M1, M2** — **todos medidos** (existência, datas, volume, resolução). 🟢
3. **Notas A, B, C** — **medidas** (buckets crus do CPI, rules de recessão, terminal). 🟢
4. **M6, M7, M8, M3, M9** — **todos medidos** (primário por liquidez + surpresas). 🟢
5. **Seção 3 (fontes externas)** — FRED e Open dos ETFs ✅; falta só a sintaxe do
   contrato ZQ específico e os calendários FOMC/CPI. 🟡

---

## Fontes (WebSearch, jul/2026)

- Polymarket Docs — Get prices history: `docs.polymarket.com/api-reference/markets/get-prices-history`
- Polymarket Docs — Orderbook: `docs.polymarket.com/trading/orderbook`
- Polymarket/agent-skills — `market-data.md` (endpoints Gamma/CLOB/data-api)
- Polymarket/py-clob-client — issues #216, #189 (fidelidade <12h volta vazia em resolvidos), #180 (`/book` stale vs `/price`)
- nautechsystems/nautilus_trader — issue #3635 (`/orderbook-history` devolve `count=0`)
- Bitquery / Polymarket Data API — campos de `/trades` (`side`, `price`, `size`, `timestamp`, `asset`, `conditionId`)
- Polymarket — eventos de CPI mensal (buckets do print BLS) e recessão (`us-recession-in-2025`, `us-recession-announced-by-nber-before-june-2025`)
- Medição própria: `data/polymarket_fed_reunioes.parquet` (M2, volume do Gamma)
