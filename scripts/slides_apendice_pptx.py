"""Slides de apêndice da semifinal — o que se mostra SE perguntarem.

Gera `Semis/Apendice.pptx`, deck separado do `KAIROS_semifinal.pptx`: os slides
não entram nos 6 minutos e a cópia compartilhada não é tocada por este script.
Para usar, anexar os 4 slides ao fim do deck.

A camada visual é importada do `slides_3a6_pptx.py` e do `relatorio_p4.py`, para
o apêndice não trocar de identidade no meio da arguição.

OS QUATRO, e a pergunta que cada um responde:
  A1  a conta inteira        — "como vocês viram probabilidade em retorno?"
  A2  o teto de risco        — "vocês escolheram a configuração que ganha?"
  A3  a camada tática        — "ela ajuda ou atrapalha?"
  A4  robustez e concentração — "quanto disso é sorte?"

O Ω NÃO entra: a fórmula dele já está no slide 5 do deck principal.

FONTE DOS NÚMEROS (nenhum digitado de cabeça):
  · grade de 8 configurações      → `Uteis/dados/backtest_metricas.csv`
  · varredura de γ                → `Uteis/dados/backtest_gamma.csv`
  · captura, alfa e t             → `Uteis/dados/backtest_diario.csv` (calculados
    aqui, mesma convenção do `graficos_p4.py`: regressão diária contra o SPY,
    taxa livre de risco zero)
  · camada tática (G4 e Δ)        → `Uteis/analises/Camada_tatica_v2.md`, D28.13
    e sua errata de 14/08 (régua ligada nas duas pontas)
  · concentração das views        → D23b do `Felipe` (`Uteis/analises/Views_novas.md`)
"""

from pathlib import Path

import numpy as np
import pandas as pd
from pptx import Presentation
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

from relatorio_p4 import (MUTED, MUTED2, ORANGE, TEXT, caixa, escreve, regua,
                          rotulo)
from slides_3a6_pptx import (BANDA, BODY, CORPO, CORPO_PT, DET, L, MINT, PE, R,
                             chamada, moldura, painel, pino, sela)

RAIZ = Path(__file__).resolve().parent.parent
DADOS = RAIZ / "Uteis" / "dados"
SAIDA = RAIZ / "Semis" / "Apendice.pptx"

CENARIO = "tilt ≤ 1"          # o cenário da entrega (10a)
PREGOES_ANO = 252
MONO = "Consolas"


def br(texto):
    """Numero no padrao do deck: virgula decimal e sinal de menos tipografico."""
    return texto.replace(".", ",").replace("-", "−")


# --------------------------------------------------------------- os números
def grade_tetos():
    """As 8 configurações, do csv: {escopo: [(teto, líquido, excesso)]}."""
    m = pd.read_csv(DADOS / "backtest_metricas.csv", index_col=0)
    saida = {"carteira": [], "tilt": []}
    for col in m.columns:
        escopo = "carteira" if col.startswith("Σ") else "tilt"
        teto = int(col.strip()[-1])
        saida[escopo].append((teto, m.loc["retorno acumulado líquido", col],
                              m.loc["excesso acumulado (líquido − benchmark)", col]))
    return {k: sorted(v) for k, v in saida.items()}


def varredura_gamma():
    """Excesso acumulado em cada γ da robustez."""
    g = pd.read_csv(DADOS / "backtest_gamma.csv", index_col=0)
    linha = "excesso acumulado (líquido − benchmark)"
    return [(c, float(g.loc[linha, c])) for c in g.columns]


def diario():
    return pd.read_csv(DADOS / "backtest_diario.csv").query("cenario == @CENARIO")


def alfa_t(r, b):
    """(alfa anualizado, beta, t do alfa) — OLS dos retornos contra o SPY."""
    X = np.column_stack([np.ones(len(b)), b])
    coef, *_ = np.linalg.lstsq(X, r, rcond=None)
    resid = r - X @ coef
    s2 = resid @ resid / (len(r) - 2)
    erro = np.sqrt(np.diag(s2 * np.linalg.inv(X.T @ X)))
    return coef[0] * PREGOES_ANO, coef[1], coef[0] / erro[0]


