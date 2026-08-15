"""Gera a página 5 do relatório v2 (uso de IA generativa e próximos passos) em PPTX.

Mesmo estilo da página 4: as primitivas de layout, a paleta e a métrica
tipográfica são importadas de `relatorio_p4.py` — nada é redefinido aqui, para
as duas páginas não divergirem.

Seções e ordem saem do `Relatório/Drafts/Plano_relatorio_v2.txt` (página 5), sem
desvio: a regra do trabalho com IA, os dados gerais, a separação do trabalho,
onde a IA agregou, onde ela falhou, limitações, próximos passos e fechamento.

Todos os números vêm de artefato medido:
  - `Dump/analises/Metricas_p5.md`   (sessões, tokens, decisões, recorreção,
                                      tipo de sessão, erro × mecanismo)
  - `Dump/graficos/p5_*.png`         (gerados por `scripts/graficos_p5.py`)
  - `LOG.md` dos três branches       (casos de falha citados)

O `p5_dashboard.png` não é usado: os quatro KPIs vão tipografados no slide, como
a tabela de métricas da página 4 — texto do gerador de gráfico não bate com a
tipografia do deck em largura de coluna.

Uso: python scripts/relatorio_p5.py [--saida CAMINHO.pptx]
"""

from __future__ import annotations

import argparse
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Emu, Inches

from relatorio_p4 import (BG, MUTED, MUTED2, ORANGE, TEXT, bloco, caixa,
                          escreve, imagem, regua, rotulo)

RAIZ = Path(__file__).resolve().parent.parent
GRAFICOS = RAIZ / "Dump" / "graficos"

# ciano de apoio, mesmo hex da paleta do `graficos_p5.py`
APOIO = RGBColor(0x4F, 0xC3, 0xD9)


