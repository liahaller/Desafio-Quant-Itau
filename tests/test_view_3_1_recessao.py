"""Testes sintéticos da view 3.1 (regra CLAUDE.md §5: caso com resultado
conhecido). Inclui o sanity check de sinal OBRIGATÓRIO da espec (item 6),
com os números do exemplo da própria espec."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from view_3_1_recessao import (build_view, build_view_direcional, curve_spread,
                              p_curve_at, p_curve_probit)

# Números do exemplo da espec (item 6), β em fração/ponto de probabilidade.
ASSETS = ["SPY", "XLK", "XLP", "TLT"]
BETAS = np.array([-0.30, -0.45, -0.10, 0.15])
# excess = [0, −0.15, +0.20, +0.45]; Σ|excess| = 0.80
# P = 2·excess/0.8 = [0, −0.375, 0.5, 1.125]; Σ P·β = 0.2875
P_ESPERADO = np.array([0.0, -0.375, 0.5, 1.125])
SUM_P_BETA = 0.2875


def test_probit_curva():
    """Spread 0 -> Phi(alpha); mais inclinação (spread maior) -> menos recessão."""
    assert np.isclose(p_curve_probit(0.0, alpha=-0.5, beta_spread=-1.0), norm.cdf(-0.5))
    p_invertida = p_curve_probit(-1.0, alpha=-0.5, beta_spread=-1.0)
    p_inclinada = p_curve_probit(2.0, alpha=-0.5, beta_spread=-1.0)
    assert p_invertida > p_inclinada  # curva invertida = mais recessão


def test_sanity_check_de_sinal_espec_item_6():
    """OBRIGATÓRIO (espec item 6): p_poly = 0.35, p_curva = 0.20 ->
    divergência +0.15 (poly mais pessimista) -> long defensivos/bonds
    (P[XLP] > 0, P[TLT] > 0), short cíclicos (P[XLK] < 0), Q > 0."""
    r = build_view(ASSETS, BETAS, k=2, p_poly=0.35, p_curva=0.20)
    assert np.allclose(r.P, P_ESPERADO)
    assert np.isclose(np.abs(r.P).sum(), 2.0)
    assert r.P[1] < 0 and r.P[2] > 0 and r.P[3] > 0
    assert r.diagnostics["sum_P_beta"] > 0  # dominado pelo termo quadrático
    assert np.isclose(r.Q, SUM_P_BETA * 0.15) and r.Q > 0


def test_divergencia_zero_q_zero():
    """Poly e curva de acordo -> Q = 0 (sem tilt)."""
    r = build_view(ASSETS, BETAS, k=2, p_poly=0.20, p_curva=0.20)
    assert np.isclose(r.Q, 0.0)


def test_sem_mercado_view_desativada():
    """Cascata item 0: sem mercado de recessão -> None (não é falha).
    Sem a curva a view falha alto (benchmark obrigatório quando ativa)."""
    assert build_view(ASSETS, BETAS, k=2) is None
    try:
        build_view(ASSETS, BETAS, k=2, p_poly=0.35)
        assert False, "p_curva ausente com view ativa deveria falhar"
    except ValueError:
        pass


def test_probabilidades_invalidas_rejeitadas():
    """p fora de [0, 1] é dado corrompido, não view."""
    try:
        build_view(ASSETS, BETAS, k=2, p_poly=1.35, p_curva=0.20)
        assert False, "deveria rejeitar p fora de [0, 1]"
    except ValueError:
        pass


def test_spread_descarta_data_sem_as_duas_pontas():
    """Feriado vem como campo vazio no CSV do FRED (NaN depois da leitura):
    a data sai do spread em vez de virar zero ou ser preenchida."""
    datas = pd.to_datetime(["2026-07-06", "2026-07-07", "2026-07-08"])
    dgs10 = pd.Series([4.30, np.nan, 4.35], index=datas)
    dtb3 = pd.Series([3.70, 3.72, np.nan], index=datas)
    spread = curve_spread(dgs10, dtb3)
    assert spread.index.tolist() == [datas[0]]
    assert np.isclose(spread.iloc[0], 0.60)


def test_p_curva_nao_usa_a_leitura_do_proprio_dia():
    """Sem lookahead: o H.15 publica a taxa de D depois do fechamento de D,
    então o rebalanceamento de D enxerga D−1. A leitura de D é uma armadilha
    plantada (spread absurdo); se entrasse, o p mudaria."""
    datas = pd.to_datetime(["2026-07-07", "2026-07-08"])
    spread = pd.Series([1.00, -5.00], index=datas)
    p = p_curve_at(spread, "2026-07-08", alpha=-0.5, beta_spread=-1.0)
    assert np.isclose(p, p_curve_probit(1.00, alpha=-0.5, beta_spread=-1.0))


def test_p_curva_pula_fim_de_semana_e_feriado():
    """Segunda usa a leitura de sexta (a última que o mercado tinha)."""
    spread = pd.Series([1.00, 1.20], index=pd.to_datetime(["2026-07-02", "2026-07-03"]))
    p_segunda = p_curve_at(spread, "2026-07-06", alpha=-0.5, beta_spread=-1.0)
    assert np.isclose(p_segunda, p_curve_probit(1.20, alpha=-0.5, beta_spread=-1.0))


def test_p_curva_sem_historico_falha_alto():
    """Data anterior ao início da série: erro, nunca benchmark inventado."""
    spread = pd.Series([1.00], index=pd.to_datetime(["2026-07-07"]))
    try:
        p_curve_at(spread, "2003-01-02", alpha=-0.5, beta_spread=-1.0)
        assert False, "deveria falhar sem leitura anterior à data"
    except ValueError:
        pass


def test_direcional_concentra_no_mercado_e_mantem_soma_2():
    """P direcional: 2 no SPY, 0 no resto — o oposto do P[SPY] = 0 do neutro."""
    view = build_view_direcional(ASSETS, beta_mercado=-0.30, divergencia=1.5)
    assert view.P[ASSETS.index("SPY")] == 2.0
    assert np.allclose(view.P[1:], 0.0)
    assert np.isclose(np.abs(view.P).sum(), 2.0)          # decisão 4
    assert np.isclose(view.Q, 2 * -0.30 * 1.5)            # Q = P·E[r]
    assert view.diagnostics["view"] == "3.1_recessao_direcional"


def test_direcional_espelha_com_o_sinal_do_beta():
    """A escolha de TESE (sinal do β) é o que troca o lado da view, e só ela."""
    medido = build_view_direcional(ASSETS, beta_mercado=+0.30, divergencia=1.5)
    tese = build_view_direcional(ASSETS, beta_mercado=-0.30, divergencia=1.5)
    assert np.isclose(medido.Q, -tese.Q)
    assert np.allclose(medido.P, tese.P)


def test_direcional_sem_divergencia_desativa():
    """Sem mercado de recessão (ou divergência NaN) a view sai, não chuta."""
    assert build_view_direcional(ASSETS, 0.3, None) is None
    assert build_view_direcional(ASSETS, 0.3, float("nan")) is None


if __name__ == "__main__":
    test_probit_curva()
    test_sanity_check_de_sinal_espec_item_6()
    test_divergencia_zero_q_zero()
    test_sem_mercado_view_desativada()
    test_probabilidades_invalidas_rejeitadas()
    test_spread_descarta_data_sem_as_duas_pontas()
    test_p_curva_nao_usa_a_leitura_do_proprio_dia()
    test_p_curva_pula_fim_de_semana_e_feriado()
    test_p_curva_sem_historico_falha_alto()
    test_direcional_concentra_no_mercado_e_mantem_soma_2()
    test_direcional_espelha_com_o_sinal_do_beta()
    test_direcional_sem_divergencia_desativa()
    print("view_3_1_recessao: 12 testes OK")