def captura(r, b):
    """Captura média em quatro cortes do retorno do benchmark."""
    q05, q95 = np.quantile(b, 0.05), np.quantile(b, 0.95)
    cortes = [("dias de alta", b > 0), ("dias de baixa", b < 0),
              ("5% piores dias", b <= q05), ("5% melhores dias", b >= q95)]
    return [(nome, r[m].mean() / b[m].mean()) for nome, m in cortes]


# Medidos fora dos csv — ficam aqui com a fonte, como no `slide8_pesquisa_pptx.py`.
TATICA_G4 = {"acumulado": 0.4261, "pregoes": 327, "acerto": 0.5443,
             "sem_3_maiores": 0.6400, "pedido_mediano": 2.54, "acima_do_teto": 0.80}
TATICA_DELTA = [(1, -2.94), (2, -6.75), (3, -8.90), (5, +3.82)]   # errata da 28.13
CONCENTRACAO = [("Incerteza", "+3,9 pp", "−0,5 pp", "48%"),
                ("Trajetória", "−1,4 pp", "+2,9 pp", "49%"),
                ("As duas juntas", "+2,2 pp", "+2,5 pp", "49%")]   # D23b


# ------------------------------------------------------------------ desenho
def moldura_ap(prs, numero, titulo):
    """A moldura do deck, com o rodapé trocado pelo desta geração."""
    s = moldura(prs, numero, titulo)
    tf = s.shapes[-1].text_frame
    tf.clear()
    escreve(tf, [("Apêndice — fora dos 6 minutos, mostrado só se perguntarem.   ",
                  MUTED, False),
                 ("scripts/slides_apendice_pptx.py", MUTED2, False)],
            8.5, primeiro=True)
    return s


def formula(slide, x, y, w, texto, tam=11.5, cor=TEXT):
    """Uma fórmula: mesma caixa de sempre, em monoespaçada."""
    tf = caixa(slide, x, y, w, 0.34)
    p = escreve(tf, [(texto, cor, False)], tam, espaco=1.15, primeiro=True)
    for run in p.runs:
        run.font.name = MONO
    return tf


def legenda(slide, x, y, w, texto, tam=CORPO_PT - 1.5, cor=BODY):
    tf = caixa(slide, x, y, w, 1.10)
    escreve(tf, [(texto, cor, False)], tam, espaco=1.28, primeiro=True)


def tabela(slide, x, y, w, cabecalho, linhas, destaque=None, alt=0.30,
           tam=CORPO_PT - 1.0, val_w=1.28):
    """Tabela de 3 colunas com uma linha opcional realçada em verde-água.

    `val_w` e a largura das colunas de valor: em tabela estreita ela encolhe,
    senao a coluna de rotulo fica com menos de uma polegada e o texto quebra.
    """
    larguras = [w - 2 * val_w, val_w, val_w]
    alinhas = [PP_ALIGN.LEFT, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT]

    xs, acum = [], x
    for larg in larguras[:len(cabecalho)]:
        xs.append(acum)
        acum += larg
    for texto, alinha, larg, cx in zip(cabecalho, alinhas, larguras, xs):
        tf = caixa(slide, cx, y, larg, 0.20)
        escreve(tf, [(texto.upper(), MUTED, False)], 8.0, spc=1.0, alinha=alinha,
                primeiro=True)
    regua(slide, x, y + alt - 0.06, x + w)

    for i, celulas in enumerate(linhas):
        ly = y + alt + i * alt
        realce = (i == destaque)
        for j, (texto, alinha, larg, cx) in enumerate(
                zip(celulas, alinhas, larguras, xs)):
            cor = MINT if realce else (MUTED2 if j == 0 else TEXT if j == 1 else MUTED)
            tf = caixa(slide, cx, ly + 0.04, larg, alt)
            escreve(tf, [(texto, cor, realce or j == 1)], tam, alinha=alinha,
                    primeiro=True)
        regua(slide, x, ly + alt - 0.06, x + w)
    return y + alt + len(linhas) * alt


def numerao(slide, x, y, w, valor, rot, sub, cor=TEXT, h=1.45):
    """Cartão de um número grande — o formato do placar do slide 8."""
    painel(slide, x, y, w, h)
    pino(slide, x + 0.20, y + 0.22, h - 0.44, cor, esp=0.05)
    tf = caixa(slide, x + 0.44, y + 0.22, w - 0.64, 0.55)
    escreve(tf, [(valor, cor, True)], 26.0, espaco=1.0, primeiro=True)
    tf = caixa(slide, x + 0.44, y + 0.82, w - 0.64, 0.50)
    escreve(tf, [(rot, TEXT, True)], CORPO_PT - 1.0, espaco=1.2, primeiro=True)
    escreve(tf, [(sub, BODY, False)], CORPO_PT - 2.0, espaco=1.22, antes=2.0)


