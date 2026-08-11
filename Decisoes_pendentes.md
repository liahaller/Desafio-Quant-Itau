# Decisões pendentes — mock do projeto

Decisões de implementação que faltam fechar antes/durante o mock. À medida que resolvemos, registramos a decisão na própria seção (status: 🔴 aberta · 🟡 em discussão · 🟢 fechada).

---

## 1. Universo de ativos e fonte de preços 🟢
Lista fechada de instrumentos negociáveis que formam o vetor de pesos.

**Decisão:**

Critério de divisão por **horizonte** (não por tamanho de ativo):
- **Camada estrutural** (posições lentas) → setores + classes de ativos.
- **Camada tática** (trades rápidos) → ações individuais, definidas depois.

Universo da camada estrutural (cobre as 5 views: Fed 2.3, inflação 2.2, eleitoral 2.4, momentum 1.2, sentimento macro 3.1):

| Ticker | O que é | Views que atende |
|--------|---------|------------------|
| XLK | Tecnologia | Fed (long-duration), eleitoral, momentum |
| XLU | Utilities (defensivo) | Fed (defensivo/duration), eleitoral |
| XLP | Consumo defensivo | Fed (defensivo) |
| XLF | Financeiro | Fed (sensível a juros), eleitoral |
| XLE | Energia | Eleitoral/regulatória |
| XLV | Saúde | Eleitoral/regulatória |
| TIP | Títulos protegidos contra inflação (TIPS) | Inflação |
| TLT | Treasuries nominais longos | Inflação (par), Fed |
| SPY | Ações EUA amplo | Âncora de mercado (prior do BL), macro |

- Granularidade: setores + classes de ativos (sem ação individual na estrutural).
- Treasuries nominais: **TLT** (longos, mais sensível a juros — amplifica as views de juros).
- Fonte de preços: yfinance · frequência diária.

**Fechado:** universo restrito aos EUA. Sem proxy de Brasil (EWZ); a view 3.1 opera apenas sobre ativos americanos.

## 2. Acesso ao Polymarket 🟢
De onde vêm os dados do poly no mock: API real · snapshot histórico · dados sintéticos.

**Decisão:** API CLOB oficial do Polymarket (endpoint `/prices-history`).

## 3. Mapeamento cenário → ativos (Camada 2) 🔴
Como estimar a matriz de retornos condicionais. Regredir retorno do ativo contra o quê (mudança de probabilidade? dummy de resolução?).

**Decisão:** _(a registrar)_

## 4. Tradução probabilidade → vetor Q 🔴
Como converter probabilidade do poly em retorno esperado (unidade que o BL exige). Ponte entre "65% de corte" e um número de retorno por ativo.

**Decisão:** _(a registrar)_

## 5. Definição operacional de "surpresa" (PEAD, 1.1) 🔴
Fórmula da surpresa. `1 − prob_atribuída`? Contínua ou por threshold?

**Decisão:** _(a registrar)_

## 6. Forma funcional do Ω reativo 🟡
Como volume, estabilidade, convergência e proximidade de evento viram um número de confiança. Versão mínima para o mock vs. versão completa.

**Decisão:** _(a registrar — delegada à Lia)_

**Contexto (registrado em 08/07/2026):**
- A reunião do grupo delegou esta decisão à Lia.
- Critério proposto para fechar (protocolo de calibração, em vez de escolha
  arbitrária):
  1. **O que a matemática já determina:** a confiança `c ∈ (0,1]` escala o
     baseline de He-Litterman — `Omega_ii = diag(P·tau·Sigma·P')_ii / c` —
     de modo que `c = 1` recupera o BL clássico e `c → 0` recolhe ao prior.
  2. **O que a semântica determina:** estrutura multiplicativa
     `c = portao(volume) × f(estabilidade) × g(proximidade)` — volume é
     veto (mercado sem liquidez invalida o preço; soma ponderada permitiria
     compensação indevida); convergência fica fora do v1 (Decisão 7).
  3. **O que o dado decide:** janela da estabilidade, forma/horizonte do
     decaimento de proximidade e threshold de volume saem de teste de
     monotonicidade no histórico — faixas de confiança maiores devem
     apresentar erro realizado da probabilidade menor; empates são
     resolvidos pela forma com menos parâmetros.
- Dependências: histórico do Polymarket via pipeline do Paulo (Decisão 2:
  `/prices-history` entrega preço; disponibilidade de **volume** a
  confirmar com o Paulo).
- **Levantamento de API (20/07/2026, Lia):** não existe endpoint pronto
  de volume histórico. `/prices-history` (CLOB) só devolve `{t, p}` —
  confirma a observação do Felipe em `Para_Paulo_e_Lia.md`. A Gamma API
  (`/markets`, `/events`) traz `volume`/`volume_24hr`, mas só o agregado
  no momento da consulta, não uma série temporal. O caminho viável é a
  **Data API** (`data-api.polymarket.com`): `/trades` (ou `/activity`)
  devolve trades individuais com `timestamp`, `price`, `size`
  (`usdcSize` em `/activity`) — dá pra reconstruir volume diário
  agregando por janela de tempo, mas não vem pronto; é trabalho de
  pipeline (paginação, filtro por `condition_id`/token, bucketização).
  **Ainda não implementado.** Continua dependendo do Paulo construir
  essa agregação antes de a calibração poder rodar com dado real —
  **isso não fecha a decisão**, só torna a dependência concreta.
