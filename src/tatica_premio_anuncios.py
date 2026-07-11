"""Tática 1.3 — Prêmio de risco de anúncios macro (sleeve long SPY vs caixa).

Módulo do Felipe. STATUS: candidata-fundadora da camada tática reformulada —
código pronto; a ENTRADA na carteira e o valor de `orcamento_max` seguem
pendentes de reunião. Espec completa (desenho, rejeitadas, pendências):
`Informações_uteis/táticas/tatica_1.3_premio_anuncios.md`.
Âncoras: Savor & Wilson (2013) — prêmio em dia de anúncio macro agendado;
Lucca & Moench (2015) só como referência, não como janela.

    sinal   = entropia normalizada H(p)/H_max da PMF do anúncio,
              medida no último snapshot <= fechamento de D-1 (sem lookahead)
    dw[SPY] = orcamento_max * sinal   (só no dia D do anúncio;
                                       janela D-1 close -> D close)

Sempre ligado, modulado: opera em TODO dia de anúncio (FOMC + CPI no v1 —
os mercados que as views 2.2/2.3 já contratam); a incerteza DIMENSIONA a
posição, não decide se liga (sem threshold). Cascata de degradação: dia sem
anúncio, ou anúncio sem PMF utilizável (mercado fino) -> None (dormente;
nunca bloqueia o BL) — quem decide "utilizável" é o chamador, passando None.

Pré-processamento (decisão 9): normalização + favorite-longshot (o stub
FALHA ALTO até a decisão 11a). A entropia não usa os VALORES dos buckets,
então a decisão 11b (bucket aberto) NÃO bloqueia esta tática.
"""

import numpy as np

from poly_preprocessing import favorite_longshot, normalize_probs
from taticas_common import OverlayResult

SPY_ASSET = "SPY"  # long-vs-caixa é a leitura direta de Savor-Wilson (espec)


def normalized_entropy(probs, fl_correction=favorite_longshot):
    """Entropia normalizada da PMF pré-processada: H(p)/log(n) em [0, 1].

    Pipeline da decisão 9: normaliza (spread bid/ask) -> favorite-longshot
    -> H = -Σ p·ln(p) (termos p = 0 contribuem 0). Exige n >= 2 buckets
    (com 1 bucket H_max = 0 e o sinal é indefinido).
    """
    p = np.asarray(fl_correction(normalize_probs(probs)), dtype=float)
    if p.ndim != 1 or p.shape[0] < 2:
        raise ValueError(f"PMF precisa de >= 2 buckets: shape {p.shape}")
    nz = p[p > 0]
    h = float(-(nz * np.log(nz)).sum())
    return h / float(np.log(p.shape[0]))


def build_overlay(assets, orcamento_max, announcement_pmf=None,
                  fl_correction=favorite_longshot, spy_asset=SPY_ASSET):
    """Tilt da tática para UM dia (contrato de chamada diária).

    Parâmetros:
      assets          : list[str] — universo na ordem do dataset do Paulo.
      orcamento_max   : orçamento da tática (fração do patrimônio) —
                        parâmetro humano de reunião, nunca default.
      announcement_pmf: probs CRUAS dos buckets do mercado do anúncio de
                        HOJE, no último snapshot <= fechamento de D-1
                        (grid de 12h garante que existe — sem lookahead).
                        None = dia sem anúncio ou sem PMF utilizável ->
                        dormente (retorna None).
      fl_correction   : correção de favorite-longshot (default: stub 11a).

    Retorna OverlayResult | None. Se dois anúncios caem no mesmo dia (ex.
    CPI e FOMC), chamar uma vez por evento e somar via apply_overlays.
    """
    if announcement_pmf is None:
        return None  # cascata: dia sem anúncio / sem PMF -> dormente
    if orcamento_max <= 0:
        raise ValueError("orcamento_max deve ser positivo (parâmetro de reunião)")
    sinal = normalized_entropy(announcement_pmf, fl_correction)
    dw = np.zeros(len(assets))
    dw[list(assets).index(spy_asset)] = orcamento_max * sinal
    return OverlayResult(dw=dw, diagnostics={
        "tatica": "1.3_premio_anuncios",
        "entropia_normalizada": sinal,
        "orcamento_max": orcamento_max,
        "janela": "D-1 close -> D close",
    })
