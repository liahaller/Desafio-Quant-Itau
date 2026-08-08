"""Tática — drift pós-anúncio dimensionado por mean-variance (módulo do Felipe).

RECONSTRUÇÃO da camada tática, sessão de 2026-08-08 (direção da seção 14 do
`Decisoes_pendentes.md`). **Não substitui `tatica_drift_pos_fomc.py`**: aquele
módulo fica intacto porque é o que a decisão 12c registra como entregue
desligado. Este é o desenho novo, e a diferença é uma só — **não existe
`orcamento`**.

Por que isso importa mais que a fórmula: a 12c não desligou a camada por efeito
fraco (só drift mediu +0,08 a +0,80 pp em `Curva_orcamento.md`). Desligou porque
o tamanho não tinha âncora — o Δ era MONÓTONO no orçamento, a grade não tinha
ótimo interior, e escolher a linha de cima seria calibrar contra o resultado de
374 pregões. Aqui o tamanho sai do MESMO passo que dimensiona uma view:

    dw = inv(δ·Σ) @ (direção × μ)          (`bl_optimizer.optimal_weights`)

com δ = 3,0 (observável, medido no nosso SPY — D7) e a mesma Σ amostral da
decisão 8. O que sobra a estimar é `μ`, o retorno diário médio da janela do
drift, e ele é MEDIDO por event-study expansivo — mesmo padrão do β das views,
mesma proibição de lookahead. Não há parâmetro livre a calibrar.

Duas sleeves rodam este mesmo template (só mudam a família, o livro e a fonte
da surpresa) — ver `scripts/backtest_v1.py`:

  1. **FOMC**, livro SPY + TLT, surpresa = decisão realizada − E_poly[véspera].
  2. **CPI**, livro TIP + TLT, surpresa = Δ breakeven no dia da divulgação.

Âncora de literatura: Neuhierl & Weber (monetary momentum, ~15 dias úteis) e
Brooks, Katz & Lustig (drift em bonds). **A literatura não fixa o sinal**: o
sinal sai do `μ` estimado, pelo mesmo precedente das views ("β manda sempre,
literatura só sanity check a posteriori" — LOG de 2026-07-09). `direcao` é
convenção de sinal da surpresa; quem diz para que lado cada ativo anda é o `μ`.

Contrato de saída: `taticas_common.OverlayResult | None` (None = dormente),
igual às três táticas antigas — o `apply_overlays` não muda.
"""

import numpy as np

from bl_optimizer import optimal_weights
from taticas_common import OverlayResult


