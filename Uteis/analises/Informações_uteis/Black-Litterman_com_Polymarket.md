# Black-Litterman com views do Polymarket

## Em uma frase
Montar a carteira partindo do consenso do mercado e só se afastar dele quando há convicção — trocando os "chutes" de opinião do gestor pelas probabilidades do Polymarket (apostas com dinheiro real).

## Como funciona
O Black-Litterman combina dois ingredientes:

- **Prior — a carteira de mercado.** O ponto de partida neutro: a carteira de equilíbrio, com pesos de mercado. Sem opinião nenhuma, é nela que ficamos.
- **Views (vetor Q) — o que o Polymarket diz.** Cada mercado relevante vira uma opinião sobre o retorno esperado de um ativo, setor ou par. Ex.: probabilidade de corte de juros → setores sensíveis a duration superam os defensivos.
- **Confiança (matriz Ω) — o quanto acreditamos em cada view.** Medida por volume, liquidez e estabilidade do mercado no Polymarket: quanto mais líquido e estável, maior a confiança.

O resultado é uma carteira que se inclina na direção das views, proporcional à confiança de cada uma.

## Por que isso é diferente
A maior crítica prática ao Black-Litterman é que as views e a confiança são subjetivas — o gestor chuta retornos e convicções. Aqui, *todas* as views vêm de probabilidades negociadas com dinheiro real e *toda* a confiança vem de métricas objetivas (volume, liquidez, estabilidade, convergência entre fontes). Transformamos o elo mais frágil e subjetivo do modelo no mais sistemático.

## O botão: overlay ↔ cérebro central
Quanto o Polymarket manda na carteira é um parâmetro, não uma decisão de arquitetura:

- **Confiança alta** → as views dominam → o Polymarket dirige a alocação.
- **Confiança baixa** → a carteira fica perto do mercado → o Polymarket só ajusta na margem (overlay).

Não precisamos escolher de antemão; calibramos o botão.

## Confiança móvel: o Ω reage à qualidade do sinal
A confiança (Ω) não precisa ser um número fixo — pode ser uma função do estado, recalculada a cada momento conforme a qualidade do sinal do Polymarket muda. Ela sobe ou desce reagindo a:

- **Volume / liquidez** do mercado naquele instante (mais volume → mais confiança).
- **Estabilidade da probabilidade:** oscilando muito → confiança cai; estável → confiança sobe.
- **Convergência entre fontes:** poly, polls e casas de aposta concordam → confiança alta; divergem → baixa. *(Fora do v1 — fica como stub; decisão 7.)*
- **Proximidade de evento:** perto de um evento agendado e incerto → confiança cai automaticamente.

O ganho: a confiança reativa **embute o controle de risco e de beta no próprio modelo**. Quando ela cai (evento volátil, fontes divergindo), a carteira recolhe sozinha em direção ao prior — menos risco. Quando sobe, ela inclina mais nas views. O overlay de risco deixa de ser um módulo separado e passa a viver dentro do Ω.

Em resumo: prior fixo + Ω reativo = uma carteira que aperta e solta a exposição ao Polymarket conforme o sinal melhora ou piora em tempo real.

## Exemplo concreto
Dos buckets de FOMC do Polymarket sai uma esperança de −20bp para a decisão; o futuro de Fed Funds (ZQ) precifica −10bp — surpresa esperada de −10bp. A view é "setores long-duration (tech) superam os defensivos", com magnitude vinda dos β estimados por regressão própria (event-study de dias de FOMC), e confiança proporcional ao volume e à estabilidade do mercado.

## Mapa de camadas — onde cada ideia entra

Como as ideias do banco se distribuem na arquitetura. Cada camada responde uma pergunta diferente.

### 1. Camada que monta o portfólio
**O que faz:** define os pesos estruturais da carteira. Cada ideia vira uma *view* no Black-Litterman (opinião direcional + confiança), e o otimizador junta tudo em pesos.

- **View de recessão (3.1)** — divergência entre o mercado de recessão do poly e a probabilidade implícita na curva de juros (probit sobre o spread 10a−3m) → tilt cíclicos vs defensivos + SPY/TLT. Reframe do antigo índice de sentimento (2026-07-10).
- **View do Fed (2.3)** — surpresa de juros (esperança do poly vs futuro de Fed Funds, em bps) → inclina entre setores sensíveis a duration (tech) e defensivos.
- **View de inflação (2.2)** — poly de CPI vs. TIPS → TIPS vs. nominais.
- **View eleitoral (2.4)** — defasagem entre o poly presidencial e o mercado acionário → tilt setorial cross-section pelos β estimados (sem cestas).

