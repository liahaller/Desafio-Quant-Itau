"""Testes do hedge de beta do `gate_transversal_neutro.py` (Felipe).

O que está sendo protegido é o `.shift(1)` do β expansivo. Sem ele o hedge
conhece o próprio retorno que está removendo, o spread sai artificialmente
limpo, e o artefato inteiro passa a medir lookahead em vez de sinal — um erro
que produz números bonitos e não levanta exceção nenhuma.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gate_transversal_neutro import (MINIMO_PREGOES, SUFIXO,  # noqa: E402
                                     neutraliza, pernas_neutras)
from gate_transversal import neutralidade  # noqa: E402


@pytest.fixture
def retornos():
    """XLP = 2×SPY + ruído. O beta verdadeiro é 2, cravado na construção."""
    rng = np.random.default_rng(7)
    datas = pd.bdate_range("2015-01-05", periods=1500)
    spy = pd.Series(rng.normal(0, 0.01, len(datas)), index=datas)
    return pd.DataFrame({
        "SPY": spy,
        "XLP": 2 * spy + rng.normal(0, 0.002, len(datas)),
        "XLK": 0.5 * spy + rng.normal(0, 0.002, len(datas)),
    }, index=datas)


def test_hedge_remove_o_beta_de_mercado(retornos):
    """A perna hedgeada perde a correlação com o SPY; a crua mantém."""
    saida = pernas_neutras(retornos, ["XLP"]).dropna()
    assert abs(saida["XLP"].corr(saida["SPY"])) > 0.9
    assert abs(saida[f"XLP{SUFIXO}"].corr(saida["SPY"])) < 0.1


def test_beta_e_defasado_um_dia(retornos):
    """O β usado em D é o estimado até D−1 — reconstruído aqui à mão."""
    saida = pernas_neutras(retornos, ["XLP"])
    mercado, ativo = retornos["SPY"], retornos["XLP"]
    beta = (ativo.expanding(min_periods=MINIMO_PREGOES).cov(mercado)
            / mercado.expanding(min_periods=MINIMO_PREGOES).var()).shift(1)
    esperado = ativo - beta * mercado

    d = retornos.index[MINIMO_PREGOES + 10]
    assert saida.loc[d, f"XLP{SUFIXO}"] == pytest.approx(esperado.loc[d])
    # e o β de D difere do β que incluiria D: é isso que o shift garante
    sem_shift = (ativo.expanding(min_periods=MINIMO_PREGOES).cov(mercado)
                 / mercado.expanding(min_periods=MINIMO_PREGOES).var())
    assert beta.loc[d] != pytest.approx(sem_shift.loc[d])


def test_primeiras_datas_ficam_NaN_ate_a_semeadura(retornos):
    """Antes de `MINIMO_PREGOES` não há β, e não se chuta um."""
    saida = pernas_neutras(retornos, ["XLP"])
    coluna = saida[f"XLP{SUFIXO}"]
    assert coluna.iloc[:MINIMO_PREGOES].isna().all()
    assert coluna.iloc[MINIMO_PREGOES:].notna().any()


def test_neutraliza_preserva_os_sinais_do_livro():
    """Trocar as pernas pelas hedgeadas não pode mexer na premissa declarada."""
    assert neutraliza({"XLP": +1, "XLK": -1}) == {
        f"XLP{SUFIXO}": +1, f"XLK{SUFIXO}": -1}


def test_spread_neutro_e_mais_neutro_que_o_cru(retornos):
    """O ponto do artefato: +XLP −XLK cru carrega beta (2 − 0,5 = 1,5)."""
    saida = pernas_neutras(retornos, ["XLP", "XLK"]).dropna()
    livro = {"XLP": +1, "XLK": -1}
    assert abs(neutralidade(saida, livro)) > 0.9
    assert abs(neutralidade(saida, neutraliza(livro))) < 0.1


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
