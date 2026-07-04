"""Testes da camada tática.

Casos sintéticos com resultado conhecido só podem ser escritos depois que
as Decisões 3, 6 e 7 (ver Decisoes_pendentes.md) forem fechadas na reunião
de 07/jul/2026. Até lá, os testes documentam a interface esperada e
confirmam que os placeholders falham de forma explícita.
"""

import pytest

from lia.camada_tatica import (
    EventoMercado,
    calcular_velocidade_ajuste,
    detectar_salto_event_driven,
    detectar_surpresa_pead,
)


def _evento_exemplo() -> EventoMercado:
    return EventoMercado(
        probabilidade_vespera=0.25,
        probabilidade_resolucao=1.0,
        serie_probabilidade=[0.20, 0.22, 0.25],
    )


def test_detectar_surpresa_pead_ainda_nao_implementado():
    with pytest.raises(NotImplementedError):
        detectar_surpresa_pead(_evento_exemplo())


def test_detectar_salto_event_driven_ainda_nao_implementado():
    with pytest.raises(NotImplementedError):
        detectar_salto_event_driven(_evento_exemplo())


def test_calcular_velocidade_ajuste_ainda_nao_implementado():
    with pytest.raises(NotImplementedError):
        calcular_velocidade_ajuste([0.20, 0.22, 0.25])
