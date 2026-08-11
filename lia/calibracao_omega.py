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


def preparar_pmf(pmf: pd.DataFrame) -> pd.DataFrame:
    """Descarta linha incompleta e renormaliza o que sobra (Decisão 6e).

    `pmf` : slots × faixas, CRU (NaN onde não houve leitura), na **grade
            completa** — uma linha por slot esperado. É o contrato do
            `load_fomc_pmf`/`load_pmf` do pipeline; a grade completa é o que
            permite `.diff()` comparar vizinhos de verdade.

    Duas regras, ambas da 6e:

    1. **Linha com qualquer faixa ausente sai inteira** (vira NaN), em vez de
       ser imputada por `carry_missing`/`ffill`. Repetir a última leitura
       injetaria variação zero, e o erro seria num sentido só: mercado
       esburacado pareceria mais estável — a mesma inversão de sinal do
       midpoint (6b), por outra porta. O buraco continua custando confiança
       pelo canal próprio (`n_slots_esperados − n_pontos`), uma vez só.
    2. **Renormaliza** (`p_b / Σ p_b`) o que sobra. Sem isso o colapso
       mistura movimento de opinião com desarranjo do livro, e a régua
       multiplicativa puniria a mesma coisa duas vezes — o desarranjo é
       inteiramente do `score_coerencia`.

    A linha descartada some do cálculo de variação e, de quebra, torna o par
    seguinte não-adjacente, que é o tratamento já registrado na 6a.
    """
    completa = pmf.notna().all(axis=1)
    limpa = pmf.where(completa, other=np.nan)
    return limpa.div(limpa.sum(axis=1), axis=0)


def variacao_total(pmf: pd.DataFrame) -> pd.Series:
    """Candidata (a) do colapso PMF→p: `0,5 · Σ_b |p_{t,b} − p_{t−1,b}|`.

    Distância de variação total entre PMFs consecutivas — a fração da massa
    de probabilidade que mudou de faixa entre um slot e o outro. Sem
    parâmetro livre, ∈ [0, 1], e **degenera exatamente em `|p_t − p_{t−1}|`
    quando há duas faixas**, que é a definição original do
    `dp_variacao_janela`. Não usa a ordem das faixas: mover massa para a
    vizinha pesa igual a mover para a ponta oposta.

    `pmf` deve vir de `preparar_pmf`. Par com qualquer ponta ausente sai
    NaN (`skipna=False`), o que descarta os não-adjacentes.
    """
    return 0.5 * pmf.diff().abs().sum(axis=1, skipna=False)


def variacao_valor_esperado(pmf: pd.DataFrame, valores) -> pd.Series:
    """Candidata (b) do colapso PMF→p: `|E_t − E_{t−1}|`, `E = Σ_b p_b·x_b`.

    Movimento na grandeza que o `Q` de fato consome, e não na PMF inteira.
    Usa a ordem e a distância entre as faixas, que a (a) ignora — em troca,
    herda o tratamento da ponta aberta (ponto médio extrapolado, decisão
    provisória de 04/08): se esta candidata vencer, a revisão daquela
    decisão obriga recalibrar. Trata como estável a PMF que espalha massa
    simetricamente.

    `valores` : valor numérico de cada faixa, na ordem das colunas.
    """
    valores = np.asarray(valores, dtype=float)
    if valores.shape != (pmf.shape[1],):
        raise ValueError(
            f"um valor por faixa: {valores.shape} vs ({pmf.shape[1]},)")
    esperado = pmf.mul(valores, axis=1).sum(axis=1, skipna=False)
    return esperado.diff().abs()


def score_estabilidade_pmf(variacao: pd.Series, janela: int) -> pd.Series:
    """Score de estabilidade a partir de uma série de variações por slot.

    Definição: **−média** das variações na janela. Quanto menos o mercado se
    move entre leituras, maior o score (máximo 0.0, série parada).

    Por que média e não desvio-padrão, como no `score_estabilidade` da série
    escalar: as duas candidatas de colapso são não-negativas por construção
    (é `|·|` nas duas), e o desvio-padrão de uma quantidade não-negativa
    mede a irregularidade do movimento, não o movimento. A média preserva a
    degeneração no caso binário — `média|Δp|`.

    Esta é a régua de produção para TODAS as views, inclusive as de faixa
    única: PMF de duas colunas cai aqui pela mesma fórmula. O campo
    `dp_variacao_janela` do `diagnostics` não é consumido em caso nenhum,
    para não haver duas estimativas da mesma quantidade no sistema.
    """
    if janela < 1:
        raise ValueError("janela deve ter pelo menos 1 período")
    return -variacao.rolling(janela, min_periods=janela).mean()


