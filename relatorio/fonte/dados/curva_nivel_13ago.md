# Curva `c` → alavancagem — o passo (2) da ordem da Lia, pré-executado

> Gerado por `scripts/curva_c.py`. O `c` aqui é uma GRADE de valores CONSTANTES no eixo de **confiança** (maior = mais peso). A régua da Lia entrega no eixo recíproco (`c >= 1`, incerteza) e **por view**: com nível 1 ela ocupa **[0,36 · 1,0]** deste eixo (mediana 0,953, medida nas 601 decisões da 2.2). Grade constante é portanto um LIMITE da régua, não a régua. **Isto mede, não escolhe** — nenhum `c` desta tabela é proposta de valor (CLAUDE.md §6).

- janela: **2025-02-10 a 2026-08-06** (374 pregões)
- views ativas: **2.2_inflacao** · **2.3_fed** · **B_trajetoria_propria** · **incerteza_anuncio** (4) — na grade constante o mesmo `c` entra em todas, então essa tabela é **sensibilidade agregada**, não o `c` de uma view
- as colunas de excesso usam teto **1** nos dois escopos (D12 em aberto); as de Σ|w| são da carteira PEDIDA, e não dependem de teto nenhum
- `irrestrito acumulado bruto` = a série sem teto composta, **sem custo** — o giro do irrestrito é proibitivo e não é o que se mede aqui

| c | incerteza (1/c) | Σ\|w\| pedida mediana | Σ\|w\| pedida máx | dias acima do teto 1 | dias de ruína (irrestrito) | irrestrito acumulado bruto | excesso — teto na carteira | excesso — teto no tilt |
|---|---|---|---|---|---|---|---|---|
| 1 | 1.00 | 221.79 | 34137.25 | 98% | 33 | — | -18.34 pp | +4.08 pp |
| 0.75 | 1.33 | 188.99 | 29259.81 | 98% | 26 | — | -18.12 pp | +4.13 pp |
| 0.5 | 2.00 | 146.22 | 22757.18 | 98% | 24 | — | -17.73 pp | +4.11 pp |
| 0.25 | 4.00 | 87.41 | 13654.68 | 98% | 13 | — | -16.55 pp | +4.22 pp |
| 0.1 | 10.00 | 40.32 | 6208.17 | 98% | 5 | — | -14.00 pp | +4.31 pp |
| 0.05 | 20.00 | 22.26 | 3253.47 | 98% | 2 | — | -12.28 pp | +4.43 pp |
| 0.02 | 50.00 | 10.62 | 1341.71 | 98% | 0 | +30.7% | -11.03 pp | +5.44 pp |
| 0.01 | 100.00 | 6.98 | 679.20 | 98% | 0 | +135.3% | -9.14 pp | +5.24 pp |

## Leitura

**Com `c = 1` (o que o backtest roda hoje) o BL pede Σ|w| mediana de 221.8 e máximo de 34,137**, com 98% dos pregões acima do teto de 1. É a alavancagem que o teto está segurando hoje.

> **Não bate com o número da seção 10 do `Decisoes_pendentes.md`** ("Σ|w| mediana 24, máx 264", medido em 05/08), e a diferença é de MÉTODO, não de dado. Sem teto o backtest **morre no primeiro dia de ruína**, então a estatística de lá só pode ter coberto os pregões anteriores a ele. No dado de hoje a primeira ruína é em **2025-03-27**, e nos 32 pregões até lá a mediana é 144 e o máximo 697 — contra 222 e 34,137 na janela inteira. Aqui a conta roda na carteira PEDIDA, que existe todo dia porque não depende de trajetória. **O registro antigo subestima o problema; não o inventa** — e a conclusão que ele sustenta (sem limitador a carteira vai à ruína) fica mais forte, não mais fraca.

**O `c` tira alavancagem, mas menos que proporcionalmente — e a forma é conhecida.** Com Ω = (1/c)·diag(P·τΣ·Pᵀ), o tilt do posterior escala como **c/(1+c)**, não como c: o Ω entra SOMADO à variância do prior da view, então perto de `c = 1` metade do peso já vem do prior e apertar o `c` rende pouco. Confere no dado: de `c = 1` a `c = 0.01` a fórmula prevê o TILT encolhendo 50.5×, e a Σ|w| pedida mediana cai 31.8×. Os dois números não têm de bater exato — Σ|w| carrega junto a perna de mercado, que não escala com o `c` — mas a ordem de grandeza fecha, e é o que valida a leitura.

