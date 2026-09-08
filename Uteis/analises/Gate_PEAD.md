# 1.1 PEAD — a surpresa da resolução deixa drift para trás?

> Gerado por `scripts/gate_pead.py`. **Mede; não decide.** Nenhum corte cravado, mesma regra do `Gate_sleeves.md`.

> ✅ **A decisão 5 FECHOU** (dono, 2026-08-11): *surpresa = resolução − probabilidade precificada na véspera*, contínua. É a mesma definição sob a qual este artefato já media — o número não mudou com o fechamento, só o status.

- janela do backtest: **2025-02-10 a 2026-08-06** (374 pregões), δ e Σ os mesmos do v1 (D7/D8)
- **h** = pregões DEPOIS do fechamento do dia do anúncio. É o eixo novo contra a D16, que mediu uma janela só
- retornos **alinhados à premissa declarada** (positivo = premissa confirmada), em **bps**

**Premissa declarada ANTES de medir:** idem, com o sinal invertido porque E_poly é Δtaxa (D17, herdada) — para a resolução, surpresa positiva = decisão mais dura que a precificada. É a do controle de FOMC do `Gate_sleeves.md`, herdada **por referência** (o script importa o mesmo dicionário, não uma cópia).

## G0 — de quais famílias a resolução é observável no dado

É aqui que a 1.1 é decidida, e não no G2.

| família | resolução no dado? | eventos | por quê |
|---|---|---|---|
| **FOMC** | ✅ | **17** | decisão realizada do DFF × E_poly da véspera |
| **CPI** | ✅ | **12** | MoM realizado do `CPIAUCSL` × E_poly da véspera. **Destravado nesta sessão** (item 8 da D28): antes o `data/` só tinha as DATAS de divulgação. A série do poly seguir terminando na véspera deixou de bloquear — a véspera é justamente o que a surpresa usa |
| **binários** | ⚠️ | 7 mercados × **1 evento cada** | a resolução só existe para o que o pull alcançou, e um evento por mercado não dá μ |

## FOMC — as 17 reuniões pareadas

| reunião    |   surpresa (bps) |
|:-----------|-----------------:|
| 2024-05-01 |             0.09 |
| 2024-06-12 |             0.75 |
| 2024-07-31 |             1.31 |
| 2024-09-18 |            -5.34 |
| 2024-11-07 |            -0.4  |
| 2024-12-18 |            -0.57 |
| 2025-01-29 |             0.52 |
| 2025-03-19 |             0.29 |
| 2025-05-07 |             0.54 |
| 2025-06-18 |             0.5  |
| 2025-07-30 |             0.75 |
| 2025-09-17 |             2.1  |
| 2025-12-10 |            -0.92 |
| 2026-01-28 |             0.18 |
| 2026-03-18 |             0.1  |
| 2026-04-29 |             0.02 |
| 2026-06-17 |             0.41 |

**G1 da surpresa: mediana |surpresa| ÷ tick do FRED (1 bp) = 0.5×.**

## Pernas e sweep da janela pós-anúncio

| janela   |   n reuniões |   D−1 sessão |   gap |   intra D |   resíduo |   eventos no μ | G2 μ (bps/dia)              | G2 bate?   |
|:---------|-------------:|-------------:|------:|----------:|----------:|---------------:|:----------------------------|:-----------|
| h = 1    |           17 |         -6.5 | -16.4 |         4 |      -7.2 |             17 | SPY -0.25 ✅ · TLT +0.44 ❌ | ❌         |
| h = 3    |           17 |         -6.5 | -16.4 |         4 |     -31.7 |             17 | SPY +0.13 ❌ · TLT +0.93 ❌ | ❌         |
| h = 5    |           17 |         -6.5 | -16.4 |         4 |     -46.8 |             17 | SPY +0.56 ❌ · TLT +1.76 ❌ | ❌         |
| h = 10   |           17 |         -6.5 | -16.4 |         4 |     -83.7 |             17 | SPY +3.88 ❌ · TLT +1.64 ❌ | ❌         |
| h = 15   |           17 |         -6.5 | -16.4 |         4 |    -108.5 |             17 | SPY +4.91 ❌ · TLT +1.37 ❌ | ❌         |

**G3** — maior |correlação| da surpresa com o que as views vivas já leem: **+0.72** (divergência da 2.3)

## CPI — as 12 divulgações pareadas

**A família que o G0 barrava.** A premissa é a do controle de CPI da D16, herdada por referência: surpresa inflacionária → o indexado (TIP) bate o nominal (TLT) (controle D16 do CPI, herdada) — surpresa positiva = inflação acima do precificado.

| divulgação   |   surpresa (p.p.) |
|:-------------|------------------:|
| 2025-03-12   |             -0.11 |
| 2025-04-10   |             -0.12 |
| 2025-06-11   |             -0.05 |
| 2025-07-15   |              0.06 |
| 2025-08-12   |             -0.04 |
| 2025-09-11   |             -0.04 |
| 2025-10-24   |             -0.06 |
| 2026-01-13   |              0.03 |
| 2026-04-10   |              0.07 |
| 2026-05-12   |              0    |
| 2026-06-10   |             -0    |
| 2026-07-14   |             -0.45 |

**G1 da surpresa: mediana |surpresa| ÷ tick da grade de baldes (0,1 p.p.) = 0.6×.**

