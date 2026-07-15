# Para Paulo e Lia — views, mercados do Polymarket e pendências de vocês

Preparado pelo Felipe (2026-07-14, branch Felipe). Duas partes:
- **Parte 1:** como funcionam TODAS as views e táticas, e o que cada uma precisa de dado — em especial quais mercados do Polymarket levantar e com que características.
- **Parte 2:** as pendências que são de vocês (decisões que não passam pelo Felipe), consolidadas de `pauta_reuniao_outros.md`.

Fontes detalhadas: `Informações_uteis/views/*.md`, `Informações_uteis/táticas/*.md`, `Decisoes_pendentes.md`.

---

# PARTE 1 — Como as views funcionam e que dados precisam

## 1.0 O que vale para TODAS as views (leiam antes das fichas individuais)

- **Universo (decisão 1):** 9 ETFs — XLK, XLU, XLP, XLF, XLE, XLV, TIP, TLT, SPY. Preços via yfinance, frequência diária.
- **Contrato de saída:** cada view devolve `ViewResult(P, Q, diagnostics)` ou `None` (desativada). `P` é um vetor alinhado ao universo com convenção **Σ|P| = 2** (o Q se lê como "retorno do lado comprado − lado vendido"); `Q` em fração decimal; `diagnostics` é o dict livre que alimenta o Ω da Lia.
- **Cascata de degradação (padrão):** sem mercado no poly no período → view desativada, Ω → ∞, o BL fica no prior. **Não é falha, é comportamento correto.** Liquidez baixa **não** desliga view — quem penaliza liquidez é o Ω reativo (módulo da Lia); nenhuma view tem interruptor próprio de liquidez.
- **Desligamento na resolução:** toda view desliga no último dia **antes do primeiro tick de resolução** do seu mercado (ex.: 5–6/nov/2024 na eleição, p salta de ~0,6 para 1,0 — usar esse salto seria alfa fabricado).
- **Preço da série do poly = midpoint bid/ask, NUNCA último trade.** Em mercado fino o último trade fica stale (série em degraus) e infla artificialmente a defasagem k que várias views estimam. ⚠️ **Isso é a condição crítica de dados do projeto:** o pipeline precisa entregar **bid e ask históricos crus** do CLOB (endpoint `/prices-history` — verificar qual preço ele entrega). Sem bid/ask histórico, as views 2.4, 3.1, C, E e G perdem a condição de fechamento.
- **Pré-processamento compartilhado** (`src/poly_preprocessing.py`, decisão 9, módulo do Felipe): midpoint bid/ask → normalização (probs não somam 1 por causa do spread) → correção de favorite-longshot → (nas PMFs) valor do bucket aberto. As duas últimas peças estão **sem forma/valor decididos (decisão 11)** — os stubs falham alto (`NotImplementedError`) de propósito, então **nenhuma view roda com dado real até a decisão 11 fechar** (ver Parte 2, Calibração).
- **Dois tipos de mercado no poly:**
  - **PMF de buckets** (faixas mutuamente exclusivas): CPI, decisão do FOMC, trajetória de juros. A view tira a esperança `E = Σ pᵢ·xᵢ`.
  - **Binário** (sim/não): eleição, recessão, geopolítica, tarifas, fiscal. A view usa a probabilidade (nível ou diferença).
- **Template poly-defasado** (2.4, C, E, G): quando não existe instrumento tradicional precificando o evento, o benchmark é o **próprio poly defasado**: `divergência = p_t − p_{t−k}`, com k estimado por teste de defasagem (Δp(t−k) → retorno(t)) e β de "absorção plena". Consequência para dados: essas views são as mais sensíveis à qualidade da série (midpoint, dias sem trade).

## 1.1 Views fechadas (entram no v1)

### View 2.2 — Inflação (TIP vs TLT) 🟢
- **Ideia:** inflação implícita no poly (mercados de CPI) vs breakeven de 10 anos. Poly acima do breakeven → long TIP / short TLT; abaixo → o inverso.
- **Fórmula:** `Q = duration(~8) × (E_poly[CPI] − breakeven_T10YIE)`; `P = +1 TIP / −1 TLT`. Sem regressão (β = duration, exceção mecânica).
- **Polymarket:** mercados **mensais de CPI**, buckets exatos (≤3.6%, 3.7%, 3.8%…) — uma **PMF**, não thresholds. `E_poly[CPI] = Σ pᵢ·xᵢ`. Tem **bucket aberto** ("≤3.6%") que precisa de valor atribuído (decisão 11b) e favorite-longshot morde a **cauda direita** (buckets caros e finos).
- **O que o Paulo precisa levantar:** cobertura histórica dos mercados de CPI nos últimos **~18 meses** (quantos meses têm mercado listado e líquido) — é a única pendência que pode invalidar a view inteira. Fallback se só houver binário: normal deslocada com vol histórica do CPI.
- **Outras fontes:** FRED `T10YIE` (breakeven 10a) — entra no pipeline.

