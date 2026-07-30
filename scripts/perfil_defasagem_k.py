"""Perfil de defasagem k das views poly-defasadas (decisões 3.1 e 3.2). Felipe.

A tese das views defasadas (2.4 eleitoral, 3.1 recessão, C, E, G) é que o
Polymarket precifica a notícia antes da bolsa e a bolsa leva k dias para
absorver. Este script MEDE o perfil — não escolhe o k. A escolha do critério
é a decisão 3.1 (opção (a) da pauta: decidir com o gráfico na mesa) e, se o
perfil disser que a resposta é contemporânea, dispara a decisão 3.2 (a view
eleitoral não liga por construção).

Alinhamento (regra fechada em 2026-07-30):
  - p do dia D = slot das 12:00 UTC de D (pré-abertura de Nova York), via
    `poly_loader.daily_preopen`.
  - Δp(D) = p(D) − p(D−1) sobre DIAS DE PREGÃO consecutivos. Numa segunda,
    Δp carrega o fim de semana inteiro — que é exatamente a informação
    disponível antes da abertura.
  - r(D) = fechamento(D)/fechamento(D−1) − 1 (o parquet do Paulo só tem
    fechamento ajustado; o `Open` é o G1, ainda não entregue).
  Consequência: o lag 0 é "quase contemporâneo" — a janela do poly termina
  antes da abertura de D e o retorno de D é medido de fechamento a
  fechamento. Coeficiente em lag >= 1 é que é defasagem de verdade.

Sensibilidade à decisão 1.1: a correção de favorite-longshot é monótona, e
uma transformação monótona não move o LAG em que a resposta aparece — só a
escala do coeficiente. O script roda o perfil com γ = 1,0 e γ = 1,25 (mesma
família do pacote de sensibilidade) para deixar isso medido, não assumido.

Uso:
    python scripts/perfil_defasagem_k.py --dados <dir raw> --precos <parquet>
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from poly_loader import daily_preopen, series_by_slot  # noqa: E402
from sensibilidade_reuniao import fl_power  # noqa: E402
from views_common import lag_regression  # noqa: E402

# Janela de varredura do perfil — é o alcance do diagnóstico, NÃO o k
# escolhido (que é decisão da reunião). 10 pregões = duas semanas.
K_MAX = 10

# Mercados designados de cada view defasada, com o arquivo cru do Paulo.
MERCADOS = {
    "2.4 eleitoral (Trump 2024)": "M5_trump_2024_*.json",
    "3.1 recessão (US 2025)": "M4_recession_*.json",
    "C geopolítica (Irã jun/2025)": "M7_iran_jun2025_*.json",
}


def retornos_diarios(caminho_parquet):
    """Retornos diários dos 9 ETFs, tabela larga indexada por data."""
    precos = pd.read_parquet(caminho_parquet)
    largo = precos.pivot(index="data", columns="ticker", values="preco_ajustado")
    return largo.pct_change().dropna()


def alinhar(p_diario, retornos):
    """Junta poly e bolsa no calendário de PREGÃO e devolve (Δp, retornos)."""
    dados = retornos.join(p_diario.rename("p"), how="inner").dropna()
    dp = dados["p"].diff()
    dados = dados.iloc[1:]
    return dp.iloc[1:], dados[retornos.columns]


def perfil_com_t(dp, retornos, k_max=K_MAX):
    """Perfil de lags + estatística t. Os coeficientes vêm de
    `views_common.lag_regression` (o caminho de produção); as SEs são
    recalculadas aqui, pela mesma matriz de desenho, só para o diagnóstico.
    """
    coefs = lag_regression(retornos.to_numpy(), dp.to_numpy(), k_max)

    dp_v = dp.to_numpy()
    T = dp_v.shape[0]
    m = T - k_max
    X = np.column_stack([np.ones(m)] + [dp_v[k_max - k: T - k] for k in range(k_max + 1)])
    Y = retornos.to_numpy()[k_max:]
    beta, *_ = np.linalg.lstsq(X, Y, rcond=None)
    # confere que a matriz de desenho local é a mesma do caminho de produção
    assert np.allclose(beta[1:], coefs), "perfil local divergiu do lag_regression"
    residuos = Y - X @ beta
    sigma2 = (residuos ** 2).sum(axis=0) / (m - X.shape[1])
    var_coef = np.diag(np.linalg.inv(X.T @ X))[1:, None] * sigma2[None, :]
    return (pd.DataFrame(coefs, columns=retornos.columns, index=range(k_max + 1)),
            pd.DataFrame(coefs / np.sqrt(var_coef), columns=retornos.columns,
                         index=range(k_max + 1)), m)


def correlacao_bidirecional(dp, retornos, lags=range(-3, 6)):
    """corr(Δp(t−k), r(t)) para k negativo E positivo.

    Checagem que a regressão sozinha não faz: k > 0 é o poly liderando a
    bolsa (a tese); k < 0 é a BOLSA liderando o poly — co-movimento de
    notícia comum, que não sustenta view nenhuma. Se o pico estiver em
    k <= 0, o que a regressão mostra não é previsibilidade.
    """
    linhas = {}
    for k in lags:
        deslocado = dp.shift(k)
        linhas[k] = retornos.corrwith(deslocado)
    return pd.DataFrame(linhas).T


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dados", default="data/raw/clob_exploracao")
    parser.add_argument("--precos", default="data/etf_prices_daily.parquet")
    parser.add_argument("--saida", default="Dump/Perfil_defasagem_k.md")
    args = parser.parse_args()

    saida = []
    print = saida.append

    retornos = retornos_diarios(args.precos)
    print("# Perfil de defasagem k — views poly-defasadas\n")
    print("> Gerado por `scripts/perfil_defasagem_k.py`. **Mede o perfil; não escolhe o k** "
          "(decisão 3.1). Alinhamento: p do dia = slot das 12:00 UTC (pré-abertura); "
          "Δp sobre pregões consecutivos; retorno de fechamento a fechamento.\n")
    print("Célula = coeficiente do lag (retorno por unidade de Δp), com **|t| > 2 em "
          "negrito**. O lag 0 é quase contemporâneo por construção — **defasagem de "
          "verdade é coeficiente forte em lag ≥ 1**.\n")

    for nome, padrao in MERCADOS.items():
        arquivo = next(Path(args.dados).glob(padrao))
        p_bruto = daily_preopen(series_by_slot(arquivo))
        print(f"\n## {nome}\n")
        for gamma in (1.0, 1.25):
            p = p_bruto if gamma == 1.0 else pd.Series(
                p_bruto ** gamma / (p_bruto ** gamma + (1 - p_bruto) ** gamma),
                index=p_bruto.index)
            dp, r = alinhar(p, retornos)
            if len(dp) < K_MAX * 3:
                print(f"*Amostra curta demais ({len(dp)} pregões) para varrer {K_MAX} lags.*")
                break
            coefs, ts, m = perfil_com_t(dp, r)
            rotulo = "sem correção FL (γ=1,0)" if gamma == 1.0 else "com FL forte (γ=1,25)"
            print(f"\n**{rotulo}** — {m} observações, {len(r.columns)} ativos\n")
            print("| lag | " + " | ".join(coefs.columns) + " |")
            print("|" + "---|" * (len(coefs.columns) + 1))
            for lag in coefs.index:
                celulas = []
                for ativo in coefs.columns:
                    valor = f"{coefs.loc[lag, ativo]:+.4f}"
                    celulas.append(f"**{valor}**" if abs(ts.loc[lag, ativo]) > 2 else valor)
                print(f"| {lag} | " + " | ".join(celulas) + " |")
            fortes = [(lag, ativo) for lag in coefs.index for ativo in coefs.columns
                      if abs(ts.loc[lag, ativo]) > 2]
            com_defasagem = sorted({lag for lag, _ in fortes if lag >= 1})
            print(f"\n- coeficientes com |t| > 2: **{len(fortes)}** de "
                  f"{coefs.size} — em lag 0: {sum(1 for lag, _ in fortes if lag == 0)}; "
                  f"em lag ≥ 1: {sum(1 for lag, _ in fortes if lag >= 1)}")
            print(f"- lags ≥ 1 com algum ativo significante: "
                  f"{com_defasagem if com_defasagem else 'NENHUM'}")
            if not com_defasagem:
                print("- ⚠️ **sem defasagem detectável neste mercado** — é o caso que "
                      "dispara a decisão 3.2 (view contemporânea ou fora do v1).")
            esperados = 0.05 * coefs.size
            print(f"- (ao acaso, a 5%, esperar-se-iam ~{esperados:.0f} de "
                  f"{coefs.size} — contagem só vale acima disso, e com sinais coerentes "
                  f"entre ativos)")

            if gamma == 1.0:
                corr = correlacao_bidirecional(dp, r)
                print("\nQuem lidera quem — `corr(Δp(t−k), r(t))`, **k < 0 = a bolsa "
                      "lidera o poly** (co-movimento, não previsão):\n")
                print("| k | " + " | ".join(corr.columns) + " |")
                print("|" + "---|" * (len(corr.columns) + 1))
                for k in corr.index:
                    marca = " ←" if k < 0 else ""
                    print(f"| {k}{marca} | "
                          + " | ".join(f"{corr.loc[k, a]:+.3f}" for a in corr.columns) + " |")
                pico = corr.abs().max(axis=1).idxmax()
                print(f"\n- maior |correlação| em **k = {pico}** "
                      f"({'poly lidera' if pico > 0 else 'contemporâneo/bolsa lidera'})")

    print("\n## Ressalva estrutural (vale para os três mercados)\n")
    print("A janela do poly de um dia (12:00 UTC → 12:00 UTC) **contém o pregão do dia "
          "anterior** (13:30–21:00 UTC). Logo, a correlação em `k = −1` é em boa parte "
          "MECÂNICA: mede o poly absorvendo a notícia do mesmo pregão, não o poly "
          "seguindo a bolsa. O que ela permite afirmar é mais fraco e mais importante: "
          "**nessa granularidade não dá para separar 'o poly antecipa' de 'os dois leem "
          "a mesma notícia na janela que se sobrepõe'.** Separar exigiria passo "
          "intradiário, que o Paulo mediu existir só nos ~30 dias mais recentes de "
          "mercado vivo — não serve para backtest.\n")
    print("Por isso a leitura correta de um pico em `k ≤ 0` não é 'a tese está errada', "
          "e sim **'o dado disponível não sustenta a tese'** — que, para efeito de "
          "decisão, dá no mesmo: a view não pode ser ligada com base nele.\n")

    Path(args.saida).write_text("\n".join(saida) + "\n", encoding="utf-8")
    sys.stdout.write(f"escrito: {args.saida} ({len(saida)} linhas)\n")


if __name__ == "__main__":
    main()
