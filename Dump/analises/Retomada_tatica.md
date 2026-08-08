# Inventário de cortes — por que cada view e cada tática caiu, e o que reabriria

> **O que é:** um lugar só com o motivo de cada corte do projeto e, ao lado, **o
> que teria de mudar** para o desenho voltar. Escrito para a sessão seguinte
> começar por aqui em vez de redescobrir.
>
> **O que NÃO é:** decisão. Nenhuma linha reabre nada — a coluna "o que reabriria"
> lista condição, não recomendação. Reabrir view ou ligar tática é decisão do
> grupo, sob o regime das seções 9/10 do `Decisoes_pendentes.md`.
>
> **Escrito por:** Felipe (sessão 14, 2026-08-08), depois da D17. Estado: 2 views
> vivas, camada tática desligada, entrega 17/08.

---

## 1. Views — 11 desenhadas, 2 vivas

**Nenhuma view foi cortada por dar excesso negativo no backtest.** Vale registrar
por quê: as duas vivas foram escolhidas na maratona de **04/08** (seção 9), e o
backtest só existiu em **05/08** (seção 10) — elas não podiam ter sido escolhidas
por número, porque não havia número.

| view | por que caiu | o que reabriria | vale a pena? |
|---|---|---|---|
| **2.2 inflação** | — **VIVA** | — | — |
| **2.3 Fed** | — **VIVA** (325 de 374 pregões, 87%) | — | — |
| 2.4 eleitoral | efeito aterrissa no **gap de abertura**: sobra 23% na janela negociável e o TLT — o "Trump trade" mais forte — some inteiro (−0,072 no gap → +0,010 no negociável). Depois **reprovou fora da amostra**: na Câmara 2026 os sinais deveriam inverter contra 2024 se o mecanismo fosse partidário, e o TLT cai nos **dois** mercados | nada barato — dois testes independentes, um deles fora da amostra | **não** |
| 3.1 recessão | no par que a view monta (defensivo − cíclico) **não há sinal** (t −0,46 a −1,05). Mas existe efeito **direcional** significante (SPY +0,59% em 10 pregões) que o P neutro em mercado (`P[SPY] = 0`) não consegue expressar | redesenhar com **P direcional** — mesma discussão da 15b, e a obrigação 5a de `views_common.py` vale para as duas juntas. Ressalvas registradas na D2b: 245 pregões, um ano só, z-score in-sample | **sim — é o corte mais defensável de todos** |
| C geopolítica/energia | mecanismo real e é a **correlação mais forte da maratona** (XLE r = +0,54 no gap), mas nada sobra na janela negociável, com **27 observações** | mais mercados de evento geopolítico do poly — pedido ao Paulo | só com dado novo |
| E tarifas | **13 dias** de cobertura | idem | só com dado novo |
| G fiscal | **3 dias** de cobertura | idem | só com dado novo |
| B trajetória (original) | três somados: duplica a 2.3 (β e P idênticos por desenho da espec), cobre metade da janela (M3 é só 2025, ~210 de 374 pregões), e o ZQ de dezembro não tem fonte grátis | **superada pela 15g** — ver linha abaixo | — |
| **15b incerteza de anúncio** | **candidata PRONTA** (8 testes), não depende do Paulo. Premissa passou: anúncio incerto rende +0,383% contra −0,704% do previsível, t de Welch +2,10, mesma direção em FOMC e CPI separados | duas decisões do grupo: **15b** (é a primeira view direcional do projeto, ΣP ≠ 0) e **15c** (escala da incerteza — entropia crua t +0,32 vs. percentil na família t +1,96) | **sim — é a mais perto de entrar** |
| 15f transversal do CPI | reprovou no **teste de sinal** | — | não |
| **15g B com β próprio** | **candidata MEDIDA.** A objeção de duplicação era do DESENHO, não da view: estimando o β contra outro vértice da curva, o ângulo entre o P dela e o da 2.3 é **95,6°** (corr −0,34) — praticamente ortogonais, dimensão nova no BL | **só o `G10a` do Paulo** (uma série do FRED, `DGS1`) — único item bloqueante do pedido G10 | **sim, e é barato** |

