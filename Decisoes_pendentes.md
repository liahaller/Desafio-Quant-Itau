# Decisões pendentes — mock do projeto

Decisões de implementação que faltam fechar antes/durante o mock. À medida que resolvemos, registramos a decisão na própria seção (status: 🔴 aberta · 🟡 em discussão · 🟢 fechada).

---

## 1. Universo de ativos e fonte de preços 🟢
Lista fechada de instrumentos negociáveis que formam o vetor de pesos.

**Decisão:**

Critério de divisão por **horizonte** (não por tamanho de ativo):
- **Camada estrutural** (posições lentas) → setores + classes de ativos.
- **Camada tática** (trades rápidos) → ações individuais — camada adiada, fora do escopo (decisão 10); universo tático a definir na retomada.

Universo da camada estrutural (cobre as views: Fed 2.3, inflação 2.2, eleitoral 2.4, recessão 3.1 — ex-sentimento macro; momentum 1.2 reclassificada como tática — adiada, decisão 10):

| Ticker | O que é | Views que atende |
|--------|---------|------------------|
| XLK | Tecnologia | Fed (long-duration), eleitoral, momentum |
| XLU | Utilities (defensivo) | Fed (defensivo/duration), eleitoral |
| XLP | Consumo defensivo | Fed (defensivo) |
| XLF | Financeiro | Fed (sensível a juros), eleitoral |
| XLE | Energia | Eleitoral/regulatória |
| XLV | Saúde | Eleitoral/regulatória |
| TIP | Títulos protegidos contra inflação (TIPS) | Inflação |
| TLT | Treasuries nominais longos | Inflação (par), Fed |
| SPY | Ações EUA amplo | Âncora de mercado (prior do BL), macro |

- Granularidade: setores + classes de ativos (sem ação individual na estrutural).
- Treasuries nominais: **TLT** (longos, mais sensível a juros — amplifica as views de juros).
- Fonte de preços: yfinance · frequência diária.

**Fechado:** universo restrito aos EUA. Sem proxy de Brasil (EWZ); a view 3.1 opera apenas sobre ativos americanos.

## 2. Acesso ao Polymarket 🟢
De onde vêm os dados do poly no mock: API real · snapshot histórico · dados sintéticos.

**Decisão:** API CLOB oficial do Polymarket (endpoint `/prices-history`).

## 3. Sensibilidade (β) por view 🟡
Cada view estima internamente o β que converte seu sinal (divergência, spread, probabilidade) em magnitude de retorno pro Q. Cada ideia da Camada 1 olha seu próprio mercado do poly (histórico + probabilidade atual) e monta P e Q sozinha — a sensibilidade vive dentro da view, não numa tabela central compartilhada.

Fecha **junto com a Decisão 4**, por família (estimar o β e fabricar o Q são a mesma operação). Em aberto: a **forma da regressão** que cada família usa para extrair a magnitude do histórico — mudança de probabilidade vs. dummy de resolução, possivelmente diferente por família.

(Nota de nomenclatura: no mapa de camadas — hoje seção de `Informações_uteis/Black-Litterman_com_Polymarket.md` — "Camada 2" = **camada tática**; o que o grupo congelou — e depois adiou de vez (decisão 10) — foi a tática, não esta estimação.)

**Decisão (parcial, reunião 2026-07-08/09):** fechada para as views **2.2** (β = duration do breakeven 10a, sem regressão — exceção mecânica), **2.3** (regressão própria event-study contra surpresa à la Kuttner; literatura B-K só como sanity check) e **2.4 — condicionalmente** (regressão própria retorno diário do ETF vs Δp(Trump), híbrida com regra explícita: o β manda sempre, literatura Pástor-Veronesi só como sanity check a posteriori, nunca inverte o β; janela expandida encerrada antes de cada rebalanceamento, sem lookahead — o critério de liquidez define só o início da amostra; teste de defasagem Δp(t−1)→retorno(t) obrigatório; condição: bid/ask histórico no CLOB). Detalhes e alternativas rejeitadas em `Informações_uteis/views/view_2.2_inflacao.md`, `view_2.3_fed.md` e `view_2.4_eleitoral.md`. **3.1 fechada condicionalmente (sessão 2026-07-10)** — reframe para view de recessão; β por regressão própria vs Δp_poly com teste de defasagem (maquinaria da 2.4) → `views/view_3.1_recessao.md`. (1.2 reclassificada como tática em 2026-07-10 — adiada junto com a camada, decisão 10.)

