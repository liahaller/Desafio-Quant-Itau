# Resposta da Lia — Ω: volume, `diagnostics`, δ e a régua


Resposta a `Dump/trocas/Pergunta_Lia_omega_volume.md` (Felipe). Na mesma ordem.


---


## 1. Volume: série no tempo, passo de 12h, só os mercados das views ativas ✅ destrava o G5


**O total lifetime não serve.** Dois motivos, e o primeiro é fatal:


1. **É lookahead.** O total inclui volume que só ocorreu *depois* da data da decisão. Num
   backtest, o veto ligaria ou desligaria usando informação do futuro — o mercado que hoje
   parece líquido pode ter feito todo o volume dele no mês seguinte ao rebalanceamento.
2. **É constante no tempo.** Um Ω que não varia deixa de ser reativo; o portão viraria filtro
   estático de universo ("esse mercado entra ou não entra"), que é outra decisão, do grupo,
   e não precisa de mim.


**O que peço ao Paulo:**


| Campo | Definição |
|---|---|
| `notional_usd` | Σ (`size` × `price`) dos trades no slot |
| `n_trades` | contagem de trades no slot |
| `t_cobertura_min` | timestamp do trade **mais antigo alcançado** dentro do cap de 20k (um por mercado) |


- **Passo: 12h**, o passo nativo do histórico. Agregar depois é trivial; desagregar é
  impossível. O passo de 12h não me limita: o rebalanceamento é diário (H = 1) e a janela da
  estabilidade é calibrada em slots, não em dias.
- **Notional *e* contagem**, no mesmo varrimento do `/trades` — custo marginal zero. Os dois
  porque medem coisas diferentes: notional é a grandeza econômica, mas um único trade grande
  infla o notional de um mercado que não tem gente negociando. Qual dos dois entra no portão
  sai do teste de monotonicidade — por isso não escolho agora.
- **⚠️ `t_cobertura_min` é obrigatório.** Antes desse timestamp, volume = **NaN, nunca 0**. Sem
  esse campo o truncamento do cap de 20k vira "volume zero" exatamente nos mercados *mais*
  líquidos, e o veto liga ao contrário do que deveria. NaN não veta — propaga como "sem dado",
  e o tratamento fica do meu lado.
- **Escopo: só os mercados das views ativas (2.2, 2.3, B).** São mercados médios; pelo F4 dele,
  99,8% das janelas de 12h do M4 têm trade, ou seja, dentro da cobertura do `/trades`. Se uma
  view voltar ao ar, peço o mercado dela na hora — não vale gastar sessão do Paulo levantando
  mercado de view desativada.


---


## 2. `diagnostics`: pode fechar, com estes campos


Regra geral que vale para todos: **campo desconhecido = NaN, nunca 0.** Zero é valor
informativo na minha régua (zera o produto).


**Qualidade da leitura**


| Campo | Tipo | Definição |
|---|---|---|
| `serie_janela` | lista de `(timestamp, p)` | a série lida na janela, crua |
| `n_pontos_janela` | int | observações efetivas |
| `n_slots_esperados_janela` | int | slots que *deveriam* existir na janela (buraco = esperados − pontos, sem eu inferir calendário) |
| `janela_slots` | int | tamanho nominal da janela usada nos escalares |
| `idade_ultimo_ponto_h` | float | horas entre o último ponto e o timestamp da decisão |
| `dp_variacao_janela` | float | desvio-padrão das **diferenças** `p_t − p_{t−1}` na janela, escala 0–1 |


Dois pontos de atenção: `dp_variacao_janela` é dispersão das *diferenças*, não do nível — é o
que `score_estabilidade` consome. E a `serie_janela` crua não é redundante com os escalares: a
janela é output da minha calibração de monotonicidade, e um escalar com janela fixa do seu lado
congela um parâmetro que é meu. Com a série, mudar a janela não custa uma ida e volta.


**Proximidade de evento**


| Campo | Tipo | Definição |
|---|---|---|
| `dias_ate_evento` | float | dias entre a decisão e o evento agendado da view (NaN se não houver data) |


`horizonte_q_dias` não substitui: horizonte da view e distância até o evento são coisas
diferentes, e o decaimento de proximidade precisa da segunda.


**Coerência do mercado** (o seu achado — ver o fim)


| Campo | Tipo | Definição |
|---|---|---|
| `soma_faixas` | float | soma das probabilidades das faixas no slot (NaN em view binária) |


Quero o **cru**, não o desvio. Eu calculo `|soma − 1|`; assim a forma funcional fica do meu
lado e você não fixa transformação minha.


