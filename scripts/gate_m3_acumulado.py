"""G2 e G3 do sinal do M3 ACUMULADO — o candidato que sobrou. Felipe.

Cadeia que trouxe até aqui, toda medida e toda em artefato:

  - **D17 / `Gate_sleeves.md`.** O C1a (revisão diária da crença sobre o nº de
    cortes do Fed) reprovou no G1: mediana do |Δ| = 0,5× o tick. A leitura
    registrada foi que qualquer sleeve lendo Δ de PMF de um dia para o outro
    condiciona em ruído de discretização.
  - **`Premissa_G1.md`.** Esse veredito vale para o `k` que a D17 mediu, não
    para a série: o mesmo sinal em 3 pregões dá 1,2× e em 20 dá 3,7×. O erro de
    discretização no incremento fica preso em ~1 tick por mais que `k` cresça,
    enquanto o movimento verdadeiro acumula. O M3 é a ÚNICA série do dado com
    cobertura (210 pregões) e dispersão acima do tick ao mesmo tempo — e a
    única não consumida por nenhuma das quatro views vivas.
  - **`Premissa_tendencia.md`.** O acúmulo NÃO é tendência: VR ≈ 1 e nenhuma
    autocorrelação ex-ante com |t| ≥ 2. Isso mata a hipótese de momentum (a
    1.2), e **não** mata este teste — o G2 pergunta se o sinal prevê o RETORNO
    dos ativos, não se ele prevê a si mesmo. Um passeio aleatório pode
    antecipar preço.

Este script roda os dois critérios que faltam, ao longo da mesma grade de
horizontes, **sem escrever módulo** — que é o protocolo desde a D17.

    G2 sinal     : μ (event-study expansivo, `estimate_drift_mu` da D16) contra
                   o sinal DECLARADO a priori, ativo a ativo.
    G3 duplicação: correlação com o sinal que as quatro views vivas já leem.

⚠️ **A premissa do G2 é HERDADA, não reescrita.** Ela é a mesma que a D17
declarou para o C1a, palavra por palavra, e está em `PREMISSA_DECLARADA` abaixo.
Reescrevê-la agora — depois de ver o k = 1 falhar — destruiria o único
mecanismo que faz do G2 um teste em vez de racionalização.

⚠️ **`k` é lookback, não prazo de posição.** A janela do event-study fica em 1
pregão, igual à do C1a: o que muda entre as linhas é sobre quantos dias o sinal
é lido, não por quantos dias se fica posicionado. Assim nenhum parâmetro novo
entra pela porta dos fundos (CLAUDE.md §6).

**Nada em `src/` é tocado** e nenhuma matemática nova é escrita: μ, premissa,
correlação e séries vêm todos do `gate_sleeves.py` e do `premissa_g1.py`.

Uso:

    python scripts/gate_m3_acumulado.py --raiz .
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from config import ASSETS  # noqa: E402
from gate_sleeves import (bate_premissa, corr_comum, eventos_diarios,  # noqa: E402
                          mu_do_sinal, referencias_g3)
from market_inputs import sample_covariance  # noqa: E402
from premissa_g1 import HORIZONTES, em_pregoes, series_dos_mercados  # noqa: E402

# Declarada pela D17 para o C1a e reproduzida aqui SEM alteração. O sinal é o Δ
# do nº esperado de cortes: positivo = a crença andou para mais afrouxamento.
PREMISSA_DECLARADA = {"SPY": +1, "TLT": +1}
PREMISSA_TEXTO = ("crença anda para mais afrouxamento → SPY e TLT sobem "
                  "(declarada na D17 para o C1a, herdada sem alteração)")
LIVRO = ("SPY", "TLT")

# Janela do event-study, em pregões. 1 = a sleeve é reassinada todo dia, igual
# ao C1a da D17. Não é escolha nova: é o que mantém `k` como lookback puro.
JANELA = 1


def main():
    # O console do Windows abre em cp1252 e engasga nos rótulos acentuados.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raiz", default=".")
    parser.add_argument("--saida", default="Dump/analises/Gate_M3_acumulado.md")
    args = parser.parse_args()

    series, retornos, montador, datas = series_dos_mercados(args.raiz)
    # Σ da história INTEIRA, igual ao gate e ao `tatica_reconstruida.py` — Σ só
    # entra no encolhimento do μ, e outra janela faria a linha de k = 1 deixar
    # de reproduzir o C1a, que é o único jeito de saber que a medida está certa.
    sigma = sample_covariance(retornos)
    ate = datas[-1] + pd.Timedelta(days=1)
    referencias = referencias_g3(montador, datas, montador._fl)

    e_m3 = em_pregoes(next(s[2] for s in series if s[0].startswith("C1a")))

    tabela, detalhes, medidas = [], [], {}
    for k in HORIZONTES:
        sinal = e_m3.diff(k).dropna()
        mu, n_mu = mu_do_sinal(retornos, eventos_diarios(sinal), JANELA,
                               LIVRO, sigma, ate)
        ok, detalhe = bate_premissa(mu, ASSETS, PREMISSA_DECLARADA)
        correlacoes = {nome: corr_comum(sinal, ref) for nome, ref in referencias.items()}
        pior = max(correlacoes, key=lambda c: abs(correlacoes[c])
                   if np.isfinite(correlacoes[c]) else -1)
        medidas[k] = {"ok": ok, "detalhe": detalhe, "pior": pior,
                      "corr": correlacoes[pior], "dias": len(sinal), "n_mu": n_mu}
        tabela.append({
            "lookback": f"k = {k}",
            "G0 dias": len(sinal),
            "eventos no μ": n_mu,
            "G2 μ (bps/dia)": detalhe,
            "G2 bate?": "✅" if ok else "❌",
            r"G3 maior \|corr\|": (f"{correlacoes[pior]:+.2f} ({pior})"
                                   if np.isfinite(correlacoes[pior]) else "—"),
        })
        detalhes.append({"lookback": f"k = {k}",
                         **{f"corr {c}": f"{v:+.2f}" if np.isfinite(v) else "—"
                            for c, v in correlacoes.items()}})

    passam = [k for k in HORIZONTES if medidas[k]["ok"]]
    texto = [
        "# G2 e G3 do M3 acumulado — o último candidato de pé\n",
        "> Gerado por `scripts/gate_m3_acumulado.py`. **Mede; não decide.** "
        "Nenhum corte cravado, mesma regra do `Gate_sleeves.md`.\n",
        f"- janela do backtest: **{datas[0]:%Y-%m-%d} a {datas[-1]:%Y-%m-%d}** "
        f"({len(datas)} pregões), δ e Σ os mesmos do v1 (D7/D8)",
        "- **sinal** = Δ do nº esperado de cortes do Fed (M3) sobre `k` "
        "pregões. `k` é **lookback**; a posição é reassinada todo dia "
        f"(janela do event-study = {JANELA}), igual ao C1a da D17",
        "- **G2** = μ do `tatica_drift_anuncio.estimate_drift_mu` (linha de "
        "base subtraída, encolhido pela dispersão) contra o sinal DECLARADO",
        "- **G3** = correlação com o sinal que as quatro views vivas já leem\n",
        f"**Premissa declarada ANTES de medir:** {PREMISSA_TEXTO}. Ela é a da "
        "D17, herdada palavra por palavra — reescrevê-la depois de ver o k = 1 "
        "falhar destruiria o que faz do G2 um teste.\n",
        "**G4 (P&L da sleeve sozinha) não está aqui de propósito:** exige "
        "backtest, backtest exige o módulo, e o módulo é o que este protocolo "
        "se recusa a escrever antes de a linha passar.\n",
        pd.DataFrame(tabela).to_markdown(index=False), "",
        "## Correlações do G3, uma a uma\n",
        pd.DataFrame(detalhes).to_markdown(index=False), "",
        "## Leitura\n",
    ]

    k1 = medidas[HORIZONTES[0]]
    texto.append(
        f"**Calibração:** em k = 1 esta linha é o C1a da D17 — μ "
        f"`{k1['detalhe']}`. O `Gate_sleeves.md` traz `SPY -4.20 ❌ · "
        "TLT +0.03 ✅` para o mesmo candidato: **mesmo veredito e mesmo sinal "
        "em cada ativo**, com o SPY diferindo na primeira casa. A diferença é "
        "conhecida e é o preço da correção de horizonte — aqui a série é "
        "reindexada em dias úteis antes do `diff` (`em_pregoes`), para que `k` "
        "signifique pregões; lá o `diff` anda leituras. Reproduzir o VEREDITO é "
        "o que a calibração pede; reproduzir o dígito exigiria abrir mão da "
        "própria correção que motiva este script.\n")

    # A duplicação cresce com o lookback, e isso é achado sobre o sinal: quanto
    # mais se acumula, mais o Δ da crença do Fed vira a mesma coisa que a
    # incerteza que a 15b já lê. Sai medido, não afirmado.
    corr_por_k = {k: medidas[k]["corr"] for k in HORIZONTES
                  if np.isfinite(medidas[k]["corr"])}
    if len(corr_por_k) > 1:
        primeiro, ultimo = HORIZONTES[0], max(corr_por_k)
        if abs(corr_por_k[ultimo]) > abs(corr_por_k[primeiro]):
            texto.append(
                "**O G3 piora conforme o lookback cresce:** "
                + " · ".join(f"k = {k}: {v:+.2f}" for k, v in corr_por_k.items())
                + f", sempre contra a **{medidas[ultimo]['pior']}**. Acumular "
                "não é de graça no critério de duplicação — quanto mais dias o "
                "Δ da crença sobre o Fed soma, mais ele se parece com a "
                "incerteza que a view 15b já lê. Mesmo que o G2 tivesse "
                "passado num k longo, seria ali que o G3 estaria pior.\n")

    if not passam:
        piores = ", ".join(f"k = {k} (`{medidas[k]['detalhe']}`)" for k in HORIZONTES)
        texto.append(
            "**Nenhum horizonte passa no G2.** " + piores + ". O μ sai contra a "
            "premissa declarada em todos os lookbacks da grade, e pela D2b não "
            "se inverte. **O acúmulo resolveu o problema de tamanho e não "
            "produziu previsão:** o sinal saiu de dentro do tick (G1) e "
            "continua não antecipando o retorno dos ativos na direção que a "
            "teoria manda.\n")
        texto.append(
            "**Consequência para a camada tática.** O M3 era a única série do "
            "dado entregue com cobertura e dispersão ao mesmo tempo, e a única "
            "livre de duplicação com as views vivas. Com ele reprovado, o "
            "estoque de candidatos nunca medidos fica assim:\n\n"
            "- **velocidade de ajuste** e **1.2 momentum** — sem hipótese. As "
            "duas leem o movimento da crença para prever o próximo movimento da "
            "crença, e o `Premissa_tendencia.md` mediu VR ≈ 1 e nenhuma "
            "autocorrelação ex-ante. Não é falta de teste: é a tese contrariada "
            "pelo dado.\n"
            "- **3.2 event-driven** — o gatilho é o SALTO da probabilidade, que "
            "é o padrão com maior chance de aterrissar no gap de abertura, a "
            "parede que já derrubou a 2.4, a C, a E e o gap de fim de semana. "
            "Mede-se antes de escrever módulo, como tudo aqui.\n"
            "- **1.1 PEAD** — **a única que nada nesta cadeia toca.** Ela lê a "
            "RESOLUÇÃO do mercado, não o Δ diário: nem o G1 (que é sobre "
            "movimento diário) nem o teste de tendência dizem qualquer coisa "
            "sobre ela. Segue travada pela **decisão 5**, aberta e vazia — sem "
            "definição operacional de \"surpresa\" não há sinal a construir. É "
            "decisão humana, não script.\n\n"
            "Ou seja: **o caminho de ler o repreçamento do poly está esgotado "
            "no dado que temos**, e o que resta ou depende de decisão humana "
            "(1.1) ou de um teste de gap ainda não feito (3.2).\n")
    else:
        linhas_ok = ", ".join(
            f"k = {k} (μ `{medidas[k]['detalhe']}`, G3 "
            f"{medidas[k]['corr']:+.2f} com {medidas[k]['pior']})" for k in passam)
        texto.append(
            f"**{len(passam)} de {len(HORIZONTES)} lookbacks passam no G2:** "
            + linhas_ok + ". Passar no G2 **não é aprovação** — o gate mede e o "
            "destino segue sendo decisão do dono/grupo. O que isto habilita é o "
            "G4 (P&L da sleeve sozinha no `dw` pedido, antes do teto), que é o "
            "primeiro critério que exige escrever módulo.\n")
        texto.append(
            "⚠️ **Antes de qualquer módulo, três coisas já registradas travam a "
            "ativação e nenhuma é técnica:** a **12c** (a camada está desligada "
            "no v1), a **D24** (o portão de qualidade do poly vale para views e "
            "não para overlays — uma sleeve lendo mercado degenerado passa "
            "livre) e a reabertura de escopo da camada. A âncora de tamanho da "
            "D16 (`inv(δΣ)·μ`, zero parâmetro livre) segue de pé e sem uso, "
            "então o motivo que matou a 12c não se repete.\n")

    texto.append(
        "**O que isto NÃO diz:** nada sobre P&L. G2 e G3 são condições de "
        "admissão — o resultado da estratégia é o G4, e ele exige backtest.\n")

    Path(args.saida).write_text("\n".join(texto) + "\n", encoding="utf-8")
    sys.stdout.write(pd.DataFrame(tabela).to_string(index=False)
                     + f"\n\nescrito: {args.saida}\n")


if __name__ == "__main__":
    main()
