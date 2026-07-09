# LOG do projeto

---

## 2026-07-08/09 — Paulo — Organização: separação dos mercados Fed (passo de preparação, NÃO é decisão metodológica)

**O que foi feito:**
- Criado `src/data_pipeline/separar_mercados_fed.py`: separa
  `data/polymarket_fed_probabilities.parquet` (que permanece **intocado**)
  em dois arquivos, por regex sobre o título do mercado:
  - `data/polymarket_fed_reunioes.parquet` — **76 mercados** (16.338 linhas):
    só resultado direto de reunião do FOMC (no change / decrease / increase
    "after [Mês] [Ano] meeting?", incl. variação "Will the Fed …").
  - `data/polymarket_fed_outros.parquet` — **255 mercados** (49.268 linhas):
    todo o resto, guardado para uso futuro (Fed Chair/pessoas: 97;
    dissidência: 42 + 10 combos; sequências multi-reunião: 40; derivative/
    odds: 18; contagem anual de cortes: 15; corte até data: 8; anual/
    emergência: 6; sem categoria: 2) — **incluindo 11 CASOS AMBÍGUOS**
    colocados ali temporariamente, sinalizados no log, aguardando decisão
    humana (ex.: "Fed rate cut by December meeting?", "Will the FED change
    rates to another level after Nov meeting?").
- Log de conferência em `data/log_separacao_mercados.txt` (lista completa
  dos 76 de reuniões, os 11 ambíguos destacados e os 255 outros por categoria).
- Verificação: reunioes + outros = original (65.606 linhas, sem perda);
  original preservado byte a byte.

**Pendente:** revisão humana da lista de "reunioes" e destino dos 11 casos
ambíguos. Tarefas 2/3 seguem pausadas conforme instrução.

**Uso de IA:**
- **Modelo:** Claude Code / Fable 5.
- **Contexto consumido:** ~105k tokens (~10% da janela de 1M, sessão acumulada).
- **Prompt inicial (verbatim):**
  > Contexto: branch "Paulo". Leia CLAUDE.md e Decisoes_pendentes.md antes
  > de começar.
  >
  > PAUSE qualquer trabalho em andamento nas Tarefas 2/3. Esta sessão é
  > só de ORGANIZAÇÃO do dataset já baixado — não baixe dados novos, não
  > delete nada.
  >
  > PROBLEMA: o dataset atual (data/polymarket_fed_probabilities.parquet)
  > mistura mercados de resultado direto de reunião do FOMC com vários
  > outros tipos (nomeação de Fed Chair, dissidência de votos, mercados
  > "derivative", sequências multi-reunião, etc). Para o trabalho atual,
  > só precisamos do núcleo de reunião — mas o resto NÃO deve ser
  > descartado, só guardado separadamente pra uso futuro.
  >
  > TAREFA: 1. Separe o dataset em DOIS arquivos, sem apagar nada do
  > original: a. data/polymarket_fed_reunioes.parquet — SÓ os mercados que
  > são o resultado direto de uma reunião do FOMC [4 padrões + variações];
  > b. data/polymarket_fed_outros.parquet — TODO o resto, mantido intacto,
  > só separado, para uso futuro. O arquivo original permanece intocado.
  > 2. Gere um log em texto simples (data/log_separacao_mercados.txt) com
  > contagens, lista completa de "reunioes" e resumo por categoria de
  > "outros". 3. NÃO decida sozinho casos ambíguos — liste sob "CASOS
  > AMBÍGUOS — decidir depois" (ou coloque temporariamente em "outros" e
  > sinalize claramente).
  >
  > Não altere Decisoes_pendentes.md nem LOG.md de forma definitiva ainda
  > — apenas registre esta ação como um passo de organização/preparação
  > na entrada do LOG.md (não como decisão metodológica fechada). Ao
  > final, me mostre o resumo do item 2 para eu revisar.

  _(Miolo da TAREFA condensado entre colchetes para o LOG; verbatim
  completo no histórico da sessão.)_
- **Iterações até aceitar:** 1 auto-correção (recategorização no log: 11
  mercados "Trump announce nominee for Chair of the Federal Reserve" e
  "Will 1 Fed rate cut happen" caíam em "sem categoria"; corrigido —
  categorias afetam só o log, não a partição dos arquivos). Aguardando
  revisão humana da lista.
- **Erros da IA:** nenhum na partição em si; só a falha de categorização
  descritiva acima, corrigida na sessão.
