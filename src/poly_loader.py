"""Leitura do dado cru do Polymarket (módulo do Felipe).

O pipeline do Paulo entrega os arquivos do `/prices-history` CRUS, um JSON por
tokenId (`{"history": [{"t": <unix>, "p": <preço>}, ...]}`), sem tratamento —
combinado no `Pedido_Paulo_dados.md`: o tratamento é a jusante, aqui.

Este módulo faz só a LEITURA e o ALINHAMENTO. Nenhuma decisão metodológica
mora aqui: normalização da PMF, correção de viés e valor de bucket aberto
seguem em `poly_preprocessing.py`, atrás das decisões 11a/11b/6.1.

MEDIDO no dado entregue (`origin/Paulo` @ 90c7574, auditoria de 2026-07-30):
  - grade de 12h em 00:00 e 12:00 UTC, com deriva de POUCOS SEGUNDOS no
    timestamp (t % 43200 entre 3 e 9 s). Cada bucket de uma PMF é um token
    com book próprio, e a deriva DIFERE entre buckets do mesmo mercado —
    por isso alinhar por `t` cru não junta as colunas; alinha-se por SLOT.
  - buckets morrem no meio da vida do mercado (M3: "no cuts" morre em
    2025-09-17, "1 cut" em 2025-10-29, os demais seguem até dezembro) —
    aqui isso vira NaN na coluna, nunca zero (o que a faixa morta significa
    é a decisão 6.1, não é escolha de quem lê o arquivo).
  - além da faixa que morre, existe faixa que SOME E VOLTA: nos meses de
    grade nova (mar/2026, 6 buckets; abr/2026, 9) os buracos são internos e
    não coincidem entre buckets — mar/2026 tem só 24 de 60 slots com todos
    os buckets precificados (abr/2026: 42 de 63). Nos meses de 2025 com
    grade de 5/6 buckets isso não acontece (M1 fecha 56/56). Também vira
    NaN: é o mesmo insumo da decisão 6.1, num caso que ela ainda não cobre.
  - leituras faltantes pontuais de 24/36/48h existem; NÃO são preenchidas.

REGRA DE ALINHAMENTO DIÁRIO (decidida pelo Felipe em 2026-07-30, escopo do
próprio módulo): o valor do pregão D é o slot das **12:00 UTC da data D** —
07:00/08:00 em Nova York, o ponto mais recente que fecha ANTES da abertura.
Sem lookahead por construção. O slot das 00:00 UTC (19:00/20:00 ET do dia
anterior) também é pré-abertura, mas 12h mais velho; fica disponível pela
série de slots completa, para quem precisar dele (ex.: gap de fim de semana).
"""

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

# Grade do /prices-history com fidelity=720 (12h), em segundos.
SLOT_SECONDS = 12 * 3600
# Tolerância de deriva em torno da borda do slot. O medido é de segundos; 5 min
# é folga larga e ainda barra arquivo em outra granularidade (os 10 min que a
# API dá em mercado vivo), que colapsaria vários pontos no mesmo slot.
SLOT_TOLERANCE = 300


def load_history(path):
    """Lê um JSON cru do `/prices-history`. Devolve `(t, p)` como ndarrays.

    `t` em segundos unix (UTC), `p` o midpoint em [0, 1]. Mercado sem série
    (M9, entregue como `{"history": []}`) devolve dois arrays vazios — é
    ausência de dado, não erro de leitura.
    """
    history = json.loads(Path(path).read_text(encoding="utf-8"))["history"]
    t = np.array([ponto["t"] for ponto in history], dtype=np.int64)
    p = np.array([ponto["p"] for ponto in history], dtype=float)
    return t, p


