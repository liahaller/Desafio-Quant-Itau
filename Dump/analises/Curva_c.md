# Curva `c` → alavancagem — o passo (2) da ordem da Lia, pré-executado

> Gerado por `scripts/curva_c.py`. O `c` da Lia **não existe ainda**: aqui ele é uma GRADE de valores constantes, para medir a sensibilidade antes de a régua chegar. **Isto mede, não escolhe** — nenhum `c` desta tabela é proposta de valor (CLAUDE.md §6).

- janela: **2025-02-10 a 2026-08-06** (374 pregões)
- view ativa: **só a 2.2** (a 2.3 espera o G8/DFF, a B o ZQ de dezembro) — com uma view só, o escalar **é** o `c` dela, não uma média
- as colunas de excesso usam teto **1** nos dois escopos (D12 em aberto); as de Σ|w| são da carteira PEDIDA, e não dependem de teto nenhum
- `irrestrito acumulado bruto` = a série sem teto composta, **sem custo** — o giro do irrestrito é proibitivo e não é o que se mede aqui

| c | incerteza (1/c) | Σ\|w\| pedida mediana | Σ\|w\| pedida máx | dias acima do teto 1 | dias de ruína (irrestrito) | irrestrito acumulado bruto | excesso — teto na carteira | excesso — teto no tilt |
|---|---|---|---|---|---|---|---|---|
| 1 | 1 | 195.13 | 34481.50 | 74% | 36 | — | -14.39 pp | -0.94 pp |
| 0.75 | 1 | 167.39 | 29555.71 | 74% | 28 | — | -14.38 pp | -0.94 pp |
| 0.5 | 2 | 130.42 | 22988.00 | 74% | 26 | — | -14.37 pp | -0.94 pp |
| 0.25 | 4 | 78.65 | 13793.20 | 74% | 16 | — | -14.33 pp | -0.94 pp |
| 0.1 | 10 | 36.30 | 6270.18 | 74% | 7 | — | -14.31 pp | -0.89 pp |
| 0.05 | 20 | 19.49 | 3284.86 | 74% | 3 | — | -14.33 pp | -0.86 pp |
| 0.02 | 50 | 8.61 | 1353.18 | 74% | 0 | -40.6% | -14.34 pp | -0.81 pp |
| 0.01 | 100 | 4.84 | 683.78 | 74% | 0 | +39.5% | -14.12 pp | -0.77 pp |

## Leitura

**Com `c = 1` (o que o backtest roda hoje) o BL pede Σ|w| mediana de 195.1 e máximo de 34,481**, com 74% dos pregões acima do teto de 1. É a alavancagem que o teto está segurando hoje.

> **Não bate com o número da seção 10 do `Decisoes_pendentes.md`** ("Σ|w| mediana 24, máx 264", medido em 05/08), e a diferença é de MÉTODO, não de dado. Sem teto o backtest **morre no primeiro dia de ruína**, então a estatística de lá só pode ter coberto os pregões anteriores a ele. No dado de hoje a primeira ruína é em **2025-03-19**, e nos 26 pregões até lá a mediana é 84 e o máximo 380 — contra 195 e 34,481 na janela inteira. Aqui a conta roda na carteira PEDIDA, que existe todo dia porque não depende de trajetória. **O registro antigo subestima o problema; não o inventa** — e a conclusão que ele sustenta (sem limitador a carteira vai à ruína) fica mais forte, não mais fraca.

**O `c` tira alavancagem, mas menos que proporcionalmente — e a forma é conhecida.** Com Ω = (1/c)·diag(P·τΣ·Pᵀ), o tilt do posterior escala como **c/(1+c)**, não como c: o Ω entra SOMADO à variância do prior da view, então perto de `c = 1` metade do peso já vem do prior e apertar o `c` rende pouco. Confere no dado: de `c = 1` a `c = 0.01` a fórmula prevê o TILT encolhendo 50.5×, e a Σ|w| pedida mediana cai 40.3×. Os dois números não têm de bater exato — Σ|w| carrega junto a perna de mercado, que não escala com o `c` — mas a ordem de grandeza fecha, e é o que valida a leitura.

**No teto de 1, o `c` não muda o resultado — o teto morde antes.** O excesso vai de -14.39 pp a -14.12 pp (escopo de carteira) e de -0.94 pp a -0.77 pp (escopo de tilt) ao longo de toda a grade, enquanto a Σ|w| pedida cai 40×. **É a resposta ao passo (3) da Lia:** para o teto virar redundante, a Σ|w| pedida teria de cair abaixo dele — e mesmo em `c = 0.01` ela ainda está em 4.8 de mediana. Nesta janela e com esta view, **o `c` não substitui o limitador de tamanho**; os dois têm de conviver, que é diferente de "o teto está fazendo o trabalho do Ω".

**A ruína do irrestrito só some com `c ≤ 0.02`.** Acima disso existe pelo menos um dia em que a carteira sem teto perde mais de 100% do patrimônio — o motivo de o teto ter entrado em 05/08. Ou seja: **algum** limitador é obrigatório até `c ≈ 0.02`; a pergunta aberta é se ele precisa continuar sendo um teto.

**Σ|w| pedida nunca cabe em 1** em toda a grade: mesmo no `c` mais apertado o BL pede mais alavancagem do que o teto mais justo da varredura permite.

**O que isto NÃO decide:** nem o `c` (é da régua da Lia), nem o nível do teto, nem o escopo dele (D12, do grupo). A tabela existe para que, no dia em que o vetor dela chegar, a resposta do passo (2) já esteja medida em vez de virar mais uma rodada de espera.

