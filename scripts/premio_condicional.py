"""Prêmio de anúncio condicionado à incerteza do evento (tática 1.3). Felipe.

`premissa_taticas.py` mediu o prêmio de anúncio INCONDICIONAL e não o achou
(FOMC +0,062% contra +0,060% dos demais dias). Mas a âncora teórica
(Savor & Wilson) diz que o prêmio é **compensação por carregar risco de
evento** — logo ele só deveria existir quando o evento é de fato incerto.
Anúncio cujo resultado o mercado já dá como certo não tem risco a compensar.

Este script mede a versão condicional: separa os anúncios pelo quanto a PMF
do próprio Polymarket estava **dispersa** na véspera e compara o retorno do
SPY entre os dois grupos.

Medida de incerteza = **entropia normalizada** da PMF (0 = toda a massa num
balde só; 1 = todos os baldes iguais). Escolhida de propósito por não
depender de nenhuma decisão em aberto: não usa o valor numérico dos baldes
(decisão 1.2, balde aberto) e é invariante à renormalização (decisão 6.1),
além de ser comparável entre grades de tamanhos diferentes (o CPI varia de
3 a 9 baldes).

Sem lookahead: a PMF do dia D é o slot das 12:00 UTC de D (07:00/08:00 em
Nova York), anterior tanto ao CPI (8:30 ET) quanto ao FOMC (14:00 ET).

MEDE — não liga nem desliga tática nem escolhe orçamento.

Uso:
    python scripts/premio_condicional.py --dados <dir raw> --precos <parquet>
"""

import argparse
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from market_loader import load_etf_prices  # noqa: E402
from poly_loader import (daily_preopen, load_cpi_releases,  # noqa: E402
                         load_payroll_releases, load_pmf)
from taticas_common import close_to_close_returns  # noqa: E402

ATIVO = "SPY"  # a tática 1.3 é long SPY vs caixa
PREFIXO_FOMC = "M3_fed_trajectory_"  # PMF do nº de cortes em 2025


def entropia_normalizada(linha):
    """Incerteza da PMF em [0, 1] — 0 = concentrada, 1 = uniforme.

    Renormaliza pela soma observada (a PMF do poly não soma 1) e ignora
    baldes sem leitura. Menos de 2 baldes vivos -> NaN, nunca número
    inventado.
    """
    p = pd.Series(linha).dropna()
    p = p[p > 0]
    if len(p) < 2 or p.sum() <= 0:
        return float("nan")
    p = p / p.sum()
    return float(-(p * np.log(p)).sum() / np.log(len(p)))


def eventos_com_incerteza(pmf, datas_evento):
    """(data -> entropia) nos dias de anúncio em que a PMF tem leitura."""
    diario = daily_preopen(pmf)
    incerteza = diario.apply(entropia_normalizada, axis=1)
    datas = pd.DatetimeIndex(datas_evento).intersection(incerteza.index)
    return incerteza.loc[datas].dropna()


def estatistica(x):
    """(n, média, mediana, t) de uma amostra de retornos.

    A mediana entra porque a amostra é pequena por construção (a PMF do poly
    só existe de 2025 em diante): um único pregão extremo — 2025-04-10, no
    meio do choque tarifário — move a média de um grupo inteiro.
    """
    x = pd.Series(x).dropna()
    if len(x) < 2:
        return len(x), float("nan"), float("nan"), float("nan")
    media, desvio = float(x.mean()), float(x.std(ddof=1))
    return len(x), media, float(x.median()), media / (desvio / np.sqrt(len(x)))


def diferenca_de_medias(a, b):
    """t de Welch para a diferença entre dois grupos independentes."""
    a, b = pd.Series(a).dropna(), pd.Series(b).dropna()
    if len(a) < 2 or len(b) < 2:
        return float("nan"), float("nan")
    var = a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)
    return float(a.mean() - b.mean()), float((a.mean() - b.mean()) / np.sqrt(var))


