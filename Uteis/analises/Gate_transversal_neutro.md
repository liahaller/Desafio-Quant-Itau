# Transversal — livro neutro de beta e o cruzamento com o SALTO

> Gerado por `scripts/gate_transversal_neutro.py`. **Mede; não decide.** Nenhum corte cravado, nenhuma premissa nova — livros, premissas e grades são importados dos artefatos anteriores.

- janela do backtest: **2025-02-10 a 2026-08-06** (374 pregões), δ e Σ os mesmos do v1 (D7/D8)
- **NEUTRO** = cada perna com o beta de mercado removido, por β **expansivo defasado em 1 dia** e semeado em 60 pregões (`MINIMO_PREGOES`, a constante que a 15f e a 3.1 direcional já usam). Sem lookahead: em cada data o hedge só conhece o passado
- **CRU** = o livro do `Gate_transversal.md`, pesos +1/−1 sem hedge

## Conferência — o hedge fez o que prometeu?

Se esta tabela não mostrar a coluna NEUTRO perto de zero, o resto do artefato não vale: seria hedge que não hedgeia.

| livro     |   corr(spread, SPY) CRU |   corr(spread, SPY) NEUTRO |
|:----------|------------------------:|---------------------------:|
| +XLK −XLF |                   -0.16 |                       0.17 |
| −XLK +XLF |                    0.16 |                      -0.17 |
| +XLE −XLK |                    0.01 |                      -0.12 |
| +XLP −XLK |                   -0.56 |                      -0.12 |
| +XLF −XLP |                    0.59 |                      -0.1  |
| +XLF −XLU |                    0.48 |                      -0.04 |

## Parte A — Δp acumulado em `k`, três livros lado a lado

