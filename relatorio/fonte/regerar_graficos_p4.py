"""Regera os três gráficos da página 4 a partir do branch do Felipe.

A legenda da curva dizia `Kairós`, e o nome do robô perdeu o acento em
16/08/2026. Trocar a letra dentro da imagem não dá: quem escreve o rótulo é o
`scripts/graficos_p4.py`, que é módulo do Felipe e não pode ser editado daqui.

Então o branch dele é extraído para um diretório de trabalho **fora do
repositório**, o rótulo é trocado na **cópia**, e o gerador roda ali. O módulo
alheio fica intacto, e a saída ainda vem melhor do que o recorte do PDF: PNG de
300 dpi com fundo transparente, desenhado sobre os mesmos CSV que o autor usou.

    python regerar_graficos_p4.py

Precisa de pandas, numpy e matplotlib (o script do Felipe), e do `origin/Felipe`
alcançável pelo git.
"""
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = Path(__file__).resolve().parent
REPO = BASE.parents[1]
DEST = BASE / "importado"
BRANCH = "origin/Felipe"
GERADOR = "scripts/graficos_p4.py"
# (nome que o gerador escreve, nome que o template usa)
FIGURAS = [("p4_curva", "p4_curva"), ("p4_composicao", "p4_decomposicao"),
           ("p4_sensibilidade", "p4_sensibilidades")]

trabalho = Path(tempfile.mkdtemp(prefix="kairos_p4_"))
try:
    pacote = trabalho / "felipe.zip"
    pacote.write_bytes(subprocess.run(
        ["git", "archive", "--format=zip", BRANCH, "src", "scripts", "Dump/dados"],
        cwd=REPO, check=True, capture_output=True).stdout)
    with zipfile.ZipFile(pacote) as z:
        z.extractall(trabalho)

    # A troca acontece aqui, na cópia — nunca no branch dele.
    gerador = trabalho / GERADOR
    fonte = gerador.read_text(encoding="utf-8")
    trocado = fonte.replace('label="Kairós (líquido)"', 'label="Kairos (líquido)"')
    if trocado == fonte:
        raise SystemExit(f"o rótulo com acento não está mais em {GERADOR} — conferir o branch")
    gerador.write_text(trocado, encoding="utf-8")

    saida = trabalho / "graficos"
    (trabalho / "analises").mkdir(exist_ok=True)  # o gerador grava a tabela lá
    rodada = subprocess.run([sys.executable, GERADOR, "--destino", str(saida),
                             "--analises", str(trabalho / "analises")],
                            cwd=trabalho, capture_output=True, encoding="utf-8", errors="replace")
    if rodada.returncode:
        raise SystemExit(f"o gerador do branch falhou:\n{rodada.stderr}")

    DEST.mkdir(exist_ok=True)
    for gerado, nome in FIGURAS:
        alvo = DEST / f"{nome}.png"
        shutil.copyfile(saida / f"{gerado}.png", alvo)
        print(f"{alvo.name:24s} {alvo.stat().st_size / 1024:.0f} KB  (300 dpi, fundo transparente)")
finally:
    shutil.rmtree(trabalho, ignore_errors=True)
