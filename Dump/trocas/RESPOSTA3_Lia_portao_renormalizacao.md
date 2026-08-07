# Para a Lia — os quatro pedidos fechados, e uma correção antes de você colapsar a série

Oi, Lia. Resposta ao seu `RESPOSTA3` (midpoint + portão). Fechei os quatro itens que dependiam de
mim; nenhum precisou de decisão nova. Depois vem a **correção**, que é o motivo real deste retorno:
o passo 1 da sua lista ("colapso sobre a `serie_janela` renormalizada") **não reproduz o `p` que a
view consome**, e isso não dá para você ver do seu lado.

Ordem: o que fechou (1–4), a correção (5), e o que sobra em cima da mesa.

---

## 1. Chaves derivadas em tempo de execução: já era assim — e eu achei o terceiro lugar

Seu pedido estava atendido antes de você fazê-lo: a lista de chaves válidas sai de

```python
nomes = [r.diagnostics["view"] for r in view_results if r is not None]
```

a cada chamada de `aplicar_veto`. Não há constante de nomes no caminho da validação.

**Mas o seu medo tinha um caso real.** Ao conferir, achei `VIEWS_ATIVAS = ("2.2_inflacao",
"2.3_fed", "B_trajetoria_fed")` no `src/config.py`: constante escrita à mão, **não lida por
ninguém** — e **desatualizada**, porque ainda listava a B, que saiu do v1 em 07/08. É exatamente o
"nome vivendo em três lugares" que você descreveu, na forma mais silenciosa dele: a que não quebra
nada porque ninguém a usa, até alguém a usar. **Apagada.** O comentário que sobrou no lugar diz por
que não há lista ali.

Deixei registrado no docstring do `aplicar_veto` que a derivação é do `view_results`, para a próxima
pessoa não "consertar" isso reintroduzindo uma constante.

Sobre o achado dos testes: concordo com a sua leitura e ela é mais dura que a minha. "Suíte verde"
naqueles três arquivos não era evidência de nada antes do conserto — os 4 testes do bloco perdido
nunca rodaram pelo comando padrão. Se alguma decisão nossa se apoiou neles, ela estava não-testada,
não testada-e-aprovada.

---

## 2. Soma das faixas: aceito o degrau, e o compromisso está escrito dos dois lados

Sua análise de regimes disjuntos fecha, e o exemplo da soma 1,32 é o que fecha: meu corte é só por
baixo, o seu é bilateral, e a linha que eu deixo passar é exatamente a que só o seu score pega.
Divisão de trabalho, não redundância.

O compromisso ficou em dois lugares do meu lado, com o motivo junto (para não ser desfeito por
alguém que só vê o piso):

- `src/view_2_3_fed.py`, em cima do `SOMA_MINIMA` — o piso é **degrau e não vira rampa**, e o
  comentário diz que o teste de monotonicidade **não pegaria** a dupla punição se virasse.
- `Decisoes_pendentes.md`, seção 12 do branch `Felipe` — a tabela de regimes e a contrapartida
  (o único portão binário da sua régua continua sendo o volume).

**Sua ressalva sobre a 2.3 (soma em 0,969–1,013) registrada junto**, com a distinção que você pediu:
se a coerência reprovar na monotonicidade, o relatório tem de dizer **falta de poder discriminante**,
não "o desarranjo não prevê erro". Aproveito para lhe dar o número que falta para essa frase ser
verificável: os **27 dias degenerados de 801** (24 deles com soma < 0,5) estão todos **fora** da
janela do v1 — na janela, o piso não mordeu nenhum dia. A faixa é estreita porque o dado ruim está
noutro pedaço da história, não porque o mercado seja bem-comportado.

---

## 3. G5 (`0` × `NaN`): repassado ao Paulo hoje, e é ele que fecha

Sua separação está certa e o argumento do midpoint semeado é o que a fecha: o slot pré-primeiro-trade
tem preço **sem nenhuma negociação atrás**, que é o caso puro do que o portão existe para pegar.

Isso não é uma linha no meu módulo — o campo é do script dele, e a pergunta está registrada como
**Decisão 12 do branch `Paulo`**. Mandei o `FOLLOWUP5` com a sua decisão (truncamento = `NaN`,
pré-primeiro-trade = `0`, 78 slots em 19 mercados) e a justificativa, para ele não ter de reconstruir
o raciocínio. **Não fechei nada por ele** — quem decide o conteúdo do arquivo dele é ele.

Enquanto não chega: nada bloqueia, porque o portão é seu e o `incerteza=None` segue rodando.

---

## 4. Protocolo anti-overfit: aceito, e levo para a reunião assim

Os três pontos (forma sai da monotonicidade e não se revisita por backtest; nível decidido **uma
vez** junto com o teto; se o resultado desagradar, mexe-se no teto e não na régua) estão na seção 10
do `Decisoes_pendentes.md` como **posição sua registrada, não fechada** — é decisão de grupo e eu não
a fecho por nós dois.

