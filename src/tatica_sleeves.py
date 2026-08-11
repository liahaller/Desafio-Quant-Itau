"""Camada tática v2 — sleeves transversais de livro neutro. Felipe.

UM módulo para a camada inteira, não um por sleeve. As duas candidatas
admitidas na **D28** (M4 recessão, M9 Câmara) compartilham tudo menos a série
de crença que leem, e escrever duas cópias garantiria divergência na primeira
correção.

**O que uma sleeve é, em uma frase:** todo pregão ela lê o `Δp` acumulado em
`k` do mercado do Polymarket, e assina um spread setorial **hedgeado contra o
SPY** na direção que a premissa declarada manda.

As decisões que este módulo implementa, todas fechadas na D28 e nenhuma tomada
aqui:

  item 3  o `k` é o BLOCO declarado, com PESO IGUAL — a média das pernas, não
          a soma. Somar daria à M4 (três lookbacks) o triplo do tamanho da M9
          (um), o que seria escolher tamanho por contagem de horizonte.
  item 4  livro HEDGEADO: cada perna entra com o beta de mercado removido, por
          β **expansivo defasado em um dia**, semeado em `MINIMO_PREGOES`.
  item 9  tamanho pela âncora `inv(δΣ)·μ` da D16 — **zero parâmetro livre**.
          Não existe `orcamento` aqui, e não se deve reintroduzir (12c).
  item 11 sleeves que compartilham livro têm os μ SOMADOS antes do `inv(δΣ)`.
  item 2  (D24) leitura ausente no slot pré-abertura desativa a perna no dia.

⚠️ **O universo negociável continua sendo o dos 9 ETFs.** A perna `XLP⊥` não
existe no mercado: ela é `XLP − β·SPY`, e uma posição nela é replicada com
`XLP` e uma ponta compensatória em `SPY`. O `dw` que sai daqui já está
traduzido para os 9 ativos reais — quem consome nunca vê a coluna sintética.

⚠️ **Onde este módulo DIVERGE do artefato que aprovou as sleeves, e é de
propósito:** o `Gate_transversal_neutro.md` mediu a Σ com a cauda da amostra
INTEIRA, o que num gate é aceitável e num backtest seria lookahead. Aqui a Σ
usa só os pregões estritamente anteriores ao dia montado. A diferença entra na
ESCALA do `dw` (via `1/σ²`), nunca no sinal — e o sinal é o que o G2 mediu.
"""

from dataclasses import dataclass
from typing import Mapping, Sequence

import numpy as np
import pandas as pd

from bl_optimizer import optimal_weights
from config import SIGMA_JANELA_PREGOES, TAU
from tatica_drift_anuncio import estimate_drift_mu
from taticas_common import OverlayResult

# Sufixo da perna hedgeada. Coluna nova em vez de sobrescrever: o retorno cru e
# o neutro precisam coexistir na mesma tabela.
SUFIXO = "⊥"

# Semeadura do β expansivo. NÃO é escolha nova: é a mesma constante que o
# `view_cpi_transversal`, a `view_3_1_direcional` e o `Gate_transversal_neutro`
# já usam para o mínimo de pregões de uma regressão neste projeto.
MINIMO_PREGOES = 60

MERCADO_REFERENCIA = "SPY"

# Janela do event-study, em pregões. 1 = sleeve reassinada todo pregão, igual
# ao C1a da D17 e a todos os gates da camada: `k` fica sendo lookback puro e
# nenhum parâmetro de permanência entra pela porta dos fundos.
JANELA = 1


@dataclass(frozen=True)
class Sleeve:
    """Uma candidata admitida. Tudo aqui é DECLARADO, nada é estimado.

    nome      : rótulo do diagnóstico.
    crenca    : `p` diário do mercado, já reindexado na grade de pregões.
    livro     : {ticker real: +1/−1} — para que lado cada setor anda quando o
                sinal SOBE. É o `LIVROS_SETORIAIS` do gate, sem alteração.
    lookbacks : os `k` do bloco declarado na D28. Entram com peso igual.
    """

    nome: str
    crenca: pd.Series
    livro: Mapping[str, int]
    lookbacks: Sequence[int]


