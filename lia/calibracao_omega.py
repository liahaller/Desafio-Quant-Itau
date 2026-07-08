"""Harness de calibração da forma funcional do Ω reativo (Decisão 6).

Implementa o protocolo registrado em Decisoes_pendentes.md (08/07/2026):
os parâmetros em aberto da Decisão 6 (janela da estabilidade,
forma/horizonte do decaimento de proximidade, threshold de volume) são
escolhidos por teste de monotonicidade no histórico — faixas de
confiança maiores devem apresentar erro realizado da probabilidade
menor. Empates são resolvidos pela forma com menos parâmetros.

Ponto técnico que delimita o escopo: o teste de monotonicidade é
invariante a transformações monótonas — só a ORDEM dos scores importa.
Por isso as candidatas aqui produzem *scores* (quanto maior, mais
confiança), sem normalização para (0,1]. A normalização final do fator
de confiança `c` que escala o baseline de He-Litterman é fechada junto
com a Decisão 6, informada pelo resultado desta calibração.

Este módulo não acessa dados externos: recebe séries já preparadas pelo
pipeline do Paulo (probabilidades do Polymarket via `/prices-history`;
volume a confirmar — ver Decisoes_pendentes.md, Decisão 6).

Nenhum parâmetro de modelo tem valor default de propósito: janela,
horizonte, threshold e nº de faixas vêm da decisão registrada ou da
grade de candidatas em teste, nunca de default no código.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Erro realizado — a grandeza que a confiança deve prever
# ---------------------------------------------------------------------------


def erro_realizado_futuro(prob: pd.Series, horizonte: int) -> pd.Series:
    """Erro realizado da probabilidade `horizonte` períodos à frente.

    Definição: |p_{t+h} − p_t|. Se a confiança em t é alta, a
    probabilidade não deveria se mover muito nos próximos h períodos.
    Os últimos `horizonte` pontos ficam NaN (não há futuro observável).
    """
    if horizonte < 1:
        raise ValueError("horizonte deve ser pelo menos 1 período")
    return (prob.shift(-horizonte) - prob).abs()


def erro_vs_resolucao(prob: pd.Series, resultado: float) -> pd.Series:
    """Erro da probabilidade contra a resolução final do mercado.

    Definição: |resultado − p_t|, com `resultado` ∈ {0, 1} (o evento
    ocorreu ou não). Alternativa ao erro futuro quando o mercado já
    resolveu — qual das duas definições entra na calibração é parte da
    Decisão 6.
    """
    if resultado not in (0.0, 1.0):
        raise ValueError("resultado deve ser 0 ou 1 (resolução do mercado)")
    return (resultado - prob).abs()


# ---------------------------------------------------------------------------
# Scores candidatos — os ingredientes da confiança (Decisão 6)
# ---------------------------------------------------------------------------


def score_estabilidade(prob: pd.Series, janela: int) -> pd.Series:
    """Score de estabilidade da probabilidade numa janela móvel.

    Definição: −desvio-padrão das variações diárias na janela. Quanto
    mais estável a probabilidade, maior o score (máximo 0.0, série
    parada). Janelas incompletas no início produzem NaN.
    """
    if janela < 2:
        raise ValueError("janela deve ter pelo menos 2 períodos")
    return -prob.diff().rolling(janela, min_periods=janela).std()


def score_proximidade(
    datas: pd.DatetimeIndex,
    data_evento,
    forma: str,
    horizonte_dias: int,
) -> pd.Series:
    """Score de distância a um evento agendado (quanto mais longe, maior).

    Duas formas candidatas em teste (a escolha é parte da Decisão 6):
    - "linear":      min(d, horizonte) / horizonte
    - "exponencial": 1 − exp(−d / horizonte)
    onde d = dias até o evento (0 no dia do evento e depois dele).
    Ambas valem 0 no dia do evento e crescem monotonicamente com d.
    """
    if horizonte_dias < 1:
        raise ValueError("horizonte_dias deve ser pelo menos 1")
    dias = (pd.Timestamp(data_evento) - datas).days
    d = np.clip(np.asarray(dias, dtype=float), 0.0, None)
    if forma == "linear":
        valores = np.minimum(d, horizonte_dias) / horizonte_dias
    elif forma == "exponencial":
        valores = 1.0 - np.exp(-d / horizonte_dias)
    else:
        raise ValueError("forma deve ser 'linear' ou 'exponencial'")
    return pd.Series(valores, index=datas)


def portao_volume(volume: pd.Series, threshold: float) -> pd.Series:
    """Portão de liquidez: 1.0 se volume ≥ threshold, senão 0.0.

    É veto, não fator gradual: mercado sem liquidez mínima invalida o
    preço como probabilidade, e nenhum outro ingrediente compensa isso
    (estrutura multiplicativa registrada na Decisão 6). O valor do
    threshold é parâmetro em calibração, sem default.
    """
    if threshold <= 0:
        raise ValueError("threshold deve ser positivo")
    return (volume >= threshold).astype(float)


def combinar_por_rank(scores: list[pd.Series]) -> pd.Series:
    """Combina scores heterogêneos num score único via produto de ranks.

    Cada score é convertido ao seu rank percentual (transformação
    monótona, sem constantes arbitrárias) e os ranks são multiplicados —
    preservando a semântica de veto: um portão em 0 zera o rank e mata a
    combinação. Datas com NaN em qualquer score ficam NaN.

    Ferramenta do harness para comparar combinações na calibração; NÃO é
    a fórmula final do Ω (normalização é fechada na Decisão 6).
    """
    if not scores:
        raise ValueError("é preciso ao menos um score para combinar")
    combinado = None
    for s in scores:
        rank = s.rank(pct=True)
        # rank() ignora zeros do portão como valores comuns; para manter o
        # veto, zero explícito no score vira zero no rank
        rank = rank.where(s != 0.0, 0.0)
        combinado = rank if combinado is None else combinado * rank
    return combinado


# ---------------------------------------------------------------------------
# Teste de monotonicidade — o critério que escolhe entre candidatas
# ---------------------------------------------------------------------------


@dataclass
class ResultadoMonotonicidade:
    """Resultado do teste de uma candidata.

    - `spearman`: correlação de posto entre score e erro realizado
      (quanto mais negativa, melhor a candidata).
    - `erro_por_faixa`: erro realizado médio em cada faixa de confiança
      (da faixa de menor score para a de maior).
    - `monotonica`: True se o erro médio é não-crescente da faixa de
      menor confiança para a de maior.
    - `n_observacoes`: pares (score, erro) válidos usados no teste.
    """

    spearman: float
    erro_por_faixa: pd.Series
    monotonica: bool
    n_observacoes: int


def avaliar_monotonicidade(
    score: pd.Series, erro_futuro: pd.Series, n_faixas: int
) -> ResultadoMonotonicidade:
    """Avalia se confiança maior corresponde a erro realizado menor.

    Alinha as duas séries pelas datas, descarta NaN, calcula a correlação
    de Spearman (score × erro) e o erro médio por faixa de score
    (quantis). A candidata "passa" quando spearman < 0 e o erro médio cai
    (ou ao menos não sobe) ao subir de faixa.
    """
    if n_faixas < 2:
        raise ValueError("n_faixas deve ser pelo menos 2")
    dados = pd.concat({"score": score, "erro": erro_futuro}, axis=1).dropna()
    if len(dados) < n_faixas:
        raise ValueError("menos observações válidas do que faixas")

    # Spearman = Pearson sobre os ranks (com empates em rank médio);
    # calculado assim para não depender de scipy
    spearman = float(dados["score"].rank().corr(dados["erro"].rank()))
    # duplicates="drop": scores com muitos empates (ex.: portão binário)
    # produzem menos faixas do que o pedido, em vez de erro
    faixas = pd.qcut(dados["score"], n_faixas, labels=False, duplicates="drop")
    erro_por_faixa = dados["erro"].groupby(faixas).mean()
    diferencas = erro_por_faixa.diff().dropna()
    monotonica = bool((diferencas <= 0).all())

    return ResultadoMonotonicidade(
        spearman=spearman,
        erro_por_faixa=erro_por_faixa,
        monotonica=monotonica,
        n_observacoes=len(dados),
    )


def comparar_candidatas(
    candidatas: dict[str, pd.Series],
    erro_futuro: pd.Series,
    n_faixas: int,
) -> pd.DataFrame:
    """Roda o teste de monotonicidade para cada candidata e ranqueia.

    Devolve um DataFrame indexado pelo nome da candidata, ordenado da
    melhor (spearman mais negativo) para a pior, com as colunas
    `spearman`, `monotonica` e `n_observacoes`. O desempate por
    simplicidade (menos parâmetros) é aplicado por quem decide, fora do
    código — o ranking aqui é só o critério estatístico.
    """
    if not candidatas:
        raise ValueError("é preciso ao menos uma candidata")
    linhas = {}
    for nome, score in candidatas.items():
        resultado = avaliar_monotonicidade(score, erro_futuro, n_faixas)
        linhas[nome] = {
            "spearman": resultado.spearman,
            "monotonica": resultado.monotonica,
            "n_observacoes": resultado.n_observacoes,
        }
    tabela = pd.DataFrame.from_dict(linhas, orient="index")
    return tabela.sort_values("spearman")
