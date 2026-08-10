# Resposta da Lia — a série de `c` por decisão, e o que ela mostra antes de você plotar

Resposta ao `Resposta à Lia — a convenção virou correção de código...` (Felipe, 10/08).
O item 2 está entregue. Tem um resultado dentro dele que muda o desenho da escolha de
13/08, e prefiro que você o veja antes de rodar a curva.

---

## 1. `lia/c_por_decisao.csv` — a série, nas duas views ✅

Gerada por `lia/exportar_c.py` (10 testes novos, **76 na minha suíte**). 2.417 linhas,
uma por `(data, view, mercado)`; 1.227 são as que a view de fato consome.

Formato — CSV longo em vez do dict, pelo motivo do item 3:

| coluna | o que é |
|---|---|
| `data`, `view`, `mercado` | a chave. `view` é `2.2_inflacao` / `2.3_fed`, como você pediu |
| `selecionado` | é este o mercado que a view consome nesta data (regra sua, item 3) |
| `c_nivel1` | a régua com `nivel = 1`, **na minha convenção** (`≥ 1`, incerteza) |
| `fator_estabilidade`, `fator_coerencia` | os dois fatores separados, para diagnóstico |
| `ativa`, `motivo_inativa` | a máscara, com os dois motivos **separados** |
| `tem_portao` | ⚠️ `False` na 2.3 — sem G5, sem veto de liquidez |
| `volume_notional`, `n_pontos_janela`, `n_slots_esperados_janela` | auditoria |

**Você não precisa de uma série por nível.** A régua é
`c = ((1 + v̄)(1 + |Σp − 1|)) ** nivel`, e o nível é só o expoente:

```python
c = df.c_nivel1 ** nivel          # qualquer nível, sem nova rodada minha
c_curva = 1.0 / c                 # para o eixo da sua curva (recíproco)
```

É por isso que a coluna se chama `c_nivel1` e não `c`: ela é o produto dos fatores, e
varrer o nível é elevá-la. Varredura contínua, se você quiser.

---

## 2. ⚠️ O que a série mostra e a grade constante escondia: **a 2.3 quase não é modulada**

Este é o resultado da entrega, e ele não estava na conversa até agora. A tradução que te
mandei em 09/08 (mediana 0,953, pior 0,362) era **só da 2.2**. Com as duas views:

| nível | 2.2 mediana | 2.2 pior | 2.3 mediana | 2.3 pior |
|---|---|---|---|---|
| 1 | 0,950 | 0,362 | **0,988** | **0,817** |
| 3 | 0,858 | 0,047 | **0,965** | **0,545** |
| 5 | 0,775 | 0,006 | **0,942** | **0,364** |

(na escala da sua curva, `1/c`; 388 decisões ativas na 2.2, 781 na 2.3, 349 dias com as
duas ativas)

**A régua discrimina quase só a 2.2.** Mesmo com nível 5 — que na 2.2 leva o pior mercado
a 0,006 — o pior dia da 2.3 fica em 0,36, que é onde a 2.2 já está com nível 1. Não é
defeito: o mercado de decisão do FOMC tem 4–5 buckets, livro que fecha (fator de coerência
mediano **1,0035**, contra 1,0200 na 2.2) e PMF que se move pouco (estabilidade mediana
1,0065 × 1,0283). Ele é simplesmente um mercado melhor comportado que o do CPI.

**Consequência para 13/08, e é por isso que mando antes:** escolher o nível olhando o
efeito agregado vai subestimar quanto ele morde a 2.2, porque a 2.3 dilui. Se a curva
sair por view, a decisão fica visível — e talvez a conversa seja sobre a 2.2, com a 2.3
quase invariante. Não estou propondo nível por view (isso seria dois botões onde a 6d
pediu um); só que o gráfico mostre as duas.

**Ressalva que pesa aqui:** parte da suavidade da 2.3 é ausência de portão (item 4). Ela
não tem veto de liquidez, então nenhuma decisão dela sai por volume zero — 0 contra 17 na
2.2. O G5 do FOMC mudaria este número, não os outros dois fatores.

---

## 3. A regra de seleção do mercado é **sua**, lida do seu código — e é por isso que o
   formato é longo

O dict `{data: {view: c}}` exige um mercado por view por data, e isso não é dado: em **80
das 496 datas** da 2.2 há 2 ou 3 mercados-mês vivos ao mesmo tempo (no FOMC a sobreposição
é a regra, não a exceção). Escolher entre eles seria eu decidindo o que a sua view consome.

Então fui ler: `_view_2_2` / `_view_2_3` do `scripts/backtest_v1.py` usam
`min(eventos futuros)` — vale o mercado do **próximo** evento. É isso que a coluna
`selecionado` reproduz, e o `mercado` fica ao lado para você conferir que estamos falando
da mesma série. **Se a sua regra mudar, o casamento se refaz do CSV, sem nova rodada
minha** — que é a razão de a série completa ir junto.

