"""Estudo estatístico do Polymarket como fonte de sinal (final). Felipe.

Três perguntas, uma amostra, um script. **Mede; não decide** — nada aqui muda
parâmetro da estratégia, `src/` ou o backtest (CLAUDE.md §6).

  Q1  o preço é uma probabilidade CALIBRADA, e como a acurácia evolui com o
      horizonte até a resolução? (Brier, BSS, Murphy, curva de calibração,
      favorito-azarão, RPS, overround, volume)
  Q2  ele ACRESCENTA informação ao mercado tradicional? (FOMC: E_poly × proxy
      do futuro de FF `DTB3 − DFF`, D12 — MAE, acerto modal, Diebold-Mariano,
      encompassing, lead-lag)
  Q3  é APLICÁVEL à carteira? (event-study do dia do anúncio nos 9 ETFs com
      surpresa-poly × surpresa-FF × Kuttner; martingale do próprio preço)

AMOSTRA — só o dado congelado em `data/`, sem pedido novo:
  - FOMC: `polymarket_fed_reunioes.parquet` (18 reuniões, 76 buckets);
    resolução lida no `DFF` (`decisoes_realizadas_fomc`), NÃO no preço terminal
    — MEDIDO: a série de todo evento termina no slot das 12:00 UTC do dia do
    anúncio, antes das 14:00 ET, então o último preço ainda é expectativa.
  - CPI m/m: `raw/clob_exploracao/CPI_*.json`; resolução = MoM do `CPIAUCSL`
    arredondado na casa que o BLS publica (`gate_pead.mom_realizado`). Mesmo
    achado: a série termina às 12:00 UTC do release (08:30 ET = 12:30 UTC).
  - Payrolls: os arquivos do G9 vêm SEM o slug do balde e o `PAYEMS`/`UNRATE`
    não estão no repo → sem y. Entram só no que não precisa de resolução
    (overround e martingale), declarado.

UNIDADE DE OBSERVAÇÃO: (mercado, h), com p_h = slot pré-abertura (12:00 UTC,
regra do `poly_loader`) do dia `resolução − h`, h na grade `HORIZONTES`.
Buckets da mesma PMF são dependentes → cluster = evento em todo IC (bootstrap
por evento) e em todo erro-padrão (cluster-robusto).

Escolhas pré-registradas no plano da sessão 46 (2026-09-17): grade de h, bins
(10 pooled / 5 por família), baseline do BSS = uniforme sobre os buckets vivos,
γ só medido, VR(2)/VR(5), DM e Newey-West em numpy (statsmodels não instalado).

Uso:
    python scripts/estudo_polymarket.py            # mede, grava CSV, figuras e MD
    python scripts/estudo_polymarket.py --demo     # auto-teste sintético
"""

import argparse
import sys
import warnings
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
from scipy import stats

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "scripts"))

from backtest_v1 import decisoes_realizadas_fomc, PONTOS_PERCENTUAIS  # noqa: E402
from gate_pead import mom_realizado                                   # noqa: E402
from graficos_p4 import PALETAS, aplicar_estilo, salvar               # noqa: E402
from market_loader import load_etf_prices, load_fred                  # noqa: E402
from poly_loader import (bucket_value, daily_preopen, load_cpi_releases,  # noqa: E402
                         load_fomc_pmf, load_pmf)
from poly_preprocessing import (bucket_values_with_open, carry_missing,  # noqa: E402
                                favorite_longshot, pmf_mean)
from premio_condicional import PAYROLL_FAMILIAS, PREFIXO_PAYROLL, prefixos_cpi  # noqa: E402
from taticas_common import close_to_close_returns                     # noqa: E402

# --- escolhas pré-registradas (plano da sessão 46) ---------------------------
HORIZONTES = (0, 1, 2, 3, 5, 10, 15, 20, 30, 45, 60)   # dias corridos antes da resolução
HORIZONTES_HEROI = (0, 20)                              # o que a estratégia lê · "1 mês" do Dune
BINS_POOLED, BINS_FAMILIA = 10, 5
B_BOOT, SEMENTE = 2000, 20260917
GAMMAS = np.round(np.arange(0.8, 1.51, 0.05), 2)
VR_Q = (2, 5)
NW_LAGS = 5
DIAS_LEADLAG = 60
# Leitura degenerada: linha em que os buckets já morreram (Σp ≈ 0, medido no
# CPI de mar/2026). Não é threshold de estratégia — é filtro de dado inválido,
# e o nº de linhas excluídas sai na tabela de cobertura.
SOMA_MINIMA = 0.5
# Preço "interior": fora da região de 1–2 ticks onde o bucket morto oscila.
# Coluna de robustez do martingale, não a medida principal.
INTERIOR = (0.02, 0.98)
# Referências externas (linhas de comparação na figura 2; não são medidas aqui)
REFERENCIAS = {"Kalshi 2026 · 3 meses": 0.087, "Kalshi 2026 · 1 h": 0.045,
               "Dune/McCullough · 12 h": 0.058}

DADOS = RAIZ / "Uteis" / "dados" / "estudo"
GRAFICOS = RAIZ / "Uteis" / "graficos"
METRICAS = RAIZ / "Uteis" / "analises" / "Metricas_estudo.md"


# =============================================================================
# 1. Amostra
# =============================================================================

def vencedor(valores, abertos, realizado):
    """Vetor 0/1 do bucket que resolve Yes numa grade ordenada com pontas abertas."""
    valores = np.asarray(valores, dtype=float)
    y = np.isclose(valores, realizado)
    if abertos[0] and realizado < valores[0]:
        y[0] = True
    if abertos[-1] and realizado > valores[-1]:
        y[-1] = True
    if y.sum() != 1:
        raise ValueError(f"realizado {realizado} não cai em exatamente um bucket de {valores}")
    return y.astype(float)


def leitura(diaria, data):
    """Linha da PMF na data ou None (sem slot, bucket sem leitura, ou degenerada)."""
    if data not in diaria.index:
        return None
    linha = diaria.loc[data].to_numpy(dtype=float)
    if not np.isfinite(linha).all() or linha.sum() < SOMA_MINIMA:
        return None
    return linha


def _linhas(familia, evento, colunas, valores, y, diaria, volume=None):
    """Expande um evento na grade de h em linhas longas (uma por bucket)."""
    linhas, faltas = [], {}
    for h in HORIZONTES:
        data = evento - pd.Timedelta(days=h)
        p = leitura(diaria, data)
        if p is None:
            faltas[h] = "sem slot" if data not in diaria.index else "degenerada"
            continue
        for k, col in enumerate(colunas):
            linhas.append({"familia": familia, "evento": evento, "mercado": col,
                           "bucket": k, "K": len(colunas), "h": h, "p": p[k],
                           "y": y[k], "valor": valores[k],
                           "volume": np.nan if volume is None else volume.get(col, np.nan)})
    return linhas, faltas


