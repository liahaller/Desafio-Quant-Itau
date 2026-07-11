"""Contrato de saída comum das views (módulo do Felipe).

Definido em sessão 2026-07-11: a ENTRADA é livre por view (cada uma tem
insumos próprios — PMF+FRED na 2.2, ZQ na 2.3, histórico defasado na
2.4/3.1); a SAÍDA é sempre a mesma:

  build_view(...) -> ViewResult | None

  - ViewResult : a view está ativa; P e Q prontos para empilhar no BL.
  - None       : view desativada (ex.: sem mercado no período, k ~ 0).
                 Não é falha — a integração simplesmente não empilha.

Convenções:
  - P     : ndarray (n,) alinhado à lista `assets` recebida pela view,
            na convenção Sigma|P| = 2 (decisão 4).
  - Q     : float, retorno esperado "lado comprado - lado vendido",
            em fração decimal (0.04 = 4%), mesma unidade dos retornos do BL.
  - diagnostics : dict livre com os insumos crus para o Omega reativo da
            Lia (divergência, caminho de degradação, dias sem trade...).
            Formato não travado — decisão 6 aberta. Interface a confirmar
            com a Lia.

Além do contrato, este arquivo hospeda a matemática COMPARTILHADA entre
views (mesma lógica do módulo da decisão 9 para o pré-processamento):
  - P_from_betas         : linha P determinística a partir do vetor β
                           (espec 2.3 item 4; espelhada por 2.4 e 3.1).
  - lag_regression       : "maquinaria da 2.4" (espec 2.4 itens 3/4;
  - full_absorption_beta   reusada pela 3.1) — regressão de lags
                           distribuídos e β de absorção plena.
  - lagged_poly_view     : corpo do template poly-defasado
                           (Q = ΣP·β × (p_t − p_{t−k})) — o mesmo nas
                           views 2.4, C, E e G; cada módulo delega.
"""

from typing import NamedTuple

import numpy as np


class ViewResult(NamedTuple):
    P: np.ndarray
    Q: float
    diagnostics: dict


def P_from_betas(betas, assets, market_asset="SPY"):
    """Linha P determinística a partir do vetor β (nunca construída à mão):
    P[i] = 2·(β_i − β_SPY)/Σ|β_j − β_SPY|.

    Convenção Σ|P| = 2 (decisão 4); P[market_asset] = 0 exato (β em excesso
    ao mercado). Acoplamento documentado nas especs (2.3 item 4, 3.1 item 4,
    2.4 item 5): o centro β_SPY só existe porque o β vem de regressão
    própria — se a origem do β mudar, P muda junto. Obrigação da 2.4 (item
    5a): medir ΣP empiricamente; se o componente direcional não for
    intencional, trocar a centragem de TODAS as views juntas, nunca de uma.
    """
    b = np.asarray(betas, dtype=float)
    if b.shape != (len(assets),):
        raise ValueError(f"betas deve alinhar com assets: {b.shape} vs {len(assets)}")
    excess = b - b[list(assets).index(market_asset)]
    denom = np.abs(excess).sum()
    if denom == 0:
        raise ValueError("βs sem dispersão em torno do mercado — P indefinido (view sem conteúdo)")
    return 2.0 * excess / denom


