"""Ω reativo — a confiança que modula as views do Black-Litterman.

Régua de produção, fechada em 09/08/2026 pela calibração das views 2.3 (FOMC,
`rodar_calibracao.py`) e 2.2 (CPI, `rodar_calibracao_cpi.py`):

    c = ( (1 + var_media) · (1 + |soma_faixas − 1|) ) ** nivel

Cada defeito da leitura **multiplica a incerteza** por (1 + tamanho do
defeito), na convenção do Felipe: `c ≥ 1`, maior = menos confiança, e o
baseline de He-Litterman (`c = 1`) é o TETO de confiança — o Ω só tira peso,
nunca adiciona. `nivel = 0` devolve `c = 1` para toda view e recupera o BL
clássico, o que torna o nível global um parâmetro de risco e não de régua
(Decisão 6d: a forma sai do teste de monotonicidade e não é revisitada por
resultado de backtest; o nível é cravado uma vez, com o teto de alavancagem).

Dois ingredientes, não quatro. O que ficou fora e por quê:

- **proximidade do evento**: reprovou no teste de monotonicidade nas DUAS
  views, com o sinal invertido (+0,09 a +0,31) — longe do evento o mercado se
  move mais, não menos. Pelo protocolo de 08/07, candidata que reprova cai.
- **convergência entre fontes**: fora do v1 desde a Decisão 7.
- **volume**: não é ingrediente e sim **veto** (Decisão 6b). Como score ele
  também reprovou (−0,03 a +0,14), e nenhum threshold calibrado melhorou a
  régua; o que sobrevive é o veto do slot sem NENHUMA negociação, que custa
  6% da amostra e move o spearman da estabilidade em 0,008 — preço nulo pela
  garantia de que o midpoint congelado não entra como "mercado estável".

A forma dos dois fatores é transformação monótona dos scores calibrados
(`1 + x` no lugar de `−x`), então o resultado do teste de monotonicidade
continua valendo — o teste só enxerga ordem. O que a forma acrescenta é a
escala: fatores ≥ 1 por construção, sem piso, teto ou truncamento, e sem
divisão por zero. A alternativa simétrica `(1 − x)` foi medida e descartada:
o fator de coerência fica negativo em 7 de 1.139 linhas do CPI (a soma do
livro vai de 0,754 a 2,725), e consertar isso exigiria truncar em zero — um
segundo portão binário, que o compromisso da Decisão 6c com o Felipe proíbe.

Este módulo não lê dados brutos: recebe o `diagnostics` do pipeline e o
volume agregado, ambos por view.
"""

import numpy as np
import pandas as pd

from lia.calibracao_omega import preparar_pmf, variacao_total

# Passo nativo do histórico do Polymarket. Não é parâmetro de modelo: é a
# grade em que o dado chega (Decisão 6, spec de volume de 05/08).
SLOT = pd.Timedelta(hours=12)


def pmf_da_serie_janela(serie_janela) -> pd.DataFrame:
    """Reconstrói a PMF da janela na **grade completa** de 12h.

    `serie_janela` é o campo cru do `diagnostics`: `[(t, {faixa: p}), ...]`,
    já filtrado pelo pipeline para linhas com ao menos uma faixa precificada.

    O ponto desta função é o que o pipeline tirou: **o slot inteiramente vazio
    não vem na lista**, então duas linhas vizinhas ali podem estar a mais de
    um slot de distância. Sem reconstruir a grade, o `.diff()` do
    `variacao_total` compararia leituras não-adjacentes e leria como "uma
    variação" o que são duas ou três — exatamente o par que a Decisão 6e manda
    descartar. Reindexar devolve o buraco como linha NaN, e o `preparar_pmf`
    o descarta pela regra já registrada.

    Devolve DataFrame vazio quando não há ponto nenhum.
    """
    if len(serie_janela) == 0:
        return pd.DataFrame()
    indice = pd.DatetimeIndex([t for t, _ in serie_janela])
    pmf = pd.DataFrame([linha for _, linha in serie_janela], index=indice)
    grade = pd.date_range(indice.min(), indice.max(), freq=SLOT)
    return pmf.reindex(grade)


