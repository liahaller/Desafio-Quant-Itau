# Resposta ao Paulo — os dois entregáveis entraram, e o que eles mudaram

**De:** Lia · **Para:** Paulo · **Data:** 2026-08-10
**Sobre:** `PEDIDO_Paulo_G5_fomc.md` e `PEDIDO_Paulo_cpi_realizado.md`

Os dois entraram no mesmo dia em que chegaram e **destravaram exatamente o que
prometiam**. Abaixo o que conferi, o que os números disseram, as respostas às
suas quatro perguntas e um achado que saiu de uma divergência de contagem entre
nós dois — que era o sintoma de um mês contado em dobro.

---

## 1. G5 do FOMC — conferido item por item, tudo bate

| O que verifiquei | Resultado |
|---|---|
| `conditionId` em comum (G5 2.3 × parquet) | **76 de 76**, 0 nulo |
| Casamento slot-a-slot com `floor("12h")` | **0 órfão nos dois sentidos** (16.321 pares) |
| Slots de PMF do loader com linha de volume | **3.905 de 3.905** |
| Separação `NaN` × `0` preservada | sim (9.090 / 445 / 6.803) |
| View 2.2 e view B | **inalteradas**, como você disse |

O detalhe que você destacou — o grid vir do próprio parquet que a view consome
— é o que fez o trabalho ficar trivial do meu lado. Não precisei reconciliar
grade nenhuma.

**Uma nota de encanamento, não é problema seu:** o `evento_id` é string no
parquet e o `load_fomc_pmf` devolve inteiro. Um `.map()` direto dá índice vazio
sem erro. Converti explicitamente e deixei um `raise` se algum `conditionId`
não casar, para não haver junção silenciosamente vazia de novo.

### O que o G5 do FOMC destravou

**A ressalva que estava aberta desde 09/08 caiu.** O ingrediente mais forte da
régua (estabilidade) estava sob suspeita de ser artefato do midpoint congelado
— mercado sem negociação parece "estável" e é fácil de prever, os dois pelo
mesmo motivo. Com o portão, o teste condicional roda na 2.3:

- spearman **−0,4005** em todos os slots → **−0,3960** só nos slots com
  negociação. Delta 0,005.
- O mecanismo **existe**: slots sem negociação têm erro futuro médio 4× menor
  (0,0037 × 0,0147). Mas são **24 contra 1.139** — real e irrelevante em volume,
  que são coisas diferentes.

**A rodada completa da 2.3 (4 ingredientes, a primeira) confirmou a régua sem
mudar nada:** variação total melhor que |ΔE|, coerência com sinal correto,
portão reprovado como score (e mantido como veto pela semântica), proximidade
reprovada de novo com o sinal invertido. A regra do que eu faria se ela
*discordasse* ficou registrada e commitada **antes** de a rodada existir
(`95ebd08`), justamente para essa confirmação valer alguma coisa.

### Uma regra minha que o seu cap de 20k obrigou a criar

Seu aviso ("não somar `NaN` como `0`") tinha uma consequência a mais do que o
texto dizia. **908 dos 3.905 slots misturam faixa truncada com faixa medida** —
situação que não existe na 2.2, onde nada bateu o cap. Somando `NaN` como
ausente, **6 slots** ficariam com soma zero e **seriam vetados**, afirmando
"ninguém negociou" onde parte é desconhecida.

Adotei: **faixa `NaN` contamina o slot inteiro** (não veta, não julga). São 6
slots de 3.905, mas é a diferença entre respeitar e furar a separação que você e
eu combinamos em 07/08. Está em `agregar_volume_slot`, usada pela calibração e
pelo exportador, com teste. **A 2.2 saiu idêntica à publicada** — conferido, não
suposto.

---

## 2. CPI realizado — as suas quatro perguntas, respondidas

Antes: obrigada por ter separado *first-print* de revisado por conta própria e
por ter mostrado os dois meses em que a escolha muda o bucket. Isso não estava
no pedido com essa clareza e é exatamente o que o teste precisava.

**1. out/2025 → fica FORA do teste, e o fato vai reportado à parte.**
O UMA resolveu 0,3%, mas resolução de oráculo não é medição independente — e é
justamente o mês em que nenhum número do BLS existe para sustentá-la. A regra
que fixei na 2.3 é que **o desfecho não sai do mercado**; aceitá-lo aqui
reintroduziria a circularidade que o alvo existe para remover, no mês mais
anômalo da amostra. Registrei o desfecho do UMA numa nota separada do relatório,
porque o fato é interessante por si: há mercado no nosso universo cujo resultado
existe só como decisão de oráculo.

**2. nov/2025 → também fora**, pelo mesmo motivo e sem hesitação: sem a base de
outubro não há MoM reproduzível, e o único 0,3% disponível vem do mercado.

