# LOG de sessões

## 2026-07-11 (sessão 3) — Felipe

**Feito:**
- Abertura: confirmado que views + integração já estavam prontas (sessão 2); bateria completa re-executada — 48 testes OK.
- **Dono do módulo da camada tática reformulada: Felipe** (decisão do Felipe em sessão — a camada não volta à Lia). Registrado na decisão 10 (`Decisoes_pendentes.md`) e na tabela de propriedade do `CLAUDE.md`.
- **Interface da camada tática fechada em sessão (Felipe, 3 escolhas):** (i) contrato de CHAMADA DIÁRIA `build_overlay(insumos do dia) → OverlayResult(dw, diagnostics) | None` — `dw` (n,) de pesos EXTRAS alinhado a `assets`, mesma unidade de w; `None` = dormente (não é falha); janelas são lógica interna da tática; (ii) layout espelho das views — um módulo por tática + `src/taticas_common.py`; (iii) soma `w_final = w_bl + Σ dw` em `taticas_common.apply_overlays` (`bl_integration.py` intocado — BL fica limpa, camada por cima).
- **3 táticas candidatas implementadas** (código pronto; **entrada na carteira e orçamentos seguem pendentes de reunião** — mesmo precedente das views B/C/E/G, docstrings marcam o status):
  - **1.3 prêmio de anúncios** (`src/tatica_premio_anuncios.py`): `dw[SPY] = orcamento_max × H(p)/H_max` no dia do anúncio (FOMC+CPI), entropia da PMF de D−1 (sem lookahead) via pré-processamento da decisão 9 (stub FL falha alto — 11a bloqueia; 11b NÃO bloqueia: entropia não usa valores de bucket). Sempre ligado, modulado.
  - **Drift pós-FOMC** (`src/tatica_drift_pos_fomc.py`): dois livros, `direção = −sign(surpresa_bps)`; SPY dias 1..janela_acoes, TLT dias 1..janela_rf truncado no dia anterior ao FOMC seguinte; surpresa zero/dia 0/sem evento → dormente. Janelas da literatura (15/50) entram como ARGUMENTO (confirmação de reunião pendente).
  - **Gap de fim de semana** (`src/tatica_gap_fds.py`): `dw = λ × Σ β_view × Δp_fds` — β reusados das views designadas ativas (tática não estima nada); sinais somam; lista vazia → dormente. Δp sobre a mesma série pré-processada da view (quem monta é o backtest).
- Testes: `tests/test_taticas.py` — **13 testes OK** (contrato/soma, entropia com caso conhecido, direção dovish/hawkish, janelas e truncagem, caso conhecido do gap, dormências, falha alta do stub 11a). Total do projeto: 61.
- **Mapa "o que falta" apresentado** (fechamento da sessão): todo o código escrevível sem dado real existe; falta só o **backtest** (dá para esqueletar com dado sintético); decisões abertas 6/11/12 + pauta de reunião (entrada B/C/E/G, entrada+orçamentos da tática, horizonte 3.1/B, k≈0, τ/δ) + dependências Paulo/Lia. Gotcha sem dono destacado: **reconciliação do Q acumulado (k dias) com Σ/π diários** — trava o backtest misturar views defasadas com as diárias.

**Quebrou / aprendido:**
- Nada quebrou (testes passaram de primeira).

**Pendente:**
- **Reunião (camada tática):** entrada da camada na carteira; orçamentos (`orcamento_max`, `orcamento_acoes`/`orcamento_rf` — por livro ou comum —, `λ`); janelas finais (15/50); fonte da expectativa do drift (ZQ vs E_poly); micro-surpresas (posição cheia por sinal); desmonte do gap em k dias; precedência tilt × rebalance no mesmo dia.
- **Paulo (backtest):** marcação diária contínua das posições táticas (o drift cobre boa parte do ano); calendário de releases do CPI (dado novo); preço de ABERTURA de segunda dos ETFs; snapshots de fim de semana do poly.
- **Lia:** nota de interação Ω ↔ camada tática (incerteza entra com sinais opostos nos dois módulos; três módulos leem o calendário FOMC).
- Anteriores seguem: decisões 6, 11, 12; entrada das views B/C/E/G; condições de dado do Paulo; τ/δ reais.

**Uso de IA:**
- **Modelo:** Claude Code / Fable 5.
- **Contexto consumido:** ~60k tokens (~6% de janela de 1M).
- **Prompt inicial (verbatim):** "montei as views do Black litterman, precisa montar o integração agora né?"
- **Iterações até aceitar:** 1 (levantamento das pendências pré-código aceito; interface fechada pelo Felipe em 3 escolhas estruturadas; código das 3 táticas aceito sem rodada de correção).
- **Erros da IA:** nenhum.
- **Decisões escaladas:** dono do módulo tático e interface da camada fechados pelo Felipe em sessão (registrados na decisão 10, não numerados); nenhuma decisão numerada fechada.
- **Tags:** —

## 2026-07-11 (sessão 2) — Felipe

**Feito:**
- **Interface das views fechada em sessão (Felipe, 3 escolhas):** entrada livre por view, saída uniforme `build_view(...) → ViewResult | None` — (i) view desativada retorna `None` (a integração não empilha); (ii) `ViewResult(P, Q, diagnostics)` com `diagnostics` dict livre para o Ω da Lia (formato não travado — decisão 6 aberta; **a confirmar com a Lia**, mesmo modelo do "a confirmar" do `bl_optimizer.py`); (iii) um módulo por view + `src/views_common.py` com o contrato. Convenções: `P` alinhado a `assets` com Σ|P| = 2; `Q` em fração decimal.
- **View 2.2 Inflação implementada** (`src/view_2_2_inflacao.py`): cascata completa da espec (PMF → fallback binário via normal deslocada com `scipy.stats.norm.ppf` → `None`); `Q = duration × (E_poly − breakeven_10a)`, `P = +1 TIP/−1 TLT`; duration e breakeven como argumentos (nada hardcoded); sem `fl_correction` decidida (decisão 11a) a view falha alto, e `bucket_values` com bucket aberto não resolvido (NaN, 11b) é rejeitado. 7 testes sintéticos (`tests/test_view_2_2_inflacao.py`).
- **Regra nova (por instrução do Felipe): a 2.2 é o template estrutural das demais views** — registrado no mapa de camadas (`Informações_uteis/Black-Litterman_com_Polymarket.md`, seção da camada 1).
- **View 2.3 Fed implementada** (`src/view_2_3_fed.py`) no mesmo molde: `estimate_betas` (OLS event-study com intercepto, retorno vs surpresa Kuttner — janela/frequência são decisão humana, entram como dado), `P_from_betas` determinístico (`P[i] = 2·(β_i−β_SPY)/Σ|β_j−β_SPY|`, P[SPY]=0, Σ|P|=2, rejeita βs sem dispersão), `Q = surpresa · ΣP·β`; cascata PMF → binário (`E_poly = p × Δtaxa do evento`, Δ como argumento sem default de sinal) → `None`; `E_FF` entra pronto em bps (extração do ZQ fica a montante). 7 testes (`tests/test_view_2_3_fed.py`), incluindo o **sanity check de sinal obrigatório do item 6 da espec** com os números do exemplo (surpresa −10bp → XLK no lado long: P[XLK]<0 e Q<0).
- **Consolidação na decisão 9:** a média de PMF com pré-processamento (normaliza → favorite-longshot → Σp·x) era idêntica nas 2.2/2.3 → virou `poly_preprocessing.pmf_mean` (com teste); a 2.2 foi ajustada para usá-la.
- **Views 2.4 Eleitoral e 3.1 Recessão implementadas** (`src/view_2_4_eleitoral.py`, `src/view_3_1_recessao.py`) no mesmo molde, por instrução do Felipe ("mesma hierarquia e estrutura"):
  - Matemática compartilhada movida para `views_common.py`: `P_from_betas` (era da 2.3; mesma construção nas 2.3/2.4/3.1) + maquinaria de defasagem da 2.4 (`lag_regression` — regressão de lags distribuídos, devolve o perfil completo; `full_absorption_beta` — soma dos coeficientes 0…k), reusada pela 3.1.
  - `poly_preprocessing.binary_prob_series` (decisão 9): midpoint de cada lado → normaliza o par → favorite-longshot; construída UMA vez a montante e usada tanto na regressão do β quanto no `build_view` (é o que faz o β absorver a parte linear da correção FL — espec 2.4 item 2b).
  - **2.4:** `Q = (ΣP·β) × (p_t − p_{t−k})`, benchmark = poly defasado; **k ≈ 0 falha alto** (`NotImplementedError` — fallback contemporâneo vs sair do v1 é pendência de reunião); desligamento antes do 1º tick de resolução e "dias sem trade" documentados como responsabilidade do backtest; `horizonte_q_dias = k` nos diagnostics (pendência transversal Q acumulado × Σ/π diários).
  - **3.1:** `Q = (ΣP·β) × (p_poly − p_curva)`; `p_curve_probit` = Φ(α + β·spread) com coeficientes publicados **como argumento** (referência exata do NY Fed = pendência, não inventada em código); sem curva com view ativa → falha alto; sanity check de sinal obrigatório (espec item 6) virou teste com os números do exemplo (divergência +0.15 → long defensivos/TLT, short XLK, Q > 0).
  - Teste com dado real segue bloqueado pelas condições do Paulo (bid/ask histórico; mercados de CPI/FOMC/recessão/presidencial no CLOB).
