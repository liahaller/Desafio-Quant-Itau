# View B (candidata) — Trajetória do Fed (caminho dos juros até o fim do ano)

**Status:** 🟡 **candidata — entrada na carteira em aberto** (entra ou não é decisão de reunião). Desenho proposto em sessão com Felipe (2026-07-10), espelhando a view 2.3 ao máximo — **não** fecha as decisões 3 e 4 (isso só acontece se a reunião aprovar a entrada). Família A (divergência + sensibilidade), com β/P **reusados da 2.3**.

## A ideia

A 2.3 pergunta "o que o Fed faz na **próxima reunião**?". Esta pergunta é a **longa**: "onde a taxa **termina o ano**?" — quantos cortes no total. As duas podem divergir de forma independente: poly e mercado podem concordar sobre setembro e discordar sobre o acumulado até dezembro. É a divergência sobre o **caminho** dos juros — a que mais mexe com ativos de duration longa — e a 2.3 não a captura.

Os dois termômetros: o poly tem mercados de cortes acumulados / taxa de fim de ano (buckets, alto volume em 2024); o mercado tradicional tem o **futuro ZQ de dezembro**, que precifica a taxa média esperada para aquele mês. Mesma maquinaria da 2.3, outro par de instrumentos.

## Como funciona (proposto — espelha a 2.3)

0. **Fórmula geral:** `surpresa_caminho = E_poly[taxa_fim_de_ano] − E_ZQdez[taxa]`, em bps. Como na 2.3, o lado do futuro **nunca degrada**; o que degrada é o cálculo de `E_poly`:
   - PMF de buckets (nº de cortes / taxa de fim de ano) disponível → caminho principal (item 1).
   - Apenas mercado binário ("corte até dezembro?") → fallback análogo ao da 2.3: `E_poly = taxa_atual + p_poly × (−25bp)`.
   - Nenhum mercado de trajetória no período → **view desativada**; Ω → ∞; o BL fica no prior.
1. **De onde vem `E_poly`:** mercados de buckets do poly ("quantos cortes em ANO" ou "taxa em dez/ANO") — uma PMF. `E_poly[taxa] = Σ pᵢ · taxaᵢ` (buckets de nº de cortes convertem mecanicamente: 25bp por corte sobre a taxa vigente). Pré-processamento pelo módulo da decisão 9 (normalização, favorite-longshot, bucket aberto — mesma estrutura de PMF das 2.2/2.3).
2. **De onde vem `E_ZQdez`:** futuro Fed Funds **de dezembro** (ZQ, yfinance): taxa implícita = `100 − preço` (média do FF no mês). Mesmas lições da 2.3: sai **esperança em bps, não probabilidade**; contrato **fixo de dezembro** do ano do mercado do poly (não rola mês a mês — o alvo é o fim do ano).
3. **β por ativo: reusados integralmente da 2.3** — a mesma regressão event-study contra surpresa à la Kuttner; nenhuma estimação nova. ⚠️ **Premissa documentada:** assume que a reação dos setores **por bp de surpresa de caminho** é a mesma que **por bp de surpresa de reunião**. Alternativa (regressão própria contra a surpresa de caminho) não foi rejeitada — é confirmação de reunião (pendências).
4. **P: idêntico à 2.3** — `P[i] = 2·(β_i − β_SPY) / Σ_j |β_j − β_SPY|`, convenção Σ|P| = 2, centro β_SPY estimado (`P[SPY] = 0` exato). Como os β são os mesmos, **o vetor P é literalmente o mesmo da 2.3** — o que muda entre as views é só a surpresa. ⚠️ Herda o acoplamento da 2.3: se a origem do β mudar lá, muda aqui junto.
5. **Q da linha:** `Q = surpresa_caminho · Σ_i P[i] · β_i`. Unidades: surpresa em bps, β em %/bp → Q em %. Mesma leitura de spread (retorno do lado comprado − lado vendido) e mesma propriedade da 2.3 (`|Q|` cresce com a dispersão dos βs).
6. **Sanity check de sinal (⚠️ teste obrigatório na implementação):** números inventados, só para fixar o sinal. Poly mais dovish que o ZQ dez: `E_poly = 4.00%`, `E_ZQdez = 4.30%` → `surpresa = −30bp`. `β_XLK = −0.08%/bp` → retorno esperado de XLK = `(−0.08) × (−30) = +2.4%` → **XLK entra long**. Mesma estrutura de teste da 2.3.
7. **Ativação/desligamento (herda a regra da 2.4/3.1):** existe mercado de trajetória → view ativa (liquidez é papel do Ω); **desliga no último dia antes do primeiro tick de resolução** (a última reunião do ano resolve o mercado — o salto de resolução não pode virar alfa).

## Decisões rejeitadas (referência)

- **Herdadas da 2.3** (mesma maquinaria, valem igual): divergência direta em probabilidade (do ZQ sai esperança, não probabilidade); β da literatura como fonte de valores; FedWatch como benchmark; P como par simples ou cesta vs cesta; centros alternativos para o P.
- **Rolar o ZQ mês a mês:** perderia o alvo fixo (fim do ano) que define a pergunta da view; o contrato é o de dezembro.

## Pendências desta view

- ⚠️ **Reunião — entra ou não.** Sub-questões a resolver na mesma discussão:
  - **Dupla exposição com a 2.3:** quando o poly é mais dovish nas duas perguntas (caso comum), as duas views empurram os mesmos setores na mesma direção. Aceitar (Σ/Ω penalizam views correlacionadas em parte) vs regra explícita (nunca ligadas juntas / teto conjunto).
  - **Confirmar o reuso do β da 2.3** (premissa do item 3) vs exigir regressão própria contra a surpresa de caminho.
  - **Janela que encolhe + rolagem anual:** o mercado "até dezembro" tem o mesmo problema de horizonte da 3.1 (a pergunta encolhe ao longo do ano; qual mercado usar em cada data na virada 2024→2025). Decidir junto com a pendência de horizonte da 3.1 — a solução deve ser a mesma.
- **Paulo:** quais mercados de cortes acumulados / taxa de fim de ano existem no CLOB (2023–25), histórico, liquidez e estrutura dos buckets; profundidade/qualidade do **ZQ de dezembro** no yfinance (o ZQ próximo já era pendência da 2.3).
- Pré-processamento das PMFs: entra no módulo da decisão 9 (verificar se os buckets de trajetória se comportam como os de FOMC — ex.: bucket aberto "5+ cortes").
