# FOLLOW-UP 2 — `Pedido_Paulo_dados.md` (G1–G6)

> **Para o Claude do Paulo:** a entrega do F1–F10 fechou quase tudo que estava aberto — IDs, séries cruas dos 9,
> cap do `/trades`, midpoint, calendários, 17 meses de CPI, granularidade em mercado vivo. Conferi arquivo por
> arquivo contra o `origin/Paulo` (@ `90c7574`): **todos os counts e datas da tabela do F3 batem**. Nada disso
> precisa ser refeito.
>
> Sobraram **6 pendências**, e duas delas valem mais que as outras quatro somadas: **G1 e G2 são dado que você
> já mediu e não salvou em arquivo**. Sem eles, três táticas e duas views ficam com código pronto rodando em
> vazio. Se o tempo acabar, **G1 + G2 completos valem mais que os seis pela metade.**
>
> Regras iguais às dos pedidos anteriores: **você levanta e reporta, não decide nada**; campo não medido vai
> como `?`, nunca preenchido por plausibilidade; **não** normalize, interpole nem converta fuso em dado cru
> (o tratamento é a jusante, em módulo do Felipe); **push com hash** no fim.
>
> Lembrete operacional: os hosts do Polymarket só resolvem **com VPN**.

---

## Prioridade

| # | Pendência | Por que trava |
|---|---|---|
| **G1** | **`Open` diário dos 9 ETFs** | Você confirmou que existe (27/07) e o parquet só tem close ajustado. Trava **as 3 táticas** |
| **G2** | **Séries do FRED salvas em arquivo** | Você mediu as 3 (27/07) e não salvou nenhuma. Trava a **view 3.1** e o benchmark da **2.2** |
| **G3** | **Série do token No** de 2 binários | Decide se o par Yes/No precisa ser normalizado ou se um lado basta |
| **G4** | **3 buracos de CPI** (abr/25, jan/26, fev/26) | Diz se a série da view 2.2 tem furo real a tratar |
| **G5** | **Volume dia a dia por mercado** | Insumo do Ω (módulo da Lia) — **alinhar com ela antes de medir** |
| **G6** | **Datas de CPI de 2022–2024** (condicional) | Só se a reunião decidir que o backtest tático volta antes de 2025 |

---

## O que NÃO precisa mais ser feito (para não gastar sessão)

- **Contrato ZQ mensal:** medido e fechado — nenhuma sintaxe funciona no yfinance. A escolha da fonte
  alternativa (CME / Nasdaq Data Link / Barchart) é **decisão do grupo**, não tarefa sua.
- **M9 (Senado 2022):** morto pelas duas vias (`/prices-history` vazio e `/trades` = 0). Medido, encerrado.
- **`/trades`:** o cap de 20k (limit 10000 + offset 10000, filtros de tempo ignorados) encerrou a discussão —
  a reconstrução de midpoint por trades saiu de cena. Não precisa medir mais nada nesse endpoint.
- **Re-puxar as séries dos 9 / dos buckets de CPI:** conferidas e aceitas.

---

## G1 — `Open` diário dos 9 ETFs (prioridade máxima)

O `data/etf_prices_daily.parquet` traz **só** `preco_ajustado` (close ajustado, `auto_adjust=True`). As três
táticas operam na **abertura**: o gap de fim de semana rende "abertura de segunda → fechamento de segunda", e o
prêmio de anúncios entra na véspera e sai na abertura. Sem `Open`, o código não roda.

Faça:
1. Acrescente a abertura ao mesmo dataset (coluna nova no formato longo, ex. `preco_abertura`) **ou** entregue um
   arquivo irmão — tanto faz, desde que seja **os mesmos 9 tickers, na mesma janela, no mesmo alinhamento de datas**
   do arquivo atual (2003-12-05 → 2026-07-08, 5.681 datas × 9).
2. **Diga em que base o `Open` veio:** ajustado (`auto_adjust=True`, mesma base do close que já está lá) ou cru.
   Não precisa escolher — precisa estar escrito, porque misturar close ajustado com open cru gera retorno
   intradiário falso em todo dia de dividendo.
3. Atualize o `data/README.md` com a coluna nova.

```
=== OPEN DOS ETFs ===
Arquivo:                <caminho>
Coluna(s) nova(s):      <nome>
Base do Open:           <ajustado auto_adjust=True | cru>
Nº de linhas:           <n>  (esperado: 51.129 se for a mesma janela)
Tickers:                <lista>
Janela:                 <primeira data> → <última data>
Alinhado ao close?      SIM / NÃO — <se NÃO, onde diverge>
Dias com Open ausente:  <n>  (e quais tickers)
```

---

## G2 — Séries do FRED salvas em arquivo (prioridade máxima)

Na resposta de 27/07 você mediu as três e confirmou que saem **sem chave**, pelo CSV público
(`fredgraph.csv?id=<ID>`): `T10YIE` (6.148 obs, desde 2003-01-02), `DGS10` (16.844, desde 1962-01-02) e
`DTB3` (18.930, desde 1954-01-04). **Nenhuma foi salva** — não há arquivo de FRED no `origin/Paulo`.

