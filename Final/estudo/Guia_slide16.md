# Guia do slide 16 e dos apêndices A1–A3

> Para ler antes do dia e ter na mão na arguição. O slide tem duas observações
> e uma conclusão; os apêndices têm o resto. Os números vêm de
> `Uteis/analises/Metricas_estudo.md` (gerado por `scripts/estudo_polymarket.py`);
> a versão completa e técnica é `Final/estudo/Estudo_polymarket.md`.

## A mensagem

**O preço do Polymarket é uma probabilidade de verdade, e na decisão do Fed
ele erra menos que o mercado de juros. Por isso ele é a opinião do nosso
Black-Litterman.**

Se der tempo de uma terceira frase: *o valor está no nível da probabilidade,
não no movimento dela* — o movimento não antecipa retorno e o preço não tem
tendência. É o que está nos apêndices.

## Fala sugerida (≈ 60 segundos)

> "Antes de confiar num sinal, medimos o sinal. Pegamos todos os contratos do
> Polymarket que a estratégia usa — decisões do Fed e CPI, 150 contratos, 30
> eventos — e olhamos o preço em 11 momentos antes de cada resolução.
>
> Primeira observação: quando o Polymarket diz 70 %, acontece 70 % das vezes.
> A curva fica em cima da diagonal, e o erro na véspera é o mesmo que o Kalshi
> publica para 2 milhões de mercados a uma hora do evento.
>
> Segunda: na decisão do Fed, o Polymarket erra 0,9 ponto-base na véspera; o
> mercado de juros, 4,8. Acertou as 17 decisões.
>
> Conclusão: é uma probabilidade confiável, e melhor que os juros no que os dois
> precificam. Por isso ela é a opinião do Black-Litterman."

---

## Slide 16

### Observação 1 — Calibração: "Quando o Polymarket diz X %, acontece X % das vezes."

**O que o gráfico mostra.** Pega todos os contratos, agrupa por preço (de 0 a
10 ¢, de 10 a 20 ¢, …) e, em cada grupo, conta quantos aconteceram. Eixo x =
preço médio do grupo; eixo y = quantos resolveram "sim". Se o preço é uma
probabilidade honesta, os pontos ficam na linha diagonal.

**De onde vem.** 150 contratos (76 desfechos de 18 reuniões do Fed + 74 faixas
de 12 CPIs mensais), lidos em 11 momentos antes da resolução (60 dias até a
véspera) = 1.416 leituras. A linha laranja usa todas; a azul só a véspera. As
barrinhas são a incerteza estatística (intervalo de 95 %). O que "aconteceu"
vem do FRED (taxa efetiva do Fed e CPI publicado), não do próprio mercado.

**Como ler.** Pontos em cima da diagonal = calibrado. O ponto grande no canto
(0,02; 0,00) são 908 leituras de faixas a 1–2 ¢ que nunca aconteceram — o
mercado acerta que são improváveis. As barras do meio são largas porque poucos
contratos ficam entre 30 e 70 ¢ (o mercado costuma ter certeza).

**O número.** Brier 0,043 na véspera — é o "erro médio" de uma previsão
probabilística (0 = perfeita; 0,25 = chutar 50 % sempre). O Kalshi publica
0,045 a uma hora do evento, com 2 milhões de mercados.

**Conclusão.** O preço do Polymarket pode ser usado como probabilidade sem
tradução. O único desvio é o clássico: azarões um pouco caros, favoritos um
pouco baratos — e a correção que a estratégia já testa como robustez
(γ = 1,1–1,25) é exatamente a que o dado pede.

### Observação 2 — Decisão do Fed: "O Polymarket erra 0,9 bps; o mercado de juros, 4,8."

**O que o gráfico mostra.** Antes de cada reunião do Fed, três "palpites" sobre
a decisão (em pontos-base): o do Polymarket (laranja), o do mercado de juros
(cinza) e o do mercado de juros corrigido do seu viés conhecido (azul
tracejado). O eixo y é o erro médio em relação ao que o Fed fez; o eixo x é
quantos dias antes da reunião. O tempo anda para a direita.

**De onde vem.** Polymarket: os mercados "o Fed corta 25 / 50 / mantém / sobe"
de cada reunião, maio/2024 a junho/2026 — a média deles é o Δtaxa esperado.
Mercado de juros: a diferença entre o T-bill de 3 meses e a taxa efetiva
(`DTB3 − DFF`), o mesmo termômetro que a estratégia usa por não haver o futuro
de fed funds gratuito. "Corrigido" = descontado o erro médio das reuniões
anteriores, que é como a estratégia o usa. O que o Fed fez: taxa efetiva do
FRED.

