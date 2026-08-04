"""Teste mínimo do proxy de surpresa de FOMC (`scripts/surpresa_fomc.py`)."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from surpresa_fomc import surpresas_em_fomc, t_dos_betas  # noqa: E402


def _serie(valores, inicio="2025-01-01"):
    return pd.Series(valores, index=pd.date_range(inicio, periods=len(valores), freq="D"))


def test_converte_pontos_percentuais_em_bps():
    """DTB3 sobe 0,10 pp -> surpresa de +10 bps."""
    dtb3 = _serie([4.00, 4.10, 4.10])
    s = surpresas_em_fomc(dtb3, [pd.Timestamp("2025-01-02")])
    assert abs(float(s.iloc[0]) - 10.0) < 1e-9


def test_data_de_fomc_sem_leitura_nao_aparece():
    """Feriado/fim de semana no dia do anúncio sai da amostra, não vira zero."""
    dtb3 = _serie([4.00, 4.05, 4.05])
    s = surpresas_em_fomc(dtb3, [pd.Timestamp("2025-06-30")])
    assert s.empty


def test_primeira_observacao_nao_vira_surpresa():
    """Sem dia anterior não há variação — a linha cai (diff = NaN)."""
    dtb3 = _serie([4.00, 4.05])
    s = surpresas_em_fomc(dtb3, [pd.Timestamp("2025-01-01")])
    assert s.empty


def test_t_dos_betas_recupera_relacao_plantada():
    """Retorno = −0,001 × surpresa + ruído pequeno -> |t| grande e sinal certo."""
    rng = np.random.default_rng(0)
    s = pd.Series(rng.normal(scale=5.0, size=200))
    r = pd.DataFrame({"SPY": -0.001 * s + rng.normal(scale=0.0005, size=200)})
    t = t_dos_betas(r, s)
    assert t["SPY"] < -10
