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

## 3. Mapeamento cenário → ativos (Camada 2) 🔴
Como estimar a matriz de retornos condicionais. Regredir retorno do ativo contra o quê (mudança de probabilidade? dummy de resolução?).

**Decisão:** _(a registrar)_

## 4. Tradução probabilidade → vetor Q 🔴
Como converter probabilidade do poly em retorno esperado (unidade que o BL exige). Ponte entre "65% de corte" e um número de retorno por ativo.

**Decisão:** _(a registrar)_

## 5. Definição operacional de "surpresa" (PEAD, 1.1) 🔴
Fórmula da surpresa. `1 − prob_atribuída`? Contínua ou por threshold?

**Decisão:** _(a registrar)_

## 6. Forma funcional do Ω reativo 🟡
Como volume, estabilidade, convergência e proximidade de evento viram um número de confiança. Versão mínima para o mock vs. versão completa.

**Decisão:** _(a registrar — delegada à Lia)_

**Contexto (registrado em 08/07/2026):**
- A reunião do grupo delegou esta decisão à Lia.
- Critério proposto para fechar (protocolo de calibração, em vez de escolha
  arbitrária):
  1. **O que a matemática já determina:** a confiança `c ∈ (0,1]` escala o
     baseline de He-Litterman — `Omega_ii = diag(P·tau·Sigma·P')_ii / c` —
     de modo que `c = 1` recupera o BL clássico e `c → 0` recolhe ao prior.
  2. **O que a semântica determina:** estrutura multiplicativa
     `c = portao(volume) × f(estabilidade) × g(proximidade)` — volume é
     veto (mercado sem liquidez invalida o preço; soma ponderada permitiria
     compensação indevida); convergência fica fora do v1 (Decisão 7).
  3. **O que o dado decide:** janela da estabilidade, forma/horizonte do
     decaimento de proximidade e threshold de volume saem de teste de
     monotonicidade no histórico — faixas de confiança maiores devem
     apresentar erro realizado da probabilidade menor; empates são
     resolvidos pela forma com menos parâmetros.
- Dependências: histórico do Polymarket via pipeline do Paulo (Decisão 2:
  `/prices-history` entrega preço; disponibilidade de **volume** a
  confirmar com o Paulo).
- **Levantamento de API (20/07/2026, Lia):** não existe endpoint pronto
  de volume histórico. `/prices-history` (CLOB) só devolve `{t, p}` —
  confirma a observação do Felipe em `Para_Paulo_e_Lia.md`. A Gamma API
  (`/markets`, `/events`) traz `volume`/`volume_24hr`, mas só o agregado
  no momento da consulta, não uma série temporal. O caminho viável é a
  **Data API** (`data-api.polymarket.com`): `/trades` (ou `/activity`)
  devolve trades individuais com `timestamp`, `price`, `size`
  (`usdcSize` em `/activity`) — dá pra reconstruir volume diário
  agregando por janela de tempo, mas não vem pronto; é trabalho de
  pipeline (paginação, filtro por `condition_id`/token, bucketização).
  **Ainda não implementado.** Continua dependendo do Paulo construir
  essa agregação antes de a calibração poder rodar com dado real —
  **isso não fecha a decisão**, só torna a dependência concreta.

## 7. Convergência entre fontes (polls, casas de aposta) 🟡
Se entra no Ω já no v1 ou fica como stub (adiciona dependências de dados).

**Decisão:** fora do v1 — fica como stub. Reavaliar depois se entra em versão futura (em aberto).

## 8. Passo final do otimizador: qual Σ e quais restrições 🔴
Surgiu na implementação do esqueleto BL (`src/bl_optimizer.py`).

**Contexto:** o passo `w = inv(δΣ)μ` aceita duas covariâncias:
- **Σ amostral** — pesos respondem só à mudança na média; com confiança zero volta exatamente a `w_mkt`.
- **Σ_bl posterior (He & Litterman)** — incorpora a incerteza das views; com confiança zero os pesos encolhem para `w_mkt/(1+τ)` (sobra caixa implícito).

Também em aberto: restrições nos pesos (long-only? soma 1? limite de alavancagem?). O esqueleto atual é irrestrito (BL padrão) e deixa a escolha do Σ para o chamador.

**Decisão:** _(a registrar)_

## 9. Matriz de relação ativos × mercados do Polymarket (insumo candidato à Camada 2) 🟡
Parâmetros em aberto de `lia/matriz_relacao.py` (distance correlation em janela móvel, ativos × mercados × tempo).

**Contexto (registrado em 20/07/2026):** construída na sessão de 06/07 como infraestrutura da camada tática antiga — a Decisão 10 realocou essa camada pro Felipe, com desenho que não reaproveita a matriz. Retomada agora com objetivo mais estreito: usar a matriz como evidência exploratória de "qual mercado do Polymarket tem mais relação com qual ativo", pra apoiar a Decisão 3 (mapeamento cenário→ativo, módulo do Felipe) — não substitui a decisão dele, só informa.

**Em aberto:**
- `janela` (nº de períodos por janela móvel): sem default de propósito, o código já impõe isso — vem de decisão registrada, não de escolha arbitrária.
- `passo`: default 1 no código, não confirmado se é o desejado.
- Série do Polymarket a usar: variação de probabilidade (Δp) ou nível (p)?

Enquanto esses três não fecham, qualquer resultado da matriz é exploratório/provisório (testado com múltiplas janelas candidatas), não uma calibração final.

**Decisão:** _(a registrar)_

---

**Próximo passo:** voltar para a Decisão 1.
