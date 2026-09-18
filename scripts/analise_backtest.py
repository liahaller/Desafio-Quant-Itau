"""Análise estatística do backtest congelado — inferência, concentração, estabilidade. Felipe.

O `backtest_v1.py` entrega um número (+3,04 pp sobre o SPY em 374 pregões); este
script responde "isso é sorte?" com a régua que a literatura usa para julgar uma
estratégia. **Mede; não decide** — não roda o backtest, não toca `src/`, lê só o
que já está gravado em `Uteis/dados/` (cenário de referência `tilt ≤ 1`).

  A  inferência do número-título — IC do Sharpe (Lo 2002 e bootstrap
     estacionário de Politis-Romano 1994), IC do excesso e da diferença de
     Sharpe (Ledoit-Wolf 2008), alpha com Newey-West, IR/TE, PSR e MinTRL
     (Bailey-López de Prado 2012), DSR (Bailey-López de Prado 2014) com o nº de
     tentativas lido do registro do projeto.
  B  de onde vem — hit ratio, payoff, HHI de concentração (López de Prado 2018,
     cap. 14), peso dos 3/10 maiores dias, tilt por nº de views ativas.
  C  estabilidade — metades, regime do SPY (alta × queda), meses, rolling IR e
     beta, drawdown e time under water.
  D  implementação — giro, giro desfeito, breakeven (relidos do backtest).

Escolhas pré-registradas (D33, sessão 48): série `tilt ≤ 1`; taxa livre zero
(convenção do projeto); bootstrap estacionário com bloco médio 10 pregões,
B = 2 000, semente fixa; Newey-West 5 lags; metades por contagem de pregões;
regime pelo sinal do retorno do SPY no dia; SR* = 0; nível 95 %; N do DSR em
GRADE (não se escolhe um), com V medido nas configurações registradas e, como
cota superior, V de tentativas independentes.

Uso:
    python scripts/analise_backtest.py            # mede, grava CSV, figuras e MD
    python scripts/analise_backtest.py --demo     # auto-teste sintético
"""

import sys
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
from scipy import stats

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "scripts"))

from config import PREGOES_POR_ANO                      # noqa: E402
from graficos_p4 import drawdown, salvar                # noqa: E402

# --- escolhas pré-registradas (D33) ------------------------------------------
CENARIO = "tilt ≤ 1"
B_BOOT, SEMENTE, BLOCO = 2000, 20260918, 10
NW_LAGS = 5
JANELA_ROLLING = 63
NIVEL = 0.95
# Nº de tentativas registradas no projeto, para a grade do DSR (nenhum é "o" N):
#   configurações com Sharpe gravado (medido abaixo) · 31 hipóteses do LOG
#   (peneira do slide 13) · + ~200 células da busca tática (D27).
N_HIPOTESES, N_CELULAS_TATICA = 31, 200

DADOS = RAIZ / "Uteis" / "dados"
SAIDA = DADOS / "analise_backtest"
GRAFICOS = RAIZ / "Uteis" / "graficos"
MD = RAIZ / "Uteis" / "analises" / "Analise_backtest.md"
PP = 100.0

# ponytail: paleta e rc copiados de estudo_polymarket (importá-lo custa 30 s de dado)
SLIDE = {"laranja": "#FFB531", "azul": "#4F8EF7", "verde": "#2FD3B0", "cinza": "#8395B5",
         "vermelho": "#C25B54", "texto": "#F5F7FB", "suave": "#BAC6DA",
         "grade": "#2A3F63", "fundo": "#0A1325"}


def _estilo_slide():
    return plt.rc_context({
        "font.size": 12, "axes.titlesize": 13, "legend.fontsize": 11,
        "xtick.labelsize": 11, "ytick.labelsize": 11, "axes.labelsize": 12,
        "text.color": SLIDE["texto"], "axes.labelcolor": SLIDE["suave"],
        "xtick.color": SLIDE["suave"], "ytick.color": SLIDE["suave"],
        "axes.edgecolor": SLIDE["grade"], "grid.color": SLIDE["grade"],
        "axes.spines.top": False, "axes.spines.right": False, "figure.autolayout": True})


# =============================================================================
# A. Inferência
# =============================================================================
def sharpe(r):
    r = np.asarray(r, dtype=float)
    return float(r.mean() / r.std(ddof=1))


def anual(sr_diario):
    return sr_diario * np.sqrt(PREGOES_POR_ANO)


def sharpe_ic_lo(r, nivel=NIVEL):
    """IC do Sharpe DIÁRIO por Lo (2002), iid: SE = √((1 + SR²/2)/T)."""
    sr, T = sharpe(r), len(r)
    se = np.sqrt((1 + 0.5 * sr ** 2) / T)
    z = stats.norm.ppf(0.5 + nivel / 2)
    return sr, sr - z * se, sr + z * se


