"""M4 recessão — a contradição com a D19c, completada em 2×2. Felipe.

**A pergunta, e é uma só:** a **D19c** mediu que o coeficiente da view 3.1 no
mercado de recessão **troca de sinal dentro da própria amostra** (SPY em
h = 10: +0,97% t +6,52 na 1ª metade, −0,35% t −2,27 na 2ª). A **D27** mediu que
a sleeve transversal no MESMO mercado **sobrevive** ao mesmo corte, em três
horizontes contíguos. As duas amostras se sobrepõem quase inteiras — não dá
para dispensar a D19c dizendo "é outro período".

Entre as duas medições mudaram **duas** coisas ao mesmo tempo:

    sinal   NÍVEL de discordância (3.1)  ×  INCREMENTO Δp em k (a sleeve)
    livro   SPY direcional (3.1)         ×  spread setorial neutro (a sleeve)

Com dois fatores mudando juntos, há duas explicações vivas e o dado publicado
não as separa:

    (1) a instabilidade mora no CANAL DE DIREÇÃO -> a sleeve é imune por
        construção (ela hedgeia exatamente esse canal), e a D19c deixa de ser
        objeção contra ela — vira mecanismo a favor;
    (2) a instabilidade mora no MERCADO M4 -> a sleeve sobreviveu por ler outra
        transformação do mesmo dado instável, e três horizontes contíguos não
        protegem contra isso, porque é a mesma amostra.

Este script preenche as duas células que faltam do 2×2 e decide entre (1) e (2).

⚠️ **Nada é declarado aqui.** Os dois livros são os já declarados para o M4
(`PREMISSAS` do `gate_event_driven.py` e `LIVROS_SETORIAIS` do
`gate_transversal.py`), importados **por referência**. A discordância é a
`divergencia_expansiva` da 3.1, o `Δp` é o do `Gate_transversal_neutro.md`, as
pernas `⊥` são as mesmas, e a partição em metades é a do `estabilidade`. O que
este script acrescenta é só o **cruzamento**.

⚠️ **Duas réguas, de propósito.** O G2 (μ encolhido, janela de 1 pregão) é a
régua em que a sleeve foi aprovada; o OLS em h = 10 é a régua em que a D19c
mediu o giro. Rodar só uma delas confundiria "a instabilidade sumiu" com "a
instabilidade não aparece neste horizonte" — o h = 10 e a janela de 1 pregão
não medem a mesma coisa, e o confundimento seria invisível.

⚠️ **As duas parcelas da discordância entram sozinhas**, porque o nível da 3.1
é `z(poly) − z(mercado)`: se o giro vier da perna do mercado (a curva de juros),
isso não é achado sobre o Polymarket nem sobre o M4.

**Nada em `src/` é tocado.**

Uso:

    python scripts/gate_recessao_2x2.py --raiz .
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from backtest_v1 import PONTOS_PERCENTUAIS  # noqa: E402
from config import SIGMA_JANELA_PREGOES  # noqa: E402
from gate_event_driven import PREMISSAS  # noqa: E402
from gate_sleeves import (bate_premissa, eventos_diarios,  # noqa: E402
                          mu_do_sinal)
from gate_transversal import LIVROS_SETORIAIS  # noqa: E402
from gate_transversal_neutro import JANELA, neutraliza, pernas_neutras  # noqa: E402
from market_loader import load_fred  # noqa: E402
from nivel_divergencia_3_1 import (PADRAO_NAO, PADRAO_SIM,  # noqa: E402
                                   spread_defasado)
from poly_loader import daily_preopen, series_by_slot  # noqa: E402
from poly_preprocessing import binary_prob_series  # noqa: E402
from premissa_g1 import em_pregoes, series_dos_mercados  # noqa: E402
from teste_sinal import ols  # noqa: E402
from view_3_1_direcional import (MINIMO_PREGOES as MINIMO_3_1,  # noqa: E402
                                 componentes_expansivos)

M4 = "M4 recessão EUA 2025"

# Horizonte da régua OLS. É o da D19c, não escolha nova: a tabela de
# estabilidade que derrubou a 3.1 direcional está em h = 10.
H_OLS = 10

# Lookbacks do `Δp` por candidata. São exatamente as células DECLARADAS na
# D28 — o bloco contíguo da M4 e a célula única da M9 —, não a grade inteira:
# varrer aqui sugeriria busca nova onde não houve.
LOOKBACKS_POR_MERCADO = {
    M4: (3, 5, 10),
    "M9 Câmara": (20,),
}


def recortes_do_sinal(sinal):
    """`[(rótulo, série)]` — amostra inteira e as duas metades.

    Mesma partição do `estabilidade` do `gate_noticia.py` (`len // 2` sobre o
    sinal já sem NaN), para as células novas serem comparáveis linha a linha
    com as que já estão publicadas. Uma partição diferente aqui tornaria o
    artefato incomparável com o `Gate_transversal_neutro.md`.
    """
    serie = pd.Series(sinal).dropna()
    corte = len(serie) // 2
    return [("inteira", serie), ("1ª metade", serie.iloc[:corte]),
            ("2ª metade", serie.iloc[corte:])]


def celula_g2(retornos, sinal, livro, sigma, ate, assets):
    """(bate, detalhe, {ticker: μ em bps}, ts, n) — a régua do G2, sem alteração.

    `ts` sai `None`: o μ encolhido não publica estatística t em artefato nenhum
    deste projeto, e inventar uma aqui daria à célula nova um critério que as
    células já publicadas não tiveram.
    """
    mu, n = mu_do_sinal(retornos, eventos_diarios(sinal), JANELA, tuple(livro),
                        sigma, ate)
    ok, detalhe = bate_premissa(mu, assets, livro)
    if mu is None:
        return ok, detalhe, {t: float("nan") for t in livro}, None, n
    vetor = np.asarray(mu, dtype=float)
    valores = {t: float(vetor[list(assets).index(t)] * PONTOS_PERCENTUAIS * 100.0)
               for t in livro}
    return ok, detalhe, valores, None, n


def celula_ols(retornos, sinal, livro, h=H_OLS):
    """(bate, detalhe, {ticker: coef em %}, {ticker: t}, n) — a régua da D19c.

    Retorno acumulado de D+1 a D+h de cada perna contra o sinal de D. O
    veredito é o mesmo critério do `bate_premissa`: o SINAL do coeficiente bate
    com o declarado a priori. Janelas sobrepostas para h > 1, então o |t| é
    otimista — é a mesma ressalva que o `Recessao_direcional.md` já declara, e
    ela não afeta o sinal, que é o que se lê aqui.
    """
    valores, ts, partes, ok, n_min = {}, {}, [], True, None
    for ticker, esperado in livro.items():
        futuro = [retornos[ticker].reindex(
            retornos.index[retornos.index > d][:h]).sum()
            if len(retornos.index[retornos.index > d]) >= h else float("nan")
            for d in sinal.index]
        coef, t, n = ols(futuro, sinal.to_numpy())
        acerta = bool(np.sign(coef) == np.sign(esperado))
        ok = ok and acerta
        n_min = n if n_min is None else min(n_min, n)
        valores[ticker], ts[ticker] = coef * PONTOS_PERCENTUAIS, t
        partes.append(f"{ticker} {coef * PONTOS_PERCENTUAIS:+.2f}% t {t:+.2f} "
                      f"{'✅' if acerta else '❌'}")
    return ok, " · ".join(partes), valores, ts, n_min


# Corte de significância do critério FORTE. É o mesmo |t| > 2 que o
# `Recessao_direcional.md` usa para negritar célula, não corte novo.
LIMIAR_T = 2.0


def gira_de_sinal(valores_1, valores_2, ts_1=None, ts_2=None):
    """Alguma perna troca de sinal entre as duas metades?

    Sem os `ts` é o critério FRACO — só a troca de sinal. Ele é diferente de
    "as duas metades reprovam": reprovar nas duas é errar de forma estável, e
    não é instabilidade.

    Com os `ts` é o critério da **D19c palavra por palavra**: *"as duas metades
    são significantes e apontam para lados opostos"*. A distinção não é
    refinamento — medido em h = 10, o critério fraco marca quase toda a tabela,
    porque com janelas sobrepostas e n ~ 200 trocar de sinal é barato. Um teste
    que reprova todo mundo não separa candidato de ruído.
    """
    def flipa(ticker):
        if not (np.isfinite(valores_1[ticker]) and np.isfinite(valores_2[ticker])):
            return False
        if np.sign(valores_1[ticker]) == np.sign(valores_2[ticker]):
            return False
        if ts_1 is None or ts_2 is None:
            return True
        return (abs(ts_1[ticker]) > LIMIAR_T) and (abs(ts_2[ticker]) > LIMIAR_T)

    return any(flipa(t) for t in valores_1)


def z_expansivo(serie, minimo=MINIMO_3_1):
    """`z` com média e desvio EXPANSIVOS — o NÍVEL de um mercado sem contraparte.

    Só a M4 tem benchmark de mercado (a curva de juros) para formar a
    discordância da 3.1. Nos outros a única versão honesta de "nível" é a
    própria crença padronizada — mesma padronização expansiva, mesmo piso
    amostral, para as linhas serem comparáveis entre candidatas.
    """
    return ((serie - serie.expanding(minimo).mean())
            / serie.expanding(minimo).std()).dropna()


def montar_sinais(args, pregoes, mercado, p_cru):
    """`[(rótulo, grupo, série)]` — as linhas de NÍVEL da candidata.

    Na M4 são as três parcelas da discordância da 3.1 mais o `Δ` dela, porque é
    a montagem exata que a D19c mediu. Em qualquer outro mercado não existe
    discordância — não há benchmark —, então o nível é o `z` da própria crença.
    """
    if mercado != M4:
        return [(f"z(p) — o NÍVEL da crença", "nível", z_expansivo(p_cru))], p_cru
    diretorio = Path(args.raiz) / args.dados
    sim = daily_preopen(series_by_slot(next(diretorio.glob(PADRAO_SIM))))
    nao = daily_preopen(series_by_slot(next(diretorio.glob(PADRAO_NAO))))
    par = pd.concat([sim.rename("sim"), nao.rename("nao")], axis=1).dropna()
    p_norm = pd.Series(binary_prob_series(par["sim"].to_numpy(),
                                          par["nao"].to_numpy()),
                       index=par.index).reindex(
        par.index.intersection(pregoes)).dropna()
    spread = spread_defasado(load_fred(Path(args.raiz) / args.dgs10),
                             load_fred(Path(args.raiz) / args.dtb3),
                             p_norm.index)
    z_poly, z_mercado = componentes_expansivos(p_norm, spread)
    discordancia = (z_poly - z_mercado).dropna()
    return [
        ("discordância (o sinal da 3.1)", "nível", discordancia),
        ("z(poly) — só a perna do Polymarket", "nível", z_poly.dropna()),
        ("z(−spread) — só a perna do mercado", "nível", z_mercado.dropna()),
        ("Δ discordância (k = 5)", "incremento", discordancia.diff(5).dropna()),
    ], p_norm


def main():
    # O console do Windows abre em cp1252 e engasga nos rótulos acentuados.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raiz", default=".")
    parser.add_argument("--dados", default="data/raw/clob_exploracao")
    parser.add_argument("--dgs10", default="data/raw/fred_DGS10.csv")
    parser.add_argument("--dtb3", default="data/raw/fred_DTB3.csv")
    parser.add_argument("--mercado", default=M4,
                        choices=sorted(LOOKBACKS_POR_MERCADO))
    parser.add_argument("--saida", default=None)
    args = parser.parse_args()

    mercado = args.mercado
    lookbacks = LOOKBACKS_POR_MERCADO[mercado]
    saida = args.saida or (
        "Dump/analises/Gate_recessao_2x2.md" if mercado == M4 else
        "Dump/analises/Gate_2x2_M9.md")

    series, retornos, _montador, datas = series_dos_mercados(args.raiz)

    # Universo estendido IDÊNTICO ao do `gate_transversal_neutro.py` — mesmas
    # pernas hedgeadas, mesmo `dropna`, mesma Σ diagonal. Reconstruir com um
    # subconjunto mudaria as datas que sobrevivem ao `dropna` e a sleeve não
    # sairia com o número já publicado.
    setoriais = sorted({a for livro, _t in LIVROS_SETORIAIS.values() for a in livro})
    estendido = pernas_neutras(retornos, setoriais).dropna()
    assets_ext = tuple(estendido.columns)
    sigma = np.diag(estendido.tail(SIGMA_JANELA_PREGOES).var().to_numpy())
    ate = datas[-1] + pd.Timedelta(days=1)

    livros = {
        "SPY direcional (livro da 3.1)": PREMISSAS[mercado][0],
        "spread neutro (livro da sleeve)": neutraliza(LIVROS_SETORIAIS[mercado][0]),
    }

    p_cru = em_pregoes(next(s for n, _f, s, _t, _u in series if n == mercado))
    sinais, p_norm = montar_sinais(args, retornos.index, mercado, p_cru)
    for k in lookbacks:
        sinais.append((f"Δp k = {k} (o sinal da sleeve)", "incremento",
                       p_cru.diff(k).dropna()))
    grupo_do_sinal = {rotulo: grupo for rotulo, grupo, _s in sinais}

    # As duas séries de probabilidade não são a mesma: a 3.1 normaliza os dois
    # lados do binário, a sleeve lê o midpoint do SIM cru. Se elas divergissem,
    # metade da comparação seria sobre a construção do `p` e não sobre a
    # transformação — então isso sai medido, não assumido.
    comum = p_norm.index.intersection(p_cru.index)
    corr_p = float(p_norm.reindex(comum).corr(p_cru.reindex(comum)))

    linhas, medidas = [], {}
    for regua, funcao in (("G2 (μ encolhido, janela 1 pregão)", "g2"),
                          (f"OLS (h = {H_OLS}, a régua da D19c)", "ols")):
        for rotulo, grupo, sinal in sinais:
            for nome_livro, livro in livros.items():
                celula = {}
                for recorte, pedaco in recortes_do_sinal(sinal):
                    if funcao == "g2":
                        celula[recorte] = celula_g2(
                            estendido, pedaco, livro, sigma, ate, assets_ext)
                    else:
                        celula[recorte] = celula_ols(estendido, pedaco, livro)
                m1, m2 = celula["1ª metade"], celula["2ª metade"]
                fraco = gira_de_sinal(m1[2], m2[2])
                forte = (gira_de_sinal(m1[2], m2[2], m1[3], m2[3])
                         if funcao == "ols" else None)
                medidas[(regua, rotulo, nome_livro)] = (celula, fraco, forte)
                linhas.append({
                    "régua": regua, "sinal": rotulo, "livro": nome_livro,
                    "inteira": "✅" if celula["inteira"][0] else "❌",
                    "1ª metade": "✅" if m1[0] else "❌",
                    "2ª metade": "✅" if m2[0] else "❌",
                    "gira (fraco)": "🛑 SIM" if fraco else "não",
                    "gira (D19c: |t| > 2 nas duas)": (
                        "—" if forte is None else ("🛑 SIM" if forte else "não")),
                    "n (inteira)": celula["inteira"][4],
                })
    tabela = pd.DataFrame(linhas)

    texto = [
        "# M4 recessão — a contradição com a D19c, em 2×2\n",
        "> Gerado por `scripts/gate_recessao_2x2.py`. **Mede; não decide.** "
        "Nenhuma premissa nova: os dois livros, a discordância, o `Δp`, as "
        "pernas `⊥` e a partição em metades são importados por referência dos "
        "artefatos anteriores. O que este artefato acrescenta é o "
        "**cruzamento** entre o sinal de um e o livro do outro.\n",
        f"- janela: **{datas[0]:%Y-%m-%d} a {datas[-1]:%Y-%m-%d}** "
        f"({len(datas)} pregões); δ e Σ os mesmos do v1 (D7/D8)",
        f"- livro da 3.1: `{PREMISSAS[mercado][0]}` — *{PREMISSAS[mercado][1]}*",
        f"- livro da sleeve: `{livros['spread neutro (livro da sleeve)']}` — "
        f"*{LIVROS_SETORIAIS[mercado][1]}*",
        f"- correlação entre as duas séries de `p` (a normalizada que a 3.1 lê "
        f"× o midpoint cru que a sleeve lê, {len(comum)} pregões comuns): "
        f"**{corr_p:+.3f}**\n",
        "## As quatro células, e as três que faltavam\n",
        "| | livro: SPY direcional | livro: spread neutro |",
        "|---|---|---|",
        "| **sinal: nível (discordância)** | a **D19c** | ⬅ célula nova |",
        "| **sinal: incremento (Δp)** | ⬅ célula nova | a **D27** |\n",
        "As parcelas da discordância (`z(poly)` e `z(−spread)` sozinhas) e o "
        "`Δ` da própria discordância entram como linhas extras: sem elas não "
        "dá para dizer se um giro veio do Polymarket ou da curva de juros.\n",
        "## Tabela\n",
        tabela.to_markdown(index=False), "",
        "**Duas colunas de giro, e a diferença entre elas é o ponto.** O "
        "critério FRACO é só a troca de sinal; o FORTE é o da D19c palavra por "
        "palavra — *as duas metades significantes e apontando para lados "
        "opostos*. No G2 só existe o fraco: o μ encolhido não publica `t` em "
        "artefato nenhum deste projeto, e inventar um aqui daria à célula nova "
        "um critério que as células já publicadas não tiveram.\n",
        "### Detalhe por perna\n",
    ]
    for (regua, rotulo, nome_livro), (celula, _f, _s) in medidas.items():
        texto.append(f"- **{regua}** · {rotulo} · {nome_livro}")
        for recorte in ("inteira", "1ª metade", "2ª metade"):
            ok, detalhe, _v, _t, n = celula[recorte]
            texto.append(f"    - {recorte}: `{detalhe}` "
                         f"({'✅' if ok else '❌'}, n = {n})")
    texto.append("")

    # --- leitura, gerada DOS NÚMEROS -----------------------------------------
    # Prosa escrita à mão sobre tabela gerada é o modo de falha que já salvou
    # cinco afirmações falsas neste projeto (D27). Toda frase abaixo é uma
    # ramificação sobre `medidas`, não um parágrafo redigido.
    texto.append("## Leitura\n")

    regua_g2 = [r for r in tabela["régua"].unique() if r.startswith("G2")][0]
    regua_ols = [r for r in tabela["régua"].unique() if r.startswith("OLS")][0]

    def gira_em(rotulo, livro):
        """O giro de cada régua, cada uma pelo critério que ela suporta."""
        celula, fraco, forte = medidas[(regua_g2, rotulo, livro)]
        _c, _f, forte_ols = medidas[(regua_ols, rotulo, livro)]
        return {regua_g2: fraco, regua_ols: forte_ols}

    # A linha de NÍVEL da candidata. Na M4 é a discordância da 3.1; em
    # qualquer outro mercado é o `z` da própria crença, porque não há
    # benchmark de mercado para formar discordância.
    disc = next(r for r, g in grupo_do_sinal.items() if g == "nível")
    spy = "SPY direcional (livro da 3.1)"
    neutro = "spread neutro (livro da sleeve)"
    d_spy, d_neutro = gira_em(disc, spy), gira_em(disc, neutro)

    # (a) o critério fraco discrimina alguma coisa em h = 10?
    ols_celulas = [(k, v) for k, v in medidas.items() if k[0] == regua_ols]
    n_fraco = sum(1 for _k, v in ols_celulas if v[1])
    n_forte = sum(1 for _k, v in ols_celulas if v[2])
    texto.append(
        f"**Antes de ler qualquer célula: em h = {H_OLS} o critério fraco "
        f"marca {n_fraco} das {len(ols_celulas)} células, e o da D19c marca "
        f"{n_forte}.** "
        + ("Com janelas sobrepostas e n ~ 200, trocar de sinal entre as "
           "metades é barato — um teste que reprova quase todo mundo não "
           "separa candidato de ruído. **Só o critério forte é lido abaixo "
           "nessa régua.**\n" if n_fraco > len(ols_celulas) * 0.7 else
           "Os dois critérios discriminam, então a leitura abaixo não depende "
           "de qual deles se escolhe.\n"))

    # (b) a D19c foi reproduzida na régua dela? Pergunta que só existe na M4:
    # é lá que a medição publicada está. Em outro mercado a linha de nível é
    # candidata nova, e afirmar que "a D19c se reproduz" seria falso.
    if mercado == M4:
        texto.append(
        f"**A D19c se reproduz aqui?** Na régua dela (OLS h = {H_OLS}, "
        f"critério forte), a discordância contra o livro direcional "
        + ("**gira de sinal** entre as metades — é o achado da D19c, "
           "reencontrado com o livro de duas pernas em vez de só o SPY.\n"
           if d_spy[regua_ols] else
           "🛑 **NÃO gira** pelo critério dela. O giro publicado é do **SPY "
           "sozinho**, e não sobrevive quando as duas pernas do livro "
           "declarado (`SPY/TLT`) têm de girar juntas com significância. Isto "
           "não desmente a D19c — mede o alcance dela, e é um resultado que "
           "este script não estava procurando.\n"))

    # (c) a célula nova que decide entre (1) e (2)
    texto.append(
        f"**O NÍVEL (`{disc}`) contra o livro NEUTRO** — a célula que separa as "
        "duas explicações — "
        + " · ".join(f"{r.split(' (')[0]}: {'🛑 gira' if g else 'não gira'}"
                     for r, g in d_neutro.items()) + ".\n")

    # As duas MARGINAIS do 2×2. É o que separa "o livro explica" de "a
    # transformação explica", e nenhuma das duas explicações pré-registradas
    # olha para as marginais — elas foram escritas supondo que só um fator
    # importava. Sai medido para o caso de o dado não escolher nenhuma delas.
    # As marginais saem SEPARADAS por régua. Somar as duas num contador só
    # misturaria o critério fraco (a única coisa que o G2 suporta) com o forte,
    # e o total passaria a depender de qual régua tem mais células — que é
    # escolha de tabela, não medida.
    def marca(regua, filtro):
        alvo = [(k, v) for k, v in medidas.items() if k[0] == regua and filtro(k)]
        gira = sum(1 for k, v in alvo if (v[2] if regua == regua_ols else v[1]))
        return gira, len(alvo)

    def marginais(regua):
        return ({g: marca(regua, lambda k, g=g: grupo_do_sinal[k[1]] == g)
                 for g in ("nível", "incremento")},
                {nome: marca(regua, lambda k, nome=nome: k[2] == nome)
                 for nome in livros})

    texto.append("\n**As marginais do 2×2 — quantas células giram, por régua:**\n")
    texto.append("| corte | " + " | ".join(
        f"{r.split(' (')[0]} ({'forte' if r == regua_ols else 'fraco'})"
        for r in (regua_g2, regua_ols)) + " |")
    texto.append("|---|---|---|")
    marg = {r: marginais(r) for r in (regua_g2, regua_ols)}
    for rotulo in list(marg[regua_g2][0]) + list(marg[regua_g2][1]):
        celulas = []
        for r in (regua_g2, regua_ols):
            grupos, livros_marg = marg[r]
            gira, total = (grupos | livros_marg)[rotulo]
            celulas.append(f"**{gira} de {total}**")
        texto.append(f"| {rotulo} | " + " | ".join(celulas) + " |")
    texto.append("")

    # O veredito sai da régua FORTE — é a única em que o critério é o da D19c.
    # A régua do G2 entra como corroboração, e as células de incremento que ela
    # marca saem NOMEADAS: esconder as exceções da marginal seria escrever a
    # conclusão em cima de um total conveniente.
    por_grupo, por_livro = marg[regua_ols]
    nivel_gira = por_grupo["nível"][0] > 0
    incremento_gira = por_grupo["incremento"][0] > 0
    livro_concentra = (min(g for g, _t in por_livro.values()) == 0
                       and max(g for g, _t in por_livro.values()) > 0)
    excecoes = [f"{k[1]} × {k[2].split(' (')[0]}" for k, v in medidas.items()
                if k[0] == regua_g2 and v[1]
                and grupo_do_sinal[k[1]] == "incremento"]
    if excecoes:
        texto.append(
            "⚠️ **As exceções, nomeadas:** no G2 (critério fraco) o grupo de "
            "incremento não sai limpo — giram " + " · ".join(
                f"`{e}`" for e in excecoes) + ". Nenhuma delas é a sleeve no "
            "livro dela, mas o total da marginal não deve ser lido como zero.\n")

    if nivel_gira and not incremento_gira and not livro_concentra:
        texto.append(
            "➡ **Nenhuma das duas explicações pré-registradas.** O giro não se "
            "concentra num livro (aparece nos dois), logo não é o canal de "
            f"direção — cai a explicação (1). E não aparece no sinal de "
            f"INCREMENTO em livro nenhum, logo não é \"o mercado {mercado} é "
            "instável\" — cai a explicação (2), que exigiria a sleeve girando "
            "também.\n\n"
            "**O eixo é a TRANSFORMAÇÃO do sinal.** O NÍVEL da crença tem "
            "relação instável com os retornos; o INCREMENTO não. Isso tem "
            "mecanismo, e ele é banal: um nível que sobe e desce ao longo da "
            "amostra fica correlacionado com o que o mercado fez em cada "
            "regime, e o coeficiente ajustado vira uma afirmação sobre o "
            "regime, não sobre o mecanismo. Diferenciar remove isso por "
            "construção.\n\n"
            f"**Consequência para a candidata {mercado}:** a objeção publicada "
            "contra este mercado mede o NÍVEL e a sleeve lê o INCREMENTO — as "
            "duas medições estão certas e não se contradizem. A objeção deixa "
            "de valer contra a sleeve e passa a ser uma **limitação a "
            "declarar**: neste mercado, qualquer view que leia NÍVEL está "
            "medindo regime.\n")
    elif livro_concentra and not incremento_gira:
        texto.append(
            "➡ **Explicação (1): a instabilidade mora no canal de direção.** O "
            "giro se concentra num livro só, e a sleeve hedgeia exatamente "
            f"esse canal. A objeção deixa de valer contra a sleeve {mercado} e "
            "passa a ser mecanismo A FAVOR dela.\n")
    elif incremento_gira:
        texto.append(
            "➡ **Explicação (2): a instabilidade mora no mercado.** O giro "
            "alcança também o sinal de incremento, que é o da sleeve — trocar "
            f"de livro ou de transformação não resolve. A sleeve {mercado} "
            "sobreviveu ao corte lendo outra fatia do mesmo dado instável, e "
            "sobreviver a horizontes vizinhos não protege contra isso, porque "
            "é a mesma amostra.\n")
    else:
        texto.append(
            "➡ **Nada gira pelo critério forte**, nem o nível nem o "
            "incremento. Nesta régua o teste não separa as duas medições — a "
            "diferença entre a D19c e a D27 não está no 2×2 medido aqui.\n")

    # (d) de qual perna do nível vem o giro, se vier
    for rotulo, apelido in [(r, a) for r, a in
                            (("z(poly) — só a perna do Polymarket", "o Polymarket"),
                             ("z(−spread) — só a perna do mercado",
                              "a curva de juros"))
                            if r in grupo_do_sinal]:
        texto.append(f"**De onde vem o giro do nível — {apelido}:** " + " · ".join(
            f"{nome.split(' (')[0]} — "
            + ", ".join(f"{r.split(' (')[0]}: {'🛑 gira' if g else 'não gira'}"
                        for r, g in gira_em(rotulo, nome).items())
            for nome in livros) + ".")
    texto.append("")

    # (e) a sleeve, na régua em que NÃO foi aprovada
    for k in lookbacks:
        rotulo = f"Δp k = {k} (o sinal da sleeve)"
        c_g2, gira_g2, _ = medidas[(regua_g2, rotulo, neutro)]
        c_ols, _, gira_ols = medidas[(regua_ols, rotulo, neutro)]
        texto.append(
            f"**A sleeve (Δp k = {k}, livro neutro) fora da régua em que foi "
            f"aprovada:** no G2 as metades saem "
            + ("✅✅" if c_g2["1ª metade"][0] and c_g2["2ª metade"][0] else "mistas")
            + f" (giro: {'🛑 sim' if gira_g2 else 'não'}); na régua da D19c "
            f"(h = {H_OLS}) o veredito da amostra inteira é "
            f"{'✅' if c_ols['inteira'][0] else '❌'} e o giro forte é "
            f"{'🛑 sim' if gira_ols else 'não'}.")
    reprova_h = [k for k in lookbacks
                 if not medidas[(regua_ols, f"Δp k = {k} (o sinal da sleeve)",
                                 neutro)][0]["inteira"][0]]
    if reprova_h:
        texto.append(
            f"\n⚠️ **Limitação que sai junto, e não é pequena:** em "
            f"k = {', '.join(str(k) for k in reprova_h)} a sleeve **reprova a "
            f"premissa em h = {H_OLS}** na amostra inteira. Ela é estável, mas "
            f"a vantagem que o G2 mede vive na janela de **1 pregão** e não se "
            f"estende a dez. Estabilidade não é o mesmo que alcance, e o G4 — "
            f"quando rodar — vai medir a segunda coisa, não a primeira.")
    texto.append("")

    # O bloco de ressalvas é PARAMETRIZADO. A versão anterior afirmava, em
    # qualquer mercado, que "não existe mercado irmão" — verdade só na M4, e
    # falsa justamente na M9, que tem irmão e reproduziu nele. Frase colada de
    # um mercado para outro é a quinta ocorrência do modo de falha "registro
    # que envelhece não levanta exceção" (D27), e aqui nasceria velha.
    texto.append(
        "**O que isto NÃO diz:** nada sobre P&L (o G4 continua sem rodar para "
        "nada), e nada sobre comparações múltiplas — as ~200 células da D27 "
        "seguem sem correção."
        + (" **Este mercado não tem irmão** (D18d), então o corte em metades "
           "é o único fora-da-amostra que ele pode ter."
           if mercado == M4 else
           " O teste de **mercado irmão** deste mercado é assunto do "
           "`Gate_mercados_irmaos.md`, não deste artefato."))
    if mercado == M4:
        texto.append(
            f"\nA correlação de **{corr_p:+.3f}** entre as duas séries de `p` "
            + ("**confirma** que a escolha da construção do `p` não é o que "
               "separa as duas medições.\n" if corr_p > 0.9 else
               "🛑 **é baixa o bastante para ser ela própria uma explicação** "
               "— parte da diferença entre a D19c e a D27 pode ser a "
               "construção do `p`, não a transformação nem o livro.\n"))
    else:
        # Fora da M4 as duas séries são o MESMO objeto (não há normalização
        # concorrente), então a correlação é tautológica e não vira frase.
        texto.append("")

    Path(Path(args.raiz) / saida).write_text("\n".join(texto) + "\n",
                                                  encoding="utf-8")
    sys.stdout.write(tabela.to_string(index=False) + "\n\n")
    sys.stdout.write(f"corr(p_norm, p_cru) = {corr_p:+.3f}\n")
    sys.stdout.write(f"escrito: {saida}\n")


if __name__ == "__main__":
    main()
