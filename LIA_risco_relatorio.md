# Lia — Risco/Calibração + Relatório

## Norte geral

Se o Felipe decide *onde* alocar, você decide *com quanta confiança* e *quanto risco tomar*. Sua peça central é o Ω reativo — a confiança que sobe e desce conforme a qualidade do sinal do Polymarket, e que embute o controle de risco dentro do próprio modelo. Você também constrói a camada tática e escreve o relatório, que é o entregável avaliado pela competição.

## O que fazer

### 1. Especificações formais (Semana 1)

**O quê:** um doc com duas definições prontas para implementação.

**Como:**
- **Definição de "surpresa" (PEAD, Decisão pendente 3):** critério operacional — a partir de qual divergência entre probabilidade da véspera e desfecho real um evento conta como surpresa e dispara o trade de drift (ex. desfecho com prob < 30% = surpresa grande). Definir também janela de holding e ativos elegíveis.
- **Forma funcional do Ω reativo (Decisão pendente 4):** como a confiança reage a volume/liquidez, estabilidade da probabilidade, convergência entre fontes e proximidade de evento agendado. Incluir como tratar conflito entre fontes (Decisão pendente 5).
- As decisões conceituais são fechadas na reunião de 07/jul; o doc as formaliza para o Felipe implementar as interfaces.

**Deadline:** 13/jul.

### 2. Ω reativo implementado (Semana 2)

**O quê:** a função de confiança rodando em código.

**Como:**
- Implementar a forma funcional especificada: Ω como função do estado, recalculado a cada período.
- Comportamento esperado: sinal ruim (volume baixo, oscilação alta, fontes divergindo, evento próximo) → confiança cai → carteira recolhe para o prior; sinal bom → confiança sobe → carteira inclina nas views.
- Respeitar a interface combinada com o Felipe na Semana 1.

**Deadline:** 20/jul.

### 3. Camada tática (Semana 2)

**O quê:** os trades curtos que ficam por cima da carteira estrutural, sem mexer nos pesos.

**Como:**
- **Drift pós-evento (PEAD):** gatilho = tamanho da surpresa (sua definição da Semana 1).
- **Event-driven:** gatilho = salto de nível da probabilidade antes da resolução (ex. fusão 40% → 70%).
- **Velocidade de ajuste:** gatilho = derivada da probabilidade durante o movimento.
- Cada sinal independente: se um não funcionar no backtest, sai sem derrubar o resto.

**Deadline:** 20/jul.

### 4. Relatório (Semanas 3–4)

**O quê:** o documento final da competição.

**Como:**
- **Semana 3 (a partir de 25/jul):** metodologia + arquitetura, que já estão estáveis. Destacar o argumento central: as views e o Ω — o elo mais criticado do BL por ser subjetivo — vêm inteiramente de probabilidades negociadas com dinheiro real e métricas objetivas. **Deadline: 27/jul.**
- **Semana 4:** resultados do backtest + conclusão, após o congelamento do modelo (28/jul). **Deadline: 30/jul.**

### 5. Fechamento

Revisão final e entrega com todos. **Deadline: 31/jul.**

## Organização com Claude Code

- Trabalhe no seu branch; você é dona do módulo de Ω e da camada tática.
- Toda sessão: começar lendo `Decisoes_pendentes.md`, terminar atualizando-o + entrada no `LOG.md`.
- Especificações e definições conceituais no doc/reunião; implementação e testes com o Claude Code. O relatório pode usar o `LOG.md` como fonte do histórico de decisões.
