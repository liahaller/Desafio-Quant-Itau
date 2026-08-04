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
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from market_loader import load_etf_prices  # noqa: E402
from poly_loader import daily_preopen, load_cpi_releases, load_pmf  # noqa: E402
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dados", default="data/raw/clob_exploracao")
    parser.add_argument("--precos", default="data/etf_prices_daily.parquet")
    parser.add_argument("--fomc", default="data/raw/fomc_dates.csv")
    parser.add_argument("--cpi", default="data/raw/cpi_release_dates.csv")
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

    saida = []
    escrever = saida.append
    escrever("# Prêmio de anúncio condicionado à incerteza (tática 1.3)\n")
    escrever("> Gerado por `scripts/premio_condicional.py`. **Mede; não decide.** "
             "Incerteza = entropia normalizada da PMF do Polymarket no slot "
             "pré-abertura do dia do anúncio (não usa valor de balde nem "
             "renormalização — independe das decisões 1.2 e 6.1).\n")

    grupos = {"FOMC (PMF de cortes 2025)": incerteza_fomc,
              "CPI (PMF do mês)": incerteza_cpi}
    todos_altos, todos_baixos = [], []
    for nome, incerteza in grupos.items():
        escrever(f"\n## {nome}\n")
        if len(incerteza) < 4:
            escrever(f"*Só {len(incerteza)} anúncios com PMF disponível — "
                     "amostra insuficiente para separar em dois grupos.*")
            continue
        r = retorno.reindex(incerteza.index).dropna()
        incerteza = incerteza.reindex(r.index)
        corte = incerteza.median()
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
        escrever("\n## Os dois tipos de anúncio juntos\n")
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

    escrever("\n## Limite de leitura\n")
    escrever("A PMF do Polymarket só existe de 2025 em diante, então a versão "
             "condicional tem **muito menos eventos** que a incondicional "
             "(que usava o calendário de FOMC desde 2022). Diferença sem "
             "significância aqui não é evidência de ausência — é amostra "
             "curta. O que a medição entrega é a ORDEM DE GRANDEZA e o sinal.\n")

    Path(args.saida).write_text("\n".join(saida) + "\n", encoding="utf-8")
    sys.stdout.write(f"escrito: {args.saida} ({len(saida)} linhas)\n")


if __name__ == "__main__":
    main()
