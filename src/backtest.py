"""Loop de backtest / rebalanceamento (I5) — a entrega final. Módulo do Felipe.

Anda nas datas, monta as views ativas do dia, chama `bl_weights_from_views`,
soma a camada tática, cobra o custo e devolve a série de retorno.

**Motor puro, sem plumbing de dado.** Quem sabe ler parquet, FRED e PMF é o
chamador: ele passa `montar_dia(data) -> (sigma, view_results, overlay_results)`
e é DELE a responsabilidade de só olhar dado anterior a `data` (o lookahead não
tem como ser checado aqui — as views recebem números, não séries). O motor cuida
do que é comum a qualquer configuração: composição, custo e contabilidade.

Custo (decisão 8, com a pesquisa que a fechou):

  - **`custo_bps` por lado sobre o giro**, e o giro é medido contra o peso
    DERIVADO — não contra o alvo de ontem. Um peso alvo de 30% que virou 31%
    sozinho, porque o ativo subiu, só precisa de 1 ponto de negociação para
    voltar a 30%, não de 30. Cobrar sobre o alvo anterior inventaria giro que
    ninguém executou.
  - **carrego declarado**: financiamento da alavancagem (Σw acima de 1) e
    aluguel das pontas vendidas. Hoje os dois são 0,0 em `config` — é cenário
    DECLARADO, não omissão: não há taxa publicada para estes 9 tickers. Ficam
    na conta para que ligar um número futuro seja trocar a constante.

Duas checagens que a pesquisa do D8 tornou obrigatórias, e por isso vivem aqui
em vez de virarem análise avulsa:

  - **giro diário médio** sai na mesma tabela do resultado (`giro`);
  - **`reversal_share`** decompõe quanto do giro é posição desfeita em 1–2
    pregões. É o mecanismo que destruiu a estratégia GTAA diária citada na
    pesquisa: o custo não vem de negociar muito, vem de negociar contra si
    mesmo. Giro alto com reversão baixa é reposicionamento; giro alto com
    reversão alta é ruído sendo pago a 2 bps a volta.

O D1 (H = 1 dia) fica sob revisão CONDICIONAL a esses dois números — e a saída
prevista, se eles forem ruins, é banda de não-negociação, não abandonar o H.
"""

from typing import NamedTuple

import numpy as np
import pandas as pd

from bl_integration import bl_weights_from_views, stack_views
from config import (ALUGUEL_BPS_ANO, CUSTO_BPS_POR_LADO, DELTA,
                    FINANCIAMENTO_SPREAD_BPS_ANO, PREGOES_POR_ANO, TAU)
from market_inputs import omega_fallback
from taticas_common import apply_overlays

BPS = 1e-4


class BacktestResult(NamedTuple):
    """diario  : DataFrame (datas × métricas) — retorno, custo, giro, contagens.
    pesos     : DataFrame (datas × ativos) — o peso ALVO carregado em cada dia.
    trades    : DataFrame (datas × ativos) — Δw executado (alvo − derivado).
    diagnostics : dict data -> {'views': [...], 'taticas': [...]} para auditoria.
    """
    diario: pd.DataFrame
    pesos: pd.DataFrame
    trades: pd.DataFrame
    diagnostics: dict


def derived_weights(w, retornos_dia):
    """Peso DERIVADO: no que o peso alvo de hoje se transformou depois do
    retorno de hoje, sem ninguém negociar.

        w_i(1 + r_i) / (1 + w·r)

    O denominador é o crescimento do patrimônio, e a ponta de caixa
    (1 − Σw) rende zero — premissa declarada junto com o financiamento.
    """
    w = np.asarray(w, dtype=float)
    r = np.asarray(retornos_dia, dtype=float)
    crescimento = 1.0 + float(w @ r)
    if crescimento <= 0.0:
        raise ValueError(
            f"patrimônio zerado ou negativo no dia (1 + w·r = {crescimento:.4f}) — "
            "com pesos irrestritos isso é ruína, não um retorno a compor")
    return w * (1.0 + r) / crescimento


def transaction_cost(w_alvo, w_derivado, custo_bps=CUSTO_BPS_POR_LADO):
    """(custo, giro) de ir do peso derivado ao peso alvo.

    giro  = Σ|Δw| (soma dos dois lados, comprado e vendido)
    custo = custo_bps × giro, em fração do patrimônio

    Teste que define a unidade (obrigatório, D8): ir de w = 0 a w = 1 num
    ativo dá giro 1 e custo exatamente `custo_bps` — um lado, uma vez.
    """
    if custo_bps < 0:
        raise ValueError("custo_bps não pode ser negativo")
    delta = np.asarray(w_alvo, dtype=float) - np.asarray(w_derivado, dtype=float)
    giro = float(np.abs(delta).sum())
    return custo_bps * BPS * giro, giro


