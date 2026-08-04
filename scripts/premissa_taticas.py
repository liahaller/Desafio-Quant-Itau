"""Premissa empírica das 3 táticas candidatas, medida no dado real. Felipe.

As três táticas já têm código pronto, mas nenhuma tinha sido confrontada com
o dado: faltava o `Open` diário, entregue no G1 do follow-up 2. Este script
MEDE a premissa de cada uma — não escolhe parâmetro, não liga nem desliga
tática (ENTRADA da camada é decisão de reunião, decisão 10).

O que dá para medir sem nenhum parâmetro humano:

  gap de fim de semana : a tática entra na ABERTURA de segunda, logo o salto
        do fim de semana (`close sexta → abertura segunda`) já passou. O que
        ela captura é o pedaço intradiário (`abertura → fechamento`). A
        premissa "a bolsa leva tempo para absorver" só vale se o intradiário
        de segunda CONTINUAR o salto — é isso que a correlação entre os dois
        mede. Correlação nula = o salto foi todo precificado na abertura.

  prêmio de anúncios   : Savor & Wilson (2013) — retorno médio do SPY em dia
        de anúncio agendado contra os demais dias. Aqui a tática é long SPY
        vs caixa, então o teste da âncora é direto.

  drift pós-FOMC       : o SINAL depende da surpresa (ZQ, sem fonte definida
        — o yfinance não serve, é decisão de grupo), então a direção NÃO é
        testável aqui. O que é testável é o TAMANHO da janela (dispersão do
        acumulado) e quantas vezes o FOMC seguinte trunca o livro de RF.

Uso:
    python scripts/premissa_taticas.py --precos <parquet close> \
        --abertura <parquet open> --fomc <csv> --saida <md>

Onde está o dado: os arquivos vivem no branch `Paulo`, não neste. Para rodar
sem fazer merge, extraia para um diretório temporário:

    git archive origin/Paulo data/ | tar -x -C <dir temporario>
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from market_loader import adjustment_gap, load_etf_prices  # noqa: E402
from poly_loader import load_cpi_releases  # noqa: E402
from taticas_common import close_to_close_returns, intraday_returns  # noqa: E402

# Fim de semana normal já são 3 dias corridos (sexta -> segunda); feriado
# prolongado entra na mesma conta, como manda a espec do gap de fim de semana.
GAP_MINIMO_DIAS = 3
# Janelas da literatura (Neuhierl-Weber / Brooks-Katz-Lustig). São os defaults
# DE ESPEC, pendentes de confirmação em reunião — aqui só dimensionam a medida.
JANELA_ACOES = 15
JANELA_RF = 50


def estatistica(x):
    """(n, média, desvio, t) de uma amostra de retornos."""
    x = pd.Series(x).dropna()
    n = len(x)
    if n < 2:
        return n, float("nan"), float("nan"), float("nan")
    media, desvio = float(x.mean()), float(x.std(ddof=1))
    return n, media, desvio, media / (desvio / np.sqrt(n))


def dias_de_reabertura(datas, gap_minimo=GAP_MINIMO_DIAS):
    """Pregões cujo pregão anterior ficou a >= `gap_minimo` dias corridos."""
    datas = pd.DatetimeIndex(datas)
    intervalo = datas.to_series().diff().dt.days
    return datas[intervalo >= gap_minimo]


def linha_tabela(rotulo, stat):
    n, media, desvio, t = stat
    return (f"| {rotulo} | {n} | {media * 100:+.3f}% | {desvio * 100:.3f}% | {t:+.2f} |")


def bloco_base_de_ajuste(abertura, fechamento, escrever):
    """Conferência que precede qualquer número de janela intradiária."""
    gap = adjustment_gap(abertura, fechamento)
    escrever("## ⚠️ Antes dos números: os dois parquets não estão na mesma base\n")
    escrever("Mediana de `abertura/fechamento − 1` por ticker. Se as duas séries "
             "estivessem no mesmo ajuste, isso seria ruído intradiário (± 0,1%):\n")
    escrever("| " + " | ".join(gap.index) + " |")
    escrever("|" + "---|" * len(gap))
    escrever("| " + " | ".join(f"{v * 100:+.3f}%" for v in gap) + " |")
    escrever(f"\n**TIP ({gap['TIP'] * 100:+.2f}%) e TLT ({gap['TLT'] * 100:+.2f}%) estão "
             "deslocados** — e são justamente os dois ETFs de pagamento MENSAL. O "
             "`etf_prices_daily.parquet` foi gerado em 2026-07-09 (`48cb12e`) e o "
             "`etf_open_daily.parquet` em 2026-08-02 (`7ea4e86`); um ex-dividendo entre "
             "os dois pulls faz o `auto_adjust=True` reescalar toda a história anterior "
             "de um só arquivo. O degrau é visível: a razão fica em −1,15% até "
             "~2026-06-01 e vai a ~0 depois.\n")
    escrever("Efeito: `abertura → fechamento` de TIP e TLT ganha **+1,15% e +0,40% "
             "fabricados por dia** na amostra antiga (com o espelho no overnight). "
             "As médias intradiárias desses dois tickers abaixo estão contaminadas; "
             "as **correlações não** (o deslocamento é constante e não muda "
             "covariância), e nada que use só fechamento é afetado. Conserto: "
             "re-baixar os dois arquivos no mesmo pull — módulo do Paulo.\n")


def bloco_gap_fds(abertura, fechamento, escrever):
    intra = intraday_returns(abertura, fechamento)
    salto = abertura / fechamento.shift(1) - 1.0  # close(D-1) -> abertura(D)
    reaberturas = dias_de_reabertura(fechamento.index)
    outros = fechamento.index.difference(reaberturas)

    escrever("## Gap de fim de semana — a tática entra DEPOIS do salto\n")
    escrever(f"{len(reaberturas)} reaberturas (pregão anterior a ≥ {GAP_MINIMO_DIAS} dias "
             f"corridos, o que inclui feriado prolongado) contra {len(outros)} demais "
             f"pregões, {fechamento.index[0].date()} → {fechamento.index[-1].date()}.\n")

    escrever("**O salto que a tática NÃO captura** (`close sexta → abertura segunda`) "
             "e o pedaço que ela captura (`abertura → fechamento de segunda`):\n")
    escrever("| ativo | salto médio | σ do salto | intradiário médio | σ intradiário | "
             "corr(salto, intradiário) | t da corr |")
    escrever("|---|---|---|---|---|---|---|")
    contaminados = {"TIP", "TLT"}  # base de ajuste diferente (bloco acima)
    for ativo in fechamento.columns:
        s = salto.loc[reaberturas, ativo].dropna()
        i = intra.loc[reaberturas, ativo].dropna()
        comum = s.index.intersection(i.index)
        s, i = s.loc[comum], i.loc[comum]
        rho = float(s.corr(i))
        t_rho = rho * np.sqrt((len(comum) - 2) / max(1 - rho ** 2, 1e-12))
        marca = " ⚠️" if ativo in contaminados else ""
        escrever(f"| {ativo}{marca} | {s.mean() * 100:+.3f}% | {s.std() * 100:.3f}% | "
                 f"{i.mean() * 100:+.3f}% | {i.std() * 100:.3f}% | {rho:+.3f} | {t_rho:+.2f} |")

    escrever("\nLeitura: **correlação positiva** = o mercado continua na direção do "
             "salto depois de abrir (a premissa da tática se sustenta); **≈ 0** = o "
             "salto do fim de semana já está inteiro no preço de abertura e a tática "
             "entra tarde; **negativa** = reversão, e o tilt na direção do Δp opera "
             "contra o dado.\n")

    escrever("Intradiário de reabertura contra os demais dias (é a janela exata da "
             "tática, `abertura → fechamento`):\n")
    escrever("| amostra | n | média | σ | t |")
    escrever("|---|---|---|---|---|")
    escrever(linha_tabela("SPY — dias de reabertura", estatistica(intra.loc[reaberturas, "SPY"])))
    escrever(linha_tabela("SPY — demais pregões", estatistica(intra.loc[outros, "SPY"])))


def bloco_premio_anuncios(fechamento, datas_fomc, datas_cpi, escrever):
    retornos = close_to_close_returns(fechamento)["SPY"]
    escrever("\n## Prêmio de anúncios (1.3) — âncora Savor & Wilson\n")
    escrever("Retorno do SPY de `fechamento(D−1) → fechamento(D)`, que é a janela "
             "declarada pela tática, em dia de anúncio agendado contra os demais.\n")
    escrever("| amostra | n | média | σ | t |")
    escrever("|---|---|---|---|---|")

    anuncios = {}
    for nome, datas in (("FOMC", datas_fomc), ("CPI", datas_cpi)):
        no_pregao = retornos.index.intersection(pd.DatetimeIndex(datas))
        anuncios[nome] = no_pregao
        if len(no_pregao):
            janela = retornos.loc[no_pregao.min():no_pregao.max()]
            escrever(linha_tabela(f"{nome} ({no_pregao.min().date()} → "
                                  f"{no_pregao.max().date()})", estatistica(retornos.loc[no_pregao])))
            fora = janela.index.difference(no_pregao)
            escrever(linha_tabela(f"demais pregões da mesma janela ({nome})",
                                  estatistica(janela.loc[fora])))
    todos = anuncios["FOMC"].union(anuncios["CPI"])
    if len(todos):
        escrever(linha_tabela("FOMC + CPI juntos", estatistica(retornos.loc[todos])))
    escrever("\nA tática é long SPY vs caixa **dimensionada pela entropia da PMF**; o "
             "que está medido aqui é só a âncora (o prêmio existe na amostra?), não o "
             "sinal — a modulação por entropia depende da decisão 11a (correção de "
             "favorite-longshot), que ainda falha alto de propósito.\n")


def bloco_drift_fomc(fechamento, datas_fomc, escrever):
    retornos = close_to_close_returns(fechamento)
    escrever("\n## Drift pós-FOMC — tamanho da janela (o sinal não é testável aqui)\n")
    escrever("A direção do tilt é `−sign(surpresa)`, e a surpresa vem do ZQ, que **não "
             "tem fonte definida** (o yfinance não serve — decisão de grupo pendente). "
             "Sem ela não dá para testar o drift; dá para medir o **tamanho** da janela "
             "que a tática ocuparia, que é o teto do que a sleeve pode render.\n")

    pregoes = retornos.index
    eventos = [d for d in pd.DatetimeIndex(datas_fomc) if d in pregoes]
    escrever(f"{len(eventos)} anúncios do FOMC caem em pregão, "
             f"{eventos[0].date()} → {eventos[-1].date()} "
             f"(o calendário entregue começa em {pd.DatetimeIndex(datas_fomc).min().date()}).\n")

    escrever("| livro | ativo | janela | n eventos | acumulado médio | σ do acumulado |")
    escrever("|---|---|---|---|---|---|")
    for livro, ativo, janela in (("ações", "SPY", JANELA_ACOES), ("RF", "TLT", JANELA_RF)):
        acumulados = []
        for d in eventos:
            pos = pregoes.get_loc(d)
            trecho = retornos[ativo].iloc[pos + 1:pos + 1 + janela]
            if len(trecho) == janela:
                acumulados.append(float((1 + trecho).prod() - 1))
        n, media, desvio, _ = estatistica(acumulados)
        escrever(f"| {livro} | {ativo} | dias úteis 1..{janela} | {n} | "
                 f"{media * 100:+.3f}% | {desvio * 100:.3f}% |")

    intervalos = pd.DatetimeIndex(sorted(datas_fomc)).to_series().diff().dt.days.dropna()
    uteis = np.busday_count(
        [d.date() for d in pd.DatetimeIndex(sorted(datas_fomc))[:-1]],
        [d.date() for d in pd.DatetimeIndex(sorted(datas_fomc))[1:]])
    escrever(f"\nTruncagem do livro de RF: o intervalo entre FOMCs é de **{uteis.min()} a "
             f"{uteis.max()} dias úteis** (mediana {int(np.median(uteis))}) — com a janela "
             f"de {JANELA_RF} dias da literatura, **{int((uteis < JANELA_RF).sum())} de "
             f"{len(uteis)}** intervalos truncam o livro antes do fim. A janela de "
             f"{JANELA_ACOES} dias do livro de ações nunca é truncada "
             f"(mínimo {uteis.min()} > {JANELA_ACOES}).\n")
    escrever(f"*(intervalo em dias corridos: {int(intervalos.min())} a "
             f"{int(intervalos.max())}.)*\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--precos", default="data/etf_prices_daily.parquet")
    parser.add_argument("--abertura", default="data/etf_open_daily.parquet")
    parser.add_argument("--fomc", default="data/raw/fomc_dates.csv")
    parser.add_argument("--cpi", default="data/raw/cpi_release_dates.csv")
    parser.add_argument("--saida", default="Dump/analises/Premissa_taticas.md")
    args = parser.parse_args()

    saida = []
    escrever = saida.append

    fechamento = load_etf_prices(args.precos)
    abertura = load_etf_prices(args.abertura)
    datas_fomc = pd.to_datetime(pd.read_csv(args.fomc)["date"])
    datas_cpi = load_cpi_releases(args.cpi)["release_date"]

    escrever("# Premissa empírica das 3 táticas candidatas\n")
    escrever("> Gerado por `scripts/premissa_taticas.py` sobre o dado do G1/G2 "
             "(follow-up 2). **Mede a premissa; não escolhe parâmetro nem liga tática** "
             "— a ENTRADA da camada segue pendente de reunião (decisão 10). Leia o "
             "bloco de base de ajuste antes das tabelas: ele diz quais números estão "
             "contaminados por um problema do dado, não pela tática.\n")

    bloco_base_de_ajuste(abertura, fechamento, escrever)
    bloco_gap_fds(abertura, fechamento, escrever)
    bloco_premio_anuncios(fechamento, datas_fomc, datas_cpi, escrever)
    bloco_drift_fomc(fechamento, datas_fomc, escrever)

    escrever("\n## Limites desta medição\n")
    escrever("- Nenhum orçamento (`lam`, `orcamento_max`, `orcamento_acoes/_rf`) entra "
             "na conta: como o `dw` é linear neles, o que está medido é o retorno **por "
             "unidade de orçamento**.\n")
    escrever("- O gap de fim de semana é medido em TODAS as reaberturas, não só nas que "
             "teriam sinal do poly — a tática só opera quando alguma view designada tem "
             "Δp de fim de semana, e essas views dependem do β (decisão 3.1) e da "
             "aprovação da reunião.\n")
    escrever(f"- O calendário de CPI entregue começa em 2025 (15 divulgações): o teste "
             f"do prêmio de CPI é de amostra curta por construção, e o G6 (datas de "
             f"2022–2024) só será levantado se a reunião mandar.\n")

    Path(args.saida).write_text("\n".join(saida) + "\n", encoding="utf-8")
    sys.stdout.write(f"escrito: {args.saida} ({len(saida)} linhas)\n")


if __name__ == "__main__":
    main()