def indices_estacionarios(T, rng, p=1.0 / BLOCO):
    """Uma reamostra de Politis-Romano: blocos de comprimento geométrico, circular."""
    idx = np.empty(T, dtype=int)
    i = rng.integers(T)
    for k in range(T):
        if k and rng.random() < p:
            i = rng.integers(T)
        idx[k] = i
        i = (i + 1) % T
    return idx


def bootstrap_estacionario(r, b, B=B_BOOT, semente=SEMENTE):
    """Reamostra (r, b) com os MESMOS índices; devolve DataFrame de estatísticas.

    sr_k / sr_b anualizados, d_sr = diferença (Ledoit-Wolf por bootstrap),
    excesso = retorno composto de r − de b (pp), ir = IR anualizado de r − b.
    """
    r, b = np.asarray(r, dtype=float), np.asarray(b, dtype=float)
    rng = np.random.default_rng(semente)
    linhas = []
    for _ in range(B):
        ix = indices_estacionarios(len(r), rng)
        rr, bb = r[ix], b[ix]
        e = rr - bb
        linhas.append((anual(sharpe(rr)), anual(sharpe(bb)), anual(sharpe(rr) - sharpe(bb)),
                       (np.prod(1 + rr) - np.prod(1 + bb)) * PP,
                       e.mean() / e.std(ddof=1) * np.sqrt(PREGOES_POR_ANO)))
    return pd.DataFrame(linhas, columns=["sr_k", "sr_b", "d_sr", "excesso", "ir"])


def ic(amostras, nivel=NIVEL):
    a = (1 - nivel) / 2
    return float(np.percentile(amostras, 100 * a)), float(np.percentile(amostras, 100 * (1 - a)))


def newey_west(X, y, lags=NW_LAGS):
    """OLS com covariância HAC de Newey-West (Bartlett). (β, V). Copiado de estudo_polymarket."""
    X, y = np.asarray(X, dtype=float), np.asarray(y, dtype=float)
    XtX_inv = np.linalg.inv(X.T @ X)
    beta = XtX_inv @ X.T @ y
    u = (y - X @ beta)[:, None] * X
    S = u.T @ u
    for L in range(1, lags + 1):
        w = 1 - L / (lags + 1)
        G = u[L:].T @ u[:-L]
        S += w * (G + G.T)
    return beta, XtX_inv @ S @ XtX_inv


def psr(sr, T, g3, g4, sr_ref=0.0):
    """Probabilistic Sharpe Ratio (Bailey-LdP 2012): P(SR verdadeiro > sr_ref).

    `sr` diário, `g3` assimetria, `g4` curtose (não excedente).
    """
    return float(stats.norm.cdf((sr - sr_ref) * np.sqrt(T - 1)
                                / np.sqrt(1 - g3 * sr + (g4 - 1) / 4 * sr ** 2)))


def min_trl(sr, g3, g4, sr_ref=0.0, nivel=NIVEL):
    """Comprimento mínimo de track record para PSR(sr_ref) ≥ nivel."""
    z = stats.norm.ppf(nivel)
    return float(1 + (1 - g3 * sr + (g4 - 1) / 4 * sr ** 2) * (z / (sr - sr_ref)) ** 2)


def sr_esperado_max(N, V):
    """E[max SR] de N tentativas de ruído com variância V (Bailey-LdP 2014)."""
    if N <= 1:
        return 0.0
    g = np.euler_gamma
    return float(np.sqrt(V) * ((1 - g) * stats.norm.ppf(1 - 1 / N)
                               + g * stats.norm.ppf(1 - 1 / (N * np.e))))


def dsr(sr, T, g3, g4, N, V):
    """Deflated Sharpe Ratio = PSR contra o SR que N tentativas de ruído já dariam."""
    return psr(sr, T, g3, g4, sr_ref=sr_esperado_max(N, V))


def sharpes_registrados(dados=DADOS):
    """Sharpe de cada configuração já medida e gravada (tetos, γ, bandas)."""
    linha = "sharpe anualizado (excesso zero)"
    met = pd.read_csv(dados / "backtest_metricas.csv", index_col=0).loc[linha]
    gam = pd.read_csv(dados / "backtest_gamma.csv", index_col=0).loc[linha]
    ban = pd.read_csv(dados / "curva_banda.csv")["sharpe"]
    return pd.concat([met.astype(float), gam.astype(float), ban.astype(float)], ignore_index=True)


