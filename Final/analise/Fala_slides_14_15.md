# Fala — slides 14 (Backtest e resultados) e 15 (Análise crítica)

> Draft para a final. Linguagem para gestor, não para estatístico: cada índice
> aparece com o que ele é em uma frase e a conclusão logo em seguida. Números
> de `Uteis/analises/Analise_backtest.md`. Tempo-alvo: ~70 s cada.

---

## Slide 14 — Backtest e resultados (~70 s)

**Abertura (o placar):**
"Em 374 pregões — fevereiro de 2025 a agosto de 2026 — a carteira rendeu
33,2 % líquido de custo, contra 30,1 % do S&P. São 3 pontos a mais, com a
mesma volatilidade — 17,6 % contra 17,9 % — e um Sharpe de 1,18 contra 1,08.
A queda máxima foi parecida: −19,6 % contra −18,8 %. Ou seja: ganhou um pouco
mais, correndo o mesmo risco."

**A curva (apontar):**
"A curva mostra de onde isso vem. Nos dois tombos, abril de 2025 e março de
2026, a carteira caiu junto com o mercado. A vantagem foi construída na
recuperação, não na defesa."

**A cascata (apontar, rápido):**
"E de onde vem o número: 28,7 pontos são o mercado — o que qualquer um teria
comprando o índice. As opiniões do Polymarket somaram 5,2 pontos; o custo de
transação tirou 3. O que sobra é o que chega ao investidor."

**O tile novo — a pergunta honesta:**
"Agora a pergunta que qualquer gestor faz: esses 3 pontos são habilidade ou
sorte? Nós medimos. Pegamos os mesmos 374 dias e simulamos milhares de
versões alternativas desse período, embaralhando os dias em blocos — como se
o mesmo ano e meio tivesse acontecido em outra ordem. Em 64 % dessas versões
a carteira ainda bate o índice. Sessenta e quatro. É mais que cara ou coroa,
mas não é prova. Para dizer com 95 % de confiança que o resultado é real,
precisaríamos de 457 pregões — faltam 83, uns quatro meses."

**Fecho:**
"Então o que dizemos é isto: o número é positivo em todas as leituras, e ele
não foi inflado — nenhum parâmetro foi escolhido olhando o resultado. Mas
quem sustenta a estratégia não é este número; é o que mostramos antes: o
Polymarket é calibrado, o retorno por ativo vem de eventos passados, e a
confiança é medida, não digitada."

---

## Slide 15 — Análise crítica (~70 s)

**Abertura:**
"Três números resumem como a gente lê a própria estratégia."

**457 — a prova exige tempo:**
"O primeiro é 457. É o número de pregões que a estatística exige para afirmar,
com 95 % de confiança, que um Sharpe deste tamanho é positivo de verdade.
Temos 374. Então a leitura é: promissora, ainda não provada. O teste que falta
é o próximo semestre — e vamos registrar antes o que esperamos ver, para não
ajustar a história depois."

**+6,2 bps — onde o ganho mora:**
"O segundo é 6,2 pontos-base por dia — pontos-base são centésimos de por
cento. Nos dias em que o S&P cai, a carteira perde em média 0,06 % a menos
que ele. Nos dias em que sobe, ganha 0,04 % a menos. Isso diz o que a
estratégia é: um tilt defensivo em cima do índice. Ela não protege de um
tombo — em abril caiu mais fundo que o mercado — mas, dia a dia, perde menos
na queda. O custo disso: no segundo semestre da janela, que foi só de alta,
ela ficou 0,6 ponto atrás do índice."

**3 de 7 — pelo protocolo da literatura:**
"O terceiro é 3 de 7. Três pesquisadores conhecidos — Arnott, Harvey e
Markowitz — publicaram um checklist de sete pontos para julgar se uma
pesquisa quantitativa é séria. Fechamos três: a hipótese foi escrita antes
do teste, os dados não olham o futuro, e uma ideia entra por acertar a
probabilidade, nunca por render mais. Três são parciais — testamos muitas
variantes, e o modelo de confiança não vê correlação entre opiniões. E um
está aberto, e só o tempo fecha: validação fora da amostra."

**Fecho:**
"Se fôssemos começar de novo: pré-registrar o próximo semestre como teste,
corrigir a busca de estratégias táticas pelo número de tentativas, e um
modelo de confiança que enxergue quando duas opiniões dizem a mesma coisa."

---

## Se perguntarem (respostas curtas)

- **"Então o backtest não prova nada?"** — Prova que o resultado não é
  negativo em nenhuma leitura e que não foi inflado por escolha de parâmetro.
  Prova de habilidade exige track record; 18 meses não bastam para ninguém.
- **"O que é esse 'embaralhar em blocos'?"** — Bootstrap: recriamos milhares
  de anos-e-meio alternativos reamostrando os dias reais em blocos de ~10, para
  manter a sequência de curto prazo. Mede quanto o resultado depende da ordem
  em que os dias caíram.
- **"64 % é bom ou ruim?"** — É honesto. Um resultado de sorte pura daria
  50 %; um resultado provado daria 95 %. Estamos no meio, e dizemos isso.
- **"Por que Sharpe 1,18 não é significativo?"** — Porque em 1,5 ano o erro
  de medida do Sharpe é de ±0,8. Qualquer Sharpe abaixo de ~1,6 em 18 meses é
  compatível com zero. É a matemática do período curto, não da estratégia.
- **"Faltam 83 pregões — e daí?"** — E daí que o próximo semestre é o teste
  de verdade, e vai ser registrado antes de ser visto.
- **"Por que mostrar os pontos fracos?"** — Porque o checklist pede, e porque
  um slide só de pontos fortes com 18 meses de dado é o que a literatura chama
  de contar história depois do fato.
- **"Defensiva mas caiu mais em abril — não é contradição?"** — Não. Dia a
  dia, perde menos na queda (em 52 % dos dias de queda). No tombo de abril a
  alavancagem de 1,9× pesou mais que o tilt. Média e cauda são coisas
  diferentes, e o slide diz as duas.

## Glossário de bolso

- **Bootstrap** — simular o mesmo período muitas vezes reamostrando os dias
  reais; dá a faixa de resultados que o acaso produziria.
- **IC95 [−13; +21]** — 95 % das simulações caem nessa faixa de excesso
  sobre o índice. Inclui zero: por isso não é prova.
- **Track record mínimo (MinTRL)** — quantos pregões seriam necessários para
  o Sharpe medido ser positivo com 95 % de confiança.
- **Ponto-base (bps)** — 0,01 %. 6,2 bps = 0,062 %.
- **Protocolo de 7 pontos** — checklist de Arnott, Harvey & Markowitz (2019)
  para pesquisa quant: motivação, testes múltiplos, dados, validação,
  dinâmica, complexidade, cultura.