def to_slots(t, tolerance=SLOT_TOLERANCE):
    """Mapeia timestamps para o índice do slot de 12h mais próximo.

    Arredonda (não trunca): a deriva medida é positiva, mas arredondar cobre
    os dois lados sem depender disso. Ponto a mais de `tolerance` da borda
    levanta erro — é sinal de outra granularidade, e empurrá-lo para um slot
    de 12h inventaria alinhamento que não existe.
    """
    t = np.asarray(t, dtype=np.int64)
    slots = np.rint(t / SLOT_SECONDS).astype(np.int64)
    desvio = np.abs(t - slots * SLOT_SECONDS)
    if desvio.size and desvio.max() > tolerance:
        pior = int(np.argmax(desvio))
        raise ValueError(
            f"timestamp {int(t[pior])} está a {int(desvio[pior])}s da grade de 12h "
            f"(tolerância {tolerance}s) — série não está em fidelity=720"
        )
    return slots


def slot_timestamps(slots):
    """Índice canônico (DatetimeIndex UTC) dos slots — descarta a deriva."""
    return pd.to_datetime(np.asarray(slots, dtype=np.int64) * SLOT_SECONDS,
                          unit="s", utc=True)


def series_by_slot(path):
    """Série de um token indexada pelo timestamp canônico do slot.

    MEDIDO no dado do Paulo: em mercado ainda VIVO, a API acrescenta um último
    ponto no instante do download, fora da grade de 12h (8 arquivos: os 7
    buckets do CPI de jul/2026 e o mercado da Câmara 2026, com 3.410 a 4.431 s
    de desvio; sempre o último ponto, nunca no meio). Esse ponto é descartado —
    ele não é um slot e alinhá-lo a um inventaria uma leitura que não existe.

    Slot repetido (não observado no dado atual, mas possível se a API devolver
    dois pontos na mesma janela) fica com a ÚLTIMA leitura.
    """
    t, p = load_history(path)
    if t.size and abs(int(t[-1]) - round(t[-1] / SLOT_SECONDS) * SLOT_SECONDS) > SLOT_TOLERANCE:
        t, p = t[:-1], p[:-1]
    slots = to_slots(t)
    serie = pd.Series(p, index=slot_timestamps(slots))
    return serie[~serie.index.duplicated(keep="last")].sort_index()


def load_pmf(directory, prefix, ordenar=True):
    """Monta a matriz slots × buckets de um mercado multi-token.

    `prefix` é o começo do nome dos arquivos do mercado (ex. `"M3_fed_trajectory_"`,
    `"CPI_july-inflation-monthly_"`); o nome do arquivo é
    `<prefix><slug do bucket>_<tokenId>.json`, então o slug sai por recorte.

    Devolve DataFrame com uma coluna por bucket, ordenado pelo valor numérico
    do slug (`bucket_value`) e indexado pelo slot. **NaN onde o bucket não tem
    leitura naquele slot** — inclui tanto a faixa que morreu quanto a leitura
    faltante pontual. Nada é preenchido nem zerado aqui (decisão 6.1).

    `ordenar=False` pula o `bucket_value` e devolve as colunas na ordem do
    arquivo. Existe pelos mercados de payrolls do G9: o Paulo os salvou **sem
    o slug do balde** (`<prefix><tokenId>.json`), então não há rótulo de onde
    tirar valor numérico. Serve para medida que não usa valor de balde — a
    entropia normalizada é invariante à ordem e à renormalização (é por isso
    que a tática de prêmio foi escrita em cima dela). **Não serve para view**:
    P e Q precisam dos valores alinhados.
    """
    arquivos = sorted(Path(directory).glob(f"{prefix}*.json"))
    if not arquivos:
        raise FileNotFoundError(f"nenhum arquivo com prefixo {prefix!r} em {directory}")
    colunas = {}
    for arquivo in arquivos:
        slug = arquivo.stem[len(prefix):].rsplit("_", 1)[0]
        colunas[slug] = series_by_slot(arquivo)
    pmf = pd.DataFrame(colunas)
    if not ordenar:
        return pmf
    # bucket aberto (valor NaN) vai para o fim — hoje só existe como ponta
    # superior ("8plus"); NaN como chave de ordenação embaralharia as colunas.
    return pmf[sorted(pmf.columns, key=lambda s: np.nan_to_num(bucket_value(s), nan=np.inf))]


