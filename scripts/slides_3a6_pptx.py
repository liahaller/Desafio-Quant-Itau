"""Slides 3 a 7 da semifinal — o diagrama que anda entre os slides.

Gera `Semis/Slides_3a6.pptx`. Os slides 3 a 6 desenham o MESMO diagrama;
o que muda de um para o outro e onde cada no esta, de que tamanho e de que cor.
A transicao Morph do PowerPoint interpola essa diferenca, entao o diagrama
parece se mover em vez de piscar.

Como o Morph sabe o que casa com o que: toda forma persistente e nomeada com o
prefixo `!!` (ex.: `!!q`). Esse prefixo e o modo "morph por nome" — mesmo nome
nos dois slides = mesmo objeto, ainda que mude posicao, tamanho, cor e texto.
Tudo que NAO e persistente recebe um nome unico do slide (`sela()`), para o
PowerPoint nao casar por acidente duas caixas de texto que nao tem relacao.

Requer PowerPoint 2016+/365. Em Google Slides e LibreOffice a transicao cai no
`<mc:Fallback>` declarado no XML e vira um fade — o deck continua correto, so
perde o movimento.

ESTILO: herda do relatorio final (`Quartas/KAIROS FINAL.pdf`) a paleta, a Segoe
UI, os rotulos de secao em caixa-alta laranja e as reguas de 0,75 pt no lugar de
molduras. O que NAO e herdado, porque relatorio se le de perto e slide se
projeta:

  · corpo em 11,5 pt (o relatorio roda em 6-7 pt) e texto de continuacao num
    cinza mais claro — o #6B8299 do papel some no projetor;
  · profundidade: fundo em gradiente diagonal, nos de canto arredondado com
    gradiente e sombra, e um halo laranja de borda suave ATRAS do no que o
    slide explica — o halo tambem e persistente, entao a luz viaja junto com o
    diagrama de um slide para o outro;
  · cor com papel: azul = o que vem do mercado (equilibrio), laranja = o que vem
    do Polymarket (Q e Omega), verde-agua = o resultado (a carteira). O no aceso
    ganha borda e brilho na PROPRIA cor, em vez de todo mundo virar laranja;
  · a carteira e alimentada por uma CHAVE que abraca os tres nos e desagua
    nela, no lugar do colchete reto de antes — e a notacao do quadro-negro, e
    em movimento ela encolhe junto com a linha.
"""

import math
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml import parse_xml
from pptx.oxml.ns import nsdecls
from pptx.util import Emu, Inches, Pt

import grafo_repo
from grafo_repo import SAIDA as GRAFO
from relatorio_p4 import (MUTED, MUTED2, ORANGE, RULE, TEXT, caixa, escreve,
                          imagem, regua, rotulo)

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "Semis" / "Slides_3a6.pptx"

# ------------------------------------------------------------------- paleta
BG0 = RGBColor(0x06, 0x10, 0x1A)      # canto escuro do fundo
BG1 = RGBColor(0x12, 0x23, 0x33)      # canto claro do fundo
PANEL_A = RGBColor(0x1B, 0x2D, 0x40)  # topo do no em repouso
PANEL_B = RGBColor(0x0C, 0x18, 0x24)  # base do no em repouso
ON_A = RGBColor(0x27, 0x42, 0x5C)     # topo do no aceso
ON_B = RGBColor(0x10, 0x1E, 0x2E)     # base do no aceso
OFF_A = RGBColor(0x14, 0x22, 0x31)    # topo do no apagado (slide 6)
OFF_B = RGBColor(0x0A, 0x15, 0x20)
EDGE = RGBColor(0x23, 0x38, 0x4C)     # fio de contorno
EDGE_OFF = RGBColor(0x18, 0x28, 0x38)
BODY = RGBColor(0x93, 0xA9, 0xBC)     # corpo de texto, metrica de projecao
BLUE = RGBColor(0x4E, 0x8F, 0xD1)     # o que vem do mercado
MINT = RGBColor(0x4F, 0xC3, 0xA1)     # o resultado

ACENTO = {"eq": BLUE, "q": ORANGE, "om": ORANGE, "cart": MINT}

L, R = 0.90, 12.43         # margens do relatorio
BANDA = 4.30               # regua que separa o diagrama da secao de baixo
DET = 4.42                 # rotulo da secao de baixo
CORPO = 4.76               # onde comeca o texto da secao de baixo
PE = 6.88                  # regua do rodape

CORPO_PT = 11.5            # metrica de corpo, escalada para projecao
ROT_PT = 9.5               # rotulo de secao

A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
SOMBRA = ('<a:outerShdw blurRad="170000" dist="44000" dir="5400000"'
          ' rotWithShape="0"><a:srgbClr val="000000"><a:alpha val="42000"/>'
          '</a:srgbClr></a:outerShdw>')


# ------------------------------------------------------------------ efeitos
def efeito(sh, xml):
    """Escreve o `effectLst` da forma.

    Substitui em vez de anexar: `shadow.inherit = False` ja deixa um
    `<a:effectLst/>` vazio no spPr, e dois deles corrompem o arquivo.
    """
    sh.shadow.inherit = False
    sp = sh._element.spPr
    velho = sp.find(A + "effectLst")
    if velho is not None:
        sp.remove(velho)
    sp.append(parse_xml(f'<a:effectLst {nsdecls("a")}>{xml}</a:effectLst>'))