def prefixos_cpi(releases, diretorio):
    """(data de divulgação -> prefixo dos arquivos) do mercado de cada mês.

    O slug do mercado vem da própria coluna `fonte` do calendário do Paulo
    ("Polymarket rules (june-inflation-monthly)"), então o casamento
    mês -> mercado não é adivinhado por nome de arquivo.
    """
    pares = {}
    for _, linha in releases.iterrows():
        fonte = str(linha["fonte"])
        if "(" not in fonte:
            continue
        slug = fonte[fonte.index("(") + 1: fonte.rindex(")")]
        prefixo = f"CPI_{slug}_"
        if list(Path(diretorio).glob(f"{prefixo}*.json")):
            pares[pd.Timestamp(linha["release_date"])] = prefixo
    return pares


# Famílias US de payrolls (G9b). O sufixo numérico é o desambiguador de mês
# repetido do Polymarket; exigir que ele seja SÓ dígitos é o que corta os
# mercados estrangeiros que a busca por "unemployment rate" traz junto
# (`january-unemployment-rate-mexico`, `...-japan`, `nov-jan-...-brazil/uk`,
# `indian-...`) sem precisar de lista de países.
_MESES = ("january|february|march|april|may|june|july|august|september|october|"
          "november|december")
PAYROLL_FAMILIAS = (
    ("nfp_jobs_added", re.compile(rf"^how-many-jobs-added-in-(?:{_MESES})(?:-\d+)?$")),
    ("unemployment_rate", re.compile(rf"^(?:{_MESES})-unemployment-rate(?:-\d+)?$")),
)
PREFIXO_PAYROLL = "G9_payrolls_"


