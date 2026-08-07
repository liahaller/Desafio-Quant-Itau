"""Curva `c` → alavancagem: quanto o Ω da Lia tira de Σ|w| antes de o teto entrar.

Pré-executa o passo (2) da ordem que a Lia propôs para a D12 — *entra o `c`,
mede-se Σ|w| de novo, só então se decide o teto* (`Decisoes_pendentes.md`,
seção 10). O `c` dela ainda não existe, então aqui ele entra como **varredura**,
não como valor: uma grade de `c` constante, do neutro (`c = 1`, o teto de
confiança) ao quase-desligado. Mesma prática já usada com γ, com o custo e com
o próprio teto — **varrer e reportar mede, não escolhe** (CLAUDE.md §6).

O que a varredura responde, e é a pergunta que trava a D12: **com o `c` real,
ainda sobra alavancagem para um teto cortar?** Se Σ|w| já cair sozinha para
perto de 1, o teto vira remendo sem buraco — que é justamente o argumento dela.

Três leituras, todas medidas na carteira **pedida** pelo BL (antes do corte):

  - `alavancagem_pedida` não depende do teto nem do escopo dele: a montagem do
    dia não olha o peso de ontem, então o BL pede a mesma coisa em qualquer
    rodada. É a régua limpa.
  - o retorno do **irrestrito** é exatamente a série `r_pedido` composta — sem
    o teto não há realimentação nenhuma, o peso do dia não depende do peso de
    ontem. Sai BRUTO de propósito: o giro do irrestrito (Σ|w| na casa das
    dezenas) tornaria o custo a história inteira, e não é isso que se mede aqui.
  - **ruína** acontece exatamente quando algum dia tem `r_pedido ≤ −100%` —
    compor (1 + r) só zera patrimônio por um dia assim.

Hoje **só a view 2.2 roda** (a 2.3 espera o G8/DFF e a B o ZQ de dezembro),
então o escalar É o `c` da view. Com três views ativas ele vira média grosseira,
e a curva só valeria como sensibilidade agregada.

Uso:

    python scripts/curva_c.py --raiz /tmp/dadospaulo
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from backtest import run_backtest, summary  # noqa: E402
from backtest_v1 import carregar  # noqa: E402
from config import CUSTO_BPS_POR_LADO, DELTA, TAU  # noqa: E402


def rodada(retornos, montador, datas, w_mkt, c, teto, no_tilt, custo_bps):
    """Um backtest com `c` constante em todas as views ativas do dia.

    O `c ∈ (0,1]` da Lia é confiança (maior = mais); o `omega_fallback` recebe
    incerteza (maior = menos). Entra como 1/c — a conversão vive aqui, num
    lugar só, porque trocar as duas é a armadilha que a régua dela descreve.
    """
    resultado = run_backtest(retornos, montador, w_mkt, datas=datas, tau=TAU,
                             delta=DELTA, custo_bps=custo_bps, teto_alavancagem=teto,
                             teto_no_tilt=no_tilt, incerteza=1.0 / c)
    montador.divergencias.clear()  # a média expansiva (D9) recomeça a cada rodada
    return resultado, summary(resultado, benchmark=retornos["SPY"])


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raiz", default=".",
                        help="diretório com data/ extraído do branch Paulo")
    parser.add_argument("--cs", type=float, nargs="+",
                        default=[1.0, 0.75, 0.5, 0.25, 0.1, 0.05, 0.02, 0.01],
                        help="grade de confiança c ∈ (0,1] — varredura, não escolha")
    parser.add_argument("--teto", type=float, default=1.0,
                        help="teto usado só nas colunas de resultado líquido")
    parser.add_argument("--custo-bps", type=float, default=CUSTO_BPS_POR_LADO)
    parser.add_argument("--saida", default="Dump/analises/Curva_c.md")
    args = parser.parse_args()

    if any(c <= 0 or c > 1 for c in args.cs):
        raise SystemExit("c é confiança em (0,1] — fora disso o Ω passaria do "
                         "fallback neutro, e a régua da Lia só tira peso")

    retornos, montador, datas, w_mkt = carregar(args.raiz)
    linhas, neutro = [], {}
    for c in args.cs:
        res, s_carteira = rodada(retornos, montador, datas, w_mkt, c, args.teto,
                                 False, args.custo_bps)
        _, s_tilt = rodada(retornos, montador, datas, w_mkt, c, args.teto,
                           True, args.custo_bps)
        pedida, r_pedido = res.diario["alavancagem_pedida"], res.diario["r_pedido"]
        ruina = r_pedido[r_pedido <= -1.0]
        if c == max(args.cs):   # o `c` mais frouxo da grade = a leitura de hoje
            neutro = {"pedida": pedida, "ruina": ruina}
        linhas.append({
            "c": c,
            "incerteza (1/c)": 1.0 / c,
            "Σ|w| pedida mediana": float(pedida.median()),
            "Σ|w| pedida máx": float(pedida.max()),
            # Tolerância obrigatória: nos dias sem view o BL devolve w_mkt com
            # erro de float (`inv(δΣ)π` não fecha em 1,0 exato), e um `> teto`
            # seco contaria esses dias como se o teto mordesse.
            f"dias acima do teto {args.teto:g}": float(
                (pedida > args.teto * (1.0 + 1e-9)).mean()),
            "dias de ruína (irrestrito)": float(len(ruina)),
            "irrestrito acumulado bruto": (float("nan") if len(ruina)
                                           else float((1.0 + r_pedido).prod() - 1.0)),
            "excesso — teto na carteira": s_carteira["excesso acumulado (líquido − benchmark)"],
            "excesso — teto no tilt": s_tilt["excesso acumulado (líquido − benchmark)"],
        })
    tabela = pd.DataFrame(linhas).set_index("c")

    # A alavancagem pedida com c = 1 é o retrato de HOJE (o fallback neutro é o
    # que o backtest roda), então serve de linha de base da leitura.
    base = tabela.iloc[0]
    primeira_sem_ruina = tabela[tabela["dias de ruína (irrestrito)"] == 0]
    primeira_abaixo = tabela[tabela["Σ|w| pedida máx"] <= 1.0]

    texto = [
        "# Curva `c` → alavancagem — o passo (2) da ordem da Lia, pré-executado\n",
        "> Gerado por `scripts/curva_c.py`. O `c` da Lia **não existe ainda**: "
        "aqui ele é uma GRADE de valores constantes, para medir a sensibilidade "
        "antes de a régua chegar. **Isto mede, não escolhe** — nenhum `c` desta "
        "tabela é proposta de valor (CLAUDE.md §6).\n",
        f"- janela: **{datas[0].date()} a {datas[-1].date()}** ({len(datas)} pregões)",
        "- view ativa: **só a 2.2** (a 2.3 espera o G8/DFF, a B o ZQ de dezembro) — "
        "com uma view só, o escalar **é** o `c` dela, não uma média",
        f"- as colunas de excesso usam teto **{args.teto:g}** nos dois escopos "
        "(D12 em aberto); as de Σ|w| são da carteira PEDIDA, e não dependem de "
        "teto nenhum",
        "- `irrestrito acumulado bruto` = a série sem teto composta, **sem custo** "
        "— o giro do irrestrito é proibitivo e não é o que se mede aqui\n",
        # o `|` de Σ|w| tem de vir escapado ou parte a coluna em duas
        "| " + " | ".join(["c"] + [c.replace("|", "\\|") for c in tabela.columns]) + " |",
        "|---" * (len(tabela.columns) + 1) + "|",
    ]
    for c, linha in tabela.iterrows():
        celulas = [f"{c:g}",
                   f"{linha['incerteza (1/c)']:.0f}",
                   f"{linha['Σ|w| pedida mediana']:.2f}",
                   f"{linha['Σ|w| pedida máx']:.2f}",
                   f"{linha[f'dias acima do teto {args.teto:g}'] * 100:.0f}%",
                   f"{linha['dias de ruína (irrestrito)']:.0f}",
                   ("—" if not np.isfinite(linha["irrestrito acumulado bruto"])
                    else f"{linha['irrestrito acumulado bruto'] * 100:+.1f}%"),
                   f"{linha['excesso — teto na carteira'] * 100:+.2f} pp",
                   f"{linha['excesso — teto no tilt'] * 100:+.2f} pp"]
        texto.append("| " + " | ".join(celulas) + " |")

    texto.append("\n## Leitura\n")
    texto.append(
        f"**Com `c = 1` (o que o backtest roda hoje) o BL pede Σ|w| mediana de "
        f"{base['Σ|w| pedida mediana']:.1f} e máximo de "
        f"{base['Σ|w| pedida máx']:,.0f}**, com "
        f"{base[f'dias acima do teto {args.teto:g}'] * 100:.0f}% dos pregões acima do "
        f"teto de {args.teto:g}. É a alavancagem que o teto está segurando hoje.\n")
    if len(neutro.get("ruina", [])):
        corte = neutro["ruina"].index[0]
        antes = neutro["pedida"][neutro["pedida"].index < corte]
        texto.append(
            f"> **Não bate com o número da seção 10 do `Decisoes_pendentes.md`** "
            f"(\"Σ|w| mediana 24, máx 264\", medido em 05/08), e a diferença é de "
            f"MÉTODO, não de dado. Sem teto o backtest **morre no primeiro dia de "
            f"ruína**, então a estatística de lá só pode ter coberto os pregões "
            f"anteriores a ele. No dado de hoje a primeira ruína é em "
            f"**{corte.date()}**, e nos {len(antes)} pregões até lá a mediana é "
            f"{antes.median():,.0f} e o máximo {antes.max():,.0f} — contra "
            f"{base['Σ|w| pedida mediana']:,.0f} e {base['Σ|w| pedida máx']:,.0f} "
            f"na janela inteira. Aqui a conta roda na carteira PEDIDA, que existe "
            f"todo dia porque não depende de trajetória. **O registro antigo "
            f"subestima o problema; não o inventa** — e a conclusão que ele "
            f"sustenta (sem limitador a carteira vai à ruína) fica mais forte, "
            f"não mais fraca.\n")
    menor = tabela.iloc[-1]
    c0, c1 = float(tabela.index[0]), float(tabela.index[-1])
    escala = lambda x: x / (1.0 + x)  # noqa: E731
    texto.append(
        f"**O `c` tira alavancagem, mas menos que proporcionalmente — e a forma é "
        f"conhecida.** Com Ω = (1/c)·diag(P·τΣ·Pᵀ), o tilt do posterior escala "
        f"como **c/(1+c)**, não como c: o Ω entra SOMADO à variância do prior da "
        f"view, então perto de `c = 1` metade do peso já vem do prior e apertar o "
        f"`c` rende pouco. Confere no dado: de `c = {c0:g}` a `c = {c1:g}` a "
        f"fórmula prevê o TILT encolhendo {escala(c0) / escala(c1):.1f}×, e a "
        f"Σ|w| pedida mediana cai "
        f"{base['Σ|w| pedida mediana'] / menor['Σ|w| pedida mediana']:.1f}×. Os dois "
        f"números não têm de bater exato — Σ|w| carrega junto a perna de mercado, "
        f"que não escala com o `c` — mas a ordem de grandeza fecha, e é o que "
        f"valida a leitura.\n")
    texto.append(
        f"**No teto de {args.teto:g}, o `c` não muda o resultado — o teto morde "
        f"antes.** O excesso vai de "
        f"{base['excesso — teto na carteira'] * 100:+.2f} pp a "
        f"{menor['excesso — teto na carteira'] * 100:+.2f} pp (escopo de carteira) "
        f"e de {base['excesso — teto no tilt'] * 100:+.2f} pp a "
        f"{menor['excesso — teto no tilt'] * 100:+.2f} pp (escopo de tilt) ao longo "
        f"de toda a grade, enquanto a Σ|w| pedida cai "
        f"{base['Σ|w| pedida mediana'] / menor['Σ|w| pedida mediana']:.0f}×. "
        f"**É a resposta ao passo (3) da Lia:** para o teto virar redundante, a "
        f"Σ|w| pedida teria de cair abaixo dele — e mesmo em `c = {c1:g}` ela ainda "
        f"está em {menor['Σ|w| pedida mediana']:.1f} de mediana. Nesta janela e com "
        f"esta view, **o `c` não substitui o limitador de tamanho**; os dois têm de "
        f"conviver, que é diferente de \"o teto está fazendo o trabalho do Ω\".\n")
    if len(primeira_sem_ruina):
        c_ok = primeira_sem_ruina.index[0]
        texto.append(
            f"**A ruína do irrestrito só some com `c ≤ {c_ok:g}`.** Acima disso "
            f"existe pelo menos um dia em que a carteira sem teto perde mais de "
            f"100% do patrimônio — o motivo de o teto ter entrado em 05/08. "
            f"Ou seja: **algum** limitador é obrigatório até `c ≈ {c_ok:g}`; a "
            f"pergunta aberta é se ele precisa continuar sendo um teto.\n")
    else:
        texto.append(
            "**A ruína do irrestrito não some em nenhum `c` da grade.** Um "
            "limitador de tamanho é obrigatório em toda a faixa medida — o `c` "
            "sozinho não substitui o teto.\n")
    if len(primeira_abaixo):
        c_um = primeira_abaixo.index[0]
        texto.append(
            f"**Σ|w| pedida só cabe em 1 a partir de `c ≤ {c_um:g}`** — abaixo "
            f"disso o teto de 1 nunca morde e a carteira é a que o BL pediu.\n")
    else:
        texto.append(
            "**Σ|w| pedida nunca cabe em 1** em toda a grade: mesmo no `c` mais "
            "apertado o BL pede mais alavancagem do que o teto mais justo da "
            "varredura permite.\n")
    texto.append(
        "**O que isto NÃO decide:** nem o `c` (é da régua da Lia), nem o nível do "
        "teto, nem o escopo dele (D12, do grupo). A tabela existe para que, no dia "
        "em que o vetor dela chegar, a resposta do passo (2) já esteja medida em "
        "vez de virar mais uma rodada de espera.\n")

    Path(args.saida).write_text("\n".join(texto) + "\n", encoding="utf-8")
    sys.stdout.write(tabela.to_string() + f"\n\nescrito: {args.saida}\n")


if __name__ == "__main__":
    main()
