# FOLLOW-UP 4 — `G8` (o item que ficou pra trás) e `G5` (destravado pela Lia)

> **Para o Claude do Paulo:** dois itens, **os dois já existiam** — nenhum é pedido novo. Não muda
> fonte, não muda universo de ativos, não abre view nova. O `G8` é a segunda metade do follow-up 3,
> que não veio; o `G5` estava parado esperando a spec da Lia, e **a spec chegou**.
>
> Regras de sempre: **você levanta e reporta, não decide nada**; campo não medido vai como `?`;
> dado cru não se normaliza. **Push com hash** no fim.

---

## Antes: o que chegou está conferido

- **G7 — conferido número por número, e passou.** Não confiei no relatório: extraí os dois parquets
  de `origin/Paulo` e o close antigo (`87721ae~1`) e refiz as medições. Bate tudo, exato: mediana
  `abertura/fechamento − 1` de **TIP +0,0000%** e **TLT −0,0230%** (nenhum ticker fora de ± 0,1%),
  `close novo/antigo` de **TIP −1,8692%** e **TLT −0,7914%**, os outros sete **0,0000% em todas as
  5.681 datas comuns**, grid `2003-12-05 → 2026-08-06` com 5.702 datas, 0 NaN e `open.index ==
  close.index`. O alfa fabricado de +1,15%/dia no TIP sumiu. **G7 fechado.**

- **E o custo que você me avisou é praticamente zero — medi.** Você marcou que eu teria de refazer
  as medições de `k`/sensibilidade porque o nível de TIP/TLT desceu. Medi a diferença nos
  **retornos** close-a-close, que é o que essas medições usam: média de |Δ| de **0,024 bps (TIP)** e
  **0,011 bps (TLT)**, correlação novo × antigo de **0,9992** e **0,99998**. O deslocamento é fator
  multiplicativo constante em todos os 5.680 dias **menos um**: **2026-06-01**, onde o retorno do TIP
  muda 115 bps e o do TLT 39 bps (é o ex-dividendo que entrou no pull novo — o arquivo antigo é que
  estava errado nesse dia). **Não preciso refazer nada.** Anota isso como resultado do G7: o conserto
  saiu de graça.

- **G9 — aceito, e o resíduo do shutdown é meu mesmo.** Você fez certo: marcou cru e não corrigiu. O
  remap fica comigo (`2025-11-20` é o release de **setembro/2025**, não de outubro; **outubro não tem
  release próprio** — o número saiu dentro do release combinado de `2025-12-16`). O seu próprio dado
  do G9b confirma sozinho: out/2025 é o único mês com "só meta" e **nenhum mercado do número**.
  **Já está tratado e rodando** (`src/poly_loader.py::load_payroll_releases`): a tática de prêmio saiu
  de **19 para 32 eventos** (7 FOMC + 13 CPI + 12 payrolls) e o efeito segurou — a diferença
  incerto−previsível ficou em +1,099% com t de Welch subindo de +2,10 para **+2,27**. **O G9 valeu:**
  era o que você levantou que virou o dobro de amostra.

---

## G8 — `DFF` do FRED (não veio, e não foi declarado)

O `FOLLOWUP3` tinha **dois** itens. A resposta cobriu só o G7:

- não tem o bloco `=== G8 — DFF ===`;
- `data/raw/fred_DFF.csv` **não existe** em `origin/Paulo` (só `DGS10`, `DTB3`, `T10YIE`);
- o commit se chama literalmente `followup3 (G7): ...`, e **depois dele vieram dois commits de G9** —
  então não foi sessão que acabou no meio.

**O ponto de processo, uma vez só e sigo em frente:** o `## Bloqueios` da resposta diz **"Nenhum"**.
Item não entregue tem de aparecer — como `?`, como bloqueio, como "não deu tempo", tanto faz. A regra
do `?` honesto existe exatamente para isso: **o silêncio é pior que o `?`**, porque eu só descobri
cruzando a árvore do git. Não é cobrança de esforço, é de sinalização.

**Por que importa:** o `DFF` é o outro lado da subtração `e_ff_bps = DTB3 − DFF`. Sem ele a **view 2.3
não roda**, e o backtest continua rodando com **uma view só** (a 2.2). É o item de maior impacto na
entrega e o mais barato da lista — é o mesmo `fredgraph.csv` que você já fez três vezes no G2, com um
ID a mais.

```
https://fred.stlouisfed.org/graph/fredgraph.csv?id=DFF
```

Mesmo formato dos outros três (`observation_date,DFF`), **cru**, sem preencher buraco nem converter
unidade, salvo em `data/raw/fred_DFF.csv`.

**O que reportar** — o mesmo bloco do G2:

```
=== G8 — DFF ===
linhas:         <n>
primeira data:  <YYYY-MM-DD>
última data:    <YYYY-MM-DD>
campos vazios:  <n>
```

*(O opcional do Nasdaq Data Link com teto de 15 min continua opcional. Se não sobrar tempo, `?` e
pronto — o caminho do FRED resolve.)*

---

## G5 — série de volume no tempo ✅ a spec da Lia chegou

