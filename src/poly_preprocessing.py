"""Pré-processamento das probabilidades do Polymarket (módulo do Felipe).

DECISAO-9 (fechada, ver Decisoes_pendentes.md): módulo compartilhado único,
caixa de ferramentas de funções puras — cada view chama o que precisa.
Nenhum "preprocess()" monolítico.

MEDIDO (follow-up do Paulo, F5, 2026-07-29): a série do `/prices-history`
JÁ É O MIDPOINT do book (bate com `/midpoint`, não com `/last-trade-price`,
em dois mercados vivos). Não existe bid/ask histórico no CLOB, então não há
`midpoint_price(bid, ask)` — o pipeline entrega a série de midpoint pronta.
Consequência: o spread NÃO é observável; qualquer haircut de custo é premissa,
não estimativa.

Peças:
  - normalize_probs    : probs não somam 1 (medido nas PMFs cruas: M1 0,978–1,060;
                         M3 0,923–1,325); divide pela soma. Vale para binários e PMFs.
  - favorite_longshot  : correção do viés no binário (γ = 1,0 = identidade,
                         decisão 1.1); favorite_longshot_pmf é a versão de PMF.
  - carry_missing      : faixa sem preço herda a última leitura (decisão 6.1).
  - bucket_values_with_open : valor das faixas abertas das pontas, meia
                         largura de grade para fora (decisão 1.2).
  - pmf_mean           : média de PMF de buckets com o pré-processamento
                         padrão (normaliza -> favorite-longshot -> Σ p·x);
                         usada pelas views 2.2 (CPI) e 2.3 (FOMC).
  - binary_prob_series : série p(sim) de mercado binário (normaliza o par
                         Yes/No -> favorite-longshot); usada pelas views
                         2.4 (eleitoral) e 3.1 (recessão).

Funções puras: recebem arrays, devolvem arrays. As séries de midpoint cruas
vêm do pipeline do Paulo (`/prices-history` por tokenId, um arquivo por token)
e são lidas e alinhadas por `poly_loader` — é ele que abre os JSONs, alinha os
tokens no slot de 12h e monta a matriz de buckets. Aqui só entra matemática.
"""

import numpy as np

# DECISAO-1.1 (fechada 2026-08-04): sem correção de favorite-longshot no v1.
# γ = 1,0 é a identidade; o relatório traz o resultado também com 1,1 e 1,25.
FL_GAMMA_V1 = 1.0
# DECISAO-1.2 (fechada 2026-08-04): faixa aberta = ponto médio extrapolado,
# ou seja, meia largura de grade para fora da ponta.
OPEN_BUCKET_SHIFT = 0.5


def normalize_probs(probs, axis=-1):
    """Normaliza probabilidades para somarem 1 (dividir pela soma).

    Os midpoints de tokens com books independentes não somam 1 — tanto no
    binário (p_sim + p_nao != 1) quanto na PMF de buckets (medido no dado cru
    do Paulo: soma entre 0,92 e 1,33). `axis` permite normalizar uma matriz
    (datas x buckets) linha a linha.
    """
    probs = np.asarray(probs, dtype=float)
    if np.any(probs < 0):
        raise ValueError("probabilidade negativa na entrada")
    total = probs.sum(axis=axis, keepdims=True)
    if np.any(total <= 0):
        raise ValueError("soma de probabilidades <= 0 — impossível normalizar")
    return probs / total


def soma_faixas(probs):
    """Soma CRUA das faixas de uma PMF, para o `diagnostics` do Ω da Lia.

    É o mesmo desarranjo que `normalize_probs` conserta — mas aqui ele é o
    SINAL, não o defeito: cada bucket tem book próprio, e o quanto a soma se
    afasta de 1 mede o desencontro entre eles (medido no cru: 0,92 a 1,33 no
    mercado de cortes do Fed). A Lia pediu o valor cru, não `|soma − 1|`: a
    forma funcional é da régua dela.

    `None` (caminho binário da cascata, sem grade de faixas) devolve NaN, e
    NaN em qualquer faixa propaga — desconhecido nunca vira 0 (regra dela).
    """
    if probs is None:
        return float("nan")
    return float(np.sum(np.asarray(probs, dtype=float)))


