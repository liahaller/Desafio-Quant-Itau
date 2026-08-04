"""Substituto do ZQ para a surpresa de juros do FOMC (decisão 6.2). Felipe.

A view 2.3 (Bernanke-Kuttner) precisa de duas coisas do mercado de juros:

  (1) SURPRESA realizada em cada dia de FOMC, para estimar o β de cada ativo
      (`view_2_3_fed.estimate_betas`);
  (2) EXPECTATIVA de Δtaxa da próxima reunião (`e_ff_bps`), que é o benchmark
      contra o qual o E_poly é comparado.

O ZQ (fed funds future do mês) atenderia as duas, mas o Paulo mediu que o
yfinance não entrega contrato mensal — e as fontes que entregam são pagas
(decisão 6.2). Este script testa o substituto que **já está na mão**: a
variação diária do T-bill de 3 meses (`DTB3`, FRED, entregue no G2) no dia
do anúncio, no lugar da variação do fed funds future.

O teste é de SINAL, não de ajuste: se o proxy presta, os β estimados com ele
têm de sair com os sinais que a literatura documenta — alta de juros derruba
ação (β < 0), derruba mais o que é sensível a duration (XLU, XLK, TLT) e
menos o financeiro (XLF, que se beneficia de juro alto).

Sem lookahead na estimação: o H.15 publica a taxa de D depois do fechamento
de D, então ΔDTB3(D) só é conhecida no fim do dia — o que é exatamente o
event-study de Kuttner (surpresa e retorno medidos no mesmo pregão), e NÃO
serve como sinal negociável no próprio dia.

MEDE — não escolhe fonte.

Uso:
    python scripts/surpresa_fomc.py --precos <parquet> --dtb3 <csv> --fomc <csv>
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from market_loader import load_etf_prices, load_fred  # noqa: E402
from taticas_common import close_to_close_returns  # noqa: E402
from view_2_3_fed import estimate_betas  # noqa: E402

# Sinal esperado do β contra surpresa de ALTA de juros (bps positivos).
# Fonte: Bernanke & Kuttner (2005) — é sanity check, não calibração.
SINAL_ESPERADO = {"SPY": "-", "XLK": "-", "XLU": "-", "TLT": "-", "TIP": "-",
                  "XLP": "-", "XLV": "-", "XLE": "?", "XLF": "?"}


def surpresas_em_fomc(dtb3, datas_fomc):
    """ΔDTB3 em bps nos dias de FOMC com leitura no dia e no dia anterior."""
    variacao = dtb3.diff() * 100.0  # pontos percentuais -> bps
    datas = pd.DatetimeIndex(datas_fomc).intersection(variacao.index)
    return variacao.loc[datas].dropna()


def t_dos_betas(retornos, surpresas):
    """t de cada β do event-study (mesma matriz de desenho do estimate_betas)."""
    s = surpresas.to_numpy()
    R = retornos.to_numpy()
    X = np.column_stack([np.ones(len(s)), s])
    beta, *_ = np.linalg.lstsq(X, R, rcond=None)
    residuos = R - X @ beta
    sigma2 = (residuos ** 2).sum(axis=0) / (len(s) - 2)
    se = np.sqrt(np.linalg.inv(X.T @ X)[1, 1] * sigma2)
    return pd.Series(beta[1] / se, index=retornos.columns)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--precos", default="data/etf_prices_daily.parquet")
    parser.add_argument("--dtb3", default="data/raw/fred_DTB3.csv")
    parser.add_argument("--fomc", default="data/raw/fomc_dates.csv")
    parser.add_argument("--saida", default="Dump/analises/Surpresa_fomc_sem_ZQ.md")
    args = parser.parse_args()

    retornos = close_to_close_returns(load_etf_prices(args.precos))
    dtb3 = load_fred(args.dtb3)
    fomc = pd.to_datetime(pd.read_csv(args.fomc)["date"])

    surpresas = surpresas_em_fomc(dtb3, fomc)
    comum = retornos.index.intersection(surpresas.index)
    r, s = retornos.loc[comum], surpresas.loc[comum]

    betas = pd.Series(estimate_betas(r.to_numpy(), s.to_numpy()), index=r.columns)
    ts = t_dos_betas(r, s)

    saida = []
    escrever = saida.append
    escrever("# Surpresa de FOMC sem o ZQ — proxy pelo T-bill de 3 meses (6.2)\n")
    escrever("> Gerado por `scripts/surpresa_fomc.py`. **Mede; não escolhe fonte.** "
             "Surpresa = ΔDTB3 do dia do anúncio, em bps, no lugar da variação do "
             "fed funds future.\n")
    escrever(f"- reuniões de FOMC com ΔDTB3 disponível: **{len(s)}** "
             f"({s.index.min().date()} a {s.index.max().date()})")
    escrever(f"- surpresa: mediana {s.median():+.1f} bps · desvio {s.std():.1f} bps "
             f"· mín {s.min():+.1f} · máx {s.max():+.1f}")
    escrever(f"- reuniões com |surpresa| > 5 bps: "
             f"{int((s.abs() > 5).sum())} de {len(s)}\n")

    escrever("β do event-study (fração de retorno por bp de surpresa de ALTA):\n")
    escrever("| ativo | β | t | sinal esperado | bate? |")
    escrever("|---|---|---|---|---|")
    acertos = 0
    testaveis = 0
    for ativo in r.columns:
        esperado = SINAL_ESPERADO.get(ativo, "?")
        observado = "-" if betas[ativo] < 0 else "+"
        if esperado == "?":
            veredito = "—"
        else:
            testaveis += 1
            bate = esperado == observado
            acertos += bate
            veredito = "✅" if bate else "❌"
        escrever(f"| {ativo} | {betas[ativo]:+.6f} | {ts[ativo]:+.2f} | "
                 f"{esperado} | {veredito} |")
    escrever(f"\n- sinais coerentes com Bernanke-Kuttner: **{acertos} de {testaveis}** "
             f"(XLE e XLF não têm sinal previsto pela literatura)")
    escrever(f"- β com |t| > 2: **{int((ts.abs() > 2).sum())}** de {len(ts)}")
    escrever(f"- dispersão dos β em torno do SPY (é ela que dá conteúdo ao P): "
             f"{float((betas - betas['SPY']).abs().sum()):.6f}")

    escrever("\n## O que este teste NÃO resolve\n")
    escrever("O proxy serve para estimar β (surpresa realizada no dia). Ele **não** "
             "entrega o `e_ff_bps` — a expectativa de Δtaxa da PRÓXIMA reunião, que é "
             "o benchmark contra o qual o E_poly é comparado. Para isso falta a taxa "
             "efetiva corrente (`DFF` no FRED, mesmo formato dos três CSVs já "
             "entregues): o excesso do T-bill de 3 meses sobre a taxa efetiva é a "
             "expectativa embutida de mudança nos próximos ~3 meses.\n")

    Path(args.saida).write_text("\n".join(saida) + "\n", encoding="utf-8")
    sys.stdout.write(f"escrito: {args.saida} ({len(saida)} linhas)\n")


if __name__ == "__main__":
    main()
