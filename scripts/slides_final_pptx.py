"""Slides novos da final — 3 (Polymarket), 4 (comparação) e 12 (second brain).

Gera `Final/Slides_novos.pptx` com três grupos, no estilo restilizado do deck da
semifinal (fundo radial, Bahnschrift + Consolas, cards em degradê, número
fantasma, halos de canto). Os slides entram no deck da final por copiar/colar
no PowerPoint com "manter formatação de origem".

  3  · como funciona o Polymarket: o card de um mercado real (o Fed de
       setembro/2025) e a probabilidade de cada desfecho andando até virar 0 ou 1.
  4  · o mesmo dia, duas previsões: para cada ETF, o retorno esperado no dia do
       anúncio segundo o MERCADO (π) e segundo o POLYMARKET (π + β·surpresa).
       Dois slides com Morph — véspera de 27/01/2026 (concordam) e véspera de
       16/09/2025 (divergem). Dado de `comparacao_etf_s4.py`.
  12 · o second brain acendendo: o grafo do repositório (`grafo_repo.py`) e o
       caminho REAL que um prompt percorreu, medido no transcript da sessão por
       `trace_sessao.py`. Uma sequência de slides Morph com avanço automático:
       um clique dispara o caminho inteiro.
  13 · IA em números: os quatro indicadores e os gráficos da página 5 do
       relatório (`Uteis/graficos/p5_*.png`, de `graficos_p5.py`) — linha do
       tempo de contexto × decisões, erros × quem pegou, esforço por tipo — e a
       peneira 31 → 7 do slide 8 da semi. Texto só nos kickers.

Como o Morph casa as formas: nome com prefixo `!!` = mesmo objeto entre slides
(anda, muda de cor, muda de tamanho); todo o resto ganha nome único do slide
(`sela`) para o PowerPoint não casar duas caixas sem relação. Requer PowerPoint
2016+/365; em outros leitores a transição cai no `<mc:Fallback>` e vira fade.

Uso:

    python scripts/slides_final_pptx.py             # gera o deck
    python scripts/slides_final_pptx.py --render    # e exporta PNG via PowerPoint
    python scripts/slides_final_pptx.py --demo      # auto-teste
"""

import json
import sys
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml import parse_xml
from pptx.oxml.ns import nsdecls
from pptx.util import Emu, Inches, Pt

matplotlib.use("Agg")
import matplotlib.dates as mdates          # noqa: E402
import matplotlib.pyplot as plt            # noqa: E402

import grafo_repo                          # noqa: E402
import graficos_p5                         # noqa: E402
from slide8_pesquisa_pptx import GRUPOS    # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "Final" / "Slides_novos.pptx"
GRAFICOS = RAIZ / "Uteis" / "graficos"
DADOS = RAIZ / "Uteis" / "dados"
FED_PARQUET = RAIZ / "data" / "polymarket_fed_reunioes.parquet"

# ------------------------------------------------------------------ paleta
# Lida do XML do deck restilizado (Semis/KAIROS_semifinal.pptx, sessão 44).
ORANGE = RGBColor(0xFF, 0xB5, 0x31)
BLUE = RGBColor(0x4F, 0x8E, 0xF7)
MINT = RGBColor(0x2F, 0xD3, 0xB0)
TEXT = RGBColor(0xF5, 0xF7, 0xFB)
BODY = RGBColor(0xBA, 0xC6, 0xDA)
MUTED = RGBColor(0x83, 0x95, 0xB5)
FOOT = RGBColor(0x58, 0x69, 0x8A)
RULE = RGBColor(0x2A, 0x3F, 0x63)
GHOST = RGBColor(0x10, 0x1A, 0x2E)
ESCURO = RGBColor(0x0A, 0x13, 0x25)     # texto sobre fatia clara
CARD_A, CARD_B = "182946", "0F182B"       # degradê do card
BORDA_A, BORDA_B = "35507A", "22345A"     # degradê da borda

COND = "Bahnschrift SemiBold Condensed"
SEMI = "Bahnschrift SemiBold"
LIGHT = "Bahnschrift SemiLight"
BAHN = "Bahnschrift"
MONO = "Consolas"
SERIF = "Georgia"

L, R = 0.80, 12.53                        # margens do deck restilizado
Y_TITULO = 0.93
PE = 7.167                                # régua do rodapé

FAMILIA_COR = {"contrato": ORANGE, "analise": MINT, "codigo": BLUE,
               "entrega": MUTED}
FAMILIA_ROT = {"contrato": "contrato", "analise": "análise", "codigo": "código",
               "entrega": "entrega"}

A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"


# --------------------------------------------------------------- primitivas
def hexa(cor):
    return f"{cor[0]:02X}{cor[1]:02X}{cor[2]:02X}"


def alpha(sh, val):
    """Transparência num preenchimento sólido (val em milésimos de %)."""
    sh.fill.fore_color._xFill.find(A + "srgbClr").append(
        parse_xml(f'<a:alpha {nsdecls("a")} val="{val}"/>'))


def efeito(sh, xml):
    sh.shadow.inherit = False
    sp = sh._element.spPr
    velho = sp.find(A + "effectLst")
    if velho is not None:
        sp.remove(velho)
    sp.append(parse_xml(f'<a:effectLst {nsdecls("a")}>{xml}</a:effectLst>'))


def brilho(cor, rad=90000, alfa=40000):
    return (f'<a:glow rad="{rad}"><a:srgbClr val="{hexa(cor)}">'
            f'<a:alpha val="{alfa}"/></a:srgbClr></a:glow>')


def caixa(slide, x, y, w, h, anchor=MSO_ANCHOR.TOP, wrap=True):
    sh = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = sh.text_frame
    tf.word_wrap = wrap
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    return sh


