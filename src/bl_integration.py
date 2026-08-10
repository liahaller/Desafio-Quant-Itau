"""Integração final: ViewResults -> P/Q empilhados -> pesos BL. Módulo do Felipe.

O elo entre as views (view_*.py), o Ω reativo (Lia) e o otimizador
(`bl_optimizer.py`). Duas funções puras:

  - stack_views  : filtra as views desativadas (None) e empilha as ativas
                   em P (k, n) e Q (k,), preservando a lista de
                   diagnostics NA MESMA ORDEM — é ela que a Lia usa para
                   montar o Ω (k, k) alinhado.
  - bl_weights_from_views : ponta a ponta de um rebalanceamento:
                   prior de equilíbrio -> posterior com as views ativas ->
                   pesos com Σ AMOSTRAL e sem restrições (decisão 8).
                   Sem nenhuma view ativa, devolve exatamente w_mkt
                   (caso neutro da decisão 8 — o BL fica no prior).

Quais views entram na lista é decisão de quem chama (o backtest): as
estruturais 2.2/2.3/2.4/3.1 são as decididas; B/C/E/G são CANDIDATAS —
entrada na carteira pendente de reunião. τ e δ vêm de decisão registrada.

⚠️ Pendência transversal ainda aberta (especs 2.4/3.1/C/E/G): o Q das
views poly-defasadas é retorno ACUMULADO em k dias (`horizonte_q_dias`
nos diagnostics) e Σ/π são diários — a reconciliação de horizonte precisa
fechar antes do backtest misturar essas views com as diárias.
"""

import numpy as np

from bl_optimizer import bl_posterior, implied_equilibrium_returns, optimal_weights


def stack_views(view_results, n_assets):
    """Empilha os ViewResult ativos em (P, Q, diagnostics).

    view_results : lista de ViewResult | None (None = view desativada —
                   simplesmente não entra, não é falha).
    n_assets     : nº de ativos do universo (valida o alinhamento de cada P).

    Retorna (P (k, n), Q (k,), diagnostics list) com k = nº de views
    ativas, na ordem da lista de entrada; ou (None, None, []) se nenhuma
    view está ativa. O Ω da Lia deve ser (k, k) nesta MESMA ordem.

    Rejeita views com `horizonte_q_dias` diferentes entre si (decisão 4.1).
    O que a checagem NÃO cobre, e segue pendente: mesmo com todas as views
    no mesmo horizonte, esse horizonte precisa bater com o de Σ e π (hoje
    diários) — só a escolha do horizonte-alvo fecha isso.
    """
    active = [r for r in view_results if r is not None]
    if not active:
        return None, None, []
    # DECISAO-4.1: empilhar Q de horizontes diferentes é somar km/h com km —
    # não dá erro, só devolve peso errado. Enquanto a reconciliação não fecha,
    # a mistura FALHA ALTO em vez de passar silenciosa.
    horizontes = {r.diagnostics.get("horizonte_q_dias", "não declarado") for r in active}
    if len(horizontes) > 1:
        raise ValueError(
            f"views ativas com horizontes de Q diferentes: {sorted(map(str, horizontes))} — "
            "TODO(DECISAO-4.1): a reconciliação de horizonte precisa fechar antes de "
            "empilhar views defasadas (Q acumulado em k dias) com views de evento (1 dia)"
        )
    for r in active:
        if np.asarray(r.P).shape != (n_assets,):
            raise ValueError(
                f"P da view {r.diagnostics.get('view', '?')} não alinha com o universo: "
                f"{np.asarray(r.P).shape} vs ({n_assets},)"
            )
    P = np.vstack([np.asarray(r.P, dtype=float) for r in active])
    Q = np.array([r.Q for r in active], dtype=float)
    return P, Q, [r.diagnostics for r in active]


def _checa_chaves(d, nomes, rotulo):
    """Casamento EXATO de chaves — sobra e falta são erro, não default."""
    faltando, sobrando = sorted(set(nomes) - set(d)), sorted(set(d) - set(nomes))
    if faltando or sobrando:
        raise ValueError(
            f"`{rotulo}` não casa com as views ativas — faltando: {faltando}; "
            f"sobrando: {sobrando}; ativas: {nomes}")


