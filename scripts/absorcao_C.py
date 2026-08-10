"""Curva de absorção da view C — de onde sai o k, sem olhar retorno de estratégia.

**MEDE; não decide.** O k da view C é a janela em que ela lê o poly
(`Q = Σ P·β × (p_t − p_{t−k})`) e, junto, quantos lags de resposta o β soma
(`full_absorption_beta`). Escolher o k pelo `t` do teste de sinal é ajustar
parâmetro à amostra; este script usa o critério que a espec 2.4 (item 6)
pré-registrou e que nunca tinha sido executado:

> a premissa é que a resposta se concentra até o lag k — **o perfil decide**.

Ou seja: a pergunta é "em quantos pregões o efeito termina de chegar", que é
sobre a TRANSMISSÃO e não sobre a view dar lucro. A curva de absorção é a
resposta acumulada `Σ_{j≤k} c_j` do perfil de lags distribuídos, normalizada
pela resposta total — quando ela achata, o efeito acabou de chegar.

Roda nos DOIS episódios do Irã separados, que não se sobrepõem em data: se os
dois acharem o mesmo patamar, é mecanismo; se discordarem, o perfil não
identifica k e isso é o resultado.

Uso:
    python scripts/absorcao_C.py [--raiz .]
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from backtest_v1 import carregar  # noqa: E402
from config import ASSETS  # noqa: E402
from teste_sinal import series_C  # noqa: E402
from views_common import lag_regression  # noqa: E402

# Um lag além da grade testada (K_GRID_C vai até 5), para a curva ter para onde
# achatar. Não passa disso: o episódio de 2026 tem 28 pregões, e cada lag a mais
# come um grau de liberdade de uma amostra que já é curta.
K_MAX = 6

# O ativo da tese: a view é "escalada no Irã -> energia". Se a absorção do XLE
# não achatar, não adianta a média dos 9 achatar.
ATIVO_DA_TESE = "XLE"


def curva(p, retornos, k_max=K_MAX):
    """(cumulativo, marginal) da resposta por lag — DataFrames (k_max+1, n_ativos).

    `cumulativo.loc[k]` é exatamente o `full_absorption_beta(coefs, k)`: o β que
    a view usaria com aquele k. A curva é essa mesma conta varrida em k.
    """
    dp = p.diff().dropna()
    R = retornos.reindex(dp.index).dropna()
    dp = dp.reindex(R.index)
    coefs = lag_regression(R[list(ASSETS)].to_numpy(), dp.to_numpy(), k_max)
    marginal = pd.DataFrame(coefs, columns=list(ASSETS))
    marginal.index.name = "lag"
    return marginal.cumsum(), marginal, len(dp)


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raiz", default=".")
    parser.add_argument("--saida", default="Dump/analises/Absorcao_C.md")
    args = parser.parse_args()

    retornos, montador, _, _ = carregar(args.raiz, views_novas=())
    series = series_C(args.raiz, montador._fl, retornos.index)

    L = ["# Curva de absorção da view C — de onde sai o k\n",
         "> Gerado por `scripts/absorcao_C.py`. **Mede; não decide.** Critério da "
         "espec 2.4 item 6 (*o perfil decide*), que não olha retorno de "
         "estratégia: o k é onde a resposta ACUMULADA para de crescer.\n",
         "A coluna que decide é a **fração da resposta final** já acumulada até "
         "cada lag, no ativo da tese (**XLE**). O patamar é onde ela chega perto "
         "de 1 e para de andar.\n"]

    fracoes = {}
    for rotulo, p in series.items():
        cum, marg, n = curva(p, retornos)
        final = cum.loc[K_MAX, ATIVO_DA_TESE]
        frac = cum[ATIVO_DA_TESE] / final if final != 0 else cum[ATIVO_DA_TESE] * np.nan
        fracoes[rotulo] = frac
        L.append(f"\n## {rotulo} — {n} pregões com Δp\n")
        L.append(f"β acumulado do {ATIVO_DA_TESE} (resposta final = "
                 f"{final:+.4f}) e o que ele representa da resposta total:\n")
        L.append("| lag k | β marginal | β acumulado | fração do total | "
                 "Σ\\|β\\| acumulado dos 9 |")
        L.append("|---|---|---|---|---|")
        for k in range(K_MAX + 1):
            L.append(f"| {k} | {marg.loc[k, ATIVO_DA_TESE]:+.4f} | "
                     f"{cum.loc[k, ATIVO_DA_TESE]:+.4f} | {frac.loc[k]:+.2f} | "
                     f"{cum.loc[k].abs().sum():.4f} |")

    L.append("\n## Os dois episódios lado a lado — fração da resposta acumulada "
             f"no {ATIVO_DA_TESE}\n")
    tabela = pd.DataFrame(fracoes)
    L.append("| lag k | " + " | ".join(tabela.columns) + " |")
    L.append("|---" * (len(tabela.columns) + 1) + "|")
    for k in range(K_MAX + 1):
        L.append(f"| {k} | " + " | ".join(f"{tabela.loc[k, c]:+.2f}"
                                          for c in tabela.columns) + " |")

    # Leitura GERADA — a conclusão sai do número, não de frase cravada à mão.
    L.append("\n## Leitura (gerada)\n")
    for rotulo in tabela.columns:
        f = tabela[rotulo]
        # onde a curva cruza 80% do total pela primeira vez e não volta a cair
        # abaixo disso — descrição da forma, não nota de corte.
        acima = [k for k in f.index if (f.loc[k:] >= 0.8).all() and f.loc[k] >= 0.8]
        pico = int(f.abs().idxmax())
        L.append(f"- **{rotulo}**: a fração acumulada atinge o máximo em "
                 f"**lag {pico}** ({f.loc[pico]:+.2f}); o primeiro lag a partir do "
                 f"qual ela fica sempre ≥ 0,8 é "
                 + (f"**{acima[0]}**." if acima else "**nenhum** — a curva não assenta."))
    if len(tabela.columns) == 2:
        a, b = tabela.columns
        L.append(f"- **Concordância entre episódios**: corr das duas curvas = "
                 f"**{tabela[a].corr(tabela[b]):+.2f}**. Se as duas apontarem o "
                 "mesmo patamar, o k é mecanismo; se discordarem, **o perfil não "
                 "identifica k** — e isso é o resultado, não uma falha da medição.")

    Path(args.saida).write_text("\n".join(L) + "\n", encoding="utf-8")
    sys.stdout.write("\n".join(L) + f"\n\nescrito: {args.saida}\n")


if __name__ == "__main__":
    main()