| mercado                                 | lookback   |   G0 dias | direcional   | setorial CRU   | setorial NEUTRO   | μ do neutro (bps/dia)         |
|:----------------------------------------|:-----------|----------:|:-------------|:---------------|:------------------|:------------------------------|
| C1a M3 trajetória do Fed (nº de cortes) | k = 1      |       201 | ❌           | ❌             | ❌                | XLK⊥ -1.56 ❌ · XLF⊥ +1.55 ❌ |
| C1a M3 trajetória do Fed (nº de cortes) | k = 2      |       200 | ❌           | ❌             | ❌                | XLK⊥ -0.24 ❌ · XLF⊥ -0.80 ✅ |
| C1a M3 trajetória do Fed (nº de cortes) | k = 3      |       199 | ❌           | ❌             | ❌                | XLK⊥ -0.36 ❌ · XLF⊥ +0.35 ❌ |
| C1a M3 trajetória do Fed (nº de cortes) | k = 5      |       197 | ❌           | ❌             | ❌                | XLK⊥ +0.25 ✅ · XLF⊥ +1.52 ❌ |
| C1a M3 trajetória do Fed (nº de cortes) | k = 10     |       194 | ❌           | ❌             | ❌                | XLK⊥ +1.32 ✅ · XLF⊥ +0.72 ❌ |
| C1a M3 trajetória do Fed (nº de cortes) | k = 20     |       184 | ❌           | ❌             | ✅                | XLK⊥ +2.91 ✅ · XLF⊥ -0.20 ✅ |
| C1b reunião do FOMC (E_poly em bps)     | k = 1      |       317 | ❌           | ❌             | ❌                | XLK⊥ +1.25 ❌ · XLF⊥ -0.99 ❌ |
| C1b reunião do FOMC (E_poly em bps)     | k = 2      |       316 | ❌           | ❌             | ❌                | XLK⊥ +0.03 ❌ · XLF⊥ +0.36 ✅ |
| C1b reunião do FOMC (E_poly em bps)     | k = 3      |       314 | ❌           | ❌             | ❌                | XLK⊥ +1.32 ❌ · XLF⊥ -0.94 ❌ |
| C1b reunião do FOMC (E_poly em bps)     | k = 5      |       313 | ❌           | ✅             | ✅                | XLK⊥ -2.10 ✅ · XLF⊥ +1.68 ✅ |
| C1b reunião do FOMC (E_poly em bps)     | k = 10     |       308 | ❌           | ✅             | ✅                | XLK⊥ -0.37 ✅ · XLF⊥ +1.23 ✅ |
| C1b reunião do FOMC (E_poly em bps)     | k = 20     |       302 | ❌           | ✅             | ✅                | XLK⊥ -2.11 ✅ · XLF⊥ +1.23 ✅ |
| CPI mensal (E_poly)                     | k = 1      |       269 | ❌           | ❌             | ❌                | XLE⊥ +1.72 ✅ · XLK⊥ +2.05 ❌ |
| CPI mensal (E_poly)                     | k = 2      |       264 | ❌           | ❌             | ❌                | XLE⊥ +4.47 ✅ · XLK⊥ +1.93 ❌ |
| CPI mensal (E_poly)                     | k = 3      |       259 | ❌           | ❌             | ❌                | XLE⊥ +2.66 ✅ · XLK⊥ +1.94 ❌ |
| CPI mensal (E_poly)                     | k = 5      |       250 | ❌           | ❌             | ❌                | XLE⊥ +0.64 ✅ · XLK⊥ +0.03 ❌ |
| CPI mensal (E_poly)                     | k = 10     |       235 | ❌           | ❌             | ❌                | XLE⊥ -0.92 ❌ · XLK⊥ +0.36 ❌ |
| CPI mensal (E_poly)                     | k = 20     |       203 | ❌           | ❌             | ❌                | XLE⊥ +0.14 ✅ · XLK⊥ +0.27 ❌ |
| M4 recessão EUA 2025                    | k = 1      |       253 | ❌           | ❌             | ❌                | XLP⊥ -0.02 ❌ · XLK⊥ -1.48 ✅ |
| M4 recessão EUA 2025                    | k = 2      |       252 | ❌           | ❌             | ✅                | XLP⊥ +0.42 ✅ · XLK⊥ -0.21 ✅ |
| M4 recessão EUA 2025                    | k = 3      |       251 | ✅           | ✅             | ✅                | XLP⊥ +4.92 ✅ · XLK⊥ -3.02 ✅ |
| M4 recessão EUA 2025                    | k = 5      |       249 | ✅           | ✅             | ✅                | XLP⊥ +3.62 ✅ · XLK⊥ -3.39 ✅ |
| M4 recessão EUA 2025                    | k = 10     |       244 | ❌           | ❌             | ✅                | XLP⊥ +2.39 ✅ · XLK⊥ -2.47 ✅ |
| M4 recessão EUA 2025                    | k = 20     |       234 | ❌           | ❌             | ✅                | XLP⊥ +1.51 ✅ · XLK⊥ -0.02 ✅ |
| M5 Trump 2024                           | k = 1      |       218 | ❌           | ✅             | ✅                | XLF⊥ +2.11 ✅ · XLP⊥ -0.14 ✅ |
| M5 Trump 2024                           | k = 2      |       217 | ❌           | ❌             | ❌                | XLF⊥ +0.62 ✅ · XLP⊥ +0.19 ❌ |
| M5 Trump 2024                           | k = 3      |       216 | ❌           | ❌             | ❌                | XLF⊥ +1.22 ✅ · XLP⊥ +1.37 ❌ |
| M5 Trump 2024                           | k = 5      |       214 | ❌           | ❌             | ❌                | XLF⊥ -0.30 ❌ · XLP⊥ +0.58 ❌ |
| M5 Trump 2024                           | k = 10     |       209 | ❌           | ❌             | ❌                | XLF⊥ +0.10 ✅ · XLP⊥ +2.10 ❌ |
| M5 Trump 2024                           | k = 20     |       199 | ❌           | ✅             | ❌                | XLF⊥ -0.36 ❌ · XLP⊥ -1.39 ✅ |
| M6 tarifas China                        | k = 1      |         8 | ❌           | ❌             | ❌                | XLP⊥ -0.26 ❌ · XLK⊥ +0.38 ❌ |
| M6 tarifas China                        | k = 2      |         7 | ❌           | ❌             | ❌                | XLP⊥ +0.05 ✅ · XLK⊥ +0.18 ❌ |
| M6 tarifas China                        | k = 3      |         6 | ❌           | ❌             | ❌                | XLP⊥ +0.09 ✅ · XLK⊥ +0.21 ❌ |
| M6 tarifas China                        | k = 5      |         4 | ❌           | ✅             | ✅                | XLP⊥ +0.26 ✅ · XLK⊥ -0.13 ✅ |
| M7 ação militar Irã (jun/2025)          | k = 1      |        58 | ❌           | ❌             | ❌                | XLE⊥ +1.83 ✅ · XLK⊥ +0.04 ❌ |
| M7 ação militar Irã (jun/2025)          | k = 2      |        57 | ❌           | ❌             | ❌                | XLE⊥ +0.57 ✅ · XLK⊥ +0.45 ❌ |
| M7 ação militar Irã (jun/2025)          | k = 3      |        56 | ❌           | ❌             | ✅                | XLE⊥ +1.19 ✅ · XLK⊥ -1.42 ✅ |
| M7 ação militar Irã (jun/2025)          | k = 5      |        54 | ❌           | ❌             | ❌                | XLE⊥ -0.82 ❌ · XLK⊥ +0.02 ❌ |
| M7 ação militar Irã (jun/2025)          | k = 10     |        49 | ❌           | ❌             | ❌                | XLE⊥ -1.58 ❌ · XLK⊥ -0.95 ✅ |
| M7 ação militar Irã (jun/2025)          | k = 20     |        39 | ❌           | ❌             | ✅                | XLE⊥ +2.01 ✅ · XLK⊥ -2.54 ✅ |
| M7 ataque ao Irã (fev/2026)             | k = 1      |        28 | ❌           | ❌             | ❌                | XLE⊥ -2.86 ❌ · XLK⊥ +1.16 ❌ |
| M7 ataque ao Irã (fev/2026)             | k = 2      |        27 | ❌           | ❌             | ❌                | XLE⊥ -1.39 ❌ · XLK⊥ +1.50 ❌ |
| M7 ataque ao Irã (fev/2026)             | k = 3      |        26 | ❌           | ❌             | ❌                | XLE⊥ -1.21 ❌ · XLK⊥ +0.83 ❌ |
| M7 ataque ao Irã (fev/2026)             | k = 5      |        24 | ❌           | ❌             | ❌                | XLE⊥ -2.11 ❌ · XLK⊥ +0.39 ❌ |
| M7 ataque ao Irã (fev/2026)             | k = 10     |        19 | ❌           | ❌             | ❌                | XLE⊥ -1.02 ❌ · XLK⊥ +0.29 ❌ |
| M7 ataque ao Irã (fev/2026)             | k = 20     |         9 | ❌           | ❌             | ❌                | XLE⊥ -1.23 ❌ · XLK⊥ +0.18 ❌ |
| M8 reconciliação fiscal                 | k = 1      |         2 | ❌           | ❌             | ❌                | XLF⊥ +3.43 ✅ · XLU⊥ +1.85 ❌ |
| M8 reconciliação fiscal                 | k = 2      |         1 | ❌           | ❌             | ❌                | μ ausente                     |
| M9 Câmara                               | k = 1      |       244 | ❌           | ❌             | ✅                | XLP⊥ +0.29 ✅ · XLK⊥ -1.08 ✅ |
| M9 Câmara                               | k = 2      |       243 | ✅           | ✅             | ✅                | XLP⊥ +0.26 ✅ · XLK⊥ -1.09 ✅ |
| M9 Câmara                               | k = 3      |       242 | ❌           | ❌             | ❌                | XLP⊥ -1.48 ❌ · XLK⊥ +0.21 ❌ |
| M9 Câmara                               | k = 5      |       238 | ❌           | ❌             | ❌                | XLP⊥ -1.68 ❌ · XLK⊥ -0.73 ✅ |
| M9 Câmara                               | k = 10     |       233 | ❌           | ✅             | ✅                | XLP⊥ +0.26 ✅ · XLK⊥ -1.51 ✅ |
| M9 Câmara                               | k = 20     |       219 | ❌           | ✅             | ✅                | XLP⊥ +2.23 ✅ · XLK⊥ -2.62 ✅ |