Você deixou o G5 parado pelo motivo certo (dependência de processo, não falha técnica) e levantou a
disponibilidade dos endpoints no follow-up 2. **A Lia respondeu e a spec abaixo é dela**, não minha —
transcrevo para você não ter de ler a thread inteira.

**O total lifetime não serve.** Dois motivos dela, e o primeiro é fatal: (1) é **lookahead** — o total
inclui volume que só ocorreu *depois* da data da decisão, então num backtest o veto ligaria usando
informação do futuro; (2) é **constante no tempo**, e um Ω que não varia deixa de ser reativo.

Então é **série**, derivada do `/trades` como você mesmo apontou no G5 do follow-up 2 (somando por
bucket). Três campos por slot:

| Campo | Definição |
|---|---|
| `notional_usd` | Σ (`size` × `price`) dos trades no slot |
| `n_trades` | contagem de trades no slot |
| `t_cobertura_min` | timestamp do trade **mais antigo alcançado** dentro do cap de 20k — **um por mercado**, não por slot |

- **Passo: 12h**, o passo nativo do histórico (o mesmo do `prices-history` com `fidelity=720`).
  Agregar depois é trivial; desagregar é impossível — por isso o passo fino.
- **Notional *e* contagem**, no mesmo varrimento — custo marginal zero. Medem coisas diferentes: um
  único trade grande infla o notional de um mercado onde não tem gente negociando. Qual dos dois entra
  no portão sai do teste de monotonicidade dela, então **não escolha um**: entregue os dois.
- **⚠️ `t_cobertura_min` é obrigatório, e é a parte que mais importa.** Antes desse timestamp, volume é
  **`NaN`, nunca `0`**. É consequência direta do seu achado do F4 (o `/trades` só alcança os ~20.000
  mais recentes): sem esse campo, o truncamento do cap vira "volume zero" exatamente nos mercados
  **mais** líquidos, e o veto da Lia ligaria ao contrário do que deveria. `NaN` não veta — propaga como
  "sem dado", e o tratamento fica do lado dela.

**Escopo: só os mercados das views ativas (2.2, 2.3, B).** Não vale gastar sessão levantando mercado de
view desativada; se uma view voltar, eu peço o mercado dela na hora. Os arquivos, para você não ter de
adivinhar — são todos os que já estão em `data/raw/clob_exploracao/`:

| View | Mercados |
|---|---|
| **2.2** inflação | as famílias `CPI_*-inflation-*-monthly` (todos os meses que você já baixou) e `M1_cpi_monthly_*` |
| **2.3** Fed (reunião) | `M2_fomc_*` |
| **B** trajetória do Fed | `M3_fed_trajectory_*` (as 9 faixas de cortes em 2025) |

São mercados **médios**, não o M5. Pelo seu F4, 99,8% das janelas de 12h do M4 têm trade — ou seja,
dentro da cobertura do `/trades`. Se algum destes estourar o cap de 20k, é exatamente o caso que o
`t_cobertura_min` existe para marcar: **reporte e siga**, não tente contornar.

**O que reportar:**

```
=== G5 — VOLUME NO TEMPO ===
Arquivo salvo:        <caminho>
Colunas:              <nomes exatos do cabeçalho>
Nº de linhas:         <n>
Nº de mercados:       <n>  (lista)
Passo:                <12h?>
Janela:               <primeiro slot> → <último slot>
Mercados que bateram no cap de 20k:  <lista, com o t_cobertura_min de cada um>
Slots sem trade:      <n>  (volume 0 legítimo, DEPOIS do t_cobertura_min — distinguir de NaN)
```

O último campo é o que separa as duas coisas que não podem se misturar: **`0` = teve slot e ninguém
negociou; `NaN` = o slot está antes do alcance do `/trades`.**

---

## Sem ação sua: uma correção de reporte no G9b (o dado está certo)

Não precisa fazer nada — é só para o número não circular errado. No G9b você reportou:

```
march-unemployment-rate-561 (2026):  série 2026-02-14 → 2026-03-28
```

Li o arquivo: a série vai até **2026-04-03**, não 03-28. E 2026-04-03 é exatamente a data de release
de março/2026 no seu próprio G9a. **O dado que você entregou está correto** — foi a data no
entregável que saiu errada.

Isso importa porque restaura um padrão que vale para **todos** os mercados resolvidos da sua
varredura: a série termina exatamente no dia do release. Sem exceção. Usei esse padrão como chave de
casamento mercado→release (em vez do nome do mês do slug, que não distingue ano), e é ele que resolve
sozinho a ambiguidade de dez/2024 vs dez/2025 que você sinalizou.

---

## O que continua parado (sem ação sua)

- **G6 (CPI 2022–2024):** segue condicional à reunião. Sem mudança.

---

## Formato da devolução

Os blocos `=== G8 — DFF ===` e `=== G5 — VOLUME NO TEMPO ===` preenchidos, e:

```
## Bloqueios
<o que não deu, com o motivo — e item não entregue entra AQUI, não some>

## Commit
<hash + branch do push>
```

E como sempre: **um `?` honesto é útil; um número inventado contamina uma decisão metodológica.**