---

## 2. Camada tática — 12 desenhos, 0 vivos, em quatro ondas

Não caiu por uma razão. Caiu por três, em ordem: **escopo** → **tamanho sem
âncora** → **falta de sinal**. Consertei a do meio e a terceira apareceu por
baixo.

| # | desenho | onde caiu | por que caiu | cortada por P&L? |
|---|---|---|---|---|
| 1 | PEAD (1.1) | reunião | fora do escopo — **nunca medida** | não |
| 2 | event-driven (3.2) | reunião | idem | não |
| 3 | velocidade de ajuste | reunião | idem | não |
| 4 | gap de fim de semana | D3b (04/08) | condicionar a \|Δp\| grande **funcionou como método** (achou SPY t +2,22, XLF t +3,21 onde a versão incondicional não achava), mas o sinal é de **reversão**, não de continuação — a tática compraria a direção do poly e perderia | não — teste de sinal |
| 5 | prêmio de anúncios (1.3) | 12c (07/08) | Δ monótono no orçamento, sem ótimo interior. **A premissa passou; o dimensionamento é que não tinha âncora** | não — parâmetro |
| 6 | drift pós-FOMC (ΔDTB3) | 12c (07/08) | idem — e o Δ dela era **POSITIVO**, +0,08 a +0,80 pp | não, **e é o ponto** ↓ |
| 7 | sleeve drift FOMC (poly) | D16 (08/08) | surpresa mediana **0,52 bps** em 17 reuniões: o poly acerta o Fed quase na mosca, não há direção a ler | sinal **e** P&L (−35,23 pp) |
| 8 | sleeve drift CPI | D16 (08/08) | μ invertido — TLT (nominal) anda mais que TIP (indexado), contra a premissa do livro; pela D2b não se inverte | sinal **e** P&L (−5,31 pp) |
| 9 | C1a revisão do M3 | D17 (08/08) | G1 = **0,5×** o tick | não — nem chegou ao P&L |
| 10 | C1b revisão da reunião | D17 (08/08) | G1 = **0,2×** o tick | não |
| 11 | C2a cauda da PMF de CPI | D17 (08/08) | μ invertido nos dois ativos; ρ = **−0,68** com a entropia da 15b (é a 15b com outro nome) | não |
| 12 | C2b cauda da PMF de reunião | D17 (08/08) | G1 = 1,2×; μ meio invertido; ρ = +0,58 com a entropia | não |

**Os dois fatos que resumem a camada:**

1. **Uma tática que media positivo foi desligada** (nº 6, +0,08 a +0,80 pp),
   porque ligar exigia escolher um `orcamento` que não sai de teoria nenhuma e a
   grade era monótona — a melhor linha era sempre a última, onde a varredura
   parou. Escolher a linha de cima seria calibrar tamanho contra 374 pregões de
   resultado. **Isso é o oposto de overfit**, e deve ir ao relatório como tal.
2. **A premissa que sobreviveu mudou de camada, não morreu:** o prêmio de
   anúncios (nº 5) virou a **view 15b**, onde quem dimensiona é o BL (τ, Ω, Σ) e
   o parâmetro sem âncora deixa de existir.

---

## 3. O que reabriria a camada tática, em ordem de custo

### 3.1 O experimento que NUNCA foi feito — e é o mais barato 🔬

**A D16 trocou duas coisas ao mesmo tempo.** Ela substituiu a âncora de tamanho
(orçamento → `inv(δΣ)·μ`) **e** a fonte da surpresa (ΔDTB3 → Polymarket). A
surpresa do poly acabou sendo ~zero e a sleeve morreu — mas a surpresa ANTIGA
nunca foi rodada com a âncora NOVA.

|  | surpresa ΔDTB3 (antiga) | surpresa do poly (D16) |
|---|---|---|
| **orçamento** (12c) | medido: **+0,08 a +0,80 pp**, desligado por falta de âncora | — |
| **`inv(δΣ)·μ`** (D16) | **nunca rodado** ⬅ | medido: −5,68 pp, reprovado |

