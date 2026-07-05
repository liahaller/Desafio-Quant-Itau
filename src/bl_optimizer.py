"""Otimizador Black-Litterman — motor central (módulo do Felipe).

Implementa o BL padrão (He & Litterman, 1999):
  1. Prior de equilíbrio via reverse optimization: pi = delta * Sigma @ w_mkt
  2. Posterior combinando prior e views:
       mu_bl    = pi + tau*Sigma @ P.T @ inv(P @ tau*Sigma @ P.T + Omega) @ (Q - P @ pi)
       Sigma_bl = Sigma + M,  M = tau*Sigma - tau*Sigma @ P.T @ inv(...) @ P @ tau*Sigma
  3. Pesos mean-variance não restritos: w = inv(delta * Sigma) @ mu

Funções puras: recebem arrays, devolvem arrays. Nenhum dado ou parâmetro
hardcoded — Q e omega virão do bridge e do Ω reativo da Lia; Sigma e w_mkt
do pipeline do Paulo; tau e delta de decisão registrada (Decisoes_pendentes.md).

Interface proposta (a confirmar com Paulo e Lia):
  sigma  : ndarray (n, n) — covariância dos retornos dos n ativos
  w_mkt  : ndarray (n,)   — pesos de mercado (soma 1)
  P      : ndarray (k, n) — k views mapeadas nos ativos
  Q      : ndarray (k,)   — retorno esperado de cada view
  omega  : ndarray (k, k) — covariância da incerteza das views
  Ordem dos ativos: a mesma em todos os arrays, definida pelo dataset do Paulo.
"""

import numpy as np


def _check_shapes(sigma, w_mkt=None, P=None, Q=None, omega=None):
    """Valida dimensões para evitar broadcasting silencioso do numpy."""
    n = sigma.shape[0]
    if sigma.shape != (n, n):
        raise ValueError(f"sigma deve ser quadrada, recebeu {sigma.shape}")
    if w_mkt is not None and w_mkt.shape != (n,):
        raise ValueError(f"w_mkt deve ter shape ({n},), recebeu {w_mkt.shape}")
    if P is not None:
        k = P.shape[0]
        if P.shape != (k, n):
            raise ValueError(f"P deve ter shape (k, {n}), recebeu {P.shape}")
        if Q is not None and Q.shape != (k,):
            raise ValueError(f"Q deve ter shape ({k},), recebeu {Q.shape}")
        if omega is not None and omega.shape != (k, k):
            raise ValueError(f"omega deve ter shape ({k}, {k}), recebeu {omega.shape}")


def implied_equilibrium_returns(sigma, w_mkt, delta):
    """Retornos implícitos de equilíbrio (reverse optimization).

    pi_prior = delta * Sigma @ w_mkt — o retorno que faz a carteira de
    mercado ser ótima para aversão a risco delta.
    """
    _check_shapes(sigma, w_mkt=w_mkt)
    return delta * sigma @ w_mkt


def bl_posterior(pi_prior, sigma, tau, P, Q, omega):
    """Média e covariância posteriores do Black-Litterman.

    Retorna (mu_bl, sigma_bl). Com omega -> infinito o posterior volta ao
    prior; com omega -> 0 as views dominam (P @ mu_bl -> Q).
    """
    _check_shapes(sigma, P=P, Q=Q, omega=omega)
    tau_sigma = tau * sigma
    # A = P @ tau*Sigma @ P.T + Omega — incerteza total das views
    A = P @ tau_sigma @ P.T + omega
    mu_bl = pi_prior + tau_sigma @ P.T @ np.linalg.solve(A, Q - P @ pi_prior)
    M = tau_sigma - tau_sigma @ P.T @ np.linalg.solve(A, P @ tau_sigma)
    sigma_bl = sigma + M
    return mu_bl, sigma_bl


def optimal_weights(mu, sigma, delta):
    """Pesos mean-variance não restritos: w = inv(delta * Sigma) @ mu.

    O chamador escolhe qual Sigma passar (amostral ou posterior do BL) —
    ver TODO(DECISAO-8) em Decisoes_pendentes.md.
    """
    _check_shapes(sigma, w_mkt=mu)
    return np.linalg.solve(delta * sigma, mu)
