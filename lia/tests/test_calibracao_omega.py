"""Testes do harness de calibração do Ω reativo (Decisão 6).

Casos sintéticos com resultado conhecido:
- erro futuro: valores exatos numa série pequena;
- estabilidade: série constante → score máximo (0); ruidosa → menor;
- proximidade: 0 no dia do evento, crescente com a distância, saturação;
- portão de volume: binário no threshold;
- combinação por rank: veto zera, ordem preservada;
- monotonicidade: regime calmo/turbulento construído → spearman negativo
  e faixas ordenadas; candidata invertida → reprovada.
"""

import numpy as np
import pandas as pd
import pytest

from lia.calibracao_omega import (
    avaliar_monotonicidade,
    combinar_por_rank,
    comparar_candidatas,
    erro_realizado_futuro,
    erro_vs_resolucao,
    portao_volume,
    score_estabilidade,
    score_proximidade,
)


def _serie(valores, inicio="2026-01-01"):
    datas = pd.date_range(inicio, periods=len(valores), freq="D")
    return pd.Series(valores, index=datas, dtype=float)


# ---------------------------------------------------------------------------
# Erro realizado
# ---------------------------------------------------------------------------


def test_erro_futuro_valores_exatos():
    prob = _serie([0.50, 0.60, 0.55, 0.90])
    erro = erro_realizado_futuro(prob, horizonte=1)
    assert erro.iloc[0] == pytest.approx(0.10)
    assert erro.iloc[1] == pytest.approx(0.05)
    assert erro.iloc[2] == pytest.approx(0.35)
    assert np.isnan(erro.iloc[3])  # sem futuro observável


def test_erro_futuro_horizonte_maior_e_validacao():
    prob = _serie([0.50, 0.60, 0.55, 0.90])
    erro = erro_realizado_futuro(prob, horizonte=2)
    assert erro.iloc[0] == pytest.approx(0.05)  # |0.55 − 0.50|
    assert np.isnan(erro.iloc[2]) and np.isnan(erro.iloc[3])
    with pytest.raises(ValueError):
        erro_realizado_futuro(prob, horizonte=0)


def test_erro_vs_resolucao():
    prob = _serie([0.20, 0.70])
    assert erro_vs_resolucao(prob, 1.0).iloc[0] == pytest.approx(0.80)
    assert erro_vs_resolucao(prob, 0.0).iloc[1] == pytest.approx(0.70)
    with pytest.raises(ValueError):
        erro_vs_resolucao(prob, 0.5)


# ---------------------------------------------------------------------------
# Scores candidatos
# ---------------------------------------------------------------------------


def test_estabilidade_serie_constante_tem_score_maximo():
    parada = _serie([0.6] * 10)
    score = score_estabilidade(parada, janela=5)
    assert score.dropna().eq(0.0).all()  # desvio zero → score máximo


def test_estabilidade_ruido_maior_da_score_menor():
    rng = np.random.default_rng(42)
    calma = _serie(0.5 + 0.001 * rng.standard_normal(30))
    ruidosa = _serie(0.5 + 0.10 * rng.standard_normal(30))
    s_calma = score_estabilidade(calma, janela=10).dropna()
    s_ruidosa = score_estabilidade(ruidosa, janela=10).dropna()
    assert s_calma.mean() > s_ruidosa.mean()
    with pytest.raises(ValueError):
        score_estabilidade(calma, janela=1)


def test_proximidade_linear_zero_no_evento_e_satura():
    datas = pd.date_range("2026-03-01", periods=15, freq="D")
    evento = "2026-03-10"
    score = score_proximidade(datas, evento, forma="linear", horizonte_dias=5)
    assert score.loc["2026-03-10"] == pytest.approx(0.0)  # dia do evento
    assert score.loc["2026-03-12"] == pytest.approx(0.0)  # depois do evento
    assert score.loc["2026-03-08"] == pytest.approx(2 / 5)  # 2 dias antes
    assert score.loc["2026-03-01"] == pytest.approx(1.0)  # saturado (9 > 5)


