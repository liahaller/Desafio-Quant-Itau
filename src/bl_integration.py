"""Integração final: ViewResults -> P/Q empilhados -> pesos BL. Módulo do Felipe.

O elo entre as views (view_*.py), o Ω reativo (Lia) e o otimizador
(`bl_optimizer.py`). Duas funções puras:

  - stack_views  : filtra as views desativadas (None) e empilha as ativas
                   em P (k, n) e Q (k,), preservando a lista de
                   diagnostics NA MESMA ORDEM — é ela que a Lia usa para
                   montar o Ω (k, k) alinhado.
  - bl_weights_from_views : ponta a ponta de um rebalanceamento:
                   prior de equilíbrio -> posterior com as views ativas ->
                   pesos com Σ AMOSTRAL e sem restrições (decisão 8).
                   Sem nenhuma view ativa, devolve exatamente w_mkt
                   (caso neutro da decisão 8 — o BL fica no prior).

Quais views entram na lista é decisão de quem chama (o backtest): as
estruturais 2.2/2.3/2.4/3.1 são as decididas; B/C/E/G são CANDIDATAS —
entrada na carteira pendente de reunião. τ e δ vêm de decisão registrada.

⚠️ Pendência transversal ainda aberta (especs 2.4/3.1/C/E/G): o Q das
views poly-defasadas é retorno ACUMULADO em k dias (`horizonte_q_dias`
nos diagnostics) e Σ/π são diários — a reconciliação de horizonte precisa
fechar antes do backtest misturar essas views com as diárias.
"""

import numpy as np

from bl_optimizer import bl_posterior, implied_equilibrium_returns, optimal_weights


def stack_views(view_results, n_assets):
    """Empilha os ViewResult ativos em (P, Q, diagnostics).

    view_results : lista de ViewResult | None (None = view desativada —
                   simplesmente não entra, não é falha).
    n_assets     : nº de ativos do universo (valida o alinhamento de cada P).

    Retorna (P (k, n), Q (k,), diagnostics list) com k = nº de views
    ativas, na ordem da lista de entrada; ou (None, None, []) se nenhuma
    view está ativa. O Ω da Lia deve ser (k, k) nesta MESMA ordem.
    """
    active = [r for r in view_results if r is not None]
    if not active:
        return None, None, []
    for r in active:
        if np.asarray(r.P).shape != (n_assets,):
            raise ValueError(
                f"P da view {r.diagnostics.get('view', '?')} não alinha com o universo: "
                f"{np.asarray(r.P).shape} vs ({n_assets},)"
            )
    P = np.vstack([np.asarray(r.P, dtype=float) for r in active])
    Q = np.array([r.Q for r in active], dtype=float)
    return P, Q, [r.diagnostics for r in active]


def bl_weights_from_views(sigma, w_mkt, tau, delta, view_results, omega=None):
    """Pesos de um rebalanceamento, ponta a ponta.

    sigma, w_mkt : covariância amostral e pesos de mercado (pipeline do Paulo).
    tau, delta   : parâmetros do BL — de decisão registrada, nunca default.
    view_results : lista de ViewResult | None (saída dos build_view).
    omega        : (k, k) do Ω reativo da Lia, alinhado às views ATIVAS na
                   ordem de stack_views; obrigatório se houver view ativa.

    Retorna (w, info) — w (n,) pesos irrestritos com Σ amostral (decisão
    8); info = dict com P/Q/diagnostics empilhados (auditoria/relatório).
    Sem view ativa: w = w_mkt exato (caso neutro da decisão 8).
    """
    sigma = np.asarray(sigma, dtype=float)
    w_mkt = np.asarray(w_mkt, dtype=float)
    P, Q, diagnostics = stack_views(view_results, n_assets=w_mkt.shape[0])

    pi_prior = implied_equilibrium_returns(sigma, w_mkt, delta)
    if P is None:
        mu = pi_prior  # BL no prior -> optimal_weights devolve w_mkt exato
    else:
        if omega is None:
            raise ValueError("omega (Ω reativo da Lia) é obrigatório quando há view ativa")
        mu, _ = bl_posterior(pi_prior, sigma, tau, P, Q, np.asarray(omega, dtype=float))
    w = optimal_weights(mu, sigma, delta)  # Σ AMOSTRAL, irrestrito (decisão 8)
    return w, {"P": P, "Q": Q, "diagnostics": diagnostics, "pi_prior": pi_prior}