def brilho(cor, rad=130000, alfa=32000):
    """Halo colado na borda da forma — o que faz o no 'acender'."""
    return (f'<a:glow rad="{rad}"><a:srgbClr val="{cor}">'
            f'<a:alpha val="{alfa}"/></a:srgbClr></a:glow>')


def mistura(a, b, t):
    """Interpola duas cores — t=0 devolve `a`, t=1 devolve `b`."""
    return RGBColor(*[round(ca + (cb - ca) * t) for ca, cb in zip(a, b)])


# ---------------------------------------------------------------- primitivas
def painel(slide, x, y, w, h, topo=PANEL_A, base=PANEL_B, borda=EDGE,
           raio=0.11, luz=""):
    """O corpo de um no: canto arredondado, gradiente vertical e sombra."""
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x),
                                Inches(y), Inches(w), Inches(h))
    sh.adjustments[0] = raio
    f = sh.fill
    f.gradient()
    f.gradient_angle = 270.0
    f.gradient_stops[0].color.rgb = topo
    f.gradient_stops[1].color.rgb = base
    if borda is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = borda
        sh.line.width = Pt(1.0)
    efeito(sh, SOMBRA + luz)
    return sh


def pino(slide, x, y, h, cor, esp=0.055):
    """A barra de acento do relatorio, aqui como pilula arredondada."""
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x),
                                Inches(y), Inches(esp), Inches(h))
    sh.adjustments[0] = 0.5
    sh.fill.solid()
    sh.fill.fore_color.rgb = cor
    sh.line.fill.background()
    sh.shadow.inherit = False
    return sh


def halo(slide, x, y, w, h, cor=ORANGE, alfa=15000, raio=1300000):
    """Mancha de luz de borda suave — a atmosfera atras do no em foco."""
    sh = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y),
                                Inches(w), Inches(h))
    sh.fill.solid()
    sh.fill.fore_color.rgb = cor
    sh.fill.fore_color._xFill.find(A + "srgbClr").append(
        parse_xml(f'<a:alpha {nsdecls("a")} val="{alfa}"/>'))
    sh.line.fill.background()
    efeito(sh, f'<a:softEdge rad="{raio}"/>')
    return sh


def _ponta(ln):
    ln.line._get_or_add_ln().append(parse_xml(
        f'<a:tailEnd {nsdecls("a")} type="triangle" w="med" len="med"/>'))
    return ln


def curva(slide, x1, y1, x2, y2, cor=MUTED, esp=1.25, ponta=True):
    """Conector curvo — o lugar do colchete reto de antes."""
    ln = slide.shapes.add_connector(MSO_CONNECTOR.CURVE, Inches(x1), Inches(y1),
                                    Inches(x2), Inches(y2))
    ln.line.color.rgb = cor
    ln.line.width = Pt(esp)
    return _ponta(ln) if ponta else ln


def chave(slide, x, y, w, h, cor=MUTED, esp=1.25, volta=0.30):
    """Uma chave deitada, abrindo para baixo, de x ate x+w.

    O PowerPoint so tem a chave em pe, entao ela nasce com os lados trocados e
    gira 90 graus — e a rotacao acontece em torno do CENTRO, por isso a caixa e
    posicionada pelo centro e nao pelo canto.
    """
    cx, cy = x + w / 2, y + h / 2
    sh = slide.shapes.add_shape(MSO_SHAPE.RIGHT_BRACE, Inches(cx - h / 2),
                                Inches(cy - w / 2), Inches(h), Inches(w))
    sh.rotation = 90.0
    sh.adjustments[0] = volta          # raio das voltas
    sh.adjustments[1] = 0.5            # a ponta no meio
    sh.fill.background()
    sh.line.color.rgb = cor
    sh.line.width = Pt(esp)
    sh.shadow.inherit = False
    return sh


def flecha(slide, x1, y1, x2, y2, cor=MUTED, esp=1.25):
    ln = slide.shapes.add_connector(1, Inches(x1), Inches(y1), Inches(x2),
                                    Inches(y2))
    ln.line.color.rgb = cor
    ln.line.width = Pt(esp)
    return _ponta(ln)


def bloco(slide, x, y, w, titulo, itens, tam=CORPO_PT):
    """Rotulo de secao + itens com chamada em negrito claro.

    E o `bloco` do relatorio com a entrelinha e a cor de corpo da projecao; o do
    relatorio fica onde esta, porque a pagina impressa continua usando a dele.
    """
    rotulo(slide, x, y, titulo, w=w, tamanho=ROT_PT)
    tf = caixa(slide, x, y + 0.34, w, 2.0)
    for i, (lead, resto) in enumerate(itens):
        escreve(tf, [(lead + " ", TEXT, True), (resto, BODY, False)], tam,
                espaco=1.26, antes=0 if i == 0 else 8.0, primeiro=i == 0)


def chamada(slide, x, y, w, h, itens, tam=CORPO_PT, cor=ORANGE):
    """Pilula de acento a esquerda + chamada em negrito claro."""
    pino(slide, x, y + 0.04, h - 0.08, cor, esp=0.05)
    tf = caixa(slide, x + 0.24, y, w - 0.24, h)
    for i, (lead, resto) in enumerate(itens):
        escreve(tf, [(lead + " ", TEXT, True), (resto, BODY, False)], tam,
                espaco=1.30, antes=0 if i == 0 else 9.0, primeiro=i == 0)


