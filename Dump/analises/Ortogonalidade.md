# Ortogonalidade — item 4 da D22 e obrigação 5a

> Gerado por `scripts/ortogonalidade.py`. **Mede; não decide.** Escala da 15b = **entropia crua** (D15c, fechada em 2026-08-10).

- janela: **2025-02-10 a 2026-08-06** (374 pregões)
- views vivas: **2.2 inflação** (274 dias) · **2.3 Fed** (325 dias) · **15g B própria** (210 dias) · **15b incerteza** (27 dias) · ****C** geopolítica (k = 1)** (72 dias) · ****C** geopolítica (k = 2)** (68 dias) · ****C** geopolítica (k = 3)** (64 dias) · ****C** geopolítica (k = 4)** (60 dias) · ****C** geopolítica (k = 5)** (56 dias)


## 1. Ângulo entre os P (dia a dia, nos pregões em que as duas vivem)

| par | dias em comum | ângulo mediano | mínimo | p05 | dias < 30° |
|---|---|---|---|---|---|
| 2.2 inflação × 2.3 Fed | 239 | 77.9° | 75.9° | 75.9° | 0 |
| 2.2 inflação × 15g B própria | 168 | 87.5° | 86.1° | 86.1° | 0 |
| 2.2 inflação × 15b incerteza | 13 | 90.0° | 90.0° | 90.0° | 0 |
| 2.2 inflação × **C** geopolítica (k = 1) | 26 | 109.6° | 92.9° | 94.4° | 0 |
| 2.2 inflação × **C** geopolítica (k = 2) | 25 | 111.8° | 86.5° | 93.2° | 0 |
| 2.2 inflação × **C** geopolítica (k = 3) | 25 | 88.7° | 71.0° | 71.3° | 0 |
| 2.2 inflação × **C** geopolítica (k = 4) | 25 | 93.2° | 71.3° | 72.9° | 0 |
| 2.2 inflação × **C** geopolítica (k = 5) | 25 | 95.2° | 81.9° | 86.5° | 0 |
| 2.3 Fed × 15g B própria | 203 | 70.9° | 69.8° | 69.8° | 0 |
| 2.3 Fed × 15b incerteza | 19 | 90.0° | 90.0° | 90.0° | 0 |
| 2.3 Fed × **C** geopolítica (k = 1) | 69 | 146.1° | 63.5° | 79.9° | 0 |
| 2.3 Fed × **C** geopolítica (k = 2) | 66 | 160.9° | 85.9° | 94.8° | 0 |
| 2.3 Fed × **C** geopolítica (k = 3) | 62 | 108.6° | 18.9° | 31.6° | 2 |
| 2.3 Fed × **C** geopolítica (k = 4) | 58 | 119.6° | 22.4° | 48.5° | 1 |
| 2.3 Fed × **C** geopolítica (k = 5) | 54 | 106.3° | 41.2° | 75.6° | 0 |
| 15g B própria × 15b incerteza | 15 | 90.0° | 90.0° | 90.0° | 0 |
| 15g B própria × **C** geopolítica (k = 1) | 50 | 100.7° | 65.9° | 73.1° | 0 |
| 15g B própria × **C** geopolítica (k = 2) | 48 | 114.1° | 71.7° | 96.0° | 0 |
| 15g B própria × **C** geopolítica (k = 3) | 46 | 116.5° | 64.8° | 73.4° | 0 |
| 15g B própria × **C** geopolítica (k = 4) | 44 | 120.9° | 60.7° | 73.6° | 0 |
| 15g B própria × **C** geopolítica (k = 5) | 42 | 127.0° | 89.0° | 111.7° | 0 |
| 15b incerteza × **C** geopolítica (k = 1) | 5 | 90.0° | 90.0° | 90.0° | 0 |
| 15b incerteza × **C** geopolítica (k = 2) | 4 | 90.0° | 90.0° | 90.0° | 0 |
| 15b incerteza × **C** geopolítica (k = 3) | 4 | 90.0° | 90.0° | 90.0° | 0 |
| 15b incerteza × **C** geopolítica (k = 4) | 4 | 90.0° | 90.0° | 90.0° | 0 |
| 15b incerteza × **C** geopolítica (k = 5) | 4 | 90.0° | 90.0° | 90.0° | 0 |

