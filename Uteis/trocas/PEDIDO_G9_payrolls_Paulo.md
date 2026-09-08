# PEDIDO `G9` — payrolls: calendário de divulgação + mercados no Polymarket

> **Para o Claude do Paulo:** pedido novo, pequeno e independente do `FOLLOWUP3` (G7/G8) — se
> vierem na mesma sessão, ótimo; se não, a ordem é G7 → G8 → G9. Não muda fonte, não muda
> universo de ativos, não abre view nova.
>
> Regras de sempre: **você levanta e reporta, não decide nada**; campo não medido vai como `?`;
> dado cru não se normaliza. **Push com hash** no fim.

---

## Por que preciso

A camada tática que entrou no v1 mede um **prêmio de anúncio condicionado à incerteza**: nos dias
de anúncio em que a PMF do Polymarket está incerta (entropia alta) o SPY rende **+0,383%**; nos
dias de anúncio previsíveis, **−0,704%**. Diferença de +1,087%, t de Welch +2,10.

O problema é o denominador: essa medição roda com **19 eventos** — 7 FOMC e 12 CPI. É pouco. E é
pouco por um motivo estrutural que não tem conserto: a PMF do Polymarket só existe **de 2025 em
diante**, então esticar a janela para trás não traz evento nenhum.

**Payrolls é o único jeito barato de aumentar a amostra.** É o terceiro grande anúncio macro
agendado, sai no mesmo formato dos outros dois (data conhecida com antecedência, divulgação antes
da abertura), e cobre o mesmo período de 2025 em diante. Se o Polymarket tiver mercado mensal de
payrolls, a amostra pode passar de 19 para perto de 30 eventos — quase o dobro, sem modelo novo.

**Não vira view.** A decisão de manter o item 5.2 fora (mercados novos não viram view) continua de
pé. Payrolls entra só como **mais linhas na mesma medição que já existe** — nenhuma regressão nova,
nenhum mapeamento cenário→ativo novo, nenhum parâmetro novo.

---

## G9a — Calendário de divulgação dos payrolls

O relatório é o **Employment Situation** do BLS (o que traz o *nonfarm payrolls*). Preciso das
**datas de divulgação**, não do valor do indicador.

Mesma estrutura do `cpi_release_dates.csv` que você já entregou: uma linha por mês de referência,
com a data em que o número saiu.

```
=== G9a — CALENDÁRIO DE PAYROLLS ===
Fonte usada:            <URL exata>   (precisa de chave? SIM / NÃO)
Arquivo salvo:          <caminho>
Nº de linhas:           <n>
Janela:                 <primeiro mês de referência> → <último>
Colunas:                <nomes exatos do cabeçalho>
Hora de divulgação:     <se a fonte declarar; se não, "?">
Meses faltando no meio: <lista, ou "nenhum">
```

Duas observações que economizam sua sessão:

1. **O BLS deu 403 numa tentativa anterior** (está no G6 do follow-up 2). Se der de novo, não
   insista — o **release calendar do FRED** é a segunda fonte e resolve igual. Reporte qual das
   duas funcionou.
2. **Cru.** Se aparecer um typo de ano como o do CPI de dez/2025, **sinalize e mantenha cru** —
   a correção é minha, no tratamento. As duas linhas não podem existir ao mesmo tempo.

## G9b — Varredura dos mercados de payrolls no Polymarket

Mesmo procedimento do `G4` (os três buracos de CPI): busca escrita ao lado, negativo é resposta
completa.

Para **cada mês de referência** da janela do G9a:

```
Mês de referência:   <mês>
Buscas feitas:       <endpoint + termo exato de cada tentativa>
Achou mercado?       SIM / NÃO
Se SIM:              slug + nº de buckets + volume + 1ª/última data  (e salve a série crua)
Se NÃO:              lacuna real (o Polymarket não abriu mercado desse mês)
```

Três coisas específicas de payrolls que valem reportar:

- **Buckets ou binário?** A tática calcula entropia normalizada sobre a PMF. Com buckets é o mesmo
  caminho do CPI; com binário (tipo "acima de X mil?") a PMF tem dois estados e ainda funciona,
  mas eu preciso saber **qual dos dois** para escolher o caminho da cascata. Se a grade de buckets
  mudar de tamanho ao longo do tempo, como muda no CPI, diga isso também.
- **A série chega até o dia da divulgação?** Preciso do slot de **12h imediatamente anterior à
  abertura** do dia do anúncio. Mercado que resolve cedo demais e para de negociar na véspera não
  serve — reporte a última data de cada série.
- **Termos de busca que provavelmente pegam:** `payrolls`, `nonfarm`, `jobs report`, `unemployment
  rate`. Se um termo achar e outro não, escreva os dois — a busca faz parte da resposta.

---

## O que continua parado (sem ação sua)

Sem mudança: **G5** (volume no tempo) segue esperando a spec do Ω com a Lia, e **G6** (CPI de
2022–2024) segue condicional à reunião.

---

## Formato da devolução

Os blocos `=== G9a — CALENDÁRIO DE PAYROLLS ===` e o levantamento do G9b, mais:

```
## Bloqueios
<o que não deu, com o motivo>

## Commit
<hash + branch do push>
```

Se o Polymarket **não tiver** mercado de payrolls em mês nenhum, isso é resposta completa e útil —
fecha o D3c com "não dá" e eu paro de contar com esses eventos. **Um `?` honesto é útil; um número
inventado contamina uma decisão metodológica.**