def bloco_inferencia(d, boot):
    r, b = d["r_liquido"].values, d["r_benchmark"].values
    T, e = len(r), r - b
    g3, g4 = float(stats.skew(r)), float(stats.kurtosis(r, fisher=False))
    sr, lo, hi = sharpe_ic_lo(r)
    beta_hat, V = newey_west(np.column_stack([np.ones(T), b]), r)
    alpha_a, t_alpha = beta_hat[0] * PREGOES_POR_ANO, beta_hat[0] / np.sqrt(V[0, 0])
    tilt_liq = (d["r_tilt"] - d["custo"]).values
    te = e.std(ddof=1) * np.sqrt(PREGOES_POR_ANO)
    excesso = (np.prod(1 + r) - np.prod(1 + b)) * PP
    linhas = [
        ("pregões (T)", T, ""),
        ("Sharpe Kairós", anual(sr), "anualizado, taxa livre zero"),
        ("Sharpe Kairós · IC95 Lo (iid)", f"[{anual(lo):.2f}; {anual(hi):.2f}]", "Lo (2002)"),
        ("Sharpe Kairós · IC95 bootstrap", "[{:.2f}; {:.2f}]".format(*ic(boot.sr_k)), "estacionário"),
        ("Sharpe SPY", anual(sharpe(b)), ""),
        ("ΔSharpe (K − SPY)", anual(sr - sharpe(b)), ""),
        ("ΔSharpe · IC95 bootstrap", "[{:.2f}; {:.2f}]".format(*ic(boot.d_sr)), "Ledoit-Wolf (2008)"),
        ("P(ΔSharpe > 0)", float((boot.d_sr > 0).mean()), "bootstrap"),
        ("excesso acumulado (pp)", excesso, "líquido − SPY, composto"),
        ("excesso · IC95 bootstrap (pp)", "[{:.1f}; {:.1f}]".format(*ic(boot.excesso)), ""),
        ("P(excesso > 0)", float((boot.excesso > 0).mean()), "bootstrap"),
        ("alpha anualizado", alpha_a, "vs SPY, taxa livre zero"),
        ("t do alpha (Newey-West)", t_alpha, f"{NW_LAGS} lags · régua de Harvey-Liu: 3"),
        ("beta vs SPY", beta_hat[1], ""),
        ("information ratio", e.mean() * PREGOES_POR_ANO / te, "excesso / tracking error"),
        ("tracking error", te, "anualizado"),
        ("t do tilt líquido", tilt_liq.mean() / (tilt_liq.std(ddof=1) / np.sqrt(T)), "r_tilt − custo"),
        ("assimetria", g3, "retornos diários"),
        ("curtose", g4, "não excedente"),
        ("ACF(1) dos retornos", float(pd.Series(r).autocorr(1)), ""),
        ("PSR(SR* = 0)", psr(sr, T, g3, g4), "Bailey-LdP (2012)"),
        ("MinTRL a 95 % (pregões)", min_trl(sr, g3, g4), f"temos {T}"),
    ]
    return pd.DataFrame(linhas, columns=["métrica", "valor", "nota"]), (sr, g3, g4)


def bloco_dsr(d, boot, momentos):
    """Grade N × V do DSR — nenhuma linha é 'a' correção; a tabela inteira é o resultado."""
    sr, g3, g4 = momentos
    T = len(d)
    regs = sharpes_registrados()
    n_reg = len(regs)
    V_reg = float(regs.var(ddof=1)) / PREGOES_POR_ANO          # variância DIÁRIA
    V_iid = (1 + 0.5 * sr ** 2) / T                             # SE² de uma tentativa de ruído (Lo)
    grade = [("configurações com Sharpe gravado", n_reg), ("hipóteses medidas (LOG)", N_HIPOTESES),
             ("+ células da busca tática (D27)", N_HIPOTESES + N_CELULAS_TATICA)]
    linhas = []
    for rot, N in grade:
        for nome_v, V in (("V medido nas configurações", V_reg), ("V de tentativas independentes", V_iid)):
            linhas.append((rot, N, nome_v, anual(np.sqrt(V)), anual(sr_esperado_max(N, V)),
                           dsr(sr, T, g3, g4, N, V)))
    return pd.DataFrame(linhas, columns=["tentativas", "N", "variância", "σ(SR) anual",
                                         "E[max SR] anual", "DSR"])


# =============================================================================
# B. De onde vem
# =============================================================================
def hhi(x):
    """Concentração de Herfindahl normalizada (0 = uniforme, 1 = um dia só)."""
    x = np.asarray(x, dtype=float)
    if len(x) < 2:
        return float("nan")
    w = x / x.sum()
    return float(((w ** 2).sum() - 1 / len(x)) / (1 - 1 / len(x)))