def amostra_fomc(raiz=RAIZ):
    """Observações (mercado, h) das reuniões do FOMC + E_poly diário por reunião."""
    fomc = pd.DatetimeIndex(sorted(pd.to_datetime(
        pd.read_csv(raiz / "data/raw/fomc_dates.csv")["date"])))
    dff = load_fred(raiz / "data/raw/fred_DFF.csv")
    realizado = decisoes_realizadas_fomc(dff, fomc)
    bruto = pd.read_parquet(raiz / "data/polymarket_fed_reunioes.parquet")
    volume = bruto.groupby("mercado")["volume"].first().to_dict()

    linhas, faltas, diarias = [], {}, {}
    for probs, valores, abertos, fim in load_fomc_pmf(raiz / "data/polymarket_fed_reunioes.parquet").values():
        # o parquet pode seguir 1–2 dias além da reunião (out/2025); a data do
        # evento é a do calendário oficial, nunca o fim da série
        cal = fomc[(fomc <= fim) & (fomc >= fim - pd.Timedelta(days=5))]
        if not len(cal) or cal[-1] not in realizado.index:
            continue
        reuniao = cal[-1]
        r = round(float(realizado[reuniao]) / 25.0) * 25.0
        y = vencedor(valores, abertos, r)
        pontas = tuple(n for n, a in (("lower", abertos[0]), ("upper", abertos[-1])) if a)
        valores_open = bucket_values_with_open(valores, open_ends=pontas)
        diaria = daily_preopen(carry_missing(probs)).dropna(how="all")
        novas, falta = _linhas("FOMC", reuniao, list(probs.columns), valores_open, y,
                               diaria, volume)
        linhas += novas
        faltas[reuniao] = falta
        diarias[reuniao] = (diaria, valores_open, r, y)
    return pd.DataFrame(linhas), faltas, diarias


def amostra_cpi(raiz=RAIZ):
    """Observações (mercado, h) dos mercados mensais de CPI com MoM publicado."""
    diretorio = raiz / "data/raw/clob_exploracao"
    releases = load_cpi_releases(raiz / "data/raw/cpi_release_dates.csv")
    mom = mom_realizado(load_fred(raiz / "data/raw/fred_CPIAUCSL.csv"))
    mes_por_release = {pd.Timestamp(l["release_date"]): pd.to_datetime(l["mes_referencia"], format="%B %Y")
                       for _, l in releases.iterrows()}
    linhas, faltas, diarias = [], {}, {}
    for release, prefixo in prefixos_cpi(releases, diretorio).items():
        mes = mes_por_release[release]
        if mes not in mom.index:
            continue  # MoM ainda não publicado (ou nunca: out/nov 2025)
        cru = load_pmf(diretorio, prefixo)
        valores = np.array([bucket_value(c) for c in cru.columns], dtype=float)
        # pontas do CPI são abertas pelas regras do mercado ("0,1 % ou menos")
        y = vencedor(valores, (True, True), float(mom[mes]))
        diaria = daily_preopen(carry_missing(cru)).dropna(how="all")
        novas, falta = _linhas("CPI", release, list(cru.columns),
                               bucket_values_with_open(valores), y, diaria)
        linhas += novas
        faltas[release] = falta
        diarias[release] = (diaria, bucket_values_with_open(valores), float(mom[mes]))
    return pd.DataFrame(linhas), faltas, diarias


def pmfs_payrolls(raiz=RAIZ):
    """{mercado: PMF crua (slots × buckets)} dos payrolls dos EUA — SEM y."""
    diretorio = raiz / "data/raw/clob_exploracao"
    saida, vistos = {}, set()
    for arquivo in sorted(diretorio.glob(f"{PREFIXO_PAYROLL}*.json")):
        mercado = arquivo.stem[len(PREFIXO_PAYROLL):].rsplit("_", 1)[0]
        if mercado in vistos or not any(p.match(mercado) for _, p in PAYROLL_FAMILIAS):
            continue
        vistos.add(mercado)
        saida[mercado] = load_pmf(diretorio, f"{PREFIXO_PAYROLL}{mercado}_", ordenar=False)
    return saida


def cobertura(obs, faltas):
    """Eventos com leitura por h e família, e por que os outros faltam."""
    linhas = []
    for familia, f in faltas.items():
        for h in HORIZONTES:
            com = obs[(obs.familia == familia) & (obs.h == h)].evento.nunique()
            motivos = [v[h] for v in f.values() if h in v]
            linhas.append({"familia": familia, "h": h, "eventos_com_leitura": com,
                           "sem_slot": motivos.count("sem slot"),
                           "degenerada": motivos.count("degenerada")})
    return pd.DataFrame(linhas)


# =============================================================================
# 2. Estatística — funções puras
# =============================================================================

def brier(p, y):
    return float(np.mean((np.asarray(p) - np.asarray(y)) ** 2))


def logloss(p, y, eps=1e-6):
    p = np.clip(np.asarray(p, dtype=float), eps, 1 - eps)
    y = np.asarray(y, dtype=float)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def brier_uniforme(K, y):
    """Brier do 'sem informação': 1/K em cada bucket vivo (baseline do BSS)."""
    return float(np.mean((1.0 / np.asarray(K, dtype=float) - np.asarray(y)) ** 2))


def bins_de(p, bins):
    return np.minimum((np.asarray(p) * bins).astype(int), bins - 1)


def murphy(p, y, bins):
    """(confiabilidade, resolução, incerteza) — Murphy (1973); soma = Brier."""
    p, y = np.asarray(p, dtype=float), np.asarray(y, dtype=float)
    idx = bins_de(p, bins)
    ybar, n = y.mean(), len(y)
    conf = res = 0.0
    for k in np.unique(idx):
        m = idx == k
        conf += m.sum() * (p[m].mean() - y[m].mean()) ** 2
        res += m.sum() * (y[m].mean() - ybar) ** 2
    return conf / n, res / n, ybar * (1 - ybar)


def curva(p, y, bins):
    """Por bin: preço médio, frequência observada, n."""
    p, y = np.asarray(p, dtype=float), np.asarray(y, dtype=float)
    idx = bins_de(p, bins)
    linhas = []
    for k in range(bins):
        m = idx == k
        linhas.append({"bin": k, "p_medio": p[m].mean() if m.any() else np.nan,
                       "freq": y[m].mean() if m.any() else np.nan, "n": int(m.sum())})
    return pd.DataFrame(linhas)


def bootstrap_por_cluster(cluster, estat, B=B_BOOT, semente=SEMENTE):
    """IC 95 % percentílico reamostrando CLUSTERS (eventos) com reposição.

    `estat(idx)` recebe os índices posicionais da reamostra e devolve escalar
    ou vetor. Devolve (p2.5, p97.5) na mesma forma.
    """
    cluster = np.asarray(cluster)
    grupos = {g: np.flatnonzero(cluster == g) for g in np.unique(cluster)}
    chaves = list(grupos)
    rng = np.random.default_rng(semente)
    amostras = []
    for _ in range(B):
        sorteio = rng.choice(len(chaves), size=len(chaves), replace=True)
        idx = np.concatenate([grupos[chaves[s]] for s in sorteio])
        amostras.append(estat(idx))
    amostras = np.asarray(amostras, dtype=float)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)   # bin vazio em toda reamostra
        return np.nanpercentile(amostras, 2.5, axis=0), np.nanpercentile(amostras, 97.5, axis=0)


def ols_cluster(X, y, cluster):
    """OLS com covariância cluster-robusta (Liang-Zeger). Devolve (β, V)."""
    X, y = np.asarray(X, dtype=float), np.asarray(y, dtype=float)
    XtX_inv = np.linalg.inv(X.T @ X)
    beta = XtX_inv @ X.T @ y
    e = y - X @ beta
    meio = np.zeros((X.shape[1], X.shape[1]))
    for g in np.unique(cluster):
        m = np.asarray(cluster) == g
        s = X[m].T @ e[m]
        meio += np.outer(s, s)
    return beta, XtX_inv @ meio @ XtX_inv


