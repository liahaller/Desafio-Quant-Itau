# Premissa empírica das 3 táticas candidatas

> Gerado por `scripts/premissa_taticas.py` sobre o dado do G1/G2 (follow-up 2). **Mede a premissa; não escolhe parâmetro nem liga tática** — a ENTRADA da camada segue pendente de reunião (decisão 10). Preços em base ajustada nos dois arquivos (`auto_adjust=True`), o que torna o retorno `abertura → fechamento` legítimo em dia de dividendo.

## ⚠️ Antes dos números: os dois parquets não estão na mesma base

Mediana de `abertura/fechamento − 1` por ticker. Se as duas séries estivessem no mesmo ajuste, isso seria ruído intradiário (± 0,1%):

| SPY | TIP | TLT | XLE | XLF | XLK | XLP | XLU | XLV |
|---|---|---|---|---|---|---|---|---|
| -0.058% | -1.149% | -0.414% | -0.047% | -0.037% | -0.064% | -0.042% | -0.036% | -0.027% |

**TIP (-1.15%) e TLT (-0.41%) estão deslocados** — e são justamente os dois ETFs de pagamento MENSAL. O `etf_prices_daily.parquet` foi gerado em 2026-07-09 (`48cb12e`) e o `etf_open_daily.parquet` em 2026-08-02 (`7ea4e86`); um ex-dividendo entre os dois pulls faz o `auto_adjust=True` reescalar toda a história anterior de um só arquivo. O degrau é visível: a razão fica em −1,15% até ~2026-06-01 e vai a ~0 depois.

Efeito: `abertura → fechamento` de TIP e TLT ganha **+1,15% e +0,40% fabricados por dia** na amostra antiga (com o espelho no overnight). As médias intradiárias desses dois tickers abaixo estão contaminadas; as **correlações não** (o deslocamento é constante e não muda covariância), e nada que use só fechamento é afetado. Conserto: re-baixar os dois arquivos no mesmo pull — módulo do Paulo.

## Gap de fim de semana — a tática entra DEPOIS do salto

1179 reaberturas (pregão anterior a ≥ 3 dias corridos, o que inclui feriado prolongado) contra 4502 demais pregões, 2003-12-05 → 2026-07-08.

**O salto que a tática NÃO captura** (`close sexta → abertura segunda`) e o pedaço que ela captura (`abertura → fechamento de segunda`):

| ativo | salto médio | σ do salto | intradiário médio | σ intradiário | corr(salto, intradiário) | t da corr |
|---|---|---|---|---|---|---|
| SPY | +0.018% | 0.837% | +0.015% | 0.878% | +0.128 | +4.44 |
| TIP ⚠️ | -1.143% | 0.233% | +1.141% | 0.297% | -0.089 | -3.08 |
| TLT ⚠️ | -0.408% | 0.661% | +0.403% | 0.608% | -0.029 | -1.01 |
| XLE | +0.026% | 1.349% | -0.015% | 1.490% | +0.106 | +3.65 |
| XLF | +0.008% | 1.262% | -0.055% | 1.429% | +0.090 | +3.11 |
| XLK | +0.015% | 1.072% | +0.070% | 1.096% | -0.100 | -3.44 |
| XLP | +0.007% | 0.686% | +0.029% | 0.744% | -0.252 | -8.92 |
| XLU | +0.055% | 0.678% | -0.007% | 1.043% | +0.010 | +0.33 |
| XLV | +0.030% | 0.700% | -0.034% | 0.864% | -0.044 | -1.52 |

Leitura: **correlação positiva** = o mercado continua na direção do salto depois de abrir (a premissa da tática se sustenta); **≈ 0** = o salto do fim de semana já está inteiro no preço de abertura e a tática entra tarde; **negativa** = reversão, e o tilt na direção do Δp opera contra o dado.

Intradiário de reabertura contra os demais dias (é a janela exata da tática, `abertura → fechamento`):

| amostra | n | média | σ | t |
|---|---|---|---|---|
| SPY — dias de reabertura | 1179 | +0.015% | 0.878% | +0.57 |
| SPY — demais pregões | 4502 | +0.015% | 0.923% | +1.07 |

## Prêmio de anúncios (1.3) — âncora Savor & Wilson

Retorno do SPY de `fechamento(D−1) → fechamento(D)`, que é a janela declarada pela tática, em dia de anúncio agendado contra os demais.

| amostra | n | média | σ | t |
|---|---|---|---|---|
| FOMC (2022-01-26 → 2026-06-17) | 36 | +0.062% | 1.343% | +0.28 |
| demais pregões da mesma janela (FOMC) | 1066 | +0.060% | 1.104% | +1.77 |
| CPI (2025-03-12 → 2026-06-10) | 13 | -0.394% | 1.461% | -0.97 |
| demais pregões da mesma janela (CPI) | 301 | +0.117% | 1.131% | +1.80 |
| FOMC + CPI juntos | 49 | -0.059% | 1.375% | -0.30 |

A tática é long SPY vs caixa **dimensionada pela entropia da PMF**; o que está medido aqui é só a âncora (o prêmio existe na amostra?), não o sinal — a modulação por entropia depende da decisão 11a (correção de favorite-longshot), que ainda falha alto de propósito.


## Drift pós-FOMC — tamanho da janela (o sinal não é testável aqui)

A direção do tilt é `−sign(surpresa)`, e a surpresa vem do ZQ, que **não tem fonte definida** (o yfinance não serve — decisão de grupo pendente). Sem ela não dá para testar o drift; dá para medir o **tamanho** da janela que a tática ocuparia, que é o teto do que a sleeve pode render.

36 anúncios do FOMC caem em pregão, 2022-01-26 → 2026-06-17 (o calendário entregue começa em 2022-01-26).

| livro | ativo | janela | n eventos | acumulado médio | σ do acumulado |
|---|---|---|---|---|---|
| ações | SPY | dias úteis 1..15 | 35 | +1.343% | 3.627% |
| RF | TLT | dias úteis 1..50 | 34 | -1.636% | 5.743% |

Truncagem do livro de RF: o intervalo entre FOMCs é de **29 a 40 dias úteis** (mediana 30) — com a janela de 50 dias da literatura, **47 de 47** intervalos truncam o livro antes do fim. A janela de 15 dias do livro de ações nunca é truncada (mínimo 29 > 15).

*(intervalo em dias corridos: 41 a 56.)*


## Limites desta medição

- Nenhum orçamento (`lam`, `orcamento_max`, `orcamento_acoes/_rf`) entra na conta: como o `dw` é linear neles, o que está medido é o retorno **por unidade de orçamento**.

- O gap de fim de semana é medido em TODAS as reaberturas, não só nas que teriam sinal do poly — a tática só opera quando alguma view designada tem Δp de fim de semana, e essas views dependem do β (decisão 3.1) e da aprovação da reunião.

- O calendário de CPI entregue começa em 2025 (15 divulgações): o teste do prêmio de CPI é de amostra curta por construção, e o G6 (datas de 2022–2024) só será levantado se a reunião mandar.

