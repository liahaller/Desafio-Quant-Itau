# LOG do projeto

---

## 2026-08-10 (3) — Paulo — G10 fecho: resposta completa ao Felipe + correção da linha 2025-01-13

**O que foi feito:**
- Reconstruída a tríade do G10 a partir dos docs em `~/Downloads` (PEDIDO → FOLLOWUP →
  RESPOSTA_FOLLOWUP) e do repo. Confirmado que os 3 entregáveis (G10a `DGS1`, G10b rótulos
  de payrolls, G10c calendário CPI) já estavam entregues e commitados em `b19c440`, e que o
  `docs/RESPOSTA_G10_Paulo.md` (resposta formal ao pedido) já fora entregue junto com o
  `FOLLOWUP_G10` (b45a602). Ou seja: o pedido original já estava respondido; a sessão foi de
  fecho, não de execução.
- **Correção no entregável:** o `RESPOSTA_FOLLOWUP_G10_Paulo.md` do Felipe mostrou que
  `2025-01-13` NÃO diverge do FRED — é typo-de-ano (+1 ano = `2026-01-13`, que o FRED
  confirma p/ December 2025). Ajustado o bloco G10c de `docs/RESPOSTA_G10_Paulo.md`: 13/15
  concordam (12 idênticas + 1 typo corrigido); 2 divergências reais (shutdown 2025). Commit
  `ae2b4be`.
- **Resposta total ao PEDIDO_G10:** escrito `docs/RESPOSTA_G10_Paulo_COMPLETA.md` (cópia em
  `~/Downloads`) — documento autossuficiente cobrindo os 3 entregáveis + as 2 decisões que o
  Felipe fechou (fredgraph confirmado; calendário não troca, os dois arquivos ficam) + aviso
  da re-puxada dos parquets (06/08, commit `87721ae`) + os 2 avisos do Felipe sobre o arquivo
  FRED (18 fevereiros de fatores sazonais no `release_id=10`; `mes_referencia` no shutdown) +
  o "o que eu NÃO fiz" (escopo respeitado: ZQ, EXPINF1YR, mercado novo, re-download, 2026, G6).

**O que quebrou:** nada de código. Busca semântica da memória offline (runtime worker,
`observation_search` exige server-beta) — usei git/arquivos direto.

**Pendente:**
- Fecho formal das Decisões 13 e 14 (calendário CPI / fonte do `DGS1`): o Felipe já deu o
  veredito no `RESPOSTA_FOLLOWUP_G10`; adicionada a atualização em `Decisoes_pendentes.md`,
  mas o flip do marcador (🔴/🟡 → fechada) aguarda confirmação humana (CLAUDE.md §6).
- Enviar `~/Downloads/RESPOSTA_G10_Paulo_COMPLETA.md` ao Felipe (ação do Paulo).

**Uso de IA:**
- **Modelo:** Claude Code / Opus 4.8.
- **Contexto consumido:** ~55% da janela.
- **Prompt inicial (verbatim):** "teste"
- **Iterações até aceitar:** ~5 rodadas de esclarecimento (o Paulo reenquadrou a sequência do
  G10 várias vezes até ficar claro que a resposta formal já existia; depois a escolha entre
  corrigir a linha do `2025-01-13` vs. enviar como estava).
- **Erros da IA:** nenhum dado fabricado. Atrito de comunicação: insisti na cronologia (git)
  quando o Paulo queria um sim/não direto sobre "já respondi o pedido?" — corrigido ao
  responder as duas perguntas literais de forma direta.
- **Decisões escaladas:** — (nenhuma nova; Decisões 13/14 atualizadas com o veredito do
  Felipe, fecho formal a confirmar pelo humano).
- **Tags:** —

## 2026-08-10 (2) — Paulo — CPI realizado (MoM) p/ o teste de não-circularidade da 2.2 (pedido da Lia)

**O que foi feito:** executado o `PEDIDO_Paulo_cpi_realizado.md`. Entregue o CPI MoM (%, pp) por
mês de referência dos mercados-mês do Polymarket (dez/2024→jul/2026), em ≥2 casas, com SA
(`CPIAUCSL`) e NSA (`CPIAUCNS`), first-print (ALFRED, vintage=data do release) e revisado lado a
lado. SA/NSA lido da *rule* de cada mercado na Gamma (não decidido): rule explícita "seasonally
adjusted" de fev/2025 em diante; 2 legados (dez/2024, jan/2025) com rule vaga → SA por inferência
(sinalizado). Casas: 2 na tabela, com nota de que a rule resolve em 1 casa.
- **Checagem de não-circularidade:** first-print SA arredondado casa com o bucket resolvido em
  **15/15** meses utilizáveis (análogo ao 16/16 do FOMC). Vintage importa: em dez/2024 e ago/2025 o
  *revisado* cairia no bucket errado; o first-print acerta.
- **Aside (out/2025 fantasma):** o mercado `october-inflation-monthly` **resolveu** (não cancelado)
  — UMA resolveu bucket 0,3% em 22/11/2025; o 0,865 era preço, não CPI. FRED não tem out/2025 em
  nenhuma vintage (ghost). nov/2025 = MoM indefinível (base out ausente). jul/2026 pendente (release
  12/08).
- **Escopo:** achei **18** mercados no clob (não 19); buracos = abr/2025 e fev/2026 (sem mercado).
  Sinalizado à Lia para reconciliar o 19º se existir.
- Artefatos: `scripts/pedido_cpi_realizado_gamma.py`, `scripts/pedido_cpi_realizado_fred.py`,
  `data/raw/cpi_rules_gamma.json`, `data/raw/cpi_realizado_mom.json`. Entregável:
  `docs/RESPOSTA_PEDIDO_Paulo_cpi_realizado.md` (cópia em `~/Downloads`).

**O que quebrou:** 1 chamada FRED transiente (HTTP 500 no NSA de abr/2026) — repuxada e conferida
(0,85006). Jul/2026 fp deu HTTP 400 (realtime no futuro) — esperado (release ainda não ocorreu).