def regressao_calibracao(p, y, cluster):
    """y = a + b·p com EP por evento; Wald de (a, b) = (0, 1)."""
    X = np.column_stack([np.ones(len(p)), p])
    beta, V = ols_cluster(X, y, cluster)
    dif = beta - np.array([0.0, 1.0])
    wald = float(dif @ np.linalg.inv(V) @ dif)
    return {"a": beta[0], "b": beta[1], "se_a": np.sqrt(V[0, 0]), "se_b": np.sqrt(V[1, 1]),
            "wald": wald, "p_wald": float(stats.chi2.sf(wald, 2))}


def gamma_otimo(p, y, gammas=GAMMAS):
    """γ da correção favorito-azarão que minimiza o Brier (só medido; D9 fixa 1,0)."""
    curva_gamma = {g: brier(favorite_longshot(np.asarray(p), g), y) for g in gammas}
    return min(curva_gamma, key=curva_gamma.get), curva_gamma


def rps(pmf, y):
    """Ranked probability score normalizado por (K − 1) — 0 = massa no bucket certo."""
    pmf = np.asarray(pmf, dtype=float)
    F = np.cumsum(pmf / pmf.sum())
    O = np.cumsum(np.asarray(y, dtype=float))
    return float(np.sum((F - O) ** 2) / (len(pmf) - 1))


def newey_west(X, y, lags=NW_LAGS):
    """OLS com covariância HAC de Newey-West (janela de Bartlett). (β, V)."""
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


def diebold_mariano(erro_a, erro_b):
    """DM sobre |erro| com correção de Harvey-Leybourne-Newbold (1 passo à frente).

    Negativo = A tem perda menor. p bicaudal da t(n−1).
    """
    d = np.abs(np.asarray(erro_a, dtype=float)) - np.abs(np.asarray(erro_b, dtype=float))
    n = len(d)
    if n < 3 or d.std(ddof=1) == 0:
        return np.nan, np.nan
    dm = d.mean() / np.sqrt(d.var(ddof=1) / n) * np.sqrt((n - 1) / n)
    return float(dm), float(2 * stats.t.sf(abs(dm), n - 1))


def acf_pooled(deltas, lag):
    """Autocorrelação pooled de uma lista de séries de Δp (média ≈ 0 por construção)."""
    num = sum(float(np.sum(d[lag:] * d[:-lag])) for d in deltas if len(d) > lag)
    den = sum(float(np.sum(d * d)) for d in deltas)
    return num / den if den > 0 else np.nan


def variance_ratio(deltas, q):
    """VR(q) de Lo-MacKinlay, pooled: var(soma de q Δ) / (q · var(Δ)). 1 = martingale."""
    um = np.concatenate([d for d in deltas])
    qs = np.concatenate([np.convolve(d, np.ones(q), "valid") for d in deltas if len(d) >= q])
    return float(qs.var() / (q * um.var())) if um.var() > 0 and len(qs) else np.nan


# =============================================================================
# 3. Q1 — calibração e acurácia por horizonte
# =============================================================================

def q1(obs):
    saida = {}
    # Brier / log-loss / BSS por família e h
    linhas = []
    for (familia, h), g in list(obs.groupby(["familia", "h"])) + \
            [(("pooled", h), g) for h, g in obs.groupby("h")]:
        bs = brier(g.p, g.y)
        base = brier_uniforme(g.K, g.y)
        lo, hi = bootstrap_por_cluster(g.evento.to_numpy(),
                                       lambda i, g=g: brier(g.p.to_numpy()[i], g.y.to_numpy()[i]))
        linhas.append({"familia": familia, "h": h, "n": len(g), "eventos": g.evento.nunique(),
                       "brier": bs, "brier_lo": lo, "brier_hi": hi, "logloss": logloss(g.p, g.y),
                       "brier_uniforme": base, "bss": 1 - bs / base})
    saida["brier_horizonte"] = pd.DataFrame(linhas)

    # Murphy + regressão de calibração + γ: pooled (todos os h) e nos h-herói
    linhas, curvas = [], []
    recortes = [("pooled", obs)] + [(f"h={h}", obs[obs.h == h]) for h in HORIZONTES_HEROI] + \
               [(f, obs[obs.familia == f]) for f in obs.familia.unique()]
    for rotulo, g in recortes:
        bins = BINS_POOLED if rotulo == "pooled" else BINS_FAMILIA   # h fixo tem ~150 obs
        conf, res, inc = murphy(g.p, g.y, bins)
        reg = regressao_calibracao(g.p.to_numpy(), g.y.to_numpy(), g.evento.to_numpy())
        gamma, _ = gamma_otimo(g.p.to_numpy(), g.y.to_numpy())
        linhas.append({"recorte": rotulo, "n": len(g), "bins": bins, "brier": brier(g.p, g.y),
                       "confiabilidade": conf, "resolucao": res, "incerteza": inc,
                       "gamma_otimo": gamma, **reg})
        c = curva(g.p, g.y, bins)
        lo, hi = bootstrap_por_cluster(
            g.evento.to_numpy(),
            lambda i, g=g, bins=bins: curva(g.p.to_numpy()[i], g.y.to_numpy()[i], bins).freq.to_numpy())
        c["freq_lo"], c["freq_hi"], c["recorte"] = lo, hi, rotulo
        curvas.append(c)
    saida["murphy"] = pd.DataFrame(linhas)
    saida["calibracao_bins"] = pd.concat(curvas, ignore_index=True)

    # favorito-azarão nos extremos
    ext = []
    for rotulo, m in (("p < 0,10", obs.p < 0.10), ("p > 0,90", obs.p > 0.90)):
        g = obs[m]
        ext.append({"faixa": rotulo, "n": len(g), "p_medio": g.p.mean(), "freq": g.y.mean()})
    saida["extremos"] = pd.DataFrame(ext)

    # RPS por (evento, h) contra uniforme e persistência (bucket do evento anterior)
    linhas = []
    for familia, gf in obs.groupby("familia"):
        eventos = sorted(gf.evento.unique())
        realizado = {e: gf[(gf.evento == e) & (gf.y == 1)].valor.iloc[0] for e in eventos}
        for i, e in enumerate(eventos):
            for h, g in gf[gf.evento == e].groupby("h"):
                g = g.sort_values("bucket")
                y = g.y.to_numpy()
                linha = {"familia": familia, "evento": e, "h": h,
                         "rps_poly": rps(g.p.to_numpy(), y),
                         "rps_uniforme": rps(np.ones(len(y)), y)}
                if i > 0:
                    # persistência: massa no bucket mais próximo do realizado anterior
                    k = int(np.argmin(np.abs(g.valor.to_numpy() - realizado[eventos[i - 1]])))
                    linha["rps_persistencia"] = rps(np.eye(len(y))[k], y)
                linhas.append(linha)
    saida["rps"] = pd.DataFrame(linhas)

    # overround Σp por (evento, h)
    soma = obs.groupby(["familia", "evento", "h"]).p.sum().rename("soma_p").reset_index()
    saida["overround"] = soma.groupby(["familia", "h"]).soma_p.agg(
        ["mean", "std", "min", "max", "count"]).reset_index()

    # Brier por tercil de volume (FOMC — único com volume por mercado)
    f = obs[(obs.familia == "FOMC") & obs.volume.notna()].copy()
    if len(f):
        f["tercil"] = pd.qcut(f.volume.rank(method="first"), 3, labels=["baixo", "médio", "alto"])
        saida["volume"] = pd.DataFrame([
            {"tercil": tercil, "n": len(g), "mercados": g.mercado.nunique(),
             "volume_mediano": g.volume.median(), "brier": brier(g.p, g.y),
             "brier_h0": brier(g[g.h == 0].p, g[g.h == 0].y)}
            for tercil, g in f.groupby("tercil", observed=True)])
    return saida