def bloco_concentracao(d):
    tt = d["r_tilt"]
    ativo = tt[tt != 0]
    s = tt.sort_values(ascending=False)
    linhas = [
        ("dias com tilt ≠ 0", int((tt != 0).sum()), ""),
        ("hit ratio do tilt", float((ativo > 0).mean()), "dias com tilt > 0"),
        ("ganho médio nos dias + (bps)", float(tt[tt > 0].mean() * 1e4), ""),
        ("perda média nos dias − (bps)", float(tt[tt < 0].mean() * 1e4), ""),
        ("payoff (ganho / |perda|)", float(tt[tt > 0].mean() / -tt[tt < 0].mean()), ""),
        ("HHI dos dias positivos", hhi(tt[tt > 0]), "López de Prado (2018)"),
        ("HHI dos dias negativos", hhi(-tt[tt < 0]), ""),
        ("soma do tilt (pp)", float(tt.sum() * PP), "perna das views, bruta"),
        ("3 maiores dias (pp)", float(s.head(3).sum() * PP), ""),
        ("sem os 3 maiores (pp)", float((tt.sum() - s.head(3).sum()) * PP), ""),
        ("3 piores dias (pp)", float(s.tail(3).sum() * PP), ""),
        ("sem os 3 piores (pp)", float((tt.sum() - s.tail(3).sum()) * PP), ""),
        ("10 maiores dias (pp)", float(s.head(10).sum() * PP), ""),
    ]
    return pd.DataFrame(linhas, columns=["métrica", "valor", "nota"])


def bloco_views_dia(d):
    g = d.groupby("n_views")["r_tilt"]
    return pd.DataFrame({"views ativas": g.size().index, "dias": g.size().values,
                         "tilt médio (bps)": g.mean().values * 1e4,
                         "hit": g.apply(lambda x: (x > 0).mean()).values})


# =============================================================================
# C. Estabilidade
# =============================================================================
def _resumo(r, b):
    return {"retorno K": (np.prod(1 + r) - 1) * PP, "retorno SPY": (np.prod(1 + b) - 1) * PP,
            "excesso (pp)": (np.prod(1 + r) - np.prod(1 + b)) * PP,
            "Sharpe K": anual(sharpe(r)), "Sharpe SPY": anual(sharpe(b)), "pregões": len(r)}


def bloco_metades(d):
    h = len(d) // 2
    r, b = d["r_liquido"].values, d["r_benchmark"].values
    return pd.DataFrame({"1ª metade": _resumo(r[:h], b[:h]), "2ª metade": _resumo(r[h:], b[h:])}).T


def bloco_regime(d):
    r, b = d["r_liquido"], d["r_benchmark"]
    e = r - b
    linhas = []
    for nome, m in (("SPY em alta", b > 0), ("SPY em queda", b <= 0)):
        linhas.append((nome, int(m.sum()), r[m].mean() * 1e4, b[m].mean() * 1e4,
                       e[m].mean() * 1e4, float((e[m] > 0).mean())))
    return pd.DataFrame(linhas, columns=["regime", "dias", "K médio (bps)", "SPY médio (bps)",
                                         "excesso médio (bps)", "hit do excesso"])


def bloco_mensal(d):
    r, b = d["r_liquido"], d["r_benchmark"]
    mk = (1 + r).resample("ME").prod() - 1
    mb = (1 + b).resample("ME").prod() - 1
    return pd.DataFrame({"mês": mk.index.strftime("%Y-%m"), "Kairós": mk.values * PP,
                         "SPY": mb.values * PP, "K > SPY": (mk.values > mb.values)})


def rolling_ir(d, janela=JANELA_ROLLING):
    e = d["r_liquido"] - d["r_benchmark"]
    return e.rolling(janela).apply(lambda x: x.mean() / x.std(ddof=1)) * np.sqrt(PREGOES_POR_ANO)


def rolling_beta(d, janela=JANELA_ROLLING):
    r, b = d["r_liquido"], d["r_benchmark"]
    return r.rolling(janela).cov(b) / b.rolling(janela).var()


def time_under_water(dd):
    """Maior sequência de pregões abaixo do pico anterior."""
    c = m = 0
    for u in (np.asarray(dd) < 0):
        c = c + 1 if u else 0
        m = max(m, c)
    return int(m)


def tabela_drawdowns(r, n=3):
    """Os n maiores drawdowns: início (pico), fundo, fim (recuperação) e profundidade."""
    dd = drawdown(pd.Series(r))
    episodios, inicio = [], None
    for t, v in dd.items():
        if v < 0 and inicio is None:
            inicio = t
        elif v == 0 and inicio is not None:
            trecho = dd.loc[inicio:t]
            episodios.append((inicio, trecho.idxmin(), t, float(trecho.min() * PP), len(trecho)))
            inicio = None
    if inicio is not None:                       # episódio aberto no fim da janela
        trecho = dd.loc[inicio:]
        episodios.append((inicio, trecho.idxmin(), pd.NaT, float(trecho.min() * PP), len(trecho)))
    tab = pd.DataFrame(episodios, columns=["início", "fundo", "recuperação", "profundidade (%)", "pregões"])
    tab = tab.sort_values("profundidade (%)").head(n).reset_index(drop=True)
    for c in ("início", "fundo", "recuperação"):     # datas como texto; episódio aberto declarado
        tab[c] = tab[c].map(lambda t: "em aberto" if pd.isna(t) else t.strftime("%Y-%m-%d"))
    return tab


