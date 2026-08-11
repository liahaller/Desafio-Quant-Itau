# Transversal — o livro estava errado, ou o gatilho?

> Gerado por `scripts/gate_transversal.py`. **Mede; não decide.** Nenhum corte cravado, mesma regra do `Gate_sleeves.md`.

- janela do backtest: **2025-02-10 a 2026-08-06** (374 pregões), δ e Σ os mesmos do v1 (D7/D8)
- **mesmo sinal, mesma grade, mesma janela de event-study** nas duas colunas de livro. A ÚNICA coisa que muda é em que ativos a premissa se expressa — é o que separa "o livro estava errado" de "o gatilho estava errado"
- **G3** é idêntico nos dois livros **por construção**: o sinal-fonte é o mesmo, e correlação de sinal não sabe em que ativo a sleeve opera. O ganho de ortogonalidade de um livro transversal está no P, e está medido na tabela de neutralidade abaixo

| mercado                                 | lookback   |   G0 dias | G1 razão / tick   | livro DIRECIONAL            | bate?   | livro SETORIAL              | bate?    | G3 maior \|corr\|   |
|:----------------------------------------|:-----------|----------:|:------------------|:----------------------------|:--------|:----------------------------|:---------|:--------------------|
| C1a M3 trajetória do Fed (nº de cortes) | k = 1      |       201 | 0.5×              | SPY -3.87 ❌ · TLT +0.03 ✅ | ❌      | XLK -6.27 ❌ · XLF -4.51 ✅ | ❌       | -0.19               |
| C1a M3 trajetória do Fed (nº de cortes) | k = 2      |       200 | 0.9×              | SPY -0.60 ❌ · TLT -1.43 ❌ | ❌      | XLK -0.99 ❌ · XLF -1.51 ✅ | ❌       | -0.31               |
| C1a M3 trajetória do Fed (nº de cortes) | k = 3      |       199 | 1.2×              | SPY -0.95 ❌ · TLT -0.78 ❌ | ❌      | XLK -1.55 ❌ · XLF -1.13 ✅ | ❌       | -0.32               |
| C1a M3 trajetória do Fed (nº de cortes) | k = 5      |       197 | 1.7×              | SPY -2.16 ❌ · TLT -1.45 ❌ | ❌      | XLK -2.83 ❌ · XLF -2.01 ✅ | ❌       | -0.34               |
| C1a M3 trajetória do Fed (nº de cortes) | k = 10     |       194 | 2.9×              | SPY -0.92 ❌ · TLT -1.43 ❌ | ❌      | XLK -0.45 ❌ · XLF -0.84 ✅ | ❌       | -0.36               |
| C1a M3 trajetória do Fed (nº de cortes) | k = 20     |       184 | 3.7×              | SPY +1.38 ✅ · TLT -1.01 ❌ | ❌      | XLK +3.76 ✅ · XLF +1.87 ❌ | ❌       | -0.42               |
| C1b reunião do FOMC (E_poly em bps)     | k = 1      |       317 | 0.2×              | SPY +2.65 ❌ · TLT +3.36 ❌ | ❌      | XLK +4.18 ❌ · XLF +2.71 ✅ | ❌       | +0.27               |
| C1b reunião do FOMC (E_poly em bps)     | k = 2      |       316 | 0.4×              | SPY +0.45 ❌ · TLT -0.71 ✅ | ❌      | XLK +0.56 ❌ · XLF +0.95 ✅ | ❌       | +0.23               |
| C1b reunião do FOMC (E_poly em bps)     | k = 3      |       314 | 0.5×              | SPY +1.31 ❌ · TLT +0.67 ❌ | ❌      | XLK +2.71 ❌ · XLF +0.89 ✅ | ❌       | +0.22               |
| C1b reunião do FOMC (E_poly em bps)     | k = 5      |       313 | 0.9×              | SPY -0.13 ✅ · TLT +1.06 ❌ | ❌      | XLK -1.96 ✅ · XLF +1.37 ✅ | ✅       | +0.21               |
| C1b reunião do FOMC (E_poly em bps)     | k = 10     |       308 | 1.6×              | SPY +0.17 ❌ · TLT +1.35 ❌ | ❌      | XLK -0.12 ✅ · XLF +1.38 ✅ | ✅       | +0.11               |
| C1b reunião do FOMC (E_poly em bps)     | k = 20     |       302 | 2.4×              | SPY +0.28 ❌ · TLT +0.84 ❌ | ❌      | XLK -1.52 ✅ · XLF +1.50 ✅ | ✅       | -0.26               |
| CPI mensal (E_poly)                     | k = 1      |       269 | 1.1×              | TIP -0.82 ❌ · TLT -0.27 ✅ | ❌      | XLE +3.96 ✅ · XLK +4.15 ❌ | ❌       | +0.16               |
| CPI mensal (E_poly)                     | k = 2      |       264 | 1.8×              | TIP -0.05 ❌ · TLT +0.55 ❌ | ❌      | XLE +3.46 ✅ · XLK +1.24 ❌ | ❌       | +0.22               |
| CPI mensal (E_poly)                     | k = 3      |       259 | 2.3×              | TIP +0.18 ✅ · TLT +1.29 ❌ | ❌      | XLE +3.77 ✅ · XLK +3.01 ❌ | ❌       | +0.26               |
| CPI mensal (E_poly)                     | k = 5      |       250 | 3.1×              | TIP -0.18 ❌ · TLT +0.27 ❌ | ❌      | XLE +2.08 ✅ · XLK +1.47 ❌ | ❌       | +0.29               |
| CPI mensal (E_poly)                     | k = 10     |       235 | 6.2×              | TIP +0.63 ✅ · TLT +2.27 ❌ | ❌      | XLE +2.03 ✅ · XLK +3.18 ❌ | ❌       | +0.30               |
| CPI mensal (E_poly)                     | k = 20     |       203 | 12.1×             | TIP +0.42 ✅ · TLT +0.77 ❌ | ❌      | XLE +0.12 ✅ · XLK +0.24 ❌ | ❌       | +0.45               |
| M4 recessão EUA 2025                    | k = 1      |       253 | 0.7×              | SPY -4.44 ✅ · TLT -1.87 ❌ | ❌      | XLP -3.38 ❌ · XLK -7.05 ✅ | ❌       | +0.09               |
| M4 recessão EUA 2025                    | k = 2      |       252 | 1.0×              | SPY -3.84 ✅ · TLT -2.03 ❌ | ❌      | XLP -2.46 ❌ · XLK -5.40 ✅ | ❌       | -0.14               |
| M4 recessão EUA 2025                    | k = 3      |       251 | 1.0×              | SPY -2.84 ✅ · TLT +0.12 ✅ | ✅      | XLP +2.29 ✅ · XLK -5.91 ✅ | ✅       | -0.17               |
| M4 recessão EUA 2025                    | k = 5      |       249 | 2.0×              | SPY -1.11 ✅ · TLT +2.70 ✅ | ✅      | XLP +2.58 ✅ · XLK -3.83 ✅ | ✅       | -0.20               |
| M4 recessão EUA 2025                    | k = 10     |       244 | 2.5×              | SPY -3.63 ✅ · TLT -1.53 ❌ | ❌      | XLP -0.28 ❌ · XLK -6.61 ✅ | ❌       | -0.24               |
| M4 recessão EUA 2025                    | k = 20     |       234 | 5.5×              | SPY -2.09 ✅ · TLT -2.13 ❌ | ❌      | XLP -0.09 ❌ · XLK -2.91 ✅ | ❌       | -0.33               |
| M5 Trump 2024                           | k = 1      |       218 | 0.5×              | SPY -2.13 ❌ · TLT +0.12 ❌ | ❌      | XLF +0.03 ✅ · XLP -1.55 ✅ | ✅       | —                   |
| M5 Trump 2024                           | k = 2      |       217 | 1.0×              | SPY -2.95 ❌ · TLT -0.34 ✅ | ❌      | XLF -2.74 ❌ · XLP -1.66 ✅ | ❌       | —                   |
| M5 Trump 2024                           | k = 3      |       216 | 1.2×              | SPY -2.19 ❌ · TLT -0.20 ✅ | ❌      | XLF -1.05 ❌ · XLP +0.08 ❌ | ❌       | —                   |
| M5 Trump 2024                           | k = 5      |       214 | 2.0×              | SPY -0.42 ❌ · TLT +0.82 ❌ | ❌      | XLF -0.88 ❌ · XLP +0.35 ❌ | ❌       | —                   |
| M5 Trump 2024                           | k = 10     |       209 | 3.0×              | SPY -0.60 ❌ · TLT +0.94 ❌ | ❌      | XLF -0.60 ❌ · XLP +1.71 ❌ | ❌       | —                   |
| M5 Trump 2024                           | k = 20     |       199 | 5.0×              | SPY +1.54 ✅ · TLT +0.09 ❌ | ❌      | XLF +1.34 ✅ · XLP -0.46 ✅ | ✅       | —                   |
| M6 tarifas China                        | k = 1      |         8 | 3.5×              | SPY +0.03 ❌ · TLT -0.29 ❌ | ❌      | XLP -0.06 ❌ · XLK +0.09 ❌ | ❌       | +0.70               |
| M6 tarifas China                        | k = 2      |         7 | 5.0×              | SPY +0.04 ❌ · TLT -0.11 ❌ | ❌      | XLP +0.13 ✅ · XLK +0.10 ❌ | ❌       | -0.73               |
| M6 tarifas China                        | k = 3      |         6 | 12.8×             | SPY +0.05 ❌ · TLT -0.01 ❌ | ❌      | XLP +0.20 ✅ · XLK +0.12 ❌ | ❌       | +0.83               |
| M6 tarifas China                        | k = 5      |         4 | 44.0×             | SPY +0.00 ❌ · TLT +8.92 ✅ | ❌      | XLP +0.07 ✅ · XLK -0.04 ✅ | ✅       | +0.82               |
| M7 ação militar Irã (jun/2025)          | k = 1      |        58 | 1.2×              | XLE +0.88 ✅ · SPY +0.14 ❌ | ❌      | XLE +0.88 ✅ · XLK +0.24 ❌ | ❌       | -0.28               |
| M7 ação militar Irã (jun/2025)          | k = 2      |        57 | 2.5×              | XLE +0.74 ✅ · SPY +0.29 ❌ | ❌      | XLE +0.74 ✅ · XLK +0.61 ❌ | ❌       | +0.42               |
| M7 ação militar Irã (jun/2025)          | k = 3      |        56 | 3.3×              | XLE -1.71 ❌ · SPY -1.17 ✅ | ❌      | XLE -1.71 ❌ · XLK -2.39 ✅ | ❌       | +0.67               |
| M7 ação militar Irã (jun/2025)          | k = 5      |        54 | 4.8×              | XLE -0.75 ❌ · SPY -0.15 ✅ | ❌      | XLE -0.75 ❌ · XLK -0.24 ✅ | ❌       | +0.73               |
| M7 ação militar Irã (jun/2025)          | k = 10     |        49 | 5.5×              | XLE -1.09 ❌ · SPY +0.22 ❌ | ❌      | XLE -1.09 ❌ · XLK -0.16 ✅ | ❌       | +0.82               |
| M7 ação militar Irã (jun/2025)          | k = 20     |        39 | 9.0×              | XLE -0.58 ❌ · SPY -2.25 ✅ | ❌      | XLE -0.58 ❌ · XLK -4.91 ✅ | ❌       | +0.79               |
| M7 ataque ao Irã (fev/2026)             | k = 1      |        28 | 4.0×              | XLE -1.41 ❌ · SPY +3.09 ❌ | ❌      | XLE -1.41 ❌ · XLK +3.51 ❌ | ❌       | -0.12               |
| M7 ataque ao Irã (fev/2026)             | k = 2      |        27 | 6.0×              | XLE +0.11 ✅ · SPY +3.33 ❌ | ❌      | XLE +0.11 ✅ · XLK +4.19 ❌ | ❌       | -0.12               |
| M7 ataque ao Irã (fev/2026)             | k = 3      |        26 | 7.7×              | XLE -0.69 ❌ · SPY +1.17 ❌ | ❌      | XLE -0.69 ❌ · XLK +1.87 ❌ | ❌       | -0.16               |
| M7 ataque ao Irã (fev/2026)             | k = 5      |        24 | 10.5×             | XLE -1.96 ❌ · SPY +0.78 ❌ | ❌      | XLE -1.96 ❌ · XLK +1.00 ❌ | ❌       | -0.27               |
| M7 ataque ao Irã (fev/2026)             | k = 10     |        19 | 11.0×             | XLE -0.68 ❌ · SPY +0.39 ❌ | ❌      | XLE -0.68 ❌ · XLK +0.59 ❌ | ❌       | -0.52               |
| M7 ataque ao Irã (fev/2026)             | k = 20     |         9 | 26.0×             | XLE -2.41 ❌ · SPY -0.04 ✅ | ❌      | XLE -2.41 ❌ · XLK +0.15 ❌ | ❌       | +0.87               |
| M8 reconciliação fiscal                 | k = 1      |         2 | 33.0×             | TLT -5.25 ✅ · SPY -0.01 ❌ | ❌      | XLF +0.01 ✅ · XLU +1.16 ❌ | ❌       | —                   |
| M8 reconciliação fiscal                 | k = 2      |         1 | 66.0×             | μ ausente                   | ❌      | μ ausente                   | ❌       | —                   |
| M9 Câmara                               | k = 1      |       244 | 0.0×              | SPY +2.82 ❌ · TLT +2.95 ✅ | ❌      | XLP +1.18 ✅ · XLK +0.71 ❌ | ❌       | -0.13               |
| M9 Câmara                               | k = 2      |       243 | 0.5×              | SPY -0.03 ✅ · TLT +1.47 ✅ | ✅      | XLP +0.26 ✅ · XLK -1.45 ✅ | ✅       | -0.21               |
| M9 Câmara                               | k = 3      |       242 | 1.0×              | SPY +2.66 ❌ · TLT +0.70 ✅ | ❌      | XLP -0.65 ❌ · XLK +2.52 ❌ | ❌       | -0.20               |
| M9 Câmara                               | k = 5      |       238 | 1.0×              | SPY +3.58 ❌ · TLT +1.52 ✅ | ❌      | XLP -0.62 ❌ · XLK +1.81 ❌ | ❌       | -0.27               |
| M9 Câmara                               | k = 10     |       233 | 1.0×              | SPY +1.43 ❌ · TLT +0.11 ✅ | ❌      | XLP +0.80 ✅ · XLK -0.93 ✅ | ✅       | -0.36               |
| M9 Câmara                               | k = 20     |       219 | 3.0×              | SPY -0.41 ✅ · TLT -1.12 ❌ | ❌      | XLP +2.30 ✅ · XLK -3.79 ✅ | ✅       | -0.33               |

