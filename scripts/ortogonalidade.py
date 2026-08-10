"""Item 4 da D22 — ortogonalidade das views, e a obrigação 5a. Felipe.

**MEDE; não decide.** A D22 exige de toda view que entra "ângulo alto entre o P
dela e o das views ativas, sem ρ alto no sinal-fonte". A 15g só tinha metade do
número (o ângulo, 95,6° contra a 2.3 — o ρ nunca fora calculado) e a **15b nunca
teve nenhuma das duas**. Desde 2026-08-10 roda também a **view C (candidata)**,
uma linha por k da grade, contra as QUATRO views ativas.

Mede três coisas sobre a MESMA passada do montador do v1:

1. **Ângulo entre os P**, dia a dia, entre todos os pares de views vivas.
2. **ρ entre os sinais-fonte** — o que a D22 chama de "ρ no sinal-fonte". É a
   metade que importa na 15b: o P dela é `[SPY=2, 0…]` e o das outras sai de
   `P_from_betas`, que crava `P[SPY] = 0` EXATO. O produto interno é zero por
   construção, então o ângulo dela é 90° com qualquer view neutra — o número
   passa, mas não testa nada. Quem testa é o ρ.
3. **ΣP por view** — a obrigação 5a do docstring de `P_from_betas`: `P[SPY] = 0`
   é exato, mas os outros 8 pesos não precisam somar zero. Se as views neutras
   já carregam direcional NÃO-intencional, ele soma ao da 15b sem aparecer.

Uso:
    python scripts/ortogonalidade.py [--raiz <dir com data/>]
"""

import argparse
import sys
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from backtest_v1 import carregar  # noqa: E402
from config import ASSETS  # noqa: E402
from teste_sinal import K_GRID_C, registros_C, series_C  # noqa: E402

# Sinal-fonte de cada view: a chave do `diagnostics` que carrega o número que a
# view lê do mundo, DEPOIS da demeanagem — é o que entra no Q, e portanto o que
# a D22 quer ver descorrelacionado.
SINAL_FONTE = {
    "2.2_inflacao": "divergencia_liquida",
    "2.3_fed": "surpresa_liquida",
    "incerteza_anuncio": "incerteza_liquida",
    "B_trajetoria_propria": "surpresa_liquida",
}

ROTULO = {
    "2.2_inflacao": "2.2 inflação",
    "2.3_fed": "2.3 Fed",
    "incerteza_anuncio": "15b incerteza",
    "B_trajetoria_propria": "15g B própria",
    **{f"C_k{k}": f"**C** geopolítica (k = {k})" for k in K_GRID_C},
}

# As quatro que já estão DENTRO. A C é candidata: o item 4 dela se mede contra
# estas, não contra as outras versões de si mesma.
ATIVAS = ("2.2_inflacao", "2.3_fed", "incerteza_anuncio", "B_trajetoria_propria")


def angulo(p1, p2):
    """Ângulo em graus entre dois P. NaN se algum for degenerado (norma 0)."""
    n1, n2 = np.linalg.norm(p1), np.linalg.norm(p2)
    if n1 == 0 or n2 == 0:
        return float("nan")
    # clip porque erro de ponto flutuante põe o cosseno em ±1,0000000002
    return float(np.degrees(np.arccos(np.clip(p1 @ p2 / (n1 * n2), -1.0, 1.0))))