- **Views candidatas B/C/E/G implementadas por instrução do Felipe** ("monte as views BCEG… quero ter tudo feito") — **registro importante: o código existe, mas a ENTRADA delas na carteira segue pendente de reunião** (docstrings de todos os módulos marcam o status; implementar não fecha a decisão do rodapé de `Decisoes_pendentes.md`):
  - C/E/G são matematicamente idênticas à 2.4 (só muda o mercado designado) → o corpo virou `views_common.lagged_poly_view` e a 2.4 passou a delegar; `view_C_geopolitica_energia.py`, `view_E_tarifas.py` e `view_G_fiscal.py` são módulos finos (docstring com específicos da espec + delegação). Sanity checks de sinal obrigatórios (item 7 de cada espec) viraram testes com os números dos exemplos.
  - **B** (`view_B_trajetoria_fed.py`) espelha a 2.3: `surpresa_caminho = E_poly[taxa_fim_de_ano] − E_ZQdez` (nível em bps), β/P **reusados da 2.3** (premissa da espec, confirmação de reunião pendente), cascata PMF → binário (`E_poly = taxa_atual + p·(−25bp)`) → None; helper `rates_from_cut_buckets` (25bp/corte, convenção da espec); sanity check item 6 como teste.
- **Integração implementada** (`src/bl_integration.py`): `stack_views` (filtra None, empilha P (k,n)/Q (k,), preserva diagnostics na ordem — é o alinhamento do Ω da Lia) e `bl_weights_from_views` (prior → posterior → pesos com Σ amostral irrestrita, decisão 8; **sem view ativa devolve w_mkt exato**; view ativa sem Ω falha alto — nunca inventar confiança). Quais views entram na lista é decisão do chamador/backtest — é aí que a pendência B/C/E/G se materializa.
- Bateria completa: 6 + 7 + 7 + 5 + 5 + 5 + 4 + 5 + 4 = **48 testes OK**.

**Quebrou / aprendido:**
- Nada quebrou (testes passaram de primeira nas duas views). Convenção de unidades explicitada para evitar erro silencioso %-vs-decimal: tudo que é retorno/inflação em fração decimal; na 2.3, taxas em bps → β em fração/bp.

**Pendente:**
- Decisão 11 (favorite-longshot + bucket aberto) segue bloqueio para qualquer view rodar com dado real (os stubs falham alto em todas).
- **Decisão 12 (nova, 🟡):** o CRITÉRIO de escolha do k a partir do perfil de lags não está especificado nas especs 2.4/3.1 ("varrer k" não diz como escolher). Encaminhamento do Felipe em sessão: **opção (a) — decidir com o perfil real na mesa** quando o dado do Paulo chegar; até lá `lag_regression` devolve o perfil completo e k entra como argumento humano. Registrada com opções/trade-offs em `Decisoes_pendentes.md`.
- **Lia:** validar o campo `diagnostics` do `ViewResult` como insumo do Ω.
- **Paulo:** condições já registradas (cobertura CPI/FOMC/recessão/presidencial no poly, bid/ask histórico no CLOB, T10YIE + DGS10/DTB3 do FRED, ZQ no yfinance). Detalhe novo a acordar quando o dado chegar: a conversão preço do ZQ → `E_FF` em bps (de qual taxa corrente subtrair a implícita 100−preço) fica a montante da view (já coberto pela pendência "fonte a acordar" da espec da 2.3).
- Pendências de desenho já registradas nas especs seguem: horizonte da 3.1/B (reunião), k≈0 (2.4/C/E/G), reconciliação do horizonte do Q (k dias) com Σ/π — **agora bloqueia o backtest misturar views poly-defasadas com as diárias** (aviso no docstring da integração) —, coeficientes exatos do probit, ΣP empírico (decisão conjunta), reuso do β da 2.3 na B, rolagem entre mercados anuais/deadline (3.1/B/C).
- **Reunião: entrada das candidatas B/C/E/G** — código pronto, decisão em aberto (rodapé de `Decisoes_pendentes.md` inalterado).
- τ e δ reais: seguem sem decisão registrada (testes usam sintéticos marcados).
- Próximo código: backtest (loop de rebalanceamento sobre o dataset do Paulo) — depende do dado e das decisões 11/12.

**Uso de IA:**
- **Modelo:** Claude Code / Fable 5.
- **Contexto consumido:** ~190k tokens (~19% de janela de 1M).
- **Prompt inicial (verbatim):** "quero começar a montar o código das views. fechamos a decisão 9 e agora vamos montando as views, por qual começamos"
- **Iterações até aceitar:** 1 (todas as entregas — interface, 8 views, maquinaria compartilhada e integração — aceitas sem rodada de correção; interface fechada pelo Felipe em 3 escolhas estruturadas; critério do k encaminhado em 1 escolha).
- **Erros da IA:** 1, auto-corrigido no mesmo turno — um Edit em `views_common.py` inseriu texto de docstring fora das aspas (seria SyntaxError); detectado e corrigido antes de rodar qualquer teste.
- **Decisões escaladas:** decisão 12 criada (🟡, critério do k — encaminhamento: fecha com o dado real); interface das views e regra do template fechadas pelo Felipe em sessão (não numeradas); implementação das candidatas B/C/E/G autorizada pelo Felipe SEM fechar a entrada delas na carteira (segue de reunião).
- **Tags:** `[PROMPT-CHAVE]` (candidato: a camada de views inteira — 8 views + maquinaria + integração, 48 testes — nasceu desta sequência curta de prompts; bom caso para o teste de reprodutibilidade).

## 2026-07-11 — Felipe