- **Especificação de interface e insumos (05/08/2026, Lia):** resposta às
  perguntas do Felipe em `Dump/trocas/Pergunta_Lia_omega_volume.md`
  (branch Felipe), registrada em `RESPOSTA_Pergunta_Lia_omega_volume.md`.
  Especifica *entradas e saída* do Ω — **não fecha a forma funcional**,
  que continua dependendo da calibração com dado real:
  - **Volume (destrava o G5 do Paulo):** série no tempo em passo de 12h,
    com `notional_usd` e `n_trades` por slot, mais `t_cobertura_min` por
    mercado (trade mais antigo alcançado dentro do cap de 20k do
    `/trades`). Antes desse timestamp, volume = NaN, nunca 0. Escopo:
    mercados das views ativas (2.2, 2.3, B). Total lifetime recusado:
    é lookahead no backtest (inclui volume posterior à data da decisão)
    e é constante no tempo, o que desliga a reatividade do Ω.
  - **`diagnostics` das views:** `serie_janela` (crua) + `n_pontos_janela`,
    `n_slots_esperados_janela`, `janela_slots`, `idade_ultimo_ponto_h`,
    `dp_variacao_janela` (desvio-padrão das *diferenças*), `dias_ate_evento`,
    `soma_faixas` (cru). Convenção: campo desconhecido = NaN, nunca 0.
  - **Saída do Ω:** vetor `c` (multiplicador de incerteza, na convenção do
    Felipe: >1 = menos confiança) + máscara `ativa` (bool). Veto de
    liquidez remove a view de P/Q em vez de virar `c` grande. Nota: a
    convenção de 08/07 registrada acima é a inversa (`c ∈ (0,1]`, maior =
    mais confiança) — `c_felipe = 1/c_lia`. A régua implica `c_felipe ≥ 1`
    sempre: o fallback He-Litterman é o teto de confiança e o Ω só tira
    peso, nunca adiciona.
  - **Quarto ingrediente candidato:** `score_coerencia = −|soma_faixas − 1|`,
    do achado do Felipe de que as faixas dos mercados de buckets não somam
    1 (92,3%–132,5% no mercado de cortes do Fed). Entra na grade de
    calibração; só entra na fórmula se passar o teste de monotonicidade.
  - **δ e teto de alavancagem:** aceita a proposta do Felipe de fechar
    dimensionamento de risco numa conversa só, com correção de alvo — δ =
    3,0 foi medido, não é parâmetro livre; o que precisa fechar junto com
    a escala do `c` é o **teto de alavancagem**, porque hoje o teto faz o
    trabalho do Ω. Ordem proposta: entra o `c` → mede-se Σ|w| de novo →
    só então se decide o teto. **Em aberto, para reunião.**

### 6a. Colapso PMF multi-bucket → `p` para o `score_estabilidade` 🟢

Levantada pelo Felipe (07/08/2026): `dp_variacao_janela` foi definido como
desvio-padrão das diferenças `p_t − p_{t−1}`, mas em mercado multi-bucket
não existe um `p` — a leitura de um slot é um vetor de 5 a 9 faixas. As
**três views ativas do v1 (2.2, 2.3, B) são todas multi-bucket**, então sem
essa regra o `score_estabilidade` fica sem insumo em todas elas.

**Resolvido quanto ao lugar (05→07/08, Lia + Felipe):** o colapso é
calculado **do lado da Lia**, a partir de `serie_janela` (crua, já
entregue completa). `dp_variacao_janela` fica `NaN` de propósito no
`diagnostics`. Motivo: é a mesma classe de transformação do `soma_faixas`,
e a regra é candidata à calibração — fixá-la no módulo do Felipe faria
cada forma testada virar uma ida e volta.

**Aberto quanto à forma funcional** — decide o teste de monotonicidade,
como nos outros ingredientes; empate resolve pela forma com menos
parâmetros (= **a**):
- **(a)** variação total entre PMFs consecutivas, `0,5·Σ_b |p_{t,b} −
  p_{t−1,b}|`. Sem parâmetro livre e degenera exatamente na definição
  original quando há 2 buckets.
- **(b)** desvio-padrão das diferenças do valor esperado `E_t = Σ_b p_b·x_b`.
  Mede movimento na grandeza que o `Q` consome. ⚠️ Herda a decisão
  provisória do **balde aberto** (ponto médio extrapolado, maratona de
  04/08): se (b) vencer, revisão daquela decisão obriga a recalibrar.

**Premissa fixada em ambas:** a PMF é **renormalizada** (`p_b/Σ_b p_b`)
antes do colapso. As PMFs cruas não somam 1 (92,3%–132,5% no mercado de
cortes do Fed); sem renormalizar, o colapso mistura movimento de opinião
com desarranjo do livro e a régua multiplicativa puniria a mesma coisa
duas vezes (`score_estabilidade` e `score_coerencia` ficariam
correlacionados, parecendo confirmação mútua no teste). O desarranjo fica
inteiramente com o `soma_faixas`.

**Implementação (escopo da Lia, sem impacto de interface):** só pares
adjacentes (Δt = 1 slot de 12h); sem normalizar pela distância temporal
(embutiria premissa de passeio aleatório) — o buraco já custa confiança
via `n_slots_esperados − n_pontos`.

### 6b. Consequências do achado "a série é midpoint, não último trade" (07/08/2026)

Medido pelo Paulo e confirmado pelo Felipe: `/prices-history` com
`fidelity=720` entrega **midpoint amostrado no instante t** (grade 00:00 e
12:00 UTC), não agregado do intervalo nem último trade. Duas consequências
para o Ω, ambas de escopo da Lia:

- **Sem lookahead na leitura:** a execução é na abertura de NY (13:30/14:30
  UTC), 1,5–2,5 h depois do ponto das 12:00 UTC. `idade_ultimo_ponto_h = 0.0`
  não é lookahead. Verificação encerrada, sem ação.