def bloco_estabilidade(d, ro, rb, mensal):
    r, b = d["r_liquido"], d["r_benchmark"]
    ddk, ddb = drawdown(r), drawdown(b)
    linhas = [
        ("máx. drawdown Kairós (%)", float(ddk.min() * PP), ""),
        ("máx. drawdown SPY (%)", float(ddb.min() * PP), ""),
        ("time under water Kairós (pregões)", time_under_water(ddk), "maior sequência abaixo do pico"),
        ("time under water SPY (pregões)", time_under_water(ddb), ""),
        ("meses K > SPY", f"{int(mensal['K > SPY'].sum())} de {len(mensal)}", ""),
        (f"rolling IR {JANELA_ROLLING}d > 0 (fração)", float((ro.dropna() > 0).mean()), ""),
        (f"rolling IR {JANELA_ROLLING}d mín / máx", f"{ro.min():.2f} / {ro.max():.2f}", ""),
        (f"rolling beta {JANELA_ROLLING}d mín / máx", f"{rb.min():.2f} / {rb.max():.2f}", ""),
    ]
    return pd.DataFrame(linhas, columns=["métrica", "valor", "nota"])


# =============================================================================
# D. Implementação (relido do backtest)
# =============================================================================
def bloco_implementacao(d, dados=DADOS):
    met = pd.read_csv(dados / "backtest_metricas.csv", index_col=0)[CENARIO]
    linhas = [
        ("giro diário médio", float(d["giro"].mean()), "fração do patrimônio"),
        ("giro desfeito em 1–2 pregões", float(met["giro desfeito em 1–2 pregões"]), "backtest_v1"),
        ("custo pago (pp)", float(d["custo"].sum() * PP), "2 bps por lado"),
        ("breakeven (bps por lado)", float(met["custo de breakeven (bps por lado)"]), "backtest_v1"),
        ("Σ|w| média", float(d["alavancagem"].mean()), ""),
        ("views ativas por dia", float(d["n_views"].mean()), ""),
    ]
    return pd.DataFrame(linhas, columns=["métrica", "valor", "nota"])


# =============================================================================
# Figuras (estilo do slide)
# =============================================================================
def _eixo_meses(ax):
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%y"))
    ax.set_axisbelow(True)


def fig_excesso_ic(d, boot):
    """Excesso acumulado K − SPY ao longo do tempo e o IC95 do valor final."""
    r, b = d["r_liquido"], d["r_benchmark"]
    exc = ((1 + r).cumprod() - (1 + b).cumprod()) * PP
    lo, hi = ic(boot.excesso)
    with _estilo_slide():
        fig, ax = plt.subplots(figsize=(7.0, 3.3))
        ax.axhline(0, color=SLIDE["suave"], lw=1.0, ls="--")
        ax.fill_between(exc.index, exc, 0, where=exc >= 0, color=SLIDE["laranja"], alpha=0.18, lw=0)
        ax.fill_between(exc.index, exc, 0, where=exc < 0, color=SLIDE["vermelho"], alpha=0.18, lw=0)
        ax.plot(exc.index, exc, color=SLIDE["laranja"], lw=2.4)
        fim = exc.index[-1] + pd.Timedelta(days=18)
        ax.plot([fim, fim], [lo, hi], color=SLIDE["azul"], lw=3.0, solid_capstyle="round")
        ax.plot([fim], [exc.iloc[-1]], "o", color=SLIDE["laranja"], ms=7, zorder=5)
        ax.annotate(f"{exc.iloc[-1]:+.1f} pp".replace(".", ","), (fim, exc.iloc[-1]),
                    xytext=(8, 0), textcoords="offset points", va="center",
                    color=SLIDE["laranja"], fontsize=13, fontweight="bold")
        for v in (lo, hi):
            ax.annotate(f"{v:+.0f}", (fim, v), xytext=(8, 0), textcoords="offset points",
                        va="center", color=SLIDE["azul"], fontsize=11)
        ax.set_xlim(exc.index[0], fim + pd.Timedelta(days=45))
        _eixo_meses(ax)
        ax.set_ylabel("Kairós − SPY (pp)")
        ax.grid(True, axis="y", lw=0.5, alpha=0.5)
        ax.text(0.01, 0.97, "IC95 bootstrap do valor final", transform=ax.transAxes,
                color=SLIDE["azul"], fontsize=11, va="top")
    return fig


