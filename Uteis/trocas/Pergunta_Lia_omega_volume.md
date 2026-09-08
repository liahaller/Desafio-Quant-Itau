# Para a Lia — três perguntas sobre o Ω, e uma régua de interface (uma das perguntas está travando o Paulo)

Oi, Lia. Três coisas curtas, em ordem de urgência — e no fim uma quarta que **não é pergunta**:
é a forma em que o Ω precisa chegar do meu lado, que mudou com o fechamento do τ.

## 1. Volume: o pedido ao Paulo está parado esperando você ⏳

Na segunda entrega o Paulo trouxe **volume total (lifetime) por mercado** — um número só por
mercado, constante no tempo. Pelo protocolo que você registrou em 08/07 (confiança
multiplicativa com volume como veto), me parece que o Ω precisa de volume **variando no
tempo**, não de um total. Mas quem especifica o Ω é você, então **não pedi**: escrevi no
follow-up (item G5) que ele deve alinhar com você antes de medir, para não levantar a série
errada duas vezes.

**O que eu preciso saber para destravar:** o Ω usa volume **por dia** (ou por 12h), volume
**acumulado até a data**, ou o **total do mercado** já serve? Se for série temporal, ele
mede a disponibilidade e levanta; se o total basta, o G5 sai da lista e ele ganha uma sessão.

Duas restrições já medidas que valem para qualquer resposta:
- o histórico do Polymarket vem em passo de **12 horas** (o passo fino de 10 min só existe
  nos ~30 dias mais recentes de mercado vivo — não serve para backtest);
- a lista de negócios individuais está **capada em 20 mil por mercado**, então volume
  reconstruído a partir dela não cobre a vida inteira dos mercados grandes.

## 2. O formato do `diagnostics` — posso fechar?

Toda view devolve `ViewResult(P, Q, diagnostics)`, e o `diagnostics` é o dict que existe
**para o seu Ω**. Ficou combinado em 11/07 que o formato não estava travado, à sua espera.
Hoje as views já entregam, conforme o caso:

`view`, `caminho` (pmf / binario — o degrau da cascata em que a view rodou),
`divergencia`, `horizonte_q_dias`, `p_poly`, `p_curva`, `surpresa_bps`, `e_poly`,
`e_poly_declarado`, `breakeven_10y`, `duration`, `e_ff_bps`, `e_zq_dez_bps`.

**Falta o que você precisar de qualidade do dado** — o que eu consigo colocar aí sem
depender de mais ninguém: nº de pontos da janela, buracos de leitura, idade do último ponto,
dispersão recente da série. Me diga quais campos e com que nomes, que eu adiciono nas oito
views de uma vez. Enquanto não vierem, o Ω vai ter que inferir de fora o que a view já sabe.

## 3. O δ é seu tanto quanto meu

O δ (aversão a risco) está na minha lista de parâmetros pendentes, mas ele é dimensionamento
de risco — e risco é seu módulo. Se a gente cravar em reuniões diferentes, um vai desfazer o
efeito do outro sem perceber. Proposta: **δ e a escala do Ω fecham na mesma conversa**, não
em duas.

## 4. A régua do Ω — o que mudou com o fechamento do τ ⚠️ interface, não metodologia

Isto **não é pergunta e não muda o que o seu módulo mede.** É a forma em que o número precisa
chegar na minha ponta. Vem do fechamento do τ (decisão provisória desta rodada, marcada para
revisão do grupo).

**O que ficou fechado:** τ = 1/T, com T = janela de estimação do Σ. E, junto com ele, que o Ω fica
**ancorado em `diag(P · τΣ · Pᵀ)`**.

**O que isso quer dizer na prática:** o `Ω` que eu recebo não deve ser variância absoluta da view.
Deve ser um **multiplicador de confiança** sobre a variância que a própria view já implica:

```
Omega[i,i] = c_i * (P @ (tau * Sigma) @ P.T)[i,i]
```

Você me entrega o vetor de `c_i` — um por view. `c_i = 1` significa "confio nesta view tanto
quanto a incerteza do prior já sugere"; `c_i > 1` é menos confiança, `c_i < 1` é mais.

**Por que essa forma e não a outra — e por que isso é bom pra você:**

1. **O valor absoluto de τ sai da conta.** Com o Ω ancorado assim, a razão `τΣ / Ω` — que é o que
   de fato determina o peso da view contra o prior no BL — vira `1 / c_i`. O τ se cancela. Ou
   seja: **a briga sobre qual é o τ certo deixa de contaminar o seu módulo.** Se o grupo revisar o
   τ depois, o seu Ω não precisa ser recalibrado.
2. **Sobra exatamente o que você mede.** O que resta na expressão é confiança *relativa* entre
   views — que é o que o seu protocolo de 08/07 (confiança multiplicativa, volume como veto)
   produz. Você não precisa mais adivinhar a escala em unidades de retorno ao quadrado.
3. **Some a armadilha de escala.** Ω em variância absoluta exige acertar a ordem de grandeza; erra
   por 10² e a view some ou domina a carteira sem ninguém perceber. Com multiplicador, um `c_i`
   errado por um fator 2 desloca o peso por um fator 2 — proporcional, auditável, e o efeito é
   legível na tabela.

**O que eu preciso de você:** o vetor `c_i`, na ordem das views ativas, e a régua que o gera. O
`P` e o `Σ` são meus e já estão prontos — você não precisa deles pra calcular o `c_i`.

**O encaixe já está no código.** `src/market_inputs.py` tem:

```python
omega_fallback(P, sigma, tau, confianca=None)
```

O seu vetor entra em `confianca` e **nada mais muda** — nem no otimizador, nem nas views. Com
`confianca=None` (o default) ele devolve `diag(P·τΣ·Pᵀ)` puro, que é o Ω de He-Litterman: o plano
B com que o backtest roda enquanto o seu módulo não chega. Funciona e entrega número, mas é
literalmente "todas as views merecem a mesma confiança" — que é justamente o que o seu módulo
existe pra corrigir.

Se a sua régua já estiver saindo em **escala absoluta**, não precisa refazer: a conversão é
dividir pela diagonal dessa mesma fórmula. Só me avise em qual das duas escalas veio, porque as
duas parecem iguais e dão carteiras diferentes.

*(Se você discordar da forma, a conversa é essa mesma — mas ela precisa acontecer antes do loop de
backtest fechar, porque a interface entra no código nesse ponto.)*

---

**Achado que talvez mude sua régua**, já que a sua confiança olha estabilidade do mercado:
medi no dado cru que as **faixas de um mercado de buckets não somam 100%** — no CPI de
jul/2025 a soma varia entre 97,8% e 106%; no mercado de cortes do Fed, entre **92,3% e
132,5%**. Cada faixa é um livro separado, e elas se desencontram. Se "quão bem o mercado
está se comportando" entra no seu Ω, **o desvio da soma em relação a 1 é um termômetro
pronto** — é medida direta de desarranjo, disponível slot a slot, e ninguém precisa levantar
dado novo para usá-la. O código para ler isso já está pronto do meu lado (`src/poly_loader.py`).
