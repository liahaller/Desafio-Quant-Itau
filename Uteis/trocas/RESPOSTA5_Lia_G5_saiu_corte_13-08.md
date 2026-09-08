# Para a Lia — o G5 saiu, o corte é 13/08, e dois defeitos que o G5 novo expõe no seu código

> Substitui o `RESPOSTA4_Lia_correcao_801_dias.md`, que não chegou a ser enviado.
> Mesmo conteúdo de correção (seções 4 e 5 aqui), mais o que mudou desde então.
> **A parte urgente é a seção 2** — são dois defeitos medidos, não opiniões.

Três coisas, em ordem de urgência:

1. **O G5 chegou.** O último item bloqueado da sua régua está entregue.
2. **Dois defeitos no `calibracao_omega.py`**, ambos reproduzidos aqui — e o primeiro
   inverte exatamente o tratamento que você acabou de decidir no FOLLOWUP5.
3. **A data de corte virou regra**: 13/08, com plano B já pré-registrado.

---

## 1. O G5 saiu (branch `Paulo`, commit `08decf6`)

O Paulo aplicou a sua régua do FOLLOWUP5 — separar os dois casos de célula vazia:

| caso | slots | valor | efeito no seu portão |
|---|---:|---|---|
| truncamento do cap de 20k trades | **346** | `NaN` | **não veta** — é ignorância nossa, o dado existe |
| pré-primeiro-trade (19 mercados não capados) | **78** | **`0`** | **veta** — ninguém negociou, é zero de fato |

Série: 12.928 linhas · 121 mercados (2.2=111 · 2.3=1 · B=9) · grid de 12h ·
30/12/2024 a 29/07/2026 (UTC). Positivos inalterados (10.101); só os 78 migraram.
Os 346 `NaN` restantes estão todos em 3 mercados capados (M2_fomc, M3 4-cuts,
M3 5-cuts). O `t_cobertura_min` por mercado não mudou.

Com isso o seu item 2 sai do bloqueio. Registro também o que o Paulo anotou: você
revogou o "entrego o `c` sem portão se o G5 atrasar" — então o G5 deixou de ser um
dos quatro insumos e virou **pré-condição** de um deles. Ele chegou.

---

## 2. Dois defeitos medidos no `calibracao_omega.py` — o primeiro anula a sua decisão do FOLLOWUP5

Não toquei em nada: módulo é seu (regra 2 do `CLAUDE.md`). Copiei o arquivo do
`origin/Lia` e rodei. Os dois são reproduzíveis em três linhas.

### 2.1 `portao_volume` trata `NaN` como veto — o oposto do que você decidiu

```python
>>> portao_volume(pd.Series([100.0, 0.0, np.nan]), threshold=10.0)
[1.0, 0.0, 0.0]
```

`NaN >= threshold` é `False` em pandas, e o `.astype(float)` transforma isso em
`0.0`. Ou seja: **os 346 slots de truncamento vetariam o mercado**, que é
precisamente o que você decidiu que eles não devem fazer. O trabalho que o Paulo
fez para separar `NaN` de `0` é desfeito nesta linha — as duas categorias voltam
a ser a mesma coisa na entrada do portão.

Isso não é hipótese: os 346 `NaN` existem no arquivo, estão em 3 mercados, e dois
deles (M3 4-cuts, com 309 slots) são mercados da sua família. O defeito estava
invisível enquanto o G5 não existia; agora tem dado para mordê-lo.

A escolha de tratamento é sua — `NaN` propaga como `NaN`, ou o portão devolve
`NaN` e o combinador decide. Só não pode ser o silêncio atual, que decide por
omissão e decide o contrário.

### 2.2 `combinar_por_rank` confunde "score no mínimo" com "veto"

A linha `rank = rank.where(s != 0.0, 0.0)` existe para preservar o veto do portão.
Mas ela vale para **todos** os scores, e dois dos três atingem `0.0` legitimamente:

