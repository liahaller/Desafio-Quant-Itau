"""Curva banda de não-negociação → giro, reversão e excesso.

A banda é a saída que o D8 previu para o caso de o giro do H = 1 dia ser feito
de ruído: o custo não vem de negociar muito, vem de **negociar contra si mesmo**
(`reversal_share`, o mecanismo que matou a GTAA diária citada na pesquisa). Δw
menor que a banda não é executado — ver `backtest.no_trade_band`.

Esta varredura existe porque o nível da banda é **threshold do modelo**, e pela
regra 6 do `CLAUDE.md` ele não se inventa: mede-se e reporta-se. **A banda não
está ligada no v1** (`banda=None`), e nenhuma linha desta tabela é proposta.

As três colunas que decidem, e nesta ordem:

  - **giro desfeito em 1–2 pregões** — é o que a banda deveria atacar. Se ele
    não cair, a banda não está mordendo o ruído, está só atrasando trade.
  - **custo de breakeven** — bps por lado que zeram o retorno. Sobe com a banda
    se o giro cortado era mesmo ruído (menos giro, mesmo bruto).
  - **excesso × SPY** — vem por último de propósito: escolher a banda por ele é
    o overfit em dois passos do protocolo anti-overfit (seção 10).

Uso:

    python scripts/curva_banda.py --raiz .
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
from market_inputs import regua_por_decisao  # noqa: E402

EXCESSO = "excesso acumulado (líquido − benchmark)"
REVERSAO = "giro desfeito em 1–2 pregões"
BREAKEVEN = "custo de breakeven (bps por lado)"


def rodada(retornos, montador, datas, w_mkt, banda, teto, custo_bps, regua=None):
    """Um backtest com a banda dada, no escopo de teto do v1 (no tilt)."""
    resultado = run_backtest(retornos, montador, w_mkt, datas=datas, tau=TAU,
                             delta=DELTA, custo_bps=custo_bps,
                             teto_alavancagem=teto, teto_no_tilt=True,
                             banda=banda, regua=regua)
    montador.reset()   # médias expansivas voltam ao estado do 1º pregão
    s = summary(resultado, benchmark=retornos["SPY"])
    # fração dos pares (dia, ativo) em que a banda impediu a negociação
    trades = resultado.trades
    s["pernas paradas pela banda"] = float((trades == 0.0).to_numpy().mean())
    return s


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raiz", default=".",
                        help="diretório com data/ extraído do branch Paulo")
    parser.add_argument("--bandas", type=float, nargs="+",
                        default=[0.001, 0.0025, 0.005, 0.01, 0.025, 0.05],
                        help="grade de banda (fração do patrimônio, por ativo) "
                             "— varredura, não escolha")
    parser.add_argument("--teto", type=float, default=1.0)
    parser.add_argument("--custo-bps", type=float, default=CUSTO_BPS_POR_LADO)
    parser.add_argument("--saida", default="Dump/analises/Curva_banda.md")
    parser.add_argument("--regua", default=None,
                        help="CSV do `c` por decisão da Lia; default segue o "
                             "--raiz, `\"\"` desliga. A entrega roda com ela "
                             "ligada no nível 1 (6q), e a banda tem de ser "
                             "medida sobre o giro que a entrega realmente faz")
    parser.add_argument("--regua-nivel", type=float, default=1.0)
    args = parser.parse_args()

    if args.regua is None:
        args.regua = str(Path(args.raiz) / "data" / "lia" / "c_por_decisao.csv")
    regua = (regua_por_decisao(args.regua, nivel=args.regua_nivel)
             if args.regua else None)

    if any(b <= 0 for b in args.bandas):
        raise SystemExit("banda é fração do patrimônio e tem de ser positiva "
                         "— o zero já entra como linha de base")

    retornos, montador, datas, w_mkt = carregar(args.raiz)
    linhas = []
    for b in [None] + list(args.bandas):
        s = rodada(retornos, montador, datas, w_mkt, b, args.teto, args.custo_bps,
                   regua=regua)
        linhas.append({
            "banda": 0.0 if b is None else b,
            "giro diário": s["giro diário médio"],
            "reversão": s[REVERSAO],
            "pernas paradas": s["pernas paradas pela banda"],
            "breakeven": s[BREAKEVEN],
            "custo pago": s["custo pago (fração do patrimônio)"],
            "excesso": s[EXCESSO],
            "sharpe": s["sharpe anualizado (excesso zero)"],
            "Σ|w|": s["alavancagem média (Σ|w|)"],
        })
    tabela = pd.DataFrame(linhas)
    base = tabela.iloc[0]

    texto = [
        "# Curva banda de não-negociação — o giro do H = 1 dia é ruído?\n",
        "> Gerado por `scripts/curva_banda.py`. **A banda não está ligada no v1** "
        "(`banda=None`): o nível é threshold do modelo e vem de decisão humana "
        "(regra 6 do `CLAUDE.md`). Esta tabela **mede e reporta** — nenhuma linha "
        "é proposta.\n",
        f"- janela: **{datas[0].date()} a {datas[-1].date()}** ({len(datas)} pregões)",
        f"- configuração de referência: teto **no tilt = {args.teto:g}**, custo "
        f"**{args.custo_bps:.1f} bps/lado**, camada tática v2 "
        + ("**ligada**" if montador.sleeves else "desligada")
        + ", régua do Ω "
        + (f"**ligada no nível {args.regua_nivel:g}** (6q)" if regua
           else "**desligada**")
        + ". As views são as do `backtest_v1.carregar` e **não são redeclaradas "
          "aqui** — foi assim que este artefato ficou anunciando \"2.2 e 2.3\" "
          "depois da D23 (mesmo erro da D25g)",
        "- banda **por ativo**: Δw abaixo dela não é executado, e o Δw grande vai "
        "inteiro — não é imposto sobre o trade, é filtro de ruído\n",
        "| banda | giro diário | desfeito em 1–2 pregões | pernas paradas | "
        "breakeven | custo pago | excesso × SPY | sharpe | Σ\\|w\\| |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for _, l in tabela.iterrows():
        rotulo = "**0 (v1)**" if l["banda"] == 0.0 else f"{l['banda'] * 100:.2f}%"
        texto.append(
            f"| {rotulo} | {l['giro diário']:.3f} | {l['reversão']:.3f} | "
            f"{l['pernas paradas'] * 100:.0f}% | {l['breakeven']:.2f} bps | "
            f"{l['custo pago'] * 100:.2f}% | {l['excesso'] * 100:+.2f} pp | "
            f"{l['sharpe']:.2f} | {l['Σ|w|']:.2f} |")

    # --- leitura CALCULADA da tabela ---------------------------------------
    # Prosa fixa acima de tabela gerada foi o erro do `curva_c.py`: o número
    # muda de rodada, a conclusão escrita à mão não. Tudo abaixo sai da tabela.
    corte_giro = 1.0 - tabela["giro diário"].iloc[-1] / base["giro diário"]
    d_rev = tabela["reversão"].iloc[-1] - base["reversão"]
    d_be = tabela["breakeven"] - base["breakeven"]
    d_exc = tabela["excesso"] - base["excesso"]
    monotona = bool((tabela["giro diário"].diff().dropna() <= 1e-12).all())

    texto.append("\n## Leitura\n")
    texto.append(
        f"**Ponto de partida (v1, sem banda):** giro diário **{base['giro diário']:.3f}**, "
        f"com **{base['reversão'] * 100:.1f}%** dele desfeito em 1–2 pregões, e custo "
        f"de breakeven de **{base['breakeven']:.2f} bps por lado** contra os "
        f"{args.custo_bps:.1f} bps premissados — **{base['breakeven'] / args.custo_bps:.0f}× "
        "de folga**, que é o número a ter em mente antes de discutir banda: "
        "o custo teria de subir uma ordem de grandeza para virar o sinal.\n")
    texto.append(
        f"**A banda corta giro:** de {base['giro diário']:.3f} a "
        f"{tabela['giro diário'].iloc[-1]:.3f} ({corte_giro * 100:.0f}% a menos) na "
        f"ponta da grade, {'monotonicamente' if monotona else 'de forma NÃO monótona'}"
        f" — na maior banda, {tabela['pernas paradas'].iloc[-1] * 100:.0f}% dos pares "
        "(dia × ativo) não negociam.\n")
    # Dissociação "pernas paradas × giro cortado": se a banda mais fina já para
    # muita perna e mesmo assim quase não corta giro, é porque as pernas
    # pequenas não CARREGAM giro — não existe cauda de trade miúdo para filtrar.
    p1, g1 = tabela["pernas paradas"].iloc[1], tabela["giro diário"].iloc[1]
    corte_1 = 1.0 - g1 / base["giro diário"]
    texto.append(
        f"**O giro está concentrado em poucas pernas grandes.** A banda mais fina "
        f"da grade ({tabela['banda'].iloc[1] * 100:.2f}%) já impede "
        f"**{p1 * 100:.0f}%** dos pares (dia × ativo) de negociar e ainda assim "
        f"corta só **{corte_1 * 100:.1f}%** do giro"
        + (" — ou seja, não existe uma cauda de trade miúdo a filtrar: quase todo "
           "o giro do v1 está em poucas pernas grandes, que a banda deixa passar "
           "inteiras por construção.\n" if corte_1 < 0.05 else
           ", então a cauda de trade miúdo existe e responde pelo giro.\n"))
    texto.append(
        "**Mas cortar giro não é o teste — o teste é a reversão.** "
        + (f"Ela {'cai' if d_rev < 0 else 'SOBE'} de {base['reversão']:.3f} para "
           f"{tabela['reversão'].iloc[-1]:.3f} ({d_rev:+.3f}). "
           + ("O giro que a banda tira é desproporcionalmente o que se desfazia: "
              "é ruído sendo pago a 2 bps a volta, e a banda ataca o mecanismo "
              "certo.\n" if d_rev < -0.01 else
              "Ou seja, **o giro que a banda tira NÃO é o que se desfazia** — ela "
              "está atrasando reposicionamento genuíno, não filtrando ruído. Nesta "
              "janela a banda não resolve o problema que motivou sua existência.\n"
              if d_rev > 0.01 else
              "Praticamente não se move: a banda tira giro dos dois tipos na mesma "
              "proporção, então não há evidência de que o giro do v1 seja ruído.\n")))
    texto.append(
        f"**Custo de breakeven:** vai de {base['breakeven']:.2f} bps a "
        f"{tabela['breakeven'].iloc[-1]:.2f} bps ({d_be.iloc[-1]:+.2f}); o máximo da "
        f"grade é **{tabela['breakeven'].max():.2f} bps**, na banda de "
        f"{tabela.loc[tabela['breakeven'].idxmax(), 'banda'] * 100:.2f}%. "
        + ("A folga contra os 2 bps premissados aumenta com a banda.\n"
           if d_be.iloc[-1] > 0 else
           "⚠️ A folga contra os 2 bps premissados **encolhe** com a banda — o giro "
           "cortado estava pagando por si.\n"))
    texto.append(
        f"**Excesso × SPY:** {base['excesso'] * 100:+.2f} pp sem banda, faixa de "
        f"{tabela['excesso'].min() * 100:+.2f} a {tabela['excesso'].max() * 100:+.2f} pp "
        f"na grade (Δ de {d_exc.min() * 100:+.2f} a {d_exc.max() * 100:+.2f} pp). "
        + ("O sinal do resultado não muda em nenhuma banda da grade.\n"
           if tabela["excesso"].min() * tabela["excesso"].max() > 0 else
           "⚠️ O sinal do resultado **muda de lado** dentro da grade — a conclusão "
           "do v1 não é robusta à banda, e isso vale mais que o número central.\n"))
    passos = tabela["excesso"].diff().dropna()
    monotono_exc = bool((passos >= 0).all() or (passos <= 0).all())
    melhor = tabela.loc[tabela["excesso"].idxmax()]
    texto.append(
        "**O que isto NÃO decide:** o nível da banda. "
        + ("O excesso é monótono na grade, então ela não seleciona nível: a melhor "
           "linha é a da ponta, e a ponta é onde eu parei de varrer. "
           if monotono_exc else
           f"O excesso **não** é monótono na grade — ele oscila e o máximo cai numa "
           f"banda interior ({melhor['banda'] * 100:.2f}%, {melhor['excesso'] * 100:+.2f} pp). "
           "É exatamente a tabela que tenta o olho a escolher a linha de maior "
           "número, e é o que o protocolo anti-overfit da seção 10 proíbe: com a "
           "reversão parada, a oscilação do excesso não tem mecanismo por trás. ")
        + "Se a banda entrar, o nível se escolhe pela **reversão e pelo breakeven** "
          "— as duas primeiras colunas —, junto com o teto, e uma vez só.\n")

    Path(args.saida).write_text("\n".join(texto) + "\n", encoding="utf-8")
    sys.stdout.write(tabela.to_string(index=False) + f"\n\nescrito: {args.saida}\n")


if __name__ == "__main__":
    main()
