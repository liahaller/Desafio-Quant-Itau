"""View de incerteza de anúncio (prêmio de risco de evento). Módulo do Felipe.

**Sem número de decisão, de propósito.** View nova é decisão metodológica do
grupo (CLAUDE.md §1, categoria 3): registrada como candidata na seção 15 de
`Decisoes_pendentes.md`. O número sai quando o grupo numerar, não daqui.

Âncora teórica: Savor & Wilson — o prêmio de anúncio é compensação por carregar
risco de EVENTO, logo só deveria existir quando o evento é de fato incerto.
Medido neste dado por `scripts/premio_condicional.py` (32 anúncios: 7 FOMC + 13
CPI + 12 payrolls; incerto − previsível = **+1,10 pp** no SPY, t de Welch
**+2,27**; +0,90 pp e t +2,34 tirando o extremo dos DOIS grupos).

    incerteza = entropia normalizada da PMF do Polymarket na véspera (0 a 1)
    β_prêmio  = ∂r_i/∂incerteza — OLS dos retornos de dia de anúncio contra a
                entropia
    P         = 2 no ativo de mercado, 0 no resto            (Σ|P| = 2)
    Q         = (Σ_i P[i]·β_i) × (entropia − média expansiva da família)

Três coisas que esta view é de propósito, e que a separam da tática 1.3 que foi
desligada na 12c:

1. **É view, não overlay — e é isso que resolve o impasse da 12c.** O overlay
   exigia um `orcamento` (fração do patrimônio) que não sai de teoria nenhuma, e
   a varredura mostrou Δ **monótono no orçamento**: sem ótimo interior, a grade
   não seleciona parâmetro, ela devolve a pergunta. Como view, quem dimensiona é
   o BL (τ, Ω, Σ) a partir de Q e da confiança — o parâmetro sem âncora deixa de
   existir. A premissa, que a 12c registrou como APROVADA ("a premissa passou; o
   dimensionamento é que não tem âncora"), é reaproveitada inteira.

2. **Sem threshold.** A medição partiu os anúncios pela MEDIANA da entropia de
   cada família; mediana é threshold, e threshold é parâmetro (CLAUDE.md §6).
   Aqui a incerteza entra CONTÍNUA: o corte some e nada é inventado.

   ⚠️ **A ESCALA da incerteza é decisão em aberto, e MEDE DIFERENTE** (medido em
   2026-08-08 nos 32 anúncios, β do SPY):

   | escala (nenhuma usa threshold) | β_SPY | t |
   |---|---|---|
   | entropia crua demeanada por família | +0,48 %/unidade | **+0,32** |
   | percentil da entropia dentro da família | +1,75 %/unidade | **+1,96** |

   A entropia CRUA linear **não sustenta a premissa**: o t cai de +2,27 (contraste
   de grupos, como a premissa foi medida) para +0,32. O percentil dentro da
   família é a versão contínua do MESMO contraste que a medição usou — a mediana
   dicotomizada é o percentil — e recupera o sinal sem cravar corte. Não é
   escolha desta função: `build_view` recebe o número já na escala que o chamador
   decidiu (`escala` vai aos diagnostics para o artefato não ficar ambíguo), e
   qual das duas entra é decisão do grupo, registrada na seção 15.

3. **A demeanagem é por família, e não é cosmética.** Medido (dossiê, "Limite de
   leitura"): a entropia não vive na mesma faixa em cada família — FOMC 0,08 a
   0,93; CPI 0,07 a 0,78; payrolls 0,68 a 0,96. Nível bruto não é comparável
   entre famílias; o desvio é. Mesma construção da DECISAO-7.4 (2.2) e da
   demeanagem da 2.3, pela mesma razão: o nível é do instrumento, o sinal é o
   desvio. `entropia_media` vem de janela EXPANSIVA no chamador (sem lookahead);
   0.0 só reproduz a fórmula crua para teste sintético.

⚠️ **PRIMEIRA VIEW DIRECIONAL DO PROJETO — decisão do grupo (seção 15).** Todas as
views estruturais são neutras em mercado por construção (`P_from_betas` crava
P[SPY] = 0 exato). O prêmio de Savor-Wilson é um prêmio de MERCADO: expressá-lo
com P[SPY] = 0 é exatamente o que impediu a view 3.1 de dizer o que ela tinha a
dizer (D2b: existe efeito direcional significante — SPY +0,59% em 10 pregões —
que a view não consegue expressar porque o P dela é neutro em mercado). Por isso
o P aqui é direcional. O que NÃO muda: a convenção Σ|P| = 2 (decisão 4) e a
identidade Q = P·E[r], que valem igual — a view continua dizendo "o retorno da
carteira P é Q". O que MUDA e é do grupo: com ΣP ≠ 0 a view mexe na exposição
direcional, e a obrigação 5a de `views_common.py` (centragem se troca em todas
as views juntas, nunca em uma) precisa ser lida antes de empilhar esta com as
neutras.

⚠️ **A ENTROPIA NÃO USA VALOR DE BALDE.** É invariante à renormalização e
independe do valor numérico das faixas — por isso funciona nos payrolls, cujos
arquivos do G9 trazem só preço e NENHUM rótulo de balde (é o que o
`Dump/trocas/PEDIDO_G10_Paulo.md` pede). Ela não depende das
decisões 1.2 (balde aberto) nem 6.1 (colapso da PMF) — foi por isso que a medição
de `premio_condicional.py` a escolheu, e a propriedade se herda aqui.

Unidades: entropia adimensional em [0, 1]; β em retorno por unidade de entropia
(fração/adimensional); Q em fração decimal, horizonte de 1 dia — o retorno
close-to-close do próprio dia do anúncio, que é o que a medição usou.
"""

