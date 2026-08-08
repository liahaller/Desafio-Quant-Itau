"""View CPI transversal — a divergência da 2.2 expressa na seção cruzada. Módulo do Felipe.

**Sem número de decisão, de propósito.** View nova é decisão metodológica do
grupo (CLAUDE.md §1, categoria 3): registrada como candidata na seção 15 de
`Decisoes_pendentes.md`. O número sai quando o grupo numerar, não daqui.

Composição de duas peças que já existem e já foram medidas — nenhum dado novo:

    divergência = a MESMA da view 2.2 (E_poly[CPI] anualizado − breakeven 10a,
                  demeanada por janela expansiva — DECISAO-7.4)
    β_i         = ∂r_i/∂breakeven — regressão do retorno diário do ativo contra
                  o Δ do T10YIE; é a `market_inputs.breakeven_duration` da 2.2
                  generalizada do PAR para os N ativos
    P[i]        = 2·(β_i − β_SPY)/Σ_j|β_j − β_SPY|      (Σ|P| = 2, P[SPY] = 0)
    Q           = (Σ_i P[i]·β_i) × divergência_líquida / dias_até_divulgação

A 2.2 responde "o mercado de CPI diverge do título indexado" com UM par casado
em duration (TIP − TLT). Esta responde a MESMA pergunta na seção cruzada: se o
breakeven vai andar, quem anda junto sai medido em cada ativo, não postulado.
A regra do horizonte é a da 2.2 (DECISAO-7.2: o repricing se distribui até a
divulgação, logo o Q é de UM dia e aperta conforme a data chega).

⚠️ SINAL COMPARTILHADO COM A 2.2 — é a decisão que o grupo tem de tomar antes de
esta view entrar em produção. As duas leem a MESMA divergência; empilhar as duas
conta a mesma informação duas vezes no BL. Foi um dos três motivos que tiraram a
view B (seção 11: "duplica a 2.3 — β e P são os mesmos por desenho, muda só a
surpresa"). Aqui o P é DIFERENTE (par casado em duration vs. seção cruzada dos
9), então não é o mesmo caso da B — mas o Q vem da mesma fonte, e isso é
correlação de view que o Ω tem de enxergar. As três saídas possíveis (só a 2.2 /
só esta / as duas com Ω que reconheça a correlação) são do grupo. Enquanto não
fechar, o backtest NÃO empilha as duas.

🛑 **ESTA VIEW REPROVOU NO TESTE DE SINAL (2026-08-08). NÃO LIGAR.** O módulo fica
no repositório porque a medição é o resultado, e ela é insumo de relatório — não
porque a view esteja pronta. Medido em 276 pregões (fev/2025 a jul/2026), com β
expansivo e divergência de média expansiva (sem lookahead):

| o que a view supõe | medido |
|---|---|
| a divergência move o breakeven até a divulgação | b +0,0039, **t +2,11** ✅ |
| o coef. PREDITIVO de cada ativo acompanha o β contemporâneo | corr = **+0,06** 🛑 |
| a carteira P rende na direção do Q (horizonte da divulgação) | b −0,048, **t −3,02**, acerto de sinal **35%** 🛑 |

**O primeiro elo existe e o segundo não.** O breakeven de fato anda na direção do
poly (isto confirma a medição da 2.2 e a lógica da DECISAO-7.2), mas o β diário
ao Δbreakeven **não se transporta para retorno futuro**: ele é dominado pelo canal
risk-on, e condicionar no sinal de divergência de inflação seleciona outro regime.
Usar esse β como mapa de transmissão é o erro de desenho, e ele não é consertável
mexendo em parâmetro.

**Não inverter.** O sinal contrário é significante (t −3,02 vira +3,02 ao inverter)
e a tentação é óbvia — mas há precedente fechado contra isso na D2b, que recusou
redesenhar a view 3.1 na direção que o dado pedia: sinal contrário à própria tese,
amostra curta, um ano só. Inverter aqui é ajustar sinal à amostra, não achar
mecanismo.

**O que este teste é, e o que ele NÃO é — controle rodado nas views incumbentes:**

| view | t (1 dia) | t (horizonte) | acerto de sinal |
|---|---|---|---|
| 2.2 (par TIP−TLT, entrega) | — | **+0,44** | 57% |
| **2.3 (entrega, é ela que carrega o backtest)** | **+0,26** | **+0,26** | 51% / 56% |
| transversal (esta) | −1,21 | **−3,02** | 35% |

**Nenhuma view do v1 passa neste teste** — a 2.3, que leva o excesso de −0,94 pp
para +2,68 pp no backtest, dá t +0,26. Logo o teste **não é certificado de
utilidade**: ele não mede o que faz uma view render dentro do BL, onde o Q
interage com Σ, w_mkt e o teto do tilt. O que ele mede bem é **sinal invertido** —
e é só nisso que a transversal se separa das outras duas: as incumbentes são
indistinguíveis de zero, esta é significativamente **ao contrário**. A
recomendação de não ligar se apoia nessa distinção, não em ela ter ficado abaixo
de uma régua que as outras cumprem.

⚠️ **MEDIDO EM 2026-08-08, e quem for ler o P precisa saber antes: esta view fica
VENDIDA em TIP** (P[TIP] = −0,29 na amostra completa; −0,25 de 2016 em diante),
enquanto a 2.2 fica comprada. Não é bug — é a mesma coisa que
`Dump/analises/Convergencia_2_2.md` já tinha achado por outro caminho: o TIP
responde muito mais ao juro de 10 anos (β +1,6 contra +10,7 do SPY) do que ao
componente de inflação, então RELATIVO AO MERCADO ele é um veículo ruim de
breakeven. O β diário é dominado pelo canal risk-on (XLE +20,4, XLF +15,2, TLT
−11,2), e o P que sai é "cíclicos e energia contra duração", não "indexado contra
nominal". As duas views tomam posições OPOSTAS no mesmo ativo a partir do mesmo
sinal — o que reforça que não são duplicatas, e reforça igualmente que empilhar
as duas sem Ω que enxergue isso é decisão do grupo, não default.

**Por que o β sai do dado diário e não dos dias de divulgação:** o canal desta
view é "o breakeven anda", e a sensibilidade a esse movimento é a mesma em dia de
anúncio ou fora dele — é exatamente o que a 2.2 já faz (mesma regressão, mesmo
instrumento, todos os pregões). Estimar só nos dias de divulgação daria **15
eventos** (o `cpi_release_dates.csv` do Paulo começa em jan/2025, e as datas vêm
das regras dos mercados do Polymarket, não de calendário oficial) contra os
milhares de pregões do T10YIE — e mediria outra coisa: a reação AO ANÚNCIO, não a
sensibilidade ao breakeven. Um calendário oficial de CPI está pedido ao Paulo
(`Dump/trocas/PEDIDO_G10_Paulo.md`, item G10c) e destravaria a
variante event-study; não é pré-requisito desta.

Unidades: β em retorno por unidade de breakeven (fração/fração, ex.: 0,8 = +0,8%
de retorno por +1 pp de breakeven — cuidado, aqui as duas pontas são FRAÇÃO);
divergência em fração decimal anual (a mesma da 2.2); Q em fração decimal, com
horizonte de 1 dia (`horizonte_q_dias`, decisão 4.1).
"""