def carry_cost(w, financiamento_bps_ano=FINANCIAMENTO_SPREAD_BPS_ANO,
               aluguel_bps_ano=ALUGUEL_BPS_ANO, pregoes_por_ano=PREGOES_POR_ANO):
    """Carrego diário das parcelas que existem porque os pesos são irrestritos
    (decisão 8): financiamento sobre a alavancagem acima de 1, aluguel sobre o
    valor vendido. Ambos zerados em `config` — cenário declarado.
    """
    w = np.asarray(w, dtype=float)
    alavancagem = max(float(w.sum()) - 1.0, 0.0)
    vendido = float(-w[w < 0].sum())
    return (financiamento_bps_ano * BPS * alavancagem
            + aluguel_bps_ano * BPS * vendido) / pregoes_por_ano


def cap_leverage(w, teto=None, w_ref=None):
    """Normaliza a carteira quando Σ|w| passa do `teto` (None = sem teto).

    Decidido em sessão (Felipe, 2026-08-05) porque a D8 previu peso
    IRRESTRITO mas não previu RUÍNA: medido no dado real, o BL com Σ amostral
    e o Ω de fallback neutro põe Σ|w| em mediana 24 e máximo 264, e o
    patrimônio vira negativo dentro da amostra. A causa é estrutural, não
    numérica — o I3b casou a duration do par TIP/TLT justamente para cancelar
    o movimento de juros, e `w ∝ Δμ/(δσ²)` numa direção de variância pequena
    explode por construção.

    Escala TODAS as pontas pelo mesmo fator, o que preserva a direção da
    carteira e só corta o tamanho. O teto é parâmetro humano — varrer vários e
    reportar (como já se faz com γ e com o custo) é a leitura honesta.

    `w_ref` = carteira que o corte NÃO toca. None (padrão) corta a carteira
    inteira, inclusive a perna de mercado que vem do prior; `w_ref = w_mkt`
    corta só o TILT (`w − w_mkt`). São as duas metades da questão de desenho
    aberta na seção 10 do `Decisoes_pendentes.md` — medir as duas **não fecha a
    D12**: o nível do teto segue esperando o `c` da Lia.

    Cuidado de escala ao comparar: com `w_ref`, o teto limita `Σ|w − w_ref|` e
    não `Σ|w|`. Com w_mkt = 100% SPY, um teto t no tilt deixa Σ|w| chegar a
    1 + t. Por isso a tabela reporta a alavancagem MEDIDA em vez de supor que
    ela é o teto — as colunas não são comparáveis pelo rótulo.
    """
    w = np.asarray(w, dtype=float)
    if teto is None:
        return w
    if teto <= 0:
        raise ValueError("teto de alavancagem deve ser positivo")
    base = np.zeros_like(w) if w_ref is None else np.asarray(w_ref, dtype=float)
    tilt = w - base
    bruta = float(np.abs(tilt).sum())
    return w if bruta <= teto else base + tilt * (teto / bruta)


def reversal_share(trades, janela=2):
    """Fração do giro total que é DESFEITA nos `janela` pregões seguintes.

    Para cada ativo e cada dia, olha o Δw líquido dos próximos `janela` dias:
    a parte dele que vai na direção oposta cancela o trade de hoje. O que
    cancela conta como reversão; o resto é reposicionamento genuíno.

    Perto de 0 = a carteira anda para algum lado e fica. Perto de 1 = compra
    hoje o que vende depois de amanhã, e paga custo nas duas pontas — é o
    modo de falha que a pesquisa do D8 aponta como o que mata estratégia
    diária. Devolve NaN se não houve giro nenhum (não zero: zero afirmaria
    "não há reversão" sobre uma carteira que nunca negociou).
    """
    if janela < 1:
        raise ValueError("janela de reversão deve ser >= 1 pregão")
    trades = pd.DataFrame(trades)
    giro_total = float(trades.abs().to_numpy().sum())
    if giro_total == 0.0:
        return float("nan")
    futuro = sum(trades.shift(-k).fillna(0.0) for k in range(1, janela + 1))
    desfeito = np.minimum(trades.abs(), np.maximum(-np.sign(trades) * futuro, 0.0))
    return float(desfeito.to_numpy().sum() / giro_total)