def tabela(slide, x, y, w, cabecalho, linhas, tam=10.5, alt=0.34):
    """Tabela de 3 colunas em metrica de projecao (a do relatorio e de 5,8 pt)."""
    c_val = 0.95
    c_rot = w - 2 * c_val
    for texto, alinha, larg, cx in (
            (cabecalho[0], PP_ALIGN.LEFT, c_rot, x),
            (cabecalho[1], PP_ALIGN.RIGHT, c_val, x + c_rot),
            (cabecalho[2], PP_ALIGN.RIGHT, c_val, x + c_rot + c_val)):
        tf = caixa(slide, cx, y, larg, 0.20)
        escreve(tf, [(texto.upper(), MUTED, False)], 8.0, spc=1.0,
                alinha=alinha, primeiro=True)
    regua(slide, x, y + alt - 0.06, x + w)

    for i, (rot, a, b) in enumerate(linhas):
        ly = y + alt + i * alt
        for texto, alinha, larg, cx, cor, negrito in (
                (rot, PP_ALIGN.LEFT, c_rot, x, MUTED2, False),
                (a, PP_ALIGN.RIGHT, c_val, x + c_rot, TEXT, True),
                (b, PP_ALIGN.RIGHT, c_val, x + c_rot + c_val, MUTED, False)):
            tf = caixa(slide, cx, ly + 0.05, larg, alt)
            escreve(tf, [(texto, cor, negrito)], tam, alinha=alinha,
                    primeiro=True)
        regua(slide, x, ly + alt - 0.06, x + w)
    return y + alt + len(linhas) * alt


# -------------------------------------------------------------------- morph
def morph(slide, dur_ms=900):
    """Liga a transicao Morph NESTE slide (ela roda ao ENTRAR nele).

    O python-pptx nao tem API de transicao (issue #942, sem previsao), mas
    preserva XML que nao entende — entao o elemento vai injetado direto no
    `<p:sld>`, depois do `<p:clrMapOvr>`, que e onde o schema o espera.
    """
    slide.element.append(parse_xml(
        '<mc:AlternateContent'
        ' xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"'
        ' xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
        '<mc:Choice Requires="p14"'
        ' xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main">'
        f'<p:transition spd="slow" p14:dur="{dur_ms}">'
        '<p159:morph option="byObject"'
        ' xmlns:p159="http://schemas.microsoft.com/office/powerpoint/2015/09/main"/>'
        '</p:transition></mc:Choice>'
        '<mc:Fallback><p:transition spd="slow"><p:fade/></p:transition>'
        '</mc:Fallback></mc:AlternateContent>'))


def sela(slide, numero):
    """Da nome unico do slide a tudo que nao e persistente.

    Sem isto o PowerPoint casaria formas pela heuristica de id/geometria e faria
    um item da secao de baixo do slide 3 "virar" outro item no slide 4.
    """
    for i, sh in enumerate(slide.shapes):
        if not sh.name.startswith("!!"):
            sh.name = f"s{numero}_{i}"


def moldura(prs, numero, titulo, banda=True):
    """Fundo, cabecalho, reguas e rodape — a moldura comum a todos os slides.

    `banda=False` tira a regua horizontal do meio: o slide 7 e dividido em duas
    colunas, e ali quem separa e um fio vertical.
    """
    s = prs.slides.add_slide(prs.slide_layouts[6])
    fundo = s.background.fill
    fundo.gradient()
    fundo.gradient_angle = 315.0
    fundo.gradient_stops[0].color.rgb = BG1
    fundo.gradient_stops[1].color.rgb = BG0

    tf = caixa(s, L, 0.32, 9.0, 0.34)
    escreve(tf, [("KAIRÓS", ORANGE, True), (f"   {titulo}", TEXT, False)],
            15.0, spc=0.8, primeiro=True)
    tf = caixa(s, R - 2.6, 0.38, 2.6, 0.24)
    escreve(tf, [(numero, MUTED, False)], 11.0, alinha=PP_ALIGN.RIGHT,
            primeiro=True)
    regua(s, L, 0.84, R)

    if banda:
        regua(s, L, BANDA, R)
    regua(s, L, PE, R)
    tf = caixa(s, L, PE + 0.10, 11.53, 0.20)
    escreve(tf, [("Diagrama e slides gerados por ", MUTED, False),
                 ("scripts/slides_3a6_pptx.py", MUTED2, False),
                 (" — nenhuma caixa foi posicionada à mão.", MUTED, False)],
            8.5, primeiro=True)
    return s


# ----------------------------------------------------------------- diagrama
# O diagrama e o mesmo em todos os slides; muda a GEOMETRIA de cada no e a cor.
# E a diferenca entre estas duas tabelas que o Morph anima.
TEXTOS = {
    "eq":   ("EQUILÍBRIO",     "o que o mercado já espera", None),
    "q":    ("OPINIÃO  ·  Q",  "quanto se espera render",   "fonte"),
    "om":   ("CONFIANÇA  ·  Ω", "o quanto ela pesa",        "fonte"),
    "cart": ("CARTEIRA  BL",   "9 ETFs, os pesos do dia",   None),
}
# geometria em polegadas, por estado: nome -> (x, y, w, h)
LINHA = {                                     # slides 3-5: uma linha larga
    "eq":   (0.90, 1.30, 3.42, 1.22),
    "q":    (4.95, 1.30, 3.42, 1.22),
    "om":   (9.01, 1.30, 3.42, 1.22),
    "cart": (4.95, 3.00, 3.42, 1.04),
}
CANTO = {                                     # slide 6: a MESMA linha, a 0,50x,
    "eq":   (0.90, 1.24, 1.86, 0.60),         # recolhida no canto superior esq.
    "q":    (3.06, 1.24, 1.86, 0.60),
    "om":   (5.22, 1.24, 1.86, 0.60),
    "cart": (3.06, 2.20, 1.86, 0.56),
}
# O corpo do texto NAO acompanha a escala da caixa: 13 pt x 0,50 daria 6,5 pt,
# ilegivel projetado. O no encolhe, o rotulo so desce para 9 pt e o subtitulo
# sai de cena — o Morph interpola os dois tamanhos do mesmo jeito.