import numpy as np
import pandas as pd

# Mesma OLS demeanada de uma matriz de retornos contra um regressor — importada
# em vez de recopiada. O nome mora na 2.3 porque foi lá que nasceu (surpresa em
# bps); movê-la para `views_common.py` é arrumação de outra sessão.
from view_2_3_fed import estimate_betas
from views_common import P_from_betas, ViewResult

# Centro da linha P (excesso sobre o mercado, mesma convenção da 2.3) —
# parametrizado só para não hardcodar ticker na lógica; o default É a decisão.
MARKET_ASSET = "SPY"

# Piso amostral da regressão do β, herdado de `market_inputs.breakeven_duration`
# (mesma regressão, mesmo instrumento) — não é threshold novo.
MINIMO_PREGOES = 60


def estimate_betas_breakeven(returns, breakeven_changes, assets=None):
    """β_i = ∂r_i/∂breakeven de cada ativo, por OLS com intercepto.

    A mesma regressão de `market_inputs.breakeven_duration` (view 2.2), com duas
    diferenças: roda nos N ativos de uma vez e devolve o VETOR, em vez de rodar
    no retorno do par já montado. Sem isso o P desta view teria de ser postulado.

    returns          : DataFrame (T, n) de retornos diários, indexado por data.
    breakeven_changes: Series do Δ do breakeven na MESMA unidade da divergência
                       (fração decimal), alinhada por data.
    assets           : ordem do universo (default: as colunas de `returns`).

    Alinha por data e descarta linha incompleta — a janela e o corte em t−1 do
    rebalanceamento (sem lookahead) são responsabilidade do chamador, como na
    2.3. Devolve β (n,) na ordem de `assets`.
    """
    R = pd.DataFrame(returns)
    if assets is not None:
        R = R[list(assets)]
    par = pd.concat([R, pd.Series(breakeven_changes).rename("__dbe")], axis=1).dropna()
    if len(par) < MINIMO_PREGOES:
        raise ValueError(
            f"amostra curta para os β do breakeven: {len(par)} pregões "
            f"(mínimo {MINIMO_PREGOES}, o mesmo de `breakeven_duration`)")
    return estimate_betas(par[R.columns].to_numpy(dtype=float),
                          par["__dbe"].to_numpy(dtype=float))


