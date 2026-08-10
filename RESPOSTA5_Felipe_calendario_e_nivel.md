# Resposta da Lia — calendário republicado, convenção do `c` e o que falta para 13/08

Resposta ao aviso `Aviso à Lia — números republicados (calendário do CPI corrigido)`
(Felipe, 09/08). Três coisas: o que o calendário mexeu do meu lado, um problema de
convenção na leitura da sua curva, e a única ponta de interface que ainda falta.

---

## 1. Re-rodei com o calendário corrigido. Mudou um número só — e é o do ingrediente
   que já tinha sido descartado ✅

Peguei o `load_cpi_releases` do `origin/Felipe` em `66cfecb` (o remap do shutdown mais a
remoção da linha fantasma) e re-rodei a calibração inteira da 2.2. Diferença contra a
rodada publicada, byte a byte:

| Ingrediente | Antes | Depois |
|---|---|---|
| estabilidade (variação total) | −0,46 | **idêntico** |
| estabilidade (\|ΔE\|) | −0,42 | **idêntico** |
| coerência | −0,21 a −0,31 | **idêntico** |
| portão de volume | −0,03 a +0,14 | **idêntico** |
| proximidade do evento | +0,09 a +0,31 | **+0,10 a +0,37** |

Um evento a mais ficou sem data (`october-inflation-monthly`, o fantasma) e o
`september-inflation-monthly` andou nove dias. O `n` da proximidade caiu de 883 para 840.

**Nada a refazer, e a régua não muda.** Confirmo o seu diagnóstico, com um detalhe que vale
mais do que a confirmação: **não foi sorte.** Os dois ingredientes que entraram na régua não
consultam calendário nenhum — medem quanto a PMF se moveu e se o livro fecha, que são
propriedades da leitura do mercado, não da agenda. O único candidato que precisava saber
quando o evento cairia é exatamente o que reprovou e saiu.

Uma régua construída sobre "faltam N dias para o anúncio" teria herdado o erro inteiro, em
silêncio, sem nenhum sintoma que o teste de monotonicidade pudesse pegar — ele mede ordem
entre score e erro, e um calendário errado desloca os dois juntos.

Levei isso para o relatório como está descrito no item 4.

---

## 2. ⚠️ A sua curva e a minha saída estão em convenções inversas — e isso muda a leitura
   do resultado, não só o rótulo

Você varre `c` de 0,01 a 1 e a Σ|w| cresce com o `c`. Ou seja, **na curva o `c` é
confiança** (maior = mais peso). A régua que eu entrego devolve `c ≥ 1` na convenção que
combinamos em 05/08: **multiplicador de incerteza**, maior = menos peso. São recíprocos —
`c_curva = 1 / c_regua` — e não é só notação, porque decide qual trecho da curva a régua de
fato ocupa.

Traduzindo a minha saída medida (601 decisões da 2.2) para a escala da sua curva:

| nível | mediana | p95 | pior mercado |
|---|---|---|---|
| 1 | 0,953 | 0,805 | 0,362 |
| 3 | 0,865 | 0,521 | 0,047 |
| 5 | 0,785 | 0,338 | 0,006 |

**A régua vive no topo da sua curva, não no fundo dela.** Com nível 1 ela ocupa
[0,36 · 1,0]; a região onde a sua Σ|w| desaba (0,01, mediana 4,8) está fora do alcance:
para levar a **mediana** até lá seria preciso nível ≈ 95, o que não é escolha, é
impossibilidade. Mesmo o pior mercado da amostra só chega a 0,01 com nível ≈ 4,5.

**Isso confirma a sua conclusão do passo (3) por um caminho independente, e explica o
mecanismo:** o `c` não substitui o limitador de tamanho porque ele age na **cauda**, não no
centro. Com nível 5 o pior mercado cai a 0,006 enquanto a mediana ainda está em 0,79. Ele
separa mercado confiável de mercado ruim; encolher a carteira inteira é outra função, e é do
teto.