import numpy as np
import pandas as pd

# Mesma OLS demeanada de uma matriz de retornos contra um regressor (ver nota
# gêmea em `view_cpi_transversal.py`).
from view_2_3_fed import estimate_betas
from views_common import ViewResult

# Ativo que carrega o prêmio de mercado de Savor-Wilson. Parametrizado só para
# não hardcodar ticker na lógica; o default É a decisão (mesmo ativo que a
# medição de `premio_condicional.py` usou).
MARKET_ASSET = "SPY"


def entropia_normalizada(probs):
    """Incerteza da PMF em [0, 1] — 0 = toda a massa num balde, 1 = uniforme.

    Renormaliza pela soma OBSERVADA (a PMF do poly não soma 1) e ignora baldes
    sem leitura. Menos de 2 baldes vivos -> NaN, nunca número inventado.

    É a mesma função que `scripts/premio_condicional.py` usou para medir a
    premissa — mora aqui agora porque virou matemática de view, e o script a
    importa daqui. Duplicá-la deixaria a medição e a view podendo divergir.

    Normalizada por log(nº de baldes VIVOS) de propósito: a grade do CPI varia de
    3 a 9 baldes e a dos payrolls de 5 a 9, então entropia bruta não é comparável
    entre meses. O preço é que o denominador muda com o nº de baldes com leitura
    — e é por isso que a demeanagem do `build_view` é POR FAMÍLIA.
    """
    p = np.asarray(pd.Series(probs).to_numpy(), dtype=float)
    p = p[np.isfinite(p) & (p > 0)]
    if len(p) < 2 or p.sum() <= 0:
        return float("nan")
    p = p / p.sum()
    return float(-(p * np.log(p)).sum() / np.log(len(p)))


def estimate_betas_incerteza(event_returns, entropias, assets=None):
    """β_i = ∂r_i/∂incerteza por OLS com intercepto, nos dias de ANÚNCIO.

    event_returns : (m, n) — retornos close-to-close dos n ativos nos m dias de
                    anúncio da janela decidida pelo chamador.
    entropias     : (m,) — entropia normalizada da PMF na véspera de cada um.

    O intercepto é o que separa esta view da tática incondicional: ele absorve o
    prêmio de anúncio MÉDIO, que `premissa_taticas.py` mediu e NÃO achou (FOMC
    +0,062% contra +0,060% dos demais dias). O que sobra no β é só a parte
    condicionada à incerteza — que é a tese de Savor-Wilson e a única que a
    medição sustenta.

    **Sem piso de eventos além do algébrico (2)**, por decisão 12b: piso é
    threshold, e o critério registrado lá para cravar um é a curva de
    estabilidade do β, não um número escolhido. O nº de eventos usado sai nos
    diagnostics do chamador, como na 2.3 (`n_eventos_beta`).
    """
    R = pd.DataFrame(event_returns)
    if assets is not None:
        R = R[list(assets)]
    par = pd.concat([R, pd.Series(entropias).rename("__h")], axis=1).dropna()
    return estimate_betas(par[R.columns].to_numpy(dtype=float),
                          par["__h"].to_numpy(dtype=float))