# =============================================================================
# 4. Q2 — FOMC: Polymarket × proxy do futuro de FF
# =============================================================================

def e_poly_diario(diarias):
    """{evento: Series diária de E_poly (bps)} a partir das PMFs pré-abertura."""
    saida = {}
    for evento, (diaria, valores, *_) in diarias.items():
        serie = {}
        for data, linha in diaria.iterrows():
            p = linha.to_numpy(dtype=float)
            if np.isfinite(p).all() and p.sum() >= SOMA_MINIMA:
                serie[data] = pmf_mean(p, valores)
        saida[evento] = pd.Series(serie, dtype=float).sort_index()
    return saida


def ultimo_antes(serie, data):
    """Última leitura estritamente anterior a `data` (informação pré-abertura)."""
    antes = serie[serie.index < data]
    return float(antes.iloc[-1]) if len(antes) else np.nan


def q2(diarias_fomc, raiz=RAIZ):
    dtb3 = load_fred(raiz / "data/raw/fred_DTB3.csv")
    dff = load_fred(raiz / "data/raw/fred_DFF.csv")
    e_ff = ((dtb3 - dff) * PONTOS_PERCENTUAIS).dropna()
    e_poly = e_poly_diario(diarias_fomc)

    # --- previsões por h ---
    linhas = []
    for evento, (diaria, valores, realizado, y) in diarias_fomc.items():
        for h in HORIZONTES:
            data = evento - pd.Timedelta(days=h)
            p = leitura(diaria, data)
            if p is None:
                continue
            # o H.15 do dia sai depois do fechamento: às 08:00 ET de `data` o
            # último DTB3 conhecido é o da véspera — mesma regra do backtest
            ff = ultimo_antes(e_ff, data)
            linhas.append({"evento": evento, "h": h, "realizado": realizado,
                           "e_poly": pmf_mean(p, valores),
                           # acerto modal pelo BUCKET vencedor: o rótulo nominal da
                           # ponta aberta (−50+) resolve, não o −62,5 da D1.2
                           "modal_poly": float(y[int(np.argmax(p))]),
                           "e_ff": ff, "modal_ff": float(round(ff / 25.0) * 25.0 == realizado)})
    prev = pd.DataFrame(linhas).dropna().sort_values(["h", "evento"])
    prev["erro_poly"] = prev.realizado - prev.e_poly
    prev["erro_ff"] = prev.realizado - prev.e_ff
    # O proxy tem viés de nível (horizonte de ~3 meses contra uma reunião). A
    # estratégia o corrige com a média EXPANSIVA dos erros passados (D12a); a
    # mesma correção entra aqui, só com reuniões anteriores — sem lookahead.
    prev["e_ff_dm"] = prev.e_ff + prev.groupby("h").erro_ff.transform(
        lambda e: e.shift(1).expanding().mean())
    prev["erro_ff_dm"] = prev.realizado - prev.e_ff_dm
    prev["modal_ff_dm"] = (np.round(prev.e_ff_dm / 25.0) * 25.0 == prev.realizado).astype(float)

    resumo = []
    for h, g in prev.groupby("h"):
        dm, p_dm = diebold_mariano(g.erro_poly, g.erro_ff)
        g_dm = g.dropna(subset=["erro_ff_dm"])
        dm2, p_dm2 = diebold_mariano(g_dm.erro_poly, g_dm.erro_ff_dm)
        resumo.append({"h": h, "n": len(g),
                       "mae_poly": g.erro_poly.abs().mean(), "mae_ff": g.erro_ff.abs().mean(),
                       "mae_ff_dm": g_dm.erro_ff_dm.abs().mean(),
                       "rmse_poly": np.sqrt((g.erro_poly ** 2).mean()),
                       "rmse_ff": np.sqrt((g.erro_ff ** 2).mean()),
                       "vies_poly": g.erro_poly.mean(), "vies_ff": g.erro_ff.mean(),
                       "acerto_modal_poly": g.modal_poly.mean(),
                       "acerto_modal_ff": g.modal_ff.mean(),
                       "acerto_modal_ff_dm": g_dm.modal_ff_dm.mean(),
                       "dm": dm, "p_dm": p_dm, "dm_vs_ff_dm": dm2, "p_dm_vs_ff_dm": p_dm2})
    resumo = pd.DataFrame(resumo)

    # --- encompassing (Fair-Shiller) nos h-herói ---
    enc = []
    for h in HORIZONTES_HEROI:
        g = prev[prev.h == h]
        X = np.column_stack([np.ones(len(g)), g.e_poly, g.e_ff])
        beta, V = newey_west(X, g.realizado.to_numpy(), lags=0)
        se = np.sqrt(np.diag(V)) * np.sqrt(len(g) / (len(g) - 3))   # HC1
        enc.append({"h": h, "n": len(g), "b_poly": beta[1], "t_poly": beta[1] / se[1],
                    "b_ff": beta[2], "t_ff": beta[2] / se[2]})
    enc = pd.DataFrame(enc)

    # --- lead-lag em dias úteis: Δpoly_t (pré-abertura) × Δff_t (fechamento) ---
    pares = []
    for evento, serie in e_poly.items():
        janela = e_ff[(e_ff.index >= evento - pd.Timedelta(days=DIAS_LEADLAG)) & (e_ff.index < evento)]
        poly = serie.reindex(janela.index)
        df = pd.DataFrame({"d_poly": poly.diff(), "d_ff": janela.diff()}).dropna()
        df["evento"] = evento
        pares.append(df)
    pares = pd.concat(pares)

    ccf = []
    for k in range(-3, 4):
        xs, ys = [], []
        for _, g in pares.groupby("evento"):
            a, b = g.d_poly.to_numpy(), g.d_ff.to_numpy()
            if k >= 0:
                xs.append(a[:len(a) - k] if k else a); ys.append(b[k:])
            else:
                xs.append(a[-k:]); ys.append(b[:len(b) + k])
        x, y = np.concatenate(xs), np.concatenate(ys)
        ccf.append({"lag_k": k, "corr": float(np.corrcoef(x, y)[0, 1]), "n": len(x),
                    "leitura": "corr(Δpoly_t, Δff_{t+k})"})
    ccf = pd.DataFrame(ccf)

    def granger(alvo, outro, n_lag=2):
        blocos = []
        for _, g in pares.groupby("evento"):
            d = pd.DataFrame({"y": g[alvo]})
            for L in range(1, n_lag + 1):
                d[f"{alvo}_l{L}"] = g[alvo].shift(L)
            d[f"{outro}_l0"] = g[outro]
            for L in range(1, n_lag + 1):
                d[f"{outro}_l{L}"] = g[outro].shift(L)
            blocos.append(d.dropna())
        d = pd.concat(blocos)
        X = np.column_stack([np.ones(len(d)), d.drop(columns="y")])
        beta, V = newey_west(X, d.y.to_numpy())
        se = np.sqrt(np.diag(V))
        nomes = ["const"] + list(d.drop(columns="y").columns)
        return pd.DataFrame({"alvo": alvo, "regressor": nomes, "coef": beta, "t_nw": beta / se, "n": len(d)})

    # (A) Δff_t ← Δpoly_t, Δpoly_{t−1}: o poly da manhã já contém o que o FF
    #     imprime no fechamento? (B) Δpoly_t ← Δff_{t−1}: o FF de ontem move o
    #     poly de hoje? A contemporânea em (B) é lookahead (fechamento > manhã)
    #     e por isso o regressor `d_ff_l0` de (B) deve ser lido como controle.
    leadlag = pd.concat([granger("d_ff", "d_poly"), granger("d_poly", "d_ff")], ignore_index=True)
    return {"fomc_vs_ff": resumo, "fomc_previsoes": prev, "encompassing": enc,
            "leadlag_ccf": ccf, "leadlag_granger": leadlag}


