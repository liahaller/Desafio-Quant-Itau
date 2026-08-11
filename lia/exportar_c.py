"""Série de `c` por decisão — o artefato pedido pelo Felipe em 10/08/2026.

A `Curva_c.md` dele varre um `c` **constante**, aplicado às duas views todo
dia. Isso não mede a régua: o efeito dela está na cauda (Decisão 6j), e grade
constante apaga por construção justamente a diferenciação entre mercado bom e
ruim que é a função do Ω. Com a série real, a curva passa a ser plotada no eixo
do **nível**, que é o eixo em que a escolha de 13/08 tem de ser feita (6d).

O que sai, por linha (`data`, `view`, `mercado`):

- `c_nivel1` — a régua da 6g com `nivel = 1`, que é o **produto dos fatores**.
  Qualquer outro nível sai por potenciação, sem nova rodada:

      c(nivel) = c_nivel1 ** nivel

  É por isso que a série não é exportada nível a nível: a régua é
  `((1 + v̄)(1 + |Σp − 1|)) ** nivel`, e o expoente é o único botão.
- `fator_estabilidade`, `fator_coerencia` — os dois fatores separados, para
  diagnóstico do lado dele (qual defeito está tirando peso em cada dia).
- `ativa` + `motivo_inativa` — a máscara, com os DOIS motivos separados
  (veto de volume · ausência de par adjacente completo). O motivo não entra na
  assinatura de `calcular_omega`, que trata os dois igual de propósito; aqui é
  coluna de log, que é o lugar que o Felipe pediu para ele ficar.
- `selecionado` — é este o mercado que a view consome nesta data, pela regra
  do backtest dele (abaixo).

**As duas views saem COM portão de volume desde 10/08/2026.** O Paulo entregou
o G5 do FOMC (`conditionId` no parquet + as 76 faixas × 18 reuniões), que era o
bloqueio do `PEDIDO_Paulo_G5_fomc.md`. A coluna `tem_portao` continua no CSV,
agora `True` nas duas views — ela marca por linha se houve leitura de volume
com que qualificar o `c`.

⚠️ Na 2.3 o portão **julga menos slots** que na 2.2: 42 das 76 faixas bateram o
cap de 20k trades do `/trades`, e slot com faixa truncada sai `NaN` (não veta,
pela 6b). O truncamento morde os slots antigos, não o run-up da reunião.

**Regra de seleção do mercado, lida do módulo do Felipe, não inventada aqui.**
Em 80 das 496 datas da 2.2 há mais de um mercado-mês vivo (2 ou 3), então
`{data: {view: c}}` exige escolher um. O `_view_2_2`/`_view_2_3` do
`scripts/backtest_v1.py` (`origin/Felipe`) usa `min(eventos futuros)` — vale o
mercado do **próximo** evento. É o que `selecionado` reproduz. A série completa
sai junto de propósito: se a regra dele mudar, o casamento se refaz do CSV, sem
nova rodada deste script.

Uso:

    python -m lia.exportar_c --dados <dir com data/ e src/> --saida <csv>
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from lia.calibracao_omega import agregar_volume_slot
from lia.omega import calcular_omega, fator_coerencia, fator_estabilidade, pmf_da_serie_janela
from lia.rodar_calibracao_cpi import _prefixos_sem_duplicata

# Calibrados na 6g; sem default no módulo de lógica, explícitos aqui.
JANELA_VARIACOES = 5
JANELA_SLOTS = JANELA_VARIACOES + 1  # off-by-one do `diagnostics` (6g)
NIVEL_BASE = 1.0  # o expoente neutro: `c_nivel1` é o produto dos fatores

VIEW_22 = "2.2_inflacao"
VIEW_23 = "2.3_fed"


def _importar_pipeline(raiz):
    """Loader do pipeline — do branch `Felipe`, que tem o remap do CPI (6i)."""
    sys.path.insert(0, str(Path(raiz) / "src"))
    import poly_loader

    return poly_loader


def mercados_cpi(raiz, loader):
    """`{prefixo do mercado: data de divulgação}` da 2.2.

    O casamento sai da coluna `fonte` do calendário, que traz o slug do mercado
    entre parênteses; o prefixo do arquivo TERMINA nesse slug (alguns trazem
    rótulo do Paulo na frente, como `CPI_G4_janeiro-2026_`). Casar por sufixo
    em vez de montar `CPI_<slug>_` alcança esses — o mercado de jan/2026 não
    seria encontrado pela montagem literal.

    Mercado sem release no calendário fica de fora: sem data não há o que
    selecionar, e inventar uma criaria evento que não existe.
    """
    releases = loader.load_cpi_releases(Path(raiz) / "data" / "raw" / "cpi_release_dates.csv")
    slug_release = {
        fonte.split("(")[-1].rstrip(")"): data
        for fonte, data in zip(releases.fonte, releases.release_date)
    }
    diretorio = Path(raiz) / "data" / "raw" / "clob_exploracao"
    prefixos = _prefixos_sem_duplicata(diretorio, slug_release)
    casados = {}
    for prefixo in prefixos:
        data = next((d for slug, d in slug_release.items() if prefixo.endswith(slug)), pd.NaT)
        if pd.notna(data):
            casados[prefixo] = pd.Timestamp(data)
    return casados


def volume_por_slot(raiz, view):
    """G5 da 2.2 agregado por SOMA das faixas: `{(mercado, slot): notional}`.

    Soma, não mínimo (6g): o mínimo veta 47% dos slots de 12h porque é comum
    uma faixa não negociar em meio dia. A agregação é a mesma da calibração
    (`agregar_volume_slot`), que preserva `0` × `NaN` no nível do slot.
    """
    caminho = Path(raiz) / "data" / "raw" / "g5_volume_no_tempo.csv"
    g5 = pd.read_csv(caminho, parse_dates=["slot_utc"])
    g5 = g5[g5.view == view].copy()
    if g5.empty:
        return pd.Series(dtype=float)
    g5["evento"] = g5.mercado.str.split("_will-").str[0]
    g5["slot_utc"] = g5.slot_utc.dt.tz_localize("UTC")
    return agregar_volume_slot(g5).soma


def volume_fomc_por_slot(raiz):
    """G5 da 2.3 agregado por reunião: `{(evento_id, slot): notional}`.

    A chave é o `conditionId` que o Paulo pôs no parquet em 10/08 — a junção
    por título dava 0 em comum, e era esse o bloqueio. O mapa
    `conditionId → evento_id` sai do próprio parquet, então volume e PMF são
    atribuídos à mesma reunião pela mesma fonte.
    """
    caminho = Path(raiz) / "data" / "raw" / "g5_volume_no_tempo.csv"
    parquet = pd.read_parquet(Path(raiz) / "data" / "polymarket_fed_reunioes.parquet")
    mapa = parquet.drop_duplicates("conditionId").set_index("conditionId")
    mapa = mapa.evento_id.astype(int)

    g5 = pd.read_csv(caminho, parse_dates=["slot_utc"])
    g5 = g5[g5.view.astype(str) == "2.3"].copy()
    if g5.empty:
        return pd.Series(dtype=float)
    g5["evento"] = g5.conditionId.map(mapa)
    if g5.evento.isna().any():
        raise ValueError("G5 da 2.3 tem conditionId fora do parquet")
    g5["slot_utc"] = g5.slot_utc.dt.tz_localize("UTC")
    return agregar_volume_slot(g5).soma


def linha_da_decisao(loader, pmf, slot, view, volume, tem_portao):
    """Roda a régua num slot de decisão e devolve a linha do CSV.

    O bloco de entrada é montado pelo `diagnostics_qualidade` do pipeline — o
    mesmo caminho da produção, e não uma reconstrução paralela da janela.
    """
    bloco = loader.diagnostics_qualidade(pmf, slot, janela_slots=JANELA_SLOTS)
    bloco["view"] = view
    c, ativa = calcular_omega([bloco], {view: volume}, nivel=NIVEL_BASE,
                              janela_variacoes=JANELA_VARIACOES)

    janela = pmf_da_serie_janela(bloco["serie_janela"])
    estabilidade = fator_estabilidade(janela, JANELA_VARIACOES)
    coerencia = fator_coerencia(janela)

    vetado = bool(pd.notna(volume) and volume <= 0)
    if ativa[view]:
        motivo = ""
    elif vetado:
        motivo = "volume_zero"
    else:
        motivo = "sem_par_adjacente"

    return {
        "data": slot.tz_convert(None).normalize(),
        "view": view,
        "c_nivel1": c[view],
        "ativa": ativa[view],
        "motivo_inativa": motivo,
        "fator_estabilidade": estabilidade,
        "fator_coerencia": coerencia,
        "volume_notional": volume,
        "tem_portao": tem_portao,
        "n_pontos_janela": bloco["n_pontos_janela"],
        "n_slots_esperados_janela": bloco["n_slots_esperados_janela"],
    }


def serie_cpi(raiz, loader):
    """Linhas da view 2.2, uma por (slot de decisão, mercado-mês)."""
    diretorio = Path(raiz) / "data" / "raw" / "clob_exploracao"
    releases = mercados_cpi(raiz, loader)
    volumes = volume_por_slot(raiz, "2.2")

    linhas = []
    for prefixo, release in releases.items():
        pmf = loader.load_pmf(diretorio, f"{prefixo}_")
        for slot in pmf.index[pmf.index.hour == 12]:
            volume = volumes.get((prefixo, slot), np.nan)
            linha = linha_da_decisao(loader, pmf, slot, VIEW_22, volume,
                                     tem_portao=True)
            linha["mercado"] = prefixo
            linha["evento"] = release
            linhas.append(linha)
    return pd.DataFrame(linhas)


def serie_fomc(raiz, loader):
    """Linhas da view 2.3, uma por (slot de decisão, reunião).

    Com portão desde 10/08. Onde o G5 não alcança (slot com faixa truncada
    pelo cap de 20k), o volume entra `NaN`, que pela 6b **não veta** — é
    ignorância nossa sobre a liquidez, não iliquidez medida.
    """
    eventos = loader.load_fomc_pmf(Path(raiz) / "data" / "polymarket_fed_reunioes.parquet")
    volumes = volume_fomc_por_slot(raiz)
    linhas = []
    for evento, (probs, _valores, _abertos, reuniao) in eventos.items():
        for slot in probs.index[probs.index.hour == 12]:
            volume = volumes.get((evento, slot), np.nan)
            linha = linha_da_decisao(loader, probs, slot, VIEW_23, volume,
                                     tem_portao=True)
            linha["mercado"] = f"FOMC_{evento}"
            linha["evento"] = pd.Timestamp(reuniao)
            linhas.append(linha)
    return pd.DataFrame(linhas)


def marcar_selecionado(tabela):
    """`selecionado`: o mercado do PRÓXIMO evento em cada (data, view).

    Regra do `_view_2_2`/`_view_2_3` do backtest do Felipe — `min` dos eventos
    ainda não ocorridos. Empate remanescente é resolvido pelo nome, de forma
    determinística, e a coluna `mercado` deixa a escolha auditável.

    O empate que a versão de 10/08 citava aqui (`M1_cpi_monthly` ×
    `CPI_july-inflation-monthly`) **não era empate entre dois mercados**: eram
    os mesmos tokenIds sob dois rótulos, e jul/2025 entrava duas vezes. Agora
    a duplicata é removida na leitura (`_prefixos_sem_duplicata`).
    """
    futuro = tabela.evento >= tabela.data
    candidatos = tabela[futuro].sort_values(["data", "view", "evento", "mercado"])
    escolhidos = candidatos.groupby(["data", "view"]).head(1).index
    return tabela.index.isin(escolhidos)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dados", required=True, help="dir com data/ e src/")
    ap.add_argument("--saida", required=True, help="CSV de saída")
    args = ap.parse_args()

    loader = _importar_pipeline(args.dados)
    tabela = pd.concat([serie_cpi(args.dados, loader), serie_fomc(args.dados, loader)],
                       ignore_index=True)
    tabela["dias_corridos_ate_evento"] = (tabela.evento - tabela.data).dt.days
    tabela["selecionado"] = marcar_selecionado(tabela)
    tabela = tabela.sort_values(["view", "data", "mercado"])

    colunas = ["data", "view", "mercado", "evento", "dias_corridos_ate_evento",
               "selecionado", "ativa", "motivo_inativa", "c_nivel1",
               "fator_estabilidade", "fator_coerencia", "volume_notional",
               "tem_portao", "n_pontos_janela", "n_slots_esperados_janela"]
    tabela[colunas].to_csv(args.saida, index=False, float_format="%.6f")

    print(f"escrito: {args.saida} — {len(tabela)} linhas")
    for view, grupo in tabela.groupby("view"):
        sel = grupo[grupo.selecionado]
        ativas = sel[sel.ativa]
        print(f"\n-- {view} --")
        print(f"   linhas: {len(grupo)} · selecionadas: {len(sel)} "
              f"em {sel.data.nunique()} datas · mercados: {grupo.mercado.nunique()}")
        print(f"   ativas (selecionadas): {len(ativas)} ({len(ativas) / len(sel):.1%})")
        print(f"   inativas: {(sel.motivo_inativa == 'volume_zero').sum()} por volume · "
              f"{(sel.motivo_inativa == 'sem_par_adjacente').sum()} por ausência de par")
        if len(ativas):
            print(f"   c (nível 1): min {ativas.c_nivel1.min():.4f} · "
                  f"mediana {ativas.c_nivel1.median():.4f} · "
                  f"p95 {ativas.c_nivel1.quantile(0.95):.4f} · "
                  f"max {ativas.c_nivel1.max():.4f}")
            for nivel in (2, 3, 5):
                elevado = ativas.c_nivel1 ** nivel
                print(f"     nível {nivel}: mediana {elevado.median():.4f} · "
                      f"p95 {elevado.quantile(0.95):.4f} · max {elevado.max():.4f}")


if __name__ == "__main__":
    main()