## 4. Tradução probabilidade → vetor Q 🟡
Como cada view converte a probabilidade do poly em retorno esperado (a unidade que o BL exige) — a ponte entre "65% de corte" e um número de retorno. Não é fórmula única: cada view traz sua própria âncora acadêmica e monta o Q a partir do histórico do seu mercado. Fecha **junto com a Decisão 3**, por família (estimar o β e fabricar o Q são a mesma operação). As 5 views estruturais se agrupam em 2 famílias:

**Família A — divergência + sensibilidade** (esqueleto comum: `Q = sensibilidade × (prob_poly − prob_mercado)`, forma relativa par/cesta):

| View | Âncora | Sinal do poly | Q natural | Falta decidir |
|------|--------|---------------|-----------|---------------|
| **2.3 Fed** | Bernanke-Kuttner (surpresa de juros → setores duration-sensitive) | divergência poly vs Fed Funds futures | `β_setor × (prob_poly − prob_FedFunds)`; tech/RE vs defensivos | 🟢 fechada → `views/view_2.3_fed.md` |
| **2.2 Inflação** | Fisher / breakeven | divergência poly-CPI vs breakeven TIPS | quase mecânico: Δinflação × duration → TIP vs TLT; não precisa de regressão | 🟢 fechada → `views/view_2.2_inflacao.md` |
| **2.4 Eleitoral** | Pástor-Veronesi (cestas por candidato) | divergência prob-implícita-no-spread-da-cesta vs prob poly | gap até o "preço justo" da cesta na prob do poly; cesta ganhadora vs perdedora | 🟢 fechada condicionalmente → `views/view_2.4_eleitoral.md` |
| **3.1 Recessão** (ex-Sentimento macro) | Estrella-Mishkin (curva 10a−3m antecipa recessão) | divergência poly-recessão vs prob implícita na curva (probit publicado) | `Q = (Σ P·β) × (p_poly − p_curva)`; cíclicos vs defensivos + SPY/TLT | 🟢 fechada condicionalmente → `views/view_3.1_recessao.md` |

**Família B — série temporal** (não encaixa no template de divergência):

| View | Âncora | Sinal do poly | Q natural | Falta decidir |
|------|--------|---------------|-----------|---------------|
| **1.2 Momentum** | Time-series momentum / sticky expectations | derivada (tendência da prob), não divergência | direcional pelo sinal da tendência; ajusta beta/setor | 🟢 reclassificada como **tática** (2026-07-10) → adiada junto com a camada (decisão 10); sem âncora de magnitude estrutural |

**Escopo:** a **camada tática** (velocidade/derivada, event-driven 3.2, PEAD 1.1) foi **adiada — removida do escopo do projeto** (decisão 10; já estava fora do v1 por depender de alta frequência que a API do poly não entrega). As views estruturais não são bloqueadas: cada uma estima seu próprio β (2.3 via β estreita de surpresa de juros; 2.2 nem precisa de regressão — converte via duration). Falta próprio de cada view (restantes): **3.1: resolvida (2026-07-10)** — é view, estreitada para recessão (caminhos "índice" e "contexto/Ω" rejeitados; o Ω reativo já cobre a leitura de regime); resta a pendência de horizonte (reunião). **1.2 (momentum): reclassificada como tática em 2026-07-10** — o gatilho é a velocidade/tendência da probabilidade (mesma natureza da camada tática) e não há âncora de magnitude para o template estrutural; adiada junto com a camada (decisão 10), reabre com a retomada.

**Pergunta de reunião (restante — 2.2/2.3/2.4/3.1 fechadas; 1.2 reclassificada como tática, 2026-07-10):**
1. Horizonte da 3.1: poly "recessão até dez" (janela que encolhe) vs curva 12m rolante + rolagem entre mercados anuais — opções mapeadas em `views/view_3.1_recessao.md`.

Cada template ainda tem **parâmetros numéricos** (as `β`, a duration, o "preço justo da cesta") que vêm de decisão humana (regra CLAUDE.md §6) — não inventados.

