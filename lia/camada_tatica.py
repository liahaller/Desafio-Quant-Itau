"""Camada tática — trades curtos sobrepostos à carteira estrutural, sem
alterar os pesos do Black-Litterman.

Os três sinais (PEAD, event-driven, velocidade de ajuste) são
independentes entre si: a falha de um no backtest não deve derrubar os
outros (ver LIA_risco_relatorio.md, Semana 2).
"""

from dataclasses import dataclass


@dataclass
class EventoMercado:
    """Representa um evento do Polymarket relevante para a camada tática."""

    probabilidade_vespera: float
    probabilidade_resolucao: float | None  # None enquanto o evento não resolveu
    serie_probabilidade: list[float]  # histórico de probabilidade até o momento


def detectar_surpresa_pead(evento: EventoMercado) -> bool:
    """Indica se o desfecho do evento conta como "surpresa" e deve
    disparar o trade de drift pós-evento (PEAD).

    TODO(DECISAO-5): critério de limiar, janela de holding e ativos
    elegíveis ainda não decididos — ver Decisoes_pendentes.md.
    """
    raise NotImplementedError(
        "Definição de 'surpresa' (PEAD) ainda não decidida "
        "(ver Decisoes_pendentes.md, Decisão 5)"
    )


def detectar_salto_event_driven(evento: EventoMercado) -> bool:
    """Indica se houve um salto de nível na probabilidade antes da
    resolução (ex.: fusão 40% -> 70%) grande o suficiente para
    caracterizar o sinal event-driven.

    TODO(DECISAO-8): tamanho do salto, unidade de medida e janela de
    tempo ainda não decididos — ver Decisoes_pendentes.md.
    """
    raise NotImplementedError(
        "Gatilho de salto event-driven ainda não decidido "
        "(ver Decisoes_pendentes.md, Decisão 8)"
    )


def calcular_velocidade_ajuste(serie_probabilidade: list[float]) -> float:
    """Calcula a velocidade (derivada) de ajuste da probabilidade durante
    um movimento, usada como gatilho do sinal de velocidade.

    TODO(DECISAO-9): forma de estimar a derivada e limiar de gatilho ainda
    não decididos — ver Decisoes_pendentes.md.
    """
    raise NotImplementedError(
        "Forma de cálculo da velocidade de ajuste ainda não decidida "
        "(ver Decisoes_pendentes.md, Decisão 9)"
    )
