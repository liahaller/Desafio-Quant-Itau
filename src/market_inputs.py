"""Σ, w_mkt e Ω de fallback — as entradas do otimizador. Módulo do Felipe.

Buraco que existia no repo: `bl_optimizer` e `bl_integration` recebem `sigma`,
`w_mkt` e `omega` PRONTOS, e nada os construía. Este módulo fecha isso, com
funções puras que recebem a tabela de preços e devolvem arrays.

Decisões de módulo tomadas aqui (escopo próprio, categoria 2 do CLAUDE.md §1),
todas sem inventar número:

  - **Σ = covariância amostral** de retornos diários em janela móvel
    (`config.SIGMA_JANELA_PREGOES`). Medido em 04/08 no dado real: número de
    condição de 173 a 245 nas janelas de 252/504/756 pregões — **bem
    invertível**, então NÃO entra encolhimento (Ledoit-Wolf e afins). O R² do
    SPY contra os outros 8 é 0,96 (o universo tem o índice e os próprios
    setores dele), alto mas longe de degenerado. Se o condicionamento piorar
    em alguma janela, `sample_covariance` avisa em vez de devolver lixo.

  - **w_mkt = 100% no ativo de mercado (SPY)** — prior CAPM. O motivo é falta
    de dado, e a saída é honesta em vez de arbitrária: para ponderar por valor
    de mercado seriam precisos os tamanhos dos 9 ETFs, que ninguém entregou;
    peso igual entre SPY e sete setores DELE contaria a bolsa duas vezes. Com
    w_mkt = e_SPY, `π = δ·Σ·w_mkt` vira exatamente o retorno de equilíbrio do
    CAPM (δ·β_i·σ²_mkt), sem nenhum número inventado, e o benchmark do backtest
    passa a ser "comprar e segurar SPY", que é o mais interpretável possível.
    `equal_weights` fica disponível como alternativa de robustez.

  - **Ω de fallback = diag(P·τΣ·Pᵀ)** enquanto o Ω reativo da Lia não chega.
    É a convenção He-Litterman: a incerteza da view proporcional à incerteza
    que o próprio prior já atribui àquela combinação de ativos. Não tem
    parâmetro livre, e é EXATAMENTE a régua que o Ω dela deve multiplicar —
    ou seja, o fallback e o contrato de interface são a mesma fórmula.
"""

import numpy as np
import pandas as pd

from config import MARKET_ASSET, SIGMA_JANELA_PREGOES

# Acima disso a inversão de Σ começa a amplificar ruído de forma material;
# é um alarme de diagnóstico, não um parâmetro do modelo (medido: 173–245).
COND_ALERTA = 1e4


def daily_returns(precos):
    """Retornos diários simples da tabela larga de fechamento."""
    return precos.pct_change().dropna(how="all")