**Decisão (parcial, reunião 2026-07-08/09):** fechada para as views **2.2 Inflação**, **2.3 Fed** e **2.4 Eleitoral** — documentação completa (fórmulas, cascata de degradação, decisões rejeitadas, pendências) em `Informações_uteis/views/view_2.2_inflacao.md`, `view_2.3_fed.md` e `view_2.4_eleitoral.md`. Em resumo:
- **2.2:** `Q = duration(10a, ~8) × (E_poly[CPI] − breakeven T10YIE)`, par TIP−TLT; E_poly via média da PMF dos buckets de CPI (com normalização, favorite-longshot e bucket aberto tratados). Exceção à Família A (sem sensibilidade estimada).
- **2.3:** `surpresa = E_poly[Δtaxa] − E_FF[Δtaxa]` (bps; E_FF do futuro ZQ, contrato do mês posterior); β por regressão própria; `P[i] = 2·(β_i − β_SPY)/Σ|β_j − β_SPY|` (função determinística do vetor β; fator 2 = convenção Σ|P| = 2, reunião 2026-07-10); `Q = surpresa · Σ P[i]·β_i`.
- **2.4 (fechada condicionalmente — condição: bid/ask histórico no CLOB):** só eleitoral ("regulatória" saiu do nome — firm-specific iria p/ tática 3.2, hoje adiada — decisão 10); evento = presidencial EUA 2024, binário de vencedor sobre p(Trump); **segunda exceção à Família A** — não há instrumento externo precificando o evento, o benchmark é o **próprio poly defasado**: `Q = (Σ P[i]·β_i) × (p_t − p_{t−k})`, com k estimado pelo teste de defasagem e β de absorção plena (soma dos coeficientes dos lags 0…k). **Q é retorno acumulado de k dias** (reconciliar horizonte com Σ/π — pendência); se k ≈ 0 a view **nunca liga** (condição permanente, não a cascata episódica — fallback contemporâneo vs sair do v1 é pendência de reunião); `P[i] ∝ (β_i − β_SPY)`, Σ|P| = 2 (fixação de escala apenas; ΣP ≠ 0 com centro em β_SPY); view desliga no último dia **antes do primeiro tick de resolução** (senão Δp = +0,4 de 5–6/nov fabrica alfa); preço da série = **midpoint bid/ask**, nunca último trade (último trade stale infla k).

- **3.1 (fechada condicionalmente, sessão 2026-07-10 — condições: mercado de recessão com bid/ask histórico no CLOB; horizonte pendente de reunião):** reframe do índice de sentimento para **view de recessão** — `Q = (Σ P[i]·β_i) × (p_poly − p_curva)`; `p_poly` de mercado binário de recessão (preferência: resolução técnica GDP; midpoint bid/ask + decisão 9); `p_curva` de probit clássico com coeficientes publicados (Estrella-Mishkin/NY Fed) sobre spread 10a−3m do FRED; β por regressão própria vs Δp_poly com teste de defasagem e absorção plena (maquinaria da 2.4); P espelha a 2.3 (`P[i] ∝ β_i − β_SPY`, Σ|P| = 2); ativação/desligamento herdados da 2.4. Detalhes e rejeitadas: `views/view_3.1_recessao.md`.

**1.2 Momentum: fechada (2026-07-10) — reclassificada como tática, adiada junto com a camada (decisão 10).** Nova decisão derivada: **9** (pré-processamento de PMFs compartilhado). Pendência transversal da normalização **fechada em reunião (2026-07-10): convenção única Σ|P| = 2** para todas as views — o Q de toda view se lê como "retorno do lado comprado − lado vendido" (spread). 2.2 e 2.4 já estavam na convenção; a 2.3 ganhou fator 2 no P (o Q dobra sozinho, pois é calculado a partir do P). Alternativa rejeitada: Σ|P| = 1 (leitura de média ponderada — exigiria mexer em 2.2 e 2.4, e o par TIP−TLT viraria ±0,5). Detalhe em `views/view_2.3_fed.md`.

## 5. Definição operacional de "surpresa" (PEAD, 1.1) 🟢
Fórmula da surpresa. `1 − prob_atribuída`? Contínua ou por threshold?

