"""Testes sintéticos da integração (regra CLAUDE.md §5). τ/δ sintéticos,
marcados como tal — os reais vêm de decisão registrada."""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bl_integration import aplicar_veto, bl_weights_from_views, stack_views
from views_common import ViewResult

SIGMA = np.array([[0.04, 0.01, 0.00],
                  [0.01, 0.03, 0.01],
                  [0.00, 0.01, 0.02]])
W_MKT = np.array([0.5, 0.3, 0.2])
TAU, DELTA = 0.05, 2.5  # sintéticos


def _view(P, Q, nome, horizonte=1):
    return ViewResult(P=np.asarray(P, dtype=float), Q=Q,
                      diagnostics={"view": nome, "horizonte_q_dias": horizonte})


def test_stack_rejeita_horizontes_misturados():
    """DECISAO-4.1: Q de 1 dia e Q acumulado em k dias não somam."""
    evento = _view([1.0, -1.0, 0.0], 0.02, "2.3_fed", horizonte=1)
    defasada = _view([0.0, 1.0, -1.0], 0.03, "2.4_eleitoral", horizonte=3)
    try:
        stack_views([evento, defasada], n_assets=3)
        assert False, "deveria rejeitar horizontes diferentes"
    except ValueError as erro:
        assert "DECISAO-4.1" in str(erro)

    # horizonte não declarado também não se mistura com horizonte declarado
    sem_horizonte = ViewResult(P=np.zeros(3), Q=0.01, diagnostics={"view": "2.2"})
    try:
        stack_views([evento, sem_horizonte], n_assets=3)
        assert False, "deveria rejeitar horizonte não declarado junto de declarado"
    except ValueError:
        pass

    # mesmo horizonte passa
    P, Q, _ = stack_views([evento, _view([0.0, 1.0, -1.0], 0.03, "b", horizonte=1)],
                          n_assets=3)
    assert P.shape == (2, 3)


def test_stack_filtra_none_e_preserva_ordem():
    """None (view desativada) sai; ordem e diagnostics preservados."""
    v1 = _view([1.0, -1.0, 0.0], 0.02, "a")
    v2 = _view([0.0, 1.0, -1.0], -0.01, "b")
    P, Q, diags = stack_views([None, v1, None, v2], n_assets=3)
    assert P.shape == (2, 3) and np.allclose(Q, [0.02, -0.01])
    assert [d["view"] for d in diags] == ["a", "b"]
    # P desalinhado com o universo é rejeitado
    try:
        stack_views([_view([1.0, -1.0], 0.02, "c")], n_assets=3)
        assert False, "deveria rejeitar P de tamanho errado"
    except ValueError:
        pass


def test_sem_view_ativa_volta_w_mkt():
    """Caso neutro da decisão 8: todas desativadas -> w = w_mkt exato."""
    w, info = bl_weights_from_views(SIGMA, W_MKT, TAU, DELTA, [None, None])
    assert np.allclose(w, W_MKT)
    assert info["P"] is None and info["diagnostics"] == []


def test_confianca_zero_encosta_no_prior():
    """Ω enorme (confiança ~0) -> pesos ~ w_mkt (a view desbota)."""
    v = _view([1.0, -1.0, 0.0], 0.05, "a")
    w, _ = bl_weights_from_views(SIGMA, W_MKT, TAU, DELTA, [v], omega=np.array([[1e9]]))
    assert np.allclose(w, W_MKT, atol=1e-4)


def test_view_altista_tilta_na_direcao_certa():
    """View long ativo 0 / short ativo 1 com Q acima do prior -> w0 sobe, w1 cai."""
    v = _view([1.0, -1.0, 0.0], 0.05, "a")
    w, info = bl_weights_from_views(SIGMA, W_MKT, TAU, DELTA, [v], omega=np.array([[1e-4]]))
    assert info["P"].shape == (1, 3)
    assert w[0] > W_MKT[0] and w[1] < W_MKT[1]


def test_omega_obrigatorio_com_view_ativa():
    """View ativa sem Ω da Lia -> falha alto (nunca inventar confiança)."""
    v = _view([1.0, -1.0, 0.0], 0.05, "a")
    try:
        bl_weights_from_views(SIGMA, W_MKT, TAU, DELTA, [v])
        assert False, "deveria exigir omega"
    except ValueError:
        pass


def test_aplicar_veto_casa_por_nome_e_ignora_os_none_da_cascata():
    """Os dicts da Lia são chaveados por view; os None da cascata não aparecem
    neles. O dict certo veta a view certa, qualquer que seja a posição."""
    views = [None, _view([1, -1, 0], 0.02, "A"), None, _view([0, 1, -1], 0.03, "B")]
    saida, incerteza = aplicar_veto(views, {"B": False, "A": True},  # ordem do dict é irrelevante
                                    incerteza={"A": 2.0, "B": 9.0})
    assert [r.diagnostics["view"] if r else None for r in saida] == [None, "A", None, None]
    # o `c` do vetado sai junto — o que sobra tem de casar com o P empilhado
    assert incerteza.tolist() == [2.0]
    P, _, _ = stack_views(saida, n_assets=3)
    assert P.shape[0] == len(incerteza)


def test_aplicar_veto_rejeita_chave_que_nao_casa():
    """O erro que a chave por nome existe para converter em exceção: dict com
    view faltando, sobrando ou com nome errado não roda calado."""
    views = [None, _view([1, -1, 0], 0.02, "A"), _view([0, 1, -1], 0.03, "B")]
    for ruim in ({"A": True}, {"A": True, "B": True, "C": True}, {"A": True, "2.3_fed": True}):
        try:
            aplicar_veto(views, ruim)
            assert False, f"deveria rejeitar ativa={ruim}"
        except ValueError:
            pass
    # incerteza é validada com o mesmo rigor de `ativa`
    try:
        aplicar_veto(views, {"A": True, "B": True}, incerteza={"A": 2.0})
        assert False, "deveria rejeitar incerteza incompleta"
    except ValueError:
        pass


def test_veto_total_devolve_a_carteira_de_mercado():
    """Vetar todas as views é o limite exato de Ω -> infinito: w = w_mkt, sem
    número mágico e sem resíduo (item 4c da resposta da Lia)."""
    views = [_view([1, -1, 0], 0.02, "A")]
    saida, _ = aplicar_veto(views, {"A": False})
    w, info = bl_weights_from_views(SIGMA, W_MKT, TAU, DELTA, saida)
    assert info["P"] is None
    assert np.allclose(w, W_MKT)


# O bloco fica no FIM do arquivo: estava no meio, e os 4 testes definidos
# depois dele nunca rodavam por `python tests/test_bl_integration.py`.
if __name__ == "__main__":
    test_stack_rejeita_horizontes_misturados()
    test_stack_filtra_none_e_preserva_ordem()
    test_sem_view_ativa_volta_w_mkt()
    test_confianca_zero_encosta_no_prior()
    test_view_altista_tilta_na_direcao_certa()
    test_omega_obrigatorio_com_view_ativa()
    test_aplicar_veto_casa_por_nome_e_ignora_os_none_da_cascata()
    test_aplicar_veto_rejeita_chave_que_nao_casa()
    test_veto_total_devolve_a_carteira_de_mercado()
    print("bl_integration: 9 testes OK")
