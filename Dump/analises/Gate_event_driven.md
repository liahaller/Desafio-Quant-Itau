# 3.2 event-driven — o salto sobra depois do gap?

> Gerado por `scripts/gate_event_driven.py`. **Mede; não decide.** Nenhum corte cravado, mesma regra do `Gate_sleeves.md`.

- janela do backtest: **2025-02-10 a 2026-08-06** (374 pregões), δ e Σ os mesmos do v1 (D7/D8)
- **salto** = dia cujo |Δp| está no topo do quantil da coluna, na distribuição do PRÓPRIO mercado. `q0.00` = todo dia com Δp ≠ 0, a linha de base
- retornos **alinhados à premissa declarada**: positivo = a premissa se confirmou, qualquer que seja a direção do mercado. Unidade: **bps**
- as duas primeiras pernas são **contemporâneas** ao Δp (o sinal é o slot pré-abertura de D): estão aqui para dizer onde o movimento foi parar, nunca como resultado de tática

✅ **Conferência de base de ajuste passa** — maior desvio de `abertura/fechamento − 1` é 0.064%, dentro do ruído intradiário. As pernas que misturam os dois parquets valem, **inclusive no dia do próprio evento**.

| mercado                                 | corte |Δp|   |   n saltos |   D−1 sessão |   gap |   intra D |   resíduo 1d |   resíduo 3d |   resíduo 5d |
|:----------------------------------------|:-------------|-----------:|-------------:|------:|----------:|-------------:|-------------:|-------------:|
| C1a M3 trajetória do Fed (nº de cortes) | q0.00        |        201 |         -9   |  -2.2 |       8.2 |         -8.9 |        -14.5 |        -21.4 |
| C1a M3 trajetória do Fed (nº de cortes) | q0.50        |        101 |        -13.7 |  -0.3 |      12.4 |        -15   |        -15.8 |        -41.5 |
| C1a M3 trajetória do Fed (nº de cortes) | q0.75        |         51 |        -32.6 |  -2.5 |      21.9 |        -35.8 |        -30.3 |        -64   |
| C1a M3 trajetória do Fed (nº de cortes) | q0.90        |         21 |        -59.5 | -27.2 |      53.5 |        -84.4 |        -67.6 |        -74.8 |
| C1b reunião do FOMC (E_poly em bps)     | q0.00        |        307 |         -4.5 |   1.8 |       5.4 |         -8.4 |         -2   |        -10.5 |
| C1b reunião do FOMC (E_poly em bps)     | q0.50        |        154 |        -10.4 |   1.8 |      10.8 |        -14.2 |          3   |        -10.1 |
| C1b reunião do FOMC (E_poly em bps)     | q0.75        |         77 |        -18.1 |  -2.2 |      19.3 |        -17.1 |          1.7 |         -1.6 |
| C1b reunião do FOMC (E_poly em bps)     | q0.90        |         31 |        -39.3 |   3.1 |      46.2 |        -36.9 |         -0.3 |        -15.7 |
| CPI mensal (E_poly)                     | q0.00        |        266 |          1.9 |   0.5 |      -0.4 |         -0.8 |         -1.8 |          0.4 |
| CPI mensal (E_poly)                     | q0.50        |        133 |          0.2 |   1.3 |      -0.6 |          0.3 |         -4.6 |         -4   |
| CPI mensal (E_poly)                     | q0.75        |         67 |          1.8 |   1.3 |       2.5 |          1.1 |         -4.3 |         -5.5 |
| CPI mensal (E_poly)                     | q0.90        |         27 |         -0.3 |   0.2 |       1.7 |          0.5 |          4.1 |          1   |
| M4 recessão EUA 2025                    | q0.00        |        193 |         12.8 |   4.6 |      -5.5 |          7.3 |         12.5 |          5.6 |
| M4 recessão EUA 2025                    | q0.50        |        107 |         16.8 |   5.9 |     -10.6 |         14.9 |         22.2 |          7.5 |
| M4 recessão EUA 2025                    | q0.75        |         52 |         37.9 |  15.3 |     -20.8 |         27.6 |         31.8 |         22.7 |
| M4 recessão EUA 2025                    | q0.90        |         20 |         51.5 |  33.3 |     -43.3 |          7.5 |        -26.5 |        -38.9 |
| M5 Trump 2024                           | q0.00        |        136 |          0.4 |   5.4 |       4   |         -2.3 |        -12.2 |         -6.5 |
| M5 Trump 2024                           | q0.50        |         94 |          4.8 |  10   |       6.5 |          2.8 |         -7.6 |          3.1 |
| M5 Trump 2024                           | q0.75        |         41 |          3.3 |   6.1 |      10.6 |         10.8 |         -8.8 |          5.8 |
| M5 Trump 2024                           | q0.90        |         19 |         -1.7 |  16   |      20.3 |         34.9 |         10.5 |         26.8 |
| M6 tarifas China                        | q0.00        |          8 |        -43.4 |  11.5 |     -31   |        -56.4 |       -182.6 |       -175.4 |
| M6 tarifas China                        | q0.50        |          4 |       -116.9 |  64.3 |      56.4 |        -39.8 |       -181.7 |       -160.8 |
| M7 ação militar Irã (jun/2025)          | q0.00        |         50 |          5.5 |   6.8 |       1.7 |         10.9 |         -5.4 |        -10   |
| M7 ação militar Irã (jun/2025)          | q0.50        |         26 |          7.5 |  13.2 |      19.8 |         18.7 |         -5.4 |        -19.2 |
| M7 ação militar Irã (jun/2025)          | q0.75        |         13 |         21.8 |  25.4 |      24.8 |         21.8 |         15.4 |          6.1 |
| M7 ação militar Irã (jun/2025)          | q0.90        |          5 |         24.1 |  40.1 |     -12.9 |         57.5 |         21.1 |        -18.6 |
| M7 ataque ao Irã (fev/2026)             | q0.00        |         28 |         17.5 |  19.4 |      -8.9 |        -22.7 |        -31.3 |        -42.9 |
| M7 ataque ao Irã (fev/2026)             | q0.50        |         14 |         14.2 |  27.1 |     -19.7 |        -27.4 |        -18.4 |        -33.6 |
| M7 ataque ao Irã (fev/2026)             | q0.75        |          8 |         15.7 |  36.1 |     -28.5 |        -41.9 |          0.9 |        -22.9 |
| M7 ataque ao Irã (fev/2026)             | q0.90        |          3 |        -16.6 |  17   |      21.6 |        -95.3 |        -22.6 |        -95.3 |
| M9 Câmara                               | q0.00        |         98 |          2   |  -3.5 |       4.2 |          1.5 |          0.5 |         -5.1 |
| M9 Câmara                               | q0.50        |         76 |          2.2 |  -6.5 |       4.8 |          0.3 |         -7.2 |         -5.4 |
| M9 Câmara                               | q0.75        |         27 |         11.4 | -12.7 |      -1.8 |         -3.8 |        -21.5 |        -35   |
| M9 Câmara                               | q0.90        |         22 |         13.4 | -12.8 |      -3   |         -2.3 |        -15.1 |        -24.9 |

