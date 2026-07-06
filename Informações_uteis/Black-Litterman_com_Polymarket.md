# Black-Litterman com views do Polymarket

## Em uma frase
Montar a carteira partindo do consenso do mercado e só se afastar dele quando há convicção — trocando os "chutes" de opinião do gestor pelas probabilidades do Polymarket (apostas com dinheiro real).

## Como funciona
O Black-Litterman combina dois ingredientes:

- **Prior — a carteira de mercado.** O ponto de partida neutro: a carteira de equilíbrio, com pesos de mercado. Sem opinião nenhuma, é nela que ficamos.
- **Views (vetor Q) — o que o Polymarket diz.** Cada mercado relevante vira uma opinião sobre o retorno esperado de um ativo, setor ou par. Ex.: probabilidade de corte de juros → setores sensíveis a duration superam os defensivos.
- **Confiança (matriz Ω) — o quanto acreditamos em cada view.** Medida por volume, liquidez e estabilidade do mercado no Polymarket: quanto mais líquido e estável, maior a confiança.

O resultado é uma carteira que se inclina na direção das views, proporcional à confiança de cada uma.

## Por que isso é diferente
A maior crítica prática ao Black-Litterman é que as views e a confiança são subjetivas — o gestor chuta retornos e convicções. Aqui, *todas* as views vêm de probabilidades negociadas com dinheiro real e *toda* a confiança vem de métricas objetivas (volume, liquidez, estabilidade, convergência entre fontes). Transformamos o elo mais frágil e subjetivo do modelo no mais sistemático.

## O botão: overlay ↔ cérebro central
Quanto o Polymarket manda na carteira é um parâmetro, não uma decisão de arquitetura:

- **Confiança alta** → as views dominam → o Polymarket dirige a alocação.
- **Confiança baixa** → a carteira fica perto do mercado → o Polymarket só ajusta na margem (overlay).

Não precisamos escolher de antemão; calibramos o botão.

## Confiança móvel: o Ω reage à qualidade do sinal
A confiança (Ω) não precisa ser um número fixo — pode ser uma função do estado, recalculada a cada momento conforme a qualidade do sinal do Polymarket muda. Ela sobe ou desce reagindo a:

- **Volume / liquidez** do mercado naquele instante (mais volume → mais confiança).
- **Estabilidade da probabilidade:** oscilando muito → confiança cai; estável → confiança sobe.
- **Convergência entre fontes:** poly, polls e casas de aposta concordam → confiança alta; divergem → baixa.
- **Proximidade de evento:** perto de um evento agendado e incerto → confiança cai automaticamente.

O ganho: a confiança reativa **embute o controle de risco e de beta no próprio modelo**. Quando ela cai (evento volátil, fontes divergindo), a carteira recolhe sozinha em direção ao prior — menos risco. Quando sobe, ela inclina mais nas views. O overlay de risco deixa de ser um módulo separado e passa a viver dentro do Ω.

Em resumo: prior fixo + Ω reativo = uma carteira que aperta e solta a exposição ao Polymarket conforme o sinal melhora ou piora em tempo real.

## Exemplo concreto
O Polymarket dá 65% de probabilidade de corte de juros; os futuros de Fed Funds precificam 45%. A view é "setores long-duration (tech, real estate) superam os defensivos", com magnitude vinda da sensibilidade histórica desses setores a surpresas de juros, e confiança proporcional ao volume e à estabilidade do mercado.

## Sinais táticos (a camada por cima)
Além de moldar a alocação estrutural via views, o Polymarket gera **sinais táticos**: trades curtos e pontuais que aproveitam a defasagem entre o momento em que o Polymarket se move e o momento em que o mercado tradicional reprecifica. Eles ficam *por cima* da carteira — não mudam os pesos estruturais, são uma camada separada de posições oportunistas. Cada um é independente: se um não funcionar, sai sem derrubar o resto.

Exemplos:

- **Drift pós-evento.** Quando um evento se resolve de forma surpreendente (desfecho real vs. a probabilidade que o Polymarket dava na véspera), as ações expostas subreagem e o preço "drifta" na direção da surpresa por dias ou semanas. O modelo se posiciona nesse drift. Ex.: algo que o poly dava 30% e aconteceu = surpresa grande → drift explorável.
- **Event-driven.** Quando a probabilidade de um evento ligado a uma empresa salta de repente (ex.: aprovação de fusão de 40% → 70%), o modelo compra ou vende a ação afetada antes de o mercado acionário precificar por completo.
- **Velocidade de ajuste.** Quando a probabilidade do poly se move rápido e o mercado ainda não reagiu, a *derivada* do movimento vira sinal para uma posição tática de curto prazo, capturando a defasagem.

Detalhe útil: o mesmo sinal pode rodar como *view* (estrutural) ou como *sinal tático* (curto prazo) dependendo do horizonte — as cestas eleitorais, por exemplo, podem tiltar setores na alocação ou virar um pair trade pontual quando o spread das cestas ainda não acompanhou o poly.