**Feito:**
- Pergunta de abertura ("dá para começar o código das views direto?") respondida com levantamento de dependências: o único código-fundação faltante era o pré-processamento das probabilidades do poly — exatamente a decisão 9, então ela foi resolvida antes de codar.
- **Decisão 9 fechada (por instrução do Felipe): Opção A** — módulo compartilhado único `src/poly_preprocessing.py` (módulo do Felipe), caixa de ferramentas de funções puras, sem `preprocess()` monolítico. O midpoint fica no módulo (não no pipeline do Paulo); implicação de interface registrada: o dataset do Paulo entrega bid/ask cru — Felipe vai alinhar com Paulo o uso da API com bid/ask histórico (mesma condição de fechamento das views 2.4/3.1). Alternativas B (por view) e C (midpoint no Paulo) documentadas como descartadas.
- **Nova decisão 11 registrada** (🔴): (a) forma da correção de favorite-longshot e (b) valor do bucket aberto das PMFs — as duas peças do módulo sem forma/valor decididos, com opções mapeadas para reunião. ⚠️ Nota de numeração: o nº 11 já existiu (entrada das candidatas B/C) e foi removido por completo em 2026-07-10; o número foi reutilizado para tema totalmente diferente — sem colisão no arquivo atual, mas atas antigas que citem "decisão 11" referem-se ao tema antigo.
- **Código novo:** `src/poly_preprocessing.py` — `midpoint_price` ((bid+ask)/2, rejeita bid>ask), `normalize_probs` (divide pela soma; binários e matriz datas×buckets), `favorite_longshot` e `open_bucket_value` como stubs que levantam `NotImplementedError` com `TODO(DECISAO-11)` (falham alto de propósito: identidade silenciosa esconderia a ausência da correção no backtest). Testes sintéticos em `tests/test_poly_preprocessing.py` — 4/4 OK.
- Achado no caminho (leitura de `PAULO_dados.md` a pedido): o mandato do Paulo não inclui limpeza de Polymarket e recomenda proxies (FedWatch) / PolymarketData.co — se a fonte final não tiver bid/ask, o midpoint deixa de existir para qualquer opção e as views 2.4/3.1 perdem a condição de fechamento. Felipe assumiu alinhar a fonte com o Paulo.

**Quebrou / aprendido:**
- Nada quebrou (testes passaram de primeira). Aprendizado: a checagem "se comporta igual nas views?" (que derrubou a tabela de sensibilidades) passou desta vez — normalização é idêntica em todas e o favorite-longshot é a mesma função elemento a elemento (muda calibração, não código).

**Pendente:**
- **Decisão 11** (favorite-longshot + bucket aberto) — reunião; até lá as views que dependem delas usam os stubs.
- **Felipe → Paulo:** alinhar fonte de dados do poly com bid/ask histórico (condição da decisão 9 e das views 2.4/3.1).
- Próxima sessão de código: **view 2.2 (inflação)** — a mais mecânica, já destravada pelo módulo novo.
- Anteriores seguem: reunião (candidatas B/C/E/G, tática reformulada, horizonte 3.1, k≈0, decisão 6), condições do Paulo.

**Uso de IA:**
- **Modelo:** Claude Code / Fable 5.
- **Contexto consumido:** ~55k tokens (~5% de janela de 1M).
- **Prompt inicial (verbatim):** "quero começar a montar o código das views. Podemos começar direto com eles ou teria outro código que teriamos que montar antes?"
- **Iterações até aceitar:** 1 (explicações da decisão 9, leitura do PAULO_dados.md e código aceitos sem rodada de correção).
- **Erros da IA:** nenhum.
- **Decisões escaladas:** decisão 9 fechada por instrução humana explícita; decisão 11 criada (aberta).
- **Tags:** —

## 2026-07-10 (sessão 3) — Felipe

**Feito:**
- **Decisão 11 removida por completo** de `Decisoes_pendentes.md` por instrução do Felipe; referências nos docs das views B e C ajustadas para texto neutro ("entrada na carteira em aberto"); rodapé atualizado. As candidatas passam a viver só nos próprios arquivos (mesmo modelo da 1.3).
- **Geração de 6 ideias novas** (views E tarifas / F petróleo / G fiscal + táticas T1 momentum monetário / T2 gap de fim de semana / T3 drift em renda fixa) e **pesquisa web de embasamento teórico** → `Informações_uteis/Pesquisa_embasamento_novas_ideias.md` (âncoras com citação e link, gotchas de desenho, 2 candidatas extras descobertas — view H chair do Fed, tática T4 ciclo FOMC — e 4 achados transversais: favorite-longshot/"Yes bias" p/ decisão 9; minoria informada ~3% p/ o Ω; mean-reversion dos binários como ressalva ao template poly-defasado; SWZ como guarda-chuva metodológico do bridge p/ o relatório).
- **Avaliação uma a uma (to-do), decisões do Felipe em cada:**
  - **F descartada** — dupla exposição com a C (mesmo canal XLE); agravante documentado: mercados de WTI do poly resolvem one-touch (precificam o máximo, não o preço terminal).
  - **E fechada como candidata** → `views/view_E_tarifas.md` (família EUA×China primário + recíprocas robustness; β aceito com fragilidade documentada; TLT no cross-section via flight-to-safety do AGKW; template poly-defasado da 2.4).
  - **T1+T3 fundidas** numa tática → `táticas/tatica_drift_pos_fomc.md` (dois livros: SPY ~15d e TLT ~50d truncado no FOMC seguinte; direção simétrica; tamanho binário por sinal com upgrade proporcional; sub-decisão marcada no arquivo: expectativa da véspera = ZQ à la Kuttner, variante E_poly registrada p/ reunião).
  - **G fechada como candidata-RESERVA** → `views/view_G_fiscal.md` (reorientada pela literatura: tributária primário/OBBB + teto da dívida robustness; **shutdown descartado como evento** — S&P flat/positivo em 10 de 13; paradoxo do TLT no teto registrado sem sinal a priori).
  - **T2 fechada como candidata** → `táticas/tatica_gap_fds.md` (sinal = Δp de fim de semana dos mercados das views ativas × β já estimados; tilt contínuo sem threshold; desmonte em 1 dia útil; mean-reversion como risco documentado).
  - **H descartada** — tripla exposição ao tema Fed (2.3+B+H) + evento único na janela.
  - **T4 descartada** — zero conexão com o poly (fora do tema) + evidência pós-amostra enfraquecendo.
- Criado `claude_ignore/guia_ideias.md` (guia pessoal do Felipe, uma linha por ideia com estado — fora da leitura/manutenção do Claude).

**Quebrou / aprendido:**
- Nada de código. Aprendizados: (i) shutdown puro não mexe em equities — a candidata fiscal só sobreviveu reorientada para tributária+teto; (ii) mercados de commodities do poly podem resolver por one-touch — a receita "média da PMF" da 2.2 não transfere sem checar o critério de resolução (item novo para validar em qualquer mercado de buckets); (iii) exposição repetida ao mesmo tema virou o filtro de corte na prática — derrubou F (×C) e H (×2.3×B); (iv) a camada tática reformulada comporta ideias sem sinal do poly no dia (drift usa ZQ), mas não ideias sem conexão nenhuma com o projeto (T4).
- **Observação (não resolvida):** `Informações_uteis/Ideias_consolidadas.md` consta como **deletado** no working tree, mas o mapa de camadas ainda aponta para ele (descrições de 1.1/1.2/3.2 ficariam sem lar) — confirmar se a deleção foi intencional.

**Pendente:**
- **Reunião:** entrada das candidatas B/C/E/G (sem número de decisão — decisão 11 removida); reabrir a camada tática reformulada (decisão 10) agora com 3 táticas e seus orçamentos (`orçamento_máx` da 1.3, `orçamento_máx_drift`, `λ` do gap); sub-questões novas: fonte da expectativa do drift (ZQ vs E_poly), micro-surpresas, janelas 15/50d, desmonte do gap (1d vs k), precedência gap × rebalance; antigas: horizonte 3.1, k≈0, decisões 6 e 9.
- **Paulo:** mercados no CLOB — tarifas EUA×China + recíprocas (condição da E), aprovação fiscal OBBB + teto/X-date (condição da G); preço de **abertura** de segunda dos ETFs (gap); ⚠️ marcação diária **contínua** no backtest (livro TLT do drift ≈ 42 dias úteis por reunião — mais pesado que os ~20 dias/ano da 1.3); condições anteriores seguem.
- **Lia:** nota Ω ↔ camada tática agora cobre 4 módulos (2.3 antes do FOMC, 1.3 no dia, drift depois, gap nas segundas).

