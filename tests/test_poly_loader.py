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
    diagnostics_qualidade,
    load_cpi_releases,
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


def test_load_cpi_releases_corrige_ano_e_ordena(tmp_path):
    csv = tmp_path / "cpi_release_dates.csv"
    csv.write_text(
        "release_date,time_et,mes_referencia,fonte\n"
        "2025-01-13,8:30 AM,December 2025,Polymarket rules\n"   # typo da fonte
        "2025-03-12,8:30 AM,February 2025,Polymarket rules\n",  # linha correta
        encoding="utf-8")
    releases = load_cpi_releases(csv)
    assert list(releases["release_date"]) == [pd.Timestamp("2025-03-12"),
                                              pd.Timestamp("2026-01-13")]


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


# --- bloco de qualidade para o Ω da Lia --------------------------------------

def _pmf_cru(n_slots, buracos=()):
    """PMF crua sintética de 2 buckets na grade de 12h, com buracos marcados.

    Buraco = linha inteira NaN (o slot não teve leitura em bucket nenhum), que
    é o caso que `n_slots_esperados − n_pontos` tem de contar.
    """
    idx = pd.to_datetime(
        [(T0 + i * SLOT_SECONDS) * 1_000_000_000 for i in range(n_slots)], utc=True)
    frame = pd.DataFrame({"a": 0.4, "b": 0.6}, index=idx)
    frame.iloc[list(buracos)] = float("nan")
    return frame


def test_diagnostics_conta_buraco_e_nao_conta_pre_nascimento():
    """Buraco de leitura e 'mercado não existia' NÃO podem virar a mesma coisa.

    A Lia calcula `esperados − pontos`; se a janela pedida for maior que a vida
    do mercado, os slots que faltam por não-existência entrariam como buraco e
    o veto dela ligaria em cima de mercado íntegro.
    """
    # 6 slots de vida (T0 .. T0+5), com o slot 2 vazio; decisão no último slot.
    cru = _pmf_cru(6, buracos=(2,))
    decisao = cru.index[-1]

    inteiro = diagnostics_qualidade(cru, decisao)
    assert inteiro["n_slots_esperados_janela"] == 6   # T0 até a decisão
    assert inteiro["n_pontos_janela"] == 5            # o buraco não é ponto
    assert inteiro["janela_slots"] is None            # vida inteira: sem janela cravada

    # Janela de 20 slots num mercado que só viveu 6: esperados continua 6.
    largo = diagnostics_qualidade(cru, decisao, janela_slots=20)
    assert largo["n_slots_esperados_janela"] == 6
    assert largo["n_pontos_janela"] == 5

    # Janela curta que NÃO alcança o buraco: zero buraco.
    curto = diagnostics_qualidade(cru, decisao, janela_slots=3)
    assert curto["n_slots_esperados_janela"] == curto["n_pontos_janela"] == 3


def test_diagnostics_idade_do_ultimo_ponto():
    """Leitura velha tem de aparecer como idade > 0, não como ausência."""
    cru = _pmf_cru(4, buracos=(3,))          # o slot da decisão está vazio
    fresco = diagnostics_qualidade(_pmf_cru(4), cru.index[-1])
    velho = diagnostics_qualidade(cru, cru.index[-1])
    assert fresco["idade_ultimo_ponto_h"] == 0.0     # o ponto é o da decisão
    assert velho["idade_ultimo_ponto_h"] == 12.0     # caiu para o slot anterior
    # Sem NENHUM ponto na janela a idade é DESCONHECIDA, nunca 0 (regra da Lia).
    vazio = diagnostics_qualidade(_pmf_cru(4, buracos=(0, 1, 2, 3)), cru.index[-1])
    assert math.isnan(vazio["idade_ultimo_ponto_h"])
    assert vazio["n_pontos_janela"] == 0


def test_diagnostics_data_naive_vira_o_slot_pre_abertura():
    """Data de pregão (naive) tem de casar com o slot das 12:00 UTC — o mesmo
    ponto que `daily_preopen` entrega à view. Se divergir, o diagnóstico
    descreveria um slot diferente do que a view usou."""
    cru = _pmf_cru(4)
    naive = pd.Timestamp(cru.index[-1]).tz_convert(None).normalize()
    assert (diagnostics_qualidade(cru, naive)["serie_janela"]
            == diagnostics_qualidade(cru, cru.index[-1])["serie_janela"])


def test_diagnostics_dp_variacao_so_com_p_inequivoco():
    """Colapsar PMF multi-bucket num escalar é transformação da régua da Lia,
    não minha: sai NaN. Com uma coluna só o `p` é inequívoco e o número sai."""
    multi = diagnostics_qualidade(_pmf_cru(6), _pmf_cru(6).index[-1])
    assert math.isnan(multi["dp_variacao_janela"])

    uma = _pmf_cru(6)[["a"]].copy()
    uma.iloc[:, 0] = [0.40, 0.42, 0.40, 0.42, 0.40, 0.42]
    saida = diagnostics_qualidade(uma, uma.index[-1])
    assert saida["dp_variacao_janela"] == pytest.approx(
        pd.Series([0.40, 0.42, 0.40, 0.42, 0.40, 0.42]).diff().std())


def test_diagnostics_serie_janela_vem_crua():
    """A Lia pediu a série crua para rejanelar sem ida e volta: os valores têm
    de ser os do arquivo, não os já tratados."""
    cru = _pmf_cru(3)
    serie = diagnostics_qualidade(cru, cru.index[-1])["serie_janela"]
    assert [t for t, _ in serie] == list(cru.index)
    assert all(linha == {"a": 0.4, "b": 0.6} for _, linha in serie)