def mercados_de_payroll(diretorio, releases):
    """(data de divulgação -> (prefixo, família)) dos mercados US de payrolls.

    **O casamento é pela DATA EM QUE A SÉRIE TERMINA**, não pelo nome do mês do
    slug. Três motivos, todos medidos no dado do G9b:

    1. O slug não distingue ano (`how-many-jobs-added-in-december` é dez/2024;
       `...-december-853` é dez/2025) — o Paulo sinalizou isso no G9b.
    2. O shutdown de 2025 desalinha mês do slug e data de release.
    3. Em TODOS os mercados resolvidos da varredura a série termina exatamente
       no dia do release. É um padrão forte o bastante para ser a chave — e,
       de quebra, é o próprio critério que a tática exige: se a série não
       alcança o dia do anúncio, não há PMF pré-abertura e o evento não serve.

    Mercado que morre antes do release simplesmente não casa e fica de fora —
    é o caso de set/2025 (série até 2025-11-07, release em 2025-11-20).

    Um release rende UM evento, nunca dois: `nfp_jobs_added` é a primária (é o
    número manchete, análogo ao CPI) e `unemployment_rate` só entra quando não
    há mercado de jobs no mês. As duas famílias saem do MESMO Employment
    Situation — contá-las em separado duplicaria o mesmo pregão.
    """
    datas = set(pd.DatetimeIndex(releases["release_date"]))
    achados = {}
    vistos = set()
    for arquivo in sorted(Path(diretorio).glob(f"{PREFIXO_PAYROLL}*.json")):
        mercado = arquivo.stem[len(PREFIXO_PAYROLL):].rsplit("_", 1)[0]
        if mercado in vistos:
            continue
        vistos.add(mercado)
        familia = next((nome for nome, padrao in PAYROLL_FAMILIAS
                        if padrao.match(mercado)), None)
        if familia is None:
            continue  # binário, meta de shutdown ou mercado estrangeiro
        prefixo = f"{PREFIXO_PAYROLL}{mercado}_"
        fim = daily_preopen(load_pmf(diretorio, prefixo, ordenar=False)).index.max()
        if fim not in datas:
            continue  # não alcança o dia do release -> não serve para a tática
        # jobs_added ganha da taxa de desemprego quando as duas existem no mês
        if fim not in achados or familia == "nfp_jobs_added":
            achados[fim] = (prefixo, familia)
    return dict(sorted(achados.items()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dados", default="data/raw/clob_exploracao")
    parser.add_argument("--precos", default="data/etf_prices_daily.parquet")
    parser.add_argument("--fomc", default="data/raw/fomc_dates.csv")
    parser.add_argument("--cpi", default="data/raw/cpi_release_dates.csv")
    parser.add_argument("--payrolls", default="data/raw/payrolls_release_dates.csv")
    parser.add_argument("--saida", default="Dump/analises/Premio_condicional.md")
    args = parser.parse_args()

    fechamento = load_etf_prices(args.precos)
    retorno = close_to_close_returns(fechamento)[ATIVO]

    fomc = pd.to_datetime(pd.read_csv(args.fomc)["date"])
    incerteza_fomc = eventos_com_incerteza(
        load_pmf(args.dados, PREFIXO_FOMC), fomc)

    releases = load_cpi_releases(args.cpi)
    partes = []
    for data, prefixo in prefixos_cpi(releases, args.dados).items():
        serie = eventos_com_incerteza(load_pmf(args.dados, prefixo), [data])
        partes.append(serie)
    incerteza_cpi = pd.concat(partes).sort_index() if partes else pd.Series(dtype=float)

    # Payrolls (G9): mesma medição, mais eventos. Não é view nova nem mercado
    # novo no modelo — é linha a mais na tática que já existe (D10/5.2).
    payrolls = mercados_de_payroll(args.dados, load_payroll_releases(args.payrolls))
    partes = [eventos_com_incerteza(load_pmf(args.dados, prefixo, ordenar=False), [data])
              for data, (prefixo, _) in payrolls.items()]
    incerteza_payroll = (pd.concat(partes).sort_index() if partes
                         else pd.Series(dtype=float))

    saida = []
    escrever = saida.append
    escrever("# Prêmio de anúncio condicionado à incerteza (tática 1.3)\n")
    escrever("> Gerado por `scripts/premio_condicional.py`. **Mede; não decide.** "
             "Incerteza = entropia normalizada da PMF do Polymarket no slot "
             "pré-abertura do dia do anúncio (não usa valor de balde nem "
             "renormalização — independe das decisões 1.2 e 6.1).\n")

    grupos = {"FOMC (PMF de cortes 2025)": incerteza_fomc,
              "CPI (PMF do mês)": incerteza_cpi,
              "Payrolls (PMF do Employment Situation)": incerteza_payroll}
    todos_altos, todos_baixos = [], []
    faixas = {}
    for nome, incerteza in grupos.items():
        escrever(f"\n## {nome}\n")
        if len(incerteza) < 4:
            escrever(f"*Só {len(incerteza)} anúncios com PMF disponível — "
                     "amostra insuficiente para separar em dois grupos.*")
            continue
        r = retorno.reindex(incerteza.index).dropna()
        incerteza = incerteza.reindex(r.index)
        corte = incerteza.median()
        faixas[nome] = (incerteza.min(), incerteza.max())
        altos, baixos = r[incerteza > corte], r[incerteza <= corte]
        todos_altos.append(altos)
        todos_baixos.append(baixos)
        escrever(f"- anúncios com PMF na véspera: **{len(r)}** "
                 f"({incerteza.index.min().date()} a {incerteza.index.max().date()})")
        escrever(f"- entropia: mín {incerteza.min():.2f} · mediana {corte:.2f} "
                 f"· máx {incerteza.max():.2f}\n")
        escrever("| grupo | n | retorno médio do SPY | mediana | t |")
        escrever("|---|---|---|---|---|")
        for rotulo, amostra in (("evento INCERTO (entropia alta)", altos),
                                ("evento previsível (entropia baixa)", baixos)):
            n, media, mediana, t = estatistica(amostra)
            escrever(f"| {rotulo} | {n} | {media * 100:+.3f}% | "
                     f"{mediana * 100:+.3f}% | {t:+.2f} |")
        dif, t_dif = diferenca_de_medias(altos, baixos)
        escrever(f"\n- diferença (incerto − previsível): **{dif * 100:+.3f}%** "
                 f"(t de Welch {t_dif:+.2f}) · nas medianas: "
                 f"{(altos.median() - baixos.median()) * 100:+.3f}%")

    if todos_altos:
        escrever("\n## As famílias de anúncio juntas\n")
        altos, baixos = pd.concat(todos_altos), pd.concat(todos_baixos)
        eventos = altos.index.union(baixos.index)
        escrever("| grupo | n | retorno médio do SPY | mediana | t |")
        escrever("|---|---|---|---|---|")
        for rotulo, amostra in (("evento INCERTO", altos),
                                ("evento previsível", baixos)):
            n, media, mediana, t = estatistica(amostra)
            escrever(f"| {rotulo} | {n} | {media * 100:+.3f}% | "
                     f"{mediana * 100:+.3f}% | {t:+.2f} |")
        dif, t_dif = diferenca_de_medias(altos, baixos)
        escrever(f"\n- diferença (incerto − previsível): **{dif * 100:+.3f}%** "
                 f"(t de Welch {t_dif:+.2f}) · nas medianas: "
                 f"{(altos.median() - baixos.median()) * 100:+.3f}%")
        # Referência na MESMA janela dos eventos — comparar com a média de 22
        # anos misturaria regimes; o que interessa é o dia sem anúncio vizinho.
        janela = retorno.loc[eventos.min():eventos.max()]
        n_base, media_base, mediana_base, _ = estatistica(janela.drop(eventos, errors="ignore"))
        escrever(f"- referência: dias SEM anúncio entre {eventos.min().date()} e "
                 f"{eventos.max().date()} — {n_base} pregões, média "
                 f"{media_base * 100:+.3f}%, mediana {mediana_base * 100:+.3f}%")
        sem_extremo = altos.drop(altos.abs().idxmax())
        escrever(f"- robustez: tirando o pregão mais extremo do grupo incerto "
                 f"({altos.abs().idxmax().date()}), a média dele vai de "
                 f"{altos.mean() * 100:+.3f}% para {sem_extremo.mean() * 100:+.3f}%")
        # Simétrico, e obrigatório desde que os payrolls entraram: o grupo
        # PREVISÍVEL passou a carregar 2025-04-04 (−5,9%, choque tarifário).
        # Tirar o extremo de um lado só faria a checagem trabalhar a favor da
        # tese. A pergunta certa é se a diferença sobrevive aos dois cortes.
        b_sem = baixos.drop(baixos.abs().idxmax())
        dif_r, t_r = diferenca_de_medias(sem_extremo, b_sem)
        escrever(f"- robustez (simétrica): tirando o extremo dos DOIS grupos "
                 f"({altos.abs().idxmax().date()} e {baixos.abs().idxmax().date()}, "
                 f"este último {baixos.abs().max() * 100:.1f}% em módulo), a "
                 f"diferença vai de {dif * 100:+.3f}% para **{dif_r * 100:+.3f}%** "
                 f"e o t de Welch de {t_dif:+.2f} para **{t_r:+.2f}**")

    escrever("\n## Limite de leitura\n")
    if faixas:
        # O corte é a MEDIANA DE CADA FAMÍLIA, então cada split é interno e
        # comparável. Mas a faixa absoluta de entropia difere muito entre
        # famílias, e isso muda como se lê o rótulo "previsível".
        escrever("**A entropia não vive na mesma faixa em toda família** — o corte "
                 "é a mediana DE CADA UMA, então cada split é interno, mas o "
                 "rótulo não é comparável entre elas:\n")
        for nome, (lo, hi) in faixas.items():
            escrever(f"- {nome}: entropia de **{lo:.2f} a {hi:.2f}**")
        escrever("\nOnde a faixa inteira é alta, o grupo \"previsível\" é apenas o "
                 "*menos incerto* da família — não um anúncio que o mercado dava "
                 "como resolvido. A leitura de Savor-Wilson (prêmio = compensação "
                 "por risco de evento) se aplica ao CONTRASTE dentro da família, "
                 "não ao nível absoluto.\n")
    escrever("A PMF do Polymarket só existe de 2025 em diante, então a versão "
             "condicional tem **muito menos eventos** que a incondicional "
             "(que usava o calendário de FOMC desde 2022). Diferença sem "
             "significância aqui não é evidência de ausência — é amostra "
             "curta. O que a medição entrega é a ORDEM DE GRANDEZA e o sinal.\n")

    Path(args.saida).write_text("\n".join(saida) + "\n", encoding="utf-8")
    sys.stdout.write(f"escrito: {args.saida} ({len(saida)} linhas)\n")


if __name__ == "__main__":
    main()