def fig_split(metades, regime):
    """Metades e regime do SPY, lado a lado."""
    with _estilo_slide():
        fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.2, 2.7))
        v = metades["excesso (pp)"].values
        cores = [SLIDE["laranja"] if x >= 0 else SLIDE["vermelho"] for x in v]
        a1.bar(metades.index, v, 0.55, color=cores)
        for i, x in enumerate(v):
            a1.annotate(f"{x:+.1f} pp".replace(".", ","), (i, x), xytext=(0, 5 if x >= 0 else -14),
                        textcoords="offset points", ha="center", fontsize=11, color=SLIDE["texto"])
        a1.set_title("excesso por metade da janela", loc="left")
        v2 = regime["excesso médio (bps)"].values
        cores2 = [SLIDE["laranja"] if x >= 0 else SLIDE["vermelho"] for x in v2]
        a2.bar(regime["regime"], v2, 0.55, color=cores2)
        for i, (x, h) in enumerate(zip(v2, regime["hit do excesso"])):
            a2.annotate(f"{x:+.1f} bps/dia\nhit {h:.0%}".replace(".", ","), (i, x),
                        xytext=(0, 5 if x >= 0 else -26), textcoords="offset points",
                        ha="center", fontsize=10, color=SLIDE["texto"])
        a2.set_title("excesso por dia, pelo regime do SPY", loc="left")
        for a in (a1, a2):
            a.set_axisbelow(True)
            a.axhline(0, color=SLIDE["suave"], lw=0.9)
            a.grid(True, axis="y", lw=0.5, alpha=0.4)
            a.margins(y=0.45)
    return fig


def fig_rolling_ir(ro):
    with _estilo_slide():
        fig, ax = plt.subplots(figsize=(7.0, 2.7))
        ax.axhline(0, color=SLIDE["suave"], lw=1.0, ls="--")
        ax.fill_between(ro.index, ro, 0, where=ro >= 0, color=SLIDE["laranja"], alpha=0.2, lw=0)
        ax.fill_between(ro.index, ro, 0, where=ro < 0, color=SLIDE["vermelho"], alpha=0.2, lw=0)
        ax.plot(ro.index, ro, color=SLIDE["laranja"], lw=1.8)
        _eixo_meses(ax)
        ax.set_ylabel(f"IR em {JANELA_ROLLING} pregões")
        ax.grid(True, axis="y", lw=0.5, alpha=0.5)
    return fig


def fig_mensal(mensal):
    with _estilo_slide():
        fig, ax = plt.subplots(figsize=(7.0, 2.7))
        x = np.arange(len(mensal))
        ax.bar(x - 0.2, mensal["Kairós"], 0.4, color=SLIDE["laranja"], label="Kairós")
        ax.bar(x + 0.2, mensal["SPY"], 0.4, color=SLIDE["cinza"], label="SPY")
        ax.axhline(0, color=SLIDE["suave"], lw=0.9)
        ax.set_axisbelow(True)
        rotulos = [m[5:] + "/" + m[2:4] if i % 2 == 0 else "" for i, m in enumerate(mensal["mês"])]
        ax.set_xticks(x, rotulos, fontsize=10)
        ax.set_ylabel("retorno do mês (%)")
        ax.legend(frameon=False, loc="upper left", ncol=2)
        ax.grid(True, axis="y", lw=0.5, alpha=0.5)
    return fig


def fig_dsr(tab_dsr, momentos, T):
    """PSR/DSR em função do nº de tentativas, para as duas variâncias."""
    sr, g3, g4 = momentos
    Ns = np.unique(np.concatenate([np.arange(1, 10), np.geomspace(10, 400, 30).astype(int)]))
    with _estilo_slide():
        fig, ax = plt.subplots(figsize=(5.2, 2.7))
        for nome, cor in (("V medido nas configurações", SLIDE["laranja"]),
                          ("V de tentativas independentes", SLIDE["azul"])):
            V = (tab_dsr.loc[tab_dsr["variância"] == nome, "σ(SR) anual"].iloc[0]
                 / np.sqrt(PREGOES_POR_ANO)) ** 2
            ax.plot(Ns, [dsr(sr, T, g3, g4, int(N), V) for N in Ns], color=cor, lw=2.0, label=nome)
        for _, linha in tab_dsr.iterrows():
            ax.plot([linha.N], [linha.DSR], "o", ms=5,
                    color=SLIDE["laranja"] if "medido" in linha["variância"] else SLIDE["azul"])
        ax.axhline(NIVEL, color=SLIDE["suave"], lw=0.9, ls="--")
        ax.set_xscale("log")
        ax.set_axisbelow(True)
        ax.set_xlabel("nº de tentativas (N)")
        ax.set_ylabel("DSR")
        ax.set_ylim(0, 1.02)
        ax.legend(frameon=False, loc="lower left", fontsize=9)
        ax.grid(True, lw=0.5, alpha=0.4)
    return fig


