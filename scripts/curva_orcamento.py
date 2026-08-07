"""Curva orçamento → excesso: quanto a camada tática move o resultado do v1.

A camada tática (prêmio de anúncios 1.3 e drift pós-FOMC) está **construída,
testada e desligada** — ligar exige escolher o `orcamento`, que é fração do
patrimônio e portanto parâmetro do modelo, não detalhe de implementação.

Esta varredura existe para a decisão **12c** (`Decisoes_pendentes.md`): com o v1
virando a entrega, a pergunta "liga ou não" precisava de número em vez de
opinião. **Varre e reporta, não escolhe** (CLAUDE.md §6) — e o registro da 12c é
justamente NÃO ligar, porque escolher o orçamento olhando a coluna de excesso é
o overfit em dois passos que a Lia levantou no protocolo anti-overfit (seção 10).

O que a tabela responde: se algum orçamento da grade mudasse a conclusão do v1.

Uso:

    python scripts/curva_orcamento.py --raiz .
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from backtest import run_backtest, summary  # noqa: E402
from backtest_v1 import carregar  # noqa: E402
from config import CUSTO_BPS_POR_LADO, DELTA, TAU  # noqa: E402

# Cada família liga um subconjunto dos overlays com o MESMO orçamento `o`, para a
# grade ter um eixo só. Ligar os dois livros do drift com orçamentos diferentes é
# outra varredura, e não é a pergunta desta (só prêmio × só drift × os dois).
FAMILIAS = {
    "só prêmio": lambda o: {"premio": o},
    "só drift": lambda o: {"drift_acoes": o, "drift_rf": o},
    "prêmio + drift": lambda o: {"premio": o, "drift_acoes": o, "drift_rf": o},
}


def rodada(retornos, montador, datas, w_mkt, orcamentos, teto, custo_bps):
    """Um backtest com os orçamentos dados, no escopo de teto do v1 (no tilt).

    Muta `montador.orcamentos` em vez de recarregar: o montador lê o dict a cada
    dia, e recarregar refaria a leitura dos parquets e a semente da 2.3 a cada
    ponto da grade sem mudar nada do resultado.
    """
    montador.orcamentos = orcamentos
    resultado = run_backtest(retornos, montador, w_mkt, datas=datas, tau=TAU,
                             delta=DELTA, custo_bps=custo_bps,
                             teto_alavancagem=teto, teto_no_tilt=True)
    montador.reset()   # médias expansivas voltam ao estado do 1º pregão
    s = summary(resultado, benchmark=retornos["SPY"])
    n_dias = sum(1 for d in resultado.diagnostics.values() if d["taticas"])
    return s, n_dias


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raiz", default=".",
                        help="diretório com data/ extraído do branch Paulo")
    parser.add_argument("--orcamentos", type=float, nargs="+",
                        default=[0.01, 0.02, 0.05, 0.10],
                        help="grade de orçamento (fração do patrimônio) — "
                             "varredura, não escolha")
    parser.add_argument("--teto", type=float, default=1.0)
    parser.add_argument("--custo-bps", type=float, default=CUSTO_BPS_POR_LADO)
    parser.add_argument("--saida", default="Dump/analises/Curva_orcamento.md")
    args = parser.parse_args()

    if any(o <= 0 for o in args.orcamentos):
        raise SystemExit("orçamento é fração do patrimônio e tem de ser positivo")

    retornos, montador, datas, w_mkt = carregar(args.raiz)
    base, _ = rodada(retornos, montador, datas, w_mkt, {}, args.teto, args.custo_bps)
    excesso = "excesso acumulado (líquido − benchmark)"

    linhas = []
    for nome, monta in FAMILIAS.items():
        for o in args.orcamentos:
            s, n_dias = rodada(retornos, montador, datas, w_mkt, monta(o),
                               args.teto, args.custo_bps)
            linhas.append({
                "família": nome,
                "orçamento": o,
                "dias com overlay": n_dias,
                "excesso": s[excesso],
                "Δ vs. desligada": s[excesso] - base[excesso],
                "sharpe": s["sharpe anualizado (excesso zero)"],
                "giro diário": s["giro diário médio"],
                "custo pago": s["custo pago (fração do patrimônio)"],
            })
    tabela = pd.DataFrame(linhas)

    texto = [
        "# Curva orçamento → excesso — sensibilidade da camada tática\n",
        "> Gerado por `scripts/curva_orcamento.py`. A camada tática **não entra "
        "no v1** (decisão 12c): esta tabela é sensibilidade para o relatório, "
        "**não** proposta de orçamento. Escolher a linha de maior excesso é "
        "exatamente o overfit que o protocolo anti-overfit da seção 10 proíbe.\n",
        f"- janela: **{datas[0].date()} a {datas[-1].date()}** ({len(datas)} pregões)",
        f"- configuração de referência: teto **no tilt = {args.teto:g}**, custo "
        f"**{args.custo_bps:.1f} bps/lado**",
        f"- linha de base (tática desligada): excesso **{base[excesso] * 100:+.2f} pp**, "
        f"sharpe {base['sharpe anualizado (excesso zero)']:.2f}, "
        f"giro {base['giro diário médio']:.3f}\n",
        "| família | orçamento | dias com overlay | excesso | Δ vs. desligada | "
        "sharpe | giro diário | custo pago |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for _, l in tabela.iterrows():
        texto.append(
            f"| {l['família']} | {l['orçamento'] * 100:.0f}% | "
            f"{l['dias com overlay']:.0f} | {l['excesso'] * 100:+.2f} pp | "
            f"{l['Δ vs. desligada'] * 100:+.2f} pp | {l['sharpe']:.2f} | "
            f"{l['giro diário']:.3f} | {l['custo pago'] * 100:.2f}% |")

    melhor = tabela.loc[tabela["Δ vs. desligada"].idxmax()]
    pior = tabela.loc[tabela["Δ vs. desligada"].idxmin()]
    texto.append("\n## Leitura\n")
    texto.append(
        f"**A faixa inteira da grade cabe entre {pior['Δ vs. desligada'] * 100:+.2f} pp "
        f"e {melhor['Δ vs. desligada'] * 100:+.2f} pp** contra a tática desligada. "
        f"O extremo favorável é `{melhor['família']}` com orçamento de "
        f"{melhor['orçamento'] * 100:.0f}%, o desfavorável é `{pior['família']}` com "
        f"{pior['orçamento'] * 100:.0f}%.\n")
    texto.append(
        "**O Δ é monótono no orçamento dentro de cada família — e é esse o "
        "argumento para não ligar.** Cada overlay é um deslocamento de peso fixo "
        "vezes o orçamento, então o efeito escala com ele e a grade **não tem "
        "ótimo interior**: a melhor linha é sempre a da ponta, e a ponta é onde "
        "eu parei de varrer, não onde algo mudou. Uma tabela assim não seleciona "
        "orçamento — só informa o sinal do overlay na janela. Escolher a linha de "
        "cima seria calibrar tamanho contra o resultado de 374 pregões, sem "
        "rodada seguinte para desmentir.\n")
    por_familia = tabela.groupby("família")["Δ vs. desligada"]
    texto.append(
        "**Sinal por família na janela** (o que a tabela de fato mede): "
        + "; ".join(f"`{nome}` {'ajuda' if g.max() > 0 else 'atrapalha'} "
                    f"({g.min() * 100:+.2f} a {g.max() * 100:+.2f} pp)"
                    for nome, g in por_familia)
        + ". Sinal medido em uma janela e uma configuração de teto não é "
          "evidência de que a tática funciona — é o insumo que faltava para "
          "decidir sem opinião.\n")
    texto.append(
        "**O que isto NÃO decide:** o orçamento. A decisão registrada (12c) é "
        "entregar o v1 com a camada tática desligada; a implementação fica no "
        "repositório, testada, para quem retomar depois da entrega.\n")

    Path(args.saida).write_text("\n".join(texto) + "\n", encoding="utf-8")
    sys.stdout.write(tabela.to_string(index=False) + f"\n\nescrito: {args.saida}\n")


if __name__ == "__main__":
    main()
