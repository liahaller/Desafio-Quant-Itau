"""View E (CANDIDATA) — Tarifas / política comercial. Módulo do Felipe.

⚠️ STATUS: candidata — a ENTRADA NA CARTEIRA é decisão de reunião ainda não
tomada. O código existe por instrução do Felipe (sessão 2026-07-11);
implementar não fecha a decisão. Espec:
`Informações_uteis/views/view_E_tarifas.md`.

Template poly-defasado (corpo compartilhado em
`views_common.lagged_poly_view` — matemática idêntica à 2.4):

    Q = (Σ P[i]·β_i) × (p_t − p_{t−k})

Específico desta view (decidido em sessão 2026-07-10):
  - Mercado designado: família EUA×China (Q1-A, primário do v1);
    recíprocas/"Liberation Day" como robustness. UM evento por vez;
    eventos episódicos — a cascata liga/desliga na janela.
  - β aceito com FRAGILIDADE DOCUMENTADA (Q2): episódios concentrados em
    2025, janela curta — sem condição extra de amostra (o limiar de volume
    da 2.4 cobre a estimabilidade).
  - β por regressão própria POR MERCADO/FAMÍLIA (lag_regression /
    full_absorption_beta); âncoras AGKW e TPU só sanity check a
    posteriori. Obrigação da espec: conferir o sinal POSITIVO esperado do
    TLT (flight to safety) — se a regressão der negativo, reportar antes
    de usar (o β manda, mas a divergência com a âncora fica registrada).
  - Backtest: desligar antes do 1º tick de resolução; dias sem trade.

Unidades: p em fração; β em fração de retorno por unidade de
probabilidade; Q em fração decimal, acumulado em k dias.
"""

from views_common import lagged_poly_view

MARKET_ASSET = "SPY"


def build_view(assets, betas, k, p_series=None, market_asset=MARKET_ASSET):
    """Monta a view E para uma data de rebalanceamento (template
    poly-defasado — ver docstring do módulo e views_common.lagged_poly_view).
    p_series = série p(evento tarifário) do mercado DESIGNADO, já
    pré-processada; None = sem mercado -> view desativada."""
    return lagged_poly_view("E_tarifas", assets, betas, k, p_series, market_asset)
