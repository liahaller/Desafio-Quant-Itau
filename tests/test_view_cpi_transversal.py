"""Testes sintéticos da view CPI transversal (regra CLAUDE.md §5: caso com
resultado conhecido).

Os βs e a divergência são plantados; o que se confere é que a view devolve
exatamente a álgebra declarada no docstring do módulo — e que ela recusa as
duas condições que a fariam mentir em silêncio (β sem dispersão, horizonte
zerado).
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from view_cpi_transversal import (MINIMO_PREGOES, build_view,
                                  estimate_betas_breakeven)

ASSETS = ["SPY", "XLK", "XLU", "TIP"]
# β em retorno por unidade de breakeven: TIP ganha com inflação, XLK sofre.
BETAS = np.array([0.4, 0.2, 0.5, 0.6])
# excess = β − β_SPY = [0, −0.2, +0.1, +0.2]; Σ|excess| = 0.5
# P = 2·excess/0.5 = [0, −0.8, 0.4, 0.8]; Σ P·β = −0.16 + 0.2 + 0.48 = 0.52
P_ESPERADO = np.array([0.0, -0.8, 0.4, 0.8])
SUM_P_BETA = 0.52


def test_estimate_betas_breakeven_recupera_beta_exato():
    """Dado exatamente linear (r = a + β·Δbe) devolve o β plantado, e o
    intercepto comum não contamina."""
    rng = np.random.default_rng(0)
    dbe = pd.Series(rng.normal(size=200) / 100.0,
                    index=pd.date_range("2024-01-01", periods=200, freq="B"))
    retornos = pd.DataFrame(0.0003 + np.outer(dbe.to_numpy(), BETAS),
                            index=dbe.index, columns=ASSETS)
    assert np.allclose(estimate_betas_breakeven(retornos, dbe, ASSETS), BETAS)


def test_estimate_betas_breakeven_alinha_por_data_e_exige_amostra():
    """Datas que só existem de um lado saem do par; abaixo do piso, erro."""
    idx = pd.date_range("2024-01-01", periods=MINIMO_PREGOES + 10, freq="B")
    dbe = pd.Series(np.linspace(-0.01, 0.01, len(idx)), index=idx)
    retornos = pd.DataFrame(np.outer(dbe.to_numpy(), BETAS), index=idx, columns=ASSETS)
    # 20 datas do breakeven sem retorno correspondente: descartadas, não erro.
    dbe_extra = pd.concat([dbe, pd.Series(0.0, index=pd.date_range("2030-01-01", periods=20, freq="B"))])
    assert np.allclose(estimate_betas_breakeven(retornos, dbe_extra, ASSETS), BETAS)
    curto = idx[: MINIMO_PREGOES - 1]
    try:
        estimate_betas_breakeven(retornos.loc[curto], dbe.loc[curto], ASSETS)
        assert False, "amostra abaixo do piso deveria ser rejeitada"
    except ValueError:
        pass


def test_caso_conhecido():
    """divergência líquida +2% em 4 pregões -> Q = Σ P·β × 0.02/4."""
    r = build_view(ASSETS, BETAS, divergencia_liquida=0.02, dias_ate_divulgacao=4,
                   soma_faixas=0.97)
    assert np.allclose(r.P, P_ESPERADO)
    assert np.isclose(np.abs(r.P).sum(), 2.0)
    assert r.P[ASSETS.index("SPY")] == 0.0
    assert np.isclose(r.Q, SUM_P_BETA * 0.02 / 4)
    assert r.diagnostics["view"] == "cpi_transversal"
    assert r.diagnostics["horizonte_q_dias"] == 1  # empilha com 2.2 e 2.3
    assert np.isclose(r.diagnostics["soma_faixas"], 0.97)


def test_q_aperta_conforme_a_divulgacao_chega():
    """DECISAO-7.2: mesmo sinal, menos dias -> Q maior (o repricing concentra)."""
    longe = build_view(ASSETS, BETAS, 0.02, 10)
    perto = build_view(ASSETS, BETAS, 0.02, 2)
    assert perto.Q > longe.Q > 0
    assert np.isclose(perto.Q / longe.Q, 5.0)


def test_sinal_segue_a_divergencia():
    """Divergência negativa (poly menos inflacionista que o título) inverte o Q,
    sem tocar no P."""
    positivo = build_view(ASSETS, BETAS, 0.02, 4)
    negativo = build_view(ASSETS, BETAS, -0.02, 4)
    assert np.isclose(negativo.Q, -positivo.Q)
    assert np.allclose(negativo.P, positivo.P)


def test_cascata_herdada_da_2_2():
    """Sem mercado de CPI a 2.2 devolve None e passa None para cá: view sai."""
    assert build_view(ASSETS, BETAS, None, 4) is None


def test_recusa_horizonte_invalido():
    """dias_ate_divulgacao < 1 é o dia da divulgação ou depois — o mercado já
    resolveu e a divergência não tem para onde fechar."""
    for dias in (0, -3):
        try:
            build_view(ASSETS, BETAS, 0.02, dias)
            assert False, f"dias_ate_divulgacao={dias} deveria ser rejeitado"
        except ValueError:
            pass


def test_recusa_betas_sem_dispersao():
    """Todos os ativos com a mesma sensibilidade: não há seção cruzada a
    expressar, e P seria 0/0 (o `P_from_betas` falha alto)."""
    try:
        build_view(ASSETS, np.full(len(ASSETS), 0.4), 0.02, 4)
        assert False, "βs sem dispersão deveriam ser rejeitados"
    except ValueError:
        pass
