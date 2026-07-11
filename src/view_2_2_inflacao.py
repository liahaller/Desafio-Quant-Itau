"""View 2.2 — Inflação (par TIP - TLT). Módulo do Felipe.

Fechada em reunião 2026-07-09 (decisões 3/4 desta view); espec completa em
`Informações_uteis/views/view_2.2_inflacao.md`. Exceção à Família A: sem
regressão — beta = duration do breakeven de 10 anos (benchmark T10YIE do
FRED, acoplado à duration; alterar um exige alterar o outro).

    Q = duration * (E_poly[CPI] - breakeven_10a)
    P = +1 TIP / -1 TLT  (Sigma|P| = 2)

Cascata de degradação (item 0 da espec):
  1. PMF de buckets de CPI disponível -> E_poly = média da PMF.
  2. Só mercado binário -> normal deslocada com vol histórica do CPI:
     E_poly = média que faz P(CPI > threshold) = prob_poly.
  3. Nenhum mercado de CPI -> view desativada (retorna None).

Unidades: TODAS as grandezas de inflação (valores dos buckets, threshold,
breakeven, vol) em fração decimal (0.037 = 3.7%). Q sai em fração decimal,
consistente com os retornos do BL.

Pré-processamento (decisão 9): a view normaliza as probs cruas e aplica a
correção de favorite-longshot (stub até a decisão 11a — a view FALHA ALTO
até lá; para testes sintéticos injeta-se `fl_correction` identidade). O
valor do bucket aberto (decisão 11b) é resolvido pelo CHAMADOR via
`poly_preprocessing.open_bucket_value` antes de montar `bucket_values`.
"""

import numpy as np
from scipy.stats import norm

from poly_preprocessing import favorite_longshot, normalize_probs, pmf_mean
from views_common import ViewResult

# Par da view (decisão 1 / espec da 2.2) — parametrizado só para não
# hardcodar ticker na lógica; o default É a decisão.
LONG_ASSET = "TIP"
SHORT_ASSET = "TLT"


def _pair_P(assets, long_asset, short_asset):
    """Linha P do par +1/-1 alinhada à lista de ativos (Sigma|P| = 2)."""
    P = np.zeros(len(assets))
    P[assets.index(long_asset)] = 1.0
    P[assets.index(short_asset)] = -1.0
    return P


def expected_inflation_from_binary(prob_yes, prob_no, threshold, cpi_vol,
                                   fl_correction=favorite_longshot):
    """Fallback binário: normal deslocada com vol histórica do CPI.

    Encontra a média mu tal que P(CPI > threshold) = p_poly com
    CPI ~ N(mu, cpi_vol):  mu = threshold + cpi_vol * Phi^{-1}(p).
    """
    if cpi_vol <= 0:
        raise ValueError("cpi_vol deve ser positiva")
    p_yes = float(fl_correction(normalize_probs([prob_yes, prob_no]))[0])
    if not 0.0 < p_yes < 1.0:
        raise ValueError(f"prob corrigida fora de (0, 1): {p_yes}")
    return threshold + cpi_vol * norm.ppf(p_yes)


def build_view(assets, breakeven_10y, duration,
               bucket_probs=None, bucket_values=None,
               binary_prob=None, binary_threshold=None, cpi_vol=None,
               fl_correction=favorite_longshot,
               long_asset=LONG_ASSET, short_asset=SHORT_ASSET):
    """Monta a view 2.2 para uma data de rebalanceamento.

    Recebe só dados até a data (quem corta é o backtest — sem lookahead
    estrutural). Segue a cascata: PMF > binário > None (desativada).

    Parâmetros:
      assets           : list[str] — universo na ordem do dataset do Paulo.
      breakeven_10y    : float — T10YIE na data, fração decimal.
      duration         : float — duration do breakeven 10a (~8; valor vem
                         de decisão registrada, não default de código).
      bucket_probs     : probs CRUAS dos buckets de CPI (ou None).
      bucket_values    : valor de cada bucket (aberto já resolvido — 11b).
      binary_prob      : tupla (p_sim, p_nao) CRUA do mercado binário (ou None).
      binary_threshold : threshold X do binário "CPI > X".
      cpi_vol          : vol histórica do CPI para o fallback.
      fl_correction    : correção de favorite-longshot (default: stub 11a).

    Retorna ViewResult (P, Q, diagnostics) ou None se não há mercado de CPI.
    """
    if bucket_probs is not None:
        e_poly = pmf_mean(bucket_probs, bucket_values, fl_correction)
        caminho = "pmf"
    elif binary_prob is not None:
        if binary_threshold is None or cpi_vol is None:
            raise ValueError("fallback binário exige binary_threshold e cpi_vol")
        e_poly = expected_inflation_from_binary(binary_prob[0], binary_prob[1],
                                                binary_threshold, cpi_vol, fl_correction)
        caminho = "binario"
    else:
        return None  # cascata item 0: sem mercado de CPI -> view desativada

    divergencia = e_poly - breakeven_10y
    Q = duration * divergencia
    P = _pair_P(list(assets), long_asset, short_asset)
    return ViewResult(P=P, Q=float(Q), diagnostics={
        "view": "2.2_inflacao",
        "caminho": caminho,
        "e_poly": e_poly,
        "breakeven_10y": breakeven_10y,
        "divergencia": divergencia,
        "duration": duration,
    })