def paragrafo(tf, runs, alinha=PP_ALIGN.LEFT, primeiro=False, entre=1.0,
              depois=0.0, antes=0.0):
    """Um parágrafo; `runs` = [(texto, fonte, pt, cor, negrito, spc, itálico)]."""
    p = tf.paragraphs[0] if primeiro else tf.add_paragraph()
    p.alignment = alinha
    p.line_spacing = entre
    p.space_after = Pt(depois)
    p.space_before = Pt(antes)
    for texto, fonte, pt, cor, *resto in runs:
        negrito = resto[0] if len(resto) > 0 else False
        spc = resto[1] if len(resto) > 1 else 0
        italico = resto[2] if len(resto) > 2 else False
        r = p.add_run()
        r.text = texto
        f = r.font
        f.name, f.size, f.bold, f.italic = fonte, Pt(pt), negrito, italico
        f.color.rgb = cor
        if spc:
            r._r.get_or_add_rPr().set("spc", str(spc))
    return p


def texto(slide, x, y, w, h, runs, alinha=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
          entre=1.0, wrap=True):
    sh = caixa(slide, x, y, w, h, anchor, wrap)
    paragrafo(sh.text_frame, runs, alinha, primeiro=True, entre=entre)
    return sh


def kicker(slide, x, y, w, rotulo, cor=ORANGE):
    return texto(slide, x, y, w, 0.2, [(rotulo, MONO, 9, cor, True, 180)])


def card(slide, x, y, w, h, raio=4000):
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x),
                                Inches(y), Inches(w), Inches(h))
    sp = sh._element.spPr
    for tag in ("solidFill", "ln", "prstGeom"):
        el = sp.find(A + tag)
        if el is not None:
            sp.remove(el)
    sp.append(parse_xml(
        f'<a:prstGeom {nsdecls("a")} prst="roundRect"><a:avLst>'
        f'<a:gd name="adj" fmla="val {raio}"/></a:avLst></a:prstGeom>'))
    sp.append(parse_xml(
        f'<a:gradFill {nsdecls("a")} rotWithShape="1"><a:gsLst>'
        f'<a:gs pos="0"><a:srgbClr val="{CARD_A}"/></a:gs>'
        f'<a:gs pos="100000"><a:srgbClr val="{CARD_B}"/></a:gs></a:gsLst>'
        '<a:lin ang="5400000" scaled="0"/></a:gradFill>'))
    sp.append(parse_xml(
        f'<a:ln {nsdecls("a")} w="9525"><a:gradFill rotWithShape="1"><a:gsLst>'
        f'<a:gs pos="0"><a:srgbClr val="{BORDA_A}"/></a:gs>'
        f'<a:gs pos="100000"><a:srgbClr val="{BORDA_B}"/></a:gs></a:gsLst>'
        '<a:lin ang="5400000" scaled="0"/></a:gradFill></a:ln>'))
    efeito(sh, "")
    sh.text_frame.text = ""
    return sh


def fio(slide, x1, y1, x2, y2, cor=RULE, pt=0.75, alfa=None):
    ln = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1),
                                    Inches(y1), Inches(x2), Inches(y2))
    ln.line.color.rgb = cor
    ln.line.width = Pt(pt)
    if alfa is not None:
        ln.line.color._xFill.find(A + "srgbClr").append(
            parse_xml(f'<a:alpha {nsdecls("a")} val="{alfa}"/>'))
    return ln


def regua_dourada(slide, x1, y, x2):
    """A régua do cabeçalho: dourado que some para a direita."""
    ln = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1),
                                    Inches(y), Inches(x2), Inches(y))
    sp = ln._element.spPr
    for el in sp.findall(A + "ln"):
        sp.remove(el)
    sp.append(parse_xml(
        f'<a:ln {nsdecls("a")} w="12700"><a:gradFill rotWithShape="1"><a:gsLst>'
        f'<a:gs pos="0"><a:srgbClr val="{hexa(ORANGE)}"/></a:gs>'
        f'<a:gs pos="30000"><a:srgbClr val="{hexa(RULE)}"/></a:gs>'
        f'<a:gs pos="100000"><a:srgbClr val="{hexa(RULE)}"><a:alpha val="30000"/>'
        '</a:srgbClr></a:gs></a:gsLst><a:lin ang="0" scaled="0"/></a:gradFill></a:ln>'))
    return ln


def ponto(slide, x, y, d, cor, luz=None, alfa=None):
    """Disco centrado em (x, y) com diâmetro d, opcionalmente aceso."""
    sh = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x - d / 2),
                                Inches(y - d / 2), Inches(d), Inches(d))
    sh.fill.solid()
    sh.fill.fore_color.rgb = cor
    if alfa is not None:
        alpha(sh, alfa)
    sh.line.fill.background()
    efeito(sh, brilho(cor, *luz) if luz else "")
    sh.text_frame.text = ""
    return sh