**3. dez/2024 e jan/2025 (SA por inferência) → aceitos, e testei se importam.**
Sua inferência usa o bucket resolvido para escolher a série, o que é levemente
circular — então rodei **com e sem os dois**. Sem eles a estabilidade vai de
−0,047 para −0,065 e a coerência de +0,002 para −0,025: muda pouco e sempre para
o lado certo. A ressalva está registrada como **imaterial, medida**, não como
"provavelmente não importa".

**4. jul/2026 → congelado sem ele.** O mercado ainda está aberto, sem bucket
vencedor, então não entraria de qualquer forma. Se o valor de 12/08 for útil
depois, ele entra sem refazer nada.

**Sobre o "19 vs 18":** você está certo, são 18. Mas a divergência não era
contagem — ver §3.

### O que o CPI realizado destravou, e o limite honesto dele

Derivei o bucket a partir do seu `sa_fp_1dec` e da grade de cada mercado (com
as pontas abertas pela decisão 11b) e comparei com a resolução: **casa em 15 de
15**, incluindo as três pontas abertas. A limitação "a verificação de não
circularidade existe numa view só" **saiu do relatório**.

O que preciso te dizer com clareza, porque é o resultado menos confortável do
dia: **o alvo por desfecho tem pouco poder na 2.2**. Os coeficientes caem de
−0,45 (2.3) para −0,05/−0,13. Fui atrás do porquê e o mecanismo é medível:

| | mediana de `p` no bucket que resolveu (último slot) | acima de 0,90 |
|---|---|---|
| 2.3 (FOMC) | **0,97** | 83% das reuniões |
| 2.2 (CPI) | **0,39** | 7% dos meses |

O mercado de inflação **não converge** antes da publicação. Então "massa alocada
fora do resultado" mede sobretudo o tamanho da surpresa do mês — propriedade do
evento, não da qualidade do livro naquele instante. **É limitação do alvo, não
da régua**, e está declarada assim.

O que sobrevive é útil: a variação total mantém o sinal correto nos 4 cortes e a
|ΔE| **inverte** nos 4. As duas empatavam na 2.3, e a escolha da régua tinha sido
por parcimônia, sem evidência. Este é o único corte que as separa — e separa a
favor da que já estava escolhida. Evidência fraca em magnitude, registrada como
tal.

---

## 3. ⚠️ O achado: `M1_cpi_monthly` é o mesmo mercado que `july-inflation-monthly`

Sua contagem dizia 18 e a minha 19. Em vez de corrigir o número, fui ver quem
era o extra:

- mesmos **6 tokenIds**;
- mesmos **56 slots**, mesmo período (16/07 a 12/08/2025);
- **diferença máxima 0,0** entre as células.

Não são mercados parecidos: é o mesmo contrato sob dois rótulos, e **jul/2025
entrava duas vezes na minha calibração da 2.2** (4,7% dos slots da grade de 12h).

**Impacto medido:** removida a duplicata, todas as candidatas melhoram
ligeiramente (a principal, de −0,4615 para −0,4717) e **nenhuma ordenação muda**
— a régua fica de pé. A validação de ponta a ponta passa de 601 para 573
decisões. O `c_por_decisao.csv` **não estava contaminado**: o exportador já
filtrava por casamento com o calendário de releases, e o `M1` nunca casava.

**Do seu lado não há nada a corrigir** — o G5 casa por nome de arquivo e está
consistente; o `data/raw` guardar o mesmo mercado sob dois rótulos é histórico
de marco, não erro de dado. Estou avisando porque **quem varrer o
`clob_exploracao` por prefixo vai contar um mercado a mais**, como eu contei. Se
algum outro script do pipeline faz essa varredura, vale conferir.

Do meu lado, a identidade de um mercado passou a ser o **tokenId**, nunca o nome
do arquivo.

---

## 4. Estado dos seus dois pedidos e o que não preciso

- **`PEDIDO_Paulo_G5_fomc.md` — atendido, fechado.** Nada pendente.
- **`PEDIDO_Paulo_cpi_realizado.md` — atendido, fechado.** As quatro perguntas
  estão respondidas acima; nenhuma delas exige trabalho novo seu.
- **jul/2026:** se o release de 12/08 sair antes da reunião e for barato, mando
  o número entrar; se não, não faz falta. **Não é pedido.**
- **Valor do CPI para os meses do *shutdown*:** não peça, não existe. A decisão
  de excluí-los é minha e está registrada.

Uma coisa que vale a pena você saber, porque afeta leitura de resultado e não só
o meu módulo: com o portão, a **2.3 continua quase invariante à régua** (1,2% das
decisões vetadas por liquidez, contra 4,0% na 2.2). Antes eu não podia separar
"mercado bom" de "falta de portão". Agora dá: o mercado do FOMC é genuinamente
mais bem comportado — livro que fecha, distribuição que se move pouco. Isso vai
à reunião de 13/08 como argumento de que a curva do nível precisa sair **por
view**.

— Lia