## Livro setorial declarado ANTES de medir

Uma perna de cada lado, mapeamento de manual, par escolhido pelo mecanismo. Nenhum otimizado, nenhum saído de varredura.

- **C1a M3 trajetória do Fed (nº de cortes)** — mais afrouxamento → equity de duração longa (XLK) bate banco (XLF), cuja margem de juros comprime
- **C1b reunião do FOMC (E_poly em bps)** — idem, invertido: E_poly é Δtaxa, então subir é apertar
- **CPI mensal (E_poly)** — surpresa inflacionária → energia (XLE) bate duração longa (XLK)
- **M4 recessão EUA 2025** — p(recessão) sobe → defensivo (XLP) bate cíclico (XLK)
- **M5 Trump 2024** — "Trump trade": desregulação financeira (XLF) bate defensivo (XLP)
- **M6 tarifas China** — p(tarifa) sobe → risco-off: defensivo bate cíclico
- **M7 ação militar Irã (jun/2025)** — p(ação militar) sobe → petróleo (XLE) bate cíclico (XLK)
- **M7 ataque ao Irã (fev/2026)** — idem, segundo episódio
- **M8 reconciliação fiscal** — p(aprovação) sobe → mais emissão: o proxy de bond (XLU) sofre e o financeiro (XLF) ganha
- **M9 Câmara** — mecanismo partidário, espelho do M5. ⚠️ é o mecanismo que a 2.4 mediu como NÃO reproduzindo fora da amostra

