"""Testes do exportador da série de `c` por decisão (artefato de 10/08/2026).

Casos sintéticos com resultado conhecido:
- seleção do mercado: vale o do PRÓXIMO evento, um por (data, view), e o
  mercado cujo evento já passou nunca é selecionado (regra do backtest do
  Felipe, replicada aqui);
- a linha da decisão carrega os dois motivos de `ativa = False` separados,
  que é a informação que a assinatura de `calcular_omega` não devolve;
- `c_nivel1` é o produto dos fatores, que é o que permite obter qualquer
  nível por potenciação sem nova rodada;
- volume ausente não veta e volume zero veta (6b), com o motivo certo.
"""

import numpy as np
import pandas as pd

from lia.exportar_c import linha_da_decisao, marcar_selecionado


class _LoaderFake:
    """Stub do pipeline: só o `diagnostics_qualidade` é consumido aqui.

    Devolve a série inteira como janela — o recorte fino já é testado em
    `test_omega.py`, e o que interessa neste arquivo é a linha do CSV.
    """

    def __init__(self, pmf):
        self.pmf = pmf

    def diagnostics_qualidade(self, pmf, slot, janela_slots=None):
        pontos = pmf[pmf.index <= slot].dropna(how="all")
        return {
            "serie_janela": [(t, linha.to_dict()) for t, linha in pontos.iterrows()],
            "n_pontos_janela": len(pontos),
            "n_slots_esperados_janela": len(pontos),
        }


def _pmf(linhas, inicio="2026-01-01 00:00"):
    indice = pd.date_range(inicio, periods=len(linhas), freq="12h", tz="UTC")
    return pd.DataFrame(linhas, index=indice)


# ---------------------------------------------------------------------------
# Seleção do mercado do dia
# ---------------------------------------------------------------------------


def _tabela(linhas):
    return pd.DataFrame(linhas, columns=["data", "view", "mercado", "evento"]).assign(
        data=lambda t: pd.to_datetime(t.data), evento=lambda t: pd.to_datetime(t.evento)
    )


def test_selecionado_e_o_mercado_do_proximo_evento():
    tabela = _tabela([
        ("2026-01-05", "2.2_inflacao", "fevereiro", "2026-02-10"),
        ("2026-01-05", "2.2_inflacao", "janeiro", "2026-01-13"),
    ])
    assert list(marcar_selecionado(tabela)) == [False, True]


def test_mercado_com_evento_passado_nunca_e_selecionado():
    tabela = _tabela([
        ("2026-01-20", "2.2_inflacao", "janeiro", "2026-01-13"),
        ("2026-01-20", "2.2_inflacao", "fevereiro", "2026-02-10"),
    ])
    assert list(marcar_selecionado(tabela)) == [False, True]


def test_view_de_mercado_unico_e_sempre_selecionada():
    """15g: sem evento datado, `evento` é NaT e a view é a sua própria escolha.

    Sem este caso, `NaT >= data` seria False e a `B_trajetoria_propria`
    sumiria da série inteira — o mercado M3 é um só, não há concorrente a
    desempatar, e a view lê o mesmo mercado todo pregão.
    """
    tabela = _tabela([
        ("2026-01-05", "B_trajetoria_propria", "M3_fed_trajectory", None),
        ("2026-01-06", "B_trajetoria_propria", "M3_fed_trajectory", None),
    ])
    assert list(marcar_selecionado(tabela)) == [True, True]


def test_view_sem_evento_nao_rouba_selecao_de_outra_view():
    """A seleção é por (data, view): NaT numa view não afeta a vizinha."""
    tabela = _tabela([
        ("2026-01-05", "B_trajetoria_propria", "M3_fed_trajectory", None),
        ("2026-01-05", "2.2_inflacao", "janeiro", "2026-01-13"),
        ("2026-01-05", "2.2_inflacao", "fevereiro", "2026-02-10"),
    ])
    assert list(marcar_selecionado(tabela)) == [True, True, False]


def test_dia_do_evento_ainda_seleciona_o_proprio_mercado():
    """`>= data`: no dia do evento o mercado ainda é o dele.

    Quem descarta o dia da divulgação é a cascata do Felipe (`faltam < 1`),
    não esta seleção — a coluna `dias_corridos_ate_evento` deixa o corte
    visível do lado dele.
    """
    tabela = _tabela([("2026-01-13", "2.2_inflacao", "janeiro", "2026-01-13")])
    assert list(marcar_selecionado(tabela)) == [True]


