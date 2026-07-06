# Cronograma geral — Estratégia Polymarket (até 31/jul)

**Projeto:** Black-Litterman com views do Polymarket · Itaú Quant AI Challenge
**Equipe:** Felipe (arquitetura BL) · Paulo (dados) · Lia (risco/calibração + relatório)

## Regras de organização (Claude Code)

1. **Um branch por membro, um dono por módulo.** Ninguém edita o módulo do outro sem avisar.
2. **`Decisoes_pendentes.md` é a fonte da verdade.** Toda sessão do Claude Code começa lendo esse arquivo e termina atualizando-o.
3. **`LOG.md` por sessão.** Cada sessão gera uma entrada curta: o que foi feito, o que quebrou, o que ficou pendente.

## Semana 1 · 07–13/jul — Fundação e dados

| Quem | Tarefa | Deadline |
|---|---|---|
| Todos | Reunião: fechar as 5 decisões em aberto e registrar em `Decisoes_pendentes.md` | 07/jul |
| Paulo | Pipeline yfinance dos 9 ETFs validado + fonte Polymarket decidida e implementada (Decisão 2) | 13/jul |
| Felipe | Esqueleto do otimizador BL rodando com dados sintéticos | 13/jul |
| Lia | Doc com definição de "surpresa" (PEAD) e forma funcional do Ω reativo | 13/jul |

## Semana 2 · 14–20/jul — Camadas estruturais

| Quem | Tarefa | Deadline |
|---|---|---|
| Paulo | Série histórica de probabilidades alinhada aos ETFs; dataset de backtest unificado | 20/jul |
| Felipe | Camada 2 (cenário→ativo) + bridge probabilidade→Q implementados | 20/jul |
| Lia | Ω reativo implementado + camada tática (drift PEAD, event-driven, velocidade) | 20/jul |

## Semana 3 · 21–27/jul — Integração e backtest

| Quem | Tarefa | Deadline |
|---|---|---|
| Todos | Integração: otimizador + dados + Ω num pipeline único | 23/jul |
| Paulo + Felipe | Backtest completo, validação e iteração de bugs | 25/jul |
| Lia | Início do relatório (metodologia + arquitetura) | 27/jul |

## Semana 4 · 28–31/jul — Relatório e fechamento

| Quem | Tarefa | Deadline |
|---|---|---|
| Todos | Revisar resultados do backtest e congelar o modelo | 28/jul |
| Lia | Finalizar relatório (resultados + conclusão) | 30/jul |
| Felipe + Paulo | Revisar e limpar código/repositório | 30/jul |
| Todos | Revisão final e entrega | 31/jul |