**Uso de IA:**
- **Modelo:** Claude Code / Fable 5 (effort max a partir do pedido de pesquisa).
- **Contexto consumido:** ~130k tokens (~13% de janela de 1M).
- **Prompt inicial (verbatim):** "veja onde estamos do projeto agora, o que falta para fazer"
- **Iterações até aceitar:** 1 (todos os arquivos aceitos de primeira — "pode seguir sua leitura" em E/G/drift/gap; a primeira to-do foi desfeita e refeita por mudança de escopo do humano — pesquisa antes de avaliar —, não por erro).
- **Erros da IA:** 1 de imprecisão, auto-apontado: na abertura da bateria T1+T3 descreveu a surpresa do drift como "a que a 2.3 já calcula" (a 2.3 calcula divergência pré-reunião; o drift usa surpresa realizada) — corrigido no próprio arquivo com a sub-decisão marcada e a variante E_poly escalada para reunião. Publicações não verificadas foram citadas como working paper (sem status de journal inventado).
- **Decisões escaladas:** nenhuma decisão numerada criada/fechada. Decisão 11 removida por instrução explícita. Desenhos de E/G/drift/gap fechados por decisão do humano em sessão (registrados nos arquivos das ideias); F/H/T4 descartadas por decisão do humano.
- **Tags:** [PROMPT-CHAVE] candidato — terceira sessão consecutiva com a mesma abertura, desdobramento reprodutível (status → ideias → pesquisa → avaliação um a um → arquivos).

## 2026-07-10 (sessão 2) — Felipe

**Feito:**
- Sessão de expansão da estratégia (sem código): to-do de 4 candidatas discutidas uma a uma — 1.3, 3.3, B e C (motivação: carteira só com views macro e 2.4 em risco no backtest).
  - **1.3 Prêmio de anúncios (Savor-Wilson):** decidido (Felipe) que **não é view do BL** (afirma "quando estar exposto", não retorno esperado; prêmio de 1 dia, ~20 eventos/ano) → vira **candidata-fundadora da camada tática reformulada** ("ideias paralelas ao BL compatíveis com granularidade ~12h"; gatilho = calendário, sinal lento). Desenho fechado em 2 baterias de perguntas: sleeve overlay long SPY vs caixa por cima do BL (alavanca temporária, BL intocado), sempre ligado em dia de anúncio FOMC+CPI, tamanho = orçamento_máx × entropia normalizada da PMF (snapshot ≤ D−1 close, sem lookahead; módulo da decisão 9), janela D−1→D close, calibração normativa no v1 com regressão como upgrade. Criado `Informações_uteis/táticas/tatica_1.3_premio_anuncios.md`; por escolha do Felipe, **registrada só no arquivo por ora** (sem nova decisão em `Decisoes_pendentes.md` — reabrir a camada mexe na decisão 10 e vai à reunião).
  - **3.3 Proxy de vol: descartada** (Felipe) — forma original exige opções/VIX (fora do universo); adaptada, usa o mesmo sinal da 1.3 com trade oposto (contradição) e o espírito defensivo já é papel do Ω. Menções removidas de `Black-Litterman_com_Polymarket.md` (bullet da camada de risco) e `Decisoes_pendentes.md` (linha da decisão 10); `Ideias_consolidadas.md` preservado (retrato histórico) e LOG antigo intacto (histórico não se reescreve).
  - **B Trajetória do Fed:** doc de candidata criado espelhando a 2.3 → `Informações_uteis/views/view_B_trajetoria_fed.md` (surpresa = E_poly[taxa fim de ano] − ZQ dez; β/P reusados da 2.3 com premissa explícita; pendências de reunião: dupla exposição com a 2.3, confirmação do reuso do β, horizonte/rolagem anual junto com a 3.1). Status 🟡 candidata — não fecha as decisões 3/4.
  - **C Geopolítica→energia: desenho fechado por delegação explícita do Felipe ao Claude** ("vou te dar controle sobre essas decisões") → `Informações_uteis/views/view_C_geopolitica_energia.md`. Decisões delegadas: âncoras Kilian & Park (2009) + Caldara & Iacoviello (2022) como sanity check; evento primário = ação militar EUA/Israel×Irã 2025 (~$29,9M + família; volumes de levantamento web, Paulo valida), robustness = cessar-fogo Rússia×Ucrânia, Israel×Hamas fora; **P cross-sectional** substituindo o esboço "XLE vs SPY" da decisão 11. Resto herda a maquinaria da 2.4. Entrada na carteira segue na decisão 11 (reunião).
- Decisão 11 atualizada com ponteiros para os docs de B e C (decisão em si segue aberta); rodapé de `Decisoes_pendentes.md` atualizado.

**Quebrou / aprendido:**
- Nada de código. Aprendizados: (i) o critério que separa view de tática não é o tema, é o objeto da afirmação — retorno esperado num horizonte de rebalance (view) vs quando/quanto estar exposto (camada); (ii) a granularidade de 12h não mata ideias de calendário (anúncios agendados) — matou a tática antiga porque lá o gatilho era salto intradiário; (iii) a 3.3 e a 1.3 eram o mesmo sinal com conclusões opostas — só uma podia existir.

**Pendente:**
- **Reunião:** decisão 11 (B e C, docs prontos); reabrir a camada tática no formato reformulado (1.3: orçamento_máx, dono do módulo — era da Lia); pendências compartilhadas: horizonte/rolagem anual (3.1 + B + C juntas), k≈0 (2.4 + C), decisões 6 e 9.
- **Paulo:** mercados Irã 2025 e Rússia×Ucrânia no CLOB (cobertura, volume, bid/ask — condição da C); mercados de trajetória do Fed + ZQ de dezembro no yfinance (condição da B); requisito novo do backtest: **marcar posições diariamente nos dias de anúncio** (~20/ano) para a camada da 1.3; calendário de releases do CPI como dado novo.
- **Lia:** nota de interação Ω ↔ camada da 1.3 (a mesma incerteza entra com sinais opostos nos dois módulos — documentar para o Ω não neutralizar a camada por construção).
- Avisos a Paulo/Lia das sessões anteriores seguem pendentes.

**Uso de IA:**
- **Modelo:** Claude Code / Fable 5.
- **Contexto consumido:** ~95k tokens (~9% de janela de 1M).
- **Prompt inicial (verbatim):** "veja onde estamos do projeto agora, o que falta para fazer"
- **Iterações até aceitar:** 1 (nenhuma rodada de correção de conteúdo; docs aceitos de primeira).
- **Erros da IA:** de conteúdo, nenhum. De condução, 1: avançou a análise completa da 1.3 sem esperar o usuário ("para, calma ai") — corrigido no ritmo da sessão.
- **Decisões escaladas:** nenhuma fechada em `Decisoes_pendentes.md`. Decisão 11 atualizada (ponteiros B/C); 3.3 removida por instrução explícita; desenho da C fechado **por delegação explícita** do Felipe (registrada no doc da view); camada tática reformulada registrada só em arquivo por escolha do Felipe.
- **Tags:** [PROMPT-CHAVE] candidato — mesma abertura da sessão anterior, com desdobramento reprodutível (status → candidatas → docs).

## 2026-07-10 — Felipe

**Feito:**
- Revisão do estado do projeto (mapa decidido × em aberto) e sessão de decisão sobre as duas views paradas — **os problemas da 1.2 e da 3.1 foram resolvidos**:
  - **1.2 Momentum: fechada** — reclassificada como **camada tática** (gatilho = tendência/velocidade da probabilidade; sem âncora de magnitude para o template estrutural) → adiada junto com a camada (decisão 10); reabre com a retomada da tática. Registrada nas decisões 1, 3, 4 e 10; removida da Camada 1 do mapa (`Black-Litterman_com_Polymarket.md`) e anotada no aviso do retrato histórico.
  - **3.1 Sentimento: fechada condicionalmente** — reframe para **view de recessão** (caminhos "índice agregado" e "contexto/Ω" rejeitados; o Ω reativo já cobre leitura de regime). Desenho fechado em 2 baterias de perguntas: `Q = (Σ P·β) × (p_poly − p_curva)`; p_poly de binário de recessão (preferência: resolução técnica GDP, condicional ao levantamento do Paulo; midpoint bid/ask + decisão 9); p_curva de probit clássico com coeficientes publicados (Estrella-Mishkin/NY Fed) sobre spread 10a−3m do FRED; β por regressão própria vs Δp_poly com teste de defasagem e absorção plena (maquinaria da 2.4); P espelha a 2.3 (Σ|P| = 2); ativação/desligamento herdados da 2.4. Criado `Informações_uteis/views/view_3.1_recessao.md` (fórmulas, cascata, 9 rejeitadas, pendências).