**Como ler.** Longe da reunião os três erram parecido (~7–10 bps). Conforme a
reunião se aproxima, o Polymarket converge para quase zero (0,9 bps na
véspera); o mercado de juros para em 4,8 (corrigido) ou 8,9 (cru). E o
Polymarket acertou o desfecho mais provável em 17 de 17 reuniões na véspera —
inclusive setembro de 2024, que estava 52 % a 47 % entre cortar 50 ou 25.

**Conclusão.** Perto da decisão, o Polymarket é o termômetro mais preciso —
porque precifica exatamente a decisão desta reunião, enquanto o T-bill mistura
três meses de caminho. Numa regressão com os dois juntos, o mercado de juros
não acrescenta nada ao Polymarket. É isso que a view 2.3 explora: a diferença
entre os dois vira a surpresa esperada.

### Conclusão do slide

"É uma probabilidade confiável — e melhor que os juros no que os dois
precificam. Por isso ela é a opinião do Black-Litterman." O BL pede uma opinião
(quanto vai render) e uma confiança (quanto ela pesa). O estudo diz que a
opinião pode vir do Polymarket sem tradução; a régua do Ω decide o peso.

---

## Apêndice A1 — Acurácia por horizonte

**O que os gráficos mostram.** À esquerda, o erro (Brier) por dias antes da
resolução, separado em Fed (laranja) e CPI (azul), com a linha branca juntando
os dois até 20 dias. As linhas pontilhadas são as referências publicadas
(Kalshi a 3 meses e a 1 hora; Dune/McCullough a 12 horas). À direita, o mesmo
em "quanto o preço acrescenta ao não sei": 0 = tão bom quanto chutar igual em
todas as faixas; 1 = perfeito.

**De onde vem.** As mesmas 1.416 leituras da calibração, agrupadas por
horizonte. A sombra é o intervalo de 95 %.

**Como ler.** O erro cai à medida que o evento se aproxima — nas duas famílias.
Fed: 0,035 a 20 dias → 0,007 na véspera (na véspera a decisão é quase certa).
CPI: 0,092 → 0,078 (o CPI é o objeto difícil; ninguém sabe o número na
véspera, e mesmo assim o mercado remove 42 % da incerteza). A linha branca para
em 20 dias porque os mercados de CPI vivem só ~30 dias; depois só sobra Fed.

**Conclusão.** O Polymarket incorpora informação continuamente até o evento, e
na véspera está no nível do melhor que se publica — com uma amostra 100 %
macro, sem escolher mercados fáceis.

## Apêndice A2 — Polymarket × mercado de juros

**Gráfico da esquerda, painel de linhas.** É o mesmo do slide 16 (erro em bps
por horizonte).

**Gráfico da esquerda, painel de barras.** Em cada horizonte, a fração de
reuniões em que o desfecho mais provável foi o que aconteceu. Polymarket: 100 %
até 2 dias antes, 94 % de 3 a 15 dias, 89 % a 20. O mercado de juros
corrigido também acerta perto do evento — a decisão do Fed raramente surpreende
na véspera. **A diferença está na distribuição, não na direção:** o Polymarket
diz "90 % de cortar 25" quando o T-bill diz "algo entre 25 e 50".

**Gráfico da direita (lead-lag).** Pergunta: quem se move primeiro, o
Polymarket ou o mercado de juros? Correlação entre o movimento diário dos dois,
para o Polymarket de hoje contra o mercado de juros de k dias antes (k < 0) ou
depois (k > 0). As barras cinza (k = −1 e 0) são altas porque as duas janelas
se sobrepõem no relógio — o Polymarket lido de manhã já viu o pregão de ontem;
é mecânico. As barras laranja (k = +1, −2) são o teste limpo: ≈ 0.

**Conclusão.** Nenhum dos dois "vê antes"; a informação chega aos dois no
mesmo dia. O ganho do Polymarket não é antecipar o mercado de juros — é dar a
distribuição da decisão com menos ruído. (Na regressão com os dois juntos, o
peso do Polymarket é 1,14 e o do mercado de juros −0,06: o segundo não
acrescenta nada.)

## Apêndice A3 — Onde está o valor

**Gráfico da esquerda (event-study).** Para cada um dos 9 ETFs, quanto do
retorno no dia da decisão do Fed é explicado pela "surpresa" — a diferença
entre o que aconteceu e o que se esperava na véspera. Três versões da surpresa:
Polymarket (laranja), mercado de juros corrigido (cinza) e a variação do T-bill
no próprio dia (azul, o método clássico). Altura da barra = R² (0 = não explica
nada; 1 = explica tudo).

**Como ler.** A surpresa do Polymarket explica pouco (média 0,08). Não porque o
Polymarket erre — é o contrário: ele acertou tanto (0,9 bps) que quase não
sobra surpresa para explicar. O que move os ETFs no dia do Fed é o *caminho*
(comunicado, projeções, coletiva), que o T-bill de 3 meses carrega em parte
(média 0,19). São 17 reuniões: barras individuais são frágeis; olhe a média.

