# Resposta da Lia — decisão 6a (colapso PMF→p), interface e dimensionamento

Resposta ao seu retorno de 2026-08-07 ("o `diagnostics` está no ar"). Ordem: a **decisão 6a**, um
**pedido de interface** que evita uma classe de erro silencioso, as **confirmações** (com uma
verificação para você fazer), e o que o item 6 muda no meu dimensionamento.

---

## 1. Decisão 6a: o colapso fica do meu lado, com grade de duas candidatas

**Saída 1**, como você preferiu. `dp_variacao_janela` fica `NaN` de propósito — **não preencha**.
Derivo tudo da `serie_janela`. O motivo é o que você já identificou (é a mesma classe de
transformação do `soma_faixas`), mais um: a regra de colapso é **candidata à calibração**, então se
ela morasse no seu módulo, cada forma testada viraria uma ida e volta.

**⚠️ O ponto que decide a regra: renormalizar antes de colapsar.**

As PMFs cruas não somam 1 — é o seu próprio achado (92,3%–132,5% no mercado de cortes do Fed). Se
o colapso rodar sobre a PMF crua, ele mistura **movimento de opinião** com **desarranjo do livro**.
Como a minha régua é multiplicativa, `score_estabilidade` e `score_coerencia` passariam a punir a
mesma coisa duas vezes, e nenhum teste de monotonicidade detectaria isso (os dois ingredientes
subiriam e desceriam juntos, parecendo confirmação mútua).

Então: **renormalizo (`p_b / Σ_b p_b`) antes de colapsar**, e o desarranjo fica inteiramente com o
`soma_faixas`. É por isso que eu precisava dos dois campos crus juntos — não era preciosismo de
formato, era separar dois sinais que o dado cru entrega grudados.

**As duas candidatas** (ambas sobre a PMF renormalizada, ambas no protocolo de monotonicidade dos
outros ingredientes):

| # | Regra | Por que está na grade |
|---|---|---|
| **a** | Variação total entre PMFs consecutivas: `0,5 · Σ_b \|p_{t,b} − p_{t−1,b}\|` | Sem parâmetro livre; ∈ [0,1] com leitura direta ("fração da massa que se moveu"); e **degenera exatamente na minha definição original quando há 2 buckets** — o caso binário continua sendo o mesmo número de antes |
| **b** | Desvio-padrão das diferenças do valor esperado `E_t = Σ_b p_b·x_b` | Mede movimento na grandeza que o `Q` de fato consome, não na PMF inteira |

Quem escolhe é o teste de monotonicidade; empate resolve pela forma com menos parâmetros (= **a**).

**Ressalva sobre a candidata b, para a ata:** ela herda o **balde aberto** (ponto médio extrapolado,
meia largura da grade — decisão provisória da maratona de 04/08). Se **b** vencer, o ingrediente
fica condicionado a uma decisão que o grupo ainda vai revisar, e a revisão obriga a recalibrar. A
candidata **a** não tem essa dependência. Isso não a desclassifica; só precisa estar escrito antes,
não depois.

**Detalhe de implementação do meu lado** (escrevo só para o número ser auditável): uso apenas
**pares adjacentes** (Δt = 1 slot de 12h). Com buraco na série, a diferença consecutiva compararia
pontos separados por 24h ou mais e inflaria a variação. Não normalizo pela distância temporal —
isso embutiria premissa de passeio aleatório, e o buraco já custa confiança por outro caminho
(`n_slots_esperados − n_pontos`). Registro o nº de pares usados junto do score.

---

## 2. Pedido de interface: chave por nome, não por posição

Você escreveu "casar na mão erra calado" — é exatamente o risco que sobra na `aplicar_veto`. Ela
recebe `ativa` e `incerteza` como **vetores posicionais** na ordem das views ativas, e a sua lista
tem os `None` da cascata intercalados. Enquanto o alinhamento for posicional, existe uma classe de
erro que nenhum de nós vê: um deslocamento de índice não levanta exceção, produz carteira
plausível e errada.

**Proposta:** eu entrego dicts chaveados pelo identificador da view —

```python
c      : dict[str, float]   # {'2.2': 1.8, '2.3': 3.1, 'B': 1.2}
ativa  : dict[str, bool]
```

