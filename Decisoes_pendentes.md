# Decisões pendentes — mock do projeto

Decisões de implementação que faltam fechar antes/durante o mock. À medida que resolvemos, registramos a decisão na própria seção (status: 🔴 aberta · 🟡 em discussão · 🟢 fechada).

---

## 1. Universo de ativos e fonte de preços 🟢
Lista fechada de instrumentos negociáveis que formam o vetor de pesos.

**Decisão:**

Critério de divisão por **horizonte** (não por tamanho de ativo):
- **Camada estrutural** (posições lentas) → setores + classes de ativos.
- **Camada tática** (trades rápidos) → ações individuais, definidas depois.

Universo da camada estrutural (cobre as 5 views: Fed 2.3, inflação 2.2, eleitoral 2.4, momentum 1.2, sentimento macro 3.1):

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

## 3. Sensibilidade (β) por view 🔴
Cada view estima internamente o β que converte seu sinal (divergência, spread, probabilidade) em magnitude de retorno pro Q. Cada ideia da Camada 1 olha seu próprio mercado do poly (histórico + probabilidade atual) e monta P e Q sozinha — a sensibilidade vive dentro da view, não numa tabela central compartilhada.

Fecha **junto com a Decisão 4**, por família (estimar o β e fabricar o Q são a mesma operação). Em aberto: a **forma da regressão** que cada família usa para extrair a magnitude do histórico — mudança de probabilidade vs. dummy de resolução, possivelmente diferente por família.

(Nota de nomenclatura: no `Mapa_de_camadas.md` "Camada 2" = **camada tática** — o que o grupo congelou foi a tática, não esta estimação.)

**Decisão:** _(a registrar junto com a Decisão 4)_

## 4. Tradução probabilidade → vetor Q 🔴
Como cada view converte a probabilidade do poly em retorno esperado (a unidade que o BL exige) — a ponte entre "65% de corte" e um número de retorno. Não é fórmula única: cada view traz sua própria âncora acadêmica e monta o Q a partir do histórico do seu mercado. Fecha **junto com a Decisão 3**, por família (estimar o β e fabricar o Q são a mesma operação). As 5 views estruturais se agrupam em 2 famílias:

**Família A — divergência + sensibilidade** (esqueleto comum: `Q = sensibilidade × (prob_poly − prob_mercado)`, forma relativa par/cesta):

| View | Âncora | Sinal do poly | Q natural | Falta decidir |
|------|--------|---------------|-----------|---------------|
| **2.3 Fed** | Bernanke-Kuttner (surpresa de juros → setores duration-sensitive) | divergência poly vs Fed Funds futures | `β_setor × (prob_poly − prob_FedFunds)`; tech/RE vs defensivos | de onde vem `β_setor` (sensibilidade estreita) |
| **2.2 Inflação** | Fisher / breakeven | divergência poly-CPI vs breakeven TIPS | quase mecânico: Δinflação × duration → TIP vs TLT; não precisa de regressão | duration/maturidade usada como conversor |
| **2.4 Eleitoral** | Pástor-Veronesi (cestas por candidato) | divergência prob-implícita-no-spread-da-cesta vs prob poly | gap até o "preço justo" da cesta na prob do poly; cesta ganhadora vs perdedora | montar as cestas (gargalo) + modelo de valor justo da cesta a p% |
| **3.1 Sentimento macro** | índice agregado de vários mercados | divergência de nível índice vs preço em juros/bolsa | tilt amplo SPY/TLT (regime de fundo) | é view ou é contexto/prior? granularidade do índice |

**Família B — série temporal** (não encaixa no template de divergência):

| View | Âncora | Sinal do poly | Q natural | Falta decidir |
|------|--------|---------------|-----------|---------------|
| **1.2 Momentum** | Time-series momentum / sticky expectations | derivada (tendência da prob), não divergência | direcional pelo sinal da tendência; ajusta beta/setor | sem âncora de divergência → magnitude é o ponto fraco; é estrutural ou tático? |

**Escopo v1:** a **camada tática** (velocidade/derivada, event-driven 3.2, PEAD 1.1) fica fora do v1 — depende de alta frequência que a API do poly não entrega. As views estruturais não são bloqueadas: cada uma estima seu próprio β (2.3 via β estreita de surpresa de juros; 2.2 nem precisa de regressão — converte via duration). Falta próprio de cada view: 2.4 depende de montar as cestas; 3.1 de definir view vs. prior; 1.2 (momentum) precisa de discussão à parte (pode sair junto com a tática).

**Perguntas de reunião:**
1. Adotam o template compartilhado da Família A (`Q = sens × divergência`, relativa) como esqueleto comum, especializando view a view só o benchmark e a sensibilidade?
2. Quais views entram no v1? (2.2 e 2.3 são as mais diretas; 2.4 depende das cestas; 3.1 depende de view-vs-prior.)
3. 1.2 momentum: view estrutural (precisa de magnitude) ou reclassifica p/ tática?

Cada template ainda tem **parâmetros numéricos** (as `β`, a duration, o "preço justo da cesta") que vêm de decisão humana (regra CLAUDE.md §6) — não inventados.

**Decisão:** _(a registrar — tudo acima em aberto)_

## 5. Definição operacional de "surpresa" (PEAD, 1.1) 🔴
Fórmula da surpresa. `1 − prob_atribuída`? Contínua ou por threshold?

**Decisão:** _(a registrar)_

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

---

**Próximo passo:** voltar para a Decisão 1.