Container: **Arquitetura complexa (2.1)** — pega as views, aplica a confiança e cospe os pesos finais.

> Divisão de trabalho: 2.2 / 2.3 / 2.4 / 3.1 dão as apostas concretas · 2.1 vira tudo em carteira.

**Template estrutural de código (sessão 2026-07-11, por instrução do Felipe):** a view 2.2 (`src/view_2_2_inflacao.py`) é o molde de implementação das demais views estruturais. Toda view segue o mesmo desenho: um módulo por view com função pura `build_view(...) → ViewResult | None` (contrato de saída em `src/views_common.py` — entrada livre por view, saída uniforme: `P` alinhado a `assets` com Σ|P| = 2, `Q` em fração decimal, `diagnostics` dict para o Ω da Lia); cascata de degradação terminando em `None` = view desativada (não é falha); pré-processamento de probabilidades só via `src/poly_preprocessing.py` (decisão 9); parâmetros numéricos sempre como argumento (nunca hardcoded — vêm de decisão registrada); teste sintético próprio em `tests/`. A matemática compartilhada entre views vive em `src/views_common.py`, ao lado do contrato: linha P a partir dos βs, maquinaria de defasagem (2.4, reusada por 3.1/C/E/G) e o corpo do template poly-defasado (`lagged_poly_view` — o mesmo nas views 2.4/C/E/G, que só delegam). Implementadas neste molde: **2.2, 2.3, 2.4 e 3.1** (decididas) e **B, C, E, G** (código pronto por instrução do Felipe, 2026-07-11 — **a entrada delas na carteira segue pendente de reunião**; docstrings marcam o status). A integração (empilhar `ViewResult` em P/Q e ligar no otimizador, com Ω da Lia alinhado às views ativas) está em `src/bl_integration.py`. 2.4/3.1/C/E/G só rodam com dado real após a condição de bid/ask histórico (Paulo).

### 2. Camada tática — adiada (fora do escopo; decisão 10)
Removida do escopo do projeto em reunião (registrada 2026-07-09); fica para retomada futura. Explorava, com trades curtos por cima da carteira estrutural, a defasagem entre o movimento do Polymarket e a reprecificação do mercado tradicional, em três momentos: **velocidade de ajuste** (age *durante* o movimento; gatilho = derivada da probabilidade — ideia descrita só aqui), **event-driven (3.2)** (age *antes* da resolução; gatilho = salto de nível) e **PEAD (1.1)** (age *depois* da resolução; gatilho = tamanho da surpresa). O **momentum em crenças (1.2)** foi reclassificado para esta camada em 2026-07-10 (gatilho = tendência da probabilidade; sem âncora de magnitude para o template estrutural) e está adiado junto com ela. Descrições completas de 1.1, 1.2 e 3.2: `Ideias_consolidadas.md`. Numeração das camadas 3 e 4 mantida para não quebrar referências.

### 3. Camada de risco / dimensionamento
**O que faz:** decide *quanto* risco tomar, não onde alocar. Pode viver dentro do Ω reativo (a confiança que sobe e desce conforme a qualidade do sinal).

- **Prêmio de anúncio macro (1.3)** — dimensiona a exposição à vol em dias de anúncio conforme a (in)certeza do poly.

### 4. Camada de calibração (Ω)
**O que faz:** ajusta a *confiança* nas views, não a carteira. Limpa e pondera o sinal antes de ele virar peso.

- **Correção de favorite-longshot bias** — limpa as probabilidades antes de virarem view.
- **Anti-narrativa (3.5)** — filtro de qualidade: detecta mercados "contaminados" e derruba a confiança neles.

### Reserva / especulativa
- **Detector de info privilegiada (3.4)** — gera sinal próprio a partir de movimentos sem catalisador público; mais ousada, fica em reserva.

**Atenção:** a **view eleitoral (2.4)** fechou como *view* estrutural (camada 1); eventos político-regulatórios firm-specific pertenciam à camada tática (3.2), adiada — fora do escopo (decisão 10).

## Norte geral do motor (Felipe)

Felipe é o dono do modelo central: o motor que transforma probabilidades do Polymarket em pesos de carteira. O trabalho é construir esse motor e a ponte que o alimenta — o bridge probabilidade→Q, onde cada view monta P, Q e o próprio β — e coordenar a integração final. Especificação canônica de cada view: `Informações_uteis/views/`. Propriedade completa dos módulos: `CLAUDE.md`.