**Decisão:** sem objeto — o PEAD (1.1) pertence à camada tática, adiada e removida do escopo em reunião (decisão 10, registrada 2026-07-09). Reabrir se/quando a tática for retomada.

## 6. Forma funcional do Ω reativo 🔴
Como volume, estabilidade, convergência e proximidade de evento viram um número de confiança. Versão mínima para o mock vs. versão completa.

**Decisão:** _(a registrar)_

## 7. Convergência entre fontes (polls, casas de aposta) 🟡
Se entra no Ω já no v1 ou fica como stub (adiciona dependências de dados).

**Decisão:** fora do v1 — fica como stub. Reavaliar depois se entra em versão futura (em aberto).

## 8. Passo final do otimizador: qual Σ e quais restrições 🟢
Surgiu na implementação do esqueleto BL (`src/bl_optimizer.py`).

**Contexto:** o passo `w = inv(δΣ)μ` aceita duas covariâncias:
- **Σ amostral** — pesos respondem só à mudança na média; com confiança zero volta exatamente a `w_mkt`.
- **Σ_bl posterior (He & Litterman)** — incorpora a incerteza das views; com confiança zero os pesos encolhem para `w_mkt/(1+τ)` (sobra caixa implícito).

Também em aberto estava: restrições nos pesos (long-only? soma 1? limite de alavancagem?).

**Decisão (parte A — qual Σ):** fechada em reunião (2026-07-07): **Σ amostral** no passo final. Motivos: caso neutro limpo (confiança zero → carteira = `w_mkt`, isola o efeito do Polymarket) e o encolhimento por incerteza já é papel do Ω reativo.

**Decisão (parte B — restrições):** fechada em reunião (2026-07-07): **B1 — irrestrito** (fórmula fechada, sem restrições nos pesos). Aceita-se short e desvio da soma = 1 vindos das views; todo desvio de `w_mkt` é atribuível ao sinal do Polymarket, e os testes analíticos permanecem válidos. Reavaliar se o backtest mostrar pesos extremos.

_Alternativas descartadas (referência para reavaliação futura):_
- **B2 — restrições formais** (long-only, soma = 1, teto por ativo) via programação quadrática (`scipy.optimize.minimize`/SLSQP). Carteira sempre realista e ótima dentro das regras, mas perde a fórmula fechada, exige solver + reescrita dos testes e distorce a atribuição view→peso quando uma trava ativa.
- **B3 — pós-processamento**: truncar pesos negativos em zero e renormalizar para somar 1. Barato (~3 linhas) e preserva o núcleo analítico, mas o resultado não é ótimo e a renormalização distorce pesos de ativos não relacionados à view.
- **B4 — travar na origem**: limitar magnitude de Q (decisão 4) e/ou piso no Ω (decisão 6) para que a carteira irrestrita raramente shorte/alavanque. Zero mudança no otimizador, mas não é garantia formal e transfere a discussão para as decisões 4 e 6.

## 9. Pré-processamento de PMFs do Polymarket — módulo compartilhado entre views? 🟢
Surgiu no fechamento das views 2.2 e 2.3 (decisões 3/4). Buckets de CPI (view 2.2) e buckets de FOMC (view 2.3) têm a mesma estrutura — PMF de faixas mutuamente exclusivas — e o pré-processamento é o mesmo trio nas duas: normalização (probs não somam 1 por causa do spread bid/ask), correção de favorite-longshot bias (Camada 4) e tratamento de bucket aberto. Candidato natural a objeto compartilhado.

⚠️ Esta é a **segunda** peça candidata a compartilhada entre views — a primeira (tabela central de sensibilidades) se revelou redundante. Antes de tratar como compartilhada, verificar se o pré-processamento de fato se comporta igual nas duas views (mesmo padrão de checagem que derrubou a tabela). Ex.: o favorite-longshot morde a cauda direita nos buckets de CPI; nos buckets de FOMC a cauda pode estar dos dois lados.

