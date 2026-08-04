"""Testes sintéticos da view 2.2 (regra CLAUDE.md §5: caso com resultado conhecido).

`_fl_identidade` é SINTÉTICO — em produção o default é γ = 1,0, que também é
identidade (decisão 1.1), mas os testes injetam explicitamente para não
depender do default.

`DUR_LONG`/`DUR_SHORT` são as durations MEDIDAS em 2026-08-04 (TIP 4,99 anos,
TLT 15,92); aqui entram arredondadas só para dar conta redonda no teste.
`dias_ate_divulgacao = 1` nos casos antigos mantém o Q igual ao repricing
total, que é o que aquelas asserções conferem.
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from view_2_2_inflacao import build_view

ASSETS = ["SPY", "TIP", "TLT", "XLK"]
DUR_LONG, DUR_SHORT = 5.0, 16.0


def _fl_identidade(p):
    return np.asarray(p, dtype=float)


def _build(*args, **kw):
    """build_view com os argumentos novos preenchidos por default de teste."""
    kw.setdefault("duration_long", DUR_LONG)
    kw.setdefault("duration_short", DUR_SHORT)
    kw.setdefault("dias_ate_divulgacao", 1)
    kw.setdefault("fl_correction", _fl_identidade)
    return build_view(*args, **kw)


def test_pmf_caso_conhecido():
    """PMF conhecida: E = 0.0355, breakeven 0.03, duration 8 -> Q = 0.044."""
    r = _build(ASSETS, breakeven_10y=0.03, duration=8.0, cpi_frequencia="anual",
               bucket_probs=[0.2, 0.5, 0.3], bucket_values=[0.03, 0.035, 0.04])
    assert np.isclose(r.Q, 8.0 * (0.0355 - 0.03))
    assert r.diagnostics["caminho"] == "pmf"


def test_P_casada_em_duration():
    """Decisão I3b: a perna do TLT entra reduzida por d_TIP/d_TLT, e a linha
    continua com Sigma|P| = 2. Com 5 e 16: hedge = 0,3125."""
    r = _build(ASSETS, 0.03, 8.0, cpi_frequencia="anual",
               bucket_probs=[0.5, 0.5], bucket_values=[0.03, 0.04])
    hedge = DUR_LONG / DUR_SHORT
    escala = 2.0 / (1.0 + hedge)
    assert np.allclose(r.P, [0.0, escala, -escala * hedge, 0.0])
    assert np.isclose(np.abs(r.P).sum(), 2.0)
    assert np.isclose(r.diagnostics["hedge_duration"], hedge)
    # a perna curta é MENOR que a longa — é o ponto da correção
    assert abs(r.P[2]) < abs(r.P[1])


def test_duration_invalida_rejeitada():
    for dl, ds in ((0.0, 16.0), (5.0, -1.0)):
        try:
            _build(ASSETS, 0.03, 8.0, cpi_frequencia="anual", duration_long=dl,
                   duration_short=ds, bucket_probs=[0.5, 0.5],
                   bucket_values=[0.03, 0.04])
            assert False, "deveria rejeitar duration não positiva"
        except ValueError:
            pass


def test_divergencia_demeanada():
    """Decisão 7.4: só a parte da divergência acima da média histórica vira Q.
    Divergência igual à média -> Q = 0, mesmo com o poly acima do breakeven."""
    r = _build(ASSETS, breakeven_10y=0.03, duration=8.0, cpi_frequencia="anual",
               bucket_probs=[0.0, 1.0, 0.0], bucket_values=[0.03, 0.035, 0.04],
               divergencia_media=0.005)
    assert np.isclose(r.diagnostics["divergencia"], 0.005)
    assert np.isclose(r.Q, 0.0)


def test_horizonte_divide_pelos_dias_ate_a_divulgacao():
    """Decisão 7.2: o repricing se distribui até a divulgação, e o Q é de 1 dia."""
    total = _build(ASSETS, 0.03, 8.0, cpi_frequencia="anual",
                   bucket_probs=[0.0, 1.0, 0.0], bucket_values=[0.03, 0.035, 0.04])
    em_dez = _build(ASSETS, 0.03, 8.0, cpi_frequencia="anual",
                    bucket_probs=[0.0, 1.0, 0.0], bucket_values=[0.03, 0.035, 0.04],
                    dias_ate_divulgacao=10)
    assert np.isclose(em_dez.Q, total.Q / 10)
    assert em_dez.diagnostics["horizonte_q_dias"] == 1
    assert em_dez.diagnostics["dias_ate_divulgacao"] == 10
    try:
        _build(ASSETS, 0.03, 8.0, cpi_frequencia="anual", dias_ate_divulgacao=0,
               bucket_probs=[0.5, 0.5], bucket_values=[0.03, 0.04])
        assert False, "deveria rejeitar dias_ate_divulgacao < 1"
    except ValueError:
        pass


def test_pmf_normalizacao_de_probs_cruas():
    """Probs cruas com spread (soma 0.9) dão o mesmo E das normalizadas."""
    crua = _build(ASSETS, 0.03, 8.0, cpi_frequencia="anual", bucket_probs=[0.18, 0.45, 0.27],
                  bucket_values=[0.03, 0.035, 0.04])
    limpa = _build(ASSETS, 0.03, 8.0, cpi_frequencia="anual", bucket_probs=[0.2, 0.5, 0.3],
                   bucket_values=[0.03, 0.035, 0.04])
    assert np.isclose(crua.Q, limpa.Q)


def test_poly_igual_breakeven_q_zero():
    """Sem divergência, a view não pede tilt: Q = 0."""
    r = _build(ASSETS, breakeven_10y=0.0355, duration=8.0, cpi_frequencia="anual",
               bucket_probs=[0.2, 0.5, 0.3], bucket_values=[0.03, 0.035, 0.04])
    assert np.isclose(r.Q, 0.0)


def test_fallback_binario():
    """p = 0.5 -> média = threshold (normal deslocada); Q = duration * (X - breakeven)."""
    r = _build(ASSETS, breakeven_10y=0.025, duration=8.0, cpi_frequencia="anual",
               binary_prob=(0.5, 0.5), binary_threshold=0.03, cpi_vol=0.005)
    assert np.isclose(r.Q, 8.0 * (0.03 - 0.025))
    assert r.diagnostics["caminho"] == "binario"
    r2 = _build(ASSETS, 0.025, 8.0, cpi_frequencia="anual", binary_prob=(0.6, 0.4),
                binary_threshold=0.03, cpi_vol=0.005)
    assert r2.diagnostics["e_poly"] > 0.03


def test_sem_mercado_view_desativada():
    """Cascata item 0: nenhum mercado de CPI -> None (não é falha)."""
    assert _build(ASSETS, 0.03, 8.0, cpi_frequencia="anual") is None


def test_default_sem_correcao_fl():
    """Decisão 1.1: default γ = 1,0 (identidade)."""
    v = build_view(ASSETS, 0.03, 8.0, cpi_frequencia="anual",
                   duration_long=DUR_LONG, duration_short=DUR_SHORT,
                   dias_ate_divulgacao=1,
                   bucket_probs=[0.5, 0.5], bucket_values=[0.03, 0.04])
    assert np.isclose(v.diagnostics["e_poly"], 0.035)


def test_bucket_aberto_nao_resolvido_rejeitado():
    """NaN em bucket_values (bucket aberto sem valor) é rejeitado."""
    try:
        _build(ASSETS, 0.03, 8.0, cpi_frequencia="anual", bucket_probs=[0.5, 0.5],
               bucket_values=[np.nan, 0.04])
        assert False, "deveria rejeitar NaN em bucket_values"
    except ValueError:
        pass


def test_mercado_mensal_e_anualizado_antes_de_comparar():
    """Grade mensal do Polymarket vs breakeven anual. PMF degenerada em 0,3%
    ao mês -> (1.003)^12 - 1 = 3,6556%, e a view fica COMPRADA em TIP."""
    r = _build(ASSETS, breakeven_10y=0.03, duration=8.0, cpi_frequencia="mensal",
               bucket_probs=[0.0, 1.0, 0.0], bucket_values=[0.002, 0.003, 0.004])
    esperado = (1.003 ** 12) - 1
    assert np.isclose(r.diagnostics["e_poly"], esperado)
    assert np.isclose(r.diagnostics["e_poly_declarado"], 0.003)
    assert np.isclose(r.Q, 8.0 * (esperado - 0.03))
    assert r.Q > 0


def test_anualizacao_entra_nos_valores_nao_na_media():
    """Jensen: anualizar os buckets != anualizar a média da PMF."""
    r = _build(ASSETS, 0.03, 8.0, cpi_frequencia="mensal",
               bucket_probs=[0.5, 0.5], bucket_values=[0.001, 0.005])
    media_dos_anualizados = 0.5 * ((1.001 ** 12) - 1) + 0.5 * ((1.005 ** 12) - 1)
    anualizada_depois = (1.003 ** 12) - 1
    assert np.isclose(r.diagnostics["e_poly"], media_dos_anualizados)
    assert not np.isclose(media_dos_anualizados, anualizada_depois)


def test_frequencia_obrigatoria_e_validada():
    """Sem declarar a unidade não roda; unidade desconhecida é rejeitada."""
    try:
        _build(ASSETS, 0.03, 8.0, bucket_probs=[0.5, 0.5], bucket_values=[0.03, 0.04])
        assert False, "cpi_frequencia deveria ser obrigatório"
    except TypeError:
        pass
    try:
        _build(ASSETS, 0.03, 8.0, cpi_frequencia="diaria", bucket_probs=[0.5, 0.5],
               bucket_values=[0.03, 0.04])
        assert False, "deveria rejeitar frequência desconhecida"
    except ValueError:
        pass