## Parte B — gatilho de SALTO, a célula que nunca existiu

A 3.2 morreu com livro direcional; a transversal foi medida só com o Δp acumulado. Este cruzamento é novo, e o argumento a priori a favor dele é que **o gap de abertura afeta menos um spread do que o índice inteiro** — o beta comum cancela nos dois lados.

| mercado                                 | corte |Δp|   |   n saltos | direcional   | setorial CRU   | setorial NEUTRO   | μ do neutro (bps/dia)         |
|:----------------------------------------|:-------------|-----------:|:-------------|:---------------|:------------------|:------------------------------|
| C1a M3 trajetória do Fed (nº de cortes) | q0.00        |        201 | ❌           | ❌             | ❌                | XLK⊥ -1.56 ❌ · XLF⊥ +1.55 ❌ |
| C1a M3 trajetória do Fed (nº de cortes) | q0.50        |        101 | ❌           | ❌             | ❌                | XLK⊥ -2.50 ❌ · XLF⊥ +1.62 ❌ |
| C1a M3 trajetória do Fed (nº de cortes) | q0.75        |         51 | ❌           | ❌             | ❌                | XLK⊥ -2.42 ❌ · XLF⊥ +1.60 ❌ |
| C1a M3 trajetória do Fed (nº de cortes) | q0.90        |         21 | ❌           | ❌             | ❌                | XLK⊥ -0.82 ❌ · XLF⊥ +0.66 ❌ |
| C1b reunião do FOMC (E_poly em bps)     | q0.00        |        307 | ❌           | ❌             | ❌                | XLK⊥ +1.25 ❌ · XLF⊥ -0.99 ❌ |
| C1b reunião do FOMC (E_poly em bps)     | q0.50        |        154 | ❌           | ❌             | ❌                | XLK⊥ +0.04 ❌ · XLF⊥ -0.59 ❌ |
| C1b reunião do FOMC (E_poly em bps)     | q0.75        |         77 | ❌           | ❌             | ❌                | XLK⊥ -0.21 ✅ · XLF⊥ -0.54 ❌ |
| C1b reunião do FOMC (E_poly em bps)     | q0.90        |         31 | ❌           | ❌             | ❌                | XLK⊥ +0.18 ❌ · XLF⊥ -0.65 ❌ |
| CPI mensal (E_poly)                     | q0.00        |        266 | ❌           | ❌             | ❌                | XLE⊥ +1.72 ✅ · XLK⊥ +2.05 ❌ |
| CPI mensal (E_poly)                     | q0.50        |        133 | ❌           | ❌             | ❌                | XLE⊥ +2.50 ✅ · XLK⊥ +3.77 ❌ |
| CPI mensal (E_poly)                     | q0.75        |         67 | ❌           | ❌             | ❌                | XLE⊥ +3.00 ✅ · XLK⊥ +1.22 ❌ |
| CPI mensal (E_poly)                     | q0.90        |         27 | ❌           | ✅             | ✅                | XLE⊥ +3.74 ✅ · XLK⊥ -0.18 ✅ |
| M4 recessão EUA 2025                    | q0.00        |        193 | ❌           | ❌             | ❌                | XLP⊥ -0.02 ❌ · XLK⊥ -1.48 ✅ |
| M4 recessão EUA 2025                    | q0.50        |        107 | ❌           | ❌             | ✅                | XLP⊥ +2.10 ✅ · XLK⊥ -2.89 ✅ |
| M4 recessão EUA 2025                    | q0.75        |         52 | ❌           | ❌             | ✅                | XLP⊥ +0.88 ✅ · XLK⊥ -1.67 ✅ |
| M4 recessão EUA 2025                    | q0.90        |         20 | ❌           | ❌             | ❌                | XLP⊥ -0.04 ❌ · XLK⊥ -0.66 ✅ |
| M5 Trump 2024                           | q0.00        |        136 | ❌           | ✅             | ✅                | XLF⊥ +2.11 ✅ · XLP⊥ -0.14 ✅ |
| M5 Trump 2024                           | q0.50        |         94 | ❌           | ✅             | ✅                | XLF⊥ +1.71 ✅ · XLP⊥ -0.35 ✅ |
| M5 Trump 2024                           | q0.75        |         41 | ✅           | ✅             | ✅                | XLF⊥ +0.81 ✅ · XLP⊥ -2.18 ✅ |
| M5 Trump 2024                           | q0.90        |         19 | ✅           | ✅             | ✅                | XLF⊥ +0.39 ✅ · XLP⊥ -1.10 ✅ |
| M6 tarifas China                        | q0.00        |          8 | ❌           | ❌             | ❌                | XLP⊥ -0.26 ❌ · XLK⊥ +0.38 ❌ |
| M6 tarifas China                        | q0.50        |          4 | ❌           | ❌             | ❌                | XLP⊥ -1.12 ❌ · XLK⊥ +2.03 ❌ |
| M7 ação militar Irã (jun/2025)          | q0.00        |         50 | ❌           | ❌             | ❌                | XLE⊥ +1.83 ✅ · XLK⊥ +0.04 ❌ |
| M7 ação militar Irã (jun/2025)          | q0.50        |         26 | ✅           | ✅             | ✅                | XLE⊥ +1.75 ✅ · XLK⊥ -1.38 ✅ |
| M7 ação militar Irã (jun/2025)          | q0.75        |         13 | ❌           | ❌             | ❌                | XLE⊥ +0.58 ✅ · XLK⊥ +0.78 ❌ |
| M7 ação militar Irã (jun/2025)          | q0.90        |          5 | ✅           | ✅             | ❌                | XLE⊥ +0.57 ✅ · XLK⊥ +0.26 ❌ |
| M7 ataque ao Irã (fev/2026)             | q0.00        |         28 | ❌           | ❌             | ❌                | XLE⊥ -2.86 ❌ · XLK⊥ +1.16 ❌ |
| M7 ataque ao Irã (fev/2026)             | q0.50        |         14 | ❌           | ❌             | ❌                | XLE⊥ -1.29 ❌ · XLK⊥ +0.93 ❌ |
| M7 ataque ao Irã (fev/2026)             | q0.75        |          8 | ❌           | ❌             | ❌                | XLE⊥ -0.65 ❌ · XLK⊥ +0.35 ❌ |
| M7 ataque ao Irã (fev/2026)             | q0.90        |          3 | ❌           | ❌             | ❌                | XLE⊥ -0.40 ❌ · XLK⊥ +0.22 ❌ |
| M9 Câmara                               | q0.00        |         98 | ❌           | ❌             | ✅                | XLP⊥ +0.29 ✅ · XLK⊥ -1.08 ✅ |
| M9 Câmara                               | q0.50        |         76 | ❌           | ❌             | ❌                | XLP⊥ -0.60 ❌ · XLK⊥ -0.47 ✅ |
| M9 Câmara                               | q0.75        |         27 | ❌           | ❌             | ❌                | XLP⊥ -1.27 ❌ · XLK⊥ +1.03 ❌ |
| M9 Câmara                               | q0.90        |         22 | ❌           | ❌             | ❌                | XLP⊥ -1.01 ❌ · XLK⊥ +1.22 ❌ |