def barra(slide, x, y, w, h, fracao, cor, rot, valor):
    """Barra horizontal com rótulo — usada para 'o que cabe' × 'o que ela pede'."""
    tf = caixa(slide, x, y - 0.26, w, 0.22)
    escreve(tf, [(rot, BODY, False)], CORPO_PT - 2.0, primeiro=True)
    trilho = painel(slide, x, y, w, h, topo=MUTED, base=MUTED)
    trilho.fill.solid()
    trilho.fill.fore_color.rgb = MUTED
    trilho.fill.transparency = 0.82
    cheio = painel(slide, x, y, max(w * fracao, 0.10), h, topo=cor, base=cor)
    cheio.fill.solid()
    cheio.fill.fore_color.rgb = cor
    tf = caixa(slide, x, y + h + 0.06, w, 0.24)
    escreve(tf, [(valor, cor, True)], CORPO_PT - 0.5, primeiro=True)


# ------------------------------------------------------------------- slides
def a1_contas(prs):
    """A cadeia inteira de contas — a única coisa que não dá para improvisar."""
    s = moldura_ap(prs, "A1", "Apêndice · a conta inteira")

    passos = [
        ("1 · EQUILÍBRIO", ["π = δ · Σ · w_mkt"],
         "Em vez de perguntar quais pesos são os melhores, perguntamos o "
         "contrário: que retornos fariam a carteira do mercado ser a ótima? "
         "É o ponto de partida, e não precisa de previsão nenhuma."),
        ("2 · A OPINIÃO", ["P[i] = 2·(β_i − β_SPY) / Σ|β − β_SPY|",
                           "Q  = (Σ P·β) × surpresa"],
         "P diz quem compra e quem vende, na proporção da sensibilidade medida. "
         "Q é essa sensibilidade vezes a surpresa de hoje: o Polymarket menos o "
         "que a bolsa já embutiu."),
        ("3 · A MISTURA", ["μ = π + peso · (Q − P·π)"],
         "Só a discordância move a carteira: se a opinião concordar com o "
         "equilíbrio, nada muda. O peso vem do Ω — a confiança medida, que está "
         "no slide 5."),
        ("4 · A CARTEIRA", ["w = inv(δ · Σ) · μ", "Σ|w − w_mkt| ≤ 1"],
         "A conta clássica de carteira ótima, sem restrição de sinal — é o que "
         "permite comprar um setor e vender outro. O teto limita o desvio "
         "contra o mercado, não o tamanho da carteira."),
    ]

    largura, vao = 2.68, 0.27
    for i, (titulo, formulas, texto) in enumerate(passos):
        x = L + i * (largura + vao)
        painel(s, x, 1.06, largura, 2.98)
        rotulo(s, x + 0.24, 1.30, titulo, w=largura - 0.40, tamanho=8.5)
        y = 1.66
        for f in formulas:
            formula(s, x + 0.24, y, largura - 0.40, f,
                    tam=10.5 if len(f) > 26 else 12.0)
            y += 0.62 if len(f) > 30 else 0.36  # a longa quebra em duas linhas
        legenda(s, x + 0.24, y + 0.16, largura - 0.40, texto)

    rotulo(s, L, DET, "O QUE CADA SÍMBOLO É", w=5.60, tamanho=9.5)
    tf = caixa(s, L, CORPO, 5.60, 2.00)
    for i, (sim, txt) in enumerate([
            ("δ", "o quanto o investidor típico odeia risco — medido no S&P 500 em 22 anos."),
            ("Σ", "como os nove fundos se mexem juntos — dois anos de histórico, até a véspera."),
            ("w_mkt", "a carteira do mercado: 100% no S&P 500, porque os setores já estão dentro dele."),
            ("β", "quanto cada fundo anda quando o evento surpreende — sai de regressão, nunca de palpite."),
            ("μ", "o retorno esperado final, já misturando equilíbrio e opinião.")]):
        escreve(tf, [(sim + "   ", ORANGE, True), (txt, BODY, False)],
                CORPO_PT - 1.0, espaco=1.26, antes=0 if i == 0 else 7.0,
                primeiro=i == 0)

    chamada(s, 6.83, CORPO - 0.34, 5.60, 1.20, [
        ("A prova de que a conta está certa.",
         "Sem nenhuma opinião ativa, ela devolve exatamente a carteira do "
         "mercado — sem sobra e sem resíduo. O caso extremo é testado "
         "automaticamente.")], cor=MINT)
    chamada(s, 6.83, CORPO + 1.02, 5.60, 1.00, [
        ("A confiança (Ω) não está aqui de propósito.",
         "A fórmula dela é o slide 5: a régua de coerência e estabilidade do "
         "próprio mercado.")])
    sela(s, "A1")
    return s


