"""View B com β PRÓPRIO — trajetória do Fed no vértice de 1 ano. Módulo do Felipe.

**Sem número de decisão, de propósito.** Candidata registrada em **15g** de
`Decisoes_pendentes.md`. O número sai quando o grupo numerar, não daqui.

É a view B da seção 11 com a UMA mudança que responde ao motivo de ela ter sido
cortada — e o resto é reuso, não reescrita: a cascata, o P e o E_poly saem do
`view_B_trajetoria_fed.build_view`, que continua intacto.

    surpresa  = E_poly[taxa de fim de ano] − benchmark do MESMO horizonte  (bps)
    surpresa_líquida = surpresa − média expansiva
    P[i]      = 2·(β_i − β_SPY)/Σ_j|β_j − β_SPY|      (Σ|P| = 2, P[SPY] = 0)
    Q         = surpresa_líquida · Σ_i P[i]·β_i

**O que muda em relação à B da espec, e por quê:**

1. **β PRÓPRIO, estimado contra o vértice da pergunta.** A espec original manda
   *reusar os β da 2.3* (item 3), e é isso — não a tese — que fazia a B duplicar a
   2.3: com o mesmo β o P sai **literalmente idêntico**, e empilhar as duas põe
   DUAS LINHAS IGUAIS no P do BL. Isso é pior que correlação: as duas viram uma
   só, ponderada pelo Ω, e o grupo acha que tem duas views.

   **Medido em 37 reuniões (2026-08-08):** trocando o vértice da regressão, o P
   muda de verdade — ângulo de **95,6°** (corr −0,34) entre o P do ΔDTB3 (o da
   2.3) e o do ΔDGS10. O curto dá long TLT/TIP/XLU; o longo dá long XLE/XLF e
   **short** TLT. Praticamente ortogonais: com β próprio, a B ocupa dimensão nova.

2. **Benchmark do mesmo horizonte da pergunta.** "Onde a taxa termina o ano?" é
   pergunta de ~1 ano. O `DTB3` (3 meses) é curto demais e o `DGS10` (10 anos) é
   longo demais; o vértice certo é o **`DGS1`**, pedido como G10a em
   `Dump/trocas/PEDIDO_G10_Paulo.md`. Some junto o problema que travou a B na
   seção 11: o benchmark **não é mais o ZQ**, que não tem fonte grátis (F6).

3. **Surpresa DEMEANADA por janela expansiva.** Mesma construção da 2.3 e da
   DECISAO-7.4 da 2.2, pela mesma razão: comparar um E_poly de fim de ano com um
   vértice de curva deixa viés de NÍVEL (prêmio de prazo), e o sinal é o desvio,
   não o nível. `surpresa_media` vem do chamador (expansiva, sem lookahead);
   0.0 reproduz a fórmula crua para teste sintético.

🛑 **CONSTRUÍDA E NÃO MEDIDA NO VÉRTICE CERTO — não ligar antes de medir.** O
`DGS1` ainda não chegou (G10a). Rodei o teste de sinal na versão PROXY (DGS10 nos
dois lados, 179 dias) e ela saiu **INVERTIDA**: t −1,79 em 1 dia, **t −2,68** em
5 dias, acerto de sinal 48%. O proxy é sabidamente errado — benchmark de 10 anos
para pergunta de 1 ano carrega prêmio de prazo dentro da "surpresa" — mas é o
**segundo desenho seguido a sair invertido** (o primeiro foi a
`view_cpi_transversal`, t −3,02). Isso é padrão, não azar.

**A ordem obrigatória, e ela não é negociável por pressa:** chegou o `DGS1` →
refazer o teste com o vértice certo → só então empilhar. Se sair invertido de
novo, **não entra e não se inverte** (precedente D2b: a 3.1 não foi redesenhada na
direção que o dado pedia; inverter é ajustar sinal à amostra).

**O que o teste é, e o que não é** (controle rodado em 08/08): a 2.2 dá t +0,44 e
a **2.3 dá t +0,26** — nenhuma view do v1 passa nele. Logo ele é **veto**, não
certificado: pega sinal invertido e não mede o que faz uma view render dentro do
BL. A régua para esta view é "não sair invertida", não "passar".

**Cobertura, o segundo motivo do corte da seção 11:** o M3
(`M3_fed_trajectory_will-N-fed-rate-cuts-happen-in-2025`) vai de 2024-12-30 a
2025-12-10 e cobre **237 dos 374 pregões (63%)** da janela do v1, com soma das
faixas média 1,007 (mín 0,882). Não há mercado de trajetória de 2026 no `data/` e
ele NÃO foi pedido (pedido grande no caminho crítico do Paulo). 63% é comparável à
convivência atual das duas views (64%) — limitação a declarar, não impedimento.

⚠️ **Herança do módulo antigo, para o chamador não levar susto:** o default de
`fl_correction` lá é o `favorite_longshot` BINÁRIO, e não o `favorite_longshot_pmf`
que a 2.2 e a 2.3 usam no caminho de PMF. Em γ = 1,0 (o do v1, D1.1) os dois são a
identidade e não muda nada; em γ ≠ 1 o vetor deixa de somar 1 e o E_poly sai
escalado sem dar erro. **Não mexi no módulo antigo** — quem chama deve passar o
`fl_correction` explicitamente, como o montador do backtest já faz com as outras.

Unidades: taxas, benchmark, E_poly e surpresa em **bps de NÍVEL** (4,00% = 400);
β em fração/bp; Q em fração decimal, horizonte de 1 dia (`horizonte_q_dias`).
"""