### View 2.3 — Fed / surpresa de juros (Bernanke-Kuttner) 🟢
- **Ideia:** poly precifica a decisão do FOMC; os Fed Funds futures também. A divergência é uma surpresa esperada que as ações ainda não pagaram; setores long-duration (tech) reagem mais.
- **Fórmula:** `surpresa = E_poly[Δtaxa] − E_FF[Δtaxa]` em bps; β por regressão própria (event-study em dias de FOMC contra surpresa à la Kuttner); `P[i] = 2·(β_i − β_SPY)/Σ|β_j − β_SPY|` (P[SPY]=0); `Q = surpresa · Σ P·β`.
- **Polymarket:** buckets de **decisão por reunião do FOMC** (−50bp, −25bp, manutenção, +25bp…) — PMF. Fallback binário: `E_poly = p × 25bp`.
- **O que o Paulo precisa levantar:** cobertura histórica dos mercados de FOMC (buckets por reunião, liquidez).
- **Outras fontes:** futuro **ZQ no yfinance** — usar o **contrato do mês posterior à reunião** (evita ajuste de média de dias). Do ZQ sai **esperança em bps, não probabilidade**. Também: **datas de FOMC + variação do FF future no dia do anúncio** (insumo da regressão do β — fonte a acordar).

### View 2.4 — Eleitoral (poly-defasado) 🟢 condicional
- **Ideia:** o poly precifica o vencedor em tempo real; a bolsa absorve com defasagem k. Divergência = `p_t − p_{t−k}` (benchmark = próprio poly defasado, não há instrumento externo).
- **Fórmula:** β por regressão própria (retorno diário do ETF vs Δp(Trump)); `P ∝ (β_i − β_SPY)`, Σ|P| = 2; `Q = (ΣP·β) × (p_t − p_{t−k})` — retorno **acumulado de k dias**.
- **Polymarket:** presidencial EUA **2024**, mercado binário de **vencedor**, sempre **p(Trump)** (p(democrata) tem quebra Biden→Harris em 21/jul/2024). 2022 como robustness (liquidez fraca esperada). Série diária, **midpoint bid/ask obrigatório** — aqui o k é o conteúdo inteiro da view, e último trade stale fabrica defasagem falsa. Reportar dias sem trade.
- **O que o Paulo precisa levantar:** histórico do mercado presidencial 2024 no CLOB e **se há bid/ask histórico** (é a condição da view); idem 2022.
- **Condição de fechamento:** bid/ask histórico. Se o teste de defasagem der k ≈ 0, a view nunca liga (pendência de reunião).

### View 3.1 — Recessão (poly vs curva de juros) 🟢 condicional
- **Ideia:** a curva 10a−3m precifica recessão (probit Estrella-Mishkin/NY Fed); o poly também, num binário. `divergência = p_poly − p_curva` — os dois lados são probabilidades do mesmo evento.
- **Fórmula:** β por regressão própria vs Δp_poly (maquinaria da 2.4: teste de defasagem + absorção plena); P espelha a 2.3; `Q = (ΣP·β) × (p_poly − p_curva)`.
- **Polymarket:** mercado **binário de recessão EUA**. **Preferência: resolução técnica** (2 trimestres de PIB negativo — resolve mecanicamente com dado do BEA); mercado NBER só se for o único líquido (declaração atrasada do NBER contamina o preço). Midpoint bid/ask. ⚠️ Favorite-longshot é **relevante aqui**: mercados de recessão vivem em p baixa, região de viés máximo.
- **O que o Paulo precisa levantar:** quais mercados de recessão existem no CLOB (2023–25), **critério de resolução de cada um**, volume e bid/ask histórico.
- **Outras fontes:** FRED `DGS10` e `DTB3` (spread 10a−3m diário); **referência exata dos coeficientes do probit publicado** (paper/tabela NY Fed) — fixar antes de rodar.
- **Pendência de reunião:** horizonte (poly pergunta "recessão até dez" — janela que encolhe — vs curva 12m rolante) + rolagem entre mercados anuais (2024→2025).

