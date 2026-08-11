"""Testes sintéticos de Σ, w_mkt e Ω de fallback (CLAUDE.md §5)."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bl_integration import bl_weights_from_views  # noqa: E402
from market_inputs import (  # noqa: E402
    breakeven_duration, equal_weights, market_weights, omega_fallback,
    regua_por_decisao, sample_covariance)

ATIVOS = ["SPY", "TIP", "TLT"]


def _retornos(n=600, seed=0):
    rng = np.random.default_rng(seed)
    return pd.DataFrame(rng.normal(scale=0.01, size=(n, 3)), columns=ATIVOS,
                        index=pd.bdate_range("2023-01-02", periods=n))


def test_sigma_recupera_covariancia_plantada():
    """Ativos independentes com vol conhecida -> Σ ~ diagonal de 1e-4."""
    sigma = sample_covariance(_retornos(), janela=500)
    assert sigma.shape == (3, 3)
    assert np.allclose(np.diag(sigma), 1e-4, rtol=0.15)
    assert abs(sigma[0, 1]) < 2e-5  # fora da diagonal ~ zero


def test_sigma_nao_olha_o_futuro():
    """Com `data`, só entram pregões ANTERIORES a ela."""
    r = _retornos()
    corte = r.index[300]
    r.loc[r.index >= corte] = 99.0  # armadilha: lixo depois do corte
    sigma = sample_covariance(r, data=corte, janela=200)
    assert np.all(np.diag(sigma) < 1e-3)  # não pegou o 99


def test_sigma_rejeita_janela_curta():
    try:
        sample_covariance(_retornos(n=10), janela=500)
        assert False, "deveria rejeitar janela curta"
    except ValueError:
        pass


def test_sigma_rejeita_mal_condicionada():
    """Dois ativos idênticos -> Σ singular -> falha alto em vez de devolver lixo."""
    r = _retornos()
    r["TLT"] = r["TIP"]
    try:
        sample_covariance(r, janela=500)
        assert False, "deveria rejeitar Σ mal condicionada"
    except ValueError as e:
        assert "condicionada" in str(e)


def test_w_mkt_e_capm():
    w = market_weights(ATIVOS)
    assert np.allclose(w, [1.0, 0.0, 0.0])
    assert np.isclose(w.sum(), 1.0)
    assert np.allclose(equal_weights(ATIVOS), 1 / 3)


def test_w_mkt_exige_ativo_de_mercado_no_universo():
    try:
        market_weights(["TIP", "TLT"])
        assert False, "deveria rejeitar universo sem SPY"
    except ValueError:
        pass


def test_omega_fallback_e_a_variancia_do_prior():
    """Com confiança 1, Ω[i,i] = P_i·τΣ·P_iᵀ exatamente."""
    sigma = np.diag([1e-4, 4e-4, 9e-4])
    P = np.array([[1.0, -1.0, 0.0], [0.0, 0.0, 1.0]])
    tau = 0.002
    omega = omega_fallback(P, sigma, tau)
    assert np.allclose(np.diag(omega), [tau * 5e-4, tau * 9e-4])
    assert np.allclose(omega - np.diag(np.diag(omega)), 0.0)  # diagonal


def test_omega_incerteza_escala_a_diagonal():
    """Incerteza MAIOR = Ω maior = MENOS peso na view (o sinal que o nome do
    argumento antigo, `confianca`, dizia ao contrário)."""
    sigma = np.diag([1e-4, 4e-4, 9e-4])
    P = np.array([[1.0, -1.0, 0.0]])
    base = omega_fallback(P, sigma, 0.002)
    dobro = omega_fallback(P, sigma, 0.002, incerteza=[2.0])
    assert np.allclose(np.diag(dobro), 2 * np.diag(base))
    for ruim in ([0.0], [-1.0], [1.0, 1.0]):
        try:
            omega_fallback(P, sigma, 0.002, incerteza=ruim)
            assert False, f"deveria rejeitar incerteza {ruim}"
        except ValueError:
            pass


def test_sem_view_a_carteira_e_o_benchmark():
    """Fecha o circuito: com w_mkt do CAPM e nenhuma view ativa, o otimizador
    devolve exatamente comprar e segurar SPY (caso neutro da decisão 8)."""
    sigma = sample_covariance(_retornos(), janela=500)
    w_mkt = market_weights(ATIVOS)
    w, _ = bl_weights_from_views(sigma, w_mkt, tau=0.002, delta=3.0,
                                 view_results=[None, None])
    assert np.allclose(w, w_mkt)


def test_breakeven_duration_recupera_o_coeficiente_plantado():
    """Par que rende 6x o Δbreakeven mais ruído -> duration medida ~ 6."""
    rng = np.random.default_rng(1)
    dbe = pd.Series(rng.normal(scale=0.0005, size=400),
                    index=pd.bdate_range("2024-01-01", periods=400))
    par = 6.0 * dbe + rng.normal(scale=1e-5, size=400)
    assert breakeven_duration(par, dbe) == pytest.approx(6.0, rel=0.05)


def test_breakeven_duration_exige_amostra():
    curta = pd.Series(np.zeros(30), index=pd.bdate_range("2024-01-01", periods=30))
    with pytest.raises(ValueError, match="amostra curta"):
        breakeven_duration(curta, curta)


# --- régua da Lia lida do CSV (D25c) -----------------------------------------

_COLUNAS = "data,view,selecionado,ativa,c_nivel1\n"


def _csv_regua(tmp_path, linhas, nome="c_por_decisao.csv"):
    caminho = tmp_path / nome
    caminho.write_text(_COLUNAS + "".join(l + "\n" for l in linhas), encoding="utf-8")
    return caminho


def test_regua_filtra_pelas_views_vivas_e_escala_pelo_nivel(tmp_path):
    """Linha sem view viva é descartada; o nível é EXPOENTE (c_nivel1 ** nivel).

    O caso é o real: o CSV traz a matriz cheia (três views no dia) e o loop só
    tem duas vivas — a terceira é sobra, e sobra vira `ValueError` no
    `aplicar_veto` se chegar lá.
    """
    csv = _csv_regua(tmp_path, [
        "2025-03-10,2.2_inflacao,True,True,2.0",
        "2025-03-10,2.3_fed,True,True,1.5",
        "2025-03-10,incerteza_anuncio,True,True,1.1",   # não está viva no loop
        "2025-03-10,2.2_inflacao,False,True,9.9",       # slot não selecionado
    ])
    vivas = ["2.2_inflacao", "2.3_fed"]

    ativa, c = regua_por_decisao(csv)("2025-03-10", vivas)
    assert sorted(ativa) == vivas and sorted(c) == vivas   # a terceira ficou fora
    assert c == {"2.2_inflacao": 2.0, "2.3_fed": 1.5}

    _, c3 = regua_por_decisao(csv, nivel=3)("2025-03-10", vivas)
    assert c3 == {"2.2_inflacao": 8.0, "2.3_fed": 3.375}

    # nível 0 = He-Litterman puro: a régua some sem precisar ser desligada
    _, c0 = regua_por_decisao(csv, nivel=0)("2025-03-10", vivas)
    assert set(c0.values()) == {1.0}


def test_regua_devolve_o_veto_e_nao_inventa_c_na_linha_inativa(tmp_path):
    """`ativa = False` vem com `c_nivel1` vazio — o NaN passa, não vira 1,0."""
    csv = _csv_regua(tmp_path, ["2025-03-10,2.2_inflacao,True,False,"])
    ativa, c = regua_por_decisao(csv)("2025-03-10", ["2.2_inflacao"])
    assert ativa == {"2.2_inflacao": False}
    assert np.isnan(c["2.2_inflacao"])


def test_regua_com_view_viva_sem_linha_falha_alto(tmp_path):
    """Chave faltando é erro no `aplicar_veto` — nunca `c = 1` por default."""
    from bl_integration import aplicar_veto
    from views_common import ViewResult

    csv = _csv_regua(tmp_path, ["2025-03-10,2.2_inflacao,True,True,1.2"])
    viva = ViewResult(P=np.array([1.0, -1.0, 0.0]), Q=0.01,
                      diagnostics={"view": "2.3_fed", "horizonte_q_dias": 1})
    with pytest.raises(ValueError, match="não casa"):
        aplicar_veto([viva], *regua_por_decisao(csv)("2025-03-10", ["2.3_fed"]))


def test_regua_recusa_csv_fora_da_convencao(tmp_path):
    """c < 1 seria confiança ACIMA do fallback — a régua só tira peso."""
    csv = _csv_regua(tmp_path, ["2025-03-10,2.2_inflacao,True,True,0.8"])
    with pytest.raises(ValueError, match="c_nivel1 < 1"):
        regua_por_decisao(csv)

    vazio = _csv_regua(tmp_path, ["2025-03-10,2.2_inflacao,True,True,"], "vazio.csv")
    with pytest.raises(ValueError, match="linha ATIVA sem"):
        regua_por_decisao(vazio)

    with pytest.raises(ValueError, match="expoente"):
        regua_por_decisao(csv, nivel=-1)


def test_regua_recusa_data_que_nao_cobre(tmp_path):
    csv = _csv_regua(tmp_path, ["2025-03-10,2.2_inflacao,True,True,1.2"])
    with pytest.raises(ValueError, match="não cobre"):
        regua_por_decisao(csv)("2025-03-11", ["2.2_inflacao"])