**Itens da view 2.4 (reunião 2026-07-09):** o binário eleitoral também entra no módulo, com três registros:
- **(a) Normalização** `p_A + p_B ≠ 1`: entra justamente por ser trivial — trivialidade replicada por view é como duas views acabam com convenções diferentes sem ninguém notar.
- **(b) Favorite-longshot:** entra, mas é quase inócuo na 2.4 — p entra como diferença (não nível) e o β é estimado sobre a mesma série transformada, então a parte linear do ajuste é absorvida pelo β; presidencial 2024 viveu ~0,35–0,65 (longe dos extremos) → segunda ordem. Sem caminho especial.
- **(c) Qual preço da série (novo item, o mais grave):** último trade vs midpoint bid/ask vs VWAP. Em mercado fino o último trade fica stale (série em degraus) e **infla artificialmente a defasagem k estimada** — para a 2.4 (onde k é o conteúdo da view) decidido **midpoint bid/ask** + reportar dias sem trade. Verificar se a mesma escolha vale para as PMFs de 2.2/2.3.

**Itens da view 3.1 (sessão 2026-07-10):** o binário de recessão entra no módulo com o mesmo trio da 2.4 — (a) normalização `p_sim + p_não ≠ 1`; (b) favorite-longshot **relevante** (mercados de recessão vivem em p baixa, região de viés máximo — ao contrário da 2.4, onde era segunda ordem); (c) preço da série = midpoint bid/ask.

**Decisão (fechada 2026-07-11, Felipe): Opção A — módulo compartilhado único** (`src/poly_preprocessing.py`, módulo do Felipe). Caixa de ferramentas de funções puras — **não** um `preprocess()` monolítico — de onde cada view chama o que precisa:
- **Midpoint bid/ask** — o módulo recebe bid e ask crus e constrói a série. Implica que o dataset do Paulo entrega colunas bid/ask (Felipe alinha com Paulo o uso da API com bid/ask histórico — mesma condição de fechamento das views 2.4 e 3.1).
- **Normalização** — dividir pela soma (binários e PMFs).
- **Favorite-longshot** — função elemento a elemento compartilhada; a **forma da correção** ainda não foi decidida → decisão 11.
- **Bucket aberto** — utilitário só das PMFs (2.2/2.3), vive no mesmo arquivo; o **valor atribuído** ainda não foi decidido → decisão 11.

_Alternativas descartadas:_ **B** (cada view implementa o seu — risco de drift silencioso de convenção na trivialidade replicada); **C** (midpoint no pipeline do Paulo — descartada porque o mandato do Paulo não inclui limpeza de Polymarket e a fonte com bid/ask será alinhada diretamente; reavaliar se a fonte final não entregar bid/ask, caso em que o midpoint deixa de existir para qualquer opção).

## 10. Escopo: camada tática adiada 🟢
Destino da camada tática (trades curtos por cima da carteira estrutural: velocidade de ajuste/derivada, event-driven 3.2, PEAD 1.1) no projeto.

**Decisão:** fechada em reunião (registrada 2026-07-09): a camada tática foi **removida do escopo do projeto — fica para retomada futura**. Já estava fora do v1 (depende de alta frequência que a API do poly não entrega); agora sai do projeto como um todo, não só do v1. Consequências:
- **Decisão 5 (surpresa do PEAD):** fecha sem objeto — reabre com a retomada da tática.
- **Decisão 1:** o universo tático ("ações individuais, definidas depois") fica sem efeito até a retomada; o universo estrutural segue inalterado.
- **Decisão 4 / view 1.2 Momentum:** fechada em 2026-07-10 — reclassificada como **tática**, adiada junto com a camada (fora do escopo). Reabre com a retomada da tática.
- **Não afetados** (não são tática): camada de risco (1.3 prêmio de anúncio), camada de calibração / Ω reativo e reserva (3.4).
- Descrições preservadas: 1.1 e 3.2 no retrato histórico (`Informações_uteis/Ideias_consolidadas.md`); "velocidade de ajuste" só na nota compacta do mapa de camadas (`Informações_uteis/Black-Litterman_com_Polymarket.md`).