## 1.2 Views candidatas (código pronto; ENTRADA na carteira é decisão de reunião)

### View B — Trajetória do Fed (taxa de fim de ano) 🟡
- **Ideia:** a 2.3 pergunta "próxima reunião"; a B pergunta "onde a taxa termina o ano". `surpresa_caminho = E_poly[taxa_fim_de_ano] − E_ZQdez`, em bps. β e P **reusados da 2.3** (nenhuma estimação nova; premissa a confirmar em reunião).
- **Polymarket:** buckets de **cortes acumulados / taxa em dezembro** ("quantos cortes em ANO", "taxa em dez/ANO") — PMF; atenção ao bucket aberto tipo "5+ cortes". Fallback binário "corte até dezembro?".
- **O que o Paulo precisa levantar:** quais mercados de trajetória existem no CLOB (2023–25), histórico, liquidez, estrutura dos buckets; e o **ZQ de dezembro** no yfinance (contrato fixo do ano, não rola mês a mês).

### View C — Geopolítica → energia (poly-defasado) 🟡
- **Ideia:** risco de oferta de petróleo (guerra/cessar-fogo/sanções) → XLE reage oposto ao resto (Kilian & Park). Benchmark = poly defasado, template da 2.4. **Um mercado designado por vez.**
- **Polymarket:** **evento primário = ação militar EUA/Israel × Irã (2025)** (ex.: "US military action against Iran before July?" e família "US strikes Iran by...?"); **robustness = família cessar-fogo Rússia × Ucrânia** (mercados por deadline). Binários, midpoint bid/ask, favorite-longshot relevante (p baixa, ~0,1–0,4). Eventos episódicos: a view liga/desliga várias vezes na janela.
- **O que o Paulo precisa levantar:** confirmar no CLOB os mercados Irã 2025 e Rússia×Ucrânia — cobertura na janela do backtest, volume, critério de resolução, bid/ask histórico. (Volumes citados nos docs vieram de levantamento web — validar no dado.)

### View E — Tarifas / política comercial (poly-defasado) 🟡
- **Ideia:** tarifas penalizam quem depende de cadeia global (tech) e disparam flight-to-safety em Treasuries (TLT sobe) — âncora Amiti et al. Benchmark = poly defasado.
- **Polymarket:** **evento primário = família EUA×China** (imposição/escalada de tarifas); **robustness = tarifas recíprocas / "Liberation Day" 2025**. Binários, midpoint bid/ask.
- **O que o Paulo precisa levantar:** mercados da família EUA×China (2024–25) e recíprocas no CLOB — cobertura, volume, critério de resolução, bid/ask histórico; **indicar o binário-mãe por período pelo critério de liquidez**.

### View G — Fiscal: tributária + teto da dívida (poly-defasado) 🟡 reserva
- **Ideia:** aprovação de pacote fiscal redistribui valor entre setores (Wagner-Zeckhauser-Ziegler); teto da dívida como robustness (paradoxo do TLT: flight-to-quality para dentro dos próprios Treasuries — sinal do TLT é empírico). Shutdown ficou FORA (sem efeito documentado em equities). Nasce como **reserva** (β mais frágil do lote — poucos episódios).
- **Polymarket:** **evento primário = aprovação de legislação tributária** (ex.: família OBBB 2025, "passa até X?"); **robustness = teto da dívida / X-date** (2023 e 2025). Binários, midpoint bid/ask.
- **O que o Paulo precisa levantar:** mercados OBBB 2025 e teto/X-date no CLOB — cobertura, volume, critério de resolução, bid/ask histórico.

## 1.3 Camada tática reformulada (overlay sobre o BL; 3 candidatas, entrada pendente de reunião)

Rodam **em paralelo ao BL** (não são views): `w_final = w_bl + Σ dw`. Gatilho de calendário, sinal lento — não sofrem com a granularidade ~12h do poly. Dono: Felipe.

### Tática 1.3 — Prêmio de anúncios macro
- **Ideia:** dia de anúncio (FOMC, CPI) paga prêmio (Savor-Wilson); o poly mede a incerteza na véspera (**entropia da PMF**) e dimensiona a posição long SPY vs caixa. Sempre ligada, modulada. É o único sinal do projeto que lê a **incerteza** (formato da PMF), não o nível.
- **Dados:** os mesmos mercados de PMF das views 2.2/2.3 (custo de dado zero); **calendário de releases do CPI (dado novo)**; datas de FOMC (já pendência da 2.3). Snapshot do poly ≤ fechamento de D−1.

