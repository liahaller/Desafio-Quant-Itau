"""Backtest com a view C empilhada — varredura em k. Felipe.

**MEDE; não decide.** A C é a última candidata (D23e) e o k dela **não está
escolhido**: a curva de absorção (`Absorcao_C.md`) NÃO identifica um patamar —
os dois episódios do Irã discordam (corr das curvas +0,08). Sem critério de
mecanismo, a grade roda inteira e reporta.

⚠️ **Esta tabela não seleciona k.** Escolher a linha de melhor excesso seria
calibrar parâmetro contra 374 pregões, que é o overfit em dois passos do
protocolo anti-overfit da seção 10 — agora sem rodada seguinte para desmentir.
O que ela responde é outra pergunta, e é a que o dono fez: **quanto a C mexe no
resultado, e se ela mexe do mesmo jeito em toda a grade.**

A primeira linha é a entrega de QUATRO views (D23) — grupo de controle: se ela
não reproduzir a linha `tilt ≤ 1` do `Backtest_v1.md`, o errado é este script.
O número não vem escrito aqui de propósito: a versão anterior citava "+6,24 pp"
e sobreviveu calada à entrada da camada (D28.13) e da régua (6q).

Uso:
    python scripts/view_C_backtest.py [--raiz .]
"""

import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from backtest_v1 import VIEWS_V1, carregar  # noqa: E402
from backtest import run_backtest, summary  # noqa: E402
from config import ASSETS, CUSTO_BPS_POR_LADO, DELTA, TAU  # noqa: E402
from market_inputs import regua_por_decisao  # noqa: E402
from teste_sinal import K_GRID_C, series_C  # noqa: E402
from views_novas import atribuicao, conta_views  # noqa: E402

