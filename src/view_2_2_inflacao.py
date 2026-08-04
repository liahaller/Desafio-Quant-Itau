"""View 2.2 — Inflação (par TIP - TLT). Módulo do Felipe.

Fechada em reunião 2026-07-09 (decisões 3/4 desta view); espec completa em
`Informações_uteis/views/view_2.2_inflacao.md`. Exceção à Família A: sem
regressão — beta = duration do breakeven de 10 anos (benchmark T10YIE do
FRED, acoplado à duration; alterar um exige alterar o outro).

    Q = duration * (E_poly[CPI] - breakeven_10a)
    P = +1 TIP / -1 TLT  (Sigma|P| = 2)

Cascata de degradação (item 0 da espec):
  1. PMF de buckets de CPI disponível -> E_poly = média da PMF.
  2. Só mercado binário -> normal deslocada com vol histórica do CPI:
     E_poly = média que faz P(CPI > threshold) = prob_poly.
  3. Nenhum mercado de CPI -> view desativada (retorna None).

Unidades: TODAS as grandezas de inflação (valores dos buckets, threshold,
breakeven, vol) em fração decimal (0.037 = 3.7%). Q sai em fração decimal,
consistente com os retornos do BL.

FREQUÊNCIA (corrigido em 2026-07-30, por instrução do Felipe em sessão):
a espec foi escrita supondo mercado de CPI **anual** (buckets 3,7% / 3,8% /
≤3,6%), mas o Paulo mediu (Nota A, 2026-07-27) que os mercados do Polymarket
são de variação **MENSAL** do CPI-U (0,0% a 0,5%). Comparar 0,3% mensal com
um breakeven de 10 anos de 2,3% produzia divergência negativa permanente de
~2 pp — a view ficaria comprada em TLT contra TIP para sempre, por unidade,
não por sinal. Por isso `cpi_frequencia` é argumento OBRIGATÓRIO: quem chama
declara a unidade do mercado, e a view anualiza antes de comparar. A
anualização entra nos VALORES DOS BUCKETS, não na média — anualizar depois
seria desigualdade de Jensen ((1+E[π])^12 != E[(1+π)^12]).

⚠️ O que a correção de unidade NÃO resolve (item de reunião, mesma família da
decisão 3.3 "prazos que não batem"): mesmo com as duas pontas anualizadas,
comparamos a expectativa de UM mês com a média implícita de DEZ ANOS, e
anualizar um mês multiplica o ruído por ~12 (0,1 pp mensal vira ~1,2 pp
anual). O sinal fica correto em unidade e nervoso em magnitude. Qualquer
amortecimento (escalar, suavizar, comparar com breakeven curto) é decisão do
grupo — não é assumido aqui.

Pré-processamento (decisão 9): a view normaliza as probs cruas e aplica a
correção de favorite-longshot (stub até a decisão 11a — a view FALHA ALTO
até lá; para testes sintéticos injeta-se `fl_correction` identidade). O
valor do bucket aberto (decisão 11b) é resolvido pelo CHAMADOR via
`poly_preprocessing.open_bucket_value` antes de montar `bucket_values`.
"""

import numpy as np
from scipy.stats import norm

from poly_preprocessing import favorite_longshot, normalize_probs, pmf_mean
from views_common import ViewResult

# Par da view (decisão 1 / espec da 2.2) — parametrizado só para não
# hardcodar ticker na lógica; o default É a decisão.
LONG_ASSET = "TIP"
SHORT_ASSET = "TLT"


def annualize_monthly(pi_mensal):
    """Variação mensal do CPI -> taxa anual equivalente: (1+π)^12 - 1.

    Composição, não multiplicação por 12: é a taxa que, repetida 12 meses,
    dá o mesmo acumulado. Aceita escalar ou array (os valores dos buckets).
    """
    return (1.0 + np.asarray(pi_mensal, dtype=float)) ** 12 - 1.0


