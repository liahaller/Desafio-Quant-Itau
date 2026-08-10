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

Rodam seis linhas:

  2.2, 2.3            controle, direto do `MontadorV1` (mesma montagem do v1)
  transversal (β cru) reprodução da 15f, que reprovou (t −3,02, acerto 35%)
  transversal (β ⊥)   **a candidata 2 do `leaveoff.md`**: o mesmo desenho com o
                      β estimado contra o Δbreakeven RESIDUALIZADO do canal
                      risk-on (retorno do SPY e ΔDGS10)
  incerteza (15b)     a view de prêmio de anúncio, `views_novas=("incerteza",)`
  B com β próprio     a 15g no vértice certo (DGS1), `views_novas=("B",)`
  C geopolítica       a última candidata, uma linha por k — montada AQUI e não
                      no `MontadorV1`, que é a ordem da D14a: o veto roda antes
                      de a view virar código de produção

As duas últimas entraram em 2026-08-10 para fechar a pendência registrada no
fim da sessão 18: elas tinham sido medidas no BACKTEST (15h) e nunca no teste de
sinal, então a tabela de veto do projeto estava incompleta justo nas duas
candidatas sem veredito negativo. A 15b roda na escala default (`entropia`); a
15h mediu as duas escalas da 15c no backtest e o veredito não mudou entre elas.

A ordem é o ponto: a 15f gastou 400 linhas de módulo numa view que este teste
teria matado em minutos (lição da 14a/D17). A ortogonalização é testada AQUI,
antes de encostar em `view_cpi_transversal.estimate_betas_breakeven`.

**Sobre o `h = 0`:** é o dia que o backtest de fato ganha — a montagem de D usa
só dado anterior à abertura de D e carrega o retorno close-to-close de D. Ele
entra porque é o ÚNICO horizonte da 15b (o Q dela é o retorno do próprio dia do
anúncio); para as demais é coluna informativa. O controle reproduz no `h = 1`,
que é a convenção em que 15f e 15g registraram os números.

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
from poly_loader import daily_preopen, series_by_slot  # noqa: E402
from poly_preprocessing import binary_prob_series  # noqa: E402
from view_cpi_transversal import estimate_betas_breakeven  # noqa: E402
from views_common import (P_from_betas, full_absorption_beta,  # noqa: E402
                          lag_regression)

# Horizontes reportados. h = 0 é o próprio pregão de D (o que o backtest ganha,
# e o único horizonte da 15b); h = 1 é o H da carteira (D9) e a convenção do
# controle; h = 5 é a janela em que a 15g mediu a B.
HORIZONTES = (0, 1, 5, "divulgação")

# Canal contra o qual o Δbreakeven é residualizado na variante ortogonalizada.
# São os dois eixos que as três medições da família de inflação apontaram como
# donos do β (risk-on e duração) — `Convergencia_2_2.md`, 15a, 17b.
CANAL_RISK_ON = "SPY"

# --- view C (candidata) ------------------------------------------------------
# Os DOIS episódios do mesmo par de perguntas (ação militar EUA/Israel × Irã).
# Episódios independentes, sem overlap: o de jun/2025 é o teste fora da amostra
# do de 2026 (D19a). A view liga e desliga — é o "evento episódico e recorrente"
# que a espec do módulo declara como a diferença dela para a 2.4.
MERCADOS_C = {
    "iran_jun2025": "M7_iran_jun2025_us-military-action-against-iran*.json",
    "iran_2026": "M7_iran_strike_*.json",
}