- Decisão 9 ganhou os itens do binário de recessão (favorite-longshot é **relevante** nesta view — p baixa, ao contrário da 2.4).
- **Decisão 11 criada (🔴 aberta):** views adicionais candidatas para reunião — B (trajetória do Fed vs ZQ de dezembro; reusa β/P da 2.3), C (geopolítica→energia; template poly-defasado da 2.4, XLE) e D (shutdown/fiscal, reserva). A candidata A (recessão) virou a 3.1 na mesma sessão.

**Quebrou / aprendido:**
- Nada de código. Aprendizado: a 3.1 original tinha 3 defeitos (dupla contagem com 2.2/2.3, sem benchmark único, índice = pilha de parâmetros arbitrários) — estreitar para o único pedaço com dois termômetros reais (recessão: poly vs curva) resolve os três de uma vez.

**Pendente:**
- **Reunião:** horizonte da 3.1 (poly "até dez" vs curva 12m rolante + rolagem entre mercados anuais — única decisão de desenho adiada pelo Felipe na sessão; opções mapeadas na view); decisão 11 (views B/C/D); decisões 6 e 9 seguem abertas.
- **Paulo:** mercados de recessão no CLOB (2023–25), critério de resolução, volume e bid/ask histórico (condição da 3.1, como na 2.4); referência exata dos coeficientes do probit a fixar antes de implementar.
- Pendências transversais inalteradas (horizonte do Q, k ↔ rebalance, k≈0 da 2.4, bid/ask histórico); avisos a Paulo/Lia das sessões anteriores seguem pendentes.

**Uso de IA:**
- **Modelo:** Claude Code / Fable 5.
- **Contexto consumido:** ~65k tokens (~6% de janela de 1M).
- **Prompt inicial (verbatim):** "veja onde estamos do projeto agora, o que falta para fazer"
- **Iterações até aceitar:** 1 (explicações leigas da 1.2 e 3.1 e registros aceitos sem rodada de correção; o horizonte da 3.1 foi adiado por escolha do humano, não por erro).
- **Erros da IA:** nenhum.
- **Decisões escaladas:** 11 (nova, aberta). Fechadas por instrução explícita do humano: 1.2 (reclassificação tática, nas decisões 3/4/10) e 3.1 (reframe para recessão, decisões 3/4 — condicional).
- **Tags:** —

## 2026-07-09 (sessão 4) — Felipe

**Feito:**
- Execução documental de decisão de time reportada pelo Felipe: **camada tática (velocidade de ajuste, event-driven 3.2, PEAD 1.1) adiada — removida do escopo do projeto**, fica para retomada futura. Registrada como **decisão 10 (🟢)** em `Decisoes_pendentes.md`; os demais documentos apontam para ela (regra "aponte, não copie").
- Edições por arquivo:
  - `Decisoes_pendentes.md`: decisão 10 criada; **decisão 5 (surpresa do PEAD) fechada sem objeto** (PEAD é inteiramente tático — reabre com a retomada); notas de adiamento nas decisões 1 (universo tático sem efeito), 3 (nota de nomenclatura) e 4 (escopo; pergunta da 1.2 vira "estrutural ou adiada junto com a tática"); rodapé atualizado.
  - `Black-Litterman_com_Polymarket.md`: seção "2. Camada tática" do mapa condensada em nota de adiamento — preserva a descrição de 1 linha da "velocidade de ajuste" (única no repositório; 1.1 e 3.2 têm lar no retrato histórico); numeração das camadas 3/4 mantida para não quebrar referências (ex.: decisão 9 cita "Camada 4"); linha "Atenção" (2.4/firm-specific) atualizada; removida a frase "mesmo sinal roda como view ou tático".
  - `CLAUDE.md`: módulos da Lia viram "Ω reativo · Relatório"; nota de adiamento abaixo da tabela (a tática volta a ser módulo dela se retomada).
  - `Ideias_consolidadas.md`: só o aviso do topo ganhou a menção do adiamento (conteúdo congelado intocado).
  - `views/view_2.4_eleitoral.md`: 3 referências à tática anotadas como adiada (status, item 0, decisões rejeitadas).
  - Inalterados: `README.md` e views 2.2/2.3 (sem menção à tática); entradas antigas do LOG (histórico não se reescreve). Camada de risco (1.3, 3.3), Ω reativo e reserva (3.4) **não** foram tocados — não são tática.

**Quebrou / aprendido:**
- Nada de código. Ponto de atenção: a "velocidade de ajuste" não tinha lar fora do mapa de camadas — deletar a seção seca apagaria a ideia do repositório, contrariando o "fica para depois"; ficou preservada na nota compacta.

**Pendente:**
- **Avisar Paulo/Lia:** decisão 10 + módulo da Lia reduzido no `CLAUDE.md` (mudanças no branch Felipe, valem após merge) — soma-se ao aviso pendente da sessão 3 (deleções de arquivos).
- Decisões abertas: 3/4 para 3.1 e 1.2; 6 e 9. Pendências transversais inalteradas (Σ|P|, horizonte do Q, k≈0, bid/ask histórico no CLOB).

**Uso de IA:**
- **Modelo:** Claude Code / Fable 5 (effort max).
- **Contexto consumido:** ~50k tokens (~5% de janela de 1M).
- **Prompt inicial (verbatim):** "Leia c:\Users\felip\Documents\Pessoal\Desafio-Quant-Itau\Informações_uteis\Black-Litterman_com_Polymarket.md. c:\Users\felip\Documents\Pessoal\Desafio-Quant-Itau\Informações_uteis\Ideias_consolidadas.md, c:\Users\felip\Documents\Pessoal\Desafio-Quant-Itau\Decisoes_pendentes.md, c:\Users\felip\Documents\Pessoal\Desafio-Quant-Itau\LOG.md, c:\Users\felip\Documents\Pessoal\Desafio-Quant-Itau\CLAUDE.md. Saiba que o Log pode ter informações desatualizadas por ser uma memoria de dump."
- **Iterações até aceitar:** 1 (a confirmar pelo humano).
- **Erros da IA:** nenhum.
- **Decisões escaladas:** 10 (nova, registrada como fechada por decisão de reunião reportada pelo humano); 5 fechada sem objeto como consequência direta da 10.
- **Tags:** —

## 2026-07-09 (sessão 3) — Felipe

**Feito:**
- **Limpeza de divergências** (sem código): auditoria dos 11 `.md` do repositório; 22 edições em 9 arquivos, todas por decisão do humano (3 baterias de perguntas):
  - `Ideias_consolidadas.md` congelado como retrato histórico (aviso no topo); Mapa/BL doc atualizados às views fechadas (2.4 sem cestas/cross-section de β; exemplo da 2.3 em bps — não probabilidade; "real estate" fora dos exemplos; convergência entre fontes anotada como stub fora do v1 — decisão 7).
  - **"Camada 2 (cenário→ativo)" absorvida no bridge:** módulos do Felipe no `CLAUDE.md` viram "Otimizador BL · Bridge probabilidade→Q (P, Q e β por view) · Integração final"; "Camada 2" volta a ter significado único (camada tática).
  - Decisão 4 compactada: linhas 2.2/2.3/2.4 da tabela da Família A apontam "fechada → `views/`"; perguntas de reunião reduzidas às restantes (3.1 e 1.2); rodapé com o próximo passo real.
  - LOG: cabeçalho faltante "2026-07-09 (sessão 1)" inserido no bloco órfão do fechamento 2.2/2.3; data da view_2.2 corrigida (08 → 09/jul).
- **Reestruturação do repositório** (decisão do humano): `CRONOGRAMA_GERAL.md` (deadlines não usados; regras duplicavam CLAUDE.md), `FELIPE_arquitetura_BL.md` (duplicava CLAUDE.md/views) e `Mapa_de_camadas.md` **deletados**; mapa de camadas + norte geral **fundidos** em `Black-Litterman_com_Polymarket.md` (nenhum conteúdo perdido; seção "Sinais táticos" deduplicada dentro da Camada tática). 11 → 8 arquivos `.md`.
- README de índice ("onde cada informação vive" + regra "aponte, não copie") proposto no chat — Felipe comita na main.

