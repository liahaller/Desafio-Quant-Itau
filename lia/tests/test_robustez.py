"""Testes da derivação do desfecho das reuniões do FOMC (robustez, item 4).

Casos sintéticos com resultado conhecido:
- `desfecho_bps`: corte de 25 bps lido da taxa efetiva; ruído diário dentro do
  mesmo regime não vira decisão; janela sem dado devolve NaN;
- `bucket_vencedor`: casamento exato nas faixas internas, cobertura além do
  valor nas pontas abertas, e −1 quando nada casa (nunca um palpite).
"""

import numpy as np
import pandas as pd

from lia.rodar_robustez import bucket_vencedor, desfecho_bps

REUNIAO = pd.Timestamp("2026-03-18")


def _dff(antes, depois):
    """Taxa efetiva constante antes e depois da reunião, com o dia dela no meio."""
    dias = pd.date_range(REUNIAO - pd.Timedelta(days=10),
                         REUNIAO + pd.Timedelta(days=10), freq="D")
    valores = [antes if d < REUNIAO else depois for d in dias]
    return pd.Series(valores, index=dias, dtype=float)


def test_desfecho_le_corte_de_25bps():
    assert desfecho_bps(_dff(4.33, 4.08), REUNIAO) == -25.0


def test_desfecho_le_manutencao():
    assert desfecho_bps(_dff(4.33, 4.33), REUNIAO) == 0.0


def test_desfecho_le_alta():
    assert desfecho_bps(_dff(4.33, 4.58), REUNIAO) == 25.0


def test_ruido_diario_nao_vira_decisao():
    """A taxa efetiva oscila alguns bps dentro do mesmo regime."""
    dias = pd.date_range(REUNIAO - pd.Timedelta(days=10),
                         REUNIAO + pd.Timedelta(days=10), freq="D")
    ruido = np.tile([4.33, 4.34, 4.32, 4.33, 4.35], len(dias) // 5 + 1)[:len(dias)]
    assert desfecho_bps(pd.Series(ruido, index=dias), REUNIAO) == 0.0


def test_desfecho_sem_dado_e_nan():
    dff = pd.Series(dtype=float, index=pd.DatetimeIndex([]))
    assert np.isnan(desfecho_bps(dff, REUNIAO))


def test_desfecho_arredonda_para_a_grade_de_25():
    # 4,33 -> 4,10 são 23 bps de queda: a decisão foi de 25
    assert desfecho_bps(_dff(4.33, 4.10), REUNIAO) == -25.0


# ---------------------------------------------------------------------------
# Casamento com a grade de buckets
# ---------------------------------------------------------------------------

VALORES = np.array([-50.0, -25.0, 0.0, 25.0])
ABERTOS = np.array([True, False, False, False])  # só a ponta inferior é aberta


def test_vencedor_casa_faixa_interna():
    assert bucket_vencedor(VALORES, ABERTOS, -25.0) == 1
    assert bucket_vencedor(VALORES, ABERTOS, 0.0) == 2


def test_ponta_aberta_cobre_alem_do_valor():
    """'50+ bps de corte' resolve com 50, 75 ou 100."""
    assert bucket_vencedor(VALORES, ABERTOS, -50.0) == 0
    assert bucket_vencedor(VALORES, ABERTOS, -75.0) == 0
    assert bucket_vencedor(VALORES, ABERTOS, -100.0) == 0


def test_ponta_fechada_nao_cobre_alem():
    """A ponta superior é fechada aqui: 50 de alta não casa com o bucket 25."""
    assert bucket_vencedor(VALORES, ABERTOS, 50.0) == -1


def test_ponta_superior_aberta_cobre_alem():
    abertos = np.array([False, False, False, True])
    assert bucket_vencedor(VALORES, abertos, 75.0) == 3


def test_desfecho_desconhecido_nao_vira_palpite():
    assert bucket_vencedor(VALORES, ABERTOS, float("nan")) == -1