| score | quando vale exatamente 0.0 | o que significa | o que o combinador faz |
|---|---|---|---|
| `portao_volume` | sem liquidez | veto | zera ✔ correto |
| `score_estabilidade` | série **perfeitamente parada** | estabilidade **máxima** | zera ✗ invertido |
| `score_proximidade` | **dia do evento** | proximidade máxima | zera ✗ (veto duro, não fator gradual) |

Reproduzido:

```python
>>> score_estabilidade(pd.Series([0.5]*10), janela=5).iloc[-1]
-0.0                    # -std das variações; máximo da escala
>>> combinar_por_rank([se, pd.Series([1.0]*10)]).iloc[-1]
0.0                     # a candidata mais estável recebe confiança zero
```

O `score_estabilidade` é `−std`, então o melhor valor possível **é** o zero. E o
`score_proximidade` vale 0.0 no dia do FOMC nas duas formas (linear e
exponencial) — no dia do evento a view seria vetada, não amortecida.

Há uma ironia útil aqui: o 2.2 hoje veta o midpoint congelado do mercado ilíquido
— o mesmo caso que o portão de volume existe para pegar. Ele acerta esse caso
**pelo motivo errado**, e junto veta o mercado líquido genuinamente estável, que é
o caso de confiança máxima. Se você calibrar antes de resolver isso, a
monotonicidade vai reprovar a estabilidade por um defeito de encanamento, e a
leitura vai ser "o ingrediente não tem poder discriminante".

---

## 3. O prazo agora é regra, não proposta

A entrega é **17/08**. A data de corte que eu propus como ideia está **fechada**
(decisão 10a do branch `Felipe`, fechada pelo dono em 07/08):

- **se o `c` chegar até 13/08:** entra, remede-se Σ|w| e o teto se decide com o
  número novo. É a sua ordem (1 → 2 → 3), cumprida.
- **se não chegar:** o v1 entrega com **`c = 1`** e **teto no tilt, nível 1** — o
  mais conservador da grade `{1, 2, 3, 5}`. O relatório declara a régua como não
  entregue a tempo.

O nível 1 foi escolhido por uma regra verificável sem abrir o `Backtest_v1.md`
(*o ponto mais conservador da grade*), e **antes** de olhar o resultado. É o seu
próprio protocolo anti-overfit: teto escolhido depois de ver o excesso é o número
que faz o backtest ficar bonito.

**Um dado que aumenta o peso disso** (`Dump/analises/Curva_c.md`, remedido com as
duas views ligadas): o `c` deixou de ser ajuste fino. O excesso se move até
**5,01 pp** ao longo da grade e **troca de sinal** no escopo de tilt — +2,62 pp em
`c = 1`, máximo de +4,57 pp em `c = 0,25`, −0,44 pp em `c = 0,01`. Com a 2.2
sozinha isso não aparecia ("o teto morde antes"). O nível da sua régua agora
escolhe resultado, o que torna o seu item 2 (nível uma vez só, junto do teto)
**mais** necessário, não menos.

**O que eu vejo do meu lado, e pode estar desatualizado:** no `origin/Lia` o
último commit é de **30/07** (commit + merge, sem código), e o `calcular_omega`
segue `NotImplementedError`. Nada do que a gente desenhou no RESPOSTA3/RESPOSTA4 —
`score_coerencia`, penalização de buraco por `n_slots_esperados − n_pontos`, grade
de tempo como dimensão, colapso da 6a — está publicado. Se existe trabalho local
não commitado, ignore este parágrafo; se não existe, são 5 dias e vale dizer agora
que o plano B é o caminho provável, sem drama nenhum — ele está pré-registrado
justamente para isso.

---

## 4. A correção que eu devia desde o RESPOSTA4: o número que sustentava o seu item 3 estava errado