def hedge_betas(retornos, tickers, referencia=MERCADO_REFERENCIA,
                minimo=MINIMO_PREGOES):
    """β de cada ticker contra o mercado, EXPANSIVO e defasado em um dia.

    Sem o `.shift(1)` o hedge conheceria o próprio retorno que está removendo,
    e o spread sairia artificialmente limpo — mesma proibição de lookahead das
    views (D7.4). Devolve DataFrame (datas × tickers), com `NaN` antes da
    semeadura.
    """
    mercado = retornos[referencia]
    var = mercado.expanding(min_periods=minimo).var()
    return pd.DataFrame(
        {t: (retornos[t].expanding(min_periods=minimo).cov(mercado) / var).shift(1)
         for t in tickers},
        index=retornos.index)


def pernas_neutras(retornos, tickers, referencia=MERCADO_REFERENCIA,
                   minimo=MINIMO_PREGOES):
    """Adiciona `TICKER⊥` = retorno do ticker com o beta de mercado removido.

    Vive em `src/` e não no script do gate porque o backtest precisa da MESMA
    construção que aprovou as sleeves. Duas cópias divergiriam na primeira
    correção, e a diferença apareceria como resultado.
    """
    betas = hedge_betas(retornos, tickers, referencia, minimo)
    saida = retornos.copy()
    for ticker in tickers:
        saida[f"{ticker}{SUFIXO}"] = retornos[ticker] - betas[ticker] * retornos[referencia]
    return saida


def neutraliza(livro):
    """{XLP: +1, XLK: −1} -> {XLP⊥: +1, XLK⊥: −1}. Mesmos sinais, pernas limpas."""
    return {f"{a}{SUFIXO}": p for a, p in livro.items()}


def _sigma_diagonal(estendido, data, janela=SIGMA_JANELA_PREGOES):
    """Σ DIAGONAL da tabela estendida, com dado estritamente anterior a `data`.

    Diagonal e não amostral cheia porque é o que o `estimate_drift_mu` e o
    `inv(δΣ)` deste módulo de fato leem — e porque a Σ cheia desta tabela é
    **singular por construção**: `XLP⊥` é combinação linear exata de `XLP` e
    `SPY`, então o guarda de condicionamento do `sample_covariance` reprova, e
    com razão.
    """
    passado = estendido[estendido.index < data]
    if len(passado) < 2:
        return None
    return np.diag(passado.tail(janela).var().to_numpy())


def _mu_da_perna(estendido, sinal, livro_neutro, data, sigma_ext, tau):
    """(μ estendido assinado, direção, n) de UM lookback, ou (None, 0, 0).

    A direção do dia sai da última leitura do sinal **estritamente anterior** a
    `data`, que é a convenção do backtest ("os pesos de D usam dado anterior a
    D") e também a do G2 que mediu estas sleeves (evento em E, retorno em E+1).
    Ler o sinal do próprio dia adiantaria o resultado em um pregão.

    **Veto da D24 (item 2):** leitura ausente vira `NaN` no `diff`, e `NaN` não
    vira direção — a perna dorme em vez de herdar a de ontem.
    """
    anteriores = sinal.index[sinal.index < data]
    if not len(anteriores):
        return None, 0.0, 0
    valor = sinal.loc[anteriores[-1]]
    if not np.isfinite(valor) or valor == 0:
        return None, 0.0, 0
    eventos = [(d, np.sign(v)) for d, v in sinal.items()
               if d < data and np.isfinite(v) and v != 0]
    mu, n = estimate_drift_mu(estendido, eventos, JANELA, tuple(livro_neutro),
                              data, sigma_ext, tau)
    if mu is None:
        return None, 0.0, n
    return np.asarray(mu, dtype=float) * float(np.sign(valor)), float(np.sign(valor)), n


