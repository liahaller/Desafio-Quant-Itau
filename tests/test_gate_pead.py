"""Testes das duas medidas novas do `gate_pead.py` (Felipe).

O que está sendo protegido é a regra da **véspera**: se a leitura do dia do
próprio anúncio entrar no E_poly, a "surpresa" passa a conter a resolução e o
PEAD vira lookahead puro — um erro que produz números lindos e falsos.
"""

import sys
import types
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gate_pead import resolucoes_binarias, surpresas_fomc  # noqa: E402


def montador_falso(probs, valores):
    """Stub com o mínimo que `surpresas_fomc` toca: `fomc_pmfs` e `_fl`.

    `_fl` = identidade, para o teste medir a regra da véspera e não a correção
    de favorite-longshot (que tem teste próprio em `test_poly_preprocessing`).
    """
    reuniao = pd.Timestamp("2025-06-18")
    return types.SimpleNamespace(
        fomc_pmfs={reuniao: (probs, np.asarray(valores, dtype=float), None)},
        _fl=lambda p: p,
    ), reuniao


@pytest.fixture
def pmf_com_leitura_no_dia():
    """PMF de três dias: duas antes da reunião e uma NO dia da reunião.

    Véspera (17/06): 50/50 entre 0 e −25 -> E_poly = −12,5 bps.
    Dia da reunião (18/06): já toda em −25 -> E_poly = −25 (é a resolução
    vazando; entrar com ela zeraria a surpresa).
    """
    datas = pd.to_datetime(["2025-06-16", "2025-06-17", "2025-06-18"])
    probs = pd.DataFrame([[0.8, 0.2], [0.5, 0.5], [0.0, 1.0]],
                         index=datas, columns=["0bp", "-25bp"])
    return probs, [0.0, -25.0]


def test_vespera_e_a_ultima_leitura_ANTES_da_reuniao(pmf_com_leitura_no_dia):
    """A leitura do dia do anúncio não entra — é resolução, não expectativa."""
    probs, valores = pmf_com_leitura_no_dia
    montador, reuniao = montador_falso(probs, valores)
    real = pd.Series({reuniao: -25.0})

    surpresa = surpresas_fomc(montador, real)
    # E_poly da véspera = 0,5·0 + 0,5·(−25) = −12,5; surpresa = −25 − (−12,5)
    assert surpresa[reuniao] == pytest.approx(-12.5)
    # se a leitura do dia entrasse, a surpresa seria 0 — o valor que denuncia
    assert surpresa[reuniao] != pytest.approx(0.0)


def test_vespera_pula_buraco_no_dado(pmf_com_leitura_no_dia):
    """Sem leitura no dia anterior, a véspera é a última que existe.

    O poly tem buracos de 24/36/48h; ancorar em "D−1 do calendário" faria um
    feriado virar reunião sem surpresa.
    """
    probs, valores = pmf_com_leitura_no_dia
    probs = probs.drop(index=pd.Timestamp("2025-06-17"))  # some a véspera
    montador, reuniao = montador_falso(probs, valores)
    real = pd.Series({reuniao: -25.0})

    surpresa = surpresas_fomc(montador, real)
    # cai para 16/06: E_poly = 0,8·0 + 0,2·(−25) = −5 -> surpresa = −20
    assert surpresa[reuniao] == pytest.approx(-20.0)


def test_reuniao_sem_decisao_realizada_sai_fora(pmf_com_leitura_no_dia):
    """Parear é condição: sem o realizado não há surpresa, e não se chuta."""
    probs, valores = pmf_com_leitura_no_dia
    montador, _reuniao = montador_falso(probs, valores)
    assert surpresas_fomc(montador, pd.Series(dtype=float)).empty


def test_reuniao_sem_leitura_anterior_sai_fora():
    """PMF que só começa no dia da reunião não tem véspera — não entra."""
    reuniao = pd.Timestamp("2025-06-18")
    probs = pd.DataFrame([[0.0, 1.0]], index=[reuniao], columns=["0bp", "-25bp"])
    montador = types.SimpleNamespace(
        fomc_pmfs={reuniao: (probs, np.array([0.0, -25.0]), None)},
        _fl=lambda p: p)
    assert surpresas_fomc(montador, pd.Series({reuniao: -25.0})).empty


def test_resolucao_binaria_le_o_ultimo_par(tmp_path):
    """`p final` e `p véspera` são as duas últimas leituras, nessa ordem."""
    import json
    # `series_by_slot` lê o formato de history do CLOB e exige a grade de 12h
    # (fidelity=720). 12h UTC é o slot pré-abertura de Nova York.
    historico = {"history": [
        {"t": int(pd.Timestamp("2025-04-14 12:00", tz="UTC").timestamp()), "p": 0.30},
        {"t": int(pd.Timestamp("2025-04-15 12:00", tz="UTC").timestamp()), "p": 0.99},
    ]}
    (tmp_path / "M6_china_tariffs_teste_1.json").write_text(json.dumps(historico))

    tabela = resolucoes_binarias(tmp_path)
    linha = tabela[tabela["mercado"] == "M6 tarifas China"].iloc[0]
    assert linha["p final"] == pytest.approx(0.99)
    assert linha["p véspera"] == pytest.approx(0.30)
    assert linha["surpresa (p.p.)"] == pytest.approx(69.0)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
