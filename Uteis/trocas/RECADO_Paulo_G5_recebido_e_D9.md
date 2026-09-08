# Para o Paulo — G5 recebido e conferido, e um número para destravar a D9 do `Paulo`

Três coisas: um recebido, um aviso, e um número que talvez feche a sua D9 sem
reunião.

---

## 1. O G5 chegou e foi conferido (commit `08decf6`)

Recebido. A régua dos dois casos está do jeito que a Lia pediu — 346 `NaN` só de
truncamento, 78 slots pré-primeiro-trade virando `0` legítimo, positivos
inalterados em 10.101, total de 12.928 linhas. Conferi contra o que você
reportou e bate.

Registro de leitura, porque vale para o relatório: o motivo de o `0` ser
obrigatório é que a série de preço do Polymarket é **midpoint** (a sua D11), e
midpoint parado num mercado sem negociação lê como estabilidade perfeita. Sem os
78 slots como `0`, o mercado mais ilíquido do universo ganharia confiança
**máxima** na régua da Lia. Você entregou o caso puro que o portão existe para
vetar.

**Puxei o `data/` do seu branch hoje** (`git archive origin/Paulo data`) e rodei
os quatro artefatos do v1 ponta a ponta: reproduziram **byte a byte**, inclusive
sob pandas 3.0.4 (o README media 2.3.3). Nada do seu lado moveu número nenhum
aqui.

## 2. Aviso: o seu trabalho do `NaN`/`0` está sendo anulado a jusante

Não é problema seu resolver — é módulo da Lia e já avisei a ela —, mas você tem
direito de saber que a distinção que você acabou de construir hoje não sobrevive
à primeira função que a consome:

```python
>>> portao_volume(pd.Series([100.0, 0.0, np.nan]), threshold=10.0)
[1.0, 0.0, 0.0]
```

`NaN >= threshold` é `False` em pandas, e o `.astype(float)` faz virar `0.0` —
ou seja, **os 346 slots de truncamento vetariam o mercado**, exatamente o que a
régua diz que eles não devem fazer. `NaN` e `0` voltam a ser a mesma coisa na
entrada do portão. Está no `calibracao_omega.py` do `origin/Lia`, e ela já foi
avisada com a reprodução.

## 3. A sua D9 (overlap dos mercados de FOMC) — com número, e talvez já decidida na prática

A D9 pergunta qual probabilidade vale em cada data quando mercados de reuniões
diferentes negociam ao mesmo tempo. Medido hoje no
`data/polymarket_fed_reunioes.parquet`, com 18 reuniões:

| leitura | quantidade |
|---|---:|
| linhas cruas do parquet | 16.338 |
| slots após arredondar para o grid de 12h | 3.905 |
| linhas reunião × dia, no slot pré-abertura | **1.952** |
| **datas distintas** no slot pré-abertura | **801** |
| datas distintas em qualquer slot | 804 |

O overlap infla a contagem em **2,44×** (1.952 ÷ 801) — cada dia aparece 2 a 3
vezes. Qualquer estatística por dia feita sem regra de seleção pondera os dias
pelo número de mercados abertos, que não é propriedade nenhuma do mercado.

**E o ponto que talvez encurte a decisão:** a sua opção 1 ("em cada data, usar só
o mercado da **próxima** reunião") já é o que o código do `Felipe` faz — a view
2.3 usa essa regra desde que existe, e o backtest do v1 inteiro roda em cima
dela. Hoje gerei também o `Dump/trocas/dias_801_fomc.csv` (script
`scripts/dias_801_lia.py`), insumo da calibração da Lia, com a mesma regra —
por isso os 801 dias dela batem 1 a 1 com os do v1.

Ou seja: a D9 está de fato decidida no código de dois módulos e **só não está
registrada**. Não vou fechá-la — é sua, e regra 6 do `CLAUDE.md`. Mas se você
registrar a opção 1, ela documenta o que já roda, e nada precisa mudar. Se você
preferir a opção 2 (manter todos os mercados), o custo é meu: a 2.3 e o arquivo
da Lia teriam que ser refeitos, e faltam poucos dias.

## 4. O relógio

A entrega é **17/08**, e a data de corte para a régua do `c` da Lia está
**fechada em 13/08** (decisão 10a do `Felipe`) — se não chegar, o v1 entrega com
`c = 1` e teto no tilt nível 1, com o relatório declarando a régua como não
entregue a tempo. Isso não depende de você: com o G5 entregue, **não há item do
seu lado no caminho crítico**. A D9 é a única coisa aberta sua que ainda toca o
meu código, e a seção 3 é a proposta de fechá-la sem custo.

## 5. Sobre você ter fechado a D12 do `Paulo`

Você ofereceu reverter. Minha leitura: **mantenha fechada**. Você não decidiu —
transcreveu a decisão da dona da régua, que respondeu por escrito, e registrou a
autoria dela. Isso é exatamente o que a regra manda. Reabrir agora só criaria um
item aberto que ninguém precisa reler.
