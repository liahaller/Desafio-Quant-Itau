"""Teste da `neutralidade` do `gate_transversal.py` (Felipe).

O que está sendo protegido é a única medida que sustenta (ou derruba) a metade
estrutural da tese transversal: se o spread for montado com os pesos somando em
vez de subtraindo, um livro que é beta puro passa por neutro.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from config import ASSETS  # noqa: E402
from gate_transversal import neutralidade  # noqa: E402


@pytest.fixture
def retornos():
    """Dois setores com beta 1 contra o SPY e ruído idiossincrático oposto."""
    # 4000 pregões, não 400: o spread cancela o mercado por construção, mas a
    # correlação amostral tem erro ~1/√n. Com n curto o teste rejeitaria a
    # medida certa (mediu 0,086 com n = 400, dentro de 2 erros-padrão).
    rng = np.random.default_rng(0)
    datas = pd.bdate_range("2010-01-04", periods=4000)
    mercado = pd.Series(rng.normal(0, 0.01, len(datas)), index=datas)
    idio = pd.Series(rng.normal(0, 0.01, len(datas)), index=datas)
    tabela = pd.DataFrame(0.0, index=datas, columns=list(ASSETS))
    tabela["SPY"] = mercado
    tabela["XLP"] = mercado + idio
    tabela["XLK"] = mercado - idio
    return tabela


def test_spread_de_betas_iguais_e_neutro(retornos):
    """+XLP −XLK cancela o mercado: sobra só o idiossincrático."""
    assert abs(neutralidade(retornos, {"XLP": +1, "XLK": -1})) < 0.05


def test_livro_com_os_dois_lados_comprados_NAO_e_neutro(retornos):
    """O erro que o teste existe para pegar: somar em vez de subtrair."""
    assert neutralidade(retornos, {"XLP": +1, "XLK": +1}) > 0.9


def test_perna_unica_e_o_proprio_ativo(retornos):
    """Livro de uma perna só devolve a correlação do ativo com o SPY."""
    medido = neutralidade(retornos, {"XLP": +1})
    esperado = retornos["XLP"].corr(retornos["SPY"])
    assert medido == pytest.approx(esperado)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
