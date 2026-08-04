"""Quanto do lag 0 sobra na janela que dá para negociar (decisões 7.3/3.2). Felipe.

O perfil de defasagem (`perfil_defasagem_k.py`) mediu o retorno de FECHAMENTO
A FECHAMENTO e achou a associação toda no lag 0. Só que a versão contemporânea
da view entra na ABERTURA de D — o Δp do dia fecha às 12:00 UTC, antes do sino
— logo o pedaço `fechamento(D−1) → abertura(D)` acontece antes de a gente
conseguir comprar. Este script parte o retorno de D em dois e mede em qual dos
dois pedaços mora a associação com o Δp:

    r_gap(D) = abertura(D)/fechamento(D−1) − 1   <- NÃO negociável
    r_oc(D)  = fechamento(D)/abertura(D) − 1     <- é o que a view captura
    r_cc(D)  = fechamento(D)/fechamento(D−1) − 1 <- o que foi medido antes

Regressão univariada de cada pedaço contra o MESMO Δp(D) contemporâneo. Se o
coeficiente de `r_oc` for uma fração pequena do de `r_cc`, a view contemporânea
não tem o que capturar; se sobreviver, ela tem conteúdo negociável.

MEDE — não decide. A entrada das views 2.4/3.1 é decisão registrada.

Nota sobre a contaminação de base de ajuste (G7, `FOLLOWUP3`): o degrau entre
os dois parquets em TIP/TLT começa em ~2026-06-01 e as duas janelas medidas
aqui (eleição 2024, recessão 2025) terminam antes disso — dentro da amostra o
deslocamento é constante, e deslocamento constante não move covariância nem
coeficiente de regressão. Só a MÉDIA de r_oc desses dois seria afetada, e
média não entra nesta conta.

Uso:
    python scripts/janela_negociavel.py --dados <dir raw> --precos <parquet close> \
        --abertura <parquet open>
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from market_loader import load_etf_prices  # noqa: E402
from poly_loader import daily_preopen, series_by_slot  # noqa: E402

MERCADOS = {
    "2.4 eleitoral (Trump 2024)": "M5_trump_2024_*.json",
    # SEGUNDO episódio eleitoral, achado em 04/08 ao revisar o corte do D2: o
    # arquivo com prefixo `M9_midterms_2022_` que o Paulo puxou por engano e
    # deixou no diretório por transparência é, na verdade, o mercado da CÂMARA
    # 2026 — 355 dias, de jul/2025 a jul/2026. É a segunda eleição que a
    # decisão 6.4 dava como inexistente. Serve de teste FORA DA AMOSTRA do
    # sinal estimado em 2024: como o mercado é "democratas controlam a Câmara"
    # (e o de 2024 é "Trump vence"), o sinal partidário deve aparecer INVERTIDO.
    "2.4 eleitoral (Câmara 2026, fora da amostra)":
        "M9_midterms_2022_will-the-democratic-party*.json",
    "3.1 recessão (US 2025)": "M4_recession_*.json",
    # Segundo mercado da view C, também achado na revisão: soma 121 dias com o
    # de jun/2025, contra os 45 que a decisão usou.
    "C geopolítica (Irã 2026)": "M7_iran_strike_*.json",
}


def ols_simples(y, x):
    """(coef, t, corr) da regressão univariada y = a + b·x, sobre o par sem NaN."""
    par = pd.concat([y, x], axis=1).dropna()
    if len(par) < 10:
        return float("nan"), float("nan"), float("nan"), len(par)
    yv, xv = par.iloc[:, 0].to_numpy(), par.iloc[:, 1].to_numpy()
    X = np.column_stack([np.ones(len(xv)), xv])
    beta, *_ = np.linalg.lstsq(X, yv, rcond=None)
    residuos = yv - X @ beta
    sigma2 = (residuos ** 2).sum() / (len(xv) - 2)
    se = np.sqrt(sigma2 * np.linalg.inv(X.T @ X)[1, 1])
    return float(beta[1]), float(beta[1] / se), float(np.corrcoef(xv, yv)[0, 1]), len(par)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dados", default="data/raw/clob_exploracao")
    parser.add_argument("--precos", default="data/etf_prices_daily.parquet")
    parser.add_argument("--abertura", default="data/etf_open_daily.parquet")
    parser.add_argument("--saida", default="Dump/analises/Janela_negociavel.md")
    args = parser.parse_args()

    fechamento = load_etf_prices(args.precos)
    abertura = load_etf_prices(args.abertura)
    datas = fechamento.index.intersection(abertura.index)
    fechamento, abertura = fechamento.loc[datas], abertura.loc[datas, fechamento.columns]

    r_cc = fechamento.pct_change()
    r_gap = abertura / fechamento.shift(1) - 1
    r_oc = fechamento / abertura - 1
    janelas = {"gap (não negociável)": r_gap, "abertura→fech. (negociável)": r_oc,
               "fech.→fech. (medido antes)": r_cc}

    saida = []
    escrever = saida.append
    escrever("# Janela negociável do lag 0 — views contemporâneas (7.3 / 3.2)\n")
    escrever("> Gerado por `scripts/janela_negociavel.py`. **Mede; não decide.** "
             "Regressão univariada de cada pedaço do retorno de D contra o Δp "
             "contemporâneo (slot das 12:00 UTC de D, pré-abertura).\n")
    escrever("`coef` = retorno por unidade de Δp; **|t| > 2 em negrito**. "
             "A coluna que decide é a razão `coef_oc / coef_cc`: quanto do efeito "
             "medido sobrevive na janela em que a view consegue entrar.\n")

    for nome, padrao in MERCADOS.items():
        arquivo = next(Path(args.dados).glob(padrao))
        p = daily_preopen(series_by_slot(arquivo))
        dp = r_cc.join(p.rename("p"), how="inner")["p"].diff().dropna()
        escrever(f"\n## {nome}\n")
        escrever("| ativo | " + " | ".join(janelas) + " | razão oc/cc |")
        escrever("|" + "---|" * (len(janelas) + 2))
        razoes = {}
        for ativo in fechamento.columns:
            celulas, coefs = [], {}
            for rotulo, retornos in janelas.items():
                coef, t, corr, n = ols_simples(retornos[ativo], dp)
                coefs[rotulo] = coef
                texto = f"{coef:+.4f} (r {corr:+.2f})"
                celulas.append(f"**{texto}**" if abs(t) > 2 else texto)
            razao = (coefs["abertura→fech. (negociável)"]
                     / coefs["fech.→fech. (medido antes)"])
            razoes[ativo] = razao
            escrever(f"| {ativo} | " + " | ".join(celulas) + f" | {razao:+.0%} |")
        escrever(f"\n- observações: {n}")
        escrever(f"- razão oc/cc mediana entre os 9 ativos: "
                 f"**{np.median(list(razoes.values())):+.0%}**")

    Path(args.saida).write_text("\n".join(saida) + "\n", encoding="utf-8")
    sys.stdout.write(f"escrito: {args.saida} ({len(saida)} linhas)\n")


if __name__ == "__main__":
    main()