def sample_covariance(returns, data=None, janela=SIGMA_JANELA_PREGOES):
    """Σ amostral dos `janela` pregões ANTERIORES a `data` (sem lookahead).

    returns : (T, n) DataFrame de retornos diários, colunas na ordem do universo.
    data    : data do rebalanceamento; None = usa a cauda da amostra inteira.

    Devolve (n, n) ndarray. Levanta se a janela não tem pregões suficientes —
    Σ estimada com menos linhas que ativos é singular por construção.
    """
    if data is not None:
        returns = returns[returns.index < pd.Timestamp(data)]
    janela_df = returns.tail(janela).dropna()
    n = janela_df.shape[1]
    if len(janela_df) < max(janela // 2, n + 1):
        raise ValueError(
            f"janela curta para estimar Σ: {len(janela_df)} pregões utilizáveis "
            f"para {n} ativos (mínimo {max(janela // 2, n + 1)})")
    sigma = janela_df.cov().to_numpy()
    cond = np.linalg.cond(sigma)
    if cond > COND_ALERTA:
        raise ValueError(
            f"Σ mal condicionada (cond = {cond:.1e}) na janela que termina em "
            f"{janela_df.index[-1].date()} — inverter isso amplifica ruído. "
            f"Medido em 04/08 no dado real: 173 a 245. Investigar antes de rodar.")
    return sigma


def empirical_duration(returns, yield_changes, asset):
    """Duration EMPÍRICA de um ativo: −Δpreço% por ponto de variação do juro.

    Estimada do próprio dado (regressão do retorno diário contra a variação
    diária do DGS10, em pontos percentuais), não copiada da ficha do emissor.
    Duas razões: é a sensibilidade OBSERVADA, que é o que interessa para casar
    uma ponta contra a outra; e não entra número inventado no modelo.

    Medido em 04/08 sobre 2016–2026 (2.508 pregões): TIP 4,99 anos (t −53),
    TLT 15,92 (t −105). A duration de ficha dos títulos subjacentes é maior
    (~7 e ~26); o que se mede aqui é a resposta efetiva ao 10 anos.

    Devolve anos. `returns` e `yield_changes` alinhados por data.
    """
    par = pd.concat([returns[asset].rename("r"), yield_changes.rename("dy")],
                    axis=1).dropna()
    if len(par) < 60:
        raise ValueError(f"amostra curta para duration de {asset}: {len(par)} pregões")
    X = np.column_stack([np.ones(len(par)), par["dy"].to_numpy()])
    beta, *_ = np.linalg.lstsq(X, par["r"].to_numpy(), rcond=None)
    return float(-beta[1] * 100.0)


def breakeven_duration(pair_returns, breakeven_changes):
    """Duration do BREAKEVEN para a view 2.2: retorno do par por unidade de
    variação do breakeven de 10 anos, estimado no próprio dado.

    Decidido em sessão (Felipe, 2026-08-05) no lugar do "~8" da espec, que
    nunca virou número fechado (LOG 2026-07-09: "valor exato da duration por
    decisão humana"). O motivo é o mesmo de `empirical_duration`: 8 é a
    duration de REFERÊNCIA do instrumento, e o que a view precisa é a
    sensibilidade do PAR que ela de fato monta — que mudou quando o I3b casou
    as durations de TIP e TLT. Medir mantém as duas pontas consistentes.

    `pair_returns`      : retorno diário do par (retornos @ P da view 2.2).
    `breakeven_changes` : Δ do breakeven na MESMA unidade da divergência
                          (fração decimal), alinhado por data.

    Devolve o coeficiente b de `r_par = a + b·Δbreakeven`. O sinal esperado é
    POSITIVO: poly mais inflacionista que o título ⇒ o breakeven sobe ⇒ o par
    (comprado no indexado) ganha. Coeficiente negativo é sinal de que o par
    está invertido, e a função deixa passar de propósito — quem lê decide, o
    número não é censurado aqui.
    """
    par = pd.concat([pd.Series(pair_returns).rename("r"),
                     pd.Series(breakeven_changes).rename("dbe")], axis=1).dropna()
    if len(par) < 60:
        raise ValueError(f"amostra curta para duration do breakeven: {len(par)} pregões")
    X = np.column_stack([np.ones(len(par)), par["dbe"].to_numpy()])
    beta, *_ = np.linalg.lstsq(X, par["r"].to_numpy(), rcond=None)
    return float(beta[1])


def market_weights(assets, market_asset=MARKET_ASSET):
    """w_mkt do prior CAPM: todo o peso no ativo de mercado.

    Ver o cabeçalho do módulo para o porquê (não há dado de tamanho, e peso
    igual contaria a bolsa duas vezes). Com este w_mkt e nenhuma view ativa,
    `bl_weights_from_views` devolve exatamente esta carteira — o benchmark do
    backtest é comprar e segurar SPY.
    """
    assets = list(assets)
    if market_asset not in assets:
        raise ValueError(f"{market_asset} não está no universo: {assets}")
    w = np.zeros(len(assets))
    w[assets.index(market_asset)] = 1.0
    return w


def equal_weights(assets):
    """Alternativa de robustez: peso igual. Conta a bolsa mais de uma vez
    (o universo tem o índice e sete setores dele) — usar só para checar
    sensibilidade do prior, nunca como caso base."""
    return np.full(len(assets), 1.0 / len(assets))


def omega_fallback(P, sigma, tau, confianca=None):
    """Ω (k, k) diagonal na convenção He-Litterman: diag(P·τΣ·Pᵀ).

    `confianca` : (k,) multiplicador por view — é ESTE o número que o Ω reativo
                  da Lia deve entregar (>1 = menos confiança, <1 = mais).
                  None = 1,0 em todas, que é o fallback neutro.

    Enquanto o módulo dela não chega, o backtest roda com o fallback; quando
    chegar, entra como `confianca` e nada mais muda. Se ela entregar em escala
    absoluta, a conversão é dividir pela diagonal desta mesma fórmula.
    """
    P = np.atleast_2d(np.asarray(P, dtype=float))
    variancias = np.diag(P @ (tau * np.asarray(sigma, dtype=float)) @ P.T)
    if confianca is None:
        confianca = np.ones(P.shape[0])
    confianca = np.asarray(confianca, dtype=float)
    if confianca.shape != (P.shape[0],):
        raise ValueError(
            f"confiança deve ter uma entrada por view: {confianca.shape} vs ({P.shape[0]},)")
    if np.any(confianca <= 0):
        raise ValueError("confiança tem de ser positiva — Ω é matriz de variância")
    if np.any(variancias <= 0):
        raise ValueError("view com variância de prior nula — P sem exposição a risco")
    return np.diag(variancias * confianca)