## Premissa declarada ANTES de medir

Sem isto o G2 é racionalização, não teste. As três da família Fed/CPI são herdadas do `Gate_sleeves.md` palavra por palavra.

- **C1a M3 trajetória do Fed (nº de cortes)** — crença anda para mais afrouxamento → SPY e TLT sobem (D17, herdada)
- **C1b reunião do FOMC (E_poly em bps)** — idem, com o sinal invertido porque E_poly é Δtaxa (D17, herdada)
- **CPI mensal (E_poly)** — surpresa inflacionária → o indexado (TIP) bate o nominal (TLT) (controle D16 do CPI, herdada)
- **M4 recessão EUA 2025** — p(recessão) sobe → risco-off: bolsa cai e duração sobe
- **M5 Trump 2024** — "Trump trade": p(Trump) sobe → bolsa sobe e duração cai (premissa da view 2.4)
- **M6 tarifas China** — p(tarifa) sobe → guerra comercial: bolsa cai e duração sobe
- **M7 ação militar Irã (jun/2025)** — p(ação militar) sobe → petróleo sobe (XLE) e bolsa cai (premissa da view C)
- **M7 ataque ao Irã (fev/2026)** — idem, segundo episódio
- **M9 Câmara** — mecanismo partidário, espelho do M5. ⚠️ é exatamente o mecanismo que a 2.4 mediu como NÃO reproduzindo fora da amostra

## G2 e G3 no corte mais exigente (q0.90)

