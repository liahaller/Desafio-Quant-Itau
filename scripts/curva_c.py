"""Curva `c` → alavancagem: quanto o Ω da Lia tira de Σ|w| antes de o teto entrar.

Executa o passo (2) da ordem que a Lia propôs para a D12 — *entra o `c`,
mede-se Σ|w| de novo, só então se decide o teto* (`Decisoes_pendentes.md`,
seção 10). **Varrer e reportar mede, não escolhe** (CLAUDE.md §6).

Duas tabelas, e elas medem coisas diferentes:

  1. **Grade de `c` CONSTANTE** — o mesmo `c` nas quatro views todo dia. Responde
     a pergunta que trava a D12: **ainda sobra alavancagem para um teto cortar?**
     Como é constante, mede o LIMITE da régua, nunca o efeito dela.
  2. **Eixo do NÍVEL, com a série por decisão da Lia** (desde 2026-08-11, quando
     o `lia/c_por_decisao.csv` foi ligado). É a régua real: `c` por view e por
     pregão, com o veto junto. `c = c_nivel1 ** nivel`, então uma série cobre o
     eixo inteiro (D25c). **É esta a tabela que a reunião de 13/08 lê.**

⚠️ A grade constante **não alcança a faixa inteira** que a régua produz: medida
nas 601 decisões da 2.2, com nível 1 ela ocupa [0,36 · 1,0] no eixo de confiança
(mediana 0,953). O trecho abaixo de 0,36 continua medindo sensibilidade — é útil
como física do modelo — mas não é cenário que a régua produza; ver
`Dump/analises/Curva_c_faixa_regua.md`.

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

A lista de views do cabeçalho do artefato é **derivada da rodada**, não escrita
aqui: ela dizia "2.2 e 2.3" e sobreviveu à entrada da 15b e da 15g (D23),
descrevendo uma carteira que já não era a medida. Na grade constante o mesmo `c`
vale para todas — sensibilidade agregada, leitura de ordem de grandeza; no eixo
do nível cada view carrega o seu, que é o ponto da régua.

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
from market_inputs import regua_por_decisao  # noqa: E402


def rodada(retornos, montador, datas, w_mkt, teto, no_tilt, custo_bps, *,
           c=None, regua=None):
    """Um backtest, ou com `c` CONSTANTE em todas as views ou com a régua real.

    O `c ∈ (0,1]` da VARREDURA constante é confiança (maior = mais), que é o
    eixo das curvas; o `omega_fallback` recebe incerteza (maior = menos). Entra
    como 1/c — a conversão vive aqui, num lugar só, porque trocar as duas é a
    armadilha que a régua descreve.

    ⚠️ Não é a convenção em que a régua da Lia ENTREGA: lá `c >= 1` já é
    incerteza e vai direto ao `omega_fallback`, sem passar por aqui. Os dois
    eixos são recíprocos (`c_varredura = 1 / c_regua`). Por isso o `regua`
    passa pelo outro parâmetro do `run_backtest` — os dois são mutuamente
    exclusivos lá, e é o que impede a grade de sobrescrever a régua calada.
    """
    resultado = run_backtest(retornos, montador, w_mkt, datas=datas, tau=TAU,
                             delta=DELTA, custo_bps=custo_bps, teto_alavancagem=teto,
                             teto_no_tilt=no_tilt, regua=regua,
                             incerteza=(None if c is None else 1.0 / c))
    montador.reset()  # as médias expansivas (D9 da 2.2, demeanagem da 2.3) recomeçam
    return resultado, summary(resultado, benchmark=retornos["SPY"])


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raiz", default=".",
                        help="diretório com data/ extraído do branch Paulo")
    parser.add_argument("--cs", type=float, nargs="+",
                        default=[1.0, 0.75, 0.5, 0.25, 0.1, 0.05, 0.02, 0.01],
                        help="grade de confiança c ∈ (0,1] — varredura, não escolha. "
                             "A régua da Lia alcança [0,36 · 1,0] com nível 1: abaixo "
                             "disso a grade mede sensibilidade, não cenário atingível")
    parser.add_argument("--regua", default=None,
                        help="CSV do `c` por decisão da Lia (extraído de origin/Lia); "
                             "o default segue o --raiz. Existindo, sai também a tabela "
                             "do eixo do NÍVEL — a régua real, insumo da escolha de "
                             "13/08. `--regua \"\"` desliga a tabela de propósito")
    parser.add_argument("--niveis", type=float, nargs="+",
                        default=[0, 1, 2, 3, 5, 8],
                        help="grade de NÍVEL da régua (expoente: c = c_nivel1 ** nivel). "
                             "Varredura, não escolha — o nível sai da reunião")
    parser.add_argument("--teto", type=float, default=1.0,
                        help="teto usado só nas colunas de resultado líquido")
    parser.add_argument("--custo-bps", type=float, default=CUSTO_BPS_POR_LADO)
    parser.add_argument("--saida", default="Dump/analises/Curva_c.md")
    args = parser.parse_args()

    # O default segue o `--raiz`: com a régua num caminho relativo fixo, rodar
    # contra a cópia do Paulo (`--raiz /outro`) faria a tabela do NÍVEL sumir
    # CALADA — e ela é o insumo de 13/08. Só o "" explícito desliga.
    if args.regua is None:
        args.regua = str(Path(args.raiz) / "data" / "lia" / "c_por_decisao.csv")

    if any(c <= 0 or c > 1 for c in args.cs):
        raise SystemExit("c é confiança em (0,1] — fora disso o Ω passaria do "
                         "fallback neutro, e a régua da Lia só tira peso")

    retornos, montador, datas, w_mkt = carregar(args.raiz)
    linhas, neutro, vistas = [], {}, set()
    for c in args.cs:
        res, s_carteira = rodada(retornos, montador, datas, w_mkt, args.teto,
                                 False, args.custo_bps, c=c)
        _, s_tilt = rodada(retornos, montador, datas, w_mkt, args.teto,
                           True, args.custo_bps, c=c)
        pedida, r_pedido = res.diario["alavancagem_pedida"], res.diario["r_pedido"]
        vistas |= {d["view"] for dia in res.diagnostics.values() for d in dia["views"]}
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
        "> Gerado por `scripts/curva_c.py`. O `c` aqui é uma GRADE de valores "
        "CONSTANTES no eixo de **confiança** (maior = mais peso). A régua da "
        "Lia entrega no eixo recíproco (`c >= 1`, incerteza) e **por view**: "
        "com nível 1 ela ocupa **[0,36 · 1,0]** deste eixo (mediana 0,953, "
        "medida nas 601 decisões da 2.2). Grade constante é portanto um LIMITE "
        "da régua, não a régua. **Isto mede, não escolhe** — nenhum `c` desta "
        "tabela é proposta de valor (CLAUDE.md §6).\n",
        f"- janela: **{datas[0].date()} a {datas[-1].date()}** ({len(datas)} pregões)",
        # DERIVADA da rodada, nunca escrita à mão: esta linha dizia "2.2 e 2.3"
        # e sobreviveu à entrada da 15b e da 15g, descrevendo uma carteira que
        # não era mais a medida. Registro que envelhece cala; medido não.
        f"- views ativas: **{'** · **'.join(sorted(vistas))}** ({len(vistas)}) — na grade "
        "constante o mesmo `c` entra em todas, então essa tabela é "
        "**sensibilidade agregada**, não o `c` de uma view",
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
                   # 2 casas: na faixa que a régua alcança a incerteza vive
                   # entre 1,0 e 2,8, e arredondar a inteiro colapsa a coluna
                   f"{linha['incerteza (1/c)']:.2f}",
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
    # A amplitude do excesso ao longo da grade é MEDIDA, não afirmada: com uma
    # view só ela era desprezível ("o teto morde antes"); com a 2.3 ligada o
    # escopo de tilt chega a trocar de sinal. Deixar a frase antiga fixa aqui
    # faria o texto contradizer a própria tabela.
    faixa = {escopo: (tabela[f"excesso — teto {escopo}"].min(),
                      tabela[f"excesso — teto {escopo}"].max())
             for escopo in ("na carteira", "no tilt")}
    troca_sinal = [e for e, (lo, hi) in faixa.items() if lo * hi < 0]
    amplitude = max(hi - lo for lo, hi in faixa.values())
    texto.append(
        (f"**No teto de {args.teto:g} o `c` move o resultado em até "
         f"{amplitude * 100:.2f} pp** — e no escopo `{'` e `'.join(troca_sinal)}` "
         f"ele chega a TROCAR o sinal do excesso. Não dá para tratar a régua "
         f"dela como ajuste fino: a escolha do nível é escolha de resultado, que "
         f"é exatamente por que o protocolo anti-overfit da seção 10 pede que o "
         f"nível saia uma vez só, junto do teto, e não por iteração contra esta "
         f"tabela.\n" if troca_sinal else
         f"**No teto de {args.teto:g} o `c` move o excesso em no máximo "
         f"{amplitude * 100:.2f} pp e não troca o sinal em nenhum escopo** — o "
         f"teto morde antes.\n"))
    texto.append(
        f"O excesso vai de "
        f"{base['excesso — teto na carteira'] * 100:+.2f} pp a "
        f"{menor['excesso — teto na carteira'] * 100:+.2f} pp (escopo de carteira) "
        f"e de {base['excesso — teto no tilt'] * 100:+.2f} pp a "
        f"{menor['excesso — teto no tilt'] * 100:+.2f} pp (escopo de tilt) ao longo "
        f"de toda a grade, enquanto a Σ|w| pedida cai "
        f"{base['Σ|w| pedida mediana'] / menor['Σ|w| pedida mediana']:.0f}×. "
        f"**É a resposta ao passo (3) da Lia:** para o teto virar redundante, a "
        f"Σ|w| pedida teria de cair abaixo dele — e mesmo em `c = {c1:g}` ela ainda "
        f"está em {menor['Σ|w| pedida mediana']:.1f} de mediana. Nesta janela e com "
        f"estas views, **o `c` não substitui o limitador de tamanho**; os dois têm de "
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
    # --- eixo do NÍVEL: a régua real, não mais o limite dela -----------------
    # A grade constante acima aplica o MESMO c a todas as views todo dia, o que
    # apaga por construção a diferenciação entre mercado bom e ruim — que é a
    # função da régua (D20b). Com a série por decisão o eixo certo é o NÍVEL, e
    # ele é reescalável fora da régua (`c = c_nivel1 ** nivel`, D25c).
    if args.regua and Path(args.regua).exists():   # `--regua ""` desliga a tabela
        c1 = pd.read_csv(args.regua)
        c1 = c1[c1["selecionado"].astype(bool) & c1["ativa"].astype(bool)]["c_nivel1"]
        linhas_nivel = []
        for nivel in [None] + list(args.niveis):
            reg = None if nivel is None else regua_por_decisao(args.regua, nivel)
            res, s_carteira = rodada(retornos, montador, datas, w_mkt, args.teto,
                                     False, args.custo_bps, regua=reg)
            _, s_tilt = rodada(retornos, montador, datas, w_mkt, args.teto,
                               True, args.custo_bps, regua=reg)
            pedida, r_pedido = res.diario["alavancagem_pedida"], res.diario["r_pedido"]
            linhas_nivel.append({
                "nível": "sem régua" if nivel is None else f"{nivel:g}",
                "c mediano (ativas)": (float("nan") if nivel is None
                                       else float((c1 ** nivel).median())),
                "c p95": (float("nan") if nivel is None
                          else float((c1 ** nivel).quantile(0.95))),
                "views/dia": float(res.diario["n_views"].mean()),
                "Σ|w| pedida mediana": float(pedida.median()),
                "dias de ruína": float((r_pedido <= -1.0).sum()),
                "excesso — teto na carteira": s_carteira["excesso acumulado (líquido − benchmark)"],
                "excesso — teto no tilt": s_tilt["excesso acumulado (líquido − benchmark)"],
            })
        nt = pd.DataFrame(linhas_nivel).set_index("nível")

        texto.append("\n## O eixo do NÍVEL — a régua REAL, não o limite dela\n")
        texto.append(
            "> A tabela acima é grade **constante**: o mesmo `c` nas quatro views "
            "todo dia. Isso mede o LIMITE da régua e nunca o efeito dela, que é de "
            "**cauda** — grade constante apaga por construção a diferenciação entre "
            "mercado bom e ruim, que é a função da régua. Abaixo entra a série **por "
            "decisão** da Lia (`lia/c_por_decisao.csv`), e o eixo passa a ser o "
            "**nível** (D20b). Como `c = c_nivel1 ** nivel`, uma série cobre o eixo "
            "inteiro (D25c) e **`nível = 0` é He-Litterman puro com o veto ligado** — "
            "é a linha que separa os dois canais da régua, o veto e a dosagem.\n")
        texto.append("| " + " | ".join(["nível"] + [c.replace("|", "\\|")
                                                    for c in nt.columns]) + " |")
        texto.append("|---" * (len(nt.columns) + 1) + "|")
        for nivel, linha in nt.iterrows():
            texto.append("| " + " | ".join([
                nivel,
                "—" if not np.isfinite(linha["c mediano (ativas)"]) else f"{linha['c mediano (ativas)']:.4f}",
                "—" if not np.isfinite(linha["c p95"]) else f"{linha['c p95']:.4f}",
                f"{linha['views/dia']:.2f}",
                f"{linha['Σ|w| pedida mediana']:.1f}",
                f"{linha['dias de ruína']:.0f}",
                f"{linha['excesso — teto na carteira'] * 100:+.2f} pp",
                f"{linha['excesso — teto no tilt'] * 100:+.2f} pp"]) + " |")

        sem, zero = nt.loc["sem régua"], nt.loc["0"] if "0" in nt.index else None
        texto.append(
            f"\n**O veto sozinho já move o número.** Sem régua o BL vê "
            f"{sem['views/dia']:.2f} views por dia" +
            (f"; com `nível = 0` — que não dosa nada, só aplica o `ativa = False` — "
             f"caem para {zero['views/dia']:.2f}, e a Σ|w| pedida mediana vai de "
             f"{sem['Σ|w| pedida mediana']:.1f} para {zero['Σ|w| pedida mediana']:.1f}. "
             f"**Separar isso importa para 13/08:** parte do efeito da régua não "
             f"depende do nível escolhido, porque o veto não tem nível.\n"
             if zero is not None else ".\n"))
        faixa_nt = nt["excesso — teto no tilt"]
        texto.append(
            f"**Ao longo do eixo do nível o excesso anda "
            f"{(faixa_nt.max() - faixa_nt.min()) * 100:.2f} pp** "
            f"(de {faixa_nt.min() * 100:+.2f} a {faixa_nt.max() * 100:+.2f} pp, escopo "
            f"de tilt), e a Σ|w| pedida mediana cai "
            f"{nt['Σ|w| pedida mediana'].max() / nt['Σ|w| pedida mediana'].min():.1f}× "
            f"da ponta frouxa à apertada. **Nenhum destes níveis é proposta** — a "
            f"escolha sai da reunião de 13/08, uma vez só, junto do teto (seção 10). "
            f"Esta tabela existe para que ela seja feita sobre um EIXO e não sobre um "
            f"ponto.\n")

    texto.append(
        "**O que isto NÃO decide:** nem o nível da régua (é escolha da reunião de "
        "13/08, no eixo da tabela acima), nem o nível do teto, nem o escopo dele "
        "(D12, do grupo). As duas tabelas medem; a escolha sai uma vez só, e não "
        "por iteração contra elas.\n")

    Path(args.saida).write_text("\n".join(texto) + "\n", encoding="utf-8")
    sys.stdout.write(tabela.to_string() + f"\n\nescrito: {args.saida}\n")


if __name__ == "__main__":
    main()