Três coisas que decorrem disso, todas verificáveis no arquivo:

- **Os mercados são os seus.** Casei por sufixo do slug do calendário em vez de montar
  `CPI_<slug>_`; dá o mesmo conjunto de 14 mercados-mês que o seu `mercados_de_cpi`.
- **Cinco mercados de CPI ficam de fora por não terem release no calendário do Paulo**
  (`january-inflation-monthly`, `december-inflation-monthly`, o `G4_janeiro-2026`, o
  `M1_cpi_monthly` duplicado e o `october-inflation-monthly` — este último é o fantasma da
  6i, e ficar de fora é o comportamento correto). Você tem a mesma limitação, pela mesma
  fonte.
- **Não filtrei o dia da divulgação.** A sua cascata tira a view quando `faltam < 1`;
  deixei a linha e a coluna `dias_corridos_ate_evento` para o corte ser seu. Atenção: os
  meus dias são **corridos**, os seus são **pregões** — não use a minha coluna para
  reproduzir o seu corte, ela é para auditoria.

Datas cobertas: 2.2 de 2025-02-08 a 2026-07-29 (426 datas); 2.3 de 2024-04-04 a
2026-06-17 (801 datas — os mesmos 801 dias da história completa). É superconjunto do seu
calendário de pregão: filtre pelo seu.

---

## 4. A 2.3 vai marcada, não escondida ⚠️

`tem_portao = False` em toda linha da 2.3. Sem o G5 do FOMC (1 mercado coberto contra os
111 do CPI — `PEDIDO_Paulo_G5_fomc.md`), o volume entra `NaN`, e pela 6b **`NaN` não
veta**. Consequências, para você decidir se usa:

- as 20 inativas da 2.3 são **todas** por ausência de par adjacente; nenhuma por liquidez;
- o `c` da 2.3 não foi qualificado por negociação nenhuma — é o mesmo status "provisório"
  que a calibração dela já tinha.

Se você preferir rodar a curva só com a 2.2 até o G5 chegar, é uma escolha defensável e o
CSV filtra numa linha. Eu mandaria as duas, porque o backtest roda as duas e uma curva de
meia carteira decide mal.

---

## 5. Cristalização (seu item 5): **estou parada, esperando o arquivo corrigido**

Você avisou que o artefato saiu errado e que manda o certo. Então **não mexi no relatório**
— a frase interpretativa continua como está, e eu não a defendo nem a corrijo com base num
número que vai mudar. Quando chegar o arquivo, eu meço no meu dado (variação total da PMF
renormalizada, grade de 12h, que é a métrica da régua) e aí a frase vai ao relatório com o
recorte que os dois lados sustentarem.

Registro só o que já vale independentemente do número: **a rejeição da proximidade não
depende dessa frase.** Ela caiu por 16 cortes de teste de monotonicidade, nas duas views,
incluindo o alvo por desfecho — nada disso passa pela interpretação do mecanismo. O que
está em jogo é uma sentença da seção "o que foi rejeitado", não um ingrediente.

---

## 6. Os outros itens — de acordo, sem ação minha

- **Convenção corrigida nos três docstrings (seu item 1):** era isso mesmo, e obrigada por
  ter caçado o terceiro. Confirmo do meu lado: a régua entra **direto** em
  `omega_fallback`, sem inverter.
- **Volume, D20a (item 3):** de acordo. Fico na (1) — passo o dict — até a reunião. Se a
  (2) passar, eu e o Paulo escrevemos.
- **`ativa = False` com dois motivos (item 4):** de acordo em não devolver o motivo na
  assinatura. Ele está no CSV como coluna de log, que é o lugar certo.
- **+1,45 pp (item 6):** combinado, fica na sua seção. Referencio de lá.
- **`desfecho_bps` / `bucket_vencedor` (item 7):** seguem disponíveis quando precisar.

---

## 7. Estado do meu lado, para 13/08

**Entregue:** `lia/c_por_decisao.csv` + `lia/exportar_c.py` (76 testes). A série reproduz
exatamente os números publicados da validação (601 decisões da 2.2, 543 ativas, 37 vetos
de volume, 21 sem par, `c` de 1,0016 a 2,7653) — o recorte por mercado selecionado é que
reduz para 426 datas.

**Preciso de você:** nada bloqueante. O arquivo corrigido da cristalização quando sair.

**Da reunião:** nível + teto no eixo do nível (D20b/6d), agora com a tabela por view do
item 2; e a interface do volume com o Paulo (D20a).

**Sem bloqueio para 13/08.**

— Lia
