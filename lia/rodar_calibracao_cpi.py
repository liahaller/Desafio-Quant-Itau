"""Calibração do Ω na view 2.2 (CPI) — a primeira rodada COM portão de volume.

Complementa `rodar_calibracao.py`, que rodou sobre o FOMC com dois
ingredientes. Ali o portão ficou de fora porque o G5 não alcança os mercados
do Fed (1 mercado de 76, sem chave comum — `PEDIDO_Paulo_G5_fomc.md`); na
2.2 o G5 cobre os 111 mercados e casa por nome exato com os arquivos de
preço, então os quatro ingredientes rodam juntos pela primeira vez.

O que esta rodada decide, além de repetir o teste dos ingredientes:

**Se o `score_estabilidade` é sinal ou artefato.** Pela Decisão 6b, a série
de `/prices-history` é midpoint amostrado, não último trade: mercado sem
negociação continua reportando o mesmo número e aparece como perfeitamente
estável. O −0,40 medido no FOMC pode ser esse viés — o mercado ilíquido
entra como "estável" e com erro futuro baixo, pelo mesmo midpoint congelado.
O teste é condicional: mede-se a estabilidade **só nos slots que passam pelo
portão**. Se o spearman sobrevive, o ingrediente é real; se some, era o
artefato.

Duas dimensões novas na grade, ambas resolvidas pelo dado (protocolo de
08/07), não por escolha aqui:

- **agregação do volume entre buckets** — a view lê a PMF inteira, mas o G5
  dá volume por bucket. `soma` mede a atividade econômica do evento;
  `minimo` é conservador (um bucket parado congela aquela faixa da PMF).
- **threshold do portão** — em quantis da própria distribuição, nunca em
  valor absoluto cravado: o que é "pouco volume" é propriedade do mercado,
  não número escolhido.

Ponto de método herdado da rodada do FOMC: cada evento (mês de referência do
CPI) é uma série própria, e nem as variações nem o alvo cruzam a fronteira
entre eventos.

Uso:

    python lia/rodar_calibracao_cpi.py --dados <dir com data/ e src/>
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from lia.calibracao_omega import (
    comparar_candidatas,
    portao_volume,
    preparar_pmf,
    score_coerencia,
    score_estabilidade_pmf,
    variacao_total,
    variacao_valor_esperado,
)

# Grades em teste. Nenhuma tem default no código: a escolha sai desta rodada,
# não de valor escrito à mão em módulo de lógica.
JANELAS_SLOTS = (5, 10, 20)
HORIZONTES_SLOTS = (2, 5)
HORIZONTES_PROXIMIDADE_DIAS = (5, 15)
# Quantis DA DISTRIBUIÇÃO POSITIVA. O 0.0 é o menor notional positivo
# observado, então `portao_volume` com ele veta exatamente os slots de volume
# zero — é a regra semântica já registrada em 07/08 (pré-primeiro-trade veta),
# sem threshold calibrado. Entra na grade para poder ser comparada com as
# versões que têm parâmetro livre.
QUANTIS_THRESHOLD = (0.0, 0.10, 0.25, 0.50)
AGREGACOES_VOLUME = ("soma", "minimo")
N_FAIXAS = 3

VIEW = "2.2"


def carregar_eventos_cpi(raiz):
    """Lê a PMF de cada mês de CPI pelo loader do pipeline (módulo do Paulo).

    Um evento por mercado-mês. O nome do arquivo é
    `<evento>_will-<slug do bucket>_<tokenId>.json`, então o prefixo do evento
    sai por recorte em `_will-` — o mesmo recorte que liga o G5 (que identifica
    por `mercado` = nome completo) à série de preço.

    Devolve `{evento: (pmf_crua, valores, data_release)}`. `data_release` é NaT
    quando o mês não está no calendário do Paulo — não se inventa data; o
    ingrediente de proximidade simplesmente não pontua ali.
    """
    sys.path.insert(0, str(Path(raiz) / "src"))
    from poly_loader import bucket_value, load_cpi_releases, load_pmf  # noqa: E402

    diretorio = Path(raiz) / "data" / "raw" / "clob_exploracao"
    releases = load_cpi_releases(Path(raiz) / "data" / "raw" / "cpi_release_dates.csv")
    # a `fonte` do calendário traz o slug do mercado entre parênteses
    slug_release = {
        fonte.split("(")[-1].rstrip(")"): data
        for fonte, data in zip(releases.fonte, releases.release_date)
    }

    prefixos = sorted({
        arquivo.name.split("_will-")[0]
        for arquivo in diretorio.glob("*.json")
        if "_will-" in arquivo.name and "inflation" in arquivo.name
    })

    eventos = {}
    for prefixo in prefixos:
        pmf = load_pmf(diretorio, f"{prefixo}_")
        valores = [bucket_value(coluna) for coluna in pmf.columns]
        # o slug do calendário é o fim do prefixo (o começo é rótulo do Paulo)
        data = next(
            (d for slug, d in slug_release.items() if prefixo.endswith(slug)),
            pd.NaT,
        )
        eventos[prefixo] = (pmf, valores, data)
    return eventos


def carregar_volume(raiz):
    """G5 da view 2.2, indexado por (evento, slot) nas duas agregações.

    `soma` e `minimo` entre os buckets do evento. Bucket sem linha no slot
    entra como ausente, não como zero: `min` de um subconjunto de buckets
    ainda é o pior bucket observado, e inventar zero para faixa não reportada
    inverteria o portão no mercado que tem mais faixas.
    """
    caminho = Path(raiz) / "data" / "raw" / "g5_volume_no_tempo.csv"
    g5 = pd.read_csv(caminho, parse_dates=["slot_utc"])
    g5 = g5[g5.view == VIEW].copy()
    g5["evento"] = g5.mercado.str.split("_will-").str[0]
    g5["slot_utc"] = g5.slot_utc.dt.tz_localize("UTC")
    agrupado = g5.groupby(["evento", "slot_utc"]).notional_usd
    return pd.DataFrame({"soma": agrupado.sum(min_count=1), "minimo": agrupado.min()})


def montar_painel(eventos, volume, daily_preopen, grade):
    """Empilha, por evento, as séries de que a calibração precisa.

    `grade` : "12h" (série crua, passo nativo) ou "24h" (só o slot
              pré-abertura). Na 24h o volume é o do próprio slot das 12:00
              UTC, e não a soma do dia: é o volume contemporâneo à leitura que
              a view consome, que é o que o portão precisa qualificar.
    """
    linhas = []
    for evento, (crua_12h, valores, data_release) in eventos.items():
        crua = crua_12h if grade == "12h" else daily_preopen(crua_12h)
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
        vol = volume.loc[evento] if evento in volume.index.get_level_values(0) else None
        indice_12h = crua_12h.index if grade == "12h" else None
        for coluna in AGREGACOES_VOLUME:
            if vol is None:
                painel[f"vol_{coluna}"] = np.nan
            elif grade == "12h":
                painel[f"vol_{coluna}"] = vol[coluna].reindex(indice_12h).to_numpy()
            else:
                diario = daily_preopen(vol[coluna])
                painel[f"vol_{coluna}"] = diario.reindex(painel.index).to_numpy()

        datas = painel.index.tz_localize(None).normalize() if grade == "12h" else painel.index
        dias = (data_release - datas).days if pd.notna(data_release) else np.nan
        painel["dias_ate_evento"] = np.clip(dias, 0, None) if pd.notna(data_release) else np.nan
        painel["evento"] = evento
        linhas.append(painel.set_index("evento", append=True).swaplevel())
    return pd.concat(linhas).sort_index()


def alvo_futuro(painel, coluna, horizonte):
    """Erro realizado: a variação observada `horizonte` slots à frente.

    Deslocado DENTRO de cada evento — `groupby` impede que o fim de um mês
    empreste futuro do começo do seguinte.
    """
    return painel.groupby(level="evento")[coluna].shift(-horizonte)


def montar_candidatas(painel, grade):
    """As candidatas em teste nesta rodada, com o nome que vai ao relatório."""
    candidatas = {}
    for coluna, forma in (("var_total", "vt"), ("var_esperado", "ve")):
        for janela in JANELAS_SLOTS:
            candidatas[f"estabilidade_{forma}_j{janela}_{grade}"] = painel.groupby(
                level="evento", group_keys=False
            )[coluna].apply(lambda s, j=janela: score_estabilidade_pmf(s, janela=j))
    candidatas[f"coerencia_{grade}"] = score_coerencia(
        painel.soma_cru, painel.linha_completa
    )
    for horizonte in HORIZONTES_PROXIMIDADE_DIAS:
        dias = painel.dias_ate_evento.to_numpy()
        for forma in ("linear", "exponencial"):
            if forma == "linear":
                valores = np.minimum(dias, horizonte) / horizonte
            else:
                valores = 1.0 - np.exp(-dias / horizonte)
            candidatas[f"proximidade_{forma}_h{horizonte}_{grade}"] = pd.Series(
                valores, index=painel.index
            )
    # o portão entra como candidato próprio: antes de ser pré-condição, ele
    # precisa passar no mesmo teste que os outros
    for agregacao in AGREGACOES_VOLUME:
        serie = painel[f"vol_{agregacao}"]
        for quantil in QUANTIS_THRESHOLD:
            threshold = serie[serie > 0].quantile(quantil)
            if not np.isfinite(threshold) or threshold <= 0:
                continue
            candidatas[f"portao_{agregacao}_q{int(quantil * 100)}_{grade}"] = (
                portao_volume(serie, threshold)
            )
    return candidatas


def diagnosticar_vies_midpoint(painel, grade):
    """Mede o viés da 6b diretamente: mercado parado é parado por iliquidez?

    Compara, entre slots com e sem negociação, (i) a fração de pares com
    variação exatamente zero — a assinatura do midpoint congelado — e (ii) o
    erro realizado à frente. Se o slot sem volume for ao mesmo tempo mais
    "estável" e mais fácil de prever, o `score_estabilidade` está sendo
    confirmado pelo artefato, não pelo sinal.
    """
    print(f"\n-- diagnóstico do viés 6b (grade {grade}) --")
    for agregacao in AGREGACOES_VOLUME:
        vol = painel[f"vol_{agregacao}"]
        erro = alvo_futuro(painel, "var_total", HORIZONTES_SLOTS[0])
        dados = pd.DataFrame({"vol": vol, "var": painel.var_total, "erro": erro}).dropna()
        if dados.empty:
            continue
        sem = dados[dados.vol <= 0]
        com = dados[dados.vol > 0]
        print(f"   volume por {agregacao}: {len(sem)} slots sem negociação, "
              f"{len(com)} com")
        for rotulo, grupo in (("sem", sem), ("com", com)):
            if grupo.empty:
                continue
            print(f"     {rotulo}: variação zero em {(grupo['var'] == 0).mean():6.1%} "
                  f"dos pares · variação média {grupo['var'].mean():.5f} · "
                  f"erro futuro médio {grupo.erro.mean():.5f}")


def testar_estabilidade_condicional(painel, grade):
    """O teste central: a estabilidade sobrevive quando só o líquido entra?

    Roda a mesma candidata sobre o painel inteiro e sobre o subconjunto que
    passa pelo portão. A comparação é entre os dois spearman — se cair para
    perto de zero no subconjunto líquido, o ingrediente vivia do midpoint
    congelado (Decisão 6b).
    """
    print(f"\n-- estabilidade condicionada ao portão (grade {grade}) --")
    linhas = {}
    for agregacao in AGREGACOES_VOLUME:
        serie = painel[f"vol_{agregacao}"]
        for quantil in QUANTIS_THRESHOLD:
            threshold = serie[serie > 0].quantile(quantil)
            if not np.isfinite(threshold) or threshold <= 0:
                continue
            passa = portao_volume(serie, threshold).fillna(1.0) > 0
            for janela in JANELAS_SLOTS:
                score = painel.groupby(level="evento", group_keys=False)[
                    "var_total"
                ].apply(lambda s, j=janela: score_estabilidade_pmf(s, janela=j))
                for horizonte in HORIZONTES_SLOTS:
                    erro = alvo_futuro(painel, "var_total", horizonte)
                    nome = (f"vt_j{janela}_h{horizonte}_{agregacao}"
                            f"_q{int(quantil * 100)}")
                    tabela = comparar_candidatas(
                        {"todos": score, "líquido": score[passa]},
                        erro,
                        N_FAIXAS,
                    )
                    linhas[nome] = {
                        "spearman_todos": tabela.loc["todos", "spearman"],
                        "spearman_liquido": tabela.loc["líquido", "spearman"],
                        "n_todos": tabela.loc["todos", "n_observacoes"],
                        "n_liquido": tabela.loc["líquido", "n_observacoes"],
                    }
    resultado = pd.DataFrame.from_dict(linhas, orient="index")
    resultado["delta"] = resultado.spearman_liquido - resultado.spearman_todos
    print(resultado.to_string(float_format=lambda v: f"{v: .4f}"))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dados", required=True, help="dir com data/ e src/")
    args = ap.parse_args()

    eventos = carregar_eventos_cpi(args.dados)
    volume = carregar_volume(args.dados)
    print(f"eventos de CPI lidos: {len(eventos)} "
          f"({sum(pd.isna(d) for _, _, d in eventos.values())} sem data no calendário)")

    sys.path.insert(0, str(Path(args.dados) / "src"))
    from poly_loader import daily_preopen  # noqa: E402

    for grade in ("12h", "24h"):
        painel = montar_painel(eventos, volume, daily_preopen, grade)
        completas = int(painel.linha_completa.sum())
        com_volume = int(painel.vol_soma.notna().sum())
        print(f"\n{'=' * 72}\nGRADE {grade} — {len(painel)} slots, "
              f"{completas} linhas completas, {com_volume} com volume, "
              f"{painel.index.get_level_values('evento').nunique()} eventos")

        diagnosticar_vies_midpoint(painel, grade)
        testar_estabilidade_condicional(painel, grade)

        candidatas = montar_candidatas(painel, grade)
        for horizonte in HORIZONTES_SLOTS:
            for coluna, rotulo in (("var_total", "variacao total"),
                                   ("var_esperado", "|dE| (robustez)")):
                erro = alvo_futuro(painel, coluna, horizonte)
                tabela = comparar_candidatas(candidatas, erro, N_FAIXAS)
                print(f"\n-- alvo: {rotulo} em h={horizonte} slots --")
                print(tabela.to_string(float_format=lambda v: f"{v: .4f}"))


if __name__ == "__main__":
    main()