# O k NÃO é escolhido aqui — o critério de tirar k do perfil de defasagem é
# decisão humana registrada (docstring de `views_common.lag_regression`, especs
# 2.4/3.1). A grade mede e reporta; escolher a linha de melhor t seria calibrar
# parâmetro contra o resultado. O `Perfil_defasagem_k.md` aponta k = 3 como o de
# maior |correlação| no episódio de jun/2025 — é insumo, não decisão.
K_GRID_C = (1, 2, 3, 4, 5)


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

    `h = 0` é o caso à parte: o retorno do PRÓPRIO D, que é o que o backtest
    ganha (a montagem de D só olha dado anterior à abertura de D) e o único
    horizonte que a 15b tem — o Q dela é o close-to-close do dia do anúncio.
    """
    if h is None:
        return float("nan")
    if h == 0:
        janela = retornos.index[retornos.index == data]
        if not len(janela):
            return float("nan")
    else:
        janela = retornos.index[retornos.index > data][:h]
        if len(janela) < h:
            return float("nan")
    return float((retornos.loc[janela].to_numpy() @ np.asarray(P)).sum())


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


def series_C(raiz, fl, pregoes):
    """{episódio: série p(evento)} nos pregões, já com o pré-processamento da view.

    A MESMA série vai para a regressão do β e para o `p_t − p_{t−k}` — é o que
    faz a parte linear da correção FL ser absorvida pelo β (espec 2.4 item 2b),
    e é por isso que ela é construída UMA vez aqui.
    """
    series = {}
    for rotulo, padrao in MERCADOS_C.items():
        arquivos = sorted(Path(raiz, "data/raw/clob_exploracao").glob(padrao))
        if not arquivos:
            continue
        bruta = daily_preopen(series_by_slot(str(arquivos[0])))
        p = pd.Series(binary_prob_series(bruta.to_numpy(), fl_correction=fl),
                      index=bruta.index)
        series[rotulo] = p.reindex(pregoes).dropna()
    return series


def registros_C(series, retornos, datas, k):
    """(registros, divergências) da view C em cada pregão com mercado vivo.

    `registros` = [(data, P, Q, None)], no formato das outras views.
    `divergências` = Série `p_t − p_{t−k}` — o SINAL-FONTE, que é o que o item 4
    da D22 quer ver descorrelacionado. Vai separado do Q de propósito: o Q é a
    divergência já multiplicada por `Σ P·β`, e correlacionar Q com Q mediria o β
    junto com o sinal.

    β EXPANSIVO por episódio e estritamente anterior a D (sem lookahead), pela
    maquinaria da 2.4: perfil de lags distribuídos -> absorção plena até k.
    Sem piso de amostra além do **mínimo algébrico** do `lag_regression` — o
    precedente da D12b: piso que não morde é threshold inventado. Dia em que a
    regressão não é identificável cai na cascata e a view não existe.
    """
    saida, divergencias = [], {}
    for data in datas:
        for p in series.values():
            historico = p[p.index < data]
            if data not in p.index or len(historico) < k + 1:
                continue
            dp = historico.diff().dropna()
            R = retornos.reindex(dp.index).dropna()
            dp = dp.reindex(R.index)
            try:
                coefs = lag_regression(R[list(ASSETS)].to_numpy(), dp.to_numpy(), k)
            except ValueError:
                continue                      # amostra insuficiente -> cascata
            betas = full_absorption_beta(coefs, k)
            ate_hoje = p[p.index <= data]
            if len(ate_hoje) < k + 1:
                continue
            try:
                P = P_from_betas(betas, list(ASSETS))
            except ValueError:
                continue                      # β sem dispersão -> view sem conteúdo
            divergencia = float(ate_hoje.iloc[-1]) - float(ate_hoje.iloc[-1 - k])
            saida.append((data, P, float((P @ betas) * divergencia), None))
            divergencias[data] = divergencia
            break                             # UM evento por vez (espec do módulo)
    return saida, pd.Series(divergencias).sort_index()


def coletar(raiz):
    """Percorre a janela do v1 e devolve os registros (data, P, Q) de cada view.

    As views 2.2, 2.3, 15b e B saem do `MontadorV1` — a MESMA montagem da
    entrega e da 15h, sem recópia de fórmula (as duas últimas só existem com
    `views_novas`, que continua `()` no caminho da entrega). As duas
    transversais são montadas aqui porque a 15f reprovou e elas não estão no
    montador; os insumos (divergência líquida e dias até a divulgação) vêm dos
    diagnostics da 2.2, que é onde a cascata roda.
    """
    retornos, montador, datas, _ = carregar(raiz, views_novas=("incerteza", "B"))
    dbe = montador.breakeven.diff().dropna()
    dbe_orto = residualizar(dbe, retornos, montador.dgs10)

    registros = {n: [] for n in ("2.2", "2.3", "transversal (β cru)",
                                 "transversal (β ⊥ risk-on)",
                                 "incerteza (15b)", "B com β próprio (15g)")}
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
            elif nome == "incerteza_anuncio":
                registros["incerteza (15b)"].append((data, view.P, view.Q, None))
            elif nome == "B_trajetoria_propria":
                registros["B com β próprio (15g)"].append((data, view.P, view.Q, None))
    # View C — montada AQUI e não no montador, de propósito: a ordem da D14a diz
    # que o veto roda antes de a view virar código de produção. A 15f gastou 400
    # linhas de módulo numa view que este teste teria matado em minutos.
    series_c = series_C(raiz, montador._fl, retornos.index)
    for k in K_GRID_C:
        registros[f"C geopolítica (k = {k})"], _ = registros_C(
            series_c, retornos, datas, k)
    # POR EPISÓDIO — é o que permite escolher o k sem olhar o resultado do
    # conjunto: os dois episódios do Irã são independentes e não se sobrepõem,
    # então o k tirado de um é pré-registro para o outro. A tabela pooled acima
    # NÃO serve para escolher (o k de melhor t nela é o k ajustado à amostra
    # inteira — overfit em um passo).
    for rotulo, serie in series_c.items():
        for k in K_GRID_C:
            registros[f"C {rotulo} (k = {k})"], _ = registros_C(
                {rotulo: serie}, retornos, datas, k)

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
    escrever("**`h = 0` é o próprio pregão de D** — o que o backtest de fato "
             "ganha (a montagem de D só olha dado anterior à abertura de D) e o "
             "ÚNICO horizonte da 15b, cujo Q é o close-to-close do dia do "
             "anúncio. O controle reproduz no `h = 1`, que é a convenção em que "
             "15f e 15g registraram os números.\n")
    escrever("As linhas **incerteza (15b)** e **B com β próprio (15g)** entraram "
             "em 2026-08-10: as duas tinham sido medidas no BACKTEST (15h) e "
             "nunca aqui, e a B com o `DGS1` era pendência de protocolo aberta "
             "na 15h (`o teste de sinal no vértice certo segue não rodado`). "
             "Rodam com `views_novas=(\"incerteza\", \"B\")`; a entrega segue "
             "`views_novas=()`.\n")
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

    escrever("\n**Como ler as linhas por episódio da C, e é o ponto todo:** as "
             "linhas `C geopolítica (k = …)` juntam os dois episódios do Irã, e "
             "por isso **não servem para escolher o k** — o k de melhor t nelas é "
             "o k ajustado à amostra inteira. As linhas `C iran_jun2025` e "
             "`C iran_2026` são os dois episódios SEPARADOS, que não se "
             "sobrepõem em data. Um k escolhido no primeiro é pré-registro para "
             "o segundo, e a comparação de SINAL entre os dois é o único teste "
             "aqui que distingue tese de ajuste de amostra.\n")

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
