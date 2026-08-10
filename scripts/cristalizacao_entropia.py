"""Cristalização da PMF por distância ao evento — o que ela faz com a 1.3. Felipe.

Traduz para o meu módulo o achado (b) da Lia (resposta de 2026-08-10): a
proximidade do evento reprovou como ingrediente da régua dela com folga grande
(+0,29 a +0,72 no alvo por desfecho), e o sinal é **longe do evento o mercado
se move mais; perto, ele cristaliza**. Para a régua isso é "candidata fora".
Para a tática 1.3 é outra coisa: o sinal dela é a entropia da PMF medida no
slot pré-abertura do PRÓPRIO dia do anúncio — ou seja, exatamente na janela em
que a cristalização estaria acontecendo.

A pergunta que este script mede, e é a única que interessa ao desenho:
**sobra variação no sinal onde a sleeve o lê?** `dw[SPY] = orcamento * sinal`
só é modulação se o `sinal` diferir entre anúncios; se a cristalização o
comprime a um valor quase constante em d = 0, a sleeve degenera em long SPY
fixo em dia de anúncio — que é outra tática, com outra justificativa.

Duas medidas por dia, as duas no slot pré-abertura (`daily_preopen`):

  - **entropia normalizada** — o sinal da 1.3, em [0, 1].
  - **variação total** `Σ|p(d) − p(d−1)|` — a mesma grandeza do ingrediente
    que entrou na régua da Lia, medida aqui do meu lado. É ela que responde à
    afirmação dela ("longe se move mais") no meu dado.

Controle obrigatório, e não é detalhe: a entropia é normalizada por
log(nº de baldes VIVOS), e balde morre quando a probabilidade zera — o que
acontece justamente perto do evento. Queda de entropia com denominador
encolhendo pode ser artefato, então o nº mediano de baldes vivos entra na
tabela ao lado. Sem essa coluna a leitura não é auditável.

MEDE — não liga, não desliga e não escolhe orçamento (CLAUDE.md §6).

Uso:
    python scripts/cristalizacao_entropia.py --dados <dir raw> --precos <parquet>
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from poly_loader import (daily_preopen, load_cpi_releases,  # noqa: E402
                         load_payroll_releases, load_pmf)
from premio_condicional import (PREFIXO_FOMC, mercados_de_payroll,  # noqa: E402
                                prefixos_cpi)
from view_incerteza_anuncio import entropia_normalizada  # noqa: E402

# Bordas em DIAS CORRIDOS antes do evento. d = 0 é o slot que a 1.3 lê; as
# demais faixas crescem porque a densidade de leitura cai com a distância.
FAIXAS = [(0, 0), (1, 2), (3, 5), (6, 10), (11, 20), (21, 60)]


def medidas_por_dia(pmf_diaria):
    """(entropia, variacao, n_baldes) por data, no slot pré-abertura.

    `pmf_diaria` : DataFrame (data x balde) — saída de `daily_preopen`.

    `variacao` é `Σ|p(d) − p(d−1)|` e só existe quando a data anterior é o dia
    corrido imediatamente anterior: com buraco no meio a diferença mede vários
    dias e não é comparável com as demais. Sem par adjacente -> NaN, nunca
    zero (zero diria "não se moveu", que é afirmação diferente de "não medi").
    """
    pmf = pd.DataFrame(pmf_diaria).sort_index()
    entropia = pmf.apply(entropia_normalizada, axis=1)
    # baldes VIVOS = os que entram no denominador log(n) da entropia
    n_baldes = (np.isfinite(pmf) & (pmf > 0)).sum(axis=1)
    variacao = pmf.diff().abs().sum(axis=1, skipna=True)
    adjacente = pmf.index.to_series().diff() == pd.Timedelta(days=1)
    return pd.DataFrame({"entropia": entropia,
                         "variacao": variacao.where(adjacente),
                         "n_baldes": n_baldes})


def com_distancia(medidas, data_evento):
    """Anexa `dias` = dias corridos ATÉ o evento, descartando o que vem depois.

    Leitura posterior ao anúncio não é insumo de tática nenhuma (o resultado já
    saiu), então sai da amostra em vez de virar faixa negativa.
    """
    dias = (pd.Timestamp(data_evento) - medidas.index).days
    saida = medidas.assign(dias=dias)
    return saida[saida["dias"] >= 0]


def perfil(quadro, faixas=FAIXAS):
    """Agrega por faixa de distância: n, entropia (média/desvio), variação, baldes.

    O desvio da entropia é o número que decide o desenho da 1.3 — é a
    dispersão do sinal ENTRE anúncios naquela distância. Média baixa com
    desvio baixo = sleeve sem modulação.
    """
    linhas = []
    for lo, hi in faixas:
        fatia = quadro[(quadro["dias"] >= lo) & (quadro["dias"] <= hi)]
        entropia = fatia["entropia"].dropna()
        linhas.append({
            "faixa": f"d = {lo}" if lo == hi else f"{lo}–{hi} dias",
            "n": len(entropia),
            "entropia média": entropia.mean() if len(entropia) else np.nan,
            "entropia desvio": entropia.std(ddof=1) if len(entropia) > 1 else np.nan,
            "variação total média": fatia["variacao"].dropna().mean(),
            "baldes vivos (mediana)": fatia["n_baldes"].median(),
        })
    return pd.DataFrame(linhas).set_index("faixa")


def _tabela_md(tabela):
    cabecalho = ["| " + " | ".join([tabela.index.name] + list(tabela.columns)) + " |",
                 "|---" * (len(tabela.columns) + 1) + "|"]
    formato = {"n": "{:.0f}", "entropia média": "{:.3f}", "entropia desvio": "{:.3f}",
               "variação total média": "{:.4f}", "baldes vivos (mediana)": "{:.1f}"}
    for faixa, linha in tabela.iterrows():
        celulas = [faixa] + [("—" if not np.isfinite(linha[c]) else formato[c].format(linha[c]))
                             for c in tabela.columns]
        cabecalho.append("| " + " | ".join(celulas) + " |")
    return cabecalho


def familias(args):
    """(nome -> lista de quadros com distância) das três famílias de anúncio.

    Mesmos mercados e mesmo casamento evento -> mercado do
    `premio_condicional.py`, importados de lá: se a medição da cristalização
    e a do prêmio puderem divergir de amostra, um dia divergem.
    """
    fomc = pd.to_datetime(pd.read_csv(args.fomc)["date"])
    medidas_fomc = medidas_por_dia(daily_preopen(load_pmf(args.dados, PREFIXO_FOMC)))
    # O M3 é mercado de TRAJETÓRIA (nº de cortes no ano): não resolve na
    # reunião, então aqui "cristalizar" é sobre a reunião, não sobre a
    # liquidação. É a mesma PMF que a 1.3 lê no dia de FOMC.
    por_reuniao = [com_distancia(medidas_fomc, data) for data in fomc]

    releases = load_cpi_releases(args.cpi)
    cpi = [com_distancia(medidas_por_dia(daily_preopen(load_pmf(args.dados, prefixo))), data)
           for data, prefixo in prefixos_cpi(releases, args.dados).items()]

    payrolls = mercados_de_payroll(args.dados, load_payroll_releases(args.payrolls))
    folha = [com_distancia(
        medidas_por_dia(daily_preopen(load_pmf(args.dados, prefixo, ordenar=False))), data)
        for data, (prefixo, _) in payrolls.items()]

    return {"FOMC (PMF de trajetória)": por_reuniao,
            "CPI (PMF do mês)": cpi,
            "Payrolls (PMF do Employment Situation)": folha}


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dados", default="data/raw/clob_exploracao")
    parser.add_argument("--fomc", default="data/raw/fomc_dates.csv")
    parser.add_argument("--cpi", default="data/raw/cpi_release_dates.csv")
    parser.add_argument("--payrolls", default="data/raw/payrolls_release_dates.csv")
    parser.add_argument("--saida", default="Dump/analises/Cristalizacao_entropia.md")
    args = parser.parse_args()

    saida = ["# Cristalização da PMF por distância ao evento — e o que ela faz com a 1.3\n",
             "> Gerado por `scripts/cristalizacao_entropia.py`. Traduz o achado (b) da "
             "Lia (2026-08-10) para o sinal da tática 1.3. **Mede; não decide** — nem "
             "entrada da sleeve, nem orçamento (CLAUDE.md §6).\n",
             "- `entropia` = o sinal da 1.3, no slot pré-abertura (12:00 UTC) do dia;",
             "- `variação total` = `Σ|p(d) − p(d−1)|` entre dias corridos ADJACENTES — "
             "a mesma grandeza do ingrediente que entrou na régua da Lia;",
             "- `baldes vivos` é CONTROLE: a entropia é normalizada por log(nº de baldes "
             "com leitura > 0), e balde morre perto do evento. Queda de entropia com "
             "essa coluna caindo junto pode ser artefato de denominador.\n"]

    tabelas = {}
    for nome, quadros in familias(args).items():
        quadros = [q for q in quadros if len(q)]
        saida.append(f"\n## {nome}\n")
        if not quadros:
            saida.append("*Nenhum mercado com leitura casada a evento.*")
            continue
        junto = pd.concat(quadros)
        tabelas[nome] = perfil(junto)
        saida.append(f"- eventos com leitura: **{len(quadros)}** · "
                     f"observações diárias: **{len(junto)}**\n")
        saida.extend(_tabela_md(tabelas[nome]))

    saida.append("\n## O que isto diz do desenho da 1.3\n")
    for nome, tabela in tabelas.items():
        perto, longe = tabela.iloc[0], tabela.loc["6–10 dias"]
        if not np.isfinite(perto["entropia média"]) or not np.isfinite(longe["entropia média"]):
            continue
        saida.append(
            f"**{nome}** — no slot que a sleeve lê (d = 0) a entropia média é "
            f"{perto['entropia média']:.3f} com desvio {perto['entropia desvio']:.3f}, "
            f"contra {longe['entropia média']:.3f} / {longe['entropia desvio']:.3f} a "
            f"6–10 dias. A variação total média vai de "
            f"{longe['variação total média']:.4f} (6–10 dias) para "
            f"{perto['variação total média']:.4f} em d = 0, com a mediana de baldes "
            f"vivos indo de {longe['baldes vivos (mediana)']:.1f} para "
            f"{perto['baldes vivos (mediana)']:.1f}.\n")
        # A pergunta da Lia é sobre a FORMA do perfil, não sobre dois pontos: se
        # a cristalização fosse monótona até o evento, o mínimo de variação
        # cairia em d = 0. Onde não cai, ela reverte no último slot — e o último
        # slot é justamente o que a sleeve lê.
        fundo = tabela["variação total média"].idxmin()
        saida.append(
            (f"↳ o mínimo de variação está em **{fundo}**, não em d = 0: a "
             f"cristalização anda até ali e **reverte no último slot** "
             f"({tabela.loc[fundo, 'variação total média']:.4f} → "
             f"{perto['variação total média']:.4f}). "
             if fundo != tabela.index[0] else
             "↳ o mínimo de variação está em **d = 0**: a cristalização é "
             "monótona até o evento nesta família. ") +
            f"Amostra do slot lido: **n = {perto['n']:.0f}** — o desvio de d = 0 "
            f"é a estatística mais frágil da tabela.\n")
    saida.append(
        "A leitura que decide o desenho é o **desvio da entropia em d = 0**, não a "
        "média: `dw[SPY] = orcamento_max · sinal` só é modulação se o sinal diferir "
        "entre anúncios no slot em que é lido. Desvio que sobrevive à cristalização "
        "= a sleeve continua dimensionando. Desvio que colapsa = a sleeve vira long "
        "SPY constante em dia de anúncio, que é outra tática e precisaria de outra "
        "justificativa.\n")
    saida.append(
        "**O que isto NÃO decide:** a entrada da 1.3 na carteira e o `orcamento_max` "
        "seguem pendentes de reunião. O número aqui é insumo dessa conversa.\n")

    Path(args.saida).write_text("\n".join(saida) + "\n", encoding="utf-8")
    sys.stdout.write(f"escrito: {args.saida}\n")


if __name__ == "__main__":
    main()
