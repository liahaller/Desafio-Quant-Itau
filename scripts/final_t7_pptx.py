"""Deck da final RECOMPOSTO no estilo T6 — grava `Final/FINAL_T7.pptx`.

O `final_t6_pptx.py` trocou a pele do deck (fundo, fontes, cores) mas manteve
a composição antiga: cards com borda em todo lugar, elementos pequenos
flutuando, vão sobrando. Aqui o deck é RECONSTRUÍDO slide a slide, com a
composição dos decks de challenge (Waterloo/Rotman 2026, Polaris/Insper —
`Final/Reestilizar/`), mantendo o estilo T6 (grafite, Segoe UI, dourado como
acento, azul só nos gráficos) e todo o conteúdo do `Final/FINAL.pptx`:

  - "Seção | Título" com régua; marca KAIRÓS à direita; nav inferior com a
    seção ativa sublinhada e nº da página.
  - Conteúdo em colunas com rótulo (kicker dourado + régua fina), texto
    corrido e números grandes SOLTOS — sem caixinhas.
  - Uma única caixa por slide, quando há conclusão: a tracejada do T6.
  - Fluxos com círculos numerados e setas finas, em vez de cards.
  - Linha de fonte em itálico no rodapé do conteúdo.
  - Imagens (gráficos matplotlib, print do Polymarket, robô, grafo) e notas
    do apresentador são lidas do `FINAL.pptx`; a sequência Morph do "segundo
    cérebro" é preservada (nós/arestas copiados e transladados, nomes `!!`).

O slide 16 do original (vazio) não entra: o deck sai com 32 slides.

Uso:
    python scripts/final_t7_pptx.py            # gera Final/FINAL_T7.pptx
    python scripts/final_t7_pptx.py --render   # e exporta PNG via PowerPoint
"""

import copy
import io
import os
import subprocess
import sys
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_LINE
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml import parse_xml
from pptx.oxml.ns import nsdecls, qn
from pptx.util import Emu, Inches, Pt

RAIZ = Path(__file__).resolve().parent.parent
ENTRADA = RAIZ / "Final" / "FINAL.pptx"
SAIDA = RAIZ / "Final" / "FINAL_T7.pptx"

# ------------------------------------------------------------------ paleta T6
BG = "15181D"
RULE = "3A404A"
TEXT = "FFFFFF"
BODY = "D5D9E0"
MUTED = "9AA3AF"
FOOT = "6B7280"
GOLD = "FFB531"
BLUE = "6C8CE0"
TEAL = "2FD3B0"

F_BODY = "Segoe UI"
F_SEMI = "Segoe UI Semibold"
F_MONO = "Consolas"
F_SERIF = "Georgia"

W, H = 13.333, 7.5
L, R = 0.55, 12.78
CW = R - L
YT = 1.30                                  # topo do conteúdo (abaixo da régua)

# Seções da nav e o slide (novo) em que cada uma começa.
NAV = [("Hipótese", 1), ("Polymarket", 3), ("Estratégia", 5), ("Backtest", 14),
       ("IA", 16), ("Conclusão", 30)]

ORIG = Presentation(ENTRADA)               # só para imagens, notas e overlays


# --------------------------------------------------------------- primitivas
def rgb(h):
    return RGBColor.from_string(h)


def r(t, c=BODY, f=F_BODY, pt=None, b=False, i=False, spc=None, base=None):
    """Um run: texto, cor, fonte, tamanho, negrito, itálico, tracking, baseline."""
    return dict(t=t, c=c, f=f, pt=pt, b=b, i=i, spc=spc, base=base)


def txt(s, x, y, w, h, paras, pt=11, align="l", anchor="t", lsp=None, after=None,
        wrap=True, name=None):
    """Caixa de texto sem margens. `paras`: str | [runs] | [[runs], [runs]]."""
    if isinstance(paras, str):
        paras = [[r(paras)]]
    elif paras and isinstance(paras[0], (dict, str)):
        paras = [paras]
    sh = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    if name:
        sh.name = name
    tf = sh.text_frame
    tf.word_wrap = wrap
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = {"t": MSO_ANCHOR.TOP, "m": MSO_ANCHOR.MIDDLE,
                          "b": MSO_ANCHOR.BOTTOM}[anchor]
    for k, runs in enumerate(paras):
        p = tf.paragraphs[0] if k == 0 else tf.add_paragraph()
        p.alignment = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER, "r": PP_ALIGN.RIGHT}[align]
        if lsp:
            p.line_spacing = lsp
        if after:
            p.space_after = Pt(after)
        for rd in runs:
            if isinstance(rd, str):
                rd = r(rd)
            rr = p.add_run()
            rr.text = rd["t"]
            f = rr.font
            f.name, f.size = rd["f"], Pt(rd["pt"] or pt)
            f.bold, f.italic = rd["b"], rd["i"]
            f.color.rgb = rgb(rd["c"])
            if rd["spc"] or rd["base"]:
                rPr = rr._r.get_or_add_rPr()
                if rd["spc"]:
                    rPr.set("spc", str(rd["spc"]))
                if rd["base"]:
                    rPr.set("baseline", str(rd["base"]))
    return sh


def rect(s, x, y, w, h, fill=None, line=None, lw=0.75, dash=False,
         shape=MSO_SHAPE.RECTANGLE, name=None):
    sh = s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    if name:
        sh.name = name
    sh.shadow.inherit = False
    if fill:
        sh.fill.solid()
        sh.fill.fore_color.rgb = rgb(fill)
    else:
        sh.fill.background()
    if line:
        sh.line.color.rgb = rgb(line)
        sh.line.width = Pt(lw)
        if dash:
            sh.line.dash_style = MSO_LINE.DASH
    else:
        sh.line.fill.background()
    sh.text_frame.text = ""
    return sh


def hrule(s, x, y, w, color=RULE):
    return rect(s, x, y, w, 0.01, fill=color)


def vrule(s, x, y, h, color=RULE):
    return rect(s, x, y, 0.01, h, fill=color)


def arrow(s, x1, y1, x2, y2, color=GOLD, lw=1.25):
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1),
                               Inches(x2), Inches(y2))
    c.line.color.rgb = rgb(color)
    c.line.width = Pt(lw)
    ln = c.line._get_or_add_ln()
    ln.append(parse_xml(f'<a:tailEnd {nsdecls("a")} type="triangle" w="med" len="med"/>'))
    return c


def badge(s, cx, cy, n, d=0.28):
    """Círculo numerado dourado (Waterloo)."""
    sh = rect(s, cx - d / 2, cy - d / 2, d, d, fill=GOLD, shape=MSO_SHAPE.OVAL)
    tf = sh.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    rr = p.add_run()
    rr.text = str(n)
    rr.font.name, rr.font.size, rr.font.bold = F_SEMI, Pt(10), True
    rr.font.color.rgb = rgb(BG)
    return sh


def caps(t):
    """Caixa alta só no latino — μ, β, Ω não viram Μ, Β."""
    return "".join(ch if "\u0370" <= ch <= "\u03ff" else ch.upper() for ch in t)