def favorite_longshot(probs, gamma=FL_GAMMA_V1):
    """Correção de favorite-longshot de uma probabilidade BINÁRIA, elemento a
    elemento (cada entrada é um p independente, não um bucket de PMF).

    DECISAO-1.1 (fechada 2026-08-04): **sem correção no v1** — `gamma = 1.0` é
    a identidade. A família `p^γ / (p^γ + (1−p)^γ)` fica disponível porque o
    resultado final é reportado também com γ = 1,1 e 1,25, como coluna de
    robustez. Motivo de não corrigir: 9 mercados resolvidos não calibram curva
    própria, e importar γ de aposta esportiva mexeria 25% na mediana de um
    mercado de p baixa sem âncora no nosso dado.
    """
    p = np.asarray(probs, dtype=float)
    if gamma == 1.0:
        return p
    q = p ** gamma
    return q / (q + (1.0 - p) ** gamma)


def favorite_longshot_pmf(probs, gamma=FL_GAMMA_V1):
    """Mesma correção sobre uma PMF: eleva cada bucket a γ e renormaliza
    sobre o conjunto de buckets (o binário é o caso particular de 2 buckets).

    Contrato de `pmf_mean`: devolve PMF já utilizável (somando 1).
    """
    p = np.asarray(probs, dtype=float)
    if gamma == 1.0:
        return p
    q = p ** gamma
    return q / q.sum(axis=-1, keepdims=True)


def carry_missing(pmf):
    """DECISAO-6.1 (fechada 2026-08-04): faixa sem preço num slot herda a
    última leitura; a normalização vem depois (`normalize_probs`/`pmf_mean`).

    `pmf` é a matriz slots × buckets do `poly_loader.load_pmf`, com NaN onde
    a faixa não tem preço. Uma regra só cobre os dois casos medidos:

      - **faixa que morre** (virou impossível): medido no M3, a faixa já
        decaiu para ~zero antes de parar de negociar ("nenhum corte" morreu
        valendo 0,0045; "1 corte", 0,0030) — carregar esse último preço é
        equivalente a zerar.
      - **faixa que some e volta** (mar/2026: só 24 dos 60 slots têm as 6
        faixas): aqui carregar é melhor que renormalizar sobre as presentes,
        que jogaria a massa da ausente proporcionalmente nas outras.

    Não olha o futuro (não precisa saber se a faixa volta) e não descarta
    slot. Linhas antes da primeira leitura de um bucket seguem NaN — quem
    consome decide (o backtest as descarta por não haver PMF ainda).
    """
    return pmf.ffill()


def bucket_values_with_open(values, shift=OPEN_BUCKET_SHIFT, open_ends=("lower", "upper")):
    """DECISAO-1.2 (fechada 2026-08-04): valor das faixas ABERTAS das pontas.

    A faixa aberta ("0,5% ou mais") entra pelo **ponto médio extrapolado**:
    a ponta é deslocada para fora em `shift` larguras de grade, com a largura
    lida da própria grade do mês (mediana das diferenças). `shift = 0.5` é a
    decisão; 0 (truncar no limite) e 1 (largura inteira) ficam disponíveis
    para a varredura de sensibilidade.

    Por que ponto médio: truncar subestima a ponta SEMPRE na mesma direção, e
    um valor cravado quebra quando a grade muda — e ela muda (3 a 9 faixas ao
    longo do histórico, com inversão de sinal em jul/2026). Ler a largura da
    grade faz a regra valer mês a mês sem exceção escrita à mão.

    `values` deve vir ordenado (é o que `poly_loader.load_pmf` entrega). A
    ponta superior pode chegar como NaN (slug "8plus"): vira vizinho + largura
    antes do deslocamento.
    """
    values = np.asarray(values, dtype=float).copy()
    finitos = values[np.isfinite(values)]
    if finitos.size < 2:
        raise ValueError("grade com menos de 2 buckets finitos — largura indefinida")
    largura = float(np.median(np.diff(finitos)))
    if "lower" in open_ends:
        values[0] -= shift * largura
    if "upper" in open_ends:
        base = values[-1] if np.isfinite(values[-1]) else values[-2] + largura
        values[-1] = base + shift * largura
    return values