### Tática — Drift pós-FOMC
- **Ideia:** após o anúncio, ações e Treasuries continuam andando na direção da surpresa realizada por semanas (Neuhierl-Weber; Brooks-Katz-Lustig). Dois livros: SPY (D→D+15 úteis) e TLT (D→D+50 úteis, truncado no FOMC seguinte, ~42 dias típicos).
- **Dados:** nenhum novo (ZQ na véspera + decisão publicada + calendário FOMC). ⚠️ Mas impõe o requisito mais pesado do backtest: **marcação diária contínua** das posições (o livro TLT cobre boa parte do ano).

### Tática — Gap de fim de semana
- **Ideia:** o poly opera 24/7; a bolsa fecha ~65h. Se p andou no fim de semana, entra na abertura de segunda na direção dos β **das views ativas** (não estima nada próprio) e desmonta no fechamento do mesmo dia. `dw = λ × Σ β_view × Δp_fds`.
- **Dados:** **snapshots de fim de semana do poly** (grid de 12h, último ≤ abertura de segunda); **preço de ABERTURA de segunda dos ETFs** (yfinance tem — dado novo pequeno). Feriados prolongados contam como fim de semana.

## 1.4 Colinha consolidada de dados (Paulo)

| Consumidor | Mercado do Polymarket | Tipo | Outras fontes | Observação crítica |
|---|---|---|---|---|
| View 2.2 | CPI mensal (buckets) | PMF | FRED `T10YIE` | cobertura ~18 meses; bucket aberto; FL na cauda direita |
| View 2.3 | Decisão FOMC por reunião (buckets) | PMF | ZQ yfinance (mês posterior); datas FOMC + ΔFF no dia | do ZQ sai esperança em bps, não probabilidade |
| View 2.4 | Presidencial 2024, vencedor, p(Trump); 2022 robustness | Binário | — | **bid/ask histórico = condição da view**; reportar dias sem trade |
| View 3.1 | Recessão EUA (preferência: resolução técnica GDP) | Binário | FRED `DGS10`/`DTB3`; coefs do probit publicado | FL relevante (p baixa); checar critério de resolução |
| View B | Cortes acumulados / taxa em dez (buckets) | PMF | ZQ **de dezembro** (contrato fixo) | bucket aberto "5+ cortes"; rolagem anual |
| View C | Irã 2025 (primário); Rússia×Ucrânia (robustness) | Binário | — | FL relevante (p ~0,1–0,4); rolagem entre deadlines |
| View E | Tarifas EUA×China (primário); recíprocas (robustness) | Binário | — | indicar binário-mãe por período (liquidez) |
| View G | OBBB 2025 (primário); teto/X-date 2023–25 (robustness) | Binário | — | reserva; registrar sinal do TLT no teto |
| Tática 1.3 | Reusa PMFs de 2.2/2.3 | PMF | Calendário de releases do CPI (novo) | snapshot D−1 sem lookahead |
| Tática drift | — (usa ZQ + decisão publicada) | — | ZQ D−1; calendário FOMC | marcação diária contínua no backtest |
| Tática gap | Reusa mercados das views ativas | Binário/PMF | Abertura de segunda dos ETFs | snapshots de fim de semana do poly |

**Transversal a tudo:** bid/ask histórico no CLOB (`/prices-history` — checar o que ele entrega) e ⚠️ **critério de resolução dos mercados de bucket** (terminal vs one-touch): mercados de commodities do poly podem resolver por one-touch, e a receita "média da PMF" não transfere sem checar isso.

---

# PARTE 2 — Pendências de vocês (o Felipe não entra nessas decisões)

## PAULO — dados

**Condição crítica (trava 2.4/3.1/C/E/G e a decisão 9):**
1. **Fonte do poly com bid/ask histórico no CLOB.** O `poly_preprocessing.midpoint_price` precisa de bid e ask crus. ⚠️ Se a fonte final só der último trade, o midpoint some e as views defasadas perdem a condição de fechamento. (O Felipe assumiu alinhar essa fonte com você — mas o levantamento do que a API entrega é seu.)

**Cobertura de mercados no CLOB (para cada um: existe? desde quando? volume? critério de resolução? bid/ask?):**
2. CPI (buckets) e FOMC (buckets) — views 2.2/2.3.
3. Recessão (preferência: resolução técnica GDP) — view 3.1.
4. Presidencial 2024, binário p(Trump) (+ 2022) — view 2.4.
5. Tarifas EUA×China + recíprocas — condição da E.
6. Fiscal OBBB + teto/X-date — condição da G.
7. Geopolítica Irã 2025 + Rússia×Ucrânia — condição da C.
8. ⚠️ **Critério de resolução dos mercados de bucket (terminal vs one-touch)** — decide se a receita "média da PMF" vale.

