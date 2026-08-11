"""Testes do harness de calibração do Ω reativo (Decisão 6).

Casos sintéticos com resultado conhecido:
- erro futuro: valores exatos numa série pequena;
- estabilidade: série constante → score máximo (0); ruidosa → menor;
- proximidade: 0 no dia do evento, crescente com a distância, saturação;
- portão de volume: binário no threshold; NaN não veta (6b);
- combinação por rank: veto explícito zera, ordem preservada, e score
  0.0 legítimo (estabilidade máxima, dia do evento) não vira veto (6b);
- monotonicidade: regime calmo/turbulento construído → spearman negativo
  e faixas ordenadas; candidata invertida → reprovada.
"""

import numpy as np
import pandas as pd
import pytest

from lia.calibracao_omega import (
    agregar_volume_slot,
    avaliar_monotonicidade,
    combinar_por_rank,
    comparar_candidatas,
    erro_realizado_futuro,
    erro_vs_resolucao,
    portao_volume,
    preparar_pmf,
    score_coerencia,
    score_estabilidade,
    score_estabilidade_pmf,
    score_proximidade,
    variacao_total,
    variacao_valor_esperado,
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


def test_portao_volume_nao_veta_volume_desconhecido():
    """NaN (truncamento do cap) não pode virar veto — Decisão 6b.

    `0` e `NaN` significam coisas opostas no G5: zero é pré-primeiro-trade
    (ninguém negociou) e NaN é truncamento (o dado existe, a API não
    entrega). Tratar os dois igual desfaz a separação que o Paulo mediu.
    """
    volume = _serie([100.0, 0.0, np.nan])
    portao = portao_volume(volume, threshold=10.0)
    assert portao.iloc[0] == 1.0
    assert portao.iloc[1] == 0.0  # negociação de fato ausente → veta
    assert np.isnan(portao.iloc[2])  # sem dado → não decide, não veta


def _long_volume(linhas):
    """G5 em formato long: (evento, slot, notional) → DataFrame."""
    return pd.DataFrame(linhas, columns=["evento", "slot_utc", "notional_usd"])


def test_agregar_volume_slot_faixa_truncada_contamina_o_slot():
    """Faixa NaN + faixas zeradas NÃO pode virar veto (Decisão 6b no slot).

    Somar tratando NaN como ausente daria soma 0 e vetaria o slot,
    afirmando "ninguém negociou" onde uma das faixas é desconhecida. Era
    o caso de 6 slots reais do FOMC.
    """
    long = _long_volume([
        (1, "2026-01-01 00:00", 0.0),
        (1, "2026-01-01 00:00", np.nan),
        (1, "2026-01-01 12:00", 0.0),
        (1, "2026-01-01 12:00", 0.0),
        (1, "2026-01-02 00:00", 40.0),
        (1, "2026-01-02 00:00", 60.0),
    ])
    saida = agregar_volume_slot(long)
    assert np.isnan(saida.loc[(1, "2026-01-01 00:00"), "soma"])  # parcial
    assert saida.loc[(1, "2026-01-01 12:00"), "soma"] == 0.0  # veto legítimo
    assert saida.loc[(1, "2026-01-02 00:00"), "soma"] == 100.0


def test_agregar_volume_slot_minimo_conhecido_apesar_do_truncamento():
    """Faixa zerada fixa o mínimo mesmo com outra faixa desconhecida.

    Volume não é negativo, então nenhuma faixa faltante poderia baixar um
    mínimo que já é zero — é o único caso em que o slot parcial ainda
    responde.
    """
    long = _long_volume([
        (1, "2026-01-01 00:00", 0.0),
        (1, "2026-01-01 00:00", np.nan),
        (1, "2026-01-01 12:00", 30.0),
        (1, "2026-01-01 12:00", np.nan),
    ])
    saida = agregar_volume_slot(long)
    assert saida.loc[(1, "2026-01-01 00:00"), "minimo"] == 0.0
    assert np.isnan(saida.loc[(1, "2026-01-01 12:00"), "minimo"])


def test_agregar_volume_slot_sem_truncamento_reproduz_a_soma_simples():
    """Sem faixa NaN, é a agregação da 6g — é o que preserva os números da 2.2."""
    long = _long_volume([
        (1, "2026-01-01 00:00", 10.0),
        (1, "2026-01-01 00:00", 5.0),
        (2, "2026-01-01 00:00", 0.0),
        (2, "2026-01-01 00:00", 7.0),
    ])
    saida = agregar_volume_slot(long)
    assert saida.loc[(1, "2026-01-01 00:00"), "soma"] == 15.0
    assert saida.loc[(1, "2026-01-01 00:00"), "minimo"] == 5.0
    assert saida.loc[(2, "2026-01-01 00:00"), "soma"] == 7.0
    assert saida.loc[(2, "2026-01-01 00:00"), "minimo"] == 0.0


def test_combinar_por_rank_veto_explicito_zera():
    a = _serie([1.0, 2.0, 3.0, 4.0])
    portao = _serie([1.0, 1.0, 0.0, 1.0])
    combinado = combinar_por_rank([a], veto=portao)
    assert combinado.iloc[2] == pytest.approx(0.0)  # veto zera
    # entre as datas não vetadas, a ordem de `a` é preservada
    assert combinado.iloc[0] < combinado.iloc[1] < combinado.iloc[3]
    with pytest.raises(ValueError):
        combinar_por_rank([])


def test_combinar_por_rank_veto_nan_nao_zera():
    """Volume desconhecido não veta: o slot é julgado só pelos graduais."""
    a = _serie([1.0, 2.0, 3.0, 4.0])
    portao = _serie([1.0, 1.0, np.nan, 1.0])
    combinado = combinar_por_rank([a], veto=portao)
    assert combinado.iloc[2] > 0.0
    assert combinado.iloc[2] == pytest.approx(combinar_por_rank([a]).iloc[2])


def test_combinar_por_rank_score_zero_legitimo_nao_e_veto():
    """Score 0.0 é valor, não veto — Decisão 6b.

    Os dois casos que a versão anterior invertia: estabilidade máxima
    (série parada, −std = 0.0) e dia do evento na proximidade.
    """
    parada = _serie([0.5] * 10)
    estabilidade = score_estabilidade(parada, janela=5)
    assert estabilidade.dropna().eq(0.0).all()  # o melhor valor possível
    combinado = combinar_por_rank([estabilidade])
    assert combinado.dropna().gt(0.0).all()  # e não vira confiança zero

    datas = pd.date_range("2026-03-01", periods=10, freq="D")
    proximidade = score_proximidade(
        datas, "2026-03-10", forma="linear", horizonte_dias=5
    )
    assert proximidade.iloc[-1] == pytest.approx(0.0)  # dia do evento
    assert combinar_por_rank([proximidade]).iloc[-1] > 0.0  # amortece, não corta


# ---------------------------------------------------------------------------
# Colapso PMF → p (Decisão 6a) e coerência (6c/6e)
# ---------------------------------------------------------------------------


def _pmf(linhas, inicio="2026-01-01"):
    datas = pd.date_range(inicio, periods=len(linhas), freq="12h")
    return pd.DataFrame(linhas, index=datas, dtype=float)


def test_preparar_pmf_descarta_incompleta_e_renormaliza():
    crua = _pmf([[0.5, 0.5], [0.6, np.nan], [0.55, 0.60]])  # soma 1,00 / — / 1,15
    pronta = preparar_pmf(crua)
    assert pronta.iloc[0].tolist() == pytest.approx([0.5, 0.5])
    assert pronta.iloc[1].isna().all()  # linha incompleta sai INTEIRA
    assert pronta.iloc[2].sum() == pytest.approx(1.0)  # desarranjo removido
    assert pronta.iloc[2, 0] == pytest.approx(0.55 / 1.15)


def test_variacao_total_degenera_no_caso_binario():
    """Com duas faixas, 0,5·Σ|Δp_b| tem de ser exatamente |Δp| — é a
    promessa que sustenta a candidata (a) na grade da 6a."""
    pmf = preparar_pmf(_pmf([[0.40, 0.60], [0.55, 0.45], [0.50, 0.50]]))
    var = variacao_total(pmf)
    assert np.isnan(var.iloc[0])  # sem par anterior
    assert var.iloc[1] == pytest.approx(0.15)  # |0,55 − 0,40|
    assert var.iloc[2] == pytest.approx(0.05)


def test_variacao_total_e_massa_movida_e_ignora_par_quebrado():
    pmf = preparar_pmf(_pmf([[0.2, 0.3, 0.5], [0.4, 0.3, 0.3],
                             [0.4, np.nan, 0.3], [0.4, 0.3, 0.3]]))
    var = variacao_total(pmf)
    assert var.iloc[1] == pytest.approx(0.2)  # 0,2 de massa mudou de faixa
    assert np.isnan(var.iloc[2])  # linha incompleta
    assert np.isnan(var.iloc[3])  # par não-adjacente: ponta anterior ausente


def test_variacao_valor_esperado_usa_a_grade():
    pmf = preparar_pmf(_pmf([[1.0, 0.0], [0.0, 1.0]]))
    var = variacao_valor_esperado(pmf, [-25.0, 0.0])
    assert var.iloc[1] == pytest.approx(25.0)
    with pytest.raises(ValueError):
        variacao_valor_esperado(pmf, [-25.0, 0.0, 25.0])


def test_score_estabilidade_pmf_parada_e_maximo():
    pmf = preparar_pmf(_pmf([[0.5, 0.5]] * 6))
    parado = score_estabilidade_pmf(variacao_total(pmf), janela=3)
    assert parado.dropna().eq(0.0).all()

    movido = _pmf([[0.5, 0.5], [0.7, 0.3], [0.4, 0.6], [0.8, 0.2],
                   [0.3, 0.7], [0.6, 0.4]])
    agitado = score_estabilidade_pmf(variacao_total(preparar_pmf(movido)), janela=3)
    assert agitado.dropna().max() < parado.dropna().min()
    with pytest.raises(ValueError):
        score_estabilidade_pmf(variacao_total(pmf), janela=0)


def test_score_coerencia_bilateral_e_nan_em_linha_incompleta():
    soma = _serie([1.00, 0.90, 1.10, 0.40])
    completa = _serie([1.0, 1.0, 1.0, 0.0])
    score = score_coerencia(soma, completa)
    assert score.iloc[0] == pytest.approx(0.0)  # livro coerente → máximo
    # bilateral: desarranjo para baixo e para cima pesam igual
    assert score.iloc[1] == pytest.approx(score.iloc[2])
    assert score.iloc[1] == pytest.approx(-0.10)
    # linha incompleta: a soma mede buraco, não desencontro (6e)
    assert np.isnan(score.iloc[3])


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
