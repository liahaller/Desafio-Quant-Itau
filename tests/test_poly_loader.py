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
    fomc_bucket_bps,
    load_cpi_releases,
    load_fomc_pmf,
    load_history,
    load_payroll_releases,
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


def test_load_cpi_releases_remapeia_shutdown_de_2025(tmp_path):
    csv = tmp_path / "cpi_release_dates.csv"
    csv.write_text(
        "release_date,time_et,mes_referencia,fonte\n"
        "2025-09-11,8:30 AM,August 2025,Polymarket rules\n"     # fora do shutdown
        "2025-10-15,8:30 AM,September 2025,Polymarket rules\n"  # atrasado -> 10-24
        "2025-11-13,8:30 AM,October 2025,Polymarket rules\n",   # nunca publicado
        encoding="utf-8")
    releases = load_cpi_releases(csv)
    assert list(releases["release_date"]) == [pd.Timestamp("2025-09-11"),
                                              pd.Timestamp("2025-10-24")]
    assert releases.loc[0, "nota_tratamento"] == ""
    assert "shutdown" in releases.loc[1, "nota_tratamento"]


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


# --- calendário de payrolls (G9a) --------------------------------------------

# Trecho real do arquivo do Paulo em torno do shutdown de 2025 (mes_referencia
# DERIVADO por "mês do release − 1", que é onde a janela do shutdown quebra).
CABECALHO = "release_date,time_et,mes_referencia,fonte"
JANELA_SHUTDOWN = [
    "2025-09-05,8:30 AM,August 2025,FRED",
    "2025-11-20,8:30 AM,October 2025,FRED [ATENCAO: gap de 76 dias]",
    "2025-12-16,8:30 AM,November 2025,FRED",
    "2026-01-09,8:30 AM,December 2025,FRED",
]


def _csv(tmp_path, linhas):
    caminho = tmp_path / "payrolls.csv"
    caminho.write_text("\n".join([CABECALHO] + linhas) + "\n", encoding="utf-8")
    return caminho


def test_payroll_releases_remapeia_o_shutdown(tmp_path):
    """2025-11-20 é o release de SETEMBRO, não de outubro: o shutdown atrasou
    o cronograma e outubro não teve release próprio."""
    r = load_payroll_releases(_csv(tmp_path, JANELA_SHUTDOWN))
    r = r.set_index(r["release_date"].dt.strftime("%Y-%m-%d"))

    assert r.loc["2025-11-20", "mes_referencia"] == "September 2025"
    assert r.loc["2025-11-20", "mes_referencia_cru"] == "October 2025"   # cru preservado
    assert "shutdown" in r.loc["2025-11-20", "nota_tratamento"]
    # o release combinado out+nov já saía com o mês certo, mas precisa da NOTA
    assert r.loc["2025-12-16", "mes_referencia"] == "November 2025"
    assert "COMBINADO" in r.loc["2025-12-16", "nota_tratamento"]
    # linha fora da janela não é tocada
    assert r.loc["2026-01-09", "nota_tratamento"] == ""
    # outubro/2025 NÃO ganha linha inventada
    assert "October 2025" not in set(r["mes_referencia"])


def test_payroll_releases_falha_alto_se_o_arquivo_mudar_de_forma(tmp_path):
    """O remap do shutdown é exceção declarada, não regra derivável. Se o resto
    do arquivo parar de obedecer a 'mês do release − 1', a exceção virou chute
    e tem de FALHAR, não ser aplicada calada."""
    csv = _csv(tmp_path, JANELA_SHUTDOWN + ["2026-02-11,8:30 AM,November 2025,FRED"])
    with pytest.raises(ValueError, match="shutdown"):
        load_payroll_releases(csv)