# =============================================================================
# Escrita
# =============================================================================
def _md(df, fmt="{:.3f}"):
    df = df.copy()
    for c in df.columns:
        if pd.api.types.is_float_dtype(df[c]):
            df[c] = df[c].map(lambda v: "—" if pd.isna(v) else fmt.format(v))
        elif pd.api.types.is_datetime64_any_dtype(df[c]):
            df[c] = df[c].dt.strftime("%Y-%m-%d")
        elif pd.api.types.is_object_dtype(df[c]):
            df[c] = df[c].map(lambda v: fmt.format(v) if isinstance(v, float) else v)
    linhas = ["| " + " | ".join(map(str, df.columns)) + " |", "|" + "---|" * len(df.columns)]
    linhas += ["| " + " | ".join(map(str, r)) + " |" for r in df.itertuples(index=False)]
    return "\n".join(linhas)


def escrever_md(t, T, caminho=MD):
    inf = t["inferencia"].set_index("métrica")["valor"]
    partes = [
        "# Análise estatística do backtest — o número e a sua incerteza\n",
        f"> Gerado por `scripts/analise_backtest.py` sobre `Uteis/dados/backtest_diario.csv` "
        f"(cenário `{CENARIO}`, {T} pregões) e as grades já gravadas. **Mede; não decide.** "
        f"Escolhas pré-registradas na D33. Bootstrap estacionário (bloco médio {BLOCO}, "
        f"B = {B_BOOT}, semente {SEMENTE}); Newey-West {NW_LAGS} lags; nível {NIVEL:.0%}.\n",
        "## A. Inferência do número-título\n", _md(t["inferencia"]), "",
        f"**Leitura.** O excesso de {float(inf['excesso acumulado (pp)']):+.2f} pp tem IC95 "
        f"{inf['excesso · IC95 bootstrap (pp)']} e P(> 0) = {float(inf['P(excesso > 0)']):.0%}; "
        f"o Sharpe {float(inf['Sharpe Kairós']):.2f} tem IC95 {inf['Sharpe Kairós · IC95 bootstrap']}; "
        f"o alpha tem t = {float(inf['t do alpha (Newey-West)']):.2f} contra a régua de 3 de "
        f"Harvey-Liu. Faltam {float(inf['MinTRL a 95 % (pregões)']) - T:.0f} pregões para o "
        f"track record mínimo a 95 %. **Em {T} pregões o número não separa habilidade de sorte** — "
        "o que sustenta a estratégia é o mecanismo medido fora do resultado (calibração do "
        "Polymarket, β por event-study, Ω julgado pelo erro da probabilidade), não o p-valor.\n",
        "### Deflated Sharpe Ratio — grade de tentativas\n",
        "Nenhuma linha é 'a' correção. `V medido` é a variância dos Sharpe das configurações "
        "gravadas (tetos, γ, bandas) — tentativas correlacionadas, logo V subestima; "
        "`V independente` é o SE² de Lo de uma tentativa de ruído do mesmo comprimento — "
        "cota superior. A verdade está entre as duas.\n", _md(t["dsr"]), "",
        "## B. De onde vem o resultado\n", _md(t["concentracao"]), "",
        "### Tilt por nº de views ativas no dia\n", _md(t["views_dia"], "{:.2f}"), "",
        "## C. Estabilidade\n", "### Metades da janela\n", _md(t["metades"].reset_index(names="metade"), "{:.2f}"), "",
        "### Regime do SPY\n", _md(t["regime"], "{:.2f}"), "",
        "### Drawdown, meses e janelas móveis\n", _md(t["estabilidade"]), "",
        "### Os 3 maiores drawdowns\n", _md(t["drawdowns"], "{:.1f}"), "",
        "### Retornos mensais\n", _md(t["mensal"], "{:.2f}"), "",
        "## D. Implementação\n", _md(t["implementacao"]), "",
        "## Referências\n",
        "Lo (2002) FAJ · Bailey & López de Prado (2012) *Sharpe Ratio Efficient Frontier* · "
        "Bailey & López de Prado (2014) *Deflated Sharpe Ratio*, JPM · Ledoit & Wolf (2008) JEF · "
        "Politis & Romano (1994) JASA · Harvey & Liu (2015) *Backtesting*, JPM · "
        "López de Prado (2018) *Advances in Financial ML*, cap. 14 · Grinold & Kahn (2000). "
        "Detalhe em `Final/analise/Pesquisa_avaliacao_estrategia.md`.",
    ]
    caminho.write_text("\n".join(partes), encoding="utf-8")
    return caminho