## Leitura

**O hedge funcionou:** a maior |correlação| com o SPY cai de **0.59** (cru) para **0.17** (neutro). Os livros neutros são spreads de verdade — o que a coluna NEUTRO mede não tem índice dentro.

**O 8 × 0 do `Gate_transversal.md` sobrevive à neutralização?** Com o livro CRU, **8** pares passam onde o direcional falha. Com o livro NEUTRO, **14**. E **0** passam só no direcional.

**A vantagem do livro setorial NÃO era beta disfarçado.** Ela sobrevive quando o índice é removido das duas pernas — o que estava sendo medido é spread, não alavancagem direcional. Esta é a versão forte do achado do artefato anterior.

**O cruzamento salto × setorial, que nunca tinha sido medido:** **6** pares (mercado, corte) passam no G2 com livro neutro e falham no direcional · **3** com livro cru · **1** só no direcional.

Onde o livro salva o gatilho do salto: **CPI mensal (E_poly)** 0.90 · **M4 recessão EUA 2025** 0.50 · **M4 recessão EUA 2025** 0.75 · **M5 Trump 2024** 0.00 · **M5 Trump 2024** 0.50 · **M9 Câmara** 0.00.

### Sobrevivem às duas metades da amostra?

- **[A] C1a M3 trajetória do Fed (nº de cortes)**, k = 20 — 1ª metade: `XLK⊥ +0.06 ✅ · XLF⊥ +0.35 ❌` (❌, n = 92) · 2ª metade: `XLK⊥ +3.69 ✅ · XLF⊥ -0.80 ✅` (✅, n = 92). 🛑 **NÃO sobrevive.**
- **[A] C1b reunião do FOMC (E_poly em bps)**, k = 5 — 1ª metade: `XLK⊥ +0.41 ❌ · XLF⊥ +0.14 ✅` (❌, n = 156) · 2ª metade: `XLK⊥ -2.30 ✅ · XLF⊥ +1.81 ✅` (✅, n = 157). 🛑 **NÃO sobrevive.**
- **[A] C1b reunião do FOMC (E_poly em bps)**, k = 10 — 1ª metade: `XLK⊥ +2.01 ❌ · XLF⊥ +0.22 ✅` (❌, n = 154) · 2ª metade: `XLK⊥ -1.51 ✅ · XLF⊥ +1.23 ✅` (✅, n = 154). 🛑 **NÃO sobrevive.**
- **[A] C1b reunião do FOMC (E_poly em bps)**, k = 20 — 1ª metade: `XLK⊥ +2.21 ❌ · XLF⊥ -1.60 ❌` (❌, n = 151) · 2ª metade: `XLK⊥ -3.13 ✅ · XLF⊥ +2.66 ✅` (✅, n = 151). 🛑 **NÃO sobrevive.**
- **[A] M4 recessão EUA 2025**, k = 2 — 1ª metade: `XLP⊥ +0.45 ✅ · XLK⊥ -1.50 ✅` (✅, n = 106) · 2ª metade: `XLP⊥ -0.00 ❌ · XLK⊥ +1.27 ❌` (❌, n = 105). 🛑 **NÃO sobrevive.**
- **[A] M4 recessão EUA 2025**, k = 3 — 1ª metade: `XLP⊥ +2.03 ✅ · XLK⊥ -2.75 ✅` (✅, n = 112) · 2ª metade: `XLP⊥ +4.34 ✅ · XLK⊥ -1.01 ✅` (✅, n = 108). **Sobrevive.**
- **[A] M4 recessão EUA 2025**, k = 5 — 1ª metade: `XLP⊥ +1.77 ✅ · XLK⊥ -2.07 ✅` (✅, n = 116) · 2ª metade: `XLP⊥ +2.78 ✅ · XLK⊥ -2.30 ✅` (✅, n = 111). **Sobrevive.**
- **[A] M4 recessão EUA 2025**, k = 10 — 1ª metade: `XLP⊥ +0.86 ✅ · XLK⊥ -2.11 ✅` (✅, n = 116) · 2ª metade: `XLP⊥ +2.29 ✅ · XLK⊥ -0.88 ✅` (✅, n = 113). **Sobrevive.**
- **[A] M4 recessão EUA 2025**, k = 20 — 1ª metade: `XLP⊥ +0.09 ✅ · XLK⊥ -0.06 ✅` (✅, n = 117) · 2ª metade: `XLP⊥ +2.02 ✅ · XLK⊥ +0.03 ❌` (❌, n = 115). 🛑 **NÃO sobrevive.**
- **[A] M5 Trump 2024**, k = 1 — 1ª metade: `XLF⊥ +0.31 ✅ · XLP⊥ -0.37 ✅` (✅, n = 41) · 2ª metade: `XLF⊥ +1.88 ✅ · XLP⊥ +0.10 ❌` (❌, n = 95). 🛑 **NÃO sobrevive.**
- **[A] M6 tarifas China**, k = 5 — 1ª metade: `XLP⊥ +0.60 ✅ · XLK⊥ -0.13 ✅` (✅, n = 2) · 2ª metade: `XLP⊥ -0.25 ❌ · XLK⊥ -0.04 ✅` (❌, n = 2). 🛑 **NÃO sobrevive.**
- **[A] M7 ação militar Irã (jun/2025)**, k = 3 — 1ª metade: `XLE⊥ -1.41 ❌ · XLK⊥ -0.97 ✅` (❌, n = 26) · 2ª metade: `XLE⊥ +3.28 ✅ · XLK⊥ +0.15 ❌` (❌, n = 27). 🛑 **NÃO sobrevive.**
- **[A] M7 ação militar Irã (jun/2025)**, k = 20 — 1ª metade: `XLE⊥ +3.07 ✅ · XLK⊥ -1.74 ✅` (✅, n = 19) · 2ª metade: `XLE⊥ +0.16 ✅ · XLK⊥ -0.81 ✅` (✅, n = 20). **Sobrevive.**
- **[A] M9 Câmara**, k = 1 — 1ª metade: `XLP⊥ -0.25 ❌ · XLK⊥ -0.70 ✅` (❌, n = 59) · 2ª metade: `XLP⊥ +0.47 ✅ · XLK⊥ -0.47 ✅` (✅, n = 39). 🛑 **NÃO sobrevive.**
- **[A] M9 Câmara**, k = 2 — 1ª metade: `XLP⊥ +0.97 ✅ · XLK⊥ -0.55 ✅` (✅, n = 66) · 2ª metade: `XLP⊥ -0.49 ❌ · XLK⊥ -0.61 ✅` (❌, n = 60). 🛑 **NÃO sobrevive.**
- **[A] M9 Câmara**, k = 10 — 1ª metade: `XLP⊥ +1.04 ✅ · XLK⊥ -1.12 ✅` (✅, n = 96) · 2ª metade: `XLP⊥ -0.29 ❌ · XLK⊥ -0.78 ✅` (❌, n = 98). 🛑 **NÃO sobrevive.**
- **[A] M9 Câmara**, k = 20 — 1ª metade: `XLP⊥ +2.83 ✅ · XLK⊥ -2.85 ✅` (✅, n = 108) · 2ª metade: `XLP⊥ +0.38 ✅ · XLK⊥ -0.98 ✅` (✅, n = 96). **Sobrevive.**
- **[B] CPI mensal (E_poly)**, q0.90 — 1ª metade: `XLE⊥ +2.17 ✅ · XLK⊥ -1.21 ✅` (✅, n = 13) · 2ª metade: `XLE⊥ +1.81 ✅ · XLK⊥ +0.01 ❌` (❌, n = 14). 🛑 **NÃO sobrevive.**
- **[B] M4 recessão EUA 2025**, q0.50 — 1ª metade: `XLP⊥ +1.45 ✅ · XLK⊥ -2.69 ✅` (✅, n = 53) · 2ª metade: `XLP⊥ +0.33 ✅ · XLK⊥ +0.42 ❌` (❌, n = 54). 🛑 **NÃO sobrevive.**
- **[B] M4 recessão EUA 2025**, q0.75 — 1ª metade: `XLP⊥ +0.63 ✅ · XLK⊥ -1.16 ✅` (✅, n = 26) · 2ª metade: `XLP⊥ +0.05 ✅ · XLK⊥ -0.42 ✅` (✅, n = 26). **Sobrevive.**
- **[B] M5 Trump 2024**, q0.00 — 1ª metade: `XLF⊥ +0.39 ✅ · XLP⊥ -0.09 ✅` (✅, n = 68) · 2ª metade: `XLF⊥ +1.86 ✅ · XLP⊥ -0.07 ✅` (✅, n = 68). **Sobrevive.**
- **[B] M5 Trump 2024**, q0.50 — 1ª metade: `XLF⊥ -0.49 ❌ · XLP⊥ -1.74 ✅` (❌, n = 47) · 2ª metade: `XLF⊥ +1.77 ✅ · XLP⊥ +0.73 ❌` (❌, n = 47). 🛑 **NÃO sobrevive.**
- **[B] M5 Trump 2024**, q0.75 — 1ª metade: `XLF⊥ -1.55 ❌ · XLP⊥ -1.53 ✅` (❌, n = 20) · 2ª metade: `XLF⊥ +1.24 ✅ · XLP⊥ -0.96 ✅` (✅, n = 21). 🛑 **NÃO sobrevive.**
- **[B] M5 Trump 2024**, q0.90 — 1ª metade: `XLF⊥ -0.09 ❌ · XLP⊥ -0.59 ✅` (❌, n = 9) · 2ª metade: `XLF⊥ +0.23 ✅ · XLP⊥ -0.53 ✅` (✅, n = 10). 🛑 **NÃO sobrevive.**
- **[B] M7 ação militar Irã (jun/2025)**, q0.50 — 1ª metade: `XLE⊥ -0.22 ❌ · XLK⊥ -1.24 ✅` (❌, n = 13) · 2ª metade: `XLE⊥ +2.45 ✅ · XLK⊥ +1.12 ❌` (❌, n = 13). 🛑 **NÃO sobrevive.**
- **[B] M9 Câmara**, q0.00 — 1ª metade: `XLP⊥ -0.54 ❌ · XLK⊥ +0.13 ❌` (❌, n = 49) · 2ª metade: `XLP⊥ +0.70 ✅ · XLK⊥ -0.97 ✅` (✅, n = 49). 🛑 **NÃO sobrevive.**

