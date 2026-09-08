# Resposta da Lia — o midpoint muda o peso do portão, fronteira da soma, e G5

Resposta ao seu retorno de 2026-08-07 (verificação do lookahead + dict + notícias). Ordem: a
**consequência do seu achado do midpoint**, que é o item mais importante daqui e não estava na
lista de nenhum dos dois; depois as respostas às suas duas perguntas; e o que muda no meu
cronograma.

---

## 1. Lookahead: aceito, sem ação — mas o *midpoint* revoga uma coisa que eu escrevi

A verificação fecha: snapshot instantâneo às 12:00 UTC, execução em 13:30/14:30 UTC, leitura 1,5 a
2,5 h **antes** da execução. Não há lookahead, nada a corrigir. Obrigada por medir em vez de
responder pela lógica.

**Mas o fato de a série ser midpoint, e não último trade, tem consequência direta no meu
`score_estabilidade`** — e é o oposto do que eu tinha assumido:

> **A série de preço nunca fica vazia por falta de negociação.** Um mercado em que ninguém negocia
> continua reportando midpoint a cada 12 h. E midpoint parado aparece na minha medição como
> **estabilidade perfeita**.

Ou seja: sem o portão de volume, o ingrediente de estabilidade daria confiança **máxima**
exatamente ao mercado mais ilíquido da amostra. Não é ruído — é inversão de sinal, e sistemática:
quanto menos gente negocia, mais estável a série parece.

Duas consequências:

1. **O portão de volume deixa de ser um dos quatro ingredientes e vira pré-condição do
   `score_estabilidade`.** Ele não está "multiplicando uma confiança"; ele está dizendo se o
   ingrediente de estabilidade tem qualquer significado naquele slot.
2. **Revogo o que escrevi em 05/08** ("se o G5 atrasar, entrego o `c` sem o portão de volume"). Sem
   volume, a estabilidade não é interpretável, e um `c` de três ingredientes seria pior que
   `c = 1`: daria confiança extra a mercado morto. Ainda bem que o G5 chegou — se não tivesse
   chegado, a decisão certa teria sido entregar sem o ingrediente de estabilidade, não sem o
   portão.

Isso também é o que decide a sua pergunta do G5 (item 3 abaixo).

---

## 2. Chave do dict: fico com o identificador longo — **não troque**

`"2.2_inflacao"`, `"2.3_fed"`, `"B_trajetoria_fed"`. Você está certo: a chave sai de
`diagnostics["view"]`, que é dado que já existe. Um apelido curto criaria um **segundo nome para a
mesma coisa** — que é a classe de erro que acabamos de fechar com o dict. Meu exemplo em 07/08 foi
descuido de escrita, não pedido de renomeação.

Um pedido pequeno, se ainda não for assim: que a lista de chaves válidas seja derivada do próprio
`view_results` em tempo de execução, e não de uma constante escrita à mão — senão o nome passa a
viver em três lugares (view, constante, meu dict) e a validação só cobre dois.

`ValueError` com o que faltou e o que sobrou, e `incerteza` validado com o mesmo rigor de `ativa`:
é exatamente o contrato que eu queria.

**Sobre o achado colateral** (o `if __name__ == "__main__"` no meio do arquivo, 4 testes que nunca
rodavam, mais dois arquivos morrendo em `NameError`): bom achado, e vale registrar a implicação —
"suíte verde" naqueles arquivos não era evidência de nada antes do conserto. Se alguma decisão
nossa foi tomada com base em teste daquele bloco, ela não estava testada.

---

## 3. Soma das faixas: **disjuntos por regime** — não são dois cortes na mesma coisa

Você fez a pergunta certa, e a resposta é que o caso aqui é diferente do 6a. No 6a, os dois
ingredientes agiriam **no mesmo slot, dentro do mesmo produto multiplicativo** — por isso a dupla
punição, e por isso o teste não pegaria. Aqui os regimes são **disjuntos**:

| Regime | Quem age | O que acontece |
|---|---|---|
| soma crua < 0,9 | sua cascata | A view é desativada no dia — **ela nem chega ao meu Ω**; não existe `c` para ela |
| soma crua ≥ 0,9 | meu `score_coerencia` | O seu piso não age; só o gradiente meu age |

Nenhum slot recebe os dois cortes. **O compromisso que mantém isso verdadeiro, e que eu peço que
fique escrito dos dois lados:** o seu piso não vira rampa, e o meu score não ganha portão binário.
O único portão binário da minha régua continua sendo o volume. No dia em que o piso 0,9 virar
gradiente, isso aqui vira dupla contagem — e é o tipo de mudança que ninguém lembra de reavaliar
depois.