**Quebrou / aprendido:**
- Nada de código. Aprendizado: a desorganização vinha de **sobreposição de lares** (a view 2.4 estava descrita em 6 lugares), não do número de arquivos. Regra adotada: um arquivo-lar por tipo de informação; os demais apontam, não copiam.

**Pendente:**
- Felipe: comitar o README na main; **avisar Paulo/Lia** das deleções (Cronograma, Mapa, FELIPE_arquitetura) — mudanças no branch Felipe, valem após merge.
- Estado das decisões inalterado: 3/4 abertas para 3.1 e 1.2; 5, 6 e 9 abertas; pendências transversais (Σ|P|, horizonte do Q, k≈0, bid/ask histórico no CLOB) seguem como estavam.

**Uso de IA:**
- **Modelo:** Claude Code / Opus 4.8 e Fable 5 (troca via `/model` no início; effort max).
- **Contexto consumido:** ~90k tokens (~9% de janela de 1M).
- **Prompt inicial (verbatim):** "Tenho um problema de organização. Tenho varios documentos de informações sobre a minha parte/as ideias/ a estratégia em geral. Acredito que tem informações conflitantes e um excesso de documentos. Vamos começar fazendo uma limpeza de informações. preciso que você leia todos os documentos md do repositório e vá me perguntando como resolver cada divergencia de informação que encontrar" (um prompt anterior na mesma sessão veio cortado e foi abortado com "stop").
- **Iterações até aceitar:** 1 (nenhuma rodada de correção; todas as escolhas coletadas em 3 baterias de perguntas estruturadas antes de editar).
- **Erros da IA:** nenhum.
- **Decisões escaladas:** — (nenhuma nova/fechada em `Decisoes_pendentes.md`; as escolhas foram de organização documental, sem impacto metodológico).
- **Tags:** —

## 2026-07-09 (sessão 2) — Felipe

**Feito:**
- Sessão de decisão (sem código): desenho da **view 2.4 Eleitoral** fechado, no mesmo processo das 2.2/2.3 (7 perguntas levantadas pela IA a partir de `Ideias_consolidadas.md` + `Mapa_de_camadas.md`; respostas/decisões do humano). Criado `Informações_uteis/views/view_2.4_eleitoral.md`.
- Decisões principais registradas:
  - Escopo só eleitoral ("regulatória" saiu do nome; firm-specific → tática 3.2). Evento: presidencial EUA 2024, binário de vencedor sobre p(Trump) (p(democrata) tem quebra de identidade em 21/jul/2024); 2022 = robustness check; Senado/Câmara/sweep fora (distribuição conjunta).
  - β por regressão própria (retorno diário do ETF vs Δp(Trump)), híbrida: β manda sempre, literatura só sanity check a posteriori (nunca inverte β); janela expandida sem lookahead; teste de defasagem Δp(t−1)→retorno(t) obrigatório.
  - **Segunda exceção à Família A:** sem instrumento externo precificando o evento, o benchmark é o **próprio poly defasado** — `Q = (Σ P[i]·β_i) × (p_t − p_{t−k})`, k estimado pela varredura de defasagem, β de absorção plena = soma dos coeficientes dos lags 0…k; **Q é retorno acumulado de k dias**. k ≈ 0 → view nunca liga (condição permanente; o que fazer é pendência). Acoplamento k ↔ frequência de rebalance co-documentado.
  - P cross-sectional `P[i] ∝ (β_i − β_SPY)` com Σ|P| = 2; centragem em β_SPY mantida por consistência com a 2.3, com obrigação de medir ΣP e decidir sobre o componente direcional (trocar 2.3 e 2.4 juntas, se for o caso).
  - Ativação sem parâmetros (existe mercado → ativa; liquidez é papel do Ω); **desligamento no último dia antes do primeiro tick de resolução** (senão o salto de 5–6/nov fabrica alfa).
  - Pré-processamento: midpoint bid/ask (nunca último trade — série stale infla k); itens (a)/(b)/(c) registrados na decisão 9.
- `Decisoes_pendentes.md` atualizado: decisões 3 e 4 agora fechadas para 2.2, 2.3 **e 2.4** (em aberto: 3.1 e 1.2); decisão 9 ganhou os itens da 2.4, incluindo o novo item "qual preço da série".

**Quebrou / aprendido:**
- Nada de código. Aprendizados: 2.2/2.3 têm benchmark porque existe um segundo instrumento precificando a mesma variável — na eleição não existe, e o benchmark correto é o poly defasado; TIP−TLT é identidade, não cesta escolhida (o argumento "par é mais legível" não transfere para a eleição); a escolha do preço da série (midpoint vs último trade) pode fabricar a defasagem k inteira.
- **Inconsistência detectada entre views:** 2.3 normaliza Σ|P| = 1; 2.2 (par +1/−1) e 2.4 usam Σ|P| = 2 — Q das views em escalas diferentes. Registrada como pendência transversal (reconciliar mudando as views juntas).

**Pendente:**
- Paulo: histórico do mercado presidencial 2024 no CLOB — **se há bid/ask histórico para reconstruir o midpoint** (a view está "fechada condicionalmente" a isso); idem 2022.
- Parâmetros numéricos por decisão humana: limiar de volume p/ estimabilidade do β; frequência de rebalanceamento (acoplada ao k).
- **k ≈ 0 (decisão de reunião não tomada):** fallback para tilt contemporâneo `Q = β·Δp` ou 2.4 fora do v1.
- **Horizonte do Q** (acumulado de k dias) a reconciliar com Σ e π antes da implementação.
- Reconciliar Σ|P| entre 2.3 e 2.4 (e 2.2) — juntas.
- Views 3.1 (Sentimento) e 1.2 (Momentum) — próximas da fila; decisão 9 (módulo PMF compartilhado) segue aberta.

**Uso de IA:**
- **Modelo:** Claude Code / Fable 5.
- **Contexto consumido:** ~90k tokens (~9% de janela de 1M).
- **Prompt inicial (verbatim):** "Fechei o desenho das views 2.2 e 2.3. agora quero seguir para a 2.4 Leia a descrição dela em c:\Users\felip\Documents\Pessoal\Desafio-Quant-Itau\Informações_uteis\Ideias_consolidadas.md e c:\Users\felip\Documents\Pessoal\Desafio-Quant-Itau\Informações_uteis\Mapa_de_camadas.md Com base nisso monte perguntas para decidirmos o que falta do seu desenho. No final vamos montar um documento simples com o que foi decidido/ rejeitado e o que a ideia deve fazer"
- **Iterações até aceitar:** 2 (perguntas aceitas de primeira; doc da 2.4 passou por 1 rodada de revisão do humano com 7 correções, todas aplicadas).
- **Erros da IA:** nas perguntas — as opções da Q4 partiam de premissa errada (exigir benchmark externo, que não existe para eleição; o humano propôs a opção D, poly defasado); Q4-B descreveu `β × Δp` incorretamente como momentum; Q6 ofereceu parâmetro desnecessário ("N meses antes") e fundiu ativação/peso/estimação; Q7 não listou a sub-decisão mais grave (qual preço da série). No doc (pegos na revisão do humano) — contradição interna Σ|P| = 2 rotulado "long 1/short 1" quando ΣP ≠ 0; Q sem declarar que é retorno acumulado de k dias nem a premissa de spike no lag k, e "β de absorção plena" usado sem definição; colisão de janelas no item 3 (fim da amostra "até a resolução" reintroduzia lookahead); k ≈ 0 tratado como a mesma cascata do item 0, escondendo decisão não tomada; unidade de p ambígua (%/fração); consequência do limiar de amostra ausente; status "🟢 fechada" incompatível com pendência declarada como invalidante.
- **Decisões escaladas:** 3 e 4 fechadas para a view 2.4 por instrução humana explícita; decisão 9 expandida (itens a/b/c da 2.4); nova pendência transversal Σ|P|.
- **Tags:** —

