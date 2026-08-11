"""Transversal — o livro estava errado, ou o gatilho? Felipe.

Todas as 13 sleeves do projeto e as quatro candidatas do `Candidatos_taticos.md`
operam **SPY/TLT direcional**: os instrumentos mais eficientes do universo, e os
mesmos que as views já tiltam. O eixo do **instrumento** nunca foi variável.

Isto não é um quinto gatilho. É a mesma leitura do poly expressa num **livro
long/short setorial**, e existe por uma razão que nenhum teste derrubou: um
livro transversal **sobrevive ao poly estar certo**. Toda tática direcional
precisa que o poly esteja errado (D16: surpresa mediana de 0,52 bps em 17
reuniões) ou atrasado (D26: VR ≈ 1, ρ ex-ante ≈ 0), e as duas premissas estão
medidas contra. Um spread entre setores não pede que o Fed surpreenda — pede
que os setores respondam de forma diferente ao mesmo choque.

Este script roda o MESMO sinal, na MESMA grade de horizontes, trocando só o
livro, e põe os dois vereditos lado a lado. Assim a pergunta "o livro estava
errado?" fica separada de "o gatilho estava errado?" — que é a única coisa que
as 13 tentativas anteriores não conseguem responder.

⚠️ **Evidência adversa, declarada antes de medir:** a **15f** e a **19b** já
reprovaram uma transversal. **Não é a mesma coisa, e o registro precisa dizer
por quê:** as duas eram *view estrutural* de inflação, com o P montado a partir
de β contra breakeven, e o elo que falhou lá foi o **transporte** β → retorno
(a corr entre coeficiente preditivo e β contemporâneo foi a −0,84). Aqui não há
β nenhum: o livro é declarado a priori e o que se mede é se o spread anda na
direção declarada. Herdar o veredito da 15f sem reescrever a premissa seria a
armadilha que a D26 registra.

⚠️ **Os livros setoriais são declarados ANTES de medir**, em `LIVROS_SETORIAIS`,
com uma perna de cada lado e mapeamento de manual. Nenhum é otimizado, nenhum
sai de varredura.

**Nada em `src/` é tocado.**

Uso:

    python scripts/gate_transversal.py --raiz .
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
from gate_noticia import estabilidade  # noqa: E402
from gate_sleeves import (COL_G3, bate_premissa, corr_comum,  # noqa: E402
                          eventos_diarios, mu_do_sinal, razao_dispersao,
                          referencias_g3)
from market_inputs import sample_covariance  # noqa: E402
from premissa_g1 import HORIZONTES, em_pregoes, series_dos_mercados  # noqa: E402

JANELA = 1

# Livro long/short DECLARADO por mercado: para que lado cada setor anda quando
# o sinal do mercado SOBE. Uma perna de cada lado, mapeamento de manual, e o
# par escolhido pelo mecanismo — não pelo resultado.
LIVROS_SETORIAIS = {
    "C1a M3 trajetória do Fed (nº de cortes)": (
        {"XLK": +1, "XLF": -1},
        "mais afrouxamento → equity de duração longa (XLK) bate banco (XLF), "
        "cuja margem de juros comprime"),
    "C1b reunião do FOMC (E_poly em bps)": (
        {"XLK": -1, "XLF": +1},
        "idem, invertido: E_poly é Δtaxa, então subir é apertar"),
    "CPI mensal (E_poly)": (
        {"XLE": +1, "XLK": -1},
        "surpresa inflacionária → energia (XLE) bate duração longa (XLK)"),
    "M4 recessão EUA 2025": (
        {"XLP": +1, "XLK": -1},
        "p(recessão) sobe → defensivo (XLP) bate cíclico (XLK)"),
    "M5 Trump 2024": (
        {"XLF": +1, "XLP": -1},
        "\"Trump trade\": desregulação financeira (XLF) bate defensivo (XLP)"),
    "M6 tarifas China": (
        {"XLP": +1, "XLK": -1},
        "p(tarifa) sobe → risco-off: defensivo bate cíclico"),
    "M7 ação militar Irã (jun/2025)": (
        {"XLE": +1, "XLK": -1},
        "p(ação militar) sobe → petróleo (XLE) bate cíclico (XLK)"),
    "M7 ataque ao Irã (fev/2026)": (
        {"XLE": +1, "XLK": -1},
        "idem, segundo episódio"),
    "M8 reconciliação fiscal": (
        {"XLF": +1, "XLU": -1},
        "p(aprovação) sobe → mais emissão: o proxy de bond (XLU) sofre e o "
        "financeiro (XLF) ganha"),
    "M9 Câmara": (
        {"XLP": +1, "XLK": -1},
        "mecanismo partidário, espelho do M5. ⚠️ é o mecanismo que a 2.4 mediu "
        "como NÃO reproduzindo fora da amostra"),
}


def neutralidade(retornos, livro):
    """Correlação do retorno do spread com o do SPY.

    É a medida honesta da alegação "ortogonal por construção": um livro
    long/short de setores só é ortogonal a quem tilta o índice se o spread não
    for o índice disfarçado. Pelo precedente **D22e**, contra P direcional o
    ângulo é 90° tautológico e o item 4 se decide só pelo ρ — este é o ρ que
    interessa para um livro, e ele é medido, não afirmado.
    """
    spread = sum(peso * retornos[ativo] for ativo, peso in livro.items())
    return corr_comum(spread, retornos["SPY"])


def main():
    # O console do Windows abre em cp1252 e engasga nos rótulos acentuados.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raiz", default=".")
    parser.add_argument("--saida", default="Dump/analises/Gate_transversal.md")
    args = parser.parse_args()

    series, retornos, montador, datas = series_dos_mercados(args.raiz)
    sigma = sample_covariance(retornos)
    ate = datas[-1] + pd.Timedelta(days=1)
    referencias = referencias_g3(montador, datas, montador._fl)

    linhas, medidas = [], {}
    for nome, _familia, serie, tick, _unidade in series:
        if nome not in LIVROS_SETORIAIS or nome not in PREMISSAS:
            continue
        direcional, _t1 = PREMISSAS[nome]
        setorial, _t2 = LIVROS_SETORIAIS[nome]
        base = em_pregoes(serie)
        if base.dropna().empty:
            continue
        for k in HORIZONTES:
            sinal = base.diff(k).dropna()
            if sinal.empty:
                continue
            eventos = eventos_diarios(sinal)
            resultado = {}
            for rotulo, livro in (("direcional", direcional),
                                  ("setorial", setorial)):
                mu, n_mu = mu_do_sinal(retornos, eventos, JANELA, tuple(livro),
                                       sigma, ate)
                ok, detalhe = bate_premissa(mu, ASSETS, livro)
                resultado[rotulo] = (ok, detalhe, n_mu)
            correlacoes = {c: corr_comum(sinal, ref)
                           for c, ref in referencias.items()}
            finitas = {c: v for c, v in correlacoes.items() if np.isfinite(v)}
            pior = max(finitas, key=lambda c: abs(finitas[c])) if finitas else None
            razao = razao_dispersao(sinal, tick)
            medidas[(nome, k)] = {"setorial_ok": resultado["setorial"][0],
                                  "direcional_ok": resultado["direcional"][0],
                                  "razao": razao, "sinal": sinal,
                                  "livro": setorial, "dias": len(sinal),
                                  "corr": finitas.get(pior, float("nan")),
                                  "pior": pior}
            linhas.append({
                "mercado": nome,
                "lookback": f"k = {k}",
                "G0 dias": len(sinal),
                "G1 razão / tick": f"{razao:.1f}×" if np.isfinite(razao) else "—",
                "livro DIRECIONAL": resultado["direcional"][1],
                "bate?": "✅" if resultado["direcional"][0] else "❌",
                "livro SETORIAL": resultado["setorial"][1],
                "bate? ": "✅" if resultado["setorial"][0] else "❌",
                COL_G3: (f"{finitas[pior]:+.2f}" if pior else "—"),
            })

    tabela = pd.DataFrame(linhas)
    mercados = list(dict.fromkeys(tabela["mercado"]))

    neutro = pd.DataFrame([
        {"mercado": nome,
         "livro": " ".join(f"{'+' if p > 0 else '−'}{a}"
                           for a, p in LIVROS_SETORIAIS[nome][0].items()),
         "corr(spread, SPY)": round(neutralidade(retornos,
                                                 LIVROS_SETORIAIS[nome][0]), 2)}
        for nome in mercados])

    so_setorial = [(m, k) for (m, k), v in medidas.items()
                   if v["setorial_ok"] and not v["direcional_ok"]]
    so_direcional = [(m, k) for (m, k), v in medidas.items()
                     if v["direcional_ok"] and not v["setorial_ok"]]
    ambos = [(m, k) for (m, k), v in medidas.items()
             if v["setorial_ok"] and v["direcional_ok"]]
    aprovados = [(m, k) for (m, k), v in medidas.items()
                 if v["setorial_ok"] and np.isfinite(v["razao"]) and v["razao"] > 1.0]

    texto = [
        "# Transversal — o livro estava errado, ou o gatilho?\n",
        "> Gerado por `scripts/gate_transversal.py`. **Mede; não decide.** "
        "Nenhum corte cravado, mesma regra do `Gate_sleeves.md`.\n",
        f"- janela do backtest: **{datas[0]:%Y-%m-%d} a {datas[-1]:%Y-%m-%d}** "
        f"({len(datas)} pregões), δ e Σ os mesmos do v1 (D7/D8)",
        "- **mesmo sinal, mesma grade, mesma janela de event-study** nas duas "
        "colunas de livro. A ÚNICA coisa que muda é em que ativos a premissa "
        "se expressa — é o que separa \"o livro estava errado\" de \"o gatilho "
        "estava errado\"",
        "- **G3** é idêntico nos dois livros **por construção**: o sinal-fonte "
        "é o mesmo, e correlação de sinal não sabe em que ativo a sleeve "
        "opera. O ganho de ortogonalidade de um livro transversal está no P, e "
        "está medido na tabela de neutralidade abaixo\n",
        tabela.to_markdown(index=False), "",
        "## Livro setorial declarado ANTES de medir\n",
        "Uma perna de cada lado, mapeamento de manual, par escolhido pelo "
        "mecanismo. Nenhum otimizado, nenhum saído de varredura.\n",
    ]
    for nome in mercados:
        texto.append(f"- **{nome}** — {LIVROS_SETORIAIS[nome][1]}")
    texto += [
        "",
        "## Neutralidade — o spread é o índice disfarçado?\n",
        "A alegação de que um livro long/short é \"ortogonal por construção\" a "
        "quem tilta o índice só vale se o spread não carregar o índice dentro. "
        "Medido, não afirmado — e é o ρ que o precedente **D22e** manda usar "
        "quando o ângulo é tautológico.\n",
        neutro.to_markdown(index=False), "",
        "## Leitura\n",
    ]

    # (a) a pergunta do artefato, respondida pela contagem
    texto.append(
        f"**A pergunta era \"o livro estava errado?\". A resposta é a contagem "
        f"de células que mudam de veredito ao trocar SÓ o livro:** "
        f"**{len(so_setorial)}** pares (mercado, k) passam no G2 **só** com o "
        f"livro setorial · **{len(so_direcional)}** passam só com o direcional "
        f"· **{len(ambos)}** passam nos dois · "
        f"**{len(medidas) - len(so_setorial) - len(so_direcional) - len(ambos)}** "
        "não passam em nenhum.\n")

    if so_setorial:
        texto.append(
            "**Onde o livro era o problema** (o gatilho serve, o SPY/TLT é que "
            "não expressava): "
            + " · ".join(f"**{m}** k = {k} (G1 "
                         + (f"{medidas[(m, k)]['razao']:.1f}×"
                            if np.isfinite(medidas[(m, k)]['razao']) else "—")
                         + f", {medidas[(m, k)]['dias']} dias)"
                         for m, k in sorted(so_setorial))
            + ".\n")
    else:
        texto.append(
            "**Nenhum par muda de reprovado para aprovado ao trocar o livro.** "
            "Isso responde o eixo do instrumento pela negativa: **o problema "
            "não era o livro.** Onde o gatilho não previa retorno direcional, "
            "ele também não prevê o spread setorial.\n")

    # (b) neutralidade — a frase TEM de sair do número. A tese diz "ortogonal
    # por construção", e um spread que carrega meio índice dentro não é.
    # Livros distintos, não linhas: vários mercados compartilham o mesmo par.
    por_livro = neutro.drop_duplicates("livro").set_index("livro")[
        "corr(spread, SPY)"]
    maior = por_livro.abs().idxmax()
    limpos = por_livro[por_livro.abs() < 0.2]
    sujos = por_livro[por_livro.abs() >= 0.2]
    texto.append(
        "**A alegação de \"ortogonal por construção\" não vale para todo "
        "spread — vale para alguns, e a diferença é medida.** Dos "
        f"**{len(por_livro)}** livros distintos declarados, "
        f"**{len(limpos)}** ficam abaixo de |0,20| contra o SPY ("
        + " · ".join(f"`{k}` {v:+.2f}" for k, v in limpos.items())
        + f") e **{len(sujos)}** não ("
        + " · ".join(f"`{k}` {v:+.2f}" for k, v in sujos.items())
        + f"). O pior é `{maior}` com **{por_livro[maior]:+.2f}** — isso é "
        "beta disfarçado, não spread neutro. **Para esses livros a tese de "
        "ortogonalidade não se sustenta**, e ela era metade da razão de ser da "
        "transversal: não competir com as views vivas pelo mesmo risco.\n")

    # (c) estabilidade de quem passa G1 e G2 no setorial
    if aprovados:
        texto.append("### As aprovações setoriais sobrevivem às duas metades?\n")
        texto.append(
            "Mesmo teste da D19c aplicado no `gate_noticia.py`: um G2 que "
            "passa na amostra inteira e troca de sinal no meio é a média de "
            "dois regimes.\n")
        sobreviventes = []
        for m, k in sorted(aprovados):
            metades = estabilidade(retornos, medidas[(m, k)]["sinal"],
                                   medidas[(m, k)]["livro"], sigma, ate)
            ambas = all(ok for _r, ok, _d, _n in metades)
            if ambas:
                sobreviventes.append((m, k))
            texto.append(
                f"- **{m}**, k = {k} — "
                + " · ".join(f"{r}: `{d}` ({'✅' if ok else '❌'}, n = {n})"
                             for r, ok, d, n in metades)
                + ". " + ("**Sobrevive.**" if ambas else "🛑 **NÃO sobrevive.**"))
        texto.append("")
        texto.append(
            f"**{len(sobreviventes)} de {len(aprovados)}** aprovações setoriais "
            "com G1 acima do tick sobrevivem ao corte"
            + (": " + " · ".join(f"**{m}** k = {k}" for m, k in sobreviventes)
               if sobreviventes else "").rstrip() + ".\n")
        # A distinção que decide o eixo: sobreviver COM os dois livros quer
        # dizer que o gatilho é que funciona, e o instrumento não acrescenta.
        so_com_setorial = [(m, k) for m, k in sobreviventes
                           if not medidas[(m, k)]["direcional_ok"]]
        nos_dois = [(m, k) for m, k in sobreviventes
                    if medidas[(m, k)]["direcional_ok"]]
        if nos_dois:
            texto.append(
                "⚠️ **Mas cuidado com o que isso credita à transversal:** "
                + " · ".join(f"**{m}** k = {k}" for m, k in nos_dois)
                + " passa **nos dois livros**. Ali quem funciona é o "
                "**gatilho**, e o livro setorial não acrescenta nada — é a "
                "mesma informação expressa de outro jeito. A transversal só "
                "tem crédito próprio onde o direcional falha e ela passa"
                + (": " + " · ".join(f"**{m}** k = {k}" for m, k in so_com_setorial)
                   if so_com_setorial else
                   ", e **não há nenhum caso desses que sobreviva ao corte da "
                   "amostra**") + ".\n")
        vistos = {m for m, _k in aprovados if m in PRECEDENTES}
        if vistos:
            texto.append("⚠️ **O que o projeto já mediu sobre esses mercados, "
                         "em outra camada:**\n")
            for nome in sorted(vistos):
                texto.append(f"- **{nome}** — {PRECEDENTES[nome]}.")
            texto.append("")
    else:
        texto.append(
            "**Nenhum par passa G1 e G2 no livro setorial ao mesmo tempo.** "
            "Onde há dispersão acima do tick o spread não anda na direção "
            "declarada; onde ele anda, o sinal está dentro do tick.\n")

    texto.append(
        "**O que isto NÃO diz:** nada sobre P&L, e nada sobre a evidência da "
        "15f/19b. Aquelas mediram uma transversal de *view estrutural* com P "
        "montado por β contra breakeven, e o elo que falhou foi o transporte "
        "β → retorno. Este artefato não reabre nem confirma aquele veredito — "
        "mede outra coisa, com livro declarado a priori e sem β nenhum.\n")

    Path(args.saida).write_text("\n".join(texto) + "\n", encoding="utf-8")
    sys.stdout.write(tabela.to_string(index=False) + "\n\n")
    sys.stdout.write(neutro.to_string(index=False) + f"\n\nescrito: {args.saida}\n")


if __name__ == "__main__":
    main()
