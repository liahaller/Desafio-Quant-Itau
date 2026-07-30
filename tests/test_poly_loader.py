"""Testes da camada de leitura do Polymarket (casos sintéticos).

Os números vêm do que foi MEDIDO no dado do Paulo (grade de 12h com deriva de
segundos, buckets que morrem, slugs das duas grades), mas o dado aqui é
sintético: o teste não pode depender de arquivo de outro branch.
"""

import json
import math
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from poly_loader import (
    SLOT_SECONDS,
    bucket_value,
    daily_preopen,
    load_history,
    load_pmf,
    series_by_slot,
    to_slots,
)

# 2025-01-08 12:00:00 UTC — bate com o primeiro ponto real do M4 (recessão).
T0 = 1736337600


def escrever(caminho, pontos):
    caminho.write_text(json.dumps({"history": [{"t": t, "p": p} for t, p in pontos]}))


def test_load_history_e_vazio(tmp_path):
    arquivo = tmp_path / "m.json"
    escrever(arquivo, [(T0, 0.195), (T0 + SLOT_SECONDS, 0.185)])
    t, p = load_history(arquivo)
    assert t.tolist() == [T0, T0 + SLOT_SECONDS]
    assert p.tolist() == [0.195, 0.185]

    vazio = tmp_path / "m9.json"
    vazio.write_text('{"history":[]}')  # caso real do M9
    t, p = load_history(vazio)
    assert t.size == 0 and p.size == 0


def test_to_slots_absorve_deriva_de_segundos():
    # deriva medida no dado real: +3 a +9 s; -4 cobre o outro lado da borda.
    slots = to_slots([T0 + 3, T0 + SLOT_SECONDS + 9, T0 + 2 * SLOT_SECONDS - 4])
    assert slots.tolist() == [T0 // SLOT_SECONDS + i for i in range(3)]


def test_to_slots_rejeita_granularidade_fina():
    with pytest.raises(ValueError, match="fidelity=720"):
        to_slots([T0, T0 + 600])  # passo de 10 min (mercado vivo)


def test_series_by_slot_normaliza_indice(tmp_path):
    arquivo = tmp_path / "m.json"
    escrever(arquivo, [(T0 + 3, 0.20), (T0 + SLOT_SECONDS + 7, 0.25)])
    serie = series_by_slot(arquivo)
    assert list(serie.index) == [
        pd.Timestamp("2025-01-08 12:00", tz="UTC"),
        pd.Timestamp("2025-01-09 00:00", tz="UTC"),
    ]
    assert serie.tolist() == [0.20, 0.25]


def test_series_by_slot_descarta_ponto_agora_de_mercado_vivo(tmp_path):
    # caso real: mercado vivo ganha um último ponto no instante do download,
    # fora da grade (medido: 3.410 a 4.431 s de desvio).
    arquivo = tmp_path / "vivo.json"
    escrever(arquivo, [(T0, 0.20), (T0 + SLOT_SECONDS, 0.25),
                       (T0 + SLOT_SECONDS + 4431, 0.26)])
    serie = series_by_slot(arquivo)
    assert len(serie) == 2
    assert serie.index[-1] == pd.Timestamp("2025-01-09 00:00", tz="UTC")

    # ponto fora da grade NO MEIO segue sendo erro (não é o "agora")
    quebrado = tmp_path / "quebrado.json"
    escrever(quebrado, [(T0, 0.2), (T0 + 600, 0.2), (T0 + SLOT_SECONDS, 0.2)])
    with pytest.raises(ValueError, match="fidelity=720"):
        series_by_slot(quebrado)


def test_load_pmf_alinha_derivas_diferentes_e_deixa_nan(tmp_path):
    # dois buckets do mesmo mercado com deriva DIFERENTE no mesmo slot, e o
    # primeiro morrendo antes do segundo (caso do M3).
    escrever(tmp_path / "M3_will-no-fed-rate-cuts-happen-in-2025_111.json",
             [(T0 + 3, 0.4), (T0 + SLOT_SECONDS + 3, 0.3)])
    escrever(tmp_path / "M3_will-2-fed-rate-cuts-happen-in-2025_222.json",
             [(T0 + 8, 0.6), (T0 + SLOT_SECONDS + 9, 0.7),
              (T0 + 2 * SLOT_SECONDS + 5, 0.9)])
    pmf = load_pmf(tmp_path, "M3_")

    assert list(pmf.columns) == ["will-no-fed-rate-cuts-happen-in-2025",
                                 "will-2-fed-rate-cuts-happen-in-2025"]
    assert len(pmf) == 3                       # deriva não criou linha extra
    assert pmf.iloc[0].tolist() == [0.4, 0.6]  # buckets alinhados no mesmo slot
    # bucket morto vira NaN, nunca zero (decisão 6.1 é de quem consome)
    assert math.isnan(pmf.iloc[2, 0]) and pmf.iloc[2, 1] == 0.9


def test_daily_preopen_pega_o_slot_das_12h(tmp_path):
    arquivo = tmp_path / "m.json"
    escrever(arquivo, [(T0, 0.20),                       # 08/01 12:00 UTC
                       (T0 + SLOT_SECONDS, 0.25),        # 09/01 00:00 UTC
                       (T0 + 2 * SLOT_SECONDS, 0.30),    # 09/01 12:00 UTC
                       (T0 + 4 * SLOT_SECONDS, 0.40)])   # 10/01 12:00 UTC
    diaria = daily_preopen(series_by_slot(arquivo))
    assert list(diaria.index) == [pd.Timestamp("2025-01-08"),
                                  pd.Timestamp("2025-01-09"),
                                  pd.Timestamp("2025-01-10")]
    assert diaria.tolist() == [0.20, 0.30, 0.40]  # o ponto das 00:00 fica fora


def test_daily_preopen_nao_preenche_buraco(tmp_path):
    arquivo = tmp_path / "m.json"
    escrever(arquivo, [(T0, 0.20), (T0 + 4 * SLOT_SECONDS, 0.40)])  # falta 09/01
    diaria = daily_preopen(series_by_slot(arquivo))
    assert list(diaria.index) == [pd.Timestamp("2025-01-08"), pd.Timestamp("2025-01-10")]


def test_bucket_value_cpi_incluindo_inversao_de_sinal():
    assert bucket_value("will-monthly-inflation-increase-by-0pt3") == 0.3
    assert bucket_value("will-monthly-inflation-increase-by-1pt0") == 1.0
    assert bucket_value("will-monthly-inflation-stay-flat-0pt0-in") == 0.0
    # grade de jul/2026: rótulos falam em QUEDA — sinal negativo
    assert bucket_value("will-monthly-inflation-decrease-by-0pt2") == -0.2


def test_bucket_value_fed_e_bucket_aberto():
    assert bucket_value("will-no-fed-rate-cuts-happen-in-2025") == 0.0
    assert bucket_value("will-3-fed-rate-cuts-happen-in-2025") == 3.0
    assert math.isnan(bucket_value("will-8plus-fed-rate-cuts-happen-in-2025"))


def test_bucket_value_rejeita_slug_desconhecido():
    with pytest.raises(ValueError, match="não reconhecido"):
        bucket_value("us-recession-in-2025")