**No teto de 1 o `c` move o excesso em no máximo 9.21 pp e não troca o sinal em nenhum escopo** — o teto morde antes.

O excesso vai de -18.34 pp a -9.14 pp (escopo de carteira) e de +4.08 pp a +5.24 pp (escopo de tilt) ao longo de toda a grade, enquanto a Σ|w| pedida cai 32×. **É a resposta ao passo (3) da Lia:** para o teto virar redundante, a Σ|w| pedida teria de cair abaixo dele — e mesmo em `c = 0.01` ela ainda está em 7.0 de mediana. Nesta janela e com estas views, **o `c` não substitui o limitador de tamanho**; os dois têm de conviver, que é diferente de "o teto está fazendo o trabalho do Ω".

**A ruína do irrestrito só some com `c ≤ 0.02`.** Acima disso existe pelo menos um dia em que a carteira sem teto perde mais de 100% do patrimônio — o motivo de o teto ter entrado em 05/08. Ou seja: **algum** limitador é obrigatório até `c ≈ 0.02`; a pergunta aberta é se ele precisa continuar sendo um teto.

**Σ|w| pedida nunca cabe em 1** em toda a grade: mesmo no `c` mais apertado o BL pede mais alavancagem do que o teto mais justo da varredura permite.


## O eixo do NÍVEL — a régua REAL, não o limite dela

> A tabela acima é grade **constante**: o mesmo `c` nas quatro views todo dia. Isso mede o LIMITE da régua e nunca o efeito dela, que é de **cauda** — grade constante apaga por construção a diferenciação entre mercado bom e ruim, que é a função da régua. Abaixo entra a série **por decisão** da Lia (`lia/c_por_decisao.csv`), e o eixo passa a ser o **nível** (D20b). Como `c = c_nivel1 ** nivel`, uma série cobre o eixo inteiro (D25c) e **`nível = 0` é He-Litterman puro com o veto ligado** — é a linha que separa os dois canais da régua, o veto e a dosagem.

| nível | c mediano (ativas) | c p95 | views/dia | Σ\|w\| pedida mediana | dias de ruína | excesso — teto na carteira | excesso — teto no tilt |
|---|---|---|---|---|---|---|---|
| sem régua | — | — | 2.24 | 221.8 | 33 | -18.34 pp | +4.08 pp |
| 0 | 1.0000 | 1.0000 | 1.99 | 177.5 | 31 | -14.77 pp | +3.17 pp |
| 1 | 1.0242 | 1.1145 | 1.99 | 174.5 | 28 | -14.86 pp | +3.04 pp |
| 2 | 1.0489 | 1.2421 | 1.99 | 168.6 | 28 | -14.99 pp | +2.87 pp |
| 3 | 1.0743 | 1.3843 | 1.99 | 162.6 | 27 | -15.18 pp | +2.60 pp |
| 5 | 1.1269 | 1.7194 | 1.99 | 147.8 | 26 | -15.71 pp | +1.88 pp |
| 8 | 1.2106 | 2.3801 | 1.99 | 130.5 | 24 | -16.68 pp | +0.49 pp |

**O veto sozinho já move o número.** Sem régua o BL vê 2.24 views por dia; com `nível = 0` — que não dosa nada, só aplica o `ativa = False` — caem para 1.99, e a Σ|w| pedida mediana vai de 221.8 para 177.5. **Separar isso importa para 13/08:** parte do efeito da régua não depende do nível escolhido, porque o veto não tem nível.

**Ao longo do eixo do nível o excesso anda 3.59 pp** (de +0.49 a +4.08 pp, escopo de tilt), e a Σ|w| pedida mediana cai 1.7× da ponta frouxa à apertada. **Nenhum destes níveis é proposta** — a escolha sai da reunião de 13/08, uma vez só, junto do teto (seção 10). Esta tabela existe para que ela seja feita sobre um EIXO e não sobre um ponto.

**O que isto NÃO decide:** nem o nível da régua (é escolha da reunião de 13/08, no eixo da tabela acima), nem o nível do teto, nem o escopo dele (D12, do grupo). As duas tabelas medem; a escolha sai uma vez só, e não por iteração contra elas.

