# Curva `c` → alavancagem — o passo (2) da ordem da Lia, pré-executado

> Gerado por `scripts/curva_c.py`. O `c` aqui é uma GRADE de valores CONSTANTES no eixo de **confiança** (maior = mais peso). A régua da Lia entrega no eixo recíproco (`c >= 1`, incerteza) e **por view**: com nível 1 ela ocupa **[0,36 · 1,0]** deste eixo (mediana 0,953, medida nas 601 decisões da 2.2). Grade constante é portanto um LIMITE da régua, não a régua. **Isto mede, não escolhe** — nenhum `c` desta tabela é proposta de valor (CLAUDE.md §6).

- janela: **2025-02-10 a 2026-08-06** (374 pregões)
- views ativas: **2.2 e 2.3** (a B fora do v1 pela decisão 11) — o mesmo `c` entra nas duas, então a curva é **sensibilidade agregada**, não o `c` de uma view
- as colunas de excesso usam teto **1** nos dois escopos (D12 em aberto); as de Σ|w| são da carteira PEDIDA, e não dependem de teto nenhum
- `irrestrito acumulado bruto` = a série sem teto composta, **sem custo** — o giro do irrestrito é proibitivo e não é o que se mede aqui

| c | incerteza (1/c) | Σ\|w\| pedida mediana | Σ\|w\| pedida máx | dias acima do teto 1 | dias de ruína (irrestrito) | irrestrito acumulado bruto | excesso — teto na carteira | excesso — teto no tilt |
|---|---|---|---|---|---|---|---|---|
| 1 | 1.00 | 191.99 | 34138.09 | 96% | 35 | — | -15.20 pp | +4.07 pp |
| 0.953 | 1.05 | 187.34 | 33316.25 | 96% | 34 | — | -15.15 pp | +4.18 pp |
| 0.865 | 1.16 | 178.00 | 31666.15 | 96% | 29 | — | -15.04 pp | +4.40 pp |
| 0.785 | 1.27 | 168.73 | 30024.93 | 96% | 27 | — | -14.92 pp | +4.63 pp |
| 0.6 | 1.67 | 143.81 | 25601.33 | 96% | 25 | — | -14.58 pp | +5.28 pp |
| 0.362 | 2.76 | 101.97 | 18144.01 | 96% | 16 | — | -13.91 pp | +5.82 pp |

## Leitura

**Com `c = 1` (o que o backtest roda hoje) o BL pede Σ|w| mediana de 192.0 e máximo de 34,138**, com 96% dos pregões acima do teto de 1. É a alavancagem que o teto está segurando hoje.

> **Não bate com o número da seção 10 do `Decisoes_pendentes.md`** ("Σ|w| mediana 24, máx 264", medido em 05/08), e a diferença é de MÉTODO, não de dado. Sem teto o backtest **morre no primeiro dia de ruína**, então a estatística de lá só pode ter coberto os pregões anteriores a ele. No dado de hoje a primeira ruína é em **2025-03-19**, e nos 26 pregões até lá a mediana é 86 e o máximo 388 — contra 192 e 34,138 na janela inteira. Aqui a conta roda na carteira PEDIDA, que existe todo dia porque não depende de trajetória. **O registro antigo subestima o problema; não o inventa** — e a conclusão que ele sustenta (sem limitador a carteira vai à ruína) fica mais forte, não mais fraca.

**O `c` tira alavancagem, mas menos que proporcionalmente — e a forma é conhecida.** Com Ω = (1/c)·diag(P·τΣ·Pᵀ), o tilt do posterior escala como **c/(1+c)**, não como c: o Ω entra SOMADO à variância do prior da view, então perto de `c = 1` metade do peso já vem do prior e apertar o `c` rende pouco. Confere no dado: de `c = 1` a `c = 0.362` a fórmula prevê o TILT encolhendo 1.9×, e a Σ|w| pedida mediana cai 1.9×. Os dois números não têm de bater exato — Σ|w| carrega junto a perna de mercado, que não escala com o `c` — mas a ordem de grandeza fecha, e é o que valida a leitura.

**No teto de 1 o `c` move o excesso em no máximo 1.74 pp e não troca o sinal em nenhum escopo** — o teto morde antes.

O excesso vai de -15.20 pp a -13.91 pp (escopo de carteira) e de +4.07 pp a +5.82 pp (escopo de tilt) ao longo de toda a grade, enquanto a Σ|w| pedida cai 2×. **É a resposta ao passo (3) da Lia:** para o teto virar redundante, a Σ|w| pedida teria de cair abaixo dele — e mesmo em `c = 0.362` ela ainda está em 102.0 de mediana. Nesta janela e com estas views, **o `c` não substitui o limitador de tamanho**; os dois têm de conviver, que é diferente de "o teto está fazendo o trabalho do Ω".

**A ruína do irrestrito não some em nenhum `c` da grade.** Um limitador de tamanho é obrigatório em toda a faixa medida — o `c` sozinho não substitui o teto.

**Σ|w| pedida nunca cabe em 1** em toda a grade: mesmo no `c` mais apertado o BL pede mais alavancagem do que o teto mais justo da varredura permite.

**O que isto NÃO decide:** nem o `c` (é da régua da Lia), nem o nível do teto, nem o escopo dele (D12, do grupo). A tabela existe para que, no dia em que o vetor dela chegar, a resposta do passo (2) já esteja medida em vez de virar mais uma rodada de espera.