| mercado                                 |   G0 saltos (q0.90) |   eventos no μ | G2 μ (bps/dia)              | G2 bate?   | G3 maior \|corr\|           |
|:----------------------------------------|--------------------:|---------------:|:----------------------------|:-----------|:----------------------------|
| C1a M3 trajetória do Fed (nº de cortes) |                  21 |             21 | SPY -0.74 ❌ · TLT -0.90 ❌ | ❌         | -0.25 (entropia CPI (15b))  |
| C1b reunião do FOMC (E_poly em bps)     |                  31 |             31 | SPY +0.87 ❌ · TLT +0.21 ❌ | ❌         | +0.54 (divergência da 2.3)  |
| CPI mensal (E_poly)                     |                  27 |             27 | TIP +0.10 ✅ · TLT +0.00 ❌ | ❌         | +0.35 (divergência da 2.2)  |
| M4 recessão EUA 2025                    |                  20 |             20 | SPY -0.70 ✅ · TLT -0.59 ❌ | ❌         | -0.39 (entropia CPI (15b))  |
| M5 Trump 2024                           |                  19 |             19 | SPY +0.58 ✅ · TLT -0.74 ✅ | ✅         | —                           |
| M7 ação militar Irã (jun/2025)          |                   5 |              5 | XLE +0.93 ✅ · SPY -0.52 ✅ | ✅         | -0.94 (entropia FOMC (15b)) |
| M7 ataque ao Irã (fev/2026)             |                   3 |              3 | XLE -0.76 ❌ · SPY +0.23 ❌ | ❌         | -1.00 (divergência da 2.3)  |
| M9 Câmara                               |                  22 |             22 | SPY +1.51 ❌ · TLT +0.47 ✅ | ❌         | -0.30 (entropia CPI (15b))  |

## Leitura

**A pergunta da D26, respondida.** Fração do movimento total (em módulo, as quatro pernas) que está no resíduo de 1 pregão — ou seja, o que sobra do fechamento do dia do salto em diante, no corte q0.90: **M7 ataque ao Irã (fev/2026)** -63% · **M5 Trump 2024** +48% · **M7 ação militar Irã (jun/2025)** +43% · **C1a M3 trajetória do Fed (nº de cortes)** -38% · **C1b reunião do FOMC (E_poly em bps)** -29% · **CPI mensal (E_poly)** +19% · **M9 Câmara** -7% · **M4 recessão EUA 2025** +6%.

A mediana entre os 8 mercados é **-1%**, e **4 de 8** têm resíduo na direção que a premissa declara. Sinal negativo aqui não é "pouco sinal": é o resíduo andando CONTRA a premissa, e pela D2b não se inverte.

**O condicionamento por salto informa?** Resíduo de 1 pregão na linha de base (`q0.00`) contra o corte mais exigente (`q0.90`): **C1a M3 trajetória do Fed (nº de cortes)** -8.9 → -84.4 bps · **C1b reunião do FOMC (E_poly em bps)** -8.4 → -36.9 bps · **CPI mensal (E_poly)** -0.8 → +0.5 bps · **M4 recessão EUA 2025** +7.3 → +7.5 bps · **M5 Trump 2024** -2.3 → +34.9 bps · **M7 ação militar Irã (jun/2025)** +10.9 → +57.5 bps · **M7 ataque ao Irã (fev/2026)** -22.7 → -95.3 bps · **M9 Câmara** +1.5 → -2.3 bps. Sobem em **4 de 8** mercados. Se o resíduo não melhora quando se exige um salto maior, "salto" não é informação — é só o mesmo Δp com menos observações.

**2 de 8 mercados passam no G2** no corte q0.90: **M5 Trump 2024**, **M7 ação militar Irã (jun/2025)**. Passar no G2 **não é aprovação** — o gate mede e o destino segue sendo decisão do dono. O que isto habilita é o G4 (P&L da sleeve), que é o primeiro critério que exige módulo.

⚠️ **Cada ✅ acima, com o que a enfraquece:**

- **M5 Trump 2024** — μ de **19 eventos**; **G3 não mensurável**: o mercado não sobrepõe as séries que as views vivas leem, então a duplicação não foi testada — não é ✅, é vazio; a **view 2.4** leu este mercado e foi cortada: o efeito aterrissa no gap (23% sobra na janela negociável) e o mecanismo partidário **reprovou fora da amostra** — o TLT cai nos dois mercados, quando deveria inverter.
- **M7 ação militar Irã (jun/2025)** — μ de **5 eventos**; G3 -0.94 (entropia FOMC (15b)); a **view C** leu este mercado e não entrou (D23f): o critério pré-registrado para fixar o `k` **não identifica k** (corr +0,08 entre os dois episódios) e o único lag em que eles concordam é o **lag 0** — o gap de abertura.

**O que isto NÃO diz:** nada sobre P&L, e nada sobre a 1.1. A 3.2 lê o SALTO; a 1.1 lê a RESOLUÇÃO, e nenhuma linha desta tabela toca a segunda. G4 continua exigindo backtest, e backtest exige o módulo que este protocolo se recusa a escrever antes de a linha passar.

