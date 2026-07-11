"""View 3.1 — Recessão (poly vs curva de juros). Módulo do Felipe.

Fechada CONDICIONALMENTE em sessão 2026-07-10 (condições: mercado de
recessão com bid/ask histórico no CLOB; horizonte pendente de reunião);
espec completa em `Informações_uteis/views/view_3.1_recessao.md`. Família A
com os DOIS lados em probabilidade do mesmo evento — divergência direta.

    divergência = p_poly − p_curva       (pontos de probabilidade)
    P[i]        = 2·(β_i − β_SPY)/Σ|β_j − β_SPY|   (views_common)
    Q           = (Σ P[i]·β_i) × (p_poly − p_curva)

Segue o template estrutural da view 2.2; herda da 2.4 a maquinaria do β
(lag_regression/full_absorption_beta em views_common, teste de defasagem
obrigatório, sem lookahead) e a regra de ativação/desligamento (liquidez é
papel do Ω, sem limiar próprio; desliga no último dia antes do primeiro
tick de resolução — responsabilidade do backtest). p_poly chega PRONTO
(binary_prob_series — mesma série da regressão do β); o favorite-longshot
é RELEVANTE aqui (recessão vive em p baixa, região de viés máximo) e o
stub da decisão 11a falha alto a montante.

O benchmark (curva) entra SÓ no Q, nunca na regressão do β (espec item 3).

Unidades: p em fração [0,1]; β em fração de retorno por ponto de
probabilidade; Q em fração decimal, com horizonte herdado dos k dias do β
de absorção plena — mesma pendência transversal de reconciliação com Σ/π
da 2.4.
"""

import numpy as np
from scipy.stats import norm

from views_common import P_from_betas, ViewResult

# Centro da linha P — o default É a decisão (espelha a 2.3, espec item 4).
MARKET_ASSET = "SPY"


def p_curve_probit(spread, alpha, beta_spread):
    """Probabilidade de recessão implícita na curva: probit clássico
    Estrella-Mishkin / NY Fed sobre o spread 10a−3m (DGS10 − DTB3, FRED):

        p_curva = Phi(alpha + beta_spread * spread)

    Coeficientes PUBLICADOS entram como argumento — a referência exata
    (paper/tabela do NY Fed) é pendência da espec e vem de decisão
    registrada, nunca inventada aqui. Nenhuma estimação nossa (espec item 2).
    `spread` em pontos percentuais, na convenção da tabela usada.
    """
    return float(norm.cdf(alpha + beta_spread * spread))


def build_view(assets, betas, k, p_poly=None, p_curva=None, market_asset=MARKET_ASSET):
    """Monta a view 3.1 para uma data de rebalanceamento.

    Parâmetros:
      assets  : list[str] — universo na ordem do dataset do Paulo.
      betas   : (n,) — β de absorção plena (views_common), fração/ponto de
                probabilidade, estimados sem lookahead pelo chamador.
      k       : defasagem usada no β de absorção plena — define o horizonte
                do Q (diagnostics); mesma pendência de critério da 2.4.
      p_poly  : p de recessão na data (binary_prob_series[-1]); None = não
                existe mercado de recessão (view desativada).
      p_curva : p implícita na curva na data (p_curve_probit) — obrigatória
                quando há mercado (sem poly não há view; sem curva não há
                benchmark).

    Retorna ViewResult ou None (cascata do item 0 da espec).
    """
    if p_poly is None:
        return None  # sem mercado de recessão -> view desativada (espec item 0)

    if p_curva is None:
        raise ValueError("p_curva é o benchmark da divergência — obrigatória quando a view está ativa")
    for nome, p in (("p_poly", p_poly), ("p_curva", p_curva)):
        if not 0.0 <= p <= 1.0:
            raise ValueError(f"{nome} fora de [0, 1]: {p}")

    divergencia = float(p_poly - p_curva)
    P = P_from_betas(betas, list(assets), market_asset)
    betas = np.asarray(betas, dtype=float)
    Q = float((P @ betas) * divergencia)
    return ViewResult(P=P, Q=Q, diagnostics={
        "view": "3.1_recessao",
        "caminho": "binario",
        "p_poly": float(p_poly),
        "p_curva": float(p_curva),
        "divergencia": divergencia,
        "horizonte_q_dias": k,  # Q herda o horizonte do β de absorção plena
        "sum_P_beta": float(P @ betas),
    })
