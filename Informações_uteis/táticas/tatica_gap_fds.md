# Tática — Gap de fim de semana (poly 24/7 × bolsa fechada)

**Status:** 🟡 candidata da **camada tática reformulada** (contrato em `tatica_1.3_premio_anuncios.md`: paralela ao BL, granularidade ~12h, gatilho de calendário, sinal lento) — desenho fechado em sessão com Felipe (2026-07-10), **condicionado à reunião** (reabrir a camada mexe na decisão 10). Sinal **exclusivo do Polymarket** — é a única candidata que explora diretamente o fato de o poly operar 24/7.

**Origem:** pesquisa de 2026-07-10 (`Informações_uteis/Pesquisa_embasamento_novas_ideias.md`). Âncoras:
- **Snowberg, Wolfers & Zitzewitz (2007, *QJE*), "Partisan impacts on the economy":** na noite da eleição de 2004, com a bolsa fechada, os movimentos do prediction market moviam os **futuros** de equity em frequência intradiária — evidência direta do mecanismo (prediction market se move fora do pregão → equities reprecificam).
- **Lou, Polk & Skouras (2019, *JFE*), "A tug of war":** retornos overnight e intradiários têm estrutura sistematicamente diferente — "o que acontece com o mercado fechado" é objeto real. Âncora secundária.
- ⚠️ **Ressalva incorporada:** binários do poly exibem **mean-reversion** de curto prazo (estudo QuantPedia sobre contratos do Polymarket) — parte do Δp de fim de semana pode reverter em vez de ser absorvida pela bolsa. Ver decisão Q2.

## A ideia

De sexta (fechamento) a segunda (abertura) a bolsa fica ~65h sem negociar; o poly não para. Se a probabilidade de um evento que as views monitoram andou no fim de semana, a informação existe, tem preço em dinheiro real — e a bolsa ainda não reagiu. A tática entra na abertura de segunda na direção que os β das views mandam e desmonta no fechamento do mesmo dia.

**Por que não é view do BL:** horizonte de 1 dia, condicional ao calendário semanal — afirma *quando* a informação chega, não retorno esperado no horizonte do rebalance. **Por que não colide com a 1.2 (momentum, adiada):** lá o gatilho é a *tendência* da probabilidade ao longo do tempo; aqui é o *nível acumulado com a bolsa fechada*, one-shot na reabertura.

## Como funciona (decidido)

1. **Formato: sleeve overlay cross-sectional por cima do BL intocado.** Tilt nos 9 ETFs: `w_tática[i] = λ × β_i × Δp_fds`, onde os `β_i` são **os já estimados pela view designada** — a tática não estima nada próprio.
2. **Fonte do sinal (Q1-A): só os mercados designados das views ativas** (2.3/2.4/3.1/C/E/G…, conforme o que a reunião aprovar). Custo de dado zero; se mais de uma view está ativa, cada mercado gera seu tilt e os tilts somam (mesma lógica de empilhamento das views no BL). ⚠️ O teste de defasagem das views já garante que só operamos mercados onde a bolsa historicamente segue o poly (k > 0).
3. **Sinal:** `Δp_fds = p(último snapshot ≤ abertura de segunda) − p(fechamento de sexta)`, midpoint bid/ask (decisão 9), em fração. Grid de 12h do poly cobre o fim de semana — **sem lookahead** (snapshot de domingo à noite decide a posição de segunda).
4. **Forma do sinal (Q2-A): contínua, sem threshold.** Δp pequeno → posição pequena naturalmente; nenhum limiar para defender (mesmo argumento da 1.3 contra liga/desliga binário). A mean-reversion fica como **risco aceito e documentado**; upgrade registrado: filtro por magnitude/volume se o backtest mostrar que Δp pequenos só carregam ruído (parâmetros humanos futuros).
5. **Janela (Q3-A): 1 dia útil** — entra na abertura de segunda, desmonta no fechamento de segunda. Leitura direta de "absorção na reabertura". Variante anotada para a reunião: desmontar em k dias da view designada (coerente com a velocidade de absorção estimada, mas acopla a tática ao k de cada view).
6. **Tamanho:** um único parâmetro humano, `λ` (orçamento da tática — escala o tilt inteiro). Feriados prolongados (bolsa fechada ≥ 3 dias) contam como "fim de semana" — mesma mecânica, registrar no backtest.
7. **Cascata de degradação:** nenhuma view ativa / sem snapshot de domingo utilizável → segunda-feira **não opera** (dormente; não é falha). Nunca bloqueia o BL. Desligamento herdado das views: se a view designada desligou (proximidade de resolução), o mercado dela sai do sinal da tática junto.

## Decisões rejeitadas (referência)

- **Conjunto próprio de mercados (Q1-B):** exigiria estimar β só para a tática — duplica maquinaria sem âncora adicional.
- **Filtro por threshold/volume no v1 (Q2-B):** 1–2 parâmetros novos a defender; fica como upgrade se o backtest pedir.
- **Desmonte em k dias no v1 (Q3-B):** acopla a tática ao k de cada view; anotada como variante de reunião.
- **Virar view do BL:** horizonte de 1 dia irreconciliável com o rebalance.
- **Usar último trade do poly:** série stale no fim de semana (volume menor) — midpoint bid/ask obrigatório, como nas views.

## Pendências

- ⚠️ **Reunião:** (a) reabrir a camada tática reformulada (decisão 10; junto com 1.3 e drift pós-FOMC); (b) valor de `λ`; (c) variante de desmonte em k dias; (d) empilhamento com o rebalance estrutural (se o rebalance cai na segunda, o tilt da tática e o novo w do BL se sobrepõem — regra de precedência a definir).
- **Backtest (Paulo):** preço de **abertura** de segunda dos ETFs (yfinance tem; dado novo pequeno); snapshots de fim de semana do poly no grid de 12h; marcação diária (já requisitada pelas outras táticas).
- **Lia:** a mesma nota de interação Ω ↔ camada (o Ω lê estabilidade da probabilidade — um fim de semana volátil derruba a confiança da view E sobe o sinal da tática; documentar, como na 1.3).
- **Validação específica:** medir no histórico se Δp_fds grandes revertem na própria segunda (mean-reversion) — se sim, a variante com filtro (Q2-B) volta à mesa.