def kicker(s, x, y, w, text, rule=True):
    """Rótulo de bloco: dourado, caixa alta, tracking, régua fina embaixo."""
    txt(s, x, y, w, 0.22, [r(caps(text), GOLD, F_SEMI, 9, spc=200)])
    if rule:
        hrule(s, x, y + 0.28, w)


def bignum(s, x, y, w, num, label, sub=None, pt=28, color=TEXT, align="l"):
    """Número grande solto + rótulo em caixa alta + linha de apoio."""
    txt(s, x, y, w, pt / 72 * 1.25, [r(num, color, F_SEMI, pt)], align=align)
    yl = y + pt / 72 * 1.25 + 0.02
    txt(s, x, yl, w, 0.2, [r(label.upper(), MUTED, F_SEMI, 7.5, spc=150)], align=align)
    if sub:
        txt(s, x, yl + 0.22, w, 0.22, [r(sub, BODY, F_BODY, 9)], align=align)


def takeaway(s, y, runs, h=0.58, pt=12.5):
    """A única caixa do slide: conclusão em caixa tracejada (T6 / Waterloo)."""
    rect(s, L, y, CW, h, line=RULE, dash=True)
    txt(s, L + 0.3, y, CW - 0.6, h, runs, pt=pt, align="c", anchor="m")


def fonte(s, text, y=6.62):
    txt(s, L, y, CW, 0.2, [r(text, FOOT, F_BODY, 8, i=True)])


def shape_orig(idx, name):
    for sh in ORIG.slides[idx - 1].shapes:
        if sh.name == name:
            return sh
    raise KeyError(f"slide {idx}: {name}")


def pic(s, idx, name, x, y, w=None, h=None, nome=None):
    """Imagem do FINAL.pptx (slide original `idx`, forma `name`)."""
    sh = shape_orig(idx, name)
    iw, ih = sh.image.size
    if w and not h:
        h = w * ih / iw
    elif h and not w:
        w = h * iw / ih
    p = s.shapes.add_picture(io.BytesIO(sh.image.blob), Inches(x), Inches(y),
                             Inches(w), Inches(h))
    if nome:
        p.name = nome
    return p


def notas(s, idx):
    o = ORIG.slides[idx - 1]
    if o.has_notes_slide and o.notes_slide.notes_text_frame.text.strip():
        s.notes_slide.notes_text_frame.text = o.notes_slide.notes_text_frame.text


def copiar_transicao(s, idx):
    """Copia a transição (Morph com avanço automático) do slide original."""
    o = ORIG.slides[idx - 1]._element
    for el in o:
        if el.tag.endswith("}AlternateContent") or el.tag == qn("p:transition"):
            novo = copy.deepcopy(el)
            cm = s._element.find(qn("p:clrMapOvr"))
            cm.addnext(novo)
            return


TIMING = (
    '<p:timing {ns}><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" '
    'nodeType="tmRoot"><p:childTnLst><p:seq concurrent="1" nextAc="seek"><p:cTn id="2" '
    'dur="indefinite" nodeType="mainSeq"><p:childTnLst><p:par><p:cTn id="3" fill="hold">'
    '<p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst><p:par><p:cTn id="4" '
    'fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst><p:par>'
    '<p:cTn id="5" presetID="0" presetClass="path" presetSubtype="0" accel="20000" '
    'decel="40000" fill="hold" nodeType="afterEffect"><p:stCondLst><p:cond delay="0"/>'
    '</p:stCondLst><p:childTnLst><p:animMotion origin="layout" path="M {mdx} 0 L 0 0" '
    'pathEditMode="relative" ptsTypes=""><p:cBhvr><p:cTn id="6" dur="550" fill="hold"/>'
    '<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cBhvr></p:animMotion></p:childTnLst>'
    '</p:cTn></p:par></p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par>'
    '</p:childTnLst></p:cTn></p:seq></p:childTnLst></p:cTn></p:par></p:tnLst></p:timing>')


def deslizar(s, sh, dx):
    """Animação de trajetória: a forma entra vindo `dx` polegadas à esquerda."""
    xml = TIMING.format(ns=nsdecls("p"), mdx=f"{-dx / W:.5f}", spid=sh.shape_id)
    s._element.append(parse_xml(xml))


