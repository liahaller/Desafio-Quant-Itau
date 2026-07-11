"""View 2.3 — Fed (surpresa de juros, Bernanke-Kuttner). Módulo do Felipe.

Fechada em reunião 2026-07-09 (decisões 3/4 desta view); espec completa em
`Informações_uteis/views/view_2.3_fed.md`. Família A com sensibilidade
ESTIMADA: β por regressão própria (event-study nos dias de FOMC, retorno
do ativo contra a surpresa à la Kuttner).

    surpresa = E_poly[Δtaxa] − E_FF[Δtaxa]           (bps)
    P[i]     = 2 · (β_i − β_SPY) / Σ_j |β_j − β_SPY|  (Σ|P| = 2, P[SPY] = 0)
    Q        = surpresa · Σ_i P[i] · β_i

Cascata de degradação (item 0 da espec) — só o lado do poly degrada; E_FF
sai SEMPRE do ZQ (contrato do mês posterior à reunião), como esperança em
bps, nunca probabilidade:
  1. PMF de buckets de decisão (−50bp, −25bp, 0, +25bp…) → E_poly = média.
  2. Só mercado binário → E_poly = p_poly × Δtaxa do evento (ex.: −25).
  3. Nenhum mercado de FOMC → view desativada (retorna None).

Segue o template estrutural da view 2.2 (`build_view(...) -> ViewResult |
None`, contrato em `views_common.py`, pré-processamento só via
`poly_preprocessing`).

Unidades: retornos e Q em fração decimal (0.008 = 0.8%); taxas/surpresa em
bps; logo β em fração/bp (ex.: −0.0008 = −0.08%/bp, comparável à literatura
B-K no sanity check). A janela amostral e a frequência da regressão são
decisão humana (pendência da espec) — entram como dado, nunca default aqui.
"""

import numpy as np

from poly_preprocessing import favorite_longshot, normalize_probs, pmf_mean
from views_common import P_from_betas, ViewResult

# Centro da linha P (espec item 4: excesso sobre o mercado) — parametrizado
# só para não hardcodar ticker na lógica; o default É a decisão.
MARKET_ASSET = "SPY"


def estimate_betas(event_returns, surprises_bps):
    """β por ativo via event-study: OLS com intercepto do retorno do ativo
    nos dias de FOMC contra a surpresa à la Kuttner (variação do FF future
    no dia do anúncio, em bps) — NUNCA contra o Δtaxa bruto (espec item 3).

    event_returns : (m, n) — retornos (fração decimal) dos n ativos nos m
                    dias de FOMC da janela decidida pelo chamador.
    surprises_bps : (m,) — surpresa realizada de cada dia, em bps.
    Retorna β (n,) em fração/bp. Literatura B-K = sanity check, não fonte.
    """
    R = np.asarray(event_returns, dtype=float)
    s = np.asarray(surprises_bps, dtype=float)
    if R.ndim != 2 or s.shape != (R.shape[0],):
        raise ValueError(f"shapes incompatíveis: returns {R.shape}, surpresas {s.shape}")
    if R.shape[0] < 2:
        raise ValueError("regressão exige pelo menos 2 dias de FOMC")
    s_c = s - s.mean()
    ss = s_c @ s_c
    if ss <= 0:
        raise ValueError("surpresas sem variância — β não identificável")
    return (R - R.mean(axis=0)).T @ s_c / ss


# P_from_betas (espec item 4) mudou-se para views_common.py — é a mesma
# construção nas views 2.3, 2.4 e 3.1; importada acima para manter a API.


def build_view(assets, e_ff_bps, betas,
               bucket_probs=None, bucket_deltas_bps=None,
               binary_prob=None, binary_delta_bps=None,
               fl_correction=favorite_longshot, market_asset=MARKET_ASSET):
    """Monta a view 2.3 para uma data de rebalanceamento.

    Recebe só dados até a data (quem corta é o backtest — sem lookahead).
    Segue a cascata: PMF > binário > None (desativada).

    Parâmetros:
      assets           : list[str] — universo na ordem do dataset do Paulo.
      e_ff_bps         : float — E_FF[Δtaxa] em bps, extraído do ZQ
                         (contrato do mês posterior) a montante.
      betas            : (n,) — β de estimate_betas, fração/bp.
      bucket_probs     : probs CRUAS dos buckets de FOMC (ou None).
      bucket_deltas_bps: Δtaxa de cada bucket em bps (aberto já resolvido
                         via open_bucket_value — decisão 11b).
      binary_prob      : tupla (p_sim, p_nao) CRUA do binário (ou None).
      binary_delta_bps : Δtaxa que o binário resolve (ex.: −25 para corte).
      fl_correction    : correção de favorite-longshot (default: stub 11a).

    Retorna ViewResult (P, Q, diagnostics) ou None se não há mercado de FOMC.
    """
    if bucket_probs is not None:
        e_poly_bps = pmf_mean(bucket_probs, bucket_deltas_bps, fl_correction)
        caminho = "pmf"
    elif binary_prob is not None:
        if binary_delta_bps is None:
            raise ValueError("fallback binário exige binary_delta_bps (ex.: -25 para corte)")
        p_yes = float(fl_correction(normalize_probs([binary_prob[0], binary_prob[1]]))[0])
        e_poly_bps = p_yes * binary_delta_bps
        caminho = "binario"
    else:
        return None  # cascata item 0: sem mercado de FOMC -> view desativada

    surpresa_bps = e_poly_bps - e_ff_bps
    P = P_from_betas(betas, list(assets), market_asset)
    betas = np.asarray(betas, dtype=float)
    Q = float(surpresa_bps * (P @ betas))
    return ViewResult(P=P, Q=Q, diagnostics={
        "view": "2.3_fed",
        "caminho": caminho,
        "e_poly_bps": e_poly_bps,
        "e_ff_bps": e_ff_bps,
        "surpresa_bps": surpresa_bps,
        "sum_P_beta": float(P @ betas),  # ∝ dispersão dos βs (espec item 5)
    })