def halo_canto(slide, nome, x, y, cor, pico):
    """Os halos de canto do deck: elipse com degradê radial que some."""
    sh = slide.shapes.add_shape(MSO_SHAPE.OVAL, Emu(x), Emu(y), Emu(7000000),
                                Emu(5200000))
    sh.name = nome
    sp = sh._element.spPr
    for tag in ("solidFill", "ln"):
        el = sp.find(A + tag)
        if el is not None:
            sp.remove(el)
    paradas = [(0, pico), (45000, pico * 4 // 10), (80000, 1000), (100000, 0)]
    gs = "".join(f'<a:gs pos="{p}"><a:srgbClr val="{hexa(cor)}"><a:alpha val="{a}"/>'
                 '</a:srgbClr></a:gs>' for p, a in paradas)
    sp.append(parse_xml(f'<a:gradFill {nsdecls("a")} rotWithShape="1"><a:gsLst>{gs}'
                        '</a:gsLst><a:path path="circle"><a:fillToRect l="50000" '
                        't="50000" r="50000" b="50000"/></a:path></a:gradFill>'))
    sp.append(parse_xml(f'<a:ln {nsdecls("a")}><a:noFill/></a:ln>'))
    sh.text_frame.text = ""
    return sh


def imagem(slide, caminho, x, y, w, h=None):
    return slide.shapes.add_picture(str(caminho), Inches(x), Inches(y), Inches(w),
                                    None if h is None else Inches(h))


# -------------------------------------------------------------- transições
def morph(slide, dur_ms=600, avanca_ms=None):
    """Morph AO ENTRAR neste slide; `avanca_ms` sai dele sozinho depois disso.

    O python-pptx não tem API de transição; o XML vai direto no `<p:sld>`, no
    lugar que o schema espera (depois de `clrMapOvr`). `advTm` é o avanço
    automático: é ele que faz a sequência do slide 12 tocar com um clique só.
    """
    adv = f' advTm="{avanca_ms}"' if avanca_ms is not None else ""
    slide.element.append(parse_xml(
        '<mc:AlternateContent'
        ' xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"'
        ' xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
        '<mc:Choice Requires="p14"'
        ' xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main">'
        f'<p:transition spd="slow"{adv} p14:dur="{dur_ms}">'
        '<p159:morph option="byObject"'
        ' xmlns:p159="http://schemas.microsoft.com/office/powerpoint/2015/09/main"/>'
        '</p:transition></mc:Choice>'
        f'<mc:Fallback><p:transition spd="fast"{adv}><p:fade/></p:transition>'
        '</mc:Fallback></mc:AlternateContent>'))


def sela(slide, tag):
    for i, sh in enumerate(slide.shapes):
        if not sh.name.startswith("!!"):
            sh.name = f"{tag}_{i}"


# ------------------------------------------------------------------ moldura
def moldura(prs, numero, secao, titulo):
    """Fundo radial, halos, número fantasma, cabeçalho, título e rodapé."""
    s = prs.slides.add_slide(prs.slide_layouts[6])
    cSld = s._element.find("{http://schemas.openxmlformats.org/presentationml/2006/main}cSld")
    cSld.insert(0, parse_xml(
        f'<p:bg {nsdecls("p", "a")}><p:bgPr><a:gradFill rotWithShape="1"><a:gsLst>'
        '<a:gs pos="0"><a:srgbClr val="10203A"/></a:gs>'
        '<a:gs pos="55000"><a:srgbClr val="0A1325"/></a:gs>'
        '<a:gs pos="100000"><a:srgbClr val="04070E"/></a:gs></a:gsLst>'
        '<a:path path="circle"><a:fillToRect l="38000" r="62000" b="100000"/></a:path>'
        '</a:gradFill><a:effectLst/></p:bgPr></p:bg>'))
    halo_canto(s, "!!glow_tl", -2600000, -2200000, BLUE, 10000)
    halo_canto(s, "!!glow_br", 8200000, 4600000, ORANGE, 7000)

    fantasma = texto(s, 7.546, -0.252, 5.413, 2.187, [(numero, COND, 150, GHOST)],
                     alinha=PP_ALIGN.RIGHT, wrap=False)
    fantasma.name = "!!ghost"
    tick = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(603504), Emu(446024),
                              Emu(45720), Emu(164592))
    tick.fill.solid()
    tick.fill.fore_color.rgb = ORANGE
    tick.line.fill.background()
    tick.name = "!!tick"

    texto(s, L, 0.467, 8.0, 0.222, [("KAIROS", MONO, 12, ORANGE, True, 300),
                                    (f"   {secao}", MONO, 11, MUTED, False, 72)],
          anchor=MSO_ANCHOR.MIDDLE)
    texto(s, 0, 0.511, 12.53, 0.167, [(numero, MONO, 9, MUTED, False, 45)],
          alinha=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)
    regua_dourada(s, L, 0.771, R)
    texto(s, L, Y_TITULO, R - L, 0.7, [(titulo, SEMI, 20, TEXT)])

    fio(s, L, PE, R, PE)
    pe = texto(s, L, 7.276, 6.56, 0.175,
               [("ITAÚ QUANT AI CHALLENGE  ·  FINAL 2026", MONO, 7, FOOT, False, 120)],
               wrap=False)
    pe.name = "!!foot_l"
    pd_ = texto(s, 5.968, 7.276, 6.56, 0.175,
                [("BLACK-LITTERMAN  ×  POLYMARKET", MONO, 7, FOOT, False, 120)],
                alinha=PP_ALIGN.RIGHT, wrap=False)
    pd_.name = "!!foot_r"
    return s


# =================================================================== slide 3
def serie_fed_set25():
    """Probabilidade de cada desfecho da reunião de 17/09/2025, pré-abertura."""
    d = pd.read_parquet(FED_PARQUET)
    d = d[d["mercado"].str.contains("September 2025")]
    w = d.pivot_table(index="data", columns="mercado", values="probabilidade")
    volume = d.groupby("mercado")["volume"].first().sum()
    curto = {}
    for c in w.columns:
        if "decreases" in c and "25 bps" in c:
            curto[c] = "corte de 25 bps"
        elif "decreases" in c:
            curto[c] = "corte de 50+ bps"
        elif "increases" in c:
            curto[c] = "alta de 25+ bps"
        else:
            curto[c] = "sem mudança"
    w = w.rename(columns=curto)
    return w[["corte de 25 bps", "sem mudança", "corte de 50+ bps", "alta de 25+ bps"]], volume


CORES_FED = {"corte de 25 bps": ORANGE, "sem mudança": BLUE,
             "corte de 50+ bps": MINT, "alta de 25+ bps": MUTED}
MARCOS = [("2025-07-30", "30/07 · Fed mantém  ", "right"),
          ("2025-08-01", "  01/08 · payroll fraco", "left"),
          ("2025-09-17", "17/09 · corta 25 bps  ", "right")]


def grafico_fed(w, destino):
    """As quatro linhas andando até 0 ou 1 — fundo transparente, tipos do deck."""
    plt.rcParams["font.family"] = [BAHN, "Segoe UI"]
    fig, ax = plt.subplots(figsize=(7.0, 3.55))
    w = w.loc["2025-07-14":"2025-09-17"]
    fim = {}
    for nome, cor in CORES_FED.items():
        s = w[nome].dropna()
        ax.plot(s.index, s.values * 100, color="#" + hexa(cor), lw=2.0 if nome.startswith("corte de 25") else 1.4,
                solid_capstyle="round", zorder=3)
        fim[nome] = (s.index[-1], s.values[-1] * 100)
    # rótulos no fim das linhas, empurrados para não se sobrepor (7 pp de vão)
    y_rot, ultimo = {}, -99.0
    for nome in sorted(fim, key=lambda n: fim[n][1]):
        ultimo = max(fim[nome][1], ultimo + 7.0)
        y_rot[nome] = ultimo
    for nome, cor in CORES_FED.items():
        ax.annotate(nome, fim[nome], xytext=(6, y_rot[nome] - fim[nome][1]),
                    textcoords="offset points", va="center", fontsize=8.5,
                    color="#" + hexa(cor))
    for dia, rot, lado in MARCOS:
        x = pd.Timestamp(dia)
        ax.axvline(x, color="#" + hexa(RULE), lw=0.8, ls=(0, (3, 3)), zorder=1)
        ax.text(x, 104, rot, fontsize=7.5, color="#" + hexa(MUTED), ha=lado,
                va="bottom")
    ax.set_ylim(0, 100)
    ax.set_xlim(w.index.min(), w.index.max() + pd.Timedelta(days=1))
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_yticklabels(["0", "25", "50", "75", "100%"], fontsize=8, color="#" + hexa(MUTED))
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonthday=[1, 15]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
    ax.tick_params(axis="x", labelsize=8, colors="#" + hexa(MUTED), length=0)
    ax.tick_params(axis="y", length=0)
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.spines["bottom"].set_color("#" + hexa(RULE))
    ax.grid(axis="y", color="#" + hexa(RULE), lw=0.5, alpha=0.6)
    ax.set_ylabel("preço do contrato \"Sim\"  (¢ = %)", fontsize=8, color="#" + hexa(MUTED))
    fig.subplots_adjust(0.07, 0.10, 0.86, 0.88)
    destino.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destino, transparent=True, dpi=200)
    plt.close(fig)
    return destino