# Onde a luz pousa em cada slide: (x, y, w, h, alfa). O halo e persistente,
# entao ele DESLIZA para o no que a fala esta explicando.
HALO = {
    "nenhum":  (1.60, 0.95, 10.10, 2.00, 9000),
    "q":       (4.16, 0.86, 5.00, 2.10, 17000),
    "omega":   (8.22, 0.86, 5.00, 2.10, 17000),
    "apagado": (1.09, 2.70, 5.80, 1.46, 15000),
}


def no(slide, nome, geo, canto, estado):
    """Um no: painel + pino de acento + texto DENTRO dele.

    O texto vai no proprio painel para andar junto no Morph; o pino e forma a
    parte porque muda de espessura quando o no acende.
    """
    x, y, w, h = geo
    titulo, subtitulo, tem_fonte = TEXTOS[nome]
    acento = ACENTO[nome]
    aceso, apagado = estado == "aceso", estado == "apagado"

    if aceso:
        topo, base, borda, luz = ON_A, ON_B, acento, brilho(str(acento))
        cor_tit, cor_sub, cor_pino, esp = acento, MUTED2, acento, 0.085
    elif apagado:
        topo, base, borda, luz = OFF_A, OFF_B, EDGE_OFF, ""
        cor_tit, cor_sub = MUTED2, MUTED
        cor_pino, esp = mistura(acento, PANEL_B, 0.62), 0.05
    else:
        topo, base, borda, luz = PANEL_A, PANEL_B, EDGE, ""
        cor_tit, cor_sub = TEXT, BODY
        cor_pino, esp = mistura(acento, PANEL_A, 0.28), 0.055

    sh = painel(slide, x, y, w, h, topo, base, borda, luz=luz)
    sh.name = f"!!{nome}"
    recuo = 0.20 if canto else 0.28
    tf = sh.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = Inches(recuo + esp + (0.12 if canto else 0.18))
    tf.margin_right = Inches(0.14)
    tf.margin_top = tf.margin_bottom = 0

    tit_pt, sub_pt = (8.5, 7.0) if canto else (13.0, 9.5)
    escreve(tf, [(titulo, cor_tit, True)], tit_pt, spc=0.5 if canto else 0.9,
            espaco=1.1, primeiro=True)
    if not canto:
        escreve(tf, [(subtitulo, cor_sub, False)], sub_pt, espaco=1.1, antes=2.0)
        if tem_fonte:
            # no slide 3 a fonte de Q e de Omega e o gestor; do 4 em diante, o
            # Polymarket — e a troca que a fala do slide 4 anuncia
            fonte = (("digitado pelo gestor", MUTED, False) if estado == "frio"
                     else ("POLYMARKET", ORANGE, True))
            escreve(tf, [fonte], sub_pt, espaco=1.1, antes=2.0)

    p = pino(slide, x + recuo, y + h * 0.24, h * 0.52, cor_pino, esp=esp)
    p.name = f"!!bar_{nome}"
    return sh


def diagrama(slide, ativo, canto=False):
    """Desenha o diagrama do BL realcando a peca que o slide esta explicando.

    `ativo` ∈ {"nenhum", "q", "omega", "apagado"}. Nada some entre um build e o
    outro — o que muda e a geometria e a cor, e e isso que o Morph anima. A
    FORMA do diagrama e a mesma nos quatro slides: no 6 ele so encolhe e recua
    para o canto, e e esse deslocamento que o Morph desenha.
    """
    geos = CANTO if canto else LINHA
    apagado = ativo == "apagado"
    forte = {"q": "q", "omega": "om"}.get(ativo)

    hx, hy, hw, hh, ha = HALO[ativo]
    h = halo(slide, hx, hy, hw, hh, alfa=ha)
    h.name = "!!halo"

    for nome, geo in geos.items():
        if apagado:
            estado = "apagado"
        elif nome == forte:
            estado = "aceso"
        elif ativo == "nenhum":
            estado = "frio"
        else:
            estado = "normal"
        no(slide, nome, geo, canto, estado)

    # operadores: dois discos no vao entre os nos, para a linha ter respiro
    eq, q, om, cart = (geos[k] for k in ("eq", "q", "om", "cart"))
    d = 0.22 if canto else 0.38
    for nome, (a, b), sinal in (("op_mais", (eq, q), "+"),
                                ("op_vezes", (q, om), "×")):
        cx = (a[0] + a[2] + b[0]) / 2
        disco = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(cx - d / 2),
                                       Inches(eq[1] + eq[3] / 2 - d / 2),
                                       Inches(d), Inches(d))
        disco.fill.solid()
        disco.fill.fore_color.rgb = OFF_A if apagado else PANEL_A
        disco.line.color.rgb = EDGE_OFF if apagado else EDGE
        disco.line.width = Pt(0.75)
        disco.shadow.inherit = False
        tf = disco.text_frame
        tf.word_wrap = False
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.margin_left = tf.margin_right = 0
        tf.margin_top = tf.margin_bottom = 0
        escreve(tf, [(sinal, MUTED if apagado else MUTED2, False)],
                9.0 if canto else 14.0, espaco=1.0, alinha=PP_ALIGN.CENTER,
                primeiro=True)
        disco.name = f"!!{nome}"

    # A carteira sai dos TRES nos juntos, nao do Q — entao quem os junta e uma
    # CHAVE que abraca a linha inteira e desagua na carteira. Tres setas
    # convergindo diziam o mesmo, com tres pontas se atropelando na mesma boca;
    # a chave e a notacao que o proprio quadro-negro usaria.
    cor_ln = mistura(MUTED, PANEL_B, 0.45) if apagado else MUTED
    bx = cart[0] + cart[2] / 2
    topo = eq[1] + eq[3] + (0.10 if canto else 0.16)
    alt = (cart[1] - topo) * 0.60
    ch = chave(slide, eq[0], topo, om[0] + om[2] - eq[0], alt, cor=cor_ln)
    ch.name = "!!chave"
    f = flecha(slide, bx, topo + alt, bx, cart[1] - 0.02, cor=cor_ln, esp=1.25)
    f.name = "!!seta_cart"