def coletar(montador, datas):
    """Uma passada do montador: P e sinal-fonte de cada view viva, por pregão."""
    Ps, sinais = {}, {}
    for data in datas:
        _, views, _ = montador(data)
        for view in views:
            if view is None:
                continue
            nome = view.diagnostics["view"]
            Ps.setdefault(nome, {})[data] = np.asarray(view.P, dtype=float)
            chave = SINAL_FONTE.get(nome)
            if chave in view.diagnostics:
                sinais.setdefault(nome, {})[data] = float(view.diagnostics[chave])
    return Ps, {n: pd.Series(s).sort_index() for n, s in sinais.items()}


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raiz", default=".")
    parser.add_argument("--saida", default="Dump/analises/Ortogonalidade.md")
    args = parser.parse_args()

    retornos, montador, datas, _ = carregar(args.raiz, views_novas=("incerteza", "B"))
    montador.escala_incerteza = "entropia"   # D15c, fechada em 2026-08-10
    montador.reset()
    Ps, sinais = coletar(montador, datas)

    # A view C entra como CANDIDATA, uma linha por k — o critério de escolher k
    # é decisão humana (`views_common.lag_regression`), então a grade mede e não
    # escolhe. Montada pelo mesmo código do teste de sinal, para as duas
    # medições não divergirem em silêncio.
    series_c = series_C(args.raiz, montador._fl, retornos.index)
    for k in K_GRID_C:
        regs, divergencias = registros_C(series_c, retornos, datas, k)
        if not regs:
            continue
        Ps[f"C_k{k}"] = {d: np.asarray(P, dtype=float) for d, P, _, _ in regs}
        sinais[f"C_k{k}"] = divergencias

    def par_valido(a, b):
        """Pares C × C não interessam: a C é candidata contra o que já entrou."""
        return not (a not in ATIVAS and b not in ATIVAS)

    L = ["# Ortogonalidade — item 4 da D22 e obrigação 5a\n",
         "> Gerado por `scripts/ortogonalidade.py`. **Mede; não decide.** Escala da "
         "15b = **entropia crua** (D15c, fechada em 2026-08-10).\n",
         f"- janela: **{datas[0].date()} a {datas[-1].date()}** ({len(datas)} pregões)",
         "- views vivas: " + " · ".join(f"**{ROTULO[n]}** ({len(Ps[n])} dias)"
                                        for n in Ps) + "\n"]

    L.append("\n## 1. Ângulo entre os P (dia a dia, nos pregões em que as duas vivem)\n")
    L.append("| par | dias em comum | ângulo mediano | mínimo | p05 | dias < 30° |")
    L.append("|---|---|---|---|---|---|")
    for a, b in combinations(Ps, 2):
        if not par_valido(a, b):
            continue
        comuns = sorted(set(Ps[a]) & set(Ps[b]))
        if not comuns:
            L.append(f"| {ROTULO[a]} × {ROTULO[b]} | 0 | — | — | — | — |")
            continue
        ang = np.array([angulo(Ps[a][d], Ps[b][d]) for d in comuns])
        L.append(f"| {ROTULO[a]} × {ROTULO[b]} | {len(comuns)} | "
                 f"{np.nanmedian(ang):.1f}° | {np.nanmin(ang):.1f}° | "
                 f"{np.nanpercentile(ang, 5):.1f}° | "
                 f"{int((ang < 30).sum())} |")

    L.append("\n## 2. ρ entre os sinais-fonte (o que de fato testa a 15b)\n")
    L.append("| par | dias em comum | ρ de Pearson | ρ de Spearman |")
    L.append("|---|---|---|---|")
    for a, b in combinations(sinais, 2):
        if not par_valido(a, b):
            continue
        s1, s2 = sinais[a].align(sinais[b], join="inner")
        if len(s1) < 3 or s1.std() == 0 or s2.std() == 0:
            L.append(f"| {ROTULO[a]} × {ROTULO[b]} | {len(s1)} | — | — |")
            continue
        L.append(f"| {ROTULO[a]} × {ROTULO[b]} | {len(s1)} | "
                 f"{s1.corr(s2):+.3f} | {s1.corr(s2, method='spearman'):+.3f} |")

    L.append("\n## 3. ΣP por view — obrigação 5a\n")
    L.append("`P_from_betas` crava `P[SPY] = 0` exato, mas os outros 8 pesos não "
             "precisam somar zero. ΣP ≠ 0 numa view NEUTRA é exposição direcional "
             "não-intencional — e ela soma à da 15b, que é direcional de propósito.\n")
    L.append("| view | dias | ΣP mediano | ΣP médio | mín | máx | Σ\\|P\\| |")
    L.append("|---|---|---|---|---|---|---|")
    for nome, porta in Ps.items():
        somas = np.array([P.sum() for P in porta.values()])
        abs_somas = np.array([np.abs(P).sum() for P in porta.values()])
        L.append(f"| {ROTULO[nome]} | {len(somas)} | {np.median(somas):+.3f} | "
                 f"{somas.mean():+.3f} | {somas.min():+.3f} | {somas.max():+.3f} | "
                 f"{np.median(abs_somas):.2f} |")

    L.append("\n**Exposição direcional agregada** — soma dos ΣP das views vivas no "
             "mesmo pregão, que é o que a carteira sente:\n")
    todas = sorted({d for porta in Ps.values() for d in porta})
    agregado = pd.Series({d: sum(P[d].sum() for P in Ps.values() if d in P)
                          for d in todas})
    com_15b = [d for d in todas if d in Ps.get("incerteza_anuncio", {})]
    sem_15b = [d for d in todas if d not in set(com_15b)]
    L.append(f"| recorte | dias | ΣP agregado mediano | mín | máx |")
    L.append("|---|---|---|---|---|")
    for rotulo, dias in (("todos os pregões", todas),
                         ("pregões SEM a 15b", sem_15b),
                         ("pregões COM a 15b", com_15b)):
        if not dias:
            continue
        v = agregado.loc[dias]
        L.append(f"| {rotulo} | {len(v)} | {v.median():+.3f} | {v.min():+.3f} | "
                 f"{v.max():+.3f} |")

    # Leitura GERADA — frase cravada à mão vira mentira na re-rodada (lição da
    # sessão 15). Os limiares abaixo são de RELATO, não de aprovação: a D22 não
    # define "ρ alto" nem "ângulo alto" em número, e inventar um aqui seria
    # fixar threshold sem decisão (CLAUDE.md §6).
    L.append("\n## Leitura (gerada)\n")
    L.append("Limiares de RELATO — |ρ| ≥ 0,50 e |ΣP| ≥ 0,50. **Não são notas de "
             "corte:** a D22 exige 'ângulo alto' e 'sem ρ alto' sem cravar "
             "número, e cravar um aqui seria inventar threshold (CLAUDE.md §6).\n")

    degenerados = [f"{ROTULO[a]} × {ROTULO[b]}"
                   for a, b in combinations(Ps, 2) if par_valido(a, b)
                   for comuns in [sorted(set(Ps[a]) & set(Ps[b]))] if comuns
                   and np.allclose([angulo(Ps[a][d], Ps[b][d]) for d in comuns], 90.0)]
    if degenerados:
        L.append("- **Ângulo de exatamente 90°, e ele NÃO testa nada** em: "
                 + " · ".join(degenerados)
                 + ". O P da 15b é `[SPY=2, 0…]` e o das neutras sai de "
                 "`P_from_betas`, que crava `P[SPY] = 0` EXATO — o produto "
                 "interno é zero por construção, em qualquer amostra. Para a 15b "
                 "o item 4 se decide **só pelo ρ**.")

    altos = []
    for a, b in combinations(sinais, 2):
        if not par_valido(a, b):
            continue
        s1, s2 = sinais[a].align(sinais[b], join="inner")
        if len(s1) >= 3 and s1.std() and s2.std() and abs(s1.corr(s2)) >= 0.50:
            altos.append(f"**{ROTULO[a]} × {ROTULO[b]}** ρ {s1.corr(s2):+.3f} "
                         f"(spearman {s1.corr(s2, method='spearman'):+.3f}, "
                         f"{len(s1)} dias)")
    L.append(("- **ρ acima do limiar de relato em: " + " · ".join(altos)
              + ".** A D22 não define o que é 'alto' — quem lê decide, e a "
                "decisão é humana.")
             if altos else "- Nenhum par de sinais-fonte passa do limiar de relato.")

    # Só as ATIVAS: a obrigação 5a fala do que já está dentro da carteira. A C é
    # candidata e o ΣP dela sai na tabela acima, sem entrar nesta conclusão.
    fora = [f"**{ROTULO[n]}** ΣP {np.median([P.sum() for P in porta.values()]):+.3f}"
            for n, porta in Ps.items()
            if n in ATIVAS and n != "incerteza_anuncio"
            and abs(np.median([P.sum() for P in porta.values()])) >= 0.50]
    if fora:
        L.append("- 🛑 **Obrigação 5a: as views NEUTRAS não são neutras** — "
                 + " · ".join(fora)
                 + ". `P[SPY] = 0` é exato, mas o resto do vetor é LÍQUIDO "
                 "COMPRADO nos outros 8 ativos, que têm β próprio ao mercado. "
                 "A regra do docstring: se o direcional não for intencional, a "
                 "centragem se troca em TODAS as views juntas, nunca em uma. "
                 "**Decisão humana — não fechada aqui.**")

    Path(args.saida).write_text("\n".join(L) + "\n", encoding="utf-8")
    sys.stdout.write("\n".join(L) + f"\n\nescrito: {args.saida}\n")


if __name__ == "__main__":
    main()