def a2_teto(prs):
    """A grade de 8 — o slide 6 afirma que ela existe; aqui ela aparece."""
    s = moldura_ap(prs, "A2", "Apêndice · o teto de risco, e as 8 configurações")

    grade = grade_tetos()
    fmt = lambda t, liq, exc: (f"teto {t}", br(f"{liq:+.1%}"),
                               br(f"{exc * 100:+.1f} pp"))

    rotulo(s, L, 1.14, "ENCOLHENDO A CARTEIRA INTEIRA", w=5.30, tamanho=9.5)
    tabela(s, L, 1.52, 5.30, ("limite", "retorno", "vs índice"),
           [fmt(*linha) for linha in grade["carteira"]])
    legenda(s, L, 3.30, 5.30,
            "Corta tudo pelo mesmo fator, inclusive a parte que é mercado. Num "
            "ano em que o índice subiu 30%, vender índice custa caro sozinho — "
            "sem ter nada a ver com a qualidade das apostas.")

    rotulo(s, 7.13, 1.14, "ENCOLHENDO SÓ O DESVIO  ·  A NOSSA", w=5.30,
           tamanho=9.5, cor=MINT)
    tabela(s, 7.13, 1.52, 5.30, ("limite", "retorno", "vs índice"),
           [fmt(*linha) for linha in grade["tilt"]], destaque=0)
    legenda(s, 7.13, 3.30, 5.30,
            "Limita só o quanto a carteira se afasta do índice e entrega a perna "
            "de mercado inteira. É o escopo da entrega — e a linha que usamos é "
            "a MAIS APERTADA da tabela, não a de melhor número.")

    rotulo(s, L, DET, "POR QUE ISSO NÃO É ESCOLHER O QUE FICOU BOM", w=5.60,
           tamanho=9.5)
    tf = caixa(s, L, CORPO, 5.60, 2.00)
    for i, (lead, resto) in enumerate([
            ("A regra veio antes.",
             " O escopo e o nível foram fixados antes de rodar o backtest, com "
             "plano B escrito. Nenhuma linha desta tabela foi escolhida depois."),
            ("Publicamos as oito.",
             " A alternativa honesta a escolher uma configuração é mostrar a "
             "grade inteira — inclusive as quatro em que perdemos do índice."),
            ("E ficamos na mais apertada.",
             " Afrouxar o limite melhoraria o número em toda a coluna. Não "
             "afrouxamos.")]):
        escreve(tf, [(lead, TEXT, True), (resto, BODY, False)], CORPO_PT - 1.0,
                espaco=1.26, antes=0 if i == 0 else 8.0, primeiro=i == 0)

    chamada(s, 6.83, CORPO - 0.34, 5.60, 1.60, [
        ("O escopo vale 18 pontos, e é mecânico.",
         "A diferença entre as duas tabelas no mesmo limite não vem das "
         "apostas: vem de uma delas vender índice e a outra não. Por ser uma "
         "escolha tão pesada, ela é a que mais precisava ser fixada antes."),
    ], cor=ORANGE)
    sela(s, "A2")
    return s