def fator_estabilidade(pmf: pd.DataFrame, janela_variacoes: int) -> float:
    """`1 + média da variação total` nas últimas `janela_variacoes` variações.

    A variação total é a candidata (a) da Decisão 6a — a fração da massa de
    probabilidade que mudou de faixa entre dois slots adjacentes, `0,5·Σ|Δp|`.
    Vem de `calibracao_omega` de propósito: uma única implementação da mesma
    quantidade no sistema, que é a razão pela qual o `dp_variacao_janela` do
    `diagnostics` não é consumido em caso nenhum.

    `janela_variacoes` é o nº de VARIAÇÕES, não de slots — a janela de N
    variações cobre N+1 slots. O nome é explícito porque o `janela_slots` do
    `diagnostics` conta slots, e o off-by-one entre os dois seria invisível.
    Calibrado: **5 variações** (vence 10 e 20 em todos os cortes das duas
    views), o que corresponde a `janela_slots = 6`.

    Devolve NaN quando não sobra nenhum par adjacente completo na janela —
    ausência de medição, que o chamador trata como view sem qualificação
    possível, nunca como confiança máxima.
    """
    if janela_variacoes < 1:
        raise ValueError("janela_variacoes deve ser pelo menos 1")
    if pmf.empty:
        return float("nan")
    variacoes = variacao_total(preparar_pmf(pmf))
    media = variacoes.tail(janela_variacoes).mean()
    return float(1.0 + media) if pd.notna(media) else float("nan")


def fator_coerencia(pmf: pd.DataFrame) -> float:
    """`1 + |soma das faixas − 1|` na leitura da decisão (última linha).

    Mede o desarranjo do livro: cada faixa é um mercado separado e elas se
    desencontram (medido: soma de 0,754 a 2,725 no CPI, 0,923 a 1,325 no
    mercado de cortes do Fed). É bilateral, ao contrário do piso da cascata do
    Felipe (soma < 0,9 desativa a view), que só corta por baixo — os dois agem
    em regimes disjuntos (Decisão 6c).

    Mede na PMF **crua**, não na renormalizada: renormalizar apagaria
    justamente a grandeza medida. É o oposto do que o colapso da estabilidade
    faz, e é o que mantém os dois ingredientes medindo coisas diferentes.

    **Linha da decisão incompleta ⇒ 1.0 (neutro).** Ali a soma mede buraco, e
    não desencontro; punir o buraco aqui seria cobrá-lo duas vezes, e o que
    fazer com uma leitura incompleta é decisão da cascata do Felipe, não do Ω.
    """
    if pmf.empty:
        return 1.0
    decisao = pmf.iloc[-1]
    if decisao.isna().any():
        return 1.0
    return float(1.0 + abs(decisao.sum() - 1.0))


def calcular_omega(
    diagnostics,
    volume_notional: dict[str, float],
    nivel: float,
    janela_variacoes: int,
) -> tuple[dict[str, float], dict[str, bool]]:
    """Calcula o multiplicador de incerteza `c` e a máscara `ativa` por view.

    `diagnostics`      : iterável de blocos do pipeline, um por view. A chave
                         de saída sai de `bloco["view"]` — derivada em runtime,
                         nunca de lista escrita à mão, para o nome da view não
                         viver em dois lugares.
    `volume_notional`  : `{view: notional_usd}` no slot da decisão, somado
                         sobre as faixas do mercado. **Ausente ou NaN não
                         veta** (Decisão 6b): é ignorância nossa (truncamento
                         do cap de 20k trades do `/trades`), não iliquidez
                         medida. `0` veta — ali ninguém negociou e o preço é
                         midpoint semeado, não probabilidade negociada.
                         A agregação é por SOMA das faixas: o mínimo entre
                         faixas foi medido e veta 47% dos slots de 12h, porque
                         é comum uma faixa não negociar em meio dia.
    `nivel`            : expoente global, **sem default** — vem da reunião de
                         risco junto com o teto de alavancagem (Decisão 6d).
                         0 devolve `c = 1` (He-Litterman puro).
    `janela_variacoes` : nº de variações da estabilidade, **sem default**.
                         Calibrado em 5.

    View inativa sai com `c = nan`: não existe confiança para uma view que não
    entra em P/Q, e devolver 1.0 ali convidaria o chamador a usá-la por
    engano.
    """
    if nivel < 0:
        raise ValueError("nivel não pode ser negativo (c ficaria < 1)")

    c: dict[str, float] = {}
    ativa: dict[str, bool] = {}
    for bloco in diagnostics:
        view = bloco["view"]
        pmf = pmf_da_serie_janela(bloco["serie_janela"])
        estabilidade = fator_estabilidade(pmf, janela_variacoes)

        volume = volume_notional.get(view, np.nan)
        sem_negociacao = pd.notna(volume) and volume <= 0
        # sem par adjacente completo não há como qualificar a leitura; a view
        # sai em vez de receber confiança que ninguém mediu
        ativa[view] = not (sem_negociacao or pd.isna(estabilidade))

        if not ativa[view]:
            c[view] = float("nan")
            continue
        c[view] = float((estabilidade * fator_coerencia(pmf)) ** nivel)
    return c, ativa
