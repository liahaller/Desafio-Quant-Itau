# Curva de absorção da view C — de onde sai o k

> Gerado por `scripts/absorcao_C.py`. **Mede; não decide.** Critério da espec 2.4 item 6 (*o perfil decide*), que não olha retorno de estratégia: o k é onde a resposta ACUMULADA para de crescer.

A coluna que decide é a **fração da resposta final** já acumulada até cada lag, no ativo da tese (**XLE**). O patamar é onde ela chega perto de 1 e para de andar.


## iran_jun2025 — 55 pregões com Δp

β acumulado do XLE (resposta final = -0.0916) e o que ele representa da resposta total:

| lag k | β marginal | β acumulado | fração do total | Σ\|β\| acumulado dos 9 |
|---|---|---|---|---|
| 0 | +0.0606 | +0.0606 | -0.66 | 0.2450 |
| 1 | +0.0157 | +0.0763 | -0.83 | 0.2846 |
| 2 | -0.0502 | +0.0261 | -0.29 | 0.6931 |
| 3 | -0.1150 | -0.0889 | +0.97 | 0.6249 |
| 4 | +0.1833 | +0.0944 | -1.03 | 0.2512 |
| 5 | -0.0733 | +0.0211 | -0.23 | 0.2862 |
| 6 | -0.1127 | -0.0916 | +1.00 | 0.9465 |

## iran_2026 — 27 pregões com Δp

β acumulado do XLE (resposta final = -0.0735) e o que ele representa da resposta total:

| lag k | β marginal | β acumulado | fração do total | Σ\|β\| acumulado dos 9 |
|---|---|---|---|---|
| 0 | +0.0313 | +0.0313 | -0.43 | 0.1602 |
| 1 | -0.0461 | -0.0147 | +0.20 | 0.2175 |
| 2 | -0.0469 | -0.0616 | +0.84 | 0.2979 |
| 3 | +0.0591 | -0.0025 | +0.03 | 0.2270 |
| 4 | -0.0686 | -0.0711 | +0.97 | 0.4195 |
| 5 | -0.0043 | -0.0754 | +1.03 | 0.3706 |
| 6 | +0.0019 | -0.0735 | +1.00 | 0.4026 |

## Os dois episódios lado a lado — fração da resposta acumulada no XLE

| lag k | iran_jun2025 | iran_2026 |
|---|---|---|
| 0 | -0.66 | -0.43 |
| 1 | -0.83 | +0.20 |
| 2 | -0.29 | +0.84 |
| 3 | +0.97 | +0.03 |
| 4 | -1.03 | +0.97 |
| 5 | -0.23 | +1.03 |
| 6 | +1.00 | +1.00 |

## Leitura (gerada)

- **iran_jun2025**: a fração acumulada atinge o máximo em **lag 4** (-1.03); o primeiro lag a partir do qual ela fica sempre ≥ 0,8 é **6**.
- **iran_2026**: a fração acumulada atinge o máximo em **lag 5** (+1.03); o primeiro lag a partir do qual ela fica sempre ≥ 0,8 é **4**.
- **Concordância entre episódios**: corr das duas curvas = **+0.08**. Se as duas apontarem o mesmo patamar, o k é mecanismo; se discordarem, **o perfil não identifica k** — e isso é o resultado, não uma falha da medição.
