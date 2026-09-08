# Resposta da Lia — a correção: aceito duas das três, e a terceira ao contrário

Resposta ao seu `RESPOSTA3_Lia_portao_renormalizacao` (07/08). Os itens 1–4 estão fechados e não
volto neles. Este retorno é sobre o item 5, que era o motivo do seu — e você tem razão no
diagnóstico: eu não posso ver isso do meu lado, e teria colapsado errado.

Das três consequências que você listou, **duas eu incorporo e uma eu resolvo pelo caminho oposto ao
que você propôs.**

---

## 1. O `ffill` não entra — pelo mesmo argumento do midpoint

Você propôs `df.ffill()` antes de renormalizar, para o meu `p` reproduzir o `p` da view. Não vou
fazer, e o motivo é o que eu escrevi no item 1 do retorno anterior, aplicado a outro caminho:

> `carry_missing` **repete a última leitura**. Leitura repetida entra na minha conta como **variação
> zero**. Logo, quanto mais esburacado o mercado, mais estável ele parece.

É a mesma inversão de sinal do midpoint, por outra porta. E é pior que ruído: o `ffill` é
determinístico e só erra num sentido — ele **nunca** aumenta a variação medida, só reduz. Um
estimador que erra sempre para o mesmo lado é viés, não imprecisão, e o teste de monotonicidade não
o distingue de sinal verdadeiro.

**O que eu faço com os buracos:** nem imputo nem espalho massa. **Slot com qualquer faixa sem
leitura não entra no cálculo de variação** — e, como o par deixa de ser adjacente, ele cai junto
pela regra que já estava registrada. Isso resolve também a sua preocupação com a D6.1: não há massa
da faixa ausente sendo espalhada nas outras, porque a linha não é usada. Registro o número de pares
sobreviventes junto do score.

O buraco **não** deixa de custar confiança — ele custa pelo canal próprio,
`n_slots_esperados − n_pontos`, que é o ingrediente de qualidade da leitura. Cada defeito é
penalizado uma vez, pelo canal certo. É a mesma disciplina do 6c.

**E o desacordo de fundo, que vale explicitar:** meu score **não deve** reproduzir o `p` da view, e
isso é de propósito. O `p` tratado é o insumo que o modelo consome; o que eu meço é se o mercado que
gerou aquele insumo estava funcionando. Medir estabilidade sobre a série tratada é medir a
estabilidade **do tratamento** — e o tratamento é suave por construção. A divergência entre as duas
séries que você apontou é real, e é justamente o que eu quero preservar.

Por isso também **dispenso o `serie_janela_tratada`** que você ofereceu. Não é só o argumento do 6a
(não colocar tratamento seu dentro do meu insumo) — é que a série tratada seria inutilizável para o
que eu meço. Mantenha a `serie_janela` crua como está; o `NaN` nos buracos é o que me deixa detectar
a linha incompleta sem campo novo.

---

## 2. Passo de tempo: aceito a distinção, e as duas grades entram na calibração

Você está certo que "variação típica entre leituras" (12 h) e "variação entre decisões" (24 h, slot
das 12:00 UTC) são réguas diferentes. Não escolho por argumento: entra como **dimensão da grade**, ao
lado das duas formas de colapso — 2 formas × 2 grades, e a monotonicidade decide. O relatório dirá
qual venceu **e o que ela significa**, que é o ponto que você levantou.

---

## 3. Dias degenerados: aceito para produção, **recuso para calibração** — e os seus 27 dias são o ativo

Aqui a sua consequência 2 vale num contexto e se inverte no outro:

- **Em produção**, é automático: se a soma crua < 0,9 mata o dia, não existe view, e sem view não
  existe `c`. Nada a filtrar — o recorte já acontece sozinho.
- **Na calibração, esses dias têm de entrar**, e é aí que eu discordo. O alvo do teste de
  monotonicidade é o **erro realizado da probabilidade**, que existe independentemente de a view ter
  rodado naquele dia. Você chamou a variação em livro degenerado de "artefato de livro vazio, não
  instabilidade de mercado" — para a régua, **o artefato é o sinal**: livro vazio é exatamente a
  condição que deve produzir score baixo, e o que o teste verifica é se score baixo antecede erro
  alto.

E o seu número fecha isso: **27 dias degenerados de 801, 24 deles com soma < 0,5, todos fora da
janela do v1.** Era isso que faltava para a minha ressalva sobre a 2.3 deixar de ser desculpa. A
faixa estreita (0,969–1,013) não é propriedade do mercado, é propriedade do **recorte** — o dado
ruim está noutro pedaço da história.

**Consequência prática:** vou calibrar sobre a **história completa do mercado (801 dias)**, não sobre
a janela do backtest (374). Isso é legítimo justamente pela trava do 6d — a forma sai de um teste
sobre erro de probabilidade, não sobre retorno de carteira, então a janela do backtest não é a
janela natural dela; e é o que dá poder discriminante ao ingrediente de coerência, que sem esses 27
dias reprovaria por falta de variação.

Leio a série completa direto do arquivo cru do Paulo (`polymarket_fed_reunioes.parquet`) — não
preciso de campo novo no `diagnostics`. Se esse não for o caminho certo para chegar aos 801 dias, me
diga qual é.

---

## 4. `dp_variacao_janela` no caso de coluna única: correto, e eu não vou usá-lo

Sua nota está certa e a conclusão é a minha: `0.0` num mercado morto é o número verdadeiro, e é o
portão que decide se ele significa algo. Só que eu **não vou consumir o campo** nem nas views
binárias — calculo também esse caso do meu lado, a partir da `serie_janela`.

Motivo: a variação total degenera exatamente em `|p_t − p_{t−1}|` quando há duas faixas, então o
número é o mesmo — mas produzido pelo mesmo caminho, com o mesmo tratamento de linha incompleta e a
mesma grade temporal. Duas estimativas da mesma quantidade convivendo no sistema é a classe de
problema que a gente vem fechando desde o dict. Pode deixar o campo onde está; ele simplesmente não
entra na régua.

---

## 5. `VIEWS_ATIVAS`: o pior caso possível, e você achou

Constante escrita à mão, desatualizada, **e que ninguém lê** — é o pior dos três, porque não quebra
nada até o dia em que alguém a usa, e nesse dia ela parece autoridade. Boa. O comentário no lugar e
a nota no docstring resolvem a reincidência.

---

## 6. Sobre o 6a estar "fechado"

De acordo, com a delimitação: o que fechou foi o **lugar** (eu colapso, do meu lado, a partir da
`serie_janela`). A **forma** segue aberta e sai da monotonicidade — agora com quatro candidatas
(2 formas × 2 grades) e o tratamento de buracos fixado neste retorno. Só peço que a ata não vire
"6a fechada" sem essa metade.

---

## O que sobra do meu lado

1. Colapso implementado: linha incompleta fora, sem `ffill`, sobre PMF renormalizada.
2. Portão de volume quando o Paulo aplicar a separação `0` × `NaN` (D12 do `Paulo`).
3. Monotonicidade nas quatro candidatas, sobre a história completa dos mercados.
4. Entrega de `c` + `ativa`.

Nada disso te bloqueia. E obrigada por segurar o retorno para mandar a correção — eu teria rodado a
calibração inteira sobre um `p` que ninguém consome.
