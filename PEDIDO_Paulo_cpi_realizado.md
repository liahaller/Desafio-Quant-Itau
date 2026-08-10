# Para o Paulo — valor realizado do CPI (pedido de robustez, **sem urgência**)

Paulo, antes de tudo: **isto não bloqueia nada e não é para 13/08.** É pedido de robustez do
relatório, e se não couber antes da entrega eu registro a limitação e sigo. Estou mandando agora
porque o levantamento é seu e vale você saber que existe, não porque preciso amanhã.

O G10c chegou certo, e o calendário corrigido já está em uso do meu lado — re-rodei a calibração
inteira da 2.2 com ele. Mudou exatamente um número (o do ingrediente que já tinha sido
descartado); o resto saiu idêntico. Obrigada pela correção.

## Por que preciso do valor, e não só da data

A calibração do Ω escolhe a forma da régua por um teste: confiança maior tem de vir antes de erro
menor. Esse "erro" precisa de um alvo, e usei dois:

1. **variação futura da probabilidade** — funciona nas duas views, mas é parcialmente circular
   quando comparo duas formas de medir movimento (cada uma tende a vencer no alvo medido por ela
   mesma);
2. **erro contra o desfecho real** — quanto de probabilidade o mercado alocou fora do que de fato
   aconteceu. Não é circular.

O (2) já roda na **2.3 (FOMC)**: derivo o desfecho do `fred_DFF.csv` que você entregou (variação da
taxa efetiva em torno da reunião, arredondada a 25 bps), e a derivação **concorda com o mercado em
16 de 16** reuniões em que ele terminou inequívoco. Funcionou bem.

Na **2.2 (CPI)** não roda, porque o desfecho é o CPI publicado e o pipeline traz as datas, não os
valores. Hoje o relatório declara isso como limitação: a verificação de não circularidade existe
numa view só.

## O que eu preciso

**Variação mensal do CPI (MoM, em pontos percentuais), na unidade dos buckets do Polymarket** —
os slugs falam `increase-by-0pt3`, `decrease-by-0pt2`, `stay-flat-0pt0`, então é a mesma grandeza,
em passo de 0,1 pp. Escopo: os meses de referência dos 19 mercados-mês que já estão no
`clob_exploracao` (dez/2024 a jul/2026).

Três detalhes que decidem se o número serve, e **nenhum deles eu quero cravar sozinha** — os três
saem da *rule* do mercado, que é o que resolve na prática:

1. **⚠️ Ajuste sazonal: SA ou NSA?** `CPIAUCSL` (ajustado) e `CPIAUCNS` (não ajustado) dão números
   diferentes no mesmo mês, e a diferença é da ordem do tamanho de um bucket — ou seja, pode trocar
   o bucket vencedor. A manchete que sai na imprensa é a SA, mas isso não é garantia da regra.
   Como você já leu as rules para montar o calendário, o mais barato é conferir lá.
2. **⚠️ Vintage: o valor da PRIMEIRA divulgação, não o revisado.** O CPI é revisado depois, e a
   série corrente do FRED traz o valor revisado. O mercado resolveu pelo número que saiu **no dia**;
   usar o revisado seria olhar para um dado que não existia na resolução. Se der trabalho pegar os
   vintages (ALFRED), **um aviso de que o valor é o revisado já me serve** — eu registro a ressalva
   em vez de mandar você atrás disso.
3. **Casas decimais e arredondamento.** Preciso do valor com pelo menos 2 casas, não arredondado a
   1. Com 1 casa não dá para saber a que distância da fronteira o mês caiu, e é a fronteira que
   decide o bucket.

## Uma pergunta avulsa (curiosidade útil, não pedido)

O CPI de **out/2025 nunca foi publicado** — foi o release fantasma que você encontrou. Mas o mercado
`CPI_october-inflation-monthly` existe no `clob_exploracao` e a série dele termina com um bucket em
0,865. **Como ele resolveu?** Se o Polymarket cancelou e devolveu, ou resolveu por alguma regra
alternativa, isso muda o que aquele mercado significa nos meus testes. Se você não souber de cabeça,
não vá atrás — eu trato aquele mês como sem desfecho, que é o conservador.

## Prioridade, para ficar claro

Última da fila, atrás de tudo que for do backtest e do G5 do FOMC (o
`PEDIDO_Paulo_G5_fomc.md` continua valendo e **esse** sim tem prazo). Se a resposta for "não dá
antes da entrega", está ótimo — a limitação já está escrita no relatório e não preciso mudar uma
linha do que está pronto.

— Lia
