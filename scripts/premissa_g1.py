"""Premissa do G1 — o sinal do poly tem tamanho acima do tick? Felipe.

O gate da D17 mediu o G1 de UM jeito só: Δ de **um** pregão, na família do
**Fed**. Deu 0,2× e 0,5×, e a leitura registrada em `Gate_sleeves.md` foi que
"qualquer sleeve que leia Δ de PMF de um dia para o outro está condicionando em
ruído de discretização". A frase está certa e é forte — mas ela mistura duas
premissas que nunca foram medidas separadas:

  (a) **HORIZONTE.** O Δ de 1 pregão é pequeno e o tick é FIXO. Acumulando k
      pregões o sinal cresce (~√k num passeio aleatório, ~k se houver tendência
      de verdade) enquanto o tick não se mexe. A razão do G1 é função de k, e o
      gate só olhou k = 1. É exatamente a diferença entre a "velocidade de
      ajuste" (derivada, k = 1) e a "1.2 momentum" (tendência sustentada,
      k grande) — duas candidatas que o `Candidatos_taticos.md` trata como a
      mesma leitura da mesma série.

  (b) **FAMÍLIA.** Todas as sleeves já medidas leem Fed ou CPI, que é onde o
      poly é mais preciso: a D16 achou surpresa mediana de 0,52 bps em 17
      reuniões. Mercado com incerteza VIVA (recessão, geopolítica, eleição)
      reprecifica em outra escala. O dado do Paulo tem sete desses, todos
      binários, e nenhum foi medido — nem no gate, nem em lugar nenhum.

Este script mede o G1 nas duas dimensões de uma vez: uma linha por mercado, uma
coluna por horizonte. **Mede; não decide** — mesma regra do gate, nenhum corte
numérico cravado. As duas linhas do Fed que a D17 já reprovou entram como
controle: são as únicas cujo veredito em k = 1 se conhece de antemão.

⚠️ **G1 é condição NECESSÁRIA, não suficiente.** Passar do tick só diz que o
sinal existe acima da granularidade do preço. Se ele prevê retorno é o G2; e
segurar k pregões de exposição para colher um Δ de k pregões tem custo que só o
G4 mede. Uma linha alta aqui é licença para rodar o próximo critério, não para
escrever módulo.

**Nada em `src/` é tocado e nenhuma matemática nova é escrita:** `razao_dispersao`
e as leituras de PMF vêm do `gate_sleeves.py` como estão.

Uso:

    python scripts/premissa_g1.py --raiz .
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from backtest_v1 import carregar  # noqa: E402
from gate_sleeves import (TICK, pmf_cpi_do_dia, pmf_fomc_do_dia,  # noqa: E402
                          pmf_m3_diaria, razao_dispersao, serie_por_dia)
from poly_loader import daily_preopen, series_by_slot  # noqa: E402
from poly_preprocessing import pmf_mean  # noqa: E402

# Horizontes em PREGÕES. É uma GRADE, não uma escolha: o que responde a premissa
# é a CURVA da razão contra k, não um k. Cravar um seria escolher parâmetro sem
# medição (CLAUDE.md §6). k = 1 é o do gate; k = 20 é ~1 mês de pregão.
HORIZONTES = (1, 2, 3, 5, 10, 20)

# Mercados binários fora da família Fed/CPI, como entregues pelo Paulo. Num
# binário o sinal É a probabilidade, então um tick de 1 centavo desloca o sinal
# em exatamente TICK — não há grade de balde para escalar, ao contrário da PMF.
# Chave = rótulo na tabela; valor = prefixo do nome do arquivo.
BINARIOS = {
    "M4 recessão EUA 2025": "M4_recession_",
    "M5 Trump 2024": "M5_trump_2024_",
    "M6 tarifas China": "M6_china_tariffs_",
    "M7 ação militar Irã (jun/2025)": "M7_iran_jun2025_",
    "M7 ataque ao Irã (fev/2026)": "M7_iran_strike_",
    "M8 reconciliação fiscal": "M8_obbb_debt_",
    "M9 Senado": "M9_midterms_2022_which-party-will-control-the-us-senate-a",
    "M9 Câmara": "M9_midterms_2022_will-the-democratic-party-control-the-ho",
}


def serie_binaria(diretorio, prefixo):
    """Série diária pré-abertura de p(SIM) de um mercado binário.

    O `_NO` é o token do outro lado do mesmo mercado (midpoints independentes,
    p_sim + p_nao != 1) — ler os dois seria contar o mesmo mercado duas vezes.
    Mercado entregue sem série (`{"history": []}`) devolve série vazia; quem
    chama decide, aqui não é erro.
    """
    arquivos = [p for p in sorted(Path(diretorio).glob(f"{prefixo}*.json"))
                if not p.stem.endswith("_NO")]
    if not arquivos:
        raise FileNotFoundError(f"nenhum arquivo com prefixo {prefixo!r} em {diretorio}")
    return daily_preopen(series_by_slot(arquivos[0]))


def em_pregoes(serie):
    """Reindexa a série na grade de dias úteis da vida do próprio mercado.

    Sem isso `.diff(k)` anda k LEITURAS, não k pregões — e leituras faltantes de
    24/36/48h existem no dado (documentadas no `poly_loader`). Num sweep de
    horizonte o erro cresce com k, então a reindexação é o que faz a coluna
    "k = 20" querer dizer 20 pregões.

    Feriado de bolsa vira NaN e sai da mediana pelo `dropna` do
    `razao_dispersao` — é o preço de não carregar calendário de bolsa numa
    medida de dispersão. Por isso o k = 1 das linhas do Fed pode divergir na
    última casa do que está no `Gate_sleeves.md`, que difere leituras
    consecutivas.
    """
    serie = pd.Series(serie).dropna()
    if serie.empty:
        return serie
    return serie.reindex(pd.bdate_range(serie.index.min(), serie.index.max()))


def tick_de_grade(datas, por_dia):
    """0,01 × amplitude MEDIANA da grade de baldes — mesma régua do gate.

    Um centavo num único balde desloca a média da PMF em no máximo
    `0,01 × (maior valor de balde − menor)`, e a grade do CPI muda mês a mês.
    """
    larguras = []
    for data in datas:
        par = por_dia(data)
        if par:
            valores = np.asarray(par[1], dtype=float)
            larguras.append(float(valores.max() - valores.min()))
    return TICK * float(np.median(larguras)) if larguras else float("nan")


def linha_da_tabela(nome, familia, serie, tick, unidade):
    """Uma linha: contexto + razão G1/tick em cada horizonte da grade."""
    serie = em_pregoes(serie)
    if serie.dropna().empty:
        return None
    vivos = serie.dropna()
    razoes = {f"k={k}": razao_dispersao(serie.diff(k), tick) for k in HORIZONTES}
    return {
        "mercado": nome,
        "família": familia,
        "dias": len(vivos),
        "janela": f"{vivos.index[0]:%Y-%m} → {vivos.index[-1]:%Y-%m}",
        "tick no sinal": f"{tick:.4g} {unidade}",
        **razoes,
    }


def series_dos_mercados(raiz):
    """`(series, retornos, montador, datas)` — as séries de todos os mercados.

    `series` é `[(nome, família, série diária, tick no sinal, unidade)]`. Um
    lugar só para a lista de mercados e para a régua do tick de cada um: o sweep
    de horizonte, o teste de tendência (`premissa_tendencia.py`) e o G2/G3 do M3
    (`gate_m3_acumulado.py`) leem exatamente as mesmas séries, e cópias
    divergiriam na primeira correção.

    O que o `carregar` trouxe sai junto para quem precisa estimar μ não ter de
    recarregar o dataset inteiro só para isso.
    """
    raiz = Path(raiz)
    retornos, montador, datas, _ = carregar(raiz)
    fl = montador._fl
    diretorio = raiz / "data/raw/clob_exploracao"

    # --- família Fed/CPI: as mesmas leituras que o gate faz ------------------
    m3_probs, m3_valores = pmf_m3_diaria(diretorio)

    def e_poly_m3(data):
        if data not in m3_probs.index:
            return None
        linha = m3_probs.loc[data].to_numpy(dtype=float)
        return pmf_mean(linha, m3_valores, fl) if np.isfinite(linha).all() else None

    def e_poly_cpi(data):
        par = pmf_cpi_do_dia(montador, data)
        return pmf_mean(*par, fl) if par else None

    def e_poly_fomc(data):
        par = pmf_fomc_do_dia(montador, data)
        return pmf_mean(*par, fl) if par else None

    series = [
        ("C1a M3 trajetória do Fed (nº de cortes)", "Fed · controle D17",
         serie_por_dia(datas, e_poly_m3),
         TICK * float(m3_valores.max() - m3_valores.min()), "cortes"),
        ("C1b reunião do FOMC (E_poly em bps)", "Fed · controle D17",
         serie_por_dia(datas, e_poly_fomc),
         tick_de_grade(datas, lambda d: pmf_fomc_do_dia(montador, d)), "bps"),
        # O `carregar` guarda os valores do CPI já divididos por 100
        # (`backtest_v1.py:134`), então a unidade é FRAÇÃO mensal, não p.p. A
        # razão do G1 é invariante a escala; o rótulo não.
        ("CPI mensal (E_poly)", "CPI",
         serie_por_dia(datas, e_poly_cpi),
         tick_de_grade(datas, lambda d: pmf_cpi_do_dia(montador, d)), "frac./mês"),
    ]
    # --- famílias nunca medidas: os binários ---------------------------------
    for nome, prefixo in BINARIOS.items():
        series.append((nome, "binário (nunca medido)",
                       serie_binaria(diretorio, prefixo), TICK, "prob."))
    return series, retornos, montador, datas


def main():
    # O console do Windows abre em cp1252 e engasga nos rótulos acentuados.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raiz", default=".")
    parser.add_argument("--saida", default="Dump/analises/Premissa_G1.md")
    args = parser.parse_args()

    linhas, ignorados = [], []
    series, *_ = series_dos_mercados(args.raiz)
    for nome, familia, serie, tick, unidade in series:
        linha = linha_da_tabela(nome, familia, serie, tick, unidade)
        (linhas if linha else ignorados).append(linha or nome)

    tabela = pd.DataFrame(linhas)
    formatada = tabela.copy()
    for k in HORIZONTES:
        formatada[f"k={k}"] = tabela[f"k={k}"].map(
            lambda v: f"{v:.1f}×" if np.isfinite(v) else "—")

    # --- leitura, GERADA dos números (prosa e tabela não podem divergir) -----
    por_nome = tabela.set_index("mercado")
    binarios = [n for n in por_nome.index if por_nome.loc[n, "família"].startswith("binário")]
    fed = [n for n in por_nome.index if n.startswith(("C1a", "C1b"))]

    def melhor_k(nome):
        razoes = {k: por_nome.loc[nome, f"k={k}"] for k in HORIZONTES}
        finitos = {k: v for k, v in razoes.items() if np.isfinite(v)}
        return max(finitos, key=finitos.get) if finitos else None

    def cruza_em(nome):
        """Menor k da grade em que a razão passa de 1× (None = nunca passa)."""
        for k in HORIZONTES:
            v = por_nome.loc[nome, f"k={k}"]
            if np.isfinite(v) and v > 1.0:
                return k
        return None

    fed_cruza = {n: cruza_em(n) for n in fed}
    bin_cruza = {n: cruza_em(n) for n in binarios}
    bin_em_1 = [n for n in binarios if np.isfinite(por_nome.loc[n, "k=1"])
                and por_nome.loc[n, "k=1"] > 1.0]

    texto = [
        "# Premissa do G1 — horizonte × família\n",
        "> Gerado por `scripts/premissa_g1.py`. **Mede; não decide.** Nenhum "
        "corte cravado, mesma regra do `Gate_sleeves.md`.\n",
        "O gate da D17 mediu o G1 num ponto só do espaço — **Δ de 1 pregão, "
        "família do Fed** — e a leitura virou regra geral: *\"qualquer sleeve "
        "que leia Δ de PMF de um dia para o outro está condicionando em ruído "
        "de discretização\"*. Esta tabela testa as duas premissas embutidas "
        "nessa generalização: que o resultado não depende do **horizonte** (as "
        "colunas) nem da **família de mercado** (as linhas).\n",
        "- **razão** = mediana |Δ do sinal em k pregões| ÷ Δ que UM tick de 1 "
        "centavo produz no sinal. Abaixo de 1× o sinal É o ruído de "
        "discretização do preço.",
        "- **binário**: o sinal é a própria probabilidade, então o tick é o "
        "centavo — não há grade de balde para escalar.",
        "- séries reindexadas em dias úteis antes do `diff`, para que `k` "
        "signifique pregões e não leituras (o dado tem buracos de 24/36/48h).\n",
        "⚠️ **G1 é condição NECESSÁRIA, não suficiente.** Passar do tick diz "
        "que o sinal existe acima da granularidade do preço — não que ele "
        "prevê retorno (G2) nem que sobrevive ao custo de segurar k pregões de "
        "exposição (G4).\n",
        formatada.to_markdown(index=False), "",
        "## Leitura\n",
    ]

    # (a) horizonte
    cruzam = {n: k for n, k in fed_cruza.items() if k is not None}
    if cruzam:
        texto.append(
            "**A premissa do horizonte NÃO se sustenta como regra geral.** "
            + " · ".join(f"{n} cruza 1× em k = {k}" for n, k in cruzam.items())
            + ". O tick é fixo e o sinal acumula, então o veredito do gate "
            "vale para o k que o gate mediu — não para a série. Isso separa "
            "a *velocidade de ajuste* (derivada, k = 1) da *1.2 momentum* "
            "(tendência, k grande): são leituras da mesma série em pontos "
            "diferentes desta curva, e só a primeira está medida como morta.\n")
    else:
        texto.append(
            "**A premissa do horizonte se sustenta na família do Fed.** "
            "Nenhuma das duas linhas do Fed cruza 1× em nenhum k da grade "
            f"(até k = {HORIZONTES[-1]}) — acumular pregões não tira o sinal "
            "de dentro do tick. O veredito da D17 não era artefato de k = 1, "
            "e isso mata a *velocidade de ajuste* e a *1.2 momentum* juntas, "
            "que são a mesma série em dois horizontes.\n")

    # (b) família
    def com_dias(nomes, k):
        return " · ".join(
            f"**{n}** {por_nome.loc[n, f'k={k}']:.1f}× em "
            f"{por_nome.loc[n, 'dias']} dias" for n in nomes)

    if bin_em_1:
        texto.append(
            "**A premissa da família NÃO se sustenta — mas o que a derruba não "
            "é \"não-Fed\", é NOTÍCIA.** Passam de 1× já em k = 1: "
            + com_dias(bin_em_1, 1)
            + ". São mercados de evento discreto (geopolítica, tarifa, "
            "votação), que reprecificam quando chega notícia. Já os binários de "
            "pergunta permanente ficam junto do Fed, abaixo do tick: "
            + com_dias([n for n in binarios if n not in bin_em_1], 1)
            + ". O corte não é a família do mercado, é se existe fluxo de "
            "notícia a que o preço responda. **Nenhuma sleeve do projeto jamais "
            "leu nenhum destes** — as 13 tentativas leram Fed ou CPI.\n")
    else:
        texto.append(
            "**A premissa da família se sustenta:** nenhum binário passa de "
            "1× em k = 1. O problema de tamanho não é da família do Fed, é "
            "do dado do poly na frequência diária.\n")

    passam = {n: k for n, k in bin_cruza.items() if k is not None}
    if passam:
        texto.append(
            "Binários que cruzam 1× em algum horizonte da grade: "
            + " · ".join(f"**{n}** (k = {k}, máximo em k = {melhor_k(n)})"
                         for n, k in passam.items())
            + ".\n")

    # (c) a tensão que decide se algo disto vira sleeve. GERADA, não escrita: o
    # conjunto que passa o tick em k = 1 e o conjunto com cobertura são quase
    # disjuntos, e a tabela precisa dizer isso sem eu cravar corte de dias.
    passa_k1 = [n for n in por_nome.index if np.isfinite(por_nome.loc[n, "k=1"])
                and por_nome.loc[n, "k=1"] > 1.0]
    mais_longo = max(por_nome.index, key=lambda n: por_nome.loc[n, "dias"])
    texto.append("### Cobertura × dispersão — as duas andam em direções opostas\n")
    if passa_k1:
        longo_k1 = max(passa_k1, key=lambda n: por_nome.loc[n, "dias"])
        texto.append(
            "Quem passa o tick em k = 1, e com quanta cobertura: "
            + com_dias(passa_k1, 1)
            + f". O de maior cobertura entre eles é **{longo_k1}** "
            f"({por_nome.loc[longo_k1, 'dias']} dias), contra "
            f"{por_nome.loc[mais_longo, 'dias']} dias do mercado mais longo da "
            f"tabela ({mais_longo}). **Sleeve precisa das duas:** G0 sem G1 é "
            "condicionar em ruído de discretização (foi o que matou C1a e C1b), "
            "e G1 sem G0 não tem quantos dias para virar carteira — um mercado "
            "de 9 pregões não sustenta overlay, por mais que se mexa.\n")
    texto.append(
        "> ⚠️ **O E_poly do CPI já tem dono.** A divergência da view 2.2 é "
        "construída dessa mesma série (`gate_sleeves.py`, referências do G3), "
        "então a linha do CPI aqui não é candidata livre: qualquer sleeve sobre "
        "ela cai no G3 antes de chegar ao G4. Ela está na tabela como régua de "
        "escala, não como vaga aberta.\n")

    if ignorados:
        texto.append("**Sem série utilizável** (entregues vazios ou sem "
                     "leitura na grade): " + " · ".join(ignorados) + ".\n")

    texto.append(
        "**O que isto NÃO diz:** que existe sleeve. Diz em que ponto do espaço "
        "(horizonte × família) o sinal do poly sai de dentro do tick — que é a "
        "primeira condição, e a única que custa um script. O G2 (μ contra "
        "premissa declarada) e o G3 (duplicação com as views vivas) continuam "
        "por rodar, e a âncora de tamanho da D16 continua de pé e sem uso.\n")

    Path(args.saida).write_text("\n".join(texto) + "\n", encoding="utf-8")
    sys.stdout.write(formatada.to_string(index=False) + f"\n\nescrito: {args.saida}\n")


if __name__ == "__main__":
    main()
