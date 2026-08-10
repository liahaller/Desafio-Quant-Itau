# Curva `c` → alavancagem — o passo (2) da ordem da Lia, pré-executado

> Gerado por `scripts/curva_c.py`. O `c` aqui é uma GRADE de valores CONSTANTES no eixo de **confiança** (maior = mais peso). A régua da Lia entrega no eixo recíproco (`c >= 1`, incerteza) e **por view**: com nível 1 ela ocupa **[0,36 · 1,0]** deste eixo (mediana 0,953, medida nas 601 decisões da 2.2). Grade constante é portanto um LIMITE da régua, não a régua. **Isto mede, não escolhe** — nenhum `c` desta tabela é proposta de valor (CLAUDE.md §6).

- janela: **2025-02-10 a 2026-08-06** (374 pregões)
- views ativas: **2.2 e 2.3** (a B fora do v1 pela decisão 11) — o mesmo `c` entra nas duas, então a curva é **sensibilidade agregada**, não o `c` de uma view
- as colunas de excesso usam teto **1** nos dois escopos (D12 em aberto); as de Σ|w| são da carteira PEDIDA, e não dependem de teto nenhum
- `irrestrito acumulado bruto` = a série sem teto composta, **sem custo** — o giro do irrestrito é proibitivo e não é o que se mede aqui

| c | incerteza (1/c) | Σ\|w\| pedida mediana | Σ\|w\| pedida máx | dias acima do teto 1 | dias de ruína (irrestrito) | irrestrito acumulado bruto | excesso — teto na carteira | excesso — teto no tilt |
|---|---|---|---|---|---|---|---|---|
| 1 | 1.00 | 191.99 | 34138.09 | 96% | 35 | — | -15.20 pp | +4.07 pp |
| 0.75 | 1.33 | 164.42 | 29259.74 | 96% | 26 | — | -14.87 pp | +4.74 pp |
| 0.5 | 2.00 | 127.82 | 22756.12 | 96% | 23 | — | -14.34 pp | +5.52 pp |
| 0.25 | 4.00 | 76.90 | 13652.68 | 96% | 14 | — | -13.46 pp | +6.23 pp |
| 0.1 | 10.00 | 35.47 | 6205.80 | 96% | 6 | — | -12.95 pp | +4.89 pp |
| 0.05 | 20.00 | 19.05 | 3251.04 | 96% | 2 | — | -13.23 pp | +2.91 pp |
| 0.02 | 50.00 | 8.43 | 1339.28 | 96% | 0 | -8.0% | -13.96 pp | +0.74 pp |
| 0.01 | 100.00 | 4.75 | 676.77 | 96% | 0 | +65.4% | -14.20 pp | -0.11 pp |

## Leitura

**Com `c = 1` (o que o backtest roda hoje) o BL pede Σ|w| mediana de 192.0 e máximo de 34,138**, com 96% dos pregões acima do teto de 1. É a alavancagem que o teto está segurando hoje.

> **Não bate com o número da seção 10 do `Decisoes_pendentes.md`** ("Σ|w| mediana 24, máx 264", medido em 05/08), e a diferença é de MÉTODO, não de dado. Sem teto o backtest **morre no primeiro dia de ruína**, então a estatística de lá só pode ter coberto os pregões anteriores a ele. No dado de hoje a primeira ruína é em **2025-03-19**, e nos 26 pregões até lá a mediana é 86 e o máximo 388 — contra 192 e 34,138 na janela inteira. Aqui a conta roda na carteira PEDIDA, que existe todo dia porque não depende de trajetória. **O registro antigo subestima o problema; não o inventa** — e a conclusão que ele sustenta (sem limitador a carteira vai à ruína) fica mais forte, não mais fraca.

**O `c` tira alavancagem, mas menos que proporcionalmente — e a forma é conhecida.** Com Ω = (1/c)·diag(P·τΣ·Pᵀ), o tilt do posterior escala como **c/(1+c)**, não como c: o Ω entra SOMADO à variância do prior da view, então perto de `c = 1` metade do peso já vem do prior e apertar o `c` rende pouco. Confere no dado: de `c = 1` a `c = 0.01` a fórmula prevê o TILT encolhendo 50.5×, e a Σ|w| pedida mediana cai 40.4×. Os dois números não têm de bater exato — Σ|w| carrega junto a perna de mercado, que não escala com o `c` — mas a ordem de grandeza fecha, e é o que valida a leitura.

**No teto de 1 o `c` move o resultado em até 6.34 pp** — e no escopo `no tilt` ele chega a TROCAR o sinal do excesso. Não dá para tratar a régua dela como ajuste fino: a escolha do nível é escolha de resultado, que é exatamente por que o protocolo anti-overfit da seção 10 pede que o nível saia uma vez só, junto do teto, e não por iteração contra esta tabela.

O excesso vai de -15.20 pp a -14.20 pp (escopo de carteira) e de +4.07 pp a -0.11 pp (escopo de tilt) ao longo de toda a grade, enquanto a Σ|w| pedida cai 40×. **É a resposta ao passo (3) da Lia:** para o teto virar redundante, a Σ|w| pedida teria de cair abaixo dele — e mesmo em `c = 0.01` ela ainda está em 4.8 de mediana. Nesta janela e com estas views, **o `c` não substitui o limitador de tamanho**; os dois têm de conviver, que é diferente de "o teto está fazendo o trabalho do Ω".

**A ruína do irrestrito só some com `c ≤ 0.02`.** Acima disso existe pelo menos um dia em que a carteira sem teto perde mais de 100% do patrimônio — o motivo de o teto ter entrado em 05/08. Ou seja: **algum** limitador é obrigatório até `c ≈ 0.02`; a pergunta aberta é se ele precisa continuar sendo um teto.

**Σ|w| pedida nunca cabe em 1** em toda a grade: mesmo no `c` mais apertado o BL pede mais alavancagem do que o teto mais justo da varredura permite.

**O que isto NÃO decide:** nem o `c` (é da régua da Lia), nem o nível do teto, nem o escopo dele (D12, do grupo). A tabela existe para que, no dia em que o vetor dela chegar, a resposta do passo (2) já esteja medida em vez de virar mais uma rodada de espera.

