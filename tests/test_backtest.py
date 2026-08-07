"""Testes sintéticos do loop de backtest (I5) — CLAUDE.md §5.

O teste do motor de custo é OBRIGATÓRIO por decisão (D8): ir de w = 0 a
w = 1 num ativo tem de cobrar exatamente `custo_bps`. Errar a unidade aqui
(por lado vs total, fração vs bps) não dá erro em lugar nenhum — só devolve
uma estratégia falsamente lucrativa.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from backtest import (  # noqa: E402
    BPS, cap_leverage, carry_cost, derived_weights, reversal_share,
    run_backtest, summary, transaction_cost)
from views_common import ViewResult  # noqa: E402
from taticas_common import OverlayResult  # noqa: E402

ATIVOS = ["SPY", "TIP", "TLT"]


def _retornos(n=40, seed=0, escala=0.01):
    rng = np.random.default_rng(seed)
    return pd.DataFrame(rng.normal(scale=escala, size=(n, 3)), columns=ATIVOS,
                        index=pd.bdate_range("2025-01-02", periods=n))


def _sigma():
    return np.diag([1e-4, 4e-5, 9e-5])


def _sem_views(_data):
    return _sigma(), [None, None], []


# --- motor de custo (obrigatório, D8) ---------------------------------------

def test_custo_de_zero_a_um_cobra_exatamente_c():
    """A âncora de unidade: entrar 100% num ativo custa `custo_bps`, uma vez."""
    custo, giro = transaction_cost([1.0, 0.0, 0.0], [0.0, 0.0, 0.0], custo_bps=2.0)
    assert giro == pytest.approx(1.0)
    assert custo == pytest.approx(2.0 * BPS)


def test_custo_conta_os_dois_lados():
    """Trocar 100% de um ativo por outro é giro 2 — comprou e vendeu."""
    custo, giro = transaction_cost([0.0, 1.0, 0.0], [1.0, 0.0, 0.0], custo_bps=2.0)
    assert giro == pytest.approx(2.0)
    assert custo == pytest.approx(2.0 * 2.0 * BPS)


def test_custo_e_medido_contra_o_peso_derivado():
    """D8: o peso que andou sozinho não é giro. Alvo igual ao derivado -> 0."""
    w = np.array([0.5, 0.3, 0.2])
    derivado = derived_weights(w, [0.02, 0.0, -0.01])
    custo, giro = transaction_cost(derivado, derivado, custo_bps=2.0)
    assert giro == pytest.approx(0.0)
    assert custo == pytest.approx(0.0)
    # e o derivado NÃO é o alvo de ontem: o ativo que subiu ganhou peso
    assert derivado[0] > w[0]


def test_peso_derivado_soma_um_quando_investido():
    """Carteira 100% investida continua somando 1 depois do drift."""
    assert derived_weights([0.6, 0.4, 0.0], [0.05, -0.02, 0.0]).sum() == pytest.approx(1.0)


def test_ruina_falha_alto():
    """1 + w·r <= 0 é ruína com peso irrestrito — não é retorno a compor."""
    with pytest.raises(ValueError, match="patrimônio"):
        derived_weights([3.0, 0.0, 0.0], [-0.5, 0.0, 0.0])


def test_carrego_zero_sem_alavancagem_nem_venda():
    assert carry_cost([0.5, 0.3, 0.2]) == pytest.approx(0.0)


def test_carrego_cobra_alavancagem_e_aluguel():
    """Com taxa declarada != 0 as duas parcelas aparecem (hoje config = 0,0)."""
    c = carry_cost([2.0, -0.5, 0.0], financiamento_bps_ano=100.0,
                   aluguel_bps_ano=50.0, pregoes_por_ano=250)
    esperado = (100.0 * BPS * 0.5 + 50.0 * BPS * 0.5) / 250
    assert c == pytest.approx(esperado)


# --- decomposição do giro (obrigatória, D8) ---------------------------------

def test_reversao_total_quando_a_posicao_e_desfeita_no_dia_seguinte():
    trades = pd.DataFrame({"SPY": [1.0, -1.0, 0.0]})
    assert reversal_share(trades, janela=2) == pytest.approx(0.5)  # metade do giro é o desfazer


def test_reversao_zero_quando_a_carteira_so_anda_para_um_lado():
    trades = pd.DataFrame({"SPY": [0.5, 0.5, 0.5]})
    assert reversal_share(trades, janela=2) == pytest.approx(0.0)


def test_reversao_fora_da_janela_nao_conta():
    """Desfazer no 4º dia não é reversão de 1–2 pregões."""
    trades = pd.DataFrame({"SPY": [1.0, 0.0, 0.0, -1.0]})
    assert reversal_share(trades, janela=2) == pytest.approx(0.0)


def test_reversao_sem_giro_e_nan():
    assert np.isnan(reversal_share(pd.DataFrame({"SPY": [0.0, 0.0]})))


# --- loop --------------------------------------------------------------------

def test_sem_view_ativa_replica_o_benchmark():
    """Caso neutro da D8: nenhuma view -> w = w_mkt todo dia -> retorno do SPY.

    Sem giro depois da entrada, o único custo é o do primeiro dia.
    """
    r = _retornos()
    w_mkt = np.array([1.0, 0.0, 0.0])
    res = run_backtest(r, _sem_views, w_mkt)
    assert np.allclose(res.pesos.to_numpy(), np.tile(w_mkt, (len(r), 1)))
    assert res.diario["r_bruto"].to_numpy() == pytest.approx(r["SPY"].to_numpy())
    assert res.diario["giro"].iloc[0] == pytest.approx(1.0)   # entrou na carteira
    assert res.diario["giro"].iloc[1:].sum() == pytest.approx(0.0)  # e ficou


def test_view_ativa_move_a_carteira_e_gera_giro():
    """Uma view com Q positivo em TIP tira peso do prior e faz a carteira girar."""
    r = _retornos()
    view = ViewResult(P=np.array([0.0, 1.0, -1.0]), Q=0.002,
                      diagnostics={"view": "sintetica", "horizonte_q_dias": 1})

    def montar(_data):
        return _sigma(), [view], []

    res = run_backtest(r, montar, np.array([1.0, 0.0, 0.0]))
    assert (res.diario["n_views"] == 1).all()
    assert res.pesos["TIP"].iloc[0] > 0        # comprou a ponta longa da view
    assert res.pesos["TLT"].iloc[0] < 0        # e vendeu a curta
    assert res.diario["giro"].iloc[1:].sum() > 0  # rebalanceia contra o drift


def test_tatica_soma_por_cima_sem_tocar_o_bl():
    """A camada tática é overlay: o w do BL fica intocado e o dw entra somando."""
    r = _retornos()
    w_mkt = np.array([1.0, 0.0, 0.0])
    overlay = OverlayResult(dw=np.array([0.1, 0.0, 0.0]),
                            diagnostics={"tatica": "sintetica"})

    def montar(_data):
        return _sigma(), [None], [overlay, None]

    res = run_backtest(r, montar, w_mkt)
    assert res.pesos["SPY"].iloc[0] == pytest.approx(1.1)
    assert (res.diario["n_taticas"] == 1).all()  # o None não conta como ativa


def test_custo_reduz_o_retorno_liquido_na_conta_do_dia():
    r = _retornos()
    res = run_backtest(r, _sem_views, np.array([1.0, 0.0, 0.0]), custo_bps=5.0)
    d = res.diario
    assert d["r_liquido"].to_numpy() == pytest.approx(
        (d["r_bruto"] - d["custo"] - d["carrego"]).to_numpy())
    assert d["custo"].iloc[0] == pytest.approx(5.0 * BPS)  # giro 1 na entrada


def test_custo_maior_derruba_o_liquido():
    r = _retornos()
    barato = run_backtest(r, _sem_views, np.array([1.0, 0.0, 0.0]), custo_bps=0.0)
    caro = run_backtest(r, _sem_views, np.array([1.0, 0.0, 0.0]), custo_bps=10.0)
    assert caro.diario["r_liquido"].sum() < barato.diario["r_liquido"].sum()


def test_breakeven_e_o_custo_que_zera_o_retorno():
    """Rodar COM o custo de breakeven tem de dar retorno somado ~ zero.

    Retornos determinísticos em que a view ACERTA (TIP acima de TLT todo dia):
    com aleatório o bruto pode ser negativo e o breakeven sai negativo, que é
    uma leitura legítima ("perde mesmo de graça") mas não testa a identidade.
    """
    r = pd.DataFrame({"SPY": 0.001, "TIP": 0.002, "TLT": -0.002},
                     index=pd.bdate_range("2025-01-02", periods=20))
    w_mkt = np.array([1.0, 0.0, 0.0])
    view = ViewResult(P=np.array([0.0, 1.0, -1.0]), Q=0.002,
                      diagnostics={"view": "sintetica", "horizonte_q_dias": 1})

    def montar(_data):
        return _sigma(), [view], []

    res = run_backtest(r, montar, w_mkt, custo_bps=0.0)
    assert res.diario["r_bruto"].sum() > 0  # senão o breakeven não é um custo
    breakeven = summary(res)["custo de breakeven (bps por lado)"]
    no_breakeven = run_backtest(r, montar, w_mkt, custo_bps=breakeven)
    assert no_breakeven.diario["r_bruto"].sum() - no_breakeven.diario["custo"].sum() \
        == pytest.approx(0.0, abs=1e-12)


def test_teto_de_alavancagem_corta_e_preserva_a_direcao():
    """Escala todas as pontas pelo mesmo fator: Σ|w| bate o teto, razões ficam."""
    w = np.array([4.0, -2.0, 2.0])       # Σ|w| = 8
    cortado = cap_leverage(w, teto=2.0)
    assert np.abs(cortado).sum() == pytest.approx(2.0)
    assert cortado / np.abs(cortado).sum() == pytest.approx(w / np.abs(w).sum())


def test_teto_nao_mexe_em_carteira_abaixo_dele():
    w = np.array([0.6, -0.2, 0.1])
    assert cap_leverage(w, teto=3.0) == pytest.approx(w)
    assert cap_leverage(w, teto=None) == pytest.approx(w)  # None = D8 literal


def test_teto_no_loop_limita_todo_dia():
    """Com view agressiva o BL estoura; com teto a carteira fica dentro dele."""
    r = _retornos(escala=0.002)
    view = ViewResult(P=np.array([0.0, 1.0, -1.0]), Q=0.01,
                      diagnostics={"view": "sintetica", "horizonte_q_dias": 1})

    def montar(_data):
        return _sigma(), [view], []

    solto = run_backtest(r, montar, np.array([1.0, 0.0, 0.0]))
    preso = run_backtest(r, montar, np.array([1.0, 0.0, 0.0]), teto_alavancagem=2.0)
    assert solto.diario["alavancagem"].max() > 2.0
    assert preso.diario["alavancagem"].max() == pytest.approx(2.0)


def test_teto_no_tilt_preserva_a_perna_de_mercado():
    """Corta o desvio de w_mkt e deixa o prior inteiro (a outra metade da D12)."""
    w_mkt = np.array([1.0, 0.0, 0.0])
    w = np.array([0.5, 2.0, -2.0])                  # tilt = (-0,5; 2; -2), Σ|tilt| = 4,5
    cortado = cap_leverage(w, teto=0.9, w_ref=w_mkt)
    tilt = cortado - w_mkt
    assert np.abs(tilt).sum() == pytest.approx(0.9)         # o teto morde o tilt
    assert tilt / np.abs(tilt).sum() == pytest.approx((w - w_mkt) / 4.5)  # direção fica
    assert np.abs(cortado).sum() > 0.9              # Σ|w| NÃO é o que está limitado


def test_atribuicao_do_dia_fecha_com_o_bruto():
    """r_bruto = perna de mercado + tilt, exato — é decomposição, não estimativa."""
    r = _retornos(escala=0.002)
    view = ViewResult(P=np.array([0.0, 1.0, -1.0]), Q=0.01,
                      diagnostics={"view": "sintetica", "horizonte_q_dias": 1})
    res = run_backtest(r, lambda _d: (_sigma(), [view], []), np.array([1.0, 0.0, 0.0]),
                       teto_alavancagem=2.0)
    d = res.diario
    assert (d["r_mercado"] + d["r_tilt"]).to_numpy() == pytest.approx(d["r_bruto"].to_numpy())
    # a perna de mercado é o benchmark: w_mkt = 100% do primeiro ativo
    assert d["r_mercado"].to_numpy() == pytest.approx(r[r.columns[0]].to_numpy())


def test_data_fora_da_tabela_falha_alto():
    r = _retornos()
    with pytest.raises(ValueError, match="fora da tabela"):
        run_backtest(r, _sem_views, np.array([1.0, 0.0, 0.0]),
                     datas=pd.DatetimeIndex(["2030-01-02"]))


def test_w_mkt_desalinhado_falha_alto():
    with pytest.raises(ValueError, match="não alinha"):
        run_backtest(_retornos(), _sem_views, np.array([1.0, 0.0]))
