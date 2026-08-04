"""Horizonte de convergência da view 2.2 (decisões 7.2 e 7.4). Felipe.

A view 2.2 diz que há um repricing a acontecer entre o que o Polymarket espera
de inflação e o que os títulos pagam — mas não diz EM QUANTOS DIAS. Com
H = 1 dia (decisão 1, fechada), o Q precisa ser retorno de UM dia, então o
repricing total tem de ser dividido por um número de dias.

Proposta a testar (7.2): o horizonte é o **calendário** — o repricing se
distribui até a divulgação do CPI, data em que o mercado do poly resolve e a
informação vira pública. Implicação testável: o retorno acumulado de TIP
contra TLT entre a data t e a divulgação R deve andar com a divergência
medida em t, e o coeficiente deve ser parecido em qualquer distância até R
(porque o gap total é o mesmo, só muda em quantos dias ele se realiza).

Proposta a testar (7.4): a divergência entra **demeanada** — inflação mensal
anualizada (~3,7%) e breakeven de 10 anos (~2,3%) são objetos diferentes, e a
diferença de nível é viés estrutural, não sinal. O script reporta a média da
divergência para mostrar o tamanho desse viés.

Ressalva de método, declarada: as janelas t→R se sobrepõem dentro de um mesmo
mês, então os t da regressão empilhada NÃO são independentes e o |t| dela é
otimista. Por isso o script também roda a versão de **um ponto por mês**
(12 episódios independentes), que é a leitura honesta do tamanho de amostra.

MEDE — não fecha o horizonte.

Uso:
    python scripts/convergencia_2_2.py --dados <dir raw> --precos <parquet> \
        --t10yie <csv> --cpi <csv>
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from janela_negociavel import ols_simples  # noqa: E402
from market_loader import load_etf_prices, load_fred  # noqa: E402
from poly_loader import daily_preopen, load_cpi_releases, load_pmf  # noqa: E402
from poly_preprocessing import (  # noqa: E402
    bucket_values_with_open, carry_missing, normalize_probs)

MESES_POR_ANO = 12


def e_poly_anual(diretorio, prefixo):
    """Série diária de inflação ANUALIZADA implícita na PMF do mês.

    Aplica as regras já fechadas: faixa faltante herda a última leitura
    (6.1), faixa aberta entra a meia largura para fora (1.2), e a
    anualização `(1+π)^12 − 1` é feita nos VALORES dos buckets, não na média
    (Jensen — mesma correção que a view 2.2 já faz).
    """
    pmf = daily_preopen(carry_missing(load_pmf(diretorio, prefixo))).dropna(how="all")
    valores_pct = bucket_values_with_open(
        [float(np.nan_to_num(v, nan=np.nan)) for v in _valores_das_colunas(pmf)])
    anualizados = (1.0 + valores_pct / 100.0) ** MESES_POR_ANO - 1.0
    linhas = pmf.fillna(0.0)
    linhas = linhas[linhas.sum(axis=1) > 0]
    return pd.Series(normalize_probs(linhas.to_numpy(), axis=1) @ anualizados,
                     index=linhas.index)


def _valores_das_colunas(pmf):
    """Valor numérico de cada bucket, na ordem das colunas do load_pmf."""
    from poly_loader import bucket_value
    return np.array([bucket_value(c) for c in pmf.columns], dtype=float)


def ols(y, x):
    """(coef, t, n) de y = a + b·x — reusa o OLS de `janela_negociavel`."""
    coef, t, _, n = ols_simples(y, x)
    return coef, t, n


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dados", default="data/raw/clob_exploracao")
    parser.add_argument("--precos", default="data/etf_prices_daily.parquet")
    parser.add_argument("--t10yie", default="data/raw/fred_T10YIE.csv")
    parser.add_argument("--cpi", default="data/raw/cpi_release_dates.csv")
    parser.add_argument("--saida", default="Dump/analises/Convergencia_2_2.md")
    args = parser.parse_args()

    precos = load_etf_prices(args.precos)
    # A view 2.2 aposta TIP contra TLT: o repricing de inflação aparece na
    # diferença entre o título indexado e o nominal, não no nível dos dois.
    tip_tlt = np.log(precos["TIP"]) - np.log(precos["TLT"])
    breakeven = load_fred(args.t10yie) / 100.0
    releases = load_cpi_releases(args.cpi)

    linhas = []
    por_mes = []
    for _, linha in releases.iterrows():
        fonte = str(linha["fonte"])
        if "(" not in fonte:
            continue
        prefixo = f"CPI_{fonte[fonte.index('(') + 1: fonte.rindex(')')]}_"
        if not list(Path(args.dados).glob(f"{prefixo}*.json")):
            continue
        R = pd.Timestamp(linha["release_date"])
        e = e_poly_anual(args.dados, prefixo)
        e = e[e.index <= R]
        if len(e) < 10 or R not in tip_tlt.index:
            continue
        div = (e - breakeven.reindex(e.index).ffill()).dropna()
        pregoes = tip_tlt.index
        for data, valor in div.items():
            if data not in pregoes:
                continue
            faltam = int(pregoes.slice_indexer(data, R).stop
                         - pregoes.slice_indexer(data, R).start) - 1
            if faltam <= 0:
                continue
            be = breakeven.reindex(pregoes).ffill()
            linhas.append({"mes": linha["mes_referencia"], "data": data,
                           "divergencia": float(valor), "faltam": faltam,
                           "retorno_ate_R": float(tip_tlt[R] - tip_tlt[data]),
                           "d_breakeven": float(be[R] - be[data])})
        if not div.empty:
            janela = tip_tlt.reindex(div.index).dropna()
            por_mes.append({"mes": linha["mes_referencia"], "slots": len(div),
                            "div_media": float(div.mean()),
                            "retorno_janela": float(janela.iloc[-1] - janela.iloc[0])
                            if len(janela) > 1 else float("nan")})

    df = pd.DataFrame(linhas)
    mensal = pd.DataFrame(por_mes)

    saida = []
    escrever = saida.append
    escrever("# Convergência da view 2.2 — horizonte do repricing (7.2 / 7.4)\n")
    escrever("> Gerado por `scripts/convergencia_2_2.py`. **Mede; não fecha o "
             "horizonte.** Divergência = inflação mensal anualizada implícita na "
             "PMF − breakeven de 10 anos. Repricing medido em `log(TIP) − log(TLT)`.\n")

    if df.empty:
        escrever("*Nenhum mês com PMF e data de divulgação casadas.*")
        Path(args.saida).write_text("\n".join(saida) + "\n", encoding="utf-8")
        return

    escrever(f"- meses utilizáveis: **{len(mensal)}** · observações diárias: {len(df)}")
    escrever(f"- **viés estrutural (7.4):** divergência média = "
             f"**{df['divergencia'].mean() * 100:+.2f} pp**, desvio "
             f"{df['divergencia'].std() * 100:.2f} pp — a média é o descasamento "
             f"1 mês × 10 anos, não sinal. É ela que a view precisa remover.\n")

    df["div_demeanada"] = df["divergencia"] - df["divergencia"].mean()
    coef, t, n = ols(df["retorno_ate_R"], df["div_demeanada"])
    escrever(f"**Regressão empilhada** (janelas sobrepostas — |t| otimista): "
             f"retorno TIP−TLT de t até a divulgação contra a divergência em t\n")
    escrever(f"- coeficiente **{coef:+.4f}** · t {t:+.2f} · n {n}\n")

    coef_be, t_be, n_be = ols(df["d_breakeven"], df["div_demeanada"])
    escrever("**Teste mais limpo — o próprio breakeven anda na direção do poly?** "
             "`log(TIP) − log(TLT)` mistura durations muito diferentes (TIP ~7 anos, "
             "TLT ~26), então o movimento do TLT abafa o sinal de inflação. Δbreakeven "
             "mede a convergência direto, sem esse ruído:\n")
    escrever(f"- Δ do breakeven de t até a divulgação contra a divergência em t: "
             f"coeficiente **{coef_be:+.5f}** · t {t_be:+.2f} · n {n_be}")
    escrever(f"- (a view prevê coeficiente **positivo**: poly mais inflacionista que "
             f"o título ⇒ o breakeven sobe até a divulgação)\n")

    escrever("**O coeficiente é estável ao longo da contagem regressiva?** "
             "(se o gap total é o mesmo, deve ser)\n")
    escrever("| dias até a divulgação | n | coef. Δbreakeven | t |")
    escrever("|---|---|---|---|")
    for rotulo, faixa in (("mais de 15", df["faltam"] > 15),
                          ("6 a 15", (df["faltam"] > 5) & (df["faltam"] <= 15)),
                          ("1 a 5", df["faltam"] <= 5)):
        sub = df[faixa]
        c, tt, nn = ols(sub["d_breakeven"], sub["div_demeanada"])
        escrever(f"| {rotulo} | {nn} | {c:+.5f} | {tt:+.2f} |")

    escrever("\n**Um ponto por mês** (episódios independentes — é a leitura "
             "honesta do tamanho de amostra):\n")
    escrever("| mês | slots | divergência média | retorno TIP−TLT na janela |")
    escrever("|---|---|---|---|")
    for _, m in mensal.iterrows():
        escrever(f"| {m['mes']} | {int(m['slots'])} | {m['div_media'] * 100:+.2f} pp "
                 f"| {m['retorno_janela'] * 100:+.2f}% |")
    if len(mensal) >= 4:
        c, tt, nn = ols(mensal["retorno_janela"],
                        mensal["div_media"] - mensal["div_media"].mean())
        escrever(f"\n- correlação entre os dois: coeficiente {c:+.4f} · t {tt:+.2f} "
                 f"· n {nn} episódios")

    Path(args.saida).write_text("\n".join(saida) + "\n", encoding="utf-8")
    sys.stdout.write(f"escrito: {args.saida} ({len(saida)} linhas)\n")


if __name__ == "__main__":
    main()
