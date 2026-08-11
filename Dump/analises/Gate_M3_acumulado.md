# G2 e G3 do M3 acumulado — o último candidato de pé

> Gerado por `scripts/gate_m3_acumulado.py`. **Mede; não decide.** Nenhum corte cravado, mesma regra do `Gate_sleeves.md`.

- janela do backtest: **2025-02-10 a 2026-08-06** (374 pregões), δ e Σ os mesmos do v1 (D7/D8)
- **sinal** = Δ do nº esperado de cortes do Fed (M3) sobre `k` pregões. `k` é **lookback**; a posição é reassinada todo dia (janela do event-study = 1), igual ao C1a da D17
- **G2** = μ do `tatica_drift_anuncio.estimate_drift_mu` (linha de base subtraída, encolhido pela dispersão) contra o sinal DECLARADO
- **G3** = correlação com o sinal que as quatro views vivas já leem

**Premissa declarada ANTES de medir:** crença anda para mais afrouxamento → SPY e TLT sobem (declarada na D17 para o C1a, herdada sem alteração). Ela é a da D17, herdada palavra por palavra — reescrevê-la depois de ver o k = 1 falhar destruiria o que faz do G2 um teste.

**G4 (P&L da sleeve sozinha) não está aqui de propósito:** exige backtest, backtest exige o módulo, e o módulo é o que este protocolo se recusa a escrever antes de a linha passar.

| lookback   |   G0 dias |   eventos no μ | G2 μ (bps/dia)              | G2 bate?   | G3 maior \|corr\|          |
|:-----------|----------:|---------------:|:----------------------------|:-----------|:---------------------------|
| k = 1      |       201 |            201 | SPY -3.87 ❌ · TLT +0.03 ✅ | ❌         | -0.19 (entropia CPI (15b)) |
| k = 2      |       200 |            200 | SPY -0.60 ❌ · TLT -1.43 ❌ | ❌         | -0.31 (entropia CPI (15b)) |
| k = 3      |       199 |            199 | SPY -0.95 ❌ · TLT -0.78 ❌ | ❌         | -0.32 (entropia CPI (15b)) |
| k = 5      |       197 |            197 | SPY -2.16 ❌ · TLT -1.45 ❌ | ❌         | -0.34 (entropia CPI (15b)) |
| k = 10     |       194 |            194 | SPY -0.92 ❌ · TLT -1.43 ❌ | ❌         | -0.36 (entropia CPI (15b)) |
| k = 20     |       184 |            184 | SPY +1.38 ✅ · TLT -1.01 ❌ | ❌         | -0.42 (entropia CPI (15b)) |

## Correlações do G3, uma a uma

| lookback   |   corr divergência da 2.2 |   corr divergência da 2.3 |   corr entropia CPI (15b) |   corr entropia FOMC (15b) |
|:-----------|--------------------------:|--------------------------:|--------------------------:|---------------------------:|
| k = 1      |                      0.06 |                     -0.04 |                     -0.19 |                       0.1  |
| k = 2      |                      0.05 |                     -0.04 |                     -0.31 |                       0.09 |
| k = 3      |                      0.08 |                     -0.01 |                     -0.32 |                       0.08 |
| k = 5      |                      0.09 |                      0.05 |                     -0.34 |                       0.04 |
| k = 10     |                      0.29 |                      0.11 |                     -0.36 |                       0.06 |
| k = 20     |                      0.3  |                      0.06 |                     -0.42 |                       0.23 |

## Leitura

**Calibração:** em k = 1 esta linha é o C1a da D17 — μ `SPY -3.87 ❌ · TLT +0.03 ✅`. O `Gate_sleeves.md` traz `SPY -4.20 ❌ · TLT +0.03 ✅` para o mesmo candidato: **mesmo veredito e mesmo sinal em cada ativo**, com o SPY diferindo na primeira casa. A diferença é conhecida e é o preço da correção de horizonte — aqui a série é reindexada em dias úteis antes do `diff` (`em_pregoes`), para que `k` signifique pregões; lá o `diff` anda leituras. Reproduzir o VEREDITO é o que a calibração pede; reproduzir o dígito exigiria abrir mão da própria correção que motiva este script.

**O G3 piora conforme o lookback cresce:** k = 1: -0.19 · k = 2: -0.31 · k = 3: -0.32 · k = 5: -0.34 · k = 10: -0.36 · k = 20: -0.42, sempre contra a **entropia CPI (15b)**. Acumular não é de graça no critério de duplicação — quanto mais dias o Δ da crença sobre o Fed soma, mais ele se parece com a incerteza que a view 15b já lê. Mesmo que o G2 tivesse passado num k longo, seria ali que o G3 estaria pior.

**Nenhum horizonte passa no G2.** k = 1 (`SPY -3.87 ❌ · TLT +0.03 ✅`), k = 2 (`SPY -0.60 ❌ · TLT -1.43 ❌`), k = 3 (`SPY -0.95 ❌ · TLT -0.78 ❌`), k = 5 (`SPY -2.16 ❌ · TLT -1.45 ❌`), k = 10 (`SPY -0.92 ❌ · TLT -1.43 ❌`), k = 20 (`SPY +1.38 ✅ · TLT -1.01 ❌`). O μ sai contra a premissa declarada em todos os lookbacks da grade, e pela D2b não se inverte. **O acúmulo resolveu o problema de tamanho e não produziu previsão:** o sinal saiu de dentro do tick (G1) e continua não antecipando o retorno dos ativos na direção que a teoria manda.

**Consequência para a camada tática.** O M3 era a única série do dado entregue com cobertura e dispersão ao mesmo tempo, e a única livre de duplicação com as views vivas. Com ele reprovado, o estoque de candidatos nunca medidos fica assim:

- **velocidade de ajuste** e **1.2 momentum** — sem hipótese. As duas leem o movimento da crença para prever o próximo movimento da crença, e o `Premissa_tendencia.md` mediu VR ≈ 1 e nenhuma autocorrelação ex-ante. Não é falta de teste: é a tese contrariada pelo dado.
- **3.2 event-driven** — o gatilho é o SALTO da probabilidade, que é o padrão com maior chance de aterrissar no gap de abertura, a parede que já derrubou a 2.4, a C, a E e o gap de fim de semana. Mede-se antes de escrever módulo, como tudo aqui.
- **1.1 PEAD** — **a única que nada nesta cadeia toca.** Ela lê a RESOLUÇÃO do mercado, não o Δ diário: nem o G1 (que é sobre movimento diário) nem o teste de tendência dizem qualquer coisa sobre ela. Segue travada pela **decisão 5**, aberta e vazia — sem definição operacional de "surpresa" não há sinal a construir. É decisão humana, não script.

Ou seja: **o caminho de ler o repreçamento do poly está esgotado no dado que temos**, e o que resta ou depende de decisão humana (1.1) ou de um teste de gap ainda não feito (3.2).

**O que isto NÃO diz:** nada sobre P&L. G2 e G3 são condições de admissão — o resultado da estratégia é o G4, e ele exige backtest.

