"""Testes sintéticos de `scripts/cristalizacao_entropia.py`. Felipe.

Casos com resultado conhecido a mão, na regra do CLAUDE.md §5: a conclusão que
o script sustenta (perfil de entropia e de variação por distância ao evento)
só vale se as três contas — variação total, distância e agregação — estiverem
certas nos casos em que a resposta é óbvia.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cristalizacao_entropia import com_distancia, medidas_por_dia, perfil  # noqa: E402


def _pmf(linhas, datas):
    return pd.DataFrame(linhas, index=pd.to_datetime(datas), columns=["a", "b"])


def test_variacao_total_e_entropia_em_caso_conhecido():
    """Uniforme -> entropia 1; toda a massa num balde -> 0. Variação = Σ|Δp|."""
    pmf = _pmf([[0.5, 0.5], [0.3, 0.7], [1.0, 0.0]],
               ["2026-01-01", "2026-01-02", "2026-01-03"])
    m = medidas_por_dia(pmf)
    assert np.isclose(m["entropia"].iloc[0], 1.0)
    assert np.isclose(m["entropia"].iloc[2], 0.0) or np.isnan(m["entropia"].iloc[2])
    assert np.isnan(m["variacao"].iloc[0])          # sem dia anterior
    assert np.isclose(m["variacao"].iloc[1], 0.4)   # |0,3−0,5| + |0,7−0,5|
    assert m["n_baldes"].tolist() == [2, 2, 1]      # o balde zerado sai do denominador


def test_dia_nao_adjacente_nao_vira_variacao():
    """Buraco no meio mede vários dias — tem de sair NaN, não número inflado."""
    pmf = _pmf([[0.5, 0.5], [0.9, 0.1]], ["2026-01-01", "2026-01-05"])
    assert np.isnan(medidas_por_dia(pmf)["variacao"].iloc[1])


def test_distancia_descarta_o_que_vem_depois_do_evento():
    pmf = _pmf([[0.5, 0.5]] * 3, ["2026-01-01", "2026-01-02", "2026-01-03"])
    quadro = com_distancia(medidas_por_dia(pmf), "2026-01-02")
    assert quadro["dias"].tolist() == [1, 0]


def test_perfil_separa_as_faixas_e_conta_so_entropia_viva():
    """Duas faixas com médias conhecidas, e a linha sem entropia não conta no n."""
    quadro = pd.DataFrame({"entropia": [0.2, 0.8, 0.6, np.nan],
                           "variacao": [0.1, 0.3, 0.5, 0.7],
                           "n_baldes": [3, 3, 3, 3],
                           "dias": [0, 1, 2, 0]})
    tabela = perfil(quadro, faixas=[(0, 0), (1, 2)])
    assert tabela.loc["d = 0", "n"] == 1
    assert np.isclose(tabela.loc["d = 0", "entropia média"], 0.2)
    assert tabela.loc["1–2 dias", "n"] == 2
    assert np.isclose(tabela.loc["1–2 dias", "entropia média"], 0.7)
    assert np.isclose(tabela.loc["1–2 dias", "variação total média"], 0.4)


if __name__ == "__main__":
    test_variacao_total_e_entropia_em_caso_conhecido()
    test_dia_nao_adjacente_nao_vira_variacao()
    test_distancia_descarta_o_que_vem_depois_do_evento()
    test_perfil_separa_as_faixas_e_conta_so_entropia_viva()
    print("ok")