import numpy as np

import view_B_trajetoria_fed
from poly_preprocessing import soma_faixas
from view_2_3_fed import SOMA_MINIMA
from view_B_trajetoria_fed import CORTE_BPS, MARKET_ASSET, rates_from_cut_buckets  # noqa: F401


def build_view(assets, benchmark_bps, betas, vertice,
               bucket_probs=None, bucket_rates_bps=None,
               binary_prob=None, taxa_atual_bps=None,
               surpresa_media=0.0, soma_minima=SOMA_MINIMA,
               fl_correction=None, market_asset=MARKET_ASSET):
    """Monta a view B de β próprio para uma data de rebalanceamento.

    Parâmetros:
      assets        : list[str] — universo na ordem do dataset do Paulo.
      benchmark_bps : float — taxa do vértice de MESMO horizonte da pergunta, em
                      bps de nível (o `DGS1`; ver item 2 do docstring do módulo).
      betas         : (n,) — β PRÓPRIOS, estimados contra a variação do MESMO
                      vértice nos dias de FOMC (`view_2_3_fed.estimate_betas`
                      com ΔDGS1). Passar aqui os β da 2.3 devolve a view antiga e
                      recria a duplicação — por isso `vertice` é obrigatório.
      vertice       : str — qual série gerou os β (ex.: `"DGS1"`). **Obrigatório**
                      e vai aos diagnostics. Não muda conta nenhuma; existe porque
                      os dois vetores de β têm a mesma cara e P ortogonais, e um
                      artefato que não diz qual rodou é irrecuperável depois.
      bucket_probs  : probs CRUAS dos buckets de trajetória (ou None).
      bucket_rates_bps : taxa de fim de ano de cada bucket, bps (converter nº de
                      cortes com `rates_from_cut_buckets`; ponta aberta resolvida
                      pelo chamador via `open_bucket_value` — decisão 11b).
      binary_prob   : tupla (p_sim, p_nao) CRUA do binário (ou None).
      taxa_atual_bps: taxa vigente (nível, bps) — exigida no fallback binário.
      surpresa_media: média EXPANSIVA da surpresa, do chamador (item 3).
      soma_minima   : piso da soma crua da PMF. **Herdado da 2.3**, não inventado
                      aqui: mesma constante, mesmo motivo (PMF degenerada sai pela
                      cascata em vez de virar chute renormalizado) e mesmo
                      compromisso de interface com o Ω da Lia — o piso é DEGRAU e
                      não vira rampa, senão conta em dobro com o
                      `score_coerencia` dela. MEDIDO no M3: a soma vai de 0,882 a
                      1,054, então o piso morde pouco e morde nos dias certos.

    Retorna ViewResult (P, Q, diagnostics) ou None.

    A cascata (PMF > binário > None), o E_poly e o P vêm de
    `view_B_trajetoria_fed.build_view` — uma implementação só, para as duas
    versões da view não poderem divergir em silêncio. O que se faz aqui é o piso
    de qualidade, a demeanagem e a reescrita do Q.
    """
    if not vertice:
        raise ValueError(
            "`vertice` é obrigatório: sem ele não se sabe se os β são próprios "
            "(ΔDGS1) ou os da 2.3 (ΔDTB3) — e os dois dão P ortogonais (15g)")
    if bucket_probs is not None:
        soma = soma_faixas(bucket_probs)
        if not np.isfinite(soma) or soma < soma_minima:
            return None  # PMF degenerada -> cascata, não chute renormalizado
    base = view_B_trajetoria_fed.build_view(
        assets, e_zq_dez_bps=benchmark_bps, betas=betas,
        bucket_probs=bucket_probs, bucket_rates_bps=bucket_rates_bps,
        binary_prob=binary_prob, taxa_atual_bps=taxa_atual_bps,
        market_asset=market_asset,
        **({} if fl_correction is None else {"fl_correction": fl_correction}))
    if base is None:
        return None

    d = base.diagnostics
    surpresa_liquida = d["surpresa_bps"] - surpresa_media
    Q = float(surpresa_liquida * d["sum_P_beta"])
    # `e_zq_dez_bps` SAI do dict: o número agora é o do vértice de curva, e deixar
    # a chave antiga com valor novo é o jeito mais eficiente de enganar quem ler o
    # artefato daqui a duas semanas. Vai como `benchmark_bps` + `vertice`.
    d = {k: v for k, v in d.items() if k != "e_zq_dez_bps"}
    return base._replace(Q=Q, diagnostics={
        **d,
        "view": "B_trajetoria_propria",   # chave própria: o Ω da Lia distingue
        "benchmark_bps": benchmark_bps,
        "vertice": vertice,
        "surpresa_media": surpresa_media,
        "surpresa_liquida": surpresa_liquida,
    })
