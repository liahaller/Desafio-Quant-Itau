"""View 2.4 — Eleitoral (cross-section setorial vs p(Trump)). Módulo do Felipe.

Fechada CONDICIONALMENTE em reunião 2026-07-09 (condição: bid/ask histórico
no CLOB para o midpoint); espec completa em
`Informações_uteis/views/view_2.4_eleitoral.md`. Segunda exceção à Família
A: não há benchmark externo — o benchmark é o PRÓPRIO poly defasado.

    divergência = p_t − p_{t−k}          (fração de probabilidade)
    P[i]        = 2·(β_i − β_SPY)/Σ|β_j − β_SPY|   (views_common)
    Q           = (Σ P[i]·β_i) × (p_t − p_{t−k})

Segue o template estrutural da view 2.2. Diferença deliberada: a série
p(Trump) chega PRONTA (via `poly_preprocessing.binary_prob_series`, a
mesma série usada na regressão do β — espec item 2b: a parte linear da
correção FL é absorvida pelo β justamente porque as duas usam a mesma
transformação). O stub da decisão 11a continua falhando alto — só que a
montante, na construção da série.

β: regressão própria (maquinaria em `views_common.lag_regression` /
`full_absorption_beta`) — β de absorção plena dos lags 0…k; janela
expandida encerrada em t−1 do rebalanceamento (sem lookahead) é
responsabilidade do chamador, assim como o teste de defasagem obrigatório.
Literatura (Pástor-Veronesi) só sanity check a posteriori; nunca inverte β.

⚠️ Responsabilidades do BACKTEST (não desta função, que só vê dados até t):
  - Desligar a view no último dia ANTES do primeiro tick de resolução
    (5–6/nov/2024: Δp = +0,4 fabricaria alfa — espec item 0).
  - Reportar dias sem trade da janela (item 2c) — dado que a view não vê.
  - Acoplamento k ↔ frequência de rebalanceamento (espec item 4).

Unidades: p em fração [0,1]; β em fração de retorno por unidade de
probabilidade; Q em fração decimal, ACUMULADO EM k DIAS — reconciliar com
o horizonte de Σ/π é pendência transversal (espec item 6).
"""

from views_common import lagged_poly_view

# Centro da linha P — parametrizado só para não hardcodar ticker na lógica;
# o default É a decisão (consistência com a 2.3, espec item 5a).
MARKET_ASSET = "SPY"


def build_view(assets, betas, k, p_series=None, market_asset=MARKET_ASSET):
    """Monta a view 2.4 para uma data de rebalanceamento.

    Parâmetros:
      assets   : list[str] — universo na ordem do dataset do Paulo.
      betas    : (n,) — β de absorção plena (views_common), fração/unidade
                 de probabilidade, estimados sem lookahead pelo chamador.
      k        : defasagem estimada pelo teste de lags (critério de escolha
                 do k = decisão humana pendente). k ≥ 1.
      p_series : série p(Trump) já pré-processada (binary_prob_series),
                 até a data do rebalanceamento inclusive; None = não existe
                 mercado (view desativada).

    Retorna ViewResult ou None. k ≈ 0 FALHA ALTO: é condição permanente
    (a tese de defasagem cai), não a cascata episódica — o que fazer
    (fallback contemporâneo vs sair do v1) é decisão de reunião não tomada.

    O corpo é o template compartilhado (views_common.lagged_poly_view) —
    o mesmo das views C/E/G.
    """
    return lagged_poly_view("2.4_eleitoral", assets, betas, k, p_series, market_asset)
