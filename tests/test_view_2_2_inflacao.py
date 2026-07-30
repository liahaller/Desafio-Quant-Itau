"""Testes sintéticos da view 2.2 (regra CLAUDE.md §5: caso com resultado conhecido).

`_fl_identidade` é SINTÉTICO — injeta identidade no lugar do stub da decisão
11a só para exercitar a matemática; em produção o default falha alto.
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from view_2_2_inflacao import build_view

ASSETS = ["SPY", "TIP", "TLT", "XLK"]


def _fl_identidade(p):
    return np.asarray(p, dtype=float)


def test_pmf_caso_conhecido():
    """PMF conhecida: E = 0.0355, breakeven 0.03, duration 8 -> Q = 0.044."""
    r = build_view(ASSETS, breakeven_10y=0.03, duration=8.0, cpi_frequencia="anual",
                   bucket_probs=[0.2, 0.5, 0.3], bucket_values=[0.03, 0.035, 0.04],
                   fl_correction=_fl_identidade)
    assert np.isclose(r.Q, 8.0 * (0.0355 - 0.03))
    assert np.allclose(r.P, [0.0, 1.0, -1.0, 0.0])
    assert np.isclose(np.abs(r.P).sum(), 2.0)  # convenção Sigma|P| = 2
    assert r.diagnostics["caminho"] == "pmf"


def test_pmf_normalizacao_de_probs_cruas():
    """Probs cruas com spread (soma 0.9) dão o mesmo E das normalizadas."""
    crua = build_view(ASSETS, 0.03, 8.0, cpi_frequencia="anual", bucket_probs=[0.18, 0.45, 0.27],
                      bucket_values=[0.03, 0.035, 0.04], fl_correction=_fl_identidade)
    limpa = build_view(ASSETS, 0.03, 8.0, cpi_frequencia="anual", bucket_probs=[0.2, 0.5, 0.3],
                       bucket_values=[0.03, 0.035, 0.04], fl_correction=_fl_identidade)
    assert np.isclose(crua.Q, limpa.Q)


def test_poly_igual_breakeven_q_zero():
    """Sem divergência, a view não pede tilt: Q = 0."""
    r = build_view(ASSETS, breakeven_10y=0.0355, duration=8.0, cpi_frequencia="anual",
                   bucket_probs=[0.2, 0.5, 0.3], bucket_values=[0.03, 0.035, 0.04],
                   fl_correction=_fl_identidade)
    assert np.isclose(r.Q, 0.0)


def test_fallback_binario():
    """p = 0.5 -> média = threshold (normal deslocada); Q = duration * (X - breakeven)."""
    r = build_view(ASSETS, breakeven_10y=0.025, duration=8.0, cpi_frequencia="anual",
                   binary_prob=(0.5, 0.5), binary_threshold=0.03, cpi_vol=0.005,
                   fl_correction=_fl_identidade)
    assert np.isclose(r.Q, 8.0 * (0.03 - 0.025))
    assert r.diagnostics["caminho"] == "binario"
    # p > 0.5 desloca a média acima do threshold
    r2 = build_view(ASSETS, 0.025, 8.0, cpi_frequencia="anual", binary_prob=(0.6, 0.4),
                    binary_threshold=0.03, cpi_vol=0.005, fl_correction=_fl_identidade)
    assert r2.diagnostics["e_poly"] > 0.03


def test_sem_mercado_view_desativada():
    """Cascata item 0: nenhum mercado de CPI -> None (não é falha)."""
    assert build_view(ASSETS, 0.03, 8.0, cpi_frequencia="anual") is None


def test_default_falha_alto_ate_decisao_11():
    """Sem fl_correction injetada, o stub da decisão 11a deve estourar."""
    try:
        build_view(ASSETS, 0.03, 8.0, cpi_frequencia="anual",
                   bucket_probs=[0.5, 0.5], bucket_values=[0.03, 0.04])
        assert False, "deveria levantar NotImplementedError (TODO DECISAO-11a)"
    except NotImplementedError:
        pass


def test_bucket_aberto_nao_resolvido_rejeitado():
    """NaN em bucket_values (bucket aberto sem valor, 11b) é rejeitado."""
    try:
        build_view(ASSETS, 0.03, 8.0, cpi_frequencia="anual", bucket_probs=[0.5, 0.5],
                   bucket_values=[np.nan, 0.04], fl_correction=_fl_identidade)
        assert False, "deveria rejeitar NaN em bucket_values"
    except ValueError:
        pass


def test_mercado_mensal_e_anualizado_antes_de_comparar():
    """Grade mensal do Polymarket (0,2% / 0,3% / 0,4%) vs breakeven anual.

    Caso conhecido: PMF degenerada em 0,3% ao mês -> (1.003)^12 - 1 = 3,6556%.
    Com breakeven de 3% e duration 8, Q = 8 * (0.036556 - 0.03) > 0 — a view
    fica COMPRADA em TIP, que é o sinal certo. Sem a anualização o mesmo dado
    daria 8 * (0.003 - 0.03) < 0: comprada em TLT por erro de unidade.
    """
    r = build_view(ASSETS, breakeven_10y=0.03, duration=8.0, cpi_frequencia="mensal",
                   bucket_probs=[0.0, 1.0, 0.0], bucket_values=[0.002, 0.003, 0.004],
                   fl_correction=_fl_identidade)
    esperado = (1.003 ** 12) - 1
    assert np.isclose(r.diagnostics["e_poly"], esperado)
    assert np.isclose(r.diagnostics["e_poly_declarado"], 0.003)
    assert np.isclose(r.Q, 8.0 * (esperado - 0.03))
    assert r.Q > 0


def test_anualizacao_entra_nos_valores_nao_na_media():
    """Jensen: anualizar os buckets != anualizar a média da PMF."""
    r = build_view(ASSETS, 0.03, 8.0, cpi_frequencia="mensal",
                   bucket_probs=[0.5, 0.5], bucket_values=[0.001, 0.005],
                   fl_correction=_fl_identidade)
    media_dos_anualizados = 0.5 * ((1.001 ** 12) - 1) + 0.5 * ((1.005 ** 12) - 1)
    anualizada_depois = (1.003 ** 12) - 1
    assert np.isclose(r.diagnostics["e_poly"], media_dos_anualizados)
    assert not np.isclose(media_dos_anualizados, anualizada_depois)


def test_frequencia_obrigatoria_e_validada():
    """Sem declarar a unidade não roda; unidade desconhecida é rejeitada."""
    try:
        build_view(ASSETS, 0.03, 8.0, bucket_probs=[0.5, 0.5],
                   bucket_values=[0.03, 0.04], fl_correction=_fl_identidade)
        assert False, "cpi_frequencia deveria ser obrigatório"
    except TypeError:
        pass
    try:
        build_view(ASSETS, 0.03, 8.0, cpi_frequencia="diaria", bucket_probs=[0.5, 0.5],
                   bucket_values=[0.03, 0.04], fl_correction=_fl_identidade)
        assert False, "deveria rejeitar frequência desconhecida"
    except ValueError:
        pass


if __name__ == "__main__":
    test_pmf_caso_conhecido()
    test_pmf_normalizacao_de_probs_cruas()
    test_poly_igual_breakeven_q_zero()
    test_fallback_binario()
    test_sem_mercado_view_desativada()
    test_default_falha_alto_ate_decisao_11()
    test_bucket_aberto_nao_resolvido_rejeitado()
    print("view_2_2_inflacao: 7 testes OK")
