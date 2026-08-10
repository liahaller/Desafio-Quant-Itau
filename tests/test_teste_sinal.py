"""Testes sintéticos do teste de sinal (`scripts/teste_sinal.py`). Felipe.

Casos com resultado conhecido de antemão — o script decide veredito de view, e
um erro de sinal aqui inverteria o veredito sem dar erro nenhum.

    python tests/test_teste_sinal.py
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from teste_sinal import medir, ols, residualizar, retorno_da_carteira  # noqa: E402


def datas(n):
    return pd.bdate_range("2025-01-01", periods=n)


def test_ols_recupera_coeficiente_conhecido():
    """y = 3 + 2x sem ruído -> coef 2, t enorme."""
    x = np.linspace(-1, 1, 50)
    coef, t, n = ols(3 + 2 * x, x)
    assert abs(coef - 2.0) < 1e-9, coef
    assert n == 50
    assert t > 1e6, t


def test_residualizar_zera_o_canal():
    """Δbe construído como combinação exata de SPY e ΔDGS10 -> resíduo ~0."""
    idx = datas(120)
    rng = np.random.default_rng(0)
    spy = pd.Series(rng.normal(0, 0.01, len(idx)), index=idx)
    dgs10 = pd.Series(np.cumsum(rng.normal(0, 0.05, len(idx))), index=idx)
    dbe = 0.4 * spy + 0.7 * dgs10.diff()
    retornos = pd.DataFrame({"SPY": spy}, index=idx)
    residuo = residualizar(dbe.dropna(), retornos, dgs10)
    assert np.abs(residuo.to_numpy()).max() < 1e-12, residuo.abs().max()


def test_residualizar_preserva_o_que_e_ortogonal():
    """Pedaço independente do canal sobrevive à residualização (corr ~ 1)."""
    idx = datas(200)
    rng = np.random.default_rng(1)
    spy = pd.Series(rng.normal(0, 0.01, len(idx)), index=idx)
    dgs10 = pd.Series(np.cumsum(rng.normal(0, 0.05, len(idx))), index=idx)
    proprio = pd.Series(rng.normal(0, 0.01, len(idx)), index=idx)
    dbe = 0.4 * spy + 0.7 * dgs10.diff() + proprio
    retornos = pd.DataFrame({"SPY": spy}, index=idx)
    residuo = residualizar(dbe.dropna(), retornos, dgs10)
    par = pd.concat([residuo, proprio], axis=1).dropna()
    assert np.corrcoef(par.iloc[:, 0], par.iloc[:, 1])[0, 1] > 0.95


def test_retorno_da_carteira_comeca_em_d_mais_1():
    """A carteira monta no CLOSE de D — o retorno de D não pode entrar."""
    idx = datas(5)
    retornos = pd.DataFrame({"A": [1.0, 0.1, 0.2, 0.3, 0.4]}, index=idx)
    assert retorno_da_carteira(retornos, idx[0], [1.0], 1) == 0.1
    assert abs(retorno_da_carteira(retornos, idx[0], [1.0], 3) - 0.6) < 1e-12
    # sem h pregões à frente -> NaN, não conta parcial
    assert np.isnan(retorno_da_carteira(retornos, idx[3], [1.0], 3))
    assert np.isnan(retorno_da_carteira(retornos, idx[0], [1.0], None))


def test_horizonte_zero_e_o_proprio_pregao():
    """`h = 0` é a exceção: o dia D entra, e só ele. É o horizonte da 15b."""
    idx = datas(5)
    retornos = pd.DataFrame({"A": [1.0, 0.1, 0.2, 0.3, 0.4]}, index=idx)
    assert retorno_da_carteira(retornos, idx[0], [1.0], 0) == 1.0
    assert retorno_da_carteira(retornos, idx[3], [1.0], 0) == 0.3
    # data fora da tabela não vira zero silencioso
    assert np.isnan(retorno_da_carteira(retornos, pd.Timestamp("2030-01-02"), [1.0], 0))


def test_medir_separa_view_certa_de_view_invertida():
    """View que acerta dá t > 0 e acerto alto; a invertida dá o espelho."""
    idx = datas(60)
    rng = np.random.default_rng(2)
    Q = rng.normal(0, 0.01, len(idx) - 1)
    retornos = pd.DataFrame({"A": np.r_[0.0, Q]}, index=idx)  # r(D+1) = Q(D)
    certa = [(idx[i], np.array([1.0]), Q[i], 1) for i in range(len(Q))]
    invertida = [(d, -P, q, h) for d, P, q, h in certa]
    coef, t, _, acerto = medir(certa, retornos, 1)
    assert coef > 0 and t > 10 and acerto > 0.95, (coef, t, acerto)
    coef_i, t_i, _, acerto_i = medir(invertida, retornos, 1)
    assert coef_i < 0 and t_i < -10 and acerto_i < 0.05, (coef_i, t_i, acerto_i)


if __name__ == "__main__":
    for nome, funcao in sorted(globals().items()):
        if nome.startswith("test_"):
            funcao()
            print(f"ok  {nome}")
    print("todos os testes passaram")