Salve as três **cruas** em `data/raw/` (`fred_T10YIE.csv`, `fred_DGS10.csv`, `fred_DTB3.csv`), exatamente como o
endpoint devolve — sem renomear coluna, sem reindexar, sem preencher feriado.

```
=== FRED (entrega física) ===
Série   | arquivo | URL exata | nº de linhas | primeira → última | como vem o valor ausente (ex. ".") | nº de ausentes
T10YIE  | ...
DGS10   | ...
DTB3    | ...
```

O "como vem o valor ausente" é o item que mais me importa depois do arquivo em si: o FRED marca feriado com um
caractere, não com linha faltando, e isso quebra o join com o calendário de pregão se ninguém avisar.

---

## G3 — Série do token No (2 mercados)

Você puxou só o token **Yes** dos 9. Preciso saber se o No é informação nova ou se é só o espelho do Yes.

Puxe o `/prices-history` do **tokenId No** de **M4** (recessão) e **M5** (Trump 2024) — os IDs estão no seu
próprio F2 — salve cru junto com os demais (mesmo padrão de nome, sufixo `_NO`) e reporte:

```
=== TOKEN NO ===
Mercado:                      <M4 | M5>
Arquivo salvo:                <nome>
Nº de linhas (No) / (Yes):    <n> / <n>
Mesmo grid de 12h que o Yes?  SIM / NÃO — <se NÃO, qual a diferença>
Soma p_yes + p_no nos instantes em que os dois existem:
  mínimo / mediana / máximo:  <v> / <v> / <v>
Nº de instantes com os dois:  <n>
```

Se a soma der 1,000 em todos os pontos, o No é redundante e eu paro de pedir. Se desencontrar, o tamanho do
desencontro é informação útil por si só.

---

## G4 — Os três buracos da varredura de CPI

Sua tabela do F8 tem 17 meses e você sinalizou **abril/2025** como lacuna. Faltam também **jan/2026** e
**fev/2026** (a tabela pula de dez/2025 para mar/2026) — esses dois não foram comentados.

Para **cada um dos três** (abr/2025, jan/2026, fev/2026):

```
Mês de referência:   <mês>
Buscas feitas:       <endpoint + termo exato de cada tentativa>
Achou mercado?       SIM / NÃO
Se SIM:              slug + nº de buckets + volume + 1ª/última data (e salve as séries cruas)
Se NÃO:              lacuna real (o Polymarket não abriu mercado desse mês)
```

Só quero saber se é buraco do Polymarket ou da busca. Negativo com a busca escrita ao lado é resposta completa.

---

## G5 — Volume dia a dia por mercado ⚠️ alinhar com a Lia antes

Você entregou **volume total por evento**. O Ω (medidor de confiança das views, módulo da **Lia**) provavelmente
precisa de volume **variando no tempo**, não de um total. **Quem especifica o que o Ω precisa é ela** — fale com
a Lia antes de medir, senão o risco é levantar a série errada.

O que dá pra reportar sem depender dela (é levantamento de disponibilidade, não escolha):

```
=== VOLUME NO TEMPO ===
Existe endpoint que devolve volume por dia (ou por 12h) de um mercado?  SIM / NÃO
Endpoint(s) testado(s):   <URL exata>
Se SIM:                   granularidade, janela coberta, cobre mercado resolvido?, campos crus
Se NÃO:                   dá pra derivar do /trades? (lembrando o cap de 20k) — SIM / NÃO, com evidência
```

---

## G6 — Datas de release do CPI de 2022–2024 (só se a reunião mandar)

O `cpi_release_dates.csv` começa em jan/2025, porque veio das *rules* dos mercados — e mercado de CPI só existe
de 2025 pra frente. Isso limita o backtest das táticas. **Não faça ainda**: depende de a reunião decidir se o
backtest volta antes de 2025.

Se mandarem fazer, é medição, não escolha de fonte:

```
Fonte testada           | Devolve 2022–2024? | Precisa de chave? | Formato | Observação
FRED release calendar   | ...
BLS (retry do 403)      | ...
```

**Correção que já pode entrar (é erro conhecido, não decisão):** a linha do CPI de **dez/2025** está com
`release_date = 2025-01-13`; o certo é **2026-01-13** — confirmei pela série do próprio mercado
(`december-inflation-us-monthly`), que termina em 2026-01-13. Você sinalizou o typo e manteve cru, que é o
procedimento certo. Se preferir manter o CSV 100% cru, mantenha e **eu corrijo no tratamento** — só me diga
qual das duas você fez, porque as duas linhas não podem existir ao mesmo tempo.

---

## Formato da devolução

Um bloco só, colável, nesta ordem — **G1, G2, G3, G4, G5, G6** — cada um com o cabeçalho `## G<n> — <título>` e
exatamente o formato pedido na seção correspondente. Sem introdução, sem resumo executivo, sem recomendação,
sem sugestão de decisão.

Fecha com:

```
## Bloqueios
<lista do que não deu, com o motivo: rate limit, endpoint fora, precisa de chave, rede, não encontrado após N buscas>

## Commit
<hash + branch do push>
```

E, como sempre: **um `?` honesto é útil; um número inventado contamina uma decisão metodológica.**
