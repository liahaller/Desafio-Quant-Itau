# Backtest com a view C empilhada — varredura em k

> Gerado por `scripts/view_C_backtest.py`. **Mede; não decide.** O k da C não está escolhido: a curva de absorção não identifica patamar (`Absorcao_C.md`). Escopo: **teto no tilt = 1**, γ = 1,0, custo de 2.0 bps/lado.

- janela: **2025-02-10 a 2026-08-06** (374 pregões)
- régua do Ω: **desligada nas duas pontas** — a régua da Lia cobre as quatro views da entrega e **não tem `c` para a C**. Por isso este artefato NÃO reproduz o número da entrega (que roda com ela desde a 6q): as duas pontas daqui são comparáveis entre si, e não com o `Backtest_v1.md`
- a primeira linha é a **entrega de 4 views** (D23) e é o grupo de controle do Δ desta tabela

| configuração | dias com a C | excesso × SPY | Δ vs. entrega | líquido | sharpe | Σ\|w\| média | giro/dia |
|---|---|---|---|---|---|---|---|
| entrega (4 views) | — | +4.08 pp | — | +34.2% | 1.21 | 1.94 | 0.320 |
| + C (k = 1) | 72 | -1.41 pp | -5.48 pp | +28.7% | 1.04 | 1.95 | 0.383 |
| + C (k = 2) | — | 🛑 **bloqueado (D4.1)** | — | — | — | — | — |
| + C (k = 3) | — | 🛑 **bloqueado (D4.1)** | — | — | — | — | — |
| + C (k = 4) | — | 🛑 **bloqueado (D4.1)** | — | — | — | — | — |
| + C (k = 5) | — | 🛑 **bloqueado (D4.1)** | — | — | — | — | — |

🛑 **A grade não roda inteira, e o motivo é uma decisão aberta desde o começo do projeto.** O `stack_views` recusa empilhar views com `horizonte_q_dias` diferentes (**DECISAO-4.1**, guarda que FALHA ALTO de propósito): o Q da C é **acumulado em k dias** e o das outras quatro é de **1 dia**. Somar os dois é somar km/h com km — não daria erro, daria peso errado.

| k | situação |
|---|---|
| 1 | roda — `horizonte_q_dias` = 1, igual às outras |
| 2 | **bloqueado** — `horizonte_q_dias` = 2 contra 1 das outras views |
| 3 | **bloqueado** — `horizonte_q_dias` = 3 contra 1 das outras views |
| 4 | **bloqueado** — `horizonte_q_dias` = 4 contra 1 das outras views |
| 5 | **bloqueado** — `horizonte_q_dias` = 5 contra 1 das outras views |

**Consequência, e ela é anterior a qualquer número:** a C só consegue conviver com as outras quatro views em **k = 1**. Para qualquer k ≥ 2 a entrada dela exige fechar a D4.1 antes — que é decisão de metodologia, não de implementação.


## Registro obrigatório da D22 — atribuição e concentração

Soma dos Δ DIÁRIOS contra a entrega de 4 views, e o que sobra dela tirando os três pregões de maior |Δ|.

| configuração | Σ dos Δ diários | sem os 3 maiores | acerto de sinal nos dias da view |
|---|---|---|---|
| + C (k = 1) | -4.11 pp | +0.37 pp | 40% (29/72) |

## Leitura (gerada)

- **A varredura mede 1 de 5 pontos da grade** — o resto está bloqueado pela D4.1. Uma grade incompleta por decisão aberta não é insumo de escolha de parâmetro; é o registro de que o parâmetro não pode ser escolhido ainda.
- **k = 1**: Δ de **-5.48 pp** contra a entrega de quatro views.
