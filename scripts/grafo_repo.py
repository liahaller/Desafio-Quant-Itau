"""O repositório como grafo — a figura do slide 7 da semifinal.

Gera `Uteis/graficos/s7_grafo.png`: cada arquivo do branch é um nó, cada menção
de um arquivo dentro de outro é uma aresta. E o mesmo desenho que o Obsidian faz
com notas e `[[links]]`, so que aqui o link nao foi escrito para virar grafo —
ele e subproduto do ritual do `CLAUDE.md` (toda sessao abre lendo as decisoes e
fecha escrevendo no LOG, citando os arquivos que tocou).

O que o desenho mede, dito na propria figura para nao virar enfeite:

  - **no** = um arquivo `.md` ou `.py` do branch (o `.git`, o cache do pytest e
    os `__pycache__` ficam de fora);
  - **aresta** = o arquivo A cita o NOME do arquivo B no seu texto. E busca de
    nome literal, entao e assimetrica na origem mas desenhada sem direcao;
  - **tamanho do no** = grau (quantas ligacoes ele tem), nao importancia julgada;
  - **cor** = a familia do arquivo (contrato, analise, codigo, entrega).

O layout e Fruchterman-Reingold em numpy — 199 nos nao justificam uma
dependencia nova so para o `spring_layout`. A semente e fixa: o grafo tem de
sair igual toda vez que for regerado, senao a figura da apresentacao muda
sozinha entre um ensaio e outro.

Uso:

    python scripts/grafo_repo.py            # mede o repo e grava o PNG
    python scripts/grafo_repo.py --demo     # auto-teste do layout
"""

import sys
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")   # sem display: o script so grava arquivo
import matplotlib.patheffects as pe        # noqa: E402
import matplotlib.pyplot as plt            # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "Uteis" / "graficos" / "s7_grafo.png"

IGNORAR = (".git", "__pycache__", ".pytest_cache", "node_modules")

# familia -> (cor, rotulo da legenda). A ordem e a da legenda.
FAMILIAS = {
    "contrato": ("#F5A623", "o contrato e o registro"),
    "analise":  ("#4FC3A1", "análise e pesquisa"),
    "codigo":   ("#4E8FD1", "código e teste"),
    "entrega":  ("#7A8798", "entrega"),
}
TEXTO, FIO = "#E8EDF2", "#38536E"


def familia(rel: Path) -> str:
    """A que familia um caminho pertence — pela pasta, nao pelo conteudo."""
    topo = rel.parts[0]
    if len(rel.parts) == 1:
        return "contrato"
    if topo in ("scripts", "src", "tests"):
        return "codigo"
    if topo == "Uteis":
        return "contrato" if rel.parts[1] == "trocas" else "analise"
    return "entrega"


def levantar(raiz: Path = RAIZ):
    """Devolve (nomes, familias, arestas) medidos na arvore de trabalho."""
    arquivos = sorted(
        p for ext in ("*.md", "*.py") for p in raiz.rglob(ext)
        if not any(parte in IGNORAR for parte in p.relative_to(raiz).parts))
    indice = {p.name: i for i, p in enumerate(arquivos)}
    textos = [p.read_text(encoding="utf-8", errors="ignore") for p in arquivos]

    arestas = set()
    for i, texto in enumerate(textos):
        for nome, j in indice.items():
            if i != j and nome in texto:
                arestas.add((min(i, j), max(i, j)))
    rel = [p.relative_to(raiz) for p in arquivos]
    return [p.name for p in rel], [familia(p) for p in rel], sorted(arestas)