def kpi(slide, x, y, w, titulo, valor, nota):
    """Um número grande com rótulo em cima e nota embaixo (o dashboard da p. 5)."""
    tf = caixa(slide, x, y, w, 0.14)
    escreve(tf, [(titulo.upper(), MUTED, False)], 5.8, spc=0.8, primeiro=True)
    tf = caixa(slide, x, y + 0.14, w, 0.30)
    escreve(tf, [(valor, ORANGE, True)], 21.0, espaco=1.0, primeiro=True)
    tf = caixa(slide, x, y + 0.47, w, 0.14)
    escreve(tf, [(nota, MUTED, False)], 6.0, primeiro=True)


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
    tf = caixa(slide, L, 0.34, 7.0, 0.30)
    escreve(tf, [("KAIRÓS", ORANGE, True),
                 ("   Uso de IA generativa e próximos passos", MUTED2, False)],
            12.0, spc=0.8, primeiro=True)
    tf = caixa(slide, R - 1.0, 0.38, 1.0, 0.20)
    escreve(tf, [("05", MUTED, False)], 9.0, alinha=PP_ALIGN.RIGHT, primeiro=True)
    regua(slide, L, 0.76, R)

    # -- 1. a regra que organizou o trabalho com IA -------------------------
    rotulo(slide, L, 0.86, "A regra que organizou o trabalho com IA", w=5.2)
    tf = caixa(slide, L, 1.04, 5.20, 0.56)
    escreve(tf, [
        ("Três frentes em paralelo, cada uma dona dos seus módulos e do seu "
         "branch, com as regras versionadas no próprio repositório — o mesmo "
         "arquivo lido no início de toda sessão, em qualquer máquina. A regra "
         "central é uma só: ", MUTED, False),
        ("a IA nunca fecha decisão metodológica", TEXT, True),
        (". Fonte, universo, forma funcional e valor de parâmetro saem de "
         "decisão humana registrada; até ela existir, o agente escreve "
         "TODO(DECISAO-N) e toca o resto da tarefa.", MUTED, False),
    ], 7.0, espaco=1.24, primeiro=True)

    chips = [
        ("Um dono por módulo.",
         " Código de outro dono não se edita: o defeito vira observação no LOG dele."),
        ("Ritual de sessão obrigatório.",
         " Toda sessão fecha com entrada no LOG e um bloco “Uso de IA”. Esta página "
         "sai dele."),
        ("Second-brain por branch.",
         " 40 análises e o registro de decisões versionados: a sessão nova lê o "
         "estado, não relembra a conversa."),
        ("Placeholder em vez de palpite.",
         " 81 decisões escaladas com data rastreável, outras 43 sem data. Nenhuma "
         "fechada pelo agente."),
    ]
    for i, (lead, resto) in enumerate(chips):
        cx = 6.20 + (i % 2) * 3.20
        cy = 1.04 + (i // 2) * 0.28
        tf = caixa(slide, cx, cy, 3.05, 0.26)
        escreve(tf, [("· ", ORANGE, True), (lead, TEXT, True), (resto, MUTED, False)],
                6.1, espaco=1.18, primeiro=True)
    regua(slide, L, 1.62, R)

    # -- 2. dados gerais: os quatro números ---------------------------------
    rotulo(slide, L, 1.70, "Dados gerais · o processo medido, não estimado", w=6.0)
    kpis = [("Sessões de IA", "91", "Felipe 55 · Lia 18 · Paulo 18"),
            ("Tokens por sessão", "232k", "média · 19,7M no total"),
            ("Decisões registradas", "81", "escaladas para decisão humana"),
            ("Taxa de recorreção", "37%", "das sessões pediram 2ª rodada (87 medidas)")]
    for i, (titulo, valor, nota) in enumerate(kpis):
        kpi(slide, L + i * 2.88, 1.90, 2.75, titulo, valor, nota)
    regua(slide, L, 2.52, R)

    # -- faixa dos três visuais ---------------------------------------------
    rotulo(slide, L, 2.60, "Linha do tempo do projeto", w=4.2)
    base = imagem(slide, GRAFICOS / "p5_timeline.png", L, 2.78, 4.20)
    tf = caixa(slide, L, base + 0.06, 4.20, 0.36)
    escreve(tf, [
        ("Barras: contexto por dia, empilhado por frente; linha: decisões "
         "acumuladas. ", MUTED, False),
        ("Oito dias de agosto concentram o grosso do contexto", TEXT, True),
        (" e a subida de 13 para 81 decisões. Hachurado: as 33 sessões cujo "
         "token foi convertido de “% da janela”.", MUTED, False),
    ], 6.4, espaco=1.22, primeiro=True)

    rotulo(slide, 5.30, 2.60, "Tipo de sessão · por sessão e por token", w=3.30)
    base = imagem(slide, GRAFICOS / "p5_donut.png", 5.30, 2.78, 3.30)
    tf = caixa(slide, 5.30, base + 0.06, 3.30, 0.32)
    escreve(tf, [
        ("Os 91 blocos do LOG classificados à mão, por regra fechada antes da "
         "contagem. Análise e medição leva ", MUTED, False),
        ("54% das sessões e 71% dos tokens", TEXT, True),
        ("; código, 15% e 4%. O caro não foi escrever código — foi medir.",
         MUTED, False),
    ], 6.4, espaco=1.22, primeiro=True)

    rotulo(slide, 8.90, 2.60, "Erros da IA × mecanismo que pegou", w=3.53)
    base = imagem(slide, GRAFICOS / "p5_erros.png", 8.90, 2.78, 3.53)
    tf = caixa(slide, 8.90, base + 0.06, 3.53, 0.43)
    escreve(tf, [
        ("145 erros contados um a um nos três LOGs. Código quebrado é a maior "
         "categoria (72) e a mais barata: 40 morrem na execução. Na outra "
         "ponta, ", MUTED, False),
        ("texto impreciso (13) e escopo errado (10) não têm um único erro pego "
         "por teste", TEXT, True),
        (" — a conferência humana pegou os 23 ainda na sessão.", MUTED, False),
    ], 6.4, espaco=1.22, primeiro=True)

    regua(slide, L, 4.98, R)

    # -- faixa de baixo: cinco blocos ---------------------------------------
    col_w, passo = 2.15, 2.335
    x = [L + i * passo for i in range(5)]
    y0, alt = 5.06, 1.94

    rotulo(slide, x[0], y0, "A separação do trabalho", w=col_w, tamanho=6.0)
    tf = caixa(slide, x[0], y0 + 0.30, col_w, alt - 0.30)
    linhas = [
        (ORANGE, "A IA sozinha.",
         " Código, varredura, medição repetida e prosa gerada a partir dos números: "
         "38 scripts, 37 arquivos de teste e 40 análises só neste branch."),
        (APOIO, "Só o humano.",
         " Fonte, universo, forma funcional, parâmetro e o que entra na entrega — "
         "e o veredito de cada régua, escrito antes de medir."),
        (TEXT, "Nenhum dos dois sozinho.",
         " O critério que julga um ingrediente é humano e declarado antes; a varredura "
         "que o aplica é da IA. Trocar a ordem produz overfit com cara de método."),
    ]
    for i, (cor, lead, resto) in enumerate(linhas):
        escreve(tf, [("■ ", cor, True), (lead, TEXT, True), (resto, MUTED, False)],
                6.1, espaco=1.18, antes=0 if i == 0 else 5.0, primeiro=(i == 0))

    bloco(slide, x[1], y0, col_w, alt, "Onde a IA agregou", [
        ("Varredura exaustiva ficou barata.",
         "13 candidatas táticas medidas antes de uma entrar, cada ingrediente do Ω "
         "testado em várias grades, horizontes e janelas — ~200 comparações só na "
         "busca tática. À mão, nada disso teria sido testado."),
        ("Prosa gerada do número.",
         "As páginas saem de gerador alimentado por artefato medido; a legenda muda "
         "quando o número muda."),
        ("Revisão cruzada entre agentes.",
         "A classificação dos 91 blocos saiu de 4 agentes com briefing único, e a "
         "conferência da própria saída pegou 3 dos 6 erros da sessão."),
        ("", "A adesão foi maior onde o erro é conferível — medição e código. Em "
             "método, a IA foi interlocutor, não autor."),
    ], tamanho=6.0)

    bloco(slide, x[2], y0, col_w, alt, "Onde a IA falhou, e o que conteve", [
        ("Premissa herdada, pega pelo humano.",
         "A IA afirmou que o mapeamento cenário→ativo estava congelado; o congelado era "
         "a camada tática. Duas rodadas de correção do dono — e o registro errado já "
         "tinha entrado em duas entradas do LOG."),
        ("Contagem que contava o que não era decisão.",
         "A primeira regra de citação lia “categoria 2” e “opção 1” como ID de decisão. "
         "Pega auditando a própria saída; a regra final declara o preço: 43 decisões "
         "ficam sem data em vez de sumir."),
        ("Defeito latente que só um assert novo revelou.",
         "O auto-teste do gerador desta página misturava LOG sintético com os LOGs reais "
         "— invisível desde que a função foi escrita."),
    ], tamanho=6.0)

    bloco(slide, x[3], y0, col_w, alt, "Limitações declaradas", [
        ("O Ω é diagonal.",
         "Não desconta views correlacionadas: duas com ρ +0,67 entram como informação "
         "independente."),
        ("Régua calibrada em duas views, aplicada a quatro.",
         "A forma foi julgada contra o erro da probabilidade nas duas que existiam."),
        ("Uma janela, um regime.",
         "374 pregões de alta do S&P, sem correção para as ~200 comparações da busca."),
        ("D12 segue aberta.",
         "Nível e escopo do teto de alavancagem ainda não têm decisão fechada."),
        ("O dado desta página tem qualidade desigual.",
         "33 das 91 sessões têm token convertido de “% da janela”: os KPIs de token são "
         "estimativa de estimativa, e ficam declarados como tal."),
    ], tamanho=6.0)

    bloco(slide, x[4], y0, col_w, alt, "Próximos passos", [
        ("Termos fora da diagonal no Ω.",
         "É a limitação com endereço mais claro: a correlação entre views já está medida."),
        ("Banda de não-negociação.",
         "Contra os 42% de giro desfeito em dois pregões — o breakeven de 22,9 bps por "
         "lado diz que há espaço para não negociar."),
        ("Ampliar o universo pelo critério certo.",
         "Não por classe de ativo, e sim por haver notícia a que o preço responda."),
        ("Validar em regime de queda.",
         "O que a página 4 admite é o que falta testar: a vantagem veio da subida."),
    ], tamanho=6.0)

    # -- fechamento + rodapé -------------------------------------------------
    tf = caixa(slide, L, 7.06, R - L, 0.18)
    escreve(tf, [
        ("Fechamento. ", ORANGE, True),
        ("Kairós troca opinião por preço observável: o que a estratégia entrega é "
         "disciplina, não adivinhação — e a mesma regra que a IA seguiu para "
         "construí-la é essa, decisão humana registrada antes do número.",
         MUTED2, False),
    ], 7.0, primeiro=True)

    regua(slide, L, 7.28, R)
    tf = caixa(slide, L, 7.33, R - L, 0.14)
    escreve(tf, [
        ("91 sessões e 19,7M de tokens lidos dos três ", MUTED, False),
        ("LOG.md", MUTED2, False),
        (" do projeto (Felipe · Lia · Paulo) por ", MUTED, False),
        ("graficos_p5.py", MUTED2, False),
        (". Tipo de sessão e taxonomia de erro são classificação manual, por regra "
         "declarada antes da contagem, linha a linha em ", MUTED, False),
        ("classificacao_*.csv", MUTED2, False),
        (".", MUTED, False),
    ], 6.0, primeiro=True)

    saida.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(saida))
    return saida


