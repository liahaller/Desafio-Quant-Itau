"""Contrato de saída comum da camada tática reformulada (módulo do Felipe).

Camada tática REFORMULADA (contrato de desenho em
`Informações_uteis/táticas/tatica_1.3_premio_anuncios.md`): sleeves overlay
que rodam EM PARALELO ao BL — não viram views e não tocam `bl_integration`.
STATUS: candidata — a ENTRADA da camada na carteira segue pendente de
reunião (reabre parcialmente a decisão 10). Dono do módulo: Felipe
(realocado da Lia por decisão do Felipe, sessão 2026-07-11).

Interface fechada em sessão (Felipe, 2026-07-11, 3 escolhas): contrato de
CHAMADA DIÁRIA — o backtest pergunta a cada tática "qual seu tilt hoje?":

  build_overlay(insumos do dia) -> OverlayResult | None

  - OverlayResult : tática ativa no dia; `dw` pronto para somar ao w do BL.
  - None          : tática dormente no dia (sem evento, sem dado utilizável)
                    — não é falha; a soma simplesmente não inclui.

Convenções:
  - dw : ndarray (n,) de pesos EXTRAS alinhado à lista `assets`, mesma
         unidade de w (fração do patrimônio). Alavancagem temporária por
         cima do BL irrestrito (decisão 8) — a carteira BL fica INTOCADA
         (atribuição limpa por camada).
  - diagnostics : dict livre (auditoria/relatório), mesma filosofia do
         ViewResult. Nota pendente com a Lia: interação Ω ↔ camada
         (a mesma incerteza entra com sinais opostos nos dois módulos).
  - Janelas (D→D+15, truncagem no FOMC seguinte, segunda-feira) são lógica
    INTERNA de cada tática; o backtest só marca diariamente e soma via
    apply_overlays.
  - Orçamentos (`orcamento_max`, `orcamento_acoes`/`orcamento_rf`, `lam`)
    são parâmetros HUMANOS de reunião — sempre argumento, nunca default.
"""

from typing import NamedTuple

import numpy as np


class OverlayResult(NamedTuple):
    dw: np.ndarray
    diagnostics: dict


def apply_overlays(w_bl, overlay_results):
    """w_final = w_bl + Σ dw das táticas ativas (None = dormente, não soma).

    Retorna (w_final (n,), diagnostics list na ordem das ativas). A
    precedência tilt × rebalanceamento estrutural no MESMO dia é pendência
    de reunião (espec gap FDS, item d) — este helper só soma.
    """
    w_bl = np.asarray(w_bl, dtype=float)
    active = [r for r in overlay_results if r is not None]
    w = w_bl.copy()
    for r in active:
        dw = np.asarray(r.dw, dtype=float)
        if dw.shape != w_bl.shape:
            raise ValueError(
                f"dw da tática {r.diagnostics.get('tatica', '?')} não alinha "
                f"com a carteira: {dw.shape} vs {w_bl.shape}"
            )
        w = w + dw
    return w, [r.diagnostics for r in active]
