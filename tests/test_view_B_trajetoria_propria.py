"""Testes sintéticos da view B de β próprio (regra CLAUDE.md §5).

O foco é o que esta versão ACRESCENTA à B antiga — demeanagem, piso de soma,
`vertice` obrigatório e a saída da chave `e_zq_dez_bps` — mais a propriedade que
justifica a view existir: β de vértices diferentes dão P diferentes.
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import view_B_trajetoria_fed
import view_B_trajetoria_propria as vB
from views_common import P_from_betas

ASSETS = ["SPY", "XLK", "XLU", "TIP"]
BETAS = np.array([-0.0004, -0.0008, -0.0001, -0.0003])   # fração/bp
# excess = [0, −4e−4, +3e−4, +1e−4]; Σ|excess| = 8e−4; P = [0, −1, 0.75, 0.25]
P_ESPERADO = np.array([0.0, -1.0, 0.75, 0.25])
SUM_P_BETA = 6.5e-4
# PMF de trajetória: 60% em "taxa termina em 400bp", 30% em "375bp" -> soma 0.9
PROBS = [0.6, 0.3]
TAXAS = [400.0, 375.0]
E_POLY = (0.6 * 400.0 + 0.3 * 375.0) / 0.9        # pmf_mean renormaliza: 391.666...


def _fl(p):
    return np.asarray(p, dtype=float)


def test_caso_conhecido_com_demeanagem():
    """benchmark 380bp -> surpresa +11,67bp; média expansiva 5bp -> líquida 6,67."""
    r = vB.build_view(ASSETS, benchmark_bps=380.0, betas=BETAS, vertice="DGS1",
                      bucket_probs=PROBS, bucket_rates_bps=TAXAS,
                      surpresa_media=5.0, soma_minima=0.5, fl_correction=_fl)
    assert np.isclose(r.diagnostics["e_poly_bps"], E_POLY)
    assert np.isclose(r.diagnostics["surpresa_bps"], E_POLY - 380.0)
    assert np.isclose(r.diagnostics["surpresa_liquida"], E_POLY - 385.0)
    assert np.isclose(r.Q, (E_POLY - 385.0) * SUM_P_BETA)
    assert np.allclose(r.P, P_ESPERADO)
    assert r.diagnostics["view"] == "B_trajetoria_propria"
    assert r.diagnostics["vertice"] == "DGS1"
    assert r.diagnostics["horizonte_q_dias"] == 1     # empilha com 2.2/2.3


def test_demeanagem_zero_reproduz_a_B_antiga():
    """Sem média, o Q tem de bater com o da B da espec — é o mesmo E_poly e o
    mesmo P; a demeanagem é a única diferença de conta entre as duas."""
    nova = vB.build_view(ASSETS, 380.0, BETAS, vertice="DGS1", bucket_probs=PROBS,
                         bucket_rates_bps=TAXAS, soma_minima=0.5, fl_correction=_fl)
    antiga = view_B_trajetoria_fed.build_view(
        ASSETS, e_zq_dez_bps=380.0, betas=BETAS, bucket_probs=PROBS,
        bucket_rates_bps=TAXAS, fl_correction=_fl)
    assert np.isclose(nova.Q, antiga.Q)
    assert np.allclose(nova.P, antiga.P)


def test_chave_do_zq_sai_dos_diagnostics():
    """O benchmark não é mais o ZQ: a chave antiga não pode sobreviver com valor
    novo, senão o artefato mente para quem ler depois."""
    r = vB.build_view(ASSETS, 380.0, BETAS, vertice="DGS1", bucket_probs=PROBS,
                      bucket_rates_bps=TAXAS, soma_minima=0.5, fl_correction=_fl)
    assert "e_zq_dez_bps" not in r.diagnostics
    assert np.isclose(r.diagnostics["benchmark_bps"], 380.0)


def test_vertice_obrigatorio():
    """Sem declarar o vértice não dá para saber se os β são próprios ou os da
    2.3 — e os dois dão P ortogonais (15g)."""
    for ruim in (None, ""):
        try:
            vB.build_view(ASSETS, 380.0, BETAS, vertice=ruim, bucket_probs=PROBS,
                          bucket_rates_bps=TAXAS, soma_minima=0.5, fl_correction=_fl)
            assert False, f"vertice={ruim!r} deveria ser rejeitado"
        except ValueError:
            pass


def test_piso_de_soma_mata_pmf_degenerada():
    """Soma 0,12 (mercado sem preço no livro) sai pela cascata, não vira PMF
    renormalizada. Mesmo piso e mesmo motivo da 2.3."""
    assert vB.build_view(ASSETS, 380.0, BETAS, vertice="DGS1",
                         bucket_probs=[0.08, 0.04], bucket_rates_bps=TAXAS,
                         fl_correction=_fl) is None
    # com o piso baixado de propósito, a mesma linha passa
    assert vB.build_view(ASSETS, 380.0, BETAS, vertice="DGS1",
                         bucket_probs=[0.08, 0.04], bucket_rates_bps=TAXAS,
                         soma_minima=0.1, fl_correction=_fl) is not None


def test_cascata_sem_mercado():
    """Sem PMF e sem binário a view sai desativada — não é falha."""
    assert vB.build_view(ASSETS, 380.0, BETAS, vertice="DGS1") is None


def test_fallback_binario_demeanado():
    """Binário cru (0.72, 0.24) -> p = 0.75; E_poly = 400 − 0.75·25 = 381,25."""
    r = vB.build_view(ASSETS, 380.0, BETAS, vertice="DGS1",
                      binary_prob=(0.75, 0.25), taxa_atual_bps=400.0,
                      surpresa_media=1.0, fl_correction=_fl)
    assert np.isclose(r.diagnostics["e_poly_bps"], 381.25)
    assert np.isclose(r.Q, (381.25 - 380.0 - 1.0) * SUM_P_BETA)
    assert r.diagnostics["caminho"] == "binario"


def test_beta_de_vertices_diferentes_da_P_diferente():
    """A propriedade que justifica a view existir (15g, medido em 95,6°): com β
    de outro vértice o P deixa de ser o da 2.3. Aqui em versão sintética — se
    esta invariante cair, a view voltou a duplicar a 2.3 sem avisar."""
    betas_curto = BETAS
    betas_longo = np.array([-0.0004, -0.0001, -0.0009, -0.0002])
    P_curto = P_from_betas(betas_curto, ASSETS)
    P_longo = P_from_betas(betas_longo, ASSETS)
    assert not np.allclose(P_curto, P_longo)
    cos = P_curto @ P_longo / (np.linalg.norm(P_curto) * np.linalg.norm(P_longo))
    assert cos < 0.5, f"P quase colineares (cos={cos:.2f}) — voltou a duplicar a 2.3"
