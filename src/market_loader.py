"""Leitura do dado de mercado do pipeline do Paulo — ETFs e FRED (módulo do Felipe).

Contraparte do `poly_loader.py` para o que não vem do Polymarket. Só LEITURA
e formato; nenhuma decisão metodológica mora aqui (calendário de pregão,
preenchimento de feriado, unidade de comparação e horizonte são de quem
consome).

Onde está o dado: os arquivos vivem no branch `Paulo`, não neste. Para rodar
sem fazer merge, extraia para um diretório temporário:

    git archive origin/Paulo data/ | tar -x -C <dir temporario>

CONFERIDO no dado entregue (`origin/Paulo` @ a9be92b, follow-up 2, G1 e G2):

  ETFs — dois parquets irmãos, mesmo formato longo (`data`, `ticker`, valor):
    - `etf_prices_daily.parquet` : `preco_ajustado` (fechamento)
    - `etf_open_daily.parquet`   : `preco_abertura`
    Os dois em base AJUSTADA (`auto_adjust=True`), 9 tickers × 5.681 datas =
    51.129 linhas, 2003-12-05 → 2026-07-08, **mesmo grid de datas** (merge
    externo dá 0 sobra dos dois lados) e zero abertura ausente.
    ⚠️ Mas **não na mesma base de ajuste**: os arquivos foram baixados com
    ~3 semanas de diferença e um ex-dividendo no meio reescalou a história
    de um só. Ver `adjustment_gap` — misturar abertura e fechamento fabrica
    retorno intradiário em TIP e TLT.

  FRED — CSV público (`fredgraph.csv?id=<ID>`), cru, cabeçalho
  `observation_date,<ID>`:
    - `fred_T10YIE.csv` : breakeven de 10 anos — benchmark da view 2.2
    - `fred_DGS10.csv`  : Treasury 10 anos  } spread 10a−3m da view 3.1
    - `fred_DTB3.csv`   : T-bill 3 meses    }
    Feriado/dia sem dado vem como **campo VAZIO** (a linha existe, o valor
    depois da vírgula é string vazia) — não como `"."`, e não como linha
    faltando. Medido: 253 vazios em 6.152 linhas (T10YIE), 719 em 16.848
    (DGS10), 799 em 18.934 (DTB3). Vira NaN aqui e NÃO é preenchido.

UNIDADE (armadilha conhecida — o mesmo tipo de erro que a correção de unidade
da 2.2 em 2026-07-30): o FRED entrega **pontos percentuais** (4.25 = 4,25%).
A view 3.1 usa o spread nessa mesma unidade, mas a 2.2 pede `breakeven_10y`
em **fração decimal** — quem chama a 2.2 divide por 100. A série sai daqui
como o arquivo traz, sem conversão silenciosa.
"""

from pathlib import Path

import pandas as pd

CHAVES_ETF = ["data", "ticker"]


def load_etf_prices(path):
    """Parquet longo dos 9 ETFs → tabela larga `datas × tickers`.

    Serve aos dois arquivos (fechamento e abertura): a coluna de valor é a
    única que não é chave, então sai por dedução em vez de nome fixo.
    """
    precos = pd.read_parquet(path)
    valor = [c for c in precos.columns if c not in CHAVES_ETF]
    if len(valor) != 1:
        raise ValueError(
            f"esperava uma coluna de valor além de {CHAVES_ETF}; achei {valor}"
        )
    return precos.pivot(index="data", columns="ticker", values=valor[0]).sort_index()


def adjustment_gap(abertura, fechamento):
    """Mediana de `abertura/fechamento − 1` por ticker: detector de base
    de ajuste diferente entre os dois parquets.

    MEDIDO em 2026-08-04, e o motivo desta função existir: os dois arquivos
    NÃO estão na mesma base. O `etf_prices_daily.parquet` foi gerado em
    2026-07-09 (commit `48cb12e`) e o `etf_open_daily.parquet` em 2026-08-02
    (`7ea4e86`); entre um download e outro passou um ex-dividendo, e o
    `auto_adjust=True` reescala TODA a história anterior à data-ex. O
    resultado é um degrau: até ~2026-06-01 a abertura fica sistematicamente
    abaixo do fechamento, e depois disso a razão vai a 1.

        TIP −1,15%  ·  TLT −0,40%   (os dois pagam mensalmente)
        demais 7 tickers: −0,13% a +0,05% (ruído intradiário normal)

    Consequência: `abertura(D) → fechamento(D)` em TIP e TLT vira retorno
    FABRICADO de +1,15% / +0,40% por dia em toda a amostra antiga (e o
    espelho no overnight). Fechamento contra fechamento não é afetado.

    Não é bug do pipeline do Paulo (módulo dele; nada aqui mexe nisso) — é
    consequência de baixar os dois arquivos em datas diferentes. O conserto
    é re-baixar os dois no mesmo pull; a observação está registrada no
    `LOG.md` para o dono do módulo.

    Sem número mágico: a função devolve a medida, quem lê decide o que é
    tolerável.
    """
    check_same_grid(abertura, fechamento)
    return (abertura / fechamento).median() - 1.0


def check_same_grid(abertura, fechamento):
    """Falha alto se as duas tabelas largas não descrevem o mesmo grid."""
    if not abertura.index.equals(fechamento.index):
        raise ValueError("abertura e fechamento em grids de data diferentes")
    if list(abertura.columns) != list(fechamento.columns):
        raise ValueError("abertura e fechamento com universos diferentes")


def load_fred(path):
    """CSV cru do FRED → Series indexada por data, com o vazio virando NaN.

    O nome da Series é o ID da série (`T10YIE`, `DGS10`, `DTB3`), que é o
    próprio cabeçalho da segunda coluna. Feriado fica NaN: preencher (ou
    juntar ao calendário de pregão) é decisão de quem consome, não daqui.
    """
    serie = pd.read_csv(Path(path), parse_dates=["observation_date"],
                        index_col="observation_date")
    if serie.shape[1] != 1:
        raise ValueError(f"esperava uma coluna de valor no CSV do FRED; achei {list(serie.columns)}")
    coluna = serie.columns[0]
    return pd.to_numeric(serie[coluna], errors="raise").rename(coluna).sort_index()