**7 de 26** aprovações com livro neutro sobrevivem ao corte: **M4 recessão EUA 2025** k = 3 · **M4 recessão EUA 2025** k = 5 · **M4 recessão EUA 2025** k = 10 · **M7 ação militar Irã (jun/2025)** k = 20 · **M9 Câmara** k = 20 · **M4 recessão EUA 2025** q0.75 · **M5 Trump 2024** q0.00.

**E o que sobrevive não é célula isolada — é BLOCO de horizontes vizinhos:** **M4 recessão EUA 2025** em k = 3, 5, 10 (3 das 6 colunas da grade, contíguas). Uma célula isolada numa grade é o padrão de quem garimpou o horizonte que funcionou; horizontes vizinhos todos passando **e** todos sobrevivendo ao corte é bem mais difícil de conseguir por sorte. É a diferença entre um resultado e um artefato de busca.

⚠️ **Cuidado com as linhas `q0.00` da parte B:** **M5 Trump 2024** sobrevive no corte `q0.00`, que é **todo dia com Δp ≠ 0** — a linha de base, não um salto. Sobreviver ali não credita o gatilho de salto; credita o Δp diário, que é outra coisa. O único sobrevivente que é salto de verdade é **M4 recessão EUA 2025** q0.75.

⚠️ **O que o projeto já mediu sobre esses mercados, em outra camada:**