def sleeve_overlay(assets, estendido, betas, sleeves, data, delta, tau=TAU,
                   referencia=MERCADO_REFERENCIA):
    """`OverlayResult` da camada tática para UM pregão, ou None se dormente.

      assets    : universo negociável na ordem do dataset (os 9 ETFs).
      estendido : retornos com as pernas `⊥`, de `pernas_neutras`.
      betas     : os β defasados, de `hedge_betas` — usados para traduzir a
                  posição sintética em posição real.
      sleeves   : as `Sleeve` admitidas.
      delta     : aversão a risco (D7: 3,0, observável — não é parâmetro livre).

    O `dw` volta indexado em `assets`, com a ponta de hedge já somada no ativo
    de referência. Sleeve dormente não entra; nenhuma sleeve ativa devolve None,
    que o `apply_overlays` trata como "não soma".
    """
    sigma_ext = _sigma_diagonal(estendido, data)
    if sigma_ext is None:
        return None

    colunas = list(estendido.columns)
    mu_total = np.zeros(len(colunas))
    detalhe, ativas = {}, 0
    for sleeve in sleeves:
        livro_neutro = neutraliza(sleeve.livro)
        pernas, direcoes, eventos = [], [], []
        for k in sleeve.lookbacks:
            mu_k, direcao, n = _mu_da_perna(
                estendido, sleeve.crenca.diff(k), livro_neutro, data,
                sigma_ext, tau)
            if mu_k is None:
                continue
            pernas.append(mu_k)
            direcoes.append(direcao)
            eventos.append(n)
        if not pernas:
            continue
        # PESO IGUAL dentro do bloco (item 3): a média, não a soma. O bloco é
        # UMA posição medida em três horizontes, não três posições.
        mu_total += np.mean(pernas, axis=0)
        ativas += 1
        detalhe[sleeve.nome] = {
            "lookbacks_ativos": len(pernas),
            "direcoes": direcoes,
            "eventos_no_mu": eventos,
        }
    if not ativas:
        return None

    # ITEM 11: um `inv(δΣ)` só, sobre a SOMA dos μ. A M4 e a M9 usam o mesmo
    # livro (`+XLP −XLK`); resolvidas em separado e somadas depois, a mesma
    # perna seria dimensionada duas vezes.
    #
    # O `inv(δΣ)` roda SÓ nas pernas dos livros, não nas 15 colunas da tabela
    # estendida. Não é atalho e não muda o resultado: a Σ aqui é diagonal por
    # construção (ver `_sigma_diagonal`), e ativo fora do livro entra com
    # μ = 0, logo peso 0. O que a restrição evita é a tabela inteira ser
    # invertida por causa de colunas que a camada não usa — basta uma delas ter
    # variância nula no recorte para o `solve` reprovar a montagem toda.
    pernas_usadas = sorted({c for s in sleeves for c in neutraliza(s.livro)},
                           key=colunas.index)
    idx = [colunas.index(c) for c in pernas_usadas]
    var_pernas = np.diag(sigma_ext)[idx]
    if not np.all(np.isfinite(var_pernas)) or np.any(var_pernas <= 0):
        return None  # perna sem variância no recorte: não há como dimensionar
    dw_ext = np.zeros(len(colunas))
    dw_ext[idx] = optimal_weights(mu_total[idx], np.diag(var_pernas), delta)

    # Tradução da posição sintética para o universo negociável: uma posição `w`
    # em `XLP⊥` = `XLP − β·SPY` é replicada com `w` em XLP e `−w·β` em SPY.
    dw = pd.Series(0.0, index=list(assets))
    linha_beta = betas.loc[data] if data in betas.index else None
    for i, coluna in enumerate(colunas):
        if not coluna.endswith(SUFIXO) or dw_ext[i] == 0.0:
            continue
        ticker = coluna[:-len(SUFIXO)]
        beta = float(linha_beta[ticker]) if linha_beta is not None else np.nan
        if not np.isfinite(beta):
            return None  # sem β conhecido não há como hedgear: dorme
        dw[ticker] += dw_ext[i]
        dw[referencia] -= dw_ext[i] * beta

    return OverlayResult(dw=dw.to_numpy(), diagnostics={
        "tatica": "sleeves_transversais",
        "sleeves_ativas": ativas,
        "detalhe": detalhe,
        "soma_abs_dw": float(np.abs(dw.to_numpy()).sum()),
        "dw": dw.to_numpy(),
    })