# =============================================================================
# 5. Q3 — aplicabilidade
# =============================================================================

def event_study(retornos, surpresas):
    """R², β e t de r_i(D) = α + β·s por ativo, para cada medida de surpresa."""
    linhas = []
    for nome, s in surpresas.items():
        comum = retornos.index.intersection(s.dropna().index)
        r, x = retornos.loc[comum], s.loc[comum].to_numpy(dtype=float)
        if len(comum) < 4 or np.ptp(x) == 0:
            continue
        X = np.column_stack([np.ones(len(x)), x])
        for ativo in r.columns:
            y = r[ativo].to_numpy(dtype=float)
            beta, *_ = np.linalg.lstsq(X, y, rcond=None)
            e = y - X @ beta
            r2 = 1 - e.var() / y.var()
            se = np.sqrt(np.linalg.inv(X.T @ X)[1, 1] * (e ** 2).sum() / (len(y) - 2))
            linhas.append({"surpresa": nome, "ativo": ativo, "n": len(y),
                           "beta": beta[1], "t": beta[1] / se, "r2": r2})
    return pd.DataFrame(linhas)


def q3(diarias_fomc, diarias_cpi, previsoes_fomc, pmfs_pay, raiz=RAIZ):
    retornos = close_to_close_returns(load_etf_prices(raiz / "data/etf_prices_daily.parquet"))
    dtb3 = load_fred(raiz / "data/raw/fred_DTB3.csv")

    # --- event-study FOMC: três medidas de surpresa no dia do anúncio ---
    h0 = previsoes_fomc[previsoes_fomc.h == 0].set_index("evento")
    s_poly = (h0.realizado - h0.e_poly)
    s_ff = (h0.realizado - h0.e_ff)
    s_kuttner = (dtb3.diff() * PONTOS_PERCENTUAIS).reindex(h0.index)
    s_ff_dm = h0.erro_ff_dm
    es_fomc = event_study(retornos, {"poly": s_poly, "ff": s_ff, "ff_dm": s_ff_dm,
                                     "kuttner_dDTB3": s_kuttner})
    es_fomc["familia"] = "FOMC"

    # --- event-study CPI: surpresa-poly × naive (mês anterior) ---
    linhas = {}
    eventos = sorted(diarias_cpi)
    for i, release in enumerate(eventos):
        diaria, valores, realizado = diarias_cpi[release]
        p = leitura(diaria, release)
        if p is None:
            continue
        anterior = diarias_cpi[eventos[i - 1]][2] if i else np.nan
        linhas[release] = {"poly": realizado - pmf_mean(p, valores),   # p.p. dos dois lados
                           "naive_mes_anterior": realizado - anterior}
    cpi = pd.DataFrame.from_dict(linhas, orient="index")
    es_cpi = event_study(retornos, {c: cpi[c] for c in cpi.columns})
    es_cpi["familia"] = "CPI"

    # --- martingale do preço cru (slots de 12 h), por família ---
    series = {"FOMC": [], "CPI": [], "Payrolls": []}
    for familia, diarias in (("FOMC", diarias_fomc), ("CPI", diarias_cpi)):
        for evento, (diaria, *_) in diarias.items():
            for col in diaria.columns:
                series[familia].append((evento, diaria[col].dropna().to_numpy()))
    for mercado, pmf in pmfs_pay.items():
        for col in pmf.columns:
            series["Payrolls"].append((mercado, pmf[col].dropna().to_numpy()))

    linhas = []
    for familia, lista in series.items():
        for rotulo, filtro in (("todos", None), ("interior", INTERIOR)):
            deltas, clusters = [], []
            for evento, s in lista:
                d = np.diff(s)
                if filtro is not None:
                    ok = (s[1:] > filtro[0]) & (s[1:] < filtro[1]) & (s[:-1] > filtro[0]) & (s[:-1] < filtro[1])
                    d = d[ok]
                if len(d) > max(VR_Q):
                    deltas.append(d); clusters.append(evento)
            if not deltas:
                continue
            est = {"acf1": lambda i: acf_pooled([deltas[j] for j in i], 1),
                   "acf2": lambda i: acf_pooled([deltas[j] for j in i], 2),
                   **{f"vr{q}": (lambda i, q=q: variance_ratio([deltas[j] for j in i], q)) for q in VR_Q}}
            linha = {"familia": familia, "filtro": rotulo, "series": len(deltas),
                     "n_deltas": int(sum(len(d) for d in deltas))}
            for nome, fn in est.items():
                linha[nome] = fn(np.arange(len(deltas)))
                lo, hi = bootstrap_por_cluster(np.asarray(clusters), fn, B=500)
                linha[f"{nome}_lo"], linha[f"{nome}_hi"] = lo, hi
            linhas.append(linha)
    return {"event_study": pd.concat([es_fomc, es_cpi], ignore_index=True),
            "martingale": pd.DataFrame(linhas)}


# =============================================================================
# 6. Figuras
# =============================================================================

def fig_calibracao(bins, p):
    fig, ax = plt.subplots(figsize=(4.6, 4.0))
    ax.plot([0, 1], [0, 1], color=p["suave"], lw=1, ls="--", zorder=1, label="calibração perfeita")
    estilo = {"pooled": (p["kairos"], "todos os horizontes (10 bins)"),
              "h=0": (p["apoio"], "véspera, h = 0 (5 bins)")}
    for recorte, (cor, rotulo) in estilo.items():
        c = bins[bins.recorte == recorte].dropna(subset=["p_medio"])
        ax.errorbar(c.p_medio, c.freq, yerr=[c.freq - c.freq_lo, c.freq_hi - c.freq],
                    fmt="-", color=cor, lw=1.2, capsize=2, alpha=0.9, label=rotulo, zorder=2)
        ax.scatter(c.p_medio, c.freq, s=10 + 110 * np.sqrt(c.n / c.n.max()), color=cor, zorder=3,
                   edgecolor=p["grade"], lw=0.5)
    ax.set_xlabel("preço no Polymarket   (tamanho do ponto = nº de observações)")
    ax.set_ylabel("frequência observada")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.grid(True, lw=0.4, alpha=0.6)
    ax.legend(frameon=False, loc="upper left")
    ax.set_title("Preço × frequência observada")
    return fig