# ------------------------------------------------------------------- slides
def s3_bl(prs):
    """Diagrama inteiro, nenhum nó aceso: só o que o Black-Litterman faz."""
    s = moldura(prs, "03", "Como o Black-Litterman funciona")
    diagrama(s, "nenhum")

    bloco(s, L, DET, 5.30, "O que o modelo faz", [
        ("Parte do equilíbrio.",
         " A carteira base é a que o mercado já carrega — não um palpite nosso."),
        ("Você entrega opinião e confiança.",
         " O modelo faz a conta e devolve os pesos do dia."),
        ("Confiança zero, carteira do mercado.",
         " O BL nunca inventa um desvio que a opinião não sustente."),
    ])

    bloco(s, 6.60, DET, 5.83, "Por que uma opinião de mercado", [
        ("Cada sinal é independente.",
         " Uma view sobre o Fed não contamina a view sobre inflação."),
        ("Não é preciso opinar sobre tudo.",
         " O que não tem view fica no equilíbrio, sem custo e sem ruído."),
        ("Probabilidade negociada, não palpite.",
         " Tem dinheiro em risco atrás de cada número."),
    ])

    # a deixa do slide 4 ocupa o vazio a esquerda da carteira, no proprio
    # diagrama — no pe do slide ela ficava espremida entre a coluna e o rodape
    pino(s, L, 3.20, 0.56, ORANGE, esp=0.05)
    tf = caixa(s, L + 0.26, 3.22, 3.50, 0.60)
    escreve(tf, [("E agora: onde o Polymarket entra nisso?", ORANGE, True)],
            14.0, espaco=1.25, primeiro=True)
    s.notes_slide.notes_text_frame.text = (
        "abre com o diagrama frio. A pergunta do fim é a deixa do slide 4 — "
        "o Morph acende o Q enquanto ela é dita.")
    sela(s, 3)
    return s


def s4_q(prs):
    """Q aceso: como uma probabilidade negociada vira opinião de retorno."""
    s = moldura(prs, "04", "A opinião (Q) vem do Polymarket")
    diagrama(s, "q")
    morph(s)

    rotulo(s, L, DET, "De onde vem o Q", w=7.4, tamanho=ROT_PT)
    passos = ["probabilidade", "− âncora", "surpresa (bps)", "× β medido",
              "retorno por ativo"]
    partes = []
    for i, passo in enumerate(passos):
        if i:
            partes.append(("   →   ", RULE, False))
        partes.append((passo, TEXT if i in (0, 4) else MUTED2, i in (0, 4)))
    tf = caixa(s, L, CORPO, 7.40, 0.26)
    escreve(tf, partes, 11.0, primeiro=True)
    regua(s, L, CORPO + 0.36, L + 7.40)
    tf = caixa(s, L, CORPO + 0.46, 7.40, 0.24)
    escreve(tf, [("Q = (E_poly − âncora) · Σ Pᵢ βᵢ", MUTED2, False)], 11.0,
            spc=0.4, primeiro=True)

    chamada(s, L, CORPO + 0.92, 7.40, 1.16, [
        ("β medido em anúncios passados.",
         " Não é número de manual nem arbitragem nossa — sai de event-study."),
        ("Em quase todo pregão há ao menos uma view ativa.",
         " Não é preciso ter opinião sobre tudo, sempre."),
    ])

    rotulo(s, 8.53, DET, "As quatro views", w=3.90, tamanho=ROT_PT)
    tabela(s, 8.53, CORPO, 3.90, ("View", "Ativa", "Exp."), [
        ("2.3  decisão do Fed", "312/374", "neutra"),
        ("2.2  inflação do mês", "253/374", "neutra"),
        ("B  taxa no fim do ano", "154/374", "neutra"),
        ("15b  dúvida na véspera", "26/374", "direc."),
    ])
    tf = caixa(s, 8.53, CORPO + 1.86, 3.90, 0.40)
    escreve(tf, [("745 view-dias em 374 pregões.", TEXT, True),
                 (" Nenhum dia depende de uma view só.", BODY, False)], 10.0,
            espaco=1.25, primeiro=True)
    s.notes_slide.notes_text_frame.text = (
        "a fala percorre UMA view inteira (o Fed); a tabela existe para as "
        "outras três serem só nomeadas.")
    sela(s, 4)
    return s


