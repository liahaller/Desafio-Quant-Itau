"""A 3.1 com P direcional — a medição que a D18d pede. Felipe.

**MEDE; NÃO DECIDE, e aqui isso é mais forte que o de costume.** A entrada da
3.1 direcional está BLOQUEADA pela D2b/D18d: o coeficiente direcional medido é
POSITIVO e a tese original da view prevê NEGATIVO. Entrar como desenhada perde;
inverter é o que a D2b proibiu. Este script existe para o grupo decidir com
número em vez de com lembrança — não para propor entrada.

O que ele responde, e é uma pergunta só:

    o P direcional captura o sinal que o P neutro apaga?

`Nivel_divergencia_3_1.md` mediu o sinal in sample (z-score da amostra inteira,
janelas sobrepostas) e declarou o |t| como otimista. Aqui a mesma discordância é
refeita **expansiva** — a padronização e o β usam só o que já tinha acontecido —
e as duas montagens rodam lado a lado nos MESMOS dias:

    P neutro     `P_from_betas`, P[SPY] = 0 exato  (a 3.1 como está no módulo)
    P direcional `directional_P`, P[SPY] = 2       (`build_view_direcional`)

A régua é a mesma do `teste_sinal.py`, e as funções vêm de lá em vez de
recopiadas — inclusive a convenção de r_P começar em D+1, que é o que faz a 2.3
reproduzir o t +0,26 registrado.

**Sobre o sinal do resultado:** a tabela sai com o β MEDIDO no dado. Como o Q é
linear no β, a versão "tese original" (β com o sinal que a espec prevê) é a
mesma linha com o t espelhado — está impressa como coluna para ninguém precisar
fazer a conta de cabeça, e para a escolha entre as duas ficar visivelmente uma
escolha de TESE, não de ajuste.

Uso:
    python scripts/view_3_1_direcional.py --saida Dump/analises/Recessao_direcional.md
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from market_loader import load_etf_prices, load_fred  # noqa: E402
from market_inputs import daily_returns  # noqa: E402
from config import ASSETS  # noqa: E402
from poly_loader import daily_preopen, series_by_slot  # noqa: E402
from poly_preprocessing import binary_prob_series  # noqa: E402
from teste_sinal import medir, ols  # noqa: E402
from view_2_3_fed import estimate_betas  # noqa: E402
from view_3_1_recessao import build_view_direcional, curve_spread  # noqa: E402
from views_common import P_from_betas, ViewResult  # noqa: E402
from nivel_divergencia_3_1 import PADRAO_NAO, PADRAO_SIM, spread_defasado  # noqa: E402

# Horizontes do `Nivel_divergencia_3_1.md`, mantidos para as duas medições serem
# comparáveis linha a linha. h = 1 é o H da carteira (D9).
HORIZONTES = (1, 5, 10, 21)

# Piso amostral da padronização expansiva e do β. Não é threshold novo: é o
# `MINIMO_PREGOES` de `view_cpi_transversal`, herdado de `breakeven_duration`.
MINIMO_PREGOES = 60

MARKET_ASSET = "SPY"


def componentes_expansivos(p_poly, spread):
    """`(z(p_poly), z(−spread))` — as duas parcelas da discordância, separadas.

    Existe como função à parte porque o `gate_recessao_2x2.py` precisa medir
    cada parcela sozinha (o poly sem o mercado, o mercado sem o poly) contra o
    mesmo livro. Recopiar a padronização lá daria duas definições do mesmo `z`,
    que divergem na primeira correção.
    """
    par = pd.concat([p_poly.rename("p"), (-spread).rename("s")], axis=1).dropna()
    z = {}
    for col in ("p", "s"):
        media = par[col].expanding(MINIMO_PREGOES).mean()
        desvio = par[col].expanding(MINIMO_PREGOES).std()
        z[col] = (par[col] - media) / desvio
    return z["p"], z["s"]


def divergencia_expansiva(p_poly, spread):
    """`z(p_poly) − z(−spread)` com média e desvio EXPANSIVOS.

    A diferença para o `nivel_divergencia_3_1.py` é toda aqui, e é a ressalva
    que aquele artefato declarou: lá o z usa média e desvio da amostra inteira
    (in sample), o que serve para dizer se HÁ sinal mas não é implementável. Aqui
    cada dia é padronizado só com o que já tinha acontecido — o `p_poly` do slot
    das 12:00 UTC de D e o spread de D−1 são conhecidos na abertura de D, então
    incluir o próprio dia na janela não é lookahead.
    """
    z_poly, z_mercado = componentes_expansivos(p_poly, spread)
    return (z_poly - z_mercado).dropna()


def beta_expansivo(retornos, divergencia, data, assets):
    """β de cada ativo contra a discordância, com dado estritamente anterior a D.

    Regressão do retorno de D+1 contra a discordância de D — é a sensibilidade
    PREDITIVA, que é o que esta view precisa (a 3.1 do módulo usa o β de absorção
    plena da 2.4, que mede outra coisa e depende do `k`). Mesma `estimate_betas`
    da 2.3, sem alterar.
    """
    passado = divergencia[divergencia.index < data]
    if len(passado) < MINIMO_PREGOES:
        return None
    seguinte = retornos.reindex(
        [retornos.index[retornos.index > d][0] if (retornos.index > d).any() else pd.NaT
         for d in passado.index])
    par = pd.DataFrame(seguinte[list(assets)].to_numpy(),
                       index=passado.index, columns=list(assets))
    par["__x"] = passado
    par = par.dropna()
    if len(par) < MINIMO_PREGOES:
        return None
    return estimate_betas(par[list(assets)].to_numpy(dtype=float),
                          par["__x"].to_numpy(dtype=float))


def coletar(args):
    """Registros (data, P, Q, h) das duas montagens, nos mesmos dias."""
    fechamento = load_etf_prices(args.precos)[list(ASSETS)]
    retornos = daily_returns(fechamento)

    sim = daily_preopen(series_by_slot(next(Path(args.dados).glob(PADRAO_SIM))))
    nao = daily_preopen(series_by_slot(next(Path(args.dados).glob(PADRAO_NAO))))
    par = pd.concat([sim.rename("sim"), nao.rename("nao")], axis=1).dropna()
    p_poly = pd.Series(
        binary_prob_series(par["sim"].to_numpy(), par["nao"].to_numpy()),
        index=par.index)
    pregoes = p_poly.index.intersection(retornos.index)
    p_poly = p_poly.loc[pregoes]
    spread = spread_defasado(load_fred(args.dgs10), load_fred(args.dtb3), pregoes)
    divergencia = divergencia_expansiva(p_poly, spread)

    registros = {"3.1 P neutro (módulo)": [], "3.1 P direcional (candidata)": []}
    for data, valor in divergencia.items():
        betas = beta_expansivo(retornos, divergencia, data, ASSETS)
        if betas is None:
            continue
        P = P_from_betas(betas, list(ASSETS), MARKET_ASSET)
        neutro = ViewResult(P=P, Q=float((P @ betas) * valor), diagnostics={})
        direcional = build_view_direcional(
            list(ASSETS), betas[list(ASSETS).index(MARKET_ASSET)], valor,
            MARKET_ASSET)
        registros["3.1 P neutro (módulo)"].append((data, neutro.P, neutro.Q, None))
        registros["3.1 P direcional (candidata)"].append(
            (data, direcional.P, direcional.Q, None))
    return retornos, divergencia, registros


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dados", default="data/raw/clob_exploracao")
    parser.add_argument("--precos", default="data/etf_prices_daily.parquet")
    parser.add_argument("--dgs10", default="data/raw/fred_DGS10.csv")
    parser.add_argument("--dtb3", default="data/raw/fred_DTB3.csv")
    parser.add_argument("--saida", default="Dump/analises/Recessao_direcional.md")
    args = parser.parse_args()

    retornos, divergencia, registros = coletar(args)

    saida = []
    escrever = saida.append
    escrever("# View 3.1 — P direcional × P neutro (D18d)\n")
    escrever("> Gerado por `scripts/view_3_1_direcional.py`. **Mede; não "
             "decide — e a entrada desta view está BLOQUEADA pela D2b/D18d.** "
             "Régua do `teste_sinal.py`: `r_P(D→D+h)` contra o `Q(D)` da própria "
             "montagem, com `r_P` começando em D+1.\n")
    escrever(f"- pregões medidos: **{len(registros['3.1 P direcional (candidata)'])}** "
             f"(discordância expansiva disponível em {len(divergencia)} dias)")
    escrever("- padronização e β **expansivos** — sem o z in sample que o "
             "`Nivel_divergencia_3_1.md` declarou como ressalva\n")
    escrever("| montagem | " + " | ".join(
        f"h = {h}: coef · t · acerto" for h in HORIZONTES) + " |")
    escrever("|" + "---|" * (len(HORIZONTES) + 1))
    for nome, regs in registros.items():
        celulas = []
        for h in HORIZONTES:
            coef, t, _, acerto = medir(regs, retornos, h)
            texto = f"{coef:+.3f} · t {t:+.2f} · {acerto:.0%}"
            celulas.append(f"**{texto}**" if abs(t) > 2 else texto)
        escrever(f"| {nome} | " + " | ".join(celulas) + " |")

    escrever("\n## O que a escolha de TESE faz com o mesmo número\n")
    escrever("O Q é linear no β, então trocar o sinal do β espelha o t. A linha "
             "de cima é o β **medido no dado** (\"prêmio de medo pago\"); a de "
             "baixo é a **tese original** da espec (mais recessão → cíclico "
             "cai). Nenhuma das duas é recomendação — a D18d pergunta ao grupo "
             "qual tese vale, e ela tem de ser declarada **antes**.\n")
    escrever("| tese | " + " | ".join(f"h = {h}" for h in HORIZONTES) + " |")
    escrever("|" + "---|" * (len(HORIZONTES) + 1))
    regs = registros["3.1 P direcional (candidata)"]
    for rotulo, sinal in (("β medido (prêmio de medo pago)", +1),
                          ("tese original da espec (β invertido)", -1)):
        celulas = []
        for h in HORIZONTES:
            espelhado = [(d, P, sinal * q, hd) for d, P, q, hd in regs]
            _, t, _, acerto = medir(espelhado, retornos, h)
            texto = f"t {t:+.2f} · {acerto:.0%}"
            celulas.append(f"**{texto}**" if abs(t) > 2 else texto)
        escrever(f"| {rotulo} | " + " | ".join(celulas) + " |")

    escrever("\n## Retorno do mercado contra a discordância (o sinal cru)\n")
    escrever("Sem view no meio: retorno de cada ativo em D+1..D+h contra a "
             "discordância expansiva de D. É a tabela do "
             "`Nivel_divergencia_3_1.md` refeita sem o z in sample.\n")
    escrever("| h | " + " | ".join(ASSETS) + " |")
    escrever("|" + "---|" * (len(ASSETS) + 1))
    datas = [d for d, _, _, _ in regs]
    x = divergencia.reindex(datas)
    for h in HORIZONTES:
        celulas = []
        for ativo in ASSETS:
            futuro = [retornos[ativo].reindex(
                retornos.index[retornos.index > d][:h]).sum()
                if len(retornos.index[retornos.index > d]) >= h else float("nan")
                for d in datas]
            coef, t, _ = ols(futuro, x.to_numpy())
            texto = f"{coef * 100:+.2f}%"
            celulas.append(f"**{texto}**" if abs(t) > 2 else texto)
        escrever(f"| {h} | " + " | ".join(celulas) + " |")
    escrever("\n> Janelas sobrepostas para h > 1: o |t| segue otimista, como no "
             "artefato original. O que muda aqui é só o z e o β, que deixaram "
             "de olhar o futuro.\n")

    escrever("\n## 🛑 Estabilidade do coeficiente dentro da própria amostra\n")
    escrever("**É a linha que a D18d precisa antes de discutir tese.** O mesmo "
             "coeficiente de SPY em h = 10, medido em pedaços da única amostra "
             "que existe (não há segundo mercado de recessão, então não há "
             "teste fora da amostra possível):\n")
    escrever("| recorte | pregões | período | coef SPY (h = 10) | t |")
    escrever("|---|---|---|---|---|")
    metade = len(divergencia) // 2
    recortes = (("amostra inteira", divergencia),
                ("1ª metade", divergencia.iloc[:metade]),
                ("2ª metade", divergencia.iloc[metade:]),
                ("dias com β (tabela acima)", divergencia.reindex(datas).dropna()))
    for rotulo, serie in recortes:
        futuro = [retornos["SPY"].reindex(
            retornos.index[retornos.index > d][:10]).sum()
            if len(retornos.index[retornos.index > d]) >= 10 else float("nan")
            for d in serie.index]
        coef, t, n = ols(futuro, serie.to_numpy())
        marca = "**" if abs(t) > 2 else ""
        escrever(f"| {rotulo} | {n} | {serie.index.min().date()} a "
                 f"{serie.index.max().date()} | {marca}{coef * 100:+.2f}%{marca} "
                 f"| {t:+.2f} |")
    escrever("\n> O sinal que a re-declaração de tese da D18d se apoiaria é o "
             "coeficiente desta coluna. Se ele **troca de sinal entre as "
             "metades**, a pergunta \"qual tese vale\" fica sem base medida — "
             "não porque a tese seja errada, mas porque a amostra não a "
             "sustenta em nenhuma direção.\n")

    Path(args.saida).write_text("\n".join(saida) + "\n", encoding="utf-8")
    sys.stdout.write("\n".join(saida) + f"\n\nescrito: {args.saida}\n")


if __name__ == "__main__":
    main()