def build_view(assets, betas, divergencia_liquida, dias_ate_divulgacao,
               soma_faixas=float("nan"), market_asset=MARKET_ASSET):
    """Monta a view CPI transversal para uma data de rebalanceamento.

    Parâmetros:
      assets              : list[str] — universo na ordem do dataset do Paulo.
      betas               : (n,) de `estimate_betas_breakeven`.
      divergencia_liquida : float — divergência da 2.2 JÁ demeanada (é o
                            `diagnostics["divergencia_liquida"]` dela), ou None
                            se não há mercado de CPI na data.
      dias_ate_divulgacao : int ≥ 1 — pregões até a divulgação (DECISAO-7.2).
      soma_faixas         : soma CRUA das faixas da PMF que gerou a divergência,
                            repassada ao Ω da Lia. Quem tem a série é o chamador
                            (mesma razão do bloco de qualidade do montador do
                            backtest): a view recebe snapshot.

    Retorna ViewResult (P, Q, diagnostics) ou None.

    **Não há cascata própria**: a degradação PMF → binário → desativada acontece
    UMA vez, na 2.2, e esta view herda o resultado. `divergencia_liquida=None`
    significa "a 2.2 já caiu pela cascata" — e é assim de propósito, para não
    existirem duas leituras do mesmo mercado que possam divergir em silêncio.
    """
    if divergencia_liquida is None:
        return None
    if dias_ate_divulgacao < 1:
        raise ValueError(
            f"dias_ate_divulgacao deve ser >= 1: {dias_ate_divulgacao} — o "
            "horizonte da view é o calendário de divulgação do CPI (DECISAO-7.2)")
    P = P_from_betas(betas, list(assets), market_asset)
    betas = np.asarray(betas, dtype=float)
    Q = float((P @ betas) * divergencia_liquida / dias_ate_divulgacao)
    return ViewResult(P=P, Q=Q, diagnostics={
        "view": "cpi_transversal",
        "caminho": "divergencia_2_2",   # o caminho da cascata é o que a 2.2 rodou
        "horizonte_q_dias": 1,          # DECISAO-7.2 + H = 1 dia (igual à 2.2)
        "divergencia_liquida": float(divergencia_liquida),
        "dias_ate_divulgacao": int(dias_ate_divulgacao),
        "dias_ate_evento": float(dias_ate_divulgacao),  # nome do contrato do Ω
        "soma_faixas": float(soma_faixas),
        "sum_P_beta": float(P @ betas),  # ∝ dispersão dos βs em torno do mercado
    })
