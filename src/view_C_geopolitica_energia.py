"""View C (CANDIDATA) — Geopolítica → energia. Módulo do Felipe.

⚠️ STATUS: candidata — a ENTRADA NA CARTEIRA é decisão de reunião ainda não
tomada. O código existe por instrução do Felipe (sessão 2026-07-11);
implementar não fecha a decisão. Espec:
`Informações_uteis/views/view_C_geopolitica_energia.md`.

Terceira view do template poly-defasado (corpo compartilhado em
`views_common.lagged_poly_view` — matemática idêntica à 2.4):

    Q = (Σ P[i]·β_i) × (p_t − p_{t−k})

Específico desta view (documentado na espec, decidido por delegação):
  - Mercado designado: ação militar EUA/Israel × Irã (primário do v1);
    cessar-fogo Rússia × Ucrânia como robustness (sinal invertido — o β
    por mercado resolve sozinho). UM evento por vez.
  - Eventos episódicos e recorrentes: a cascata liga/desliga várias vezes
    na janela (diferença vs 2.4).
  - Favorite-longshot RELEVANTE (p baixa, ~0,1–0,4 — como na 3.1); série
    via binary_prob_series (a mesma da regressão do β).
  - β por regressão própria POR MERCADO (lag_regression /
    full_absorption_beta); âncoras Kilian-Park e Caldara-Iacoviello só
    como sanity check a posteriori, nunca invertem o β.
  - Backtest: desligar antes do 1º tick de resolução; dias sem trade;
    rolagem entre mercados de deadline (pendência compartilhada com 3.1/B).

Unidades: p em fração; β em fração de retorno por unidade de
probabilidade; Q em fração decimal, acumulado em k dias.
"""

from views_common import lagged_poly_view

MARKET_ASSET = "SPY"


def build_view(assets, betas, k, p_series=None, market_asset=MARKET_ASSET):
    """Monta a view C para uma data de rebalanceamento (template
    poly-defasado — ver docstring do módulo e views_common.lagged_poly_view).
    p_series = série p(evento) do mercado DESIGNADO do período, já
    pré-processada; None = sem mercado -> view desativada."""
    return lagged_poly_view("C_geopolitica_energia", assets, betas, k, p_series, market_asset)
