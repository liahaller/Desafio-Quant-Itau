# Resposta ao PEDIDO da Lia — valor realizado do CPI (MoM) por mês de referência

**De:** Paulo · **Para:** Lia · **Data:** 2026-08-10
**Pedido:** `Downloads/PEDIDO_Paulo_cpi_realizado.md` (robustez do relatório — teste de não
circularidade do Ω na view 2.2, análogo ao que já roda na 2.3/FOMC).

---

## TL;DR

- Entreguei o **CPI MoM (variação mensal, em pontos percentuais — a unidade dos buckets)**
  para todos os meses de referência dos mercados-mês do Polymarket, em **≥2 casas decimais**.
- **Ajuste sazonal (SA vs NSA):** a *rule* de todo mercado a partir de fev/2025 diz
  **explicitamente SA** (“seasonally adjusted CPI-U”). Entrego **SA como o número que serve**,
  e dou o **NSA ao lado** para você ver a diferença. Os dois mercados mais antigos (dez/2024,
  jan/2025) têm rule **vaga** (não nomeiam a série) — sinalizado abaixo.
- **Vintage:** entrego o **first-print** (valor que existia no dia do release, via **ALFRED**),
  que é o correto para o seu teste, **e** o revisado ao lado. **Vale a pena**: em **dez/2024** e
  **ago/2025** o valor *revisado* cairia no **bucket errado**; o first-print cai no certo.
- **Checagem de não-circularidade (o que você queria):** o first-print SA arredondado a 1 casa
  cai no bucket que o mercado resolveu em **15 de 15** meses com desfecho utilizável — análogo
  ao seu **16/16** do FOMC. **A view 2.2 agora tem verificação de não-circularidade.**
- **3 meses ficam de fora do teste** (com motivo, não por falta de dado meu): **out/2025**
  (release fantasma — resolvido pelo mercado mas ausente do FRED), **nov/2025** (MoM indefinível
  porque a base out/2025 não existe) e **jul/2026** (ainda não saiu — release 12/08/2026).
- **Aside respondida:** o mercado `october-inflation-monthly` **resolveu** (não foi cancelado) —
  UMA resolveu o bucket **0,3%** em 22/11/2025. Detalhe e implicação na seção 6.

---

## 1. Escopo — reconciliação do “19” (achei 18)

Você citou **19 mercados-mês** no `clob_exploracao` (dez/2024 a jul/2026). Varrendo o clob por
família de mercado, eu conto **18 mercados** cobrindo esses meses. A janela dez/2024→jul/2026 tem
20 meses; faltam **dois buracos reais** (sem mercado no Polymarket, não é falha de coleta):

