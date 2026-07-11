"""View B (CANDIDATA) — Trajetória do Fed (taxa de fim de ano). Módulo do Felipe.

⚠️ STATUS: candidata — a ENTRADA NA CARTEIRA é decisão de reunião ainda não
tomada. O código existe por instrução do Felipe (sessão 2026-07-11) para a
integração ficar pronta; implementar não fecha a decisão. Espec:
`Informações_uteis/views/view_B_trajetoria_fed.md`.

Espelha a 2.3 com outro par de instrumentos — a pergunta longa ("onde a
taxa termina o ano?"):

    surpresa_caminho = E_poly[taxa_fim_de_ano] − E_ZQdez[taxa]   (bps)
    P                = idêntico à 2.3 (β REUSADOS da 2.3 — espec item 3/4)
    Q                = surpresa_caminho · Σ P[i]·β_i

Cascata (item 0 — o lado do ZQ de dezembro nunca degrada):
  1. PMF de buckets (nº de cortes / taxa de fim de ano) → E_poly = média.
  2. Só binário ("corte até dezembro?") → E_poly = taxa_atual + p·(−25bp).
  3. Nenhum mercado de trajetória → view desativada (None).

Premissa documentada (espec item 3, confirmação de reunião pendente): a
reação por bp de surpresa de CAMINHO = por bp de surpresa de REUNIÃO
(β reusados da 2.3; o vetor P sai literalmente o mesmo). Desligamento
antes do 1º tick de resolução (última reunião do ano) = backtest.

Unidades: taxas/E_poly/E_ZQ em NÍVEL, em bps (4.00% = 400); surpresa em
bps; β em fração/bp (os da 2.3) → Q em fração decimal.
"""

import numpy as np

from poly_preprocessing import favorite_longshot, normalize_probs, pmf_mean
from views_common import P_from_betas, ViewResult

MARKET_ASSET = "SPY"
CORTE_BPS = 25.0  # convenção da espec (itens 0/1): 25bp por corte


def rates_from_cut_buckets(taxa_atual_bps, n_cuts):
    """Converte buckets de nº de cortes em taxa de fim de ano (bps):
    taxa_atual − 25bp·n (conversão mecânica da espec, item 1)."""
    return np.asarray(taxa_atual_bps, dtype=float) - CORTE_BPS * np.asarray(n_cuts, dtype=float)


def build_view(assets, e_zq_dez_bps, betas,
               bucket_probs=None, bucket_rates_bps=None,
               binary_prob=None, taxa_atual_bps=None,
               fl_correction=favorite_longshot, market_asset=MARKET_ASSET):
    """Monta a view B para uma data de rebalanceamento.

    Parâmetros:
      assets          : list[str] — universo na ordem do dataset do Paulo.
      e_zq_dez_bps    : taxa implícita no ZQ de DEZEMBRO (100 − preço), em
                        bps de NÍVEL — contrato fixo do ano do mercado.
      betas           : (n,) — os MESMOS β da 2.3 (fração/bp), sem
                        estimação nova (premissa da espec, item 3).
      bucket_probs    : probs CRUAS dos buckets de trajetória (ou None).
      bucket_rates_bps: taxa de fim de ano de cada bucket, bps (buckets de
                        nº de cortes: converter com rates_from_cut_buckets;
                        aberto resolvido via open_bucket_value — 11b).
      binary_prob     : tupla (p_sim, p_nao) CRUA do binário (ou None).
      taxa_atual_bps  : taxa vigente (nível, bps) — exigida no fallback.

    Retorna ViewResult ou None se não há mercado de trajetória.
    """
    if bucket_probs is not None:
        e_poly_bps = pmf_mean(bucket_probs, bucket_rates_bps, fl_correction)
        caminho = "pmf"
    elif binary_prob is not None:
        if taxa_atual_bps is None:
            raise ValueError("fallback binário exige taxa_atual_bps (E_poly = taxa_atual + p·(−25bp))")
        p_yes = float(fl_correction(normalize_probs([binary_prob[0], binary_prob[1]]))[0])
        e_poly_bps = taxa_atual_bps + p_yes * (-CORTE_BPS)
        caminho = "binario"
    else:
        return None  # cascata item 0: sem mercado de trajetória -> view desativada

    surpresa_bps = e_poly_bps - e_zq_dez_bps
    P = P_from_betas(betas, list(assets), market_asset)
    betas = np.asarray(betas, dtype=float)
    Q = float(surpresa_bps * (P @ betas))
    return ViewResult(P=P, Q=Q, diagnostics={
        "view": "B_trajetoria_fed",
        "caminho": caminho,
        "e_poly_bps": e_poly_bps,
        "e_zq_dez_bps": e_zq_dez_bps,
        "surpresa_bps": surpresa_bps,
        "sum_P_beta": float(P @ betas),
    })