def pmf_mean(probs, values, fl_correction=favorite_longshot_pmf):
    """Média de uma PMF de buckets com o pré-processamento padrão:
    normaliza (midpoints não somam 1) -> favorite-longshot -> Σ pᵢ·xᵢ.

    `values` deve vir com o bucket aberto já resolvido (open_bucket_value,
    decisão 11b) — NaN é rejeitado. Se a forma da decisão 11a exigir
    renormalizar após a correção, isso entra na própria favorite_longshot
    (contrato: devolve PMF utilizável). `fl_correction` injetável só para
    teste sintético; o default falha alto até a decisão 11a.
    """
    probs = np.asarray(probs, dtype=float)
    values = np.asarray(values, dtype=float)
    if probs.shape != values.shape:
        raise ValueError(f"probs e values devem alinhar: {probs.shape} vs {values.shape}")
    if np.any(np.isnan(values)):
        raise ValueError("values contém NaN — bucket aberto não resolvido (decisão 11b)")
    p = np.asarray(fl_correction(normalize_probs(probs)), dtype=float)
    # Contrato acima, verificado: a correção tem de devolver PMF utilizável.
    # A armadilha real é passar aqui a `favorite_longshot` BINÁRIA — inócua em
    # γ = 1,0 (identidade), mas em γ ≠ 1 ela devolve p^γ/(p^γ+(1−p)^γ) faixa a
    # faixa, que não soma 1, e a média sairia escalada SEM ERRO. Como γ ≠ 1 só
    # aparece na coluna de robustez (seção 9), o silêncio duraria até o número
    # final. Falha alto em vez disso.
    if not np.isclose(p.sum(), 1.0, atol=1e-9):
        raise ValueError(
            f"fl_correction devolveu vetor que soma {p.sum():.6f}, não 1 — na PMF "
            "use `favorite_longshot_pmf` (renormaliza sobre as faixas); a "
            "`favorite_longshot` binária só vale no caminho de 2 buckets")
    return float(p @ values)


def binary_prob_series(p_yes, p_no=None, fl_correction=favorite_longshot):
    """Série p(sim) de um mercado binário: normalização par a par
    (p_sim + p_não != 1) -> favorite-longshot.

    `p_yes`/`p_no` são as séries de midpoint dos dois tokenIds, já alinhadas
    no mesmo grid de 12h. `p_no=None` = só a série do Yes disponível (é o caso
    da entrega atual do Paulo, que puxou só o token Yes dos 9 mercados): sem o
    par não há o que normalizar, vai direto para a correção FL.

    Usada pelas views 2.4 e 3.1. Construir UMA vez a montante e passar a
    MESMA série tanto para a regressão do β quanto para o build_view — é o
    que faz a parte linear da correção FL ser absorvida pelo β (espec 2.4,
    item 2b). `fl_correction` default = stub da decisão 11a (falha alto).
    """
    p_yes = np.asarray(p_yes, dtype=float)
    if p_no is None:
        p = p_yes
    else:
        p_no = np.asarray(p_no, dtype=float)
        if p_yes.shape != p_no.shape:
            raise ValueError(f"p_yes e p_no devem alinhar: {p_yes.shape} vs {p_no.shape}")
        p = normalize_probs(np.column_stack([p_yes, p_no]), axis=1)[:, 0]
    return np.asarray(fl_correction(p), dtype=float)


# `open_bucket_value(bound, side)` foi substituída por `bucket_values_with_open`,
# que resolve as duas pontas de uma vez lendo a largura da própria grade — a
# regra da decisão 1.2 é sobre a GRADE do mês, não sobre um bucket isolado.