def fig_brier(tab, p):
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.8))
    cores = {"FOMC": p["kairos"], "CPI": p["apoio"], "pooled": p["texto"]}
    for familia, g in tab.groupby("familia"):
        g = g.sort_values("h")
        if familia == "pooled":   # além de 20 dias só sobra FOMC: pooled viraria composição
            g = g[g.h <= 20]
            familia = "pooled (h ≤ 20)"
        cor = cores[familia.split()[0]]
        axes[0].plot(g.h, g.brier, "o-", color=cor, lw=1.4, ms=4, label=familia)
        if not familia.startswith("pooled"):
            axes[0].fill_between(g.h, g.brier_lo, g.brier_hi, color=cor, alpha=0.07, lw=0)
        axes[1].plot(g.h, g.bss, "o-", color=cor, lw=1.4, ms=4, label=familia)
    for (nome, valor), ls in zip(REFERENCIAS.items(), (":", "--", "-.")):
        axes[0].axhline(valor, color=p["suave"], lw=0.8, ls=ls, label=f"{nome} · {valor:.3f}")
    axes[0].set_xlabel("dias corridos antes da resolução"); axes[0].set_ylabel("Brier (menor = melhor)")
    axes[0].invert_xaxis(); axes[0].set_ylim(0, 0.13)
    axes[0].legend(frameon=False, ncol=2, loc="upper center", fontsize=7.5)
    axes[1].axhline(0, color=p["grade"], lw=1); axes[1].invert_xaxis(); axes[1].set_ylim(-0.05, 1.05)
    axes[1].set_xlabel("dias corridos antes da resolução"); axes[1].set_ylabel("skill vs uniforme (BSS)")
    axes[1].legend(frameon=False, loc="lower left")
    for ax in axes:
        ax.grid(True, lw=0.4, alpha=0.6)
    axes[0].set_title("Acurácia por horizonte (banda = IC 95 % por evento)")
    axes[1].set_title("Quanto acrescenta ao 'não sei' (1/K em cada bucket)")
    return fig


def fig_fomc_ff(tab, p):
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.8))
    tab = tab.sort_values("h")
    axes[0].plot(tab.h, tab.mae_poly, "o-", color=p["kairos"], label="Polymarket")
    axes[0].plot(tab.h, tab.mae_ff, "s-", color=p["bench"], label="futuro de FF (proxy DTB3−DFF)")
    axes[0].plot(tab.h, tab.mae_ff_dm, "s--", color=p["apoio"], label="proxy corrigido do viés (D12a)")
    axes[0].set_ylabel("erro absoluto médio (bps)"); axes[0].set_title("Erro do Δtaxa previsto")
    w = 0.38
    barras = tab.sort_values("h", ascending=False)   # mesmo sentido do painel da esquerda
    x = np.arange(len(barras))
    axes[1].bar(x - w / 2, barras.acerto_modal_poly, w, color=p["kairos"], label="Polymarket")
    axes[1].bar(x + w / 2, barras.acerto_modal_ff_dm, w, color=p["apoio"], label="proxy corrigido")
    axes[1].set_xticks(x, barras.h); axes[1].set_ylim(0, 1.2)
    axes[1].set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    axes[1].set_ylabel("acerto do desfecho modal"); axes[1].set_title("Acerto da decisão mais provável")
    axes[0].invert_xaxis()
    axes[0].legend(frameon=False, loc="lower left")
    axes[1].legend(frameon=False, loc="upper center", ncol=2)
    for ax in axes:
        ax.set_xlabel("dias corridos antes da reunião"); ax.grid(True, lw=0.4, alpha=0.6, axis="y")
    return fig


def fig_leadlag(ccf, p):
    fig, ax = plt.subplots(figsize=(5.6, 3.8))
    # Δpoly_t cobre [08:00 ET de t−1, 08:00 ET de t]; Δff_{t+k} cobre
    # [16:00 ET de t+k−1, 16:00 ET de t+k]: as janelas se cruzam só em k ∈ {−1, 0}.
    sobre = ccf.lag_k.isin([-1, 0])
    ax.bar(ccf.lag_k[sobre], ccf["corr"][sobre], color=p["bench"], label="janelas sobrepostas (mecânico)")
    ax.bar(ccf.lag_k[~sobre], ccf["corr"][~sobre], color=p["kairos"], label="sem sobreposição (o teste)")
    ax.axhline(0, color=p["grade"], lw=1)
    n = int(ccf.n.min())
    ax.axhline(1.96 / np.sqrt(n), color=p["suave"], lw=0.8, ls=":", label="±1,96/√n")
    ax.axhline(-1.96 / np.sqrt(n), color=p["suave"], lw=0.8, ls=":")
    ax.set_xlabel("k   (k > 0: Polymarket de hoje × futuro de FF k dias DEPOIS)")
    ax.set_ylabel("corr(ΔE_poly_t, ΔE_FF_{t+k})")
    ax.set_title("Quem se move primeiro — 60 dias antes de cada reunião")
    ax.grid(True, lw=0.4, alpha=0.6, axis="y"); ax.legend(frameon=False, fontsize=7.5)
    return fig


def fig_event_study(es, p):
    f = es[es.familia == "FOMC"].pivot(index="ativo", columns="surpresa", values="r2")
    ordem = [c for c in ("poly", "ff_dm", "kuttner_dDTB3") if c in f.columns]
    f = f[ordem]
    fig, ax = plt.subplots(figsize=(7.5, 3.8))
    x = np.arange(len(f)); w = 0.8 / len(ordem)
    cores = {"poly": p["kairos"], "ff_dm": p["bench"], "kuttner_dDTB3": p["apoio"]}
    rotulos = {"poly": "surpresa-Polymarket", "ff_dm": "surpresa-FF (proxy corrigido)",
               "kuttner_dDTB3": "Kuttner (ΔDTB3 do dia)"}
    for j, col in enumerate(ordem):
        ax.bar(x + (j - (len(ordem) - 1) / 2) * w, f[col], w, color=cores[col], label=rotulos[col])
    ax.set_xticks(x, f.index); ax.set_ylabel("R² do retorno do dia do FOMC")
    ax.set_title("Qual expectativa explica o retorno do dia do anúncio?")
    ax.grid(True, lw=0.4, alpha=0.6, axis="y"); ax.legend(frameon=False)
    return fig


# Paleta do deck restilizado (slides_final_pptx.py) para as figuras que vão
# DENTRO do slide 16 — mais vivas que a paleta do relatório.
SLIDE = {"laranja": "#FFB531", "azul": "#4F8EF7", "verde": "#2FD3B0", "cinza": "#8395B5",
         "texto": "#F5F7FB", "suave": "#BAC6DA", "grade": "#2A3F63", "fundo": "#0A1325"}


