"""Teste da regra de reprodução do `gate_mercados_irmaos.py` (Felipe).

O que está sendo protegido é a distinção entre as duas relações. Trocar
`espelho` por `igual` inverte o veredito de TODAS as células do par partidário
sem que nenhum número pareça estranho — e foi essa distinção que matou a view
2.4 (mecanismo partidário exige que o sinal inverta quando o partido inverte).
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gate_mercados_irmaos import IRMAOS, reproduz  # noqa: E402


def test_espelho_exige_sinais_opostos():
    """Mecanismo partidário: o irmão tem de inverter."""
    ok, _d = reproduz({"SPY": +2.0, "TLT": -1.0}, {"SPY": -3.0, "TLT": +0.5},
                      "espelho")
    assert ok is True


def test_espelho_reprova_quando_os_dois_andam_junto():
    """É EXATAMENTE o padrão que matou a 2.4: o TLT cai nos dois mercados."""
    ok, detalhe = reproduz({"SPY": +2.0, "TLT": -1.0},
                           {"SPY": +3.0, "TLT": -0.5}, "espelho")
    assert ok is False
    assert "❌" in detalhe


def test_igual_exige_o_mesmo_sinal():
    """Dois episódios da mesma pergunta: o sinal tem de repetir."""
    assert reproduz({"XLE": +1.0}, {"XLE": +2.0}, "igual")[0] is True
    assert reproduz({"XLE": +1.0}, {"XLE": -2.0}, "igual")[0] is False


def test_as_duas_relacoes_dao_vereditos_opostos_no_mesmo_dado():
    """Trocar a relação inverte o veredito — é por isso que ela é declarada."""
    a, b = {"SPY": +1.0}, {"SPY": -1.0}
    assert reproduz(a, b, "espelho")[0] is not reproduz(a, b, "igual")[0]


def test_precisa_de_TODOS_os_ativos_do_livro():
    """Uma perna certa e outra errada reprova — não é maioria, é conjunção."""
    ok, _d = reproduz({"XLE": +1.0, "XLK": +1.0},
                      {"XLE": +1.0, "XLK": -1.0}, "igual")
    assert ok is False


def test_mu_zero_sai_do_denominador():
    """Sinal zero não testa direção nenhuma: não conta como acerto nem erro."""
    ok, detalhe = reproduz({"XLE": +1.0, "XLK": 0.0},
                           {"XLE": +2.0, "XLK": +1.0}, "igual")
    assert ok is True          # decidido só pelo XLE
    assert "—" in detalhe      # o XLK aparece marcado como não testado


def test_mu_ausente_nao_vira_veredito():
    assert reproduz(None, {"XLE": +1.0}, "igual")[0] is None


def test_pares_declarados_usam_relacao_conhecida():
    """Guarda contra digitar uma relação que o `reproduz` não entende."""
    assert {r for _a, _b, r, _m in IRMAOS.values()} <= {"espelho", "igual"}


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