## Neutralidade — o spread é o índice disfarçado?

A alegação de que um livro long/short é "ortogonal por construção" a quem tilta o índice só vale se o spread não carregar o índice dentro. Medido, não afirmado — e é o ρ que o precedente **D22e** manda usar quando o ângulo é tautológico.

| mercado                                 | livro     |   corr(spread, SPY) |
|:----------------------------------------|:----------|--------------------:|
| C1a M3 trajetória do Fed (nº de cortes) | +XLK −XLF |               -0.16 |
| C1b reunião do FOMC (E_poly em bps)     | −XLK +XLF |                0.16 |
| CPI mensal (E_poly)                     | +XLE −XLK |                0.01 |
| M4 recessão EUA 2025                    | +XLP −XLK |               -0.56 |
| M5 Trump 2024                           | +XLF −XLP |                0.59 |
| M6 tarifas China                        | +XLP −XLK |               -0.56 |
| M7 ação militar Irã (jun/2025)          | +XLE −XLK |                0.01 |
| M7 ataque ao Irã (fev/2026)             | +XLE −XLK |                0.01 |
| M8 reconciliação fiscal                 | +XLF −XLU |                0.48 |
| M9 Câmara                               | +XLP −XLK |               -0.56 |

## Leitura

**A pergunta era "o livro estava errado?". A resposta é a contagem de células que mudam de veredito ao trocar SÓ o livro:** **8** pares (mercado, k) passam no G2 **só** com o livro setorial · **0** passam só com o direcional · **3** passam nos dois · **43** não passam em nenhum.

