"""Testes do Ω reativo.

Casos sintéticos com resultado conhecido só podem ser escritos depois que
a forma funcional (Decisão 6, ver Decisoes_pendentes.md) for fechada na
reunião de 07/jul/2026. Até lá, o teste documenta a interface esperada e
confirma que o placeholder falha de forma explícita.
"""

import pytest

from lia.omega import SinaisOmega, calcular_omega


def test_calcular_omega_ainda_nao_implementado():
    sinais = SinaisOmega(
        volume_liquidez=1.0,
        estabilidade_probabilidade=1.0,
        convergencia_fontes=1.0,
        proximidade_evento=1.0,
    )
    with pytest.raises(NotImplementedError):
        calcular_omega(sinais)