# --------------------------------------------------------------- moldura
def novo_slide(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = rgb(BG)
    return s


def cabecalho(s, secao, titulo=None):
    n = len(secao) + (len(titulo) + 5 if titulo else 0)
    pt = 20 if n <= 60 else 18 if n <= 81 else 16 if n <= 91 else 14
    runs = [r(secao, TEXT, F_SEMI, pt)]
    if titulo:
        runs += [r("  |  ", MUTED, F_BODY, pt), r(titulo, TEXT, F_BODY, pt)]
    txt(s, L, 0.38, 10.6, 0.5, runs, anchor="m")
    txt(s, 11.3, 0.38, R - 11.3, 0.5, [r("KAIRÓS", GOLD, F_SEMI, 11, spc=300)],
        align="r", anchor="m")
    hrule(s, L, 0.95, CW)


def rodape(s, idx, total):
    """Barra de navegação: seções do deck, ativa em destaque, nº da página."""
    ativa = [n for n, ini in NAV if idx >= ini][-1]
    y = H - 0.42
    hrule(s, L, y - 0.08, CW)
    n = len(NAV)
    wtot = CW - 0.8
    for i, (item, _) in enumerate(NAV):
        xi = L + i * wtot / n
        on = item == ativa
        txt(s, xi, y, wtot / n, 0.3, [r(item, TEXT if on else MUTED, F_SEMI if on else F_BODY, 8.5)],
            align="c", anchor="m")
        if on:
            rect(s, xi + wtot / n / 2 - 0.45, y + 0.29, 0.9, 0.03, fill=GOLD)
    txt(s, R - 0.65, y, 0.65, 0.3, [r(str(idx), MUTED, F_BODY, 9)], align="r", anchor="m")


def capa_base(s, sub, tagline, idx):
    """Capa e fechamento: marca grande, régua dourada, subtítulo, tagline, robô."""
    txt(s, L, 0.55, 8, 0.25, [r("ITAÚ QUANT AI CHALLENGE  ·  FINAL 2026", GOLD, F_SEMI, 9, spc=300)])
    txt(s, L, 1.85, 6.6, 1.7, [r("KAIROS", GOLD, F_SEMI, 96)], anchor="m")
    rect(s, L + 0.05, 3.72, 1.1, 0.04, fill=GOLD)
    txt(s, L, 3.95, 6.2, 1.0, [r(sub, TEXT, F_SEMI, 22)], lsp=1.05)
    txt(s, L, 5.05, 6.2, 1.0, tagline, pt=15, lsp=1.15)
    pic(s, idx, "Picture 22", 6.75, 0.72, h=6.15)
    hrule(s, L, 7.0, CW)
    txt(s, L, 7.08, 6, 0.3, [r("BLACK-LITTERMAN  ×  POLYMARKET", MUTED, F_SEMI, 8, spc=200)],
        anchor="m")


# --------------------------------------------------------------- slides
def s01_capa(s):
    capa_base(s, "Black-Litterman movido a probabilidade",
              [r("Kairós", GOLD, F_SERIF, 15, b=True, i=True),
               r(", no grego: o instante certo de agir. O modelo só age quando o mercado "
                 "de previsão traz oportunidade.", BODY, F_SERIF, 15, i=True)], 1)
    notas(s, 1)


def s02_hipotese(s):
    cabecalho(s, "Hipótese")
    kicker(s, L, 3.0, 3, "A pergunta", rule=False)
    txt(s, L, 3.4, 11.6, 1.8, [r("O ", TEXT, F_SEMI, 34), r("Polymarket", GOLD, F_SEMI, 34),
                                r(" é um sinal válido para estratégias quantitativas?",
                                  TEXT, F_SEMI, 34)], lsp=1.1)
    notas(s, 2)


def s03_polymarket(s):
    cabecalho(s, "Como o Polymarket funciona", "Um mercado de previsão, por dentro")
    kicker(s, L, YT, 4.6, "Como funciona")
    passos = [("Uma pergunta com data.", "Qual será a decisão do Fed em dezembro?"),
              ("Cada resposta é um contrato.", "Paga US$ 1 se acontecer, zero se não."),
              ("O preço é a probabilidade.", "62 centavos = 62% de chance."),
              ("As respostas formam uma distribuição.", "A média dela é o corte esperado.")]
    for i, (a, b) in enumerate(passos):
        y = YT + 0.55 + i * 1.15
        badge(s, L + 0.14, y + 0.15, i + 1)
        txt(s, L + 0.5, y, 4.1, 1.0, [[r(a, TEXT, F_SEMI, 13.5)], [r(b, BODY, F_BODY, 11.5)]],
            lsp=1.1, after=3)
    ph = 5.0
    pw = ph * 950 / 784
    pic(s, 3, "print_polymarket", R - pw, YT + 0.05, w=pw, h=ph)
    txt(s, R - pw, YT + ph + 0.15, pw, 0.2,
        [r("polymarket.com · mercado encerrado em 10/12/2025 · US$ 393,9 milhões negociados "
           "nessa pergunta", FOOT, F_BODY, 8, i=True)])
    notas(s, 3)


def s04_comparacao(s):
    cabecalho(s, "Polymarket", "Polymarket × mercado tradicional")
    kicker(s, L, YT, CW, "Reunião do Fed de dezembro/2025  ·  corte esperado, em bps")
    gw = 9.0
    gh = gw / 2.043
    pic(s, 4, "grafico_comparacao", L + (CW - gw) / 2, YT + 0.45, w=gw, h=gh)
    takeaway(s, 6.3, [r("surpresa", GOLD, F_SEMI, 16), r("   =   ", TEXT, F_BODY, 16),
                       r("polymarket", GOLD, F_SEMI, 16), r("   −   ", TEXT, F_BODY, 16),
                       r("mercado", BLUE, F_SEMI, 16)], h=0.6)
    notas(s, 4)


def s05_ficha(s):
    cabecalho(s, "Ficha técnica", "O que foi testado")
    # tabela à esquerda: rótulo | valor, réguas finas entre linhas
    kicker(s, L, YT, 5.3, "Ficha técnica")
    linhas = [("Universo", "9 ETFs americanos"), ("Benchmark", "S&P 500 (SPY)"),
              ("Janela", "374 pregões · fev/25 a ago/26"), ("Rebalanceamento", "Diário"),
              ("Custo", "2 bps por lado"), ("Plataforma", "Python")]
    for i, (a, b) in enumerate(linhas):
        y = YT + 0.45 + i * 0.82
        txt(s, L, y, 2.2, 0.66, [r(a, BODY, F_BODY, 13)], anchor="m")
        txt(s, L + 2.0, y, 3.3, 0.66, [r(b, TEXT, F_SEMI, 13.5)], align="r", anchor="m")
        hrule(s, L, y + 0.74, 5.3)
    x0, wc = 6.5, 6.28
    # os 9 ETFs: grade 3×3 de texto
    kicker(s, x0, YT, wc, "Os 9 ETFs")
    etfs = [("SPY", "S&P 500"), ("TIP", "Tesouro indexado à inflação"), ("TLT", "Tesouro de 20+ anos"),
            ("XLE", "Energia"), ("XLF", "Financeiro"), ("XLK", "Tecnologia"),
            ("XLP", "Consumo básico"), ("XLU", "Serviços públicos"), ("XLV", "Saúde")]
    for i, (t, d) in enumerate(etfs):
        x = x0 + (i % 3) * (wc / 3)
        y = YT + 0.45 + (i // 3) * 0.68
        txt(s, x, y, wc / 3 - 0.1, 0.6, [[r(t, TEXT, F_SEMI, 13)], [r(d, MUTED, F_BODY, 9.5)]])
    y2 = YT + 2.75
    kicker(s, x0, y2, wc, "De onde vêm os dados")
    fontes = [("Polymarket", "probabilidades, a cada 12h"), ("yfinance", "preços dos ETFs"),
              ("FRED", "juros e inflação")]
    for i, (t, d) in enumerate(fontes):
        x = x0 + i * (wc / 3)
        txt(s, x, y2 + 0.45, wc / 3 - 0.1, 0.6, [[r(t, TEXT, F_SEMI, 13)], [r(d, MUTED, F_BODY, 9.5)]])
    y3 = y2 + 1.5
    kicker(s, x0, y3, wc, "Os mercados que usamos")
    mercados = [("Fed", GOLD), ("Inflação", GOLD), ("Cortes no ano", GOLD),
                ("Dúvida", GOLD), ("Recessão", BLUE), ("Câmara", BLUE)]
    for i, (t, c) in enumerate(mercados):
        x = x0 + (i % 3) * (wc / 3)
        y = y3 + 0.42 + (i // 3) * 0.38
        txt(s, x, y, wc / 3 - 0.1, 0.32, [r("●  ", c, F_BODY, 9), r(t, BODY, F_BODY, 12)],
            anchor="m")
    txt(s, x0, y3 + 1.3, wc, 0.2, [r("dourado: views   ·   azul: camada tática", FOOT, F_BODY, 8, i=True)])
    notas(s, 5)


def s06_bl(s):
    cabecalho(s, "Como o Black-Litterman funciona")
    # a equação do modelo, em três termos numerados e dois operadores
    termos = [("Equilíbrio", "o que o mercado já espera", None),
              ("Previsão  (Q)", "quanto se espera render", "digitado pelo gestor"),
              ("Confiança  (Ω)", "o quanto ela pesa", "digitado pelo gestor")]
    xs = [L, L + 4.25, L + 8.5]
    for i, (a, b, c) in enumerate(termos):
        x = xs[i]
        badge(s, x + 0.14, YT + 0.16, i + 1)
        paras = [[r(a.upper(), TEXT, F_SEMI, 13, spc=150)], [r(b, BODY, F_BODY, 10.5)]]
        if c:
            paras.append([r(c, MUTED, F_BODY, 10.5)])
        txt(s, x + 0.5, YT + 0.02, 3.2, 1.1, paras, lsp=1.2)
    for x, op in ((L + 3.75, "+"), (L + 8.0, "×")):
        txt(s, x, YT - 0.03, 0.5, 0.5, [r(op, MUTED, F_BODY, 26)], align="c", anchor="m")
    arrow(s, L + CW / 2, YT + 1.25, L + CW / 2, YT + 1.75)
    txt(s, L, YT + 1.82, CW, 0.4, [r("=   CARTEIRA BL", TEXT, F_SEMI, 15, spc=150),
                                   r("      9 ETFs, os pesos do dia", BODY, F_BODY, 12)],
        align="c", anchor="m")
    hrule(s, L, YT + 2.5, CW)
    y2 = YT + 2.8
    kicker(s, L, y2, 5.8, "Por que o Black-Litterman")
    txt(s, L, y2 + 0.5, 5.8, 2.2, [
        [r("Opiniões independentes. ", TEXT, F_SEMI), r("Permite criar previsões diferentes e pontuais.")],
        [r("Não é preciso opinar sobre tudo. ", TEXT, F_SEMI),
         r("Nem sempre o Polymarket vai dar informação de valor.")]], pt=13, lsp=1.2, after=10)
    kicker(s, 6.9, y2, R - 6.9, "O que o Black-Litterman faz")
    txt(s, 6.9, y2 + 0.5, R - 6.9, 2.6, [
        [r("Parte do equilíbrio. ", TEXT, F_SEMI), r("A carteira base é a que o mercado já carrega.")],
        [r("Você entrega opinião e confiança. ", TEXT, F_SEMI),
         r("O modelo faz a conta e devolve os pesos do dia.")],
        [r("Sem confiança nas views, o BL devolve a carteira de mercado. ", TEXT, F_SEMI),
         r("Todo desvio do benchmark é proporcional à confiança na opinião.")]],
        pt=13, lsp=1.2, after=10)
    notas(s, 6)


def s07_q_omega(s):
    cabecalho(s, "A previsão (Q) e a confiança (Ω)", "Onde o Polymarket entra no Black-Litterman")
    kicker(s, L, YT, CW, "O modelo")
    txt(s, L, YT + 0.4, 8.6, 0.45, [r("μ = π + τΣPᵀ ( PτΣPᵀ + ", TEXT, F_SEMI, 20), r("Ω", GOLD, F_SEMI, 20),
                                   r(" )⁻¹ ( ", TEXT, F_SEMI, 20), r("Q", GOLD, F_SEMI, 20),
                                   r(" − Pπ )", TEXT, F_SEMI, 20)], anchor="m")
    txt(s, 9.3, YT + 0.4, R - 9.3, 0.45, [r("τ = 1/504      δ = 3,0", MUTED, F_MONO, 11)],
        align="r", anchor="m")
    txt(s, L, YT + 0.92, CW, 0.25, [r("π = δΣw_mkt: o equilíbrio   ·   w = (δΣ)⁻¹μ: a carteira",
                                      MUTED, F_BODY, 10.5)])
    y2 = YT + 1.5
    kicker(s, L, y2, 5.7, "A previsão (Q)")
    txt(s, L, y2 + 0.45, 5.7, 0.4, [r("Q", GOLD, F_SEMI, 16), r(" = ( E_poly − âncora − viés ) · Σ Pᵢ βᵢ", TEXT, F_SEMI, 16)])
    txt(s, L, y2 + 0.92, 5.7, 0.3, [r("Pᵢ", GOLD, F_SEMI, 12), r(" = 2 (βᵢ − β_SPY) / Σⱼ |βⱼ − β_SPY|", BODY, F_BODY, 12)])
    txt(s, L, y2 + 1.4, 5.7, 1.8, [
        [r("β medido. ", TEXT, F_SEMI), r("Regressão dos retornos nos dias de anúncio contra a surpresa do dia.")],
        [r("P[SPY] = 0 e Σ|P| = 2. ", TEXT, F_SEMI), r("A cesta não aposta na direção da bolsa.")],
        [r("Viés. ", TEXT, F_SEMI), r("A média de que se desconta a surpresa só usa o passado.")]],
        pt=11.5, lsp=1.15, after=6)
    x2 = 6.9
    kicker(s, x2, y2, R - x2, "A confiança (Ω)")
    txt(s, x2, y2 + 0.45, R - x2, 0.4, [r("Ω", GOLD, F_SEMI, 16), r(" = c · diag( P τΣ Pᵀ )", TEXT, F_SEMI, 16)])
    txt(s, x2, y2 + 0.92, R - x2, 0.3, [r("c", GOLD, F_SEMI, 12), r(" = ( (1 + v̄) · (1 + |Σp − 1|) )", BODY, F_BODY, 12),
                                        r("nível", BODY, F_BODY, 9, base=30000),
                                        r("      nível = 1   ·   c ≥ 1", MUTED, F_BODY, 10.5)])
    y3 = y2 + 1.5
    kicker(s, x2, y3, R - x2, "O que entrou na régua")
    txt(s, x2 + 2.6, y3 - 0.02, R - x2 - 2.6, 0.25,
        [r("185 de 2.795 views vetadas por falta de liquidez", MUTED, F_BODY, 9)], align="r")
    pic(s, 7, "grafico_regua", x2, y3 + 0.45, w=R - x2)
    notas(s, 7)


VIEWS = [
    dict(idx=8, aba="2.3 · A decisão do Fed", dias="312", tipo="NEUTRA",
         poly=("Corte esperado na próxima reunião", "média das faixas, em bps"),
         contra=("T-bill 3m − Fed funds", "o corte que os juros já embutem"),
         cesta=("XLU · TLT · TIP", "contra XLK", "sem posição no índice"),
         formula=" = ( E_poly − (T-bill 3m − Fed funds) − média ) · Σ Pᵢ βᵢ",
         legenda="βᵢ: reação de cada ETF ao T-bill nos dias de FOMC   ·   média: só do passado",
         frase=("Confiança mediana c = 1,01. ", "O livro do Fed é o mais estável das quatro.")),
    dict(idx=9, aba="2.2 · A inflação do mês", dias="253", tipo="NEUTRA",
         poly=("Inflação do mês, anualizada", "média das faixas do CPI"),
         contra=("Breakeven de 10 anos", "a inflação que os títulos embutem"),
         cesta=("TIP", "contra TLT", "par casado pela duration"),
         formula=" = D · ( E_poly − breakeven − média ) / dias até o CPI",
         legenda="D: duration do breakeven, medida (8,31 a 8,38)   ·   sem regressão",
         frase=("Limitação declarada. ", "Compara um mês de inflação com dez anos de breakeven.")),
    dict(idx=10, aba="B · A taxa no fim do ano", dias="154", tipo="NEUTRA",
         poly=("Cortes até o fim do ano", "vira taxa de fim de ano"),
         contra=("Treasury de 1 ano", "o prazo da própria pergunta"),
         cesta=("XLE · XLP · XLF", "contra XLU · XLK", "β próprio, contra o Treasury de 1 ano"),
         formula=" = ( E_poly − Treasury 1 ano − média ) · Σ Pᵢ βᵢ",
         legenda="E_poly: Fed funds do fim de 2024 − 25 bps por corte",
         frase=("β próprio. ", "Com o β da view do Fed, as duas views seriam a mesma.")),
    dict(idx=11, aba="15b · A dúvida na véspera", dias="26", tipo="DIRECIONAL",
         poly=("Dúvida na véspera do anúncio", "entropia da distribuição, de 0 a 1"),
         contra=("Média do tipo de anúncio", "Fed, inflação ou emprego"),
         cesta=("SPY", "só o índice", "a única view direcional"),
         formula=" = 2 · β_SPY · ( H − média da família )",
         legenda="H: entropia na véspera   ·   β_SPY: regressão do S&P nos dias de anúncio",
         frase=("Resultado frágil. ", "Sem os três maiores dias, ela vira negativa.")),
]


def s_view(s, k):
    v = VIEWS[k]
    cabecalho(s, "As quatro views", v["aba"])
    # stepper: as quatro views numa linha, a ativa em branco com sublinhado dourado
    pitch = CW / 4
    for i, vv in enumerate(VIEWS):
        on = i == k
        txt(s, L + i * pitch, YT, pitch, 0.3, [r(vv["aba"], TEXT if on else MUTED, F_SEMI if on else F_BODY, 11)],
            align="c", anchor="m", name=f"!!vw_aba{i}")
    luz = rect(s, L + k * pitch + pitch / 2 - 0.6, YT + 0.34, 1.2, 0.03, fill=GOLD, name="!!luz")
    hrule(s, L, YT + 0.42, CW)
    if k > 0:
        deslizar(s, luz, pitch)
    # atividade: nº de pregões e a faixa
    y1 = YT + 0.62
    txt(s, L, y1, 2.2, 0.45, [r(v["dias"], GOLD, F_SEMI, 26), r(" / 374", BODY, F_BODY, 11)], anchor="b")
    txt(s, L, y1 + 0.5, 2.4, 0.2, [r(f"PREGÕES ATIVOS  ·  {v['tipo']}", MUTED, F_SEMI, 7.5, spc=150)])
    pic(s, v["idx"], "!!vw_faixa", 2.95, y1 + 0.02, w=R - 2.95, nome="!!vw_faixa")
    # a view em três termos: polymarket − contra × β cesta
    y2 = YT + 1.6
    cols = [("Polymarket", v["poly"][0], None, v["poly"][1]),
            ("Contra", v["contra"][0], None, v["contra"][1]),
            ("Cesta", v["cesta"][0], v["cesta"][1], v["cesta"][2])]
    xs = [L, L + 4.2, L + 8.4]
    for i, (kk, a, b, c) in enumerate(cols):
        x = xs[i]
        kicker(s, x, y2, 3.6, kk)
        paras = [[r(a, TEXT, F_SEMI, 15)]]
        if b:
            paras.append([r(b, BODY, F_BODY, 12)])
        paras.append([r(c, MUTED, F_BODY, 10.5)])
        txt(s, x, y2 + 0.45, 3.6, 1.3, paras, lsp=1.1, after=3)
    for x, op in ((L + 3.65, "−"), (L + 7.8, "× β")):
        txt(s, x, y2 + 0.45, 0.6, 0.6, [r(op, GOLD, F_SEMI, 16)], align="c", anchor="m")
    # a conta
    y3 = YT + 3.35
    kicker(s, L, y3, CW, "A conta")
    txt(s, L, y3 + 0.42, CW, 0.4, [r("Q", GOLD, F_SEMI, 17), r(v["formula"], TEXT, F_SEMI, 17)])
    txt(s, L, y3 + 0.88, CW, 0.25, [r(v["legenda"], MUTED, F_BODY, 10.5)])
    takeaway(s, 6.0, [r(v["frase"][0], TEXT, F_SEMI), r(v["frase"][1], BODY, F_BODY)], h=0.55)
    notas(s, v["idx"])


def s12_tatica(s):
    cabecalho(s, "A camada tática", "O movimento da probabilidade vira um spread setorial")
    passos = [("O sinal", "Δp em k pregões",
               "Quanto a probabilidade andou em k pregões. A direção é o sinal desse Δp."),
              ("O livro", "XLP⊥  ×  XLK⊥",
               "Spread setorial com o beta de mercado removido das duas pernas. O hedge vira posição em SPY."),
              ("O μ", "média(direção × drift)",
               "Retorno médio nos dias após os eventos passados, menos a linha de base. Poucos eventos pedem menos tamanho."),
              ("O tamanho", "dw = inv(δΣ) · μ",
               "Usa o δ e o τ do Black-Litterman. Nenhum parâmetro novo.")]
    pitch = CW / 4
    for i, (k, a, b) in enumerate(passos):
        x = L + i * pitch
        badge(s, x + 0.14, YT + 0.13, i + 1)
        txt(s, x + 0.45, YT, pitch - 0.6, 0.25, [r(caps(k), GOLD, F_SEMI, 8.5, spc=200)], anchor="m")
        txt(s, x + 0.45, YT + 0.32, pitch - 0.6, 0.3, [r(a, TEXT, F_SEMI, 13)])
        txt(s, x + 0.45, YT + 0.68, pitch - 0.6, 1.0, [r(b, BODY, F_BODY, 10)], lsp=1.12)
    y2 = YT + 1.75
    hrule(s, L, y2 - 0.15, CW)
    # coluna A: as duas sleeves + dois números
    kicker(s, L, y2, 4.2, "As duas sleeves")
    txt(s, L, y2 + 0.45, 4.2, 1.0, [
        [r("Recessão nos EUA. ", TEXT, F_SEMI), r("Lida em 3, 5 e 10 pregões, com peso igual.")],
        [r("Maioria na Câmara. ", TEXT, F_SEMI), r("O mesmo livro, lido em 20 pregões.")]],
        pt=11.5, lsp=1.12, after=4)
    txt(s, L, y2 + 1.45, 4.2, 0.2, [r("Sobe a chance de recessão: compra XLP, vende XLK.", MUTED, F_BODY, 9)])
    bignum(s, L, y2 + 1.85, 2.0, "+42,6 pp", "Sozinha, sem teto", pt=24)
    bignum(s, L + 2.1, y2 + 1.85, 2.0, "–2,94 pp", "Dentro da carteira", pt=24)
    txt(s, L, y2 + 2.85, 4.2, 0.2, [r("8 de 10 candidatas foram reprovadas antes destas duas entrarem.", FOOT, F_BODY, 8, i=True)])
    vrule(s, 4.95, y2, 3.1)
    # coluna B: gráfico de abril
    xb, wb = 5.15, 4.5
    kicker(s, xb, y2, wb, "Abril de 2025  ·  o que ela leu")
    pic(s, 12, "grafico_recessao", xb, y2 + 0.45, w=wb)
    txt(s, xb, y2 + 2.65, wb, 0.5, [r("De "), r("38% para 66%", TEXT, F_SEMI), r(" em sete pregões, nas três leituras.")],
        pt=11.5)
    vrule(s, 9.85, y2, 3.1)
    # coluna C: o que ela fez
    xc, wc = 10.05, R - 10.05
    kicker(s, xc, y2, wc, "O que ela fez")
    for j, (tk, num, desc) in enumerate((("XLK", "−0,54", "vende tecnologia"), ("SPY", "+0,58", "a ponta de hedge"))):
        y = y2 + 0.45 + j * 0.6
        txt(s, xc, y, 0.7, 0.3, [r(tk, MUTED, F_MONO, 10)], anchor="m")
        txt(s, xc + 0.7, y, wc - 0.7, 0.3, [r(num, TEXT, F_SEMI, 14)], anchor="m")
        txt(s, xc, y + 0.28, wc, 0.2, [r(desc, MUTED, F_BODY, 9)])
    hrule(s, xc, y2 + 1.68, wc)
    txt(s, xc, y2 + 1.78, wc, 0.2, [r("03/04/2025", MUTED, F_SEMI, 7.5, spc=150)])
    txt(s, xc, y2 + 1.98, wc, 0.45, [r("+0,85%", TEXT, F_SEMI, 24)])
    txt(s, xc, y2 + 2.45, wc, 0.4, [r("no dia em que o S&P caiu "), r("−4,9%", TEXT, F_SEMI)], pt=10)
    txt(s, xc, y2 + 2.85, wc, 0.2, [r("No repique de 09/04 ela devolveu 1,5%.", FOOT, F_BODY, 8, i=True)])
    notas(s, 12)


def s13_teto(s):
    cabecalho(s, "A estratégia e o teto de risco", "Views e camada tática passam pelo mesmo teto de risco")
    yc = 4.0                                               # eixo do fluxo
    # 1 · Polymarket
    badge(s, L + 0.14, yc - 0.75, 1)
    txt(s, L + 0.5, yc - 0.87, 1.7, 0.25, [r("POLYMARKET", GOLD, F_SEMI, 8.5, spc=200)], anchor="m")
    txt(s, L + 0.5, yc - 0.45, 1.8, 1.0, [r("a probabilidade de cada evento", TEXT, F_SEMI, 14)], lsp=1.1)
    # 2 · estrutural / 3 · tática
    xb, wb = 3.25, 4.75
    camadas = [(2, yc - 2.05, "Camada estrutural  ·  lê o nível",
                "2.3 Fed   ·   2.2 Inflação   ·   B Fim do ano   ·   15b Véspera",
                [r("Q e Ω", TEXT, F_SEMI, 13), r("    →    ", GOLD, F_SEMI, 13), r("Black-Litterman", TEXT, F_SEMI, 13)]),
               (3, yc + 0.75, "Camada tática  ·  lê o movimento",
                "Recessão   ·   Câmara",
                [r("Δp em k pregões", TEXT, F_SEMI, 13), r("    →    ", GOLD, F_SEMI, 13), r("spread XLP × XLK", TEXT, F_SEMI, 13)])]
    for n, y, k, itens, conta in camadas:
        badge(s, xb + 0.14, y + 0.13, n)
        txt(s, xb + 0.45, y, wb - 0.45, 0.25, [r(caps(k), GOLD, F_SEMI, 8.5, spc=200)], anchor="m")
        hrule(s, xb, y + 0.36, wb)
        txt(s, xb, y + 0.5, wb, 0.3, [r(itens, BODY, F_BODY, 12)])
        txt(s, xb, y + 0.92, wb, 0.35, conta)
        arrow(s, L + 2.4, yc, xb - 0.12, y + 0.65, lw=1.0)
    # 4 · teto de risco — a única caixa do slide
    xt, wt, ht = 8.7, 2.35, 1.8
    rect(s, xt, yc - ht / 2, wt, ht, line=GOLD, lw=1.0, dash=True)
    badge(s, xt + 0.16, yc - ht / 2 + 0.2, 4, d=0.26)
    txt(s, xt + 0.45, yc - ht / 2 + 0.08, wt - 0.5, 0.25, [r("TETO DE RISCO", GOLD, F_SEMI, 8.5, spc=200)], anchor="m")
    txt(s, xt + 0.22, yc - 0.3, wt - 0.4, 0.45, [r("Σ|w − w_mkt| ≤ 1", TEXT, F_SEMI, 16)])
    txt(s, xt + 0.22, yc + 0.2, wt - 0.4, 0.55, [r("tudo encolhe na mesma proporção", MUTED, F_BODY, 10.5)], lsp=1.1)
    for _, y, *_ in camadas:
        arrow(s, xb + wb + 0.12, y + 0.65, xt - 0.12, yc, lw=1.0)
    # 5 · carteira
    xc = 11.4
    arrow(s, xt + wt + 0.12, yc, xc - 0.12, yc, lw=1.0)
    badge(s, xc + 0.14, yc - 0.75, 5)
    txt(s, xc + 0.45, yc - 0.87, R - xc - 0.45, 0.25, [r("CARTEIRA", GOLD, F_SEMI, 8.5, spc=200)], anchor="m")
    txt(s, xc, yc - 0.45, R - xc, 0.9, [r("9 ETFs, os pesos do dia", TEXT, F_SEMI, 14)], lsp=1.1)
    notas(s, 13)


def s14_backtest(s):
    cabecalho(s, "Backtest e resultados", "+3,0 pp sobre o SPY, ao mesmo risco")
    wl = 3.3
    kicker(s, L, YT, wl, "O placar")
    placar = [("Retorno líquido", "+33,2%", "SPY +30,1%"), ("Sharpe", "1,18", "SPY 1,08"),
              ("Volatilidade", "17,6%", "SPY 17,9%"), ("Máx. queda", "–19,6%", "SPY −18,8%")]
    for i, (k, n, sp) in enumerate(placar):
        x = L + (i % 2) * (wl / 2)
        y = YT + 0.45 + (i // 2) * 0.95
        txt(s, x, y, wl / 2, 0.2, [r(k.upper(), MUTED, F_SEMI, 7.5, spc=150)])
        txt(s, x, y + 0.2, wl / 2, 0.45, [r(n, TEXT, F_SEMI, 24)])
        txt(s, x, y + 0.66, wl / 2, 0.2, [r(sp, MUTED, F_BODY, 8.5)])
        if i % 2 == 1:
            hrule(s, L, y + 0.9, wl)
    txt(s, L, YT + 2.38, wl, 0.2, [r("placar completo no apêndice A8", FOOT, F_BODY, 8, i=True)])
    y2 = YT + 2.7
    kicker(s, L, y2, wl, "De onde vem o resultado")
    pic(s, 14, "Picture 46", L, y2 + 0.42, w=2.9)
    txt(s, L, y2 + 2.38, wl, 0.6, [
        [r("Soma dos retornos diários, não capitalização", BODY, F_BODY, 7.5), r(" — daí +30,9 pp aqui e +33,2% na curva.", MUTED, F_BODY, 7.5)],
        [r("E sem juros: ", BODY, F_BODY, 7.5), r("o caixa não é remunerado e o Sharpe usa taxa livre de risco zero, igual para Kairos e SPY.", MUTED, F_BODY, 7.5)]])
    vrule(s, L + wl + 0.35, YT, 5.5)
    xg = L + wl + 0.7
    kicker(s, xg, YT, R - xg, "Curva acumulada e drawdown")
    txt(s, xg + 3.5, YT - 0.02, R - xg - 3.5, 0.25, [r("374 pregões · 10/02/2025 a 06/08/2026 · líquido de custo", MUTED, F_BODY, 8.5)], align="r")
    pic(s, 14, "Picture 50", xg, YT + 0.45, w=R - xg)
    notas(s, 14)


def s15_critica(s):
    cabecalho(s, "Análise crítica", "Três números, uma leitura: positiva, defensiva — e ainda não provada")
    cols = [("A prova exige tempo", "457", "pregões de track record mínimo a 95 %  ·  temos 374",
             "O excesso é positivo em toda leitura, mas ainda não é prova de habilidade. Faltam 83 pregões — "
             "o próximo semestre é o teste fora da amostra, pré-registrado antes de ser visto.",
             "PSR 93% · IC95 do excesso [−12,9; 20,6] pp · alpha t = 0,6 contra a régua de 3 (Harvey–Liu)"),
            ("Onde o ganho mora", "+6,2 bps", "por dia de queda do SPY  ·  –3,9 nos de alta",
             "Perde menos quando o mercado cai, ganha menos quando sobe: é um tilt defensivo sobre beta 0,95, "
             "não proteção de cauda — no tombo de abril caiu mais fundo que o índice, e na 2ª metade, só de alta, ficou atrás.",
             "hit 52% nos dias de queda, 43% nos de alta · metades +3,3 / –0,6 pp · máx. queda –19,6 % × SPY –18,8 %"),
            ("Pelo protocolo da literatura", "3 de 7", "pontos de Arnott, Harvey & Markowitz fechados",
             "Rigor onde depende de nós: hipótese antes do teste, dados sem look-ahead, admissão por mecanismo. "
             "Parcial onde o desenho limita: testes múltiplos, Ω diagonal. Aberto onde só o tempo resolve: validação fora da amostra.",
             "fechados: motivação · dados · cultura  —  parciais: testes múltiplos · dinâmica · complexidade  —  aberto: fora da amostra")]
    pitch = CW / 3
    for i, (k, num, lab, corpo, nota) in enumerate(cols):
        x = L + i * pitch
        w = pitch - 0.4
        kicker(s, x, YT, w, k)
        txt(s, x, YT + 0.4, w, 0.75, [r(num, TEXT, F_SEMI, 40)], anchor="m")
        txt(s, x, YT + 1.2, w, 0.4, [r(lab.upper(), MUTED, F_SEMI, 7.5, spc=100)], lsp=1.1)
        txt(s, x, YT + 1.7, w, 1.9, [r(corpo, BODY, F_BODY, 11)], lsp=1.15)
        txt(s, x, YT + 3.65, w, 0.6, [r(nota, MUTED, F_BODY, 8.5)], lsp=1.1)
        if i:
            vrule(s, x - 0.2, YT, 4.3)
    y2 = 5.85
    kicker(s, L, y2, CW, "Faríamos diferente")
    txt(s, L, y2 + 0.4, CW, 0.25, [r("Pré-registrar o próximo semestre como teste fora da amostra · corrigir a busca "
                                     "tática pelo nº de tentativas (DSR) · um Ω que enxergue a correlação entre views.",
                                     BODY, F_BODY, 10.5)])
    fonte(s, "Arnott, Harvey & Markowitz (2019) · Bailey & López de Prado (2012, 2014) · Harvey & Liu (2015)  ·  "
             "Final/analise/Pesquisa_avaliacao_estrategia.md  ·  apêndice A9", y=6.68)
    notas(s, 15)


def s_ia(s, idx):
    """Setup de IA (originais 17–29): grafo + overlay Morph copiado e transladado."""
    cabecalho(s, "Setup de IA", "O segundo cérebro")
    o = ORIG.slides[idx - 1]
    g = shape_orig(idx, "!!grafo")
    gw = g.width / 914400
    gp = pic(s, idx, "!!grafo", L, YT, w=gw, nome="!!grafo")
    dx, dy = gp.left - g.left, gp.top - g.top
    tree = s.shapes._spTree
    nid = max(int(e.get("id")) for e in tree.iter(qn("p:cNvPr"))) + 1
    for sh in o.shapes:
        if sh.name == "!!veu" or sh.name.startswith(("!!n_", "!!e_", "!!pulso")):
            el = copy.deepcopy(sh._element)
            off = el.find(".//" + qn("a:off"))
            off.set("x", str(int(off.get("x")) + dx))
            off.set("y", str(int(off.get("y")) + dy))
            el.find(".//" + qn("p:cNvPr")).set("id", str(nid))
            nid += 1
            for c in el.iter(qn("a:srgbClr")):
                if c.get("val") == "04070E":
                    c.set("val", BG)
            tree.append(el)
    txt(s, L, YT + gw + 0.06, gw, 0.2, [r("209 arquivos  ·  719 ligações  ·  medido no branch por grafo_repo.py",
                                          FOOT, F_MONO, 7.5)], align="c", name="!!grafo_leg")
    x2 = 6.45
    w2 = R - x2
    kicker(s, x2, YT, w2, "O setup")
    txt(s, x2, YT + 0.42, w2, 1.3, [
        [r("CLAUDE.md. ", TEXT, F_SEMI), r("Regras e papéis, lidos no começo de toda sessão.")],
        [r("Ritual de fim. ", TEXT, F_SEMI), r("Toda sessão fecha escrevendo no LOG e nas decisões pendentes.")],
        [r("Pesquisa vira arquivo. ", TEXT, F_SEMI), r("E cita os arquivos que usou — foi isso que virou o grafo.")]],
        pt=11.5, lsp=1.12, after=4)
    y3 = YT + 1.75
    kicker(s, x2, y3, w2, "Prompt exemplo")
    rect(s, x2, y3 + 0.42, 0.04, 0.95, fill=GOLD)
    txt(s, x2 + 0.22, y3 + 0.42, w2 - 0.22, 0.95,
        [r("“Preciso montar um draft inicial das minhas falas da final. Vou começar pela explicação da "
           "aplicação do Black Litterman na estratégia. Leia o repositório e o código para montar uma "
           "explicação para eu me embasar”", BODY, F_SERIF, 11.5, i=True)], lsp=1.15, anchor="m")
    y4 = y3 + 1.6
    kicker(s, x2, y4, w2, "O que acendeu, na ordem")
    itens = [sh for sh in o.shapes if sh.name.startswith("!!li_")]
    itens.sort(key=lambda sh: int(sh.name.split("_")[1]))
    cor = {"FFB531": GOLD, "2FD3B0": TEAL, "4F8EF7": BLUE}
    for sh in itens:
        k = int(sh.name.split("_")[1])
        runs = sh.text_frame.paragraphs[0].runs
        c = cor.get(str(runs[1].font.color.rgb), BODY)
        txt(s, x2 + (k // 6) * 3.15, y4 + 0.42 + (k % 6) * 0.235, 3.1, 0.22,
            [r(runs[0].text, FOOT, F_MONO, 8.5), r(runs[1].text, c, F_MONO, 9)], anchor="m",
            name=sh.name)
    if idx == 17:
        txt(s, x2, y4 + 0.42, w2, 0.22, [r("clique para ver o caminho", FOOT, F_MONO, 9)], anchor="m")
    if idx == 29:
        txt(s, x2, y4 + 1.9, w2, 0.25, [r("23 comandos · 11 arquivos · ", TEXT, F_MONO, 9, b=True),
                                        r("contrato  →  análise  →  código  →  dado", GOLD, F_MONO, 9, b=True)])
    copiar_transicao(s, idx)
    notas(s, idx)


def s30_ia_numeros(s):
    cabecalho(s, "IA em números", "Medimos o uso de IA como medimos a estratégia: pelo registro.")
    kpis = [("91", "Sessões de IA", "Felipe 55 · Lia 18 · Paulo 18"),
            ("232k", "Tokens por sessão", "média · 19,7M no total"),
            ("81", "Decisões registradas", "escaladas ao humano"),
            ("37%", "Taxa de recorreção", "pediram 2ª rodada")]
    pitch = CW / 4
    for i, (n, k, sub) in enumerate(kpis):
        x = L + i * pitch
        bignum(s, x, YT, pitch - 0.3, n, k, sub, pt=30)
        if i:
            vrule(s, x - 0.25, YT + 0.05, 1.05)
    hrule(s, L, YT + 1.3, CW)
    y2 = YT + 1.5
    kicker(s, L, y2, 6.6, "145 erros da IA  ·  quem pegou")
    pic(s, 30, "s13_12", L, y2 + 0.45, w=6.6)
    x2 = 7.5
    kicker(s, x2, y2, R - x2, "Onde foi o esforço")
    pic(s, 30, "s13_14", x2, y2 + 0.45, w=R - x2)
    notas(s, 30)


def s31_resposta(s):
    cabecalho(s, "Resposta da hipótese")
    txt(s, L, 1.95, 11.6, 0.9, [r("Resposta da hipótese", TEXT, F_SEMI, 44)], anchor="m")
    kicker(s, L, 3.2, 4, "A hipótese, do slide 2", rule=False)
    txt(s, L, 3.55, 10.8, 1.1, [r("“Mercados de previsão antecipam o mercado financeiro. ", BODY, F_SEMI, 22),
                                r("Esse é o nosso sinal.”", GOLD, F_SEMI, 22)], lsp=1.1)
    txt(s, L, 4.85, 11.6, 0.35, [r("O que 150 contratos do Polymarket, 30 eventos e 1416 leituras dizem.", MUTED, F_BODY, 14)])
    notas(s, 31)


def s32_fonte_dados(s):
    cabecalho(s, "O Polymarket como fonte de dados", "Calibrado e mais preciso que o mercado de juros.")
    obs = [(L, 5.8, "Observação 1  ·  calibração", "Quando o Polymarket diz X %, acontece X % das vezes.",
            "0,043", "Brier na véspera", "IC95 [0,022; 0,067]", "s16_16"),
           (6.9, R - 6.9, "Observação 2  ·  decisão do Fed",
            "Na decisão do Fed, o Polymarket erra 0,9 bps; o mercado de juros, 4,8.",
            "0,9 × 4,8", "bps de erro na véspera", "Polymarket × futuro de FF", "s16_22")]
    for x, w, k, frase, num, lab, sub, img in obs:
        kicker(s, x, YT, w, k)
        txt(s, x, YT + 0.4, w, 0.55, [r(frase, TEXT, F_SEMI, 13)], lsp=1.1)
        txt(s, x, YT + 1.0, 2.1, 0.55, [r(num, GOLD, F_SEMI, 30)], anchor="m")
        txt(s, x + 2.2, YT + 1.05, w - 2.2, 0.2, [r(lab.upper(), MUTED, F_SEMI, 7.5, spc=150)])
        txt(s, x + 2.2, YT + 1.28, w - 2.2, 0.22, [r(sub, BODY, F_BODY, 9)])
        pic(s, 32, img, x, YT + 1.65, w=w - 0.3)
    takeaway(s, 6.05, [r("É uma probabilidade confiável — e melhor que os juros no que os dois precificam. ", TEXT, F_SEMI),
                       r("Por isso ela é a opinião do Black-Litterman.", GOLD, F_SEMI)], h=0.5)
    fonte(s, "150 contratos do Polymarket (Fed e CPI) · 30 eventos · 1416 leituras em 11 horizontes · "
             "resolução no FRED · apêndice A1–A3")
    notas(s, 32)


def s33_fechamento(s):
    capa_base(s, "A opinião vem de quem tem dinheiro em risco. A medida vem do Black-Litterman.",
              [r("Kairós", GOLD, F_SERIF, 15, b=True, i=True),
               r(": a carteira só se move quando a probabilidade se move. Obrigado pela oportunidade.",
                 BODY, F_SERIF, 15, i=True)], 33)
    notas(s, 33)


# --------------------------------------------------------------- montagem
SLIDES = ([s01_capa, s02_hipotese, s03_polymarket, s04_comparacao, s05_ficha, s06_bl, s07_q_omega]
          + [lambda s, k=k: s_view(s, k) for k in range(4)]
          + [s12_tatica, s13_teto, s14_backtest, s15_critica]
          + [lambda s, i=i: s_ia(s, i) for i in range(17, 30)]
          + [s30_ia_numeros, s31_resposta, s32_fonte_dados, s33_fechamento])
SEM_NAV = {1, len(SLIDES)}                 # capa e fechamento têm rodapé próprio


def montar():
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(W), Inches(H)
    for i, fn in enumerate(SLIDES, 1):
        s = novo_slide(prs)
        fn(s)
        if i not in SEM_NAV:
            rodape(s, i, len(SLIDES))
    prs.save(SAIDA)
    return len(SLIDES)


def render(arquivo, pasta):
    pasta.mkdir(parents=True, exist_ok=True)
    ps = (f"$app = New-Object -ComObject PowerPoint.Application; "
          f"$p = $app.Presentations.Open('{arquivo}', $true, $false, $false); "
          f"for ($i=1; $i -le $p.Slides.Count; $i++) {{ $p.Slides.Item($i).Export("
          f"('{str(pasta).replace(chr(92), '/')}/s{{0:d2}}.png' -f $i).Replace('/','\\'), 'PNG', 1280, 720) }}; "
          f"$p.Close(); $app.Quit()")
    subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True)


if __name__ == "__main__":
    n = montar()
    print("ok", SAIDA.relative_to(RAIZ), f"({n} slides)")
    if "--render" in sys.argv:
        pasta = Path(os.environ.get("RENDER_DIR", RAIZ / "Final" / "render_t7"))
        render(SAIDA, pasta)
        print("PNG em", pasta)
