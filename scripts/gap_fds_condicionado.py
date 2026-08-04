"""Gap de fim de semana, versão condicionada (decisão D3b). Felipe.

A tática (c) entra na ABERTURA da reabertura (segunda ou pós-feriado) quando a
probabilidade do Polymarket andou enquanto a bolsa estava fechada, e captura o
pedaço `abertura → fechamento` desse dia. A medição incondicional de 04/08
mostrou continuação fraca e trocando de sinal por setor.

Este script aplica a ela o mesmo tratamento que salvou a tática de prêmio de
anúncios no D3: **condicionar**. A hipótese é que o dia de reabertura só paga
quando o fim de semana trouxe notícia de verdade — ou seja, quando |Δp| do
poly foi grande. Se a relação existir só no grupo de |Δp| alto, a tática vive
condicionada; se for igual nos dois grupos (ou ausente), não há o que salvar.

Alinhamento (regras já fechadas): p do dia = slot das 12:00 UTC (pré-abertura);
Δp de reabertura = p(D) − p(último pregão anterior), que carrega o fim de
semana inteiro; retorno = `fechamento(D)/abertura(D) − 1`, a única janela que
a tática consegue negociar.

MEDE — não liga a tática nem escolhe orçamento.

Uso:
    python scripts/gap_fds_condicionado.py --dados <dir raw> --precos <parquet> \
        --abertura <parquet>
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from janela_negociavel import ols_simples  # noqa: E402
from market_loader import load_etf_prices  # noqa: E402
from poly_loader import daily_preopen, series_by_slot  # noqa: E402
from premissa_taticas import dias_de_reabertura  # noqa: E402

MERCADOS = {
    "M4 recessão (2025)": "M4_recession_us-recession-in-2025_1*.json",
    "M9 Câmara (2026)": "M9_midterms_2022_will-the-democratic-party*.json",
}
# A tática é long/short de mercado amplo mais tilt setorial; SPY é o ativo em
# que a premissa foi escrita, XLP é o setor que mediu REVERSÃO na incondicional.
ATIVOS = ("SPY", "XLK", "XLF", "XLP")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dados", default="data/raw/clob_exploracao")
    parser.add_argument("--precos", default="data/etf_prices_daily.parquet")
    parser.add_argument("--abertura", default="data/etf_open_daily.parquet")
    parser.add_argument("--saida", default="Dump/analises/Gap_fds_condicionado.md")
    args = parser.parse_args()

    fechamento = load_etf_prices(args.precos)
    abertura = load_etf_prices(args.abertura).reindex(fechamento.index)
    intradiario = fechamento / abertura[fechamento.columns] - 1.0
    reaberturas = dias_de_reabertura(fechamento.index)

    saida = []
    escrever = saida.append
    escrever("# Gap de fim de semana condicionado ao tamanho do Δp (D3b)\n")
    escrever("> Gerado por `scripts/gap_fds_condicionado.py`. **Mede; não decide.** "
             "Só dias de reabertura (pregão cujo anterior ficou a ≥ 3 dias "
             "corridos). Retorno = abertura → fechamento do próprio dia, que é a "
             "única janela que a tática negocia.\n")
    escrever("A tática prevê **continuação**: coeficiente positivo, e maior no "
             "grupo de Δp grande.\n")

    for nome, padrao in MERCADOS.items():
        p = daily_preopen(series_by_slot(next(Path(args.dados).glob(padrao))))
        dp = p.reindex(fechamento.index).dropna().diff().dropna()
        dp = dp.reindex(reaberturas).dropna()
        if len(dp) < 12:
            escrever(f"\n## {nome}\n\n*Só {len(dp)} reaberturas — amostra "
                     "insuficiente para separar em dois grupos.*")
            continue
        corte = dp.abs().median()
        grande, pequeno = dp[dp.abs() > corte], dp[dp.abs() <= corte]
        escrever(f"\n## {nome}\n")
        escrever(f"- reaberturas com Δp: **{len(dp)}** "
                 f"({dp.index.min().date()} a {dp.index.max().date()})")
        escrever(f"- |Δp| mediano no fim de semana: **{corte:.4f}** "
                 f"({corte * 100:.2f} pontos de probabilidade)\n")
        escrever("| ativo | Δp GRANDE (n=%d) | Δp pequeno (n=%d) |"
                 % (len(grande), len(pequeno)))
        escrever("|---|---|---|")
        for ativo in ATIVOS:
            celulas = []
            for sub in (grande, pequeno):
                coef, t, _, n = ols_simples(intradiario[ativo].reindex(sub.index), sub)
                texto = f"{coef:+.4f} (t {t:+.2f})"
                celulas.append(f"**{texto}**" if abs(t) > 2 else texto)
            escrever(f"| {ativo} | " + " | ".join(celulas) + " |")

    escrever("\n> Amostra pequena por construção: só há uma reabertura por semana, "
             "e cada mercado do poly vive ~1 ano. Ausência de significância aqui "
             "não é prova de ausência de efeito — é falta de dado.\n")

    Path(args.saida).write_text("\n".join(saida) + "\n", encoding="utf-8")
    sys.stdout.write(f"escrito: {args.saida} ({len(saida)} linhas)\n")


if __name__ == "__main__":
    main()
