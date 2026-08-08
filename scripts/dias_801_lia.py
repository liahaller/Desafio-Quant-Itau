"""Os 801 dias do FOMC, resolvidos — insumo da calibração do Ω reativo (Lia).

"801 dias" é uma **construção**, não o tamanho do parquet: lendo o arquivo
direto saem 3.905 slots crus, 1.952 linhas (reunião × dia) ou 804 datas
distintas, e nenhum é o número. Os 18 mercados se sobrepõem — todo par de
reuniões consecutivas tem overlap —, então sem uma regra de seleção o mesmo dia
aparece 2 a 3 vezes e a contagem infla.

A regra, que é a mesma da view 2.3 (por isso os dias batem 1 a 1 com o v1):

  - 1 linha por DATA;
  - vale o mercado da **próxima** reunião (a primeira com `reuniao >= data`);
  - slot **pré-abertura** (12:00 UTC, `daily_preopen`);
  - série **CRUA** — sem `carry_missing`, sem renormalizar, sem cortar
    slot degenerado.

Sai crua de propósito: a Lia calibra sobre o que o mercado publicou, e o
`carry_missing` é tratamento da view, não do dado. Os dois canais que ela
separa saem em colunas próprias — `n_faixas_ausentes` é o canal de **buraco**,
`soma_cru` é o de **coerência** —, justamente para que o mesmo defeito não seja
penalizado duas vezes.

O `p` colapsado NÃO sai aqui: o colapso da PMF multi-bucket é a decisão 6a, que
segue aberta com 4 candidatas. Este arquivo é o insumo dela, não a saída.

Uso:

    python scripts/dias_801_lia.py --raiz .
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from poly_loader import daily_preopen, load_fomc_pmf  # noqa: E402

SAIDA = Path("Dump/trocas/dias_801_fomc.csv")


def montar(path_parquet):
    """Monta a tabela de 1 linha por dia pela regra da próxima reunião."""
    eventos = load_fomc_pmf(path_parquet)
    # ordem cronológica: a "próxima reunião" de um dia é a primeira que
    # ainda não aconteceu, então basta varrer do fim para o começo e deixar
    # a reunião mais próxima sobrescrever a mais distante.
    por_reuniao = sorted(eventos.items(), key=lambda kv: kv[1][3], reverse=True)

    linhas = {}
    for evento_id, (probs, _valores, _abertos, reuniao) in por_reuniao:
        diario = daily_preopen(probs)
        diario = diario[diario.index <= reuniao]  # o mercado morre na reunião
        for data, faixas in diario.iterrows():
            linhas[data] = {
                "evento_id": evento_id,
                "reuniao": reuniao.date(),
                "dias_ate_reuniao": (reuniao - data).days,
                "n_faixas_esperadas": len(faixas),
                "n_faixas_presentes": int(faixas.notna().sum()),
                "n_faixas_ausentes": int(faixas.isna().sum()),
                "soma_cru": float(faixas.sum(skipna=True)),
            }

    tabela = pd.DataFrame.from_dict(linhas, orient="index").sort_index()
    tabela.index.name = "data"
    tabela["degenerado"] = tabela.soma_cru < 0.9
    tabela["linha_completa"] = tabela.n_faixas_ausentes == 0
    return tabela


def conferir(tabela):
    """Os números que a mensagem à Lia afirma — se mudarem, o texto mente."""
    deg = tabela[tabela.degenerado]
    assert len(tabela) == 801, f"esperado 801 dias, saiu {len(tabela)}"
    assert len(deg) == 25, f"esperado 25 dias degenerados, saiu {len(deg)}"
    assert (deg.soma_cru < 0.5).sum() == 24, "esperado 24 dias com soma < 0,5"
    assert not deg.linha_completa.any(), (
        "havia livro COMPLETO somando < 0,9 — a soma baixa deixou de medir só buraco"
    )
    return deg


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--raiz", default=".", help="diretório que contém data/")
    args = ap.parse_args()

    raiz = Path(args.raiz)
    tabela = montar(raiz / "data" / "polymarket_fed_reunioes.parquet")
    deg = conferir(tabela)

    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    tabela.to_csv(SAIDA)

    print(f"dias:                {len(tabela)}")
    print(f"reuniões usadas:     {tabela.evento_id.nunique()}")
    print(f"janela:              {tabela.index.min().date()} a {tabela.index.max().date()}")
    print(f"linhas completas:    {int(tabela.linha_completa.sum())}")
    print(f"degenerados (< 0,9): {len(deg)}  (soma < 0,5: {int((deg.soma_cru < 0.5).sum())})")
    print(f"  faixas ausentes:   mediana {deg.n_faixas_ausentes.median():.0f} "
          f"de {deg.n_faixas_esperadas.median():.0f}")
    print(f"  onde caem:         {deg.index.min().date()} a {deg.index.max().date()}")
    print(f"escrito: {SAIDA}")


if __name__ == "__main__":
    main()