def s3_polymarket(prs, numero="03"):
    w, volume = serie_fed_set25()
    png = grafico_fed(w, GRAFICOS / "s3_fed_set25.png")
    vespera = w.ffill().loc[:"2025-09-16 12:00"].iloc[-1]

    s = moldura(prs, numero, "Como funciona o Polymarket",
                "Um contrato paga US$ 1 se o evento acontece. O preço é a probabilidade.")

    # --- o "print" do mercado, com os números reais da véspera
    x, y, wc, hc = L, 1.75, 4.55, 3.25
    card(s, x, y, wc, hc)
    kicker(s, x + 0.28, y + 0.22, 4.0, "MERCADO REAL  ·  POLYMARKET")
    texto(s, x + 0.28, y + 0.50, 4.0, 0.4, [("Fed decision in September 2025?", SEMI, 14, TEXT)])
    fio(s, x + 0.28, y + 0.98, x + wc - 0.28, y + 0.98)
    ly = y + 1.10
    for nome in vespera.sort_values(ascending=False).index:
        p = float(vespera[nome])
        cor = ORANGE if nome.startswith("corte de 25") else MUTED
        texto(s, x + 0.28, ly, 2.2, 0.26, [(nome, LIGHT, 11.5, BODY if cor is MUTED else TEXT)],
              anchor=MSO_ANCHOR.MIDDLE)
        texto(s, x + wc - 1.05, ly, 0.77, 0.26, [(f"{round(p * 100):d}¢", MONO, 12, cor, True)],
              alinha=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)
        barra = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x + 0.28),
                                   Inches(ly + 0.30), Inches(max(0.03, 3.99 * p)), Inches(0.05))
        barra.fill.solid()
        barra.fill.fore_color.rgb = cor
        barra.line.fill.background()
        efeito(barra, brilho(ORANGE, 40000, 35000) if cor is ORANGE else "")
        ly += 0.46
    milhoes = f"{volume / 1e6:,.0f}".replace(",", ".")
    texto(s, x + 0.28, y + hc - 0.42, 4.0, 0.2,
          [(f"US$ {milhoes} mi negociados  ·  leitura de 16/09/2025, véspera",
            MONO, 8, MUTED)])

    # --- a probabilidade andando
    kicker(s, 5.75, 1.75, 6.5, "A PROBABILIDADE ANDA ATÉ VIRAR 0 OU 100")
    imagem(s, png, 5.55, 1.98, 6.98)

    # --- faixa de baixo: os dois números do slide 2 e como o Kairós lê
    yb = 5.28
    for i, (num, rot) in enumerate([("90,1%", "de acerto a 1 mês da resolução"),
                                    ("US$ 26,2 bi", "negociados no 1º tri de 2026")]):
        cx = L + i * 2.95
        card(s, cx, yb, 2.72, 1.6)
        texto(s, cx + 0.25, yb + 0.22, 2.3, 0.65, [(num, COND, 30, ORANGE)])
        texto(s, cx + 0.25, yb + 0.95, 2.3, 0.5, [(rot, BAHN, 9.5, BODY)], entre=1.05)
    cx = L + 2 * 2.95
    card(s, cx, yb, R - cx, 1.6)
    kicker(s, cx + 0.28, yb + 0.22, 5.0, "O QUE O KAIROS LÊ")
    tf = caixa(s, cx + 0.28, yb + 0.52, R - cx - 0.56, 1.0).text_frame
    paragrafo(tf, [("O preço de cada desfecho, duas vezes por dia. ", SEMI, 11.5, TEXT),
                   ("Sempre a leitura anterior à abertura da bolsa — nunca a do dia.", LIGHT, 11.5, BODY)],
              primeiro=True, entre=1.12, depois=4)
    paragrafo(tf, [("Quem errar perde dinheiro de verdade. ", SEMI, 11.5, TEXT),
                   ("É o que faz do preço uma opinião com custo, não uma pesquisa.", LIGHT, 11.5, BODY)],
              entre=1.12)
    sela(s, "s3")
    return s


