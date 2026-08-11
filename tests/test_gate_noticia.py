"""Teste da `estabilidade` do `gate_noticia.py` (Felipe).

O que está sendo protegido é o único teste fora da amostra que este projeto
tem para mercado sem irmão: partir a amostra em duas. Se as metades vazarem uma
na outra, um sinal que troca de regime passa a "sobreviver ao corte" e a D19c
deixa de ser reproduzível.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from config import ASSETS  # noqa: E402
from gate_noticia import estabilidade  # noqa: E402


@pytest.fixture
def cenario_que_troca_de_regime():
    """Sinal +1 todo dia; SPY sobe na 1ª metade e cai na 2ª.

    Com a premissa "sinal sobe → SPY sobe", a amostra inteira mediria ~0 e as
    metades medem ✅ e ❌ — que é exatamente o padrão da D19c.
    """
    datas = pd.bdate_range("2025-01-06", periods=120)
    retornos = pd.DataFrame(0.0, index=datas, columns=list(ASSETS))
    metade = len(datas) // 2
    retornos.loc[datas[:metade], "SPY"] = +0.01
    retornos.loc[datas[metade:], "SPY"] = -0.01
    sinal = pd.Series(1.0, index=datas)
    # Σ diagonal só para o encolhimento ter o que usar; a direção do μ não
    # depende dela, e é a direção que este teste mede.
    sigma = np.eye(len(ASSETS)) * 1e-4
    return retornos, sinal, sigma, datas[-1] + pd.Timedelta(days=1)


def test_metades_medem_regimes_opostos(cenario_que_troca_de_regime):
    retornos, sinal, sigma, ate = cenario_que_troca_de_regime
    metades = estabilidade(retornos, sinal, {"SPY": +1}, sigma, ate)

    assert [r for r, _ok, _d, _n in metades] == ["1ª metade", "2ª metade"]
    primeira, segunda = metades[0][1], metades[1][1]
    assert primeira is True and segunda is False


def test_metades_nao_se_sobrepoem_e_cobrem_tudo(cenario_que_troca_de_regime):
    """n da 1ª + n da 2ª tem de bater com o total, sem repetir evento."""
    retornos, sinal, sigma, ate = cenario_que_troca_de_regime
    metades = estabilidade(retornos, sinal, {"SPY": +1}, sigma, ate)
    inteira = estabilidade(retornos, sinal, {"SPY": +1}, sigma, ate)

    soma = metades[0][3] + metades[1][3]
    # o último evento de cada metade pode não ter janela fechada; a folga é de
    # no máximo um por metade, e o que o teste barra é vazamento (soma > total)
    assert soma <= len(sinal)
    assert soma >= len(sinal) - 2
    assert inteira[0][3] == metades[0][3]  # determinístico


def test_premissa_oposta_inverte_os_dois_veredictos(cenario_que_troca_de_regime):
    """Trocar o sinal declarado troca ✅ por ❌ nas duas metades — nada assimétrico."""
    retornos, sinal, sigma, ate = cenario_que_troca_de_regime
    metades = estabilidade(retornos, sinal, {"SPY": -1}, sigma, ate)
    assert metades[0][1] is False and metades[1][1] is True


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