— e a `aplicar_veto` monta o vetor na ordem dela. Custo do meu lado: zero (é como eu produzo o
número de qualquer forma). Do seu: uma linha, e a classe de erro some.

Se preferir manter vetores, então que a função receba também a lista de nomes e **valide** contra a
ordem interna. Módulo seu, decisão sua — só não deixe posicional sem validação, porque esse é
justamente o erro que passa no teste verde.

---

## 3. Confirmações — e uma verificação para você fazer

- **1a (medir na série crua, antes do `carry_missing` e do `daily_preopen`):** certo, e é o que
  torna o campo utilizável. Medido depois, `n_slots_esperados − n_pontos` seria zero em todo
  mercado e o ingrediente de qualidade não existiria.
- **1b (truncar pelo nascimento do mercado):** certo. Sem isso o veto ligaria em cima de mercado
  íntegro, só recém-nascido.
- **1c (`janela_slots = None`, vida inteira até a data):** é o contrato que eu queria.

**⚠️ Verificação, não acusação:** no seu exemplo, `idade_ultimo_ponto_h = 0.0` na data da decisão.
Confirme que o último ponto da `serie_janela` é o último slot **fechado antes** do timestamp de
decisão, e não o slot que **contém** esse timestamp. Se for o segundo caso, o ponto pode carregar
preço formado depois do horário de execução — lookahead de meio slot, pequeno demais para aparecer
no retorno e grande o bastante para inflar artificialmente a estabilidade medida (a série "acerta"
o próprio futuro imediato). Se já for o slot fechado, ignore.

**Item 3 (o campo mede imputação, não falta de dado ao modelo):** entendido, e para o Ω essa é a
leitura mais útil das duas. Muda o nome do que eu meço: não é "quanto dado faltou", é **"quanto do
que o modelo leu foi carregado do slot anterior"** — imputação é exatamente o tipo de coisa que
deve custar confiança. Vou descrever assim no relatório, e obrigada por escrever isso; não estava
em lugar nenhum e eu teria lido o campo errado.

---

## 4. Item 6: o que muda no meu dimensionamento com **uma** view ativa

Com k = 1, o `c` deixa de ser confiança *relativa entre views* e vira **controle do tamanho da
aposta no tempo**. Três consequências:

1. **A calibração continua rodando.** O teste de monotonicidade é sobre **slots no tempo**, não
   entre views — a amostra é a vida da 2.2, não o número de views. O protocolo não muda.
2. **A comparação entre views fica sem amostra.** O que eu não consigo validar com uma view só é se
   a régua ordena bem *entre* mercados diferentes. Se a 2.3 destravar com o `DFF`, recalibro com as
   duas e essa parte passa a ter teste.
3. **Com k = 1, `c` e teto de alavancagem são literalmente a mesma alavanca.** Isso reforça a ordem
   que combinamos: cravar o teto agora seria cravar duas vezes o mesmo número, e a segunda vez
   desfazendo a primeira.

**E uma honestidade sobre o número, para a reunião não ler errado:** +15,7% contra +30,1%. Como o
meu `c` só encolhe o tilt (`c ≥ 1`), ele **vai melhorar** esse resultado — mas **por subtração**: no
limite `c → ∞` a carteira vira o próprio benchmark. O Ω não conserta view que não agrega; ele
impede que ela machuque. Se depois de o `c` entrar a carteira ainda perder do SPY, o problema está
na 2.2 (ou no fato de rodarmos com uma view só), **não** no dimensionamento de risco — e é melhor
isso estar escrito antes de o resultado aparecer do que depois.

---

## 5. O que eu entrego, e em que ordem

1. Colapso PMF→p implementado (duas candidatas) sobre a `serie_janela`.
2. Teste de monotonicidade nos ingredientes que já têm dado: **estabilidade, proximidade,
   coerência**. Sem portão de volume enquanto o G5 não chega — a estrutura é multiplicativa, o
   portão entra depois sem tocar na interface.
3. Entrega: `c` + `ativa` (dicts por view, convenção daqui: `c ≥ 1`, maior = menos confiança).

Até lá, `incerteza=None` segue valendo e o backtest não para.
