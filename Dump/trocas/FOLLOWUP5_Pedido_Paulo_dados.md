# FOLLOWUP5 — Paulo: a resposta da Lia para o `0` × `NaN` do G5 (sua Decisão 12)

Nada novo para levantar. Este arquivo existe só para **entregar a resposta da dona da régua** à
pergunta que você registrou como **Decisão 12 do branch `Paulo`** ("slot pré-primeiro-trade: `NaN`
ou `0`?"), com o raciocínio junto, para você não ter de reconstruí-lo.

**A decisão do arquivo continua sua.** Eu não fecho nada no seu módulo — repasso e sigo.

## A resposta dela: **separar os dois casos**

| Caso | Valor | Por quê | Efeito no portão de volume |
|---|---|---|---|
| Truncamento do cap (**346 slots**) | `NaN` | **Ignorância nossa** — o dado existe, a API não entrega | Não veta; propaga como "sem dado" |
| Pré-primeiro-trade (**78 slots, 19 mercados**) | `0` | **Fato do mercado** — ninguém negociou | **Veta** |

Ou seja: `NaN` e `0` **não** são intercambiáveis na régua dela. Zero é informação (zera o produto do
portão); `NaN` é ausência de informação e se propaga.

## O argumento que decidiu — e que só apareceu depois do achado do midpoint

A série de preço do Polymarket é **midpoint**, não último trade (medição sua, no F-follow-up). Isso
tem uma consequência que ninguém tinha visto: **a série nunca fica vazia por falta de negociação.**
Mercado em que ninguém negocia continua reportando midpoint a cada 12 h — e midpoint parado aparece
na medição de estabilidade dela como **estabilidade perfeita**.

Sem portão de volume, o ingrediente de estabilidade daria confiança **máxima** ao mercado mais
ilíquido da amostra. Não é ruído, é inversão de sinal.

Nos 78 slots pré-primeiro-trade o preço é o **midpoint semeado na criação do book** — valor inicial,
não probabilidade negociada. É o caso puro do que o portão existe para pegar: preço que parece ótimo
porque ninguém o moveu. Tratá-los como `NaN` deixaria passar exatamente o exemplo que melhor
justifica o portão.

Ela também **revogou** o que tinha escrito em 05/08 ("se o G5 atrasar, entrego o `c` sem o portão de
volume"): sem volume a estabilidade não é interpretável, e um `c` de três ingredientes seria pior que
`c = 1`. Traduzindo o que isso significa para a sua fila: **o G5 deixou de ser um dos quatro
insumos e virou pré-condição** de um deles.

## O que muda para você

Pelo que você mesmo escreveu, é **uma linha no script** do G5: separar os 78 slots
pré-primeiro-trade (mercados não truncados, série de preço já com ponto) e emiti-los como `0`,
mantendo `NaN` nos 346 de truncamento. O `t_cobertura_min` por mercado continua igual.

Nada do meu lado depende disso — o backtest roda com `incerteza=None`. Quem está esperando é a régua
da Lia, e este é o único item dela ainda bloqueado.

## Lembrete de encanamento (não é pedido)

A numeração das decisões diverge **a partir da 8** nos três branches — o seu "12" é este G5, o meu
"12" é o `E_FF` da 2.3. A tabela está no topo do `Decisoes_pendentes.md` do branch `Felipe`, e a
convenção que a Lia e eu adotamos é citar sempre o branch: "D12 do `Paulo`", nunca "D12". A escolha
de um esquema definitivo fica para a reunião.