def directional_P(assets, market_asset=MARKET_ASSET):
    """Linha P direcional: Σ|P| = 2 concentrado no ativo de mercado.

    Não passa por `P_from_betas` de propósito — aquela crava P[market] = 0 exato
    (excesso sobre o mercado), que é o oposto do que esta view precisa dizer.
    A convenção Σ|P| = 2 (decisão 4) é mantida: com uma perna só, P[mercado] = 2
    e o Q correspondente é `P·E[r]` = 2·E[r_mercado] — a mesma identidade das
    outras views, sem exceção de escala escondida.
    """
    assets = list(assets)
    if market_asset not in assets:
        raise ValueError(f"ativo de mercado {market_asset!r} fora do universo: {assets}")
    P = np.zeros(len(assets))
    P[assets.index(market_asset)] = 2.0
    return P


def build_view(assets, betas, entropia, entropia_media=0.0,
               soma_faixas=float("nan"), familia=None, escala="entropia",
               market_asset=MARKET_ASSET):
    """Monta a view de incerteza para uma data de rebalanceamento.

    Parâmetros:
      assets         : list[str] — universo na ordem do dataset do Paulo.
      betas          : (n,) de `estimate_betas_incerteza`.
      entropia       : float — incerteza do evento de HOJE na escala declarada em
                       `escala`, ou None se o dia não é de anúncio. NaN (PMF
                       ilegível) cai pela cascata igual a None.
      entropia_media : centro EXPANSIVO da MESMA família e da MESMA escala (ver
                       item 3 do docstring do módulo). 0.0 só para teste
                       sintético; no percentil o centro é 0,5 por construção.
      soma_faixas    : soma CRUA das faixas, repassada ao Ω da Lia.
      familia        : 'fomc' | 'cpi' | 'payrolls' — vai só aos diagnostics, para
                       o Ω e o relatório saberem de qual demeanagem o número veio.
      escala         : 'entropia' | 'percentil' — qual das duas escalas do item 2
                       o chamador usou. Não muda a conta (é o mesmo desvio vezes
                       o mesmo β); vai aos diagnostics porque os dois números têm
                       a MESMA cara e significância medida muito diferente, e um
                       artefato que não diz qual rodou é irrecuperável depois.

    Retorna ViewResult (P, Q, diagnostics) ou None.

    **Cascata (item 0 do padrão das views):** dia sem anúncio ou PMF ilegível ->
    None (view desativada, não é falha). Não há degrau binário aqui: entropia de
    um mercado binário é a de uma Bernoulli, que existe e é legítima — quem
    decide se um binário conta como "evento incerto" é o chamador, ao montar a
    lista de anúncios.
    """
    if entropia is None or not np.isfinite(entropia):
        return None
    P = directional_P(assets, market_asset)
    betas = np.asarray(betas, dtype=float)
    incerteza_liquida = float(entropia) - float(entropia_media)
    Q = float((P @ betas) * incerteza_liquida)
    return ViewResult(P=P, Q=Q, diagnostics={
        "view": "incerteza_anuncio",
        "caminho": "pmf",               # a entropia só existe se houve PMF
        "horizonte_q_dias": 1,          # retorno close-to-close do dia do anúncio
        "familia": familia,
        "escala": escala,
        "entropia": float(entropia),
        "entropia_media": float(entropia_media),
        "incerteza_liquida": incerteza_liquida,
        "dias_ate_evento": 0.0,         # o evento é HOJE (contrato do Ω)
        "soma_faixas": float(soma_faixas),
        "sum_P_beta": float(P @ betas),
        "direcional": True,             # ΣP ≠ 0 — sinalizado, não escondido
    })
