"""Testes do `gate_recessao_2x2.py` (Felipe).

O que está sendo protegido é o critério de GIRO — a peça de que depende a
resposta à contradição com a D19c. Se o critério forte deixar de exigir
significância nas duas metades, ele vira o critério fraco, que mede 13 de 14
células em h = 10 e não separa candidato de ruído; se o `celula_ols` errar o
sinal esperado, o veredito inverte sem que a tabela mude de aparência.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gate_recessao_2x2 import (celula_ols, gira_de_sinal,  # noqa: E402
                               recortes_do_sinal)
from view_3_1_direcional import (componentes_expansivos,  # noqa: E402
                                 divergencia_expansiva)

LIVRO = {"XLP": +1, "XLK": -1}


@pytest.fixture
def datas():
    return pd.bdate_range("2024-01-02", periods=200)


def montar(datas, efeito):
    """Retornos em que XLP anda `efeito × sinal` no pregão seguinte, XLK ao contrário."""
    rng = np.random.default_rng(0)
    sinal = pd.Series(rng.normal(size=len(datas)), index=datas)
    movimento = (efeito * sinal).shift(1).fillna(0.0)
    return sinal, pd.DataFrame({"XLP": movimento, "XLK": -movimento}, index=datas)


def test_celula_ols_aprova_quando_as_pernas_andam_como_declarado(datas):
    sinal, retornos = montar(datas, 2.0)
    ok, _detalhe, valores, ts, _n = celula_ols(retornos, sinal, LIVRO, h=1)
    assert ok
    assert valores["XLP"] > 0 and valores["XLK"] < 0
    assert abs(ts["XLP"]) > 2


def test_celula_ols_reprova_o_livro_invertido(datas):
    """O erro que o teste existe para pegar: ler o veredito com o livro trocado."""
    sinal, retornos = montar(datas, 2.0)
    ok, _detalhe, _valores, _ts, _n = celula_ols(
        retornos, sinal, {"XLP": -1, "XLK": +1}, h=1)
    assert not ok


def test_celula_ols_enxerga_o_giro_entre_as_metades(datas):
    """Relação que inverte no meio da amostra — o caso da D19c, sintético."""
    efeito = pd.Series([2.0] * 100 + [-2.0] * 100, index=datas)
    sinal, retornos = montar(datas, efeito)
    recortes = dict(recortes_do_sinal(sinal))
    _ok1, _d1, v1, t1, _n1 = celula_ols(retornos, recortes["1ª metade"], LIVRO, h=1)
    _ok2, _d2, v2, t2, _n2 = celula_ols(retornos, recortes["2ª metade"], LIVRO, h=1)
    assert gira_de_sinal(v1, v2, t1, t2)


def test_criterio_forte_exige_significancia_nas_duas_metades():
    """A distinção que sustenta a leitura inteira do artefato."""
    v1, v2 = {"XLP": +1.0}, {"XLP": -1.0}
    assert gira_de_sinal(v1, v2)                                    # fraco
    assert not gira_de_sinal(v1, v2, {"XLP": 0.5}, {"XLP": -0.5})    # t baixo
    assert not gira_de_sinal(v1, v2, {"XLP": 3.0}, {"XLP": -0.5})    # só uma
    assert gira_de_sinal(v1, v2, {"XLP": 3.0}, {"XLP": -3.0})        # as duas


def test_mesmo_sinal_nas_duas_metades_nao_gira():
    assert not gira_de_sinal({"XLP": +1.0}, {"XLP": +2.0},
                             {"XLP": 9.0}, {"XLP": 9.0})


def test_recortes_particionam_a_amostra(datas):
    sinal = pd.Series(range(len(datas)), index=datas, dtype=float)
    recortes = dict(recortes_do_sinal(sinal))
    assert len(recortes["inteira"]) == len(datas)
    assert len(recortes["1ª metade"]) == len(datas) // 2
    assert (len(recortes["1ª metade"]) + len(recortes["2ª metade"])
            == len(recortes["inteira"]))
    assert recortes["1ª metade"].index.intersection(
        recortes["2ª metade"].index).empty


def test_componentes_reproduzem_a_discordancia_da_3_1():
    """O refactor não pode mudar o número que o `Recessao_direcional.md` publica."""
    datas = pd.bdate_range("2024-01-02", periods=300)
    rng = np.random.default_rng(1)
    p_poly = pd.Series(rng.uniform(0.1, 0.9, len(datas)), index=datas)
    spread = pd.Series(rng.normal(size=len(datas)), index=datas)
    z_poly, z_mercado = componentes_expansivos(p_poly, spread)
    esperado = divergencia_expansiva(p_poly, spread)
    pd.testing.assert_series_equal((z_poly - z_mercado).dropna(), esperado)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