def _to_anual(valores, cpi_frequencia):
    """Converte para base anual conforme a frequência declarada pelo chamador."""
    if cpi_frequencia == "mensal":
        return annualize_monthly(valores)
    if cpi_frequencia == "anual":
        return np.asarray(valores, dtype=float)
    raise ValueError(f"cpi_frequencia deve ser 'mensal' ou 'anual': {cpi_frequencia!r}")


def _pair_P(assets, long_asset, short_asset, duration_long, duration_short):
    """Linha P do par, CASADA EM DURATION e normalizada com Sigma|P| = 2.

    Medido em 2026-08-04 (`Dump/analises/Convergencia_2_2.md`): o par +1/-1
    ingênuo NÃO é aposta de inflação. TIP responde ao juro de 10 anos com
    duration empírica de ~5 anos e TLT com ~16 — a perna do TLT domina, e a
    oscilação de juros abafa o sinal. Na prática o par cru deu coeficiente
    NEGATIVO contra a divergência (-0,077), enquanto o breakeven, medido
    direto, deu +0,0063 com t +3,42. A tese estava certa e o instrumento
    errado.

    Casar duration = vender `d_long / d_short` de TLT por unidade de TIP, para
    que um deslocamento paralelo da curva se cancele e sobre o componente de
    inflação. As durations vêm MEDIDAS (`market_inputs.empirical_duration`),
    nunca de constante no código.
    """
    if duration_long <= 0 or duration_short <= 0:
        raise ValueError(
            f"durations devem ser positivas: {duration_long}, {duration_short}")
    hedge = duration_long / duration_short  # unidades de short por unidade de long
    escala = 2.0 / (1.0 + hedge)            # mantém Sigma|P| = 2
    P = np.zeros(len(assets))
    P[assets.index(long_asset)] = escala
    P[assets.index(short_asset)] = -escala * hedge
    return P


def expected_inflation_from_binary(prob_yes, prob_no, threshold, cpi_vol,
                                   fl_correction=favorite_longshot):
    """Fallback binário: normal deslocada com vol histórica do CPI.

    Encontra a média mu tal que P(CPI > threshold) = p_poly com
    CPI ~ N(mu, cpi_vol):  mu = threshold + cpi_vol * Phi^{-1}(p).
    """
    if cpi_vol <= 0:
        raise ValueError("cpi_vol deve ser positiva")
    p_yes = float(fl_correction(normalize_probs([prob_yes, prob_no]))[0])
    if not 0.0 < p_yes < 1.0:
        raise ValueError(f"prob corrigida fora de (0, 1): {p_yes}")
    return threshold + cpi_vol * norm.ppf(p_yes)