- **Decisões escaladas:** nenhuma nova registrada em `Decisoes_pendentes.md`
  (instrução explícita de não alterá-lo); os 11 casos ambíguos aguardam
  decisão via log de separação.
- **Tags:** —

## 2026-07-08 — Paulo — Tarefa 2: probabilidades do Polymarket (Fed/FOMC)

**O que foi feito:**
- Criado `src/data_pipeline/download_polymarket_fed.py` (3 etapas, tudo
  cache-first em `cache/` — reexecutar não repete chamadas já salvas):
  - Etapa 1 (descoberta): `/tags` da Gamma API → tag **"Fed Rates"
    (id 100196)** identificado entre 42 candidatos; `/events` paginado
    (closed=true) → 127 eventos, 85 filtrados por título com "fed"/"fomc".
  - Etapa 2 (download): CLOB `/prices-history` com `interval=all` +
    `fidelity=720` (12h), 1 chamada por token Yes, cache por token, delay
    0,2s e retry 3× com backoff.
  - Etapa 3 (consolidação): `data/polymarket_fed_probabilities.parquet`,
    tabela longa `[data, mercado, probabilidade, evento_id]`, eventos em
    ordem cronológica de reunião (proxy: endDate), **65.606 linhas**.
- Documentação em `data/README.md`; testes em `tests/test_polymarket_fed.py`
  (5 testes: 4 passam, 1 xfail documentado — ver overlap abaixo).

**Números pedidos:**
- **Data real de início da cobertura:** primeiro evento **2023-12-06**,
  primeiro ponto de preço **2023-12-07** (último: 2026-06-17). Sem lacunas
  > 6 meses entre eventos consecutivos.
- **Total de eventos:** 85 filtrados (Fed/FOMC), 83 com dados de preço;
  385 mercados percorridos, 331 com histórico (54 vazios).
- **Chamadas de API:** execução final 388; sessão inteira ≈ 765 (365 da
  1ª execução com tag errado — ver "Erros da IA" — e ~12 de sondagem de
  parâmetros do `/prices-history`).

**O que quebrou:**
- A Gamma API ignora `limit>100` em `/tags` e `/events`: a 1ª execução parou
  na 1ª página, escolheu o tag errado ("federal government") e achou só
  1 evento. Corrigido paginando pelo tamanho real do batch até página vazia.
- `interval=max` no `/prices-history` volta vazio para mercados resolvidos
  antigos (290 de 295 vazios na 2ª execução). Corrigido com `interval=all` +
  `fidelity=720` — 12h é a granularidade mais fina que a API gratuita devolve
  para mercados resolvidos (testado: 180/60/10 voltam vazios), confirmando a
  limitação documentada.

**Achados nos dados:**
- **Overlap intrínseco:** mercados de reuniões diferentes do FOMC negociam
  simultaneamente — 82 de 82 pares de eventos consecutivos com overlap de
  datas. O teste "sem overlap" pedido na tarefa está como `xfail` documentado;
  a regra de encadeamento foi escalada (Decisão 9).
- Cobertura do Polymarket (dez/2023→) é ~20 anos mais curta que a série dos
  ETFs (dez/2003→) — escalado como Decisão 8 (afeta a Decisão 3), conforme
  instrução da tarefa.
- 54 mercados com histórico vazio mesmo com os parâmetros corretos (2 eventos
  ficaram sem nenhum dado) — provavelmente mercados de baixíssima atividade.
- Observação: `PAULO_dados.md` descreve o Path B como "proxies de mercado
  tradicional (CME FedWatch)", mas a instrução desta sessão define Path B
  como Gamma+CLOB do Polymarket. Segui a instrução explícita; vale alinhar
  a nomenclatura no time.

**Pendente:**
- Tarefa 3 (dataset unificado): bloqueada pelas Decisões 8 e 9 (janela de
  backtest e regra de overlap/encadeamento) + regra de junção de calendários.
- Decisões 8 e 9 aguardando reunião.

