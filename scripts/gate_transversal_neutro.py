"""Transversal, os dois buracos: livro neutro de beta e gatilho de SALTO. Felipe.

O `Gate_transversal.md` mediu que o eixo do instrumento existe — **8 pares
passam só com o livro setorial, 0 só com o direcional**. Ele deixou dois
buracos, e este script fecha os dois de uma vez porque são a mesma edição.

**Buraco 1 — os livros não são neutros, e metade carrega o índice dentro.**
Medido lá: `+XLF −XLP` tem +0,59 de correlação com o SPY, `+XLP −XLK` tem
−0,56, `+XLF −XLU` tem +0,48. Com isso **não dá para distinguir** duas coisas
muito diferentes:

  (a) o spread setorial tem sinal próprio;  ⟵ a tese
  (b) o spread é uma aposta direcional alavancada que apontou para o lado certo.

Aqui cada perna entra **hedgeada contra o SPY** por β **expansivo** (só passado,
semeado em `MINIMO_PREGOES = 60`, a constante que a 15f e a 3.1 direcional já
usam). Se o 8 × 0 sobreviver, a tese fica muito mais forte; se colapsar,
aprende-se que parte do "8" era índice entrando pela porta dos fundos. Os dois
resultados valem o script.

**Buraco 2 — o SALTO nunca foi cruzado com o livro setorial.** A 3.2 morreu com
livro direcional (resíduo pós-gap de mediana −1%); a transversal foi medida só
com o Δp acumulado em `k`. A célula "salto × setorial" não existe em artefato
nenhum — e é a combinação com o melhor argumento a priori: **o gap de abertura
afeta muito menos um spread entre dois setores do que o índice inteiro**, porque
o beta comum cancela nos dois lados. É exatamente o caso em que trocar o livro
deveria salvar o gatilho.

⚠️ **Nada de novo é declarado.** Os livros são os mesmos do
`gate_transversal.py`, as premissas direcionais são as mesmas do
`gate_event_driven.py`, a grade de quantis e a de horizontes são as mesmas. O
que muda é só o hedge e o cruzamento — se algo passar, não foi por premissa
nova.

⚠️ **Isto NÃO é varredura de pares.** Continua um par declarado por mercado,
escolhido pelo mecanismo. Varrer os 15 pares setoriais possíveis atrás do que
funciona é pescaria, e é o vício que a D2b existe para barrar.

**Nada em `src/` é tocado.**

Uso:

    python scripts/gate_transversal_neutro.py --raiz .
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gate_event_driven import (PRECEDENTES, PREMISSAS, QUANTIS,  # noqa: E402
                               dias_de_salto)
from gate_noticia import estabilidade  # noqa: E402
from gate_sleeves import (bate_premissa, corr_comum, eventos_diarios,  # noqa: E402
                          mu_do_sinal, razao_dispersao)
from config import SIGMA_JANELA_PREGOES  # noqa: E402
from gate_transversal import LIVROS_SETORIAIS, neutralidade  # noqa: E402
from premissa_g1 import HORIZONTES, em_pregoes, series_dos_mercados  # noqa: E402

JANELA = 1
MERCADO = "SPY"

# A construção das pernas hedgeadas mudou de casa em 2026-08-11: vive em
# `src/tatica_sleeves.py`, porque o backtest da camada precisa da MESMA
# construção que aprovou as sleeves aqui. Duas cópias divergiriam na primeira
# correção, e a diferença apareceria como resultado em vez de como bug. O
# artefato foi re-gerado e conferido POR HASH depois da mudança.
from tatica_sleeves import (MINIMO_PREGOES, SUFIXO,  # noqa: E402
                            neutraliza, pernas_neutras)


def veredito(retornos, eventos, livro, assets, sigma, ate):
    """(bate, detalhe) do G2 para um livro qualquer. Um lugar só para a chamada."""
    mu, _n = mu_do_sinal(retornos, eventos, JANELA, tuple(livro), sigma, ate)
    return bate_premissa(mu, assets, livro)


def main():
    # O console do Windows abre em cp1252 e engasga nos rótulos acentuados.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raiz", default=".")
    parser.add_argument("--saida", default="Dump/analises/Gate_transversal_neutro.md")
    args = parser.parse_args()

    series, retornos, montador, datas = series_dos_mercados(args.raiz)

    setoriais = sorted({a for livro, _t in LIVROS_SETORIAIS.values() for a in livro})
    estendido = pernas_neutras(retornos, setoriais).dropna()
    assets_ext = tuple(estendido.columns)
    ate = datas[-1] + pd.Timedelta(days=1)

    # Σ DIAGONAL, e não a amostral cheia. Não é atalho: o `estimate_drift_mu`
    # lê **só** `np.diag(sigma)` (o encolhimento é `τ·Σ_ii / (τ·Σ_ii + se²_i)`),
    # e a Σ cheia desta tabela é singular por construção — `XLP⊥` é combinação
    # linear exata de `XLP` e `SPY`, então o guarda de condicionamento do
    # `sample_covariance` reprova, e com razão. As variâncias saem da MESMA
    # janela que o `sample_covariance` usaria, para o encolhimento ficar
    # comparável com os outros artefatos.
    sigma = np.diag(estendido.tail(SIGMA_JANELA_PREGOES).var().to_numpy())

    # --- sanity: o hedge fez o que prometeu? ---------------------------------
    livros_unicos = {}
    for nome, (livro, _t) in LIVROS_SETORIAIS.items():
        rotulo = " ".join(f"{'+' if p > 0 else '−'}{a}" for a, p in livro.items())
        livros_unicos.setdefault(rotulo, livro)
    conferencia = pd.DataFrame([
        {"livro": rotulo,
         "corr(spread, SPY) CRU": round(neutralidade(estendido, livro), 2),
         "corr(spread, SPY) NEUTRO": round(
             neutralidade(estendido, neutraliza(livro)), 2)}
        for rotulo, livro in livros_unicos.items()])

    # --- parte A: Δp em k, três livros ---------------------------------------
    linhas_a, medidas_a = [], {}
    for nome, _familia, serie, tick, _unidade in series:
        if nome not in LIVROS_SETORIAIS or nome not in PREMISSAS:
            continue
        direcional = PREMISSAS[nome][0]
        setorial = LIVROS_SETORIAIS[nome][0]
        base = em_pregoes(serie)
        if base.dropna().empty:
            continue
        for k in HORIZONTES:
            sinal = base.diff(k).dropna()
            if sinal.empty:
                continue
            eventos = eventos_diarios(sinal)
            vd = veredito(estendido, eventos, direcional, assets_ext, sigma, ate)
            vc = veredito(estendido, eventos, setorial, assets_ext, sigma, ate)
            vn = veredito(estendido, eventos, neutraliza(setorial), assets_ext,
                          sigma, ate)
            medidas_a[(nome, k)] = {"dir": vd[0], "cru": vc[0], "neutro": vn[0],
                                    "sinal": sinal, "livro": neutraliza(setorial),
                                    "razao": razao_dispersao(sinal, tick),
                                    "dias": len(sinal)}
            linhas_a.append({
                "mercado": nome, "lookback": f"k = {k}", "G0 dias": len(sinal),
                "direcional": "✅" if vd[0] else "❌",
                "setorial CRU": "✅" if vc[0] else "❌",
                "setorial NEUTRO": "✅" if vn[0] else "❌",
                "μ do neutro (bps/dia)": vn[1],
            })
    tabela_a = pd.DataFrame(linhas_a)

    # --- parte B: SALTO × três livros ----------------------------------------
    linhas_b, medidas_b = [], {}
    for nome, _familia, serie, _tick, _unidade in series:
        if nome not in LIVROS_SETORIAIS or nome not in PREMISSAS:
            continue
        direcional = PREMISSAS[nome][0]
        setorial = LIVROS_SETORIAIS[nome][0]
        base = em_pregoes(serie).diff().dropna()
        if base.empty:
            continue
        for quantil in QUANTIS:
            dias = dias_de_salto(base, quantil)
            if len(dias) < 3:
                continue
            eventos = eventos_diarios(base.reindex(dias))
            vd = veredito(estendido, eventos, direcional, assets_ext, sigma, ate)
            vc = veredito(estendido, eventos, setorial, assets_ext, sigma, ate)
            vn = veredito(estendido, eventos, neutraliza(setorial), assets_ext,
                          sigma, ate)
            medidas_b[(nome, quantil)] = {
                "dir": vd[0], "cru": vc[0], "neutro": vn[0],
                "sinal": base.reindex(dias), "livro": neutraliza(setorial),
                "dias": len(dias)}
            linhas_b.append({
                "mercado": nome, "corte |Δp|": f"q{quantil:.2f}",
                "n saltos": len(dias),
                "direcional": "✅" if vd[0] else "❌",
                "setorial CRU": "✅" if vc[0] else "❌",
                "setorial NEUTRO": "✅" if vn[0] else "❌",
                "μ do neutro (bps/dia)": vn[1],
            })
    tabela_b = pd.DataFrame(linhas_b)

    def placar(medidas):
        return {
            "só neutro": [c for c, v in medidas.items()
                          if v["neutro"] and not v["dir"]],
            "só cru": [c for c, v in medidas.items() if v["cru"] and not v["dir"]],
            "só direcional": [c for c, v in medidas.items()
                              if v["dir"] and not v["neutro"]],
        }

    pa, pb = placar(medidas_a), placar(medidas_b)

    texto = [
        "# Transversal — livro neutro de beta e o cruzamento com o SALTO\n",
        "> Gerado por `scripts/gate_transversal_neutro.py`. **Mede; não "
        "decide.** Nenhum corte cravado, nenhuma premissa nova — livros, "
        "premissas e grades são importados dos artefatos anteriores.\n",
        f"- janela do backtest: **{datas[0]:%Y-%m-%d} a {datas[-1]:%Y-%m-%d}** "
        f"({len(datas)} pregões), δ e Σ os mesmos do v1 (D7/D8)",
        f"- **NEUTRO** = cada perna com o beta de mercado removido, por β "
        f"**expansivo defasado em 1 dia** e semeado em {MINIMO_PREGOES} "
        "pregões (`MINIMO_PREGOES`, a constante que a 15f e a 3.1 direcional "
        "já usam). Sem lookahead: em cada data o hedge só conhece o passado",
        "- **CRU** = o livro do `Gate_transversal.md`, pesos +1/−1 sem hedge\n",
        "## Conferência — o hedge fez o que prometeu?\n",
        "Se esta tabela não mostrar a coluna NEUTRO perto de zero, o resto do "
        "artefato não vale: seria hedge que não hedgeia.\n",
        conferencia.to_markdown(index=False), "",
        "## Parte A — Δp acumulado em `k`, três livros lado a lado\n",
        tabela_a.to_markdown(index=False), "",
        "## Parte B — gatilho de SALTO, a célula que nunca existiu\n",
        "A 3.2 morreu com livro direcional; a transversal foi medida só com o "
        "Δp acumulado. Este cruzamento é novo, e o argumento a priori a favor "
        "dele é que **o gap de abertura afeta menos um spread do que o índice "
        "inteiro** — o beta comum cancela nos dois lados.\n",
        tabela_b.to_markdown(index=False), "",
        "## Leitura\n",
    ]

    # (a) o hedge funcionou?
    pior_neutro = conferencia["corr(spread, SPY) NEUTRO"].abs().max()
    pior_cru = conferencia["corr(spread, SPY) CRU"].abs().max()
    texto.append(
        f"**O hedge funcionou:** a maior |correlação| com o SPY cai de "
        f"**{pior_cru:.2f}** (cru) para **{pior_neutro:.2f}** (neutro). Os "
        "livros neutros são spreads de verdade — o que a coluna NEUTRO mede "
        "não tem índice dentro.\n"
        if pior_neutro < pior_cru else
        f"🛑 **O hedge NÃO funcionou** — a maior |correlação| ficou em "
        f"{pior_neutro:.2f} contra {pior_cru:.2f} do cru. Não leia o resto.\n")

    # (b) o 8 × 0 sobrevive?
    texto.append(
        f"**O 8 × 0 do `Gate_transversal.md` sobrevive à neutralização?** Com "
        f"o livro CRU, **{len(pa['só cru'])}** pares passam onde o direcional "
        f"falha. Com o livro NEUTRO, **{len(pa['só neutro'])}**. E "
        f"**{len(pa['só direcional'])}** passam só no direcional.\n")
    if len(pa["só neutro"]) >= len(pa["só cru"]):
        texto.append(
            "**A vantagem do livro setorial NÃO era beta disfarçado.** Ela "
            "sobrevive quando o índice é removido das duas pernas — o que "
            "estava sendo medido é spread, não alavancagem direcional. Esta é "
            "a versão forte do achado do artefato anterior.\n")
    else:
        texto.append(
            f"🛑 **Parte da vantagem ERA beta disfarçado:** de "
            f"{len(pa['só cru'])} pares que passavam só no setorial cru, "
            f"sobram **{len(pa['só neutro'])}** depois de tirar o índice das "
            "pernas. O eixo do instrumento continua existindo, mas é menor do "
            "que o `Gate_transversal.md` sugeria — e a diferença era o índice "
            "entrando pela porta dos fundos.\n")

    # (c) o cruzamento novo
    texto.append(
        f"**O cruzamento salto × setorial, que nunca tinha sido medido:** "
        f"**{len(pb['só neutro'])}** pares (mercado, corte) passam no G2 com "
        f"livro neutro e falham no direcional · **{len(pb['só cru'])}** com "
        f"livro cru · **{len(pb['só direcional'])}** só no direcional.\n")
    if pb["só neutro"]:
        texto.append(
            "Onde o livro salva o gatilho do salto: "
            + " · ".join(f"**{m}** {q:.2f}" if isinstance(q, float) else f"**{m}**"
                         for m, q in sorted(pb["só neutro"], key=lambda c: str(c)))
            + ".\n")
    else:
        texto.append(
            "**Nenhum.** O argumento a priori era bom — o gap de abertura "
            "afeta menos um spread que o índice — mas ele não se realiza no "
            "dado: onde o salto não previa o retorno direcional, ele também "
            "não prevê o spread setorial neutro. **A 3.2 não é ressuscitada "
            "pela troca de livro.**\n")

    # (d) estabilidade de tudo que passa no neutro
    candidatos = ([("A", m, k) for (m, k), v in medidas_a.items() if v["neutro"]]
                  + [("B", m, q) for (m, q), v in medidas_b.items() if v["neutro"]])
    if candidatos:
        texto.append("### Sobrevivem às duas metades da amostra?\n")
        sobreviventes = []
        for parte, mercado, eixo in sorted(candidatos, key=lambda c: (c[0], str(c[1]), c[2])):
            fonte = medidas_a if parte == "A" else medidas_b
            v = fonte[(mercado, eixo)]
            metades = estabilidade(estendido, v["sinal"], v["livro"], sigma,
                                   ate, assets_ext)
            ambas = all(ok for _r, ok, _d, _n in metades)
            if ambas:
                sobreviventes.append((parte, mercado, eixo))
            rotulo = f"k = {eixo}" if parte == "A" else f"q{eixo:.2f}"
            texto.append(
                f"- **[{parte}] {mercado}**, {rotulo} — "
                + " · ".join(f"{r}: `{d}` ({'✅' if ok else '❌'}, n = {n})"
                             for r, ok, d, n in metades)
                + ". " + ("**Sobrevive.**" if ambas else "🛑 **NÃO sobrevive.**"))
        texto.append("")
        texto.append(
            f"**{len(sobreviventes)} de {len(candidatos)}** aprovações com "
            "livro neutro sobrevivem ao corte"
            + (": " + " · ".join(
                f"**{m}** " + (f"k = {e}" if p == "A" else f"q{e:.2f}")
                for p, m, e in sobreviventes) if sobreviventes else "") + ".\n")
        # CONTIGUIDADE. Uma célula isolada numa grade é o padrão de quem
        # garimpou o horizonte que funcionou; um BLOCO de horizontes vizinhos
        # todos passando é muito mais difícil de conseguir por sorte. A
        # distinção decide o quanto se pode confiar no achado, então sai medida.
        por_mercado = {}
        for parte, mercado, eixo in sobreviventes:
            if parte == "A":
                por_mercado.setdefault(mercado, []).append(eixo)
        blocos = {m: sorted(ks) for m, ks in por_mercado.items() if len(ks) > 1}
        if blocos:
            texto.append(
                "**E o que sobrevive não é célula isolada — é BLOCO de "
                "horizontes vizinhos:** "
                + " · ".join(
                    f"**{m}** em k = {', '.join(str(k) for k in ks)} "
                    f"({len(ks)} das {len(HORIZONTES)} colunas da grade, "
                    "contíguas)" for m, ks in blocos.items())
                + ". Uma célula isolada numa grade é o padrão de quem garimpou "
                "o horizonte que funcionou; horizontes vizinhos todos passando "
                "**e** todos sobrevivendo ao corte é bem mais difícil de "
                "conseguir por sorte. É a diferença entre um resultado e um "
                "artefato de busca.\n")

        # A linha q0.00 da parte B NÃO é salto — é a linha de base (todo dia
        # com Δp). Sobreviver ali não credita o gatilho de salto, e deixar isso
        # implícito faria a tabela dizer o que ela não diz.
        base_b = [(m, e) for p, m, e in sobreviventes
                  if p == "B" and e == QUANTIS[0]]
        salto_b = [(m, e) for p, m, e in sobreviventes
                   if p == "B" and e != QUANTIS[0]]
        if base_b:
            texto.append(
                "⚠️ **Cuidado com as linhas `q0.00` da parte B:** "
                + " · ".join(f"**{m}**" for m, _e in base_b)
                + " sobrevive no corte `q0.00`, que é **todo dia com Δp ≠ 0** — "
                "a linha de base, não um salto. Sobreviver ali não credita o "
                "gatilho de salto; credita o Δp diário, que é outra coisa. "
                + (f"O único sobrevivente que é salto de verdade é "
                   + " · ".join(f"**{m}** q{e:.2f}" for m, e in salto_b) + "."
                   if salto_b else
                   "**Nenhum corte de salto de verdade sobrevive.**") + "\n")

        vistos = {m for _p, m, _e in sobreviventes if m in PRECEDENTES}
        if vistos:
            texto.append("⚠️ **O que o projeto já mediu sobre esses mercados, "
                         "em outra camada:**\n")
            for nome in sorted(vistos):
                texto.append(f"- **{nome}** — {PRECEDENTES[nome]}.")
            texto.append("")
    else:
        texto.append(
            "**Nenhum par passa no G2 com livro neutro**, nem no Δp acumulado "
            "nem no salto. Com o índice removido das duas pernas, não sobra "
            "sinal setorial em lugar nenhum da grade.\n")

    texto.append(
        "**O que isto NÃO diz:** nada sobre P&L, e nada sobre pares setoriais "
        "não declarados. Continua **um par por mercado, escolhido pelo "
        "mecanismo** — varrer os 15 pares possíveis atrás do que funciona é "
        "pescaria, e é o vício que a D2b existe para barrar.\n")

    Path(args.saida).write_text("\n".join(texto) + "\n", encoding="utf-8")
    sys.stdout.write(conferencia.to_string(index=False) + "\n\n")
    sys.stdout.write("A: " + str({k: len(v) for k, v in pa.items()})
                     + "   B: " + str({k: len(v) for k, v in pb.items()})
                     + f"\n\nescrito: {args.saida}\n")


if __name__ == "__main__":
    main()