**Gráfico da direita (placar).** Seis vereditos do estudo:
- ✔ calibrado (b = 1,04; p = 0,15) — Observação 1;
- ✔ skill na véspera (73 %) — remove 73 % da incerteza do "não sei";
- ✔ erra menos que o FF (0,9 × 4,8 bps) — Observação 2;
- ✕ a surpresa explica o dia do Fed? R² 0,08 — quase não sobra surpresa;
- ✕ o movimento da probabilidade antecipa o retorno dos ETFs? não (t ≈ 0 em
  h = 0, 1, 5, medido antes em `Teste_sinal.md`);
- ✕ o preço do Polymarket tem tendência? não — reverte em 12 h (VR(5) = 0,78 <
  1; autocorrelação −0,13). É ruído de tick, não momentum.

**Conclusão.** Os três ✕ dizem *onde* o valor está: no nível, não no
movimento. Se o movimento fosse sinal, o certo seria negociar o Δp. Não é —
então o desenho certo é o nosso: nível como opinião (Q = β × surpresa),
estabilidade como confiança (Ω), Black-Litterman no meio.

---

## Se a banca perguntar

- **"Amostra pequena."** — 150 contratos, 30 eventos. Pequena em eventos, por
  isso toda incerteza é calculada reamostrando eventos, não contratos. A
  diferença 0,9 × 4,8 bps passa no teste com 17 reuniões. E é 100 % o dado que
  a estratégia usa — não escolhemos mercados.
- **"O Kalshi mediu 2 milhões; vocês, 150."** — O estudo amplo exclui 80 % dos
  mercados e não tem benchmark de mercado tradicional. O nosso tem os dois:
  amostra declarada e comparação com o mercado de juros no mesmo objeto.
- **"Isso é o futuro de fed funds de verdade?"** — Não, é o T-bill de 3 meses
  menos a taxa efetiva — o proxy que a estratégia usa (o contrato é pago).
  Mostramos cru e corrigido do viés; a conclusão vale nos dois. O paper do Fed
  de 2026 acha o mesmo para o Kalshi contra o futuro real.
- **"Tem viés?"** — Pequeno e conhecido: azarões abaixo de 10 ¢ nunca
  ganharam. A correção que o dado pede (γ ≈ 1,1–1,2) já está na varredura de
  robustez da estratégia.
- **"Se é tão bom, por que não negociar o Polymarket?"** — Porque o preço dele
  não tem tendência (reverte em 12 h) e o movimento não antecipa retorno. O
  valor está no nível, e nível vira carteira via β e Black-Litterman.
- **"A surpresa não explica o dia do Fed. Então a view 2.3 não serve?"** — Ela
  faz o que promete: transforma a diferença Polymarket × juros em tilt. Como o
  Polymarket acerta, a surpresa é pequena e o tilt é pequeno — e a régua do Ω
  decide o peso. O estudo explica *por que* o tilt é modesto; não o invalida.
- **"Olharam o futuro (lookahead)?"** — Preço lido às 08:00 de Nova York,
  antes de qualquer anúncio; mercado de juros lido no fechamento do dia
  anterior; viés corrigido só com reuniões passadas. Conferido contra o
  artefato do slide 4.
- **"E payrolls?"** — Sem resolução no nosso dado (arquivos sem rótulo de
  faixa). Entram só nos testes que não precisam dela. Com o dado, entram pelo
  mesmo script.

## Palavras que aparecem

- **Brier** — erro médio de uma previsão em probabilidade: (preço − resultado)².
  0 = perfeito; 0,25 = chutar 50 % sempre.
- **bps** — pontos-base; 25 bps = 0,25 ponto percentual, um "passo" do Fed.
- **Futuro de fed funds / proxy** — o preço que o mercado de juros dá para a
  taxa do Fed; aqui, T-bill de 3 meses menos taxa efetiva.
- **Calibração** — quando diz X %, acontece X % das vezes.
- **Skill (BSS)** — quanto o preço reduz a incerteza de quem chuta igual em
  todas as faixas. 0 = nada; 1 = tudo.
- **VR (razão de variâncias)** — mede se o preço tem tendência. 1 = anda sem
  memória; < 1 = vai e volta; > 1 = continua na direção.
- **Lead-lag** — quem se move primeiro.

## Onde está cada coisa

| o quê | arquivo |
|---|---|
| script (mede tudo; `--demo` = auto-teste) | `scripts/estudo_polymarket.py` |
| tabelas | `Uteis/dados/estudo/*.csv` · `Uteis/analises/Metricas_estudo.md` |
| figuras | `Uteis/graficos/estudo_*` |
| paper completo | `Final/estudo/Estudo_polymarket.md` |
| slides 16, A1–A3 | `scripts/slides_final_pptx.py` → `Final/Slides_novos.pptx` (slides 18–21 do arquivo) |