def s5_omega(prs):
    """Ω aceso: o que decide se a view entra e com que peso."""
    s = moldura(prs, "05", "A confiança (Ω) é medida, não declarada")
    diagrama(s, "omega")
    morph(s)

    bloco(s, L, DET, 7.40, "O que decide se a view entra", [
        ("Estabilidade da distribuição.",
         " Quanto a probabilidade se moveu antes de a gente olhar para ela."),
        ("Coerência do mercado.",
         " O quanto o livro deixa de somar 1 — mercado incoerente não entra."),
        ("O critério foi declarado antes de medir.",
         " Testamos quatro; só estes dois tinham efeito. Mercado ilíquido é vetado."),
    ])

    chamada(s, L, 6.34, 7.40, 0.46, [
        ("c ≥ 1, sempre.",
         " O Black-Litterman clássico é o teto da confiança, nunca o piso."),
    ])

    rotulo(s, 8.53, DET, "Quatro testados, dois ficaram", w=3.90, tamanho=ROT_PT)
    tabela(s, 8.53, CORPO, 3.90, ("Critério", "Veredito", ""), [
        ("estabilidade", "ENTRA", ""),
        ("coerência", "ENTRA", ""),
        ("volume negociado", "VETO", ""),
        ("proximidade do evento", "FORA", ""),
    ])
    tf = caixa(s, 8.53, CORPO + 1.86, 3.90, 0.40)
    escreve(tf, [("185 de 2.795 views vetadas", TEXT, True),
                 (" pela régua, sem nenhuma decisão discricionária.", BODY,
                  False)], 10.0, espaco=1.25, primeiro=True)
    s.notes_slide.notes_text_frame.text = (
        "o número das views vetadas fica na tela, não na fala.")
    sela(s, 5)
    return s


# nos que so existem no slide 6: (nome, x, y, w, h, titulo, subtitulo, acento)
NOVOS = [
    ("!!tat", 0.90, 3.06, 6.18, 0.72, "CAMADA TÁTICA",
     "lê o movimento da probabilidade", ORANGE),
    ("!!teto", 7.90, 2.24, 2.05, 0.86, "TETO DE RISCO",
     "divide o espaço entre as duas", ORANGE),
    ("!!final", 10.38, 2.24, 2.05, 0.86, "CARTEIRA DO DIA",
     "9 ETFs, uma alocação só", MINT),
]


def s6_tatica(prs):
    """O diagrama inteiro recua para o canto e vira UMA das duas camadas."""
    s = moldura(prs, "06", "A camada tática e o teto de risco")
    diagrama(s, "apagado", canto=True)
    morph(s)

    rotulo(s, L, 0.94, "Camada estrutural  ·  lê o nível", w=6.00, cor=MUTED,
           tamanho=8.5)

    for nome, x, y, w, h, titulo, sub, acento in NOVOS:
        sh = painel(s, x, y, w, h, ON_A, ON_B, acento,
                    luz=brilho(str(acento), rad=110000, alfa=26000))
        sh.name = nome
        tf = sh.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.margin_left = Inches(0.50 if w > 3 else 0.42)
        tf.margin_right = Inches(0.12)
        tf.margin_top = tf.margin_bottom = 0
        escreve(tf, [(titulo, acento, True)], 13.0 if w > 3 else 11.0,
                spc=0.9 if w > 3 else 0.4, espaco=1.1, primeiro=True)
        escreve(tf, [(sub, MUTED2, False)], 9.5 if w > 3 else 8.5, espaco=1.15,
                antes=2.0)
        p = pino(s, x + 0.24, y + h * 0.24, h * 0.52, acento, esp=0.085)
        p.name = f"{nome}_bar"

    # As DUAS camadas entram no teto pela MESMA boca, e cada uma chega nela de
    # onde de fato termina — a carteira BL em cima, a tatica embaixo.
    bx, by = NOVOS[1][1], NOVOS[1][2] + NOVOS[1][4] / 2
    cart = CANTO["cart"]
    curva(s, cart[0] + cart[2], cart[1] + cart[3] / 2, bx, by, cor=MUTED2)
    curva(s, NOVOS[0][1] + NOVOS[0][3], NOVOS[0][2] + NOVOS[0][4] / 2, bx, by,
          cor=MUTED2)
    flecha(s, NOVOS[1][1] + NOVOS[1][3], by, NOVOS[2][1] - 0.04, by, cor=MUTED2)

    bloco(s, L, DET, 4.30, "O que a camada tática negocia", [
        ("Recessão nos EUA.",
         " Janelas de 3, 5 e 10 pregões. XLP defensivo contra XLK cíclico."),
        ("Maioria na Câmara.",
         " Janela de 20 pregões, mesmo livro, neutro ao índice."),
        ("Nenhum parâmetro novo.",
         " O tamanho sai da mesma conta que dimensiona uma view — quem "
         "dimensiona é o BL."),
    ])

    rotulo(s, 5.60, DET, "Abril de 2025", w=3.30, tamanho=ROT_PT)
    chamada(s, 5.60, CORPO, 3.30, 1.60, [
        ("De 37% para 65% em uma semana.",
         " É o salto da chance de recessão no Polymarket."),
        ("Compra o defensivo, vende o cíclico.",
         " No dia 3 de abril a bolsa cai 5% — e a camada ganha."),
    ])

    rotulo(s, 9.30, DET, "O teto de risco", w=3.13, tamanho=ROT_PT)
    tf = caixa(s, 9.30, CORPO - 0.06, 3.13, 0.40)
    escreve(tf, [("Σ | w − w_mkt |  ≤  1", ORANGE, True)], 17.0, espaco=1.0,
            primeiro=True)
    tf = caixa(s, 9.30, CORPO + 0.46, 3.13, 1.20)
    escreve(tf, [("8 configurações testadas", TEXT, True),
                 (" — o teto saiu do Sharpe, não da preferência.", BODY,
                  False)], CORPO_PT, espaco=1.30, primeiro=True)
    escreve(tf, [("O Ω diz quanta confiança;", TEXT, True),
                 (" o teto diz quanto espaço cada camada ocupa.", BODY,
                  False)], CORPO_PT, espaco=1.30, antes=9.0)
    s.notes_slide.notes_text_frame.text = (
        "estado final: o Morph empilha a camada estrutural no canto enquanto "
        "a tática e o teto entram.")
    sela(s, 6)
    return s


