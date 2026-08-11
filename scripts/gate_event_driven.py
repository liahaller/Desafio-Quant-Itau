"""3.2 event-driven — o salto da crença sobra depois do gap? Felipe.

A 3.2 é uma das duas candidatas táticas cujo item 3 da D22 sobreviveu à sessão
25: ela lê o **salto de nível** da probabilidade, não o encadeamento de
movimentos que o `Premissa_tendencia.md` derrubou (VR ≈ 1, ρ ex-ante ≈ 0).

A D26 registrou que o teste que falta é de **uma linha**: *quanto do movimento
sobra do fechamento do dia do salto em diante?* O salto é o padrão com maior
chance de aterrissar no **gap de abertura** — a parede que já derrubou a 2.4, a
view C, a E e o gap de fim de semana. Se não sobrar nada, a 3.2 morre como o C3
morreu, e custou um script.

Este script decompõe o retorno em volta de cada salto em QUATRO pernas, para
separar o que a sleeve poderia capturar do que já passou quando ela olha:

    D−1 sessão : open(D−1) → close(D−1)   concorrente ao Δp, NÃO negociável
    gap        : close(D−1) → open(D)     overnight, NÃO negociável
    intra D    : open(D) → close(D)       negociável (destravado em 18/08)
    resíduo h  : close(D) → close(D+h)    negociável — é o que a D26 pergunta

O sinal do dia D é o slot pré-abertura de D, então `Δp(D) = p(D) − p(D−1)` é um
movimento que aconteceu inteiro dentro de `[pré-abertura D−1, pré-abertura D]`:
as duas primeiras pernas são **contemporâneas ao salto** e estão aqui só para
dizer onde o movimento foi parar, nunca como resultado de tática.

⚠️ **"Salto" é threshold, e threshold sem âncora é o que a 12c e a D13 mataram
duas vezes.** Por isso aqui ele é uma **GRADE de quantis** do |Δp| do próprio
mercado, não um valor: o que responde a pergunta é a curva contra o corte, não
um corte. Mesma disciplina do `HORIZONTES` do `premissa_g1.py` (CLAUDE.md §6).

⚠️ **A premissa de cada mercado é declarada ANTES de medir**, em
`PREMISSAS` — e as três da família Fed/CPI são herdadas palavra por palavra do
`Gate_sleeves.md`. Declarar por escrito é o que faz do G2 um teste em vez de
racionalização (D26).

**Nada em `src/` é tocado.** μ, premissa, correlação e séries vêm do
`gate_sleeves.py` e do `premissa_g1.py`; as pernas saem dos dois parquets do
Paulo, que desde 2026-08-09 estão na mesma base de ajuste (conferido aqui de
novo, antes de qualquer número).

Uso:

    python scripts/gate_event_driven.py --raiz .
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from config import ASSETS  # noqa: E402
from gate_sleeves import (COL_G3, bate_premissa, corr_comum,  # noqa: E402
                          eventos_diarios, mu_do_sinal, referencias_g3)
from market_inputs import sample_covariance  # noqa: E402
from market_loader import adjustment_gap, load_etf_prices  # noqa: E402
from premissa_g1 import em_pregoes, series_dos_mercados  # noqa: E402

# Cortes de |Δp| em QUANTIL da distribuição do próprio mercado. 0.0 = todos os
# dias com sinal, a linha de base contra a qual o condicionamento se lê: se o
# resíduo não melhora do quantil 0 para o 0,90, "salto" não é informação.
QUANTIS = (0.0, 0.50, 0.75, 0.90)

# Horizontes do resíduo, em pregões. Grade pelo mesmo motivo dos quantis.
HORIZONTES_RESIDUO = (1, 3, 5)

# Ruído intradiário tolerado na conferência de base de ajuste, igual ao
# `premissa_taticas.py`. Acima disso a razão abertura/fechamento não é ruído.
LIMIAR_BASE_AJUSTE = 0.001

# Premissa DECLARADA por mercado, antes de estimar: para que lado cada ativo
# anda quando o sinal do mercado SOBE. As três primeiras são as do
# `Gate_sleeves.md` / do controle da D16, herdadas sem reescrita.
PREMISSAS = {
    "C1a M3 trajetória do Fed (nº de cortes)": (
        {"SPY": +1, "TLT": +1},
        "crença anda para mais afrouxamento → SPY e TLT sobem (D17, herdada)"),
    "C1b reunião do FOMC (E_poly em bps)": (
        {"SPY": -1, "TLT": -1},
        "idem, com o sinal invertido porque E_poly é Δtaxa (D17, herdada)"),
    "CPI mensal (E_poly)": (
        {"TIP": +1, "TLT": -1},
        "surpresa inflacionária → o indexado (TIP) bate o nominal (TLT) "
        "(controle D16 do CPI, herdada)"),
    "M4 recessão EUA 2025": (
        {"SPY": -1, "TLT": +1},
        "p(recessão) sobe → risco-off: bolsa cai e duração sobe"),
    "M5 Trump 2024": (
        {"SPY": +1, "TLT": -1},
        "\"Trump trade\": p(Trump) sobe → bolsa sobe e duração cai (premissa "
        "da view 2.4)"),
    "M6 tarifas China": (
        {"SPY": -1, "TLT": +1},
        "p(tarifa) sobe → guerra comercial: bolsa cai e duração sobe"),
    "M7 ação militar Irã (jun/2025)": (
        {"XLE": +1, "SPY": -1},
        "p(ação militar) sobe → petróleo sobe (XLE) e bolsa cai (premissa da "
        "view C)"),
    "M7 ataque ao Irã (fev/2026)": (
        {"XLE": +1, "SPY": -1},
        "idem, segundo episódio"),
    "M8 reconciliação fiscal": (
        {"TLT": -1, "SPY": +1},
        "p(aprovação) sobe → mais emissão: duração cai e bolsa sobe"),
    "M9 Câmara": (
        {"SPY": -1, "TLT": +1},
        "mecanismo partidário, espelho do M5. ⚠️ é exatamente o mecanismo que a "
        "2.4 mediu como NÃO reproduzindo fora da amostra"),
}

# Janela do event-study do G2, em pregões. 1 = sleeve reassinada no dia do
# salto, igual ao C1a da D17 — mantém o quantil como único eixo novo.
JANELA_G2 = 1

# O que o projeto JÁ mediu sobre cada mercado, em outra camada. Não é opinião
# sobre o resultado: é o registro que impede uma linha que passa aqui de ser
# lida como achado novo quando a mesma premissa já foi a júri e perdeu.
PRECEDENTES = {
    "M4 recessão EUA 2025": "a **view 3.1** leu este mercado, e a D19c mediu "
                            "que o coeficiente **troca de sinal dentro da "
                            "própria amostra** (SPY em h = 10: +0,97% t +6,52 "
                            "na 1ª metade, **−0,35% t −2,27** na 2ª). Não há "
                            "segundo mercado de recessão, então não existe "
                            "teste fora da amostra — e agora se sabe que não "
                            "existe nem dentro dela",
    "M5 Trump 2024": "a **view 2.4** leu este mercado e foi cortada: o efeito "
                     "aterrissa no gap (23% sobra na janela negociável) e o "
                     "mecanismo partidário **reprovou fora da amostra** — o TLT "
                     "cai nos dois mercados, quando deveria inverter",
    "M9 Câmara": "mesmo mecanismo partidário da 2.4, e é o segundo mercado do "
                 "teste fora da amostra que a reprovou",
    "M7 ação militar Irã (jun/2025)": "a **view C** leu este mercado e não "
                                      "entrou (D23f): o critério pré-registrado "
                                      "para fixar o `k` **não identifica k** "
                                      "(corr +0,08 entre os dois episódios) e o "
                                      "único lag em que eles concordam é o "
                                      "**lag 0** — o gap de abertura",
    "M7 ataque ao Irã (fev/2026)": "segundo episódio do par que a D23f mediu",
}


def pernas_do_dia(abertura, fechamento, h):
    """As quatro pernas do retorno, cada uma como DataFrame datas × tickers.

    Indexadas pelo dia D do salto: `pernas[nome].loc[D, ativo]` é o retorno
    daquela perna em volta do salto de D. O resíduo olha para a FRENTE, então
    as últimas `h` datas saem NaN — evento sem janela fechada não entra na
    média, que é a mesma regra do `estimate_drift_mu`.
    """
    return {
        "D−1 sessão": (fechamento / abertura - 1.0).shift(1),
        "gap": abertura / fechamento.shift(1) - 1.0,
        "intra D": fechamento / abertura - 1.0,
        f"resíduo {h}d": fechamento.shift(-h) / fechamento - 1.0,
    }


def retorno_alinhado(perna, dias, direcao, declarado):
    """Média, em bps, do retorno da perna ALINHADO à premissa declarada.

    Alinhar = multiplicar pelo sinal do Δp e pelo sinal que a premissa declara
    para o ativo. Assim "positivo" quer dizer sempre *a premissa se confirmou*,
    e as pernas de mercados com direções opostas somam na mesma unidade. A
    média é sobre os ativos do livro declarado, que é o único lugar onde a
    premissa diz alguma coisa.
    """
    valores = []
    for ativo, esperado in declarado.items():
        if ativo not in perna.columns:
            continue
        serie = perna[ativo].reindex(dias)
        valores.append((serie * direcao.reindex(dias) * esperado).dropna())
    if not valores:
        return float("nan"), 0
    juntos = pd.concat(valores)
    return float(juntos.mean() * 1e4), int(len(valores[0].dropna()))


def dias_de_salto(sinal, quantil):
    """Dias em que |Δp| está no topo `quantil` da distribuição do mercado.

    `quantil = 0` devolve todo dia com Δp não nulo — a linha de base. O corte
    é do PRÓPRIO mercado: um Δp de 2 pontos é rotina no Irã e é salto no Fed,
    e um limiar absoluto misturaria as duas coisas.
    """
    vivo = sinal[sinal != 0].dropna()
    if vivo.empty:
        return vivo.index
    if quantil <= 0:
        return vivo.index
    return vivo.index[vivo.abs() >= vivo.abs().quantile(quantil)]


def main():
    # O console do Windows abre em cp1252 e engasga nos rótulos acentuados.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raiz", default=".")
    parser.add_argument("--saida", default="Dump/analises/Gate_event_driven.md")
    args = parser.parse_args()
    raiz = Path(args.raiz)

    series, retornos, montador, datas = series_dos_mercados(raiz)
    fechamento = load_etf_prices(raiz / "data/etf_prices_daily.parquet")[list(ASSETS)]
    abertura = load_etf_prices(raiz / "data/etf_open_daily.parquet")[list(ASSETS)]

    # Conferência ANTES de qualquer número: as pernas `gap` e `intra` misturam
    # os dois parquets, e um degrau de ajuste entre eles fabricaria retorno.
    degrau = adjustment_gap(abertura, fechamento)
    contaminados = sorted(degrau.index[degrau.abs() > LIMIAR_BASE_AJUSTE])

    sigma = sample_covariance(retornos)
    ate = datas[-1] + pd.Timedelta(days=1)
    referencias = referencias_g3(montador, datas, montador._fl)

    linhas, g2_linhas, medidas = [], [], {}
    for nome, _familia, serie, _tick, _unidade in series:
        if nome not in PREMISSAS:
            continue
        declarado, _texto = PREMISSAS[nome]
        sinal = em_pregoes(serie).diff().dropna()
        if sinal.empty:
            continue
        direcao = np.sign(sinal)
        for quantil in QUANTIS:
            dias = dias_de_salto(sinal, quantil)
            if len(dias) < 3:
                continue
            pernas = pernas_do_dia(abertura, fechamento, HORIZONTES_RESIDUO[0])
            linha = {"mercado": nome, "corte |Δp|": f"q{quantil:.2f}",
                     "n saltos": len(dias)}
            for rotulo, perna in pernas.items():
                media, _n = retorno_alinhado(perna, dias, direcao, declarado)
                linha[rotulo] = media
            for h in HORIZONTES_RESIDUO[1:]:
                perna = pernas_do_dia(abertura, fechamento, h)[f"resíduo {h}d"]
                linha[f"resíduo {h}d"], _ = retorno_alinhado(
                    perna, dias, direcao, declarado)
            linhas.append(linha)
            medidas[(nome, quantil)] = linha

        # G2/G3 no corte mais exigente com eventos suficientes: é onde a tese
        # do salto vive. Cortes menores estão na tabela das pernas.
        dias = dias_de_salto(sinal, QUANTIS[-1])
        if len(dias) >= 3:
            eventos = eventos_diarios(sinal.reindex(dias))
            mu, n_mu = mu_do_sinal(retornos, eventos, JANELA_G2,
                                   tuple(declarado), sigma, ate)
            ok, detalhe = bate_premissa(mu, ASSETS, declarado)
            correlacoes = {c: corr_comum(sinal.reindex(dias), ref)
                           for c, ref in referencias.items()}
            finitas = {c: v for c, v in correlacoes.items() if np.isfinite(v)}
            pior = max(finitas, key=lambda c: abs(finitas[c])) if finitas else None
            g2_linhas.append({
                "mercado": nome,
                f"G0 saltos (q{QUANTIS[-1]:.2f})": len(dias),
                "eventos no μ": n_mu,
                "G2 μ (bps/dia)": detalhe,
                "G2 bate?": "✅" if ok else "❌",
                COL_G3: (f"{finitas[pior]:+.2f} ({pior})" if pior else "—"),
            })

    tabela = pd.DataFrame(linhas)
    colunas_perna = ["D−1 sessão", "gap", "intra D"] + [
        f"resíduo {h}d" for h in HORIZONTES_RESIDUO]
    formatada = tabela.copy()
    for coluna in colunas_perna:
        formatada[coluna] = tabela[coluna].map(
            lambda v: f"{v:+.1f}" if np.isfinite(v) else "—")

    g2 = pd.DataFrame(g2_linhas)

    # --- leitura, GERADA dos números -----------------------------------------
    # A pergunta da D26 é uma razão, não um nível: do movimento que a premissa
    # prevê, quanto está DEPOIS do fechamento do dia do salto? Somo em módulo
    # para a razão não explodir quando pernas de sinais opostos se cancelam.
    def sobra(linha, h):
        pernas = [abs(linha[c]) for c in ("D−1 sessão", "gap", "intra D",
                                          f"resíduo {h}d")
                  if np.isfinite(linha[c])]
        resid = linha[f"resíduo {h}d"]
        total = sum(pernas)
        return (resid / total) if total > 0 and np.isfinite(resid) else float("nan")

    h1 = HORIZONTES_RESIDUO[0]
    mais_exigente = tabela[tabela["corte |Δp|"] == f"q{QUANTIS[-1]:.2f}"]
    fracoes = {r["mercado"]: sobra(r, h1) for _, r in mais_exigente.iterrows()}
    fracoes = {m: v for m, v in fracoes.items() if np.isfinite(v)}
    positivos = {m: v for m, v in fracoes.items() if v > 0}

    texto = [
        "# 3.2 event-driven — o salto sobra depois do gap?\n",
        "> Gerado por `scripts/gate_event_driven.py`. **Mede; não decide.** "
        "Nenhum corte cravado, mesma regra do `Gate_sleeves.md`.\n",
        f"- janela do backtest: **{datas[0]:%Y-%m-%d} a {datas[-1]:%Y-%m-%d}** "
        f"({len(datas)} pregões), δ e Σ os mesmos do v1 (D7/D8)",
        "- **salto** = dia cujo |Δp| está no topo do quantil da coluna, na "
        "distribuição do PRÓPRIO mercado. `q0.00` = todo dia com Δp ≠ 0, a "
        "linha de base",
        "- retornos **alinhados à premissa declarada**: positivo = a premissa "
        "se confirmou, qualquer que seja a direção do mercado. Unidade: **bps**",
        "- as duas primeiras pernas são **contemporâneas** ao Δp (o sinal é o "
        "slot pré-abertura de D): estão aqui para dizer onde o movimento foi "
        "parar, nunca como resultado de tática\n",
    ]

    if contaminados:
        texto.append(
            "> 🛑 **Conferência de base de ajuste REPROVOU** em "
            + ", ".join(f"{t} ({degrau[t] * 100:+.2f}%)" for t in contaminados)
            + ". As pernas `gap` e `intra D` desses tickers estão "
            "contaminadas por retorno fabricado — não leia esta tabela até o "
            "conserto (módulo do Paulo).\n")
    else:
        texto.append(
            "✅ **Conferência de base de ajuste passa** — maior desvio de "
            f"`abertura/fechamento − 1` é {degrau.abs().max() * 100:.3f}%, "
            "dentro do ruído intradiário. As pernas que misturam os dois "
            "parquets valem, **inclusive no dia do próprio evento**.\n")

    texto += [formatada.to_markdown(index=False), "",
              "## Premissa declarada ANTES de medir\n",
              "Sem isto o G2 é racionalização, não teste. As três da família "
              "Fed/CPI são herdadas do `Gate_sleeves.md` palavra por palavra.\n"]
    for nome, (_declarado, descricao) in PREMISSAS.items():
        if nome in set(tabela["mercado"]):
            texto.append(f"- **{nome}** — {descricao}")
    texto.append("")

    if not g2.empty:
        texto += [f"## G2 e G3 no corte mais exigente (q{QUANTIS[-1]:.2f})\n",
                  g2.to_markdown(index=False), ""]

    texto.append("## Leitura\n")

    # (a) a pergunta da D26, respondida como razão
    if fracoes:
        ordenado = sorted(fracoes.items(), key=lambda kv: -abs(kv[1]))
        detalhe = " · ".join(f"**{m}** {v:+.0%}" for m, v in ordenado)
        texto.append(
            f"**A pergunta da D26, respondida.** Fração do movimento total "
            f"(em módulo, as quatro pernas) que está no resíduo de {h1} "
            f"pregão — ou seja, o que sobra do fechamento do dia do salto em "
            f"diante, no corte q{QUANTIS[-1]:.2f}: " + detalhe + ".\n")
        mediana = float(np.median(list(fracoes.values())))
        texto.append(
            f"A mediana entre os {len(fracoes)} mercados é **{mediana:+.0%}**, "
            f"e **{len(positivos)} de {len(fracoes)}** têm resíduo na direção "
            "que a premissa declara. Sinal negativo aqui não é \"pouco sinal\": "
            "é o resíduo andando CONTRA a premissa, e pela D2b não se inverte.\n")

    # (b) o condicionamento por salto informa? (curva contra o quantil)
    melhora = []
    for nome in tabela["mercado"].unique():
        base = medidas.get((nome, QUANTIS[0]))
        topo = medidas.get((nome, QUANTIS[-1]))
        if base and topo and np.isfinite(base[f"resíduo {h1}d"]) \
                and np.isfinite(topo[f"resíduo {h1}d"]):
            melhora.append((nome, base[f"resíduo {h1}d"], topo[f"resíduo {h1}d"]))
    subiram = [m for m, b, t in melhora if t > b]
    if melhora:
        texto.append(
            "**O condicionamento por salto informa?** Resíduo de "
            f"{h1} pregão na linha de base (`q0.00`) contra o corte mais "
            f"exigente (`q{QUANTIS[-1]:.2f}`): "
            + " · ".join(f"**{m}** {b:+.1f} → {t:+.1f} bps" for m, b, t in melhora)
            + f". Sobem em **{len(subiram)} de {len(melhora)}** mercados. Se o "
            "resíduo não melhora quando se exige um salto maior, \"salto\" não "
            "é informação — é só o mesmo Δp com menos observações.\n")

    # (c) G2/G3
    if not g2.empty:
        passam = g2[g2["G2 bate?"] == "✅"]["mercado"].tolist()
        if not passam:
            texto.append(
                f"**Nenhum mercado passa no G2** no corte q{QUANTIS[-1]:.2f}: "
                + " · ".join(f"{r['mercado']} (`{r['G2 μ (bps/dia)']}`)"
                             for _, r in g2.iterrows())
                + ". O μ do resíduo sai contra a premissa declarada em todos, "
                "e pela D2b não se inverte.\n")
        else:
            texto.append(
                f"**{len(passam)} de {len(g2)} mercados passam no G2** no corte "
                f"q{QUANTIS[-1]:.2f}: " + ", ".join(f"**{m}**" for m in passam)
                + ". Passar no G2 **não é aprovação** — o gate mede e o destino "
                "segue sendo decisão do dono. O que isto habilita é o G4 (P&L "
                "da sleeve), que é o primeiro critério que exige módulo.\n")
            # Cada linha ✅ sai acompanhada do que a enfraquece. Gerado, não
            # escrito: um veredito positivo com n de um dígito e sem G3 medido
            # é exatamente o tipo de registro que envelhece sem levantar
            # exceção — quarta ocorrência do modo de falha, na D26.
            texto.append("⚠️ **Cada ✅ acima, com o que a enfraquece:**\n")
            for _, linha in g2[g2["G2 bate?"] == "✅"].iterrows():
                mercado = linha["mercado"]
                partes = [f"**{mercado}** — μ de **{linha['eventos no μ']} "
                          f"eventos**"]
                if linha[COL_G3] == "—":
                    partes.append(
                        "**G3 não mensurável**: o mercado não sobrepõe as "
                        "séries que as views vivas leem, então a duplicação "
                        "não foi testada — não é ✅, é vazio")
                else:
                    partes.append(f"G3 {linha[COL_G3]}")
                if mercado in PRECEDENTES:
                    partes.append(PRECEDENTES[mercado])
                texto.append("- " + "; ".join(partes) + ".")
            texto.append("")

    texto.append(
        "**O que isto NÃO diz:** nada sobre P&L, e nada sobre a 1.1. A 3.2 lê o "
        "SALTO; a 1.1 lê a RESOLUÇÃO, e nenhuma linha desta tabela toca a "
        "segunda. G4 continua exigindo backtest, e backtest exige o módulo que "
        "este protocolo se recusa a escrever antes de a linha passar.\n")

    Path(args.saida).write_text("\n".join(texto) + "\n", encoding="utf-8")
    sys.stdout.write(formatada.to_string(index=False) + "\n\n")
    if not g2.empty:
        sys.stdout.write(g2.to_string(index=False) + "\n")
    sys.stdout.write(f"\nescrito: {args.saida}\n")


if __name__ == "__main__":
    main()
