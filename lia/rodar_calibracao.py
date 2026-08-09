"""Roda o teste de monotonicidade sobre o dado real do FOMC (Decisão 6).

Escolhe a forma funcional dos ingredientes do Ω pelo protocolo registrado em
08/07: faixas de confiança maiores devem apresentar erro realizado da
probabilidade menor; empates resolvem pela forma com menos parâmetros.

Escopo desta rodada — **dois ingredientes**, não os quatro. O portão de
volume não entra porque o G5 não alcança os mercados do FOMC (chave ausente
no parquet e 1 mercado de 76 — ver `PEDIDO_Paulo_G5_fomc.md`), e sem portão
o `score_estabilidade` sai junto: pela Decisão 6b o portão é pré-condição
dele, já que o midpoint congela e o mercado sem negociação aparece como
perfeitamente estável. Sobram proximidade e coerência, ambos calibráveis com
o que existe hoje.

Ponto de método: cada evento (reunião) é uma série própria e as variações
NUNCA cruzam a fronteira entre eventos — os 18 mercados se sobrepõem no
tempo, e um `.diff()` sobre o painel empilhado compararia PMFs de reuniões
diferentes. Calcula-se por evento e empilha-se depois.

O alvo é o mesmo para todas as candidatas (variação total h slots à frente),
para que os `spearman` sejam comparáveis entre si; a robustez com alvo em
`|ΔE|` é reportada ao lado, e a leitura só muda se a ordenação mudar.

Uso:

    python lia/rodar_calibracao.py --dados <dir com data/ e src/>
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from lia.calibracao_omega import (
    comparar_candidatas,
    preparar_pmf,
    score_coerencia,
    score_estabilidade_pmf,
    score_proximidade,
    variacao_total,
    variacao_valor_esperado,
)

# Grades em teste. Nenhuma tem default no código: a escolha sai deste
# script, não de valor escrito à mão em módulo de lógica.
JANELAS_SLOTS = (5, 10, 20)
HORIZONTES_SLOTS = (2, 5)
HORIZONTES_PROXIMIDADE_DIAS = (5, 15)
N_FAIXAS = 3


def carregar_eventos(raiz):
    """Lê a PMF do FOMC pelo loader do pipeline (módulo do Felipe/Paulo)."""
    sys.path.insert(0, str(Path(raiz) / "src"))
    from poly_loader import daily_preopen, load_fomc_pmf  # noqa: E402

    caminho = Path(raiz) / "data" / "polymarket_fed_reunioes.parquet"
    return load_fomc_pmf(caminho), daily_preopen


def montar_painel(eventos, daily_preopen, grade):
    """Empilha, por evento, as séries de que a calibração precisa.

    `grade` : "12h" (série crua, passo nativo) ou "24h" (só o slot
              pré-abertura, que é o que a view enxerga). É a dimensão de
              grade temporal registrada na Decisão 6e.

    Devolve um DataFrame com MultiIndex (evento, data) e as colunas
    `var_total`, `var_esperado`, `soma_cru`, `linha_completa`,
    `dias_ate_evento`.
    """
    linhas = []
    for evento_id, (probs, valores, _abertos, reuniao) in eventos.items():
        crua = probs if grade == "12h" else daily_preopen(probs)
        if len(crua) < max(JANELAS_SLOTS) + max(HORIZONTES_SLOTS) + 1:
            continue  # série curta demais para janela + horizonte
        pronta = preparar_pmf(crua)
        painel = pd.DataFrame(
            {
                "var_total": variacao_total(pronta),
                "var_esperado": variacao_valor_esperado(pronta, valores),
                "soma_cru": crua.sum(axis=1, skipna=True),
                "linha_completa": crua.notna().all(axis=1).astype(float),
            }
        )
        dias = (reuniao - painel.index.tz_localize(None).normalize()).days
        painel["dias_ate_evento"] = np.clip(dias, 0, None)
        painel["evento"] = evento_id
        linhas.append(painel.set_index("evento", append=True).swaplevel())
    return pd.concat(linhas).sort_index()


def alvo_futuro(painel, coluna, horizonte):
    """Erro realizado: a variação observada `horizonte` slots à frente.

    Deslocado DENTRO de cada evento — `groupby` impede que o fim de uma
    reunião empreste futuro do começo da seguinte.
    """
    return painel.groupby(level="evento")[coluna].shift(-horizonte)


def montar_candidatas(painel, grade):
    """As candidatas em teste nesta rodada, com o nome que vai ao relatório."""
    candidatas = {}
    for coluna, forma in (("var_total", "vt"), ("var_esperado", "ve")):
        for janela in JANELAS_SLOTS:
            score = painel.groupby(level="evento", group_keys=False)[coluna].apply(
                lambda s, j=janela: score_estabilidade_pmf(s, janela=j)
            )
            candidatas[f"estabilidade_{forma}_j{janela}_{grade}"] = score
    candidatas[f"coerencia_{grade}"] = score_coerencia(
        painel.soma_cru, painel.linha_completa
    )
    datas = painel.index.get_level_values("data")
    for horizonte in HORIZONTES_PROXIMIDADE_DIAS:
        for forma in ("linear", "exponencial"):
            dias = painel.dias_ate_evento.to_numpy()
            if forma == "linear":
                valores = np.minimum(dias, horizonte) / horizonte
            else:
                valores = 1.0 - np.exp(-dias / horizonte)
            candidatas[f"proximidade_{forma}_h{horizonte}_{grade}"] = pd.Series(
                valores, index=painel.index
            )
    return candidatas, datas


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dados", required=True, help="dir com data/ e src/")
    args = ap.parse_args()

    eventos, daily_preopen = carregar_eventos(args.dados)
    print(f"eventos lidos: {len(eventos)}")

    for grade in ("12h", "24h"):
        painel = montar_painel(eventos, daily_preopen, grade)
        completas = int(painel.linha_completa.sum())
        print(f"\n{'=' * 72}\nGRADE {grade} — {len(painel)} slots, "
              f"{completas} linhas completas, "
              f"{painel.index.get_level_values('evento').nunique()} eventos")
        candidatas, _ = montar_candidatas(painel, grade)
        for horizonte in HORIZONTES_SLOTS:
            for coluna, rotulo in (("var_total", "variacao total"),
                                   ("var_esperado", "|dE| (robustez)")):
                erro = alvo_futuro(painel, coluna, horizonte)
                tabela = comparar_candidatas(candidatas, erro, N_FAIXAS)
                print(f"\n-- alvo: {rotulo} em h={horizonte} slots "
                      f"(n={int(tabela.n_observacoes.max())}) --")
                print(tabela.to_string(float_format=lambda v: f"{v: .4f}"))


if __name__ == "__main__":
    main()
