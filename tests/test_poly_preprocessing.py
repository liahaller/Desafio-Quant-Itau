"""Testes sintéticos do pré-processamento (regra CLAUDE.md §5: caso com resultado conhecido)."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from poly_preprocessing import (
    normalize_probs,
    favorite_longshot,
    favorite_longshot_pmf,
    bucket_values_with_open,
    carry_missing,
    pmf_mean,
    soma_faixas,
    binary_prob_series,
)


def test_normalize_binario():
    """Binário com spread: 0.62 + 0.36 -> normaliza para somar 1."""
    p = normalize_probs([0.62, 0.36])
    assert np.isclose(p.sum(), 1.0)
    assert np.isclose(p[0], 0.62 / 0.98)


def test_normalize_pmf_por_linha():
    """Matriz (datas x buckets) normaliza cada linha independentemente."""
    pmf = np.array([[0.10, 0.30, 0.50], [0.20, 0.20, 0.20]])
    out = normalize_probs(pmf, axis=1)
    assert np.allclose(out.sum(axis=1), 1.0)
    assert np.allclose(out[1], [1 / 3, 1 / 3, 1 / 3])


def test_pmf_mean():
    """Probs cruas [0.6, 0.3] normalizam para [2/3, 1/3]; média conhecida.
    Com γ = 1,0 (decisão 1.1) o default é a identidade. NaN em values
    (bucket aberto não resolvido) segue falhando alto."""
    m = pmf_mean([0.6, 0.3], [3.0, 6.0])
    assert np.isclose(m, 4.0)
    try:
        pmf_mean([0.5, 0.5], [np.nan, 6.0])
        assert False, "deveria rejeitar NaN em values"
    except ValueError:
        pass


def test_binary_prob_series():
    """Par (0.60, 0.30) normaliza para p_sim = 2/3; sem o No, a série passa
    direto; shapes desalinhados falham alto."""
    p = binary_prob_series([0.60, 0.42], [0.30, 0.50])
    assert np.allclose(p, [0.6 / 0.9, 0.42 / 0.92])
    so_yes = binary_prob_series([0.60, 0.42])
    assert np.allclose(so_yes, [0.60, 0.42])
    try:
        binary_prob_series([0.60, 0.42], [0.30])
        assert False, "deveria rejeitar p_yes e p_no desalinhados"
    except ValueError:
        pass


def test_favorite_longshot_gamma_1_e_identidade():
    """Decisão 1.1: sem correção no v1 — γ = 1,0 devolve a entrada intacta,
    tanto no binário quanto na PMF."""
    p = [0.03, 0.20, 0.65]
    assert np.allclose(favorite_longshot(p), p)
    assert np.allclose(favorite_longshot_pmf(p), p)


def test_favorite_longshot_gamma_maior_derruba_p_baixa():
    """γ > 1 encolhe probabilidade baixa (é o efeito que a 3.1 sofreria) e
    mantém a série em [0, 1]."""
    p = np.array([0.03, 0.50, 0.90])
    corrigida = favorite_longshot(p, gamma=1.25)
    assert corrigida[0] < 0.03
    assert np.isclose(corrigida[1], 0.5)  # p = 0,5 é ponto fixo
    assert corrigida[2] > 0.90
    assert np.all((corrigida >= 0) & (corrigida <= 1))
    pmf = favorite_longshot_pmf([0.1, 0.3, 0.6], gamma=1.25)
    assert np.isclose(pmf.sum(), 1.0)


def test_bucket_aberto_e_meia_largura_para_fora():
    """Decisão 1.2: grade 0,1/0,2/0,3 -> pontas viram 0,05 e 0,35."""
    v = bucket_values_with_open([0.1, 0.2, 0.3])
    assert np.allclose(v, [0.05, 0.2, 0.35])
    assert np.allclose(bucket_values_with_open([0.1, 0.2, 0.3], shift=0.0),
                       [0.1, 0.2, 0.3])  # truncar, para a varredura
    # só a ponta superior aberta (caso do M3, nº de cortes)
    assert np.allclose(bucket_values_with_open([0.0, 1.0, 2.0], open_ends=("upper",)),
                       [0.0, 1.0, 2.5])


def test_bucket_aberto_resolve_nan_da_ponta():
    """Slug '8plus' chega como NaN: vira vizinho + largura, depois desloca."""
    v = bucket_values_with_open([0.0, 1.0, 2.0, np.nan], open_ends=("upper",))
    assert np.allclose(v, [0.0, 1.0, 2.0, 3.5])


def test_bucket_aberto_com_grade_invertida():
    """Grade de jul/2026 (inflação caindo) é decrescente — a largura mediana
    é negativa e o deslocamento sai para fora do mesmo jeito."""
    v = bucket_values_with_open([0.1, 0.0, -0.1])
    assert v[0] > 0.1 and v[-1] < -0.1


def test_carry_missing_cobre_os_dois_casos():
    """Decisão 6.1: faixa que some e volta herda a última leitura; faixa que
    morre carrega o último preço (que é ~0 no dado real)."""
    pmf = pd.DataFrame({
        "a": [0.50, np.nan, 0.40],   # some e volta
        "b": [0.45, 0.50, np.nan],   # morre no fim
    })
    out = carry_missing(pmf)
    assert out.loc[1, "a"] == 0.50
    assert out.loc[2, "b"] == 0.50
    assert not out.isna().any().any()


if __name__ == "__main__":
    test_normalize_binario()
    test_normalize_pmf_por_linha()
    test_pmf_mean()
    test_binary_prob_series()
    print("poly_preprocessing: testes OK")


def test_soma_faixas_vem_crua_e_desconhecido_nao_vira_zero():
    """O desarranjo do livro é o SINAL do Ω da Lia — ela pediu a soma crua, não
    |soma − 1|. Medido no dado do Paulo: 0,92 a 1,33 no mercado de cortes."""
    assert soma_faixas([0.30, 0.62]) == pytest.approx(0.92)
    assert soma_faixas([0.55, 0.45, 0.33]) == pytest.approx(1.33)
    # caminho binário da cascata: não há grade de faixas -> NaN, nunca 0
    assert np.isnan(soma_faixas(None))
    # faixa sem leitura contamina a soma: desconhecido propaga, não some
    assert np.isnan(soma_faixas([0.4, np.nan, 0.3]))


def test_pmf_mean_recusa_correcao_binaria_com_gamma():
    """A binária numa PMF é inócua em γ = 1,0 e ERRADA em γ ≠ 1 — e γ ≠ 1 só
    aparece na coluna de robustez (seção 9), então o erro só apareceria no
    número final. Tem de falhar alto na hora."""
    probs, valores = [0.5, 0.3, 0.2], [-50.0, -25.0, 0.0]
    binaria_com_gamma = lambda p: favorite_longshot(p, gamma=1.25)  # noqa: E731
    with pytest.raises(ValueError, match="não 1"):
        pmf_mean(probs, valores, binaria_com_gamma)
    # a correção CERTA passa: renormaliza sobre as faixas
    esperado = float(favorite_longshot_pmf(normalize_probs(probs), 1.25)
                     @ np.array(valores))
    assert np.isclose(pmf_mean(probs, valores,
                               lambda p: favorite_longshot_pmf(p, 1.25)), esperado)