def aplicar_veto(view_results, ativa, incerteza=None):
    """Aplica o `ativa` do Ω da Lia: view inativa vira None.

    Veto é view que SAI de P e Q, não Ω gigante (decisão dela, item 4c da
    resposta de 2026-08-07): é o limite exato de Ω → ∞, sem número mágico e
    sem resíduo da view vetada empurrando peso.

    `ativa = False` tem DOIS motivos desde a resposta dela de 2026-08-10
    (item 3b): veto de liquidez (volume zero no slot) e ausência de leitura
    mensurável (nenhum par de slots adjacentes completo na janela). Aqui o
    tratamento é o MESMO de propósito — nos dois casos não há medição em que
    apoiar peso, e o limite Ω → ∞ é a resposta certa para ambos. O motivo não
    entra na assinatura: ele é log do lado dela, não regra deste lado.
    Medido nas 601 decisões da 2.2: 37 por volume, 21 por ausência, 543 ativas.

    `ativa` e `incerteza` são DICTS chaveados pelo identificador da view —
    exatamente a string de `diagnostics["view"]` (`"2.2_inflacao"`,
    `"2.3_fed"`, ...), não o apelido curto. Posicional foi removido de
    propósito (pedido dela de 2026-08-07): os vetores vinham na ordem das
    views ATIVAS enquanto `view_results` tem intercalados os None das views
    que já nasceram desativadas pela cascata, e um deslocamento de índice não
    levanta exceção — veta a view errada, o backtest roda igual e o número sai
    diferente sem avisar. Com chave por nome, o mesmo erro vira ValueError.

    A lista de chaves válidas é DERIVADA de `view_results` a cada chamada, não
    de constante escrita à mão (pedido dela de 2026-08-07): o nome vive só onde
    a view o emite, então a validação cobre todos os lugares em que ele existe.

    Devolve `(view_results, incerteza)` já alinhados entre si: a lista com os
    vetados virados None, e o `incerteza` como VETOR na ordem de `stack_views`,
    reduzido aos sobreviventes, pronto para `omega_fallback`.
    """
    nomes = [r.diagnostics["view"] for r in view_results if r is not None]
    if len(set(nomes)) != len(nomes):
        raise ValueError(f"views ativas com nome repetido — a chave não identifica: {nomes}")
    _checa_chaves(ativa, nomes, "ativa")
    if incerteza is not None:
        _checa_chaves(incerteza, nomes, "incerteza")

    saida, sobreviventes = [], []
    for r in view_results:
        if r is None:
            saida.append(None)  # já desativada pela cascata: não aparece nos dicts
            continue
        nome = r.diagnostics["view"]
        saida.append(r if ativa[nome] else None)
        if ativa[nome] and incerteza is not None:
            sobreviventes.append(incerteza[nome])
    return saida, (None if incerteza is None else np.asarray(sobreviventes, dtype=float))


def bl_weights_from_views(sigma, w_mkt, tau, delta, view_results, omega=None):
    """Pesos de um rebalanceamento, ponta a ponta.

    sigma, w_mkt : covariância amostral e pesos de mercado (pipeline do Paulo).
    tau, delta   : parâmetros do BL — de decisão registrada, nunca default.
    view_results : lista de ViewResult | None (saída dos build_view).
    omega        : (k, k) do Ω reativo da Lia, alinhado às views ATIVAS na
                   ordem de stack_views; obrigatório se houver view ativa.

    Retorna (w, info) — w (n,) pesos irrestritos com Σ amostral (decisão
    8); info = dict com P/Q/diagnostics empilhados (auditoria/relatório).
    Sem view ativa: w = w_mkt exato (caso neutro da decisão 8).
    """
    sigma = np.asarray(sigma, dtype=float)
    w_mkt = np.asarray(w_mkt, dtype=float)
    P, Q, diagnostics = stack_views(view_results, n_assets=w_mkt.shape[0])

    pi_prior = implied_equilibrium_returns(sigma, w_mkt, delta)
    if P is None:
        mu = pi_prior  # BL no prior -> optimal_weights devolve w_mkt exato
    else:
        if omega is None:
            raise ValueError("omega (Ω reativo da Lia) é obrigatório quando há view ativa")
        mu, _ = bl_posterior(pi_prior, sigma, tau, P, Q, np.asarray(omega, dtype=float))
    w = optimal_weights(mu, sigma, delta)  # Σ AMOSTRAL, irrestrito (decisão 8)
    return w, {"P": P, "Q": Q, "diagnostics": diagnostics, "pi_prior": pi_prior}
