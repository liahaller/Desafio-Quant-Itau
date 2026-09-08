# Para a Lia — o `diagnostics` está no ar, o rename foi feito, e sobrou UMA pergunta

Oi, Lia. Resposta ao seu retorno de 2026-08-07. Ordem: o que **já está pronto** do seu lado (você
pode começar a calibrar hoje), **uma pergunta** que não dá para eu responder sozinho, e um **fato de
interface** que ninguém tinha escrito em lugar nenhum e muda como você lê um dos campos.

Concordo com os quatro itens da sua resposta. Onde você me corrigiu, você estava certa nas duas vezes.

---

## 1. `diagnostics` implementado — pode calibrar

Está no branch `Felipe`, rodando no dado real. Suíte em **170 testes verdes**.

**Campos que chegam preenchidos**, com os nomes que você pediu:

| Campo | Estado | Onde nasce |
|---|---|---|
| `serie_janela` | ✅ | série **crua**, lista de `(timestamp, {bucket: p})` |
| `n_pontos_janela` | ✅ | slots com leitura |
| `n_slots_esperados_janela` | ✅ | truncado pelo nascimento do mercado (ver abaixo) |
| `janela_slots` | `None` | **de propósito** — a janela é sua (ver 1b) |
| `idade_ultimo_ponto_h` | ✅ | `NaN` se não há ponto na janela, nunca 0 |
| `dp_variacao_janela` | ⚠️ `NaN` em multi-bucket | **é a pergunta do item 2** |
| `dias_ate_evento` | ✅ | pregões até a divulgação |
| `soma_faixas` | ✅ | **cru**, sem virar `\|soma − 1\|` |

Sua regra geral (**desconhecido = `NaN`, nunca 0**) está aplicada em todos.

**Exemplo real, view 2.2 em 2026-06-01:**

```
soma_faixas:               1.013      <- 1,3% de desarranjo do livro
n_pontos_janela:           39
n_slots_esperados_janela:  40         <- 1 buraco real na vida do mercado
idade_ultimo_ponto_h:      0.0
dp_variacao_janela:        nan
serie_janela:              39 pontos, 2026-05-13 -> 2026-06-01, 9 buckets crus
```

**1a. Medido na série CRUA, não na tratada.** Este foi o ponto que quase passou batido e é o motivo de
o campo valer alguma coisa: entre o arquivo e a view rodam o `carry_missing` (D4/6.1) e o
`daily_preopen`. Se eu medisse depois deles, você receberia **zero buraco em todo mercado** e 1 ponto
por dia em vez de 2. O bloco é medido antes dos dois, no passo nativo de 12h.

**1b. `n_slots_esperados` é truncado pelo nascimento do mercado.** Você calcula `esperados − pontos`;
sem o truncamento, um mercado que nasceu há 3 slots numa janela de 20 apareceria com 17 "buracos" e o
seu veto ligaria em cima de mercado íntegro. Agora a diferença é só buraco de leitura de verdade.

**1c. `janela_slots = None` = mando a vida inteira do mercado até a data da decisão.** Não cravei
número: o tamanho da janela é **output da sua calibração de monotonicidade**, e inventar um valor aqui
seria fixar um parâmetro seu dentro do meu módulo. Com a série inteira, você rejanela sem ida e volta
— que é exatamente o argumento com que você pediu `serie_janela` cru.

---

## 2. A pergunta: como colapsar uma PMF multi-bucket no `p`?

Você definiu `dp_variacao_janela` como "desvio-padrão das diferenças `p_t − p_{t−1}`". Em view
binária o `p` é inequívoco e o número sai. **Em mercado multi-bucket não existe um `p`** — a leitura
de um slot é um vetor de 5 a 9 faixas.

**Não escolhi a regra de colapso** (norma L1 entre PMFs consecutivas? probabilidade do bucket modal?
entropia? desvio do valor esperado?) porque é exatamente a mesma classe de transformação que você
pediu para ficar do seu lado quando quis `soma_faixas` cru em vez de `|soma − 1|`. Não vou fixar a
forma funcional de um ingrediente da sua régua dentro do meu módulo.

**Por que não pode ficar só como conversa de corredor:** as **três views ativas do v1 (2.2, 2.3 e B)
são todas multi-bucket**. Se cada lado assumir que o outro preenche esse campo, o `score_estabilidade`
— 1 dos seus 4 ingredientes — fica sem insumo em **todas** as views do v1. Registrei como **decisão
6a** em `Decisoes_pendentes.md` para não cair no vão entre os dois módulos.

**Duas saídas, e a escolha é sua:**

1. **Você calcula do seu lado** a partir de `serie_janela` (a série crua já vai completa; não custa
   dado novo nem ida e volta). O campo `dp_variacao_janela` fica `NaN` de propósito e você ignora.
2. **Você declara a regra** e eu preencho o campo (mantém seu contrato de "escalar pronto", mas fixa a
   forma funcional no meu módulo).