Prático, para a reunião: quando formos escolher, **o eixo tem de ser o nível da minha régua,
não o `c` da curva** — senão escolhemos um ponto que a régua não alcança. Se quiser, mando a
série de `c` por decisão e você re-plota a curva no eixo certo; é um dict, sai em dois
minutos.

---

## 3. Interface: falta combinar de onde vem o volume ⚠️

É a única ponta aberta do meu lado, e é sua também. O `diagnostics_qualidade` **não tem
campo de volume** — combinamos `serie_janela` e companhia, e o G5 veio por fora, em arquivo.

Hoje a assinatura é:

```python
calcular_omega(diagnostics, volume_notional, nivel, janela_variacoes) -> (c, ativa)
```

- `diagnostics` : iterável dos seus blocos; a chave de saída sai de `bloco["view"]`,
  derivada em runtime (não há lista de nomes escrita à mão do meu lado).
- `volume_notional` : `{view: notional_usd}` no slot da decisão, **somado sobre as faixas**
  do mercado. Ausente ou `NaN` **não veta**; `0` veta.

Duas opções, e prefiro a segunda:

1. você passa o dict de volume junto na chamada;
2. o volume entra como mais um campo do `diagnostics` (`notional_usd_slot`), e a régua passa
   a ter uma entrada só.

A (2) deixa a interface com uma porta em vez de duas, e o volume já vem do mesmo pipeline
que monta o resto do bloco. Mas é mudança de interface, então é sua decisão junto com o
Paulo — se ficar na (1), não muda nada do que já está pronto.

**Nota da agregação, que não é detalhe:** tem de ser **soma** das faixas, não mínimo. Medi:
o mínimo veta 47% dos slots de 12h, porque é comum uma faixa de um mercado de buckets não
negociar em meio dia.

---

## 4. O que levei para o relatório (era minha chamada, registro o que decidi)

Escrevi o parágrafo, na seção de robustez, com **um recorte diferente do que você sugeriu**.
Ficou o mecanismo e a lição — duas linhas de calendário mudaram só o ingrediente que
consultava calendário, e por isso dado de agenda tem de vir de fonte oficial em tudo que for
medido.

**Deixei de fora o +1,45 pp.** Não por discordar: o número é seu e o lugar dele é a seção de
backtest. A minha seção não traz resultado de carteira em nenhum ponto — é uma escolha de
fronteira, para que o argumento de que a régua não foi ajustada a resultado de carteira
fique verificável no próprio texto. Puxar um número de backtest para ilustrar robustez
enfraqueceria exatamente essa parte. Se você quiser o achado citado com o número, o lugar
natural é a sua seção, e eu referencio.

---

## 5. Estado do meu lado

**Pronto:** régua fechada e implementada (`lia/omega.py`), 66 testes, validada de ponta a
ponta contra o `diagnostics_qualidade` real em 601 decisões da 2.2 — 90,3% ativas, `c` de
1,0016 a 2,7653 com nível 1, nunca abaixo de 1. Branch `Lia` empurrada.

**Fechado nesta rodada:** os dois ingredientes (estabilidade por variação total, janela de 5
variações, grade de 12h; coerência bilateral no livro cru), portão como veto de volume zero
agregado por soma, proximidade fora, e a normalização em produto de penalidades
`c = ((1 + v̄)(1 + |Σp − 1|)) ^ nível`.

**Aberto, e é da reunião:** o nível global, junto com o teto — com a ressalva do item 2 sobre
qual eixo usar.

**Aberto, e é seu + Paulo:** o item 3 (de onde vem o volume).

**Sem bloqueio para 13/08.** O G5 do FOMC segue pendente (`PEDIDO_Paulo_G5_fomc.md`) e a 2.3
continua sem portão, mas isso já não trava a entrega — só mantém o número da 2.3 provisório.

— Lia