**Uso de IA:**
- **Modelo:** Claude Code / Fable 5.
- **Contexto consumido:** ~75k tokens (~7,5% da janela de 1M).
- **Prompt inicial (verbatim):**
  > Contexto: branch "Paulo", projeto Black-Litterman + Polymarket. Leia
  > PAULO_dados.md e CLAUDE.md antes de começar. Trabalhe SOMENTE dentro
  > deste branch. Siga o ritual de sessão do CLAUDE.md (início: ler
  > Decisoes_pendentes.md e LOG.md; fim: atualizar ambos + bloco "Uso de IA").
  >
  > OBJETIVO: mapear e baixar dados históricos de mercados de decisão do
  > Fed (FOMC) via Polymarket, usando a API gratuita já decidida
  > (Decisão 2 fechada — Path B, Gamma API + CLOB API, sem provedores pagos).
  >
  > [ETAPA 1 — Descoberta: /tags → tag_id Fed Rates com cache em
  > cache/tags.json; /events paginado (closed=true) com cache em
  > cache/fed_events.json; filtro local por "fed"/"fomc"; reportar evento
  > mais antigo, total e lacunas > 6 meses.
  > ETAPA 2 — Download: /prices-history por token com cache em
  > cache/prices_history/, delay 0,2s, retry 3× com backoff.
  > ETAPA 3 — Consolidação: parquet longo [data, mercado, probabilidade,
  > evento_id]; README com data real de início; teste de [0,1] e overlap.
  > RESTRIÇÕES: só pasta de dados e cache/ (+ LOG.md e Decisoes_pendentes.md
  > ao final); não decidir sozinho a reconciliação de cobertura — registrar
  > em Decisoes_pendentes.md; não repetir chamadas já cacheadas.]
  >
  > Ao final, atualize LOG.md com: data real de início da cobertura,
  > total de eventos, número de chamadas de API feitas, e qualquer decisão
  > escalada para Decisoes_pendentes.md.

  _(Trecho entre colchetes condensado do prompt original para o LOG; o
  verbatim completo está no histórico da sessão.)_
- **Iterações até aceitar:** 3 execuções do pipeline até o resultado correto
  (2 rodadas de auto-correção); ainda não revisado pelo humano.
- **Erros da IA:** (1) assumiu que a Gamma API honraria `limit=500` — o teto
  real é 100 e a paginação parou cedo, escolhendo o tag errado e gastando
  365 chamadas de API na execução descartada; (2) assumiu que `interval=max`
  funcionaria para mercados resolvidos — retorna vazio; era preciso
  `interval=all` + `fidelity`. Ambos detectados e corrigidos na sessão.
- **Decisões escaladas:** Decisão 2 registrada como fechada (por instrução
  explícita do humano no prompt); **Decisões 8 e 9 abertas** (reconciliação
  de cobertura; overlap/encadeamento dos mercados FOMC).
- **Tags:** `[PROMPT-CHAVE]`

## 2026-07-08 — Paulo — Tarefa 1: pipeline de preços dos ETFs

**O que foi feito:**
- Criado `src/data_pipeline/download_prices.py`: baixa via yfinance o histórico
  diário de preço ajustado (auto_adjust=True, splits/dividendos incorporados)
  dos 9 tickers da Decisão 1 (fechada): XLK, XLU, XLP, XLF, XLE, XLV, TIP, TLT, SPY.
- Parâmetros (tickers, período, caminho de saída) em `config/data_config.json`
  — `start`/`end` nulos = histórico máximo disponível.
- Validação no console: cobertura por ticker, buracos dentro da cobertura de
  cada ticker, alinhamento de datas na janela comum, NaN.
- Saída: `data/etf_prices_daily.parquet` — tabela única, formato longo,
  colunas `[data, ticker, preco_ajustado]`, 51.129 linhas (5.681 datas × 9 tickers).
- Formato documentado em `data/README.md`.
- Testes em `tests/test_etf_prices.py` (6 testes, todos passando): sem NaN,
  todos os tickers presentes, datas 100% alinhadas entre tickers, intervalo
  de datas esperado (início 2003-12-05, fim ≥ 2026-07-01), preços positivos.
- Criado `.venv` local com yfinance 1.5.1, pandas 3.0.3, pyarrow 24.0.0, pytest.

**Achados nos dados:**
- Nenhum buraco em nenhum ticker (nenhuma data em que um ticker deixou de
  negociar enquanto os outros negociaram, dentro da própria cobertura).
- Históricos com inícios diferentes: SPY desde 1993-01-29, setoriais (XLK,
  XLU, XLP, XLF, XLE, XLV) desde 1998-12-22, TLT desde 2002-07-30,
  **TIP desde 2003-12-05 (é o gargalo)**.
