"""Pré-processamento das probabilidades do Polymarket (módulo do Felipe).

DECISAO-9 (fechada, ver Decisoes_pendentes.md): módulo compartilhado único,
caixa de ferramentas de funções puras — cada view chama o que precisa.
Nenhum "preprocess()" monolítico.

Peças:
  - midpoint_price     : série de preço = (bid + ask) / 2 (decisão da 2.4/3.1;
                         último trade stale infla a defasagem k).
  - normalize_probs    : probs não somam 1 por causa do spread bid/ask;
                         divide pela soma. Vale para binários e PMFs.
  - favorite_longshot  : correção do viés — forma AINDA NÃO DECIDIDA.
                         # TODO(DECISAO-11a)
  - open_bucket_value  : valor do bucket aberto das PMFs (2.2/2.3) —
                         AINDA NÃO DECIDIDO. # TODO(DECISAO-11b)
  - pmf_mean           : média de PMF de buckets com o pré-processamento
                         padrão (normaliza -> favorite-longshot -> Σ p·x);
                         usada pelas views 2.2 (CPI) e 2.3 (FOMC).
  - binary_prob_series : série p(sim) de mercado binário (midpoint de cada
                         lado -> normaliza o par -> favorite-longshot);
                         usada pelas views 2.4 (eleitoral) e 3.1 (recessão).

Funções puras: recebem arrays, devolvem arrays. Bid/ask crus vêm do
pipeline do Paulo (interface registrada na decisão 9).
"""

import numpy as np


def midpoint_price(bid, ask):
    """Série de preço da probabilidade: midpoint = (bid + ask) / 2.

    Nunca usar último trade: em mercado fino ele fica stale (série em
    degraus) e infla artificialmente a defasagem k estimada (views 2.4/3.1).
    Entradas: arrays alinhados de bid e ask (mesmo shape).
    """
    bid = np.asarray(bid, dtype=float)
    ask = np.asarray(ask, dtype=float)
    if bid.shape != ask.shape:
        raise ValueError(f"bid e ask devem ter o mesmo shape: {bid.shape} vs {ask.shape}")
    if np.any(bid > ask):
        raise ValueError("bid > ask em pelo menos um ponto — dado corrompido")
    return (bid + ask) / 2.0


def normalize_probs(probs, axis=-1):
    """Normaliza probabilidades para somarem 1 (dividir pela soma).

    O spread bid/ask faz as probs cruas não somarem 1 — tanto no binário
    (p_sim + p_nao != 1) quanto na PMF de buckets. `axis` permite normalizar
    uma matriz (datas x buckets) linha a linha.
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
    normaliza (spread bid/ask) -> favorite-longshot -> Σ pᵢ·xᵢ.

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


def binary_prob_series(bid_yes, ask_yes, bid_no, ask_no, fl_correction=favorite_longshot):
    """Série diária p(sim) de um mercado binário, com o trio padrão:
    midpoint bid/ask de cada lado -> normalização par a par
    (p_sim + p_não != 1 pelo spread) -> favorite-longshot.

    Usada pelas views 2.4 e 3.1. Construir UMA vez a montante e passar a
    MESMA série tanto para a regressão do β quanto para o build_view — é o
    que faz a parte linear da correção FL ser absorvida pelo β (espec 2.4,
    item 2b). `fl_correction` default = stub da decisão 11a (falha alto).
    """
    p_yes = midpoint_price(bid_yes, ask_yes)
    p_no = midpoint_price(bid_no, ask_no)
    pair = normalize_probs(np.column_stack([p_yes, p_no]), axis=1)
    return np.asarray(fl_correction(pair[:, 0]), dtype=float)


def open_bucket_value(bound, side):
    """Valor representativo do bucket aberto de uma PMF (ex. '<=3.6%').

    # TODO(DECISAO-11b): valor/regra não decididos (ponto médio extrapolado
    # vs valor fixo vs truncar no limite). Stub que falha alto de propósito.
    `side`: 'lower' para bucket '<= bound', 'upper' para '>= bound'.
    """
    raise NotImplementedError("TODO(DECISAO-11b): valor do bucket aberto pendente")