def _estilo_slide():
    return plt.rc_context({
        "font.size": 13, "axes.titlesize": 14, "legend.fontsize": 12,
        "xtick.labelsize": 12, "ytick.labelsize": 12, "axes.labelsize": 13,
        "text.color": SLIDE["texto"], "axes.labelcolor": SLIDE["suave"],
        "xtick.color": SLIDE["suave"], "ytick.color": SLIDE["suave"],
        "axes.edgecolor": SLIDE["grade"], "grid.color": SLIDE["grade"],
        "axes.spines.top": False, "axes.spines.right": False, "figure.autolayout": True})


def fig_slide_calibracao(bins):
    """Calibração para o slide 16: sem barras de erro, ticks em %, pontos ∝ n."""
    with _estilo_slide():
        fig, ax = plt.subplots(figsize=(7.0, 3.6))
        ax.plot([0, 1], [0, 1], color=SLIDE["suave"], lw=1.3, ls="--", label="calibração perfeita", zorder=1)
        series = (("pooled", SLIDE["laranja"], "todos os horizontes", 2.6),
                  ("h=0", SLIDE["verde"], "véspera do evento", 2.0))
        for recorte, cor, rotulo, lw in series:
            c = bins[bins.recorte == recorte].dropna(subset=["p_medio"])
            ax.plot(c.p_medio, c.freq, "-", color=cor, lw=lw, label=rotulo, zorder=2)
            ax.scatter(c.p_medio, c.freq, s=30 + 170 * np.sqrt(c.n / c.n.max()), color=cor,
                       zorder=3, edgecolor=SLIDE["fundo"], lw=0.8)
        ticks = [0, 0.25, 0.5, 0.75, 1]
        rotulos = [f"{int(t * 100)} %" for t in ticks]
        ax.set_xticks(ticks, rotulos); ax.set_yticks(ticks, rotulos)
        ax.set_xlim(-0.02, 1.02); ax.set_ylim(-0.03, 1.05)
        ax.set_xlabel("o que o Polymarket disse"); ax.set_ylabel("quantas vezes aconteceu")
        ax.grid(True, lw=0.5, alpha=0.5)
        ax.legend(frameon=False, loc="upper left", handlelength=1.8)
    return fig


def fig_slide_mae(tab):
    """Erro do Δtaxa por horizonte para o slide 16, com o valor da véspera na ponta."""
    with _estilo_slide():
        fig, ax = plt.subplots(figsize=(7.0, 3.6))
        tab = tab.sort_values("h")
        ax.plot(tab.h, tab.mae_ff, "-o", color=SLIDE["cinza"], lw=1.5, ms=4, label="mercado de juros (cru)")
        ax.plot(tab.h, tab.mae_ff_dm, "--s", color=SLIDE["azul"], lw=2.2, ms=5, label="mercado de juros (corrigido)")
        ax.plot(tab.h, tab.mae_poly, "-o", color=SLIDE["laranja"], lw=3.0, ms=6, label="Polymarket")
        for serie, cor in ((tab.mae_poly, SLIDE["laranja"]), (tab.mae_ff_dm, SLIDE["azul"])):
            v = float(serie.iloc[0])                       # h = 0, a véspera
            ax.annotate(f"{v:.1f} bps".replace(".", ","), (0, v), xytext=(9, 0),
                        textcoords="offset points", ha="left", va="center", color=cor,
                        fontsize=13, fontweight="bold")
        ax.set_xlim(63, -12); ax.set_ylim(0, 13)
        ax.set_xticks([60, 45, 30, 20, 10, 0])
        ax.set_xlabel("dias antes da reunião do Fed"); ax.set_ylabel("erro médio (bps)")
        ax.grid(True, lw=0.5, alpha=0.5)
        ax.legend(frameon=False, loc="lower left", handlelength=2.2)
    return fig


def fig_sintese(celulas, p):
    """Placar 'onde está o valor': lista de (pergunta, veredito, número)."""
    fig, ax = plt.subplots(figsize=(7.5, 0.72 * len(celulas) + 0.3))
    ax.axis("off"); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    passo = 1 / len(celulas)
    for i, (pergunta, ok, numero) in enumerate(celulas):
        y = 1 - (i + 0.5) * passo
        cor = p["apoio"] if ok else p["negativo"]
        ax.text(0.02, y, "✔" if ok else "✖", color=cor, fontsize=15, va="center", ha="left", fontweight="bold")
        ax.text(0.08, y + 0.18 * passo, pergunta, color=p["texto"], fontsize=10, va="center", ha="left")
        ax.text(0.08, y - 0.22 * passo, numero.replace(".", ","), color=p["suave"], fontsize=8.5,
                va="center", ha="left")
        if i:
            ax.axhline(y + 0.5 * passo, color=p["grade"], lw=0.6, xmin=0.02, xmax=0.98)
    return fig


# =============================================================================
# 7. Markdown
# =============================================================================

def _md(df, fmt="{:.3f}"):
    df = df.copy()
    for c in df.columns:
        if pd.api.types.is_float_dtype(df[c]):
            df[c] = df[c].map(lambda v: "—" if pd.isna(v) else fmt.format(v))
        elif pd.api.types.is_datetime64_any_dtype(df[c]):
            df[c] = df[c].dt.strftime("%Y-%m-%d")
    linhas = ["| " + " | ".join(map(str, df.columns)) + " |", "|" + "---|" * len(df.columns)]
    linhas += ["| " + " | ".join(map(str, r)) + " |" for r in df.itertuples(index=False)]
    return "\n".join(linhas)


def escrever_metricas(tabelas, caminho=METRICAS):
    t = tabelas
    partes = [
        "# Métricas do estudo — Polymarket como fonte de sinal\n",
        "> Gerado por `scripts/estudo_polymarket.py`. **Mede; não decide.** Fonte "
        "dos números de `Final/estudo/Estudo_polymarket.md`; nada é digitado à mão.\n",
        "## Cobertura por horizonte\n", _md(t["cobertura_h"]),
        "\n## Q1 · Brier, log-loss e skill por horizonte (IC 95 % por evento)\n",
        _md(t["brier_horizonte"]),
        "\n## Q1 · Decomposição de Murphy, regressão de calibração e γ ótimo\n", _md(t["murphy"]),
        "\n## Q1 · Extremos (favorito-azarão)\n", _md(t["extremos"]),
        "\n## Q1 · RPS médio por família e h\n",
        _md(t["rps"].groupby(["familia", "h"])[["rps_poly", "rps_uniforme", "rps_persistencia"]].mean().reset_index()),
        "\n## Q1 · Overround (Σp da PMF) por família e h\n", _md(t["overround"]),
    ]
    if "volume" in t:
        partes += ["\n## Q1 · Brier por tercil de volume (FOMC)\n", _md(t["volume"])]
    partes += [
        "\n## Q2 · FOMC — Polymarket × futuro de FF (proxy DTB3−DFF) por horizonte\n",
        _md(t["fomc_vs_ff"]),
        "\n## Q2 · Encompassing (Δreal = a + b₁·E_poly + b₂·E_FF, EP HC1)\n", _md(t["encompassing"]),
        "\n## Q2 · Lead-lag — correlação cruzada\n", _md(t["leadlag_ccf"]),
        "\n## Q2 · Lead-lag — regressões com EP de Newey-West\n", _md(t["leadlag_granger"]),
        "\n## Q3 · Event-study do dia do anúncio\n", _md(t["event_study"]),
        "\n## Q3 · Martingale do preço (slots de 12 h)\n", _md(t["martingale"]),
    ]
    Path(caminho).write_text("\n".join(partes) + "\n", encoding="utf-8")
    return caminho


