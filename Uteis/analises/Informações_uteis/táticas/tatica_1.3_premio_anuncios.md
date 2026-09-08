# Tática 1.3 — Prêmio de risco de anúncios macro (camada de anúncios)

**Status:** 🟡 candidata-fundadora da **camada tática reformulada** — desenho fechado em sessão com Felipe (2026-07-10), **condicionado à reunião** (reabrir a camada mexe na decisão 10 e no módulo da Lia). Por decisão do Felipe, registrada por ora só neste arquivo (sem nova entrada em `Decisoes_pendentes.md`).

**O que é a camada reformulada:** ideias que rodam **em paralelo ao BL** (não viram views) e que **não sofrem com a granularidade de ~12h** do histórico do Polymarket — o que matou a camada tática original foi exigir reação intradiária a saltos de probabilidade; aqui o gatilho é um **calendário conhecido** e o sinal é lento.

**Origem:** ideia 1.3 do banco de ideias (`Ideias_consolidadas.md`). Base: Savor & Wilson (2013) — dias de anúncio macro agendado pagam prêmio de retorno desproporcional em ações; Lucca & Moench (2015) — drift pré-FOMC (~24h antes) como referência, não como janela.

## A ideia

Em dia de anúncio macro (FOMC, CPI), quem carrega risco de ações é pago por isso. O Polymarket mede, na véspera, **quanta incerteza** existe sobre o anúncio (o formato da PMF dos buckets). A camada colhe o prêmio em todo dia de anúncio, dimensionando a posição pela incerteza do poly: mais incerteza → prêmio esperado maior → posição maior.

**Por que não é view do BL:** view é afirmação sobre retorno esperado num horizonte compatível com o rebalance; isto é afirmação sobre **quando estar exposto** — prêmio de 1 dia, ~20 eventos/ano, sem magnitude estimável decente para um Q. É também o único sinal do projeto que lê a **incerteza** (formato da PMF) em vez do **nível** da probabilidade — ortogonal às views por construção.

## Como funciona (decidido)

1. **Formato: sleeve overlay por cima do BL.** Posição própria **long SPY vs caixa**, adicionada à carteira BL apenas nos dias de anúncio (alavancagem temporária de até `orçamento_máx`). A carteira BL fica **intocada** — atribuição limpa por camada. Sem carve-out permanente (não há drag de caixa fora dos ~20 dias/ano); a carteira já é irrestrita (decisão 8), então a alavancagem temporária não quebra premissa.
2. **Sempre ligado, modulado:** a camada opera em **todo** dia de anúncio (Savor-Wilson incondicional); a incerteza do poly **dimensiona** a posição, não decide se liga. Sem threshold binário — sinal contínuo é menos sensível à marcação diária e não cria mais um limiar para defender.
3. **Sinal = entropia normalizada da PMF:** `H(p)/H_máx ∈ [0,1]`, medida no último snapshot ≤ fechamento de D−1 (grid de 12h garante que existe — **sem lookahead**; CPI sai 8h30 ET, FOMC 14h ET). PMF pré-processada pelo módulo da decisão 9 (normalização, favorite-longshot, bucket aberto — os mesmos mercados das views 2.2/2.3).
4. **Tamanho: escala normativa (v1):** `peso_SPY = orçamento_máx × entropia_normalizada`. Um único parâmetro humano (`orçamento_máx`); a escala não promete magnitude de retorno, só ordena a exposição. **Upgrade registrado:** regressão própria (retorno do SPY no dia do anúncio vs entropia na véspera) quando houver histórico suficiente — ~20 obs/ano torna o β ruidoso hoje.
5. **Janela: D−1 close → D close.** Exatamente a frequência da âncora (Savor-Wilson mede o prêmio close-to-close do dia do anúncio). 1 dia de exposição por evento; preço diário dos ETFs (yfinance) — o poly não precisa de intradiário.
6. **Eventos no v1: só FOMC + CPI** — os mercados que as views 2.2/2.3 já contratam (custo de dados zero). Calendário de anúncios = dado novo (datas de FOMC já são pendência da 2.3; datas de release do CPI se somam).
7. **Cascata de degradação:** sem mercado de FOMC/CPI cobrindo o anúncio → aquele evento **não opera** (camada dormente naquele dia; não é falha). Sem PMF utilizável (mercado fino demais) → mesma coisa. A camada nunca bloqueia o BL.

## Decisões rejeitadas (referência)

- **Virar view do BL:** Q de 1 dia irreconciliável com o horizonte do rebalance; magnitude sem regressão viável (~40 obs em 2 anos); ferramenta errada.
- **Escalar a carteira BL inteira (`w_final = λ·w`):** sujaria a atribuição view→peso nos dias de anúncio.
- **Sleeve SPY vs TLT:** short de TLT em dia de anúncio sem âncora própria; long-vs-caixa é a leitura direta de Savor-Wilson.
- **Liga/desliga por threshold de incerteza:** limiar arbitrário (mais um parâmetro) e sensível à marcação diária.
- **Só operar quando o poly está incerto (ideia original do banco):** substituída por "sempre ligado, modulado" — o prêmio médio existe incondicionalmente; o poly vira modulador.
- **Carve-out fixo de capital:** drag de caixa ~95% do tempo.
- **Desvio-padrão da PMF como sinal:** unidade diferente por evento (bps vs pontos de inflação), exige normalização própria e briga com o bucket aberto.
- **`1 − p(favorito)`:** joga fora o formato do resto da distribuição.
- **Janela D−2→D ou janela por evento (drift Lucca-Moench):** drift só documentado para FOMC; dois caminhos no código sem ganho claro no v1.
- **Regressão já no v1:** amostra pequena demais (β ruidoso); fica como upgrade.

## Pendências

- ⚠️ **Reunião:** (a) reabrir a camada tática neste formato (mexe na decisão 10; módulo voltaria à Lia ou seria realocado — dono a definir); (b) valor de `orçamento_máx` (parâmetro humano, regra CLAUDE.md §6); (c) se aprovada, registrar decisão nova em `Decisoes_pendentes.md`.
- **Backtest (Paulo):** o motor precisa **marcar posições diariamente nos dias de anúncio** (~20/ano), mesmo com rebalance estrutural semanal/mensal — requisito de engenharia, não de dado. Calendário de releases do CPI entra como dado novo (datas de FOMC já eram pendência da 2.3).
- **Interação com o Ω (documentar com a Lia):** a mesma incerteza entra com sinais opostos nos dois módulos — aqui incerteza↑ = prêmio↑ (compra); no Ω incerteza↑ = confiança↓ (encolhe a view). Não é contradição (prêmio de risco ≠ qualidade de sinal), mas precisa estar escrito para o Ω não "neutralizar" a camada por construção.
- **Upgrade da calibração:** trocar escala normativa por regressão própria quando a amostra permitir (critério de "suficiente" = decisão humana futura).