# =================================================================== slide 4
ETFS = [("XLK", "tecnologia"), ("SPY", "S&P 500"), ("XLF", "financeiro"),
        ("XLE", "energia"), ("XLV", "saúde"), ("XLP", "consumo básico"),
        ("TIP", "Treasury · inflação"), ("XLU", "utilities"), ("TLT", "Treasury 20+")]
DIAS_S4 = [("2026-01-27", "concordam"), ("2025-09-16", "divergem")]
EIXO_MIN, EIXO_MAX = -1.8, 0.6            # % — o alcance dos dois dias
X0, X1 = 3.55, 11.95                      # onde o eixo vive no slide
Y0, PASSO = 2.72, 0.42                    # primeira linha e espaçamento


def x_de(valor_pct):
    return X0 + (valor_pct - EIXO_MIN) / (EIXO_MAX - EIXO_MIN) * (X1 - X0)


def fmt_pct(v):
    return f"{v * 100:+.2f}%".replace(".", ",").replace("+", "+ ").replace("-", "− ")


def s4_comparacao(prs, numero="04"):
    d = pd.read_csv(DADOS / "s4_comparacao.csv", index_col=0, parse_dates=True)
    slides = []
    for k, (dia, estado) in enumerate(DIAS_S4):
        r = d.loc[dia]
        if estado == "concordam":
            titulo = "Na maioria dos dias, Polymarket e mercado esperam a mesma coisa."
            lead, resto = ("Surpresa de 0 bps.  ",
                           "Polymarket e juros precificam a mesma decisão — o Kairós não tem opinião e carrega a carteira do mercado.")
        else:
            titulo = "Em alguns, divergem — e é aí que o Kairós age."
            lead, resto = (f"Surpresa de {r['surpresa_liquida']:+.0f} bps.  ",
                           "O Polymarket vê menos corte do que os juros embutem: dinheiro em risco discorda do preço. A conta vira retorno esperado por ETF.")
        s = moldura(prs, numero, "O mesmo dia, duas previsões", titulo)

        # faixa do dia — o card persiste, o texto troca (fade)
        cd = card(s, L, 1.72, R - L, 0.72)
        cd.name = "!!faixa"
        data_br = pd.Timestamp(dia).strftime("%d/%m/%Y")
        texto(s, L + 0.28, 1.86, 3.0, 0.45,
              [("VÉSPERA DO FED", MONO, 9, ORANGE, True, 180),
               (f"   {data_br}", MONO, 9, MUTED, False, 60)], anchor=MSO_ANCHOR.MIDDLE)
        texto(s, L + 3.3, 1.79, R - L - 3.6, 0.6,
              [(lead, SEMI, 11.5, TEXT), (resto, LIGHT, 11.5, BODY)],
              anchor=MSO_ANCHOR.MIDDLE, entre=1.1)

        # eixo
        y_top, y_bot = Y0 - 0.28, Y0 + PASSO * (len(ETFS) - 1) + 0.28
        for v in (-1.5, -1.0, -0.5, 0.0, 0.5):
            x = x_de(v)
            ln = fio(s, x, y_top, x, y_bot, RULE, 1.25 if v == 0 else 0.6,
                     None if v == 0 else 45000)
            ln.name = f"!!grade_{v}"
            t = texto(s, x - 0.5, y_bot + 0.04, 1.0, 0.2,
                      [(f"{v:+.1f}%".replace(".", ",").replace("+0,0", "0,0"), MONO, 8, MUTED)],
                      alinha=PP_ALIGN.CENTER)
            t.name = f"!!tick_{v}"
        t = texto(s, L, y_bot + 0.04, X0 - L - 0.2, 0.2,
                  [("retorno esperado no dia do anúncio  →", MONO, 8, MUTED, False, 60)],
                  wrap=False)
        t.name = "!!eixo_rot"

        # as nove linhas
        for i, (etf, setor) in enumerate(ETFS):
            y = Y0 + i * PASSO
            t = texto(s, L, y - 0.15, 0.7, 0.3, [(etf, MONO, 11.5, TEXT, True)],
                      anchor=MSO_ANCHOR.MIDDLE)
            t.name = f"!!etf_{etf}"
            t = texto(s, L + 0.72, y - 0.15, 2.0, 0.3, [(setor, LIGHT, 9.5, MUTED)],
                      anchor=MSO_ANCHOR.MIDDLE)
            t.name = f"!!setor_{etf}"
            ln = fio(s, X0, y, X1, y, RULE, 0.5, 35000)
            ln.name = f"!!trilho_{etf}"

            pi, poly = float(r[f"pi_{etf}"]), float(r[f"poly_{etf}"])
            xm, xp = x_de(pi * 100), x_de(poly * 100)
            lig = fio(s, xm, y, xp, y, ORANGE, 2.0, 55000)
            lig.name = f"!!lig_{etf}"
            pp = ponto(s, xp, y, 0.19, ORANGE, luz=(70000, 40000))
            pp.name = f"!!pm_{etf}"
            pm = ponto(s, xm, y, 0.13, BLUE, luz=(50000, 30000))
            pm.name = f"!!mk_{etf}"
            esquerda = poly < -0.0015
            t = texto(s, xp - 0.95 if esquerda else xp + 0.17, y - 0.13, 0.8, 0.26,
                      [(fmt_pct(poly), MONO, 9, ORANGE, True)],
                      alinha=PP_ALIGN.RIGHT if esquerda else PP_ALIGN.LEFT,
                      anchor=MSO_ANCHOR.MIDDLE)
            t.name = f"!!val_{etf}"

        # legenda
        yl = 6.66
        ponto(s, X0 + 0.08, yl + 0.1, 0.13, BLUE).name = "!!leg_mk"
        t = texto(s, X0 + 0.24, yl, 3.6, 0.2,
                  [("MERCADO", MONO, 8.5, TEXT, True, 100),
                   ("  o equilíbrio π — o prêmio normal do dia", LIGHT, 9, MUTED)],
                  anchor=MSO_ANCHOR.MIDDLE)
        t.name = "!!leg_mk_t"
        ponto(s, X0 + 4.05, yl + 0.1, 0.15, ORANGE).name = "!!leg_pm"
        t = texto(s, X0 + 4.23, yl, 4.6, 0.2,
                  [("POLYMARKET", MONO, 8.5, TEXT, True, 100),
                   ("  π + β × surpresa — β medido em reuniões passadas", LIGHT, 9, MUTED)],
                  anchor=MSO_ANCHOR.MIDDLE)
        t.name = "!!leg_pm_t"
        t = texto(s, L, 6.93, R - L, 0.2,
                  [("surpresa = o corte que o Polymarket precifica − o que o T-bill de 3 meses embute, "
                    "líquida do viés do instrumento  ·  apêndices A5 e A6", MONO, 7.5, FOOT)])
        t.name = "!!nota"

        # a régua e a nota de rodapé ficam; anotar o dado bruto para a banca
        s.notes_slide.notes_text_frame.text = (
            f"{dia}: E_poly = {r['e_poly_bps']:+.1f} bps · juros (DTB3 − DFF) = {r['e_ff_bps']:+.1f} bps · "
            f"surpresa bruta {r['surpresa_bps']:+.1f} · líquida {r['surpresa_liquida']:+.1f} bps · "
            f"{int(r['dias_ate_evento'])} pregão até a reunião.")
        if k > 0:
            morph(s, 900)
        sela(s, f"s4{'ab'[k]}")
        slides.append(s)
    return slides


