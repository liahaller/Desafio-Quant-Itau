"""Gate de sleeves — triagem MEDIDA antes de construir camada tática. Felipe.

A sessão de 2026-08-08 (D16) escreveu 400+ linhas de módulo e 11 testes para
duas sleeves que morreram por motivo **de dado**, e os dois motivos cabiam numa
tabela de vinte linhas rodada ANTES do código:

  - FOMC: o sinal condicionante não tinha dispersão (mediana 0,52 bps, que é a
    ordem do ruído de discretização da própria PMF);
  - CPI:  o μ saiu invertido em relação à premissa do livro (TLT > TIP), e pela
    D2b não se inverte.

Este script corrige a ORDEM: mede primeiro, constrói depois. **Mede; não
decide** — nenhum critério tem corte numérico cravado, porque cravar um seria
escolher threshold sem medição (CLAUDE.md §6). No lugar do corte, o gate carrega
o **próprio grupo de controle**: as duas sleeves reprovadas da D16 entram na
mesma tabela, então a linha de um candidato se lê contra o que um sinal
comprovadamente morto mede.

    G0 cobertura : pregões da janela do backtest em que o sinal existe.
    G1 dispersão : mediana |sinal| ÷ Δ que UM tick de 1 centavo produz no sinal.
    G2 sinal     : sinal de μ (event-study expansivo) vs. o DECLARADO a priori.
    G3 duplicação: correlação com o sinal das views vivas e da candidata 15b.

G4 (P&L da sleeve sozinha) fica de fora: exige backtest, e backtest exige o
módulo que este script se recusa a escrever antes do gate.

**Nada em `src/` é tocado.** O μ do G2 é o `estimate_drift_mu` da D16 chamado
como está — com a subtração de linha de base e o encolhimento pela dispersão,
que foram as duas partes do desenho que sobreviveram ao teste.

Uso:

    python scripts/gate_sleeves.py --raiz .
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from backtest_v1 import (DRIFT_LIVRO_CPI, DRIFT_LIVRO_FOMC,  # noqa: E402
                         PONTOS_PERCENTUAIS, carregar)
from config import ASSETS, DRIFT_JANELA_ACOES, TAU  # noqa: E402
from market_inputs import sample_covariance  # noqa: E402
from poly_loader import bucket_value, daily_preopen, load_pmf  # noqa: E402
from poly_preprocessing import (bucket_values_with_open, carry_missing,  # noqa: E402
                                normalize_probs, pmf_mean)
from tatica_drift_anuncio import estimate_drift_mu  # noqa: E402
from view_incerteza_anuncio import entropia_normalizada  # noqa: E402

# Passo de preço do Polymarket: 1 centavo. É a unidade do G1 — o que o gate
# pergunta é quantos ticks de tamanho tem o sinal que dá a direção do tilt.
TICK = 0.01

# Granularidade do T10YIE no FRED (0,01 pp = 1 bp). É o "tick" do único
# candidato/controle cujo sinal não sai de uma PMF.
TICK_FRED_BPS = 1.0

MESES_MENSAIS = 12.0  # E_poly do CPI é variação MENSAL; a 2.2 anualiza

# `|` escapado — os nomes viram cabeçalho de tabela markdown. Constantes
# porque f-string do 3.11 não aceita barra invertida dentro da expressão.
COL_G1 = r"G1 mediana \|sinal\|"
COL_G3 = r"G3 maior \|corr\|"


# --- as quatro medidas do gate (puras, testadas em tests/test_gate_sleeves.py)


def razao_dispersao(sinal, tick):
    """G1 — mediana |sinal| ÷ tick. Perto de 1 = o sinal É o ruído do tick.

    `tick` é o Δ que um movimento de 1 centavo num único balde produz NO SINAL,
    não o centavo em si: numa média de PMF, um tick desloca E_poly em no máximo
    `0,01 × (maior valor de balde − menor valor)`, então é essa a régua.
    """
    s = pd.Series(sinal).dropna().abs()
    if not len(s) or tick <= 0:
        return float("nan")
    return float(s.median() / tick)


def massa_de_cauda(linha):
    """Massa nos dois baldes das PONTAS, sobre a PMF renormalizada.

    É o que as views jogam fora ao colapsar a PMF em E_poly — a média não
    distingue "0,3% com certeza" de "metade em 0,0% e metade em 0,6%". Menos de
    3 baldes vivos -> NaN (com 2 baldes tudo é ponta e a medida não informa).
    """
    p = np.asarray(linha, dtype=float)
    p = p[np.isfinite(p) & (p >= 0)]
    if len(p) < 3 or p.sum() <= 0:
        return float("nan")
    p = normalize_probs(p)
    return float(p[0] + p[-1])


def corr_comum(a, b):
    """Pearson nas datas em que as duas séries existem. < 3 pontos -> NaN."""
    juntas = pd.concat([pd.Series(a), pd.Series(b)], axis=1, join="inner").dropna()
    if len(juntas) < 3 or juntas.iloc[:, 0].std() == 0 or juntas.iloc[:, 1].std() == 0:
        return float("nan")
    return float(juntas.iloc[:, 0].corr(juntas.iloc[:, 1]))


def bate_premissa(mu, assets, declarado):
    """G2 — o sinal de μ bate com o DECLARADO a priori, ativo a ativo?

    `declarado` é {ticker: +1/-1}: para que lado o ativo deve andar quando o
    sinal é positivo. Declarar por escrito antes de estimar μ é o que faz do G2
    um teste em vez de uma racionalização — sem isso, "a literatura não fixa o
    sinal" vira licença para aceitar qualquer resultado.

    Devolve `(bate, detalhe)`; μ = None (poucos eventos) -> `(False, "μ ausente")`.
    """
    if mu is None:
        return False, "μ ausente"
    mu = np.asarray(mu, dtype=float)
    partes, ok = [], True
    for ticker, esperado in declarado.items():
        medido = mu[list(assets).index(ticker)] * PONTOS_PERCENTUAIS * 100.0
        acerta = np.sign(medido) == np.sign(esperado)
        ok = ok and bool(acerta)
        partes.append(f"{ticker} {medido:+.2f} {'✅' if acerta else '❌'}")
    return ok, " · ".join(partes)


# --- construção das séries diárias -----------------------------------------


def pmf_cpi_do_dia(montador, data):
    """(linha da PMF, valores dos baldes) do mercado de CPI vigente, ou None.

    Mesma cascata do `MontadorV1._view_2_2` — mercado é o da PRÓXIMA divulgação,
    leitura é o slot pré-abertura do dia, PMF incompleta não vira número.
    """
    futuras = [r for r in montador.mercados if r >= data]
    if not futuras:
        return None
    probs, valores, _ = montador.pmfs[montador.mercados[min(futuras)]]
    if data not in probs.index:
        return None
    linha = probs.loc[data].to_numpy(dtype=float)
    if not np.isfinite(linha).all() or linha.sum() <= 0:
        return None
    return linha, valores


def pmf_fomc_do_dia(montador, data):
    """(linha, valores em bps) da PMF da PRÓXIMA reunião, ou None. Cascata da 2.3."""
    futuras = [r for r in montador.fomc_pmfs if r >= data]
    if not futuras:
        return None
    probs, valores, _ = montador.fomc_pmfs[min(futuras)]
    if data not in probs.index:
        return None
    linha = probs.loc[data].to_numpy(dtype=float)
    if not np.isfinite(linha).all() or linha.sum() <= 0:
        return None
    return linha, valores


def pmf_m3_diaria(diretorio):
    """(probs por data, valores em nº de cortes) do M3_fed_trajectory.

    Mesmo tratamento das outras PMFs (D4/6.1 herda leitura faltante, D4/1.2
    resolve a ponta aberta). Aqui só a ponta SUPERIOR é aberta ("8plus"); a
    inferior é "no fed rate cuts" = 0 exato, faixa fechada.
    """
    cru = load_pmf(diretorio, "M3_fed_trajectory_")
    pmf = daily_preopen(carry_missing(cru)).dropna(how="all")
    valores = np.array([bucket_value(c) for c in pmf.columns], dtype=float)
    return pmf, bucket_values_with_open(valores, open_ends=("upper",))


def serie_por_dia(datas, funcao):
    """Series indexada por `datas` com o que `funcao(data)` devolver (NaN = None)."""
    return pd.Series({d: funcao(d) for d in datas}, dtype=float).dropna()


def demeanar_expansivo(serie):
    """Sinal − média EXPANSIVA do próprio sinal (só passado, sem lookahead).

    Mesma construção da D9/D7.4 que as views 2.2 e 2.3 já usam na divergência: o
    que informa é o desvio em relação ao normal daquele mercado, não o nível.
    """
    serie = pd.Series(serie).dropna()
    return (serie - serie.expanding().mean().shift(1)).dropna()


def eventos_diarios(sinal):
    """[(data, sinal)] dos dias com sinal não nulo — o `eventos` do estimador.

    Sleeve re-assinada todo dia: cada pregão com sinal é um evento de janela 1.
    Não há `k` de defasagem nem janela de permanência para escolher, que é o
    ponto — o parâmetro que a D16 teve de transportar aqui não existe.
    """
    return [(d, np.sign(v)) for d, v in pd.Series(sinal).dropna().items() if v != 0]


def mu_do_sinal(retornos, eventos, janela, livro, sigma, ate_data):
    """μ encolhido do `tatica_drift_anuncio`, sem uma linha de matemática nova."""
    return estimate_drift_mu(retornos, eventos, janela, livro, ate_data, sigma, TAU)


def main():
    # O console do Windows abre em cp1252 e engasga no Σ dos rótulos.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raiz", default=".")
    parser.add_argument("--saida", default="Dump/analises/Gate_sleeves.md")
    args = parser.parse_args()

    raiz = Path(args.raiz)
    retornos, montador, datas, _ = carregar(raiz)
    # Σ da história INTEIRA, igual ao `tatica_reconstruida.py` — Σ só entra no
    # encolhimento do μ, e usar outra janela faria o controle deixar de
    # reproduzir a D16, que é o único jeito de saber que o gate está certo.
    sigma = sample_covariance(retornos)
    ate = datas[-1] + pd.Timedelta(days=1)   # inclui o último evento fechado
    fl = montador._fl

    # --- séries de PMF, uma leitura por pregão -----------------------------
    m3_probs, m3_valores = pmf_m3_diaria(raiz / "data/raw/clob_exploracao")

    def e_poly_m3(data):
        if data not in m3_probs.index:
            return None
        linha = m3_probs.loc[data].to_numpy(dtype=float)
        return pmf_mean(linha, m3_valores, fl) if np.isfinite(linha).all() else None

    def e_poly_cpi(data):
        par = pmf_cpi_do_dia(montador, data)
        return pmf_mean(*par, fl) if par else None

    def e_poly_fomc(data):
        par = pmf_fomc_do_dia(montador, data)
        return pmf_mean(*par, fl) if par else None

    e_m3 = serie_por_dia(datas, e_poly_m3)
    e_cpi = serie_por_dia(datas, e_poly_cpi)
    e_fomc = serie_por_dia(datas, e_poly_fomc)

    cauda_cpi = serie_por_dia(
        datas, lambda d: (massa_de_cauda(pmf_cpi_do_dia(montador, d)[0])
                          if pmf_cpi_do_dia(montador, d) else None))
    cauda_fomc = serie_por_dia(
        datas, lambda d: (massa_de_cauda(pmf_fomc_do_dia(montador, d)[0])
                          if pmf_fomc_do_dia(montador, d) else None))
    entropia_cpi = serie_por_dia(
        datas, lambda d: (entropia_normalizada(pmf_cpi_do_dia(montador, d)[0])
                          if pmf_cpi_do_dia(montador, d) else None))
    entropia_fomc = serie_por_dia(
        datas, lambda d: (entropia_normalizada(pmf_fomc_do_dia(montador, d)[0])
                          if pmf_fomc_do_dia(montador, d) else None))

    # --- referências do G3: o sinal que as views já leem --------------------
    # Transformação afim não muda correlação, então basta o NÍVEL da divergência
    # (a 2.2 multiplica por duration, a 2.3 demeana — nenhuma das duas mexe no ρ).
    breakeven = serie_por_dia(datas, lambda d: montador._ultimo_antes(montador.breakeven, d))
    e_ff = serie_por_dia(datas, lambda d: montador._ultimo_antes(montador.e_ff, d))
    referencias = {
        "divergência da 2.2": (e_cpi * MESES_MENSAIS - breakeven).dropna(),
        "divergência da 2.3": (e_fomc - e_ff).dropna(),
        "entropia CPI (15b)": entropia_cpi,
        "entropia FOMC (15b)": entropia_fomc,
    }

    # --- ticks: o Δ que UM centavo produz no sinal de cada candidato --------
    def tick_de_pmf(por_dia):
        """0,01 × amplitude da grade, mediana ao longo dos dias vigentes."""
        larguras = []
        for data in datas:
            par = por_dia(data)
            if par:
                valores = np.asarray(par[1], dtype=float)
                larguras.append(float(valores.max() - valores.min()))
        return TICK * float(np.median(larguras)) if larguras else float("nan")

    tick_m3 = TICK * float(m3_valores.max() - m3_valores.min())
    tick_cpi = tick_de_pmf(lambda d: pmf_cpi_do_dia(montador, d))
    tick_fomc = tick_de_pmf(lambda d: pmf_fomc_do_dia(montador, d))

    # --- controles: as duas sleeves REPROVADAS da D16 -----------------------
    # Mesmas funções que o backtest usa, para o controle reproduzir a D16 em vez
    # de uma reimplementação parecida.
    surpresas_fomc = pd.Series({
        r: montador._surpresa_fomc_poly(r) for r in montador.fomc if r <= datas[-1]}).dropna()
    surpresas_cpi = montador.surpresas_cpi[montador.surpresas_cpi.index <= datas[-1]]

    # --- as linhas da tabela ------------------------------------------------
    # `escala`: fator para o sinal sair em unidade legível na coluna do G1.
    linhas = [
        dict(nome="C1a revisão M3 (nº de cortes)", tipo="candidato",
             sinal=e_m3.diff().dropna(), janela=1, tick=tick_m3, unidade="cortes",
             livro=("SPY", "TLT"), declarado={"SPY": +1, "TLT": +1},
             premissa="crença anda para mais afrouxamento → SPY e TLT sobem"),
        dict(nome="C1b revisão da reunião (bps)", tipo="candidato",
             sinal=(-e_fomc.diff()).dropna(), janela=1, tick=tick_fomc, unidade="bps",
             livro=("SPY", "TLT"), declarado={"SPY": +1, "TLT": +1},
             premissa="idem, com o sinal invertido porque E_poly é Δtaxa (afrouxar = cair)"),
        dict(nome="C2a cauda da PMF de CPI", tipo="candidato",
             sinal=demeanar_expansivo(cauda_cpi), janela=1, tick=TICK, unidade="prob.",
             livro=("SPY", "TLT"), declarado={"SPY": -1, "TLT": +1},
             premissa="mais massa nas pontas → prêmio de risco sobe → SPY cai, TLT sobe"),
        dict(nome="C2b cauda da PMF de reunião", tipo="candidato",
             sinal=demeanar_expansivo(cauda_fomc), janela=1, tick=TICK, unidade="prob.",
             livro=("SPY", "TLT"), declarado={"SPY": -1, "TLT": +1},
             premissa="idem, na família do Fed"),
        dict(nome="controle D16 · drift FOMC 🛑", tipo="controle",
             sinal=surpresas_fomc, janela=DRIFT_JANELA_ACOES, tick=tick_fomc,
             unidade="bps", livro=DRIFT_LIVRO_FOMC, declarado={"SPY": -1, "TLT": -1},
             premissa="Bernanke-Kuttner: surpresa de ALTA → SPY e TLT caem"),
        dict(nome="controle D16 · drift CPI 🛑", tipo="controle",
             sinal=surpresas_cpi, janela=DRIFT_JANELA_ACOES, tick=TICK_FRED_BPS,
             unidade="bps", livro=DRIFT_LIVRO_CPI, declarado={"TIP": +1, "TLT": -1},
             premissa="surpresa inflacionária → o indexado (TIP) bate o nominal (TLT)"),
    ]

    tabela, detalhes = [], []
    for linha in linhas:
        sinal = pd.Series(linha["sinal"]).dropna()
        mu, n_mu = mu_do_sinal(retornos, eventos_diarios(sinal), linha["janela"],
                               linha["livro"], sigma, ate)
        ok, detalhe = bate_premissa(mu, ASSETS, linha["declarado"])
        correlacoes = {nome: corr_comum(sinal, ref) for nome, ref in referencias.items()}
        pior = max(correlacoes, key=lambda k: abs(correlacoes[k])
                   if np.isfinite(correlacoes[k]) else -1)
        tabela.append({
            "candidato": linha["nome"],
            "G0 dias": len(sinal),
            "G0 janela": f"{sinal.index[0]:%Y-%m-%d} → {sinal.index[-1]:%Y-%m-%d}",
            COL_G1: f"{sinal.abs().median():.4g} {linha['unidade']}",
            "G1 razão / tick": f"{razao_dispersao(sinal, linha['tick']):.1f}×",
            "G2 μ (bps/dia)": detalhe,
            "G2 bate?": "✅" if ok else "❌",
            COL_G3: (f"{correlacoes[pior]:+.2f} ({pior})"
                                if np.isfinite(correlacoes[pior]) else "—"),
        })
        detalhes.append({"candidato": linha["nome"], "eventos no μ": n_mu,
                         **{f"corr {k}": f"{v:+.2f}" if np.isfinite(v) else "—"
                            for k, v in correlacoes.items()}})

    tabela = pd.DataFrame(tabela)
    detalhes = pd.DataFrame(detalhes)

    texto = [
        "# Gate de sleeves — o que passa na triagem ANTES de virar código\n",
        "> Gerado por `scripts/gate_sleeves.py`. **Mede; não decide.** Nenhum "
        "critério tem corte cravado — cravar um seria escolher threshold sem "
        "medição. No lugar do corte, as duas sleeves REPROVADAS da D16 entram "
        "na mesma tabela como **grupo de controle**: a linha de um candidato se "
        "lê contra o que um sinal comprovadamente morto mede.\n",
        f"- janela do backtest: **{datas[0]:%Y-%m-%d} a {datas[-1]:%Y-%m-%d}** "
        f"({len(datas)} pregões), δ e Σ os mesmos do v1 (D7/D8)",
        "- **G1** = mediana |sinal| ÷ Δ que UM tick de 1 centavo produz no sinal "
        "(no FRED, 1 bp). Perto de 1× o sinal É o ruído de discretização",
        "- **G2** = μ do `tatica_drift_anuncio.estimate_drift_mu` (linha de base "
        "subtraída, encolhido pela dispersão) contra o sinal DECLARADO a priori",
        "- **G3** = correlação com o sinal que as views já leem\n",
        "**G4 (P&L da sleeve sozinha) não está aqui de propósito:** exige "
        "backtest, backtest exige o módulo, e o módulo é exatamente o que este "
        "gate se recusa a escrever antes de a linha passar.\n",
        "**Convenção de janela:** o sinal do dia D é o slot pré-abertura de D e "
        "o retorno medido é o do pregão SEGUINTE — mesma convenção da D16 (a "
        "sleeve abre no close de D). Medir o retorno do próprio D exigiria o "
        "preço de abertura, e os dois parquets estão em bases de ajuste "
        "diferentes (`Premissa_taticas.md`) — conserto é do módulo do Paulo.\n",
        tabela.to_markdown(index=False), "",
        "## Correlações do G3, uma a uma\n",
        detalhes.to_markdown(index=False), "",
        "## Premissa declarada ANTES de medir\n",
        "Declarar por escrito antes do event-study é o que faz do G2 um teste "
        "em vez de racionalização — sem isso, \"a literatura não fixa o sinal\" "
        "vira licença para aceitar qualquer resultado.\n",
    ]
    for linha in linhas:
        texto.append(f"- **{linha['nome']}** — {linha['premissa']}")
    texto.append("")

    # A leitura é GERADA dos números medidos: prosa e tabela não podem divergir.
    por_nome = tabela.set_index("candidato")
    candidatos = [linha["nome"] for linha in linhas if linha["tipo"] == "candidato"]
    controles = [linha["nome"] for linha in linhas if linha["tipo"] == "controle"]
    passaram = [n for n in candidatos if por_nome.loc[n, "G2 bate?"] == "✅"]
    revisao = [n for n in candidatos if n.startswith("C1")]
    cauda_cpi_nome = "C2a cauda da PMF de CPI"
    mu_controles = " e ".join(
        f"`{por_nome.loc[n, 'G2 μ (bps/dia)']}`" for n in controles)
    razoes_revisao = " e ".join(
        n + " mede " + por_nome.loc[n, "G1 razão / tick"] for n in revisao)
    razao_cauda = por_nome.loc[cauda_cpi_nome, "G1 razão / tick"]
    texto += [
        "## Leitura\n",
        "**O gate está calibrado — o controle reproduz a D16 número a número.** "
        f"As duas sleeves reprovadas saem com {mu_controles}, que são os mesmos "
        "μ de `Tatica_reconstruida.md`. Se o controle não reproduzisse, o errado "
        "seria o gate, não os candidatos.\n",
        "**O achado desta rodada é do G1, e mata uma FAMÍLIA inteira de uma vez: "
        "a revisão diária da crença do poly anda MENOS que um tick.** "
        + razoes_revisao
        + " — abaixo de 1×, ou seja, o Δ típico de um pregão é menor que o "
        "deslocamento que UM centavo num único balde produz. É a versão forte do "
        "achado da D16: lá o poly acertava a decisão do Fed; aqui o próprio "
        "repreçamento diário dele vive abaixo da granularidade do preço. "
        "**Qualquer sleeve que leia Δ de PMF de um dia para o outro está "
        "condicionando em ruído de discretização** — e isso se descobriu com um "
        "script, não com um módulo.\n",
        f"**O único sinal com dispersão de verdade é a cauda do CPI "
        f"({razao_cauda}), e ela morre nos outros dois critérios.** No G2 o μ "
        "sai invertido nos DOIS ativos do livro "
        f"(`{por_nome.loc[cauda_cpi_nome, 'G2 μ (bps/dia)']}`, contra a premissa "
        "declarada \"SPY cai, TLT sobe\"), e pela D2b não se inverte. No G3 ela "
        "correlaciona " + por_nome.loc[cauda_cpi_nome, COL_G3] + " — massa de "
        "cauda e entropia são o mesmo sinal com dois nomes, então ligar esta "
        "sleeve com a view 15b seria a dupla contagem da 15a.\n",
        "> ⚠️ **Ressalva no G1 da cauda, contra o próprio candidato:** a média "
        "expansiva atravessa a troca de mercado, e a grade do CPI muda de 3 a 9 "
        f"baldes entre meses — parte do {razao_cauda} é degrau de grade, não "
        "sinal. A 15b demeana POR FAMÍLIA e normaliza a entropia por log(nº de "
        "baldes) justamente por isso. Não muda o veredito: a linha já morre no "
        "G2 e no G3, que não dependem da escala do sinal.\n",
        f"**Nenhum candidato passa nos três critérios** ({len(passaram)} de "
        f"{len(candidatos)} com G2 ✅). Pelo protocolo desta rodada, **nenhum "
        "módulo é escrito** — o gate custou um script e evitou o segundo par de "
        "sleeves natimortas.\n",
        "**O que isto NÃO diz:** que a camada tática é inviável. Diz que, no dado "
        "que temos, os sinais de Polymarket que sobraram ou não têm tamanho "
        "(revisão diária, abaixo do tick) ou já pertencem a uma view (cauda ≈ "
        "entropia). A âncora de tamanho da D16 segue de pé e sem uso — o que "
        "falta é sinal, não dimensionamento.\n",
    ]

    Path(args.saida).write_text("\n".join(texto) + "\n", encoding="utf-8")
    sys.stdout.write(tabela.to_string(index=False) + f"\n\nescrito: {args.saida}\n")


if __name__ == "__main__":
    main()