def run_backtest(retornos, montar_dia, w_mkt, *, datas=None, tau=TAU, delta=DELTA,
                 custo_bps=CUSTO_BPS_POR_LADO, teto_alavancagem=None,
                 teto_no_tilt=False, incerteza=None, w_inicial=None):
    """Anda nas datas e devolve o BacktestResult.

    retornos   : DataFrame (datas × ativos) de retornos diários, colunas na
                 ordem do universo (`config.ASSETS`).
    montar_dia : callable(data) -> (sigma, view_results, overlay_results).
                 `sigma` (n, n); `view_results` lista de ViewResult|None
                 (None = view desativada, cascata); `overlay_results` lista de
                 OverlayResult|None (None = tática dormente). Sem view ativa a
                 carteira do dia é exatamente `w_mkt` (caso neutro da D8).
    w_mkt      : (n,) pesos de mercado — prior do BL e ponto de partida.
    datas      : subconjunto de `retornos.index` a percorrer; None = todas.
    teto_alavancagem : Σ|w| máximo carregado (None = irrestrito, a D8 literal).
                 O corte é aplicado DEPOIS da camada tática, sobre a carteira
                 que de fato vai a mercado — e portanto o giro e o custo são
                 medidos já no peso cortado.
    teto_no_tilt : False (padrão) = o teto corta a carteira inteira; True = corta
                 só o desvio em relação a `w_mkt`, deixando a perna de mercado
                 intacta. Muda o que o teto limita (`Σ|w − w_mkt|`, não `Σ|w|`)
                 — ver `cap_leverage`.
    incerteza  : ESCALAR aplicado a todas as views ativas do dia (None = 1,0, o
                 fallback neutro). É ferramenta de VARREDURA — serve para medir
                 a sensibilidade ao `c` antes de a régua da Lia existir, não
                 para cravar confiança. O vetor de verdade é por view e chega
                 pelo `aplicar_veto`, não por aqui. Convenção do `omega_fallback`:
                 maior = MENOS confiança, e o `c ∈ (0,1]` dela entra como 1/c.
    w_inicial  : peso já carregado antes da primeira data. None = zeros, ou
                 seja, a primeira montagem paga o custo de entrar na carteira.

    O retorno do dia D usa os pesos montados com dado ANTERIOR a D e os
    retornos DE D — o custo é cobrado nesse mesmo dia, no rebalanceamento que
    o produziu.
    """
    retornos = pd.DataFrame(retornos)
    ativos = list(retornos.columns)
    w_mkt = np.asarray(w_mkt, dtype=float)
    if w_mkt.shape != (len(ativos),):
        raise ValueError(f"w_mkt não alinha com o universo: {w_mkt.shape} vs ({len(ativos)},)")
    datas = pd.DatetimeIndex(retornos.index if datas is None else datas)
    faltando = datas.difference(retornos.index)
    if len(faltando):
        raise ValueError(f"datas fora da tabela de retornos: {list(faltando[:3])}")

    w_derivado = np.zeros(len(ativos)) if w_inicial is None else np.asarray(w_inicial, dtype=float)
    linhas, pesos, trades, diagnostics = [], {}, {}, {}

    for data in datas:
        sigma, view_results, overlay_results = montar_dia(data)
        sigma = np.asarray(sigma, dtype=float)

        # O Ω tem de ser montado com o MESMO P que o BL vai empilhar, então o
        # stack roda antes. `incerteza=None` = fallback He-Litterman, que é o
        # TETO de confiança (a régua da Lia só tira peso, nunca adiciona). É
        # aqui que o vetor dela entra, depois de passar por `aplicar_veto` —
        # e nada mais muda.
        P, _, _ = stack_views(view_results, n_assets=len(ativos))
        omega = None if P is None else omega_fallback(
            P, sigma, tau, None if incerteza is None else np.full(P.shape[0], incerteza))
        w_bl, info = bl_weights_from_views(sigma, w_mkt, tau, delta, view_results, omega)
        w_pedido, diag_taticas = apply_overlays(w_bl, overlay_results or ())
        w_alvo = cap_leverage(w_pedido, teto_alavancagem, w_mkt if teto_no_tilt else None)

        custo, giro = transaction_cost(w_alvo, w_derivado, custo_bps)
        carrego = carry_cost(w_alvo)
        r_ativos = retornos.loc[data].to_numpy(dtype=float)
        r_bruto = float(w_alvo @ r_ativos)
        # Atribuição do dia, exata por linearidade: r_bruto = mercado + tilt.
        # `r_tilt` carrega TUDO que não é o prior — o tilt da view, a tática e,
        # no teto de carteira, também o pedaço da perna de mercado que o corte
        # tirou. É essa terceira parcela que a comparação dos dois escopos isola.
        r_mercado = float(w_mkt @ r_ativos)

        linhas.append({
            "data": data,
            "r_bruto": r_bruto,
            "r_mercado": r_mercado,
            "r_tilt": r_bruto - r_mercado,
            "custo": custo,
            "carrego": carrego,
            "r_liquido": r_bruto - custo - carrego,
            "giro": giro,
            "alavancagem": float(np.abs(w_alvo).sum()),
            # Σ|w| PEDIDO pelo BL, antes do corte. Não depende do teto nem do
            # escopo dele (a montagem do dia não olha o peso de ontem), então
            # sai igual em qualquer rodada — é a régua para responder "com o `c`
            # da Lia, ainda sobra alavancagem a cortar?".
            "alavancagem_pedida": float(np.abs(w_pedido).sum()),
            # Retorno que a carteira não-cortada teria feito HOJE. Contrafactual
            # de 1 dia, não trajetória: <= -100% marca o dia em que o irrestrito
            # zera o patrimônio (a ruína que motivou o teto).
            "r_pedido": float(w_pedido @ r_ativos),
            "n_views": 0 if P is None else P.shape[0],
            "n_taticas": len(diag_taticas),
        })
        pesos[data] = w_alvo
        trades[data] = w_alvo - w_derivado
        diagnostics[data] = {"views": info["diagnostics"], "taticas": diag_taticas}
        w_derivado = derived_weights(w_alvo, r_ativos)

    diario = pd.DataFrame(linhas).set_index("data")
    quadro = lambda d: pd.DataFrame(d, index=ativos).T.rename_axis("data")  # noqa: E731
    return BacktestResult(diario, quadro(pesos), quadro(trades), diagnostics)


