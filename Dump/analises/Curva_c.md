# Curva `c` → alavancagem — o passo (2) da ordem da Lia, pré-executado

> Gerado por `scripts/curva_c.py`. O `c` aqui é uma GRADE de valores CONSTANTES no eixo de **confiança** (maior = mais peso). A régua da Lia entrega no eixo recíproco (`c >= 1`, incerteza) e **por view**: com nível 1 ela ocupa **[0,36 · 1,0]** deste eixo (mediana 0,953, medida nas 601 decisões da 2.2). Grade constante é portanto um LIMITE da régua, não a régua. **Isto mede, não escolhe** — nenhum `c` desta tabela é proposta de valor (CLAUDE.md §6).

- janela: **2025-02-10 a 2026-08-06** (374 pregões)
- views ativas: **2.2_inflacao** · **2.3_fed** · **B_trajetoria_propria** · **incerteza_anuncio** (4) — na grade constante o mesmo `c` entra em todas, então essa tabela é **sensibilidade agregada**, não o `c` de uma view
- as colunas de excesso usam teto **1** nos dois escopos (D12 em aberto); as de Σ|w| são da carteira PEDIDA, e não dependem de teto nenhum
- `irrestrito acumulado bruto` = a série sem teto composta, **sem custo** — o giro do irrestrito é proibitivo e não é o que se mede aqui

| c | incerteza (1/c) | Σ\|w\| pedida mediana | Σ\|w\| pedida máx | dias acima do teto 1 | dias de ruína (irrestrito) | irrestrito acumulado bruto | excesso — teto na carteira | excesso — teto no tilt |
|---|---|---|---|---|---|---|---|---|
| 1 | 1.00 | 220.48 | 34138.09 | 97% | 33 | — | -17.89 pp | +6.24 pp |
| 0.75 | 1.33 | 187.78 | 29259.74 | 97% | 26 | — | -17.89 pp | +6.73 pp |
| 0.5 | 2.00 | 145.11 | 22756.12 | 97% | 24 | — | -17.90 pp | +7.32 pp |
| 0.25 | 4.00 | 86.71 | 13652.68 | 97% | 14 | — | -17.83 pp | +8.09 pp |
| 0.1 | 10.00 | 39.52 | 6205.80 | 96% | 6 | — | -17.02 pp | +6.27 pp |
| 0.05 | 20.00 | 21.08 | 3251.04 | 96% | 2 | — | -16.58 pp | +4.33 pp |
| 0.02 | 50.00 | 9.25 | 1339.28 | 96% | 0 | -7.6% | -17.63 pp | +3.39 pp |
| 0.01 | 100.00 | 5.16 | 676.77 | 96% | 0 | +65.6% | -17.01 pp | +1.28 pp |

## Leitura

**Com `c = 1` (o que o backtest roda hoje) o BL pede Σ|w| mediana de 220.5 e máximo de 34,138**, com 97% dos pregões acima do teto de 1. É a alavancagem que o teto está segurando hoje.

> **Não bate com o número da seção 10 do `Decisoes_pendentes.md`** ("Σ|w| mediana 24, máx 264", medido em 05/08), e a diferença é de MÉTODO, não de dado. Sem teto o backtest **morre no primeiro dia de ruína**, então a estatística de lá só pode ter coberto os pregões anteriores a ele. No dado de hoje a primeira ruína é em **2025-03-27**, e nos 32 pregões até lá a mediana é 143 e o máximo 697 — contra 220 e 34,138 na janela inteira. Aqui a conta roda na carteira PEDIDA, que existe todo dia porque não depende de trajetória. **O registro antigo subestima o problema; não o inventa** — e a conclusão que ele sustenta (sem limitador a carteira vai à ruína) fica mais forte, não mais fraca.

**O `c` tira alavancagem, mas menos que proporcionalmente — e a forma é conhecida.** Com Ω = (1/c)·diag(P·τΣ·Pᵀ), o tilt do posterior escala como **c/(1+c)**, não como c: o Ω entra SOMADO à variância do prior da view, então perto de `c = 1` metade do peso já vem do prior e apertar o `c` rende pouco. Confere no dado: de `c = 1` a `c = 0.01` a fórmula prevê o TILT encolhendo 50.5×, e a Σ|w| pedida mediana cai 42.7×. Os dois números não têm de bater exato — Σ|w| carrega junto a perna de mercado, que não escala com o `c` — mas a ordem de grandeza fecha, e é o que valida a leitura.

