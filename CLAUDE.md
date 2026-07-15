# CLAUDE.md — Regras do projeto (Black-Litterman + Polymarket · Itaú Quant AI Challenge)

Este arquivo define como qualquer instância do Claude Code deve se comportar neste repositório. Estas regras têm precedência sobre qualquer instrução implícita na tarefa.

## 1. Regra de ouro: Claude não decide sozinho — mas tria antes de travar

- **Decisões metodológicas são tomadas por humanos**, nunca pelo Claude: fontes de dados, universo de ativos, forma funcional de fórmulas (Q, Ω), mapeamento cenário→ativo, parâmetros do modelo.
- Ao surgir uma decisão nova, **classificar antes de parar** — a maioria das dúvidas não justifica travar a tarefa:
  1. **Detalhe de implementação** (nome, estrutura de código, escolha técnica sem impacto metodológico): decidir sozinho e seguir. Não perguntar, não registrar.
  2. **Decisão do escopo do dono da sessão** (afeta só módulos do dono; não muda interface, premissa compartilhada nem dado entregue por outro membro): apresentar ao usuário na hora, com recomendação, e resolver na conversa. Só vai para `Decisoes_pendentes.md` se o usuário mandar.
  3. **Decisão que depende de outros membros** (muda interface entre módulos, premissa compartilhada, dado que outro membro entrega, ou metodologia): registrar em `Decisoes_pendentes.md` (contexto, opções, trade-offs — sem fechar sozinho) e seguir com o resto usando placeholder `# TODO(DECISAO-N)`.
- **Não travar por qualquer dúvida:** acumular as questões de categoria 2 e apresentá-las juntas no ponto natural da tarefa; parar imediatamente só quando o próximo passo depende diretamente da resposta.
- O que nunca se assume sozinho (é sempre categoria 2 ou 3): matemática do modelo, valores de parâmetros (τ, magnitudes de view, thresholds), fontes e universo de dados.

## 2. Propriedade de módulos — nunca mexa no que não é seu

| Dono | Módulos |
|---|---|
| **Felipe** | Otimizador BL · Bridge probabilidade→Q (P, Q e β por view) · Integração final · Camada tática reformulada (candidata) |
| **Paulo** | Pipeline de dados (yfinance + Polymarket) · Dataset de backtest |
| **Lia** | Ω reativo · Relatório |

> A camada tática ORIGINAL (PEAD 1.1, event-driven 3.2, velocidade de ajuste — era módulo da Lia) foi adiada em reunião: fora do escopo do projeto (decisão 10 em `Decisoes_pendentes.md`). A camada tática REFORMULADA (1.3 prêmio de anúncios, drift pós-FOMC, gap de fim de semana — candidatas, entrada pendente de reunião) foi **realocada ao Felipe** (2026-07-11).

- Cada sessão do Claude Code trabalha **apenas nos módulos do dono da sessão**, no branch do dono.
- É proibido editar, refatorar, "melhorar" ou formatar código de módulo alheio — mesmo que pareça bugado. Se encontrar um problema em módulo de outro membro, registre em `LOG.md` como observação para o dono.
- Interfaces entre módulos (formato de entrada/saída) só mudam com acordo registrado em `Decisoes_pendentes.md`.

## 3. Ritual de sessão (obrigatório)

**Início de toda sessão:**
1. Ler `Decisoes_pendentes.md` — é a fonte da verdade sobre o que está decidido e o que está em aberto.
2. Ler a última entrada do `LOG.md` para saber o estado atual.

**Fim de toda sessão:**
1. Atualizar `Decisoes_pendentes.md` se algo novo surgiu (nunca marcar decisão como fechada sem instrução explícita do humano).
2. Adicionar entrada no `LOG.md`: data, dono da sessão, o que foi feito, o que quebrou, o que ficou pendente.
3. Incluir na mesma entrada o bloco **"Uso de IA"** (insumo do relatório de uso de IA do desafio):
   - **Modelo:** modelo/ferramenta usados na sessão (ex.: Claude Code / Fable 5).
   - **Contexto consumido:** % ou tokens de contexto usados na sessão.
   - **Prompt inicial (verbatim):** o primeiro prompt do humano na sessão, colado sem editar.
   - **Iterações até aceitar:** nº de rodadas de correção até o resultado ser aceito.
   - **Erros da IA:** alucinações, código quebrado, suposições indevidas (ou "nenhum").
   - **Decisões escaladas:** nº das decisões registradas em `Decisoes_pendentes.md` nesta sessão (ou "—").
   - **Tags:** `[PROMPT-CHAVE]` se o prompt da sessão for candidato ao teste de reprodutibilidade.

## 4. Escopo da tarefa

- Fazer **exatamente o que foi pedido** — nada além. Sem refatorações não solicitadas, sem features extras, sem "aproveitar para melhorar".
- Se a instrução for ambígua em ponto metodológico, perguntar antes de implementar; ambiguidade trivial se resolve pela triagem da regra 1 (categoria 1: decide e segue).
- Não criar arquivos novos fora do módulo do dono sem pedido explícito.
- **Sempre** apresentar repostas diretas e consisas. Evitar escrever muito texto.

## 5. Convenções de código

- **Linguagem:** Python.
- **Estilo:** PEP 8; nomes de variáveis e funções em inglês; comentários e docstrings em português.
- **Notação matemática:** seguir a notação do BL nos nomes (`P`, `Q`, `omega`, `tau`, `pi_prior`) para o código espelhar o paper.
- **Dados:** nenhum dado hardcoded em módulos de lógica; todo acesso a dados passa pelo pipeline do Paulo. Parâmetros de configuração em arquivo de config, não espalhados no código.
- **Funções puras onde possível:** o otimizador e o bridge recebem entradas e devolvem saídas, sem estado global.
- **Validação:** toda função matemática nova deve ter um teste mínimo (caso sintético com resultado conhecido) antes de ser considerada pronta.
- **Commits:** mensagens curtas em português, uma mudança lógica por commit, sempre no branch do dono.

## 6. O que o Claude NUNCA faz neste projeto

- Fechar uma decisão de `Decisoes_pendentes.md` por conta própria.
- Editar módulo de outro membro.
- Trocar fonte de dados, universo de ativos ou fórmula sem instrução explícita.
- Fazer merge entre branches.
- Deletar ou reescrever `Decisoes_pendentes.md`, `LOG.md` ou os arquivos de arquitetura.
- Inventar valores numéricos "razoáveis" para parâmetros do modelo (τ, magnitudes de view, thresholds) — todos vêm de decisão registrada.