TETO = 1.0   # escopo de referência desde 05/08 e plano B da 10a


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raiz", default=".")
    parser.add_argument("--custo-bps", type=float, default=CUSTO_BPS_POR_LADO)
    parser.add_argument("--saida", default="Dump/analises/View_C_backtest.md")
    # DESLIGADA por default, ao contrário dos outros scripts: a régua da Lia
    # cobre as QUATRO views da entrega e **não tem `c` para a C**. Com ela
    # ligada, todo k da grade morre no casamento de chaves do `aplicar_veto` —
    # a C viva sem linha no CSV — e a varredura não mede nada. Ligar exigiria
    # ou a Lia estender a régua à C, ou inventar `c = 1` para ela, que é
    # exatamente a confiança-sem-medição que a régua existe para evitar.
    parser.add_argument("--regua", default="",
                        help="CSV do `c` por decisão da Lia. **Default vazio** "
                             "— o CSV não cobre a C. Controle e grade usam a "
                             "MESMA configuração, então o Δ mede a C")
    parser.add_argument("--regua-nivel", type=float, default=1.0)
    args = parser.parse_args()

    regua = (regua_por_decisao(args.regua, nivel=args.regua_nivel)
             if args.regua else None)

    retornos, montador, datas, w_mkt = carregar(args.raiz)
    montador.series_C = series_C(args.raiz, montador._fl, retornos.index)

    def rodar(views, k):
        montador.views_novas, montador.k_C = views, k
        montador.reset()
        res = run_backtest(retornos, montador, w_mkt, datas=datas, tau=TAU,
                           delta=DELTA, custo_bps=args.custo_bps,
                           teto_alavancagem=TETO, teto_no_tilt=True,
                           regua=regua)
        return res, summary(res, benchmark=retornos["SPY"])

    base_res, base_sum = rodar(VIEWS_V1, None)
    base = base_sum["excesso acumulado (líquido − benchmark)"]

    L = ["# Backtest com a view C empilhada — varredura em k\n",
         "> Gerado por `scripts/view_C_backtest.py`. **Mede; não decide.** O k da "
         "C não está escolhido: a curva de absorção não identifica patamar "
         "(`Absorcao_C.md`). Escopo: **teto no tilt = 1**, γ = 1,0, custo de "
         f"{args.custo_bps:.1f} bps/lado.\n",
         f"- janela: **{datas[0].date()} a {datas[-1].date()}** ({len(datas)} pregões)",
         "- régua do Ω: "
         + (f"**ligada no nível {args.regua_nivel:g}** (6q), igual nas duas "
            "pontas" if regua else
            "**desligada nas duas pontas** — a régua da Lia cobre as quatro "
            "views da entrega e **não tem `c` para a C**. Por isso este "
            "artefato NÃO reproduz o número da entrega (que roda com ela "
            "desde a 6q): as duas pontas daqui são comparáveis entre si, e "
            "não com o `Backtest_v1.md`"),
         "- a primeira linha é a **entrega de 4 views** (D23) e é o grupo de "
         "controle do Δ desta tabela\n",
         "| configuração | dias com a C | excesso × SPY | Δ vs. entrega | líquido "
         "| sharpe | Σ\\|w\\| média | giro/dia |",
         "|---|---|---|---|---|---|---|---|"]

    resultados, bloqueados = {}, {}
    for rotulo, views, k in ([("entrega (4 views)", VIEWS_V1, None)]
                             + [(f"+ C (k = {k})", VIEWS_V1 + ("C",), k)
                                for k in K_GRID_C]):
        try:
            res, s = rodar(views, k)
        except ValueError as erro:
            # A régua não cobre a C: o erro é de casamento de chaves e NÃO é a
            # D4.1. Sem esta separação a linha saía rotulada como bloqueio de
            # horizonte, que é falso — e falso justamente sobre o k = 1, o
            # único que a D4.1 deixa passar.
            if "não casa com as views ativas" in str(erro):
                L.append(f"| {rotulo} | — | 🛑 **sem `c` na régua** | — | — | "
                         "— | — | — |")
                continue
            # DECISAO-4.1 — guarda deliberado do `stack_views`: o Q da C é
            # ACUMULADO EM k DIAS e o das outras views é de 1 dia. Somar os dois
            # é somar km/h com km. Não é bug deste script; é a reconciliação de
            # horizonte que nunca fechou, mordendo pela primeira vez.
            bloqueados[k] = str(erro).split(" — ")[0]
            L.append(f"| {rotulo} | — | 🛑 **bloqueado (D4.1)** | — | — | — | — | — |")
            continue
        resultados[rotulo] = res
        excesso = s["excesso acumulado (líquido − benchmark)"]
        dias = conta_views(res, "C_geopolitica_energia") if k else "—"
        L.append(f"| {rotulo} | {dias} | {excesso * 100:+.2f} pp | "
                 f"{'—' if k is None else f'{(excesso - base) * 100:+.2f} pp'} | "
                 f"{s['retorno acumulado líquido'] * 100:+.1f}% | "
                 f"{s['sharpe anualizado (excesso zero)']:.2f} | "
                 f"{s['alavancagem média (Σ|w|)']:.2f} | "
                 f"{s['giro diário médio']:.3f} |")

    if bloqueados:
        L.append("\n🛑 **A grade não roda inteira, e o motivo é uma decisão "
                 "aberta desde o começo do projeto.** O `stack_views` recusa "
                 "empilhar views com `horizonte_q_dias` diferentes "
                 "(**DECISAO-4.1**, guarda que FALHA ALTO de propósito): o Q da "
                 "C é **acumulado em k dias** e o das outras quatro é de **1 "
                 "dia**. Somar os dois é somar km/h com km — não daria erro, "
                 "daria peso errado.\n")
        L.append("| k | situação |")
        L.append("|---|---|")
        for k in K_GRID_C:
            L.append(f"| {k} | " + ("**bloqueado** — `horizonte_q_dias` = "
                                    f"{k} contra 1 das outras views"
                                    if k in bloqueados else
                                    "roda — `horizonte_q_dias` = 1, igual às outras")
                     + " |")
        L.append("\n**Consequência, e ela é anterior a qualquer número:** a C só "
                 "consegue conviver com as outras quatro views em **k = 1**. "
                 "Para qualquer k ≥ 2 a entrada dela exige fechar a D4.1 antes — "
                 "que é decisão de metodologia, não de implementação.\n")

    L.append("\n## Registro obrigatório da D22 — atribuição e concentração\n")
    L.append("Soma dos Δ DIÁRIOS contra a entrega de 4 views, e o que sobra dela "
             "tirando os três pregões de maior |Δ|.\n")
    L.append("| configuração | Σ dos Δ diários | sem os 3 maiores | acerto de "
             "sinal nos dias da view |")
    L.append("|---|---|---|---|")
    rodadas = [k for k in K_GRID_C if f"+ C (k = {k})" in resultados]
    for k in rodadas:
        a = atribuicao(resultados[f"+ C (k = {k})"], base_res,
                       {"C_geopolitica_energia"})
        L.append(f"| + C (k = {k}) | {a['soma'] * 100:+.2f} pp | "
                 f"{a['sem_3_maiores'] * 100:+.2f} pp | "
                 f"{a['acerto']:.0%} ({a['n_positivos']}/{a['n_dias']}) |")

    L.append("\n## Leitura (gerada)\n")
    deltas = {k: (summary(resultados[f"+ C (k = {k})"], benchmark=retornos["SPY"])
                  ["excesso acumulado (líquido − benchmark)"] - base)
              for k in rodadas}
    if len(deltas) < len(K_GRID_C):
        L.append(f"- **A varredura mede {len(deltas)} de {len(K_GRID_C)} pontos "
                 "da grade** — o resto está bloqueado pela D4.1. Uma grade "
                 "incompleta por decisão aberta não é insumo de escolha de "
                 "parâmetro; é o registro de que o parâmetro não pode ser "
                 "escolhido ainda.")
    for k, v in deltas.items():
        L.append(f"- **k = {k}**: Δ de **{v * 100:+.2f} pp** contra a entrega de "
                 "quatro views.")

    Path(args.saida).write_text("\n".join(L) + "\n", encoding="utf-8")
    sys.stdout.write("\n".join(L) + f"\n\nescrito: {args.saida}\n")


if __name__ == "__main__":
    main()