def test_payroll_releases_nao_reaplica_correcao_ja_feita_na_fonte(tmp_path):
    """Se o Paulo (ou o FRED) corrigir na origem, o tratamento tem de ser
    idempotente — não pode empurrar a linha um mês a mais."""
    corrigido = [linha.replace("October 2025", "September 2025")
                 for linha in JANELA_SHUTDOWN]
    r = load_payroll_releases(_csv(tmp_path, corrigido))
    assert list(r["mes_referencia"]) == ["August 2025", "September 2025",
                                         "November 2025", "December 2025"]


# --- PMF de decisão do FOMC (parquet do Paulo) -------------------------------

def test_fomc_bucket_bps_le_as_duas_redacoes():
    """As 18 reuniões entregues vêm em dois padrões de título; os dois têm de
    dar o mesmo número, e o `+` da ponta sai marcado separado do valor."""
    assert fomc_bucket_bps("Fed decreases interest rates by 25 bps after 2025 May meeting?") \
        == (-25.0, False)
    assert fomc_bucket_bps("Will the Fed decrease interest rates by 25 bps in January?") \
        == (-25.0, False)
    assert fomc_bucket_bps("Fed decreases interest rates by 75+ bps after X?") == (-75.0, True)
    assert fomc_bucket_bps("Fed raises interest rates by 25+ bps after X?") == (25.0, True)
    assert fomc_bucket_bps("Will the Fed increase interest rates by 50+ bps in X?") == (50.0, True)
    assert fomc_bucket_bps("No change in Fed interest rates after X?") == (0.0, False)
    assert fomc_bucket_bps("Will there be no change in Fed interest rates?") == (0.0, False)
    with pytest.raises(ValueError, match="não reconhecido"):
        fomc_bucket_bps("Fed cuts rates a lot?")


def _parquet_fomc(tmp_path, titulos, n_slots=3):
    """Parquet sintético no formato do `polymarket_fed_reunioes.parquet`."""
    linhas = []
    for i in range(n_slots):
        for j, titulo in enumerate(titulos):
            linhas.append({"data": pd.Timestamp("2025-09-18 12:00:03") + pd.Timedelta(hours=12 * i),
                           "mercado": titulo, "probabilidade": 0.1 * (j + 1),
                           "volume": 1.0, "evento_id": 42})
    caminho = tmp_path / "fomc.parquet"
    pd.DataFrame(linhas).to_parquet(caminho)
    return caminho


def test_load_fomc_pmf_ordena_por_delta_e_marca_as_pontas(tmp_path):
    """Colunas na ordem do Δtaxa (não a do arquivo), pontas abertas marcadas
    e ainda NÃO resolvidas — resolver é a decisão 1.2, a jusante."""
    caminho = _parquet_fomc(tmp_path, [
        "No change in Fed interest rates after X?",
        "Fed increases interest rates by 25+ bps after X?",
        "Fed decreases interest rates by 50+ bps after X?",
        "Fed decreases interest rates by 25 bps after X?",
    ])
    (probs, valores, abertos, reuniao), = load_fomc_pmf(caminho).values()
    assert list(valores) == [-50.0, -25.0, 0.0, 25.0]
    assert list(abertos) == [True, False, False, True]
    assert probs.shape == (3, 4)
    assert probs.index.tz is not None and set(probs.index.hour) <= {0, 12}
    assert reuniao == pd.Timestamp("2025-09-19")  # último slot da série
    # a coluna do bucket de −50 é a do título correspondente, não a 1ª do arquivo
    assert "decreases interest rates by 50+" in probs.columns[0]


def test_load_fomc_pmf_rejeita_faixa_aberta_no_meio(tmp_path):
    """Ponta aberta é regra de PONTA (D1.2). Se um `+` aparecer no miolo, a
    grade mudou de forma e aplicar a regra cega inventaria valor."""
    caminho = _parquet_fomc(tmp_path, [
        "Fed decreases interest rates by 50 bps after X?",
        "Fed decreases interest rates by 25+ bps after X?",   # aberto no meio
        "No change in Fed interest rates after X?",
    ])
    with pytest.raises(ValueError, match="faixa aberta fora das pontas"):
        load_fomc_pmf(caminho)