def summary(resultado, benchmark=None, pregoes_por_ano=PREGOES_POR_ANO):
    """Tabela de leitura do backtest, com o custo de BREAKEVEN em destaque.

    O custo de breakeven (D8) é a métrica do relatório: quantos bps por lado
    zerariam o retorno líquido. Comparar com os 2 bps premissados diz se a
    estratégia sobrevive a um custo realista sem precisar cravar o custo certo.

    `benchmark` : Series de retorno diário do comprar-e-segurar (com w_mkt =
    100% SPY, é o SPY) alinhada ao índice — entra para o excesso ser lido na
    mesma janela, nunca contra uma média de outro período.
    """
    diario = resultado.diario
    liquido, bruto = diario["r_liquido"], diario["r_bruto"]
    giro_total = float(diario["giro"].sum())
    linhas = {
        "pregões": float(len(diario)),
        "retorno acumulado bruto": float((1.0 + bruto).prod() - 1.0),
        "retorno acumulado líquido": float((1.0 + liquido).prod() - 1.0),
        "retorno médio diário líquido": float(liquido.mean()),
        "vol anualizada": float(liquido.std(ddof=1) * np.sqrt(pregoes_por_ano)),
        "sharpe anualizado (excesso zero)": (
            float(liquido.mean() / liquido.std(ddof=1) * np.sqrt(pregoes_por_ano))
            if liquido.std(ddof=1) > 0 else float("nan")),
        "giro diário médio": float(diario["giro"].mean()),
        "giro desfeito em 1–2 pregões": reversal_share(resultado.trades),
        "custo pago (fração do patrimônio)": float(diario["custo"].sum()),
        # bps que zeram o retorno: o bruto acumulado dividido pelo giro total.
        # Acima do premissado = folga; abaixo = a estratégia é do custo, não nossa.
        "custo de breakeven (bps por lado)": (
            float(bruto.sum() / giro_total / BPS) if giro_total > 0 else float("nan")),
        "alavancagem média (Σ|w|)": float(diario["alavancagem"].mean()),
        "views ativas por dia (média)": float(diario["n_views"].mean()),
        # Atribuição aditiva: a perna de mercado compõe (é uma carteira de
        # verdade), o tilt entra como SOMA das contribuições diárias — não é
        # uma carteira que se possa comprar, então compor não teria sentido.
        # Por isso as duas linhas não fecham exatamente com o acumulado.
        "perna de mercado (composta)": float((1.0 + diario["r_mercado"]).prod() - 1.0),
        "tilt (soma das contribuições diárias)": float(diario["r_tilt"].sum()),
    }
    if benchmark is not None:
        b = pd.Series(benchmark).reindex(diario.index)
        linhas["benchmark acumulado"] = float((1.0 + b).prod() - 1.0)
        linhas["excesso acumulado (líquido − benchmark)"] = (
            linhas["retorno acumulado líquido"] - linhas["benchmark acumulado"])
    return pd.Series(linhas)