# ----------------------------------------------- slide 7: o repo como grafo
# A figura sai de `scripts/grafo_repo.py` (no = arquivo, aresta = um arquivo
# citando o nome do outro). As contagens do slide sao lidas do MESMO
# levantamento que desenha o PNG — nao ha numero de grafo digitado aqui.
ESQ, W_ESQ = 0.90, 5.95            # coluna da figura
DIR, W_DIR = 7.30, 5.13            # coluna dos dados
DIVISOR = 6.95                     # o fio que separa as duas
TIMELINE = RAIZ / "Uteis" / "graficos" / "p5_timeline.png"


def kpi(slide, x, y, w, titulo, valor, nota):
    """Numero grande, rotulo em cima e nota embaixo.

    O rotulo tem duas linhas de folga de proposito: na faixa de quatro, a
    celula tem 1,45" e "DECISOES REGISTRADAS" nao cabe numa linha so.
    """
    tf = caixa(slide, x, y, w, 0.30)
    escreve(tf, [(titulo.upper(), MUTED, False)], 7.5, spc=0.8, espaco=1.15,
            primeiro=True)
    tf = caixa(slide, x, y + 0.32, w, 0.42)
    escreve(tf, [(valor, ORANGE, True)], 25.0, espaco=1.0, primeiro=True)
    tf = caixa(slide, x, y + 0.76, w, 0.30)
    escreve(tf, [(nota, BODY, False)], 8.0, espaco=1.18, primeiro=True)


def legenda(slide, x, y, itens, tam=8.5):
    """Bolinha + nome, em linha — a chave de cor da figura."""
    for cor, texto in itens:
        d = 0.085
        ponto = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x),
                                       Inches(y + 0.035), Inches(d), Inches(d))
        ponto.fill.solid()
        ponto.fill.fore_color.rgb = cor
        ponto.line.fill.background()
        ponto.shadow.inherit = False
        tf = caixa(slide, x + 0.15, y, 2.0, 0.20)
        escreve(tf, [(texto, MUTED2, False)], tam, primeiro=True)
        # largura media de caractere ~0,55 em; o resto e o respiro entre itens
        x += 0.15 + len(texto) * tam * 0.55 / 72 + 0.30
    return x


def s7_ia(prs):
    """O repositório como grafo: o contrato no meio, tudo pendurado nele."""
    if not GRAFO.exists():
        grafo_repo.monta()
    nomes, _, arestas = grafo_repo.levantar()

    s = moldura(prs, "07", "A infraestrutura de IA", banda=False)
    fio = s.shapes.add_connector(1, Inches(DIVISOR), Inches(0.98),
                                 Inches(DIVISOR), Inches(PE - 0.10))
    fio.line.color.rgb = RULE
    fio.line.width = Pt(0.75)

    # ---- coluna da esquerda: a figura
    rotulo(s, ESQ, 0.94, "O repositório como grafo", w=4.0, tamanho=ROT_PT)
    tf = caixa(s, ESQ, 0.94, W_ESQ, 0.20)
    escreve(tf, [(f"{len(nomes)} arquivos", TEXT, True),
                 (f"  ·  {len(arestas)} ligações", MUTED, False)], 9.5,
            alinha=PP_ALIGN.RIGHT, primeiro=True)
    legenda(s, ESQ, 1.20, [(ORANGE, "contrato"), (MINT, "análise"),
                           (BLUE, "código"), (MUTED, "entrega")])

    halo(s, ESQ + 0.40, 1.66, 5.10, 3.80, alfa=9000)
    imagem(s, GRAFO, ESQ + (W_ESQ - 4.05) / 2, 1.44, 4.05)
    tf = caixa(s, ESQ, 5.58, W_ESQ, 0.20)
    escreve(tf, [("uma ligação é um arquivo citando o nome do outro — "
                  "ninguém escreveu link para virar grafo", MUTED, False)],
            8.5, primeiro=True)

    for i, (titulo, valor, nota) in enumerate([
        ("Sessões de IA", "91", "Felipe 55 · Lia 18 · Paulo 18"),
        ("Tokens por sessão", "232k", "média — 19,7M no total"),
        ("Decisões registradas", "81", "escaladas para decisão humana"),
        ("Recorreção", "37%", "das sessões pediram 2ª rodada"),
    ]):
        kpi(s, ESQ + i * 1.49, 5.82, 1.45, titulo, valor, nota)

    # ---- coluna da direita: as regras, a linha do tempo e o fecho
    bloco(s, DIR, 0.94, W_DIR, "As regras, escritas antes", [
        ("Um dono por módulo, um branch por dono.",
         " Código de outro dono não se edita — o defeito vira observação no "
         "LOG dele."),
        ("Ritual de sessão obrigatório.",
         " Abre lendo as decisões pendentes, fecha escrevendo no LOG."),
        ("Pedido e resposta viram arquivo.",
         " 3 PEDIDO_*.md e 8 RESPOSTA_*.md: a conversa entre membros ficou no "
         "repositório, não no chat."),
    ])

    rotulo(s, DIR, 3.30, "Contexto por dia  ·  decisões acumuladas", w=W_DIR,
           tamanho=ROT_PT)
    imagem(s, TIMELINE, DIR, 3.58, W_DIR)

    chamada(s, DIR, 5.92, W_DIR, 0.70, [
        ("A IA nunca fecha decisão metodológica.",
         " Nenhuma sessão recomeçava do zero, e nenhuma decidia sozinha."),
    ])

    s.notes_slide.notes_text_frame.text = (
        "o grafo é o argumento: o contrato (CLAUDE.md, LOG.md, "
        "Decisoes_pendentes.md) é o miolo de onde tudo pende — o second brain "
        "não é metáfora, é a forma que o repositório tomou. Medido no branch "
        "Felipe pelo grafo_repo.py, não estimado.")
    sela(s, 7)
    return s