## 2. ρ entre os sinais-fonte (o que de fato testa a 15b)

| par | dias em comum | ρ de Pearson | ρ de Spearman |
|---|---|---|---|
| 2.2 inflação × 2.3 Fed | 239 | -0.197 | -0.380 |
| 2.2 inflação × 15g B própria | 168 | +0.673 | +0.765 |
| 2.2 inflação × 15b incerteza | 13 | -0.132 | -0.269 |
| 2.2 inflação × **C** geopolítica (k = 1) | 26 | +0.175 | +0.156 |
| 2.2 inflação × **C** geopolítica (k = 2) | 25 | +0.663 | +0.451 |
| 2.2 inflação × **C** geopolítica (k = 3) | 25 | +0.827 | +0.674 |
| 2.2 inflação × **C** geopolítica (k = 4) | 25 | +0.818 | +0.732 |
| 2.2 inflação × **C** geopolítica (k = 5) | 25 | +0.865 | +0.771 |
| 2.3 Fed × 15g B própria | 203 | -0.462 | -0.520 |
| 2.3 Fed × 15b incerteza | 19 | +0.193 | +0.284 |
| 2.3 Fed × **C** geopolítica (k = 1) | 69 | -0.013 | -0.005 |
| 2.3 Fed × **C** geopolítica (k = 2) | 66 | +0.043 | +0.084 |
| 2.3 Fed × **C** geopolítica (k = 3) | 62 | +0.107 | +0.088 |
| 2.3 Fed × **C** geopolítica (k = 4) | 58 | +0.104 | +0.059 |
| 2.3 Fed × **C** geopolítica (k = 5) | 54 | +0.129 | +0.105 |
| 15g B própria × 15b incerteza | 15 | -0.091 | -0.043 |
| 15g B própria × **C** geopolítica (k = 1) | 50 | +0.157 | +0.172 |
| 15g B própria × **C** geopolítica (k = 2) | 48 | +0.255 | +0.231 |
| 15g B própria × **C** geopolítica (k = 3) | 46 | +0.241 | +0.260 |
| 15g B própria × **C** geopolítica (k = 4) | 44 | +0.202 | +0.250 |
| 15g B própria × **C** geopolítica (k = 5) | 42 | +0.186 | +0.250 |
| 15b incerteza × **C** geopolítica (k = 1) | 5 | -0.388 | -0.300 |
| 15b incerteza × **C** geopolítica (k = 2) | 4 | -0.838 | -0.800 |
| 15b incerteza × **C** geopolítica (k = 3) | 4 | -0.827 | -0.800 |
| 15b incerteza × **C** geopolítica (k = 4) | 4 | -0.878 | -0.800 |
| 15b incerteza × **C** geopolítica (k = 5) | 4 | -0.869 | -0.800 |

## 3. ΣP por view — obrigação 5a

`P_from_betas` crava `P[SPY] = 0` exato, mas os outros 8 pesos não precisam somar zero. ΣP ≠ 0 numa view NEUTRA é exposição direcional não-intencional — e ela soma à da 15b, que é direcional de propósito.