**Volume** (quando o G5 chegar): `volume_usd_janela`, `n_trades_janela`, `cobertura_ok` (bool:
a janela inteira está depois de `t_cobertura_min`).


---


## 3. δ: de acordo em fechar junto — mas o alvo não é o δ, é o teto


De acordo com o princípio: dimensionamento de risco fecha numa conversa só. Uma correção de
alvo, porém — **δ = 3,0 foi medido no nosso SPY, então não é parâmetro livre, é observável.**
Não é aí que a briga está.


O que precisa fechar na mesma conversa que a escala do `c` é o **teto de alavancagem** (sua
decisão 10). Motivo: hoje o teto está fazendo o trabalho do Ω. Com `c = 1` toda view é confiada
tanto quanto o prior, a exposição ativa explode (Σ|w| mediana 24, máx 264) e o teto corta a
carteira inteira — inclusive a perna de mercado, que é justamente a explicação que você mesmo
levanta para a carteira perder do comprar-e-segurar SPY.


Como a minha régua **só tira peso** (ver item 4), parte dessa alavancagem cai por construção
quando o `c` entrar. Por isso proponho esta ordem na reunião:


1. entra o `c`;
2. mede-se Σ|w| de novo;
3. só então se decide se ainda é preciso teto — e, se for, se ele corta a carteira toda ou só
   o tilt da view.


Fechar o teto antes de o `c` entrar é calibrar um remendo contra um buraco que vai mudar de
tamanho.


---


## 4. A régua: de acordo — e não é mudança para mim


A âncora `diag(P·τΣ·Pᵀ)` é a mesma que registrei em 08/07 (`Omega_ii = diag(P·τΣ·Pᵀ)_ii / c`).
O argumento do τ se cancelar está certo e é bem-vindo. Quatro notas operacionais:


**a) ⚠️ A convenção está invertida entre nós.** Eu registrei `c ∈ (0,1]`, *maior = mais
confiança*; você usa `c_i > 1` = *menos* confiança. Mesma matemática (`c_seu = 1/c_meu`), nomes
opostos. **Entrego na sua convenção.** Sugestão para o seu lado: renomear o argumento de
`omega_fallback` de `confianca` para `incerteza` (ou `mult_incerteza`) — o nome atual diz o
contrário do que o número faz, e é exatamente a armadilha que você descreve ("as duas parecem
iguais e dão carteiras diferentes"). Módulo seu, decisão sua.


**b) `c_i ≥ 1` sempre.** A régua é produto de fatores em (0,1] na convenção de confiança; na
sua, isso vira `c_i ≥ 1`, com 1 = mercado perfeito. Ou seja: **o seu fallback He-Litterman é o
teto de confiança, e o meu módulo só tira peso, nunca adiciona.** É conservador de propósito —
conte com isso ao dimensionar o item 3.


**c) Veto não é `c` grande, é view que sai.** Entrego dois vetores na ordem das views ativas:


```
c      : (k,) float  — multiplicador de incerteza, na sua convenção
ativa  : (k,) bool   — False = view vetada por liquidez
```


View com `ativa=False` sai de `P` e `Q` antes do otimizador. É o limite exato de Ω → ∞, sem
número mágico no modelo; um teto tipo `1e4` deixaria resíduo da view vetada e introduziria um
parâmetro inventado.


**d) Escala: nunca esteve em absoluta.** O `lia/calibracao_omega.py` produz *scores* sem
normalização, de propósito — o teste de monotonicidade é invariante a transformação monótona,
só a ordem importa. A normalização para `c` fecha junto com o item 3.


---


## Achado das faixas que não somam 100%: entra como candidato


Concordo que é o melhor tipo de sinal para o meu módulo — mede desarranjo do livro diretamente,
existe slot a slot e não custa dado novo. Entra na grade de calibração como quarto ingrediente
candidato:


```
score_coerencia = −|soma_faixas − 1|
```


Entra na fórmula final **se passar o teste de monotonicidade**, como os outros três — não abro
exceção ao protocolo nem para achado bom. É esse o pedido de `soma_faixas` no item 2.


---


## O que trava o quê


- **Paulo: destravado agora.** A spec do item 1 é suficiente para ele levantar.
- **`diagnostics`: pode implementar já** — não depende de mais ninguém.
- **`c_i` real depende do G5.** Sem volume, a calibração roda com 3 dos 4 ingredientes.
- **Se o G5 atrasar, entrego o `c` sem o portão.** A estrutura é multiplicativa, então o portão
  de volume entra depois **sem mudar a interface** — é só mais um fator. Melhor um `c` de três
  ingredientes calibrados do que `c = 1` em tudo.
- Até lá, o fallback `c = 1` segue valendo e o backtest não para.