## 2026-07-09 (sessão 1) — Felipe

**Feito:**
- Sessão de decisão (sem código): fechamento das decisões 3 e 4 **por view**, ideia por ideia, para as duas primeiras views estruturais:
  - **View 2.2 Inflação (fechada):** divergência em pontos de inflação (E_poly[CPI] via média da PMF dos buckets do poly vs breakeven T10YIE/FRED); Q = duration do breakeven 10a (~8) × Δinflação, par TIP−TLT; β = duration (exceção à Família A, sem regressão); cascata de degradação (PMF → binário via normal deslocada → view desativada com Ω→∞); pré-processamento das probs (normalização bid/ask, favorite-longshot, bucket aberto).
  - **View 2.3 Fed (fechada):** surpresa = E_poly[Δtaxa] − E_FF[Δtaxa] em bps (E_poly da PMF dos buckets de FOMC; E_FF do futuro ZQ via yfinance, contrato do mês posterior à reunião); β por regressão própria event-study contra surpresa à la Kuttner (literatura B-K só como sanity check); P = função determinística do vetor β, centrado em β_SPY (P[SPY]=0 exato); Q = surpresa · Σ P[i]·β_i (retorno do portfólio long-short definido por P); sanity check de sinal marcado como teste obrigatório.
- Criados `Informações_uteis/views/view_2.2_inflacao.md` e `view_2.3_fed.md` (resumo da ideia, decisões fechadas e rejeitadas, pendências por view).
- **Decisão 9 registrada** em `Decisoes_pendentes.md`: pré-processamento de PMFs como módulo compartilhado entre 2.2 e 2.3 (aberta — verificar se se comporta igual nas duas antes de compartilhar).
- Decisões 3 e 4 atualizadas para 🟡 com registro parcial (2.2 e 2.3 fechadas; 2.4, 3.1 e 1.2 em aberto).

**Quebrou / aprendido:**
- Nada de código. Aprendizados registrados nos docs das views: mercados de CPI/FOMC do poly são **buckets exatos (PMF)**, não thresholds (CDF); do ZQ sai **esperança em bps, não probabilidade** (não existe p_FF); benchmark e duration da 2.2 são acoplados; origem do β e construção de P na 2.3 são acopladas (β da literatura quebraria o centro β_SPY).

**Pendente:**
- Views 2.4 (Eleitoral), 3.1 (Sentimento) e 1.2 (Momentum) — próximas da fila para fechar 3/4 por completo.
- Decisão 9 aberta (módulo de PMF compartilhado).
- Pendências críticas de dados (Paulo): cobertura histórica dos mercados de CPI e de FOMC no poly (~18 meses), inclusão do FRED (T10YIE) no pipeline, qualidade do histórico do ZQ no yfinance.
- Fonte das datas de FOMC + variação do FF future no dia (para a regressão da 2.3) a acordar; parâmetros numéricos (janela da regressão, valor exato da duration) por decisão humana.

**Uso de IA:**
- **Modelo:** Claude Code / Fable 5.
- **Contexto consumido:** ~65k tokens (~6.5% de janela de 1M).
- **Prompt inicial (verbatim):** "vamos fechar as decisões 3 e 4 juntas como falado. quero passar ideia por idea e decidir o que precisa"
- **Iterações até aceitar:** 4 (doc da 2.2: 1 rodada de correção com 6 pontos; doc da 2.3: 2 rodadas — unificação da fórmula/notação do Q/sinal, depois colapso de itens duplicados e interpretação do Q).
- **Erros da IA:** descreveu os mercados de CPI do poly como thresholds (">X%") quando são buckets exatos (PMF); introduziu um `p_FF` inexistente no fallback binário da 2.3 (do ZQ sai esperança, não probabilidade); duplicou a fórmula da surpresa em dois itens do doc; notação do Q imprecisa (`P · (β × surpresa)`) e sem interpretação do portfólio long-short.
- **Decisões escaladas:** 9 (nova, aberta); 3 e 4 parcialmente fechadas (views 2.2 e 2.3) por instrução humana explícita.
- **Tags:** —

## 2026-07-08 (sessão 3) — Felipe

**Feito:**
- Sessão de discussão (sem código). Explicada a Decisão 3 (mapeamento cenário→ativo): o que é, opções da forma da regressão (Δprob vs. dummy de resolução vs. surpresa macro realizada), trade-offs, onde entra no BL (alimenta a magnitude de Q, não P/Ω) e que partes toca.
- **Reframe conceitual da Decisão 3 registrado (decisão do Felipe):** descartada como objeto a **tabela central de sensibilidades** (grade única cenários × ativos que traduziria prob crua). É redundante — nunca alimentamos prob crua ao BL para uma tabela central traduzir. Na arquitetura real cada view da Camada 1 monta P e Q sozinha a partir do histórico do seu próprio mercado poly. A conta de sensibilidade (β) **não some**, mas passa a ser interna a cada view/família.
- **Colapso Decisão 3 ↔ Decisão 4 registrado:** "estimar magnitude" (3) e "fabricar Q da probabilidade" (4) viram quase a mesma operação por família; devem ser fechadas juntas, por família. Adicionadas notas cruzadas nas duas seções.
- Ajustada a frase da "Consequência p/ o planejamento" (Decisão 4) que dizia que o β vinha de um "mapeamento cenário→ativo" central — agora reflete que a sensibilidade é interna a cada view.

**Quebrou / aprendido:**
- Nada de código. Aprendizado: a tabela central de sensibilidades era incompatível com a arquitetura "cada view monta seu P/Q"; Decisões 3 e 4 não são independentes — colapsam por família.

**Pendente:**
- Decisão 3 segue 🔴: descarte da tabela central está registrado, mas a **forma da regressão por família** (Δprob vs. dummy de resolução) segue aberta — fecha junto com a Decisão 4.
- Decisão 4 segue 🔴 — fechar view a view / por família (próximo passo sugerido: 2.2 Inflação).
- Decisões 5 e 6 seguem abertas.

**Uso de IA:**
- **Modelo:** Claude Code / Opus 4.8.
- **Contexto consumido:** ~75k tokens (~38% de janela de 200k).
- **Prompt inicial (verbatim):** "preciso fechar as decisões 3 e 4. comece me explicando a 3, as opções que tenho, seus trade offs, onde ela entra do black littermann e que partes do projeto ela engloba?"
- **Iterações até aceitar:** 1 (explicação da Decisão 3 aceita; registro do reframe feito conforme decisão conceitual passada pelo Felipe).
- **Erros da IA:** nenhum.
- **Decisões escaladas:** reframe da Decisão 3 (descarte da tabela central) e colapso 3↔4 registrados; nenhuma fechada como 🟢.
- **Tags:** —

## 2026-07-08 (sessão 2) — Felipe

**Feito:**
- Sessão de discussão sobre a Decisão 4 (sem código). Explicada a decisão como um todo (ponte prob→Q, template por view, Famílias A/B).
- **Correção de nomenclatura + registro:** identificada colisão do termo "Camada 2" nos documentos. No `Mapa_de_camadas.md`, **Camada 2 = camada tática**; no `FELIPE_arquitetura_BL.md` e na Decisão 3, "Camada 2" = mapeamento cenário→ativo. O que o grupo congelou (por exigir dados de alta frequência que a granularidade da API não dá) é a **camada tática**, não o mapeamento de sensibilidades — que **segue de pé**.
- Correções aplicadas no `Decisoes_pendentes.md`: título da Decisão 3 sem o "(Camada 2)" ambíguo; nota de status deixando claro que o mapeamento não está congelado (é fonte das β da Família A); célula do Fed ajustada; **parágrafo "Consequência p/ o planejamento" da Decisão 4 reescrito** com a premissa certa (congelado = tática; mapeamento vivo → magnitudes das views estruturais não bloqueadas).
- Implicação registrada: com o mapeamento vivo, a Família A inteira tem fonte de β; o que separa as views é o trabalho próprio de cada uma (cestas na 2.4, view-vs-prior na 3.1, magnitude frágil na 1.2).

