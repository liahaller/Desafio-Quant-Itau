# Camada tática v2 — a primeira rodada ligada desde a 12c

> Gerado por `scripts/camada_tatica_v2.py`. **Mede; não decide.** Nenhuma configuração é escolhida por este número: pela régua 28.0 o resultado não reprova candidata, e o **G4 é relatório, não portão** (item 12 da D28).

- sleeves ligadas: **M4 recessão EUA 2025** (k = 3, 5, 10) · **M9 Câmara** (k = 20)
- janela: **2025-02-10 a 2026-08-06** (374 pregões); teto de referência = **1**, no tilt (10a)
- tamanho pela âncora `inv(δΣ)·μ` da D16 — **sem `orcamento`**, zero parâmetro livre
- régua do Ω (Lia): **LIGADA nas DUAS pontas**, nível 1 (6q) — é a configuração da entrega. O Δ desta página mede a camada, e não a régua, porque ela é a mesma dos dois lados

## 1. O que a camada muda na ENTREGA

|   teto no tilt | excesso × SPY (sem)   | excesso × SPY (com)   | Δ        |   Σ|w| média (com) |   giro (com) |   breakeven bps (com) |
|---------------:|:----------------------|:----------------------|:---------|-------------------:|-------------:|----------------------:|
|              1 | +5.98 pp              | +3.04 pp              | -2.94 pp |              1.915 |        0.396 |                22.869 |
|              2 | +6.51 pp              | -0.24 pp              | -6.75 pp |              2.831 |        0.734 |                12.674 |
|              3 | +7.22 pp              | -1.68 pp              | -8.90 pp |              3.742 |        1.091 |                 9.146 |
|              5 | +4.17 pp              | +7.99 pp              | +3.82 pp |              5.521 |        1.66  |                 8.249 |

## 2. O G4 — a camada SOZINHA, no `dw` pedido

Antes de qualquer teto: é a P&L da estratégia isolada, não a sobra da disputa pelo teto com o tilt das views.

|   pregões ativos |   acumulado (composto) |   acumulado sem os 3 maiores em |valor| |   acerto de sinal |   maior dia |   pior dia |
|-----------------:|-----------------------:|----------------------------------------:|------------------:|------------:|-----------:|
|              327 |                 0.4261 |                                    0.64 |            0.5443 |      0.0715 |    -0.1126 |

**Σ|dw| que a camada PEDE:** mediana **2.54** · máximo **8.15** · pede mais que o teto inteiro em **80%** dos pregões ativos.

## Leitura

**No teto de referência a camada custa -2.94 pp de excesso.** Isso não a reprova: a régua 28.0 não contém resultado, e as duas sleeves passaram pelos quatro itens dela antes de o backtest rodar. O que o número faz é dimensionar o custo da decisão.

**A camada sozinha (G4) acumula +42.61 pp** em 327 pregões ativos, com acerto de sinal de 54%. Sem os 3 maiores dias em |valor| sobra +64.00 pp — o resultado **não** é um punhado de pregões, que é o vício que a 15h pegou numa view.

**A camada disputa o teto com as views, e é uma disputa desigual:** ela pede Σ|dw| mediano de **2.54** contra um teto de **1** para o tilt INTEIRO. Em mais da metade dos pregões ativos o pedido dela sozinho já não cabe, então o corte tira peso das views também — parte do Δ da seção 1 é isso, não a P&L da camada.

**E a grade de tetos deveria separar as duas coisas.** Se a camada perdesse por si, o Δ seria negativo em toda a grade; se perdesse por disputar o teto, melhoraria conforme o teto afrouxa. Medido: teto 1: -2.94 pp · teto 2: -6.75 pp · teto 3: -8.90 pp · teto 5: +3.82 pp.

🛑 **O Δ NÃO é monótono no teto, e isso derruba as duas leituras simples.** Ele piora até o teto 3 e só então vira. Um padrão assim não é *"a camada perde"* nem *"a camada só disputa espaço"*: o que muda com o teto é a MISTURA entre o tilt das views e o da camada, e ela não é linear porque o corte reescala os dois juntos. **Nenhuma linha desta grade é proposta** — ler o teto 5 como recomendação seria escolher configuração pelo resultado, que é o que a régua 28.0 barra.

⚠️ **O achado da rodada é a tensão entre os dois números.** A camada é positiva sozinha (+42.6 pp) e NEGATIVA quando somada (-2.94 pp). Não há contradição: com o teto no tilt, o corte reescala o tilt das views e o da camada JUNTOS, então entrar não é somar — é dividir um orçamento fixo de risco. A camada só melhora a entrega se render mais por unidade de Σ|w| do que o tilt que ela desloca, e nesta janela ela não rende.

**Isso é medição, não veredito.** A régua 28.0 admite as duas sleeves por mecanismo, e o dono já declarou que prejuízo não reprova. O que este parágrafo acrescenta é QUAL é o custo e de onde ele vem — insumo para a decisão de entregar a camada ligada ou desligada, que é do dono e não deste artefato.

⚠️ **O G4 é BRUTO de custo e sem teto.** Ele mede o `dw` pedido (Σ|dw| mediano 2.54), então não é o retorno de uma carteira executável — é o sinal da estratégia. O custo aparece na seção 1, onde o breakeven da entrega com a camada é de 22.9 bps por lado contra os 2 bps premissados.

**O que isto NÃO diz:** nada sobre admissão — as sleeves já foram admitidas pela D28, com base em G0/G1/G2/G3, no corte da amostra e, na M9, no teste de mercado irmão. E nada corrige as ~200 células da D27 para comparações múltiplas, que segue sendo a maior limitação declarada das duas.