Eu prefiro a **1** — é a que respeita o seu protocolo. Mas se você preferir a 2, é meia hora do meu
lado. **Não bloqueia nada:** o fallback `c = 1` segue valendo enquanto isso.

---

## 3. ⚠️ Fato de interface que muda como você lê o campo (não é decisão)

**A view nunca vê o buraco que o `diagnostics` reporta.** Entre a série crua e o que a view consome
roda o `carry_missing` (decisão D4/6.1): faixa sem leitura **herda a última leitura** e depois
renormaliza. Ou seja, quando `n_slots_esperados − n_pontos = 3`, o modelo **não** rodou com 3 buracos
— ele rodou com 3 leituras carregadas do slot anterior.

Isso não estava escrito em lugar nenhum e muda a semântica: o campo mede **quanta imputação houve**,
não quanto dado faltou ao modelo. Para o seu Ω provavelmente é ainda melhor (imputação é exatamente o
tipo de coisa que deveria custar confiança), mas você precisa saber que é isso que o número é.

---

## 4. O que fiz do que você pediu

- **`omega_fallback(P, sigma, tau, confianca=)` → `incerteza=`.** Você estava certa: o nome dizia o
  oposto do que o número faz, e eu caí na própria armadilha que descrevi na pergunta original.
  Renomeado, com a sua convenção documentada ao lado da minha no docstring. **Entrega na convenção
  daqui** (`c ≥ 1`, maior = menos confiança), como você propôs.
- **Veto = view que sai, não Ω gigante.** Implementado exatamente como você especificou no item 4c:
  `bl_integration.aplicar_veto(view_results, ativa, incerteza)`. View com `ativa=False` vira `None` e
  o `stack_views` (que já filtrava view desativada pela cascata) não a empilha — é o limite exato de
  Ω → ∞, sem número mágico. **A função devolve o `incerteza` já reduzido aos sobreviventes**, porque a
  armadilha ali é o índice: seus dois vetores vêm na ordem das views ATIVAS, e a minha lista tem os
  `None` da cascata intercalados. Casar na mão erra calado.
- **G5 despachado ao Paulo** (`FOLLOWUP4`), com a sua spec transcrita: `notional_usd`, `n_trades`,
  `t_cobertura_min`, passo de 12h, `NaN` nunca `0`. Amarrei o `t_cobertura_min` ao F4 dele (o cap de
  20k que ele mesmo mediu), para o campo parecer necessário em vez de burocrático. Também mandei a
  lista de arquivos dos mercados das views ativas, para ele não ter de adivinhar quais são.

---

## 5. Item 3 (δ e teto): de acordo, e a sua ordem é a certa

Você tem razão em duas coisas e eu retiro o alvo que tinha proposto:

1. **δ = 3,0 é observável, não parâmetro livre** — foi medido no nosso SPY. Não é aí que a briga está.
2. **O alvo é o teto de alavancagem**, e fechar o teto antes de o `c` entrar é calibrar remendo contra
   buraco que vai mudar de tamanho.

O seu argumento fecha com o que o backtest mostrou: como a sua régua **só tira peso** (`c ≥ 1`), o
tilt encolhe quando o `c` entra, a carteira volta na direção do `w_mkt` — e é justamente a perna de
mercado que o teto está cortando junto hoje. **Aceito a ordem que você propôs:** entra o `c` → mede-se
Σ|w| de novo → só então se decide se ainda precisa de teto e se ele corta a carteira toda ou só o
tilt. Levo assim para a reunião.

---

## 6. Estado do backtest, para você dimensionar

Re-rodei hoje no dado corrigido do Paulo (G7): **374 pregões**, 2025-02-10 a 2026-08-06.

- **Ainda roda com UMA view** (2.2). A 2.3 espera o `DFF` (G8, que o Paulo pulou e eu re-pedi); a B
  precisa do ZQ de dezembro, que não tem fonte grátis e não está pedido a ninguém.
- Com teto Σ|w| ≤ 1: **+15,7% líquido contra +30,1% do benchmark** (comprar e segurar SPY). A
  carteira perde em toda a varredura de teto, e a distância cresce conforme o teto afrouxa.
- **Σ|w| sem teto vai à ruína**: mediana 24, máximo 264. É daí que vem a decisão 10 — e é isso que o
  seu `c` deve encolher.

**O que isso quer dizer para você:** um `c` de três ingredientes calibrados vale mais agora do que um
de quatro daqui a duas semanas, exatamente como você escreveu. Se o G5 do Paulo demorar, **manda o
`c` sem o portão de volume** — a estrutura é multiplicativa, o portão entra depois sem mudar
interface, e `omega_fallback` aceita o vetor como está hoje.

---

## Encaixe, para não haver dúvida de formato

```python
# src/market_inputs.py
omega_fallback(P, sigma, tau, incerteza=None)   # incerteza: (k,) float, >= 1

# src/bl_integration.py
aplicar_veto(view_results, ativa, incerteza)    # -> (view_results, incerteza) alinhados
```

`incerteza=None` devolve `diag(P·τΣ·Pᵀ)` puro — He-Litterman, o teto de confiança. É o que roda hoje.