**Quebrou / aprendido:**
- Nada de código. Aprendizado: as entradas anteriores do LOG (07/07 e 07/08 sessão 1) atribuíram o congelamento à "Camada 2 (decisão 3)" por causa da colisão de nomes — o correto é **camada tática congelada**. Histórico das entradas antigas preservado; correção fica registrada aqui.

**Pendente:**
- Decisão 4 segue aberta — próximo passo: fechar view a view, começando pela **2.2 Inflação**.
- Decisão 3 (mapeamento cenário→ativo) segue aberta (forma da regressão), mas **não congelada**.
- Decisões 5 e 6 seguem abertas.

**Uso de IA:**
- **Modelo:** Claude Code / Opus 4.8.
- **Contexto consumido:** ~70k tokens (~35% de janela de 200k).
- **Prompt inicial (verbatim):** "preciso fechar a decisão 4. Acho bom passarmos por cada uma das ideias para também relembrar como elas funcionam e decidir juntos como as views serão formadas por elas. Comece explicando de forma rápida e consisa a decisão 4 como um todo"
- **Iterações até aceitar:** 3 (explicação da Decisão 4 aceita; depois 2 rodadas de correção sobre qual camada estava congelada, até a IA acertar que é a tática e reescrever o registro).
- **Erros da IA:** 1 — inverteu inicialmente o que estava congelado (afirmou que o mapeamento de sensibilidades estava frozen; na verdade é a camada tática). Corrigido após o usuário apontar.
- **Decisões escaladas:** nenhuma fechada. Correção de registro nas Decisões 3 e 4 (nomenclatura + parágrafo de consequência).
- **Tags:** —

## 2026-07-08 — Felipe

**Feito:**
- Sessão de discussão sobre a Decisão 4 (probabilidade → Q). Insight-chave do usuário: a Camada 1 tem múltiplas views, cada uma com a própria análise/âncora, então a Decisão 4 **não é uma fórmula única** — é um template por view.
- Reescrita da seção 4 do `Decisoes_pendentes.md` com o reframe (status segue 🔴 aberta): 5 views estruturais agrupadas em 2 famílias.
  - **Família A (divergência + sensibilidade):** 2.3 Fed, 2.2 inflação, 2.4 eleitoral, 3.1 sentimento macro — esqueleto comum `Q = sens × (prob_poly − prob_mercado)`, forma relativa.
  - **Família B (série temporal):** 1.2 momentum — não encaixa no template de divergência.
  - Tabelas por view (âncora, sinal do poly, Q natural, o que falta decidir) + 3 perguntas de reunião.
- Consequência registrada: o "Camada 2 congelada" só bloqueia parte das views — **2.2 (mecânica via duration) e 2.3 (beta estreita) destravam sem a Camada 2**.

**Quebrou / aprendido:**
- Nada quebrou (sessão sem código). Aprendizado: a Decisão 4 deve ser especializada por view, não global.

**Pendente:**
- Decisão 4 segue aberta — agora estruturada como template por view; falta a reunião responder as 3 perguntas (adotar template Família A? quais views no v1? 1.2 estrutural ou tático?).
- Parâmetros numéricos por view (β, duration, valor justo da cesta) ainda dependem de decisão humana.
- Decisões 3, 5 e 6 seguem abertas (3 congelada até a reformulação da Camada 2).

**Uso de IA:**
- **Modelo:** Claude Code / Opus 4.8.
- **Contexto consumido:** ~50k tokens (~25% de janela de 200k).
- **Prompt inicial (verbatim):** "Das decisões pendentes quero resolver a 4 agora. me explique o que tenho que escolher, as opções e trade-offs"
- **Iterações até aceitar:** 2 (explicação inicial das opções; usuário reformulou com o insight de "template por view" e a explicação foi refeita e aceita).
- **Erros da IA:** nenhum.
- **Decisões escaladas:** Decisão 4 reescrita/reestruturada (mantida em aberto; nenhuma fechada).
- **Tags:** —

## 2026-07-07 — Felipe

**Feito:**
- Sessão de discussão (sem código novo): explicação detalhada das decisões 4 e 8, do cálculo completo do Black-Litterman (π, P, Q, Ω, posterior, pesos) e dos trade-offs de cada opção.
- **Decisão 8 fechada em reunião** e registrada em `Decisoes_pendentes.md`:
  - Parte A: **Σ amostral** no passo final (caso neutro limpo: confiança zero → `w_mkt`; encolhimento por incerteza fica a cargo do Ω reativo).
  - Parte B: **B1 — irrestrito** (fórmula fechada, aceita short/desvio de soma = 1; reavaliar se o backtest mostrar pesos extremos). Alternativas B2/B3/B4 mantidas no arquivo como referência.
- Docstring de `optimal_weights` em `src/bl_optimizer.py` atualizado: TODO(DECISAO-8) → decisão fechada.
- Limpeza: seção 8 estava duplicada em `Decisoes_pendentes.md` (usuário removeu a duplicata; sobra de linha "Decisão" consolidada na edição).

**Quebrou / aprendido:**
- Nada quebrou. Alinhamento do time: Camada 2 (decisão 3) fica de fora por ora — vai passar por reformulação; foco apenas na camada estrutural.

**Pendente:**
- Decisão 4 (probabilidade → Q) segue aberta — é a única que bloqueia o bridge e agora deve ser discutida sem depender da Camada 2 (magnitudes não virão da regressão da decisão 3 por enquanto).
- Decisões 3, 5 e 6 seguem abertas (3 congelada até a reformulação da Camada 2).

**Uso de IA:**
- **Modelo:** Claude Code / Fable 5.
- **Contexto consumido:** ~55k tokens (~25% de janela de 200k).
- **Prompt inicial (verbatim):** "Sentei e discuti com o meu grupo sobre o que iriamos fazer com as decisões pendentes. Olhando o que faltava, decidimos que eu iria ficar responsável por entender e fechar as decisões 4 e 8, por que fazem parte das minhas responsabilidades. Me explique de forma consisa e rápida o que precisamos decidir na 4."
- **Iterações até aceitar:** 1 (explicações aceitas sem rodada de correção; uma iteração extra a pedido do usuário para aprofundar o cálculo do BL).
- **Erros da IA:** nenhum (um Edit falhou por edição concorrente do usuário no arquivo, não por erro do modelo).
- **Decisões escaladas:** — (nenhuma nova; decisão 8 foi fechada por instrução humana explícita).
- **Tags:** —

## 2026-07-05 — Felipe

**Feito:**
- Esqueleto do otimizador BL (`src/bl_optimizer.py`): reverse optimization (`implied_equilibrium_returns`), posterior He & Litterman (`bl_posterior` → μ_bl e Σ_bl) e pesos mean-variance irrestritos (`optimal_weights`). Funções puras, validação de shapes, sem dados/parâmetros hardcoded.
- Testes sintéticos (`tests/test_bl_optimizer.py`, 4 testes, todos passando): round-trip da reverse optimization, confiança ~0 → posterior = prior (e Σ_bl → (1+τ)Σ), confiança total → P·μ_bl = Q, tilt monotônico com a confiança. `python tests/test_bl_optimizer.py` roda testes + demo ponta a ponta.

**Quebrou / aprendido:**
- Primeira versão do teste de monotonicidade assumia tilt positivo, mas o prior de equilíbrio já implicava spread (2,1%) maior que a view (2%) — view era baixista em relação ao prior. Corrigido usando view de 5% no teste/demo.

**Pendente:**
- Interface proposta (arrays numpy com shapes documentados no docstring de `bl_optimizer.py`, ordem de ativos definida pelo dataset) precisa de ok do Paulo e da Lia.
- Nova decisão registrada: item 8 em `Decisoes_pendentes.md` (Σ amostral vs Σ_bl no passo de pesos + restrições da carteira).
- τ e δ reais dependem de decisão; os dos testes são sintéticos e marcados como tal.