# ================================================================== slide 12
GX, GY, GW = 0.62, 1.55, 5.45             # onde o grafo entra no slide
CX = 6.45                                 # a coluna da direita
PASSO_MS = 320                            # dwell entre passos; o Morph dura 550


def grafo_para_slide():
    """(png, posições por nome em polegadas do slide, nº nós, nº arestas)."""
    nomes, familias, arestas = grafo_repo.levantar()
    pos = grafo_repo.layout(len(nomes), arestas)
    ext = float(np.abs(pos).max()) * 1.08
    png = grafo_repo.desenhar(nomes, familias, arestas, pos,
                              GRAFICOS / "s12_grafo.png", rotulos=3, miudos=0,
                              extensao=ext)
    # o PNG é quadrado, eixos em [-ext, ext] e sem recorte: mapa linear
    xy = {n: (GX + (x + ext) / (2 * ext) * GW, GY + (ext - y) / (2 * ext) * GW)
          for n, (x, y) in zip(nomes, pos)}
    return png, xy, len(nomes), len(arestas)


def s12_second_brain(prs, numero="12"):
    trace = json.loads((DADOS / "trace_sessao.json").read_text(encoding="utf-8"))
    png, xy, n_nos, n_arestas = grafo_para_slide()
    arquivos = trace["arquivos"]
    faltando = [a["nome"] for a in arquivos if a["nome"] not in xy]
    assert not faltando, f"arquivos do trace fora do grafo: {faltando}"
    passos = len(arquivos)
    slides = []
    for k in range(passos + 2):           # 0 = repouso · 1..n = acende · n+1 = pousa
        final = k == passos + 1
        acesos = arquivos[:min(k, passos)]
        s = moldura(prs, numero, "Setup de IA",
                    "Um prompt não lê o repositório inteiro: acende um caminho.")

        img = imagem(s, png, GX, GY, GW, GW)
        img.name = "!!grafo"
        veu = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(GX), Inches(GY),
                                 Inches(GW), Inches(GW))
        veu.fill.solid()
        veu.fill.fore_color.rgb = RGBColor(0x04, 0x07, 0x0E)
        alpha(veu, 42000 if acesos else 0)   # escurece quando o caminho acende
        veu.line.fill.background()
        efeito(veu, '<a:softEdge rad="700000"/>')   # sem borda dura no fundo
        veu.text_frame.text = ""
        veu.name = "!!veu"
        t = texto(s, GX + 0.1, GY + GW - 0.02, GW, 0.2,
                  [(f"{n_nos} arquivos  ·  {n_arestas} ligações  ·  medido no branch por grafo_repo.py",
                    MONO, 7.5, FOOT)], alinha=PP_ALIGN.CENTER)
        t.name = "!!grafo_leg"

        # o caminho: fio entre nós consecutivos, nó aceso, e o pulso no atual
        for i, a in enumerate(acesos):
            x, y = xy[a["nome"]]
            cor = FAMILIA_COR[a["familia"]]
            if i > 0:
                x0, y0 = xy[acesos[i - 1]["nome"]]
                ln = fio(s, x0, y0, x, y, ORANGE, 1.5, 70000)
                ln.name = f"!!e_{i}"
            p = ponto(s, x, y, 0.2, cor, luz=(100000, 60000))
            p.name = f"!!n_{i}"
        if acesos and not final:
            x, y = xy[acesos[-1]["nome"]]
            pulso = ponto(s, x, y, 0.55, ORANGE, alfa=40000)
            efeito(pulso, '<a:softEdge rad="150000"/>')
            pulso.name = "!!pulso"

        # --- coluna da direita
        cw = R - CX
        kicker(s, CX, 1.72, cw, "O SETUP")
        tf = caixa(s, CX, 2.0, cw, 1.25).text_frame
        for i, (lead, resto) in enumerate([
                ("CLAUDE.md.", "Regras e papéis, lidos no começo de toda sessão."),
                ("Ritual de fim.", "Toda sessão fecha escrevendo no LOG e nas decisões pendentes."),
                ("Pesquisa vira arquivo.", "E cita os arquivos que usou — foi isso que virou o grafo.")]):
            paragrafo(tf, [(lead + " ", SEMI, 11, TEXT), (resto, LIGHT, 11, BODY)],
                      primeiro=i == 0, entre=1.1, depois=3)

        card(s, CX, 3.35, cw, 1.42)
        kicker(s, CX + 0.26, 3.55, cw - 0.5, f"PROMPT REAL  ·  SESSÃO {trace['sessao']}  ·  08/09/2026")
        prompt = trace["prompt"].strip()
        if len(prompt) > 230:
            prompt = prompt[:230].rsplit(" ", 1)[0] + " …"
        texto(s, CX + 0.26, 3.82, cw - 0.5, 0.9, [(f"“{prompt}”", SERIF, 10.5, BODY, False, 0, True)],
              entre=1.12)

        kicker(s, CX, 4.98, cw, "O QUE ACENDEU, NA ORDEM")
        col_w = cw / 2
        for i, a in enumerate(acesos):
            cx = CX + (i // 6) * col_w
            cy = 5.26 + (i % 6) * 0.235
            t = texto(s, cx, cy, col_w - 0.1, 0.22,
                      [(f"{i + 1:02d}  ", MONO, 8.5, FOOT),
                       (a["nome"], MONO, 9, FAMILIA_COR[a["familia"]])],
                      anchor=MSO_ANCHOR.MIDDLE, wrap=False)
            t.name = f"!!li_{i}"
        if final:
            familias = []
            for a in arquivos:
                rot = FAMILIA_ROT[a["familia"]]
                if rot not in familias:
                    familias.append(rot)
            texto(s, CX, 6.72, cw, 0.3,
                  [(f"{trace['comandos']} comandos · {passos} arquivos · ", MONO, 9, TEXT, True),
                   ("  →  ".join(familias) + "  →  dado", MONO, 9, ORANGE, True)],
                  anchor=MSO_ANCHOR.MIDDLE)
        elif not acesos:
            texto(s, CX, 5.26, cw, 0.3, [("clique para ver o caminho", MONO, 9, FOOT, False, 0, True)],
                  anchor=MSO_ANCHOR.MIDDLE)

        s.notes_slide.notes_text_frame.text = (
            "Sequência Morph com avanço automático: um clique no slide de repouso toca o caminho inteiro. "
            "O caminho é o real, medido no transcript da sessão (trace_sessao.py), não desenhado.")
        if k > 0:
            morph(s, 550, None if final else PASSO_MS)
        sela(s, f"s12_{k}")
        slides.append(s)
    return slides



# ================================================================== slide 13
COR_TIPO = {"pesquisa": ORANGE, "analise": BLUE, "codigo": MINT}
SUB_CURTO = {"Decisões registradas": "escaladas ao humano",
             "Taxa de recorreção": "pediram 2ª rodada"}


def dados_ia():
    """Os números da página 5, lidos do CSV que `graficos_p5.py` gravou."""
    quadro = pd.read_csv(DADOS / "log_sessoes.csv", parse_dates=["data"])
    return (graficos_p5.indicadores(quadro), quadro.groupby("tipo").size(),
            quadro.groupby("tipo")["tokens"].sum())


def barra_empilhada(slide, x, y, w, h, partes, minimo=0.32):
    """Barra horizontal dividida; a fatia mostra o rótulo se couber."""
    total = sum(v for v, _, _ in partes)
    cx = x
    for valor, cor, rotulo in partes:
        lw = w * valor / total
        r = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(cx), Inches(y),
                                   Inches(lw), Inches(h))
        r.fill.solid()
        r.fill.fore_color.rgb = cor
        r.line.color.rgb = ESCURO
        r.line.width = Pt(0.75)
        efeito(r, "")
        r.text_frame.text = ""
        if lw >= minimo:
            texto(slide, cx, y, lw, h, [(rotulo, MONO, 8.5, ESCURO, True)],
                  alinha=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, wrap=False)
        cx += lw