def build_view(assets, breakeven_10y, duration, *, cpi_frequencia,
               duration_long, duration_short,
               dias_ate_divulgacao, divergencia_media=0.0,
               bucket_probs=None, bucket_values=None,
               binary_prob=None, binary_threshold=None, cpi_vol=None,
               fl_correction=favorite_longshot,
               long_asset=LONG_ASSET, short_asset=SHORT_ASSET):
    """Monta a view 2.2 para uma data de rebalanceamento.

    Recebe só dados até a data (quem corta é o backtest — sem lookahead
    estrutural). Segue a cascata: PMF > binário > None (desativada).

    Parâmetros:
      assets           : list[str] — universo na ordem do dataset do Paulo.
      breakeven_10y    : float — T10YIE na data, fração decimal.
      duration         : float — duration do breakeven 10a (~8; valor vem
                         de decisão registrada, não default de código).
      cpi_frequencia   : 'mensal' ou 'anual' — unidade do mercado de CPI que
                         alimenta a view. OBRIGATÓRIO (ver docstring do
                         módulo): os mercados entregues são MENSAIS e o
                         breakeven é anual; sem declarar, a comparação sai
                         errada em ~2 pp sem dar erro.
      bucket_probs     : probs CRUAS dos buckets de CPI (ou None).
      bucket_values    : valor de cada bucket (aberto já resolvido — 11b),
                         na unidade declarada em `cpi_frequencia`.
      binary_prob      : tupla (p_sim, p_nao) CRUA do mercado binário (ou None).
      binary_threshold : threshold X do binário "CPI > X".
      cpi_vol          : vol histórica do CPI para o fallback.
      fl_correction    : correção de favorite-longshot (default: stub 11a).

    Retorna ViewResult (P, Q, diagnostics) ou None se não há mercado de CPI.
    """
    if bucket_probs is not None:
        # anualiza os VALORES antes da média (Jensen: (1+E[π])^12 != E[(1+π)^12])
        e_poly = pmf_mean(bucket_probs, _to_anual(bucket_values, cpi_frequencia),
                          fl_correction)
        e_poly_declarado = pmf_mean(bucket_probs, bucket_values, fl_correction)
        caminho = "pmf"
    elif binary_prob is not None:
        if binary_threshold is None or cpi_vol is None:
            raise ValueError("fallback binário exige binary_threshold e cpi_vol")
        # aqui a normal é montada na unidade declarada (threshold e vol vêm
        # nela) e a média sai depois — anualizar a média é aproximação, não
        # identidade, mas o caminho binário já é o degrau degradado da cascata.
        e_poly_declarado = expected_inflation_from_binary(
            binary_prob[0], binary_prob[1], binary_threshold, cpi_vol, fl_correction)
        e_poly = float(_to_anual(e_poly_declarado, cpi_frequencia))
        caminho = "binario"
    else:
        return None  # cascata item 0: sem mercado de CPI -> view desativada

    if dias_ate_divulgacao < 1:
        raise ValueError(
            f"dias_ate_divulgacao deve ser >= 1: {dias_ate_divulgacao} — o "
            "horizonte da view é o calendário de divulgação do CPI (decisão 7.2)")
    divergencia = e_poly - breakeven_10y
    # DECISAO-7.4: a divergência entra DEMEANADA. Medido: a média é +2,03 pp
    # com desvio de 2,26 pp — do tamanho de toda a variação do sinal. É o
    # descasamento estrutural entre inflação de 1 mês anualizada e breakeven de
    # 10 anos, não informação; sem removê-la a view fica comprada em inflação
    # por aritmética. `divergencia_media` vem de janela EXPANSIVA no chamador
    # (sem lookahead); 0.0 só para teste sintético.
    divergencia_liquida = divergencia - divergencia_media
    # DECISAO-7.2: o repricing se distribui até a divulgação, data em que o
    # mercado do poly resolve e a informação vira pública. Medido: o breakeven
    # anda na direção do poly até lá (+0,0063, t +3,42) e o coeficiente cai na
    # reta final, que é o que a regra prevê. Dividir pelos dias que faltam faz
    # o Q ser de UM dia — o H da decisão 1 — e a view apertar conforme a data
    # chega.
    Q = duration * divergencia_liquida / dias_ate_divulgacao
    P = _pair_P(list(assets), long_asset, short_asset, duration_long, duration_short)
    return ViewResult(P=P, Q=float(Q), diagnostics={
        "view": "2.2_inflacao",
        "caminho": caminho,
        "e_poly": e_poly,                      # base anual, comparável ao breakeven
        "e_poly_declarado": e_poly_declarado,  # como veio do mercado
        "cpi_frequencia": cpi_frequencia,
        "horizonte_q_dias": 1,                 # decisão 7.2 + H = 1 dia
        "breakeven_10y": breakeven_10y,
        "divergencia": divergencia,
        "divergencia_media": divergencia_media,
        "divergencia_liquida": divergencia_liquida,
        "dias_ate_divulgacao": dias_ate_divulgacao,
        "duration": duration,
        "hedge_duration": duration_long / duration_short,
    })
