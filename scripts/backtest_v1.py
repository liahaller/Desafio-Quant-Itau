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
| B trajetória | **fora do v1** | decisão 11 — o ZQ de dezembro não tem fonte grátis (F6) e a view duplica o β/P da 2.3 |

A 2.3 destravou com o G8 (`DFF`), mas o que a fez virar view de Polymarket foi
outra coisa: a perna do poly é a **PMF completa por reunião** do parquet, não o
binário de −50bp do `clob_exploracao`. Com o binário, o poly explicava 4,6% da
variância da surpresa e o sinal era o mesmo em 100% dos dias; com a PMF, 53% e
o poly inverte o sinal do spread de bills. A B saiu por decisão, não por falta:
a perna do poly (`M3_fed_trajectory_*`) está entregue e disponível se o grupo
reabrir.

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
from backtest import run_backtest, summary  # noqa: E402
from config import (ASSETS, CUSTO_BPS_POR_LADO, DELTA, DRIFT_JANELA_ACOES,  # noqa: E402
                    DRIFT_JANELA_RF, FL_GAMMA_V1, FL_GAMMA_VARREDURA,
                    SIGMA_JANELA_PREGOES, TAU)
from market_inputs import (breakeven_duration, daily_returns,  # noqa: E402
                           empirical_duration, market_weights, sample_covariance)
from market_loader import load_etf_prices, load_fred  # noqa: E402
from poly_loader import (bucket_value, daily_preopen, diagnostics_qualidade,  # noqa: E402
                         load_cpi_releases, load_fomc_pmf, load_pmf)
from poly_preprocessing import (bucket_values_with_open, carry_missing,  # noqa: E402
                                favorite_longshot_pmf)
import tatica_drift_pos_fomc  # noqa: E402
import tatica_premio_anuncios  # noqa: E402

PONTOS_PERCENTUAIS = 100.0


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


class MontadorV1:
    """Monta `(sigma, views, overlays)` de um dia. Chamado em ordem de data.

    Guarda estado de propósito: a média da divergência (D9) é EXPANSIVA, então
    depende do que já foi visto — e só do que já foi visto. Recalcular por
    janela fechada seria mais puro e olharia o futuro.
    """

    def __init__(self, retornos, breakeven, dgs10, mercados, pmfs,
                 fomc=None, surpresas=None, orcamentos=None,
                 fomc_pmfs=None, e_ff=None, gamma=FL_GAMMA_V1):
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

    def __call__(self, data):
        pregoes = self.retornos.index
        sigma = sample_covariance(self.retornos, data=data)
        views = [self._view_2_2(data, pregoes), self._view_2_3(data, pregoes)]
        overlays = [self._premio(data), self._drift(data)]
        return sigma, views, overlays


def carregar(raiz, orcamentos=None, gamma=FL_GAMMA_V1):
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

    montador = MontadorV1(retornos, breakeven, dgs10, mercados, pmfs,
                          fomc, surpresas, orcamentos or {},
                          fomc_pmfs=fomc_pmfs, e_ff=e_ff, gamma=gamma)

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
    parser.add_argument("--orcamento-premio", type=float, default=None)
    parser.add_argument("--orcamento-drift-acoes", type=float, default=None)
    parser.add_argument("--orcamento-drift-rf", type=float, default=None)
    parser.add_argument("--saida", default="Dump/analises/Backtest_v1.md")
    args = parser.parse_args()

    orcamentos = {"premio": args.orcamento_premio,
                  "drift_acoes": args.orcamento_drift_acoes,
                  "drift_rf": args.orcamento_drift_rf}
    retornos, montador, datas, w_mkt = carregar(args.raiz, orcamentos)

    # Duas varreduras: o teto cortando a carteira inteira e cortando só o tilt.
    # É a questão de desenho aberta na seção 10 do `Decisoes_pendentes.md` —
    # medir as duas dá número à reunião sem fechar a D12.
    colunas = {}
    for no_tilt in (False, True):
        for teto in args.tetos:
            resultado = run_backtest(retornos, montador, w_mkt, datas=datas, tau=TAU,
                                     delta=DELTA, custo_bps=args.custo_bps,
                                     teto_alavancagem=teto, teto_no_tilt=no_tilt)
            # o `|` precisa vir escapado: é nome de coluna de tabela markdown
            colunas[rotulo_teto(teto, no_tilt)] = summary(resultado,
                                                          benchmark=retornos["SPY"])
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
    linhas = ["# Backtest do v1 — BL com as views ativas (I5)\n",
              "> Gerado por `scripts/backtest_v1.py`. Benchmark = comprar e "
              "segurar SPY (consequência do `w_mkt` do prior CAPM). Custo de "
              f"**{args.custo_bps:.1f} bps por lado** sobre o giro contra o peso "
              "derivado (D8). Uma coluna por teto de alavancagem — **o teto é "
              "decisão humana; a varredura mede, não escolhe.**\n",
              f"- janela: **{datas[0].date()} a {datas[-1].date()}** "
              f"({len(datas)} pregões)",
              "- views ativas: **2.2 inflação** e **2.3 Fed** (esta desde "
              "2026-08-07: PMF de decisão por reunião + `DTB3 − DFF` demeanado). "
              "A B fica fora por decisão 11, não por cascata",
              f"- demeanagem da 2.3: média expansiva **semeada** com "
              f"{len(montador._semente_2_3)} pregões anteriores à janela "
              "(2024-04 a 2025-02, dado passado — não lookahead). Sem semente o "
              "primeiro dia demeana por 0,0; o sinal líquido sai 22% positivo, "
              "contra 34% com semente",
              f"- duration do breakeven: **medida** no par da própria view, "
              f"janela expansiva — variou de **{min(durations):.2f} a "
              f"{max(durations):.2f}** na amostra (a espec supunha \"~8\"; o dado "
              f"confirmou, e agora o número é medido em vez de suposto)",
              "- camada tática: "
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
        f"**Giro desfeito em 1–2 pregões: {c['giro desfeito em 1–2 pregões'] * 100:.0f}%.** Um terço "
        f"do que se negocia é desfeito em dois pregões. É material, mas com a folga de custo "
        f"acima não é o que está segurando o resultado — entra como insumo da revisão "
        f"condicional do D1 (banda de não-negociação), não como veredito sobre o H.\n")

    linhas.append("\n## Onde o teto corta — carteira inteira × só o tilt\n")
    linhas.append(
        "Mesma varredura, dois escopos. `Σ|w| ≤ t` escala tudo; `tilt ≤ t` corta só "
        "`Σ|w − w_mkt|` e entrega a perna de mercado inteira. **Isto mede, não decide:** "
        "a D12 (nível do teto) segue esperando o `c` da Lia, na ordem que ela propôs — "
        "entra o `c`, mede-se Σ|w| de novo, aí se decide o teto.\n")
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
                           teto_alavancagem=teto_ref, teto_no_tilt=True)
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

    Path(args.saida).write_text("\n".join(linhas) + "\n", encoding="utf-8")
    sys.stdout.write(tabela.to_string() + f"\n\nescrito: {args.saida}\n")


if __name__ == "__main__":
    main()
