"""Ω reativo — confiança que modula as views do Black-Litterman.

A forma funcional exata (Decisão pendente 6, ver Decisoes_pendentes.md)
ainda não foi fechada em reunião. Este módulo define a interface esperada
para que o restante do pipeline (bridge probabilidade -> Q, do Felipe)
possa ser integrado sem esperar a implementação final.
"""

from dataclasses import dataclass


@dataclass
class SinaisOmega:
    """Sinais de entrada para o cálculo da confiança (Ω) reativa.

    Os valores chegam já calculados pelo pipeline de dados (Paulo); este
    módulo não lê dados brutos nem acessa fontes externas.
    """

    volume_liquidez: float  # TODO(DECISAO-6): unidade/normalização a definir
    estabilidade_probabilidade: float  # TODO(DECISAO-6): unidade/normalização a definir
    convergencia_fontes: float  # TODO(DECISAO-7): forma de medir conflito entre fontes
    proximidade_evento: float  # TODO(DECISAO-6): unidade (dias? fração da janela?)


def calcular_omega(sinais: SinaisOmega) -> float:
    """Calcula a confiança reativa (Ω) a partir dos sinais de mercado.

    TODO(DECISAO-6): forma funcional (linear, não-linear, pesos, faixa de
    saída) ainda não decidida — ver Decisoes_pendentes.md.
    """
    raise NotImplementedError(
        "Forma funcional do Ω reativo ainda não decidida "
        "(ver Decisoes_pendentes.md, Decisão 6)"
    )