def estimate_drift_mu(retornos, eventos, janela, ativos_livro, ate_data,
                      sigma, tau):
    """μ (n,) — retorno diário médio na janela do drift, por unidade de direção.

    μ[i] = média, sobre os eventos passados, de `direção_e × (r̄_{e,i} − r̄_base,i)`,
    onde `r̄_{e,i}` é o retorno diário médio do ativo `i` nos dias úteis
    1..`janela` após o evento `e` e `r̄_base,i` é o retorno diário médio do ativo
    na amostra inteira até `ate_data`. Ativo fora de `ativos_livro` entra com
    μ = 0 — o livro é onde a âncora de literatura existe; o `inv(δΣ)` depois
    espalha o hedge.

    **A subtração da linha de base não é refinamento, é o que separa drift de
    prêmio de risco.** Medido em 08/08 sem ela: com a direção do FOMC saindo +1
    em quase todo evento (a maioria das reuniões da janela decidiu 0 contra um
    E_poly que precificava corte), μ[SPY] deu +10,53 bps/dia — que é o retorno
    médio do próprio bull market, não o drift do anúncio. A sleeve viraria "long
    SPY sempre que houve reunião". É a mesma correção que as views 2.2 e 2.3 já
    fazem com a média expansiva da divergência (D7.4 / decisão 12).

    **Expansivo e sem lookahead:** só entra evento cuja janela INTEIRA terminou
    estritamente antes de `ate_data`, e a linha de base também só olha para
    trás. Um evento em curso contaminaria o μ com o retorno que a sleeve ainda
    vai capturar.

    **ENCOLHIMENTO pela própria incerteza (obrigatório, não é opção).** Um μ de
    uma dúzia de eventos entrar no `inv(δΣ)` sem desconto é o mesmo que dar
    Ω = 0 a uma view — confiança infinita numa estimativa curta. O fator é o
    mesmo da convenção registrada do Ω (`diag(P·τΣ·Pᵀ)`, D7), aqui na versão de
    um ativo só:

        fator_i = τ·Σ_ii / (τ·Σ_ii + se²_i),   se²_i = var_entre_eventos_i / n

    Sem parâmetro novo: τ e Σ são os mesmos do BL. Com poucos eventos, ou com
    dispersão alta entre eles, o fator vai a zero e a sleeve simplesmente não
    pede tamanho — que é o comportamento correto e não uma escolha.

    retornos      : DataFrame (datas × tickers), a grade de pregões do backtest.
    eventos       : iterável de `(data_do_evento, direcao)` — direção em {−1, +1}.
    ate_data      : data que está sendo montada (exclusiva).
    sigma, tau    : os do BL (D7/D8) — entram só no encolhimento.
    Retorna `(mu (n,), n_eventos_usados)`; `(None, 0)` com menos de 2 eventos
    fechados (com um evento não há como medir a dispersão, e sem ela não há
    como encolher — a sleeve fica dormente em vez de chutar).
    """
    if janela < 1:
        raise ValueError("janela deve ser >= 1 dia útil")
    assets = list(retornos.columns)
    idx = retornos.index
    base = retornos[idx < ate_data].to_numpy(dtype=float).mean(axis=0)
    blocos = []
    for data_evento, direcao in eventos:
        if direcao == 0:
            continue  # surpresa exatamente zero não informa direção
        bloco = retornos.iloc[idx.searchsorted(data_evento, side="right"):][:janela]
        if len(bloco) < janela or bloco.index[-1] >= ate_data:
            continue  # janela incompleta ou ainda em curso -> fora do μ
        excesso = bloco.to_numpy(dtype=float).mean(axis=0) - base
        blocos.append(float(np.sign(direcao)) * excesso)
    if len(blocos) < 2:
        return None, len(blocos)
    blocos = np.asarray(blocos)
    media = blocos.mean(axis=0)
    se2 = blocos.var(axis=0, ddof=1) / len(blocos)
    prior2 = tau * np.diag(np.asarray(sigma, dtype=float))
    mu = np.zeros(len(assets))
    for ativo in ativos_livro:
        i = assets.index(ativo)
        mu[i] = media[i] * prior2[i] / (prior2[i] + se2[i]) if se2[i] > 0 else media[i]
    return mu, len(blocos)


def build_overlay(assets, familia, dias_desde_evento, direcao, mu, sigma, delta,
                  janela, n_eventos_mu=None):
    """Tilt da sleeve para UM dia (contrato de chamada diária).

      assets            : universo na ordem do dataset do Paulo.
      familia           : rótulo do anúncio ("fomc", "cpi") — só diagnóstico.
      dias_desde_evento : dias ÚTEIS desde o anúncio. A posição abre no CLOSE
                          de D, então o tilt vale a partir do dia 1. None =
                          sem evento no histórico -> dormente.
      direcao           : sinal da surpresa realizada. None/0 -> dormente.
      mu                : (n,) de `estimate_drift_mu`. None -> dormente (ainda
                          não há evento fechado para estimar).
      sigma             : (n, n) Σ amostral do dia — a MESMA que o BL usa.
      delta             : aversão a risco (D7: 3,0, observável).
      janela            : dias úteis que a sleeve fica ligada.

    Retorna `OverlayResult | None`.
    """
    if dias_desde_evento is None or direcao is None or mu is None:
        return None
    if delta <= 0:
        raise ValueError("delta deve ser positivo")
    if janela < 1:
        raise ValueError("janela deve ser >= 1 dia útil")
    direcao = float(np.sign(direcao))
    if direcao == 0.0 or not 1 <= dias_desde_evento <= janela:
        return None  # sem direção ou fora da janela -> dormente

    mu = np.asarray(mu, dtype=float)
    if mu.shape != (len(assets),):
        raise ValueError(f"mu deve ter shape ({len(assets)},), recebeu {mu.shape}")
    dw = optimal_weights(direcao * mu, np.asarray(sigma, dtype=float), delta)
    return OverlayResult(dw=dw, diagnostics={
        "tatica": f"drift_{familia}",
        "familia": familia,
        "direcao": direcao,
        "dias_desde_evento": dias_desde_evento,
        "janela": janela,
        "n_eventos_mu": n_eventos_mu,
        # Σ|dw| da sleeve sozinha: é ele que o teto do backtest vai disputar
        # com o tilt das views. Sai daqui para a atribuição não ter de subtrair.
        "soma_abs_dw": float(np.abs(dw).sum()),
        # O dw PEDIDO (antes do teto), para a atribuição separar "a sleeve perde
        # dinheiro" de "a sleeve rouba o teto das views" — no `r_tilt` do
        # backtest as duas coisas chegam somadas.
        "dw": dw,
    })