def carregar(dados=DADOS):
    d = pd.read_csv(dados / "backtest_diario.csv", parse_dates=["data"])
    d = d[d["cenario"] == CENARIO].set_index("data").sort_index()
    # controle: a cascata do backtest fecha na série que vamos analisar
    assert np.allclose(d["r_liquido"], d["r_mercado"] + d["r_tilt"] - d["custo"] + d["carrego"])
    return d


def main():
    d = carregar()
    boot = bootstrap_estacionario(d["r_liquido"], d["r_benchmark"])
    inferencia, momentos = bloco_inferencia(d, boot)
    ro, rb, mensal = rolling_ir(d), rolling_beta(d), bloco_mensal(d)
    metades, regime = bloco_metades(d), bloco_regime(d)
    t = {
        "inferencia": inferencia, "dsr": bloco_dsr(d, boot, momentos),
        "concentracao": bloco_concentracao(d), "views_dia": bloco_views_dia(d),
        "metades": metades, "regime": regime, "mensal": mensal,
        "estabilidade": bloco_estabilidade(d, ro, rb, mensal),
        "drawdowns": tabela_drawdowns(d["r_liquido"]),
        "implementacao": bloco_implementacao(d),
        "rolling": pd.DataFrame({"ir": ro, "beta": rb}),
        "bootstrap": boot,
    }
    SAIDA.mkdir(parents=True, exist_ok=True)
    for nome, tab in t.items():
        tab.to_csv(SAIDA / f"{nome}.csv", index=nome in ("metades", "rolling"))
    for nome, fig in (("ab_excesso_ic", fig_excesso_ic(d, boot)), ("ab_split", fig_split(metades, regime)),
                      ("ab_rolling_ir", fig_rolling_ir(ro)), ("ab_mensal", fig_mensal(mensal)),
                      ("ab_dsr", fig_dsr(t["dsr"], momentos, len(d)))):
        salvar(fig, GRAFICOS, nome)
    print(escrever_md(t, len(d)).relative_to(RAIZ))
    print(_md(inferencia))


def demo():
    rng = np.random.default_rng(1)
    # PSR de uma série gaussiana longa bate com a normal; N = 1 não deflaciona
    r = rng.normal(0.0005, 0.01, 20000)
    sr, g3, g4 = sharpe(r), float(stats.skew(r)), float(stats.kurtosis(r, fisher=False))
    assert abs(psr(sr, len(r), g3, g4) - stats.norm.cdf(sr * np.sqrt(len(r) - 1))) < 0.01
    assert dsr(sr, len(r), g3, g4, 1, 0.5) == psr(sr, len(r), g3, g4)
    assert dsr(sr, len(r), g3, g4, 100, 1e-4) < psr(sr, len(r), g3, g4)
    # no MinTRL a PSR é exatamente o nível
    T_min = min_trl(sr, g3, g4)
    assert abs(psr(sr, T_min, g3, g4) - NIVEL) < 1e-9
    # E[max SR] cresce com N e com V
    assert sr_esperado_max(10, 1.0) < sr_esperado_max(100, 1.0) < sr_esperado_max(100, 4.0)
    # bootstrap: índices válidos, e a média do Sharpe reamostrado fica perto do amostral
    b = rng.normal(0.0004, 0.01, 300)
    r2 = 0.9 * b + rng.normal(0.0002, 0.004, 300)
    ix = indices_estacionarios(300, np.random.default_rng(0))
    assert len(ix) == 300 and ix.min() >= 0 and ix.max() < 300
    bt = bootstrap_estacionario(r2, b, B=300)
    assert abs(bt.sr_k.mean() - anual(sharpe(r2))) < 0.5 and set(bt.columns) == {"sr_k", "sr_b", "d_sr", "excesso", "ir"}
    # Newey-West recupera o beta de uma regressão sem ruído
    X = np.column_stack([np.ones(300), b])
    beta_hat, V = newey_west(X, 0.001 + 0.9 * b)
    assert np.allclose(beta_hat, [0.001, 0.9]) and V.shape == (2, 2)
    # HHI: uniforme = 0, concentrado = 1; TuW de série só de alta = 0
    assert abs(hhi(np.ones(10))) < 1e-12 and abs(hhi(np.array([0, 0, 5.0])) - 1) < 1e-12
    assert time_under_water(drawdown(pd.Series(np.full(50, 0.001)))) == 0
    sobe_desce = pd.Series([0.01, -0.02, 0.0, 0.03], index=pd.date_range("2025-01-01", periods=4))
    assert time_under_water(drawdown(sobe_desce)) == 2
    tab = tabela_drawdowns(sobe_desce)
    assert len(tab) == 1 and abs(tab.loc[0, "profundidade (%)"] + 2.0) < 1e-9
    print("demo ok")


if __name__ == "__main__":
    if "--demo" in sys.argv:
        demo()
    else:
        main()
