"""Testes sintéticos da view de incerteza de anúncio (regra CLAUDE.md §5).

Cobre as três propriedades que a view PRECISA ter para valer o que o docstring
dela promete: a entropia é invariante à renormalização (é o que a faz funcionar
nos payrolls sem rótulo de balde), o intercepto da regressão come o prêmio
incondicional (que a medição não achou), e o P é direcional sem quebrar a
convenção Σ|P| = 2.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from view_incerteza_anuncio import (build_view, directional_P,
                                    entropia_normalizada,
                                    estimate_betas_incerteza)

ASSETS = ["SPY", "XLK", "XLU", "TIP"]
BETAS = np.array([0.05, 0.03, -0.01, 0.0])  # retorno por unidade de entropia
# P = [2, 0, 0, 0] -> Σ P·β = 2 × 0.05 = 0.10
SUM_P_BETA = 0.10


def test_entropia_extremos_conhecidos():
    """Uniforme = 1 exato; toda a massa num balde = 0; menos de 2 vivos = NaN."""
    assert np.isclose(entropia_normalizada([0.25, 0.25, 0.25, 0.25]), 1.0)
    assert np.isclose(entropia_normalizada([1.0, 0.0, 0.0]), float("nan"), equal_nan=True)
    assert np.isclose(entropia_normalizada([0.9, 0.1]),
                      -(0.9 * np.log(0.9) + 0.1 * np.log(0.1)) / np.log(2))
    assert np.isnan(entropia_normalizada([0.4]))
    assert np.isnan(entropia_normalizada([np.nan, np.nan, 0.5]))


def test_entropia_invariante_a_renormalizacao():
    """A PMF do poly não soma 1 — a entropia tem de ignorar a escala. É esta
    propriedade que dispensa o valor dos baldes (decisões 1.2 e 6.1) e permite
    usar payrolls, cujos arquivos do G9 não trazem rótulo de faixa."""
    crua = [0.30, 0.42, 0.12, 0.09]
    assert np.isclose(entropia_normalizada(crua),
                      entropia_normalizada(np.array(crua) / sum(crua)))
    assert np.isclose(entropia_normalizada(crua),
                      entropia_normalizada(np.array(crua) * 3.7))


def test_estimate_betas_incerteza_ignora_premio_incondicional():
    """Retorno = prêmio fixo + β·entropia. O intercepto absorve o prêmio médio
    (que `premissa_taticas.py` mediu e não achou) e o β sai limpo."""
    h = pd.Series([0.10, 0.35, 0.55, 0.70, 0.90, 0.45])
    premio_incondicional = 0.004
    R = pd.DataFrame(premio_incondicional + np.outer(h.to_numpy(), BETAS), columns=ASSETS)
    assert np.allclose(estimate_betas_incerteza(R, h, ASSETS), BETAS)


def test_directional_P_mantem_convencao():
    """Σ|P| = 2 (decisão 4) com uma perna só, e ΣP ≠ 0 de propósito."""
    P = directional_P(ASSETS)
    assert np.allclose(P, [2.0, 0.0, 0.0, 0.0])
    assert np.isclose(np.abs(P).sum(), 2.0)
    assert P.sum() != 0.0
    try:
        directional_P(["XLK", "TIP"])
        assert False, "ativo de mercado fora do universo deveria ser rejeitado"
    except ValueError:
        pass


def test_caso_conhecido_com_demeanagem():
    """entropia 0.80 contra média da família 0.62 -> Q = Σ P·β × 0.18."""
    r = build_view(ASSETS, BETAS, entropia=0.80, entropia_media=0.62,
                   soma_faixas=0.98, familia="cpi")
    assert np.isclose(r.diagnostics["incerteza_liquida"], 0.18)
    assert np.isclose(r.Q, SUM_P_BETA * 0.18)
    assert np.allclose(r.P, [2.0, 0.0, 0.0, 0.0])
    assert r.diagnostics["view"] == "incerteza_anuncio"
    assert r.diagnostics["horizonte_q_dias"] == 1  # empilha com 2.2 e 2.3
    assert r.diagnostics["direcional"] is True
    assert r.diagnostics["familia"] == "cpi"


def test_anuncio_menos_incerto_que_a_media_inverte_o_sinal():
    """A tese é o CONTRASTE, não o nível: evento mais previsível que o normal da
    família pede prêmio negativo, não prêmio zero."""
    incerto = build_view(ASSETS, BETAS, entropia=0.80, entropia_media=0.62)
    previsivel = build_view(ASSETS, BETAS, entropia=0.44, entropia_media=0.62)
    assert incerto.Q > 0 > previsivel.Q


def test_demeanagem_por_familia_muda_o_sinal_do_mesmo_numero():
    """Mesma entropia 0.80: alta para o CPI (média 0.62), baixa para payrolls
    (média 0.83). É o motivo medido de a demeanagem ser por família."""
    como_cpi = build_view(ASSETS, BETAS, 0.80, entropia_media=0.62, familia="cpi")
    como_payroll = build_view(ASSETS, BETAS, 0.80, entropia_media=0.83, familia="payrolls")
    assert como_cpi.Q > 0 > como_payroll.Q


def test_cascata_dia_sem_anuncio_e_pmf_ilegivel():
    """Sem evento (None) e PMF ilegível (NaN) desativam a view — não é falha."""
    assert build_view(ASSETS, BETAS, entropia=None) is None
    assert build_view(ASSETS, BETAS, entropia=float("nan")) is None
    assert build_view(ASSETS, BETAS,
                      entropia=entropia_normalizada([0.7])) is None
