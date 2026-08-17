"""Injeta imagem e SVGs no template, gera o PDF e valida contra o edital."""
import re
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Caminhos derivados do próprio arquivo — o script roda a partir do repositório,
# sem depender do diretório de trabalho `X:` em que o backtest foi remontado.
BASE = Path(__file__).resolve().parent
SVG = BASE / "svg"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"


def inline_svg(caminho):
    """SVG pronto para embutir: sem cabeçalho XML e sem tamanho fixo."""
    s = Path(caminho).read_text(encoding="utf-8")
    s = re.sub(r"<\?xml.*?\?>|<!DOCTYPE.*?>", "", s, flags=re.S)
    s = re.sub(r'(<svg[^>]*?)\s(width|height)="[^"]*"', r"\1", s)
    return s.strip()


html = (BASE / "template.html").read_text(encoding="utf-8")
html = html.replace("{{KAIROS_IMG}}", (BASE / "kairos_datauri.txt").read_text(encoding="utf-8"))
html = html.replace("{{SVG_PIPELINE}}", inline_svg(BASE / "pipeline.svg"))
html = html.replace("{{SVG_ARQUITETURA}}", inline_svg(BASE / "arquitetura.svg"))
html = html.replace("{{SVG_CURVA}}", inline_svg(SVG / "curva.svg"))
html = html.replace("{{SVG_INGREDIENTES}}", inline_svg(SVG / "ingredientes.svg"))
html = html.replace("{{SVG_REGUA}}", inline_svg(SVG / "regua.svg"))

destino = BASE / "KAIROS.html"
destino.write_text(html, encoding="utf-8")
pdf = BASE.parent / "KAIROS.pdf"

subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                f"--print-to-pdf={pdf}", str(destino)],
               check=True, capture_output=True)

# ---------------------------------------------------------------- validação
import pymupdf  # noqa: E402

doc = pymupdf.open(pdf)
r = doc[0].rect
texto = "\n".join(p.get_text() for p in doc)
palavras = len(re.findall(r"[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ'’-]*", texto))

print(f"tamanho do arquivo : {pdf.stat().st_size / 1024:.0f} KB")
print(f"páginas            : {doc.page_count}   {'OK' if doc.page_count <= 5 else 'FALHA — 6+ elimina'}")
print(f"dimensão           : {r.width:.0f} x {r.height:.0f} pt  (ratio {r.width / r.height:.4f})"
      f"   {'OK 16:9' if abs(r.width / r.height - 16 / 9) < 0.001 else 'FALHA'}")

# A contagem do PDF inclui rótulos de eixo dos gráficos. A referência de 750 do
# edital é sobre texto do relatório, então mede-se também só a prosa: o HTML sem
# SVG, sem estilo e sem marcação.
prosa = re.sub(r"<svg.*?</svg>|<style.*?</style>|<!--.*?-->", " ", html, flags=re.S)
prosa = re.sub(r"<[^>]+>", " ", prosa)
n_prosa = len(re.findall(r"[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ'’-]*", prosa))
print(f"palavras (prosa)   : {n_prosa}   {'OK' if n_prosa <= 780 else 'acima da referência de 750'}")
print(f"palavras (com gráficos): {palavras}")

# Anonimato: nada que identifique autores, equipe ou instituição.
proibido = ["Lia", "Felipe", "Paulo", "Insper", "Haller", "liahaller", "github"]
achados = [t for t in proibido if re.search(rf"\b{t}\b", texto, re.I)]
print(f"anonimato          : {'OK — nenhum identificador' if not achados else 'FALHA: ' + str(achados)}")

# Fidelidade ao que cada autor entregou. As páginas 1, 2, 4 e 5 foram remontadas
# no template a partir dos PDFs recebidos, e o texto delas tem de continuar sendo
# o mesmo. Compara-se o conjunto de caracteres, sem espaço e em caixa alta: o
# tracking dos títulos separa letra por letra na extração, e a caixa muda com o
# `text-transform` do CSS — nada disso é conteúdo. As únicas diferenças aceitas
# são as combinadas, declaradas aqui uma a uma; qualquer outra é reportada.
from collections import Counter  # noqa: E402

ORIGENS = [
    # (pdf entregue, página nele, página no relatório, falta, sobra)
    # "01 / 05" virou "01"; e o excesso sobre o SPY, que a p1 trazia como +3,1 pp
    # (a subtração dos números já arredondados, 33,2 − 30,1), passou a +3,0 pp, que
    # é o medido: 3,045 pp no `backtest_diario.csv`, e o que as páginas 4 e 5 dizem.
    ("kairos_p1.pdf",      0, 0, {"1": 1, "/": 1, "5": 1}, {}),
    ("kairos_p2_final.pdf", 0, 1, {"0": 1, "/": 1, "5": 1}, {"→": 1}),    # idem; a seta do fluxo virou texto
    ("KAIROSv2_p4_p5.pdf", 0, 3, {"Ó": 2, "·": 4}, {"O": 2}),             # KAIRÓS→KAIROS; marcador "·" virou filete
    ("KAIROSv2_p4_p5.pdf", 1, 4, {"Ó": 2, "·": 4}, {"O": 2}),
]
caracteres = lambda t: Counter(re.sub(r"\s+", "", t).upper())  # noqa: E731
for arquivo, origem, destino, falta_ok, sobra_ok in ORIGENS:
    caminho = pdf.parent / arquivo
    if not caminho.exists():
        print(f"conteúdo pág. {destino + 1}   : sem {arquivo} para conferir")
        continue
    a = caracteres(pymupdf.open(caminho)[origem].get_text())
    b = caracteres(doc[destino].get_text())
    falta, sobra = dict(a - b), dict(b - a)
    igual = falta == falta_ok and sobra == sobra_ok
    print(f"conteúdo pág. {destino + 1}   : "
          + ("OK — nada mudou além do combinado" if igual
             else f"DIVERGE  falta {falta}  sobra {sobra}"))

# Extrato de uma página só, para revisar a página da dona sem abrir as cinco.
# Sai daqui e não à mão de propósito: solto, ele envelheceria calado a cada
# regeração do entregável — que é o modo de falha já registrado no LOG.
extrato = pdf.parent / "KAIROS_pagina3.pdf"
uma = pymupdf.open()
uma.insert_pdf(doc, from_page=2, to_page=2)
uma.save(extrato)
print(f"extrato da pág. 3  : {extrato.name}")

for i, p in enumerate(doc, 1):
    p.get_pixmap(dpi=100).save(BASE / f"pag{i}.png")
print(f"\nprévias: {BASE}/pag1..{doc.page_count}.png")
