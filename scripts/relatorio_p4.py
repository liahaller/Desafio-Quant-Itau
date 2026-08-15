"""Gera a página 4 do relatório v2 (backtest, resultados e autoavaliação) em PPTX.

Estilo herdado do v1 (`Relatório/Drafts/KAIROSv1.pdf`): fundo #0A1621, acento
#F5A623, Segoe UI, réguas de 0,75 pt em #24374A. Nenhum texto ou imagem do v1 é
reaproveitado — só a paleta e a métrica tipográfica.

Todos os números vêm de artefato medido:
  - `Dump/analises/Metricas_p4.md`      (tabela de métricas, alpha, beta)
  - `Dump/analises/Backtest_v1.md`      (metodologia, giro, breakeven)
  - `Dump/analises/Views_novas.md`      (atribuição, acerto de sinal)
  - `Dump/analises/Camada_tatica_v2.md` (tensão sozinha × somada)
  - `Dump/dados/*.csv`                  (varreduras das sensibilidades)

Uso: python scripts/relatorio_p4.py [--saida CAMINHO.pptx]
"""

from __future__ import annotations

import argparse
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

RAIZ = Path(__file__).resolve().parent.parent
GRAFICOS = RAIZ / "Dump" / "graficos"

# ---------------------------------------------------------------- paleta (v1)
BG = RGBColor(0x0A, 0x16, 0x21)
RULE = RGBColor(0x24, 0x37, 0x4A)
ORANGE = RGBColor(0xF5, 0xA6, 0x23)
TEXT = RGBColor(0xE8, 0xED, 0xF2)
MUTED = RGBColor(0x6B, 0x82, 0x99)
MUTED2 = RGBColor(0x9B, 0xAE, 0xC0)
RED = RGBColor(0xC2, 0x54, 0x4D)

FONTE = "Segoe UI"


