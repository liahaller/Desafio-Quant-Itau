"""Recorta os gráficos da página 5 e a arte da capa dos PDFs entregues.

Esses gráficos vieram embutidos num PDF pronto. Em vez de redesenhá-los (o que
mudaria o número), recorta-se a região do PDF original em 4x e troca-se o preto
do fundo pelo fundo do relatório — o desenho não é tocado, só a cor que o cerca.

Os três da página 4 NÃO saem daqui: como a legenda de um deles precisava perder
o acento, eles são redesenhados pelo gerador do próprio autor — ver
`regerar_graficos_p4.py`.
"""
import base64
import sys
from pathlib import Path

import numpy
import pymupdf

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = Path(__file__).resolve().parent
DEST = BASE / "importado"
DEST.mkdir(exist_ok=True)
FUNDO = (11, 22, 34)   # --fundo do template
ESCURO = 14            # até aqui é fundo, não desenho

# (arquivo, página, retângulo no PDF de origem, nome de saída)
RECORTES = [
    ("KAIROSv2_p4_p5.pdf", 1, (60, 190, 370, 321), "p5_linha_do_tempo"),
    ("KAIROSv2_p4_p5.pdf", 1, (379, 190, 623, 323), "p5_tipo_de_sessao"),
    ("KAIROSv2_p4_p5.pdf", 1, (638, 190, 899, 315), "p5_erros"),
]


def sem_fundo(pix):
    """Troca o preto do gráfico pelo fundo do relatório, sem tocar no desenho."""
    a = numpy.frombuffer(pix.samples, dtype=numpy.uint8).reshape(pix.height, pix.width, pix.n).copy()
    fundo = (a[:, :, 0] <= ESCURO) & (a[:, :, 1] <= ESCURO) & (a[:, :, 2] <= ESCURO)
    a[fundo, 0], a[fundo, 1], a[fundo, 2] = FUNDO
    return pymupdf.Pixmap(pix.colorspace, pix.width, pix.height, a.tobytes(), pix.alpha)


for arquivo, pagina, caixa, nome in RECORTES:
    p = pymupdf.open(BASE.parent / arquivo)[pagina]
    pix = p.get_pixmap(matrix=pymupdf.Matrix(4, 4), clip=pymupdf.Rect(*caixa))
    saida = DEST / f"{nome}.png"
    sem_fundo(pix).save(saida)
    print(f"{saida.name:24s} {pix.width}x{pix.height}px  ({saida.stat().st_size / 1024:.0f} KB)")

# A arte do robô sai da mesma fonte: a imagem embutida na página 1 entregue. Fica
# em base64 porque o template a injeta como data URI, e assim ninguém precisa
# guardar o JPEG à parte.
capa = pymupdf.open(BASE.parent / "kairos_p1.pdf")
arte = capa.extract_image(capa[0].get_images(full=True)[0][0])
(BASE / "kairos_datauri.txt").write_text(
    f"data:image/{arte['ext']};base64," + base64.b64encode(arte["image"]).decode(), encoding="utf-8")
print(f"{'kairos_datauri.txt':24s} {arte['width']}x{arte['height']}px  "
      f"({len(arte['image']) / 1024:.0f} KB, da página 1)")