- **abr/2025** — buraco já conhecido (documentado no G4).
- **fev/2026** — **não existe** mercado mensal de CPI US (confirmei na Gamma: `public-search`
  por “february 2026 inflation” não traz mercado; o clob só tem `february-inflation-monthly` =
  fev/**2025**).

Ou seja: 20 meses − 2 buracos = **18 mercados**. Se você tinha um 19º na sua lista, me diga qual
(slug) que eu concilio — pode ser um mercado que saiu do clob ou uma contagem diferente do buraco.
**Isto não muda nenhum valor abaixo**, só o total.

---

## 2. Detalhe 1 — Ajuste sazonal: **SA** (lido da rule, não decidido por mim)

A rule de cada mercado (texto oficial na Gamma) resolve isso. Do fev/2025 em diante o texto é
idêntico e **explícito**:

> “This is a market about the one-month percent change in the **seasonally adjusted** Consumer
> Price Index for All Urban Consumers (CPI-U) published by the BLS… resolve to the number the
> one-month **seasonally adjusted** CPI-U increased in *[mês]* according to the monthly BLS report.”

→ Fonte correta = **`CPIAUCSL`** (SA). O NSA (`CPIAUCNS`) vai ao lado só para referência.

**Validação cruzada (bônus):** se a régua fosse NSA, o casamento com os buckets **quebraria** em
vários meses — ex.: fev/2025 NSA = **0,44** cairia no bucket 0,4%, mas o mercado resolveu **0,2%**
(= SA 0,22). O SA casa 15/15; o NSA não. Isso confirma que (a) a rule é mesmo SA e (b) puxei a
série certa.

**⚠️ Exceção honesta — os dois mercados mais antigos:** `december-inflation-monthly` (dez/2024) e
`january-inflation-monthly` (jan/2025) têm rule **legada e vaga** (“a market on the inflation rate
for December, measuring the monthly increase in consumer prices”) — **não** nomeiam SA/NSA nem a
série. Para esses dois, “SA pela rule” é **inferência** minha (por consistência com os buckets: o
SA casa, o NSA não). Dou os dois valores mesmo assim; a ressalva fica registrada.

---

## 3. Detalhe 2 — Vintage: **first-print** (ALFRED), com o revisado ao lado

Você pediu o valor que existia **no dia** da resolução, não o revisado. Entrego o **first-print**
tirado do **ALFRED** (FRED com `realtime = data do release`), que reconstrói a série tal como
publicada naquele dia. **A escolha importa na prática:**

| Mês | first-print SA → bucket | revisado SA → bucket | bucket que o mercado resolveu |
|---|---|---|---|
| **dez/2024** | 0,39 → **0,4%** ✓ | 0,34 → 0,3% ✗ | **0,4%** |
| **ago/2025** | 0,38 → **≥0,4%** ✓ | 0,35 → 0,3% ✗ | **≥0,4%** |

Nesses dois meses o **revisado erraria o bucket**. Por isso o first-print é o número certo para o
seu teste. (Nos demais meses os dois arredondam para o mesmo bucket, mas diferem na 2ª casa —
que é justamente a distância à fronteira que você quer enxergar.)

---

## 4. Detalhe 3 — Casas decimais e arredondamento

- Entrego **2 casas** na tabela (o cálculo interno tem ~5 casas; disponível se precisar de mais).
- **Como o mercado resolve:** a própria rule diz que a fonte “reports to the **one decimal point**
  (e.g. 0.4%). Thus, this is the level of precision that will be used when resolving the market.”
  Ou seja, **a fronteira do bucket é no número de 1 casa** do BLS. Por isso, na coluna de checagem,
  arredondo o first-print SA a 1 casa antes de comparar com o bucket — e dou a 2ª casa para você
  medir a folga até a fronteira.

---

## 5. Tabela principal — CPI MoM (%, pp) por mês de referência

`SA = CPIAUCSL`, `NSA = CPIAUCNS`. `first-print` = ALFRED na data do release; `revisado` = série
corrente do FRED. `SA-fp→1casa` = first-print SA arredondado (a grandeza que o mercado resolve).
`bate?` = esse valor cai no bucket vencedor?

| Mês ref | Release | SA first-print | SA revisado | NSA first-print | NSA revisado | Bucket venc. | SA-fp→1casa | bate? |
|---|---|---|---|---|---|---|---|---|
| dez/2024 | 2025-01-15 | 0.39 | 0.34 | 0.04 | 0.04 | 0.4% | 0.4% | ✓ |
| jan/2025 | 2025-02-12 | 0.47 | 0.43 | 0.65 | 0.65 | ≥0.4% | 0.5% | ✓ |
| fev/2025 | 2025-03-12 | 0.22 | 0.23 | 0.44 | 0.44 | 0.2% | 0.2% | ✓ |
| mar/2025 | 2025-04-10 | -0.05 | 0.03 | 0.22 | 0.22 | ≤0.1% | -0.1% | ✓ |
| mai/2025 | 2025-06-11 | 0.08 | 0.10 | 0.21 | 0.21 | 0.1% | 0.1% | ✓ |
| jun/2025 | 2025-07-15 | 0.29 | 0.25 | 0.34 | 0.34 | 0.3% | 0.3% | ✓ |
| jul/2025 | 2025-08-12 | 0.20 | 0.23 | 0.15 | 0.15 | 0.2% | 0.2% | ✓ |
| ago/2025 | 2025-09-11 | 0.38 | 0.35 | 0.29 | 0.29 | ≥0.4% | 0.4% | ✓ |
| set/2025 | 2025-10-24 | 0.31 | 0.30 | 0.25 | 0.25 | 0.3% | 0.3% | ✓ |
| **out/2025** | — | — | — | — | — | 0.3% | — | — (ghost, ver §6) |
| **nov/2025** | 2025-12-18 | — | — | — | — | 0.3% | — | — (base ausente, ver §6) |
| dez/2025 | 2026-01-13 | 0.31 | 0.30 | -0.02 | -0.02 | 0.3% | 0.3% | ✓ |
| jan/2026 | 2026-02-13 | 0.17 | 0.17 | 0.37 | 0.37 | 0.2% | 0.2% | ✓ |
| mar/2026 | 2026-04-10 | 0.87 | 0.87 | 1.05 | 1.05 | ≥0.8% | 0.9% | ✓ |
| abr/2026 | 2026-05-12 | 0.64 | 0.64 | 0.85 | 0.85 | 0.6% | 0.6% | ✓ |
| mai/2026 | 2026-06-10 | 0.47 | 0.47 | 0.63 | 0.63 | 0.5% | 0.5% | ✓ |
| jun/2026 | 2026-07-14 | -0.42 | -0.42 | -0.35 | -0.35 | ≤0.1% | -0.4% | ✓ |
| **jul/2026** | 2026-08-12 | — | — | — | — | — | — | — (pendente, ver §6) |

> Onde `first-print == revisado` (2026-01 em diante), é porque a série ainda não sofreu revisão
> de fator sazonal desde o release — não é erro. As revisões SA aparecem nos meses de 2024–2025.

---

## 6. Os três meses fora do teste (com motivo)

**out/2025 — release fantasma, mas o mercado resolveu.** O CPI de out/2025 **nunca foi publicado**
pelo BLS (shutdown de 2025): `CPIAUCSL` e `CPIAUCNS` têm out/2025 = `.` (ausente) em **todas as
vintages** do ALFRED — confirmei que nunca existiu no FRED. **Porém o mercado
`october-inflation-monthly` NÃO foi cancelado:** o UMA **resolveu** o bucket **0,3%** (Yes) em
**2025-11-22** (os outros buckets resolveram No). Ou seja, há um desfecho de mercado (0,3%) que **o
pipeline do FRED não consegue reproduzir**. **Isto é uma decisão sua, não minha** (CLAUDE.md §1):
ou você (a) confia na resolução do UMA e usa 0,3% como “realizado”, ou (b) trata out/2025 como sem
desfecho (o conservador que você já sugeriu). Eu **não** cravei — deixo o fato posto.

**nov/2025 — MoM indefinível pelo FRED.** O índice de nov/2025 **existe** (`CPIAUCSL` = 325,063),
mas o MoM de 1 mês precisa da **base out/2025**, que é o buraco acima. Logo o FRED (`units=pch`)
não computa nov/2025 (nem revisado, nem first-print). O mercado `november-inflation-monthly`
resolveu **0,3%** — ou seja, existiu um número de novembro que o mercado usou, mas o FRED **não o
carrega como MoM de 1 mês** (por falta da base out/2025). Recomendo tratar nov/2025 **com
ressalva**: tenho o índice de novembro, mas não um MoM de 1 casa reproduzível de forma limpa pelo
pipeline do FRED.

**jul/2026 — ainda não saiu.** Release agendado **12/08/2026**; hoje é 10/08/2026. O mercado
`july-inflation-us-monthly` ainda está aberto (sem bucket vencedor). Fica pendente por calendário,
não por dado — te mando o valor assim que sair, se ajudar.

---

## 7. Aside respondida — como o `october-inflation-monthly` resolveu

Você perguntou porque a série dele termina com um bucket em 0,865 e o CPI de out/2025 nunca saiu.
**Resposta:** o mercado **resolveu normalmente pelo UMA** (não houve cancelamento/reembolso):

- `closed = true`, `closedTime = 2025-11-22`, todos os 5 buckets com `umaResolutionStatus = resolved`.
- **Bucket vencedor: 0,3%** (`outcomePrices = ["1","0"]`); os demais buckets resolveram `["0","1"]`.
- O 0,865 que você viu é **preço de mercado** no fim da vida (probabilidade implícita ~86,5% no
  bucket que acabou ganhando), **não** o valor do CPI.
- A data de resolução (22/11) bate com o atraso do shutdown (o set/2025 também escorregou de ~13
  para 24/10).

**Implicação para os seus testes:** aquele mercado **tem** desfecho de mercado (0,3%), mas **não
tem** valor realizado no FRED. Então, se você usar o desfecho do UMA, out/2025 entra como 0,3%; se
exigir o valor realizado do FRED como alvo, out/2025 fica sem alvo. Escolha metodológica sua.

---

## 8. Método e reprodutibilidade

- **Séries:** `CPIAUCSL` (SA) e `CPIAUCNS` (NSA), do FRED/ALFRED.
- **MoM %:** variação percentual mês-a-mês calculada pelo próprio FRED (`units=pch`) sobre o índice.
- **first-print:** ALFRED com `realtime_start = realtime_end = data do release` (a série tal como
  existia no dia); **revisado:** série corrente (sem `realtime`).
- **Datas de release:** calendário oficial do FRED (`cpi_release_dates_fred.csv`, release id=10),
  que já reflete os atrasos do shutdown (set/2025 → 24/10; out/2025 ausente).
- **SA/NSA e bucket vencedor:** lidos da Gamma (`/events?slug=`), campos `description` (rule) e
  `outcomePrices` por bucket. Nada normalizado, nada inventado.
- **Scripts** (no branch Paulo): `scripts/pedido_cpi_realizado_gamma.py` (regras + resolução) e
  `scripts/pedido_cpi_realizado_fred.py` (FRED/ALFRED + checagem de bucket).
- **Artefatos crus** (`data/raw/`): `cpi_rules_gamma.json` (descrições/rules e resolução por
  mercado) e `cpi_realizado_mom.json` (a tabela acima em JSON, com erros por célula).

---

## 9. O que fica como decisão sua (não decidi)

1. **out/2025:** usar o desfecho do UMA (0,3%) ou tratar como sem alvo? (§6)
2. **nov/2025:** aceitar como “com ressalva” (índice existe, MoM de 1 casa não reproduzível) ou
   como sem alvo?
3. **Dois legados (dez/2024, jan/2025):** aceitar SA por inferência (a rule não nomeia a série)?
4. **jul/2026:** quer o valor quando sair (12/08) ou já congela sem ele?

Qualquer uma dessas eu implemento assim que você decidir — não bloqueia o que está acima.

---

## 10. Nota de robustez do teste de não-circularidade

Com os 15 meses utilizáveis, o first-print SA arredondado casa com o bucket resolvido em **15/15**.
Isso replica na 2.2 (CPI) exatamente o que a 2.3 (FOMC) já tinha (16/16): a **derivação do desfecho
concorda com o mercado**, então o alvo “erro contra o desfecho real” passa a existir **também na
view de inflação** — a limitação que o relatório declarava (“verificação existe numa view só”)
pode ser reescrita. Os únicos meses sem esse fecho são out/2025 (ghost) e nov/2025 (base ausente),
que são efeito do shutdown, não do método.

— Paulo