def layout(n, arestas, passos=600, semente=7, gravidade=8.0):
    """Fruchterman-Reingold: repulsao entre todos, atracao ao longo da aresta.

    As forcas sao as do FR classico — repulsao k²/d entre todos, atracao d²/k
    ao longo da aresta. Isso importa para a CARA do grafo: a versao anterior
    usava repulsao 1/d² com atracao linear, que e um cristal de Coulomb — todo
    mundo equidistante, disco perfeito, cara de imagem de banco. O FR classico
    deixa o miolo denso e a periferia esgarcada em gavinhas de um fio so, que e
    a forma que um grafo de notas de fato tem.

    A unica peca fora do manual e a gravidade, pelo mesmo motivo pratico que o
    Obsidian tem uma: sem ela os arquivos sem NENHUMA ligacao sao expulsos para
    fora do quadro (com 8,0 eles pousam espalhados na borda, junto das folhas).

    Semente fixa porque a figura entra numa apresentacao: o grafo nao pode
    trocar de forma entre um ensaio e o outro.
    """
    rng = np.random.default_rng(semente)
    k = 1.0                                   # distancia de repouso de uma aresta
    lado = np.sqrt(n) * k
    pos = rng.uniform(-lado / 2, lado / 2, (n, 2))

    adj = np.zeros((n, n))
    for i, j in arestas:
        adj[i, j] = adj[j, i] = 1.0

    for passo in range(passos):
        t = 0.1 * lado * (1.0 - passo / passos)   # resfriamento linear
        delta = pos[:, None, :] - pos[None, :, :]
        dist = np.linalg.norm(delta, axis=-1) + 1e-9
        forca = (k * k / dist - adj * dist * dist / k)
        desloc = (forca[:, :, None] * delta / dist[:, :, None]).sum(axis=1)
        desloc -= gravidade * pos
        norma = np.linalg.norm(desloc, axis=1) + 1e-9
        pos += desloc / norma[:, None] * np.minimum(norma, t)[:, None]
    return pos - pos.mean(axis=0)


def desenhar(nomes, familias, arestas, pos, destino: Path, rotulos=3):
    """Grafo em fundo transparente, para o gradiente do slide passar por baixo."""
    grau = np.zeros(len(nomes))
    for i, j in arestas:
        grau[i] += 1
        grau[j] += 1

    plt.rcParams["font.family"] = ["Segoe UI", "DejaVu Sans"]
    # A figura entra no slide com ~2/3 do tamanho em que e desenhada, entao fio
    # e tipo sao dimensionados PARA A REDUCAO: 0,45 pt de linha e 8 pt de texto
    # somem na hora de projetar.
    fig, eixo = plt.subplots(figsize=(6.1, 5.6))
    for i, j in arestas:
        eixo.plot(pos[[i, j], 0], pos[[i, j], 1], color=FIO, lw=0.9,
                  alpha=0.65, zorder=1, solid_capstyle="round")

    tam = 9 + 30 * np.sqrt(grau)
    for chave, (cor, _) in FAMILIAS.items():
        m = np.array([f == chave for f in familias])
        if not m.any():
            continue
        # o halo por baixo e o que o Obsidian faz no fundo escuro: o ponto
        # acende em vez de so existir
        eixo.scatter(pos[m, 0], pos[m, 1], s=tam[m] * 5, c=cor, lw=0,
                     alpha=0.10, zorder=1.5)
        eixo.scatter(pos[m, 0], pos[m, 1], s=tam[m], c=cor, lw=0,
                     alpha=0.95, zorder=2)

    # Rotulos em dois pesos, como um print de vault de verdade: os hubs em
    # destaque e um punhado de nomes miudos em volta. Sem os miudos o desenho
    # vira ilustracao generica; com todos eles, vira borrao — por isso um so
    # entra se a caixa dele nao encostar em nenhuma ja colocada.
    extensao = float(np.ptp(pos, axis=0).max())
    por_pt = extensao / (fig.get_size_inches()[0] * 72)   # unidade de dado / pt
    caixas = []

    def cabe(x, y, texto, corpo):
        w = len(texto) * corpo * 0.55 * por_pt / 2
        h = corpo * 1.4 * por_pt / 2
        for cx, cy, cw, ch in caixas:
            if abs(x - cx) < w + cw and abs(y - cy) < h + ch:
                return False
        caixas.append((x, y, w, h))
        return True

    ordem = np.argsort(grau)[::-1]
    for posicao, i in enumerate(ordem[:rotulos + 22]):
        hub = posicao < rotulos
        corpo = 13.0 if hub else 8.0
        raio = (tam[i] / np.pi) ** 0.5      # do centro ate a borda, em pontos
        # no acima do centro leva o nome em cima, abaixo leva embaixo: os tres
        # hubs sao vizinhos, e todos com o nome em cima se atropelam
        acima = pos[i, 1] >= 0
        desvio = (raio + 5.0) * (1 if acima else -1)
        if not cabe(pos[i, 0], pos[i, 1] + desvio * por_pt, nomes[i], corpo):
            continue
        eixo.annotate(nomes[i], pos[i], xytext=(0, desvio),
                      textcoords="offset points", ha="center",
                      va="bottom" if acima else "top", fontsize=corpo,
                      color=TEXTO if hub else "#8FA5B8", zorder=3,
                      path_effects=[pe.withStroke(
                          linewidth=3.0 if hub else 2.2, foreground="#0A1621")])

    eixo.axis("off")
    eixo.set_aspect("equal")
    eixo.margins(0.06)
    fig.subplots_adjust(0, 0, 1, 1)
    destino.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destino, transparent=True, dpi=160, bbox_inches="tight",
                pad_inches=0.02)
    plt.close(fig)
    return destino


