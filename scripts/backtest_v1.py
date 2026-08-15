"""Backtest do v1 — liga o motor do I5 no dado real do Paulo. Felipe.

O motor (`src/backtest.py`) é puro; toda a plumbing de dado mora aqui, que é
onde a responsabilidade de NÃO OLHAR O FUTURO também mora. Três regras que
este arquivo aplica em cada montagem do dia D:

  - a PMF é o slot das **12:00 UTC de D** (07:00/08:00 em Nova York), anterior
    tanto ao CPI (8:30 ET) quanto à abertura;
  - o breakeven e a curva vêm da última leitura **estritamente anterior** a D;
  - a média da divergência (D9) e a duration empírica são de janela
    **EXPANSIVA** — só com o que já tinha acontecido em D.

## O que roda e o que não roda hoje

| view | estado | por quê |
|---|---|---|
| **2.2 inflação** | **roda** | PMF de CPI + T10YIE + calendário, tudo entregue |
| **2.3 Fed** | **roda** (desde 2026-08-07) | PMF de decisão por reunião (`polymarket_fed_reunioes.parquet`) + `DTB3 − DFF` como `E_FF`, com a surpresa DEMEANADA |
| **15b incerteza** | **roda** (desde 2026-08-10) | entropia da PMF na véspera do anúncio; escala = entropia CRUA (D15c). Direcional (`P[SPY] = 2`), ratificada na D15b. Só existe em dia de anúncio: **27 pregões** |
| **15g B própria** | **roda** (desde 2026-08-10) | trajetória do Fed com β contra o ΔDGS1 — o vértice da pergunta, não os β da 2.3. Dupla leitura da PMF de reunião aceita na D15a; item 4 da D22 fechado na D22e. **210 pregões** |

A 2.3 destravou com o G8 (`DFF`), mas o que a fez virar view de Polymarket foi
outra coisa: a perna do poly é a **PMF completa por reunião** do parquet, não o
binário de −50bp do `clob_exploracao`. Com o binário, o poly explicava 4,6% da
variância da surpresa e o sinal era o mesmo em 100% dos dias; com a PMF, 53% e
o poly inverte o sinal do spread de bills.

A B saiu do v1 pela decisão 11 e **voltou em 2026-08-10** com β próprio: o que a
seção 11 barrava era o desenho que reusava os β da 2.3 (P literalmente idêntico),
não a view. Com o β contra o ΔDGS1 o ângulo é 87,5°–95,6°, e a objeção cai.

## Camada tática

Desligada por padrão. Os orçamentos (`--orcamento-*`) são **parâmetros de
reunião** (CLAUDE.md §6 — não se inventa número de modelo), então sem eles a
camada não entra e o backtest mede só o BL. Passar qualquer um liga a tática
correspondente.

Uso (o dado vive no branch `Paulo`, não neste):

    git archive origin/Paulo data/ | tar -x -C /tmp/dadospaulo
    python scripts/backtest_v1.py --raiz /tmp/dadospaulo --duration-breakeven <d>
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import view_2_2_inflacao  # noqa: E402
import view_2_3_fed  # noqa: E402
import view_B_trajetoria_propria  # noqa: E402
import view_C_geopolitica_energia  # noqa: E402
import view_incerteza_anuncio  # noqa: E402
from backtest import run_backtest, summary  # noqa: E402
from config import (ASSETS, CUSTO_BPS_POR_LADO, DELTA, DRIFT_JANELA_ACOES,  # noqa: E402
                    DRIFT_JANELA_RF, FL_GAMMA_V1, FL_GAMMA_VARREDURA,
                    SIGMA_JANELA_PREGOES, TAU)
from market_inputs import (breakeven_duration, daily_returns,  # noqa: E402
                           empirical_duration, market_weights,
                           regua_por_decisao, sample_covariance)
from market_loader import load_etf_prices, load_fred  # noqa: E402
from poly_loader import (bucket_value, daily_preopen, diagnostics_qualidade,  # noqa: E402
                         load_cpi_releases, load_fomc_pmf, load_payroll_releases,
                         load_pmf)
from poly_preprocessing import (bucket_values_with_open, carry_missing,  # noqa: E402
                                favorite_longshot_pmf, soma_faixas)
from views_common import full_absorption_beta, lag_regression  # noqa: E402
import tatica_drift_anuncio  # noqa: E402
import tatica_drift_pos_fomc  # noqa: E402
import tatica_premio_anuncios  # noqa: E402
import tatica_sleeves  # noqa: E402
from poly_preprocessing import pmf_mean  # noqa: E402

PONTOS_PERCENTUAIS = 100.0

# Camada tática RECONSTRUÍDA (sessão de 2026-08-08, direção da seção 14). Duas
# sleeves do mesmo template `tatica_drift_anuncio`, sem orçamento — o tamanho
# sai de δ e Σ. Os livros são onde a âncora de literatura existe; a janela é a
# de Neuhierl-Weber já registrada em `config.DRIFT_JANELA_ACOES` (15), TRANSPOSTA
# para o CPI por não haver número próprio medido — transporte declarado, não
# parâmetro novo (CLAUDE.md §6: não inventar valor).
DRIFT_LIVRO_FOMC = ("SPY", "TLT")
DRIFT_LIVRO_CPI = ("TIP", "TLT")

# --- views novas (candidatas das seções 15b e 15g), DESLIGADAS por default ----
#
# `views_novas=()` mantém a entrega da 12c/D13 intocada — nada abaixo desta
# linha roda no caminho padrão. Ligar é `views_novas=("incerteza", "B")`.
PREFIXO_M3 = "M3_fed_trajectory_"   # "will N fed rate cuts happen in 2025"

# O M3 pergunta quantos cortes acontecem DENTRO de 2025, então a taxa de fim de
# ano de um balde é `taxa do fim de 2024 − 25bp × N` — e NÃO a taxa de hoje
# menos 25bp × N, que contaria em dobro os cortes já feitos no ano corrente
# (em nov/2025, com 2 cortes já entregues, o erro é de 50 bps de nível).
# É leitura da REGRA do mercado, declarada aqui porque não estava escrita em
# lugar nenhum: a espec da B só dizia "taxa_atual".
M3_INICIO_DO_ANO = pd.Timestamp("2025-01-01")


def mercados_de_cpi(releases, diretorio):
    """(data de divulgação -> prefixo dos arquivos) — o slug sai da coluna
    `fonte` do calendário do Paulo, nunca de adivinhação por nome de arquivo.
    """
    pares = {}
    for _, linha in releases.iterrows():
        fonte = str(linha["fonte"])
        if "(" not in fonte:
            continue
        prefixo = f"CPI_{fonte[fonte.index('(') + 1: fonte.rindex(')')]}_"
        if list(Path(diretorio).glob(f"{prefixo}*.json")):
            pares[pd.Timestamp(linha["release_date"])] = prefixo
    return dict(sorted(pares.items()))


def pmf_diaria(diretorio, prefixo):
    """(probs por data, valores em fração MENSAL, série CRUA) de um mercado.

    Aplica as regras fechadas: faixa faltante herda a última leitura (D4/6.1)
    e faixa aberta entra a meia largura para fora (D4/1.2). Os valores saem em
    fração decimal mensal — a view anualiza sozinha (`cpi_frequencia`).

    A série CRUA sai junto porque o `diagnostics` do Ω da Lia tem de ser medido
    ANTES do tratamento: depois do `carry_missing` não há mais buraco para
    contar, e depois do `daily_preopen` sobram 1 ponto por dia em vez de 2. O
    que ela mede é a qualidade do dado que entrou, não a do já consertado.
    """
    cru = load_pmf(diretorio, prefixo)
    pmf = daily_preopen(carry_missing(cru)).dropna(how="all")
    valores = bucket_values_with_open(
        np.array([bucket_value(c) for c in pmf.columns], dtype=float))
    return pmf, valores / PONTOS_PERCENTUAIS, cru


def pmf_fomc_diaria(parquet):
    """{data da reunião: (probs por data, Δtaxa em bps, série CRUA)}.

    Mesmo tratamento da `pmf_diaria` do CPI, com as mesmas decisões fechadas:
    faixa faltante herda a última leitura (D4/6.1) e ponta aberta entra a meia
    largura para fora (D4/1.2) — aqui a máscara de ponta aberta vem do próprio
    título do mercado (`load_fomc_pmf`), porque a grade muda de reunião para
    reunião (4 ou 5 faixas, ponta inferior em −50+ ou −75+).

    A série CRUA sai junto pelo mesmo motivo do CPI: o `diagnostics` do Ω da
    Lia mede a qualidade do dado que ENTROU, antes do conserto.
    """
    saida = {}
    for probs, valores, abertos, reuniao in load_fomc_pmf(parquet).values():
        pontas = tuple(nome for nome, aberto in (("lower", abertos[0]),
                                                 ("upper", abertos[-1])) if aberto)
        diaria = daily_preopen(carry_missing(probs)).dropna(how="all")
        saida[reuniao] = (diaria, bucket_values_with_open(valores, open_ends=pontas), probs)
    return dict(sorted(saida.items()))


def pmf_m3_diaria(diretorio):
    """(probs por data, valores em nº de cortes) do M3_fed_trajectory.

    Mesmo tratamento das outras PMFs (D4/6.1 herda leitura faltante, D4/1.2
    resolve a ponta aberta). Só a ponta SUPERIOR é aberta ("8plus"); a inferior
    é "no fed rate cuts" = 0 exato, faixa fechada.
    """
    cru = load_pmf(diretorio, PREFIXO_M3)
    pmf = daily_preopen(carry_missing(cru)).dropna(how="all")
    valores = np.array([bucket_value(c) for c in pmf.columns], dtype=float)
    return pmf, bucket_values_with_open(valores, open_ends=("upper",)), cru


def entropias_de_anuncio(diretorio, prefixo, datas, familia, ordenar=True):
    """{data de anúncio: (entropia, família, soma crua)} — insumo da view 15b.

    Construção IDÊNTICA à da medição que justifica a view
    (`premio_condicional.eventos_com_incerteza`): entropia da PMF no slot
    pré-abertura do próprio dia do anúncio, sobre a série CRUA. Sem
    `carry_missing` de propósito — a entropia é invariante à renormalização e
    ignora balde sem leitura, então tratar a linha mediria o tratamento.
    """
    diario = daily_preopen(load_pmf(diretorio, prefixo, ordenar=ordenar))
    saida = {}
    for data in pd.DatetimeIndex(datas).intersection(diario.index):
        linha = diario.loc[data].to_numpy(dtype=float)
        h = view_incerteza_anuncio.entropia_normalizada(linha)
        if np.isfinite(h):
            saida[data] = (h, familia, soma_faixas(linha))
    return saida


def percentil_expansivo(valor, passados):
    """Fração dos eventos PASSADOS da mesma família com entropia ≤ `valor`.

    É a versão CONTÍNUA do contraste de grupos que mediu a premissa (a mediana é
    o percentil dicotomizado), e por isso não crava threshold nenhum. Amostra
    passada vazia -> NaN, nunca 0,5 inventado.
    """
    p = pd.Series(passados, dtype=float).dropna()
    return float((p <= valor).mean()) if len(p) else float("nan")


def calendario_de_anuncios(raiz, diretorio):
    """DataFrame (data × [entropia, familia, soma]) das 3 famílias de anúncio.

    O casamento release -> mercado das famílias de CPI e payrolls é IMPORTADO de
    `premio_condicional`, não recopiado: é a mesma regra (slug na coluna `fonte`
    do calendário; payroll casado pela data em que a série termina, com o
    desempate jobs > desemprego), e duas cópias um dia divergem — o mesmo
    argumento que trouxe a `entropia_normalizada` para dentro de `src/`.
    """
    from premio_condicional import (PREFIXO_FOMC, mercados_de_payroll,  # noqa: E402
                                    prefixos_cpi)

    fomc = pd.to_datetime(pd.read_csv(raiz / "data/raw/fomc_dates.csv")["date"])
    eventos = entropias_de_anuncio(diretorio, PREFIXO_FOMC, fomc, "fomc")
    for data, prefixo in prefixos_cpi(
            load_cpi_releases(raiz / "data/raw/cpi_release_dates.csv"), diretorio).items():
        eventos.update(entropias_de_anuncio(diretorio, prefixo, [data], "cpi"))
    payrolls = load_payroll_releases(raiz / "data/raw/payrolls_release_dates.csv")
    for data, (prefixo, _) in mercados_de_payroll(diretorio, payrolls).items():
        eventos.update(entropias_de_anuncio(diretorio, prefixo, [data], "payrolls",
                                            ordenar=False))
    return pd.DataFrame.from_dict(
        eventos, orient="index", columns=["entropia", "familia", "soma"]).sort_index()


class MontadorV1:
    """Monta `(sigma, views, overlays)` de um dia. Chamado em ordem de data.

    Guarda estado de propósito: a média da divergência (D9) é EXPANSIVA, então
    depende do que já foi visto — e só do que já foi visto. Recalcular por
    janela fechada seria mais puro e olharia o futuro.
    """

    def __init__(self, retornos, breakeven, dgs10, mercados, pmfs,
                 fomc=None, surpresas=None, orcamentos=None,
                 fomc_pmfs=None, e_ff=None, gamma=FL_GAMMA_V1,
                 decisoes_fomc=None, surpresas_cpi=None, tatica=(),
                 anuncios=None, m3=None, dgs1=None, taxa_base_m3=None,
                 views_novas=(), escala_incerteza="entropia",
                 series_C=None, k_C=None, sleeves=()):
        self.retornos = retornos
        self.breakeven = breakeven
        self.dgs10 = dgs10
        self.mercados = mercados          # data de divulgação -> prefixo
        self.pmfs = pmfs                  # prefixo -> (probs, valores)
        self.fomc = fomc if fomc is not None else pd.DatetimeIndex([])
        self.surpresas = surpresas if surpresas is not None else pd.Series(dtype=float)
        self.fomc_pmfs = fomc_pmfs or {}  # data da reunião -> (probs, valores, cru)
        self.e_ff = e_ff if e_ff is not None else pd.Series(dtype=float)
        self.orcamentos = orcamentos or {}
        # γ do favorite-longshot: 1,0 no v1 (D1.1) — as views recebem SEMPRE a
        # correção de PMF, que em γ = 1,0 é a identidade e em γ ≠ 1 renormaliza
        # sobre as faixas. É o que torna a coluna de robustez γ confiável.
        self.gamma = gamma
        # Camada tática reconstruída (2026-08-08): decisão REALIZADA do FOMC em
        # bps (lida no DFF) e surpresa de inflação do dia da divulgação em bps
        # (Δ breakeven). `tatica` é a tupla de sleeves ligadas ("fomc", "cpi");
        # vazia (default) mantém a entrega da 12c intocada.
        self.decisoes_fomc = decisoes_fomc if decisoes_fomc is not None else pd.Series(dtype=float)
        self.surpresas_cpi = surpresas_cpi if surpresas_cpi is not None else pd.Series(dtype=float)
        self.tatica = tuple(tatica)
        # Views novas CANDIDATAS (15b incerteza, 15g B com β próprio). Fora do
        # v1: `views_novas=()` é o default e nada disto é chamado. A entrada é
        # decisão do grupo (15a–15c e 15g) — aqui só existe o que permite MEDIR.
        self.anuncios = anuncios if anuncios is not None else pd.DataFrame(
            columns=["entropia", "familia", "soma"])
        self.m3 = m3                      # (probs, valores em nº de cortes, cru)
        self.dgs1 = dgs1 if dgs1 is not None else pd.Series(dtype=float)
        self.taxa_base_m3 = taxa_base_m3  # taxa do fim de 2024, bps (ver M3_INICIO_DO_ANO)
        self.views_novas = tuple(views_novas)
        self.escala_incerteza = escala_incerteza
        # View C (CANDIDATA, 2026-08-10). `series_C` = {episódio: série p já
        # pré-processada}; `k_C` = a janela de leitura do poly. O k NÃO tem
        # default: a curva de absorção (`Absorcao_C.md`) NÃO identifica um k, e
        # cravar um aqui seria escolher parâmetro sem critério. Quem liga a view
        # informa qual k está medindo.
        self.series_C = series_C or {}
        self.k_C = k_C
        # Camada tática v2 (D28): as sleeves transversais admitidas. Tupla
        # vazia (default) mantém a entrega da 12c intocada — o `overlays`
        # devolve None e nada é somado ao tilt.
        self.sleeves = tuple(sleeves)
        if self.sleeves:
            tickers = sorted({a for s in self.sleeves for a in s.livro})
            self._estendido = tatica_sleeves.pernas_neutras(retornos, tickers).dropna()
            self._betas = tatica_sleeves.hedge_betas(retornos, tickers)
        else:
            self._estendido = self._betas = None
        self.surpresas_B = []             # histórico para a média expansiva da B
        self._cache_surpresa_poly = {}    # reuniao -> surpresa (depende do γ)
        self.divergencias = []            # histórico para a média expansiva (2.2)
        self.surpresas_2_3 = []           # idem, para a demeanagem da 2.3
        self._semente_2_3 = []            # histórico PRÉ-janela, ver `semear_2_3`
        self._datas_pre = []              # datas da semente, para re-semear no γ

    def semear_2_3(self, datas_pre):
        """Pré-preenche a média expansiva da 2.3 com o histórico ANTERIOR à janela.

        Decisão do dono em 2026-08-07 (refinamento da seção 12). Sem semente a
        média nasce vazia no primeiro pregão do backtest: o dia 1 demeana por
        0,0 (viés inteiro do proxy passa cru) e os primeiros meses usam um zero
        estimado com meia dúzia de pontos. O efeito medido era o sinal ficar do
        mesmo lado em 78% dos dias, contra 45%/55% no levantamento completo.

        **Não é lookahead:** tudo que entra aqui é estritamente anterior ao
        primeiro dia negociado, e a média segue expansiva dali em diante. Roda
        pelo MESMO `_view_2_3` do backtest — semeia exatamente os dias em que a
        view teria existido, sem duplicar a fórmula da surpresa.

        A 2.2 não tem semente porque não tem o que semear: a janela começa na
        primeira PMF de CPI (2025-02-08), então não existe dia anterior a ela.
        """
        pregoes = self.retornos.index
        self._datas_pre = datas_pre
        self._semente_2_3 = []
        self.surpresas_2_3.clear()
        for data in datas_pre:
            self._view_2_3(data, pregoes)
        self._semente_2_3 = list(self.surpresas_2_3)
        return len(self._semente_2_3)

    def set_gamma(self, gamma):
        """Troca o γ do favorite-longshot e RE-SEMEIA a média da 2.3.

        A semente é feita de surpresas, e a surpresa depende de γ: manter a
        semente de γ = 1,0 numa rodada de γ = 1,25 demeanaria a janela por uma
        média que aquele γ nunca produziria. É a única armadilha da coluna de
        robustez, e ela não daria erro nenhum.
        """
        self.gamma = gamma
        self._cache_surpresa_poly.clear()  # o E_poly da sleeve também depende do γ
        self.semear_2_3(self._datas_pre)

    def reset(self):
        """Volta os históricos expansivos ao estado do primeiro pregão.

        Obrigatório entre rodadas da varredura: sem isso a média expansiva da
        rodada seguinte já começa com a série INTEIRA da anterior — inclusive
        dias posteriores à data que está sendo montada, que é lookahead puro.
        Mora aqui, e não no laço, para uma view nova não reintroduzir o bug
        por esquecimento (foi assim que ele apareceu com a 2.3).

        Restaura a semente em vez de zerar: ela é histórico pré-janela, não
        resíduo da rodada anterior.
        """
        self.divergencias.clear()
        self.surpresas_2_3[:] = self._semente_2_3
        self.surpresas_B.clear()

    # --- insumos ------------------------------------------------------------

    def _fl(self, probs):
        """Correção de favorite-longshot das views, no γ desta rodada."""
        return favorite_longshot_pmf(probs, self.gamma)

    def _ultimo_antes(self, serie, data):
        """Última leitura ESTRITAMENTE anterior a `data` (sem lookahead)."""
        anteriores = serie[serie.index < data].dropna()
        return float(anteriores.iloc[-1]) if len(anteriores) else None

    def _durations(self, data):
        """Duration empírica de TIP e TLT com o dado anterior a `data`.

        Medidas, não copiadas da ficha do emissor — mesma decisão de módulo do
        `market_inputs`. Expansiva: em cada rebalanceamento usa toda a história
        disponível até ali, e nada além.
        """
        r = self.retornos[self.retornos.index < data]
        dy = self.dgs10.diff().reindex(r.index)
        return (empirical_duration(r, dy, view_2_2_inflacao.LONG_ASSET),
                empirical_duration(r, dy, view_2_2_inflacao.SHORT_ASSET))

    def _duration_breakeven(self, data, duration_long, duration_short):
        """Duration do breakeven MEDIDA no par que a view monta, expansiva.

        Decidida em sessão no lugar do "~8" da espec (ver
        `market_inputs.breakeven_duration`). O par depende das durations do
        dia, então o P é remontado aqui — é o mesmo `pair_P` que a view usa,
        não uma cópia da fórmula.
        """
        P = view_2_2_inflacao.pair_P(
            list(ASSETS), view_2_2_inflacao.LONG_ASSET,
            view_2_2_inflacao.SHORT_ASSET, duration_long, duration_short)
        r = self.retornos[self.retornos.index < data]
        return breakeven_duration(pd.Series(r.to_numpy() @ P, index=r.index),
                                  self.breakeven.diff().reindex(r.index))

    def _view_2_2(self, data, pregoes):
        """View 2.2 do dia, ou None se não há mercado de CPI vivo (cascata)."""
        futuras = [r for r in self.mercados if r >= data]
        if not futuras:
            return None
        release = min(futuras)
        probs, valores, cru = self.pmfs[self.mercados[release]]
        if data not in probs.index:
            return None  # sem leitura pré-abertura nesse dia
        linha = probs.loc[data].to_numpy(dtype=float)
        if not np.isfinite(linha).all() or linha.sum() <= 0:
            return None  # PMF incompleta -> cascata, não chute

        breakeven = self._ultimo_antes(self.breakeven, data)
        if breakeven is None:
            return None
        faltam = int(pregoes.slice_indexer(data, release).stop
                     - pregoes.slice_indexer(data, release).start) - 1
        if faltam < 1:
            return None  # é o dia da divulgação: o mercado resolve, a view sai

        duration_long, duration_short = self._durations(data)
        duration = self._duration_breakeven(data, duration_long, duration_short)
        # D9: a divergência entra demeanada, com a média de janela EXPANSIVA.
        media = float(np.mean(self.divergencias)) if self.divergencias else 0.0
        view = view_2_2_inflacao.build_view(
            list(ASSETS), breakeven_10y=breakeven, duration=duration,
            cpi_frequencia="mensal", duration_long=duration_long,
            duration_short=duration_short, dias_ate_divulgacao=faltam,
            fl_correction=self._fl,
            divergencia_media=media, bucket_probs=linha, bucket_values=valores)
        if view is not None:
            self.divergencias.append(view.diagnostics["divergencia"])
            # Bloco de qualidade da leitura (Ω da Lia). Mora aqui, e não dentro
            # da view, porque a view recebe SNAPSHOT — quem tem a série é o
            # montador. Para ela a diferença não existe: chega um dict só.
            # A view ganha do bloco em caso de conflito (ela sabe o caminho da
            # cascata que rodou; o montador não).
            view.diagnostics.update({
                **diagnostics_qualidade(cru, data, dias_ate_evento=faltam),
                **view.diagnostics,
            })
        return view

    def _betas_fomc(self, data):
        """β da 2.3 por event-study EXPANSIVO: só reuniões anteriores a `data`.

        A surpresa realizada é o ΔDTB3 do dia do FOMC (D6, no lugar da variação
        do ZQ). Sem eventos suficientes ou sem variância na surpresa a view cai
        pela cascata em vez de estourar — é condição de dado num loop diário,
        não erro de chamada.

        Quantos eventos são "suficientes" foi FECHADO em 2026-08-07 (decisão
        12b): sem piso adicional no v1 — vale o do próprio `estimate_betas` (2,
        o mínimo algébrico). Motivo: na janela o β nunca foi estimado com menos
        de 25 eventos, então qualquer piso menor não desativa pregão nenhum, e
        cravar um número seria threshold sem medição. O nº usado continua saindo
        nos diagnostics (`n_eventos_beta`).
        """
        dias = self.surpresas.index[self.surpresas.index < data].intersection(self.retornos.index)
        if len(dias) < 2:
            return None, 0
        s = self.surpresas.loc[dias].to_numpy(dtype=float)
        if np.ptp(s) == 0:
            return None, len(dias)  # surpresa constante -> β não identificável
        return view_2_3_fed.estimate_betas(self.retornos.loc[dias].to_numpy(dtype=float), s), len(dias)

    def _view_2_3(self, data, pregoes):
        """View 2.3 do dia, ou None se falta mercado, β ou âncora (cascata)."""
        futuras = [r for r in self.fomc_pmfs if r >= data]
        if not futuras:
            return None
        reuniao = min(futuras)            # vale o mercado da PRÓXIMA reunião
        probs, valores, cru = self.fomc_pmfs[reuniao]
        if data not in probs.index:
            return None                   # sem leitura pré-abertura nesse dia
        linha = probs.loc[data].to_numpy(dtype=float)
        if not np.isfinite(linha).all():
            return None
        e_ff = self._ultimo_antes(self.e_ff, data)
        betas, n_eventos = self._betas_fomc(data)
        if e_ff is None or betas is None:
            return None
        faltam = int(pregoes.slice_indexer(data, reuniao).stop
                     - pregoes.slice_indexer(data, reuniao).start) - 1
        if faltam < 1:
            return None                   # dia da reunião: o mercado resolve
        # Decisão de 2026-08-07: a surpresa entra DEMEANADA, média expansiva
        # (mesma construção da D7.4 da 2.2) — sem ZQ, o e_ff tem horizonte de
        # ~3 meses contra uma reunião, e o viés de nível é do instrumento.
        media = float(np.mean(self.surpresas_2_3)) if self.surpresas_2_3 else 0.0
        view = view_2_3_fed.build_view(
            list(ASSETS), e_ff_bps=e_ff, betas=betas, bucket_probs=linha,
            bucket_deltas_bps=valores, surpresa_media=media,
            fl_correction=self._fl)
        if view is not None:
            self.surpresas_2_3.append(view.diagnostics["surpresa_bps"])
            view.diagnostics.update({
                **diagnostics_qualidade(cru, data, dias_ate_evento=faltam),
                **view.diagnostics, "n_eventos_beta": n_eventos,
            })
        return view

    # --- views novas, CANDIDATAS (15b e 15g) --------------------------------

    def _escala_anuncios(self, data):
        """(x de hoje, x dos anúncios PASSADOS, centro) na escala declarada.

        Duas escalas, nenhuma com threshold, e a 15c está ABERTA sobre qual
        entra — por isso as duas rodam pelo mesmo caminho e o que muda é só a
        transformação do regressor:

          - `entropia` : o número cru; centro = média expansiva da família.
          - `percentil`: posição dentro da própria família (a versão contínua do
            contraste de grupos que mediu a premissa); centro = média dos
            percentis passados da família, que é ~0,5 por construção.

        Sem lookahead nas duas: hoje é ranqueado contra os anúncios ANTERIORES,
        e o regressor de treino contra o próprio conjunto de treino.
        """
        passados = self.anuncios[self.anuncios.index < data]
        familia = self.anuncios.loc[data, "familia"]
        entropia = float(self.anuncios.loc[data, "entropia"])
        if self.escala_incerteza == "entropia":
            x_pass = passados["entropia"].astype(float)
            x_hoje = entropia
        elif self.escala_incerteza == "percentil":
            x_pass = passados.groupby("familia")["entropia"].transform(
                lambda g: g.rank(pct=True))
            mesma = passados.loc[passados["familia"] == familia, "entropia"]
            x_hoje = percentil_expansivo(entropia, mesma)
        else:
            raise ValueError(f"escala desconhecida: {self.escala_incerteza!r}")
        centro = x_pass[passados["familia"] == familia]
        if not len(centro) or not np.isfinite(x_hoje):
            return None
        return x_hoje, x_pass, float(centro.mean())

    def _view_incerteza(self, data):
        """View de incerteza de anúncio (15b) do dia, ou None (cascata).

        Só existe em dia de anúncio: o Q é o retorno close-to-close do PRÓPRIO
        dia, e a entropia sai do slot pré-abertura — a mesma janela que a
        medição de `premio_condicional.py` usou.
        """
        if "incerteza" not in self.views_novas or data not in self.anuncios.index:
            return None
        escala = self._escala_anuncios(data)
        if escala is None:
            return None
        x_hoje, x_pass, centro = escala
        dias = x_pass.index.intersection(self.retornos.index)
        if len(dias) < 2 or float(np.ptp(x_pass.loc[dias])) == 0.0:
            return None                   # β não identificável -> cascata
        betas = view_incerteza_anuncio.estimate_betas_incerteza(
            self.retornos.loc[dias], x_pass.loc[dias], assets=list(ASSETS))
        view = view_incerteza_anuncio.build_view(
            list(ASSETS), betas=betas, entropia=x_hoje, entropia_media=centro,
            soma_faixas=float(self.anuncios.loc[data, "soma"]),
            familia=self.anuncios.loc[data, "familia"],
            escala=self.escala_incerteza)
        if view is not None:
            view.diagnostics["n_eventos_beta"] = len(dias)
        return view

    def _betas_dgs1(self, data):
        """β da B por event-study EXPANSIVO contra o ΔDGS1 dos dias de FOMC.

        Mesmo estimador da 2.3, outro vértice — e é justamente isso que separa
        esta view da 2.3 (15g: ângulo de 95,6° entre os dois P). Reusar os β da
        2.3, como manda a espec antiga, poria duas linhas iguais no P do BL.
        """
        delta = (self.dgs1.diff() * PONTOS_PERCENTUAIS).dropna()
        dias = self.fomc[self.fomc < data].intersection(
            self.retornos.index).intersection(delta.index)
        if len(dias) < 2:
            return None, len(dias)
        s = delta.loc[dias].to_numpy(dtype=float)
        if np.ptp(s) == 0:
            return None, len(dias)
        return (view_2_3_fed.estimate_betas(
            self.retornos.loc[dias].to_numpy(dtype=float), s), len(dias))

    def _view_B(self, data):
        """View B com β próprio (15g) do dia, ou None (cascata)."""
        if "B" not in self.views_novas or self.m3 is None or self.taxa_base_m3 is None:
            return None
        probs, valores, _ = self.m3
        if data not in probs.index:
            return None
        linha = probs.loc[data].to_numpy(dtype=float)
        if not np.isfinite(linha).all():
            return None
        benchmark = self._ultimo_antes(self.dgs1, data)
        betas, n_eventos = self._betas_dgs1(data)
        if benchmark is None or betas is None:
            return None
        media = float(np.mean(self.surpresas_B)) if self.surpresas_B else 0.0
        view = view_B_trajetoria_propria.build_view(
            list(ASSETS), benchmark_bps=benchmark * PONTOS_PERCENTUAIS,
            betas=betas, vertice="DGS1", bucket_probs=linha,
            bucket_rates_bps=view_B_trajetoria_propria.rates_from_cut_buckets(
                self.taxa_base_m3, valores),
            surpresa_media=media, fl_correction=self._fl)
        if view is not None:
            self.surpresas_B.append(view.diagnostics["surpresa_bps"])
            view.diagnostics["n_eventos_beta"] = n_eventos
        return view

    def _view_C(self, data):
        """View C geopolítica (candidata) do dia, ou None (cascata).

        β EXPANSIVO por episódio, estritamente anterior a D — a maquinaria da
        2.4 (perfil de lags distribuídos -> absorção plena até k). UM evento por
        vez, como a espec do módulo manda: o primeiro episódio vivo ganha o dia.

        Sem piso de amostra além do mínimo algébrico do `lag_regression`
        (precedente D12b: piso que não morde é threshold inventado).
        """
        if "C" not in self.views_novas or self.k_C is None:
            return None
        k = self.k_C
        for p in self.series_C.values():
            historico = p[p.index < data]
            if data not in p.index or len(historico) < k + 1:
                continue
            dp = historico.diff().dropna()
            R = self.retornos.reindex(dp.index).dropna()
            try:
                betas = full_absorption_beta(
                    lag_regression(R[list(ASSETS)].to_numpy(),
                                   dp.reindex(R.index).to_numpy(), k), k)
            except ValueError:
                continue                  # amostra insuficiente -> cascata
            ate_hoje = p[p.index <= data]
            if len(ate_hoje) < k + 1:
                continue
            return view_C_geopolitica_energia.build_view(
                list(ASSETS), betas=betas, k=k,
                p_series=ate_hoje.to_numpy(dtype=float))
        return None

    # --- camada tática ------------------------------------------------------

    def _premio(self, data):
        orcamento = self.orcamentos.get("premio")
        if orcamento is None:
            return None
        pmf_do_dia = None
        if data in self.mercados:                       # dia de divulgação do CPI
            probs, _, _ = self.pmfs[self.mercados[data]]
            if data in probs.index:
                pmf_do_dia = probs.loc[data].to_numpy(dtype=float)
        if pmf_do_dia is None or not np.isfinite(pmf_do_dia).all() or pmf_do_dia.sum() <= 0:
            return None                                 # dormente (cascata)
        return tatica_premio_anuncios.build_overlay(
            list(ASSETS), orcamento, announcement_pmf=pmf_do_dia)

    def _drift(self, data):
        acoes, rf = self.orcamentos.get("drift_acoes"), self.orcamentos.get("drift_rf")
        if acoes is None or rf is None or not len(self.fomc):
            return None
        passados = self.fomc[self.fomc < data]
        futuros = self.fomc[self.fomc >= data]
        if not len(passados) or passados[-1] not in self.surpresas.index:
            return None
        pregoes = self.retornos.index
        conta = lambda a, b: int(pregoes.slice_indexer(a, b).stop  # noqa: E731
                                 - pregoes.slice_indexer(a, b).start) - 1
        desde = conta(passados[-1], data)
        ate_proximo = conta(data, futuros[0]) if len(futuros) else None
        # DRIFT_JANELA_RF = None significa "até a véspera do próximo FOMC"
        # (config): sem calendário à frente não há janela, e inventar uma seria
        # cravar o número da literatura sem decisão.
        janela_rf = DRIFT_JANELA_RF
        if janela_rf is None:
            if ate_proximo is None or ate_proximo < 1:
                return None
            janela_rf = ate_proximo
        return tatica_drift_pos_fomc.build_overlay(
            list(ASSETS), dias_desde_fomc=desde,
            surpresa_bps=float(self.surpresas[passados[-1]]),
            orcamento_acoes=acoes, orcamento_rf=rf,
            janela_acoes=DRIFT_JANELA_ACOES, janela_rf=janela_rf,
            dias_ate_proximo_fomc=ate_proximo)

    # --- camada tática RECONSTRUÍDA (2026-08-08) ----------------------------
    #
    # Duas sleeves do mesmo template (`tatica_drift_anuncio`), sem orçamento.
    # Só rodam com `tatica=True`; a configuração da 12c (`tatica=False`) não
    # passa por aqui e continua entregando exatamente o mesmo número.

    def _dias_uteis(self, de, ate):
        pregoes = self.retornos.index
        return int(pregoes.slice_indexer(de, ate).stop
                   - pregoes.slice_indexer(de, ate).start) - 1

    def _surpresa_fomc_poly(self, reuniao):
        """Decisão REALIZADA − E_poly[véspera], em bps. None = sem os dois lados.

        Esta é a diferença de fundo entre a sleeve nova e a `_drift` antiga: lá a
        surpresa é o ΔDTB3 do dia (proxy de mercado, zero Polymarket na sleeve
        que mede melhor em `Curva_orcamento.md`); aqui os dois lados são os do
        projeto — a PMF de decisão do poly na véspera e o que o Fed fez.

        ⚠️ **A decisão realizada é lida no DFF com janela para a frente**, e isso
        NÃO é lookahead de preço: a decisão é pública às 14h ET do próprio dia D,
        e a sleeve só abre no close de D. O DFF é o instrumento de leitura de um
        fato já público (a taxa efetiva só migra para o novo alvo no dia
        seguinte), não uma informação que o mercado ainda não tinha. Fica
        declarado porque é a única premissa não-mecânica das duas sleeves.
        """
        if reuniao in self._cache_surpresa_poly:
            return self._cache_surpresa_poly[reuniao]
        surpresa = None
        if reuniao in self.decisoes_fomc.index and reuniao in self.fomc_pmfs:
            probs, valores, _ = self.fomc_pmfs[reuniao]
            anteriores = probs.index[probs.index < reuniao]
            if len(anteriores):
                linha = probs.loc[anteriores[-1]].to_numpy(dtype=float)
                # Mesmo piso da 2.3 (D12): PMF degenerada não vira E_poly
                # renormalizado — sem leitura utilizável a sleeve fica dormente.
                if np.isfinite(linha).all() and linha.sum() >= view_2_3_fed.SOMA_MINIMA:
                    e_poly = pmf_mean(linha, valores, self._fl)
                    surpresa = float(self.decisoes_fomc[reuniao]) - float(e_poly)
        self._cache_surpresa_poly[reuniao] = surpresa
        return surpresa

    def _sleeves(self, data):
        """Camada tática v2 — as sleeves transversais da D28, em UM overlay.

        Um overlay só para as duas: elas compartilham o livro (`+XLP −XLK`), e
        o item 11 manda somar os μ antes do `inv(δΣ)`. Dois `OverlayResult`
        separados seriam somados pelo `apply_overlays` depois do
        dimensionamento, que é a dupla contagem que o item existe para barrar.

        A Σ da camada é a diagonal da tabela ESTENDIDA e sai de dentro do
        módulo — não é a `sigma` amostral das views, que não tem as pernas `⊥`.
        """
        if not self.sleeves:
            return None
        return tatica_sleeves.sleeve_overlay(
            list(ASSETS), self._estendido, self._betas, self.sleeves, data,
            DELTA)

    def _drift_fomc(self, data, sigma):
        """Sleeve 1 — drift pós-FOMC com a surpresa medida no Polymarket."""
        if "fomc" not in self.tatica or not len(self.fomc):
            return None
        eventos = []
        for reuniao in self.fomc[self.fomc < data]:
            surpresa = self._surpresa_fomc_poly(reuniao)
            if surpresa is not None and surpresa != 0.0:
                eventos.append((reuniao, np.sign(surpresa)))
        if not eventos:
            return None
        mu, n_eventos = tatica_drift_anuncio.estimate_drift_mu(
            self.retornos, eventos, DRIFT_JANELA_ACOES, DRIFT_LIVRO_FOMC, data,
            sigma, TAU)
        ultimo, direcao = eventos[-1]
        overlay = tatica_drift_anuncio.build_overlay(
            list(ASSETS), "fomc", dias_desde_evento=self._dias_uteis(ultimo, data),
            direcao=direcao, mu=mu, sigma=sigma, delta=DELTA,
            janela=DRIFT_JANELA_ACOES, n_eventos_mu=n_eventos)
        if overlay is not None:
            overlay.diagnostics["surpresa_bps"] = self._surpresa_fomc_poly(ultimo)
        return overlay

    def _drift_cpi(self, data, sigma):
        """Sleeve 2 — drift pós-CPI, surpresa = Δ breakeven no dia da divulgação.

        Sem dado novo: o T10YIE do dia D fecha com o dia, e a sleeve abre no
        close de D. É a mesma construção de surpresa REALIZADA que a `_drift`
        antiga usa no FOMC (ΔDTB3), transposta para a família de inflação — e o
        complemento temporal da view 2.2, que opera a divergência ANTES e sai no
        dia da divulgação (`faltam < 1`).
        """
        if "cpi" not in self.tatica or not len(self.surpresas_cpi):
            return None
        passadas = self.surpresas_cpi[self.surpresas_cpi.index < data]
        eventos = [(d, np.sign(s)) for d, s in passadas.items() if s != 0.0]
        if not eventos:
            return None
        mu, n_eventos = tatica_drift_anuncio.estimate_drift_mu(
            self.retornos, eventos, DRIFT_JANELA_ACOES, DRIFT_LIVRO_CPI, data,
            sigma, TAU)
        ultimo, direcao = eventos[-1]
        overlay = tatica_drift_anuncio.build_overlay(
            list(ASSETS), "cpi", dias_desde_evento=self._dias_uteis(ultimo, data),
            direcao=direcao, mu=mu, sigma=sigma, delta=DELTA,
            janela=DRIFT_JANELA_ACOES, n_eventos_mu=n_eventos)
        if overlay is not None:
            overlay.diagnostics["surpresa_bps"] = float(passadas.loc[ultimo])
        return overlay

    def __call__(self, data):
        pregoes = self.retornos.index
        sigma = sample_covariance(self.retornos, data=data)
        views = [self._view_2_2(data, pregoes), self._view_2_3(data, pregoes),
                 self._view_incerteza(data), self._view_B(data),
                 self._view_C(data)]
        overlays = [self._premio(data), self._drift(data),
                    self._drift_fomc(data, sigma), self._drift_cpi(data, sigma),
                    self._sleeves(data)]
        return sigma, views, overlays


def decisoes_realizadas_fomc(dff, fomc, antes=3, depois=5):
    """Δtaxa DECIDIDA em cada reunião, em bps, lida no DFF (taxa efetiva).

    Média das `depois` leituras seguintes menos a das `antes` anteriores: o novo
    alvo só vale a partir do dia seguinte ao anúncio, e a média de poucos dias
    tira o ruído de fim de mês do overnight. Medido na janela do v1, devolve os
    valores redondos que a decisão de fato teve (0 ou −25 bps).

    Insumo da sleeve de drift; **não** é insumo da view 2.3 (aquela usa
    `DTB3 − DFF` como âncora de expectativa, decisão 12).
    """
    saida = {}
    for reuniao in fomc:
        pre = dff[dff.index < reuniao].tail(antes)
        pos = dff[dff.index > reuniao].head(depois)
        if len(pre) == antes and len(pos) == depois:
            saida[reuniao] = (pos.mean() - pre.mean()) * PONTOS_PERCENTUAIS
    return pd.Series(saida, dtype=float)


# As views que a ENTREGA liga. Deixa de ser `()` em 2026-08-10: a 15b e a 15g
# passaram a régua da D22 e as três decisões que as travavam fecharam (D15a
# dupla leitura · D15b P direcional · D15c entropia crua · D22e item 4).
# Mora aqui, e não no `main`, porque é este default que define "o v1" para as
# varreduras irmãs (`curva_c.py`, `curva_banda.py`, …) — cravar no `main` faria
# a entrega e as varreduras medirem carteiras diferentes em silêncio.
VIEWS_V1 = ("incerteza", "B")

# As sleeves da camada tática v2, ADMITIDAS na D28 depois de passarem G0/G1/G2/
# G3, o corte da amostra e — na M9 — o teste de mercado irmão. O `k` de cada
# uma é o BLOCO declarado no item 3, não uma escolha do backtest: mudar esta
# tupla olhando o resultado é exatamente o overfit que a régua 28.0 barra.
#
# ⚠️ **A ENTREGA vai com a camada LIGADA** (D28.13, dono, 2026-08-11), então o
# `carregar` tem `sleeves=True` por default — mesma lógica do `VIEWS_V1`: é
# este default que define "o v1" para as varreduras irmãs, e cravar a decisão
# só no `main` faria a entrega e as varreduras medirem carteiras diferentes em
# silêncio. Custa −2,16 pp de excesso no teto de referência
# (`Camada_tatica_v2.md`); a decisão foi tomada com esse número na mesa.
# (mercado, prefixo do arquivo do poly, lookbacks do bloco)
SLEEVES_V2 = (
    ("M4 recessão EUA 2025", "M4_recession_", (3, 5, 10)),
    ("M9 Câmara",
     "M9_midterms_2022_will-the-democratic-party-control-the-ho", (20,)),
)


def montar_sleeves(diretorio, retornos, declaradas=SLEEVES_V2):
    """As `Sleeve` da D28, com a crença já na grade de pregões do mercado.

    O livro NÃO é redigitado aqui: vem do `LIVROS_SETORIAIS` do
    `gate_transversal`, que é onde ele foi declarado antes de medir. Uma cópia
    literal nesta função poderia divergir do livro que aprovou a sleeve sem
    nada acusar. Import local porque o `premissa_g1` importa o `carregar` deste
    módulo — no nível de módulo o ciclo fecharia.
    """
    from gate_transversal import LIVROS_SETORIAIS  # noqa: E402
    from premissa_g1 import em_pregoes, serie_binaria  # noqa: E402

    saida = []
    for mercado, prefixo, lookbacks in declaradas:
        crenca = em_pregoes(serie_binaria(diretorio, prefixo))
        saida.append(tatica_sleeves.Sleeve(
            nome=mercado, crenca=crenca.reindex(retornos.index.union(crenca.index)),
            livro=LIVROS_SETORIAIS[mercado][0], lookbacks=lookbacks))
    return tuple(saida)


def carregar(raiz, orcamentos=None, gamma=FL_GAMMA_V1, tatica=(),
             views_novas=VIEWS_V1, escala_incerteza="entropia",
             sleeves=True):
    """(retornos, montador, datas, w_mkt) — toda a plumbing de dado do v1.

    Separado do `main` para as varreduras irmãs (ex.: `curva_c.py`) rodarem o
    MESMO montador em vez de reimplementar a leitura e arriscar divergir dela.
    """
    raiz = Path(raiz)
    precos = load_etf_prices(raiz / "data/etf_prices_daily.parquet")[list(ASSETS)]
    retornos = daily_returns(precos)
    breakeven = load_fred(raiz / "data/raw/fred_T10YIE.csv") / PONTOS_PERCENTUAIS
    dgs10 = load_fred(raiz / "data/raw/fred_DGS10.csv")
    releases = load_cpi_releases(raiz / "data/raw/cpi_release_dates.csv")
    diretorio = raiz / "data/raw/clob_exploracao"
    mercados = mercados_de_cpi(releases, diretorio)
    pmfs = {p: pmf_diaria(diretorio, p) for p in set(mercados.values())}

    fomc = pd.to_datetime(pd.read_csv(raiz / "data/raw/fomc_dates.csv")["date"])
    fomc = pd.DatetimeIndex(sorted(fomc))
    # D6: ΔDTB3 do dia do FOMC no lugar da variação do ZQ (que não tem fonte
    # grátis). É a surpresa REALIZADA, insumo do drift — não da view 2.3.
    dtb3 = load_fred(raiz / "data/raw/fred_DTB3.csv")
    surpresas = (dtb3.diff() * PONTOS_PERCENTUAIS).reindex(fomc).dropna()

    # View 2.3: PMF de decisão por reunião + âncora de mercado. Sem ZQ grátis,
    # `E_FF = DTB3 − DFF` em bps (decisão de 2026-08-07, provisória) — e a
    # surpresa entra demeanada, ver `_view_2_3`.
    fomc_pmfs = pmf_fomc_diaria(raiz / "data/polymarket_fed_reunioes.parquet")
    dff = load_fred(raiz / "data/raw/fred_DFF.csv")
    e_ff = ((dtb3 - dff) * PONTOS_PERCENTUAIS).dropna()

    # Camada tática reconstruída: decisão realizada do FOMC (DFF) e surpresa de
    # inflação do dia da divulgação (Δ T10YIE em bps). Nenhum dado novo — as duas
    # séries já estavam no `data/` para outras finalidades.
    decisoes_fomc = decisoes_realizadas_fomc(dff, fomc)
    t10yie = load_fred(raiz / "data/raw/fred_T10YIE.csv")
    surpresas_cpi = (t10yie.diff() * PONTOS_PERCENTUAIS).reindex(
        pd.DatetimeIndex(list(mercados))).dropna()

    # Insumos das views novas — carregados só quando alguma está ligada, para o
    # caminho da entrega (views_novas=()) não pagar por eles nem mudar de nada.
    anuncios = m3 = dgs1 = taxa_base = None
    if "incerteza" in views_novas:
        anuncios = calendario_de_anuncios(raiz, diretorio)
    if "B" in views_novas:
        m3 = pmf_m3_diaria(diretorio)
        dgs1 = load_fred(raiz / "data/raw/fred_DGS1.csv")
        base = dff[dff.index < M3_INICIO_DO_ANO]
        taxa_base = float(base.iloc[-1]) * PONTOS_PERCENTUAIS if len(base) else None

    montador = MontadorV1(retornos, breakeven, dgs10, mercados, pmfs,
                          fomc, surpresas, orcamentos or {},
                          fomc_pmfs=fomc_pmfs, e_ff=e_ff, gamma=gamma,
                          decisoes_fomc=decisoes_fomc,
                          surpresas_cpi=surpresas_cpi, tatica=tatica,
                          anuncios=anuncios, m3=m3, dgs1=dgs1,
                          taxa_base_m3=taxa_base, views_novas=views_novas,
                          escala_incerteza=escala_incerteza,
                          sleeves=montar_sleeves(diretorio, retornos)
                          if sleeves else ())

    # Começa quando as duas condições existem: Σ com janela cheia e PMF de CPI.
    primeira_pmf = min(probs.index.min() for probs, _, _ in pmfs.values())
    inicio = max(retornos.index[SIGMA_JANELA_PREGOES], primeira_pmf)
    datas = retornos.index[retornos.index >= inicio]
    # A média expansiva da 2.3 entra semeada com o que existe ANTES da janela
    # (dado passado, não lookahead) — ver `MontadorV1.semear_2_3`.
    montador.semear_2_3(retornos.index[retornos.index < inicio])
    return retornos, montador, datas, market_weights(ASSETS)


def rotulo_teto(teto, no_tilt):
    """Nome da coluna. `|` escapado — vira cabeçalho de tabela markdown."""
    return f"tilt ≤ {teto:g}" if no_tilt else f"Σ\\|w\\| ≤ {teto:g}"


def main():
    # O console do Windows abre em cp1252 e engasga no Σ dos rótulos; o
    # arquivo de saída já vai em utf-8.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raiz", default=".",
                        help="diretório com data/ extraído do branch Paulo")
    parser.add_argument("--custo-bps", type=float, default=CUSTO_BPS_POR_LADO)
    parser.add_argument("--tetos", type=float, nargs="+", default=[1.0, 2.0, 3.0, 5.0],
                        help="tetos de Σ|w| a varrer — o teto é decisão humana, "
                             "então o script reporta vários em vez de cravar um")
    parser.add_argument("--gammas", type=float, nargs="+",
                        default=list(FL_GAMMA_VARREDURA),
                        help="grade de γ do favorite-longshot para a coluna de "
                             "robustez (D1.1 fixa o v1 em γ = 1,0)")
    parser.add_argument("--regua", default=None,
                        help="CSV do `c` por decisão da Lia; o default segue o "
                             "--raiz. `--regua \"\"` desliga a régua e volta ao "
                             "Ω sem dosagem — o que a entrega rodava até 14/08")
    parser.add_argument("--regua-nivel", type=float, default=1.0,
                        help="expoente da régua (c = c_nivel1 ** nivel). **Não é "
                             "escolha deste script:** nível 1 é a decisão 6q da "
                             "Lia, fechada em 13/08. 0 zera a dosagem mas MANTÉM "
                             "o veto de liquidez, que não é dosagem")
    parser.add_argument("--orcamento-premio", type=float, default=None)
    parser.add_argument("--orcamento-drift-acoes", type=float, default=None)
    parser.add_argument("--orcamento-drift-rf", type=float, default=None)
    parser.add_argument("--saida", default="Dump/analises/Backtest_v1.md")
    parser.add_argument("--csv-dir", default="Dump/dados",
                        help="pasta dos CSV de série diária e varreduras — o "
                             "markdown reporta escalares, e todo gráfico da "
                             "página 4 precisa do dia a dia. `--csv-dir \"\"` "
                             "desliga")
    args = parser.parse_args()

    orcamentos = {"premio": args.orcamento_premio,
                  "drift_acoes": args.orcamento_drift_acoes,
                  "drift_rf": args.orcamento_drift_rf}
    retornos, montador, datas, w_mkt = carregar(args.raiz, orcamentos)

    # A régua do Ω da Lia (6q, nível 1). Mesmo default de caminho do
    # `curva_c.py`: com o CSV num relativo fixo, rodar contra a cópia do Paulo
    # (`--raiz /outro`) desligaria a régua CALADO. Só o "" explícito desliga.
    if args.regua is None:
        args.regua = str(Path(args.raiz) / "data" / "lia" / "c_por_decisao.csv")
    regua = (regua_por_decisao(args.regua, nivel=args.regua_nivel)
             if args.regua else None)

    # Duas varreduras: o teto cortando a carteira inteira e cortando só o tilt.
    # É a questão de desenho aberta na seção 10 do `Decisoes_pendentes.md` —
    # medir as duas dá número à reunião sem fechar a D12.
    colunas = {}
    diarios = []
    for no_tilt in (False, True):
        for teto in args.tetos:
            resultado = run_backtest(retornos, montador, w_mkt, datas=datas, tau=TAU,
                                     delta=DELTA, custo_bps=args.custo_bps,
                                     teto_alavancagem=teto, teto_no_tilt=no_tilt,
                                     regua=regua)
            # o `|` precisa vir escapado: é nome de coluna de tabela markdown
            colunas[rotulo_teto(teto, no_tilt)] = summary(resultado,
                                                          benchmark=retornos["SPY"])
            diarios.append(resultado.diario.assign(
                cenario=rotulo_teto(teto, no_tilt),
                r_benchmark=retornos["SPY"].reindex(resultado.diario.index)))
            montador.reset()  # as médias expansivas recomeçam a cada rodada
    tabela = pd.DataFrame(colunas)

    # A duration medida é a decisão desta sessão — sai no relatório, não fica só
    # dentro do loop. Vem dos diagnostics da última rodada (é a mesma em todas:
    # o teto corta o peso, não a view).
    # filtra por view: com a 2.3 ligada a lista tem diagnostics de duas formas
    # diferentes, e um `d["duration"]` seco estoura na primeira linha da 2.3.
    views_do_dia = [d for dia in resultado.diagnostics.values() for d in dia["views"]]
    durations = [d["duration"] for d in views_do_dia if d["view"] == "2.2_inflacao"]

    tatica_ligada = [f"{k} = {v}" for k, v in orcamentos.items() if v is not None]
    sleeves_ligadas = ", ".join(s.nome for s in montador.sleeves)
    linhas = ["# Backtest do v1 — BL com as views ativas (I5)\n",
              "> Gerado por `scripts/backtest_v1.py`. Benchmark = comprar e "
              "segurar SPY (consequência do `w_mkt` do prior CAPM). Custo de "
              f"**{args.custo_bps:.1f} bps por lado** sobre o giro contra o peso "
              "derivado (D8). Uma coluna por teto de alavancagem — **o teto é "
              "decisão humana; a varredura mede, não escolhe.**\n",
              f"- janela: **{datas[0].date()} a {datas[-1].date()}** "
              f"({len(datas)} pregões)",
              "- views ativas: **2.2 inflação** · **2.3 Fed** · **15b incerteza** "
              "· **15g B com β próprio**. As duas últimas entraram em 2026-08-10 "
              "(D15a/D15b/D15c fechadas + item 4 da D22 medido na D22e); a 15b é "
              "**direcional** (`P[SPY] = 2`) e vive só em dia de anúncio",
              "- ⚠️ **a carteira NÃO é neutra em mercado, e nunca foi**: o ΣP "
              "mediano das views é +0,96 (2.2), +1,74 (2.3), +1,24 (15g) e +2,00 "
              "(15b) — `P[SPY] = 0` significa que a view não toma posição no SPY, "
              "não que ela seja neutra (`Dump/analises/Ortogonalidade.md`)",
              f"- demeanagem da 2.3: média expansiva **semeada** com "
              f"{len(montador._semente_2_3)} pregões anteriores à janela "
              "(2024-04 a 2025-02, dado passado — não lookahead). Sem semente o "
              "primeiro dia demeana por 0,0; o sinal líquido sai 22% positivo, "
              "contra 34% com semente",
              f"- duration do breakeven: **medida** no par da própria view, "
              f"janela expansiva — variou de **{min(durations):.2f} a "
              f"{max(durations):.2f}** na amostra (a espec supunha \"~8\"; o dado "
              f"confirmou, e agora o número é medido em vez de suposto)",
              "- camada tática v2 (sleeves da D28): "
              + (f"**LIGADA** (D28.13) — {sleeves_ligadas}. Os números desta "
                 "tabela **já incluem** o overlay das sleeves"
                 if sleeves_ligadas else "**desligada**"),
              "- régua do Ω (Lia): "
              + (f"**LIGADA**, nível **{args.regua_nivel:g}** (decisão 6q, "
                 "13/08) — o `c` por view e por pregão dosa a confiança de cada "
                 "view antes do teto, e o veto de liquidez dela desativa view "
                 "sem negociação no slot"
                 if regua else
                 "**DESLIGADA** — Ω no fallback He-Litterman, sem dosagem"),
              "- camada tática antiga (orçamentos de drift, 12c): "
              + (", ".join(tatica_ligada) if tatica_ligada
                 else "**desligada** — os orçamentos são parâmetro de reunião") + "\n",
              "- **duas varreduras de escopo do teto:** `Σ|w| ≤ t` corta a "
              "carteira inteira; `tilt ≤ t` corta só `Σ|w − w_mkt|` e deixa a "
              "perna de mercado do prior intacta\n",
              "| métrica | " + " | ".join(tabela.columns) + " |",
              "|---" * (len(tabela.columns) + 1) + "|"]
    for nome, linha in tabela.iterrows():
        linhas.append(f"| {nome} | " + " | ".join(f"{v:,.4f}" for v in linha) + " |")

    linhas.append("\n## Giro — as duas checagens obrigatórias do D8\n")
    linhas.append("O custo não vem de negociar muito, vem de negociar contra si "
                  "mesmo: **giro desfeito em 1–2 pregões** é o mecanismo que "
                  "destruiu a GTAA diária citada na pesquisa do D8. Se ele for "
                  "alto, a saída prevista **não** é abandonar o H = 1 dia — é "
                  "banda de não-negociação.\n")
    for coluna in tabela.columns:
        c = tabela[coluna]
        linhas.append(f"- **{coluna}:** giro diário médio {c['giro diário médio']:.3f} "
                      f"· desfeito em 1–2 pregões {c['giro desfeito em 1–2 pregões']:.3f} "
                      f"· custo de breakeven "
                      f"{c['custo de breakeven (bps por lado)']:.2f} bps/lado "
                      f"(premissa: {args.custo_bps:.1f})")

    # Leitura dos números — descritiva, sem fechar decisão (CLAUDE.md §1).
    teto0 = args.tetos[0]
    c = tabela[rotulo_teto(teto0, False)]
    t = tabela[rotulo_teto(teto0, True)]
    linhas.append("\n## Leitura\n")
    # A leitura é GERADA do sinal medido: com duas views o resultado mudou de
    # lado, e frase cravada à mão vira mentira na re-rodada seguinte.
    perde = c["excesso acumulado (líquido − benchmark)"] < 0
    linhas.append(
        f"**A carteira {'perde do' if perde else 'bate o'} comprar-e-segurar SPY** no teto de "
        f"carteira mais apertado: {c['retorno acumulado líquido'] * 100:+.1f}% contra "
        f"{c['benchmark acumulado'] * 100:+.1f}% do benchmark "
        f"({c['excesso acumulado (líquido − benchmark)'] * 100:+.2f} pp).\n")
    linhas.append(
        f"**Folga de custo.** O retorno BRUTO é {c['retorno acumulado bruto'] * 100:+.1f}% e o "
        f"custo de breakeven ({c['custo de breakeven (bps por lado)']:.1f} bps/lado) é "
        f"{c['custo de breakeven (bps por lado)'] / args.custo_bps:.1f}× a premissa de "
        f"{args.custo_bps:.0f} bps — o resultado não está sendo decidido pelo custo.\n")
    linhas.append(
        f"**O escopo do teto é mecânico, não da view.** O teto de carteira escala TODAS "
        f"as pontas pelo mesmo fator, inclusive a de SPY que vem do prior. Com "
        f"{c['views ativas por dia (média)']:.2f} view(s) ativa(s) por pregão em média, parte "
        f"do orçamento de Σ|w| sai do SPY para os pares das views — numa janela em que o SPY "
        f"fez {c['benchmark acumulado'] * 100:+.1f}%, reduzir exposição a ele custa caro por si "
        f"só. A seção seguinte mede o tamanho disso.\n")
    linhas.append(
        f"**Giro desfeito em 1–2 pregões: {c['giro desfeito em 1–2 pregões'] * 100:.0f}%.** "
        f"Essa fração do que se negocia é desfeita em dois pregões. É material, mas com a folga de custo "
        f"acima não é o que está segurando o resultado — entra como insumo da revisão "
        f"condicional do D1 (banda de não-negociação), não como veredito sobre o H.\n")

    linhas.append("\n## Onde o teto corta — carteira inteira × só o tilt\n")
    linhas.append(
        "Mesma varredura, dois escopos. `Σ|w| ≤ t` escala tudo; `tilt ≤ t` corta só "
        "`Σ|w − w_mkt|` e entrega a perna de mercado inteira. **Isto mede, não decide:** "
        "a D12 (nível do teto) segue aberta. O `c` da Lia já entrou (6q, nível 1), que "
        "era o passo 1 da ordem proposta por ela; esta tabela é o passo 2 — a Σ|w| "
        "medida COM a régua —, e o passo 3, escolher o teto, é da reunião.\n")
    linhas.append(
        "> Os rótulos NÃO são comparáveis entre si. `tilt ≤ t` limita o desvio, não a "
        "carteira: com w_mkt = 100% SPY, Σ|w| pode chegar a 1 + t. Compare pela "
        "**alavancagem medida**, que é a coluna ao lado.\n")
    linhas.append("| escopo | teto | Σ\\|w\\| medida | líquido | excesso | "
                  "tilt (soma diária) | giro/dia |")
    linhas.append("|---|---|---|---|---|---|---|")
    for teto in args.tetos:
        for escopo, no_tilt in (("carteira", False), ("só o tilt", True)):
            k = tabela[rotulo_teto(teto, no_tilt)]
            linhas.append(
                f"| {escopo} | {teto:g} | {k['alavancagem média (Σ|w|)']:.2f} | "
                f"{k['retorno acumulado líquido'] * 100:+.2f}% | "
                f"{k['excesso acumulado (líquido − benchmark)'] * 100:+.2f} pp | "
                f"{k['tilt (soma das contribuições diárias)'] * 100:+.2f}% | "
                f"{k['giro diário médio']:.3f} |")

    ganho = (t["excesso acumulado (líquido − benchmark)"]
             - c["excesso acumulado (líquido − benchmark)"])
    linhas.append(
        f"\n**No teto {teto0:g}, preservar a perna de mercado muda o excesso em "
        f"{ganho * 100:+.2f} pp** ({c['excesso acumulado (líquido − benchmark)'] * 100:+.2f} pp "
        f"→ {t['excesso acumulado (líquido − benchmark)'] * 100:+.2f} pp), a um custo de "
        f"alavancagem de {c['alavancagem média (Σ|w|)']:.2f} → "
        f"{t['alavancagem média (Σ|w|)']:.2f} de Σ|w| médio. Com o escopo no tilt a carteira "
        + ("**passa a bater** o comprar-e-segurar SPY"
           if t["excesso acumulado (líquido − benchmark)"] > 0
           else "**continua perdendo** do comprar-e-segurar SPY") + ".\n")
    # Comparação a alavancagem IGUAL — a única honesta entre os dois escopos.
    # Quando o teto morde todo dia, cortar o tilt em t e a carteira em 1 + t
    # caem no mesmo Σ|w| medido; o script confere em vez de supor.
    alav, exc = (tabela.loc["alavancagem média (Σ|w|)"],
                 tabela.loc["excesso acumulado (líquido − benchmark)"])
    pares = [(rotulo_teto(x, True), r)
             for x in args.tetos
             for r in (rotulo_teto(y, False) for y in args.tetos)
             if abs(alav[r] - alav[rotulo_teto(x, True)]) < 1e-6]
    if pares:
        linhas.append("\n**A mesma comparação com Σ|w| IGUAL** (o rótulo engana, a "
                      "alavancagem medida não):\n")
        for rt, rc in pares:
            linhas.append(f"- Σ|w| = **{alav[rt]:.2f}**: `{rc}` dá "
                          f"{exc[rc] * 100:+.2f} pp de excesso, `{rt}` dá "
                          f"{exc[rt] * 100:+.2f} pp — diferença de "
                          f"**{(exc[rt] - exc[rc]) * 100:+.2f} pp** só por causa de "
                          f"ONDE o teto corta, com o mesmo tamanho de carteira.")
        linhas.append("")
    linhas.append(
        f"A parcela de tilt é o que separa os dois desenhos: {c['tilt (soma das contribuições diárias)'] * 100:+.2f}% "
        f"no corte de carteira contra {t['tilt (soma das contribuições diárias)'] * 100:+.2f}% no corte de tilt. "
        "No corte de carteira essa parcela mistura duas coisas — o tilt da view **e** o pedaço "
        "da perna de mercado que o corte tirou; no corte de tilt ela é só a view. A diferença "
        "entre as duas é a conta do que o escopo do teto cobra por si só.\n")

    # --- robustez γ (promessa da seção 9) -----------------------------------
    # A D1.1 fecha o v1 em γ = 1,0 (sem correção): 9 mercados resolvidos não
    # calibram curva própria. A promessa da seção 9 é REPORTAR o resultado
    # também em γ = 1,1 e 1,25 — não escolher entre eles.
    teto_ref = min(args.tetos)
    gamma_linhas = {}
    for g in args.gammas:
        montador.set_gamma(g)   # re-semeia: a semente depende de γ
        res = run_backtest(retornos, montador, w_mkt, datas=datas, tau=TAU,
                           delta=DELTA, custo_bps=args.custo_bps,
                           teto_alavancagem=teto_ref, teto_no_tilt=True,
                           regua=regua)
        gamma_linhas[g] = summary(res, benchmark=retornos["SPY"])
        montador.reset()
    montador.set_gamma(FL_GAMMA_V1)

    linhas.append("\n## Robustez γ (favorite-longshot) — promessa da seção 9\n")
    linhas.append(
        f"O v1 roda em **γ = {FL_GAMMA_V1:g}** (D1.1: sem correção — 9 mercados "
        "resolvidos não calibram curva própria, e importar γ de aposta esportiva "
        "mexeria a mediana sem âncora no nosso dado). A coluna existe para "
        "**reportar**, não para escolher: se o resultado só sobrevive em um γ, "
        "isso tem de aparecer.\n")
    linhas.append(f"Medido no escopo de referência (**tilt ≤ {teto_ref:g}**), com a "
                  "semente da 2.3 recalculada em cada γ — a surpresa depende dele.\n")
    linhas.append("| γ | excesso × SPY | líquido | sharpe | Σ\\|w\\| média | giro diário |")
    linhas.append("|---|---|---|---|---|---|")
    for g, s in gamma_linhas.items():
        linhas.append(
            f"| {g:g} | {s['excesso acumulado (líquido − benchmark)'] * 100:+.2f} pp | "
            f"{s['retorno acumulado líquido'] * 100:+.1f}% | "
            f"{s['sharpe anualizado (excesso zero)']:.2f} | "
            f"{s['alavancagem média (Σ|w|)']:.2f} | {s['giro diário médio']:.3f} |")
    excs = [s["excesso acumulado (líquido − benchmark)"] for s in gamma_linhas.values()]
    linhas.append(
        f"\n**Faixa do excesso na varredura: {min(excs) * 100:+.2f} pp a "
        f"{max(excs) * 100:+.2f} pp** — "
        + ("o sinal do resultado **não** depende do γ nesta janela.\n"
           if min(excs) * max(excs) > 0 else
           "⚠️ o sinal do resultado **muda** com o γ: a conclusão do v1 não é "
           "robusta à correção de favorite-longshot, e isso vale mais que o "
           "número central.\n"))

    # --- limitações declaradas (D23b / D23d) ---------------------------------
    # Obrigatórias pela D22: "sem os 3 maiores" e acerto de sinal têm de estar
    # escritos, e a leitura do número da entrega não pode ficar por conta de
    # quem lê. Os NÚMEROS de atribuição são citados do artefato que os mede
    # (`Views_novas.md`) em vez de copiados: número copiado envelhece calado —
    # foi assim que a linha "views ativas: 2.2 e 2.3" sobreviveu à D23. O que
    # dá para derivar da própria rodada é derivado aqui.
    pregoes_por_view = pd.Series(
        [d["view"] for d in views_do_dia]).value_counts().sort_values(ascending=False)

    linhas.append("\n## Limitações declaradas — leia antes de citar o número\n")
    linhas.append(
        "> Obrigatório pela **D22/D23b**, e escrito aqui porque o lugar de uma "
        "limitação é o artefato que produz o número, não a seção de quem o cita.\n")
    linhas.append(
        "**1. O excesso da entrega NÃO é desempenho das views novas.** Medida uma a "
        "uma contra o v1 anterior de duas views (`Dump/analises/Views_novas.md`), a "
        "**15b** entrega quase tudo num único pregão — tirados os três maiores dias, "
        "o Δ dela vira **negativo** — e a **15g** mede **negativo** no backtest. As "
        "duas têm acerto de sinal de ~49%, ou seja cara ou coroa. Pela D22 sinal "
        "fraco **não reprova** (a régua de admissão é mecanismo, não performance), "
        "mas o número-título não pode ser lido como se as duas o tivessem "
        "carregado.\n")
    linhas.append("**2. Cobertura desigual — cada view vive num número diferente de "
                  "pregões:**\n")
    for view, n in pregoes_por_view.items():
        linhas.append(f"- `{view}`: **{n} de {len(datas)}** pregões "
                      f"({n / len(datas) * 100:.0f}%)")
    linhas.append(
        "\nA 15b vive só em dia de anúncio, **por desenho**; a 15g acaba junto com o "
        "mercado de trajetória (não há mercado de 2026 no `data/`). Média de views "
        f"por pregão: **{c['views ativas por dia (média)']:.2f}** de "
        f"{len(pregoes_por_view)}.\n")
    linhas.append(
        "**3. O Ω é diagonal e não enxerga correlação entre views.** Com ρ +0,673 "
        "entre o sinal-fonte da 15g e o da 2.2 (`Dump/analises/Ortogonalidade.md`), "
        "isso deixou de ser hipotético: duas views correlacionadas entram como se "
        "fossem informação independente, e o BL soma confiança que não existe. É "
        "**limitação de modelo declarada** (D15a, D22e), não bug — o Ω da Lia dosa "
        "cada view, não o par.\n")
    linhas.append(
        "**4. Horizonte do Q (D4.1) segue aberto, fora do caminho crítico.** Nenhuma "
        "das quatro views tem `horizonte_q_dias ≠ 1`, então o empilhamento é "
        "homogêneo aqui. O caso concreto medido está na view C, que o `stack_views` "
        "**recusou** empilhar por Q acumulado em k dias — ela ficou fora do v1 "
        "(D23f), e é o exemplo de que a limitação morde de verdade.\n")
    linhas.append(
        "**5. O conjunto de views está FECHADO em quatro** (D23e). A camada "
        "tática ANTIGA (orçamentos de drift, 12c) segue desligada; a camada "
        + ("v2 está **LIGADA** (D28.13) e o overlay das sleeves entra nos "
           "números acima" if sleeves_ligadas else "v2 está desligada")
        + ".\n")

    # --- CSV das séries (insumo dos gráficos) --------------------------------
    # O markdown acima reporta escalares; curva, drawdown e trades por dia são
    # séries. Sem este dump elas morrem na memória e qualquer gráfico obriga a
    # re-rodar a varredura inteira. Os pesos por ativo e os diagnostics por view
    # ficam de fora: nenhum bloco da p.4 os consome hoje.
    if args.csv_dir:
        destino = Path(args.csv_dir)
        destino.mkdir(parents=True, exist_ok=True)
        pd.concat(diarios).to_csv(destino / "backtest_diario.csv")
        tabela.to_csv(destino / "backtest_metricas.csv")
        pd.DataFrame(gamma_linhas).to_csv(destino / "backtest_gamma.csv")

    Path(args.saida).write_text("\n".join(linhas) + "\n", encoding="utf-8")
    sys.stdout.write(tabela.to_string() + f"\n\nescrito: {args.saida}\n")


if __name__ == "__main__":
    main()