def test_proximidade_exponencial_monotona_e_limitada():
    datas = pd.date_range("2026-03-01", periods=10, freq="D")
    evento = "2026-03-10"
    score = score_proximidade(
        datas, evento, forma="exponencial", horizonte_dias=3
    )
    assert score.loc["2026-03-10"] == pytest.approx(0.0)
    # datas em ordem cronológica aproximam o evento → score não-crescente
    diffs = score.diff().dropna()
    assert (diffs <= 0).all()
    assert (score < 1.0).all()
    with pytest.raises(ValueError):
        score_proximidade(datas, evento, forma="quadratica", horizonte_dias=3)


def test_portao_volume_binario_no_threshold():
    volume = _serie([100.0, 5000.0, 999.0, 1000.0])
    portao = portao_volume(volume, threshold=1000.0)
    assert list(portao) == [0.0, 1.0, 0.0, 1.0]
    with pytest.raises(ValueError):
        portao_volume(volume, threshold=0.0)


def test_combinar_por_rank_veto_e_ordem():
    a = _serie([1.0, 2.0, 3.0, 4.0])
    portao = _serie([1.0, 1.0, 0.0, 1.0])
    combinado = combinar_por_rank([a, portao])
    assert combinado.iloc[2] == pytest.approx(0.0)  # veto zera
    # entre as datas não vetadas, a ordem de `a` é preservada
    assert combinado.iloc[0] < combinado.iloc[1] < combinado.iloc[3]
    with pytest.raises(ValueError):
        combinar_por_rank([])


# ---------------------------------------------------------------------------
# Teste de monotonicidade e comparação de candidatas
# ---------------------------------------------------------------------------


def _cenario_dois_regimes(seed=7, n=120):
    """Metade calma (prob quase parada), metade turbulenta.

    Por construção, o score de estabilidade deve prever o erro futuro:
    regime calmo → score alto e erro pequeno; turbulento → o oposto.
    """
    rng = np.random.default_rng(seed)
    calmo = 0.5 + np.cumsum(0.002 * rng.standard_normal(n // 2))
    turbulento = 0.5 + np.cumsum(0.05 * rng.standard_normal(n // 2))
    prob = _serie(np.clip(np.concatenate([calmo, turbulento]), 0.01, 0.99))
    return prob


def test_monotonicidade_candidata_boa_passa():
    prob = _cenario_dois_regimes()
    score = score_estabilidade(prob, janela=10)
    erro = erro_realizado_futuro(prob, horizonte=5)
    resultado = avaliar_monotonicidade(score, erro, n_faixas=3)
    assert resultado.spearman < -0.5  # confiança alta ↔ erro baixo
    assert resultado.monotonica
    assert resultado.n_observacoes > 0


def test_monotonicidade_candidata_invertida_reprova():
    prob = _cenario_dois_regimes()
    score_invertido = -score_estabilidade(prob, janela=10)
    erro = erro_realizado_futuro(prob, horizonte=5)
    resultado = avaliar_monotonicidade(score_invertido, erro, n_faixas=3)
    assert resultado.spearman > 0.5
    assert not resultado.monotonica


def test_monotonicidade_validacoes():
    prob = _cenario_dois_regimes()
    erro = erro_realizado_futuro(prob, horizonte=5)
    score = score_estabilidade(prob, janela=10)
    with pytest.raises(ValueError):
        avaliar_monotonicidade(score, erro, n_faixas=1)
    curta = _serie([0.5, 0.6])
    with pytest.raises(ValueError):
        avaliar_monotonicidade(curta, curta, n_faixas=3)


def test_comparar_candidatas_ranqueia_boa_primeiro():
    prob = _cenario_dois_regimes()
    erro = erro_realizado_futuro(prob, horizonte=5)
    boa = score_estabilidade(prob, janela=10)
    tabela = comparar_candidatas(
        {"estabilidade_j10": boa, "invertida": -boa}, erro, n_faixas=3
    )
    assert list(tabela.index) == ["estabilidade_j10", "invertida"]
    assert tabela.loc["estabilidade_j10", "spearman"] < 0
    assert bool(tabela.loc["estabilidade_j10", "monotonica"])
    with pytest.raises(ValueError):
        comparar_candidatas({}, erro, n_faixas=3)