**A assimetria é a favor:** o seu corte é só **por baixo**; o meu `−|soma − 1|` é **bilateral**.
Soma 1,32 — o caso que você mesmo mediu no mercado de cortes do Fed — passa inteira pela sua
cascata e só o meu score pega. Não há redundância nem buraco: há divisão de trabalho.

**Ressalva honesta sobre a 2.3:** você reportou soma entre 0,969 e 1,013 na janela do backtest. É
faixa estreita, então nessa view o ingrediente de coerência vai ter pouca variação — e um
ingrediente com pouca variação pode não passar no teste de monotonicidade **por falta de poder
discriminante, não por estar errado**. Se ele cair por esse motivo, vou registrar a distinção em
vez de deixar o relatório dizer "o desarranjo não prevê erro".

---

## 4. G5: **separar** — pré-primeiro-trade é `0`, truncamento é `NaN`

Vale a linha do script. Os dois casos são opostos, e na minha régua `NaN` e `0` fazem coisas
diferentes:

| Caso | Valor | Por quê | Efeito no portão |
|---|---|---|---|
| Truncamento do cap (346 slots) | `NaN` | **Ignorância nossa** — o dado existe, a API não entrega | Não veta; propaga como "sem dado" |
| Pré-primeiro-trade (78 slots, 19 mercados) | `0` | **Fato do mercado** — ninguém negociou | Veta |

E o item 1 reforça o segundo caso: nesses slots o preço é o **midpoint semeado na criação** — valor
inicial do book, não probabilidade negociada. É o caso puro do que o portão existe para pegar:
preço que parece ótimo (perfeitamente estável, porque ninguém o moveu) e não tem nada por trás.
Tratar esses 78 slots como `NaN` seria deixar passar exatamente o exemplo que melhor justifica o
portão.

---

## 5. k = 2: retiro a ressalva de 07/08, com uma nota de tamanho

Com a 2.3 ativa em 87% dos pregões e as duas convivendo em 64%, a ordenação **entre** views passa a
ter amostra — retiro o que escrevi sobre ficar sem teste. Nota de tamanho, para o relatório não
vender demais: são **dois mercados**, não vinte. O teste responde "a régua ordena certo entre 2.2 e
2.3?", não "a régua generaliza entre mercados". Vou reportar assim.

---

## 6. O +2,68 pp muda o **nível** do `c`, não a **forma** — e um risco de processo

Reancorado, obrigada. O número novo muda uma coisa e não muda outra:

- **Não muda a forma.** O teste de monotonicidade é sobre **erro realizado da probabilidade**, não
  sobre retorno da carteira. A régua relativa sai dali, independente de o backtest estar ganhando
  ou perdendo — é justamente o que impede que ela seja escolhida pelo resultado.
- **Muda a leitura do nível.** Com excesso positivo, um `c` global alto passa a ser **custo**, não
  conserto. Isso **não** é motivo para eu calibrar um `c` menor: seria escolher o número pelo
  resultado, exatamente o que o protocolo existe para evitar. É motivo para o nível global entrar
  na conversa de risco com esse número na mesa.

**⚠️ Risco de processo, e proponho travar agora:** se eu calibrar o `c`, o grupo ajustar o teto
olhando o resultado, e eu reajustar o `c` olhando o resultado de novo, viramos overfit em dois
passos — e nenhum dos dois lados vê, porque cada passo isolado parece razoável. Proposta:

1. a **forma** do `c` sai da monotonicidade e **não é revisitada por resultado de backtest**;
2. o **nível** global é escolhido **uma vez**, na conversa de risco, junto com o teto;
3. se o resultado depois desagradar, muda-se o teto, não a régua.

Também anoto o dado a favor da variante que você mediu: teto no **tilt** dá +2,68 pp contra −7,91
pp do teto de carteira, na mesma alavancagem de 1,90. Isso responde a "questão de desenho aberta"
da sua decisão 10 com número, não com opinião.

---

## 7. Numeração: convenção adotada

"D12 do `Paulo`", "D12 do `Felipe`" — sempre com o branch. Registrei do meu lado.

---

## O que eu faço agora, nesta ordem

1. Colapso PMF→p (duas candidatas) sobre a `serie_janela` **renormalizada**.
2. Portão de volume com o G5, assim que a separação `0` × `NaN` do item 4 estiver no arquivo.
3. Teste de monotonicidade nos quatro ingredientes, agora com duas views.
4. Entrega: `c` + `ativa`, dicts chaveados por `diagnostics["view"]`, convenção `c ≥ 1`.

Nada disso bloqueia você: `incerteza=None` segue rodando.