**Onde o livro era o problema** (o gatilho serve, o SPY/TLT é que não expressava): **C1b reunião do FOMC (E_poly em bps)** k = 5 (G1 0.9×, 313 dias) · **C1b reunião do FOMC (E_poly em bps)** k = 10 (G1 1.6×, 308 dias) · **C1b reunião do FOMC (E_poly em bps)** k = 20 (G1 2.4×, 302 dias) · **M5 Trump 2024** k = 1 (G1 0.5×, 218 dias) · **M5 Trump 2024** k = 20 (G1 5.0×, 199 dias) · **M6 tarifas China** k = 5 (G1 44.0×, 4 dias) · **M9 Câmara** k = 10 (G1 1.0×, 233 dias) · **M9 Câmara** k = 20 (G1 3.0×, 219 dias).

**A alegação de "ortogonal por construção" não vale para todo spread — vale para alguns, e a diferença é medida.** Dos **6** livros distintos declarados, **3** ficam abaixo de |0,20| contra o SPY (`+XLK −XLF` -0.16 · `−XLK +XLF` +0.16 · `+XLE −XLK` +0.01) e **3** não (`+XLP −XLK` -0.56 · `+XLF −XLP` +0.59 · `+XLF −XLU` +0.48). O pior é `+XLF −XLP` com **+0.59** — isso é beta disfarçado, não spread neutro. **Para esses livros a tese de ortogonalidade não se sustenta**, e ela era metade da razão de ser da transversal: não competir com as views vivas pelo mesmo risco.

