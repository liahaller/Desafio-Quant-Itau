# Conclusões sobre a camada tática — sessão 25 (2026-08-11, Felipe)

> 🟢 **SUPERADO em parte na sessão 27 (2026-08-11).** A camada tática **entrou
> na entrega**, com duas sleeves transversais (M4 recessão, M9 Câmara) —
> **D28**, `src/tatica_sleeves.py`, `Dump/analises/Camada_tatica_v2.md`.
>
> **O que este arquivo acertou e continua de pé:** o eixo 1 da seção 5 (*livro
> transversal em vez de direcional*) foi exatamente por onde a camada saiu do
> zero, e o eixo 2 (*mercado com fluxo de notícia*) segue barrado por cobertura.
> A conclusão da seção 1 — *"o sinal tem tamanho, não se encadeia e não antecipa
> o retorno dos ativos"* — vale para o sinal **direcional**; no livro **neutro**
> ele antecipa, e é essa a diferença que a camada explora.
>
> **O que este arquivo diz e NÃO vale mais:** a seção 4 lista a *1.1 PEAD* como
> "intocada" e travada pela decisão 5. A decisão 5 **fechou** e a 1.1 foi
> **medida e reprovada** fora do Fed (D28.c). A seção 7 lista a decisão 5 e a
> D24 como travas — as duas **fecharam** (D28, itens 7 e 2).
>
> Nada abaixo foi reescrito: fica como o registro do que se sabia ao fim da
> sessão 25.

Escrito para a **próxima sessão**, cujo objetivo declarado pelo dono é *achar uma
nova forma de ativar a camada tática*. Este arquivo diz o que ficou medido, o que
ficou morto **com número**, o que nenhum teste tocou, e o que teria de ser
verdade para uma tentativa nova não repetir as treze anteriores.

**Nada aqui fecha decisão.** O registro formal está na **D26** do
`Decisoes_pendentes.md`.

---

## 1. A conclusão de uma frase

O diagnóstico que o projeto carregava — *"falta sinal, não dimensionamento"* —
estava **certo na conclusão e errado na causa**, e a diferença muda o que se
tenta a seguir.

- **Errado:** "o sinal do Polymarket é pequeno demais para operar."
- **Certo:** **o sinal tem tamanho; ele simplesmente não antecipa o retorno dos
  ativos.**

Isso é mais forte que o diagnóstico antigo, porque fecha a porta por medição em
vez de por limitação instrumental — e porque elimina a saída fácil de "então
vamos olhar com mais resolução".

---

## 2. O que esta sessão mediu

Três artefatos novos, encadeados. Cada um só existe porque o anterior derrubou
uma premissa que estava sendo tratada como fato.

| artefato | pergunta | script |
|---|---|---|
| `Dump/analises/Premissa_G1.md` | o veredito da D17 depende do horizonte e da família de mercado? | `scripts/premissa_g1.py` |
| `Dump/analises/Premissa_tendencia.md` | o sinal acumulado é tendência (negociável) ou convergência (inútil)? | `scripts/premissa_tendencia.py` |
| `Dump/analises/Gate_M3_acumulado.md` | o candidato que sobreviveu passa no G2 e no G3? | `scripts/gate_m3_acumulado.py` |

Nada em `src/` foi tocado. `Gate_sleeves.md` saiu com **hash idêntico** depois da
extração do `referencias_g3` — a verificação está no `LOG.md` da sessão.

---

## 3. O que ficou morto, com número

### 3.1 A generalização da D17 — derrubada (mas o veredito dela sobrevive)

O `Gate_sleeves.md` afirma: *"qualquer sleeve que leia Δ de PMF de um dia para o
outro está condicionando em ruído de discretização"*. A frase vale para o `k` que
a D17 mediu, **não para a série**:

| | k=1 | k=3 | k=5 | k=10 | k=20 |
|---|---|---|---|---|---|
| M3 trajetória do Fed | 0,5× | **1,2×** | 1,7× | 2,9× | 3,7× |
| C1b reunião do FOMC | 0,2× | 0,5× | 0,9× | **1,6×** | 2,4× |

O tick é fixo e o erro de discretização no incremento fica preso em ~1 tick por
mais que `k` cresça, enquanto o movimento verdadeiro acumula. **Acumular resolve
o problema de tamanho.** Só isso — ver 3.3.

### 3.2 Momentum e velocidade de ajuste — sem hipótese

Não é "não testamos": é **tese contrariada pelo dado**, que é o critério de
reprovação da régua D22.

