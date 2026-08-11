"""Roda o teste de monotonicidade sobre o dado real do FOMC (Decisão 6).

Escolhe a forma funcional dos ingredientes do Ω pelo protocolo registrado em
08/07: faixas de confiança maiores devem apresentar erro realizado da
probabilidade menor; empates resolvem pela forma com menos parâmetros.

Escopo — **os quatro ingredientes**, desde 10/08/2026. Até então o portão de
volume ficava de fora porque o G5 não alcançava os mercados do FOMC (chave
ausente no parquet e 1 mercado de 76 — `PEDIDO_Paulo_G5_fomc.md`), e sem
portão o `score_estabilidade` saía junto: pela Decisão 6b o portão é
pré-condição dele, já que o midpoint congela e o mercado sem negociação
aparece como perfeitamente estável. O Paulo entregou `conditionId` no parquet
e as 76 faixas × 18 reuniões no G5, então a rodada de dois ingredientes que
gerou a 6f está superada por esta.

Esta rodada é **confirmatória** por decisão registrada na 6m, tomada e
commitada ANTES de qualquer número sair: se concordar com a 6g, confirma a
régua em duas views com portão; se discordar, a régua não muda — ela foi
fechada por parcimônia, e trocar a forma ao ver a segunda view seria escolher
depois do dado (trava da 6d).

Ponto de método: cada evento (reunião) é uma série própria e as variações
NUNCA cruzam a fronteira entre eventos — os 18 mercados se sobrepõem no
tempo, e um `.diff()` sobre o painel empilhado compararia PMFs de reuniões
diferentes. Calcula-se por evento e empilha-se depois.

O alvo é o mesmo para todas as candidatas (variação total h slots à frente),
para que os `spearman` sejam comparáveis entre si; a robustez com alvo em
`|ΔE|` é reportada ao lado, e a leitura só muda se a ordenação mudar.

Uso:

    python lia/rodar_calibracao.py --dados <dir com data/ e src/>
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from lia.calibracao_omega import (
    agregar_volume_slot,
    comparar_candidatas,
    portao_volume,
    preparar_pmf,
    score_coerencia,
    score_estabilidade_pmf,
    score_proximidade,
    variacao_total,
    variacao_valor_esperado,
)

# Grades em teste. Nenhuma tem default no código: a escolha sai deste
# script, não de valor escrito à mão em módulo de lógica.
JANELAS_SLOTS = (5, 10, 20)
HORIZONTES_SLOTS = (2, 5)
HORIZONTES_PROXIMIDADE_DIAS = (5, 15)
QUANTIS_THRESHOLD = (0.0, 0.10, 0.25, 0.50)
AGREGACOES_VOLUME = ("soma", "minimo")
N_FAIXAS = 3

VIEW = "2.3"


def carregar_eventos(raiz):
    """Lê a PMF do FOMC pelo loader do pipeline (módulo do Felipe/Paulo)."""
    sys.path.insert(0, str(Path(raiz) / "src"))
    from poly_loader import daily_preopen, load_fomc_pmf  # noqa: E402

    caminho = Path(raiz) / "data" / "polymarket_fed_reunioes.parquet"
    return load_fomc_pmf(caminho), daily_preopen


def carregar_volume(raiz):
    """G5 da view 2.3, indexado por (evento, slot) nas duas agregações.

    A chave é o `conditionId`, que o Paulo pôs no parquet em 10/08 — a
    junção por título do mercado dava 0 em comum, que era o bloqueio do
    `PEDIDO_Paulo_G5_fomc.md`. O mapa `conditionId → evento_id` sai do
    próprio parquet, então o volume é atribuído à reunião pela mesma fonte
    que define os eventos, sem parse de nome de arquivo.

    `evento_id` é string no parquet e inteiro na saída do `load_fomc_pmf`;
    a conversão explícita evita um índice que não casa em silêncio.
    """
    caminho = Path(raiz) / "data" / "raw" / "g5_volume_no_tempo.csv"
    parquet = pd.read_parquet(Path(raiz) / "data" / "polymarket_fed_reunioes.parquet")
    mapa = parquet.drop_duplicates("conditionId").set_index("conditionId")
    mapa = mapa.evento_id.astype(int)

    g5 = pd.read_csv(caminho, parse_dates=["slot_utc"])
    g5 = g5[g5.view.astype(str) == VIEW].copy()
    g5["evento"] = g5.conditionId.map(mapa)
    if g5.evento.isna().any():
        raise ValueError("G5 da 2.3 tem conditionId fora do parquet")
    g5["slot_utc"] = g5.slot_utc.dt.tz_localize("UTC")
    return agregar_volume_slot(g5)


def montar_painel(eventos, daily_preopen, grade, volume=None):
    """Empilha, por evento, as séries de que a calibração precisa.

    `grade` : "12h" (série crua, passo nativo) ou "24h" (só o slot
              pré-abertura, que é o que a view enxerga). É a dimensão de
              grade temporal registrada na Decisão 6e.
    `volume`: saída de `carregar_volume`, ou None para a rodada sem portão
              (é o que o `rodar_robustez` usa, onde o portão não entra).

    Devolve um DataFrame com MultiIndex (evento, data) e as colunas
    `var_total`, `var_esperado`, `soma_cru`, `linha_completa`,
    `dias_ate_evento` — mais `vol_soma` e `vol_minimo` quando há volume.
    """
    linhas = []
    eventos_com_volume = (
        set() if volume is None else set(volume.index.get_level_values(0))
    )
    for evento_id, (probs, valores, _abertos, reuniao) in eventos.items():
        crua = probs if grade == "12h" else daily_preopen(probs)
        if len(crua) < max(JANELAS_SLOTS) + max(HORIZONTES_SLOTS) + 1:
            continue  # série curta demais para janela + horizonte
        pronta = preparar_pmf(crua)
        painel = pd.DataFrame(
            {
                "var_total": variacao_total(pronta),
                "var_esperado": variacao_valor_esperado(pronta, valores),
                "soma_cru": crua.sum(axis=1, skipna=True),
                "linha_completa": crua.notna().all(axis=1).astype(float),
            }
        )
        if volume is not None:
            vol = volume.loc[evento_id] if evento_id in eventos_com_volume else None
            for coluna in AGREGACOES_VOLUME:
                if vol is None:
                    painel[f"vol_{coluna}"] = np.nan
                elif grade == "12h":
                    painel[f"vol_{coluna}"] = vol[coluna].reindex(probs.index).to_numpy()
                else:
                    diario = daily_preopen(vol[coluna])
                    painel[f"vol_{coluna}"] = diario.reindex(painel.index).to_numpy()
        dias = (reuniao - painel.index.tz_localize(None).normalize()).days
        painel["dias_ate_evento"] = np.clip(dias, 0, None)
        painel["evento"] = evento_id
        linhas.append(painel.set_index("evento", append=True).swaplevel())
    return pd.concat(linhas).sort_index()


def alvo_futuro(painel, coluna, horizonte):
    """Erro realizado: a variação observada `horizonte` slots à frente.

    Deslocado DENTRO de cada evento — `groupby` impede que o fim de uma
    reunião empreste futuro do começo da seguinte.
    """
    return painel.groupby(level="evento")[coluna].shift(-horizonte)


def montar_candidatas(painel, grade):
    """As candidatas em teste nesta rodada, com o nome que vai ao relatório."""
    candidatas = {}
    for coluna, forma in (("var_total", "vt"), ("var_esperado", "ve")):
        for janela in JANELAS_SLOTS:
            score = painel.groupby(level="evento", group_keys=False)[coluna].apply(
                lambda s, j=janela: score_estabilidade_pmf(s, janela=j)
            )
            candidatas[f"estabilidade_{forma}_j{janela}_{grade}"] = score
    candidatas[f"coerencia_{grade}"] = score_coerencia(
        painel.soma_cru, painel.linha_completa
    )
    datas = painel.index.get_level_values("data")
    for horizonte in HORIZONTES_PROXIMIDADE_DIAS:
        for forma in ("linear", "exponencial"):
            dias = painel.dias_ate_evento.to_numpy()
            if forma == "linear":
                valores = np.minimum(dias, horizonte) / horizonte
            else:
                valores = 1.0 - np.exp(-dias / horizonte)
            candidatas[f"proximidade_{forma}_h{horizonte}_{grade}"] = pd.Series(
                valores, index=painel.index
            )
    # o portão entra como candidato próprio: antes de ser pré-condição, ele
    # passa pelo mesmo teste que os outros (foi assim que reprovou como score
    # na 2.2 e mesmo assim ficou como veto, pela semântica da 6b)
    for agregacao in AGREGACOES_VOLUME:
        if f"vol_{agregacao}" not in painel:
            continue
        serie = painel[f"vol_{agregacao}"]
        for quantil in QUANTIS_THRESHOLD:
            threshold = serie[serie > 0].quantile(quantil)
            if not np.isfinite(threshold) or threshold <= 0:
                continue
            candidatas[f"portao_{agregacao}_q{int(quantil * 100)}_{grade}"] = (
                portao_volume(serie, threshold)
            )
    return candidatas, datas


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dados", required=True, help="dir com data/ e src/")
    args = ap.parse_args()

    eventos, daily_preopen = carregar_eventos(args.dados)
    volume = carregar_volume(args.dados)
    print(f"eventos lidos: {len(eventos)} · "
          f"slots com volume no G5: {len(volume)}")

    # Os dois diagnósticos são os mesmos da rodada do CPI, importados em vez
    # de reescritos: são a mesma conta sobre outro painel, e duas
    # implementações da mesma quantidade é a classe de problema já fechada.
    from lia.rodar_calibracao_cpi import (  # noqa: E402
        diagnosticar_vies_midpoint,
        testar_estabilidade_condicional,
    )

    for grade in ("12h", "24h"):
        painel = montar_painel(eventos, daily_preopen, grade, volume)
        completas = int(painel.linha_completa.sum())
        com_volume = int(painel.vol_soma.notna().sum())
        print(f"\n{'=' * 72}\nGRADE {grade} — {len(painel)} slots, "
              f"{completas} linhas completas, {com_volume} com volume, "
              f"{painel.index.get_level_values('evento').nunique()} eventos")

        diagnosticar_vies_midpoint(painel, grade)
        testar_estabilidade_condicional(painel, grade)

        candidatas, _ = montar_candidatas(painel, grade)
        for horizonte in HORIZONTES_SLOTS:
            for coluna, rotulo in (("var_total", "variacao total"),
                                   ("var_esperado", "|dE| (robustez)")):
                erro = alvo_futuro(painel, coluna, horizonte)
                tabela = comparar_candidatas(candidatas, erro, N_FAIXAS)
                print(f"\n-- alvo: {rotulo} em h={horizonte} slots "
                      f"(n={int(tabela.n_observacoes.max())}) --")
                print(tabela.to_string(float_format=lambda v: f"{v: .4f}"))


if __name__ == "__main__":
    main()