**Atualização (2026-07-11, Felipe) — camada tática REFORMULADA:** das duas pendências que reabriam parcialmente esta decisão, o **dono do módulo está resolvido: Felipe** (decisão do Felipe em sessão; a camada reformulada não volta à Lia). Interface fechada em sessão (3 escolhas): contrato de chamada diária `build_overlay(...) → OverlayResult(dw, diagnostics) | None`, um módulo por tática + `src/taticas_common.py`, soma `w_final = w_bl + Σ dw` via `apply_overlays` em `taticas_common.py` (`bl_integration.py` intocado). **Código das 3 candidatas implementado** (`src/tatica_premio_anuncios.py`, `tatica_drift_pos_fomc.py`, `tatica_gap_fds.py`) — como nas views B/C/E/G, implementar NÃO fecha a entrada: **a entrada da camada na carteira e os orçamentos (`orcamento_max`, `orcamento_acoes`/`orcamento_rf`, `lam`) seguem pendentes de reunião**, junto com as sub-questões das especs (janelas 15/50, ZQ vs E_poly, micro-surpresas, desmonte em k dias, precedência tilt × rebalance).

## 11. Parâmetros do pré-processamento: fórmula do favorite-longshot e valor do bucket aberto 🔴
Surgiu no fechamento da decisão 9 (2026-07-11). O módulo `src/poly_preprocessing.py` (decisão 9, opção A) tem duas peças sem forma/valor decididos — ficam como stub `# TODO(DECISAO-11)` até fechar:

- **(a) Forma da correção de favorite-longshot** (Camada 4): como transformar p cru em p corrigido. Relevância varia por view: máxima na 3.1 (recessão vive em p baixa, região de viés máximo), cauda direita na 2.2, dos dois lados na 2.3, segunda ordem na 2.4 (p entra como diferença e o β absorve a parte linear). Opções a mapear: calibração própria sobre mercados resolvidos do poly vs curva da literatura (ex. Page & Clemen) vs sem correção no v1 (aceitar o viés e documentar).
- **(b) Valor atribuído ao bucket aberto** das PMFs (ex. "≤3.6%" → que número entra na média?): ponto médio extrapolado com meia-largura do bucket vizinho vs valor fixo escolhido vs truncar no limite.

**Decisão:** _(a registrar)_

## 12. Critério de escolha do k (defasagem) nas views 2.4 e 3.1 🟡
Surgiu na implementação da maquinaria de defasagem (sessão 2026-07-11, sessão 2). As especs das views 2.4 e 3.1 mandam "varrer k no teste de defasagem" e usar o β de absorção plena (soma dos coeficientes dos lags 0…k), mas **não especificam o critério que escolhe o k** a partir do perfil de lags.

Estado do código: `views_common.lag_regression` devolve o perfil completo de coeficientes; `k` entra como argumento humano nos `build_view` das 2.4/3.1 — nada roda sem essa decisão.

Opções mapeadas:
- **(a) Inspeção do perfil com dado real:** rodar a regressão quando o dado do Paulo chegar, olhar o perfil (spike vs resposta distribuída — inspeção que a espec 2.4 item 6 já exige de qualquer jeito, pois decide se a fórmula do Q vale) e fechar o critério em reunião com o perfil na mesa.
- **(b) Último lag estatisticamente significativo:** critério clássico, mas exige escolher limiar de t-stat e erros-padrão (mais uma decisão numérica).
- **(c) Máximo R² ajustado:** automático, sem limiar, mas pode escolher k grande por ruído e ignora a premissa de spike da fórmula do Q.

**Encaminhamento (Felipe, 2026-07-11): opção (a)** — a decisão final do critério fica em aberto até o perfil real existir; a questão volta à reunião junto com o dado. Acoplada às pendências k≈0 (2.4) e k ↔ frequência de rebalanceamento.

**Decisão:** _(a registrar — fecha com o perfil real na mesa)_

---

**Próximo passo:** reunião decide (a) a entrada das **views candidatas B, C, E e G** (docs em `Informações_uteis/views/`; G já nasce reserva; F e H foram descartadas em sessão — registro em `Informações_uteis/Pesquisa_embasamento_novas_ideias.md`) e (b) a entrada da **camada tática reformulada** com 3 candidatas (1.3 prêmio de anúncios, drift pós-FOMC e gap de fim de semana — docs em `Informações_uteis/táticas/`; código pronto, dono = Felipe desde 2026-07-11; reabre parcialmente a decisão 10: faltam entrada e orçamentos). Pendências da 3.1 (horizonte — reunião; mercado/bid-ask — Paulo, agora também condição da decisão 9) e decisões 6, 11 e 12 seguem abertas (9 fechada em 2026-07-11: opção A; 12 com encaminhamento: fecha com o perfil de lags real).
