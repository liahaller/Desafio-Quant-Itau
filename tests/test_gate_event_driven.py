"""Testes das três medidas novas do `gate_event_driven.py` (Felipe).

Casos sintéticos com resultado conhecido à mão, como manda o CLAUDE.md §5. O
que está sendo protegido é a decomposição em pernas: se `gap` e `intra D`
trocarem de lugar, ou se o resíduo olhar para trás em vez de para a frente, a
conclusão da 3.2 se inverte sem que nenhum número pareça absurdo.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gate_event_driven import (dias_de_salto, pernas_do_dia,  # noqa: E402
                               retorno_alinhado)


@pytest.fixture
def precos():
    """Três pregões com abertura e fechamento cravados à mão, um ticker.

    fechamento: 100, 110, 121   (+10% e +10%)
    abertura:   100, 105, 110   (gap de +5% no D2; intradiário de +4,76%)
    """
    datas = pd.bdate_range("2025-01-06", periods=3)
    fechamento = pd.DataFrame({"SPY": [100.0, 110.0, 121.0]}, index=datas)
    abertura = pd.DataFrame({"SPY": [100.0, 105.0, 110.0]}, index=datas)
    return abertura, fechamento, datas


def test_pernas_decompoem_o_retorno_do_dia(precos):
    """gap × intra reconstrói o close-to-close: nenhum pedaço se perde."""
    abertura, fechamento, datas = precos
    pernas = pernas_do_dia(abertura, fechamento, 1)
    d2 = datas[1]

    assert pernas["gap"].loc[d2, "SPY"] == pytest.approx(0.05)          # 105/100
    assert pernas["intra D"].loc[d2, "SPY"] == pytest.approx(110 / 105 - 1)
    # (1+gap)(1+intra) = 110/100 = o close-to-close do dia
    reconstruido = ((1 + pernas["gap"].loc[d2, "SPY"])
                    * (1 + pernas["intra D"].loc[d2, "SPY"]) - 1)
    assert reconstruido == pytest.approx(0.10)


def test_residuo_olha_para_a_frente_e_sessao_anterior_para_tras(precos):
    """As duas pernas com defasagem apontam para lados opostos no tempo.

    É o erro que inverteria a conclusão da 3.2 sem parecer absurdo: um resíduo
    que olha para trás mede o próprio salto e "sobra" 100% do movimento.
    """
    abertura, fechamento, datas = precos
    pernas = pernas_do_dia(abertura, fechamento, 1)
    d1, d2, d3 = datas

    # resíduo de D2 = close(D3)/close(D2) − 1, para a FRENTE
    assert pernas["resíduo 1d"].loc[d2, "SPY"] == pytest.approx(121 / 110 - 1)
    # última data não tem janela fechada -> NaN, não entra em média nenhuma
    assert np.isnan(pernas["resíduo 1d"].loc[d3, "SPY"])
    # "D−1 sessão" de D2 = o intradiário de D1, para TRÁS
    assert pernas["D−1 sessão"].loc[d2, "SPY"] == pytest.approx(
        fechamento.loc[d1, "SPY"] / abertura.loc[d1, "SPY"] - 1)
    assert np.isnan(pernas["D−1 sessão"].loc[d1, "SPY"])


def test_alinhamento_inverte_com_a_premissa_e_com_o_sinal(precos):
    """Alinhar = sinal do Δp × sinal declarado. Positivo = premissa confirmada."""
    _abertura, fechamento, datas = precos
    perna = fechamento.pct_change()  # +10% em D2 e D3
    subindo = pd.Series([1.0, 1.0, 1.0], index=datas)

    # premissa "sinal sobe → SPY sobe", e o ativo subiu: confirma, +1000 bps
    media, _n = retorno_alinhado(perna, datas[1:], subindo, {"SPY": +1})
    assert media == pytest.approx(1000.0)
    # mesma perna, premissa oposta: mesmo número com o sinal trocado
    media_oposta, _n = retorno_alinhado(perna, datas[1:], subindo, {"SPY": -1})
    assert media_oposta == pytest.approx(-1000.0)
    # sinal do poly caindo com premissa positiva dá o mesmo que subir com
    # premissa negativa — é o que faz mercados de direções opostas somarem
    caindo = -subindo
    media_caindo, _n = retorno_alinhado(perna, datas[1:], caindo, {"SPY": +1})
    assert media_caindo == pytest.approx(-1000.0)


def test_alinhamento_ignora_ativo_fora_do_livro(precos):
    """Ativo que a premissa não declara não entra na média (nem como zero)."""
    _abertura, fechamento, datas = precos
    perna = fechamento.pct_change()
    subindo = pd.Series(1.0, index=datas)
    media, _n = retorno_alinhado(perna, datas[1:], subindo, {"TLT": +1})
    assert np.isnan(media)


def test_quantil_zero_pega_todo_dia_com_sinal():
    """`q0.00` é a linha de base: todo Δp não nulo, e só os não nulos."""
    datas = pd.bdate_range("2025-01-06", periods=5)
    sinal = pd.Series([0.0, 0.01, -0.02, 0.0, 0.05], index=datas)
    assert len(dias_de_salto(sinal, 0.0)) == 3
    assert datas[0] not in dias_de_salto(sinal, 0.0)


def test_quantil_corta_pelo_modulo_e_nao_pelo_sinal():
    """Um Δp muito negativo é salto tanto quanto um muito positivo."""
    datas = pd.bdate_range("2025-01-06", periods=4)
    sinal = pd.Series([0.01, -0.50, 0.02, 0.03], index=datas)
    topo = dias_de_salto(sinal, 0.75)
    assert list(topo) == [datas[1]]


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