**Outras fontes a incluir no pipeline:**
9. FRED: `T10YIE` (2.2); `DGS10` e `DTB3` (3.1).
10. ZQ (Fed Funds futures) no yfinance — contrato próximo (2.3) e contrato de dezembro (B). A conversão preço → E_FF em bps (de qual taxa corrente subtrair a implícita `100 − preço`) fica a montante da view — **acordar com o Felipe quando o dado chegar**.
11. Coeficientes exatos do probit (Estrella-Mishkin / NY Fed) — referência a fixar antes de rodar a 3.1.

**Requisitos de engenharia do backtest:**
12. **Marcação diária contínua** das posições táticas (o livro TLT do drift ≈ 42 dias úteis por reunião — bem mais pesado que os ~20 dias/ano da 1.3).
13. Calendário de releases do CPI (dado novo).
14. Preço de **abertura de segunda** dos ETFs (gap de fim de semana).
15. Snapshots de fim de semana do poly.

## LIA — Ω reativo + relatório

1. **Decisão 6 🟡 — forma funcional do Ω reativo:** como volume, estabilidade, convergência e proximidade de evento viram um número de confiança; versão mínima do mock vs completa. **Delegada a você (reunião 08/07)** — seu protocolo de calibração proposto já está incorporado na seção 6 de `Decisoes_pendentes.md` (baseline He-Litterman escalado por confiança c; forma multiplicativa com volume como veto; parâmetros por teste de monotonicidade no histórico). ⚠️ **Trava a integração:** view ativa sem Ω falha alto de propósito (`bl_integration.py` não inventa confiança). É a decisão aberta mais urgente do seu lado. Dependência: **volume histórico do poly** (confirmar com o Paulo).
2. **Validar o campo `diagnostics` do `ViewResult`** como insumo do Ω — o formato está deliberadamente não travado esperando você (cada view já entrega um dict com seus diagnósticos; diga o que falta/sobra).
3. **Nota de interação Ω ↔ camada tática:** a mesma incerteza entra com sinais opostos nos dois módulos (na tática 1.3, incerteza↑ = prêmio↑ = compra; no Ω, incerteza↑ = confiança↓ = encolhe a view). Não é contradição (prêmio de risco ≠ qualidade de sinal), mas precisa estar documentado para o Ω não neutralizar a tática por construção. Hoje **4 módulos leem o calendário FOMC**: view 2.3 (antes), tática 1.3 (no dia), drift (depois), gap (nas segundas).
4. **Relatório:** SWZ (Snowberg-Wolfers-Zitzewitz) como guarda-chuva metodológico do bridge probabilidade→Q — achado da pesquisa para embasar o relatório.
5. Lembrete de semântica que afeta o Ω: **liquidez baixa não desliga view** (papel do Ω) e **view desativada = Ω → ∞** (BL no prior).

## CALIBRAÇÃO (decisão de reunião — sem dono fixo; vocês dois participam)

**Decisão 11 🔴 — pré-processamento das probabilidades** (`poly_preprocessing.py`; os stubs levantam `NotImplementedError` de propósito — **trava TODAS as views com dado real**):
- **(11a) Forma da correção do favorite-longshot bias:** calibração própria sobre mercados resolvidos do poly vs curva da literatura (Page & Clemen) vs sem correção no v1 (aceitar o viés e documentar). Relevância máxima na 3.1 (p baixa), cauda direita na 2.2, segunda ordem na 2.4.
- **(11b) Valor do bucket aberto** das PMFs (ex. "≤3.6%" → que número entra na média?): ponto médio extrapolado vs valor fixo vs truncar no limite.

## Avisos do Felipe (mudanças no branch Felipe — valem após merge)

- Decisão 10: camada tática original adiada; camada reformulada realocada ao Felipe (módulo da Lia no `CLAUDE.md` reduzido a "Ω reativo · Relatório").
- Arquivos `.md` deletados: Cronograma, Mapa de camadas, FELIPE_arquitetura, Ideias_consolidadas (conteúdo vivo migrou para `Decisoes_pendentes.md`, `Informações_uteis/views/` e `táticas/`).
- Felipe assumiu alinhar diretamente com o Paulo a fonte do poly com bid/ask.