def lag_regression(returns, dp, k_max):
    """Regressão de lags distribuídos (maquinaria da 2.4, espec itens 3/4):
    r_i(t) = a_i + Σ_{k=0}^{k_max} c_{k,i} · Δp(t−k), OLS conjunta.

    returns : (T, n) retornos diários dos n ativos, alinhados a dp.
    dp      : (T,) Δp diário do poly (série já pré-processada — midpoint/
              normalização/FL via poly_preprocessing; a MESMA série usada
              depois no build_view, para o β absorver a parte linear da
              correção).
    Devolve coefs (k_max+1, n) — linha k = coeficiente do lag k. O CRITÉRIO
    de escolher k a partir do perfil é decisão humana (pendência das especs
    2.4/3.1); esta função só entrega o perfil completo. Janela amostral e
    fim em t−1 do rebalanceamento (sem lookahead) são responsabilidade do
    chamador.
    """
    R = np.asarray(returns, dtype=float)
    dp = np.asarray(dp, dtype=float)
    if R.ndim != 2 or dp.shape != (R.shape[0],):
        raise ValueError(f"shapes incompatíveis: returns {R.shape}, dp {dp.shape}")
    T = dp.shape[0]
    m = T - k_max
    if m < k_max + 3:  # nº de linhas < nº de parâmetros (+1 de folga)
        raise ValueError(f"amostra insuficiente para k_max={k_max}: {m} linhas utilizáveis")
    X = np.column_stack([np.ones(m)] + [dp[k_max - k: T - k] for k in range(k_max + 1)])
    coefs, _, rank, _ = np.linalg.lstsq(X, R[k_max:], rcond=None)
    if rank < X.shape[1]:
        raise ValueError("lags colineares — perfil não identificável")
    return coefs[1:]


def lagged_poly_view(view_name, assets, betas, k, p_series=None, market_asset="SPY"):
    """Corpo do template poly-defasado (benchmark = o próprio poly defasado):

        divergência = p_t − p_{t−k}
        Q           = (Σ P[i]·β_i) × divergência

    Idêntico nas views 2.4 (eleitoral), C (geopolítica), E (tarifas) e
    G (fiscal) — cada módulo de view delega para cá com seu `view_name` e
    documenta no próprio docstring o mercado designado e as
    responsabilidades do backtest (desligar antes do 1º tick de resolução,
    dias sem trade, acoplamento k ↔ rebalance).

    `p_series` já pré-processada (poly_preprocessing.binary_prob_series —
    a MESMA série da regressão do β); None = sem mercado -> view
    desativada. k ≈ 0 FALHA ALTO: condição permanente (a tese de defasagem
    cai) — fallback contemporâneo vs sair do v1 é pendência de reunião.
    Q em fração decimal, ACUMULADO EM k DIAS (pendência transversal de
    reconciliação com Σ/π).
    """
    if p_series is None:
        return None  # sem mercado designado -> view desativada (cascata item 0)

    if k < 1:
        raise NotImplementedError(
            "k ~ 0: sem defasagem não há tese — fallback contemporâneo vs sair do v1 "
            "é pendência de reunião (espec 2.4, item 4; compartilhada por C/E/G)"
        )
    p = np.asarray(p_series, dtype=float)
    if p.ndim != 1 or p.shape[0] < k + 1:
        raise ValueError(f"p_series precisa de pelo menos k+1={k + 1} pontos, tem {p.shape}")

    p_t = float(p[-1])
    p_t_menos_k = float(p[-1 - k])
    divergencia = p_t - p_t_menos_k
    P = P_from_betas(betas, list(assets), market_asset)
    betas = np.asarray(betas, dtype=float)
    Q = float((P @ betas) * divergencia)
    return ViewResult(P=P, Q=Q, diagnostics={
        "view": view_name,
        "caminho": "binario",
        "p_t": p_t,
        "p_t_menos_k": p_t_menos_k,
        "divergencia": divergencia,
        "k": k,
        "horizonte_q_dias": k,  # Q é retorno acumulado de k dias
        "sum_P_beta": float(P @ betas),
    })


def full_absorption_beta(lag_coefs, k):
    """β de absorção plena: soma dos coeficientes dos lags 0…k (resposta
    cumulativa) do perfil devolvido por lag_regression. Premissa embutida
    (espec 2.4 item 6): resposta concentrada num spike no lag k — se o
    perfil for distribuído, a fórmula do Q superconta; o perfil decide.
    """
    lag_coefs = np.asarray(lag_coefs, dtype=float)
    if not 0 <= k < lag_coefs.shape[0]:
        raise ValueError(f"k={k} fora do perfil de {lag_coefs.shape[0]} lags")
    return lag_coefs[: k + 1].sum(axis=0)