**No teto de 1 o `c` move o excesso em no máximo 6.81 pp e não troca o sinal em nenhum escopo** — o teto morde antes.

O excesso vai de -17.89 pp a -17.01 pp (escopo de carteira) e de +6.24 pp a +1.28 pp (escopo de tilt) ao longo de toda a grade, enquanto a Σ|w| pedida cai 43×. **É a resposta ao passo (3) da Lia:** para o teto virar redundante, a Σ|w| pedida teria de cair abaixo dele — e mesmo em `c = 0.01` ela ainda está em 5.2 de mediana. Nesta janela e com estas views, **o `c` não substitui o limitador de tamanho**; os dois têm de conviver, que é diferente de "o teto está fazendo o trabalho do Ω".

**A ruína do irrestrito só some com `c ≤ 0.02`.** Acima disso existe pelo menos um dia em que a carteira sem teto perde mais de 100% do patrimônio — o motivo de o teto ter entrado em 05/08. Ou seja: **algum** limitador é obrigatório até `c ≈ 0.02`; a pergunta aberta é se ele precisa continuar sendo um teto.

**Σ|w| pedida nunca cabe em 1** em toda a grade: mesmo no `c` mais apertado o BL pede mais alavancagem do que o teto mais justo da varredura permite.


## O eixo do NÍVEL — a régua REAL, não o limite dela

> A tabela acima é grade **constante**: o mesmo `c` nas quatro views todo dia. Isso mede o LIMITE da régua e nunca o efeito dela, que é de **cauda** — grade constante apaga por construção a diferenciação entre mercado bom e ruim, que é a função da régua. Abaixo entra a série **por decisão** da Lia (`lia/c_por_decisao.csv`), e o eixo passa a ser o **nível** (D20b). Como `c = c_nivel1 ** nivel`, uma série cobre o eixo inteiro (D25c) e **`nível = 0` é He-Litterman puro com o veto ligado** — é a linha que separa os dois canais da régua, o veto e a dosagem.

| nível | c mediano (ativas) | c p95 | views/dia | Σ\|w\| pedida mediana | dias de ruína | excesso — teto na carteira | excesso — teto no tilt |
|---|---|---|---|---|---|---|---|
| sem régua | — | — | 2.24 | 220.5 | 33 | -17.89 pp | +6.24 pp |
| 0 | 1.0000 | 1.0000 | 1.99 | 177.3 | 31 | -12.13 pp | +6.16 pp |
| 1 | 1.0242 | 1.1145 | 1.99 | 174.3 | 28 | -12.32 pp | +5.98 pp |
| 2 | 1.0489 | 1.2421 | 1.99 | 168.3 | 28 | -12.54 pp | +5.75 pp |
| 3 | 1.0743 | 1.3843 | 1.99 | 161.7 | 26 | -12.80 pp | +5.46 pp |
| 5 | 1.1269 | 1.7194 | 1.99 | 146.6 | 26 | -13.36 pp | +4.74 pp |
| 8 | 1.2106 | 2.3801 | 1.99 | 130.3 | 24 | -14.42 pp | +3.48 pp |

**O veto sozinho já move o número.** Sem régua o BL vê 2.24 views por dia; com `nível = 0` — que não dosa nada, só aplica o `ativa = False` — caem para 1.99, e a Σ|w| pedida mediana vai de 220.5 para 177.3. **Separar isso importa para 13/08:** parte do efeito da régua não depende do nível escolhido, porque o veto não tem nível.

**Ao longo do eixo do nível o excesso anda 2.77 pp** (de +3.48 a +6.24 pp, escopo de tilt), e a Σ|w| pedida mediana cai 1.7× da ponta frouxa à apertada. **Nenhum destes níveis é proposta** — a escolha sai da reunião de 13/08, uma vez só, junto do teto (seção 10). Esta tabela existe para que ela seja feita sobre um EIXO e não sobre um ponto.

**O que isto NÃO decide:** nem o nível da régua (é escolha da reunião de 13/08, no eixo da tabela acima), nem o nível do teto, nem o escopo dele (D12, do grupo). As duas tabelas medem; a escolha sai uma vez só, e não por iteração contra elas.