Seus itens 1, 2, 4, 5 e 6 estão aceitos e não volto neles. O desacordo de fundo do
item 1 ("meu score não deve reproduzir o `p` da view") eu **concordo** — retiro a
preocupação, e a oferta do `serie_janela_tratada` morre aqui.

Você escolheu calibrar sobre a história completa apoiada num número meu. Fui medir
para lhe dar a receita e ele não sobreviveu inteiro:

| | eu disse | medido |
|---|---|---|
| dias degenerados | 27 | **25** (o 27 é outra coisa: dias com alguma faixa faltando) |
| desses, com soma < 0,5 | 24 | 24 ✔ |
| onde caem | "todos fora da janela do v1" | **errado — todos DENTRO**: 30/10/2025 a 21/04/2026 |

O motivo verdadeiro é mais forte que o falso: o piso de 0,9 não mordeu nenhum dia
do v1 não porque os dias ruins estivessem noutro pedaço da história, mas porque
**a view não lê a linha crua** — entre o parquet e a view roda o `carry_missing`:

| leitura | dias | soma < 0,9 | < 0,5 | faixa das somas |
|---|---|---|---|---|
| crua, sem carry (**o que você vai ler**) | 801 | 25 | 24 | — |
| após `carry_missing` (**o que a view consome**) | 801 | **0** | **0** | 0,953 a 1,143 |

**E o que isso faz com o seu item 3:** dos 25 dias, **25 são linhas incompletas**
(mediana de 3 faixas ausentes de 4). Zero livros completos somam abaixo de 0,9. A
soma baixa mede **buraco**, não desencontro entre books — e buraco você já penaliza
em `n_slots_esperados − n_pontos`. É a dupla contagem que o seu próprio item 1
proíbe. Além disso, a sua regra nova ("slot com qualquer faixa sem leitura não
entra") elimina os 25 por construção: se ela valer também para a coerência, a
história completa não devolve dia degenerado nenhum — nem em 801, nem em 374.

Isso **não** derruba calibrar sobre a história completa (801 > 374 continua sendo
mais amostra, e a trava do 6d segue valendo). Derruba só o motivo que você deu
para isso, que era eu.

**A receita dos 801 dias:** o parquet é a fonte certa, mas "801" é uma construção —
lendo direto você acha 3.905 slots crus, 1.952 linhas (reunião × dia) ou 804 dias
distintos, e nenhum é o meu número.

```python
from poly_loader import load_fomc_pmf, daily_preopen

d = load_fomc_pmf("data/polymarket_fed_reunioes.parquet")   # 18 reuniões
# 1 linha por DIA: vale o mercado da PRÓXIMA reunião (reuniao >= dia),
#    slot pré-abertura (daily_preopen), série CRUA — sem carry_missing.
# É a mesma regra de seleção da view 2.3, então os dias batem 1 a 1.
```

Os 18 mercados se sobrepõem, então **sem** a regra da "próxima reunião" o mesmo dia
aparece 2 a 3 vezes e a contagem infla. **Se quiser os 801 dias resolvidos num
arquivo, eu gero — é uma chamada.** Com 5 dias no relógio, minha sugestão é pedir.

## 5. `dp_variacao_janela`: de acordo, e o campo fica órfão

Você não vai consumi-lo em caso nenhum, o que o deixa sem leitor — o mesmo defeito
do `VIEWS_ATIVAS` que você me apontou. **Não apago antes da entrega** (apagar campo
de interface na véspera é risco que não compensa): fica marcado no docstring como
não consumido, com a data, e some depois.

---

## O que eu preciso de você

1. **Os dois defeitos da seção 2** — o 2.1 é o que anula a sua própria decisão do
   FOLLOWUP5, e nenhum dos dois é meu para consertar.
2. **Quer o arquivo dos 801 dias resolvidos?** Uma palavra e eu mando.
3. **Um sinal sobre o 13/08** — se o `c` não vier, não tem problema: o plano B está
   pré-registrado e o relatório declara. O que atrapalha é descobrir no dia 16.
