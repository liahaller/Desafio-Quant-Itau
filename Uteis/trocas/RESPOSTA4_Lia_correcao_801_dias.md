# Resposta ao seu `RESPOSTA4_Felipe_buracos_calibracao` — o número que sustenta o seu item 3 estava errado

Seus itens 1, 2, 4, 5 e 6 estão aceitos e não volto neles: o argumento do `ffill` como viés
unidirecional fecha, a grade de tempo como dimensão da calibração é melhor que escolher por
argumento, e o desacordo de fundo do item 1 ("meu score não deve reproduzir o `p` da view") eu
**concordo** — retiro a preocupação, e a oferta do `serie_janela_tratada` morre aqui.

Este retorno é sobre o **item 3**. Você fez uma escolha de método (calibrar sobre a história
completa) apoiada num número meu — "27 dias degenerados de 801, 24 deles com soma < 0,5, todos fora
da janela do v1". **Fui medir para lhe dar a receita de como chegar aos 801 dias e o número não
sobreviveu inteiro.** Melhor agora que depois da calibração.

---

## 1. O que está certo, o que está errado

| | o que eu disse | medido agora |
|---|---|---|
| dias degenerados | 27 | **25** (o 27 é outra coisa: dias com **alguma faixa faltando**) |
| desses, com soma < 0,5 | 24 | **24** ✔ |
| onde caem | "todos fora da janela do v1" | **errado — todos DENTRO**: 30/10/2025 a 21/04/2026 |

O erro do "fora da janela" tem conserto e o motivo verdadeiro é mais forte que o falso: o piso de 0,9
não mordeu nenhum dia do v1 **não** porque os dias ruins estivessem noutro pedaço da história, e sim
porque **a view não lê a linha crua**. Entre o parquet e a view roda o `carry_missing`, e depois dele:

| leitura | dias | soma < 0,9 | < 0,5 | faixa das somas |
|---|---|---|---|---|
| crua, sem carry (**o que você vai ler**) | 801 | 25 | 24 | — |
| após `carry_missing` (**o que a view consome**) | 801 | **0** | **0** | 0,953 a 1,143 |

Ou seja: no histórico **inteiro**, e não só na janela do v1, nenhum dia chega ao piso depois do
tratamento. A minha ressalva de que "a faixa 0,969–1,013 é propriedade do recorte" estava errada pelo
mesmo motivo — ela é propriedade do **tratamento**, que é exatamente a distinção que você fez no seu
item 1.

## 2. E o que isso faz com o seu item 3 — não é o ativo que você esperava

Dos 25 dias degenerados, **25 são linhas incompletas**, com mediana de **3 faixas ausentes de 4**.
Zero livros completos somando abaixo de 0,9. A soma baixa não é desencontro entre books: é faixa que
não existe na linha, contada como ausência.

Três consequências, todas do seu lado da fronteira — eu meço, você decide:

1. **O poder discriminante viria do canal errado.** Se esses dias entrarem no `score_coerencia`, o
   que o score estará medindo é buraco, não desarranjo — e buraco você já penaliza em
   `n_slots_esperados − n_pontos`. É a dupla contagem que você proíbe no seu próprio item 1
   ("cada defeito é penalizado uma vez, pelo canal certo").
2. **A sua regra nova já os descarta.** "Slot com qualquer faixa sem leitura não entra" elimina os 25
   por construção. Se a regra valer também para a coerência, a história completa não devolve
   nenhum dia degenerado — nem 801, nem 374.
3. **Sua ressalva original volta de pé, e agora com número:** se o ingrediente de coerência reprovar
   na monotonicidade, é **falta de poder discriminante**. Não porque a janela do v1 seja estreita,
   mas porque em livro completo a soma dessa família de mercados quase não se afasta de 1.

Isso **não** derruba calibrar sobre a história completa — 801 dias contra 374 continua sendo mais
amostra, e a trava do 6d segue valendo. Derruba só o motivo que você deu para isso, que era eu.

## 3. A receita dos 801 dias (era o que eu ia mandar de qualquer jeito)

O parquet é a fonte certa. Mas "801" é uma construção, não o tamanho do arquivo — lendo direto você
encontra 3.905 slots crus, ou 1.952 linhas (reunião × dia), ou 804 dias distintos, e nenhum é o meu
número. A receita:

```python
from poly_loader import load_fomc_pmf, daily_preopen

d = load_fomc_pmf("data/polymarket_fed_reunioes.parquet")   # 18 reuniões
# 1 linha por DIA: vale o mercado da PRÓXIMA reunião (reuniao >= dia),
#    slot pré-abertura (daily_preopen), série CRUA — sem carry_missing.
# É a mesma regra de seleção que a view 2.3 usa, então os dias batem 1 a 1.
```

Os 18 mercados se sobrepõem (todo par de reuniões consecutivas tem overlap), então **sem** a regra da
"próxima reunião" o mesmo dia aparece 2 a 3 vezes e a contagem infla. Se você quiser os 801 dias já
resolvidos num arquivo, eu gero — é uma chamada, e evita que a gente descubra na reunião que estava
contando dias diferentes.

## 4. `dp_variacao_janela`: de acordo, e o campo fica órfão

Você não vai consumi-lo em caso nenhum. Isso o deixa sem leitor — o mesmo defeito do `VIEWS_ATIVAS`
que você me apontou. **Não vou apagá-lo antes da entrega** (apagar campo de interface na véspera é o
risco que não compensa): fica marcado no docstring como não consumido, com a data, e some depois.
Se você preferir que suma agora, digo o contrário sem discutir — é o seu insumo.

## 5. O prazo, que ninguém tinha dito em voz alta

A entrega é **17/08**. O que sobra do seu lado são quatro itens, e o item 2 (portão de volume)
continua preso na D12 do **Paulo** — que já está com a sua decisão na mão (`FOLLOWUP5`), mas não
respondeu.

Estamos propondo ao grupo uma **data de corte** — a proposta é **13/08**, ainda não fechada:

- **se o `c` chegar até lá:** entra, remede-se Σ|w| e o teto se decide com o número novo. É a sua
  ordem (1 → 2 → 3), cumprida.
- **se não chegar:** o v1 entrega com `c = 1` e teto no tilt, com o nível escolhido por critério
  escrito **antes** de olhar o excesso, e o relatório declara a régua como não entregue a tempo.

O motivo de fixar isso agora, e não no dia 15, é o seu próprio protocolo anti-overfit: teto escolhido
depois de ver o resultado é o número que faz o backtest ficar bonito.

**Um dado que aumenta o peso disso** (`Dump/analises/Curva_c.md`, remedido hoje com as duas views
ligadas): o `c` deixou de ser ajuste fino. Na mesma grade de antes, o excesso se move até **5,01 pp**
e **troca de sinal** no escopo de tilt (+2,62 pp em `c = 1`, máximo de +4,57 pp em `c = 0,25`,
−0,44 pp em `c = 0,01`). Com a 2.2 sozinha isso não aparecia — a leitura antiga era "o teto morde
antes". O nível da sua régua agora escolhe resultado, o que torna o seu item 2 (nível uma vez só,
junto do teto) mais necessário, não menos.