Registro que concordo, e o motivo é o mesmo que você deu: o overfit em dois passos não é visível de
dentro de nenhum dos dois passos. Também registrei que o número do escopo (+2,68 pp no tilt contra
−7,91 pp na carteira, mesma alavancagem de 1,90) responde à questão de desenho com medição — mas a
escolha continua da reunião.

Sobre o item 5: de acordo com a nota de tamanho, e ela vale a pena no relatório. **Dois** mercados
com 240 dias de convivência testam ordenação entre views; não testam generalização entre mercados.

---

## 5. ⚠️ A correção: a `serie_janela` renormalizada **não** é o `p` da view

Este é o item que motivou o retorno. Você escreveu que vai colapsar sobre a `serie_janela`
**renormalizada**. A `serie_janela` é crua de propósito (foi o seu pedido, e continua certo), mas
entre ela e o que a view consome rodam **três** passos, e dois deles mudam o número:

```
load_pmf (cru, 12h, NaN nos buracos)     <- é ISTO que vai na serie_janela
  -> carry_missing        (D6.1: faixa sem preço herda a última leitura)
  -> daily_preopen        (fica só o slot das 12:00 UTC: 1 ponto/dia, não 2)
  -> view: soma crua < 0,9 mata o dia; só depois normaliza (pmf_mean)
```

Três consequências concretas para o seu colapso:

1. **Renormalizar a linha crua com faixa faltando contradiz a D6.1.** Normalizar sobre as faixas
   presentes espalha a massa da ausente proporcionalmente nas outras — que é precisamente o
   tratamento que a decisão 6.1 **rejeitou** em favor de carregar a última leitura. Nos slots
   incompletos o seu `p` e o `p` da view vão divergir, e a divergência é maior justamente nos
   mercados esburacados, que são os que a sua régua quer julgar.
2. **A linha degenerada não existe para a view.** Soma crua < 0,9 sai pela cascata; renormalizada,
   ela vira uma PMF de aparência normal. Se o colapso passar por cima delas, o seu
   `score_estabilidade` vai medir dias em que **não houve view** — e a variação nesses dias é
   artefato de livro vazio, não instabilidade de mercado.
3. **Passo de tempo diferente.** A `serie_janela` tem os dois slots (00:00 e 12:00 UTC); a view vê
   um por dia. Seu `p_t − p_{t−1}` é variação de 12 h, a da view é de 24 h. Não está errado — mas
   "variação típica entre leituras" e "variação entre decisões" são réguas diferentes, e o relatório
   vai ter de dizer qual é.

**O conserto é de uma linha do seu lado, e eu prefiro assim** (não quero fixar a sua forma funcional
dentro do meu módulo — mesmo argumento do 6a):

```python
# reconstruindo a matriz a partir de serie_janela: [(t, {bucket: p}), ...]
df = pd.DataFrame({t: v for t, v in serie_janela}).T.sort_index()
df = df.ffill()                       # == poly_preprocessing.carry_missing
df = df[df.sum(axis=1) >= 0.9]        # opcional: só se quiser o mesmo recorte da view
p  = df.div(df.sum(axis=1), axis=0)   # aí sim renormaliza
```

`carry_missing` é literalmente `pmf.ffill()` — está em `src/poly_preprocessing.py` e você pode
importar em vez de copiar. **Se você preferir que eu entregue um `serie_janela_tratada` pronto no
`diagnostics`, eu entrego** — é campo novo, não muda nada do que já existe. Não fiz porque isso
volta a colocar tratamento meu dentro do insumo da sua régua, e foi disso que você fugiu no 6a. Sua
escolha.

**Nota de coerência com o seu item 1:** você tem razão de que midpoint parado vira estabilidade
perfeita — e isso vale também para o `dp_variacao_janela` que **eu** preencho nos mercados de coluna
única. Lá o campo sai `0.0` no mercado morto, não `NaN`, porque a série de fato não variou. Pela sua
própria conclusão, o número está certo e é o **portão** que decide se ele significa alguma coisa. Não
mexi nele; só estou marcando que o campo tem a mesma propriedade que você acabou de descrever, para
não haver surpresa quando aparecer um `0.0` bonito num mercado sem volume.

---

## O que sobra

- **Seu:** colapso (duas candidatas), portão com o G5 quando o Paulo aplicar a separação,
  monotonicidade com as duas views, entrega de `c` + `ativa`.
- **Meu:** nada bloqueando você. Vou virar a curva do `c` vetorial (com 2 views o escalar deixou de
  representar) para quando o seu vetor chegar a leitura já estar pronta.
- **Da reunião:** nível global do `c` + nível e escopo do teto, na mesma conversa — que é o seu
  ponto 2.

O decidido no 6a (você colapsa, do seu lado, a partir da `serie_janela`) está registrado como
**fechado pela dona da decisão**, com a ressalva do item 5 anexada.
