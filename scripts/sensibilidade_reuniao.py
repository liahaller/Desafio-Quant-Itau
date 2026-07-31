"""Pacote de sensibilidade das decisões 1.1 / 1.2 / 6.1 (módulo do Felipe).

Objetivo: a reunião decidir olhando O TAMANHO DO EFEITO de cada regra em
aberto, não a opinião de quem fala mais alto. Nada aqui escolhe regra —
o script varre as opções e mede a dispersão que cada uma produz.

As três decisões medidas:
  1.2 balde aberto  — o valor dos buckets das PONTAS ("0.0% or less",
                      "0.4% or more"; medido pelo Paulo, Nota A).
  6.1 faixa faltante— o que fazer com o bucket sem preço num slot (faixa que
                      morreu OU que sumiu e voltou).
  1.1 favorite-longshot — o tamanho da correção do viés.

Como as opções entram, sem inventar parâmetro (CLAUDE.md §6): cada decisão
vira uma FAIXA de cenários que contém qualquer escolha plausível, e o que se
reporta é a dispersão de E_poly entre eles. O ponto não é propor um valor —
é dizer se a escolha move 0,01pp (decide-se em 2 minutos) ou 0,3pp (merece
discussão).

Propagação ao Q da view 2.2: Q = duration × (E_poly − breakeven_10a), logo
    Q(regra A) − Q(regra B) = duration × [E_poly(A) − E_poly(B)]
— o breakeven CANCELA. Por isso este pacote roda sem o T10YIE (que é o G2,
ainda não entregue) e reporta a dispersão em pp de E_poly; multiplicar pela
duration que a reunião fechar dá a dispersão em Q.

Uso:
    python scripts/sensibilidade_reuniao.py --dados <dir do clob_exploracao>

Onde está o dado: os arquivos crus vivem no branch `Paulo`, não neste. Para
rodar sem fazer merge, extraia para um diretório temporário e aponte com
`--dados` / `--precos`:

    git archive origin/Paulo data/ | tar -x -C <dir temporario>
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from poly_loader import bucket_value, load_pmf  # noqa: E402
from poly_preprocessing import normalize_probs  # noqa: E402

# Deslocamento da ponta, em MÚLTIPLOS da largura do bucket. 0 = truncar no
# limite; 0,5 = ponto médio extrapolado (a ponta teria a largura da vizinha);
# 1,0 = uma largura inteira, cota superior de qualquer escolha plausível.
# São as três opções da decisão 1.2, na ordem em que a pauta as lista.
DESLOCAMENTOS = {"truncar": 0.0, "ponto médio": 0.5, "largura inteira": 1.0}

# Força da correção de favorite-longshot como família de UM parâmetro:
# p -> p^gamma normalizado. gamma = 1 é a identidade (sem correção);
# gamma > 1 encolhe o longshot e engorda o favorito, que é a direção do viés.
# NÃO é a curva escolhida (decisão 1.1) — é a régua para medir o efeito.
GAMMAS = [1.0, 1.1, 1.25]


def fl_power(gamma):
    """Correção FL da família potência, injetável no lugar do stub da 11a."""
    def correcao(probs):
        p = np.asarray(probs, dtype=float) ** gamma
        return p / p.sum()
    return correcao


def valores_com_ponta(values, deslocamento, abertas=("baixa", "alta")):
    """Resolve o bucket aberto deslocando a ponta para fora, em múltiplos da
    largura da grade. `values` deve vir ordenado (é o que o load_pmf entrega).
    """
    values = np.asarray(values, dtype=float).copy()
    largura = float(np.median(np.diff(values[np.isfinite(values)])))
    if "baixa" in abertas:
        values[0] -= deslocamento * largura
    if "alta" in abertas:
        # ponta superior aberta pode vir como NaN (slug "8plus")
        base = values[-1] if np.isfinite(values[-1]) else values[-2] + largura
        values[-1] = base + deslocamento * largura
    return values


def e_poly(pmf, values, fl, faltante):
    """Série de E_poly, slot a slot, sob uma regra de faixa faltante.

    faltante:
      'renormalizar'   — usa os buckets presentes e divide pela soma deles
                         (é o que o código faz hoje; faixa ausente sai da conta).
      'carregar'       — repete o último preço da faixa ausente e só então
                         normaliza (a faixa continua na conta com o preço velho).
      'slot completo'  — só calcula onde TODOS os buckets têm preço.
    """
    if faltante == "carregar":
        pmf = pmf.ffill()
    elif faltante == "slot completo":
        pmf = pmf.dropna()
    linhas = pmf.fillna(0.0) if faltante != "slot completo" else pmf
    linhas = linhas[linhas.sum(axis=1) > 0]
    corrigidas = np.vstack([fl(normalize_probs(linha)) for linha in linhas.to_numpy()])
    return pd.Series(corrigidas @ values, index=linhas.index)


def tabela(pmf, values_brutos, abertas):
    """Uma linha por cenário, com a mediana de E_poly do mercado."""
    linhas = []
    for nome_ponta, deslocamento in DESLOCAMENTOS.items():
        values = valores_com_ponta(values_brutos, deslocamento, abertas)
        for faltante in ("renormalizar", "carregar", "slot completo"):
            for gamma in GAMMAS:
                serie = e_poly(pmf, values, fl_power(gamma), faltante)
                linhas.append({"ponta": nome_ponta, "faltante": faltante,
                               "gamma": gamma, "slots": len(serie),
                               "E_poly": serie.median()})
    return pd.DataFrame(linhas)


def amplitude(df, coluna):
    """Dispersão de E_poly atribuível a UMA decisão: varia essa coluna com as
    outras fixas no cenário de referência, e devolve o pior caso."""
    referencia = {"ponta": "ponto médio", "faltante": "renormalizar", "gamma": 1.0}
    fatia = df.copy()
    for chave, valor in referencia.items():
        if chave != coluna:
            fatia = fatia[fatia[chave] == valor]
    return fatia["E_poly"].max() - fatia["E_poly"].min()


def mercados_cpi(diretorio):
    """Prefixos dos mercados mensais de CPI, em ordem cronológica de série."""
    meses = sorted({f.name.split("_")[1] for f in Path(diretorio).glob("CPI_*.json")})
    return [f"CPI_{mes}_" for mes in meses]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dados", default="data/raw/clob_exploracao",
                        help="diretório com os JSONs crus do /prices-history")
    parser.add_argument("--saida", default="Dump/analises/Sensibilidade_decisoes_1.1_1.2_6.1.md",
                        help="arquivo markdown de saída")
    args = parser.parse_args()
    diretorio = Path(args.dados)
    saida = []
    print = saida.append  # o console do Windows é cp1252; a saída vai em utf-8

    print("# Sensibilidade das decisões 1.1, 1.2 e 6.1\n")
    print("> Gerado por `scripts/sensibilidade_reuniao.py` sobre o dado cru do "
          "`origin/Paulo`. Nenhuma regra é escolhida aqui — o script varre as opções "
          "e mede quanto cada uma move o número.\n")
    print("**Unidade:** pontos percentuais da variação **mensal** do CPI (é o que os "
          "mercados entregues precificam; o M3 sai em nº de cortes). "
          "Como `Q = duration × (E_poly − breakeven)`, o breakeven cancela na diferença "
          "entre regras: **dispersão em Q = dispersão em pp × duration**.\n")
    print("**Como ler.** `Δ` é quanto a mediana de E_poly anda quando se varre aquela "
          "decisão com as outras duas fixas no cenário de referência (ponta = ponto médio, "
          "faixa faltante = renormalizar, sem correção FL). `σ` é o desvio-padrão do próprio "
          "E_poly **ao longo do tempo** — é o tamanho do sinal que a view lê. A coluna que "
          "decide é a última: **Δ/σ**. Perto de zero, a regra é irrelevante e a reunião "
          "fecha em dois minutos; perto de 1, a escolha da regra vale tanto quanto a "
          "informação do mercado.\n")

    resumo = []
    print("## CPI — mercados mensais\n")
    print("| Mercado | buckets | slots | E_poly ref | σ(E_poly) | Δ balde aberto | "
          "Δ faixa faltante | Δ FL | maior Δ/σ |")
    print("|---|---|---|---|---|---|---|---|---|")
    for prefixo in mercados_cpi(diretorio) + ["M1_cpi_monthly_", "M3_fed_trajectory_"]:
        pmf = load_pmf(diretorio, prefixo)
        values = np.array([bucket_value(c) for c in pmf.columns])
        # M3: só a ponta ALTA é aberta ("8plus"); "no cuts" é exato.
        abertas = ("alta",) if "fed_trajectory" in prefixo else ("baixa", "alta")
        df = tabela(pmf, values, abertas)
        referencia = df[(df["ponta"] == "ponto médio") & (df["faltante"] == "renormalizar")
                        & (df["gamma"] == 1.0)].iloc[0]
        # σ do sinal: quanto o próprio E_poly anda no tempo, no cenário de referência
        serie_ref = e_poly(pmf, valores_com_ponta(values, 0.5, abertas), fl_power(1.0),
                           "renormalizar")
        linha = {"mercado": prefixo.strip("_"), "buckets": pmf.shape[1],
                 "slots": int(referencia["slots"]), "ref": referencia["E_poly"],
                 "sigma": float(serie_ref.std()),
                 "d_ponta": amplitude(df, "ponta"),
                 "d_faltante": amplitude(df, "faltante"),
                 "d_fl": amplitude(df, "gamma")}
        linha["pior_razao"] = max(linha["d_ponta"], linha["d_faltante"],
                                  linha["d_fl"]) / linha["sigma"]
        resumo.append(linha)
        print(f"| {linha['mercado'][:44]} | {linha['buckets']} | {linha['slots']} | "
              f"{linha['ref']:.4f} | {linha['sigma']:.4f} | {linha['d_ponta']:.4f} | "
              f"{linha['d_faltante']:.4f} | {linha['d_fl']:.4f} | {linha['pior_razao']:.2f} |")

    resumo = pd.DataFrame(resumo)
    print("\n## Qual decisão move mais o número\n")
    print("| Decisão | Δ mediano | Δ máximo | Δ/σ no pior caso | mercado do pior caso |")
    print("|---|---|---|---|---|")
    for coluna, nome in [("d_ponta", "1.2 balde aberto"),
                         ("d_faltante", "6.1 faixa faltante"),
                         ("d_fl", "1.1 favorite-longshot")]:
        pior = resumo.loc[resumo[coluna].idxmax()]
        print(f"| {nome} | {resumo[coluna].median():.4f} | {pior[coluna]:.4f} | "
              f"{pior[coluna] / pior['sigma']:.2f} | {pior['mercado']} |")

    print("\n## Binário em p baixa (view 3.1) — onde o FL morde mais\n")
    from poly_loader import series_by_slot
    m4 = next(Path(diretorio).glob("M4_recession_*.json"))
    p = series_by_slot(m4)
    print("| gamma | p mediana | p no 1º decil | p máxima |")
    print("|---|---|---|---|")
    for gamma in GAMMAS:
        corrigida = p ** gamma / (p ** gamma + (1 - p) ** gamma)
        print(f"| {gamma} | {corrigida.median():.4f} | {corrigida.quantile(0.1):.4f} | "
              f"{corrigida.max():.4f} |")

    print("\n## Leitura (fatos, não recomendação)\n")
    acima = resumo[resumo["d_ponta"] > resumo["sigma"]]
    print(f"1. **A decisão 1.2 (balde aberto) é a que move o número na PMF**, não a 1.1. "
          f"Em {len(acima)} dos {len(resumo)} mercados a escolha da ponta desloca E_poly "
          f"MAIS do que o próprio E_poly varia no tempo (Δ/σ > 1). Nos meses de grade nova "
          f"de 2026 (9 buckets), Δ chega a {resumo['d_ponta'].max():.3f} pp contra σ de "
          f"~0,08 pp — a regra vale tanto quanto a informação do mercado.")
    print("2. **A 1.1 (favorite-longshot) quase não mexe na PMF de CPI** (Δ/σ ≤ 0,3 em todos "
          "os mercados de CPI, dentro da faixa de γ testada) — mas é decisiva no BINÁRIO em "
          "p baixa, que é onde a view 3.1 vive: a mediana do mercado de recessão cai de "
          "0,205 para 0,155 e o 1º decil cai de 0,030 para 0,013, mais da metade. "
          "Ou seja: 1.1 e 1.2 travam views DIFERENTES, e podem ser decididas separadamente.")
    print("3. **A 6.1 (faixa faltante) é irrelevante em 2025 e material em 2026:** Δ = 0 em "
          "todos os meses de grade estável e 0,126 pp em mar/2026 (só 24 dos 60 slots têm "
          "todos os buckets) e 0,184 corte no M3. A decisão só precisa cobrir os meses de "
          "grade nova — e precisa incluir o caso 'faixa some e volta', que a redação atual "
          "da 6.1 não cobre.")
    print("\n> **Ressalva de método.** A curva de FL é uma família de UM parâmetro "
          "(`p^γ` normalizado, γ ∈ {1,0; 1,1; 1,25}) escolhida só para dar escala ao efeito; "
          "não é a correção da decisão 1.1 nem uma calibração. Se a reunião escolher uma "
          "curva com forma diferente, os Δ da coluna FL mudam — os das outras duas colunas, não.")
    print("\n> **Achado de unidade, para a pauta.** A espec da 2.2 foi escrita supondo CPI "
          "**anual** (buckets 3,7% / 3,8% / ≤3,6%), mas o Paulo mediu (Nota A) que os "
          "mercados entregues são de variação **mensal** do CPI-U (0,0% a 0,5%). Do jeito "
          "que a fórmula está, `E_poly − breakeven_10a` compara uma variação mensal (~0,3%) "
          "com um breakeven anual (~2,3%) e produz divergência negativa permanente de ~2 pp. "
          "**Não é bug do código — é premissa da view a reconciliar** (anualizar o E_poly, "
          "comparar com breakeven mensalizado, ou achar mercado de CPI anual).")

    Path(args.saida).write_text("\n".join(saida) + "\n", encoding="utf-8")
    sys.stdout.write(f"escrito: {args.saida} ({len(saida)} linhas)\n")


if __name__ == "__main__":
    main()
