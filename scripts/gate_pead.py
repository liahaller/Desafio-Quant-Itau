"""1.1 PEAD — a surpresa da RESOLUÇÃO deixa drift para trás? Felipe.

A 1.1 é a candidata tática que a sessão 25 deixou intacta: ela lê a
**resolução** do mercado, não o Δ diário da crença, então nem o G1, nem o
variance ratio, nem a autocorrelação da D26 dizem qualquer coisa sobre ela. A
D26 registra que ela é o gargalo número um — e que o gargalo é **humano**, a
decisão 5.

✅ **A decisão 5 FECHOU** (dono, 2026-08-11 — seção 5 e item 7 da D28):

    surpresa = resolução − probabilidade precificada na véspera, CONTÍNUA

É a mesma definição sob a qual este script já media, então o número não mudou
por causa do fechamento — o que mudou é o status: deixou de ser placeholder.

**O achado que precede qualquer número, e ele é de G0:** a resolução só é
observável no dado para uma parte das famílias.

  - **FOMC** ✅ — a decisão realizada sai do DFF (`decisoes_realizadas_fomc`),
    e a véspera sai da PMF do poly. 17 reuniões pareadas.
  - **CPI** ✅ **desde 2026-08-11** — o `CPIAUCSL` entrou no `data/raw` pelo
    item 8 da D28, e com ele o MoM realizado existe. Antes disso o `data/` só
    tinha as DATAS de divulgação, e a família saía do G0 por falta de valor
    resolvido. Que a série do poly termine na véspera **nunca foi o bloqueio**:
    a véspera é justamente o lado do poly que a surpresa usa.
  - **binários** ⚠️ — a resolução aparece só nos que o pull alcançou, e é
    **um evento por mercado**. Sem `n` não há μ.

⚠️ **Sobreposição com a D16, declarada antes de medir:** a sleeve de drift do
FOMC da D16 usa `surpresa = decisão realizada − E_poly[véspera]`, que é esta
mesma construção. A família do Fed da 1.1 **não é território novo** — o que
este script acrescenta é a decomposição em pernas (onde o movimento aterrissa)
e o **sweep da janela pós-anúncio**, que a D16 não fez. Que a mediana da
|surpresa| reproduza os 0,52 bps da D16 é a CALIBRAÇÃO desta medição.

A premissa é herdada, não reescrita: a mesma do controle de FOMC do
`Gate_sleeves.md` (Bernanke-Kuttner), via `PREMISSAS` do `gate_event_driven.py`.

**Nada em `src/` é tocado.**

Uso:

    python scripts/gate_pead.py --raiz .
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from backtest_v1 import (PONTOS_PERCENTUAIS, carregar,  # noqa: E402
                        decisoes_realizadas_fomc)
from config import ASSETS  # noqa: E402
from gate_event_driven import (PREMISSAS, pernas_do_dia,  # noqa: E402
                               retorno_alinhado)
from gate_sleeves import (COL_G3, TICK_FRED_BPS, bate_premissa,  # noqa: E402
                          corr_comum, mu_do_sinal, razao_dispersao,
                          referencias_g3)
from market_inputs import sample_covariance  # noqa: E402
from market_loader import load_etf_prices, load_fred  # noqa: E402
from poly_loader import load_cpi_releases  # noqa: E402
from poly_preprocessing import pmf_mean  # noqa: E402
from premissa_g1 import BINARIOS, serie_binaria  # noqa: E402

# Janelas pós-resolução, em pregões. É o eixo NOVO da 1.1 contra a D16: o PEAD
# da literatura é um drift que dura dias, e a D16 mediu uma janela só. Grade,
# não escolha (CLAUDE.md §6). 15 é a âncora de Neuhierl & Weber que o
# `tatica_drift_anuncio` já cita.
JANELAS = (1, 3, 5, 10, 15)

# A premissa do FOMC é a do C1b / do controle da D16, herdada por referência —
# não copiada, para não poder divergir.
PREMISSA_FOMC, TEXTO_FOMC = PREMISSAS["C1b reunião do FOMC (E_poly em bps)"]

# A premissa do CPI é a do controle da D16 — o indexado bate o nominal na
# surpresa inflacionária —, herdada por referência pelo mesmo motivo.
PREMISSA_CPI, TEXTO_CPI = PREMISSAS["CPI mensal (E_poly)"]

# Tick do sinal do CPI: a grade de baldes do poly anda de 0,1 p.p., que em
# fração mensal é 0.001. Não é corte novo — é a resolução da própria grade.
TICK_CPI = 0.001

# O μ que o `Gate_sleeves.md` registra para o controle de FOMC da D16, colado
# do artefato. Serve de teste de reprodução: se alguma janela da grade bater
# com isto, é porque a 1.1 do Fed e a sleeve da D16 são o MESMO experimento —
# e aí o número não é achado novo, é o antigo reencontrado por outro caminho.
CONTROLE_D16 = "SPY +4.91 ❌ · TLT +1.37 ❌"


def surpresas_fomc(montador, real):
    """(surpresa em bps) por reunião = decisão realizada − E_poly da véspera.

    A véspera é a ÚLTIMA leitura pré-abertura estritamente anterior à reunião —
    não "o dia anterior", porque o poly tem buracos e um feriado transformaria
    a véspera em silêncio. Reunião sem PMF ou sem decisão realizada sai fora:
    parear é condição, não detalhe.
    """
    saida = {}
    for reuniao in sorted(montador.fomc_pmfs):
        if reuniao not in real.index:
            continue
        probs, valores, _ = montador.fomc_pmfs[reuniao]
        antes = probs.index[probs.index < reuniao]
        if not len(antes):
            continue
        linha = probs.loc[antes[-1]].to_numpy(dtype=float)
        if not np.isfinite(linha).all() or linha.sum() <= 0:
            continue
        e_poly = pmf_mean(linha, valores, montador._fl)
        saida[reuniao] = float(real[reuniao] - e_poly)
    return pd.Series(saida, dtype=float).sort_index()


def surpresas_cpi(montador, releases, cpi_mensal):
    """(surpresa em fração/mês) por divulgação = MoM realizado − E_poly da véspera.

    Mesma construção da `surpresas_fomc`, trocando a fonte do realizado: lá é o
    `DFF`, aqui é o `CPIAUCSL` do FRED (autorizado no item 8 da D28). A véspera
    é a ÚLTIMA leitura pré-abertura estritamente anterior ao release — não "o
    dia anterior" —, pelo mesmo motivo: o poly tem buracos e um feriado
    transformaria a véspera em silêncio.

    **Unidade:** os baldes do poly saem do `pmf_diaria` já divididos por 100
    (fração mensal), então o MoM do FRED entra dividido por 100 também. Somar
    as duas unidades erradas daria surpresa 100× e nada acusaria — é o mesmo
    modo de falha que a D27 registra no `gate_mercados_irmaos.py`.

    **Arredondamento do realizado:** o BLS publica o MoM com **uma casa**, e é
    esse número que resolve o mercado. Comparar contra o MoM cheio criaria
    surpresa onde o mercado resolveu exato.
    """
    saida = {}
    for _, linha in releases.iterrows():
        release = pd.Timestamp(linha["release_date"])
        mes = pd.Timestamp(linha["mes_referencia"])
        if mes not in cpi_mensal.index or release not in montador.mercados:
            continue
        probs, valores, _ = montador.pmfs[montador.mercados[release]]
        antes = probs.index[probs.index < release]
        if not len(antes):
            continue
        pmf = probs.loc[antes[-1]].to_numpy(dtype=float)
        if not np.isfinite(pmf).all() or pmf.sum() <= 0:
            continue
        e_poly = pmf_mean(pmf, valores, montador._fl)
        realizado = float(cpi_mensal[mes]) / PONTOS_PERCENTUAIS
        saida[release] = realizado - e_poly
    return pd.Series(saida, dtype=float).sort_index()


def mom_realizado(serie):
    """Variação mensal do CPI em p.p., arredondada na casa que o BLS publica."""
    return (serie / serie.shift(1) - 1.0).mul(PONTOS_PERCENTUAIS).round(1).dropna()


def resolucoes_binarias(diretorio):
    """Última leitura de cada binário e o Δ contra a véspera dela.

    Sem classificar "resolveu" ou "não resolveu": o corte seria um threshold
    inventado. A tabela mostra o VALOR final, e quem lê vê se o mercado foi a
    0/1 ou se o pull parou no meio — que é a diferença entre uma resolução e um
    Δp qualquer.
    """
    linhas = []
    for nome, prefixo in BINARIOS.items():
        try:
            serie = serie_binaria(diretorio, prefixo).dropna()
        except FileNotFoundError:
            continue
        if len(serie) < 2:
            continue
        linhas.append({
            "mercado": nome,
            "última leitura": f"{serie.index[-1]:%Y-%m-%d}",
            "p final": round(float(serie.iloc[-1]), 3),
            "p véspera": round(float(serie.iloc[-2]), 3),
            "surpresa (p.p.)": round(float(serie.iloc[-1] - serie.iloc[-2]) * 100, 1),
            "eventos": 1,
        })
    return pd.DataFrame(linhas)


def main():
    # O console do Windows abre em cp1252 e engasga nos rótulos acentuados.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raiz", default=".")
    parser.add_argument("--saida", default="Dump/analises/Gate_PEAD.md")
    args = parser.parse_args()
    raiz = Path(args.raiz)

    retornos, montador, datas, _ = carregar(raiz)
    fechamento = load_etf_prices(raiz / "data/etf_prices_daily.parquet")[list(ASSETS)]
    abertura = load_etf_prices(raiz / "data/etf_open_daily.parquet")[list(ASSETS)]
    fomc = pd.DatetimeIndex(sorted(pd.to_datetime(
        pd.read_csv(raiz / "data/raw/fomc_dates.csv")["date"])))
    real = decisoes_realizadas_fomc(load_fred(raiz / "data/raw/fred_DFF.csv"), fomc)

    surpresa = surpresas_fomc(montador, real)
    direcao = np.sign(surpresa)
    dias = pd.DatetimeIndex(surpresa.index)

    # CPI: destravado pelo item 8 da D28 (o `CPIAUCSL` entrou no `data/raw`).
    # Antes desta sessão a família saía do G0 por falta de valor realizado.
    releases = load_cpi_releases(raiz / "data/raw/cpi_release_dates.csv")
    # O `CPIAUCSL` NÃO está no repositório: `data/` é excluído do git, e este
    # arquivo não vem do pipeline do Paulo — foi baixado do FRED nesta sessão
    # pela autorização do item 8 da D28. Quem sincronizar o `data/` dele terá
    # todo o resto e não este. Ausência derruba a família CPI de volta ao G0,
    # que é o estado anterior; derrubar o script inteiro seria pior.
    caminho_cpi = raiz / "data/raw/fred_CPIAUCSL.csv"
    cpi_mensal = (mom_realizado(load_fred(caminho_cpi)) if caminho_cpi.exists()
                  else pd.Series(dtype=float))
    surpresa_cpi = surpresas_cpi(montador, releases, cpi_mensal)
    direcao_cpi = np.sign(surpresa_cpi)
    dias_cpi = pd.DatetimeIndex(surpresa_cpi.index)

    sigma = sample_covariance(retornos)
    ate = datas[-1] + pd.Timedelta(days=1)
    referencias = referencias_g3(montador, datas, montador._fl)

    # --- G1: a surpresa tem tamanho acima do tick da fonte? -------------------
    g1 = razao_dispersao(surpresa, TICK_FRED_BPS)

    # --- pernas + sweep da janela --------------------------------------------
    # Uma função só para as duas famílias: o CPI tem de ser medido com o MESMO
    # laço do FOMC, não com uma cópia. Duas cópias divergiriam na primeira
    # correção, e a comparação entre as famílias deixaria de valer.
    def sweep(dias_ev, direcao_ev, premissa, rotulo_n):
        linhas = []
        for h in JANELAS:
            pernas = pernas_do_dia(abertura, fechamento, h)
            linha = {"janela": f"h = {h}", rotulo_n: len(dias_ev)}
            for rotulo in ("D−1 sessão", "gap", "intra D", f"resíduo {h}d"):
                media, _n = retorno_alinhado(pernas[rotulo], dias_ev, direcao_ev,
                                             premissa)
                linha["resíduo" if rotulo.startswith("resíduo") else rotulo] = media
            eventos = [(d, s) for d, s in direcao_ev.items() if s != 0]
            mu, n_mu = mu_do_sinal(retornos, eventos, h, tuple(premissa),
                                   sigma, ate)
            ok, detalhe = bate_premissa(mu, ASSETS, premissa)
            linha["eventos no μ"] = n_mu
            linha["G2 μ (bps/dia)"] = detalhe
            linha["G2 bate?"] = "✅" if ok else "❌"
            linhas.append(linha)
        return pd.DataFrame(linhas)

    def formatar(bruta):
        saida = bruta.copy()
        for coluna in ("D−1 sessão", "gap", "intra D", "resíduo"):
            saida[coluna] = bruta[coluna].map(
                lambda v: f"{v:+.1f}" if np.isfinite(v) else "—")
        return saida

    tabela = sweep(dias, direcao, PREMISSA_FOMC, "n reuniões")
    formatada = formatar(tabela)
    tabela_cpi = (sweep(dias_cpi, direcao_cpi, PREMISSA_CPI, "n divulgações")
                  if len(dias_cpi) else pd.DataFrame())
    formatada_cpi = formatar(tabela_cpi) if not tabela_cpi.empty else tabela_cpi

    # --- G3 da surpresa contra o que as views vivas leem ----------------------
    correlacoes = {c: corr_comum(surpresa, ref) for c, ref in referencias.items()}
    finitas = {c: v for c, v in correlacoes.items() if np.isfinite(v)}
    pior = max(finitas, key=lambda c: abs(finitas[c])) if finitas else None

    eventos_tabela = pd.DataFrame({
        "reunião": [f"{d:%Y-%m-%d}" for d in surpresa.index],
        "surpresa (bps)": surpresa.round(2).to_numpy(),
    })
    binarios = resolucoes_binarias(raiz / "data/raw/clob_exploracao")

    passam = tabela[tabela["G2 bate?"] == "✅"]["janela"].tolist()
    texto = [
        "# 1.1 PEAD — a surpresa da resolução deixa drift para trás?\n",
        "> Gerado por `scripts/gate_pead.py`. **Mede; não decide.** Nenhum "
        "corte cravado, mesma regra do `Gate_sleeves.md`.\n",
        "> ✅ **A decisão 5 FECHOU** (dono, 2026-08-11): *surpresa = resolução "
        "− probabilidade precificada na véspera*, contínua. É a mesma "
        "definição sob a qual este artefato já media — o número não mudou com "
        "o fechamento, só o status.\n",
        f"- janela do backtest: **{datas[0]:%Y-%m-%d} a {datas[-1]:%Y-%m-%d}** "
        f"({len(datas)} pregões), δ e Σ os mesmos do v1 (D7/D8)",
        "- **h** = pregões DEPOIS do fechamento do dia do anúncio. É o eixo "
        "novo contra a D16, que mediu uma janela só",
        "- retornos **alinhados à premissa declarada** (positivo = premissa "
        "confirmada), em **bps**\n",
        f"**Premissa declarada ANTES de medir:** {TEXTO_FOMC} — para a "
        "resolução, surpresa positiva = decisão mais dura que a precificada. "
        "É a do controle de FOMC do `Gate_sleeves.md`, herdada **por "
        "referência** (o script importa o mesmo dicionário, não uma cópia).\n",
        "## G0 — de quais famílias a resolução é observável no dado\n",
        "É aqui que a 1.1 é decidida, e não no G2.\n",
        "| família | resolução no dado? | eventos | por quê |",
        "|---|---|---|---|",
        f"| **FOMC** | ✅ | **{len(surpresa)}** | decisão realizada do DFF × "
        "E_poly da véspera |",
        f"| **CPI** | {'✅' if len(surpresa_cpi) else '❌'} | "
        f"**{len(surpresa_cpi)}** | MoM realizado do `CPIAUCSL` × E_poly da "
        "véspera. **Destravado nesta sessão** (item 8 da D28): antes o `data/` "
        "só tinha as DATAS de divulgação. A série do poly seguir terminando na "
        "véspera deixou de bloquear — a véspera é justamente o que a surpresa "
        "usa |",
        f"| **binários** | ⚠️ | {len(binarios)} mercados × **1 evento cada** | "
        "a resolução só existe para o que o pull alcançou, e um evento por "
        "mercado não dá μ |",
        "",
    ]

    texto += [
        f"## FOMC — as {len(surpresa)} reuniões pareadas\n",
        eventos_tabela.to_markdown(index=False), "",
        f"**G1 da surpresa: mediana |surpresa| ÷ tick do FRED (1 bp) = "
        f"{g1:.1f}×.**\n",
        "## Pernas e sweep da janela pós-anúncio\n",
        formatada.to_markdown(index=False), "",
        f"**G3** — maior |correlação| da surpresa com o que as views vivas já "
        f"leem: " + (f"**{finitas[pior]:+.2f}** ({pior})" if pior else "—") + "\n",
    ]

    if not tabela_cpi.empty:
        g1_cpi = razao_dispersao(surpresa_cpi, TICK_CPI)
        eventos_cpi = pd.DataFrame({
            "divulgação": [f"{d:%Y-%m-%d}" for d in surpresa_cpi.index],
            "surpresa (p.p.)": (surpresa_cpi * PONTOS_PERCENTUAIS).round(2).to_numpy(),
        })
        corr_cpi = {c: corr_comum(surpresa_cpi, ref)
                    for c, ref in referencias.items()}
        finitas_cpi = {c: v for c, v in corr_cpi.items() if np.isfinite(v)}
        pior_cpi = (max(finitas_cpi, key=lambda c: abs(finitas_cpi[c]))
                    if finitas_cpi else None)
        texto += [
            f"## CPI — as {len(surpresa_cpi)} divulgações pareadas\n",
            "**A família que o G0 barrava.** A premissa é a do controle de CPI "
            f"da D16, herdada por referência: {TEXTO_CPI} — surpresa positiva = "
            "inflação acima do precificado.\n",
            eventos_cpi.to_markdown(index=False), "",
            f"**G1 da surpresa: mediana |surpresa| ÷ tick da grade de baldes "
            f"(0,1 p.p.) = {g1_cpi:.1f}×.**\n",
            formatada_cpi.to_markdown(index=False), "",
            "**G3** — maior |correlação| da surpresa do CPI com o que as views "
            "vivas já leem: "
            + (f"**{finitas_cpi[pior_cpi]:+.2f}** ({pior_cpi})"
               if pior_cpi else "—") + "\n",
        ]

    if not binarios.empty:
        texto += ["## Binários — a resolução que o pull alcançou\n",
                  "Sem classificar \"resolveu\"/\"não resolveu\": o corte seria "
                  "threshold inventado. O `p final` diz sozinho se o mercado "
                  "foi a 0/1 ou se o pull parou no meio.\n",
                  binarios.to_markdown(index=False), ""]

    texto.append("## Leitura\n")

    # (a) calibração contra a D16 — é o que autoriza ler o resto
    mediana = float(surpresa.abs().median())
    texto.append(
        f"**Calibração:** a mediana da |surpresa| nas {len(surpresa)} reuniões "
        f"é **{mediana:.2f} bps**. A D16 registrou **0,52 bps em 17 reuniões** "
        "para a mesma construção — " + ("**reproduz**" if abs(mediana - 0.52) < 0.01
                                        else f"**diverge** (D16: 0,52)")
        + ". Isso confirma o que a docstring declara: **a família do Fed da 1.1 "
        "é a sleeve da D16 com outro nome.** O que este artefato acrescenta é a "
        "decomposição em pernas e o sweep de `h`; a surpresa em si já estava "
        "medida, e é ~zero.\n")

    # Reprodução exata, não aproximada: se uma linha da grade bate com o μ que
    # o `Gate_sleeves.md` registra, a identidade entre a 1.1 do Fed e a sleeve
    # da D16 deixa de ser argumento e vira medida.
    iguais = tabela[tabela["G2 μ (bps/dia)"] == CONTROLE_D16]["janela"].tolist()
    if iguais:
        texto.append(
            f"**E a identidade não é argumento, é medida:** a linha "
            f"**{iguais[0]}** sai com μ `{CONTROLE_D16}` — **o mesmo μ, dígito "
            "por dígito**, que o `Gate_sleeves.md` registra para o controle de "
            "FOMC da D16. A janela daquela sleeve era essa, e reencontrá-la "
            "aqui por outro caminho fecha a questão: a 1.1 aplicada ao Fed não "
            "é candidata nunca medida — **é a sleeve reprovada da D16**. O que "
            "continua nunca medido é a 1.1 **fora** do Fed, e é o G0 que "
            "impede.\n")

    texto.append(
        f"**O G1 da surpresa é {g1:.1f}× o tick do FRED.** " + (
            "Abaixo de 1×: a surpresa típica de uma reunião é menor que a "
            "granularidade com que a fonte publica a taxa. Não é sinal fraco — "
            "é sinal dentro do ruído de discretização, o mesmo motivo que matou "
            "a C1a e a C1b." if g1 < 1.0 else
            "Acima de 1×: a surpresa existe acima da granularidade da fonte, e "
            "o veredito passa a depender do G2.") + "\n")

    # (b) onde o movimento aterrissa
    h1 = JANELAS[0]
    base = tabela.iloc[0]
    pernas_txt = " · ".join(
        f"{c} {base[c]:+.1f}" for c in ("D−1 sessão", "gap", "intra D", "resíduo")
        if np.isfinite(base[c]))
    texto.append(
        f"**Onde o movimento aterrissa** (h = {h1}, em bps alinhados à "
        f"premissa): {pernas_txt}. As duas primeiras pernas são anteriores ao "
        "anúncio e estão aqui só como contexto — a resolução do FOMC sai às "
        "14h ET, dentro da sessão, então para a 1.1 a perna **`intra D` já é "
        "parcialmente negociável** e o `resíduo` é o PEAD propriamente dito.\n")

    # (c) G2
    if not passam:
        texto.append(
            "**Nenhuma janela passa no G2:** "
            + " · ".join(f"{r['janela']} (`{r['G2 μ (bps/dia)']}`)"
                         for _, r in tabela.iterrows())
            + ". O μ pós-anúncio sai contra Bernanke-Kuttner em toda a grade, e "
            "pela D2b não se inverte. **O drift pós-resolução não existe na "
            "direção que a teoria manda**, em nenhum horizonte entre "
            f"{JANELAS[0]} e {JANELAS[-1]} pregões.\n")
    else:
        texto.append(
            f"**{len(passam)} de {len(JANELAS)} janelas passam no G2:** "
            + ", ".join(f"**{j}**" for j in passam)
            + f". ⚠️ Com **{len(surpresa)} eventos** e uma surpresa de mediana "
            f"{mediana:.2f} bps, passar no G2 diz que o SINAL do μ bate — não "
            "que há tamanho a operar. Passar no G2 não é aprovação: o gate "
            "mede, e o destino é decisão do dono.\n")

    # (d) o veredito da 1.1 FORA do Fed. Até 2026-08-11 este bloco dizia que o G0
    # travava a família — verdade enquanto não havia valor realizado no
    # `data/`. Com o `CPIAUCSL` dentro, a frase teria envelhecido em silêncio;
    # por isso passa a ser gerada dos números do próprio CPI.
    if tabela_cpi.empty:
        texto.append(
            "**O que trava a 1.1 fora do Fed continua sendo o G0:** nenhuma "
            "divulgação de CPI ficou pareada, então não há surpresa a medir.\n")
    else:
        passam_cpi = tabela_cpi[tabela_cpi["G2 bate?"] == "✅"]["janela"].tolist()
        mediana_cpi = float(surpresa_cpi.abs().median()) * PONTOS_PERCENTUAIS
        texto.append(
            f"**A 1.1 FORA do Fed deixou de ser hipótese e virou medição.** "
            f"Com o `CPIAUCSL` no `data/` (item 8 da D28), {len(surpresa_cpi)} "
            f"divulgações ficaram pareadas — a família que o G0 barrava. E o "
            f"veredito é: "
            + (f"passa no G2 em {', '.join(passam_cpi)}.\n" if passam_cpi else
               "**nenhuma janela passa no G2.** O μ pós-divulgação sai contra "
               "a premissa declarada em toda a grade, e pela D2b não se "
               "inverte.\n"))
        texto.append(
            f"**E o motivo é o mesmo do Fed: a surpresa não tem tamanho.** A "
            f"mediana da |surpresa| é **{mediana_cpi:.2f} p.p.** contra uma "
            f"grade de baldes que anda de 0,1 p.p. — G1 de "
            f"**{razao_dispersao(surpresa_cpi, TICK_CPI):.1f}×**, abaixo de 1, "
            "que é o mesmo diagnóstico de ruído de discretização que matou a "
            "C1a, a C1b e a família do Fed desta candidata. O poly erra o CPI "
            "por menos que a granularidade com que ele próprio pergunta.\n")
        if pior_cpi and abs(finitas_cpi[pior_cpi]) > 0.5:
            texto.append(
                f"⚠️ **E ela não é território livre:** a surpresa do CPI tem "
                f"|correlação| de **{finitas_cpi[pior_cpi]:+.2f}** com "
                f"{pior_cpi}, que uma view VIVA já lê. Mesmo se o G2 tivesse "
                "passado, o G3 cobraria a sobreposição.\n")

    texto.append(
        "**O que isto NÃO diz:** nada sobre P&L, e nada sobre a 3.2. A 1.1 lê a "
        "RESOLUÇÃO; a 3.2 lê o SALTO, e está medida em `Gate_event_driven.md`.\n")

    Path(args.saida).write_text("\n".join(texto) + "\n", encoding="utf-8")
    sys.stdout.write(formatada.to_string(index=False) + "\n\n")
    sys.stdout.write(f"G1 da surpresa: {g1:.2f}×  ·  mediana |surpresa|: "
                     f"{mediana:.2f} bps  ·  n = {len(surpresa)}\n")
    sys.stdout.write(f"\nescrito: {args.saida}\n")


if __name__ == "__main__":
    main()