def daily_preopen(serie):
    """Aplica a regra de alinhamento diário: slot das 12:00 UTC de cada data.

    Aceita Series ou DataFrame indexado por slot (saída de `series_by_slot` /
    `load_pmf`) e devolve o mesmo objeto indexado por DATA (sem timezone),
    contendo só o ponto pré-abertura de cada dia.

    Datas sem o slot das 12:00 UTC (leitura faltante) simplesmente não
    aparecem — quem decide o que fazer com o buraco é o backtest, não este
    módulo. O join com o calendário de pregão também é lá: aqui vem toda data
    corrida, inclusive fim de semana e feriado (que é justamente o insumo da
    tática de gap de fim de semana).
    """
    preopen = serie[serie.index.hour == 12]
    return preopen.set_axis(preopen.index.tz_convert(None).normalize())


def diagnostics_qualidade(pmf_cru, decisao, janela_slots=None, dias_ate_evento=np.nan):
    """Bloco de qualidade da leitura para o Ω da Lia (spec dela de 2026-08-07).

    Mede na série CRUA — saída de `load_pmf`, passo nativo de 12h, com NaN nos
    buracos. É de propósito, e é o ponto central desta função: depois do
    `carry_missing` não existe mais buraco para contar, e depois do
    `daily_preopen` sobra 1 ponto por dia em vez de 2. O que a Lia mede é a
    qualidade do dado que ENTROU, não a do dado já consertado.

    Regra geral dela, aplicada em todos os campos: **desconhecido = NaN, nunca
    0** — zero é valor informativo na régua (zera o produto).

    `decisao`      : data do rebalanceamento (naive) ou o slot exato (tz-aware).
                     Naive vira o slot das 12:00 UTC daquela data, que é o ponto
                     pré-abertura que a view usa (regra de alinhamento do módulo).
    `janela_slots` : N nominal. A janela é os N slots que terminam NO slot da
                     decisão, inclusive — o slot da decisão é informação
                     disponível, não lookahead. **None = vida inteira do mercado
                     até a decisão**, e é o default de propósito: o tamanho da
                     janela é output da calibração de monotonicidade da LIA, não
                     número meu para cravar (CLAUDE.md §6). Mandando a série
                     inteira, ela rejanela do lado dela sem ida e volta — que é
                     exatamente o motivo pelo qual ela pediu `serie_janela` cru.

    `n_slots_esperados_janela` é truncado pelo início da série: mercado que
    nasceu há 3 slots espera 3, não N. É o que separa "buraco de leitura" de
    "mercado ainda não existia" — a Lia calcula `esperados − pontos` e precisa
    que a diferença seja só a primeira coisa.

    `dp_variacao_janela` sai NaN em mercado multi-bucket: colapsar a PMF num
    escalar `p` é transformação da régua dela, não minha (mesmo argumento com
    que ela pediu `soma_faixas` cru). Só é calculado quando a série tem uma
    coluna só, caso em que o `p` é inequívoco. Ver pergunta aberta no LOG.
    """
    decisao = pd.Timestamp(decisao)
    if decisao.tz is None:
        decisao = decisao.normalize().tz_localize("UTC") + pd.Timedelta(hours=12)
    slot = pd.Timedelta(hours=12)
    nascimento = pmf_cru.index.min() if len(pmf_cru.index) else decisao
    inicio = nascimento if janela_slots is None else decisao - slot * (janela_slots - 1)

    janela = pmf_cru[(pmf_cru.index >= inicio) & (pmf_cru.index <= decisao)]
    # linha sem NENHUM bucket precificado não é leitura; é buraco com carimbo.
    pontos = janela.dropna(how="all")

    esperados = int((decisao - max(inicio, nascimento)) / slot) + 1

    if len(pontos):
        idade_h = (decisao - pontos.index[-1]) / pd.Timedelta(hours=1)
    else:
        idade_h = np.nan  # sem ponto na janela: idade é desconhecida, não 0

    uma_coluna = pontos.shape[1] == 1 if pontos.ndim == 2 else True
    if uma_coluna and len(pontos) > 1:
        p = pontos.iloc[:, 0] if pontos.ndim == 2 else pontos
        dp_variacao = float(p.diff().std())
    else:
        dp_variacao = np.nan

    return {
        "serie_janela": [(t, linha.to_dict()) for t, linha in pontos.iterrows()],
        "n_pontos_janela": int(len(pontos)),
        "n_slots_esperados_janela": esperados,
        "janela_slots": None if janela_slots is None else int(janela_slots),
        "idade_ultimo_ponto_h": float(idade_h),
        "dp_variacao_janela": dp_variacao,
        "dias_ate_evento": float(dias_ate_evento),
    }


