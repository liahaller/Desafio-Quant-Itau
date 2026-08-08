"""Camada tática RECONSTRUÍDA — as duas sleeves de drift, sem orçamento.

Mede o que a decisão 12c cobrava. A 12c desligou a camada porque o tamanho não
tinha âncora: o Δ era monótono no orçamento, a grade não tinha ótimo interior, e
escolher a linha de cima era calibrar contra o resultado. As sleeves deste
arquivo **não têm orçamento** — o tamanho sai de `inv(δΣ)·μ`, o mesmo passo que
dimensiona uma view, com δ observável (D7) e μ estimado por event-study
expansivo (`tatica_drift_anuncio`).

Por isso **não há grade aqui**: cada linha é uma CONFIGURAÇÃO (quais sleeves
ligadas), não um ponto de varredura. Não existe parâmetro para escolher olhando
a coluna de excesso — que era exatamente a armadilha da 12c.

**Mede; não decide.** A entrada da camada continua sendo decisão do grupo, sob o
regime das seções 9/10.

Uso:

    python scripts/tatica_reconstruida.py --raiz .
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from backtest import run_backtest, summary  # noqa: E402
from backtest_v1 import DRIFT_LIVRO_CPI, DRIFT_LIVRO_FOMC, carregar  # noqa: E402
from config import ASSETS, CUSTO_BPS_POR_LADO, DELTA, DRIFT_JANELA_ACOES, TAU  # noqa: E402
from market_inputs import sample_covariance  # noqa: E402
from tatica_drift_anuncio import estimate_drift_mu  # noqa: E402

CONFIGS = {
    "desligada (v1, 12c)": (),
    "só drift FOMC (poly)": ("fomc",),
    "só drift CPI": ("cpi",),
    "as duas sleeves": ("fomc", "cpi"),
}


def rodada(retornos, montador, datas, w_mkt, sleeves, teto, custo_bps):
    """Um backtest com as sleeves dadas, no escopo de teto do v1 (no tilt)."""
    montador.tatica = tuple(sleeves)
    resultado = run_backtest(retornos, montador, w_mkt, datas=datas, tau=TAU,
                             delta=DELTA, custo_bps=custo_bps,
                             teto_alavancagem=teto, teto_no_tilt=True)
    montador.reset()
    s = summary(resultado, benchmark=retornos["SPY"])
    diags = [d for dia in resultado.diagnostics.values() for d in dia["taticas"]]
    dias = sum(1 for dia in resultado.diagnostics.values() if dia["taticas"])
    soma_abs = [d["soma_abs_dw"] for d in diags if "soma_abs_dw" in d]
    # P&L da sleeve SOZINHA, no dw pedido (antes do teto): separa "perde
    # dinheiro" de "rouba o teto das views". Soma das contribuições diárias, a
    # mesma convenção do `r_tilt` do `summary`.
    pnl = sum(float(d["dw"] @ retornos.loc[data].to_numpy(dtype=float))
              for data, dia in resultado.diagnostics.items()
              for d in dia["taticas"] if "dw" in d)
    return s, dias, (float(np.median(soma_abs)) if soma_abs else float("nan")), pnl


def eventos_e_mu(montador, datas):
    """μ FINAL de cada sleeve (todos os eventos fechados) — sanity check.

    Serve só para o relatório dizer PARA QUE LADO o dado mandou cada livro, e se
    isso bate com a literatura. O backtest nunca usa este μ: lá ele é reestimado
    a cada dia com o que já fechou.
    """
    fim = datas[-1] + pd.Timedelta(days=1)
    saida = {}
    brutas_fomc = {r: montador._surpresa_fomc_poly(r)
                   for r in montador.fomc[montador.fomc < fim]}
    brutas_fomc = {k: v for k, v in brutas_fomc.items() if v is not None}
    brutas_cpi = montador.surpresas_cpi[montador.surpresas_cpi.index < fim].to_dict()
    sigma = sample_covariance(montador.retornos)
    for nome, brutas, livro in (("fomc", brutas_fomc, DRIFT_LIVRO_FOMC),
                                ("cpi", brutas_cpi, DRIFT_LIVRO_CPI)):
        eventos = [(d, np.sign(s)) for d, s in brutas.items() if s != 0.0]
        mu, n = estimate_drift_mu(montador.retornos, eventos, DRIFT_JANELA_ACOES,
                                  livro, fim, sigma, TAU)
        saida[nome] = (mu, n, len(eventos), livro, list(brutas.values()))
    return saida


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raiz", default=".")
    parser.add_argument("--teto", type=float, default=1.0)
    parser.add_argument("--custo-bps", type=float, default=CUSTO_BPS_POR_LADO)
    parser.add_argument("--saida", default="Dump/analises/Tatica_reconstruida.md")
    args = parser.parse_args()

    retornos, montador, datas, w_mkt = carregar(args.raiz)
    excesso = "excesso acumulado (líquido − benchmark)"

    linhas = []
    base = None
    for nome, sleeves in CONFIGS.items():
        s, dias, soma_abs, pnl = rodada(retornos, montador, datas, w_mkt, sleeves,
                                        args.teto, args.custo_bps)
        base = base if base is not None else s[excesso]
        linhas.append({
            "configuração": nome,
            "dias com sleeve": dias,
            "excesso": s[excesso],
            "Δ vs. desligada": s[excesso] - base,
            "sharpe": s["sharpe anualizado (excesso zero)"],
            "giro diário": s["giro diário médio"],
            "Σ|dw| mediano da sleeve": soma_abs,
            "P&L da sleeve sozinha": pnl,
        })
    tabela = pd.DataFrame(linhas)
    mus = eventos_e_mu(montador, datas)

    texto = [
        "# Camada tática reconstruída — duas sleeves de drift, sem orçamento\n",
        "> Gerado por `scripts/tatica_reconstruida.py`. **Mede; não decide** — a "
        "entrada da camada é decisão do grupo. Sem grade de orçamento **de "
        "propósito**: o tamanho sai de `inv(δΣ)·μ`, então não existe parâmetro "
        "para escolher olhando a coluna de excesso (era a armadilha da 12c).\n",
        f"- janela: **{datas[0].date()} a {datas[-1].date()}** ({len(datas)} pregões)",
        f"- teto **no tilt = {args.teto:g}**, custo **{args.custo_bps:.1f} bps/lado**, "
        f"δ = {DELTA:g} (D7, observável), janela do drift = {DRIFT_JANELA_ACOES} "
        "dias úteis (Neuhierl-Weber)\n",
        "| configuração | dias com sleeve | excesso | Δ vs. desligada | sharpe | "
        "giro diário | Σ\\|dw\\| mediano | P&L da sleeve sozinha |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for _, l in tabela.iterrows():
        soma = ("—" if not np.isfinite(l["Σ|dw| mediano da sleeve"])
                else f"{l['Σ|dw| mediano da sleeve']:.2f}")
        pnl = "—" if not l["dias com sleeve"] else f"{l['P&L da sleeve sozinha'] * 100:+.2f} pp"
        texto.append(
            f"| {l['configuração']} | {l['dias com sleeve']:.0f} | "
            f"{l['excesso'] * 100:+.2f} pp | {l['Δ vs. desligada'] * 100:+.2f} pp | "
            f"{l['sharpe']:.2f} | {l['giro diário']:.3f} | {soma} | {pnl} |")

    texto.append("\n## A surpresa que as sleeves condicionam\n")
    texto.append(
        "Distribuição do sinal que dá a DIREÇÃO do tilt. É aqui que a sleeve do "
        "FOMC morre, e o motivo não é de modelagem.\n")
    texto.append("| sleeve | eventos | mediana \\|surpresa\\| | máx \\|surpresa\\| | "
                 "positivas | negativas |")
    texto.append("|---|---|---|---|---|---|")
    for nome, (_, _, _, _, surpresas) in mus.items():
        v = np.array(surpresas, dtype=float)
        texto.append(f"| {nome} | {len(v)} | {np.median(np.abs(v)):.2f} bps | "
                     f"{np.max(np.abs(v)):.2f} bps | {(v > 0).sum()} | {(v < 0).sum()} |")

    texto.append("\n## O μ que dimensiona cada sleeve\n")
    texto.append(
        "Retorno diário médio da janela do drift, por unidade de direção da "
        "surpresa, estimado com TODOS os eventos fechados da amostra. É o "
        "sanity check de sinal: o backtest reestima este μ a cada dia, só com o "
        "que já fechou.\n")
    texto.append("| sleeve | eventos com surpresa | eventos no μ | livro | μ (bps/dia) |")
    texto.append("|---|---|---|---|---|")
    for nome, (mu, n_mu, n_ev, livro, _) in mus.items():
        valores = ("—" if mu is None else " · ".join(
            f"{a} {mu[list(ASSETS).index(a)] * 1e4:+.2f}" for a in livro))
        texto.append(f"| {nome} | {n_ev} | {n_mu} | {' + '.join(livro)} | {valores} |")

    pior = tabela.iloc[1:]["P&L da sleeve sozinha"].min()
    texto.append("\n## Leitura\n")
    texto.append(
        "**As duas sleeves perdem dinheiro por conta própria, e não é o teto.** A "
        "coluna `P&L da sleeve sozinha` soma `dw · r` no dw PEDIDO, antes de "
        "qualquer corte — se ela é negativa, a sleeve não está sendo espremida "
        "pelo teto, está errando. Ela é negativa nas duas "
        f"(pior: {pior * 100:+.2f} pp).\n")
    texto.append(
        "**Mecanismo da sleeve do FOMC, e ele é uma descoberta sobre o dado, não "
        "sobre o modelo:** o Polymarket ACERTA a decisão do Fed quase na mosca. A "
        "surpresa é a decisão realizada menos o `E_poly` da véspera, e a tabela "
        "acima mostra que ela vive na casa de 1 bp — ordem de grandeza do ruído "
        "de discretização da própria PMF. Uma sleeve que toma direção pelo SINAL "
        "desse resíduo está condicionando em ruído, e nenhum ajuste de tamanho "
        "conserta isso. É o oposto do problema da 12c: lá faltava âncora para o "
        "tamanho, aqui falta sinal para a direção.\n")
    texto.append(
        "**Mecanismo da sleeve do CPI:** a surpresa (Δ breakeven no dia) é "
        "balanceada em sinal, mas o μ estimado diz que depois de surpresa "
        "inflacionária o TLT (nominal) anda MAIS que o TIP (indexado) — contrário "
        "à premissa que justifica o livro. Mesma classe de inversão da view "
        "transversal (15f) e da B em proxy (15g).\n")
    texto.append(
        "**O que isto NÃO diz:** que a camada tática é inviável. Diz que estas "
        "duas sleeves, com este dado, não pagam o espaço que ocupam. A âncora de "
        "tamanho sem parâmetro (`inv(δΣ)·μ` com encolhimento pela dispersão) "
        "sobrevive ao teste e fica disponível para qualquer sleeve futura — foi "
        "ela que permitiu medir sem calibrar nada contra o resultado.\n")

    Path(args.saida).write_text("\n".join(texto) + "\n", encoding="utf-8")
    sys.stdout.write(tabela.to_string(index=False) + f"\n\nescrito: {args.saida}\n")


if __name__ == "__main__":
    main()
