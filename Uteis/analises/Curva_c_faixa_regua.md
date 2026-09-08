# Curva `c` → alavancagem — o passo (2) da ordem da Lia, pré-executado

> Gerado por `scripts/curva_c.py`. O `c` aqui é uma GRADE de valores CONSTANTES no eixo de **confiança** (maior = mais peso). A régua da Lia entrega no eixo recíproco (`c >= 1`, incerteza) e **por view**: com nível 1 ela ocupa **[0,36 · 1,0]** deste eixo (mediana 0,953, medida nas 601 decisões da 2.2). Grade constante é portanto um LIMITE da régua, não a régua. **Isto mede, não escolhe** — nenhum `c` desta tabela é proposta de valor (CLAUDE.md §6).

- janela: **2025-02-10 a 2026-08-06** (374 pregões)
- views ativas: **2.2_inflacao** · **2.3_fed** · **B_trajetoria_propria** · **incerteza_anuncio** (4) — na grade constante o mesmo `c` entra em todas, então essa tabela é **sensibilidade agregada**, não o `c` de uma view
- as colunas de excesso usam teto **1** nos dois escopos (D12 em aberto); as de Σ|w| são da carteira PEDIDA, e não dependem de teto nenhum
- `irrestrito acumulado bruto` = a série sem teto composta, **sem custo** — o giro do irrestrito é proibitivo e não é o que se mede aqui

| c | incerteza (1/c) | Σ\|w\| pedida mediana | Σ\|w\| pedida máx | dias acima do teto 1 | dias de ruína (irrestrito) | irrestrito acumulado bruto | excesso — teto na carteira | excesso — teto no tilt |
|---|---|---|---|---|---|---|---|---|
| 1 | 1.00 | 220.48 | 34138.09 | 97% | 33 | — | -17.89 pp | +6.24 pp |
| 0.953 | 1.05 | 214.92 | 33316.25 | 97% | 32 | — | -17.89 pp | +6.32 pp |
| 0.865 | 1.16 | 203.83 | 31666.15 | 97% | 30 | — | -17.89 pp | +6.48 pp |
| 0.785 | 1.27 | 192.87 | 30024.93 | 97% | 27 | — | -17.89 pp | +6.65 pp |
| 0.6 | 1.67 | 163.66 | 25601.33 | 97% | 25 | — | -17.90 pp | +7.13 pp |
| 0.362 | 2.76 | 115.36 | 18144.01 | 97% | 16 | — | -17.89 pp | +7.58 pp |

## Leitura

**Com `c = 1` (o que o backtest roda hoje) o BL pede Σ|w| mediana de 220.5 e máximo de 34,138**, com 97% dos pregões acima do teto de 1. É a alavancagem que o teto está segurando hoje.

> **Não bate com o número da seção 10 do `Decisoes_pendentes.md`** ("Σ|w| mediana 24, máx 264", medido em 05/08), e a diferença é de MÉTODO, não de dado. Sem teto o backtest **morre no primeiro dia de ruína**, então a estatística de lá só pode ter coberto os pregões anteriores a ele. No dado de hoje a primeira ruína é em **2025-03-27**, e nos 32 pregões até lá a mediana é 143 e o máximo 697 — contra 220 e 34,138 na janela inteira. Aqui a conta roda na carteira PEDIDA, que existe todo dia porque não depende de trajetória. **O registro antigo subestima o problema; não o inventa** — e a conclusão que ele sustenta (sem limitador a carteira vai à ruína) fica mais forte, não mais fraca.

**O `c` tira alavancagem, mas menos que proporcionalmente — e a forma é conhecida.** Com Ω = (1/c)·diag(P·τΣ·Pᵀ), o tilt do posterior escala como **c/(1+c)**, não como c: o Ω entra SOMADO à variância do prior da view, então perto de `c = 1` metade do peso já vem do prior e apertar o `c` rende pouco. Confere no dado: de `c = 1` a `c = 0.362` a fórmula prevê o TILT encolhendo 1.9×, e a Σ|w| pedida mediana cai 1.9×. Os dois números não têm de bater exato — Σ|w| carrega junto a perna de mercado, que não escala com o `c` — mas a ordem de grandeza fecha, e é o que valida a leitura.

**No teto de 1 o `c` move o excesso em no máximo 1.34 pp e não troca o sinal em nenhum escopo** — o teto morde antes.

O excesso vai de -17.89 pp a -17.89 pp (escopo de carteira) e de +6.24 pp a +7.58 pp (escopo de tilt) ao longo de toda a grade, enquanto a Σ|w| pedida cai 2×. **É a resposta ao passo (3) da Lia:** para o teto virar redundante, a Σ|w| pedida teria de cair abaixo dele — e mesmo em `c = 0.362` ela ainda está em 115.4 de mediana. Nesta janela e com estas views, **o `c` não substitui o limitador de tamanho**; os dois têm de conviver, que é diferente de "o teto está fazendo o trabalho do Ω".

**A ruína do irrestrito não some em nenhum `c` da grade.** Um limitador de tamanho é obrigatório em toda a faixa medida — o `c` sozinho não substitui o teto.

**Σ|w| pedida nunca cabe em 1** em toda a grade: mesmo no `c` mais apertado o BL pede mais alavancagem do que o teto mais justo da varredura permite.

**O que isto NÃO decide:** nem o nível da régua (é escolha da reunião de 13/08, no eixo da tabela acima), nem o nível do teto, nem o escopo dele (D12, do grupo). As duas tabelas medem; a escolha sai uma vez só, e não por iteração contra elas.