### As aprovações setoriais sobrevivem às duas metades?

Mesmo teste da D19c aplicado no `gate_noticia.py`: um G2 que passa na amostra inteira e troca de sinal no meio é a média de dois regimes.

- **C1b reunião do FOMC (E_poly em bps)**, k = 10 — 1ª metade: `XLK +2.54 ❌ · XLF +1.77 ✅` (❌, n = 154) · 2ª metade: `XLK -3.62 ✅ · XLF -0.62 ❌` (❌, n = 154). 🛑 **NÃO sobrevive.**
- **C1b reunião do FOMC (E_poly em bps)**, k = 20 — 1ª metade: `XLK +3.30 ❌ · XLF +1.13 ✅` (❌, n = 151) · 2ª metade: `XLK -5.92 ✅ · XLF +0.54 ✅` (✅, n = 151). 🛑 **NÃO sobrevive.**
- **M4 recessão EUA 2025**, k = 3 — 1ª metade: `XLP -0.10 ❌ · XLK -3.97 ✅` (❌, n = 112) · 2ª metade: `XLP +4.30 ✅ · XLK -2.18 ✅` (✅, n = 108). 🛑 **NÃO sobrevive.**
- **M4 recessão EUA 2025**, k = 5 — 1ª metade: `XLP +0.88 ✅ · XLK -2.00 ✅` (✅, n = 116) · 2ª metade: `XLP +2.86 ✅ · XLK -3.02 ✅` (✅, n = 111). **Sobrevive.**
- **M5 Trump 2024**, k = 20 — 1ª metade: `XLF +0.25 ✅ · XLP +0.66 ❌` (❌, n = 92) · 2ª metade: `XLF +1.12 ✅ · XLP -1.16 ✅` (✅, n = 100). 🛑 **NÃO sobrevive.**
- **M6 tarifas China**, k = 5 — 1ª metade: `XLP +4.23 ✅ · XLK +2.55 ❌` (❌, n = 2) · 2ª metade: `XLP -10.17 ❌ · XLK -0.26 ✅` (❌, n = 2). 🛑 **NÃO sobrevive.**
- **M9 Câmara**, k = 10 — 1ª metade: `XLP +1.66 ✅ · XLK -0.02 ✅` (✅, n = 96) · 2ª metade: `XLP -0.15 ❌ · XLK -0.78 ✅` (❌, n = 98). 🛑 **NÃO sobrevive.**
- **M9 Câmara**, k = 20 — 1ª metade: `XLP +3.00 ✅ · XLK -3.62 ✅` (✅, n = 108) · 2ª metade: `XLP +0.40 ✅ · XLK -1.53 ✅` (✅, n = 96). **Sobrevive.**

