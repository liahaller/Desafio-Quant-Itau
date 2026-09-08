# Premissa empírica das 3 táticas candidatas

> Gerado por `scripts/premissa_taticas.py` sobre o dado do G1/G2 (follow-up 2). **Mede a premissa; não escolhe parâmetro nem liga tática** — a ENTRADA da camada segue pendente de reunião (decisão 10). Leia o bloco de base de ajuste antes das tabelas: ele diz se algum número está contaminado por um problema do dado, e não pela tática.

## Antes dos números: os dois parquets estão na MESMA base

Mediana de `abertura/fechamento − 1` por ticker. Se as duas séries estivessem no mesmo ajuste, isso seria ruído intradiário (± 0,1%):

| SPY | TIP | TLT | XLE | XLF | XLK | XLP | XLU | XLV |
|---|---|---|---|---|---|---|---|---|
| -0.059% | +0.000% | -0.023% | -0.046% | -0.038% | -0.064% | -0.042% | -0.034% | -0.027% |

**Nenhum ticker acima de ± 0.1% — a conferência passa.** O deslocamento de TIP e TLT que contaminava as médias intradiárias desta análise (ex-dividendo entre os pulls de `etf_prices_daily.parquet` e `etf_open_daily.parquet`, com `auto_adjust=True` reescalando um arquivo só) **não está mais no dado**: os dois arquivos vieram no mesmo ajuste. As janelas intradiárias abaixo valem para todos os tickers, inclusive no dia do próprio evento.

## Gap de fim de semana — a tática entra DEPOIS do salto

1183 reaberturas (pregão anterior a ≥ 3 dias corridos, o que inclui feriado prolongado) contra 4519 demais pregões, 2003-12-05 → 2026-08-06.

**O salto que a tática NÃO captura** (`close sexta → abertura segunda`) e o pedaço que ela captura (`abertura → fechamento de segunda`):

| ativo | salto médio | σ do salto | intradiário médio | σ intradiário | corr(salto, intradiário) | t da corr |
|---|---|---|---|---|---|---|
| SPY | +0.019% | 0.837% | +0.014% | 0.878% | +0.128 | +4.42 |
| TIP | +0.001% | 0.221% | -0.016% | 0.280% | +0.001 | +0.05 |
| TLT | -0.018% | 0.662% | +0.011% | 0.604% | -0.027 | -0.93 |
| XLE | +0.024% | 1.350% | -0.013% | 1.488% | +0.106 | +3.67 |
| XLF | +0.009% | 1.260% | -0.055% | 1.426% | +0.090 | +3.12 |
| XLK | +0.015% | 1.072% | +0.068% | 1.098% | -0.101 | -3.50 |
| XLP | +0.008% | 0.686% | +0.028% | 0.744% | -0.252 | -8.96 |
| XLU | +0.054% | 0.677% | -0.008% | 1.043% | +0.010 | +0.34 |
| XLV | +0.031% | 0.699% | -0.035% | 0.864% | -0.045 | -1.53 |

Leitura: **correlação positiva** = o mercado continua na direção do salto depois de abrir (a premissa da tática se sustenta); **≈ 0** = o salto do fim de semana já está inteiro no preço de abertura e a tática entra tarde; **negativa** = reversão, e o tilt na direção do Δp opera contra o dado.

Intradiário de reabertura contra os demais dias (é a janela exata da tática, `abertura → fechamento`):

| amostra | n | média | σ | t |
|---|---|---|---|---|
| SPY — dias de reabertura | 1183 | +0.014% | 0.878% | +0.54 |
| SPY — demais pregões | 4519 | +0.015% | 0.922% | +1.09 |

## Prêmio de anúncios (1.3) — âncora Savor & Wilson

Retorno do SPY de `fechamento(D−1) → fechamento(D)`, que é a janela declarada pela tática, em dia de anúncio agendado contra os demais.

| amostra | n | média | σ | t |
|---|---|---|---|---|
| FOMC (2022-01-26 → 2026-07-29) | 37 | +0.018% | 1.350% | +0.08 |
| demais pregões da mesma janela (FOMC) | 1093 | +0.059% | 1.096% | +1.77 |
| CPI (2025-03-12 → 2026-07-14) | 13 | -0.210% | 1.441% | -0.53 |
| demais pregões da mesma janela (CPI) | 323 | +0.114% | 1.120% | +1.83 |
| FOMC + CPI juntos | 50 | -0.041% | 1.363% | -0.21 |

A tática é long SPY vs caixa **dimensionada pela entropia da PMF**; o que está medido aqui é só a âncora (o prêmio existe na amostra?), não o sinal — a modulação por entropia depende da decisão 11a (correção de favorite-longshot), que ainda falha alto de propósito.


## Drift pós-FOMC — tamanho da janela (o sinal não é testável aqui)

A direção do tilt é `−sign(surpresa)`, e a surpresa vem do ZQ, que **não tem fonte definida** (o yfinance não serve — decisão de grupo pendente). Sem ela não dá para testar o drift; dá para medir o **tamanho** da janela que a tática ocuparia, que é o teto do que a sleeve pode render.

37 anúncios do FOMC caem em pregão, 2022-01-26 → 2026-07-29 (o calendário entregue começa em 2022-01-26).

| livro | ativo | janela | n eventos | acumulado médio | σ do acumulado |
|---|---|---|---|---|---|
| ações | SPY | dias úteis 1..15 | 36 | +1.366% | 3.577% |
| RF | TLT | dias úteis 1..50 | 35 | -1.615% | 5.659% |

Truncagem do livro de RF: o intervalo entre FOMCs é de **29 a 40 dias úteis** (mediana 30) — com a janela de 50 dias da literatura, **47 de 47** intervalos truncam o livro antes do fim. A janela de 15 dias do livro de ações nunca é truncada (mínimo 29 > 15).

*(intervalo em dias corridos: 41 a 56.)*


## Limites desta medição

- Nenhum orçamento (`lam`, `orcamento_max`, `orcamento_acoes/_rf`) entra na conta: como o `dw` é linear neles, o que está medido é o retorno **por unidade de orçamento**.

- O gap de fim de semana é medido em TODAS as reaberturas, não só nas que teriam sinal do poly — a tática só opera quando alguma view designada tem Δp de fim de semana, e essas views dependem do β (decisão 3.1) e da aprovação da reunião.

- O calendário de CPI entregue começa em 2025 (15 divulgações): o teste do prêmio de CPI é de amostra curta por construção, e o G6 (datas de 2022–2024) só será levantado se a reunião mandar.