- **Variance ratio do M3: 0,97 a 1,18** ao longo de toda a grade. Passeio
  aleatório. O crescimento do item 3.1 é ruído se acumulando — não é tendência.
- **Autocorrelação ex-ante (deriva removida pela média expansiva): nenhum
  |t| ≥ 2** em nenhum horizonte (o maior é t +1,6 em k=3).

As duas candidatas leem "o movimento da crença para prever o próximo movimento
da crença". Esse encadeamento não existe. **A *1.2 momentum* e a *velocidade de
ajuste* perdem a razão de ser** — juntas, metade do estoque nunca medido.

⚠️ **Erro meu, corrigido dentro da sessão:** eu havia lido o crescimento da
mediana como "mais rápido que √k, logo tendência". Era artefato da mediana — em
k=1 a maioria dos dias tem variação zero, o que prende a mediana perto do zero e
faz qualquer acúmulo parecer explosivo. O variance ratio é a medida honesta e diz
1. Quem reabrir isto: **não use mediana para julgar acúmulo.**

### 3.3 O M3 acumulado — reprovado no G2, e piorando no G3

Era a única série do dado entregue com **cobertura** (210 pregões) e **dispersão
acima do tick** ao mesmo tempo, e a única **não consumida por nenhuma das quatro
views vivas**. Premissa herdada da D17 palavra por palavra ("crença anda para
mais afrouxamento → SPY e TLT sobem"), sem reescrita depois de ver o k=1 falhar.

| lookback | μ (bps/dia) | G2 | G3 maior \|corr\| |
|---|---|---|---|
| k=1 | SPY −3,87 ❌ · TLT +0,03 ✅ | ❌ | −0,19 |
| k=3 | SPY −0,95 ❌ · TLT −0,78 ❌ | ❌ | −0,32 |
| k=10 | SPY −0,92 ❌ · TLT −1,43 ❌ | ❌ | −0,36 |
| k=20 | SPY +1,38 ✅ · TLT −1,01 ❌ | ❌ | −0,42 |

**Nenhum horizonte passa**, e pela D2b não se inverte. Pior: **o G3 degrada
exatamente onde o G1 melhora** — quanto mais dias o Δ da crença soma, mais ele
vira a entropia que a view 15b já lê (−0,19 → −0,42). Os dois critérios apontam
para lados opostos do mesmo eixo, o que fecha a janela por cima e por baixo.

---

## 4. O que NENHUM teste desta sessão tocou

Todas as perguntas desta sessão são sobre o **sobe-e-desce diário** da crença.
Duas coisas ficam de fora disso, e são o estoque real da próxima tentativa:

- **1.1 PEAD — intocada.** Lê a **resolução** do mercado, não o Δ diário. Nem o
  G1 (que é sobre movimento diário), nem o variance ratio, nem a autocorrelação
  dizem qualquer coisa sobre ela. Continua travada pela **decisão 5**, que está
  🔴 **aberta e vazia**: sem definição operacional de "surpresa" não existe sinal
  a construir. **É decisão humana, não script** — e é o gargalo número um.
- **3.2 event-driven — não medida.** O gatilho é o **salto** da probabilidade,
  que é o padrão com maior chance de aterrissar no gap de abertura (a parede que
  já derrubou a 2.4, a C, a E e o gap de fim de semana). Mede-se em uma linha
  antes de escrever módulo: **quanto do movimento sobra do fechamento do dia do
  salto em diante?** Se sobrar zero, morre como o C3 morreu.

---

## 5. Para a próxima sessão: o que teria de ser verdade

Uma tentativa nova só evita virar a 14ª entrada da mesma tabela se mudar pelo
menos uma destas premissas — as três primeiras já estão medidas contra, então
mudar significa **mudar de eixo**, não insistir.

| premissa da camada até aqui | estado | o que sobra |
|---|---|---|
| o poly está **errado** sobre o Fed | ❌ D16: surpresa mediana 0,52 bps em 17 reuniões | procurar onde ele NÃO é preciso |
| o poly ajusta em **rampa** (a crença leva dias para assentar, e dá para entrar no meio do movimento) | ❌ esta sessão: VR ≈ 1, ρ ex-ante ≈ 0 — ele reprecifica **de uma vez** | — |
| **acumular horizonte** cria sinal | ❌ esta sessão: resolve tamanho, não previsão | — |
| a informação é **negociável** quando aterrissa | ⚠️ nunca medido para a 3.2 | teste do resíduo pós-gap |
| o sinal está no **nível/forma**, não no movimento | ⚠️ parcialmente ocupado pela 15b | famílias que a 15b não lê |
| o gatilho é a **resolução**, não o repreçamento | ⚠️ intocado (1.1) | destravar a decisão 5 |

**Três eixos que esta sessão abriu e não fechou** (nenhum é recomendação — são as
únicas células vazias que sobraram):

1. **Livro transversal em vez de direcional.** Toda sleeve medida operou SPY/TLT
   direcional — os instrumentos mais eficientes do universo e os mesmos que as
   views já tiltam. O único lugar onde este projeto achou t-stat de verdade foi
   **transversal** (XLF +3,21, XLP −8,96 no estudo do gap). Long/short de setores
   não exige saber **se** o Fed corta, e é ortogonal por construção a quem tilta
   o índice. **Sobrevive ao poly estar certo** — que é a única premissa que
   nenhum teste derrubou.
2. **Mercado com fluxo de notícia.** O corte medido não é "Fed × não-Fed", é
   **se existe notícia a que o preço responda**: Irã 1,2× e 4,0× já em k=1,
   tarifas 3,5×; enquanto recessão 0,7×, Trump 0,5× e Câmara **0,0×** ficam
   junto do Fed. ⚠️ **Mas cobertura e dispersão são quase disjuntas no dado
   entregue** — o que se mexe dura 3, 9, 29 ou 59 pregões. Isto é pedido de
   dado ao Paulo, não desenho.
3. **1.1 PEAD**, se e quando a decisão 5 fechar.

---

## 6. Armadilhas — o que não repetir

- **Rodar a linha do gate ANTES de abrir o editor.** Continua sendo a regra mais
  cara já aprendida (a D16 custou 400+ linhas e 11 testes para descobrir o que o
  gate responde em uma linha). Esta sessão inteira produziu **três artefatos e
  zero módulo**.
- **Declarar a premissa por escrito antes de estimar, e herdá-la sem reescrever.**
  O G2 do M3 usou a premissa da D17 palavra por palavra. Reescrevê-la depois de
  ver o k=1 falhar teria destruído o único mecanismo que faz do G2 um teste em
  vez de racionalização.
- **Não usar mediana para julgar acúmulo** (ver 3.2). Use variance ratio.
- **Reindexar em dias úteis antes de qualquer `diff(k)`.** Sem isso, "k" anda
  leituras, não pregões — e o dado tem buracos de 24/36/48h. É por isso que o k=1
  desta sessão dá SPY −3,87 contra os −4,20 do `Gate_sleeves.md`: mesmo veredito,
  dígito diferente, e a diferença é a correção.
- **Prosa gerada dos números, nunca escrita à mão.** Dois parágrafos que eu havia
  redigido foram derrubados pela própria checagem embutida antes de virar
  artefato: um afirmava reversão dominante (o placar real era 4×3, com um
  positivo de n=216), outro dava o estoque de candidatos por esgotado (ignorava a
  1.1). **Registro que envelhece não levanta exceção** — é a quarta ocorrência
  deste modo de falha no projeto.

---

## 7. O que trava a ativação, independente de achar sinal

Nenhuma é técnica e nenhuma se resolve em script:

- **Decisão 5** 🔴 — aberta e vazia. Destrava a 1.1.
- **D24** 🔴 — o portão de qualidade do poly vale para views e **não** para
  overlays. Uma sleeve que leia mercado com PMF degenerada passa livre pelo veto
  que mata a view equivalente. Vira pergunta real **no momento em que alguém
  reativar a tática** — que é exatamente a próxima sessão.
- **12c** 🟢 — a camada está desligada no v1. ⚠️ A âncora de tamanho da D16
  (`inv(δΣ)·μ`, **zero parâmetro livre**) segue de pé e sem uso, então o motivo
  que matou a 12c não se repete: **não volte a introduzir `orcamento`.**
- **Reabertura de escopo** da camada — decisão de grupo (a "decisão 10", cujo
  ponteiro no `CLAUDE.md` aponta para o vazio desde a reorganização do arquivo).

---

## 8. Se nada passar

A conclusão negativa **é entrega**, e mais forte que a antiga: não é "não
tentamos", nem "faltou dado" — é *o sinal do Polymarket tem tamanho mensurável,
não se encadeia, e não antecipa o retorno dos ativos no universo e na janela
medidos*. Isso vale relatório tanto quanto uma sleeve que funcionasse, e o
caminho até aqui está inteiro em artefato reproduzível.
