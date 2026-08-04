"""O sinal de NÍVEL da view 3.1 tem conteúdo? (decisão D2b). Felipe.

Por que este teste existe. No D2 eu tirei a 3.1 junto com as views defasadas,
e a classificação estava errada: a 3.1 **não** aposta em defasagem. O sinal
dela é a DIVERGÊNCIA DE NÍVEL entre dois termômetros lidos no mesmo dia — a
probabilidade de recessão do Polymarket contra a probabilidade implícita na
curva de juros — que é a mesma família da 2.2, e a 2.2 sobreviveu.

O perfil de defasagem e a janela negociável mediram `Δp` (variação da
probabilidade) contra retorno. Isso testa a tese de defasagem, não a tese de
divergência. Este script mede o que faltou: **o nível da discordância prevê o
retorno dos dias seguintes?**

Contorno da trava de parâmetro: o probit de Estrella-Mishkin exige α e β
publicados, que ninguém buscou ainda. Como o probit é transformação monótona
do spread, testo a discordância em **z-score**: `z(p_poly) − z(−spread)`.
Se a discordância padronizada não prevê nada, nenhuma calibração de probit
salva a view; se prever, a calibração vira refinamento, não pré-requisito.

Sem lookahead: p do dia D é o slot das 12:00 UTC (pré-abertura), o spread é a
última leitura ANTERIOR a D (o H.15 publica D depois do fechamento de D), a
entrada é na ABERTURA de D e o retorno vai até o fechamento de D+N−1.

Ressalva declarada: os z-scores usam média e desvio da amostra inteira (in
sample) — serve para dizer se HÁ sinal, não para medir o retorno realizável.
Janelas sobrepostas para N > 1: o |t| é otimista.

MEDE — não decide a entrada da view.

Uso:
    python scripts/nivel_divergencia_3_1.py --dados <dir raw> --precos <parquet> \
        --abertura <parquet> --dgs10 <csv> --dtb3 <csv>
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
from poly_loader import daily_preopen, series_by_slot  # noqa: E402
from poly_preprocessing import binary_prob_series  # noqa: E402
from view_3_1_recessao import curve_spread  # noqa: E402

HORIZONTES = (1, 5, 10, 21)
PADRAO_SIM = "M4_recession_us-recession-in-2025_1*.json"
PADRAO_NAO = "M4_recession_*_NO.json"


def z(serie):
    """Padroniza (in sample — declarado no cabeçalho)."""
    return (serie - serie.mean()) / serie.std()


def spread_defasado(dgs10, dtb3, datas):
    """Spread da última leitura ESTRITAMENTE anterior a cada data (regra de
    lookahead já fechada na view 3.1)."""
    spread = curve_spread(dgs10, dtb3)
    return pd.Series(
        [spread[spread.index < d].iloc[-1] if (spread.index < d).any() else np.nan
         for d in datas], index=datas)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dados", default="data/raw/clob_exploracao")
    parser.add_argument("--precos", default="data/etf_prices_daily.parquet")
    parser.add_argument("--abertura", default="data/etf_open_daily.parquet")
    parser.add_argument("--dgs10", default="data/raw/fred_DGS10.csv")
    parser.add_argument("--dtb3", default="data/raw/fred_DTB3.csv")
    parser.add_argument("--saida", default="Dump/analises/Nivel_divergencia_3_1.md")
    args = parser.parse_args()

    fechamento = load_etf_prices(args.precos)
    abertura = load_etf_prices(args.abertura).reindex(
        fechamento.index)[fechamento.columns]

    sim = daily_preopen(series_by_slot(next(Path(args.dados).glob(PADRAO_SIM))))
    nao = daily_preopen(series_by_slot(next(Path(args.dados).glob(PADRAO_NAO))))
    par = pd.concat([sim.rename("sim"), nao.rename("nao")], axis=1).dropna()
    p_poly = pd.Series(binary_prob_series(par["sim"].to_numpy(), par["nao"].to_numpy()),
                       index=par.index)

    pregoes = p_poly.index.intersection(fechamento.index)
    p_poly = p_poly.loc[pregoes]
    spread = spread_defasado(load_fred(args.dgs10), load_fred(args.dtb3), pregoes)
    # Curva invertida (spread baixo) = mais risco de recessão -> inverte o sinal
    # para os dois termômetros apontarem para o mesmo lado.
    divergencia = (z(p_poly) - z(-spread)).dropna()

    saida = []
    escrever = saida.append
    escrever("# View 3.1 — o sinal de NÍVEL prevê retorno? (D2b)\n")
    escrever("> Gerado por `scripts/nivel_divergencia_3_1.py`. **Mede; não decide.** "
             "Discordância padronizada entre a probabilidade de recessão do Polymarket "
             "e a curva de juros (`z(p_poly) − z(−spread)`), contra o retorno dos "
             "pregões seguintes, entrando na abertura.\n")
    escrever(f"- pregões com os dois termômetros: **{len(divergencia)}** "
             f"({divergencia.index.min().date()} a {divergencia.index.max().date()})")
    escrever(f"- discordância: mediana {divergencia.median():+.2f} desvios · "
             f"mín {divergencia.min():+.2f} · máx {divergencia.max():+.2f}")
    escrever(f"- correlação entre os dois termômetros (nível): "
             f"**{p_poly.corr(-spread):+.2f}**\n")

    escrever("Coeficiente do retorno futuro contra a discordância "
             "(**|t| > 2 em negrito**); a view prevê **negativo** para ativo "
             "cíclico — mais risco de recessão do que a curva reconhece:\n")
    escrever("| N pregões | " + " | ".join(fechamento.columns) + " |")
    escrever("|" + "---|" * (len(fechamento.columns) + 1))
    for N in HORIZONTES:
        futuro = fechamento.shift(-(N - 1)) / abertura - 1.0
        celulas = []
        for ativo in fechamento.columns:
            coef, t, _, n = ols_simples(futuro[ativo].reindex(divergencia.index),
                                        divergencia)
            texto = f"{coef * 100:+.2f}%"
            celulas.append(f"**{texto}**" if abs(t) > 2 else texto)
        escrever(f"| {N} | " + " | ".join(celulas) + " |")
    escrever(f"\n- (coeficiente = retorno por 1 desvio de discordância; n ≈ {n})")

    escrever("\nMesma conta no par que a view realmente monta — **defensivo menos "
             "cíclico** (XLP+XLU contra XLK+XLF), que é onde o P da 3.1 concentra "
             "peso. A view prevê coeficiente **positivo** aqui:\n")
    escrever("| N pregões | coeficiente | t | n |")
    escrever("|---|---|---|---|")
    for N in HORIZONTES:
        futuro = fechamento.shift(-(N - 1)) / abertura - 1.0
        par_def = ((futuro["XLP"] + futuro["XLU"]) / 2
                   - (futuro["XLK"] + futuro["XLF"]) / 2)
        coef, t, _, n = ols_simples(par_def.reindex(divergencia.index), divergencia)
        marca = "**" if abs(t) > 2 else ""
        escrever(f"| {N} | {marca}{coef * 100:+.2f}%{marca} | {t:+.2f} | {n} |")

    escrever("\n> Janelas sobrepostas para N > 1 e z-score in sample: o |t| é "
             "otimista e o coeficiente não é retorno realizável. O que a tabela "
             "responde é **se existe sinal**, não quanto ele rende.\n")

    Path(args.saida).write_text("\n".join(saida) + "\n", encoding="utf-8")
    sys.stdout.write(f"escrito: {args.saida} ({len(saida)} linhas)\n")


if __name__ == "__main__":
    main()