def altura_do_texto(tf, largura: float) -> float:
    """Altura em polegadas que o texto ocupa, medida no Segoe UI real.

    Sem renderizador nesta máquina, é o único jeito de pegar texto que estoura a
    caixa e invade a régua de baixo — o defeito que não aparece no `.pptx`.
    """
    from PIL import ImageFont
    fontes = {False: r"C:\Windows\Fonts\segoeui.ttf",
              True: r"C:\Windows\Fonts\segoeuib.ttf"}
    carregada = {}

    def largura_de(texto, negrito, tamanho):
        chave = (negrito, round(tamanho, 1))
        if chave not in carregada:   # 4 px por pt: precisão suficiente, cache barato
            carregada[chave] = ImageFont.truetype(fontes[negrito], int(tamanho * 4))
        return carregada[chave].getlength(texto) / 4 / 72

    total = 0.0
    for p in tf.paragraphs:
        runs = [(r.text, bool(r.font.bold), r.font.size.pt) for r in p.runs]
        if not runs:
            continue
        tamanho = max(r[2] for r in runs)
        palavras = []
        for texto, negrito, tam in runs:
            for i, palavra in enumerate(texto.split(" ")):
                if i == 0 and palavras and not texto.startswith(" "):
                    anterior = palavras[-1]      # o run emenda na palavra anterior
                    palavras[-1] = (anterior[0] + palavra, anterior[1], anterior[2])
                else:
                    palavras.append((palavra, negrito, tam))
        espaco = largura_de(" ", False, tamanho)
        linhas, corrida = 1, 0.0
        for palavra, negrito, tam in palavras:
            larg = largura_de(palavra, negrito, tam)
            if corrida and corrida + espaco + larg > largura:
                linhas, corrida = linhas + 1, larg
            else:
                corrida += (espaco if corrida else 0) + larg
        total += (p.space_before.pt if p.space_before else 0) / 72
        total += linhas * tamanho * (p.line_spacing or 1.0) / 72
    return total


def demo() -> None:
    """Auto-teste do layout: nada vaza da moldura nem da própria caixa."""
    alvo = RAIZ / "Dump" / "_demo_p5.pptx"
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
    assert len(slide.shapes) > 30, f"slide com poucas formas: {len(slide.shapes)}"

    estourou = []
    for s in slide.shapes:
        if not s.has_text_frame or not s.text_frame.text.strip():
            continue
        real = altura_do_texto(s.text_frame, Emu(s.width).inches)
        if real > Emu(s.height).inches + 0.01:
            estourou.append((s.text_frame.text[:40], round(real, 2),
                             round(Emu(s.height).inches, 2)))
    assert not estourou, f"texto maior que a caixa: {estourou}"
    alvo.unlink()
    print("demo ok — nada fora da moldura, nenhum texto estourando a caixa")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--saida", default=str(RAIZ / "Relatório" / "Drafts" / "KAIROSv2_p5.pptx"))
    ap.add_argument("--demo", action="store_true", help="roda o auto-teste de layout")
    args = ap.parse_args()
    if args.demo:
        demo()
    else:
        print(monta(Path(args.saida)))
