"""Teste de sinal das views — VETO, não certificado. Felipe.

Promove ao repositório o teste que rodou ad-hoc nas sessões 12/16 e vivia no
scratchpad (pendência de reprodutibilidade registrada no fim da 15g). Mede uma
coisa só:

    a carteira P da view rende na direção que o Q dela aponta?

    r_P(D→D+h) = Σ_i P_i(D) · r_i          regredido contra   Q(D)

**O que este teste É e o que NÃO é (15f, e a distinção decide como citá-lo):**
nenhuma view do v1 passa — a 2.3, que carrega o backtest, dá t +0,26. Logo ele
não mede utilidade dentro do BL, onde o Q interage com Σ, w_mkt e o teto. O que
ele separa bem é **sinal invertido**: as incumbentes são indistinguíveis de
zero, a transversal (15f) era significativamente ao contrário. Por isso as duas
views da entrega entram na tabela como **grupo de controle embutido** — se elas
não reproduzirem o registrado, o errado é o script.

Rodam quatro linhas:

  2.2, 2.3            controle, direto do `MontadorV1` (mesma montagem do v1)
  transversal (β cru) reprodução da 15f, que reprovou (t −3,02, acerto 35%)
  transversal (β ⊥)   **a candidata 2 do `leaveoff.md`**: o mesmo desenho com o
                      β estimado contra o Δbreakeven RESIDUALIZADO do canal
                      risk-on (retorno do SPY e ΔDGS10)

A ordem é o ponto: a 15f gastou 400 linhas de módulo numa view que este teste
teria matado em minutos (lição da 14a/D17). A ortogonalização é testada AQUI,
antes de encostar em `view_cpi_transversal.estimate_betas_breakeven`.

Uso:
    python scripts/teste_sinal.py --raiz . --saida Dump/analises/Teste_sinal.md
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from backtest_v1 import carregar  # noqa: E402
from config import ASSETS  # noqa: E402
from view_cpi_transversal import estimate_betas_breakeven  # noqa: E402
from views_common import P_from_betas  # noqa: E402

# Horizontes reportados. h = 1 é o H da carteira (D9); h = 5 é a janela em que a
# 15g mediu a B, mantida para as duas medições ficarem comparáveis.
HORIZONTES = (1, 5, "divulgação")

# Canal contra o qual o Δbreakeven é residualizado na variante ortogonalizada.
# São os dois eixos que as três medições da família de inflação apontaram como
# donos do β (risk-on e duração) — `Convergencia_2_2.md`, 15a, 17b.
CANAL_RISK_ON = "SPY"


def ols(y, x):
    """(coef, t, n) da regressão univariada y = a + b·x sobre o par sem NaN."""
    par = pd.concat([pd.Series(y).rename("y"), pd.Series(x).rename("x")],
                    axis=1).dropna()
    if len(par) < 10:
        return float("nan"), float("nan"), len(par)
    yv, xv = par["y"].to_numpy(), par["x"].to_numpy()
    X = np.column_stack([np.ones(len(xv)), xv])
    beta, *_ = np.linalg.lstsq(X, yv, rcond=None)
    residuos = yv - X @ beta
    se = np.sqrt((residuos ** 2).sum() / (len(xv) - 2)
                 * np.linalg.inv(X.T @ X)[1, 1])
    return float(beta[1]), float(beta[1] / se), len(par)


def residualizar(dbe, retornos, dgs10):
    """Δbreakeven limpo do canal risk-on: resíduo de OLS contra r_SPY e ΔDGS10.

    É o conserto proposto na candidata 2. A causa medida da morte da 15f é que o
    β diário ao Δbreakeven é dominado por risk-on e duração (XLE +20,4, XLF
    +15,2, TLT −11,2 contra o breakeven cru), então o P que sai é "cíclicos e
    energia contra duração" e não "quem responde a inflação". Tirando esses dois
    eixos do regressor, o que sobra do Δbreakeven é o pedaço não explicado por
    eles — e o β contra ele é a sensibilidade que a view supunha estar medindo.
    """
    par = pd.concat([dbe.rename("dbe"), retornos[CANAL_RISK_ON].rename("mkt"),
                     dgs10.diff().rename("dy")], axis=1).dropna()
    X = np.column_stack([np.ones(len(par)), par["mkt"], par["dy"]])
    beta, *_ = np.linalg.lstsq(X, par["dbe"].to_numpy(), rcond=None)
    return pd.Series(par["dbe"].to_numpy() - X @ beta, index=par.index)


def retorno_da_carteira(retornos, data, P, h):
    """Σ dos h retornos de `P` a partir de D+1 (a carteira monta no close de D).

    D+1 e não D é convenção do CONTROLE, não escolha: com ela a 2.3 reproduz
    exatamente o t +0,26 / 51% registrado na 15f (ver 15g).
    """
    if h is None:
        return float("nan")
    seguintes = retornos.index[retornos.index > data][:h]
    if len(seguintes) < h:
        return float("nan")
    return float((retornos.loc[seguintes].to_numpy() @ np.asarray(P)).sum())


def medir(registros, retornos, h):
    """(coef, t, n, acerto) de r_P(h) contra Q, para uma lista de (data, P, Q, hd).

    `h = "divulgação"` usa o horizonte PRÓPRIO de cada dia (pregões até a
    divulgação do CPI) — é nele que a 15f mediu o t −3,02 que reprovou a view, e
    é a única coluna comparável ao número registrado. Views sem horizonte
    próprio (a 2.3) saem NaN nessa coluna.
    """
    Q = [q for _, _, q, _ in registros]
    rP = [retorno_da_carteira(retornos, d, P, hd if h == "divulgação" else h)
          for d, P, _, hd in registros]
    coef, t, n = ols(rP, Q)
    par = pd.DataFrame({"q": Q, "r": rP}).dropna()
    acerto = float((np.sign(par["q"]) == np.sign(par["r"])).mean()) if len(par) else float("nan")
    return coef, t, n, acerto


def transporte(registros, retornos, betas_finais, h):
    """corr entre o coef. PREDITIVO de cada ativo e o β contemporâneo.

    É o elo 2 da 15f, o que mediu +0,06 e matou a view: o β diz quem se move
    quando o breakeven anda, e o coeficiente preditivo diz quem se move DEPOIS,
    condicionado ao sinal. Se os dois não se parecem, o β não é mapa de
    transmissão e o P está montado sobre a coisa errada.
    """
    sinal = [q for _, _, q, _ in registros]
    preditivos = []
    for ativo in ASSETS:
        col = [retorno_da_carteira(retornos, d,
                                   np.eye(len(ASSETS))[list(ASSETS).index(ativo)],
                                   hd if h == "divulgação" else h)
               for d, _, _, hd in registros]
        preditivos.append(ols(col, sinal)[0])
    par = pd.DataFrame({"pred": preditivos, "beta": betas_finais}).dropna()
    return float(np.corrcoef(par["pred"], par["beta"])[0, 1]) if len(par) > 2 else float("nan")


def coletar(raiz):
    """Percorre a janela do v1 e devolve os registros (data, P, Q) de cada view.

    As views 2.2 e 2.3 saem do `MontadorV1` — a MESMA montagem da entrega, sem
    recópia de fórmula. As duas transversais são montadas aqui porque a 15f
    reprovou e elas não estão no montador; os insumos (divergência líquida e
    dias até a divulgação) vêm dos diagnostics da 2.2, que é onde a cascata roda.
    """
    retornos, montador, datas, _ = carregar(raiz)
    dbe = montador.breakeven.diff().dropna()
    dbe_orto = residualizar(dbe, retornos, montador.dgs10)

    registros = {n: [] for n in ("2.2", "2.3", "transversal (β cru)",
                                 "transversal (β ⊥ risk-on)")}
    for data in datas:
        _, views, _ = montador(data)
        for view in views:
            if view is None:
                continue
            nome = view.diagnostics.get("view")
            if nome == "2.2_inflacao":
                div = view.diagnostics["divergencia_liquida"]
                faltam = view.diagnostics["dias_ate_divulgacao"]
                registros["2.2"].append((data, view.P, view.Q, faltam))
                # β expansivo, só com dado estritamente anterior a D.
                passado = retornos[retornos.index < data]
                for rotulo, serie in (("transversal (β cru)", dbe),
                                      ("transversal (β ⊥ risk-on)", dbe_orto)):
                    betas = estimate_betas_breakeven(
                        passado, serie.reindex(passado.index), ASSETS)
                    P = P_from_betas(betas, list(ASSETS), CANAL_RISK_ON)
                    Q = float((P @ betas) * div / faltam)
                    registros[rotulo].append((data, P, Q, faltam))
            elif nome == "2.3_fed":
                registros["2.3"].append((data, view.P, view.Q, None))
    # β do fim da janela, para o elo 2 (o transporte) das duas transversais.
    betas_finais = {
        "transversal (β cru)": estimate_betas_breakeven(
            retornos, dbe.reindex(retornos.index), ASSETS),
        "transversal (β ⊥ risk-on)": estimate_betas_breakeven(
            retornos, dbe_orto.reindex(retornos.index), ASSETS),
    }
    return retornos, registros, betas_finais


def main():
    # O console do Windows abre em cp1252 e engasga no Σ/⊥ dos rótulos — mesma
    # linha do `backtest_v1.main`.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raiz", default=".")
    parser.add_argument("--saida", default="Dump/analises/Teste_sinal.md")
    args = parser.parse_args()

    retornos, registros, betas_finais = coletar(args.raiz)

    saida = []
    escrever = saida.append
    escrever("# Teste de sinal das views — VETO, não certificado\n")
    escrever("> Gerado por `scripts/teste_sinal.py`. **Mede; não decide.** "
             "Regressão de `r_P(D→D+h)` contra o `Q(D)` da própria view. "
             "As views 2.2 e 2.3 são **controle embutido**: se elas não "
             "reproduzirem o registrado na 15f, o errado é o script.\n")
    escrever("| view | n | " + " | ".join(
        f"h = {h}: coef · t · acerto" for h in HORIZONTES) + " |")
    escrever("|" + "---|" * (len(HORIZONTES) + 2))
    for nome, regs in registros.items():
        celulas = []
        for h in HORIZONTES:
            coef, t, n, acerto = medir(regs, retornos, h)
            texto = f"{coef:+.4f} · t {t:+.2f} · {acerto:.0%}"
            celulas.append(f"**{texto}**" if abs(t) > 2 else texto)
        escrever(f"| {nome} | {len(regs)} | " + " | ".join(celulas) + " |")

    escrever("\n## Elo 2 — o transporte do β (foi ele que matou a 15f)\n")
    escrever("corr entre o coeficiente PREDITIVO de cada ativo e o β "
             "contemporâneo usado para montar o P. A 15f mediu **+0,06**.\n")
    escrever("| variante | " + " | ".join(f"h = {h}" for h in HORIZONTES) + " |")
    escrever("|" + "---|" * (len(HORIZONTES) + 1))
    for nome, betas in betas_finais.items():
        celulas = [f"{transporte(registros[nome], retornos, betas, h):+.2f}"
                   for h in HORIZONTES]
        escrever(f"| {nome} | " + " | ".join(celulas) + " |")

    escrever("\n## P do último pregão (onde cada variante fica posicionada)\n")
    escrever("| variante | " + " | ".join(ASSETS) + " |")
    escrever("|" + "---|" * (len(ASSETS) + 1))
    for nome in betas_finais:
        P = registros[nome][-1][1]
        escrever(f"| {nome} | " + " | ".join(f"{v:+.2f}" for v in P) + " |")

    Path(args.saida).write_text("\n".join(saida) + "\n", encoding="utf-8")
    sys.stdout.write("\n".join(saida) + f"\n\nescrito: {args.saida}\n")


if __name__ == "__main__":
    main()