def a3_tatica(prs):
    """A camada tática por dentro: positiva sozinha, negativa somada."""
    s = moldura_ap(prs, "A3", "Apêndice · a camada tática por dentro")

    g4 = TATICA_G4
    numerao(s, L, 1.10, 3.60, br(f"+{g4['acumulado'] * 100:.1f} pp"),
            "Sozinha, fora da carteira",
            f"{g4['pregoes']} pregões ativos · acerta a direção em "
            f"{g4['acerto'] * 100:.0f}% deles · e sem os três melhores dias sobe "
            f"para +{g4['sem_3_maiores'] * 100:.0f} pp", cor=MINT, h=1.85)
    numerao(s, 4.75, 1.10, 3.60, br(f"{TATICA_DELTA[0][1]:+.1f} pp"),
            "Ao entrar na carteira",
            "O excesso sobre o índice cai de +6,0 pp para +3,0 pp. Não é "
            "contradição — é divisão de um orçamento fixo de risco.", cor=ORANGE,
            h=1.85)

    chamada(s, L, 3.22, 7.45, 0.90, [
        ("Diga assim, se perguntarem:",
         "“o limite de risco é fixo. Quando a camada tática entra, ela não "
         "soma — ela divide. Nessa janela, o que ela deslocou valia um pouco "
         "mais do que o que ela trouxe.”")])

    rotulo(s, 8.83, 1.10, "POR QUE ELA NÃO CABE", w=3.60, tamanho=9.5)
    barra(s, 8.83, 1.78, 3.60, 0.22, 1 / g4["pedido_mediano"], MUTED2,
          "O limite de risco da carteira inteira", "1,0")
    barra(s, 8.83, 2.58, 3.60, 0.22, 1.0, ORANGE,
          "O que a camada tática pede sozinha",
          br(f"{g4['pedido_mediano']:.2f}"))
    legenda(s, 8.83, 3.10, 3.60,
            f"Em {g4['acima_do_teto'] * 100:.0f}% dos dias ativos o pedido dela "
            "sozinho já não cabe — então o corte encolhe também as outras "
            "apostas.")

    rotulo(s, L, DET, "E AFROUXAR O LIMITE RESOLVERIA? NÃO", w=5.60, tamanho=9.5)
    tabela(s, L, CORPO - 0.06, 5.60, ("limite de risco", "efeito", ""),
           [(f"teto {t}", br(f"{d:+.2f} pp"), "") for t, d in TATICA_DELTA],
           alt=0.28)
    legenda(s, L, CORPO + 1.34, 5.60,
            "O efeito piora até o teto 3 e só depois vira. Um padrão assim não "
            "se lê como 'a camada perde' nem como 'ela só disputa espaço' — e "
            "escolher o limite que fica bom seria exatamente o overfit que a "
            "gente diz evitar.")

    chamada(s, 6.83, CORPO - 0.34, 5.60, 1.10, [
        ("Ela entrou por mecanismo, não por lucro.",
         "Lê o movimento da probabilidade, não o nível; nenhum parâmetro foi "
         "escolhido olhando resultado. Prejuízo não reprova — e o custo dessa "
         "decisão está medido acima.")], cor=MINT)
    chamada(s, 6.83, CORPO + 0.96, 5.60, 1.10, [
        ("O único teste fora da amostra do projeto.",
         "A aposta da Câmara repete o comportamento em um mercado parecido, que "
         "não foi usado para construí-la. É o teste mais forte que temos, e é o "
         "único.")])
    sela(s, "A3")
    return s


