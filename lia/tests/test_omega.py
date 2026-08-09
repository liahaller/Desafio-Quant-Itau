"""Testes da régua de produção do Ω (Decisão 6, fechada em 09/08/2026).

Casos sintéticos com resultado conhecido:
- reconstrução da grade: slot inteiramente vazio volta como linha NaN, para o
  par não-adjacente não ser lido como uma variação só (6e);
- fator de estabilidade: PMF parada → 1.0; massa movida conhecida → valor
  exato; respeita a janela e descarta o par quebrado;
- fator de coerência: bilateral, medido no cru, neutro em linha incompleta;
- `calcular_omega`: `nivel = 0` recupera He-Litterman (c = 1), volume zero
  veta, volume ausente/NaN não veta (6b), e c ≥ 1 sempre.
"""

import numpy as np
import pandas as pd
import pytest

from lia.omega import (
    calcular_omega,
    fator_coerencia,
    fator_estabilidade,
    pmf_da_serie_janela,
)


def _serie_janela(linhas, inicio="2026-01-01 00:00", passo_h=12):
    """`[(t, {faixa: p}), ...]` no formato cru do `diagnostics`."""
    instantes = pd.date_range(inicio, periods=len(linhas), freq=f"{passo_h}h")
    return [(t, dict(linha)) for t, linha in zip(instantes, linhas)]


def _pmf(linhas):
    """PMF na grade completa, a partir das linhas na ordem dos slots."""
    return pmf_da_serie_janela(_serie_janela(linhas))


# ---------------------------------------------------------------------------
# Reconstrução da grade
# ---------------------------------------------------------------------------


def test_grade_reconstroi_slot_vazio_como_linha_nan():
    # o pipeline entrega só os slots com leitura: aqui falta o das 12:00
    serie = [
        (pd.Timestamp("2026-01-01 00:00"), {"a": 0.6, "b": 0.4}),
        (pd.Timestamp("2026-01-02 00:00"), {"a": 0.5, "b": 0.5}),
    ]
    pmf = pmf_da_serie_janela(serie)
    assert len(pmf) == 3  # 00:00, 12:00 (buraco) e 00:00 do dia seguinte
    assert pmf.iloc[1].isna().all()


def test_grade_vazia_devolve_dataframe_vazio():
    assert pmf_da_serie_janela([]).empty


def test_grade_reconstruida_quebra_a_adjacencia():
    """O buraco não pode virar 'uma variação' entre as leituras vizinhas."""
    serie = [
        (pd.Timestamp("2026-01-01 00:00"), {"a": 0.6, "b": 0.4}),
        (pd.Timestamp("2026-01-02 00:00"), {"a": 0.1, "b": 0.9}),
    ]
    # sem reconstruir a grade, o salto de 0,5 entraria como uma variação
    assert np.isnan(fator_estabilidade(pmf_da_serie_janela(serie),
                                       janela_variacoes=3))


# ---------------------------------------------------------------------------
# Fator de estabilidade
# ---------------------------------------------------------------------------


def test_estabilidade_pmf_parada_vale_um():
    pmf = _pmf([{"a": 0.6, "b": 0.4}] * 4)
    assert fator_estabilidade(pmf, janela_variacoes=3) == pytest.approx(1.0)


def test_estabilidade_massa_movida_e_exata():
    # 10 pontos de massa migram de "a" para "b" em cada passo:
    # variação total = 0,5 · (0,1 + 0,1) = 0,1 por par, três pares
    pmf = _pmf([
        {"a": 0.6, "b": 0.4},
        {"a": 0.5, "b": 0.5},
        {"a": 0.4, "b": 0.6},
        {"a": 0.3, "b": 0.7},
    ])
    assert fator_estabilidade(pmf, janela_variacoes=3) == pytest.approx(1.1)


def test_estabilidade_usa_so_as_ultimas_variacoes():
    # dois pares parados no fim; a turbulência do começo fica fora da janela
    pmf = _pmf([
        {"a": 0.9, "b": 0.1},
        {"a": 0.1, "b": 0.9},
        {"a": 0.5, "b": 0.5},
        {"a": 0.5, "b": 0.5},
        {"a": 0.5, "b": 0.5},
    ])
    assert fator_estabilidade(pmf, janela_variacoes=2) == pytest.approx(1.0)


def test_estabilidade_descarta_par_com_linha_incompleta():
    # a linha do meio perdeu uma faixa: sai inteira (6e) e quebra os dois
    # pares que a tocam, sobrando só o último
    pmf = _pmf([
        {"a": 0.6, "b": 0.4},
        {"a": 0.5, "b": np.nan},
        {"a": 0.4, "b": 0.6},
        {"a": 0.3, "b": 0.7},
    ])
    assert fator_estabilidade(pmf, janela_variacoes=3) == pytest.approx(1.1)


def test_estabilidade_sem_par_valido_e_nan():
    pmf = _pmf([{"a": 0.6, "b": 0.4}])
    assert np.isnan(fator_estabilidade(pmf, janela_variacoes=3))


def test_estabilidade_valida_janela():
    pmf = _pmf([{"a": 0.5, "b": 0.5}] * 3)
    with pytest.raises(ValueError):
        fator_estabilidade(pmf, janela_variacoes=0)


