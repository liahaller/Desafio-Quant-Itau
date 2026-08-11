"""O sinal acumulado é TENDÊNCIA ou CONVERGÊNCIA? Felipe.

O `Premissa_G1.md` mostrou que a razão sinal/tick cresce com o horizonte: o M3
sai de 0,5× em 1 pregão para 3,7× em 20. Isso derrubou o veredito da D17 como
regra geral — mas **não** basta para dizer que existe algo negociável, e a
diferença é o que este script mede.

Duas leituras explicam o mesmo crescimento, e só uma vira sleeve:

  - **TENDÊNCIA.** Os movimentos se encadeiam: quem subiu ontem tende a subir
    hoje. É informação disponível ANTES, e é negociável.
  - **CONVERGÊNCIA.** A probabilidade caminha para o desfecho à medida que a
    data chega. Também produz acumulação — e é inútil, porque o destino só se
    conhece depois. Um mercado que vai de 0,30 para 1,00 ao longo de meses
    "tem tendência" em retrospecto e não dava nenhum sinal no meio do caminho.

O separador é a **autocorrelação dos incrementos**, e ela precisa de um cuidado
que é o ponto central deste script: uma deriva constante (que é a cara da
convergência) já produz autocorrelação positiva no incremento BRUTO, sem
nenhuma previsibilidade real. Por isso a mesma medida sai duas vezes:

  - **ρ bruto** — com a deriva dentro.
  - **ρ demeanado** — com a deriva tirada pela média EXPANSIVA do próprio sinal
    (`demeanar_expansivo` do gate, convenção D9/D7.4 que as views 2.2 e 2.3 já
    usam: só passado, sem lookahead).

**O ρ demeanado é a parte ex-ante.** A distância entre os dois é o tamanho da
deriva. Se ρ demeanado morre em zero, o crescimento do G1 é convergência mais
ruído acumulando, e não há o que operar por mais horizonte que se dê.

O **variance ratio** entra como controle da medida anterior: se o crescimento
fosse só ruído se somando, VR ficaria em 1 e a mediana cresceria com √k. VR
acima de 1 diz que os incrementos se somam de verdade — sem dizer se isso é
tendência ou deriva, que é justamente o que o ρ separa.

⚠️ **Incrementos NÃO sobrepostos** no ρ: com sobreposição, incrementos vizinhos
compartilham pregões e a autocorrelação sai positiva por construção. O preço é
`n` pequeno em k grande (210 pregões ÷ 20 = 10 pontos), e por isso o `n` vai na
tabela — sem ele o ρ de k = 20 é indistinguível de acaso.

**Nada em `src/` é tocado.** As séries são as MESMAS do `premissa_g1.py`,
importadas de lá.

Uso:

    python scripts/premissa_tendencia.py --raiz .
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gate_sleeves import corr_comum, demeanar_expansivo  # noqa: E402
from premissa_g1 import HORIZONTES, em_pregoes, series_dos_mercados  # noqa: E402


def variance_ratio(serie, k):
    """VR(k) = Var(Δk) ÷ (k · Var(Δ1)). Passeio aleatório -> 1.

    Acima de 1 os incrementos se SOMAM (persistência); abaixo, se cancelam
    (reversão). É a versão em variância do que a `razao_dispersao` mede em
    mediana — se o crescimento do sinal com o horizonte fosse só ruído
    acumulando, VR ficaria em 1 e a mediana cresceria com √k.

    Incrementos sobrepostos (mais pontos), SEM a correção de viés de
    Lo-MacKinlay: ela puxa VR para baixo em amostra pequena, e o uso aqui é
    comparar linhas da mesma tabela, onde o viés é comum a todas. Série curta
    demais ou constante -> NaN.
    """
    serie = pd.Series(serie).astype(float)
    d1 = serie.diff().dropna()
    dk = serie.diff(k).dropna()
    if len(d1) < 2 or len(dk) < 2 or not np.isfinite(d1.var()) or d1.var() <= 0:
        return float("nan")
    return float(dk.var() / (k * d1.var()))


def incrementos_nao_sobrepostos(serie, k):
    """Incrementos de k pregões que não compartilham nenhum dia entre si.

    `diff(k)` na posição i é `s[i] − s[i−k]`; pegar de k em k a partir de k dá
    as janelas [0,k], [k,2k], ... A série precisa vir reindexada em dias úteis
    (`em_pregoes`), senão "k posições" não é "k pregões".
    """
    return pd.Series(serie).diff(k).iloc[k::k].dropna()


def rho_com_t(incrementos):
    """`(ρ, t, n)` da autocorrelação de lag 1 de uma série de incrementos.

    `t = ρ·√(n−2) ÷ √(1−ρ²)` é o t de Student padrão do coeficiente de Pearson.
    Ele está aqui porque sem `n` o ρ de horizonte longo é ilegível: com 10
    pontos, |ρ| de 0,3 é acaso. Menos de 4 pares -> `(NaN, NaN, n)`.
    """
    inc = pd.Series(incrementos).dropna()
    n = len(inc) - 1
    if n < 4:
        return float("nan"), float("nan"), max(n, 0)
    rho = corr_comum(inc, inc.shift(1))
    if not np.isfinite(rho) or abs(rho) >= 1.0:
        return rho, float("nan"), n
    return rho, float(rho * np.sqrt(n - 2) / np.sqrt(1 - rho ** 2)), n


def main():
    # O console do Windows abre em cp1252 e engasga nos rótulos acentuados.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raiz", default=".")
    parser.add_argument("--saida", default="Dump/analises/Premissa_tendencia.md")
    args = parser.parse_args()

    vr, rho_dem, rho_bruto, medidas = [], [], [], {}
    series, *_ = series_dos_mercados(args.raiz)
    for nome, familia, serie, _, _ in series:
        serie = em_pregoes(serie)
        if serie.dropna().empty:
            continue
        linha_vr = {"mercado": nome, "família": familia}
        linha_dem = {"mercado": nome}
        linha_bruto = {"mercado": nome}
        for k in HORIZONTES:
            inc = incrementos_nao_sobrepostos(serie, k)
            r_dem, t_dem, n = rho_com_t(demeanar_expansivo(inc))
            r_bruto, _, _ = rho_com_t(inc)
            medidas[(nome, k)] = {"vr": variance_ratio(serie, k), "rho_dem": r_dem,
                                  "t_dem": t_dem, "n": n, "rho_bruto": r_bruto}
            linha_vr[f"k={k}"] = medidas[(nome, k)]["vr"]
            linha_dem[f"k={k}"] = (f"{r_dem:+.2f} (t {t_dem:+.1f}, n {n})"
                                   if np.isfinite(t_dem) else f"— (n {n})")
            linha_bruto[f"k={k}"] = (f"{r_bruto:+.2f}" if np.isfinite(r_bruto)
                                     else "—")
        vr.append(linha_vr)
        rho_dem.append(linha_dem)
        rho_bruto.append(linha_bruto)

    tab_vr = pd.DataFrame(vr)
    fmt_vr = tab_vr.copy()
    for k in HORIZONTES:
        fmt_vr[f"k={k}"] = tab_vr[f"k={k}"].map(
            lambda v: f"{v:.2f}" if np.isfinite(v) else "—")

    mercados = list(tab_vr["mercado"])
    m3 = next((n for n in mercados if n.startswith("C1a")), None)

    texto = [
        "# Premissa da tendência — o sinal acumulado é negociável?\n",
        "> Gerado por `scripts/premissa_tendencia.py`. **Mede; não decide.**\n",
        "O `Premissa_G1.md` mostrou o sinal do poly crescendo com o horizonte e "
        "derrubou o veredito da D17 como regra geral. Crescer, porém, não é "
        "bastar: **tendência** (movimentos se encadeiam, informação disponível "
        "antes) e **convergência** (a probabilidade caminha para o desfecho à "
        "medida que a data chega) produzem exatamente a mesma acumulação, e só "
        "a primeira vira sleeve.\n",
        "- **VR** = Var(Δk) ÷ (k · Var(Δ1)). Passeio aleatório = 1. Acima de 1 "
        "os incrementos se somam; não diz se por tendência ou por deriva.",
        "- **ρ demeanado** = autocorrelação de lag 1 dos incrementos NÃO "
        "sobrepostos, com a deriva tirada pela média expansiva do próprio sinal "
        "(D9/D7.4, só passado). **É a parte ex-ante — a única negociável.**",
        "- **ρ bruto** = a mesma coisa com a deriva dentro. A distância entre os "
        "dois é o tamanho da convergência.",
        "- `n` = pares de incrementos que sobraram. Em k grande ele desaba "
        "(210 pregões ÷ 20 = 10 janelas), e sem ele o ρ é ilegível.\n",
        "## Variance ratio — os incrementos se somam?\n",
        fmt_vr.to_markdown(index=False), "",
        "## ρ demeanado — sobra previsibilidade depois de tirar a deriva?\n",
        pd.DataFrame(rho_dem).to_markdown(index=False), "",
        "## ρ bruto — a mesma medida com a deriva dentro\n",
        pd.DataFrame(rho_bruto).to_markdown(index=False), "",
        "## Leitura\n",
    ]

    # --- leitura GERADA dos números (prosa e tabela não podem divergir) ------
    def linha_do(nome):
        return {k: medidas[(nome, k)] for k in HORIZONTES}

    if m3:
        d = linha_do(m3)
        sig = [k for k in HORIZONTES if np.isfinite(d[k]["t_dem"])
               and abs(d[k]["t_dem"]) >= 2.0]
        com_n = ", ".join(
            f"k={k}: ρ {d[k]['rho_dem']:+.2f} (t {d[k]['t_dem']:+.1f}, n {d[k]['n']})"
            for k in HORIZONTES if np.isfinite(d[k]["t_dem"]))
        vr_m3 = ", ".join(f"k={k}: {d[k]['vr']:.2f}" for k in HORIZONTES
                          if np.isfinite(d[k]["vr"]))
        texto.append(
            f"**A linha que decide é a do {m3}** — a única série com cobertura "
            "e dispersão ao mesmo tempo, e a única não consumida por nenhuma "
            f"das quatro views vivas.\n\n- VR: {vr_m3}\n- ρ demeanado: {com_n}\n")
        if sig:
            texto.append(
                "**Sobra previsibilidade ex-ante** em " +
                ", ".join(f"k = {k}" for k in sig) +
                " (|t| ≥ 2). O crescimento do G1 não é só convergência: depois "
                "de tirar a deriva pela média expansiva, o incremento passado "
                "ainda informa o próximo. **Isto libera o G2** — não aprova "
                "sleeve nenhuma, só diz que existe o que testar.\n")
        else:
            texto.append(
                "**Não sobra previsibilidade ex-ante em nenhum horizonte da "
                "grade** (nenhum |t| ≥ 2), e o VR fica colado em 1. Tirada a "
                "deriva, o incremento passado não informa o próximo: a série "
                "de crença do poly se comporta como passeio aleatório.\n")
            texto.append(
                "**O que isto mata: a hipótese de MOMENTUM.** A *1.2 momentum* "
                "existia por supor que a tendência sustentada da crença se "
                "encadeia — não se encadeia. Ela perde a razão de ser, e junto "
                "com a *velocidade de ajuste* (já morta em k = 1) fecha a "
                "família inteira de \"ler o movimento da crença para prever o "
                "próximo movimento da crença\".\n")
            texto.append(
                "**O que isto NÃO mata: o G2.** Ele pergunta outra coisa — se o "
                "sinal prevê o RETORNO dos ativos, não se ele prevê a si mesmo. "
                "Um passeio aleatório pode perfeitamente antecipar preço. E a "
                "razão de rodar o G2 num horizonte acumulado continua de pé "
                "pelo argumento do G1, que VR = 1 não desfaz: o erro de "
                "discretização no incremento fica limitado a ~1 tick por mais "
                "que `k` cresça, enquanto o movimento verdadeiro acumula. Em "
                "k ≥ 3 o G2 deixa de condicionar em arredondamento — que era "
                "exatamente o vício que matou C1a e C1b em k = 1. **O que caiu "
                "foi o motivo para ESPERAR que o G2 passe, não a legitimidade "
                "de rodá-lo.**\n")

    # O sinal do que É significativo importa tanto quanto quantos são: este
    # projeto já achou reversão duas vezes (gap de fim de semana, D3b; correlação
    # salto × intradiário do `Premissa_taticas.md`). Se a terceira vier junto,
    # isso é padrão, não coincidência — e sai medido, não afirmado.
    significativos = [(n, k, medidas[(n, k)]["rho_dem"], medidas[(n, k)]["t_dem"],
                       medidas[(n, k)]["n"])
                      for n in mercados for k in HORIZONTES
                      if np.isfinite(medidas[(n, k)]["t_dem"])
                      and abs(medidas[(n, k)]["t_dem"]) >= 2.0]
    if significativos:
        negativos = [s for s in significativos if s[2] < 0]
        # Ordenar por `n` é o que separa achado de acaso: metade das linhas
        # significativas vive em amostra de duas dezenas de janelas.
        por_n = sorted(significativos, key=lambda s: -s[4])
        texto.append(
            f"**Fora do M3, {len(significativos)} pares chegam a |t| ≥ 2 — "
            f"{len(negativos)} negativos e "
            f"{len(significativos) - len(negativos)} positivos**, sem sinal "
            "dominante: " + " · ".join(
                f"{n} k = {k} (ρ {r:+.2f}, t {t:+.1f}, n {nn})"
                for n, k, r, t, nn in por_n) + ".\n")
        robustos = [s for s in por_n if s[4] >= 100]
        if robustos and all(s[2] < 0 for s in robustos):
            texto.append(
                "O sinal só fica consistente quando se olha a amostra: **os "
                + f"{len(robustos)} pares com n ≥ 100 são TODOS negativos** ("
                + " · ".join(f"{n} k = {k}, ρ {r:+.2f}" for n, k, r, _, _ in robustos)
                + "), e os positivos vivem em amostra de duas dezenas de "
                "janelas. Reversão, não tendência — o poly exagera e volta. É a "
                "**terceira** vez que este projeto encontra reversão onde "
                "procurava continuação (a primeira matou o gap de fim de semana "
                "na D3b; a segunda está na correlação salto × intradiário do "
                "`Premissa_taticas.md`). Sleeve de momentum compraria "
                "exatamente o lado errado disto.\n")

    # O contraste bruto × demeanado é o que separa deriva de tendência, e ele
    # é o argumento inteiro deste script — sai medido, não afirmado.
    maiores = sorted(
        ((abs(medidas[(n, k)]["rho_bruto"] - medidas[(n, k)]["rho_dem"]), n, k)
         for n in mercados for k in HORIZONTES
         if np.isfinite(medidas[(n, k)]["rho_bruto"])
         and np.isfinite(medidas[(n, k)]["rho_dem"])), reverse=True)[:3]
    if maiores:
        texto.append(
            "**Onde a deriva mais pesa** (maior distância entre ρ bruto e ρ "
            "demeanado): " + " · ".join(
                f"{n} em k = {k} ({medidas[(n, k)]['rho_bruto']:+.2f} → "
                f"{medidas[(n, k)]['rho_dem']:+.2f})" for _, n, k in maiores)
            + ". É a convergência aparecendo como se fosse tendência — e é "
            "exatamente por isso que a leitura acima usa a coluna demeanada.\n")

    texto.append(
        "**O que isto NÃO diz:** que existe (ou não) sleeve. Diz se o "
        "crescimento do sinal com o horizonte contém parte negociável. G2 (μ "
        "contra premissa declarada) e G3 (duplicação com as views vivas) "
        "continuam sendo os critérios seguintes, e nenhum módulo se escreve "
        "antes deles.\n")

    Path(args.saida).write_text("\n".join(texto) + "\n", encoding="utf-8")
    sys.stdout.write(fmt_vr.to_string(index=False)
                     + "\n\n" + pd.DataFrame(rho_dem).to_string(index=False)
                     + f"\n\nescrito: {args.saida}\n")


if __name__ == "__main__":
    main()
