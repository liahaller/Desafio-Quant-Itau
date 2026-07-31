# Para a Lia — três perguntas sobre o Ω (uma delas está travando o Paulo)

Oi, Lia. Três coisas curtas, em ordem de urgência.

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

---

**Achado que talvez mude sua régua**, já que a sua confiança olha estabilidade do mercado:
medi no dado cru que as **faixas de um mercado de buckets não somam 100%** — no CPI de
jul/2025 a soma varia entre 97,8% e 106%; no mercado de cortes do Fed, entre **92,3% e
132,5%**. Cada faixa é um livro separado, e elas se desencontram. Se "quão bem o mercado
está se comportando" entra no seu Ω, **o desvio da soma em relação a 1 é um termômetro
pronto** — é medida direta de desarranjo, disponível slot a slot, e ninguém precisa levantar
dado novo para usá-la. O código para ler isso já está pronto do meu lado (`src/poly_loader.py`).