**2 de 8** aprovações setoriais com G1 acima do tick sobrevivem ao corte: **M4 recessão EUA 2025** k = 5 · **M9 Câmara** k = 20.

⚠️ **Mas cuidado com o que isso credita à transversal:** **M4 recessão EUA 2025** k = 5 passa **nos dois livros**. Ali quem funciona é o **gatilho**, e o livro setorial não acrescenta nada — é a mesma informação expressa de outro jeito. A transversal só tem crédito próprio onde o direcional falha e ela passa: **M9 Câmara** k = 20.

⚠️ **O que o projeto já mediu sobre esses mercados, em outra camada:**

- **M4 recessão EUA 2025** — a **view 3.1** leu este mercado, e a D19c mediu que o coeficiente **troca de sinal dentro da própria amostra** (SPY em h = 10: +0,97% t +6,52 na 1ª metade, **−0,35% t −2,27** na 2ª). Não há segundo mercado de recessão, então não existe teste fora da amostra — e agora se sabe que não existe nem dentro dela.
- **M5 Trump 2024** — a **view 2.4** leu este mercado e foi cortada: o efeito aterrissa no gap (23% sobra na janela negociável) e o mecanismo partidário **reprovou fora da amostra** — o TLT cai nos dois mercados, quando deveria inverter.
- **M9 Câmara** — mesmo mecanismo partidário da 2.4, e é o segundo mercado do teste fora da amostra que a reprovou.

**O que isto NÃO diz:** nada sobre P&L, e nada sobre a evidência da 15f/19b. Aquelas mediram uma transversal de *view estrutural* com P montado por β contra breakeven, e o elo que falhou foi o transporte β → retorno. Este artefato não reabre nem confirma aquele veredito — mede outra coisa, com livro declarado a priori e sem β nenhum.

