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

### 6a. Colapso PMF multi-bucket → `p` para o `score_estabilidade` 🟡

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
(quatro candidatas: 2 formas × 2 grades).

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
