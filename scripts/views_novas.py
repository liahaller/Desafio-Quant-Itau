"""Backtest com as duas views novas empilhadas — 15b e 15g. Felipe.

**MEDE; não decide.** Este script liga cada view no `MontadorV1`, roda o MESMO
backtest do v1 e reporta o Δ contra a linha de base.

⚠️ **A base mudou de significado em 2026-08-10, e o número não.** As duas
ENTRARAM na entrega (D15a/D15b/D15c fechadas + item 4 na D22e), então a primeira
linha — `views_novas=()` — deixou de ser "o v1 entregue" e passou a ser **o v1 de
DUAS views**, a configuração anterior. A tabela continua valendo e continua sendo
o artefato obrigatório da D22 ("sem os 3 maiores" + acerto de sinal): ela mede a
**contribuição marginal de cada view** contra a carteira que existia antes delas,
que é exatamente a conta que a régua exige. O que mudou é o rótulo, não a
medição.

    incerteza (15b) : view direcional (ΣP ≠ 0) do prêmio de anúncio de
                      Savor-Wilson, ativa só em DIA de anúncio.
    B própria (15g) : trajetória do Fed com β estimado contra o ΔDGS1 (o vértice
                      da pergunta), não contra os β da 2.3 — que era o que fazia
                      o P sair idêntico ao dela.

A escala da incerteza (15c) FECHOU em 2026-08-10: entra a **entropia crua**. As
duas continuam na tabela de propósito — a D15c registra que a escolhida é a de
número maior e sobrevivência pior, e apagar a linha do percentil esconderia
justamente a comparação que sustenta essa ressalva.

Uso:
    python scripts/views_novas.py --raiz <dir com data/ do branch Paulo>
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from backtest_v1 import PONTOS_PERCENTUAIS, carregar  # noqa: E402
from backtest import run_backtest, summary  # noqa: E402
from config import ASSETS, CUSTO_BPS_POR_LADO, DELTA, TAU  # noqa: E402
from views_common import P_from_betas  # noqa: E402

# Escopo de referência de todas as varreduras desde 05/08 e configuração do
# plano B pré-registrado (10a): teto NO TILT, nível 1.
TETO = 1.0

# (rótulo, views ligadas, escala da incerteza)
CONFIGURACOES = (
    ("v1 anterior (2.2 + 2.3)", (), "entropia"),
    ("+ incerteza (entropia crua)", ("incerteza",), "entropia"),
    ("+ incerteza (percentil)", ("incerteza",), "percentil"),
    ("+ B com β próprio (DGS1)", ("B",), "entropia"),
    ("+ as duas (entropia crua)", ("incerteza", "B"), "entropia"),
    ("+ as duas (percentil)", ("incerteza", "B"), "percentil"),
)


def conta_views(resultado, nome):
    """Nº de pregões em que a view `nome` ficou ativa."""
    return sum(any(d.get("view") == nome for d in dia["views"])
               for dia in resultado.diagnostics.values())


def diagnostico_medio(resultado, nome, chave):
    """Média de `chave` nos dias em que a view `nome` esteve ativa (NaN se nunca)."""
    valores = [d[chave] for dia in resultado.diagnostics.values()
               for d in dia["views"] if d.get("view") == nome and chave in d]
    return float(np.mean(valores)) if valores else float("nan")


def dias_ativos(resultado, nomes):
    """Datas em que qualquer view de `nomes` esteve ativa."""
    return [data for data, dia in resultado.diagnostics.items()
            if any(d.get("view") in nomes for d in dia["views"])]


def atribuicao(resultado, base, nomes):
    """De onde vem o Δ: soma dos deltas diários, concentração e acerto de sinal.

    Obrigatória e não decorativa. Uma view ativa em poucos pregões pode mover o
    acumulado inteiro com UM dia — e a medição da premissa
    (`Premio_condicional.md`) já tinha identificado 2025-04-10, o choque
    tarifário, como o extremo do grupo "incerto". Sem esta conta, "a view
    performou" e "a view pegou um dia" ficam com a mesma cara na tabela.
    """
    delta = resultado.diario["r_liquido"] - base.diario["r_liquido"]
    ativos = [d for d in dias_ativos(resultado, nomes) if d in delta.index]
    maiores = delta.abs().sort_values(ascending=False).head(3).index
    nos_dias = delta.loc[ativos]
    return {
        "soma": float(delta.sum()),
        "sem_3_maiores": float(delta.drop(maiores).sum()),
        "maiores": [(d, float(delta[d])) for d in maiores],
        "acerto": float((nos_dias > 0).mean()) if len(nos_dias) else float("nan"),
        "n_dias": len(nos_dias),
        "n_positivos": int((nos_dias > 0).sum()),
    }


def P_da_B(montador, data):
    """P da B no fim da janela — o vetor, para ler a direção que ela pede.

    Recalculado fora do laço porque o `diagnostics` do motor guarda o dict da
    view, não o P. Mesmo β do backtest (`_betas_dgs1`, expansivo até `data`).
    """
    betas, _ = montador._betas_dgs1(data)
    return None if betas is None else P_from_betas(betas, list(ASSETS))


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raiz", default=".")
    parser.add_argument("--custo-bps", type=float, default=CUSTO_BPS_POR_LADO)
    parser.add_argument("--saida", default="Dump/analises/Views_novas.md")
    args = parser.parse_args()

    # Carrega UMA vez com tudo disponível e alterna as views ligadas entre as
    # rodadas: o dado é idêntico em todas as linhas por construção, em vez de
    # por coincidência de seis leituras separadas.
    retornos, montador, datas, w_mkt = carregar(
        args.raiz, views_novas=("incerteza", "B"))

    resultados, resumos = {}, {}
    for rotulo, ligadas, escala in CONFIGURACOES:
        montador.views_novas = ligadas
        montador.escala_incerteza = escala
        montador.reset()
        res = run_backtest(retornos, montador, w_mkt, datas=datas, tau=TAU,
                           delta=DELTA, custo_bps=args.custo_bps,
                           teto_alavancagem=TETO, teto_no_tilt=True)
        resultados[rotulo] = res
        resumos[rotulo] = summary(res, benchmark=retornos["SPY"])
    montador.views_novas = ()
    montador.reset()

    base = resumos[CONFIGURACOES[0][0]]["excesso acumulado (líquido − benchmark)"]
    L = []
    L.append("# Backtest com as views novas empilhadas — 15b (incerteza) e 15g (B própria)\n")
    L.append("> Gerado por `scripts/views_novas.py`. **Mede; não decide.** As duas "
             "views ENTRARAM na entrega em 2026-08-10 (D15a/D15b/D15c + item 4 na "
             "D22e) — este arquivo é o **registro obrigatório da D22** (atribuição "
             "'sem os 3 maiores' + acerto de sinal), não mais uma proposta. Escopo "
             "de referência: **teto no tilt = 1**, γ = 1,0 (D1.1), custo de "
             f"{args.custo_bps:.1f} bps/lado.\n")
    L.append(f"- janela: **{datas[0].date()} a {datas[-1].date()}** ({len(datas)} pregões)")
    L.append("- ⚠️ a primeira linha (`views_novas=()`) é o **v1 de DUAS views**, a "
             "configuração ANTERIOR — não a entregue. Ela segue sendo o grupo de "
             "controle e a base contra a qual o Δ de cada view é medido: se ela "
             "não reproduzir o +4,07 pp registrado, o errado é este script")
    L.append("- a configuração ENTREGUE é a linha **`+ as duas (entropia crua)`**\n")

    L.append("| configuração | dias com a view | excesso × SPY | Δ vs. v1 | líquido | "
             "sharpe | Σ\\|w\\| média | giro/dia |")
    L.append("|---|---|---|---|---|---|---|---|")
    for rotulo, ligadas, _ in CONFIGURACOES:
        s, res = resumos[rotulo], resultados[rotulo]
        dias = []
        if "incerteza" in ligadas:
            dias.append(f"incerteza {conta_views(res, 'incerteza_anuncio')}")
        if "B" in ligadas:
            dias.append(f"B {conta_views(res, 'B_trajetoria_propria')}")
        excesso = s["excesso acumulado (líquido − benchmark)"]
        L.append(
            f"| {rotulo} | {' · '.join(dias) if dias else '—'} | "
            f"{excesso * 100:+.2f} pp | "
            f"{'—' if not ligadas else f'{(excesso - base) * 100:+.2f} pp'} | "
            f"{s['retorno acumulado líquido'] * 100:+.1f}% | "
            f"{s['sharpe anualizado (excesso zero)']:.2f} | "
            f"{s['alavancagem média (Σ|w|)']:.2f} | {s['giro diário médio']:.3f} |")

    L.append("\n## O que cada view fez por dentro\n")
    for rotulo, nome, chaves in (
            ("+ incerteza (entropia crua)", "incerteza_anuncio",
             (("entropia", "entropia média"), ("incerteza_liquida", "incerteza líquida"),
              ("sum_P_beta", "Σ P·β"), ("n_eventos_beta", "eventos no β"))),
            ("+ incerteza (percentil)", "incerteza_anuncio",
             (("entropia", "percentil médio"), ("incerteza_liquida", "incerteza líquida"),
              ("sum_P_beta", "Σ P·β"), ("n_eventos_beta", "eventos no β"))),
            ("+ B com β próprio (DGS1)", "B_trajetoria_propria",
             (("e_poly_bps", "E_poly (bps)"), ("benchmark_bps", "DGS1 (bps)"),
              ("surpresa_bps", "surpresa crua (bps)"),
              ("surpresa_liquida", "surpresa líquida (bps)"),
              ("sum_P_beta", "Σ P·β"), ("n_eventos_beta", "eventos no β")))):
        res = resultados[rotulo]
        partes = " · ".join(f"{legenda} {diagnostico_medio(res, nome, chave):+.4g}"
                            for chave, legenda in chaves)
        L.append(f"- **{rotulo}** ({conta_views(res, nome)} dias): {partes}")

    L.append("\n## De onde vem o Δ — atribuição e concentração\n")
    L.append("Soma dos Δ DIÁRIOS de retorno líquido contra o v1 (não composta, por "
             "isso não bate exatamente com o acumulado da tabela acima), e o que "
             "sobra dela tirando os três pregões de maior |Δ|. **Uma view ativa em "
             "poucos dias pode carregar o acumulado inteiro com um pregão só.**\n")
    L.append("| configuração | Σ dos Δ diários | sem os 3 maiores | acerto de sinal "
             "nos dias da view |")
    L.append("|---|---|---|---|")
    nomes_por_config = {"incerteza": "incerteza_anuncio", "B": "B_trajetoria_propria"}
    atrib = {}
    for rotulo, ligadas, _ in CONFIGURACOES[1:]:
        nomes = {nomes_por_config[x] for x in ligadas}
        a = atribuicao(resultados[rotulo], resultados[CONFIGURACOES[0][0]], nomes)
        atrib[rotulo] = a
        L.append(f"| {rotulo} | {a['soma'] * 100:+.2f} pp | "
                 f"{a['sem_3_maiores'] * 100:+.2f} pp | "
                 f"{a['acerto']:.0%} ({a['n_positivos']}/{a['n_dias']}) |")
    L.append("\nOs três pregões de maior |Δ| em cada configuração:\n")
    for rotulo in atrib:
        dias = " · ".join(f"**{d.date()}** {v * 100:+.2f} pp (SPY "
                          f"{retornos['SPY'][d] * 100:+.2f}%)"
                          for d, v in atrib[rotulo]["maiores"])
        L.append(f"- {rotulo}: {dias}")

    P_B = P_da_B(montador, datas[-1])
    if P_B is not None:
        L.append("\n**P da B no fim da janela** (β expansivo contra o ΔDGS1) — a "
                 "15g mediu 95,6° de ângulo contra o P da 2.3 usando o DGS10 como "
                 "proxy; esta linha é o vértice CERTO:\n")
        L.append("| view | " + " | ".join(ASSETS) + " |")
        L.append("|---" * (len(ASSETS) + 1) + "|")
        L.append("| B_trajetoria_propria | " + " | ".join(f"{v:+.2f}" for v in P_B) + " |")
    L.append("\nA view de incerteza é **direcional por construção** (15b): "
             "P[SPY] = +2 e 0 no resto, Σ|P| = 2. **Ela não é a única view com "
             "ΣP ≠ 0** — a obrigação 5a foi finalmente executada em 2026-08-10 "
             "(`Dump/analises/Ortogonalidade.md`) e mediu ΣP mediano de +0,96 na "
             "2.2, +1,74 na 2.3 e +1,24 na 15g. As views ditas neutras são "
             "líquidas COMPRADAS nos 8 ativos que não são o SPY; a 15b declara o "
             "direcional, não o introduz.\n")

    # Leitura GERADA do que foi medido — frase cravada à mão vira mentira na
    # re-rodada seguinte (lição da sessão 15).
    L.append("\n## Leitura\n")
    for rotulo in atrib:
        a, s = atrib[rotulo], resumos[rotulo]
        excesso = s["excesso acumulado (líquido − benchmark)"]
        sobrevive = np.sign(a["sem_3_maiores"]) == np.sign(a["soma"]) and a["soma"] != 0
        L.append(
            f"- **{rotulo}**: excesso {excesso * 100:+.2f} pp contra "
            f"{base * 100:+.2f} pp do v1 ({(excesso - base) * 100:+.2f} pp). O Δ "
            + ("**sobrevive**" if sobrevive else "**NÃO sobrevive**")
            + f" à retirada dos três pregões extremos ({a['soma'] * 100:+.2f} pp → "
            f"{a['sem_3_maiores'] * 100:+.2f} pp), e o acerto de sinal nos dias da "
            f"view é de {a['acerto']:.0%}.")
    L.append("\n**Pendência de protocolo PAGA (D21b):** a 15g exigia a ordem `DGS1 "
             "chegou → refazer o teste de sinal no vértice certo → só então "
             "empilhar`. Quando este script rodou pela primeira vez, a etapa do "
             "meio estava pulada. Ela rodou depois (`scripts/teste_sinal.py`, "
             "`Dump/analises/Teste_sinal.md`): a B dá **t +0,33 · 51%** em h = 1 e "
             "**não sai invertida** — passa o veto do item 3 da D22.\n")
    L.append("**O que este arquivo não faz:** não decide. A entrega roda com as "
             "duas ligadas por decisão registrada (D15a/D15b/D15c/D22e), e os "
             "números acima existem para que o Δ de cada uma seja lido como "
             "contribuição medida, não como desempenho prometido.\n")

    Path(args.saida).write_text("\n".join(L) + "\n", encoding="utf-8")
    sys.stdout.write("\n".join(L[4:]) + f"\n\nescrito: {args.saida}\n")


if __name__ == "__main__":
    main()
