"""Camada tática v2 ligada — o que ela muda na entrega. Felipe.

Primeira rodada de backtest da camada desde que a **12c** a desligou. As duas
sleeves admitidas na **D28** (M4 recessão, M9 Câmara) entram pelo
`MontadorV1._sleeves`, com o `k` do bloco DECLARADO no item 3 e o tamanho pela
âncora `inv(δΣ)·μ` da D16 — **zero parâmetro livre**.

⚠️ **O G4 sai aqui como RELATÓRIO, não como portão** (item 12 da D28). A régua
28.0 do dono não contém resultado: excesso negativo não reprova candidata que
não foi desprovada, lê o Polymarket, não tem overfit e não tem variável
não teórica. Usar o número desta página para escolher configuração seria
reintroduzir a escolha por resultado — o overfit em dois passos do protocolo
da seção 10, agora sem rodada seguinte para desmentir.

**Duas perguntas, e elas são diferentes:**

  1. quanto a camada RENDE sozinha? -> o G4, medido no `dw` PEDIDO, antes de
     qualquer teto. É a P&L da sleeve como estratégia isolada.
  2. quanto a camada muda a ENTREGA? -> a comparação com × sem, no teto de
     referência. Aqui ela disputa o mesmo teto que o tilt das views, então a
     diferença NÃO é a P&L dela: parte é o peso que ela tira das views.

Misturar as duas é o erro que a D10 já cometeu uma vez, quando o teto de
carteira fez a view 2.2 parecer −14 pp pior do que era.

Uso:

    python scripts/camada_tatica_v2.py --raiz .
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from backtest import run_backtest, summary  # noqa: E402
from backtest_v1 import (PONTOS_PERCENTUAIS, SLEEVES_V2,  # noqa: E402
                         carregar)
from config import ASSETS  # noqa: E402
from market_inputs import regua_por_decisao  # noqa: E402

# Tetos varridos. É a MESMA grade da D10, herdada — 1 é o de referência da
# entrega (10a) e os outros existem para responder "a camada perde por si ou
# por disputar o teto?". Não é grade nova e nada aqui escolhe teto.
TETOS = (1.0, 2.0, 3.0, 5.0)

# Quantas maiores contribuições diárias a coluna de robustez remove. Obrigatória
# desde a 15h, que mostrou uma view "de +3,89 pp" que era UM pregão.
MAIORES = 3


def acumulado(serie):
    """Retorno composto de uma série de retornos diários."""
    return float((1.0 + pd.Series(serie).fillna(0.0)).prod() - 1.0)


ROTULO = "sleeves_transversais"


def _diagnostico_da_camada(resultado, data):
    """O diagnóstico da camada no dia, ou None se ela dormiu.

    O `diagnostics` do backtest é `{data: {"views": [...], "taticas":
    [...]}}` — a lista das táticas ATIVAS. Filtrar pelo rótulo é o que
    separa esta camada das sleeves de drift da D16, que podem estar
    ligadas na mesma rodada.
    """
    dia = resultado.diagnostics.get(data) or {}
    return next((d for d in dia.get("taticas", [])
                 if d.get("tatica") == ROTULO), None)


def pnl_da_camada(resultado, retornos, datas):
    """P&L diária da camada sozinha — o G4, no `dw` PEDIDO (antes do teto).

    Antes do teto de propósito: depois dele o `dw` da camada já foi encolhido
    junto com o tilt das views, e o que se mediria seria a sobra da disputa,
    não a estratégia.
    """
    linhas = {}
    for data in datas:
        alvo = _diagnostico_da_camada(resultado, data)
        if alvo is None:
            continue
        dw = np.asarray(alvo["dw"], dtype=float)
        linhas[data] = float(dw @ retornos.loc[data, list(ASSETS)].to_numpy())
    return pd.Series(linhas, dtype=float).sort_index()


def consumo_do_teto(resultado, datas):
    """Σ|dw| pedido pela camada, dia a dia. Quanto do teto ela quer."""
    linhas = {}
    for data in datas:
        alvo = _diagnostico_da_camada(resultado, data)
        if alvo is not None:
            linhas[data] = float(alvo["soma_abs_dw"])
    return pd.Series(linhas, dtype=float).sort_index()


def main():
    # O console do Windows abre em cp1252 e engasga nos rótulos acentuados.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raiz", default=".")
    parser.add_argument("--saida", default="Dump/analises/Camada_tatica_v2.md")
    parser.add_argument("--regua", default=None,
                        help="CSV do `c` por decisão da Lia; o default segue o "
                             "--raiz. `--regua \"\"` mede as duas pontas SEM "
                             "régua, que é como o −2,16 pp da D28.13 saiu")
    parser.add_argument("--regua-nivel", type=float, default=1.0,
                        help="nível da régua (6q). As duas pontas usam o mesmo: "
                             "comparar ponta com régua contra ponta sem mediria "
                             "a régua, não a camada")
    args = parser.parse_args()

    if args.regua is None:
        args.regua = str(Path(args.raiz) / "data" / "lia" / "c_por_decisao.csv")
    regua = (regua_por_decisao(args.regua, nivel=args.regua_nivel)
             if args.regua else None)

    rodadas = {}
    for ligada in (False, True):
        retornos, montador, datas, w_mkt = carregar(args.raiz, sleeves=ligada)
        for teto in TETOS:
            resultado = run_backtest(retornos, montador, w_mkt, datas=datas,
                                     teto_alavancagem=teto, teto_no_tilt=True,
                                     regua=regua)
            rodadas[(ligada, teto)] = (resultado, retornos, datas)
    spy = rodadas[(False, TETOS[0])][1]["SPY"].reindex(
        rodadas[(False, TETOS[0])][2])

    # --- comparação com × sem, ao longo da grade de tetos --------------------
    linhas = []
    for teto in TETOS:
        celula = {}
        for ligada in (False, True):
            resultado, _r, _d = rodadas[(ligada, teto)]
            s = summary(resultado, benchmark=spy)
            celula[ligada] = s
        linhas.append({
            "teto no tilt": f"{teto:.0f}",
            "excesso × SPY (sem)":
                celula[False]["excesso acumulado (líquido − benchmark)"],
            "excesso × SPY (com)":
                celula[True]["excesso acumulado (líquido − benchmark)"],
            "Δ": (celula[True]["excesso acumulado (líquido − benchmark)"]
                  - celula[False]["excesso acumulado (líquido − benchmark)"]),
            "Σ|w| média (com)": celula[True]["alavancagem média (Σ|w|)"],
            "giro (com)": celula[True]["giro diário médio"],
            "breakeven bps (com)": celula[True]["custo de breakeven (bps por lado)"],
        })
    tabela = pd.DataFrame(linhas)
    formatada = tabela.copy()
    for coluna in ("excesso × SPY (sem)", "excesso × SPY (com)", "Δ"):
        formatada[coluna] = tabela[coluna].map(
            lambda v: f"{v * PONTOS_PERCENTUAIS:+.2f} pp")
    for coluna in ("Σ|w| média (com)", "giro (com)", "breakeven bps (com)"):
        formatada[coluna] = tabela[coluna].round(3)

    # --- G4: a camada sozinha ------------------------------------------------
    resultado, retornos, datas = rodadas[(True, TETOS[0])]
    pnl = pnl_da_camada(resultado, retornos, datas)
    consumo = consumo_do_teto(resultado, datas)
    sem_maiores = pnl.drop(pnl.abs().nlargest(MAIORES).index)
    acerto = float((pnl > 0).mean()) if len(pnl) else float("nan")

    g4 = pd.DataFrame([{
        "pregões ativos": len(pnl),
        "acumulado (composto)": acumulado(pnl),
        f"acumulado sem os {MAIORES} maiores em |valor|": acumulado(sem_maiores),
        "acerto de sinal": acerto,
        "maior dia": float(pnl.max()) if len(pnl) else float("nan"),
        "pior dia": float(pnl.min()) if len(pnl) else float("nan"),
    }])

    texto = [
        "# Camada tática v2 — a primeira rodada ligada desde a 12c\n",
        "> Gerado por `scripts/camada_tatica_v2.py`. **Mede; não decide.** "
        "Nenhuma configuração é escolhida por este número: pela régua 28.0 o "
        "resultado não reprova candidata, e o **G4 é relatório, não portão** "
        "(item 12 da D28).\n",
        f"- sleeves ligadas: "
        + " · ".join(f"**{m}** (k = {', '.join(str(k) for k in ks)})"
                     for m, _p, ks in SLEEVES_V2),
        f"- janela: **{datas[0]:%Y-%m-%d} a {datas[-1]:%Y-%m-%d}** "
        f"({len(datas)} pregões); teto de referência = **1**, no tilt (10a)",
        "- tamanho pela âncora `inv(δΣ)·μ` da D16 — **sem `orcamento`**, zero "
        "parâmetro livre",
        "- régua do Ω (Lia): "
        + (f"**LIGADA nas DUAS pontas**, nível {args.regua_nivel:g} (6q) — é a "
           "configuração da entrega. O Δ desta página mede a camada, e não a "
           "régua, porque ela é a mesma dos dois lados"
           if regua else
           "**DESLIGADA nas duas pontas** — não é a configuração da entrega "
           "desde a 6q") + "\n",
        "## 1. O que a camada muda na ENTREGA\n",
        formatada.to_markdown(index=False), "",
        "## 2. O G4 — a camada SOZINHA, no `dw` pedido\n",
        "Antes de qualquer teto: é a P&L da estratégia isolada, não a sobra "
        "da disputa pelo teto com o tilt das views.\n",
        g4.round(4).to_markdown(index=False), "",
        f"**Σ|dw| que a camada PEDE:** mediana **{consumo.median():.2f}** · "
        f"máximo **{consumo.max():.2f}** · pede mais que o teto inteiro em "
        f"**{float((consumo > TETOS[0]).mean()):.0%}** dos pregões ativos.\n",
        "## Leitura\n",
    ]

    # --- leitura, gerada DOS NÚMEROS -----------------------------------------
    # Prosa escrita à mão sobre tabela gerada é o modo de falha que já salvou
    # cinco afirmações falsas neste projeto (D27).
    delta_ref = float(tabela.loc[tabela["teto no tilt"] == "1", "Δ"].iloc[0])
    deltas = tabela["Δ"].to_numpy()
    texto.append(
        f"**No teto de referência a camada custa "
        f"{delta_ref * PONTOS_PERCENTUAIS:+.2f} pp de excesso.** "
        + ("Isso não a reprova: a régua 28.0 não contém resultado, e as duas "
           "sleeves passaram pelos quatro itens dela antes de o backtest "
           "rodar. O que o número faz é dimensionar o custo da decisão.\n"
           if delta_ref < 0 else
           "O sinal é favorável, e continua não sendo critério de admissão "
           "pela mesma régua — entra no relatório como medida, não como "
           "justificativa.\n"))

    texto.append(
        f"**A camada sozinha (G4) acumula "
        f"{acumulado(pnl) * PONTOS_PERCENTUAIS:+.2f} pp** em "
        f"{len(pnl)} pregões ativos, com acerto de sinal de {acerto:.0%}. "
        f"Sem os {MAIORES} maiores dias em |valor| sobra "
        f"{acumulado(sem_maiores) * PONTOS_PERCENTUAIS:+.2f} pp — "
        + ("o resultado **não** é um punhado de pregões, que é o vício que a "
           "15h pegou numa view.\n"
           if abs(acumulado(sem_maiores)) > abs(acumulado(pnl)) * 0.5 else
           "🛑 **o resultado é concentrado em poucos pregões**, exatamente o "
           "padrão que a 15h flagrou: o acumulado não descreve o dia típico.\n"))

    texto.append(
        f"**A camada disputa o teto com as views, e é uma disputa desigual:** "
        f"ela pede Σ|dw| mediano de **{consumo.median():.2f}** contra um teto "
        f"de **{TETOS[0]:.0f}** para o tilt INTEIRO. "
        + ("Em mais da metade dos pregões ativos o pedido dela sozinho já não "
           "cabe, então o corte tira peso das views também — parte do Δ da "
           "seção 1 é isso, não a P&L da camada.\n"
           if float((consumo > TETOS[0]).mean()) > 0.5 else
           "Na maioria dos pregões o pedido dela cabe no teto, então o Δ da "
           "seção 1 é majoritariamente a P&L dela própria.\n"))

    monotono = bool(np.all(np.diff(deltas) >= 0) or np.all(np.diff(deltas) <= 0))
    texto.append(
        "**E a grade de tetos deveria separar as duas coisas.** Se a camada "
        "perdesse por si, o Δ seria negativo em toda a grade; se perdesse por "
        "disputar o teto, melhoraria conforme o teto afrouxa. Medido: "
        + " · ".join(f"teto {t:.0f}: {d * PONTOS_PERCENTUAIS:+.2f} pp"
                     for t, d in zip(TETOS, deltas)) + ".\n")
    if not monotono:
        texto.append(
            "🛑 **O Δ NÃO é monótono no teto, e isso derruba as duas leituras "
            "simples.** Ele piora até o teto "
            f"{TETOS[int(np.argmin(deltas))]:.0f} e só então vira. Um padrão "
            "assim não é *\"a camada perde\"* nem *\"a camada só disputa "
            "espaço\"*: o que muda com o teto é a MISTURA entre o tilt das "
            "views e o da camada, e ela não é linear porque o corte reescala "
            "os dois juntos. **Nenhuma linha desta grade é proposta** — ler o "
            "teto 5 como recomendação seria escolher configuração pelo "
            "resultado, que é o que a régua 28.0 barra.\n")
    elif deltas[-1] > deltas[0]:
        texto.append("O Δ **melhora** com o teto mais frouxo — a disputa "
                     "explica parte do custo.\n")
    else:
        texto.append("O Δ **não** melhora com o teto mais frouxo — a disputa "
                     "pelo teto não é a explicação; o custo é da camada.\n")

    # A tensão que os dois números criam. Sai medida porque é o achado da
    # rodada: uma leitura só do G4 (positivo) ou só do Δ (negativo) descreveria
    # metade do que aconteceu.
    if acumulado(pnl) > 0 and delta_ref < 0:
        texto.append(
            f"⚠️ **O achado da rodada é a tensão entre os dois números.** A "
            f"camada é positiva sozinha "
            f"({acumulado(pnl) * PONTOS_PERCENTUAIS:+.1f} pp) e NEGATIVA "
            f"quando somada ({delta_ref * PONTOS_PERCENTUAIS:+.2f} pp). Não "
            "há contradição: com o teto no tilt, o corte reescala o tilt das "
            "views e o da camada JUNTOS, então entrar não é somar — é dividir "
            "um orçamento fixo de risco. A camada só melhora a entrega se "
            "render mais por unidade de Σ|w| do que o tilt que ela desloca, e "
            "nesta janela ela não rende.\n")
        texto.append(
            "**Isso é medição, não veredito.** A régua 28.0 admite as duas "
            "sleeves por mecanismo, e o dono já declarou que prejuízo não "
            "reprova. O que este parágrafo acrescenta é QUAL é o custo e de "
            "onde ele vem — insumo para a decisão de entregar a camada ligada "
            "ou desligada, que é do dono e não deste artefato.\n")

    texto.append(
        f"⚠️ **O G4 é BRUTO de custo e sem teto.** Ele mede o `dw` pedido "
        f"(Σ|dw| mediano {consumo.median():.2f}), então não é o retorno de uma "
        "carteira executável — é o sinal da estratégia. O custo aparece na "
        "seção 1, onde o breakeven da entrega com a camada é de "
        f"{tabela['breakeven bps (com)'].iloc[0]:.1f} bps por lado contra os "
        "2 bps premissados.\n")

    texto.append(
        "**O que isto NÃO diz:** nada sobre admissão — as sleeves já foram "
        "admitidas pela D28, com base em G0/G1/G2/G3, no corte da amostra e, "
        "na M9, no teste de mercado irmão. E nada corrige as ~200 células da "
        "D27 para comparações múltiplas, que segue sendo a maior limitação "
        "declarada das duas.\n")

    Path(Path(args.raiz) / args.saida).write_text("\n".join(texto) + "\n",
                                                  encoding="utf-8")
    sys.stdout.write(formatada.to_string(index=False) + "\n\n")
    sys.stdout.write(g4.round(4).to_string(index=False) + "\n\n")
    sys.stdout.write(f"escrito: {args.saida}\n")


if __name__ == "__main__":
    main()