def load_cpi_releases(path):
    """Calendário de divulgação do CPI, com o erro de ano da fonte corrigido.

    O `cpi_release_dates.csv` do Paulo vem das *rules* dos próprios mercados
    do Polymarket (o BLS bloqueia raspagem — F7). Uma linha traz erro de
    digitação DA FONTE: o CPI de dez/2025 aparece com divulgação em
    2025-01-13, quando o certo é 2026-01-13 (confirmado pela série do
    mercado `december-inflation-us-monthly`, que termina nessa data). O
    Paulo manteve o arquivo cru e sinalizou, que é o procedimento certo —
    a correção é aqui, no tratamento.

    A regra é geral, não uma exceção com data cravada: **divulgação nunca
    precede o mês de referência**; quando precede, é ano errado, e soma-se
    um ano. Qualquer recorrência futura do mesmo typo cai na mesma regra.

    Devolve o DataFrame ordenado por data (o arquivo cru está fora de ordem,
    consequência do mesmo typo).
    """
    releases = pd.read_csv(path, parse_dates=["release_date"])
    referencia = pd.to_datetime(releases["mes_referencia"], format="%B %Y")
    ano_errado = releases["release_date"] < referencia
    releases.loc[ano_errado, "release_date"] += pd.DateOffset(years=1)
    return releases.sort_values("release_date").reset_index(drop=True)


# Remap do shutdown de 2025 no calendário de payrolls (G9a). A `release_date` é
# MEDIDA (FRED release id=50); só o `mes_referencia` é DERIVADO pelo Paulo por
# "mês do release − 1", e a derivação quebra numa janela — ele marcou cru e
# sinalizou, como combinado, e a correção é aqui no tratamento.
#
# O que aconteceu: o shutdown de 2025 abriu um buraco de 76 dias (2025-09-05 ->
# 2025-11-20) e o BLS remanejou o cronograma. Quatro releases normais viraram
# três, então "mês − 1" desalinha.
#
# NÃO é regra derivável (ao contrário do typo de ano do CPI, que cai em
# "divulgação nunca precede o mês de referência"): é fato histórico. Fica como
# exceção declarada, com validação — se o arquivo mudar, a correção não se
# aplica calada.
#
# Corroborado pelo PRÓPRIO dado do G9b, sem fonte externa: out/2025 é o único
# mês da varredura com "só meta" e NENHUM mercado do número — exatamente o que
# se espera de um mês sem release próprio.
_SHUTDOWN_2025 = {
    # release        -> (mes_referencia correto, nota)
    "2025-11-20": ("September 2025",
                   "release de setembro atrasado pelo shutdown (o cru dizia October)"),
    "2025-12-16": ("November 2025",
                   "release COMBINADO out+nov; outubro não teve release próprio "
                   "e a taxa de desemprego de outubro nunca foi publicada"),
}


