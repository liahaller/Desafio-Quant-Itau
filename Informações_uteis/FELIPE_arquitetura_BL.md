# Felipe — Arquitetura Black-Litterman

## Norte geral

Você é o dono do modelo central: o motor que transforma probabilidades do Polymarket em pesos de carteira. O BL parte da carteira de mercado (prior) e se inclina na direção das views proporcionalmente à confiança (Ω). Seu trabalho é construir esse motor e as duas pontes que o alimentam: cenário→ativo e probabilidade→Q. Você também coordena a integração final.

## O que fazer

### 1. Esqueleto do otimizador BL (Semana 1)

**O quê:** o motor rodando de ponta a ponta com dados sintéticos.

**Como:**
- Implementar o BL padrão: prior de equilíbrio (pesos de mercado + retornos implícitos via reverse optimization), estrutura para matriz P (mapeamento das views nos ativos), vetor Q (retornos das views) e matriz Ω (confiança).
- Rodar com Q e Ω inventados só para validar a mecânica: confiança alta → carteira segue as views; confiança baixa → carteira fica no prior.
- Interfaces claras: o Ω vem da Lia, os dados vêm do Paulo — definir os formatos de entrada com eles já na Semana 1.

**Deadline:** 13/jul.

### 2. Camada 2 — mapeamento cenário→ativo (Semana 2)

**O quê:** a tabela de sensibilidades que responde "se o cenário X acontecer, o que fazem os ativos?".

**Como:**
- Regressões condicionais / análise de eventos no histórico dos ETFs: sensibilidade de cada ativo a cada estado do mundo (corte de juros, recessão, etc.).
- Depende do dataset do Paulo — comece com a estrutura e dados parciais, feche quando o dataset unificado chegar (20/jul).
- A decisão conceitual do mapeamento (Decisão pendente 1) deve ter sido fechada na reunião de 07/jul.

**Deadline:** 20/jul.

### 3. Bridge probabilidade→Q (Semana 2)

**O quê:** o tradutor que transforma "Polymarket dá 65% de corte" numa view concreta (ex. "long-duration supera defensivos em X%").

**Como:**
- Implementar a fórmula fechada na reunião de 07/jul (Decisão pendente 2): magnitude vinda da sensibilidade histórica (Camada 2) ponderada pela probabilidade (ou pela divergência poly vs. mercado, ex. poly 65% vs. Fed Funds 45%).
- Aplicar a correção de favorite-longshot bias antes da tradução.

**Deadline:** 20/jul.

### 4. Integração e backtest (Semana 3)

- Coordenar a integração: otimizador + dados (Paulo) + Ω reativo (Lia) num pipeline único. **Deadline: 23/jul.**
- Rodar o backtest completo com Paulo, validar e iterar. **Deadline: 25/jul.**

### 5. Fechamento (Semana 4)

Revisar resultados (28/jul), limpar código/repositório com Paulo (30/jul), entrega (31/jul).

## Organização com Claude Code

- Trabalhe no seu branch; você é dono do otimizador, da Camada 2 e do bridge.
- Toda sessão: começar lendo `Decisoes_pendentes.md`, terminar atualizando-o + entrada no `LOG.md`.
- Decisões conceituais (forma do Q, mapeamento) na conversa/reunião; implementação mecânica e validação numérica com o Claude Code.