def test_estabilidade_renormaliza_antes_de_colapsar():
    # livro somando 1,2 mas com a MESMA proporção nos dois slots: depois de
    # renormalizar não houve movimento de opinião nenhum (6a)
    pmf = _pmf([
        {"a": 0.72, "b": 0.48},
        {"a": 0.60, "b": 0.40},
    ])
    assert fator_estabilidade(pmf, janela_variacoes=1) == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# Fator de coerência
# ---------------------------------------------------------------------------


def test_coerencia_livro_fechado_vale_um():
    assert fator_coerencia(_pmf([{"a": 0.5, "b": 0.5}] * 2)) == pytest.approx(1.0)


def test_coerencia_e_bilateral():
    acima = _pmf([{"a": 0.7, "b": 0.5}])   # soma 1,2
    abaixo = _pmf([{"a": 0.5, "b": 0.3}])  # soma 0,8
    assert fator_coerencia(acima) == pytest.approx(1.2)
    assert fator_coerencia(abaixo) == pytest.approx(1.2)


def test_coerencia_mede_na_leitura_da_decisao():
    # o desarranjo antigo não conta: só a última linha
    pmf = _pmf([{"a": 0.9, "b": 0.6}, {"a": 0.5, "b": 0.5}])
    assert fator_coerencia(pmf) == pytest.approx(1.0)


def test_coerencia_neutra_em_linha_incompleta():
    pmf = _pmf([{"a": 0.5, "b": 0.5}, {"a": 0.5, "b": np.nan}])
    assert fator_coerencia(pmf) == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# Régua completa
# ---------------------------------------------------------------------------


def _diagnostics(view, linhas):
    return {"view": view, "serie_janela": _serie_janela(linhas)}


def _movimento(n=4):
    return [{"a": 0.6 - 0.1 * i, "b": 0.4 + 0.1 * i} for i in range(n)]


def test_nivel_zero_recupera_he_litterman():
    blocos = [_diagnostics("2.2_inflacao", _movimento())]
    c, ativa = calcular_omega(blocos, {"2.2_inflacao": 500.0},
                              nivel=0.0, janela_variacoes=3)
    assert ativa["2.2_inflacao"] is True
    assert c["2.2_inflacao"] == pytest.approx(1.0)


def test_c_e_o_produto_das_penalidades():
    # variação média 0,1 e livro fechado → c = 1,1
    blocos = [_diagnostics("2.2_inflacao", _movimento())]
    c, _ = calcular_omega(blocos, {"2.2_inflacao": 500.0},
                          nivel=1.0, janela_variacoes=3)
    assert c["2.2_inflacao"] == pytest.approx(1.1)


def test_c_nunca_fica_abaixo_de_um():
    # mercado impecável: parado e com o livro fechando exatamente em 1
    blocos = [_diagnostics("2.3_fed", [{"a": 0.5, "b": 0.5}] * 4)]
    c, _ = calcular_omega(blocos, {"2.3_fed": 10.0},
                          nivel=1.0, janela_variacoes=3)
    assert c["2.3_fed"] == pytest.approx(1.0)
    assert c["2.3_fed"] >= 1.0


def test_volume_zero_veta_a_view():
    blocos = [_diagnostics("2.2_inflacao", _movimento())]
    c, ativa = calcular_omega(blocos, {"2.2_inflacao": 0.0},
                              nivel=1.0, janela_variacoes=3)
    assert ativa["2.2_inflacao"] is False
    assert np.isnan(c["2.2_inflacao"])


def test_volume_ausente_ou_nan_nao_veta():
    """Truncamento do cap de 20k é ignorância nossa, não iliquidez (6b)."""
    blocos = [_diagnostics("2.2_inflacao", _movimento())]
    for volumes in ({}, {"2.2_inflacao": np.nan}):
        _, ativa = calcular_omega(blocos, volumes,
                                  nivel=1.0, janela_variacoes=3)
        assert ativa["2.2_inflacao"] is True


def test_sem_leitura_mensuravel_a_view_sai():
    """Sem par adjacente completo não há qualificação — não vira c = 1."""
    blocos = [_diagnostics("B_camara", [{"a": 0.6, "b": 0.4}])]
    c, ativa = calcular_omega(blocos, {"B_camara": 900.0},
                              nivel=1.0, janela_variacoes=3)
    assert ativa["B_camara"] is False
    assert np.isnan(c["B_camara"])


def test_chave_sai_do_bloco_e_views_sao_independentes():
    blocos = [
        _diagnostics("2.2_inflacao", _movimento()),
        _diagnostics("2.3_fed", [{"a": 0.5, "b": 0.5}] * 4),
    ]
    c, ativa = calcular_omega(blocos, {"2.2_inflacao": 0.0, "2.3_fed": 700.0},
                              nivel=1.0, janela_variacoes=3)
    assert set(c) == {"2.2_inflacao", "2.3_fed"}
    assert ativa == {"2.2_inflacao": False, "2.3_fed": True}
    assert c["2.3_fed"] == pytest.approx(1.0)


def test_nivel_negativo_e_rejeitado():
    with pytest.raises(ValueError):
        calcular_omega([], {}, nivel=-1.0, janela_variacoes=3)


def test_nivel_escala_a_penalidade_monotonicamente():
    blocos = [_diagnostics("2.2_inflacao", _movimento())]
    valores = [
        calcular_omega(blocos, {"2.2_inflacao": 500.0},
                       nivel=n, janela_variacoes=3)[0]["2.2_inflacao"]
        for n in (0.0, 0.5, 1.0, 2.0)
    ]
    assert valores == sorted(valores)
    assert valores[0] == pytest.approx(1.0)