- **M4 recessão EUA 2025** — a **view 3.1** leu este mercado, e a D19c mediu que o coeficiente **troca de sinal dentro da própria amostra** (SPY em h = 10: +0,97% t +6,52 na 1ª metade, **−0,35% t −2,27** na 2ª). Não há segundo mercado de recessão, então não existe teste fora da amostra — e agora se sabe que não existe nem dentro dela.
- **M5 Trump 2024** — a **view 2.4** leu este mercado e foi cortada: o efeito aterrissa no gap (23% sobra na janela negociável) e o mecanismo partidário **reprovou fora da amostra** — o TLT cai nos dois mercados, quando deveria inverter.
- **M7 ação militar Irã (jun/2025)** — a **view C** leu este mercado e não entrou (D23f): o critério pré-registrado para fixar o `k` **não identifica k** (corr +0,08 entre os dois episódios) e o único lag em que eles concordam é o **lag 0** — o gap de abertura.
- **M9 Câmara** — mesmo mecanismo partidário da 2.4, e é o segundo mercado do teste fora da amostra que a reprovou.

**O que isto NÃO diz:** nada sobre P&L, e nada sobre pares setoriais não declarados. Continua **um par por mercado, escolhido pelo mecanismo** — varrer os 15 pares possíveis atrás do que funciona é pescaria, e é o vício que a D2b existe para barrar.

