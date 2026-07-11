"""Tática — Drift pós-FOMC (momentum monetário; dois livros: SPY e TLT).

Módulo do Felipe. STATUS: candidata da camada tática reformulada — código
pronto; ENTRADA, orçamentos e janelas finais pendentes de reunião. Espec
completa: `Informações_uteis/táticas/tatica_drift_pos_fomc.md`.
Âncoras: Neuhierl & Weber (monetary momentum — ações continuam na direção
da surpresa por ~15 dias úteis); Brooks, Katz & Lustig (bonds — drift de
~50 dias, mecanismo de fluxo lento).

    surpresa = Δtaxa_decidida − E[Δtaxa na véspera]   (bps; E do ZQ em D-1)
    direção  = −sign(surpresa)   dovish (surpresa < 0)  -> LONG SPY e TLT
                                 hawkish (surpresa > 0) -> SHORT SPY e TLT
    livro de ações: dw[SPY] = direção × orcamento_acoes,
                    dias úteis 1..janela_acoes após o FOMC
    livro de RF   : dw[TLT] = direção × orcamento_rf,
                    dias úteis 1..janela_rf, TRUNCADO no dia anterior ao
                    FOMC seguinte (evita carregar drift para dentro da
                    próxima reunião)

Tamanho binário por sinal no v1 (micro-surpresas tomam posição cheia —
sub-questão de calibração registrada para reunião); upgrade proporcional a
|surpresa| registrado na espec. Janelas: os valores da literatura (15 ações
/ 50 bonds) são defaults DE ESPEC pendentes de confirmação — entram como
argumento, nunca hardcoded. Só FOMC no v1 (sem âncora de drift pós-CPI).

Complementaridade (registro): a view 2.3 opera a divergência ANTES da
reunião e desliga na resolução; este drift abre no close do dia do anúncio
com a surpresa REALIZADA — sem sobreposição. Sub-questão de reunião: fonte
da expectativa da véspera (ZQ, leitura direta da âncora, vs E_poly).
"""

import numpy as np

from taticas_common import OverlayResult

SPY_ASSET = "SPY"
TLT_ASSET = "TLT"  # BKL é sobre Treasuries nominais; TIP rejeitado na espec


def build_overlay(assets, dias_desde_fomc, surpresa_bps,
                  orcamento_acoes, orcamento_rf, janela_acoes, janela_rf,
                  dias_ate_proximo_fomc=None,
                  spy_asset=SPY_ASSET, tlt_asset=TLT_ASSET):
    """Tilt da tática para UM dia (contrato de chamada diária).

    Parâmetros:
      assets               : universo na ordem do dataset do Paulo.
      dias_desde_fomc      : dias ÚTEIS desde o último anúncio (0 = dia do
                             anúncio — a posição abre no CLOSE de D, logo o
                             tilt vale a partir do dia 1). None = sem FOMC
                             no histórico -> dormente.
      surpresa_bps         : surpresa realizada do último FOMC, em bps
                             (Δtaxa_decidida − E_ZQ[Δtaxa] de D-1). None =
                             sem ZQ na véspera ou decisão não publicada ->
                             dormente (cascata; nunca bloqueia o BL).
      orcamento_acoes/_rf  : orçamento por livro (fração do patrimônio) —
                             parâmetros humanos de reunião (por livro ou
                             comum é sub-questão da reunião).
      janela_acoes/_rf     : janelas em dias úteis — literatura: 15 / 50;
                             confirmação de reunião pendente.
      dias_ate_proximo_fomc: dias úteis até o PRÓXIMO anúncio (se o
                             calendário já der); trunca o livro de RF no
                             dia anterior ao FOMC seguinte. None = sem
                             truncagem (fim de amostra).

    Retorna OverlayResult | None.
    """
    if dias_desde_fomc is None or surpresa_bps is None:
        return None  # cascata: sem evento ou sem surpresa utilizável
    if orcamento_acoes <= 0 or orcamento_rf <= 0:
        raise ValueError("orçamentos devem ser positivos (parâmetros de reunião)")
    if janela_acoes < 1 or janela_rf < 1:
        raise ValueError("janelas devem ser >= 1 dia útil")

    direcao = -float(np.sign(surpresa_bps))
    if direcao == 0.0:
        return None  # surpresa exatamente zero: âncora é sign-based, sem drift

    equity_on = 1 <= dias_desde_fomc <= janela_acoes
    bonds_on = (1 <= dias_desde_fomc <= janela_rf
                and (dias_ate_proximo_fomc is None or dias_ate_proximo_fomc >= 1))
    if not equity_on and not bonds_on:
        return None  # fora das janelas -> dormente

    assets = list(assets)
    dw = np.zeros(len(assets))
    if equity_on:
        dw[assets.index(spy_asset)] = direcao * orcamento_acoes
    if bonds_on:
        dw[assets.index(tlt_asset)] = direcao * orcamento_rf
    return OverlayResult(dw=dw, diagnostics={
        "tatica": "drift_pos_fomc",
        "surpresa_bps": float(surpresa_bps),
        "direcao": direcao,
        "dias_desde_fomc": dias_desde_fomc,
        "livro_acoes_ativo": equity_on,
        "livro_rf_ativo": bonds_on,
    })
