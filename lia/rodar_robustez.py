"""Robustez da calibração do Ω: o resultado depende do corte escolhido?

Duas verificações que a calibração principal (`rodar_calibracao.py` e
`rodar_calibracao_cpi.py`) deixou em aberto:

**1. Número de faixas do teste.** As rodadas usaram tercis. Aqui o teste roda
com 2, 3, 4 e 5 faixas. Ponto de método que o resultado torna explícito: o
`spearman` **não depende** de `n_faixas` — ele é calculado sobre os postos, e
as faixas só existem para a leitura de monotonicidade. Então a robustez que
importa aqui não é a da ordenação (que é invariante por construção, e afirmar
o contrário seria vender como resultado algo que é identidade), e sim a da
**flag de monotonicidade**: uma candidata que só é monotônica em tercis está
apoiada no corte.

**2. Alvo alternativo: erro contra a resolução do mercado.** A calibração usou
a variação futura da probabilidade, o que é circular para a comparação entre
as duas formas de colapso — cada uma tende a vencer no alvo medido por ela
mesma. O erro contra o desfecho é independente das duas.

⚠️ **O desfecho NÃO pode sair do próprio mercado.** Tomar o bucket com maior
probabilidade no último slot como "resultado" assumiria que o mercado acertou,
e o erro contra ele seria pequeno por construção justamente onde o mercado
estava confiante — circularidade pior que a que se queria remover. O desfecho
vem do **DFF** (taxa efetiva dos fed funds, FRED, entregue pelo Paulo), e a
derivação é validada contra as reuniões em que o mercado estava inequívoco.

Escopo: desde 10/08/2026 o alvo por desfecho roda nas **duas views**. Na 2.3 o
desfecho vem do DFF; na 2.2 vem do **CPI MoM realizado** que o Paulo entregou
(`cpi_realizado_mom.json`) — SA *first-print* do ALFRED, o valor que existia no
dia do release, arredondado à casa decimal em que a própria rule do mercado
resolve. Antes disso o pipeline trazia só as datas de divulgação, e a limitação
"a verificação existe numa view só" era declarada no relatório.

Decisões da dona sobre o recorte da 2.2 (registradas na 6m, antes de rodar):
out/2025 e nov/2025 ficam **fora** — têm resolução do UMA mas nenhum valor do
BLS, e desfecho que sai do mercado é a circularidade que o teste existe para
evitar; jul/2026 fica fora por calendário (release em 12/08, mercado aberto).
Sobram **15 meses**. Os dois mercados legados (dez/2024, jan/2025) têm rule que
não nomeia a série, então "SA" ali é inferência — roda-se a **sensibilidade sem
os dois** para medir se a ressalva importa.

Uso:

    python -m lia.rodar_robustez --dados <dir com data/ e src/>
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from lia.calibracao_omega import (
    comparar_candidatas,
    erro_vs_resolucao,
    preparar_pmf,
)
from lia.rodar_calibracao import (
    HORIZONTES_SLOTS,
    alvo_futuro,
    carregar_eventos,
    montar_candidatas,
    montar_painel,
)

FAIXAS_EM_TESTE = (2, 3, 4, 5)

# Janelas de dias corridos em torno da reunião para ler a taxa efetiva. A
# decisão do FOMC sai no 2º dia e vale a partir do dia seguinte, então o dia
# da reunião fica FORA das duas janelas.
DIAS_ANTES = (-7, -1)
DIAS_DEPOIS = (1, 7)
PASSO_BPS = 25.0  # a grade de decisão do Fed; não é parâmetro de modelo


def carregar_dff(raiz):
    """Taxa efetiva dos fed funds (FRED DFF), entregue pelo pipeline."""
    dff = pd.read_csv(Path(raiz) / "data" / "raw" / "fred_DFF.csv",
                      parse_dates=["observation_date"])
    return dff.set_index("observation_date").DFF


def desfecho_bps(dff: pd.Series, reuniao) -> float:
    """Δ da taxa efetiva na reunião, em bps, arredondado à grade de 25.

    Média da taxa na janela posterior menos média na anterior. A média (em vez
    da leitura de um dia) absorve o ruído diário da taxa efetiva, que oscila
    alguns pontos-base dentro do mesmo regime de política.

    Devolve NaN quando falta dado em qualquer das duas janelas — sem desfecho
    inventado.
    """
    reuniao = pd.Timestamp(reuniao)
    antes = dff.loc[reuniao + pd.Timedelta(days=DIAS_ANTES[0]):
                    reuniao + pd.Timedelta(days=DIAS_ANTES[1])]
    depois = dff.loc[reuniao + pd.Timedelta(days=DIAS_DEPOIS[0]):
                     reuniao + pd.Timedelta(days=DIAS_DEPOIS[1])]
    if antes.empty or depois.empty:
        return float("nan")
    delta = (depois.mean() - antes.mean()) * 100.0
    return float(np.round(delta / PASSO_BPS) * PASSO_BPS)


def bucket_vencedor(valores, abertos, delta) -> int:
    """Índice do bucket que o desfecho resolveu, ou -1 se nenhum casa.

    As colunas vêm ordenadas pelo Δtaxa. As pontas podem ser ABERTAS ("50+
    bps"), e aí cobrem tudo além do próprio valor; as faixas internas exigem
    casamento exato com a grade de 25 bps.
    """
    if np.isnan(delta):
        return -1
    if abertos[0] and delta <= valores[0]:
        return 0
    if abertos[-1] and delta >= valores[-1]:
        return len(valores) - 1
    casam = np.flatnonzero(np.isclose(valores, delta))
    return int(casam[0]) if casam.size else -1


def validar_desfechos(eventos, dff):
    """Confere a derivação do DFF contra as reuniões inequívocas do mercado.

    Nas reuniões em que o mercado terminou com um bucket acima de 0,9, o
    desfecho é conhecido sem ambiguidade. Se a derivação do DFF concordar
    nessas, ela está lendo a grade certa — e nas demais ela responde o que o
    mercado não respondeu.
    """
    linhas = []
    for evento, (probs, valores, abertos, reuniao) in eventos.items():
        delta = desfecho_bps(dff, reuniao)
        indice = bucket_vencedor(valores, abertos, delta)
        ultima = probs.iloc[-1].dropna()
        if ultima.empty:
            continue
        mercado = ultima.idxmax()
        confiante = ultima.max() > 0.9
        derivado = probs.columns[indice] if indice >= 0 else None
        linhas.append({
            "evento": evento,
            "reuniao": reuniao.date(),
            "delta_bps": delta,
            "p_max_final": round(float(ultima.max()), 3),
            "concorda": (derivado == mercado) if derivado is not None else False,
            "inequivoco": confiante,
        })
    return pd.DataFrame(linhas).set_index("evento")


def erro_contra_desfecho(eventos, dff, grade, daily_preopen):
    """Massa de probabilidade que o mercado alocou FORA do desfecho.

    `1 − p_vencedor` sobre a PMF renormalizada, que é `0,5·Σ_b |p_b − δ_b|`
    contra a distribuição degenerada no bucket que resolveu — a mesma métrica
    de distância usada no resto da calibração, só que contra o resultado em vez
    de contra a leitura seguinte. Reusa `erro_vs_resolucao` para não haver duas
    implementações da mesma conta.

    Evento sem desfecho derivável fica de fora, nunca com erro inventado.
    """
    pedacos = []
    for evento, (probs, valores, abertos, reuniao) in eventos.items():
        indice = bucket_vencedor(valores, abertos, desfecho_bps(dff, reuniao))
        if indice < 0:
            continue
        crua = probs if grade == "12h" else daily_preopen(probs)
        pronta = preparar_pmf(crua)
        if pronta.empty:
            continue
        erro = erro_vs_resolucao(pronta.iloc[:, indice], 1.0)
        erro.index = pd.MultiIndex.from_product(
            [[evento], erro.index], names=["evento", "data"])
        pedacos.append(erro)
    return pd.concat(pedacos).sort_index() if pedacos else pd.Series(dtype=float)


def carregar_cpi_realizado(raiz):
    """CPI MoM realizado por mercado-mês, do arquivo do Paulo.

    Devolve `{slug: (valor_1casa, bucket_resolvido, legado)}`. `legado`
    marca os dois mercados cuja rule não nomeia a série (dez/2024 e
    jan/2025), para a sensibilidade da 6m.

    Fica de fora quem não tem `sa_fp_1dec`: out/2025 (o BLS nunca publicou
    — shutdown) e nov/2025 (sem MoM, porque falta a base de outubro) têm
    resolução do UMA mas nenhum valor independente, e a 6h fixou que o
    desfecho não sai do mercado; jul/2026 ainda não teve release.
    """
    caminho = Path(raiz) / "data" / "raw" / "cpi_realizado_mom.json"
    with open(caminho, encoding="utf-8") as arquivo:
        registros = json.load(arquivo)
    return {
        r["slug"]: (r["sa_fp_1dec"], r["bucket_vencedor"], r["ajuste_regra"] == "?")
        for r in registros
        if r.get("sa_fp_1dec") is not None
    }


def bucket_do_valor(valores, realizado):
    """Índice do bucket de CPI que o valor realizado resolveu, ou -1.

    Mesma regra do `bucket_vencedor` do FOMC, com a diferença registrada na
    decisão 11b: no CPI as **pontas são abertas** pelas regras do mercado
    ("0,1% ou menos"), mas o slug não diz isso — sai `increase-by-0pt1`
    igual a um bucket interno. Então trata-se primeira e última coluna como
    abertas, e as internas exigem casamento exato com a grade de 0,1 pp.
    """
    if realizado is None or np.isnan(realizado):
        return -1
    if realizado <= valores[0]:
        return 0
    if realizado >= valores[-1]:
        return len(valores) - 1
    casam = np.flatnonzero(np.isclose(valores, realizado, atol=1e-6))
    return int(casam[0]) if casam.size else -1


def validar_desfechos_cpi(eventos, realizado):
    """Confere a derivação do CPI do FRED contra o bucket que o UMA resolveu.

    Análoga à validação do DFF na 2.3, e com o mesmo estatuto: o alvo é o
    valor do BLS, e a concordância com a resolução do mercado só mostra que
    a leitura da grade de buckets está certa. Discordância aqui seria erro
    de grade, não evidência sobre o mercado.
    """
    linhas = []
    for evento, (pmf, valores, _data) in eventos.items():
        chave = next((s for s in realizado if evento.endswith(s)), None)
        if chave is None:
            continue
        valor, bucket_uma, legado = realizado[chave]
        indice = bucket_do_valor(valores, valor)
        derivado = pmf.columns[indice] if indice >= 0 else None
        linhas.append({
            "slug": chave,
            "cpi_realizado": valor,
            "bucket_derivado": derivado.split("increase-by-")[-1] if derivado else None,
            "bucket_uma": bucket_uma,
            "legado": legado,
        })
    return pd.DataFrame(linhas).set_index("slug")


def erro_contra_desfecho_cpi(eventos, realizado, grade, daily_preopen, sem_legados=False):
    """Massa que o mercado alocou fora do bucket que o CPI realizado resolveu.

    Mesma métrica da 2.3 (`erro_vs_resolucao` sobre a PMF renormalizada),
    com o desfecho vindo do BLS em vez do DFF. `sem_legados` remove
    dez/2024 e jan/2025 — a sensibilidade da 6m.
    """
    pedacos = []
    for evento, (pmf, valores, _data) in eventos.items():
        chave = next((s for s in realizado if evento.endswith(s)), None)
        if chave is None:
            continue
        valor, _bucket_uma, legado = realizado[chave]
        if sem_legados and legado:
            continue
        indice = bucket_do_valor(valores, valor)
        if indice < 0:
            continue
        crua = pmf if grade == "12h" else daily_preopen(pmf)
        pronta = preparar_pmf(crua)
        if pronta.empty:
            continue
        erro = erro_vs_resolucao(pronta.iloc[:, indice], 1.0)
        erro.index = pd.MultiIndex.from_product(
            [[evento], erro.index], names=["evento", "data"])
        pedacos.append(erro)
    return pd.concat(pedacos).sort_index() if pedacos else pd.Series(dtype=float)


def relatar_faixas(candidatas, erro, rotulo):
    """Roda o teste com 2, 3, 4 e 5 faixas e mostra onde a flag muda."""
    with np.errstate(invalid="ignore", divide="ignore"):
        tabelas = {n: comparar_candidatas(candidatas, erro, n)
                   for n in FAIXAS_EM_TESTE}
    base = tabelas[3]
    saida = pd.DataFrame({
        "spearman": base.spearman,
        "n_obs": base.n_observacoes,
    })
    for n in FAIXAS_EM_TESTE:
        saida[f"mono_{n}"] = tabelas[n].monotonica.reindex(base.index)
    colunas = [f"mono_{n}" for n in FAIXAS_EM_TESTE]
    saida["mono_sempre"] = saida[colunas].all(axis=1)
    print(f"\n-- {rotulo} --")
    print(saida.to_string(float_format=lambda v: f"{v: .4f}"))

    # A invariância é a checagem que impede vender identidade como resultado.
    # `equal_nan`: candidata que fica CONSTANTE no recorte tem spearman NaN em
    # todas as contagens — é degeneração da candidata, não dependência do
    # corte, e sem isto a checagem acusaria uma diferença que não existe.
    iguais = all(np.allclose(tabelas[n].spearman.reindex(base.index),
                             base.spearman, equal_nan=True)
                 for n in FAIXAS_EM_TESTE)
    print(f"   spearman idêntico nas {len(FAIXAS_EM_TESTE)} contagens de "
          f"faixa: {iguais}")
    degeneradas = list(base.index[base.spearman.isna()])
    if degeneradas:
        print(f"   AVISO: score constante neste recorte (spearman "
              f"indefinido): {', '.join(degeneradas)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dados", required=True, help="dir com data/ e src/")
    args = ap.parse_args()

    eventos, daily_preopen = carregar_eventos(args.dados)
    dff = carregar_dff(args.dados)

    print("=" * 72)
    print("VALIDAÇÃO DO DESFECHO DERIVADO DO DFF")
    validacao = validar_desfechos(eventos, dff)
    inequivocas = validacao[validacao.inequivoco]
    print(validacao.to_string())
    print(f"\nreuniões com desfecho derivável: "
          f"{int(validacao.delta_bps.notna().sum())} de {len(validacao)}")
    print(f"concordância nas inequívocas (p_max > 0,9): "
          f"{int(inequivocas.concorda.sum())} de {len(inequivocas)}")
    ambiguas = validacao[~validacao.inequivoco]
    if len(ambiguas):
        print(f"reuniões que o mercado NÃO resolveu e o DFF resolveu: "
              f"{int((ambiguas.delta_bps.notna()).sum())}")

    for grade in ("12h", "24h"):
        painel = montar_painel(eventos, daily_preopen, grade)
        candidatas, _ = montar_candidatas(painel, grade)
        print("\n" + "=" * 72)
        print(f"GRADE {grade} — {len(painel)} slots")

        for horizonte in HORIZONTES_SLOTS:
            relatar_faixas(candidatas, alvo_futuro(painel, "var_total", horizonte),
                           f"alvo: variação futura, h={horizonte} slots")

        erro = erro_contra_desfecho(eventos, dff, grade, daily_preopen)
        alinhado = erro.reindex(painel.index)
        if alinhado.notna().sum() > max(FAIXAS_EM_TESTE):
            relatar_faixas(candidatas, alinhado,
                           "alvo: erro contra o DESFECHO (DFF) — não circular")

    rodar_cpi(args.dados, daily_preopen)


def rodar_cpi(raiz, daily_preopen):
    """O mesmo teste por desfecho na 2.2, com o CPI realizado do Paulo.

    Fecha a limitação que o relatório declarava: até 10/08/2026 a
    verificação de não circularidade existia numa view só.
    """
    from lia.rodar_calibracao_cpi import (  # noqa: E402
        carregar_eventos_cpi,
        carregar_volume,
    )
    from lia.rodar_calibracao_cpi import montar_candidatas as montar_candidatas_cpi
    from lia.rodar_calibracao_cpi import montar_painel as montar_painel_cpi

    eventos = carregar_eventos_cpi(raiz)
    realizado = carregar_cpi_realizado(raiz)
    volume = carregar_volume(raiz)

    print("\n" + "=" * 72)
    print("VIEW 2.2 (CPI) — DESFECHO DERIVADO DO CPI REALIZADO (BLS/ALFRED)")
    validacao = validar_desfechos_cpi(eventos, realizado)
    print(validacao.to_string())
    concorda = validacao.bucket_derivado.notna()
    print(f"\nmeses com desfecho derivável: {len(validacao)} de {len(eventos)} "
          f"mercados-mês ({len(realizado)} com valor no arquivo do Paulo)")
    print(f"derivação casa a grade da PMF em: {int(concorda.sum())} de "
          f"{len(validacao)}")
    print(f"legados com SA inferido (dez/2024, jan/2025): "
          f"{int(validacao.legado.sum())}")

    for grade in ("12h", "24h"):
        painel = montar_painel_cpi(eventos, volume, daily_preopen, grade)
        candidatas = montar_candidatas_cpi(painel, grade)
        print("\n" + "=" * 72)
        print(f"CPI · GRADE {grade} — {len(painel)} slots")
        for sem_legados in (False, True):
            erro = erro_contra_desfecho_cpi(
                eventos, realizado, grade, daily_preopen, sem_legados
            )
            alinhado = erro.reindex(painel.index)
            if alinhado.notna().sum() <= max(FAIXAS_EM_TESTE):
                continue
            rotulo = ("alvo: erro contra o DESFECHO (CPI realizado)"
                      + (" — SEM os 2 legados" if sem_legados else ""))
            relatar_faixas(candidatas, alinhado, rotulo)


if __name__ == "__main__":
    main()
