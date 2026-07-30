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


def load_pmf(directory, prefix):
    """Monta a matriz slots × buckets de um mercado multi-token.

    `prefix` é o começo do nome dos arquivos do mercado (ex. `"M3_fed_trajectory_"`,
    `"CPI_july-inflation-monthly_"`); o nome do arquivo é
    `<prefix><slug do bucket>_<tokenId>.json`, então o slug sai por recorte.

    Devolve DataFrame com uma coluna por bucket, ordenado pelo valor numérico
    do slug (`bucket_value`) e indexado pelo slot. **NaN onde o bucket não tem
    leitura naquele slot** — inclui tanto a faixa que morreu quanto a leitura
    faltante pontual. Nada é preenchido nem zerado aqui (decisão 6.1).
    """
    arquivos = sorted(Path(directory).glob(f"{prefix}*.json"))
    if not arquivos:
        raise FileNotFoundError(f"nenhum arquivo com prefixo {prefix!r} em {directory}")
    colunas = {}
    for arquivo in arquivos:
        slug = arquivo.stem[len(prefix):].rsplit("_", 1)[0]
        colunas[slug] = series_by_slot(arquivo)
    pmf = pd.DataFrame(colunas)
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
