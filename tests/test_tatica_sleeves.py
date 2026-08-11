"""Testes da camada tática v2 (`src/tatica_sleeves.py`). Felipe.

O que está sendo protegido são as quatro peças em que um erro NÃO apareceria
como exceção — sairia como número plausível no backtest:

  1. o hedge, que é o que faz o livro ser spread e não beta disfarçado;
  2. a tradução da perna sintética (`XLP⊥`) para o universo negociável — errar
     a ponta de SPY deixa a carteira com exposição direcional silenciosa;
  3. o peso igual dentro do bloco (item 3 da D28): média, não soma;
  4. o veto da D24 (item 2), que tem de DORMIR em vez de herdar a direção de
     ontem quando falta leitura.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from config import ASSETS  # noqa: E402
from tatica_sleeves import (MINIMO_PREGOES, SUFIXO, Sleeve,  # noqa: E402
                            hedge_betas, neutraliza, pernas_neutras,
                            sleeve_overlay)

LIVRO = {"XLP": +1, "XLK": -1}
DELTA = 3.0
N = 400


@pytest.fixture
def mundo():
    """XLP e XLK com beta 2 e 0,5 contra o SPY, mais idiossincrático oposto.

    Betas DIFERENTES de propósito: com betas iguais a ponta de hedge do spread
    cancelaria sozinha, e o teste da tradução passaria mesmo com a conta errada.
    """
    rng = np.random.default_rng(0)
    datas = pd.bdate_range("2020-01-01", periods=N)
    mercado = pd.Series(rng.normal(0, 0.01, N), index=datas)
    idio = pd.Series(rng.normal(0, 0.01, N), index=datas)
    tabela = pd.DataFrame(0.0, index=datas, columns=list(ASSETS))
    tabela["SPY"] = mercado
    tabela["XLP"] = 2.0 * mercado + idio
    tabela["XLK"] = 0.5 * mercado - idio
    return tabela


@pytest.fixture
def crenca(mundo):
    """`p` que sobe quando o idiossincrático de XLP vai subir no dia seguinte.

    É a premissa do livro construída à mão: sinal sobe -> XLP bate XLK. Sem
    isso o μ sairia zero e os testes de tamanho não distinguiriam nada.
    """
    idio = mundo["XLP"] - 2.0 * mundo["SPY"]
    return (idio.shift(-1).fillna(0.0) * 10).cumsum()


def montar(mundo):
    tickers = sorted(LIVRO)
    return (pernas_neutras(mundo, tickers).dropna(),
            hedge_betas(mundo, tickers))


def test_o_hedge_remove_o_mercado_da_perna(mundo):
    """Sem isto o resto do módulo mede beta, não spread."""
    estendido, _ = montar(mundo)
    for ticker in LIVRO:
        crua = estendido[ticker].corr(estendido["SPY"])
        neutra = estendido[f"{ticker}{SUFIXO}"].corr(estendido["SPY"])
        assert abs(neutra) < abs(crua)
        assert abs(neutra) < 0.1


def test_o_beta_do_hedge_e_defasado(mundo):
    """β de D só pode conhecer até D−1 — a proibição de lookahead da D7.4."""
    betas = hedge_betas(mundo, sorted(LIVRO))
    assert betas.iloc[:MINIMO_PREGOES].isna().all().all()
    truncado = hedge_betas(mundo.iloc[:-1], sorted(LIVRO))
    ultima = truncado.index[-1]
    assert betas.loc[ultima, "XLP"] == pytest.approx(truncado.loc[ultima, "XLP"])


def test_a_ponta_de_spy_replica_a_perna_sintetica(mundo, crenca):
    """`w` em `XLP⊥` = `w` em XLP mais `−w·β` em SPY. Errar aqui deixa
    exposição direcional silenciosa na carteira."""
    estendido, betas = montar(mundo)
    data = estendido.index[-1]
    overlay = sleeve_overlay(list(ASSETS), estendido, betas,
                             [Sleeve("t", crenca, LIVRO, (1,))], data, DELTA)
    assert overlay is not None
    dw = pd.Series(overlay.dw, index=list(ASSETS))
    esperado = -(dw["XLP"] * betas.loc[data, "XLP"]
                 + dw["XLK"] * betas.loc[data, "XLK"])
    assert dw["SPY"] == pytest.approx(esperado)


def test_o_bloco_entra_com_peso_igual_e_nao_somado(mundo, crenca):
    """Item 3 da D28: três lookbacks são UMA posição medida três vezes.

    Se o bloco somasse, o `dw` do bloco seria ~3× o de uma perna só; com média
    ele fica na mesma ordem de grandeza.
    """
    estendido, betas = montar(mundo)
    data = estendido.index[-1]

    def soma_abs(lookbacks):
        r = sleeve_overlay(list(ASSETS), estendido, betas,
                           [Sleeve("t", crenca, LIVRO, lookbacks)], data, DELTA)
        return r.diagnostics["soma_abs_dw"]

    uma, bloco = soma_abs((1,)), soma_abs((1, 1, 1))
    assert bloco == pytest.approx(uma)


def test_sleeves_no_mesmo_livro_somam_o_mu_uma_vez_so(mundo, crenca):
    """Item 11: duas sleeves idênticas dão o DOBRO, não duas posições soltas
    que se somariam de outro jeito — e a linearidade do `inv(δΣ)` tem de valer."""
    estendido, betas = montar(mundo)
    data = estendido.index[-1]
    uma = sleeve_overlay(list(ASSETS), estendido, betas,
                         [Sleeve("a", crenca, LIVRO, (1,))], data, DELTA)
    duas = sleeve_overlay(list(ASSETS), estendido, betas,
                          [Sleeve("a", crenca, LIVRO, (1,)),
                           Sleeve("b", crenca, LIVRO, (1,))], data, DELTA)
    assert duas.diagnostics["sleeves_ativas"] == 2
    np.testing.assert_allclose(duas.dw, 2.0 * np.asarray(uma.dw), rtol=1e-9)


def test_veto_da_d24_dorme_em_vez_de_herdar(mundo, crenca):
    """Leitura ausente na véspera desativa a perna. O erro que isto pega é a
    sleeve carregar a direção de ontem num dia em que o mercado não leu."""
    estendido, betas = montar(mundo)
    data = estendido.index[-1]
    furada = crenca.copy()
    furada.loc[furada.index[furada.index < data][-2:]] = np.nan
    assert sleeve_overlay(list(ASSETS), estendido, betas,
                          [Sleeve("t", furada, LIVRO, (1,))], data, DELTA) is None


def test_sem_eventos_suficientes_a_camada_dorme(mundo):
    """Menos de 2 eventos fechados -> `estimate_drift_mu` devolve None, e a
    sleeve não pode chutar tamanho."""
    estendido, betas = montar(mundo)
    data = estendido.index[MINIMO_PREGOES + 2]
    plana = pd.Series(0.0, index=mundo.index)
    assert sleeve_overlay(list(ASSETS), estendido, betas,
                          [Sleeve("t", plana, LIVRO, (1,))], data, DELTA) is None


def test_a_sigma_nao_olha_o_futuro(mundo, crenca):
    """O `dw` de D tem de sair igual quando o futuro é cortado da tabela."""
    estendido, betas = montar(mundo)
    data = estendido.index[-30]
    sleeves = [Sleeve("t", crenca, LIVRO, (1,))]
    cheio = sleeve_overlay(list(ASSETS), estendido, betas, sleeves, data, DELTA)
    cortado = sleeve_overlay(list(ASSETS), estendido[estendido.index <= data],
                             betas, sleeves, data, DELTA)
    np.testing.assert_allclose(cheio.dw, cortado.dw, rtol=1e-9)


def test_neutraliza_preserva_os_sinais():
    assert neutraliza(LIVRO) == {f"XLP{SUFIXO}": +1, f"XLK{SUFIXO}": -1}


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