def score_coerencia(
    soma_cru: pd.Series, linha_completa: pd.Series
) -> pd.Series:
    """Score de coerência do livro: `−|soma_cru − 1|`, só em linha completa.

    Mede desarranjo entre as faixas — cada uma é um livro separado e elas se
    desencontram (medido: 0,953 a 1,143 nas linhas completas do FOMC; até
    1,325 no mercado de cortes). É bilateral de propósito: soma acima de 1 é
    tão desarranjada quanto abaixo, e o piso de sanidade da cascata do
    Felipe (soma < 0,9 desativa a view) só corta por baixo — os dois atuam
    em regimes disjuntos (Decisão 6c).

    **NaN em linha incompleta** (Decisão 6e): ali a soma mede buraco, não
    desencontro, e buraco já é penalizado no canal próprio. Medido no dado:
    dos 25 dias com soma < 0,9 em 801, os 25 são linhas incompletas — zero
    livros completos somam abaixo de 0,9.
    """
    desvio = (soma_cru - 1.0).abs()
    return -desvio.where(linha_completa.astype(bool))


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
    """Portão de liquidez: 1.0 se volume ≥ threshold, 0.0 se abaixo, NaN sem dado.

    É veto, não fator gradual: mercado sem liquidez mínima invalida o
    preço como probabilidade, e nenhum outro ingrediente compensa isso
    (estrutura multiplicativa registrada na Decisão 6). O valor do
    threshold é parâmetro em calibração, sem default.

    **NaN entra e NaN sai** (Decisão 6b, 07/08/2026). No G5 as duas
    células vazias significam coisas opostas: `0` é pré-primeiro-trade
    (ninguém negociou — veta) e `NaN` é truncamento do cap de 20k trades
    (ignorância nossa, o dado existe — não veta). `NaN >= threshold` é
    False em pandas, então converter direto para float veta o truncamento
    e desfaz a separação — era este o defeito medido pelo Felipe em
    08/08, com 346 slots reais para mordê-lo.
    """
    if threshold <= 0:
        raise ValueError("threshold deve ser positivo")
    portao = (volume >= threshold).astype(float)
    return portao.where(volume.notna())


def agregar_volume_slot(long: pd.DataFrame) -> pd.DataFrame:
    """Agrega o volume das faixas de um evento em volume do slot.

    Recebe o G5 em formato long (colunas `evento`, `slot_utc`,
    `notional_usd`) e devolve `soma` e `minimo` por (evento, slot).

    **Faixa `NaN` contamina o slot inteiro** (Decisão 6b, generalizada ao
    slot em 10/08/2026). O G5 separa `0` (pré-primeiro-trade: ninguém
    negociou, veta) de `NaN` (truncamento do cap de 20k: o dado existe e
    nós é que não o alcançamos, não veta). Somar tratando `NaN` como
    ausente destrói a separação no agregado: um slot com uma faixa
    truncada e as demais em zero somaria zero e **vetaria**, afirmando
    "ninguém negociou" onde parte é desconhecida.

    Isso não aparecia na 2.2 — lá nenhuma faixa bateu o cap, e nenhum
    slot mistura os dois tipos de célula, então esta função reproduz
    exatamente a agregação anterior naquele dado. No FOMC, 42 das 76
    faixas bateram o cap: 908 slots de 3.905 misturam, e 6 deles
    receberiam veto espúrio pela regra ingênua.

    O `minimo` admite um caso a mais: se alguma faixa conhecida é zero, o
    mínimo é zero mesmo com outras desconhecidas — volume não é negativo,
    então nenhuma faixa faltante poderia baixá-lo. Só quando todas as
    conhecidas são positivas é que a faixa ausente pode esconder o mínimo.
    """
    grupos = long.groupby(["evento", "slot_utc"]).notional_usd
    completo = grupos.apply(lambda s: s.notna().all())
    soma = grupos.sum(min_count=1).where(completo)
    minimo = grupos.min()  # `min` já ignora NaN
    return pd.DataFrame({
        "soma": soma,
        "minimo": minimo.where(completo | (minimo == 0)),
    })


def combinar_por_rank(
    scores: list[pd.Series], veto: pd.Series | None = None
) -> pd.Series:
    """Combina scores GRADUAIS num score único via produto de ranks.

    Cada score é convertido ao seu rank percentual (transformação
    monótona, sem constantes arbitrárias) e os ranks são multiplicados.
    Datas com NaN em qualquer score ficam NaN.

    `veto` : saída de `portao_volume` (1.0 passa · 0.0 veta · NaN sem
             dado), aplicada como multiplicador DEPOIS da combinação. O
             portão não entra no produto de ranks porque não é um
             ingrediente ao lado dos outros: pela Decisão 6b ele é
             pré-condição do `score_estabilidade` — sem liquidez, o
             midpoint congela e a série ilíquida parece perfeitamente
             estável. NaN no portão **não veta** (vale 1.0): truncamento
             do cap é ignorância nossa, não iliquidez medida.

    **Zero num score NÃO é veto.** A versão anterior inferia veto de
    `score == 0.0`, o que invertia dois dos três ingredientes:
    `score_estabilidade` é −desvio-padrão, então 0.0 é o MELHOR valor
    possível (série parada), e `score_proximidade` vale 0.0 no dia do
    evento, onde a view deve ser amortecida e não cortada. Defeito
    medido pelo Felipe em 08/08; o veto agora é explícito e só o portão
    o produz.

    Ferramenta do harness para comparar combinações na calibração; NÃO é
    a fórmula final do Ω (normalização é fechada na Decisão 6).
    """
    if not scores:
        raise ValueError("é preciso ao menos um score para combinar")
    combinado = None
    for s in scores:
        rank = s.rank(pct=True)
        combinado = rank if combinado is None else combinado * rank
    if veto is not None:
        # NaN → 1.0: sem dado de volume não se veta (Decisão 6b). A
        # contagem de slots nessa situação é reportada por quem chama.
        combinado = combinado * veto.reindex(combinado.index).fillna(1.0)
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
