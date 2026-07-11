"""Tática — Gap de fim de semana (poly 24/7 × bolsa fechada).

Módulo do Felipe. STATUS: candidata da camada tática reformulada — código
pronto; ENTRADA e valor de `lam` pendentes de reunião. Espec completa:
`Informações_uteis/táticas/tatica_gap_fds.md`.
Âncoras: Snowberg, Wolfers & Zitzewitz (2007); Lou, Polk & Skouras (2019).
Sinal EXCLUSIVO do Polymarket (explora o poly operar 24/7).

    Δp_fds = p(último snapshot <= abertura de segunda) − p(close de sexta)
    dw     = lam × Σ_views β_view × Δp_fds_view    (tilt cross-sectional)

Os β são OS JÁ ESTIMADOS pelas views designadas ativas (2.3/2.4/3.1/C/E/G,
conforme a reunião aprovar) — a tática não estima nada próprio. O Δp vem da
MESMA série pré-processada da view (poly_preprocessing.binary_prob_series,
decisão 9 — midpoint obrigatório: último trade fica stale no fim de semana).
Janela: entra na ABERTURA de segunda, desmonta no FECHAMENTO de segunda
(1 dia útil; variante "desmonte em k dias" anotada para reunião). Feriados
prolongados (bolsa fechada >= 3 dias) contam como fim de semana.

Sinal contínuo, sem threshold: Δp pequeno -> posição pequena naturalmente.
Mean-reversion dos binários do poly = risco aceito e documentado; upgrade
registrado: filtro por magnitude/volume se o backtest pedir.
"""

import numpy as np

from taticas_common import OverlayResult


def build_overlay(assets, lam, view_signals):
    """Tilt da tática para UM dia (contrato de chamada diária).

    Parâmetros:
      assets       : universo na ordem do dataset do Paulo.
      lam          : orçamento/escala do tilt inteiro — parâmetro humano de
                     reunião, nunca default.
      view_signals : lista de tuplas (view_name, betas (n,), dp_fds) das
                     views ATIVAS cujo mercado teve snapshot de fim de
                     semana utilizável. Quem monta é o backtest: Δp sobre a
                     MESMA série pré-processada da view; view desligada
                     (proximidade de resolução) sai da lista junto —
                     desligamento herdado. O teste de defasagem das views
                     já garante que só operamos mercados com k > 0.
                     Lista vazia ou None (dia que não é reabertura pós-fim
                     de semana) -> dormente (retorna None).

    Retorna OverlayResult | None. Tilts de múltiplas views SOMAM (mesma
    lógica do empilhamento de views no BL).
    """
    if not view_signals:
        return None  # cascata: sem view ativa / sem snapshot -> dormente
    if lam <= 0:
        raise ValueError("lam deve ser positivo (parâmetro de reunião)")
    n = len(assets)
    dw = np.zeros(n)
    sinais = []
    for view_name, betas, dp_fds in view_signals:
        b = np.asarray(betas, dtype=float)
        if b.shape != (n,):
            raise ValueError(
                f"betas da view {view_name} não alinham com o universo: "
                f"{b.shape} vs ({n},)"
            )
        dw += lam * b * float(dp_fds)
        sinais.append({"view": view_name, "dp_fds": float(dp_fds)})
    return OverlayResult(dw=dw, diagnostics={
        "tatica": "gap_fds",
        "lam": lam,
        "sinais": sinais,
        "janela": "abertura de segunda -> fechamento de segunda",
    })