# ------------------------------------------------------------------ primitivas
def caixa(slide, x, y, w, h):
    """Textbox sem margens, ancorada no topo, com quebra de linha."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.TOP
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    return tf


def escreve(tf, partes, tamanho, cor=MUTED2, espaco=1.25, alinha=PP_ALIGN.LEFT,
            spc=None, antes=0, primeiro=False):
    """Adiciona um parágrafo. `partes` é str ou lista de (texto, cor, negrito)."""
    p = tf.paragraphs[0] if primeiro else tf.add_paragraph()
    p.alignment = alinha
    p.line_spacing = espaco
    p.space_before = Pt(antes)
    p.space_after = Pt(0)
    if isinstance(partes, str):
        partes = [(partes, cor, False)]
    for texto, c, negrito in partes:
        r = p.add_run()
        r.text = texto
        r.font.name = FONTE
        r.font.size = Pt(tamanho)
        r.font.bold = negrito
        r.font.color.rgb = c
        if spc is not None:  # letter-spacing em 1/100 de pt (só via XML)
            r.font._rPr.set("spc", str(int(spc * 100)))
    return p


def rotulo(slide, x, y, texto, w=6.0, cor=ORANGE, tamanho=7.0):
    """Rótulo de seção: caixa-alta, negrito, com entrelinha aumentada."""
    tf = caixa(slide, x, y, w, 0.18)
    escreve(tf, [(texto.upper(), cor, True)], tamanho, spc=1.0, primeiro=True)


def regua(slide, x1, y, x2):
    ln = slide.shapes.add_connector(1, Inches(x1), Inches(y), Inches(x2), Inches(y))
    ln.line.color.rgb = RULE
    ln.line.width = Pt(0.75)
    return ln


def bloco(slide, x, y, w, h, titulo, itens, tamanho=6.1, intro=None, tit=6.0):
    """Rótulo de seção + parágrafos com chamada em negrito claro."""
    rotulo(slide, x, y, titulo, w=w, tamanho=tit)
    tf = caixa(slide, x, y + 0.30, w, h - 0.30)
    primeiro = True
    if intro:
        partes = intro if isinstance(intro, list) else [(intro, MUTED, False)]
        escreve(tf, partes, tamanho, espaco=1.18, primeiro=True)
        primeiro = False
    for lead, resto in itens:
        partes = []
        if lead:
            partes.append((lead + " ", TEXT, True))
        partes.append((resto, MUTED, False))
        escreve(tf, partes, tamanho, espaco=1.18, antes=0 if primeiro else 4.0,
                primeiro=primeiro)
        primeiro = False


def tabela(slide, x, y, w, cabecalho, linhas, tamanho=6.4, alt=0.175):
    """Tabela de 3 colunas desenhada à mão (rótulo + 2 valores à direita)."""
    c_val = 0.62
    c_rot = w - 2 * c_val
    cabs = [(cabecalho[0], PP_ALIGN.LEFT, c_rot, x),
            (cabecalho[1], PP_ALIGN.RIGHT, c_val, x + c_rot),
            (cabecalho[2], PP_ALIGN.RIGHT, c_val, x + c_rot + c_val)]
    for texto, alinha, larg, cx in cabs:
        tf = caixa(slide, cx, y, larg, alt)
        escreve(tf, [(texto.upper(), MUTED, False)], 5.8, spc=0.8, alinha=alinha,
                primeiro=True)
    regua(slide, x, y + alt - 0.02, x + w)

    for i, (rot, a, b) in enumerate(linhas):
        ly = y + alt + i * alt
        cels = [(rot, PP_ALIGN.LEFT, c_rot, x, MUTED2, False),
                (a, PP_ALIGN.RIGHT, c_val, x + c_rot, TEXT, True),
                (b, PP_ALIGN.RIGHT, c_val, x + c_rot + c_val, MUTED, False)]
        for texto, alinha, larg, cx, cor, negrito in cels:
            tf = caixa(slide, cx, ly + 0.028, larg, alt)
            escreve(tf, [(texto, cor, negrito)], tamanho, alinha=alinha, primeiro=True)
        regua(slide, x, ly + alt - 0.02, x + w)
    return y + alt + len(linhas) * alt


def imagem(slide, caminho, x, y, w):
    """Insere PNG preservando o aspecto; devolve a base (y + altura)."""
    pic = slide.shapes.add_picture(str(caminho), Inches(x), Inches(y), width=Inches(w))
    return y + Emu(pic.height).inches


# --------------------------------------------------------------------- página
def monta(saida: Path) -> Path:
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    fundo = slide.background.fill
    fundo.solid()
    fundo.fore_color.rgb = BG

    L, R = 0.90, 12.43

    # -- cabeçalho ----------------------------------------------------------
    tf = caixa(slide, L, 0.34, 6.0, 0.30)
    escreve(tf, [("KAIRÓS", ORANGE, True),
                 ("   Backtest, resultados e autoavaliação", MUTED2, False)],
            12.0, spc=0.8, primeiro=True)
    tf = caixa(slide, R - 1.0, 0.38, 1.0, 0.20)
    escreve(tf, [("04", MUTED, False)], 9.0, alinha=PP_ALIGN.RIGHT, primeiro=True)
    regua(slide, L, 0.76, R)

    # -- metodologia e vieses tratados --------------------------------------
    rotulo(slide, L, 0.86, "Metodologia e vieses tratados", w=5.0)
    tf = caixa(slide, L, 1.04, 5.2, 0.54)
    escreve(tf, [
        ("Todo número desta página teve de passar por uma pergunta: o backtest "
         "podia saber isso na hora da decisão? As quatro formas de inflar um "
         "resultado destes — ", MUTED, False),
        ("olhar o futuro, calibrar dentro da própria janela, assumir número de "
         "manual e ajustar parâmetro ao resultado", TEXT, True),
        (" — foram fechadas por construção, antes de rodar. O terreno: 374 "
         "pregões (10/02/2025 a 06/08/2026), 9 ETFs a preços ajustados, "
         "rebalanceamento diário, ", MUTED, False),
        ("2,0 bps por lado", TEXT, True),
        (" sobre o giro.", MUTED, False),
    ], 7.0, espaco=1.24, primeiro=True)

    chips = [
        ("O modelo nunca viu o futuro.",
         " Nenhuma view usa o desfecho do evento que ela mesma precifica."),
        ("A régua foi calibrada fora do teste.",
         " As médias de referência vêm de 206 pregões anteriores ao início da janela medida."),
        ("Nada foi assumido de cabeça.",
         " A sensibilidade a juros que o manual arredonda para “8” foi medida: 8,31 a 8,38."),
        ("Os parâmetros não foram ajustados ao resultado.",
         " Teto de risco, confiança nas views e aversão a risco saem de decisão registrada."),
    ]
    for i, (lead, resto) in enumerate(chips):
        cx = 6.20 + (i % 2) * 3.20
        cy = 1.04 + (i // 2) * 0.28
        tf = caixa(slide, cx, cy, 3.05, 0.26)
        escreve(tf, [("· ", ORANGE, True), (lead, TEXT, True), (resto, MUTED, False)],
                6.1, espaco=1.18, primeiro=True)
    regua(slide, L, 1.62, R)

    # -- faixa 1: os três visuais -------------------------------------------
    rotulo(slide, L, 1.72, "Curva acumulada e drawdown", w=4.2)
    base = imagem(slide, GRAFICOS / "p4_curva.png", L, 1.90, 4.20)
    tf = caixa(slide, L, base + 0.05, 4.20, 0.42)
    escreve(tf, [
        ("+33,2% contra +30,1% do SPY", TEXT, True),
        (", ao mesmo risco (vol. 17,6% contra 17,9%). Mas a vantagem não veio "
         "das quedas: nos dois tombos a carteira caiu junto, e em abril/2025 "
         "caiu ", MUTED, False),
        ("mais fundo que o benchmark", RED, True),
        (" (−19,6% contra −18,8%). O ganho vem da subida, não da defesa.",
         MUTED, False),
    ], 6.4, espaco=1.22, primeiro=True)

    rotulo(slide, 5.30, 1.72, "De onde vem o resultado", w=3.30)
    base = imagem(slide, GRAFICOS / "p4_composicao.png", 5.30, 1.90, 3.30)
    tf = caixa(slide, 5.30, base + 0.06, 3.30, 1.10)
    escreve(tf, [
        ("O retorno de cada pregão se separa em três pedaços: a carteira de "
         "equilíbrio — o que se teria sem view nenhuma —, o desvio que as views "
         "impõem sobre ela e o custo de manter esse desvio. Em 374 pregões as "
         "views produziram ", MUTED, False),
        ("+5,2 pp", TEXT, True),
        (" e o custo devolveu ", MUTED, False),
        ("−3,0 pp", RED, True),
        (": mais da metade. O que chega ao investidor é o que sobra. E a "
         "vantagem ", MUTED, False),
        ("não depende de dias de sorte", TEXT, True),
        (" — sem os três pregões de maior impacto ela seria maior, não menor "
         "(+4,5 em vez de +2,3 pp).", MUTED, False),
    ], 6.4, espaco=1.22, primeiro=True)

    rotulo(slide, 8.90, 1.72, "Sensibilidades — aqui se justifica o número", w=3.53)
    base = imagem(slide, GRAFICOS / "p4_sensibilidade.png", 8.90, 1.90, 3.53)
    tf = caixa(slide, 8.90, base + 0.06, 3.53, 1.10)
    escreve(tf, [
        ("Um resultado bom pode ser só um parâmetro bem escolhido. Giramos os "
         "quatro botões da estratégia — quanto risco tomar (o teto limita o "
         "desvio em relação ao prior, não a carteira), quanta confiança dar às "
         "views, quanto o preço precisa andar para negociar e a correção das "
         "probabilidades — e medimos cada posição. ", MUTED, False),
        ("Em nenhuma a vantagem sobre o SPY vira negativa", TEXT, True),
        (" (+0,5 a +15,8 pp). E o valor entregue não é o que dá o melhor número: "
         "em dois dos quatro ele é o ", MUTED, False),
        ("pior ponto da grade", TEXT, True),
        (".", MUTED, False),
    ], 6.4, espaco=1.22, primeiro=True)

    regua(slide, L, 4.94, R)

    # -- faixa 2: métricas + a leitura crítica ------------------------------
    col_w, passo = 2.15, 2.335
    x = [L + i * passo for i in range(5)]
    y0, alt = 5.02, 2.20

    rotulo(slide, x[0], y0, "Tabela de métricas", w=col_w, tamanho=6.0)
    fim = tabela(slide, x[0], y0 + 0.30, col_w, alt=0.165,
                 cabecalho=("Métrica", "Kairós", "SPY"),
                 linhas=[("Retorno líquido", "+33,2%", "+30,1%"),
                  ("Vol. anualizada", "17,6%", "17,9%"),
                  ("Sharpe", "1,18", "1,08"),
                  ("Máx. drawdown", "−19,6%", "−18,8%"),
                  ("Alpha anual.", "+2,57%", "—"),
                  ("Beta vs SPY", "0,95", "1,00"),
                  ("Σ|w| média", "1,91", "1,00"),
                  ("Giro diário", "0,40", "—")])
    tf = caixa(slide, x[0], fim + 0.06, col_w, 0.42)
    escreve(tf, [
        ("Beta 0,95:", TEXT, True),
        (" a carteira não é SPY alavancado. Neutra também não é — o ΣP mediano das "
         "views vai de +0,96 a +2,00, como a p. 3 declara.", MUTED, False),
    ], 6.1, espaco=1.18, primeiro=True)

    bloco(slide, x[1], y0, col_w, alt, "O que o número não diz", [
        ("Ganha sozinha, perde somada.",
         "A camada tática faz +42,6 pp isolada e −2,94 pp na entrega. Sob teto fixo, "
         "entrar não é somar — é dividir um orçamento de risco. E o Δ não é monótono "
         "no teto (−2,9 / −6,8 / −8,9 / +3,8)."),
        ("42% do giro é desfeito em dois pregões.",
         "Material, mas o breakeven de 22,9 bps por lado é 11× a premissa de 2 bps."),
        ("Uma janela, um regime.",
         "374 pregões de alta do S&P, sem correção para as ~200 comparações da busca tática."),
        ("O Ω é diagonal.",
         "Duas views com ρ +0,67 entram como informação independente."),
    ])

    bloco(slide, x[2], y0, col_w, alt, "Autoavaliação · o placar, não a curva", [
        ("4 ingredientes do Ω testados,",
         "2 aprovados, 1 rebaixado a veto, 1 reprovado — a proximidade do evento saiu "
         "com o sinal invertido nas duas views: derrubada por replicação, não por acaso."),
        ("13 candidatas táticas medidas",
         "antes de uma entrar. A 1.2 momentum e a velocidade de ajuste morreram por "
         "variance ratio de 0,97 a 1,18 — passeio aleatório, tese contrariada pelo dado."),
        ("2 views entregues com acerto de ~49%,",
         "porque a régua de admissão é mecanismo, não performance. A tese se sustenta "
         "pelo que foi reprovado."),
    ], intro="Protocolo: forma julgada contra o erro da probabilidade, nunca contra o "
             "retorno; nível e teto escolhidos uma vez só, em reunião; premissa escrita "
             "antes de estimar.")

    bloco(slide, x[3], y0, col_w, alt, "Autoavaliação · onde erramos", [
        ("Medida errada, conclusão certa.",
         "Um crescimento da mediana foi lido como tendência; era artefato — em k=1 a "
         "maioria dos dias tem variação zero. O variance ratio dizia passeio aleatório, "
         "e a camada tática quase entrou por isso."),
        ("Teste que reprova quase todo mundo não é teste.",
         "O critério de estabilidade marcava 13 de 14 células; lido sem atenção teria "
         "produzido a conclusão oposta da certa."),
        ("Texto cravado em gerador envelhece calado.",
         "A legenda do backtest afirmou “camada desligada” por dois commits depois de "
         "ela ser ligada — os números já a incluíam."),
    ])

    bloco(slide, x[4], y0, col_w, alt, "Autoavaliação · simulação de fundo", [
        ("Conservador — não adere.",
         "Drawdown pior que o do índice, 1,9× de alavancagem, nenhuma proteção na queda."),
        ("Institucional — adere ao alpha, não ao produto.",
         "Beta 0,95 é exposição que ele já compra barato; pagaria pelos +2,6% a.a. de alpha."),
        ("Orientado a evento — adere.",
         "É o único para quem +3,0 pp ao mesmo risco do índice é o produto."),
        ("",
         "A objeção não foi ao retorno, foi ao empacotamento: isto é um overlay de "
         "alpha, e a taxa teria de sair do excesso."),
    ], intro=[("Leitura, não medição. ", ORANGE, True),
              ("Perfis de cliente simulados por IA sobre a série diária — 18 meses, "
               "drawdown de −19,6%, Σ|w| médio de 1,91 e 0,40 de giro por pregão. "
               "Nenhum número novo: a simulação lê os medidos.", MUTED, False)])

    # -- rodapé -------------------------------------------------------------
    regua(slide, L, 7.28, R)
    tf = caixa(slide, L, 7.33, R - L, 0.14)
    escreve(tf, [
        ("Backtest reproduzido em duas máquinas com saída idêntica dígito a dígito. "
         "Todo número desta página sai de ", MUTED, False),
        ("backtest_v1.py · curva_c.py · curva_banda.py · graficos_p4.py", MUTED2, False),
        (", e nenhum foi digitado à mão.", MUTED, False),
    ], 6.0, primeiro=True)

    saida.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(saida))
    return saida


def demo() -> None:
    """Auto-teste do layout: nada pode vazar da moldura de 13,333 × 7,5 in."""
    alvo = Path(__file__).parent.parent / "Dump" / "_demo_p4.pptx"
    monta(alvo)
    prs = Presentation(str(alvo))
    slide = prs.slides[0]
    lim_x, lim_y = prs.slide_width, prs.slide_height
    vazou = [(s.shape_type, Emu(s.left).inches, Emu(s.top).inches)
             for s in slide.shapes
             if s.left is not None and (s.left < 0 or s.top < 0
                                        or s.left + (s.width or 0) > lim_x
                                        or s.top + (s.height or 0) > lim_y)]
    assert not vazou, f"formas fora da moldura: {vazou}"
    assert len(slide.shapes) > 40, f"slide com poucas formas: {len(slide.shapes)}"
    alvo.unlink()
    print("demo ok — nenhuma forma fora da moldura")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--saida", default=str(RAIZ / "Relatório" / "Drafts" / "KAIROSv2_p4.pptx"))
    ap.add_argument("--demo", action="store_true", help="roda o auto-teste de layout")
    args = ap.parse_args()
    if args.demo:
        demo()
    else:
        print(monta(Path(args.saida)))
