"""View G (CANDIDATA-RESERVA) — Legislação fiscal. Módulo do Felipe.

⚠️ STATUS: candidata-RESERVA — a ENTRADA NA CARTEIRA é decisão de reunião
ainda não tomada, e a G já nasce reserva (só sobe se a reunião derrubar
outra candidata; β mais frágil do lote — poucos episódios). O código
existe por instrução do Felipe (sessão 2026-07-11); implementar não fecha
a decisão. Espec: `Informações_uteis/views/view_G_fiscal.md`.

Template poly-defasado (corpo compartilhado em
`views_common.lagged_poly_view` — matemática idêntica à 2.4):

    Q = (Σ P[i]·β_i) × (p_t − p_{t−k})

Específico desta view (decidido em sessão 2026-07-10):
  - Mercado designado: legislação TRIBUTÁRIA (Q1-A, ex.: família OBBB
    2025 "passa até X?"); teto da dívida / X-date como robustness.
    Shutdown está FORA como evento (sem efeito documentado em equities).
    UM evento por vez; cascata liga/desliga na janela.
  - β por regressão própria POR MERCADO/EVENTO; âncora WZZ só sanity
    check a posteriori no evento tributário. No teto da dívida o TLT NÃO
    tem sinal a priori (paradoxo do flight-to-quality para dentro dos
    próprios Treasuries) — reportar o sinal que a regressão der.
  - Backtest: desligar antes do 1º tick de resolução (votação final);
    dias sem trade.

Unidades: p em fração; β em fração de retorno por unidade de
probabilidade; Q em fração decimal, acumulado em k dias.
"""

from views_common import lagged_poly_view

MARKET_ASSET = "SPY"


def build_view(assets, betas, k, p_series=None, market_asset=MARKET_ASSET):
    """Monta a view G para uma data de rebalanceamento (template
    poly-defasado — ver docstring do módulo e views_common.lagged_poly_view).
    p_series = série p(aprovação) do mercado DESIGNADO, já pré-processada;
    None = sem mercado -> view desativada."""
    return lagged_poly_view("G_fiscal", assets, betas, k, p_series, market_asset)