| view | dias | ΣP mediano | ΣP médio | mín | máx | Σ\|P\| |
|---|---|---|---|---|---|---|
| 2.2 inflação | 274 | +0.961 | +0.962 | +0.961 | +0.962 | 2.00 |
| 2.3 Fed | 325 | +1.736 | +1.749 | +1.726 | +1.811 | 2.00 |
| 15g B própria | 210 | +1.241 | +1.160 | +0.546 | +1.310 | 2.00 |
| 15b incerteza | 27 | +2.000 | +2.000 | +2.000 | +2.000 | 2.00 |
| **C** geopolítica (k = 1) | 72 | -1.573 | -1.295 | -1.818 | +1.085 | 2.00 |
| **C** geopolítica (k = 2) | 68 | -1.726 | -1.520 | -1.787 | +0.215 | 2.00 |
| **C** geopolítica (k = 3) | 64 | -1.084 | -0.762 | -2.000 | +1.927 | 2.00 |
| **C** geopolítica (k = 4) | 60 | -1.506 | -1.064 | -2.000 | +1.785 | 2.00 |
| **C** geopolítica (k = 5) | 56 | -1.246 | -1.171 | -2.000 | +0.628 | 2.00 |

**Exposição direcional agregada** — soma dos ΣP das views vivas no mesmo pregão, que é o que a carteira sente:

| recorte | dias | ΣP agregado mediano | mín | máx |
|---|---|---|---|---|
| todos os pregões | 364 | +2.773 | -7.155 | +8.294 |
| pregões SEM a 15b | 337 | +2.773 | -7.155 | +8.294 |
| pregões COM a 15b | 27 | +4.214 | -4.647 | +8.031 |

## Leitura (gerada)

Limiares de RELATO — |ρ| ≥ 0,50 e |ΣP| ≥ 0,50. **Não são notas de corte:** a D22 exige 'ângulo alto' e 'sem ρ alto' sem cravar número, e cravar um aqui seria inventar threshold (CLAUDE.md §6).

- **Ângulo de exatamente 90°, e ele NÃO testa nada** em: 2.2 inflação × 15b incerteza · 2.3 Fed × 15b incerteza · 15g B própria × 15b incerteza · 15b incerteza × **C** geopolítica (k = 1) · 15b incerteza × **C** geopolítica (k = 2) · 15b incerteza × **C** geopolítica (k = 3) · 15b incerteza × **C** geopolítica (k = 4) · 15b incerteza × **C** geopolítica (k = 5). O P da 15b é `[SPY=2, 0…]` e o das neutras sai de `P_from_betas`, que crava `P[SPY] = 0` EXATO — o produto interno é zero por construção, em qualquer amostra. Para a 15b o item 4 se decide **só pelo ρ**.
- **ρ acima do limiar de relato em: **2.2 inflação × 15g B própria** ρ +0.673 (spearman +0.765, 168 dias) · **2.2 inflação × **C** geopolítica (k = 2)** ρ +0.663 (spearman +0.451, 25 dias) · **2.2 inflação × **C** geopolítica (k = 3)** ρ +0.827 (spearman +0.674, 25 dias) · **2.2 inflação × **C** geopolítica (k = 4)** ρ +0.818 (spearman +0.732, 25 dias) · **2.2 inflação × **C** geopolítica (k = 5)** ρ +0.865 (spearman +0.771, 25 dias) · **15b incerteza × **C** geopolítica (k = 2)** ρ -0.838 (spearman -0.800, 4 dias) · **15b incerteza × **C** geopolítica (k = 3)** ρ -0.827 (spearman -0.800, 4 dias) · **15b incerteza × **C** geopolítica (k = 4)** ρ -0.878 (spearman -0.800, 4 dias) · **15b incerteza × **C** geopolítica (k = 5)** ρ -0.869 (spearman -0.800, 4 dias).** A D22 não define o que é 'alto' — quem lê decide, e a decisão é humana.
- 🛑 **Obrigação 5a: as views NEUTRAS não são neutras** — **2.2 inflação** ΣP +0.961 · **2.3 Fed** ΣP +1.736 · **15g B própria** ΣP +1.241. `P[SPY] = 0` é exato, mas o resto do vetor é LÍQUIDO COMPRADO nos outros 8 ativos, que têm β próprio ao mercado. A regra do docstring: se o direcional não for intencional, a centragem se troca em TODAS as views juntas, nunca em uma. **Decisão humana — não fechada aqui.**