- **⚠️ O portão de volume vira pré-condição do `score_estabilidade`, não um
  ingrediente ao lado dele.** A série de preço nunca fica vazia por falta de
  negociação: mercado sem trade continua reportando midpoint, e midpoint
  parado é lido como **estabilidade perfeita**. Sem o portão, o ingrediente
  daria confiança máxima ao mercado mais ilíquido — inversão sistemática de
  sinal, não ruído. **Revoga** o registro de 05/08 ("se o G5 atrasar, entregar
  o `c` sem o portão de volume"): sem volume, o certo seria entregar sem o
  ingrediente de estabilidade, não sem o portão.

**Tratamento do volume ausente (G5, resposta ao Paulo em 07/08):**
truncamento do cap de 20k = `NaN` (ignorância nossa; **não veta**);
pré-primeiro-trade = `0` (fato do mercado, ninguém negociou; **veta**). O
segundo caso é justamente aquele em que o preço é o midpoint semeado na
criação — valor inicial do book, não probabilidade negociada.

### 6c. Fronteira entre a cascata do Felipe e o `score_coerencia` 🟡

O Felipe fechou "PMF com soma crua < 0,9 desativa a view no dia" (D12 do
branch `Felipe`), e o `score_coerencia` da Lia pune a mesma grandeza. **Não
é dupla contagem porque os regimes são disjuntos:** soma < 0,9 → a view é
desativada e nem chega ao Ω (não existe `c` para ela); soma ≥ 0,9 → o piso
não age e só o gradiente age. Diferente do caso do 6a, onde os dois agiriam
no mesmo slot dentro do mesmo produto.

**Compromisso que sustenta a separação, registrado dos dois lados:** o piso
do Felipe não vira rampa, e o `score_coerencia` não ganha portão binário —
o único portão binário da régua continua sendo o volume. Se o piso virar
gradiente, isto passa a ser dupla contagem.

Assimetria útil: o corte do Felipe é só por baixo; `−|soma − 1|` é
bilateral. Soma 1,32 (medida no mercado de cortes do Fed) passa pela
cascata e só o score pega.

**Ressalva:** na janela do v1 a soma da 2.3 fica entre 0,969 e 1,013 —
faixa estreita. O ingrediente pode cair no teste de monotonicidade por
**falta de poder discriminante**, não por estar errado; se cair, a
distinção vai registrada em vez de virar "o desarranjo não prevê erro".

### 6d. Disciplina de calibração — forma × nível 🟡

Proposta da Lia (07/08), para a reunião. Com o backtest agora positivo
(+2,68 pp de excesso, teto no tilt), um `c` global alto passa a ser
**custo**, não conserto — o que cria risco de overfit em dois passos:
calibrar o `c`, ajustar o teto olhando o resultado, e reajustar o `c`
olhando o resultado de novo. Cada passo isolado parece razoável e ninguém
vê o conjunto. Trava proposta:

1. a **forma** do `c` sai do teste de monotonicidade (sobre **erro
   realizado da probabilidade**, não sobre retorno da carteira) e **não é
   revisitada por resultado de backtest**;
2. o **nível** global é escolhido **uma vez**, na conversa de risco, junto
   com o teto de alavancagem;
3. se o resultado depois desagradar, muda-se o teto, não a régua.

### 6e. Tratamento de buracos e janela da calibração (07/08/2026)

Resposta à correção do Felipe (`RESPOSTA3_Lia_portao_renormalizacao`): a
`serie_janela` crua **não** reproduz o `p` que a view consome, porque entre
as duas rodam `carry_missing` (D6.1) e `daily_preopen`.

- **`ffill` recusado.** `carry_missing` repete a última leitura, e leitura
  repetida entra na conta como **variação zero** — quanto mais esburacado o
  mercado, mais estável ele pareceria. Mesma inversão de sinal do midpoint
  (6b), por outro caminho, e pior que ruído: o `ffill` é determinístico e só
  erra num sentido (nunca aumenta a variação medida), o que é viés e não
  imprecisão. O teste de monotonicidade não distingue viés de sinal.
- **Regra adotada:** slot com qualquer faixa sem leitura **não entra** no
  cálculo de variação (e o par deixa de ser adjacente, caindo pela regra já
  registrada em 6a). Não contradiz a D6.1 — não há massa de faixa ausente
  sendo espalhada, porque a linha não é usada. O buraco segue custando
  confiança pelo canal próprio (`n_slots_esperados − n_pontos`): cada
  defeito penalizado uma vez, mesma disciplina do 6c. Registra-se o nº de
  pares sobreviventes junto do score.
- **Princípio de fundo:** o score **não deve** reproduzir o `p` da view. O
  `p` tratado é o insumo do modelo; o score mede se o mercado que gerou esse
  insumo estava funcionando. Medir sobre a série tratada seria medir a
  estabilidade do tratamento, que é suave por construção. Por isso também
  foi dispensada a oferta de um campo `serie_janela_tratada`.
- **Grade temporal:** 12 h ("variação entre leituras") e 24 h ("variação
  entre decisões", slot das 12:00 UTC) entram como **dimensão da grade** —
  2 formas × 2 grades, decide a monotonicidade.
- **Janela da calibração — dias degenerados.** Em produção o recorte é
  automático (soma < 0,9 mata o dia, sem view não há `c`). **Na calibração
  eles entram:** o alvo do teste é o erro realizado da probabilidade, que
  existe mesmo quando a view não rodou, e livro degenerado é exatamente a
  condição que deve produzir score baixo — o artefato é o sinal. Com o
  número do Felipe (27 dias degenerados de 801, 24 com soma < 0,5, **todos
  fora da janela do v1**), a calibração roda sobre a **história completa dos
  mercados (801 dias)**, não sobre os 374 pregões do backtest. Legítimo pela
  trava do 6d: a forma sai de teste sobre erro de probabilidade, não sobre
  retorno de carteira. É o que dá poder discriminante ao `score_coerencia` —
  a faixa estreita da 2.3 (0,969–1,013) é propriedade do recorte, não do
  mercado.
- **`dp_variacao_janela` não é consumido nem no caso binário.** A variação
  total degenera em `|p_t − p_{t−1}|` com duas faixas, então o número seria
  o mesmo — mas calculá-lo do lado da Lia mantém um único caminho (mesmo
  tratamento de linha incompleta, mesma grade). Duas estimativas da mesma
  quantidade no sistema é a classe de problema já fechada no dict.

**Delimitação do 6a:** fechado quanto ao **lugar**; a **forma** segue aberta
(quatro candidatas: 2 formas × 2 grades). ✅ **Forma fechada em 09/08 pela
dona** — ver 6g.

### Nota de encanamento — numeração divergente entre branches

A numeração de `Decisoes_pendentes.md` diverge **a partir da 8** nos três
branches. Convenção adotada (07/08): citar sempre com o branch — "D12 do
`Paulo`", "D12 do `Felipe`" — nunca "D12" sozinho. A tabela de
correspondência está no topo do arquivo no branch `Felipe`.

## 7. Convergência entre fontes (polls, casas de aposta) 🟡
Se entra no Ω já no v1 ou fica como stub (adiciona dependências de dados).

**Decisão:** fora do v1 — fica como stub. Reavaliar depois se entra em versão futura (em aberto).

## 8. Passo final do otimizador: qual Σ e quais restrições 🔴
Surgiu na implementação do esqueleto BL (`src/bl_optimizer.py`).

**Contexto:** o passo `w = inv(δΣ)μ` aceita duas covariâncias:
- **Σ amostral** — pesos respondem só à mudança na média; com confiança zero volta exatamente a `w_mkt`.
- **Σ_bl posterior (He & Litterman)** — incorpora a incerteza das views; com confiança zero os pesos encolhem para `w_mkt/(1+τ)` (sobra caixa implícito).

Também em aberto: restrições nos pesos (long-only? soma 1? limite de alavancagem?). O esqueleto atual é irrestrito (BL padrão) e deixa a escolha do Σ para o chamador.

**Decisão:** _(a registrar)_

## 9. Matriz de relação ativos × mercados do Polymarket (insumo candidato à Camada 2) 🟡
Parâmetros em aberto de `lia/matriz_relacao.py` (distance correlation em janela móvel, ativos × mercados × tempo).

**Contexto (registrado em 20/07/2026):** construída na sessão de 06/07 como infraestrutura da camada tática antiga — a Decisão 10 realocou essa camada pro Felipe, com desenho que não reaproveita a matriz. Retomada agora com objetivo mais estreito: usar a matriz como evidência exploratória de "qual mercado do Polymarket tem mais relação com qual ativo", pra apoiar a Decisão 3 (mapeamento cenário→ativo, módulo do Felipe) — não substitui a decisão dele, só informa.

**Em aberto:**
- `janela` (nº de períodos por janela móvel): sem default de propósito, o código já impõe isso — vem de decisão registrada, não de escolha arbitrária.
- `passo`: default 1 no código, não confirmado se é o desejado.
- Série do Polymarket a usar: variação de probabilidade (Δp) ou nível (p)?

Enquanto esses três não fecham, qualquer resultado da matriz é exploratório/provisório (testado com múltiplas janelas candidatas), não uma calibração final.

**Decisão:** _(a registrar)_

---

**Próximo passo:** voltar para a Decisão 1.

### 6f. Primeira rodada de calibração com dado real (09/08/2026) 🟡

Rodada por `lia/rodar_calibracao.py` sobre as 18 reuniões do FOMC
(`polymarket_fed_reunioes.parquet`, `origin/Paulo` em `033e0d8`): 3.905
slots na grade de 12h, 1.952 na de 24h. **Dois ingredientes**, não quatro —
o portão de volume ficou de fora porque o G5 não alcança os mercados do
FOMC (ver `PEDIDO_Paulo_G5_fomc.md`), e sem portão o `score_estabilidade`
não é interpretável (6b).

Resultado, estável nas 8 combinações (2 grades × 2 alvos × 2 horizontes):

| Ingrediente | spearman | monotônica | Leitura |
|---|---|---|---|
| estabilidade (variação total) | −0,31 a −0,40 | ✅ | melhor candidata em **todos** os cortes |
| estabilidade (\|ΔE\|) | −0,29 a −0,36 | ✅ | perde para a variação total em todos |
| coerência | −0,15 a −0,18 | ✅ | mais fraco, sinal correto, consistente |
| proximidade | **+0,09 a +0,22** | ✗ | **reprovada, com o sinal invertido** |

**Decide a 6a a favor da candidata (a), variação total:** vence a (b) em
todos os cortes, tem menos parâmetros e não depende do balde aberto — os
três critérios apontam para o mesmo lado, sem precisar de desempate.
**A confirmar pela dona antes de virar decisão fechada.**

**Achado que contraria o protocolo de 08/07:** a proximidade tem o sinal
oposto ao suposto. Longe da reunião o mercado se move **mais**, não menos —
a probabilidade se cristaliza à medida que a decisão chega. Duas saídas, em
aberto: (i) o ingrediente sai da régua, pelo protocolo (candidata que
reprova cai); (ii) entra com o sinal invertido, como hipótese nova e
declarada — proximidade do evento passa a **somar** confiança. Escolher o
sinal depois de ver o dado exige cuidado com o 6d; a favor de (ii) está o
fato de haver mecanismo econômico, não só ajuste.

⚠️ **Ressalva sobre a estabilidade nesta rodada:** o spearman de −0,40 pode
estar inflado pelo próprio viés que a 6b descreve. Sem o portão, mercado
ilíquido entra como "estável" (midpoint congelado) **e** com erro futuro
baixo (o midpoint continua congelado) — o teste confirmaria o ingrediente
pelo artefato. Só o G5 estendido separa as duas explicações. Enquanto isso,
o número é provisório e não sustenta sozinho a entrada da estabilidade na
régua.

### 6g. Segunda calibração — view 2.2 (CPI), com portão. Régua fechada (09/08/2026) 🟢

Rodada por `lia/rodar_calibracao_cpi.py` sobre os 19 mercados-mês de CPI
(`clob_exploracao` + `g5_volume_no_tempo.csv`, `origin/Paulo`): 1.198 slots na
grade de 12h, 18 eventos. **É a primeira rodada com os quatro ingredientes**:
o G5 casa 111/111 com os mercados da 2.2 (chave por nome exato de arquivo),
6.360 slots de preço com volume, nenhum truncamento do cap de 20k. O bloqueio
do `PEDIDO_Paulo_G5_fomc.md` era só da família FOMC — o pedido segue de pé
para tirar a 2.3 do provisório, mas deixou de bloquear a entrega.

| Ingrediente | spearman (12h) | monotônica | Leitura |
|---|---|---|---|
| estabilidade (variação total, j5) | −0,46 | ✅ | melhor candidata, de novo |
| estabilidade (\|ΔE\|, j5) | −0,42 | ✅ | perde no alvo dela, ganha no próprio |
| coerência | −0,21 a −0,31 | ✅ | **mais forte que no FOMC** (−0,15/−0,18) |
| portão de volume (qualquer threshold) | −0,03 a +0,14 | — | reprovado como score |
| proximidade | +0,10 a +0,37 | ✗ | **reprovada de novo, sinal invertido** |

**Grade e janela que o dado escolheu:** 12h (vence 24h em todos os cortes) e
**5 variações** (vence 10 e 20 em todos os cortes das duas views). Atenção ao
off-by-one: 5 variações = 6 slots, então `janela_slots = 6` no `diagnostics`.

**O achado que destrava a entrega — a estabilidade não era artefato.** A
ressalva da 6f (o −0,40 do FOMC podendo ser o viés do midpoint da 6b) foi
testada e **cai**:
- Veto estrito (volume > 0, agregado por soma): spearman −0,4615 → −0,4531.
  Delta +0,008, ao custo de 6% da amostra.
- Diagnóstico direto: variação exatamente zero em **4,4%** dos pares sem
  negociação contra **1,2%** com negociação — o congelamento existe (3,7×) mas
  é raro, e o erro futuro médio é quase igual (0,032 sem × 0,035 com).
- Threshold calibrado (q10/q25/q50) só **piora** (delta até +0,14) e come
  amostra; agregar por `minimo` entre faixas veta 47% dos slots de 12h,
  porque é comum uma faixa não negociar em meio dia.

**Quatro decisões fechadas pela dona nesta sessão:**

1. **6a a favor da candidata (a), variação total.** ⚠️ Mudança de fundamento:
   no FOMC ela vencia em todos os cortes; no CPI as duas **empatam** — cada
   uma vence no alvo medido por ela mesma (circularidade do alvo). O
   desempate passa a ser o do protocolo: menos parâmetros e independência do
   balde aberto. O relatório registra "empate resolvido por parcimônia", não
   "vitória estatística".
2. **Portão de volume: veto no slot sem NENHUMA negociação, agregado por
   soma das faixas.** Sem threshold calibrado — o dado não sustenta nenhum, e
   o veto em zero é gratuito. Preserva a semântica da 6b e a separação
   `0` × `NaN` combinada com o Paulo em 07/08 (`NaN` não veta).
3. **Proximidade sai da régua.** Reprovou nas duas views, 16 cortes, sempre
   com o mesmo sinal invertido. Pelo protocolo de 08/07, candidata que
   reprova cai; entrar com o sinal trocado seria escolher sinal depois de ver
   o dado, que é o que a trava da 6d evita. O achado (**a probabilidade se
   cristaliza à medida que a decisão chega**) vai ao relatório como
   resultado, e fica como candidata a versão futura.
4. **Normalização score → `c`: produto de penalidades.**
   ```
   c = ( (1 + var_media) · (1 + |soma_faixas − 1|) ) ** nivel
   ```
   Cada defeito multiplica a incerteza por (1 + tamanho do defeito). `c ≥ 1`
   por construção — sem piso, teto ou truncamento, e sem divisão por zero. É
   transformação monótona dos scores calibrados, então o teste de
   monotonicidade continua valendo (ele só enxerga ordem).
   **A forma simétrica `(1 − x)` foi medida e descartada:** o fator de
   coerência fica **negativo em 7 de 1.139 linhas** do CPI (a soma do livro
   vai de 0,754 a 2,725, mediana 1,017), e consertar exigiria truncar em
   zero — um segundo portão binário, que o compromisso da 6c com o Felipe
   proíbe.

**Régua de produção, implementada em `lia/omega.py`** (55 testes na suíte da
Lia). Medido no dado real, através do `diagnostics_qualidade` do pipeline —
601 decisões da 2.2: 90,3% ativas, 37 inativas por veto de volume, 21 por
ausência de par adjacente completo. Com `nivel = 1`: `c` de 1,0016 a 2,7653,
mediana 1,0495, p95 1,2426.

**Regra nova, de escopo da Lia, registrada porque afeta o que o Felipe
recebe:** view sem nenhum par adjacente completo na janela sai como
**inativa**, não com `c = 1`. Sem par não há como qualificar a leitura, e
entregar confiança máxima onde nada foi medido é o pior erro disponível. Não
é o portão binário que a 6c proíbe — não é o `score_coerencia` vetando, é
ausência de medição, mesma classe do veto de liquidez.

**Continua aberto (é o que vai à reunião, pela 6d):** o **nível global** e o
**teto de alavancagem**, fechados juntos e uma vez só. Insumo para a
conversa: com `nivel = 1` a régua é suave (mediana 1,05), então o `c` cru
quase não modula — `nivel` é o botão, e `nivel = 0` devolve He-Litterman
puro. A forma acima **não** é revisitada por resultado de backtest.

### 6h. Robustez da calibração — faixas e alvo por desfecho (09/08/2026) 🟡

Rodada por `lia/rodar_robustez.py` sobre a view 2.3 (18 reuniões). Fecha o
item 4 da lista de trabalho da Lia. **Não altera a régua da 6g** — as duas
verificações a confirmam.

**1. Nº de faixas (2, 3, 4, 5).** O `spearman` é **idêntico** nas quatro, e
isso é identidade, não robustez: ele é calculado sobre postos e as faixas só
servem à leitura de monotonicidade. Registrado explicitamente no script e no
relatório para não apresentar tautologia como resultado. O que varia é a
**flag de monotonicidade**, e ela se mantém nas quatro contagens para os dois
ingredientes da régua nas configurações escolhidas; oscila só em janela 20 e
na grade 24h, ambas já descartadas por outro critério.

**2. Alvo por desfecho, independente das candidatas.** A variação futura é
alvo circular para comparar as duas formas de colapso. O alvo alternativo é a
massa que o mercado alocou **fora do bucket que resolveu** — `1 − p_vencedor`
sobre a PMF renormalizada, que é a mesma distância de variação total usada no
resto, medida contra o resultado em vez de contra a leitura seguinte
(`erro_vs_resolucao` reusado, sem segunda implementação).

⚠️ **O desfecho não sai do mercado.** Usar o bucket mais provável no último
slot assumiria que o mercado acertou e daria erro pequeno por construção onde
ele estava confiante — circularidade pior que a original. Sai do **DFF**
(taxa efetiva, FRED, já entregue pelo Paulo): média da taxa em [+1, +7] menos
média em [−7, −1] dias da reunião, arredondada à grade de 25 bps. **Validação:
concorda com o mercado em 16 de 16 reuniões inequívocas** (p_max > 0,9) e
resolve as 2 que o mercado não resolveu — inclusive o corte surpresa de 50 bps
de set/2024, em que o mercado terminou 0,517 × 0,468.

| Ingrediente | Alvo: variação futura | Alvo: desfecho (DFF) |
|---|---|---|
| estabilidade (variação total) | −0,31 a −0,40 | −0,44 a −0,46 |
| estabilidade (\|ΔE\|) | −0,29 a −0,38 | −0,43 a −0,47 |
| **coerência** | −0,15 a −0,18 | **−0,45 a −0,46** |
| proximidade | +0,07 a +0,22 | **+0,29 a +0,72** |

**Três consequências:**
1. **A coerência é bem mais forte do que a 6f indicava** — triplica no alvo
   independente e é a melhor candidata isolada na grade 24h. Coerente com o
   que ela mede: livro que não fecha é mercado que não processa informação,
   não mercado agitado. A ressalva da 6c sobre poder discriminante fica
   definitivamente para trás.
2. **A rejeição da proximidade fica mais forte** (+0,72 no pior caso): o sinal
   invertido não era artefato do alvo.
3. **As duas formas de colapso empatam de fato** (0,002 a 0,017, ordem
   trocando entre grades). Confirma o desempate por parcimônia da 6g: não
   havia vencedora a encontrar.

**Ponto novo, para a dona decidir — janela 5 × 10.** A régua usa 5 variações,
que vence com folga no alvo de variação futura nas duas views. No alvo por
desfecho, **10 fica ligeiramente à frente na 2.3** (−0,458 × −0,443, diferença
de 0,015). Mantida a de 5 por ser o critério declarado antes do teste, e
porque a diferença aparece só na view que ainda não tem portão. **Registrado
agora, antes de olhar backtest** — pela 6d, revisitar depois do resultado de
carteira não seria admissível.

**Limite do escopo:** o alvo por desfecho **só roda na 2.3**. Para a 2.2
exigiria o CPI publicado pelo BLS; o pipeline traz as datas de divulgação, não
os valores. Se essa série entrar, a verificação de não circularidade passa a
ter duas views — **candidato a pedido ao Paulo, não pedido ainda.**

### 6i. Recalibração com o calendário do CPI corrigido (09/08/2026) 🟢

Aviso do Felipe: o G10c do Paulo trouxe o calendário oficial do CPI (FRED) e
expôs dois erros na janela do shutdown de 2025 — o CPI de set/2025 saiu em
24/10 (não 15/10) e o de out/2025 **nunca foi publicado** (`2025-11-13` era
evento fantasma). Corrigido em `load_cpi_releases` (`origin/Felipe` em
`66cfecb`), com o arquivo do Paulo mantido cru.

**Re-rodada a calibração da 2.2 inteira. Mudou um número só:**

| Ingrediente | Antes | Depois |
|---|---|---|
| estabilidade (vt e \|ΔE\|), coerência, portão | — | **idênticos** |
| proximidade | +0,09 a +0,31 | **+0,10 a +0,37** (n: 883 → 840) |

**A régua não muda, e não é sorte:** os dois ingredientes que entraram não
consultam calendário — medem movimento da PMF e fechamento do livro, que são
propriedades da leitura, não da agenda. O único candidato que dependia da data
do evento é justamente o que reprovou. Uma régua com proximidade dentro teria
herdado o erro em silêncio: o teste de monotonicidade mede ordem entre score e
erro, e calendário errado desloca os dois juntos.

**Registrado no relatório** (seção de robustez), com o recorte do mecanismo e
da lição — "calendário oficial em tudo que for medido". O +1,45 pp de impacto
no backtest **ficou de fora de propósito**: é número do Felipe e o lugar dele
é a seção de backtest; a seção do Ω não cita resultado de carteira em ponto
nenhum, e é isso que torna verificável no próprio texto a afirmação de que a
régua não foi ajustada a resultado.

### 6j. ⚠️ Convenção do `c`: a curva do Felipe e a saída da régua são inversas 🟡

Levantado ao ler `Curva_c.md` (09/08). Na curva dele o `c` varre 0,01 a 1 e a
Σ|w| **cresce** com o `c` — é **confiança**. A régua entrega `c ≥ 1`,
**multiplicador de incerteza** (convenção combinada em 05/08). São recíprocos,
e não é questão de rótulo: decide que trecho da curva a régua alcança.

Traduzida para a escala da curva (601 decisões da 2.2):

| nível | mediana | p95 | pior mercado |
|---|---|---|---|
| 1 | 0,953 | 0,805 | 0,362 |
| 3 | 0,865 | 0,521 | 0,047 |
| 5 | 0,785 | 0,338 | 0,006 |

**A régua vive no topo da curva.** A região em que a Σ|w| do Felipe desaba
(0,01, mediana 4,8) é inalcançável pela mediana — exigiria nível ≈ 95. Mesmo
o pior mercado só chega lá com nível ≈ 4,5.

**Confirma a conclusão do passo (3) dele por caminho independente e mostra o
mecanismo:** o `c` não substitui o limitador de tamanho porque age na
**cauda**, não no centro (com nível 5, o pior mercado cai a 0,006 e a mediana
segue em 0,79). Discriminar mercado bom de ruim e encolher a carteira inteira
são funções diferentes.

**Consequência para a reunião:** o eixo da escolha tem de ser o **nível da
régua**, não o `c` da curva — senão escolhe-se um ponto que a régua não
alcança. Oferecida ao Felipe a série de `c` por decisão para ele replotar no
eixo certo. **Aberto até a reunião.**

### 6k. ⚠️ A régua modula quase só a 2.2 — a 2.3 é quase invariante (10/08/2026) 🟡

Saiu da série de `c` por decisão pedida pelo Felipe (`lia/exportar_c.py` →
`lia/c_por_decisao.csv`, entregue em `RESPOSTA6_Felipe_serie_c.md`). A tradução
da 6j para a escala da curva dele era **só da 2.2**; com as duas views:

| nível | 2.2 mediana | 2.2 pior | 2.3 mediana | 2.3 pior |
|---|---|---|---|---|
| 1 | 0,950 | 0,362 | **0,988** | **0,817** |
| 3 | 0,858 | 0,047 | **0,965** | **0,545** |
| 5 | 0,775 | 0,006 | **0,942** | **0,364** |

(388 decisões ativas na 2.2, 781 na 2.3, 349 dias com as duas ativas)

**Mecanismo, não defeito:** o mercado de decisão do FOMC tem 4–5 buckets, livro
que fecha (fator de coerência mediano 1,0035 × 1,0200 na 2.2) e PMF que se move
pouco (estabilidade 1,0065 × 1,0283). Parte da suavidade, porém, é **ausência
de portão** — sem o G5 do FOMC nenhuma decisão da 2.3 sai por volume zero (0
contra 17 na 2.2).

**Para a reunião (junto com a 6d/6j):** a curva do nível deve sair **por view**.
Escolher olhando o efeito agregado subestima quanto o nível morde a 2.2, porque
a 2.3 dilui. **Não** se propõe nível por view — seriam dois botões onde a 6d
pediu um; propõe-se só que o gráfico separe.

**Regra de seleção do mercado do dia — lida do módulo do Felipe, não decidida
aqui.** Em 80 das 496 datas da 2.2 há 2 ou 3 mercados-mês vivos (no FOMC a
sobreposição é a regra), então `{data: {view: c}}` exige escolher um.
`_view_2_2`/`_view_2_3` do `scripts/backtest_v1.py` usam `min(eventos futuros)`
— vale o mercado do **próximo** evento, e é isso que a coluna `selecionado`
reproduz. A série completa vai junto: se a regra dele mudar, o casamento se
refaz do CSV sem nova rodada. Cinco mercados de CPI ficam de fora por não terem
release no calendário do Paulo (inclusive o fantasma da 6i, corretamente).

### 6l. Cristalização: medição do Felipe retirada, frase do relatório congelada (10/08/2026) 🟡

O Felipe mediu entropia e variação total por distância ao evento
(`Dump/analises/Cristalizacao_entropia.md`) e encontrou **reversão no último
slot** — o que contradiria a frase interpretativa da seção "o que foi
rejeitado" do relatório ("a probabilidade se cristaliza à medida que a decisão
chega"). **Ele avisou depois que o artefato está errado e que envia o
corrigido.**

**Estado: parado, de propósito.** O relatório **não foi alterado** e a frase
segue como está — não se corrige texto com base em número que vai mudar, nem se
defende a frase contra ele. Quando o arquivo certo chegar, a verificação roda no
dado desta régua (variação total da PMF renormalizada, grade de 12h) e a frase
vai ao relatório com o recorte que os dois lados sustentarem.

**O que já vale, independentemente do número:** a rejeição da proximidade **não
depende dessa frase** — ela caiu em 16 cortes do teste de monotonicidade, nas
duas views, incluindo o alvo por desfecho da 6h. O que está em jogo é uma
sentença interpretativa, não um ingrediente da régua.

### 6m. Regra de decisão declarada ANTES de rodar a 2.3 com portão (10/08/2026) 🟡

O Paulo entregou o G5 do FOMC (`conditionId` no parquet + as 76 faixas × 18
reuniões) e o valor realizado do CPI. Isso permite, pela primeira vez, rodar a
**2.3 com os quatro ingredientes** e estender o **alvo por desfecho à 2.2** — as
duas lacunas que a 6f e a 6h declaravam.

**Este registro é feito com o dado em disco e nenhum resultado calculado.** É o
que o torna verificável: a regra abaixo não pode ter sido escolhida depois de
ver o número, porque o commit que a grava é anterior ao que produz o número.

**Regra, escolhida pela dona:**
1. A rodada da 2.3 com portão é **confirmatória**. Se concordar com a 6g, a
   régua fica confirmada em duas views com portão.
2. **Se discordar, a régua não muda.** A 6g fechou a 6a por **parcimônia**, não
   por vitória estatística (as duas formas já empatavam no CPI); trocar a forma
   ao ver a segunda view seria escolher depois do dado — exatamente o que a
   trava da 6d evita. A discordância vai ao relatório como **limitação
   registrada**, não como motivo de troca.
3. O que a rodada **pode** mudar: a ressalva da 6f (estabilidade possivelmente
   inflada pelo viés do midpoint) e os números da tabela por view da 6k, que
   foram medidos sem portão na 2.3.

**Decisões da dona sobre o alvo por desfecho da 2.2** (perguntas devolvidas pelo
Paulo na entrega do CPI realizado):
- **Desfecho = `sa_fp_1dec`** — CPI MoM SA *first-print* (ALFRED, valor que
  existia no dia do release), arredondado a 1 casa, que é a precisão em que a
  própria rule do mercado resolve. O revisado erraria o bucket em dez/2024 e
  ago/2025.
- **out/2025 e nov/2025 ficam FORA do teste**, reportados à parte. Os dois têm
  desfecho do UMA (0,3%) mas nenhum valor do BLS: out/2025 nunca foi publicado
  (shutdown) e nov/2025 não tem MoM porque falta a base de outubro. Pela 6h o
  desfecho **não sai do mercado**, e resolução de oráculo não é medição
  independente — aceitá-los reintroduziria a circularidade nos dois meses mais
  anômalos da série. O fato vai ao relatório numa nota separada.
- **dez/2024 e jan/2025 entram com SA**, com ressalva: a rule desses dois é
  legada e não nomeia a série, então "SA" é inferência do Paulo por
  consistência com os buckets — que usa o desfecho para escolher a série, e é
  levemente circular. **Roda-se a sensibilidade com e sem os dois**; se o
  resultado não mudar, a ressalva é imaterial e fica registrada como tal.
- **jul/2026 fora** — release em 12/08/2026, mercado ainda aberto, sem bucket
  vencedor. Não é escolha metodológica, é calendário.
- Sobram **15 meses** utilizáveis, contra 16 reuniões na 2.3.

**Correção de fato na 6g:** lá está escrito "19 mercados-mês de CPI". São
**18** — contados os slugs distintos no `clob_exploracao`, que é a mesma conta
do Paulo. As 111 faixas (que o G5 casa 111/111) estão certas; o erro era só no
número de mercados-mês. ⚠️ **Este item deixou de ser correção de texto ao ser
investigado — virou a 6n.**

**RESULTADO da rodada declarada acima (mesma sessão, commits `1a9386d` e
`0f01741`): confirmatória em todos os pontos.** Nada da régua muda.

| Ingrediente (alvo variação total) | 2.3 sem portão (6f) | 2.3 COM portão | Veredito |
|---|---|---|---|
| estabilidade (variação total, j5) | −0,40 | **−0,4005** | melhor candidata de novo |
| estabilidade (\|ΔE\|, j5) | −0,36 | −0,3756 | perde de novo |
| coerência | −0,15 a −0,18 | −0,15 a −0,18 | sinal correto, estável |
| portão como score | não testável | −0,10 a +0,19 | reprovado, como na 2.2 |
| proximidade | +0,09 a +0,22 | +0,07 a +0,22 | reprovada, sinal invertido |

- **A ressalva da 6f cai.** Condicionar a estabilidade aos slots que passam
  pelo portão move o spearman de −0,4005 para −0,3960 (delta +0,005). O
  ingrediente não vivia do artefato do midpoint, e agora isso está medido nas
  **duas** views, não por analogia.
- **O mecanismo da 6b existe e é irrelevante em volume**, que são coisas
  diferentes: na 2.3 os slots sem negociação têm erro futuro médio 4× menor
  (0,0037 × 0,0147) — a assinatura exata do artefato — mas são **24 contra
  1.139**. O diagnóstico vai ao relatório com esse recorte.
- **12h vence 24h** de novo em todos os cortes, e j5 vence em h=2 (j10 vence em
  h=5, coerente com o já registrado na 6h).

**Regra nova de escopo da Lia, registrada porque muda o que o Felipe recebe:
faixa com volume `NaN` contamina o slot inteiro.** No G5 do FOMC, 908 dos 3.905
slots misturam faixa truncada pelo cap de 20k (`NaN`) com faixa medida. Somar
tratando `NaN` como ausente daria soma zero e **vetaria** em 6 desses slots,
afirmando "ninguém negociou" onde parte é desconhecida — o contrário da
separação `0` × `NaN` combinada com o Paulo em 07/08. A regra é a mesma
disciplina da 6e (linha incompleta não entra). **Não muda a 2.2**: lá nenhuma
faixa bateu o cap, não há slot misto, e a re-rodada saiu idêntica à publicada.
Implementada em `agregar_volume_slot`, usada pelos dois lados (calibração e
exportador), com 3 testes.

**Resultado do alvo por desfecho na 2.2** (15 meses, derivação casa o bucket
resolvido em **15/15**, incluindo as 3 pontas abertas):

| Ingrediente | 2.3 (DFF) | 2.2 (CPI realizado) |
|---|---|---|
| estabilidade (variação total) | −0,44 a −0,46 | −0,05 a −0,13 |
| estabilidade (\|ΔE\|) | −0,43 a −0,47 | **+0,11 a +0,26** |
| coerência | −0,45 a −0,46 | −0,02 a +0,01 |
| proximidade | +0,29 a +0,72 | +0,16 a +0,25 |

- **A magnitude despenca na 2.2, e a causa foi medida, não suposta:** no último
  slot, a probabilidade no bucket que resolveu tem mediana **0,97** no FOMC
  (83% acima de 0,9) e **0,39** no CPI (7% acima de 0,9). O mercado de inflação
  não converge, então `1 − p_vencedor` mede sobretudo o tamanho da surpresa do
  mês — propriedade do evento, não da qualidade do livro. **É limitação do
  alvo, não da régua**, e vai declarada assim.
- **O que sobrevive é a distinção que faltava:** a variação total mantém o
  sinal correto nos 4 cortes; a \|ΔE\| **inverte** nos 4. O empate da 6h/6g era
  real, e o único corte que separa as duas separa a favor da escolhida. Vai ao
  relatório como **evidência fraca em magnitude e favorável em direção** — não
  como confirmação.
- **Sensibilidade dos dois legados (SA inferido) — imaterial**, como a 6m
  antecipava: sem eles a estabilidade vai de −0,047 para −0,065 e a coerência
  de +0,002 para −0,025. Muda pouco, e sempre para o lado certo.
- **Proximidade reprovada mais uma vez**, agora também no alvo independente da
  2.2. São 20 cortes acumulados.

### 6n. ⚠️ Um mês de CPI entrava DUAS vezes na calibração (10/08/2026) 🟢

Saiu de investigar a divergência de contagem da 6m (nós 19, o Paulo 18) em vez
de tratá-la como detalhe. O 19º "mercado" era `M1_cpi_monthly`, rótulo de um
marco anterior do pipeline: **os mesmos 6 tokenIds, os mesmos 56 slots e
diferença máxima 0,0** contra `CPI_july-inflation-monthly`. Não é mercado
parecido — é o mesmo contrato sob dois nomes de arquivo, e jul/2025 entrava
duplicado na 2.2 (56 de 1.198 slots da grade de 12h, 4,7%).

**Correção:** a identidade do mercado passa a ser o **tokenId**, não o nome do
arquivo (`_prefixos_sem_duplicata`); entre prefixos com o mesmo conjunto de
tokens fica o que casa com o calendário de releases.

**Impacto medido — a régua não muda:** todas as candidatas melhoram
ligeiramente (vt_j5 de −0,4615 para −0,4717; coerência de −0,3131 para
−0,3214) e **nenhuma ordenação se altera**. A validação de ponta a ponta passa
de 601 para 573 decisões (515 ativas, 89,9%; os 37 vetos de liquidez e 21 sem
par não mudam).

**Não contaminava o `c_por_decisao.csv`** — o exportador já filtrava por
casamento com o calendário, e `M1_cpi_monthly` nunca casava. A versão de 10/08
do `marcar_selecionado` citava esse par como "empate entre dois mercados para o
mesmo evento": o sintoma tinha sido visto e classificado errado.

**Observação para o Paulo (não é edição em módulo dele):** o
`clob_exploracao` guarda o mesmo mercado sob dois rótulos. Nada a corrigir no
dado — o G5 casa por nome de arquivo e está consistente —, mas quem varrer o
diretório por prefixo conta um mercado a mais.

### 6o. Tabela por view atualizada COM portão na 2.3 (10/08/2026) 🟡

Regerado o `c_por_decisao.csv` (`0f01741`). A 2.2 saiu **idêntica**; a 2.3 tem
agora **10 decisões inativas por veto de volume** (antes 0), de 801.

| nível | 2.2 mediana | 2.2 pior | 2.3 mediana | 2.3 pior |
|---|---|---|---|---|
| 1 | 0,950 | 0,362 | 0,988 | 0,817 |
| 3 | 0,858 | 0,047 | 0,965 | 0,545 |
| 5 | 0,775 | 0,006 | 0,942 | 0,364 |

(388 decisões ativas na 2.2, 771 na 2.3, 349 dias com as duas ativas)

**A ressalva da 6k cai: a suavidade da 2.3 não era ausência de portão.** Com o
portão, a 2.3 perde 1,2% das decisões por liquidez contra 4,0% na 2.2, e os
quantis do `c` não se movem. O mercado do FOMC é genuinamente mais bem
comportado. **A conclusão da 6k para a reunião fica de pé e mais forte:** a
curva do nível tem de sair **por view**.