def test_uma_selecao_por_data_e_view():
    tabela = _tabela([
        ("2026-01-05", "2.2_inflacao", "janeiro", "2026-01-13"),
        ("2026-01-05", "2.2_inflacao", "fevereiro", "2026-02-10"),
        ("2026-01-05", "2.3_fed", "fomc_marco", "2026-03-18"),
        ("2026-01-05", "2.3_fed", "fomc_janeiro", "2026-01-28"),
    ])
    tabela["selecionado"] = marcar_selecionado(tabela)
    contagem = tabela[tabela.selecionado].groupby(["data", "view"]).size()
    assert (contagem == 1).all()
    assert set(tabela[tabela.selecionado].mercado) == {"janeiro", "fomc_janeiro"}


def test_empate_no_mesmo_evento_resolve_deterministicamente():
    """Dois mercados para o mesmo release (M1 × CPI_july): escolha estável."""
    tabela = _tabela([
        ("2026-01-05", "2.2_inflacao", "M1_cpi", "2026-01-13"),
        ("2026-01-05", "2.2_inflacao", "CPI_janeiro", "2026-01-13"),
    ])
    primeira = list(marcar_selecionado(tabela))
    segunda = list(marcar_selecionado(tabela.iloc[::-1].copy()))
    assert sum(primeira) == 1
    assert primeira == segunda[::-1]  # a ordem das linhas não muda a escolha


# ---------------------------------------------------------------------------
# A linha da decisão
# ---------------------------------------------------------------------------


PARADA = [{"a": 0.5, "b": 0.5}] * 8


def test_c_nivel1_e_o_produto_dos_fatores():
    pmf = _pmf([{"a": 0.5, "b": 0.5}, {"a": 0.6, "b": 0.4}, {"a": 0.55, "b": 0.45},
                {"a": 0.5, "b": 0.52}, {"a": 0.48, "b": 0.5}, {"a": 0.5, "b": 0.5}])
    linha = linha_da_decisao(_LoaderFake(pmf), pmf, pmf.index[-1], "2.2_inflacao",
                             volume=1000.0, tem_portao=True)
    assert linha["ativa"]
    assert linha["c_nivel1"] == (
        linha["fator_estabilidade"] * linha["fator_coerencia"])
    assert linha["c_nivel1"] >= 1.0


def test_qualquer_nivel_sai_por_potenciacao():
    """O contrato do artefato: `c(nivel) = c_nivel1 ** nivel`."""
    pmf = _pmf(PARADA)
    linha = linha_da_decisao(_LoaderFake(pmf), pmf, pmf.index[-1], "2.2_inflacao",
                             volume=500.0, tem_portao=True)
    assert linha["c_nivel1"] == 1.0  # mercado parado e livro fechado
    assert linha["c_nivel1"] ** 5 == 1.0


def test_volume_zero_veta_com_motivo_de_volume():
    pmf = _pmf(PARADA)
    linha = linha_da_decisao(_LoaderFake(pmf), pmf, pmf.index[-1], "2.2_inflacao",
                             volume=0.0, tem_portao=True)
    assert not linha["ativa"]
    assert linha["motivo_inativa"] == "volume_zero"
    assert np.isnan(linha["c_nivel1"])


def test_volume_ausente_nao_veta():
    """NaN é ignorância nossa, não iliquidez medida (6b) — é o caso da 2.3."""
    pmf = _pmf(PARADA)
    linha = linha_da_decisao(_LoaderFake(pmf), pmf, pmf.index[-1], "2.3_fed",
                             volume=np.nan, tem_portao=False)
    assert linha["ativa"]
    assert linha["motivo_inativa"] == ""


def test_sem_par_adjacente_sai_com_motivo_proprio():
    """Uma leitura só na janela: não há variação para medir."""
    pmf = _pmf([{"a": 0.5, "b": 0.5}])
    linha = linha_da_decisao(_LoaderFake(pmf), pmf, pmf.index[-1], "2.2_inflacao",
                             volume=1000.0, tem_portao=True)
    assert not linha["ativa"]
    assert linha["motivo_inativa"] == "sem_par_adjacente"