def monta(destino: Path = SAIDA):
    nomes, familias, arestas = levantar()
    pos = layout(len(nomes), arestas)
    desenhar(nomes, familias, arestas, pos, destino)
    return destino, len(nomes), len(arestas)


# --------------------------------------------------------------- auto-teste
def demo() -> None:
    """Dois testes: a forca de mola separa grupos, e a gravidade segura orfao.

    A gravidade e a unica peca fora do algoritmo de manual, e foi ela que
    quebrou na primeira versao (orfao expulso para fora do quadro) — entao ela
    e testada no valor que a figura de fato usa.
    """
    grupo_a = [(i, j) for i in range(5) for j in range(i + 1, 5)]
    grupo_b = [(i, j) for i in range(5, 10) for j in range(i + 1, 10)]
    ligados = grupo_a + grupo_b + [(0, 5)]

    # com gravidade fraca, quem manda e a mola: dois grupos, dois lugares
    pos = layout(10, ligados, passos=400, gravidade=0.5)
    dentro = np.linalg.norm(pos[:5] - pos[:5].mean(0), axis=1).mean()
    entre = np.linalg.norm(pos[:5].mean(0) - pos[5:].mean(0))
    assert entre > 2 * dentro,         f"os grupos nao se separaram ({entre:.2f} × {dentro:.2f})"
    assert np.allclose(pos, layout(10, ligados, passos=400, gravidade=0.5)),         "o layout nao e deterministico — a figura mudaria entre ensaios"

    # na gravidade de producao, o no sem aresta pousa no aro, nao no infinito
    n = 60
    estrela = [(0, i) for i in range(1, n - 6)]          # 6 orfaos no fim
    raio = np.linalg.norm(layout(n, estrela, passos=400), axis=1)
    aro = np.percentile(raio[:n - 6], 95)
    assert raio[n - 6:].max() < 1.5 * aro,         f"orfao escapou do quadro ({raio[n - 6:].max():.2f} × aro {aro:.2f})"

    caminho, n, m = monta()
    assert caminho.exists() and caminho.stat().st_size > 20_000, "PNG vazio"
    print(f"ok — {caminho.relative_to(RAIZ)}: {n} arquivos · {m} ligações")


if __name__ == "__main__":
    if "--demo" in sys.argv:
        demo()
    else:
        caminho, n, m = monta()
        print(f"{caminho}  ({n} nós, {m} arestas)")
