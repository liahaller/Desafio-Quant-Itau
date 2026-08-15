"""Gráficos da página 5 do relatório — o uso de IA medido a partir dos LOGs.

Quatro saídas: `p5_dashboard` (os quatro números), `p5_timeline` (contexto por
dia × decisões acumuladas), `p5_donut` (tipo de sessão) e `p5_erros` (erro da IA
× mecanismo que o pegou).

Os dois primeiros saem só do parser. Os dois últimos precisam de uma coisa que
o LOG não registra — tipo de sessão e taxonomia de erro —, que vive nos
`Dump/dados/classificacao_*.csv`: classificação feita à mão, por regra declarada
ANTES da contagem, um arquivo por recorte do LOG. Sem esses arquivos o script
ainda roda e entrega os dois primeiros.


A página 5 mede o **processo**, não a estratégia: a fonte é o bloco "Uso de IA"
que o ritual do `CLAUDE.md` obriga em toda entrada de `LOG.md`. Este script é o
parser que a sessão 31 deixou pendente ("se os gráficos da página 5 forem
feitos, ele precisa virar script").

Lê os **três** LOGs — o do branch atual pela árvore de trabalho, os da Lia e do
Paulo por `git show origin/<branch>:LOG.md`. Nada de outro membro é copiado para
dentro do branch: a regra 2 do `CLAUDE.md` vale também para arquivo.

Duas coisas que ele **não** faz sozinho, porque são decisão do dono:

  - **não inventa janela de contexto.** Felipe registrou tokens (53 de 55
    sessões); Lia e Paulo registraram quase tudo em "% da janela", sem dizer o
    tamanho dela. A conversão usa a regra declarada em `JANELA_POR_DATA`, que é
    a virada documentada no `LOG.md` do Felipe — e o CSV marca cada sessão com
    `token_medido`, para a página poder declarar a cobertura em vez de fingir
    que os 91 números têm a mesma qualidade.
  - **não descobre decisão em prosa livre.** O universo de decisões sai dos
    cabeçalhos de cada `Decisoes_pendentes.md`; o campo "Decisões escaladas" só
    responde *quando* cada uma apareceu pela primeira vez. Procurar ID conhecido
    em texto erra menos que extrair ID de texto — e a numeração colide entre
    branches (o aviso está no topo do próprio arquivo), então a chave é
    `(dono, id)`, nunca o número sozinho.

O painel de baixo não é eixo secundário de propósito: barra e linha medem coisas
de escala diferente, então vão em dois painéis com o mesmo x, como o `p4_curva`
já faz com a curva e o drawdown.

Uso:

    python scripts/graficos_p5.py            # três LOGs → Dump/graficos + Dump/dados
    python scripts/graficos_p5.py --demo     # auto-teste em LOG sintético
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")   # sem display: o script só grava arquivo
import matplotlib.dates as mdates          # noqa: E402
import matplotlib.pyplot as plt            # noqa: E402

# Onde mora o LOG de cada frente. `None` = árvore de trabalho (branch atual).
FONTES = {"Felipe": None, "Lia": "origin/Lia", "Paulo": "origin/Paulo"}

# Regra de conversão "% da janela" → tokens, decidida pelo dono (2026-08-15).
# A virada é a que o LOG do Felipe documenta: última menção a 200k em 08/07,
# primeira menção a 1M em 09/07. Não é estimativa do script — é premissa
# declarada, e por isso mora aqui em cima e não espalhada no código.
JANELA_POR_DATA = ((pd.Timestamp("2026-07-08"), 200_000), (None, 1_000_000))

PALETAS = {
    # mesma paleta da página 4 (âmbar da ampulheta, ciano dos reflexos)
    "escuro": {"texto": "#E6EAF0", "suave": "#8B97A8", "grade": "#2A3444",
               "kairos": "#F5A623", "bench": "#7A8798", "apoio": "#4FC3D9",
               "negativo": "#C25B54"},
    "claro": {"texto": "#1B2430", "suave": "#5C6B7A", "grade": "#D5DCE4",
              "kairos": "#C97A05", "bench": "#8A97A6", "apoio": "#1E7F97",
              "negativo": "#A83A33"},
}
# Cor por dono, em ordem fixa — identidade não pode trocar entre figuras.
COR_DO_DONO = {"Felipe": "kairos", "Lia": "apoio", "Paulo": "negativo"}
# O donut mede outra entidade (tipo de trabalho), então NÃO pode reusar as cores
# dos donos: mesma cor com dois significados na mesma página é erro de leitura.
COR_DO_TIPO = {"pesquisa": "#F5A623", "analise": "#8E7CC3", "codigo": "#6FBF9B"}
ROTULO_TIPO = {"pesquisa": "pesquisa e decisão", "analise": "análise e medição",
               "codigo": "código"}
ROTULO_ERRO = {"alucinacao_numerica": "alucinação\nnumérica",
               "premissa_herdada": "premissa\nherdada",
               "generalizacao": "generalização\nalém do teste",
               "codigo_quebrado": "código\nquebrado",
               # as duas saíram do "outro" dos classificadores, separadas por
               # decisão do dono: entregar a coisa errada ≠ descrever mal a certa
               "texto_impreciso": "texto impreciso\nou contraditório",
               "escopo_errado": "escopo ou\ncondução errada",
               "outro": "outro"}
ROTULO_BARROU = {"execucao_teste": "execução / teste",
                 "confererencia_humana": "conferência humana",
                 "autocorrecao": "auto-correção na sessão",
                 "so_depois": "só pego em sessão posterior"}
# Ordem das camadas da barra: da contenção mais barata para a mais cara.
ORDEM_BARROU = ["execucao_teste", "autocorrecao", "confererencia_humana", "so_depois"]

CABECALHO = re.compile(r"^##\s+(?:Sess[ãa]o\s+)?(\d{4}-\d{2}-\d{2})", re.M)
CABECALHO_DECISAO = re.compile(r"^#{2,3}\s+(?:Decis[ãa]o\s+)?(\d{1,2}[a-z]?)\b", re.M)
MIL = 1_000


def aplicar_estilo(p):
    """rcParams da paleta. Fundo transparente: quem pinta é o slide."""
    plt.rcParams.update({
        "figure.facecolor": "none", "axes.facecolor": "none",
        "savefig.facecolor": "none", "savefig.transparent": True,
        "text.color": p["texto"], "axes.labelcolor": p["suave"],
        "xtick.color": p["suave"], "ytick.color": p["suave"],
        "axes.edgecolor": p["grade"], "grid.color": p["grade"],
        "font.size": 9, "axes.titlesize": 10, "legend.fontsize": 8.5,
        "axes.spines.top": False, "axes.spines.right": False,
        "figure.autolayout": True,
    })


def ler_fonte(ref, arquivo, raiz=Path(".")):
    """Conteúdo de `arquivo`: da árvore de trabalho, ou do branch por `git show`."""
    if ref is None:
        return (raiz / arquivo).read_text(encoding="utf-8")
    return subprocess.run(["git", "show", f"{ref}:{arquivo}"], check=True,
                          capture_output=True).stdout.decode("utf-8")


def blocos(texto):
    """`[(data, corpo)]` de cada sessão, em ordem CRONOLÓGICA.

    Os três LOGs não concordam na ordem: o do Felipe e o do Paulo são
    mais-novo-primeiro, o da Lia é mais-velho-primeiro. Em vez de configurar
    isso por dono, o sentido sai do próprio arquivo.
    """
    achados = list(CABECALHO.finditer(texto))
    saida = [(pd.Timestamp(m.group(1)),
              texto[m.end(): achados[i + 1].start() if i + 1 < len(achados) else len(texto)])
             for i, m in enumerate(achados)]
    if saida and saida[0][0] > saida[-1][0]:
        saida.reverse()
    return saida


def campo(corpo, nome):
    """Texto de um item do bloco 'Uso de IA' (`- **Nome:** ...`), em uma linha."""
    achado = re.search(rf"{nome}:\*\*(.*?)(?=\n- \*\*|\Z)", corpo, re.S)
    return " ".join(achado.group(1).split()) if achado else None


def janela_em(data):
    """Tamanho da janela de contexto vigente na data, pela regra declarada."""
    for limite, tamanho in JANELA_POR_DATA:
        if limite is None or data <= limite:
            return tamanho


def tokens_da_sessao(texto, data):
    """`(tokens, medido)`. `medido=False` quando saiu de conversão do %."""
    if texto is None:
        return float("nan"), False
    achado = re.search(r"(\d+[.,]?\d*)\s*k\b", texto)
    if achado:
        return float(achado.group(1).replace(",", ".")) * MIL, True
    achado = re.search(r"(\d+[.,]?\d*)\s*%", texto)
    if achado:
        return float(achado.group(1).replace(",", ".")) / 100 * janela_em(data), False
    return float("nan"), False


def primeiro_inteiro(texto):
    """Primeiro inteiro do campo ('~5 rodadas' → 5, '0 rodadas' → 0)."""
    achado = re.search(r"\d+", texto or "")
    return int(achado.group()) if achado else None


def ids_de_decisao(texto):
    """IDs dos cabeçalhos do `Decisoes_pendentes.md` ('12', '15b', '6a')."""
    vistos = []
    for identificador in CABECALHO_DECISAO.findall(texto):
        if identificador not in vistos:
            vistos.append(identificador)
    return vistos


def cita(texto, identificador):
    """O campo cita esta decisão de forma INEQUÍVOCA?

    Um número solto em prosa não serve: "as **13** foram fechadas" é uma
    contagem e "**3** e **4** fechadas" são dois IDs, e nada na frase separa os
    dois casos. Então só contam as quatro formas que não admitem outra leitura:

        6q, 15b, 23e   sufixo de letra — contagem não tem letra
        D28, D22e      prefixo D
        **29**         negrito (é como o ritual marca decisão)
        Decisões 8 e 9 depois da palavra, inclusive em lista
        16 (nova       abrindo o campo e já declarando que é decisão

    O preço é subcontar: decisão citada só como número cru fica sem data e
    aparece em "sem data de registro" no `Metricas_p5.md`, em vez de sumir. O
    `(?![\\w.])` é o que impede `4` de casar dentro da view `2.4` ou de `4.1`.
    """
    if not texto:
        return False
    ident = re.escape(identificador)
    formas = [rf"(?<![\w.])D?{ident}(?![\w.])"] if identificador[-1].isalpha() else [
        rf"\*\*D?{ident}\*\*",
        rf"(?<![\w.])D\s?{ident}(?![\w.])",
        rf"[Dd]ecis(?:ão|ões|ao|oes)s?\s+(?:\d{{1,2}}\s*(?:,|e)\s*)*{ident}(?![\w.])",
        # "2 (seção 10 ...)" é contagem; "16 (nova ...)" não tem outra leitura
        rf"^{ident}\s*\((?:nova|novo|reabertura|criada|registrada)",
    ]
    return any(re.search(f, texto) for f in formas)


def sessoes(dono, ref, raiz=Path(".")):
    """`(quadro, sem_data)`: uma linha por sessão, e as decisões nunca citadas."""
    pendentes = ids_de_decisao(ler_fonte(ref, "Decisoes_pendentes.md", raiz))
    linhas = []
    for data, corpo in blocos(ler_fonte(ref, "LOG.md", raiz)):
        escaladas = campo(corpo, "Decis[õo]es escaladas")
        novas = [i for i in pendentes if cita(escaladas, i)]
        pendentes = [i for i in pendentes if i not in novas]
        tokens, medido = tokens_da_sessao(campo(corpo, "Contexto consumido"), data)
        linhas.append({
            "data": data, "dono": dono, "tokens": tokens, "token_medido": medido,
            "iteracoes": primeiro_inteiro(campo(corpo, "Itera[çc][õo]es at[ée] aceitar")),
            "decisoes": len(novas), "quais": " ".join(novas),
            "prompt_chave": "[PROMPT-CHAVE]" in corpo,
        })
    # `idx` é a chave que casa com o CSV de classificação, então tem de sair do
    # MESMO procedimento nos dois lados: inverte se o arquivo é novo-primeiro,
    # depois ordena por data de forma estável. O LOG do Paulo não é monotônico
    # (começa novo-primeiro e volta a crescer no fim), então inverter sozinho
    # não basta — sem a ordenação estável o casamento sai trocado.
    quadro = pd.DataFrame(linhas).sort_values("data", kind="stable")
    return quadro.reset_index(drop=True).assign(idx=range(len(quadro))), pendentes


def montar(raiz=Path("."), fontes=FONTES):
    """`(quadro, sem_data)`: as três frentes num só quadro, ordenado no tempo."""
    partes, sem_data = [], {}
    for dono, ref in fontes.items():
        parte, sem_data[dono] = sessoes(dono, ref, raiz)
        partes.append(parte)
    quadro = pd.concat(partes, ignore_index=True)
    return quadro.sort_values(["data", "dono"]).reset_index(drop=True), sem_data


def _linhas_csv(caminho):
    """`(tipos, erros)` de um CSV de classificação, separados pelo marcador."""
    tipos, erros, atual = [], [], None
    for linha in Path(caminho).read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if linha.startswith("---"):
            atual = erros
            continue
        if not linha or linha.startswith("#"):
            continue
        campos = [c.strip() for c in linha.split("|")]
        (erros if atual is erros else tipos).append(campos)
    return tipos, erros


def carregar_classificacao(arquivos):
    """`(tipos, erros)` classificados à mão, casados com a ordem de `montar()`.

    A chave não pode ser `(dono, data)`: há cinco sessões do Felipe no mesmo dia.
    Então o casamento é POSICIONAL — `idx` cronológico dentro de cada dono, o
    mesmo que `sessoes()` atribui. Cada arquivo é normalizado para ordem
    crescente antes de concatenar, porque os LOGs não concordam no sentido e o
    classificador leu na ordem do arquivo.
    """
    tipos, erros = [], []
    for caminho in sorted(arquivos):
        parte_tipos, parte_erros = _linhas_csv(caminho)
        if len(parte_tipos) > 1 and parte_tipos[0][0] > parte_tipos[-1][0]:
            parte_tipos.reverse()
        tipos += parte_tipos
        erros += parte_erros

    tipos = pd.DataFrame(tipos, columns=["data", "dono", "tipo", "nota"])
    # a coluna às vezes vem como "2026-07-09 (sessao 2)" para desambiguar o dia:
    # o sufixo não serve para nada aqui, porque o casamento é por posição
    tipos["data"] = pd.to_datetime(tipos["data"].str.extract(r"(\d{4}-\d{2}-\d{2})")[0])
    tipos = tipos.sort_values(["dono", "data"], kind="stable").reset_index(drop=True)
    tipos["idx"] = tipos.groupby("dono").cumcount()

    erros = pd.DataFrame(erros, columns=["data", "dono", "tipo_erro", "barrou", "nota"])
    return tipos, erros


def juntar(quadro, tipos):
    """Cola o tipo de sessão no quadro, conferindo que as datas batem."""
    unido = quadro.merge(tipos[["dono", "idx", "tipo"]], on=["dono", "idx"], how="left")
    faltando = unido["tipo"].isna().sum()
    assert not faltando, f"{faltando} sessões sem classificação — CSV desalinhado"
    conferencia = quadro.merge(tipos[["dono", "idx", "data"]], on=["dono", "idx"],
                               suffixes=("", "_csv"))
    desalinhadas = conferencia[conferencia["data"] != conferencia["data_csv"]]
    assert desalinhadas.empty, f"datas divergem na junção:\n{desalinhadas.head()}"
    return unido


def indicadores(quadro):
    """Os quatro números do dashboard, mais a cobertura que os qualifica."""
    medido = quadro[quadro["token_medido"]]
    com_iteracao = quadro["iteracoes"].dropna()
    return {
        "Sessões de IA": (f"{len(quadro)}",
                          " · ".join(f"{d} {n}" for d, n in
                                     quadro["dono"].value_counts().items())),
        "Tokens por sessão": (f"{quadro['tokens'].mean() / MIL:,.0f}k".replace(",", "."),
                              f"média · {quadro['tokens'].sum() / 1e6:.1f}M no total"
                              .replace(".", ",")),
        "Decisões registradas": (f"{int(quadro['decisoes'].sum())}",
                                 "escaladas para decisão humana"),
        "Taxa de recorreção": (f"{(com_iteracao > 1).mean():.0%}",
                               f"das sessões pediram 2ª rodada ({len(com_iteracao)} medidas)"),
    }


def salvar(fig, destino, nome):
    """SVG para o slide (vetor, não borra no projetor) e PNG como reserva."""
    destino.mkdir(parents=True, exist_ok=True)
    caminhos = []
    for extensao, dpi in (("svg", None), ("png", 300)):
        alvo = destino / f"{nome}.{extensao}"
        fig.savefig(alvo, dpi=dpi, bbox_inches="tight", transparent=True)
        caminhos.append(alvo)
    plt.close(fig)
    return caminhos


def grafico_dashboard(quadro, p, destino):
    """Quatro placas de número. Não é gráfico: o dado é um escalar por placa."""
    itens = indicadores(quadro)
    fig, eixos = plt.subplots(1, len(itens), figsize=(9.2, 1.7))
    for eixo, (rotulo, (valor, nota)) in zip(eixos, itens.items()):
        eixo.axis("off")
        eixo.text(0, 0.92, rotulo.upper(), fontsize=7.5, color=p["suave"], va="top")
        eixo.text(0, 0.52, valor, fontsize=25, fontweight="bold",
                  color=p["kairos"], va="center")
        eixo.text(0, 0.10, nota, fontsize=6.8, color=p["suave"], va="center")
    return salvar(fig, destino, "p5_dashboard")


def grafico_timeline(quadro, p, destino):
    """Contexto por dia (empilhado por frente) e decisões acumuladas embaixo.

    Dois painéis com o mesmo x em vez de eixo secundário: tokens e decisões não
    dividem escala, e sobrepor as duas num só eixo é o erro clássico de leitura.
    """
    dias = pd.Index(sorted(quadro["data"].unique()), name="data")
    fatia = lambda sub: (sub.pivot_table(index="data", columns="dono", values="tokens",
                                         aggfunc="sum", fill_value=0.0)
                         .reindex(dias, fill_value=0.0) / MIL)
    medido = fatia(quadro[quadro["token_medido"]])
    derivado = fatia(quadro[~quadro["token_medido"]])
    acumulado = quadro.groupby("data")["decisoes"].sum().cumsum()

    fig, (ax, axd) = plt.subplots(
        2, 1, figsize=(9.2, 3.9), sharex=True, gridspec_kw={"height_ratios": [2.4, 1]})
    base = pd.Series(0.0, index=dias)
    for dono in COR_DO_DONO:                      # ordem fixa: cor segue a frente
        cor = p[COR_DO_DONO[dono]]
        for quadro_parte, hachura in ((medido, None), (derivado, "///")):
            if dono not in quadro_parte:
                continue
            # hachura = veio de "% da janela", não de token registrado. A régua
            # da conversão é premissa declarada, e a barra tem de dizer isso.
            ax.bar(dias, quadro_parte[dono], bottom=base, width=0.78, color=cor,
                   label=dono if hachura is None else None, linewidth=0,
                   hatch=hachura, edgecolor=p["grade"], alpha=1.0 if hachura is None else 0.8)
            base += quadro_parte[dono]
    ax.set_ylabel("contexto consumido (k tokens)")
    ax.bar(dias[:1], 0, color=p["suave"], hatch="///", edgecolor=p["grade"],
           label="convertido de % da janela")
    ax.legend(frameon=False, loc="upper left", ncol=4)
    ax.grid(axis="y", lw=0.5, alpha=0.5)
    pico = base.idxmax()
    ax.annotate(f"{base.max():,.0f}k".replace(",", "."), (pico, base.max()),
                xytext=(0, 4), textcoords="offset points", ha="center",
                fontsize=8, color=p["texto"])

    axd.fill_between(acumulado.index, acumulado, 0, color=p["bench"], alpha=0.25, lw=0)
    axd.plot(acumulado.index, acumulado, color=p["bench"], lw=1.8)
    axd.set_ylabel("decisões\nregistradas")
    axd.grid(axis="y", lw=0.5, alpha=0.5)
    axd.annotate(f"{int(acumulado.iloc[-1])}", (acumulado.index[-1], acumulado.iloc[-1]),
                 xytext=(6, 0), textcoords="offset points", va="center",
                 fontsize=9, fontweight="bold", color=p["texto"])
    axd.xaxis.set_major_formatter(mdates.ConciseDateFormatter(mdates.AutoDateLocator()))
    return salvar(fig, destino, "p5_timeline")


def grafico_donut(quadro, p, destino):
    """Onde o esforço foi parar: por sessão e por token, lado a lado.

    Os dois anéis existem porque discordam — sessão de pesquisa é curta e sessão
    de análise queima varredura, então contar cabeça e contar token dá leituras
    diferentes do mesmo trabalho.
    """
    ordem = [t for t in COR_DO_TIPO if t in set(quadro["tipo"])]
    cores = [COR_DO_TIPO[t] for t in ordem]
    fig, eixos = plt.subplots(1, 2, figsize=(7.0, 3.2))
    medidas = (("por sessão", quadro.groupby("tipo").size()),
               ("por token consumido", quadro.groupby("tipo")["tokens"].sum()))
    for eixo, (titulo, serie) in zip(eixos, medidas):
        serie = serie.reindex(ordem, fill_value=0)
        fatias, _, _ = eixo.pie(
            serie, colors=cores, startangle=90, counterclock=False,
            autopct=lambda v: f"{v:.0f}%", pctdistance=0.74,
            wedgeprops={"width": 0.42, "edgecolor": "none"},
            textprops={"fontsize": 8.5, "color": p["texto"], "fontweight": "bold"})
        eixo.set_title(titulo, color=p["suave"], fontsize=9)
    fig.legend(fatias, [ROTULO_TIPO[t] for t in ordem], frameon=False,
               ncol=len(ordem), loc="lower center", bbox_to_anchor=(0.5, -0.04))
    return salvar(fig, destino, "p5_donut")


def grafico_erros(erros, p, destino):
    """Tipo do erro × mecanismo que o pegou, empilhado.

    A camada `so_depois` é a que interessa: é onde a contenção FALHOU e o erro
    chegou a um artefato. Por isso ela é a última da pilha, no topo, e é a única
    pintada na cor de alerta.
    """
    tabela = (erros.pivot_table(index="tipo_erro", columns="barrou", aggfunc="size",
                                fill_value=0)
              .reindex(columns=[c for c in ORDEM_BARROU if c in set(erros["barrou"])],
                       fill_value=0))
    tabela = tabela.loc[tabela.sum(axis=1).sort_values(ascending=False).index]
    tons = {"execucao_teste": p["apoio"], "autocorrecao": p["bench"],
            "confererencia_humana": p["kairos"], "so_depois": p["negativo"]}

    fig, ax = plt.subplots(figsize=(6.8, 3.3))
    base = pd.Series(0, index=tabela.index, dtype=float)
    for coluna in tabela.columns:
        ax.bar(range(len(tabela)), tabela[coluna], 0.62, bottom=base,
               color=tons[coluna], label=ROTULO_BARROU[coluna], linewidth=0)
        base += tabela[coluna]
    for i, total in enumerate(base):
        ax.annotate(f"{total:.0f}", (i, total), xytext=(0, 4), fontsize=8.5,
                    textcoords="offset points", ha="center", color=p["texto"])
    ax.set_xticks(range(len(tabela)),
                  [ROTULO_ERRO.get(t, t) for t in tabela.index], fontsize=8.5)
    ax.set_ylabel("erros registrados")
    ax.margins(y=0.18)
    ax.grid(axis="y", lw=0.5, alpha=0.5)
    ax.legend(frameon=False, loc="upper right", ncol=1)
    return salvar(fig, destino, "p5_erros")


def _tabela_erros(erros):
    """Erros por tipo × quem barrou, em markdown, com totais."""
    tabela = erros.pivot_table(index="tipo_erro", columns="barrou", aggfunc="size",
                               fill_value=0)
    colunas = [c for c in ORDEM_BARROU if c in tabela.columns]
    tabela = tabela[colunas]
    tabela = tabela.loc[tabela.sum(axis=1).sort_values(ascending=False).index]
    linhas = ["\n## Erros da IA — tipo × mecanismo que pegou\n",
              "| tipo | " + " | ".join(ROTULO_BARROU[c].replace("\n", " ")
                                       for c in colunas) + " | total |",
              "|---" * (len(colunas) + 2) + "|"]
    for nome, linha in tabela.iterrows():
        rotulo = ROTULO_ERRO.get(nome, nome).replace("\n", " ")
        linhas.append(f"| {rotulo} | " + " | ".join(str(v) for v in linha)
                      + f" | **{linha.sum()}** |")
    totais = tabela.sum()
    linhas.append("| **total** | " + " | ".join(f"**{v}**" for v in totais)
                  + f" | **{totais.sum()}** |")
    return linhas


def escrever_metricas(quadro, sem_data, caminho, tipos=None, erros=None):
    """Números do dashboard + a auditoria de onde cada um saiu."""
    medido = int(quadro["token_medido"].sum())
    orfas = sum(len(v) for v in sem_data.values())
    linhas = [
        "# Métricas da página 5 — uso de IA\n",
        "> Gerado por `scripts/graficos_p5.py` a partir dos três `LOG.md` "
        "(branch atual + `origin/Lia` + `origin/Paulo`). Não editar à mão.\n",
        "| indicador | valor | nota |", "|---|---|---|",
    ]
    linhas += [f"| {r} | {v} | {n} |" for r, (v, n) in indicadores(quadro).items()]
    linhas += [
        "\n## Qualidade do dado de contexto\n",
        f"- **{medido} de {len(quadro)} sessões** registram tokens direto no LOG.",
        f"- As outras **{len(quadro) - medido}** registram só \"% da janela\" e "
        "foram convertidas pela regra declarada em `JANELA_POR_DATA` "
        "(200k até 2026-07-08, 1M depois) — decisão do dono, não do script.",
        "\n## Decisões, por sessão que as registrou\n",
        "| data | dono | decisões |", "|---|---|---|",
    ]
    linhas += [f"| {l.data:%Y-%m-%d} | {l.dono} | {l.quais} |"
               for l in quadro.itertuples() if l.decisoes]
    linhas += [
        "\n## Decisões sem data de registro\n",
        f"Existem no `Decisoes_pendentes.md` mas nenhum campo \"Decisões "
        f"escaladas\" as cita de forma inequívoca (ver `cita()`), então ficam "
        f"fora da curva acumulada: **{orfas}** ao todo.\n",
    ]
    linhas += [f"- **{dono}:** {' '.join(ids) if ids else '—'}"
               for dono, ids in sem_data.items()]

    if tipos is not None:
        contagem = tipos["tipo"].value_counts()
        por_token = quadro.groupby("tipo")["tokens"].sum() / quadro["tokens"].sum()
        linhas += ["\n## Tipo de sessão\n",
                   "> Classificado à mão pela regra declarada antes da contagem: "
                   "vale o que a sessão DEIXOU, e no desempate a medição ganha do "
                   "código (o script era o meio, a medição era o fim).\n",
                   "| tipo | sessões | % das sessões | % dos tokens |",
                   "|---|---|---|---|"]
        linhas += [f"| {ROTULO_TIPO.get(t, t)} | {contagem[t]} | "
                   f"{contagem[t] / len(tipos):.0%} | {por_token.get(t, 0):.0%} |"
                   for t in COR_DO_TIPO if t in contagem]
    if erros is not None:
        linhas += _tabela_erros(erros)
    Path(caminho).write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return caminho


def gerar(raiz, dados, analises, destino, tema, fontes=FONTES):
    p = PALETAS[tema]
    aplicar_estilo(p)
    quadro, sem_data = montar(raiz, fontes)
    dados, analises = Path(dados), Path(analises)
    for pasta in (dados, analises):
        pasta.mkdir(parents=True, exist_ok=True)
    saidas = []
    # A classificação é trabalho humano num CSV à parte; sem ela o script ainda
    # entrega dashboard e linha do tempo, que saem só do parser.
    arquivos = sorted(dados.glob("classificacao_*.csv"))
    tipos = erros = None
    if arquivos:
        tipos, erros = carregar_classificacao(arquivos)
        quadro = juntar(quadro, tipos)   # o `tipo` entra antes do dump: o CSV de
                                         # sessões é o que se confere depois

    saidas.append(dados / "log_sessoes.csv")
    quadro.to_csv(saidas[0], index=False, encoding="utf-8")
    saidas += grafico_dashboard(quadro, p, Path(destino))
    saidas += grafico_timeline(quadro, p, Path(destino))
    if arquivos:
        saidas += grafico_donut(quadro, p, Path(destino))
        saidas += grafico_erros(erros, p, Path(destino))
    saidas.append(escrever_metricas(quadro, sem_data, analises / "Metricas_p5.md",
                                    tipos, erros))
    return saidas


def demo():
    """Auto-teste: um LOG sintético em que cada regra tem resposta conhecida."""
    import tempfile

    log = """# LOG

## 2026-07-08 — Teste
- **Contexto consumido:** ~50% da janela.
- **Iterações até aceitar:** 3 rodadas.
- **Decisões escaladas:** Decisão 4 registrada; a view 2.4 não é decisão.
- **Tags:** `[PROMPT-CHAVE]`

## 2026-07-20 — Teste
- **Contexto consumido:** ~50% da janela.
- **Iterações até aceitar:** 1.
- **Decisões escaladas:** **D4** de novo, a **D15b** nova, e as 15 foram fechadas.
- **Tags:** —

## 2026-07-25 — Teste
- **Contexto consumido:** ~90k tokens.
- **Iterações até aceitar:** 2.
- **Decisões escaladas:** 16 (nova, aberta); 2 pedidos gerados na sessão.
- **Tags:** —
"""
    decisoes = ("## 2. Contagem\n## 4. Alguma coisa\n## 15. Outra\n"
                "### 15b. Subitem\n## 16. Aberta no campo\n")
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "LOG.md").write_text(log, encoding="utf-8")
        (tmp / "Decisoes_pendentes.md").write_text(decisoes, encoding="utf-8")
        q, sem_data = montar(tmp, {"Teste": None})

        assert list(q["data"].dt.strftime("%m-%d")) == ["07-08", "07-20", "07-25"]
        # a mesma "50% da janela" vale 100k antes da virada e 500k depois
        assert list(q["tokens"]) == [100_000, 500_000, 90_000], list(q["tokens"])
        assert list(q["token_medido"]) == [False, False, True], "% não é medido"
        assert list(q["iteracoes"]) == [3, 1, 2], list(q["iteracoes"])
        # "Decisão 4" conta uma vez só (o **D4** seguinte não reconta); a view
        # "2.4" não vira decisão 4; "as 15 foram fechadas" e "2 pedidos" são
        # contagem, não ID; "16 (nova" é ID; "**D15b**" casa apesar do D
        assert list(q["quais"]) == ["4", "15b", "16"], list(q["quais"])
        assert q["decisoes"].sum() == 3, q["quais"].tolist()
        assert sem_data == {"Teste": ["2", "15"]}, sem_data
        assert list(q["prompt_chave"]) == [True, False, False]
        assert indicadores(q)["Taxa de recorreção"][0] == "67%"

        # classificação em ordem DECRESCENTE, como sai de um LOG novo-primeiro:
        # o carregador tem de virar para casar com a ordem cronológica do parser
        (tmp / "classificacao_teste.csv").write_text(
            "2026-07-25|Teste|codigo|terceira\n"
            "2026-07-20|Teste|analise|segunda\n"
            "2026-07-08|Teste|pesquisa|primeira\n"
            "--- ERROS ---\n"
            "2026-07-20|Teste|codigo_quebrado|execucao_teste|bug de unidade\n"
            "2026-07-25|Teste|alucinacao_numerica|so_depois|numero num artefato\n",
            encoding="utf-8")
        tipos, erros = carregar_classificacao([tmp / "classificacao_teste.csv"])
        unido = juntar(q, tipos)
        assert list(unido["tipo"]) == ["pesquisa", "analise", "codigo"], unido["tipo"]
        # a de 07-25 é a única "codigo" e tem 90k: o donut por token tem de dar 90k
        assert unido.groupby("tipo")["tokens"].sum()["codigo"] == 90_000
        assert len(erros) == 2 and set(erros["barrou"]) == {"execucao_teste", "so_depois"}

        saidas = gerar(tmp, tmp, tmp, tmp / "fig", "escuro", {"Teste": None})
        assert all(Path(s).exists() for s in saidas), saidas
        assert any("p5_donut" in str(s) for s in saidas), saidas
    print(f"demo ok — {len(saidas)} arquivos gerados e conferidos")


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raiz", default=".", help="raiz do repositório")
    parser.add_argument("--dados", default="Dump/dados")
    parser.add_argument("--analises", default="Dump/analises")
    parser.add_argument("--destino", default="Dump/graficos")
    parser.add_argument("--tema", choices=sorted(PALETAS), default="escuro")
    parser.add_argument("--demo", action="store_true",
                        help="auto-teste em LOG sintético, sem tocar no Dump")
    args = parser.parse_args()

    if args.demo:
        return demo()
    for caminho in gerar(Path(args.raiz), args.dados, args.analises,
                         args.destino, args.tema):
        sys.stdout.write(f"escrito: {caminho}\n")


if __name__ == "__main__":
    main()