- O dataset salvo foi recortado à janela comum **2003-12-05 → 2026-07-08**
  para garantir datas alinhadas e zero NaN (exigência da tarefa). O histórico
  pré-2003 dos demais tickers foi descartado no arquivo final — o download
  completo continua disponível se o time quiser outra regra.

**O que quebrou:**
- Primeira execução: XLK e XLE voltaram vazios (erro transitório do cache do
  yfinance, "database is locked") e o script salvou um parquet vazio.
  Corrigido: retry individual por ticker (até 3×) e abort sem salvar se
  qualquer ticker ficar vazio ou a janela comum for vazia.

**Observações para o time:**
- O período de backtest não está definido em nenhuma decisão. O arquivo hoje
  cobre 2003→2026 (janela comum), mas o Polymarket/proxies só existem em
  período muito mais curto — a janela efetiva do backtest será definida pela
  Decisão 2. Não registrei nada novo em `Decisoes_pendentes.md` (instrução
  explícita da sessão de não alterá-lo).
- `PAULO_dados.md` está na raiz do repo, não em `Informações_uteis/` como
  referenciado no prompt.

**Pendente:**
- Tarefa 2 (fonte de probabilidades do Polymarket — Decisão 2, aberta):
  aguardando mapeamento dos mercados relevantes do Polymarket.
- Tarefa 3 (dataset unificado de backtest): depende da Tarefa 2.
- Em aberto da Decisão 1: incluir ou não proxy de Brasil (EWZ).

**Uso de IA:**
- **Modelo:** Claude Code / Fable 5.
- **Contexto consumido:** ~45k tokens (~22% da janela).
- **Prompt inicial (verbatim):**
  > Contexto: este é o branch "Paulo" de um projeto de otimização de portfólio
  > Black-Litterman. Leia o arquivo Informações_uteis/PAULO_dados.md para
  > entender minha tarefa completa antes de começar, mas nesta sessão execute
  > SOMENTE a Tarefa 1 descrita abaixo.
  >
  > Trabalhe SOMENTE dentro deste branch. Não altere CLAUDE.md nem
  > Decisoes_pendentes.md além de, ao final, registrar uma entrada em LOG.md
  > resumindo o que foi feito.
  >
  > TAREFA 1 — Pipeline de preços dos ETFs:
  >
  > 1. Criar um script Python (usando yfinance) que baixe o histórico diário
  >    dos 9 ativos já decididos (Decisão 1, fechada): XLK, XLU, XLP, XLF,
  >    XLE, XLV, TIP, TLT, SPY.
  > 2. Usar preço ajustado (adjusted close), já incorporando splits e
  >    dividendos.
  > 3. Validar a série:
  >    - Checar se há datas faltando/buracos em cada ticker
  >    - Checar se as datas estão alinhadas entre os 9 tickers
  >    - Reportar no console quaisquer inconsistências encontradas
  > 4. Salvar o resultado em formato padronizado: parquet, tabela única no
  >    formato longo (colunas: [data, ticker, preço_ajustado]).
  > 5. Documentar o formato do arquivo salvo num README curto dentro da
  >    pasta de dados (nome do arquivo, colunas, período coberto, fonte).
  > 6. Escrever um teste simples que confirme: nenhum ticker com NaN, todas
  >    as datas presentes em todos os tickers, intervalo de datas conforme
  >    esperado.
  >
  > NÃO comece a Tarefa 2 (Polymarket) nem a Tarefa 3 (dataset unificado)
  > nesta sessão — elas ficam para depois que os mercados relevantes do
  > Polymarket forem mapeados.
  >
  > Ao final, atualize LOG.md com: o que foi feito, qualquer problema
  > encontrado nos dados (buracos, tickers com histórico mais curto que
  > os outros, etc.), e o que fica pendente (Tarefa 2, aguardando
  > mapeamento dos mercados do Polymarket).

  (Antes deste, houve um prompt de diagnóstico read-only interrompido pelo
  próprio usuário.)
- **Iterações até aceitar:** 1 rodada de auto-correção (bug do arquivo vazio,
  descrito acima); resultado ainda não revisado pelo humano.
- **Erros da IA:** a 1ª versão do script salvou um parquet vazio quando o
  download de XLK/XLE falhou silenciosamente (validação passou em vácuo).
  Detectado e corrigido na própria sessão.
- **Decisões escaladas:** — (nenhuma nova; observação sobre janela de
  backtest registrada acima, sem alterar `Decisoes_pendentes.md`).
- **Tags:** `[PROMPT-CHAVE]`