def load_payroll_releases(path):
    """Calendário de divulgação do Employment Situation, com o shutdown de 2025
    corrigido. Espelha `load_cpi_releases`: o Paulo entrega cru, a correção é aqui.

    Devolve o DataFrame ordenado por data, com duas colunas a mais:
      - `mes_referencia_cru` : o que veio do arquivo (auditoria)
      - `nota_tratamento`    : por que a linha foi corrigida (vazio se não foi)

    **Outubro/2025 não ganha linha**: o payroll de outubro saiu DENTRO do release
    de 2025-12-16, não em release próprio. Inventar uma linha para ele criaria um
    evento que não existe no calendário — e o `-` honesto vale mais.
    """
    releases = pd.read_csv(path, parse_dates=["release_date"])
    releases["mes_referencia_cru"] = releases["mes_referencia"]
    releases["nota_tratamento"] = ""

    chaves = releases["release_date"].dt.strftime("%Y-%m-%d")
    for data, (correto, nota) in _SHUTDOWN_2025.items():
        alvo = chaves == data
        if not alvo.any():
            continue  # arquivo sem essa linha: nada a corrigir, e não é erro
        # A nota vale mesmo quando o mês derivado já saiu certo: 2025-12-16 cai
        # em "November" pela regra do Paulo e está certo para o payroll de
        # novembro, MAS foi um release combinado out+nov — quem lê o calendário
        # precisa saber disso mesmo sem haver o que corrigir.
        releases.loc[alvo, "mes_referencia"] = correto
        releases.loc[alvo, "nota_tratamento"] = nota

    # Validação: fora da janela do shutdown, "mês do release − 1" TEM de valer.
    # Se parar de valer, o arquivo mudou de forma e a exceção acima virou chute.
    referencia = pd.to_datetime(releases["mes_referencia"], format="%B %Y")
    esperado = (releases["release_date"].dt.to_period("M") - 1).dt.to_timestamp()
    desvio = (referencia != esperado) & (releases["nota_tratamento"] == "")
    if desvio.any():
        ruins = releases.loc[desvio, "release_date"].dt.date.tolist()
        raise ValueError(
            f"mes_referencia não bate com 'mês do release − 1' fora da janela do "
            f"shutdown: {ruins} — o arquivo do Paulo mudou de forma e o remap "
            f"declarado em _SHUTDOWN_2025 precisa ser revisto, não aplicado cego")
    return releases.sort_values("release_date").reset_index(drop=True)


# `0pt3` -> 0.3 ; `1pt0` -> 1.0
_DECIMAL = re.compile(r"(\d+)pt(\d+)")
# CPI: `...-increase-by-0pt3`, `...-decrease-by-0pt2`, `...-stay-flat-0pt0-in`
_CPI = re.compile(r"(increase|decrease|stay-flat)-(?:by-)?(\d+pt\d+)")
# Fed: `will-3-fed-rate-cuts-...`, `will-no-fed-rate-cuts-...`, `will-8plus-...`
_FED = re.compile(r"will-(no|\d+plus|\d+)-fed-rate-cuts?")


def bucket_value(slug):
    """Valor numérico do bucket a partir do slug do mercado.

    CPI (em pontos percentuais de variação mensal) e nº de cortes do Fed —
    as duas grades de bucket entregues. Devolve **NaN para bucket aberto**
    (`8plus`), que é exatamente o que `poly_preprocessing.pmf_mean` rejeita
    citando a decisão 11b: o valor de faixa aberta é decisão humana, não
    leitura de arquivo.

    ATENÇÃO (decisão 11b, medido na varredura de 17 meses): as pontas da grade
    de CPI também são ABERTAS pelas regras do mercado ("0,1% ou menos"), mas o
    slug não diz isso — sai `increase-by-0pt1` igual a um bucket interno.
    Quais pontas tratar como abertas vem das regras do mercado, não daqui.

    A grade do CPI muda mês a mês (3 a 9 buckets, deslocamento em mar/2026 e
    INVERSÃO DE SINAL em jul/2026, quando os rótulos passam a falar em queda) —
    por isso o valor sai do slug de cada arquivo, nunca de tabela fixa.
    """
    cpi = _CPI.search(slug)
    if cpi:
        direcao, numero = cpi.groups()
        valor = float(_DECIMAL.sub(r"\1.\2", numero))
        return -valor if direcao == "decrease" else valor
    fed = _FED.search(slug)
    if fed:
        quantidade = fed.group(1)
        if quantidade == "no":
            return 0.0
        if quantidade.endswith("plus"):
            return float("nan")  # bucket aberto — decisão 11b
        return float(quantidade)
    raise ValueError(f"slug não reconhecido: {slug!r}")
