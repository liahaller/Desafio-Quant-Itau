"""Teste entre mercados IRMÃOS — o único fora-da-amostra de verdade. Felipe.

Partir a amostra em duas metades é fora-da-amostra de pobre: as duas metades
vêm do mesmo mercado, do mesmo ano e do mesmo regime. O teste forte é outro —
**o mecanismo se repete num segundo mercado que deveria ter o mesmo
mecanismo?**

Foi assim que a **view 2.4** morreu, e é o precedente que este script reproduz:
na Câmara 2026 os sinais deveriam inverter contra o Trump 2024 se o mecanismo
fosse partidário, e o **TLT caiu nos dois**. Mecanismo que não inverte quando o
partido inverte não é mecanismo partidário — é fator comum.

Dois pares de irmãos existem no dado, e a relação esperada entre eles é
**diferente**, por isso está declarada em `IRMAOS`:

  - **partidário** (M5 Trump 2024 ↔ M9 Câmara) — relação **ESPELHO**. Um "SIM"
    em cada mercado significa o partido oposto, então o μ cru tem de sair com
    sinais OPOSTOS. Sinal igual nos dois = reprova.
  - **geopolítico** (M7 Irã jun/2025 ↔ M7 Irã fev/2026) — relação **IGUAL**.
    Os dois perguntam a mesma coisa, então o μ cru tem de sair com o MESMO
    sinal. Sinal oposto = reprova. Foi o que matou a view C na D23f.

⚠️ **O M4 recessão não tem irmão, e isso é limite estrutural, não omissão.** Não
existe segundo mercado de recessão no dado (a própria D18d registra). Ele nunca
vai ter este teste — vai depender para sempre do corte em metades **mais** a
explicação da contradição com a D19c. O artefato diz isso explicitamente para
ninguém ler a ausência dele como aprovação.

⚠️ **O teste é sobre o μ CRU**, não sobre o alinhado à premissa. Alinhar já
embute a resposta: as premissas do M5 e do M9 são espelhadas por declaração, e
comparar dois números já espelhados esconderia justamente o padrão que derrubou
a 2.4. Aqui se olha para que lado cada ativo andou, sem correção de sinal.

**Nada novo é declarado** — mercados, livros, premissas e grades vêm todos dos
artefatos anteriores. **Nada em `src/` é tocado.**

Uso:

    python scripts/gate_mercados_irmaos.py --raiz .
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from backtest_v1 import PONTOS_PERCENTUAIS  # noqa: E402
from config import SIGMA_JANELA_PREGOES  # noqa: E402
from gate_event_driven import PREMISSAS  # noqa: E402
from gate_sleeves import eventos_diarios, mu_do_sinal  # noqa: E402
from gate_transversal import LIVROS_SETORIAIS  # noqa: E402
from gate_transversal_neutro import SUFIXO, neutraliza, pernas_neutras  # noqa: E402
from premissa_g1 import HORIZONTES, em_pregoes, series_dos_mercados  # noqa: E402

JANELA = 1

# Pares de irmãos e a relação que o mecanismo declarado exige entre eles.
# "espelho" = μ cru tem de sair com sinais OPOSTOS nos dois mercados.
# "igual"   = μ cru tem de sair com o MESMO sinal nos dois.
IRMAOS = {
    "partidário": ("M5 Trump 2024", "M9 Câmara", "espelho",
                   "um \"SIM\" em cada mercado significa o partido oposto — "
                   "se o mecanismo for partidário, o μ inverte. **É o teste "
                   "exato que derrubou a view 2.4**"),
    "geopolítico": ("M7 ação militar Irã (jun/2025)", "M7 ataque ao Irã (fev/2026)",
                    "igual",
                    "os dois perguntam a mesma coisa, então o μ tem de repetir "
                    "o sinal. **É o teste que derrubou a view C na D23f**"),
}

# As células que sobreviveram ao corte da amostra no `Gate_transversal_neutro.md`
# e que caem num par de irmãos. Declaradas aqui para o cruzamento ser exato em
# vez de "vale olhar" — é a pergunta que este script existe para responder.
CELULAS_VIVAS = {
    "M9 Câmara": ("neutro +XLP −XLK⊥", "k = 20"),
    "M7 ação militar Irã (jun/2025)": ("neutro +XLE −XLK⊥", "k = 20"),
    # q0.00 é corte de SALTO, não lookback: não existe nesta grade. O vizinho
    # mais próximo é k = 1 (todo dia com Δp), e é ele que se olha.
    "M5 Trump 2024": ("neutro +XLF −XLP⊥", "k = 1"),
}

# Mercado sem irmão no dado — entra no artefato como linha explícita.
SEM_IRMAO = {
    "M4 recessão EUA 2025":
        "não existe segundo mercado de recessão no dado (registrado na própria "
        "D18d). Este teste **nunca** vai ser aplicável a ele.",
    "CPI mensal (E_poly)": "família com mercado único por mês, sem par contemporâneo.",
    "C1a M3 trajetória do Fed (nº de cortes)": "mercado único.",
    "C1b reunião do FOMC (E_poly em bps)": "mercado único.",
    "M6 tarifas China": "mercado único, e 8 pregões.",
    "M8 reconciliação fiscal": "mercado único, e 2 pregões.",
}


def mu_cru(retornos, sinal, livro, assets, sigma, ate):
    """μ por ativo do livro, em bps/dia, SEM alinhar a premissa nenhuma.

    Alinhar embutiria a resposta: as premissas dos irmãos partidários já são
    espelhadas por declaração, e comparar dois números já espelhados esconderia
    o padrão que derrubou a 2.4. O que se compara aqui é para que lado cada
    ativo de fato andou.
    """
    mu, n = mu_do_sinal(retornos, eventos_diarios(sinal), JANELA, tuple(livro),
                        sigma, ate)
    if mu is None:
        return None, 0
    # Mesma conversão do `bate_premissa`, por referência e não por cópia: um
    # fator diferente aqui faria esta tabela e as dos outros artefatos falarem
    # unidades diferentes sem nada acusar.
    indice = list(assets)
    return ({a: float(mu[indice.index(a)]) * PONTOS_PERCENTUAIS * 100.0
             for a in livro}, n)


def reproduz(mu_a, mu_b, relacao):
    """O mecanismo se repete? Compara sinal a sinal, ativo a ativo.

    Devolve `(veredito, detalhe)`. Ativo com μ exatamente zero em qualquer dos
    lados não conta como concordância nem como discordância — devolve None e
    sai do denominador, porque sinal zero não testa direção nenhuma.
    """
    if mu_a is None or mu_b is None:
        return None, "μ ausente"
    esperado = -1.0 if relacao == "espelho" else +1.0
    partes, oks = [], []
    for ativo in mu_a:
        a, b = mu_a[ativo], mu_b[ativo]
        if a == 0 or b == 0:
            partes.append(f"{ativo} {a:+.2f}/{b:+.2f} —")
            continue
        ok = np.sign(a) == esperado * np.sign(b)
        oks.append(ok)
        partes.append(f"{ativo} {a:+.2f}/{b:+.2f} {'✅' if ok else '❌'}")
    if not oks:
        return None, " · ".join(partes)
    return all(oks), " · ".join(partes)


def main():
    # O console do Windows abre em cp1252 e engasga nos rótulos acentuados.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raiz", default=".")
    parser.add_argument("--saida", default="Dump/analises/Gate_mercados_irmaos.md")
    args = parser.parse_args()

    series, retornos, montador, datas = series_dos_mercados(args.raiz)
    setoriais = sorted({a for livro, _t in LIVROS_SETORIAIS.values() for a in livro})
    estendido = pernas_neutras(retornos, setoriais).dropna()
    assets_ext = tuple(estendido.columns)
    # Σ diagonal pelo mesmo motivo do `gate_transversal_neutro.py`: o
    # `estimate_drift_mu` lê só a diagonal, e a Σ cheia da tabela estendida é
    # singular por construção.
    sigma = np.diag(estendido.tail(SIGMA_JANELA_PREGOES).var().to_numpy())
    ate = datas[-1] + pd.Timedelta(days=1)

    sinais = {nome: em_pregoes(serie) for nome, _f, serie, _t, _u in series}

    linhas = []
    for familia, (a, b, relacao, _texto) in IRMAOS.items():
        if a not in sinais or b not in sinais:
            continue
        # Os livros testados são os DECLARADOS dos dois irmãos, aplicados aos
        # dois mercados. Inventar um livro comum aqui seria declarar premissa
        # nova no meio de um teste de reprodução.
        livros = {"direcional SPY/TLT": PREMISSAS[a][0]}
        for mercado in (a, b):
            livro = LIVROS_SETORIAIS[mercado][0]
            rotulo = " ".join(f"{'+' if p > 0 else '−'}{t}" for t, p in livro.items())
            livros[f"setorial {rotulo}"] = livro
            livros[f"neutro {rotulo}{SUFIXO}"] = neutraliza(livro)
        for rotulo, livro in livros.items():
            for k in HORIZONTES:
                sa, sb = sinais[a].diff(k).dropna(), sinais[b].diff(k).dropna()
                if sa.empty or sb.empty:
                    continue
                ma, na = mu_cru(estendido, sa, livro, assets_ext, sigma, ate)
                mb, nb = mu_cru(estendido, sb, livro, assets_ext, sigma, ate)
                ok, detalhe = reproduz(ma, mb, relacao)
                linhas.append({
                    "par": familia, "relação": relacao, "livro": rotulo,
                    "lookback": f"k = {k}", "n A / n B": f"{na} / {nb}",
                    "μ cru A/B (bps/dia)": detalhe,
                    "reproduz?": "✅" if ok else ("—" if ok is None else "❌"),
                })
    tabela = pd.DataFrame(linhas)

    texto = [
        "# Mercados irmãos — o mecanismo se repete no segundo mercado?\n",
        "> Gerado por `scripts/gate_mercados_irmaos.py`. **Mede; não decide.** "
        "Nenhum corte cravado e **nenhuma premissa nova** — mercados, livros e "
        "grades vêm dos artefatos anteriores.\n",
        f"- janela do backtest: **{datas[0]:%Y-%m-%d} a {datas[-1]:%Y-%m-%d}** "
        f"({len(datas)} pregões)",
        "- **μ CRU**, sem alinhar a premissa: alinhar embutiria a resposta, "
        "porque as premissas dos irmãos partidários já são espelhadas por "
        "declaração. O que se compara é para que lado cada ativo andou",
        "- os livros testados são os **declarados dos dois irmãos**, aplicados "
        "aos dois mercados. Inventar um livro comum seria declarar premissa "
        "nova no meio de um teste de reprodução\n",
        "## A relação exigida por cada par, declarada antes de medir\n",
    ]
    for familia, (a, b, relacao, motivo) in IRMAOS.items():
        texto.append(f"- **{familia}** — {a} ↔ {b}, relação **{relacao}**: "
                     f"{motivo}.")
    texto += ["", tabela.to_markdown(index=False), "", "## Leitura\n"]

    for familia, (a, b, relacao, _m) in IRMAOS.items():
        bloco = tabela[tabela["par"] == familia]
        if bloco.empty:
            continue
        passa = bloco[bloco["reproduz?"] == "✅"]
        total = len(bloco[bloco["reproduz?"] != "—"])
        # LINHA DE BASE DO ACASO, e ela é obrigatória: com livro de 2 ativos e
        # exigência de acerto nos DOIS, jogar moeda reproduz 25% das células.
        # Contar acertos sem esse denominador é o jeito mais fácil de ler
        # ruído como mecanismo.
        n_pernas = int(np.median([len(l) for l in
                                  (PREMISSAS[a][0], LIVROS_SETORIAIS[a][0])]))
        acaso = 0.5 ** n_pernas
        taxa = len(passa) / total if total else float("nan")
        texto.append(
            f"**{familia.capitalize()} ({a} ↔ {b}, relação {relacao}): "
            f"{len(passa)} de {total} células reproduzem "
            f"({taxa:.0%}), contra **{acaso:.0%}** que sair-se-ia por acaso "
            f"(livro de {n_pernas} pernas, exigindo acerto nas duas).**"
            + (" Onde reproduz: "
               + " · ".join(f"`{r['livro']}` {r['lookback']}"
                            for _, r in passa.iterrows()) + "."
               if len(passa) else
               " **Em nenhum livro e em nenhum horizonte da grade.** O "
               "mecanismo declarado não se repete no segundo mercado — é o "
               "mesmo veredito que a view irmã já tinha recebido, agora medido "
               "também na camada tática.") + "\n")
        texto.append(
            "⚠️ **A taxa acima NÃO é um teste estatístico, e não deve ser "
            "lida como um.** As células não são independentes: os horizontes "
            "se sobrepõem (k = 3 e k = 5 leem quase os mesmos dias) e os "
            f"livros compartilham perna. O `n` efetivo é muito menor que "
            f"{total}, então a distância entre {taxa:.0%} e {acaso:.0%} não "
            "sustenta significância. Ela serve para uma coisa só: dizer se a "
            "reprodução é **rara** ou **comum** neste par. O que decide "
            "candidata é o cruzamento célula a célula, logo abaixo.\n")
        if total and taxa <= acaso * 1.5:
            texto.append(
                "⚠️ **Isso é praticamente o acaso.** A taxa de reprodução não "
                "se separa do que moeda jogada produziria, então este par "
                "**não** confirma o mecanismo — as células que reproduzem são "
                "compatíveis com sorte, e as que não reproduzem não são "
                "surpresa.\n")

    # O cruzamento EXATO: a célula que sobreviveu ao corte é a mesma que
    # reproduz no irmão? Contar reproduções no par inteiro não responde isso —
    # e é a única pergunta que muda o destino de cada candidata.
    texto.append("### O cruzamento que decide o nível 2\n")
    texto.append(
        "A pergunta não é *\"o par reproduz em alguma célula?\"* — é **se a "
        "célula exata que sobreviveu ao corte da amostra é uma das que "
        "reproduzem**. Uma célula que passa no corte mas reprova no irmão está "
        "medindo o mercado, não o mecanismo.\n")
    for mercado, (livro_vivo, eixo_vivo) in CELULAS_VIVAS.items():
        familia = next((f for f, (a, b, _r, _m) in IRMAOS.items()
                        if mercado in (a, b)), None)
        if familia is None:
            continue
        alvo = tabela[(tabela["par"] == familia)
                      & (tabela["livro"] == livro_vivo)
                      & (tabela["lookback"] == eixo_vivo)]
        if alvo.empty:
            texto.append(f"- **{mercado}** — célula `{livro_vivo}` {eixo_vivo} "
                         "não existe nesta grade.")
            continue
        linha = alvo.iloc[0]
        veredito_celula = linha["reproduz?"]
        texto.append(
            f"- **{mercado}** · `{livro_vivo}` · {eixo_vivo} — "
            f"**{veredito_celula}** · μ cru A/B: {linha['μ cru A/B (bps/dia)']}. "
            + ("**A célula viva reproduz no mercado irmão** — é a evidência "
               "mais forte disponível para uma célula deste nível."
               if veredito_celula == "✅" else
               "**A célula viva NÃO reproduz no irmão:** ela sobrevive ao "
               "corte dentro do próprio mercado e falha quando o mercado "
               "muda. É o padrão que matou a view irmã."))
    texto.append("")
    texto.append(
        "⚠️ **Sobre o M5 Trump:** a célula viva dele é o corte `q0.00` do "
        "gatilho de SALTO, que **não existe nesta grade de lookbacks** — "
        "`q0.00` é \"todo dia com Δp ≠ 0\", cujo vizinho mais próximo é k = 1, "
        "e é essa a linha lida acima. A correspondência é aproximada, e está "
        "dita para não ser lida como exata.\n")

    texto.append("### Os mercados que NÃO têm irmão\n")
    texto.append("A ausência deste teste **não é aprovação** — é limite do "
                 "dado, e precisa estar visível ao lado de qualquer veredito "
                 "positivo nesses mercados.\n")
    for mercado, motivo in SEM_IRMAO.items():
        texto.append(f"- **{mercado}** — {motivo}")
    texto.append("")
    texto.append(
        "⚠️ **O caso que importa é o M4 recessão.** É a única célula que passou "
        "todos os critérios da maratona, e é justamente a que **nunca** poderá "
        "ser confirmada por mercado irmão. Ela vai depender para sempre de "
        "duas coisas: o corte em metades (que passa, inclusive em três "
        "horizontes contíguos no livro neutro) e a **explicação da contradição "
        "com a D19c**, que mediu inversão dentro da amostra neste mesmo "
        "mercado com a montagem da view 3.1.\n")

    texto.append(
        "**O que isto NÃO diz:** nada sobre P&L, e nada sobre os mercados sem "
        "irmão. Reprovar aqui é evidência forte contra o mecanismo; passar aqui "
        "seria evidência forte a favor — a ausência do teste não é nem uma "
        "coisa nem outra.\n")

    Path(args.saida).write_text("\n".join(texto) + "\n", encoding="utf-8")
    sys.stdout.write(tabela.to_string(index=False) + f"\n\nescrito: {args.saida}\n")


if __name__ == "__main__":
    main()