**Pendente:** decisões da Lia registradas na Decisão 15 (tratamento de out/2025, nov/2025, SA
inferido nos legados, jul/2026). Nada bloqueia — a limitação anterior do relatório ("verificação
só na 2.3") já pode ser reescrita com o 15/15.

**Uso de IA:**
- **Modelo:** Claude Code / Opus 4.8.
- **Contexto consumido:** ~55% da janela.
- **Prompt inicial (verbatim):** "'/Users/paulomello/Downloads/PEDIDO_Paulo_cpi_realizado.md' faca
  tudo que a lia pediu, responda tudo que ela pediu, nao pule nada ou deixe nada em branco. e
  responda em um md baixe no meu pc para eu mandar para ela. depois de terminar, revise tudo. ask me
  clarifying questions. antes de executar, estime quantos tokens vai gastar e quanto tempo vai levar"
- **Iterações até aceitar:** 1 rodada (perguntas de esclarecimento respondidas com "A"; execução
  direta e aceita).
- **Erros da IA:** nenhum material. 1 valor ficou `None` por erro transiente da API (não alucinação)
  — detectado na revisão e repuxado. Contagem 19→18 conciliada com honestidade (não forcei o 19).
- **Decisões escaladas:** Decisão 15 (nova; tratamento dos meses sem alvo utilizável — call da Lia).
- **Tags:** `[PROMPT-CHAVE]` (execução completa do pedido de CPI realizado — reprodutibilidade).

---

## 2026-08-10 — Paulo — G5 alcança o FOMC (chave `conditionId` + as 76 faixas)

**O que foi feito:** executado o `PEDIDO_Paulo_G5_fomc.md` (recado da Lia) inteiro. Os dois
problemas que ela mediu (0 chaves em comum; G5 com 1 mercado FOMC contra 76 do parquet) estão
resolvidos. Entregável em `docs/RESPOSTA_PEDIDO_Paulo_G5_fomc.md`.

- **Item 1 — chave no parquet:** `scripts/g5b_fomc_conditionid.py`. Acrescenta `conditionId` +
  `slug` ao `data/polymarket_fed_reunioes.parquet` (aditivo; 16.338 linhas / 76 mercados / 18
  eventos inalterados). Resolve por `gamma /events?id=` (18 chamadas, 1 por evento já no parquet →
  sem risco de mudar o universo; mesma fonte da Decisão 2). Casamento `question→conditionId`
  **76/76**. Junção G5×parquet por `conditionId`: **0 → 76** em comum.
- **Item 2 — G5 estendido ao FOMC:** `scripts/g5_volume_no_tempo.py` ganhou o estágio `fomc_stage`,
  que lê a view 2.3 do parquet enriquecido (grid de 12h e `conditionId` vêm do próprio parquet que a
  2.3 consome → alinhamento de slot **1:1**, 0 divergência conferida). Os `.json` `M2_fomc_*` deixam
  de ser lidos (o parquet cobre o FOMC inteiro, sem duplicar). Mesma regra `NaN`/`0` da Decisão 12.
  View 2.3: 1→**76 faixas**, 16.321 linhas (>0: 6.803 · `0`: 445 · `NaN`: 9.073 · 42/76 bateram o cap).
- **Cobertura honesta (o `?` que a Lia pediu):** as 76 faixas das 18 reuniões estão **todas**
  presentes. 12/18 reuniões 100% cobertas em todos os slots; 6 truncadas pelo cap de 20k só nos
  slots **iniciais** (Nov/2024, Dec/2024, Jan/2025, Mar/2025, Jul/2025, Sep/2025) — em todas o run-up
  colado na reunião fica inteiro. **Todas as reuniões de Oct/2025 em diante (6) estão 100%** (bate com
  a prioridade de recência dela).
- **Pipeline coerente:** `src/data_pipeline/download_polymarket_fed.py` (build_table) passou a emitir
  `conditionId`+`slug`, para um rebuild completo já sair com a chave. Não re-rodei (o parquet-fonte
  `_probabilities` não está em disco; enriqueci o `_reunioes` via g5b, sem derivar do que a Lia mediu).

**O que quebrou (e foi corrigido antes da entrega):**
- `fomc_grid` convertia `datetime64[ms]` com `//10**9` (unidade errada) → todos os slots colapsavam
  em ~1970, `slots=1` por mercado. Detectado pela janela `1970-01-01` no report; corrigido para
  `astype("datetime64[s]")` e re-rodado (trades já cacheados). Segunda passada: janela correta
  `2024-04-04 → 2026-07-29`.

**Conferências:** view 2.2 (CPI, 111 mercados, 6.699 linhas) e view B (9 mercados, 5.964 linhas)
**idênticas byte a byte ao `HEAD`** (Lia pediu para não tocar). Slot-set das 76 faixas bate 1:1 com o
parquet (0 mismatch). Sintaxe dos 3 scripts OK.

**Pendente:** nada bloqueia a Lia. Rótulo da coluna `mercado` na 2.3 hoje é o `slug` completo (chave
legível) — troco numa linha se ela preferir outro.

**Interface alterada (registrada):** esquema do `polymarket_fed_reunioes.parquet` ganhou 2 colunas
(`conditionId`, `slug`). Mudança **pedida pela consumidora (Lia) no `PEDIDO_Paulo_G5_fomc.md`** e
aditiva/retrocompatível — nota em `Decisoes_pendentes.md` (§ interface).

**Uso de IA:**
- **Modelo:** Claude Code / Opus 4.8.
- **Contexto consumido:** ~50% da janela.
- **Prompt inicial (verbatim):** "'/Users/paulomello/Downloads/PEDIDO_Paulo_G5_fomc.md' responda isso para a lia. responda tudo que ela pediu, nao deixe nada faltando. apos terminar, revise."
- **Iterações até aceitar:** ~2 rodadas internas (bug de unidade do `fomc_grid` ms→s; ajuste da ordem de colunas no entregável na revisão).
- **Erros da IA:** (1) `fomc_grid` com `//10**9` sobre `datetime64[ms]` colapsou o grid em 1970 — pego pela janela do report e corrigido; (2) o entregável citou a ordem de colunas errada (`conditionId/slug` antes de `probabilidade`) — corrigido na revisão contra o parquet real.
- **Decisões escaladas:** — (nenhuma decisão metodológica nova; a mudança de esquema foi pedida pela Lia, registrada como nota de interface).
- **Tags:** `[PROMPT-CHAVE]` (execução completa do pedido G5-FOMC — reprodutibilidade).

---

## 2026-08-08 — Paulo — G10 (DGS1 · rótulo baldes payrolls · calendário CPI oficial)

**O que foi feito:** executado o `PEDIDO_G10_Paulo.md` inteiro, na ordem G10a→G10b→G10c,
ao vivo. Três scripts novos, entregável em `docs/RESPOSTA_G10_Paulo.md`.

- **G10a — `DGS1`:** `scripts/g10a_fred_dgs1.py`. `data/raw/fred_DGS1.csv` — **16.853
  linhas**, 1962-01-02→2026-08-06, **719 dias sem leitura** (campo vazio). Vértice de 1 ano
  da view B. **Escolha de fonte reportada:** o pedido templou a API `series/observations`,
  mas ela devolve valor com padding (`4.0600000000`) e ausência `"."` — NÃO idêntico aos
  `fred_DTB3/DGS10` (2 casas, ausência = campo vazio). Como "idêntico" é requisito e não se
  normaliza dado cru, usei o **fredgraph** (mesma fonte do G2/G8) → formato de fato idêntico.
  Mesma série, muda só a formatação; se preferir a API, é 1 linha. Reportado no entregável.
- **G10b — rótulo dos baldes:** `scripts/g10b_payrolls_bucket_labels.py`. Partindo do
  `payrolls_polymarket_markets.csv` (33, já US-only), `gamma /events?slug=`, 1 linha por
  balde → `data/raw/payrolls_bucket_labels.csv`, **182 linhas** (= soma dos `n_buckets`,
  bate). Colunas `slug_mercado, token_id, outcome, slug_desfecho, familia`. `token_id`=
  `clobTokenIds[0]` **casa 182/182** com os JSONs do G9b. `outcome`=`groupItemTitle` cru;
  binários sem grupo → `outcomes`. Nenhum mercado sem rótulo. Todos os 26 multi-bucket têm
  ponta aberta nas duas extremidades (listado).
- **G10c — calendário oficial do CPI:** `scripts/g10c_cpi_calendar.py`. `release_id` do CPI
  = **10**, confirmado por **nome exato** em `/fred/releases` (o 345 "Research CPI" foi
  descartado). `data/raw/cpi_release_dates_fred.csv` — **953 linhas**, 1949-03-24→2026-12-10
  (~250 desde 2003). **NÃO** sobrescrevi o `cpi_release_dates.csv`. Conferência com as 15
  atuais: **12 batem, 3 divergem** — `2025-01-13`(FRED `01-15`), `2025-10-15`(FRED `10-24`,
  shutdown +9d), `2025-11-13`(FRED não tem nov/2025; pula p/ `12-18`, shutdown). Reportado
  como aviso ANTES de qualquer troca, como o Felipe pediu.

**O que quebrou:** nada de código. Sonda inicial deu DNS-fail no sandbox e FRED deu 000
transitório; ambos resolvidos rodando com rede (fora do sandbox). Achado que mudou a
implementação do G10a: a API `observations` não é format-compatível com os `fred_*.csv`.

**Pendente:** trocar `cpi_release_dates.csv` pelo `_fred.csv` (decisão do grupo — 3
divergências do shutdown a ponderar). Fonte do G10a (fredgraph vs. API) — aguarda ok do
Felipe. G6 e Decisões de reunião seguem.

**Fecho de sessão (mesmo dia):** criado `docs/FOLLOWUP_G10_Paulo.md` — recado do `Paulo`
ao `Felipe` levando a decisão do calendário CPI (3 perguntas concretas) + a confirmação da
fonte do G10a. Registradas em `Decisoes_pendentes.md` a **Decisão 13 do `Paulo`** (troca do
calendário CPI, 🔴 aberta — grupo) e a **Decisão 14 do `Paulo`** (fonte do DGS1, 🟡
confirmação do Felipe, não bloqueia). Nenhuma fechada por conta própria. Estado do G10:
tudo entregue/commitado/pushed; o único aberto é a decisão do Felipe/grupo — depois dela o
`Paulo` executa o lado dos dados.

**Uso de IA:**
- **Modelo:** Claude Code / Opus 4.8.
- **Contexto consumido:** ~55% da janela.
- **Prompt inicial (verbatim):** "'/Users/paulomello/Downloads/PEDIDO_G10_Paulo.md' faca isso direitinho, exatamente da forma que ele pediu. quando terminar, cheque se fez tudo que ele pediu e exatamente da mesma forma. essa parte é essencial e nao pode ter erros."
- **Iterações até aceitar:** G10 em ~3 rodadas — (1) execução dos três + correção do G10a (fredgraph vs. API por formato); (2) correção do hash no entregável; (3) follow-up ao Felipe + Decisões 13/14 + fecho de sessão.
- **Erros da IA:** dois, ambos pegos na verificação: (a) 1ª versão do G10a usou a API `observations` literal e o formato saiu não-idêntico (padding + `"."`) — corrigido para fredgraph; (b) o `git commit --amend` que preencheu o hash gerou commit novo, então o entregável citou um hash morto (`0a0daea`) — corrigido para o commit real `b19c440` na conferência final.
- **Decisões escaladas:** 2 — Decisão 13 do `Paulo` (troca do calendário CPI, 🔴 grupo) e Decisão 14 do `Paulo` (fonte do DGS1, 🟡 confirmação do Felipe). Ambas reportadas em `docs/FOLLOWUP_G10_Paulo.md`, nenhuma fechada por conta própria.
- **Tags:** `[PROMPT-CHAVE]` (execução completa do G10 — reprodutibilidade).

---

## 2026-08-08 — Paulo — D9 fechada (overlap FOMC) via recado do `Felipe`

**O que foi feito:**
- Lido o recado `RECADO_Paulo_G5_recebido_e_D9.md` (Felipe/Lia). Conteúdo: (1) recebido
  do G5 — reproduziu byte a byte, inclusive sob pandas 3.0.4; (2) aviso de que o
  `NaN`/`0` do G5 é anulado a jusante no `portao_volume` do `origin/Lia` (módulo da Lia,
  já avisada — não é item do `Paulo`); (3) proposta de fechar a **D9** (overlap FOMC) na
  **opção 1**, com número; (4) relógio (entrega 17/08, corte 13/08 — nada do `Paulo` no
  caminho crítico); (5) recomendação de manter a D12 do `Paulo` fechada.
- **Decisão do humano (Paulo): D9 → opção 1** — em cada data, usar só o mercado da
  **próxima** reunião do FOMC. Registrada em `Decisoes_pendentes.md` (§9, 🟢), com
  autoria do `Paulo`, o raciocínio (metodológico > custo) e o número do overlap (2,44×;
  1.952 reunião×dia vs. 801 datas distintas). Documenta o que o código do `Felipe` (2.3)
  e o da Lia (`dias_801_fomc.csv`) já rodam — nada precisa mudar a jusante.
- Nenhuma mudança de código nem de dado nesta sessão — só registro de decisão.

**O que quebrou:** nada.

**Pendente:**
- Aviso (2) do recado: o `portao_volume` colapsa `NaN` e `0` na entrada (é do módulo da
  Lia; ela já foi avisada pelo Felipe com reprodução). **Não é item do `Paulo`.**
- Decisões 3–8, 10, 11 do `Paulo`: aguardam reunião. D9 e D12 agora fechadas.
- G6 (CPI 2022–2024): condicional à reunião.

**Uso de IA:**
- **Modelo:** Claude Code / Opus 4.8.
- **Contexto consumido:** ~30% da janela.
- **Prompt inicial (verbatim):** "'/Users/paulomello/Downloads/RECADO_Paulo_G5_recebido_e_D9.md' o felipe  a lia fizeram isso para me mandar de recado. eu preciso responder algo ou é so um recado mesmo?"
- **Iterações até aceitar:** 1 rodada (triagem do recado → o humano escolheu a opção 1 → registro).
- **Erros da IA:** nenhum. Não decidi a D9 sozinho — apresentei o trade-off como insumo e o `Paulo` escolheu (CLAUDE.md §1).
- **Decisões escaladas:** D9 (fechada pelo humano nesta sessão, opção 1).
- **Tags:** —

---

## 2026-08-08 — Paulo — FOLLOWUP5 (G5): régua da Lia p/ o `NaN`-vs-`0` (Decisão 12 do `Paulo`)

**O que foi feito:**
- Executado o `FOLLOWUP5_Pedido_Paulo_dados.md` — a Lia (dona da régua Ω) respondeu à
  **Decisão 12 do `Paulo`** (slot pré-primeiro-trade: `NaN` ou `0`?): **separar os dois
  casos**. Truncamento do cap = `NaN` (dado existe, API não alcança; propaga, não veta);
  pré-primeiro-trade em mercado não capado = `0` (fato do mercado, ninguém negociou; veta
  o portão de volume).
- **Implementado** exatamente isso — a "uma linha" que ela previu: em
  `scripts/g5_volume_no_tempo.py`, a condição do `NaN` passou a exigir `res["bateu_cap"]`;
  mercado não capado antes do 1º trade cai no `else` e vira `0`. Docstring + rótulos do
  report atualizados para a régua dos dois casos. Re-rodado com o cache local
  (`data/raw/g5_cache/`, git-ignored) — **zero chamada nova de API**.
- **Conferido contra o CSV:** `g5_volume_no_tempo.csv` — `NaN` **424→346** (só
  truncamento: 2 M3 capados, 4-cuts=309 + 5-cuts=37), `0` **2403→2481** (+78
  pré-1º-trade nos 19 mercados não capados), positivos **10101** inalterados, total
  **12928** inalterado. `NaN` em mercado não capado agora = **0**. `t_cobertura_min` por
  mercado **inalterado** (`g5_volume_cobertura.csv` não mudou).
- Entregável: `docs/RESPOSTA_FOLLOWUP5_Pedido_Paulo_dados.md` (decisão + código + prova
  numérica + encanamento da numeração + Bloqueios) + cópia em `~/Downloads/`.
- **Decisão 12 do `Paulo`** marcada **🟢 fechada** no `Decisoes_pendentes.md`, atribuída à
  Lia (FOLLOWUP5), com a implementação registrada. Não fechei por conta própria — transcrevi
  a decisão da dona da régua, que respondeu por escrito.

**Encanamento (registrado):** a numeração das decisões diverge a partir da 8 entre os três
branches — "12" do `Paulo` é este G5, "12" do `Felipe` é o `E_FF` da 2.3. Convenção adotada:
citar sempre o branch ("D12 do `Paulo`"). Esquema definitivo fica para a reunião.

**O que quebrou:** nada. Mudança de uma condição, verificada contra o CSV-fonte.

**Pendente:**
- **G6 (CPI 2022–2024):** condicional à reunião, sem mudança.
- Decisões 3–11 do `Paulo`: aguardam reunião. A régua da Lia não tem mais item bloqueado no G5.

**Uso de IA:**
- **Modelo:** Claude Code / Opus 4.8.
- **Contexto consumido:** ~35% da janela.
- **Prompt inicial (verbatim):** "'/Users/paulomello/Downloads/FOLLOWUP5_Pedido_Paulo_dados.md' responda em um md. nao deixe nada de fora, revise para ver se esta tudo do jeito que ele pediu"
- **Iterações até aceitar:** 1 rodada (mudança única, conferida na primeira passada).
- **Erros da IA:** nenhum. Números todos reconferidos contra o CSV após o re-run.
- **Decisões escaladas:** — (nenhuma nova; fechei a Decisão 12 do `Paulo` com a resposta escrita da Lia).
- **Tags:** `[PROMPT-CHAVE]` (aplicação da régua da Lia ao G5 — reprodutibilidade).

---

## 2026-08-07 — Paulo — FOLLOWUP4 (G8 + G5): DFF do FRED e série de volume no tempo

**O que foi feito:**
- Executado o `FOLLOWUP4_Pedido_Paulo_dados.md` **inteiro** — os dois itens pedidos
  (G8 e G5), ao vivo. (Numa 1ª rodada só o G8 foi feito por leitura estreita do
  prompt; o Paulo pediu explicitamente para responder tudo, e o G5 foi executado na
  sequência.)

- **G8 — DFF:** baixada ao vivo a série **DFF** (Effective Federal Funds Rate) via
  `fredgraph.csv?id=DFF`, mesmo caminho público sem chave do G2. Novo
  `scripts/g8_fred_dff.py` (clone do `g2_fred.py`). Salvo cru em
  `data/raw/fred_DFF.csv` (`observation_date,DFF`), sem tratar. **26.334 linhas,
  1954-07-01 → 2026-08-05, 0 campos vazios** (DFF é taxa diária de calendário, sem
  buraco de feriado). Fecha o outro lado de `e_ff_bps = DTB3 − DFF` (view 2.3).

- **G5 — volume no tempo (spec da Lia):** novo `scripts/g5_volume_no_tempo.py`.
  Série 12h derivada do `data-api /trades` para os **121 mercados** das views ativas
  (2.2 = 111 [105 CPI_* + 6 M1] · 2.3 = 1 [M2] · B = 9 [M3]) já em
  `clob_exploracao/`. Por mercado: resolve `conditionId`, pagina `/trades` até o teto
  de 20k (F4), agrega por slot de 12h em `notional_usd = Σ(size×price)` **e**
  `n_trades`, e marca `t_cobertura_min` (trade mais antigo alcançado, 1 por mercado).
  Grid de 12h vem da série `/prices-history` já baixada. **Antes do `t_cobertura_min`
  = NaN (campos vazios); depois, slot sem trade = 0 legítimo.** Saídas:
  `data/raw/g5_volume_no_tempo.csv` (12.928 linhas) + `g5_volume_cobertura.csv`
  (1 linha/mercado). Janela 2024-12-30 → 2026-07-29 UTC. **3 mercados capados** no 20k
  (M2 set/2025, M3 4-cuts, M3 5-cuts) com `t_cobertura_min` reportado. 2.403 slots-0
  legítimos, 424 slots-NaN.
- **Resolução de IDs:** 21 dos 121 mercados são famílias que o filtro `clob_token_ids`
  do Gamma não indexa; resolvidos pelo evento (`/events?slug=` + match do tokenId em
  `clobTokenIds`) — `*-inflation-monthly`, `CPI_G4_janeiro`, `M1`, `M3` — e o M2 pelo
  slug de mercado com `closed=true`. Zero mercado sem resolver.
- Entregável: `docs/RESPOSTA_FOLLOWUP4_Pedido_Paulo_dados.md` (blocos `=== G8 ===` e
  `=== G5 ===` + Bloqueios + Commit) + cópia em `~/Downloads/`.

**Ponto de processo (aceito):** o G8 era a 2ª metade do FOLLOWUP3 e não foi sinalizado
na resposta do G7. Corrigido; item não entregue passa a entrar em Bloqueios.

**Levantado, NÃO decidido (para a Lia) — registrado como Decisão 12:** a regra "antes
de `t_cobertura_min` = NaN" foi aplicada literal a todos os mercados. Dos 424 NaN, 346
são de truncamento do cap (o caso que a regra protege) e 78 são "pré-primeiro-trade" em
19 mercados NÃO capados (a série de preço tem slot antes do 1º trade). Estes últimos
poderiam ser lidos como 0; sinalizado no entregável e escalado em `Decisoes_pendentes.md`
(Decisão 12), não fechei sozinho.

**Polimento final do entregável (mesma sessão):** o título/abertura do MD ainda diziam
"foco no G8" (sobra da 1ª rodada) e só citavam FRED — corrigido para refletir G8+G5 e o
Polymarket, com ponteiro explícito para `g5_volume_cobertura.csv` como a lista dos 121
mercados. Recalculei todos os números do entregável a partir dos CSVs-fonte antes de
liberar o envio: batem exatos.

**O que quebrou:** 1ª e 2ª rodadas do G5 deixaram ~79 e depois 21 mercados sem
`conditionId` (o filtro `clob_token_ids` não indexa famílias antigas; regex de slug de
evento era lowercase-only e não pegava `CPI_G4_...`; série M não tem slug de evento no
nome). Corrigido em duas iterações (resolver por evento + override da série M + fallback
`closed=true` no M2). Cache em disco (`data/raw/g5_cache/`, git-ignored) tornou os
re-runs incrementais.

**Pendente:**
- **G6 (CPI 2022–2024):** condicional à reunião, sem mudança (não é item do FOLLOWUP4).

**Uso de IA:**
- **Modelo:** Claude Code / Opus 4.8.
- **Contexto consumido:** ~65% da janela.
- **Prompt inicial (verbatim):** "'/Users/paulomello/Downloads/FOLLOWUP4_Pedido_Paulo_dados.md' responda isso em um md. foque nas principais questoes dele: parte do g8"
- **Iterações até aceitar:** ~5 rodadas (G8 direto; G5 exigiu 2 correções do resolvedor
  de `conditionId` até resolver os 121; depois o Paulo pediu para responder TUDO — G5 foi
  feito na sequência; e verificação final + polimento de título/lista antes do envio).
- **Erros da IA:** (1) leitura estreita do 1º prompt entregou só o G8 — o Paulo pediu
  tudo e o G5 foi feito na sequência; (2) resolvedor de `conditionId` do G5 falhou em
  famílias antigas/série M — corrigido antes da entrega. Nenhum número inventado (todos
  reconferidos contra os CSVs no fim).
- **Decisões escaladas:** **Decisão 12** (G5: tratamento `NaN`-vs-`0` do slot
  pré-primeiro-trade em mercados não capados — dona é a Lia).
- **Tags:** `[PROMPT-CHAVE]` (execução completa do follow-up 4 — reprodutibilidade).

---

## 2026-08-06 — Paulo — FOLLOWUP3 (G7): unificar a base de ajuste dos dois parquets de ETF

**O que foi feito:**
- Respondido o `FOLLOWUP3_Pedido_Paulo_dados.md` (item único G7). O Felipe mediu que
  `etf_open_daily.parquet` e `etf_prices_daily.parquet` estavam em bases de ajuste
  diferentes: a razão abertura/fechamento de **TIP (−1,15%)** e **TLT (−0,41%)** ficava
  num degrau em vez do ruído intradiário dos outros 7. Causa: os dois arquivos saíram de
  pulls em datas diferentes (close 09/jul, open 02/ago) e o `auto_adjust=True` reescala
  toda a história a cada ex-dividendo — TIP e TLT distribuem mensalmente.
- **Conserto:** novo `scripts/g7_reajuste_etfs.py` — um único `yf.download(..., auto_adjust=True)`
  e salva Open e Close a partir do MESMO objeto `raw`. Fonte/universo/janela inalterados
  (yfinance, mesmos 9, período máximo comum); só a base passou a ser compartilhada. Formato
  mantido (dois arquivos irmãos em formato longo).
- **Resultado (ao vivo):** teste do G7 passou — TIP +0,000% e TLT −0,023%, todos os 9 dentro
  de ± 0,1%. Janela esticou de 2003-12-05→2026-07-08 para **2003-12-05→2026-08-06** (+21
  pregões; 51.129→51.318 linhas/arquivo), 0 NaN, mesmas datas nos dois arquivos.
- **Fechamento mudou? SIM, só TIP e TLT** — deslocamento de NÍVEL de toda a história
  (TIP ≈ −1,869%, TLT ≈ −0,791% nas 5.681 datas comuns; os outros 7 = 0,000%). Reportado ao
  Felipe porque as medições dele de `k`/sensibilidade em cima do close de TIP/TLT precisam ser
  refeitas; os outros 7 ficam.
- `data/README.md` atualizado com a data/hora do download de cada arquivo (pedido do Felipe:
  registrar timestamp para comparabilidade) e a nova janela/linhas.
- Entregável: `docs/RESPOSTA_FOLLOWUP3_Pedido_Paulo_dados.md` (bloco `=== G7 ===` + Bloqueios +
  Commit) + cópia em `~/Downloads/`.

**O que quebrou:** nada. `pytest tests/test_etf_prices.py` segue passando (6 passed; o teste não
fixa contagem de linhas nem data final).

**Pendente:** G5 (série de volume, espera spec do Ω da Lia) e G6 (CPI 2022–2024, condicional à
reunião) — inalterados desde o follow-up 2.

**Uso de IA:**
- **Modelo:** Claude Code / Opus 4.8.
- **Contexto consumido:** ~45% da janela.
- **Prompt inicial (verbatim):** "'/Users/paulomello/Downloads/FOLLOWUP3_Pedido_Paulo_dados.md' responda esse follow up 3 e crie uma resposta em md"
- **Iterações até aceitar:** 1 rodada (execução direta; correção de dead-code num ternário do script antes de rodar).
- **Erros da IA:** nenhum de método. Deixei um `if False` residual no comparador e um typo ("fechabelo") no MD — ambos corrigidos antes do commit.
- **Decisões escaladas:** — (nenhuma nova; G7 é re-pull, não decisão metodológica).
- **Tags:** `[PROMPT-CHAVE]` (execução completa do follow-up 3 — reprodutibilidade).

---

## 2026-07-08/09 — Paulo — Organização: separação dos mercados Fed (passo de preparação, NÃO é decisão metodológica)

**O que foi feito:**
- Criado `src/data_pipeline/separar_mercados_fed.py`: separa
  `data/polymarket_fed_probabilities.parquet` (que permanece **intocado**)
  em dois arquivos, por regex sobre o título do mercado:
  - `data/polymarket_fed_reunioes.parquet` — **76 mercados** (16.338 linhas):
    só resultado direto de reunião do FOMC (no change / decrease / increase
    "after [Mês] [Ano] meeting?", incl. variação "Will the Fed …").
  - `data/polymarket_fed_outros.parquet` — **255 mercados** (49.268 linhas):
    todo o resto, guardado para uso futuro (Fed Chair/pessoas: 97;
    dissidência: 42 + 10 combos; sequências multi-reunião: 40; derivative/
    odds: 18; contagem anual de cortes: 15; corte até data: 8; anual/
    emergência: 6; sem categoria: 2) — **incluindo 11 CASOS AMBÍGUOS**
    colocados ali temporariamente, sinalizados no log, aguardando decisão
    humana (ex.: "Fed rate cut by December meeting?", "Will the FED change
    rates to another level after Nov meeting?").
- Log de conferência em `data/log_separacao_mercados.txt` (lista completa
  dos 76 de reuniões, os 11 ambíguos destacados e os 255 outros por categoria).
- Verificação: reunioes + outros = original (65.606 linhas, sem perda);
  original preservado byte a byte.

**Pendente:** revisão humana da lista de "reunioes" e destino dos 11 casos
ambíguos. Tarefas 2/3 seguem pausadas conforme instrução.

**Uso de IA:**
- **Modelo:** Claude Code / Fable 5.
- **Contexto consumido:** ~105k tokens (~10% da janela de 1M, sessão acumulada).
- **Prompt inicial (verbatim):**
  > Contexto: branch "Paulo". Leia CLAUDE.md e Decisoes_pendentes.md antes
  > de começar.
  >
  > PAUSE qualquer trabalho em andamento nas Tarefas 2/3. Esta sessão é
  > só de ORGANIZAÇÃO do dataset já baixado — não baixe dados novos, não
  > delete nada.
  >
  > PROBLEMA: o dataset atual (data/polymarket_fed_probabilities.parquet)
  > mistura mercados de resultado direto de reunião do FOMC com vários
  > outros tipos (nomeação de Fed Chair, dissidência de votos, mercados
  > "derivative", sequências multi-reunião, etc). Para o trabalho atual,
  > só precisamos do núcleo de reunião — mas o resto NÃO deve ser
  > descartado, só guardado separadamente pra uso futuro.
  >
  > TAREFA: 1. Separe o dataset em DOIS arquivos, sem apagar nada do
  > original: a. data/polymarket_fed_reunioes.parquet — SÓ os mercados que
  > são o resultado direto de uma reunião do FOMC [4 padrões + variações];
  > b. data/polymarket_fed_outros.parquet — TODO o resto, mantido intacto,
  > só separado, para uso futuro. O arquivo original permanece intocado.
  > 2. Gere um log em texto simples (data/log_separacao_mercados.txt) com
  > contagens, lista completa de "reunioes" e resumo por categoria de
  > "outros". 3. NÃO decida sozinho casos ambíguos — liste sob "CASOS
  > AMBÍGUOS — decidir depois" (ou coloque temporariamente em "outros" e
  > sinalize claramente).
  >
  > Não altere Decisoes_pendentes.md nem LOG.md de forma definitiva ainda
  > — apenas registre esta ação como um passo de organização/preparação
  > na entrada do LOG.md (não como decisão metodológica fechada). Ao
  > final, me mostre o resumo do item 2 para eu revisar.

  _(Miolo da TAREFA condensado entre colchetes para o LOG; verbatim
  completo no histórico da sessão.)_
- **Iterações até aceitar:** 1 auto-correção (recategorização no log: 11
  mercados "Trump announce nominee for Chair of the Federal Reserve" e
  "Will 1 Fed rate cut happen" caíam em "sem categoria"; corrigido —
  categorias afetam só o log, não a partição dos arquivos). Aguardando
  revisão humana da lista.
- **Erros da IA:** nenhum na partição em si; só a falha de categorização
  descritiva acima, corrigida na sessão.
- **Decisões escaladas:** nenhuma nova registrada em `Decisoes_pendentes.md`
  (instrução explícita de não alterá-lo); os 11 casos ambíguos aguardam
  decisão via log de separação.
- **Tags:** —

## 2026-07-08 — Paulo — Tarefa 2: probabilidades do Polymarket (Fed/FOMC)

**O que foi feito:**
- Criado `src/data_pipeline/download_polymarket_fed.py` (3 etapas, tudo
  cache-first em `cache/` — reexecutar não repete chamadas já salvas):
  - Etapa 1 (descoberta): `/tags` da Gamma API → tag **"Fed Rates"
    (id 100196)** identificado entre 42 candidatos; `/events` paginado
    (closed=true) → 127 eventos, 85 filtrados por título com "fed"/"fomc".
  - Etapa 2 (download): CLOB `/prices-history` com `interval=all` +
    `fidelity=720` (12h), 1 chamada por token Yes, cache por token, delay
    0,2s e retry 3× com backoff.
  - Etapa 3 (consolidação): `data/polymarket_fed_probabilities.parquet`,
    tabela longa `[data, mercado, probabilidade, evento_id]`, eventos em
    ordem cronológica de reunião (proxy: endDate), **65.606 linhas**.
- Documentação em `data/README.md`; testes em `tests/test_polymarket_fed.py`
  (5 testes: 4 passam, 1 xfail documentado — ver overlap abaixo).

**Números pedidos:**
- **Data real de início da cobertura:** primeiro evento **2023-12-06**,
  primeiro ponto de preço **2023-12-07** (último: 2026-06-17). Sem lacunas
  > 6 meses entre eventos consecutivos.
- **Total de eventos:** 85 filtrados (Fed/FOMC), 83 com dados de preço;
  385 mercados percorridos, 331 com histórico (54 vazios).
- **Chamadas de API:** execução final 388; sessão inteira ≈ 765 (365 da
  1ª execução com tag errado — ver "Erros da IA" — e ~12 de sondagem de
  parâmetros do `/prices-history`).

**O que quebrou:**
- A Gamma API ignora `limit>100` em `/tags` e `/events`: a 1ª execução parou
  na 1ª página, escolheu o tag errado ("federal government") e achou só
  1 evento. Corrigido paginando pelo tamanho real do batch até página vazia.
- `interval=max` no `/prices-history` volta vazio para mercados resolvidos
  antigos (290 de 295 vazios na 2ª execução). Corrigido com `interval=all` +
  `fidelity=720` — 12h é a granularidade mais fina que a API gratuita devolve
  para mercados resolvidos (testado: 180/60/10 voltam vazios), confirmando a
  limitação documentada.

**Achados nos dados:**
- **Overlap intrínseco:** mercados de reuniões diferentes do FOMC negociam
  simultaneamente — 82 de 82 pares de eventos consecutivos com overlap de
  datas. O teste "sem overlap" pedido na tarefa está como `xfail` documentado;
  a regra de encadeamento foi escalada (Decisão 9).
- Cobertura do Polymarket (dez/2023→) é ~20 anos mais curta que a série dos
  ETFs (dez/2003→) — escalado como Decisão 8 (afeta a Decisão 3), conforme
  instrução da tarefa.
- 54 mercados com histórico vazio mesmo com os parâmetros corretos (2 eventos
  ficaram sem nenhum dado) — provavelmente mercados de baixíssima atividade.
- Observação: `PAULO_dados.md` descreve o Path B como "proxies de mercado
  tradicional (CME FedWatch)", mas a instrução desta sessão define Path B
  como Gamma+CLOB do Polymarket. Segui a instrução explícita; vale alinhar
  a nomenclatura no time.

**Pendente:**
- Tarefa 3 (dataset unificado): bloqueada pelas Decisões 8 e 9 (janela de
  backtest e regra de overlap/encadeamento) + regra de junção de calendários.
- Decisões 8 e 9 aguardando reunião.

**Uso de IA:**
- **Modelo:** Claude Code / Fable 5.
- **Contexto consumido:** ~75k tokens (~7,5% da janela de 1M).
- **Prompt inicial (verbatim):**
  > Contexto: branch "Paulo", projeto Black-Litterman + Polymarket. Leia
  > PAULO_dados.md e CLAUDE.md antes de começar. Trabalhe SOMENTE dentro
  > deste branch. Siga o ritual de sessão do CLAUDE.md (início: ler
  > Decisoes_pendentes.md e LOG.md; fim: atualizar ambos + bloco "Uso de IA").
  >
  > OBJETIVO: mapear e baixar dados históricos de mercados de decisão do
  > Fed (FOMC) via Polymarket, usando a API gratuita já decidida
  > (Decisão 2 fechada — Path B, Gamma API + CLOB API, sem provedores pagos).
  >
  > [ETAPA 1 — Descoberta: /tags → tag_id Fed Rates com cache em
  > cache/tags.json; /events paginado (closed=true) com cache em
  > cache/fed_events.json; filtro local por "fed"/"fomc"; reportar evento
  > mais antigo, total e lacunas > 6 meses.
  > ETAPA 2 — Download: /prices-history por token com cache em
  > cache/prices_history/, delay 0,2s, retry 3× com backoff.
  > ETAPA 3 — Consolidação: parquet longo [data, mercado, probabilidade,
  > evento_id]; README com data real de início; teste de [0,1] e overlap.
  > RESTRIÇÕES: só pasta de dados e cache/ (+ LOG.md e Decisoes_pendentes.md
  > ao final); não decidir sozinho a reconciliação de cobertura — registrar
  > em Decisoes_pendentes.md; não repetir chamadas já cacheadas.]
  >
  > Ao final, atualize LOG.md com: data real de início da cobertura,
  > total de eventos, número de chamadas de API feitas, e qualquer decisão
  > escalada para Decisoes_pendentes.md.

  _(Trecho entre colchetes condensado do prompt original para o LOG; o
  verbatim completo está no histórico da sessão.)_
- **Iterações até aceitar:** 3 execuções do pipeline até o resultado correto
  (2 rodadas de auto-correção); ainda não revisado pelo humano.
- **Erros da IA:** (1) assumiu que a Gamma API honraria `limit=500` — o teto
  real é 100 e a paginação parou cedo, escolhendo o tag errado e gastando
  365 chamadas de API na execução descartada; (2) assumiu que `interval=max`
  funcionaria para mercados resolvidos — retorna vazio; era preciso
  `interval=all` + `fidelity`. Ambos detectados e corrigidos na sessão.
- **Decisões escaladas:** Decisão 2 registrada como fechada (por instrução
  explícita do humano no prompt); **Decisões 8 e 9 abertas** (reconciliação
  de cobertura; overlap/encadeamento dos mercados FOMC).
- **Tags:** `[PROMPT-CHAVE]`

## 2026-07-08 — Paulo — Tarefa 1: pipeline de preços dos ETFs

**O que foi feito:**
- Criado `src/data_pipeline/download_prices.py`: baixa via yfinance o histórico
  diário de preço ajustado (auto_adjust=True, splits/dividendos incorporados)
  dos 9 tickers da Decisão 1 (fechada): XLK, XLU, XLP, XLF, XLE, XLV, TIP, TLT, SPY.
- Parâmetros (tickers, período, caminho de saída) em `config/data_config.json`
  — `start`/`end` nulos = histórico máximo disponível.
- Validação no console: cobertura por ticker, buracos dentro da cobertura de
  cada ticker, alinhamento de datas na janela comum, NaN.
- Saída: `data/etf_prices_daily.parquet` — tabela única, formato longo,
  colunas `[data, ticker, preco_ajustado]`, 51.129 linhas (5.681 datas × 9 tickers).
- Formato documentado em `data/README.md`.
- Testes em `tests/test_etf_prices.py` (6 testes, todos passando): sem NaN,
  todos os tickers presentes, datas 100% alinhadas entre tickers, intervalo
  de datas esperado (início 2003-12-05, fim ≥ 2026-07-01), preços positivos.
- Criado `.venv` local com yfinance 1.5.1, pandas 3.0.3, pyarrow 24.0.0, pytest.

**Achados nos dados:**
- Nenhum buraco em nenhum ticker (nenhuma data em que um ticker deixou de
  negociar enquanto os outros negociaram, dentro da própria cobertura).
- Históricos com inícios diferentes: SPY desde 1993-01-29, setoriais (XLK,
  XLU, XLP, XLF, XLE, XLV) desde 1998-12-22, TLT desde 2002-07-30,
  **TIP desde 2003-12-05 (é o gargalo)**.
- O dataset salvo foi recortado à janela comum **2003-12-05 → 2026-07-08**
  para garantir datas alinhadas e zero NaN (exigência da tarefa). O histórico
  pré-2003 dos demais tickers foi descartado no arquivo final — o download
  completo continua disponível se o time quiser outra regra.

**O que quebrou:**
- Primeira execução: XLK e XLE voltaram vazios (erro transitório do cache do
  yfinance, "database is locked") e o script salvou um parquet vazio.
  Corrigido: retry individual por ticker (até 3×) e abort sem salvar se
  qualquer ticker ficar vazio ou a janela comum for vazia.

**Observações para o time:**
- O período de backtest não está definido em nenhuma decisão. O arquivo hoje
  cobre 2003→2026 (janela comum), mas o Polymarket/proxies só existem em
  período muito mais curto — a janela efetiva do backtest será definida pela
  Decisão 2. Não registrei nada novo em `Decisoes_pendentes.md` (instrução
  explícita da sessão de não alterá-lo).
- `PAULO_dados.md` está na raiz do repo, não em `Informações_uteis/` como
  referenciado no prompt.

**Pendente:**
- Tarefa 2 (fonte de probabilidades do Polymarket — Decisão 2, aberta):
  aguardando mapeamento dos mercados relevantes do Polymarket.
- Tarefa 3 (dataset unificado de backtest): depende da Tarefa 2.
- Em aberto da Decisão 1: incluir ou não proxy de Brasil (EWZ).

**Uso de IA:**
- **Modelo:** Claude Code / Fable 5.
- **Contexto consumido:** ~45k tokens (~22% da janela).
- **Prompt inicial (verbatim):**
  > Contexto: este é o branch "Paulo" de um projeto de otimização de portfólio
  > Black-Litterman. Leia o arquivo Informações_uteis/PAULO_dados.md para
  > entender minha tarefa completa antes de começar, mas nesta sessão execute
  > SOMENTE a Tarefa 1 descrita abaixo.
  >
  > Trabalhe SOMENTE dentro deste branch. Não altere CLAUDE.md nem
  > Decisoes_pendentes.md além de, ao final, registrar uma entrada em LOG.md
  > resumindo o que foi feito.
  >
  > TAREFA 1 — Pipeline de preços dos ETFs:
  >
  > 1. Criar um script Python (usando yfinance) que baixe o histórico diário
  >    dos 9 ativos já decididos (Decisão 1, fechada): XLK, XLU, XLP, XLF,
  >    XLE, XLV, TIP, TLT, SPY.
  > 2. Usar preço ajustado (adjusted close), já incorporando splits e
  >    dividendos.
  > 3. Validar a série:
  >    - Checar se há datas faltando/buracos em cada ticker
  >    - Checar se as datas estão alinhadas entre os 9 tickers
  >    - Reportar no console quaisquer inconsistências encontradas
  > 4. Salvar o resultado em formato padronizado: parquet, tabela única no
  >    formato longo (colunas: [data, ticker, preço_ajustado]).
  > 5. Documentar o formato do arquivo salvo num README curto dentro da
  >    pasta de dados (nome do arquivo, colunas, período coberto, fonte).
  > 6. Escrever um teste simples que confirme: nenhum ticker com NaN, todas
  >    as datas presentes em todos os tickers, intervalo de datas conforme
  >    esperado.
  >
  > NÃO comece a Tarefa 2 (Polymarket) nem a Tarefa 3 (dataset unificado)
  > nesta sessão — elas ficam para depois que os mercados relevantes do
  > Polymarket forem mapeados.
  >
  > Ao final, atualize LOG.md com: o que foi feito, qualquer problema
  > encontrado nos dados (buracos, tickers com histórico mais curto que
  > os outros, etc.), e o que fica pendente (Tarefa 2, aguardando
  > mapeamento dos mercados do Polymarket).

  (Antes deste, houve um prompt de diagnóstico read-only interrompido pelo
  próprio usuário.)
- **Iterações até aceitar:** 1 rodada de auto-correção (bug do arquivo vazio,
  descrito acima); resultado ainda não revisado pelo humano.
- **Erros da IA:** a 1ª versão do script salvou um parquet vazio quando o
  download de XLK/XLE falhou silenciosamente (validação passou em vácuo).
  Detectado e corrigido na própria sessão.
- **Decisões escaladas:** — (nenhuma nova; observação sobre janela de
  backtest registrada acima, sem alterar `Decisoes_pendentes.md`).
- **Tags:** `[PROMPT-CHAVE]`

---

## Sessão 2026-07-22 — Paulo

**O que foi feito:**
- Mapeamento exploratório de mercados do Polymarket úteis como views para o modelo Black-Litterman.
- Definida estratégia de filtro: mercados recorrentes e gerais (macro, risco de mercado, energia, tech, saúde, câmbio) — não específicos por empresa.
- Gerada lista de 30 mercados candidatos com estimativa de volume médio em USD e mapeamento para os ETFs do portfólio (XLK, XLU, XLP, XLF, XLE, XLV, TIP, TLT, SPY).
- Criado `scripts/explorar_mercados_polymarket.py` para download futuro dos mercados via Gamma API (top 100 por volume).
- Identificado que o acesso à internet está bloqueado no sandbox do Claude Code — download real fica pendente.

**O que quebrou:**
- Sandbox sem acesso à rede: chamadas à Gamma API falharam com `NameResolutionError`. WebFetch também bloqueado (`ECONNREFUSED`).

**Pendente:**
- Download real dos 30 mercados via `scripts/explorar_mercados_polymarket.py` (requer terminal externo ou liberação de rede no Claude Code).
- Definição de quais dos 30 serão efetivamente usados como views (decisão metodológica — Felipe/reunião).
- Tarefas 2 e 3 seguem pausadas.

**Uso de IA:**
- **Modelo:** Claude Code / Sonnet 4.6.
- **Contexto consumido:** ~15k tokens (~7% da janela).
- **Prompt inicial (verbatim):** "quero q vc me ajude a achar 10-15 mercados que vao ser uteis para ajudar nas views dos nossos etfs. me ajude a filtrar isso, nao gaste muitos tokens, como devemos fazer isso?"
- **Iterações até aceitar:** 0 rodadas de correção de código (sessão exploratória, sem implementação).
- **Erros da IA:** volumes estimados são aproximações da base de conhecimento do modelo, não dados reais da API.
- **Decisões escaladas:** — (nenhuma nova em `Decisoes_pendentes.md`).
- **Tags:** —

## Sessão 2026-07-27 — Paulo

**O que foi feito:**
- Criado dashboard estático das reuniões do FOMC (`scripts/gerar_dashboard_reunioes.py`
  → `data/dashboard_reunioes_fed.html`): lista de reuniões por data à esquerda,
  clique exibe o gráfico das probabilidades de cada desfecho ao longo do tempo.
- Confirmada a granularidade dos dados: 1 ponto a cada 12h (00:00 e 12:00 UTC);
  gaps de 24/36/48h são leituras faltantes pontuais.
- Limpeza do repositório (a pedido): mantidos só `polymarket_fed_reunioes.parquet`
  + dashboard + scripts que os geram + pipeline ETF. Removidos cache/,
  intermediários (`probabilities`/`outros`), previews antigas e logs.
- Adicionada coluna `volume` (volume total lifetime por mercado, do Gamma) ao
  pipeline de download e ao `reunioes.parquet`; exibida no dashboard.
- Rede do sandbox voltou a funcionar — re-download real dos dados executado.
- Testadas 3 reuniões antigas (dez/2023, jan/2024, mar/2024), fora do tag
  "Fed Rates"; **removidas a pedido** (baixa qualidade/volume). Extensão da
  descoberta revertida no `download_polymarket_fed.py`.
- Teste `tests/test_polymarket_fed.py` repontado para `reunioes.parquet`
  (colunas + volume não-negativo); 5 passed, 1 xfailed.

**O que quebrou:**
- Leitura do parquet falhava com o Python do anaconda (pyarrow 19); resolvido
  usando o `.venv` (pyarrow 24).

**Pendente:**
- Mercados cumulativos "Fed rate cut by <data>?" (estrutura diferente) seguem
  em aberto — Decisão 10 em `Decisoes_pendentes.md`.

**Uso de IA:**
- **Modelo:** Claude Code / Sonnet 4.6.
- **Contexto consumido:** ~55% da janela.
- **Prompt inicial (verbatim):** "sem gastar muitos tokens, veja as reunioes que eu tenho. eu so quero todas as reunioes do fed. sem falar quantos cuts vao ter e etc... o dashboard deve ser simples. uma lista com DATA de todos os mercados de reuniao e eu aperto em qual quero display. simples. so quero isso"
- **Iterações até aceitar:** ~2 rodadas (dashboard aceito de primeira; reuniões antigas incluídas e depois revertidas).
- **Erros da IA:** exibi "March 2026 vol=$0" numa checagem intermediária por usar `first` em vez da soma — artefato de display, corrigido; nenhum código quebrado.
- **Decisões escaladas:** Decisão 10 (extensão do universo de eventos FOMC).
- **Tags:** —

## Sessão 2026-07-27 (2) — Paulo

**O que foi feito:**
- Criado `data/GUIA_DE_USO.md`: mini-guia em markdown para o grupo carregar/
  consumir os datasets. Cobre ambiente (`.venv`), leitura dos dois parquets
  (`etf_prices_daily`, `polymarket_fed_reunioes`) com snippets de `read_parquet`/
  `pivot`/retornos e filtro por `evento_id`, abertura do dashboard, comandos de
  regeneração do pipeline e regras de convivência (não regenerar em outros
  branches, mudança de esquema só via `Decisoes_pendentes.md`).
- Documentação apenas; nenhuma mudança em código de pipeline ou dados.

**O que quebrou:**
- Nada.

**Pendente:**
- Sem novidades. Decisões 3–9 seguem aguardando reunião; Decisão 10 (mercados
  cumulativos) segue em aberto.

**Uso de IA:**
- **Modelo:** Claude Code / Opus 4.8.
- **Contexto consumido:** ~10% da janela.
- **Prompt inicial (verbatim):** "faca um mini guia em markdown de como as pessoas do grupo devem usar / puxar esses dados"
- **Iterações até aceitar:** 0 rodadas de correção (guia aceito de primeira).
- **Erros da IA:** nenhum.
- **Decisões escaladas:** — (nenhuma nova).
- **Tags:** —

## Sessão 2026-07-29 — Paulo

**O que foi feito:**
- Copiados para o repo (`docs/`) os pedidos recebidos: `Pedido_Paulo_dados.md`
  e `Para_Paulo_e_Lia.md` (commit d614376).
- Executado o `Pedido_Paulo_dados.md` inteiro, medindo ao vivo contra a API do
  Polymarket (VPN necessária — os hosts estavam bloqueados na rede local):
  - `scripts/explorar_clob_bidask.py`: seção 1 (bid/ask). **Achado central: não
    há bid/ask histórico** — `/prices-history` dá série única `{t,p}`;
    `/orderbook-history` vazio; book real-time some na resolução (404); fallback
    = proxy via `data-api /trades` (tem `side`). Escalado como Decisão 11.
  - `scripts/levantar_mercados_pedido.py`: seções 2–4. Mediu os 9 mercados
    (existência, datas, volume do endpoint, resolução, dias sem trade) + Notas
    A/B/C (buckets crus do CPI; rules NBER vs two-pronged; terminal, não one-touch).
  - Fontes externas: FRED via CSV público (sem chave — T10YIE/DGS10/DTB3) e
    Open dos 9 ETFs no yfinance, ambos confirmados.
- Entregável consolidado em `docs/RESPOSTA_Pedido_Paulo_dados.md` (formato da
  seção 4 do pedido), com tudo etiquetado medido vs [DOC] vs pendente. Cópia em
  `~/Downloads/` para envio ao autor do pedido.
- Retornos crus salvos em `data/raw/clob_exploracao/` (entrega física, seção 6).

**O que quebrou:**
- DNS não resolvia os hosts do Polymarket (Claude Code e máquina do Paulo) até
  ligar a VPN. Depois disso, tudo rodou.
- Primeira tentativa do script falhou: mercado resolvido no Gamma exige
  `closed=true` (sem isso, `/markets?slug=` volta vazio) — corrigido.

**Pendente:**
- Decisão 11 (fonte da série do poly: série única vs proxy de `/trades`) —
  aguarda reunião.
- M9 (midterms 2022): `/prices-history` vem vazio (mercado velho) — sem série.
- Pontas da seção 3: sintaxe do contrato ZQ específico (mês/dezembro) no
  yfinance e calendários FOMC/CPI (decisão de fonte).
- Nada commitado ainda nesta sessão (por instrução do Paulo).

**Uso de IA:**
- **Modelo:** Claude Code / Opus 4.8.
- **Contexto consumido:** ~55% da janela.
- **Prompt inicial (verbatim):** "faca um mini guia em markdown de como as pessoas do grupo devem usar / puxar esses dados"
- **Iterações até aceitar:** ~3 rodadas (guia → cópia dos pedidos → execução da
  seção 1 → md consolidado com todas as seções medidas).
- **Erros da IA:** (1) primeira versão da seção 1 ficou documental por eu supor
  sem rede; resolvido rodando de verdade após a VPN. (2) no levantamento, o M9
  pegou por engano os mercados de 2026 (maior volume) em vez do de 2022 —
  corrigido medindo o mercado 2022 específico.
- **Decisões escaladas:** Decisão 11 (não há bid/ask histórico no Polymarket).
- **Tags:** `[PROMPT-CHAVE]` (execução do `Pedido_Paulo_dados.md` — candidato a
  teste de reprodutibilidade).

## Sessão 2026-07-29 (2) — Paulo

**O que foi feito:**
- Executado o `FOLLOWUP_Pedido_Paulo_dados.md` inteiro (F1–F10), medindo ao vivo
  contra a API do Polymarket/yfinance/Fed (VPN ligada):
  - **F1:** push das 7 commits locais da branch `Paulo` (`48cb12e..fe15206`) —
    scripts e `data/raw/` que estavam só na máquina foram para o `origin/Paulo`.
  - **F2/F3/F9:** `scripts/followup_ids_series.py` (+`_extra`) — IDs (conditionId,
    tokenIds Yes/No, slugs) dos 9 mercados + buckets de M1/M3; séries cruas salvas
    (125 arquivos em `data/raw/clob_exploracao/`); contagem de lacunas 12h de
    M2/M5/M6/M8 (todos 0% ausentes).
  - **F4:** `scripts/followup_trades_dim.py` — dimensionamento do `data-api /trades`.
    **Achado central:** limit e offset capados em 10000 → só ~20k trades mais
    recentes; timestamp ignorado; não cobre vida inteira de mercado grande. M4:
    99,8% das janelas 12h têm BUY+SELL (proxy viável na janela). M9/2022 = 0 trades.
  - **F5:** `scripts/followup_live_price.py` — a série do `/prices-history` bate com
    **midpoint** (medido em 2 mercados vivos), não com último trade.
  - **F6:** nenhuma sintaxe de contrato ZQ mensal funciona no yfinance (só `ZQ=F`).
  - **F7:** `scripts/followup_calendars.py` — `data/raw/fomc_dates.csv` (48 linhas,
    2022–2027, raspado do Fed; data exata via PDF do statement) e
    `data/raw/cpi_release_dates.csv` (15 linhas, via rules do Polymarket; BLS deu 403).
  - **F8:** `scripts/followup_cpi_sweep.py` — 17 meses de CPI US (dez/24→jul/26),
    com as mudanças de formato (3→4→5→6→9 buckets; grade sobe em mar/26; jul/26 vira
    buckets de deflação). Séries de bucket salvas com prefixo `CPI_`.
  - **F10:** granularidade em mercado vivo — fina (600s) só nos últimos ~30 dias;
    12h para a vida inteira.
- Entregável: `docs/RESPOSTA_FOLLOWUP_Pedido_Paulo_dados.md` (formato F1–F10 do
  pedido) + cópia em `~/Downloads/` para envio.

**O que quebrou:**
- BLS bloqueia bot (HTTP 403) — datas de CPI vieram das rules dos mercados.
- 1ª passada do F2 pegou mercados errados por busca-por-volume (M5 é slug de
  mercado, não evento; M9 pegou Câmara 2026 em vez do Senado 2022) — corrigido no
  `followup_ids_series_extra.py`.
- 1ª versão do F7 marcou reuniões com "*" como extraordinárias (na verdade é SEP) e
  incluiu o "notation vote" de 22/08/2025 — corrigido.

**Pendente:**
- Decisão 11 atualizada com os fatos medidos (série = midpoint; teto de 20k no
  /trades) — segue aberta, aguarda reunião.
- CPI jan/2025 sem data de release (descrição vazia); CPI abr/2025 não existe como
  evento US separado; typo na fonte do release de dez/2025 (rules dizem "2025").
- ZQ contrato específico e escolha de fonte de calendário: decisão do grupo.

**Uso de IA:**
- **Modelo:** Claude Code / Opus 4.8.
- **Contexto consumido:** ~60% da janela.
- **Prompt inicial (verbatim):** "'/Users/paulomello/Downloads/FOLLOWUP_Pedido_Paulo_dados.md' responda e faca tudo e gere um md para mandar"
- **Iterações até aceitar:** ~3 rodadas internas de correção (F2 mercados errados;
  F7 tipo de reunião + notation vote; F7 parse de CPI).
- **Erros da IA:** (1) busca-por-volume pegou mercados errados no M5/M9 — corrigido;
  (2) rótulo de reunião FOMC ("*"=SEP, não extraordinária) e notation vote — corrigido.
- **Decisões escaladas:** — (nenhuma nova; Decisão 11 atualizada com medições).
- **Tags:** `[PROMPT-CHAVE]` (execução completa do follow-up — reprodutibilidade).

## Sessão 2026-08-02 — Paulo

**O que foi feito:**
- Executado o `FOLLOWUP2_Pedido_Paulo_dados.md` inteiro (G1–G6), ao vivo (VPN
  ligada), com entrega física dos dados:
  - **G1:** `scripts/g1_open_etfs.py` — Open diário (auto_adjust=True) dos 9 ETFs
    entregue como arquivo irmão `data/etf_open_daily.parquet` (coluna
    `preco_abertura`), reindexado às datas EXATAS do close: 51.129 linhas,
    2003-12-05→2026-07-08, **0 Open ausente, alinhamento 100%**. `data/README.md`
    atualizado.
  - **G2:** `scripts/g2_fred.py` — 3 séries do FRED salvas cruas em `data/raw/`
    (`fred_T10YIE.csv` 6.152, `fred_DGS10.csv` 16.848, `fred_DTB3.csv` 18.934).
    **Achado que corrige a nota do Felipe:** o `fredgraph.csv` marca ausente como
    **campo VAZIO**, não `"."` (linha presente, valor vazio).
  - **G3:** `scripts/g3_token_no.py` — token No de M4 e M5. Em ambos **No = 1 − Yes
    exato** (soma 1,000). M5: grelha idêntica ponto a ponto (614/614). M4: mesmos
    slots de 12h, mas timestamp exato só casa em 472/716 (No amostrado em segundos
    diferentes dentro do slot). Séries No salvas cruas (sufixo `_NO`).
  - **G4:** `scripts/g4_cpi_holes.py` — abr/2025 = **lacuna real**; jan/2026 =
    **buraco da busca** (mercado existe: `january-inflation-us-monthly`, 5 buckets,
    série salva); fev/2026 = **lacuna real** (após ~9 buscas). Removidos arquivos
    salvos por engano em matches de ano errado.
  - **G5:** só disponibilidade (espera spec do Ω com a Lia). **Não há endpoint de
    série de volume** (clob/gamma/data-api → 404 ou vazio; só agregados-snapshot no
    Gamma). Derivável do `data-api /trades` (`size`+`timestamp`) mas sob o teto de
    20k trades → incompleto p/ mercado grande.
  - **G6:** não medido (condicional à reunião). Typo de dez/2025: **mantido cru**
    (`2025-01-13`), correção fica com o Felipe no tratamento.
- Entregável: `docs/RESPOSTA_FOLLOWUP2_Pedido_Paulo_dados.md` (formato G1–G6 +
  Bloqueios + Commit) + cópia em `~/Downloads/`.

**O que quebrou:**
- 1ª passada do G4 casou mercados de ano errado (april-us-monthly = 2026;
  february-monthly = 2025) — desambiguado pelas datas da série e corrigido; probe
  manual confirmou fev/2026 inexistente.
- G3 M5 não resolve por `/events` (é slug de MERCADO) — ajustado para `/markets`.

**Pendente:**
- G5: levantar a série de volume de fato depende da spec do Ω (Lia).
- G6: levantar datas de CPI 2022–2024 depende de decisão de reunião.
- Correção do release de dez/2025 (2025-01-13 → 2026-01-13): a cargo do Felipe (tratamento).

**Uso de IA:**
- **Modelo:** Claude Code / Opus 4.8.
- **Contexto consumido:** ~55% da janela.
- **Prompt inicial (verbatim):** "'/Users/paulomello/Downloads/FOLLOWUP2_Pedido_Paulo_dados.md' preciso responder esse md em formato de md para mandar para o felipe. responda absolutamente tudo da forma que ele precisa"
- **Iterações até aceitar:** ~2 rodadas internas (G3 M5 via /markets; G4 desambiguação de ano + probe fev/2026).
- **Erros da IA:** G4 1ª passada rotulou mercados de ano errado como achados —
  detectado pelas datas e corrigido antes da entrega.
- **Decisões escaladas:** — (nenhuma nova).
- **Tags:** `[PROMPT-CHAVE]` (execução completa do follow-up 2 — reprodutibilidade).

## Sessão 2026-08-06 (G9) — Paulo

**O que foi feito:**
- Executado o `PEDIDO_G9_payrolls_Paulo.md` (calendário de payrolls + varredura de
  mercados de payrolls no Polymarket), ao vivo, VPN ligada.
- **G9a (calendário): BLOCKED.** As duas fontes nomeadas falharam: BLS `empsit.htm`
  = **403** (bot-block do servidor, independe de VPN); FRED página
  `fred.stlouisfed.org/release/dates?rid=50` = **000** (Akamai recusa a conexão por
  esta rede, mesmo com VPN); FRED API `api.stlouisfed.org` = alcançável mas exige
  **api_key** (não temos). `api.bls.gov` responde 200 mas só dá **valores** da série,
  não datas de release. **Não fabriquei datas por regra** ("1ª sexta" tem exceções +
  atrasos do shutdown de 2025). Byproduto: 5 datas de release + hora **8:30 AM ET**
  extraídas do texto da regra de mercados do Polymarket (não é o calendário completo).
- **G9b (varredura): POSITIVO.** `scripts/g9b_payrolls_polymarket.py` — 4 termos
  (`payrolls`, `nonfarm`, `jobs report`, `unemployment rate`) no `/public-search`,
  séries cruas via `/prices-history` (fidelity=720). Achado: **existe mercado mensal
  de emprego US de 2025 em diante, em duas famílias multi-bucket** —
  `how-many-jobs-added-in-<mês>` (NFP, 5–8 buckets, análogo direto ao CPI) e
  `<mês>-unemployment-rate` (US, 4–9 buckets, mesmo relatório) — mais binários
  `*-prints-negative` (jun/jul 2025) e meta de release-timing (out/2025, shutdown).
  Grade de buckets **varia de tamanho** ao longo do tempo (como no CPI). Séries
  multi-bucket **alcançam o dia do release** (slot de 12h anterior existe). Cobertura
  janela 2025-01→2026-08: 15 meses com multi-bucket US (2 perturbados pelo shutdown:
  set/nov 2025), 3 só binário/meta (jun/jul/out 2025), lacunas reais abr+mai 2025
  (ago/2026 é o mês corrente, esperado). Filtrei mercados estrangeiros (Japão, México,
  Brasil, UK, Índia, Canadá) que a busca por "unemployment rate" trouxe.
- Artefatos: `data/raw/clob_exploracao/G9_payrolls_*.json` (234 séries cruas),
  `data/raw/payrolls_polymarket_markets.csv` (33 linhas, resumo medido),
  `docs/RESPOSTA_PEDIDO_G9_payrolls_Paulo.md` (formato G9a + G9b + Bloqueios + Commit).

**O que quebrou:**
- 1ª passada do `head -120` matou o script por SIGPIPE (série truncada) — re-rodado com
  redirect a arquivo.
- Atribuição de mês de referência via texto da regra falhava (jan/2025 virou falso
  negativo; mercados estrangeiros contaminavam) — corrigido: mês vem do nome no slug +
  ano inferido da data da série (mesmo padrão de desambiguação do G4), e filtro US-only.

**Addendum (mesma sessão) — G9a DESTRAVADO:**
- O Paulo forneceu uma **FRED API key** gratuita. Criado `scripts/g9a_payrolls_calendar.py`
  (chave lida de `config/secrets.json`, **git-ignored** via novo `.gitignore`; a chave NÃO
  é versionada). Gerado `data/raw/payrolls_release_dates.csv` — 23 datas, dez/2024→nov/2026,
  mesmo cabeçalho do cpi_release_dates.csv. `release_date` medido; `mes_referencia` derivado
  (mês−1) com a ressalva do **shutdown 2025** sinalizada CRU no CSV (gap de 76 dias
  2025-09-05→2025-11-20). Validação cruzada: as 5 datas em comum com as regras dos mercados
  (G9b) batem 100%. Doc G9a atualizado de "bloqueado" para "resolvido".

**Pendente:**
- G9a: só resíduo o remanejo do shutdown 2025 (correção com o Felipe no tratamento).
- Sem relação com G9: G5 (spec do Ω com a Lia) e G6 (reunião) continuam parados.

**Uso de IA:**
- **Modelo:** Claude Code / Opus 4.8.
- **Contexto consumido:** ~40% da janela.
- **Prompt inicial (verbatim):** "'/Users/paulomello/Downloads/PEDIDO_G9_payrolls_Paulo.md' responda isso em um md"
- **Iterações até aceitar:** ~2 rodadas internas (fix do SIGPIPE/head; correção da
  atribuição de mês + filtro US-only e re-run).
- **Erros da IA:** 1ª tabela de cobertura tinha jan/2025 como falso negativo e mercados
  estrangeiros misturados — detectado pelas datas de série e corrigido antes da entrega.
- **Decisões escaladas:** — (nenhuma nova; G9a é bloqueio de acesso a dado, não decisão metodológica).
- **Tags:** `[PROMPT-CHAVE]` (execução completa do G9 — reprodutibilidade).