# ----------------------------------------------------------------- montagem
def monta(saida: Path = SAIDA) -> Path:
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    for construtor in (s3_bl, s4_q, s5_omega, s6_tatica, s7_ia):
        construtor(prs)
    saida.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(saida))
    return saida


# ---------------------------------------------------------------- auto-teste
MC_TAG = ("{http://schemas.openxmlformats.org/markup-compatibility/2006}"
          "AlternateContent")


def moldura_da_forma(sh):
    """Caixa que a forma de fato ocupa na tela.

    A chave e guardada em pe e girada 90 graus, e o `.left/.top` do arquivo e o
    da caixa NAO girada — que cai fora do slide. A rotacao e em torno do
    centro, entao a caixa na tela sai do centro mais a projecao dos lados.
    """
    ang = math.radians(sh.rotation or 0.0)
    w, h = sh.width, sh.height
    larg = abs(w * math.cos(ang)) + abs(h * math.sin(ang))
    alt = abs(w * math.sin(ang)) + abs(h * math.cos(ang))
    cx, cy = sh.left + w / 2, sh.top + h / 2
    return cx - larg / 2, cy - alt / 2, cx + larg / 2, cy + alt / 2


def demo() -> None:
    """Checa o que o .pptx nao denuncia: o Morph quebrado, effectLst duplicado
    e caixa fora da moldura. Roda com `python scripts/slides_3a6_pptx.py --demo`.
    """
    from pptx import Presentation as _P

    caminho = monta()
    prs = _P(str(caminho))
    slides = list(prs.slides)
    larg, alt = prs.slide_width, prs.slide_height

    for i, s in enumerate(slides, start=3):
        for sh in s.shapes:
            x0, y0, x1, y1 = moldura_da_forma(sh)
            assert x0 >= -Emu(1) and y0 >= -Emu(1), \
                f"slide {i}: caixa fora da moldura ({sh.name})"
            assert x1 <= larg + Emu(9144), \
                f"slide {i}: caixa estoura a direita ({sh.name})"
            assert y1 <= alt + Emu(9144), \
                f"slide {i}: caixa estoura embaixo ({sh.name})"
            # dois <a:effectLst> no mesmo spPr corrompem o arquivo, e o
            # python-pptx salva sem reclamar — so o PowerPoint denuncia
            sp = getattr(sh._element, "spPr", None)
            if sp is not None:
                assert len(sp.findall(A + "effectLst")) <= 1, \
                    f"slide {i}: effectLst duplicado ({sh.name})"

    # O teste que importa: o diagrama so anda se os nomes `!!` casarem em TODOS
    # os slides. Um nome que aparece num slide e some no seguinte vira corte.
    nomes = []
    for i, s in enumerate(slides, start=3):
        lista = [sh.name for sh in s.shapes if sh.name.startswith("!!")]
        assert len(lista) == len(set(lista)), f"slide {i}: nome !! repetido"
        nomes.append(set(lista))
    nucleo = nomes[0]
    assert len(nucleo) == 13, \
        f"o diagrama tem 13 formas persistentes, achei {sorted(nucleo)}"
    for i, conj in enumerate(nomes[:4], start=3):
        assert nucleo <= conj, \
            f"slide {i} perdeu formas do diagrama: {sorted(nucleo - conj)}"
    assert not nomes[4], "o slide 7 não tem diagrama — nada de `!!` nele"

    # e a transicao precisa estar de fato no XML dos slides 4, 5 e 6
    for i, s in enumerate(slides, start=3):
        tem = s.element.find(MC_TAG) is not None
        assert tem == (i in (4, 5, 6)), \
            f"slide {i}: transicao morph {'sobrando' if tem else 'faltando'}"

    assert len(slides) == 5, f"o deck tem 5 slides (3 a 7), achei {len(slides)}"
    print(f"ok — {caminho.name}: 5 slides (3 a 7) · {len(nucleo)} formas viajam "
          f"entre 3 e 6 · morph nos slides 4, 5 e 6")


if __name__ == "__main__":
    import sys

    if "--demo" in sys.argv:
        demo()
    else:
        print(monta())
