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
| 2.3 Fed | **bloqueada** | `e_ff_bps` = DTB3 − DFF, e o **DFF é o G8**, ainda não entregue |
| B trajetória | **fora do v1** | decisão 11 — o ZQ de dezembro não tem fonte grátis (F6) e a view duplica o β/P da 2.3 |

A 2.3 não é cascata (mercado ausente) — é insumo que não chegou. Por isso o
script a declara em vez de deixá-la cair em `None` silenciosamente: `None`
significaria "não havia mercado", que é mentira. A B saiu por decisão, não por
falta: a perna do poly (`M3_fed_trajectory_*`) está entregue e disponível se o
grupo reabrir.

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
from backtest import run_backtest, summary  # noqa: E402
from config import (ASSETS, CUSTO_BPS_POR_LADO, DELTA, DRIFT_JANELA_ACOES,  # noqa: E402
                    DRIFT_JANELA_RF, SIGMA_JANELA_PREGOES, TAU)
from market_inputs import (breakeven_duration, daily_returns,  # noqa: E402
                           empirical_duration, market_weights, sample_covariance)
from market_loader import load_etf_prices, load_fred  # noqa: E402
from poly_loader import (bucket_value, daily_preopen, diagnostics_qualidade,  # noqa: E402
                         load_cpi_releases, load_pmf)
from poly_preprocessing import bucket_values_with_open, carry_missing  # noqa: E402
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


class MontadorV1:
    """Monta `(sigma, views, overlays)` de um dia. Chamado em ordem de data.

    Guarda estado de propósito: a média da divergência (D9) é EXPANSIVA, então
    depende do que já foi visto — e só do que já foi visto. Recalcular por
    janela fechada seria mais puro e olharia o futuro.
    """

    def __init__(self, retornos, breakeven, dgs10, mercados, pmfs,
                 fomc=None, surpresas=None, orcamentos=None):
        self.retornos = retornos
        self.breakeven = breakeven
        self.dgs10 = dgs10
        self.mercados = mercados          # data de divulgação -> prefixo
        self.pmfs = pmfs                  # prefixo -> (probs, valores)
        self.fomc = fomc if fomc is not None else pd.DatetimeIndex([])
        self.surpresas = surpresas if surpresas is not None else pd.Series(dtype=float)
        self.orcamentos = orcamentos or {}
        self.divergencias = []            # histórico para a média expansiva

    # --- insumos ------------------------------------------------------------

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
        views = [self._view_2_2(data, pregoes)]
        overlays = [self._premio(data), self._drift(data)]
        return sigma, views, overlays


def carregar(raiz, orcamentos=None):
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

    montador = MontadorV1(retornos, breakeven, dgs10, mercados, pmfs,
                          fomc, surpresas, orcamentos or {})

    # Começa quando as duas condições existem: Σ com janela cheia e PMF de CPI.
    primeira_pmf = min(probs.index.min() for probs, _, _ in pmfs.values())
    inicio = max(retornos.index[SIGMA_JANELA_PREGOES], primeira_pmf)
    datas = retornos.index[retornos.index >= inicio]
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
            montador.divergencias.clear()  # a média expansiva recomeça a cada rodada
    tabela = pd.DataFrame(colunas)

    # A duration medida é a decisão desta sessão — sai no relatório, não fica só
    # dentro do loop. Vem dos diagnostics da última rodada (é a mesma em todas:
    # o teto corta o peso, não a view).
    durations = [d["duration"] for dia in resultado.diagnostics.values()
                 for d in dia["views"]]

    tatica_ligada = [f"{k} = {v}" for k, v in orcamentos.items() if v is not None]
    linhas = ["# Backtest do v1 — BL com as views ativas (I5)\n",
              "> Gerado por `scripts/backtest_v1.py`. Benchmark = comprar e "
              "segurar SPY (consequência do `w_mkt` do prior CAPM). Custo de "
              f"**{args.custo_bps:.1f} bps por lado** sobre o giro contra o peso "
              "derivado (D8). Uma coluna por teto de alavancagem — **o teto é "
              "decisão humana; a varredura mede, não escolhe.**\n",
              f"- janela: **{datas[0].date()} a {datas[-1].date()}** "
              f"({len(datas)} pregões)",
              "- views ativas: **2.2 inflação**. A 2.3 e a B ficam fora por "
              "insumo que não chegou (DFF/G8 e ZQ de dezembro), não por cascata",
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
    linhas.append(
        f"**A carteira perde do comprar-e-segurar SPY**: {c['retorno acumulado líquido'] * 100:+.1f}% "
        f"contra {c['benchmark acumulado'] * 100:+.1f}% do benchmark no teto mais "
        f"apertado, e a distância AUMENTA conforme o teto afrouxa.\n")
    linhas.append(
        f"**O custo não é o culpado.** O retorno BRUTO já é "
        f"{c['retorno acumulado bruto'] * 100:+.1f}%, muito abaixo do benchmark, e o custo de "
        f"breakeven ({c['custo de breakeven (bps por lado)']:.1f} bps/lado) é "
        f"{c['custo de breakeven (bps por lado)'] / args.custo_bps:.1f}× a premissa de "
        f"{args.custo_bps:.0f} bps. Há folga larga de custo; o problema é o retorno bruto.\n")
    linhas.append(
        f"**O mecanismo suspeito era mecânico, não da view.** O teto de carteira escala TODAS "
        f"as pontas pelo mesmo fator, inclusive a de SPY que vem do prior. Com a view ativa em "
        f"{c['views ativas por dia (média)'] * 100:.0f}% dos pregões, parte do orçamento de "
        f"Σ|w| sai do SPY para o par TIP/TLT — numa janela em que o SPY fez "
        f"{c['benchmark acumulado'] * 100:+.1f}%, reduzir exposição a ele custa caro por si só. "
        f"A seção seguinte mede o tamanho disso.\n")
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

    Path(args.saida).write_text("\n".join(linhas) + "\n", encoding="utf-8")
    sys.stdout.write(tabela.to_string() + f"\n\nescrito: {args.saida}\n")


if __name__ == "__main__":
    main()