| janela   |   n divulgações |   D−1 sessão |   gap |   intra D |   resíduo |   eventos no μ | G2 μ (bps/dia)              | G2 bate?   |
|:---------|----------------:|-------------:|------:|----------:|----------:|---------------:|:----------------------------|:-----------|
| h = 1    |              12 |          4.3 |  -3.7 |       0.8 |      15.1 |             12 | TIP -0.10 ❌ · TLT -1.11 ✅ | ❌         |
| h = 3    |              12 |          4.3 |  -3.7 |       0.8 |      11   |             12 | TIP -0.07 ❌ · TLT -1.18 ✅ | ❌         |
| h = 5    |              12 |          4.3 |  -3.7 |       0.8 |       5.8 |             12 | TIP -0.07 ❌ · TLT -0.47 ✅ | ❌         |
| h = 10   |              12 |          4.3 |  -3.7 |       0.8 |      -1.4 |             12 | TIP -0.08 ❌ · TLT -0.02 ✅ | ❌         |
| h = 15   |              12 |          4.3 |  -3.7 |       0.8 |     -11.6 |             12 | TIP -0.16 ❌ · TLT +0.50 ❌ | ❌         |

**G3** — maior |correlação| da surpresa do CPI com o que as views vivas já leem: **+0.58** (divergência da 2.2)

## Binários — a resolução que o pull alcançou

Sem classificar "resolveu"/"não resolveu": o corte seria threshold inventado. O `p final` diz sozinho se o mercado foi a 0/1 ou se o pull parou no meio.

| mercado                        | última leitura   |   p final |   p véspera |   surpresa (p.p.) |   eventos |
|:-------------------------------|:-----------------|----------:|------------:|------------------:|----------:|
| M4 recessão EUA 2025           | 2025-12-31       |     0.003 |       0.003 |               0   |         1 |
| M5 Trump 2024                  | 2024-11-06       |     0.999 |       0.623 |              37.6 |         1 |
| M6 tarifas China               | 2025-04-15       |     1     |       0.995 |               0.5 |         1 |
| M7 ação militar Irã (jun/2025) | 2025-06-21       |     0.418 |       0.44  |              -2.2 |         1 |
| M7 ataque ao Irã (fev/2026)    | 2026-02-27       |     0.165 |       0.095 |               7   |         1 |
| M8 reconciliação fiscal        | 2025-07-03       |     0.88  |       0.265 |              61.5 |         1 |
| M9 Câmara                      | 2026-07-29       |     0.855 |       0.855 |               0   |         1 |

## Leitura

**Calibração:** a mediana da |surpresa| nas 17 reuniões é **0.52 bps**. A D16 registrou **0,52 bps em 17 reuniões** para a mesma construção — **reproduz**. Isso confirma o que a docstring declara: **a família do Fed da 1.1 é a sleeve da D16 com outro nome.** O que este artefato acrescenta é a decomposição em pernas e o sweep de `h`; a surpresa em si já estava medida, e é ~zero.

**E a identidade não é argumento, é medida:** a linha **h = 15** sai com μ `SPY +4.91 ❌ · TLT +1.37 ❌` — **o mesmo μ, dígito por dígito**, que o `Gate_sleeves.md` registra para o controle de FOMC da D16. A janela daquela sleeve era essa, e reencontrá-la aqui por outro caminho fecha a questão: a 1.1 aplicada ao Fed não é candidata nunca medida — **é a sleeve reprovada da D16**. O que continua nunca medido é a 1.1 **fora** do Fed, e é o G0 que impede.

**O G1 da surpresa é 0.5× o tick do FRED.** Abaixo de 1×: a surpresa típica de uma reunião é menor que a granularidade com que a fonte publica a taxa. Não é sinal fraco — é sinal dentro do ruído de discretização, o mesmo motivo que matou a C1a e a C1b.

**Onde o movimento aterrissa** (h = 1, em bps alinhados à premissa): D−1 sessão -6.5 · gap -16.4 · intra D +4.0 · resíduo -7.2. As duas primeiras pernas são anteriores ao anúncio e estão aqui só como contexto — a resolução do FOMC sai às 14h ET, dentro da sessão, então para a 1.1 a perna **`intra D` já é parcialmente negociável** e o `resíduo` é o PEAD propriamente dito.

**Nenhuma janela passa no G2:** h = 1 (`SPY -0.25 ✅ · TLT +0.44 ❌`) · h = 3 (`SPY +0.13 ❌ · TLT +0.93 ❌`) · h = 5 (`SPY +0.56 ❌ · TLT +1.76 ❌`) · h = 10 (`SPY +3.88 ❌ · TLT +1.64 ❌`) · h = 15 (`SPY +4.91 ❌ · TLT +1.37 ❌`). O μ pós-anúncio sai contra Bernanke-Kuttner em toda a grade, e pela D2b não se inverte. **O drift pós-resolução não existe na direção que a teoria manda**, em nenhum horizonte entre 1 e 15 pregões.

**A 1.1 FORA do Fed deixou de ser hipótese e virou medição.** Com o `CPIAUCSL` no `data/` (item 8 da D28), 12 divulgações ficaram pareadas — a família que o G0 barrava. E o veredito é: **nenhuma janela passa no G2.** O μ pós-divulgação sai contra a premissa declarada em toda a grade, e pela D2b não se inverte.

**E o motivo é o mesmo do Fed: a surpresa não tem tamanho.** A mediana da |surpresa| é **0.06 p.p.** contra uma grade de baldes que anda de 0,1 p.p. — G1 de **0.6×**, abaixo de 1, que é o mesmo diagnóstico de ruído de discretização que matou a C1a, a C1b e a família do Fed desta candidata. O poly erra o CPI por menos que a granularidade com que ele próprio pergunta.

⚠️ **E ela não é território livre:** a surpresa do CPI tem |correlação| de **+0.58** com divergência da 2.2, que uma view VIVA já lê. Mesmo se o G2 tivesse passado, o G3 cobraria a sobreposição.

**O que isto NÃO diz:** nada sobre P&L, e nada sobre a 3.2. A 1.1 lê a RESOLUÇÃO; a 3.2 lê o SALTO, e está medida em `Gate_event_driven.md`.