A célula vazia é o desenho nº 6 com o parâmetro que o matou **removido**. E o
ΔDTB3 tem dispersão de verdade onde o poly não tinha: σ = 3,3 bps, mínimo −11,
máximo +4, com 3 de 36 reuniões acima de 5 bps (`Surpresa_fomc_sem_ZQ.md`).

**Como fazer, e o custo:** **uma linha no `gate_sleeves.py`**, não um módulo. O
G1 responde primeiro se a mediana de \|ΔDTB3\| passa de 1 bp (o tick do FRED) —
se não passar, morre pelo mesmo motivo da sleeve do poly e custou uma linha. Se
passar, aí sim vale o módulo, e o G2 já tem o sinal declarado e **medido 7 de 7**
em `Surpresa_fomc_sem_ZQ.md` (Bernanke-Kuttner: surpresa de alta → SPY e TLT
caem).

> ⚠️ Contra o próprio candidato: a mediana **com sinal** do ΔDTB3 é +0,0 bps. A
> mediana do valor ABSOLUTO não está medida — é exatamente o que a linha do gate
> responde, e pode matar a ideia de imediato.

### 3.2 Os três desenhos que ninguém mediu

PEAD (1.1), event-driven (3.2) e velocidade de ajuste saíram **por escopo, sem
uma única medição**. São os únicos desenhos táticos do projeto cujo sinal nunca
foi testado — todo o resto já tem certidão de óbito com número.

**Custo:** uma linha do gate cada, se houver como construir o sinal com o dado do
`data/`. **Ressalva honesta:** saíram de decisão de prioridade em reunião, então
medi-las é reabrir escopo, não só rodar script.

### 3.3 O gap de fim de semana, invertido

O nº 4 achou sinal — de **reversão**. Não foi invertido porque seriam 25
observações de um mercado, num ano em que a reversão intradiária foi o regime.
**Reabriria com:** mais mercados do poly cobrindo reaberturas, para a reversão ser
testada fora daquele ano. É pedido ao Paulo.

### 3.4 O que está bloqueado em terceiros

- **`etf_open_daily.parquet` está em outra base de ajuste** que o
  `etf_prices_daily.parquet`: TIP e TLT ganham +1,15% e +0,40% fabricados por dia
  na amostra antiga (`Premissa_taticas.md`). Enquanto isso não for corrigido (um
  pull dos dois no mesmo dia — **módulo do Paulo**), **nenhuma tática pode medir
  o retorno do PRÓPRIO dia do evento**, só do seguinte. Como o achado transversal
  do projeto é que a informação aterrissa no **gap de abertura**, este conserto é
  o que destravaria a única janela onde ainda pode haver sinal.

### 3.5 A classe inteira que nunca foi tentada

**Todos os 12 desenhos leem uma PMF do Polymarket** (o nº 6 é a exceção parcial,
via ΔDTB3). Se a conclusão da D17 é que o poly ou não tem tamanho (revisão diária
abaixo do tick) ou já pertence a uma view, então a tática que sobra é a que **não
lê o poly**. Isso é mudança de premissa do projeto, não de desenho — **decisão do
grupo**, e provavelmente fora do escopo de um desafio sobre Polymarket.

---

## 4. Ferramenta pronta para a próxima sessão

| | |
|---|---|
| **Gate** | `scripts/gate_sleeves.py` → `Dump/analises/Gate_sleeves.md`. Uma linha por candidato: G0 cobertura, G1 dispersão ÷ tick, G2 sinal declarado a priori, G3 duplicação com as views. Carrega as duas sleeves reprovadas da D16 como **grupo de controle** — se elas não reprovarem, o gate está errado |
| **Âncora de tamanho** | `src/tatica_drift_anuncio.estimate_drift_mu` + `build_overlay`. `inv(δΣ)·μ` com encolhimento pela dispersão, **zero parâmetro livre**. Sobreviveu ao teste e está **sem uso** |
| **Regra da casa** | rodar a linha do gate **antes** de abrir editor. A D16 custou 400+ linhas e 11 testes para descobrir o que o gate responde em uma linha |

**O resumo em uma frase, e é o que a próxima sessão precisa aceitar ou
derrubar:** *falta sinal, não dimensionamento.*