def legenda(slide, x, y, itens):
    cx = x
    for cor, rotulo in itens:
        ponto(slide, cx + 0.06, y + 0.1, 0.11, cor)
        texto(slide, cx + 0.19, y, 2.4, 0.2, [(rotulo, LIGHT, 8.5, MUTED)],
              anchor=MSO_ANCHOR.MIDDLE, wrap=False)
        cx += 0.19 + 0.062 * len(rotulo) + 0.18


def s13_ia_numeros(prs, numero="13"):
    """Os gráficos da página 5 do relatório, no slide — texto só nos kickers."""
    kpis, por_sessao, por_token = dados_ia()
    s = moldura(prs, numero, "IA em números",
                "Medimos o uso de IA como medimos a estratégia: pelo registro.")

    # --- os quatro indicadores, a largura toda
    gw = (R - L - 3 * 0.12) / 4
    for i, (rot, (valor, sub)) in enumerate(kpis.items()):
        x = L + i * (gw + 0.12)
        card(s, x, 1.62, gw, 0.86)
        texto(s, x + 0.22, 1.66, 1.5, 0.6, [(valor, COND, 30, ORANGE)],
              anchor=MSO_ANCHOR.MIDDLE)
        texto(s, x + 1.35, 1.74, gw - 1.5, 0.3, [(rot.upper(), MONO, 7.5, TEXT, True, 60)],
              anchor=MSO_ANCHOR.MIDDLE, wrap=False)
        texto(s, x + 1.35, 2.02, gw - 1.5, 0.3, [(SUB_CURTO.get(rot, sub), LIGHT, 8.5, MUTED)],
              anchor=MSO_ANCHOR.MIDDLE, wrap=False)

    # --- os dois gráficos do relatório: linha do tempo e erros × quem pegou
    kicker(s, L, 2.66, 6.2, "CONTEXTO POR DIA  ·  DECISÕES ACUMULADAS")
    imagem(s, GRAFICOS / "p5_timeline.png", L, 2.9, 6.25)
    xr = L + 6.25 + 0.38
    kicker(s, xr, 2.66, R - xr, "145 ERROS DA IA  ·  QUEM PEGOU")
    imagem(s, GRAFICOS / "p5_erros.png", xr, 2.92, R - xr)

    # --- onde foi o esforço (o donut do relatório, em duas barras)
    kicker(s, L, 5.6, 6.2, "ONDE FOI O ESFORÇO")
    ordem = [t for t in COR_TIPO if t in por_sessao.index]
    for j, (rot, serie) in enumerate((("por sessão", por_sessao), ("por token", por_token))):
        y = 5.88 + j * 0.34
        texto(s, L, y, 0.9, 0.24, [(rot, LIGHT, 8.5, MUTED)], anchor=MSO_ANCHOR.MIDDLE)
        barra_empilhada(s, L + 0.95, y, 6.25 - 0.95, 0.24,
                        [(float(serie[t]), COR_TIPO[t], f"{serie[t] / serie.sum():.0%}")
                         for t in ordem])
    legenda(s, L + 0.95, 6.62, [(COR_TIPO[t], graficos_p5.ROTULO_TIPO[t]) for t in ordem])

    # --- a peneira da pesquisa, em pontos
    medidas, passaram = sum(g[1] for g in GRUPOS), sum(g[2] for g in GRUPOS)
    kicker(s, xr, 5.6, R - xr, f"PESQUISA  ·  {medidas} HIPÓTESES MEDIDAS, {passaram} ENTRARAM")
    for i, (rot, total, k) in enumerate(GRUPOS):
        y = 5.9 + i * 0.25
        texto(s, xr, y - 0.02, 1.7, 0.2, [(rot, LIGHT, 8.5, BODY)], anchor=MSO_ANCHOR.MIDDLE)
        inicio = (total - k) // 2
        for j in range(total):
            aceso = inicio <= j < inicio + k
            ponto(s, xr + 1.8 + j * 0.2, y + 0.08, 0.13 if aceso else 0.09,
                  ORANGE if aceso else RULE, luz=(50000, 40000) if aceso else None)
        texto(s, xr + 1.8 + 13 * 0.2 + 0.1, y - 0.02, 1.2, 0.2,
              [(f"{k} de {total}", MONO, 8, ORANGE)], anchor=MSO_ANCHOR.MIDDLE)

    s.notes_slide.notes_text_frame.text = (
        "Gráficos da página 5 do relatório (Uteis/graficos/p5_*.png, graficos_p5.py; corte "
        "de 15/08, 91 sessões dos três LOGs). Esforço: 31/54/15 % das sessões e 25/71/4 % "
        "dos tokens. Erros: 145, 88 % pegos na própria sessão. Peneira: GRUPOS do slide 8 "
        "da semi. Uma que caiu: momentum do sinal, VR 0,97–1,18 (Premissa_tendencia.md).")
    sela(s, "s13")
    return s