# =============================================================================
# 8. Orquestração
# =============================================================================

def medir(raiz=RAIZ):
    fomc, faltas_fomc, diarias_fomc = amostra_fomc(raiz)
    cpi, faltas_cpi, diarias_cpi = amostra_cpi(raiz)
    obs = pd.concat([fomc, cpi], ignore_index=True)
    tabelas = {"observacoes": obs,
               "cobertura_h": cobertura(obs, {"FOMC": faltas_fomc, "CPI": faltas_cpi})}
    tabelas.update(q1(obs))
    tabelas.update(q2(diarias_fomc, raiz))
    tabelas.update(q3(diarias_fomc, diarias_cpi, tabelas["fomc_previsoes"], pmfs_payrolls(raiz), raiz))
    return tabelas


def sintese(t):
    bh = t["brier_horizonte"]
    b0 = bh[(bh.familia == "pooled") & (bh.h == 0)].iloc[0]
    reg = t["murphy"][t["murphy"].recorte == "pooled"].iloc[0]
    ff = t["fomc_vs_ff"].set_index("h")
    es = t["event_study"]
    r2 = es[es.familia == "FOMC"].groupby("surpresa").r2.mean()
    mart = t["martingale"][(t["martingale"].filtro == "todos")]
    vr = mart[mart.familia == "FOMC"].iloc[0]
    reg0 = t["murphy"][t["murphy"].recorte == "h=0"].iloc[0]
    return [
        ("Preço = probabilidade calibrada na véspera (b ≈ 1, a ≈ 0)",
         reg0.p_wald > 0.05, f"b = {reg0.b:.2f} · p(Wald) = {reg0.p_wald:.2f} · pooled b = {reg.b:.2f}"),
        ("Acrescenta ao 'não sei' na véspera (skill vs uniforme)",
         b0.bss > 0, f"Brier {b0.brier:.3f} · BSS {b0.bss:.2f}"),
        ("Erra menos que o futuro de FF na véspera (MAE em bps, proxy corrigido)",
         ff.loc[0, "mae_poly"] < ff.loc[0, "mae_ff_dm"],
         f"{ff.loc[0, 'mae_poly']:.1f} × {ff.loc[0, 'mae_ff_dm']:.1f} · acerto modal "
         f"{ff.loc[0, 'acerto_modal_poly']:.0%} × {ff.loc[0, 'acerto_modal_ff_dm']:.0%}"),
        ("A surpresa-poly explica o retorno do dia do FOMC",
         r2.get("poly", 0) > 0.2, f"R² médio {r2.get('poly', np.nan):.2f} — quase não sobra surpresa"),
        ("Δp antecipa o retorno dos ETFs antes do anúncio (Teste_sinal.md)",
         False, "t ≈ 0 em h = 0, 1, 5"),
        ("O movimento do preço tem tendência explorável (VR > 1)",
         vr.vr5_lo > 1, f"VR(5) = {vr.vr5:.2f} [{vr.vr5_lo:.2f}; {vr.vr5_hi:.2f}] — reversão de tick"),
    ]


def gerar(tema="escuro"):
    p = PALETAS[tema]
    aplicar_estilo(p)
    t = medir()
    DADOS.mkdir(parents=True, exist_ok=True)
    for nome, df in t.items():
        df.to_csv(DADOS / f"{nome}.csv", index=False)
    figuras = {"estudo_1_calibracao": fig_calibracao(t["calibracao_bins"], p),
               "estudo_2_brier": fig_brier(t["brier_horizonte"], p),
               "estudo_3_fomc_ff": fig_fomc_ff(t["fomc_vs_ff"], p),
               "estudo_4_leadlag": fig_leadlag(t["leadlag_ccf"], p),
               "estudo_5_event_study": fig_event_study(t["event_study"], p),
               "estudo_6_sintese": fig_sintese(sintese(t), p),
               "estudo_s0_calibracao": fig_slide_calibracao(t["calibracao_bins"]),
               "estudo_s2_mae": fig_slide_mae(t["fomc_vs_ff"])}
    for nome, fig in figuras.items():
        salvar(fig, GRAFICOS, nome)
    escrever_metricas(t)
    return t


# =============================================================================
# 9. Auto-teste
# =============================================================================

def demo():
    rng = np.random.default_rng(0)
    n = 20000
    p = rng.uniform(0.01, 0.99, n)
    y = (rng.uniform(size=p.shape) < p).astype(float)      # calibrado por construção
    cluster = np.arange(n) // 5
    conf, res, inc = murphy(p, y, 10)
    # a identidade de Murphy fecha contra o Brier do previsor BINADO (p̄ do bin)
    p_bin = pd.Series(p).groupby(bins_de(p, 10)).transform("mean").to_numpy()
    assert conf < 0.002 and abs(conf - res + inc - brier(p_bin, y)) < 1e-12
    reg = regressao_calibracao(p, y, cluster)
    assert abs(reg["b"] - 1) < 0.03 and reg["p_wald"] > 0.01
    assert abs(brier(np.full(n, 0.5), y) - 0.25) < 1e-3
    assert rps([0, 1, 0], [0, 1, 0]) == 0 and rps([1, 0, 0], [0, 0, 1]) == 1
    g, _ = gamma_otimo(p, y, np.array([0.8, 1.0, 1.25]))
    assert g == 1.0
    ruido = [rng.normal(size=500) for _ in range(30)]
    assert abs(variance_ratio(ruido, 5) - 1) < 0.1 and abs(acf_pooled(ruido, 1)) < 0.05
    dm, pv = diebold_mariano(rng.normal(size=18), rng.normal(size=18) * 3)
    assert dm < 0 and pv < 0.05
    dm0, _ = diebold_mariano(np.arange(5.0), np.arange(5.0))
    assert np.isnan(dm0)                                    # séries idênticas: d ≡ 0
    X = np.column_stack([np.ones(200), rng.normal(size=200)])
    b, V = newey_west(X, X @ [1, 2] + rng.normal(size=200) * 0.1)
    assert np.allclose(b, [1, 2], atol=0.05) and V.shape == (2, 2)
    assert list(vencedor([-50, -25, 0, 25], (True, False, False, True), -75)) == [1, 0, 0, 0]
    assert list(vencedor([-50, -25, 0, 25], (True, False, False, True), -25)) == [0, 1, 0, 0]
    lo, hi = bootstrap_por_cluster(cluster, lambda i: brier(p[i], y[i]), B=50)
    assert lo < brier(p, y) < hi
    print("demo ok")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true")
    parser.add_argument("--tema", default="escuro", choices=list(PALETAS))
    args = parser.parse_args()
    if args.demo:
        demo()
        return
    t = gerar(args.tema)
    obs = t["observacoes"]
    print(f"observações: {len(obs)} · eventos: {obs.evento.nunique()} · "
          f"mercados: {obs.mercado.nunique()}")
    print(t["brier_horizonte"][t["brier_horizonte"].familia == "pooled"][["h", "n", "brier", "bss"]].to_string(index=False))
    print(t["fomc_vs_ff"][["h", "n", "mae_poly", "mae_ff", "mae_ff_dm", "acerto_modal_poly",
                           "acerto_modal_ff_dm", "p_dm", "p_dm_vs_ff_dm"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
