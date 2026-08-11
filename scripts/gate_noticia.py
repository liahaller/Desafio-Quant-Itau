"""Notícia — o gate completo nos mercados que nenhuma sleeve jamais leu. Felipe.

As 13 tentativas táticas do projeto leram **Fed ou CPI**. O `Premissa_G1.md`
mediu, pela primeira vez, o G1 fora dessas duas famílias e achou que o corte
não é *"Fed × não-Fed"* — é **se existe fluxo de notícia a que o preço
responda**: tarifas 3,5×, Irã 1,2× e 4,0× já em k = 1, contra recessão 0,7×,
Trump 0,5× e Câmara 0,0×.

O que o `Premissa_G1.md` mediu foi **só o G1**. Este script roda o gate
inteiro nesses mercados — G0, G1, G2 e G3, ao longo da mesma grade de
horizontes do `gate_m3_acumulado.py` — porque um G1 alto sozinho nunca
autorizou nada (é condição necessária, e a cauda do CPI já passou o G1 com
20,1× para morrer no G2 e no G3).

⚠️ **A tensão que decide esta candidata é o G0, e ela é estrutural no dado
entregue: cobertura e dispersão são quase disjuntas.** O que se mexe dura 3, 9,
29 ou 59 pregões; o que dura não se mexe. Por isso o G0 vem na mesma linha que
o resto, e não numa nota de rodapé — uma sleeve precisa das duas.

⚠️ **As premissas são declaradas ANTES de medir e herdadas POR REFERÊNCIA** do
`gate_event_driven.py` (o script importa o mesmo dicionário, não uma cópia).
Isso não é economia de linha: é o que garante que a 3.2 e a notícia estejam
sendo julgadas contra a MESMA tese em cada mercado, e que a diferença entre os
dois artefatos seja só o gatilho.

**Nada em `src/` é tocado.**

Uso:

    python scripts/gate_noticia.py --raiz .
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from config import ASSETS  # noqa: E402
from gate_event_driven import PRECEDENTES, PREMISSAS  # noqa: E402
from gate_sleeves import (COL_G1, COL_G3, bate_premissa,  # noqa: E402
                          corr_comum, eventos_diarios, mu_do_sinal,
                          razao_dispersao, referencias_g3)
from market_inputs import sample_covariance  # noqa: E402
from premissa_g1 import HORIZONTES, em_pregoes, series_dos_mercados  # noqa: E402

# Janela do event-study, em pregões. 1 = sleeve reassinada todo dia, igual ao
# C1a da D17 e ao `gate_m3_acumulado.py`: `k` fica sendo lookback puro e nenhum
# parâmetro de permanência entra pela porta dos fundos.
JANELA = 1

# Só as famílias que nenhuma sleeve leu. Fed e CPI ficam de fora porque já têm
# gate próprio (`Gate_sleeves.md`, `Gate_M3_acumulado.md`) — repetir aqui
# duplicaria artefato e daria duas fontes da verdade para o mesmo número.
FAMILIA = "binário (nunca medido)"


def estabilidade(retornos, sinal, declarado, sigma, ate, assets=ASSETS):
    """O veredito do G2 sobrevive às duas metades da própria amostra?

    Não é refinamento: é o teste que a **D19c** já rodou no mercado de recessão
    e que derrubou a 3.1 direcional — o coeficiente vinha +0,97% (t +6,52) na
    1ª metade e **−0,35% (t −2,27)** na 2ª, as duas significantes e opostas.
    Um G2 que passa na amostra inteira e troca de sinal no meio não é sinal, é
    a média de dois regimes; e como não há segundo mercado de recessão, partir
    a amostra é o único teste fora da amostra disponível.

    `assets` é a ordem do universo em que `mu` é indexado — default o do v1. O
    `gate_transversal_neutro.py` passa um universo estendido (com as pernas
    hedgeadas), e é por isso que o parâmetro existe.

    Devolve `[(rótulo, bate, detalhe, n)]` para as duas metades.
    """
    sinal = pd.Series(sinal).dropna()
    corte = len(sinal) // 2
    saida = []
    for rotulo, pedaco in (("1ª metade", sinal.iloc[:corte]),
                           ("2ª metade", sinal.iloc[corte:])):
        mu, n_mu = mu_do_sinal(retornos, eventos_diarios(pedaco), JANELA,
                               tuple(declarado), sigma, ate)
        ok, detalhe = bate_premissa(mu, assets, declarado)
        saida.append((rotulo, ok, detalhe, n_mu))
    return saida


def main():
    # O console do Windows abre em cp1252 e engasga nos rótulos acentuados.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raiz", default=".")
    parser.add_argument("--saida", default="Dump/analises/Gate_noticia.md")
    args = parser.parse_args()

    series, retornos, montador, datas = series_dos_mercados(args.raiz)
    sigma = sample_covariance(retornos)
    ate = datas[-1] + pd.Timedelta(days=1)
    referencias = referencias_g3(montador, datas, montador._fl)

    linhas, medidas, sem_serie = [], {}, []
    for nome, familia, serie, tick, _unidade in series:
        if familia != FAMILIA or nome not in PREMISSAS:
            continue
        declarado, _texto = PREMISSAS[nome]
        base = em_pregoes(serie)
        if base.dropna().empty:
            sem_serie.append(nome)
            continue
        for k in HORIZONTES:
            sinal = base.diff(k).dropna()
            if sinal.empty:
                continue
            eventos = eventos_diarios(sinal)
            mu, n_mu = mu_do_sinal(retornos, eventos, JANELA, tuple(declarado),
                                   sigma, ate)
            ok, detalhe = bate_premissa(mu, ASSETS, declarado)
            correlacoes = {c: corr_comum(sinal, ref)
                           for c, ref in referencias.items()}
            finitas = {c: v for c, v in correlacoes.items() if np.isfinite(v)}
            pior = max(finitas, key=lambda c: abs(finitas[c])) if finitas else None
            razao = razao_dispersao(sinal, tick)
            medidas[(nome, k)] = {"ok": ok, "n_mu": n_mu, "razao": razao,
                                  "corr": finitas.get(pior, float("nan")),
                                  "pior": pior, "dias": len(sinal),
                                  "sinal": sinal, "declarado": declarado}
            linhas.append({
                "mercado": nome,
                "lookback": f"k = {k}",
                "G0 dias": len(sinal),
                "eventos no μ": n_mu,
                "G1 razão / tick": f"{razao:.1f}×" if np.isfinite(razao) else "—",
                "G2 μ (bps/dia)": detalhe,
                "G2 bate?": "✅" if ok else "❌",
                COL_G3: (f"{finitas[pior]:+.2f} ({pior})" if pior else "—"),
            })

    tabela = pd.DataFrame(linhas)
    mercados = list(dict.fromkeys(tabela["mercado"]))

    # Passa nos TRÊS critérios mensuráveis de uma vez. G0 não entra como corte
    # (não há corte cravado) — entra como coluna, e a leitura abaixo o confronta.
    aprovados = [(m, k) for (m, k), v in medidas.items()
                 if v["ok"] and np.isfinite(v["razao"]) and v["razao"] > 1.0]

    texto = [
        "# Notícia — o gate completo nos mercados nunca lidos por sleeve\n",
        "> Gerado por `scripts/gate_noticia.py`. **Mede; não decide.** Nenhum "
        "corte cravado, mesma regra do `Gate_sleeves.md`.\n",
        f"- janela do backtest: **{datas[0]:%Y-%m-%d} a {datas[-1]:%Y-%m-%d}** "
        f"({len(datas)} pregões), δ e Σ os mesmos do v1 (D7/D8)",
        "- **G1** = mediana |Δ do sinal em k pregões| ÷ 1 centavo. Num binário "
        "o sinal É a probabilidade, então o tick é o centavo",
        "- **G2** = μ do `tatica_drift_anuncio.estimate_drift_mu` contra o "
        "sinal DECLARADO. **k é lookback**, não prazo de posição: a sleeve é "
        f"reassinada todo dia (janela do event-study = {JANELA})",
        "- **G3** = correlação com o sinal que as quatro views vivas já leem\n",
        "⚠️ **O G0 está na tabela de propósito.** Nos mercados de notícia ele é "
        "o critério mordaz, não a formalidade: dispersão e cobertura andam em "
        "direções opostas no dado entregue.\n",
        tabela.to_markdown(index=False), "",
        "## Premissa declarada ANTES de medir\n",
        "Herdadas **por referência** do `gate_event_driven.py` — o mesmo "
        "dicionário, não uma cópia. A 3.2 e a notícia julgam a mesma tese em "
        "cada mercado; o que muda entre os dois artefatos é só o gatilho.\n",
    ]
    for nome in mercados:
        texto.append(f"- **{nome}** — {PREMISSAS[nome][1]}")
    texto.append("")
    texto.append("## Leitura\n")

    # (a) a tensão G0 × G1, gerada dos números
    por_mercado = {}
    for nome in mercados:
        ks = [k for k in HORIZONTES if (nome, k) in medidas]
        melhor = max(ks, key=lambda k: medidas[(nome, k)]["razao"]
                     if np.isfinite(medidas[(nome, k)]["razao"]) else -1)
        por_mercado[nome] = (medidas[(nome, HORIZONTES[0])]["dias"],
                             medidas[(nome, melhor)]["razao"], melhor)
    ordenado = sorted(por_mercado.items(), key=lambda kv: -kv[1][1])
    texto.append(
        "**Cobertura × dispersão, mercado a mercado** (dias em k = 1 · melhor "
        "G1 da grade): "
        + " · ".join(f"**{m}** {d} dias, {r:.1f}× em k = {k}"
                     for m, (d, r, k) in ordenado)
        + ". O de maior dispersão é "
        + f"**{ordenado[0][0]}**, com **{ordenado[0][1][0]} pregões** de "
        "cobertura. Sleeve precisa das duas coisas ao mesmo tempo, e no dado "
        "entregue elas quase não coexistem.\n")

    # (b) G2
    passam = sorted({m for m, _k in
                     [(m, k) for (m, k), v in medidas.items() if v["ok"]]})
    if not passam:
        texto.append(
            "**Nenhum mercado passa no G2 em nenhum lookback da grade.** O μ "
            "sai contra a premissa declarada em toda a tabela, e pela D2b não "
            "se inverte.\n")
    else:
        detalhe = []
        for nome in passam:
            ks = [f"k = {k}" for k in HORIZONTES
                  if medidas.get((nome, k), {}).get("ok")]
            detalhe.append(f"**{nome}** ({', '.join(ks)})")
        texto.append(
            f"**{len(passam)} de {len(mercados)} mercados passam no G2 em pelo "
            "menos um lookback:** " + " · ".join(detalhe)
            + ". Passar no G2 **não é aprovação** — o gate mede, e o destino é "
            "decisão do dono.\n")

    # (c) o cruzamento que importa: quem passa G1 E G2 ao mesmo tempo
    if aprovados:
        texto.append(
            "**Quem passa G1 e G2 ao mesmo tempo** (o G1 acima de 1× e o μ na "
            "direção declarada): "
            + " · ".join(
                f"**{m}** em k = {k} (G1 {medidas[(m, k)]['razao']:.1f}×, "
                f"{medidas[(m, k)]['dias']} dias, G3 "
                + (f"{medidas[(m, k)]['corr']:+.2f}"
                   if np.isfinite(medidas[(m, k)]['corr']) else "não mensurável")
                + ")" for m, k in sorted(aprovados))
            + ".\n")
        # Um G2 que passa na amostra inteira e troca de sinal no meio é a
        # média de dois regimes. A D19c derrubou a 3.1 exatamente assim, e no
        # mesmo mercado — então este teste vem ANTES de qualquer comemoração.
        texto.append("### As aprovações sobrevivem às duas metades da amostra?\n")
        texto.append(
            "A **D19c** derrubou a view 3.1 direcional partindo a amostra do "
            "mercado de recessão em duas: +0,97% (t +6,52) na 1ª metade, "
            "**−0,35% (t −2,27)** na 2ª. Como não há segundo mercado de "
            "recessão, partir a amostra é o único teste fora da amostra que "
            "existe. Mesmo teste, aplicado a cada aprovação:\n")
        estaveis = []
        for m, k in sorted(aprovados):
            metades = estabilidade(retornos, medidas[(m, k)]["sinal"],
                                   medidas[(m, k)]["declarado"], sigma, ate)
            ambas = all(ok for _r, ok, _d, _n in metades)
            estaveis.append(((m, k), ambas))
            partes = " · ".join(
                f"{r}: `{d}` ({'✅' if ok else '❌'}, n = {n})"
                for r, ok, d, n in metades)
            texto.append(
                f"- **{m}**, k = {k} — {partes}. "
                + ("**Sobrevive nas duas metades.**" if ambas else
                   "🛑 **NÃO sobrevive** — o veredito da amostra inteira é a "
                   "média de dois regimes, não um sinal."))
        texto.append("")
        sobreviventes = [par for par, ok in estaveis if ok]
        texto.append(
            f"**{len(sobreviventes)} de {len(aprovados)}** aprovações "
            "sobrevivem ao corte da amostra"
            + (": " + " · ".join(f"**{m}** k = {k}" for m, k in sobreviventes)
               if sobreviventes else
               ". Nenhuma passa a ser candidata de fato: a estabilidade é "
               "condição da tese, não refinamento") + ".\n")

        # Cada aprovação sai acompanhada do que já se mediu contra o mercado.
        # Registro que envelhece não levanta exceção — quarta ocorrência na D26.
        vistos = {m for m, _k in aprovados if m in PRECEDENTES}
        if vistos:
            texto.append("⚠️ **O que o projeto já mediu sobre esses mercados, "
                         "em outra camada:**\n")
            for nome in sorted(vistos):
                texto.append(f"- **{nome}** — {PRECEDENTES[nome]}.")
            texto.append("")
    else:
        texto.append(
            "**Nenhum par (mercado, lookback) passa G1 e G2 ao mesmo tempo.** "
            "Onde há dispersão o μ não bate; onde o μ bate, o sinal está dentro "
            "do tick. Os dois critérios não se encontram no dado entregue.\n")

    if sem_serie:
        texto.append("**Sem série utilizável:** " + " · ".join(sem_serie) + ".\n")

    texto.append(
        "**O que trava esta candidata, e não é nenhum veredito acima:** o "
        "**pedido de dado**. Mercados de evento com fluxo de notícia têm "
        "dispersão de sobra e duram poucos pregões; o que dura um ano é "
        "pergunta permanente e não se mexe. O pedido ao Paulo é *mais mercados "
        "de evento com notícia*, não mais histórico dos mesmos — nenhum "
        "horizonte desta grade conserta um mercado de 9 pregões.\n")

    texto.append(
        "⚠️ **A D24 pega esta candidata em cheio** e continua 🔴: o portão de "
        "qualidade do poly vale para views e **não** para overlays. Mercado de "
        "notícia curto é exatamente o de PMF degenerada — uma sleeve aqui "
        "passaria livre pelo veto que mata a view equivalente.\n")

    texto.append(
        "**O que isto NÃO diz:** nada sobre P&L (G4 exige backtest, backtest "
        "exige o módulo que este protocolo se recusa a escrever antes de a "
        "linha passar), e nada sobre o gatilho de SALTO nesses mesmos "
        "mercados — isso está em `Gate_event_driven.md`.\n")

    Path(args.saida).write_text("\n".join(texto) + "\n", encoding="utf-8")
    sys.stdout.write(tabela.to_string(index=False) + f"\n\nescrito: {args.saida}\n")


if __name__ == "__main__":
    main()
