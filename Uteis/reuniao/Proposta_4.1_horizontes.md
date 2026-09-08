# Decisão 4.1 — mistura de horizontes: levantamento e proposta

> **Dono: Felipe** (assumido em 2026-07-30). A 4.1 era o único item que travava o backtest
> inteiro e não tinha dono; como sou dono do bridge probabilidade→Q, ela cai naturalmente
> aqui. Isto é **proposta**, não decisão fechada — a escolha do horizonte-alvo e a premissa
> de absorção são do grupo.

## 1. O problema, sem jargão

Cada view devolve um número `Q` que quer dizer "esperamos tanto de retorno". Só que **não é
o mesmo "tanto"**: uma diz *"+2% acumulados em 3 dias"*, outra *"+0,8% no dia do anúncio"*,
outra *"+4% quando o mercado de títulos reprecificar, sem prazo"*. O código empilha as três
na mesma matriz e o Black-Litterman soma. É somar km/h com km: **não dá erro, não trava, só
devolve peso errado.**

## 2. Levantamento — em que horizonte cada view devolve Q hoje

| View | Como o Q é construído | Horizonte real do Q |
|---|---|---|
| **2.2 inflação** | `duration × (E_poly − breakeven)` | **indefinido** — é o repricing TOTAL de quando o gap fechar. Ninguém decidiu em quanto tempo fecha |
| **2.3 Fed** | `surpresa_bps × ΣP·β`, com β de event-study sobre retornos **diários** dos dias de FOMC | **1 dia** (o do anúncio) |
| **B trajetória do Fed** | mesmo β de event-study da 2.3 | **1 dia** |
| **2.4 eleitoral** | `ΣP·β × (p_t − p_{t−k})`, β de absorção plena dos lags 0…k | **k dias acumulados** |
| **3.1 recessão** | idem (template poly-defasado) | **k dias acumulados** |
| **C, E, G** | idem (template poly-defasado) | **k dias acumulados** |

E o quarto participante, que costuma ser esquecido na discussão:

| Insumo | Horizonte |
|---|---|
| **Σ e π** (`bl_optimizer`) | **diários** — Σ é covariância de retorno diário, e `π = δΣw` sai na mesma base |

Ou seja: hoje o BL recebe Q de **três horizontes diferentes** contra um prior de **um quarto**.

## 3. O que já foi feito no código (não decide nada)

- Toda view passou a **declarar** seu horizonte em `diagnostics["horizonte_q_dias"]`
  (`1` para as de evento, `k` para as defasadas, `None` na 2.2, que genuinamente não tem um).
- `bl_integration.stack_views` **recusa empilhar** views de horizontes diferentes, com erro
  citando a 4.1. Antes passava silenciosamente. Isso é o padrão já usado no projeto para o
  favorite-longshot: melhor falhar alto do que rodar com número errado sem ninguém ver.
- **O que a checagem NÃO cobre:** mesmo com todas as views no mesmo horizonte, ele ainda
  precisa bater com o de Σ e π. Só a escolha do horizonte-alvo fecha isso.

## 4. Proposta

**Adotar um horizonte-alvo H único, igual ao intervalo de rebalanceamento, e converter tudo
para ele — inclusive Σ e π.** É a forma padrão: o BL é um modelo de um período, e o período
é o intervalo entre duas decisões de carteira.

Conversões, por tipo de view:

| Tipo | Regra | Precisa de decisão? |
|---|---|---|
| Evento (2.3, B) | o Q já é o movimento de um dia específico. Entra inteiro **se o evento cai dentro do período**; a view fica desativada se não cai | não — é mecânico |
| Defasada com `k ≤ H` (2.4, 3.1, C, E, G) | a absorção termina dentro do período: Q entra inteiro | não |
| Defasada com `k > H` | só parte da absorção acontece no período: `Q × H/k` | **sim** — supõe absorção linear ao longo dos k dias; o perfil de lags medido diz se isso é razoável |
| 2.2 inflação | `Q × H/H_conv`, onde `H_conv` é o prazo de convergência do breakeven | **sim** — `H_conv` não existe hoje |
| Σ, π | `Σ_H = H × Σ_diário` (e π recalculado a partir dele) | não — é a convenção usual |

**Duas perguntas para a reunião, e só duas:**

1. **Qual é H?** (o intervalo de rebalanceamento — diário, semanal, mensal). Ele já precisa
   ser decidido para o backtest existir, então não é decisão nova; é a mesma decisão sendo
   usada em mais um lugar.
2. **Qual é o `H_conv` da 2.2?** Em quantos dias se supõe que o breakeven fecha o gap contra
   o poly. Sem isso a 2.2 não tem como entrar numa carteira multi-view — hoje o Q dela é um
   repricing total sem prazo, o que na prática a faz gritar mais alto que todas as outras.

**Não proponho valor para nenhuma das duas** (regra do projeto: parâmetro numérico vem de
decisão registrada).

## 5. Efeito colateral que a reunião precisa saber

Com H diário e as views defasadas usando `k > 1`, o fator `H/k` **encolhe** o Q das views
defasadas — que são justamente as que dependem da tese de defasagem. Combinado com o perfil
de defasagem medido (`Dump/analises/Perfil_defasagem_k.md`, onde o dado não sustenta a defasagem no
episódio eleitoral), pode ser que a decisão certa não seja "como converter", e sim **quais
views sobrevivem à conversão**. Vale olhar os dois documentos na mesma sessão.
