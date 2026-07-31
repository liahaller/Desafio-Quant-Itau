"""Pré-processamento das probabilidades do Polymarket (módulo do Felipe).

DECISAO-9 (fechada, ver Decisoes_pendentes.md): módulo compartilhado único,
caixa de ferramentas de funções puras — cada view chama o que precisa.
Nenhum "preprocess()" monolítico.

MEDIDO (follow-up do Paulo, F5, 2026-07-29): a série do `/prices-history`
JÁ É O MIDPOINT do book (bate com `/midpoint`, não com `/last-trade-price`,
em dois mercados vivos). Não existe bid/ask histórico no CLOB, então não há
`midpoint_price(bid, ask)` — o pipeline entrega a série de midpoint pronta.
Consequência: o spread NÃO é observável; qualquer haircut de custo é premissa,
não estimativa.

Peças:
  - normalize_probs    : probs não somam 1 (medido nas PMFs cruas: M1 0,978–1,060;
                         M3 0,923–1,325); divide pela soma. Vale para binários e PMFs.
  - favorite_longshot  : correção do viés — forma AINDA NÃO DECIDIDA.
                         # TODO(DECISAO-11a)
  - open_bucket_value  : valor do bucket aberto das PMFs (2.2/2.3) —
                         AINDA NÃO DECIDIDO. # TODO(DECISAO-11b)
  - pmf_mean           : média de PMF de buckets com o pré-processamento
                         padrão (normaliza -> favorite-longshot -> Σ p·x);
                         usada pelas views 2.2 (CPI) e 2.3 (FOMC).
  - binary_prob_series : série p(sim) de mercado binário (normaliza o par
                         Yes/No -> favorite-longshot); usada pelas views
                         2.4 (eleitoral) e 3.1 (recessão).

Funções puras: recebem arrays, devolvem arrays. As séries de midpoint cruas
vêm do pipeline do Paulo (`/prices-history` por tokenId, um arquivo por token).
"""

import numpy as np


def normalize_probs(probs, axis=-1):
    """Normaliza probabilidades para somarem 1 (dividir pela soma).

    Os midpoints de tokens com books independentes não somam 1 — tanto no
    binário (p_sim + p_nao != 1) quanto na PMF de buckets (medido no dado cru
    do Paulo: soma entre 0,92 e 1,33). `axis` permite normalizar uma matriz
    (datas x buckets) linha a linha.
    """
    probs = np.asarray(probs, dtype=float)
    if np.any(probs < 0):
        raise ValueError("probabilidade negativa na entrada")
    total = probs.sum(axis=axis, keepdims=True)
    if np.any(total <= 0):
        raise ValueError("soma de probabilidades <= 0 — impossível normalizar")
    return probs / total


def favorite_longshot(probs):
    """Correção de favorite-longshot bias (Camada 4).

    # TODO(DECISAO-11a): forma da correção não decidida (calibração própria
    # vs curva da literatura vs sem correção no v1). Stub que falha alto de
    # propósito — identidade silenciosa esconderia a ausência da correção
    # no backtest (relevante sobretudo para a 3.1, que vive em p baixa).
    """
    raise NotImplementedError("TODO(DECISAO-11a): forma do favorite-longshot pendente")


def pmf_mean(probs, values, fl_correction=favorite_longshot):
    """Média de uma PMF de buckets com o pré-processamento padrão:
    normaliza (midpoints não somam 1) -> favorite-longshot -> Σ pᵢ·xᵢ.

    `values` deve vir com o bucket aberto já resolvido (open_bucket_value,
    decisão 11b) — NaN é rejeitado. Se a forma da decisão 11a exigir
    renormalizar após a correção, isso entra na própria favorite_longshot
    (contrato: devolve PMF utilizável). `fl_correction` injetável só para
    teste sintético; o default falha alto até a decisão 11a.
    """
    probs = np.asarray(probs, dtype=float)
    values = np.asarray(values, dtype=float)
    if probs.shape != values.shape:
        raise ValueError(f"probs e values devem alinhar: {probs.shape} vs {values.shape}")
    if np.any(np.isnan(values)):
        raise ValueError("values contém NaN — bucket aberto não resolvido (decisão 11b)")
    p = fl_correction(normalize_probs(probs))
    return float(p @ values)


def binary_prob_series(p_yes, p_no=None, fl_correction=favorite_longshot):
    """Série p(sim) de um mercado binário: normalização par a par
    (p_sim + p_não != 1) -> favorite-longshot.

    `p_yes`/`p_no` são as séries de midpoint dos dois tokenIds, já alinhadas
    no mesmo grid de 12h. `p_no=None` = só a série do Yes disponível (é o caso
    da entrega atual do Paulo, que puxou só o token Yes dos 9 mercados): sem o
    par não há o que normalizar, vai direto para a correção FL.

    Usada pelas views 2.4 e 3.1. Construir UMA vez a montante e passar a
    MESMA série tanto para a regressão do β quanto para o build_view — é o
    que faz a parte linear da correção FL ser absorvida pelo β (espec 2.4,
    item 2b). `fl_correction` default = stub da decisão 11a (falha alto).
    """
    p_yes = np.asarray(p_yes, dtype=float)
    if p_no is None:
        p = p_yes
    else:
        p_no = np.asarray(p_no, dtype=float)
        if p_yes.shape != p_no.shape:
            raise ValueError(f"p_yes e p_no devem alinhar: {p_yes.shape} vs {p_no.shape}")
        p = normalize_probs(np.column_stack([p_yes, p_no]), axis=1)[:, 0]
    return np.asarray(fl_correction(p), dtype=float)


def open_bucket_value(bound, side):
    """Valor representativo do bucket aberto de uma PMF (ex. '<=3.6%').

    # TODO(DECISAO-11b): valor/regra não decididos (ponto médio extrapolado
    # vs valor fixo vs truncar no limite). Stub que falha alto de propósito.
    `side`: 'lower' para bucket '<= bound', 'upper' para '>= bound'.
    """
    raise NotImplementedError("TODO(DECISAO-11b): valor do bucket aberto pendente")