def a4_robustez(prs):
    """Concentração, robustez e cauda — a resposta a 'quanto disso é sorte?'."""
    s = moldura_ap(prs, "A4", "Apêndice · robustez, concentração e cauda")

    d = diario()
    r, b = d["r_liquido"].to_numpy(), d["r_benchmark"].to_numpy()
    alfa, beta, t = alfa_t(r, b)

    rotulo(s, L, 1.14, "SEM OS TRÊS MAIORES DIAS", w=3.55, tamanho=9.5)
    tabela(s, L, 1.52, 3.55, ("aposta", "soma", "sem 3"),
           [(nome, total, sem3) for nome, total, sem3, _ in CONCENTRACAO],
           alt=0.28, tam=CORPO_PT - 2.0, val_w=0.95)
    legenda(s, L, 2.82, 3.55,
            "A aposta de incerteza vira negativa sem os três maiores dias — e "
            "isso foi escrito ANTES de ligá-la. O acerto de direção das duas é "
            "de 48% e 49%: cara ou coroa.")

    rotulo(s, 4.85, 1.14, "SE CORRIGIRMOS O VIÉS DE AZARÃO", w=3.55, tamanho=9.5)
    tabela(s, 4.85, 1.52, 3.55, ("correção", "vs índice", ""),
           [(f"γ = {g.replace('.', ',')}", br(f"{e * 100:+.1f} pp"), "")
            for g, e in varredura_gamma()], alt=0.28, tam=CORPO_PT - 2.0, val_w=0.95)
    legenda(s, 4.85, 2.82, 3.55,
            "Apostadores pagam caro demais no azarão. Não corrigimos esse viés "
            "no resultado principal — e corrigir só melhoraria o número. A "
            "conclusão não depende disso.")

    rotulo(s, 8.88, 1.14, "CAPTURA DE ALTA E DE QUEDA", w=3.55, tamanho=9.5)
    tabela(s, 8.88, 1.52, 3.55, ("no dia em que", "captura", ""),
           [(nome, f"{c:.0%}".replace("%", "%"), "") for nome, c in captura(r, b)],
           alt=0.28, tam=CORPO_PT - 2.0, val_w=0.95)
    legenda(s, 8.88, 3.10, 3.55,
            "No dia comum a carteira cai um pouco menos que o índice. Nos dias "
            "extremos a vantagem some: caímos quase igual e subimos menos.")

    rotulo(s, L, DET, "E O GANHO DE TRÊS PONTOS — É SORTE?", w=5.60, tamanho=9.5)
    tf = caixa(s, L, CORPO, 5.60, 2.00)
    for i, (lead, resto) in enumerate([
            ("Pode ser, e não temos como provar o contrário.",
             br(f" O teste dá {t:.2f}") +
             " e o mínimo para se afirmar algo é 2. Com um ano e meio de dados, "
             "chegar lá é matematicamente impossível."),
            ("Não é um mês sortudo.",
             " A carteira bateu o índice em 11 dos 19 meses do período."),
            ("O que defendemos é o método.",
             " Cada peça foi escolhida por um motivo escrito antes de medir — e "
             "nenhuma aposta foi cortada por dar prejuízo.")]):
        escreve(tf, [(lead, TEXT, True), (resto, BODY, False)], CORPO_PT - 1.0,
                espaco=1.26, antes=0 if i == 0 else 8.0, primeiro=i == 0)

    chamada(s, 6.83, CORPO - 0.34, 5.60, 1.10, [
        ("O custo não decide o resultado.",
         "Supomos 2 bps por lado. O custo teria de ser 11 vezes maior para "
         "zerar o ganho — e testamos negociar menos, sem melhora.")])
    chamada(s, 6.83, CORPO + 0.96, 5.60, 1.10, [
        ("Alfa e beta, para quem pedir.",
         br(f"Beta de {beta:.2f}") + br(f" e alfa de {alfa:+.2%} ao ano") +
         ", pela regressão diária contra o S&P 500, com taxa livre de risco "
         "zero para os dois lados.")], cor=MINT)
    sela(s, "A4")
    return s


def monta(saida: Path = SAIDA) -> Path:
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    for construtor in (a1_contas, a2_teto, a3_tatica, a4_robustez):
        construtor(prs)
    saida.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(saida))
    return saida


def demo() -> None:
    """Checagem mínima: os números do deck batem com os artefatos da entrega."""
    grade = grade_tetos()
    assert len(grade["carteira"]) == 4 and len(grade["tilt"]) == 4
    # a linha da entrega é o teto 1 no tilt: +33,2% líquido, +3,04 pp de excesso
    teto1 = grade["tilt"][0]
    assert teto1[0] == 1 and abs(teto1[1] - 0.3316) < 5e-4, teto1
    assert abs(teto1[2] - 0.0304) < 5e-4, teto1
    # alfa e beta têm de reproduzir a página 4 do relatório
    d = diario()
    alfa, beta, t = alfa_t(d["r_liquido"].to_numpy(), d["r_benchmark"].to_numpy())
    assert abs(alfa - 0.0257) < 5e-4 and abs(beta - 0.95) < 5e-3, (alfa, beta)
    assert 0.6 < t < 0.7, t
    # a captura na cauda é pior que a captura na alta — é o achado do slide A4
    cap = dict(captura(d["r_liquido"].to_numpy(), d["r_benchmark"].to_numpy()))
    assert cap["5% piores dias"] > cap["5% melhores dias"], cap
    prs = Presentation(str(monta()))
    assert len(list(prs.slides)) == 4
    print(f"ok — 4 slides em {SAIDA}")


if __name__ == "__main__":
    demo()