# ------------------------------------------------------------------- render
def render(pptx: Path, pasta: Path):
    """Exporta cada slide em PNG pelo próprio PowerPoint (COM) — conferência."""
    import win32com.client
    pasta.mkdir(parents=True, exist_ok=True)
    app = win32com.client.Dispatch("PowerPoint.Application")
    pres = app.Presentations.Open(str(pptx), WithWindow=False)
    try:
        for i, sl in enumerate(pres.Slides, 1):
            sl.Export(str(pasta / f"slide{i:02d}.png"), "PNG", 1920, 1080)
    finally:
        pres.Close()
    return sorted(pasta.glob("slide*.png"))


def monta(saida: Path = SAIDA) -> Path:
    prs = Presentation()
    prs.slide_width, prs.slide_height = Emu(12192000), Emu(6858000)
    s3_polymarket(prs)
    s4_comparacao(prs)
    s12_second_brain(prs)
    s13_ia_numeros(prs)
    saida.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(saida))
    return saida


def demo():
    # o mapa do eixo do slide 4 é linear e cobre o alcance declarado
    assert abs(x_de(EIXO_MIN) - X0) < 1e-9 and abs(x_de(EIXO_MAX) - X1) < 1e-9
    assert fmt_pct(-0.0153) == "− 1,53%" and fmt_pct(0.0003) == "+ 0,03%"
    # o trace tem de caber no grafo: é a asserção que o slide 12 faz
    _, xy, n, _ = grafo_para_slide()
    trace = json.loads((DADOS / "trace_sessao.json").read_text(encoding="utf-8"))
    assert all(a["nome"] in xy for a in trace["arquivos"]) and n > 100
    print("demo ok")


if __name__ == "__main__":
    if "--demo" in sys.argv:
        demo()
        sys.exit()
    saida = monta()
    print(f"gravado {saida.relative_to(RAIZ)}")
    if "--render" in sys.argv:
        pasta = Path(sys.argv[sys.argv.index("--render") + 1]) if len(sys.argv) > sys.argv.index("--render") + 1 else saida.parent / "render"
        for p in render(saida, pasta):
            print("  ", p)
