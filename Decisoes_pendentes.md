# Decisões pendentes — mock do projeto

Decisões de implementação que faltam fechar antes/durante o mock. À medida que resolvemos, registramos a decisão na própria seção (status: 🔴 aberta · 🟡 em discussão · 🟢 fechada).

---

## ⚠️ Aviso de numeração — o mesmo número é decisão DIFERENTE em cada branch

Levantado em 2026-08-07 (sessão 6, Felipe), ao ver o Paulo abrir uma "Decisão 12"
que não é a nossa. **Não é decisão minha e não estou renumerando nada** — é fato
de encanamento, registrado para ninguém citar número achando que o outro entende.

De 1 a 7 os três branches batem (o 7 diverge só no status). **De 8 em diante são
três numerações paralelas:**

| # | `Felipe` | `Paulo` | `Lia` |
|---|---|---|---|
| 8 | passo final do otimizador | reconciliação de cobertura poly × ETFs | passo final do otimizador |
| 9 | maratona de 04/08 (13 provisórias) | encadeamento dos mercados FOMC | matriz ativos × mercados |
| 10 | sessão de 05/08 (2 do backtest) | extensão do universo FOMC | — |
| 11 | view B fora do v1 | fonte da série de preço do poly | — |
| 12 | `E_FF` da 2.3 sem o ZQ | G5: slot pré-primeiro-trade `NaN` ou `0` | — |

**Agravante interno ao branch `Felipe`:** nos `Dump/analises/` e no `LOG.md`,
"D11" e "D12" são os **dois itens da seção 10** (duration medida e teto de
alavancagem), não as seções 11 e 12. E o `LOG.md` de 31/07 chama de "Decisão 12"
o critério de escolha do `k` — que não existe como seção em nenhum branch.

**Opções para a reunião (não escolhidas):** (a) prefixo por dono (`F8`, `P8`,
`L8`); (b) um dono único do arquivo e renumeração no merge; (c) faixas
reservadas por dono; (d) manter e sempre citar branch junto do número.

**Enquanto não fecha:** ao citar decisão, diga o branch — "D12 do `Paulo`", não
"D12".

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

## 6. Forma funcional do Ω reativo 🔴
Como volume, estabilidade, convergência e proximidade de evento viram um número de confiança. Versão mínima para o mock vs. versão completa.

**Decisão:** _(a registrar)_

### 6a. Como colapsar uma PMF multi-bucket no `p` que alimenta o `score_estabilidade` 🟢
Surgiu na implementação do `diagnostics` (sessão de 2026-08-07), depois da resposta da Lia.

**Contexto:** a Lia definiu `dp_variacao_janela` como "desvio-padrão das diferenças `p_t − p_{t−1}`". Em view binária o `p` é inequívoco. **Em mercado multi-bucket não existe um `p`** — a leitura de um slot é um vetor de 5 a 9 faixas. Hoje o campo sai `NaN` nesses mercados (`src/poly_loader.py::diagnostics_qualidade`), e a série crua completa vai em `serie_janela`.

**Por que é decisão dela e não minha:** escolher o colapso (norma L1 entre PMFs consecutivas, probabilidade do bucket modal, entropia, desvio do valor esperado…) é fixar a forma funcional de um ingrediente da régua dela dentro do meu módulo — o mesmo argumento com que ela pediu `soma_faixas` cru em vez de `|soma − 1|`.

**Por que não pode ficar só como conversa:** as **três views ativas do v1 (2.2, 2.3, B) são todas multi-bucket**. Se cada lado assumir que o outro preenche, o `score_estabilidade` — 1 dos 4 ingredientes do `c` — fica sem insumo em todas as views do v1.

**Opções, sem fechar:**
1. Ela calcula do lado dela a partir de `serie_janela` (não custa dado novo nem ida e volta; o campo `dp_variacao_janela` fica `NaN` de propósito e ela ignora).
2. Ela declara a regra de colapso e eu preencho o campo no `diagnostics` (mantém o contrato dela de "escalar pronto", mas fixa a forma funcional no meu módulo).

**Não bloqueia o backtest:** o fallback `c = 1` segue valendo (`omega_fallback` com `incerteza=None`).

**Fato de interface a comunicar junto (não é decisão):** entre a série crua e o que a view consome roda o `carry_missing` (D4/6.1). Ou seja, **a view nunca vê o buraco** que o `diagnostics` reporta — o modelo já o tapou carregando a última leitura. Isso muda como ela lê `n_slots_esperados − n_pontos`.

**Decisão (declarada pela DONA da decisão em 2026-08-07, `RESPOSTA3`):
opção 1 — ela colapsa do lado dela, a partir da `serie_janela`.** O
`dp_variacao_janela` continua saindo `NaN` de propósito em mercado multi-bucket
e **nada muda no meu módulo**. A forma do colapso segue dela (duas candidatas em
teste); o que fechou aqui é **quem calcula**, que era a pergunta de interface.

⚠️ **Ressalva de reprodução, levantada por mim no retorno (não é decisão):** ela
pretende colapsar sobre a `serie_janela` **renormalizada**, e a `serie_janela` é
CRUA — renormalizar a linha crua **não** reproduz o `p` que a view consome. Entre
uma e outra rodam o `carry_missing` (D6.1: faixa sem preço herda a última
leitura, em vez de a massa dela ser espalhada nas presentes) e, na 2.3, o piso de
soma 0,9 (a linha degenerada mata o dia em vez de virar PMF renormalizada).

**Encerramento da ressalva (`RESPOSTA4` dela, 2026-08-07):** a divergência é
**de propósito e ela está certa** — o score dela não deve reproduzir o `p` da
view. O `p` tratado é o que o modelo consome; o que ela mede é se o mercado que
gerou aquele insumo estava funcionando, e medir sobre a série tratada mediria a
suavidade do tratamento. Retirei a preocupação e a oferta do
`serie_janela_tratada`. Ela também **recusa o `ffill`** pelo mesmo argumento do
midpoint (leitura repetida entra como variação zero: erro num sentido só = viés,
não ruído) e trata buraco descartando o slot, penalizando-o pelo canal próprio
(`n_slots_esperados − n_pontos`).

**Delimitação que ela pediu para constar na ata (e é justa):** o que fechou na 6a
foi o **lugar** (ela colapsa, do lado dela, a partir da `serie_janela`). A
**forma continua aberta** e sai do teste de monotonicidade, agora com **quatro
candidatas** — 2 formas de colapso × 2 grades de tempo (12 h entre leituras × 24 h
entre decisões). Não registrar a 6a como "fechada" sem esta metade.

## 7. Convergência entre fontes (polls, casas de aposta) 🟡
Se entra no Ω já no v1 ou fica como stub (adiciona dependências de dados).

**Decisão:** fora do v1 — fica como stub. Reavaliar depois se entra em versão futura (em aberto).

## 8. Passo final do otimizador: qual Σ e quais restrições 🟢
Surgiu na implementação do esqueleto BL (`src/bl_optimizer.py`).

**Contexto:** o passo `w = inv(δΣ)μ` aceita duas covariâncias:
- **Σ amostral** — pesos respondem só à mudança na média; com confiança zero volta exatamente a `w_mkt`.
- **Σ_bl posterior (He & Litterman)** — incorpora a incerteza das views; com confiança zero os pesos encolhem para `w_mkt/(1+τ)` (sobra caixa implícito).

Também estava em aberto: restrições nos pesos (long-only? soma 1? limite de alavancagem?).

**Decisão (fechada em reunião, 2026-07-07):**

- **Parte A — Σ amostral** no passo final de pesos, **não** a Σ_bl posterior de
  He & Litterman. Motivo registrado: dá o caso neutro limpo — confiança zero
  devolve exatamente `w_mkt`, e o encolhimento por incerteza fica a cargo do Ω
  reativo, num lugar só.
- **Parte B — irrestrito** (opção B1): fórmula fechada, aceitando short e desvio
  de soma = 1. Ficou com a ressalva explícita de reavaliar se o backtest
  mostrasse pesos extremos — **e mostrou**: é a origem da discussão de teto de
  alavancagem da seção 10, que segue aberta e não reabre esta.

> ⚠️ **Registro reposto em 2026-08-07 (sessão 8), por instrução do dono.** Esta
> seção esteve 🔴 "(a registrar)" entre 2026-07-09 e 2026-08-07: a decisão foi
> apagada por acidente na limpeza da seção duplicada (sessão 3 de 09/07), que
> removeu a cópia com o texto e manteve a vazia. O conteúdo acima vem da ata do
> `LOG.md` de 2026-07-07 e bate com o que o código faz desde então
> (`src/bl_optimizer.py`, docstring de `optimal_weights`: "DECISAO-8 (fechada)").
> **Nada foi decidido agora — só recolocado.** As alternativas B2/B3/B4 que a ata
> menciona como "mantidas no arquivo" foram perdidas na mesma limpeza; vale
> reconferir na reunião se alguém as quiser de volta.

---

## 9. Maratona de 2026-08-04 — 13 decisões 🟢 (provisórias)

Fechadas pelo Felipe com autorização do grupo, para não travar a entrega.
**Provisórias: o grupo revisa depois** — prioridade em τ/δ, que encosta no
módulo da Lia. Justificativa e números de cada uma no `LOG.md` (sessão 2 de
04/08); medições em `Dump/analises/`.

| Item | Decisão |
|---|---|
| Prazo da carteira (H) | 1 dia |
| Views ativas | 2.2 · 2.3 · ~~B~~ (a B saiu do v1 em 2026-08-07 — ver seção 11) |
| Views fora | 2.4, 3.1, C, E, G |
| Camada tática | entra: prêmio de anúncio condicionado à incerteza + drift pós-FOMC |
| Tática fora | gap de fim de semana |
| Balde aberto | ponto médio extrapolado (meia largura da grade) |
| Faixa faltante na PMF | carrega a última leitura, depois renormaliza |
| Favorite-longshot | sem correção no v1 (γ = 1,0); γ ∈ {1,0; 1,1; 1,25} como robustez |
| Surpresa de juros | ΔDTB3 do FRED (o ZQ não tem fonte grátis); falta `DFF` para a expectativa |
| δ | 3,0 (medido no nosso SPY) |
| τ | 1/T, T = janela do Σ; Ω ancorado em `diag(P·τΣ·Pᵀ)` |
| Custo de transação | 2 bps/lado sobre o giro + financiamento e aluguel declarados; métrica do relatório = custo de breakeven |
| Horizonte da 2.2 | divergência demeanada, repricing dividido pelos pregões até a divulgação |

---

## 10. Sessão de 2026-08-05 — 2 decisões do backtest 🟢 (provisórias)

Tomadas pelo Felipe em sessão, no mesmo regime da seção 9 (**provisórias, o
grupo revisa**). As duas saíram de o loop de backtest ter rodado e batido nelas —
nenhuma foi escolhida no vazio. Números em `Dump/analises/Backtest_v1.md`.

| Item | Decisão | Por que precisa de revisão do grupo |
|---|---|---|
| **Duration do breakeven (view 2.2)** | **medida** no par que a view monta (`market_inputs.breakeven_duration`), janela expansiva — deu **8,31 a 8,38** | A espec supunha "~8" e o LOG de 09/07 deixou o valor exato como decisão humana. O dado confirmou o palpite, mas a fonte mudou: agora é medição, não referência do instrumento. |
| **Teto de alavancagem** | **Σ\|w\| com teto**, varrido em {1, 2, 3, 5} — sem teto o backtest vai à ruína (Σ\|w\| mediana 24, máx 264) | ⚠️ **Encosta no módulo da Lia.** Teto é dimensionamento de risco, mesma família do δ — e pelo `Pergunta_Lia_omega_volume.md` risco é módulo dela. Além disso o teto é remendo no lugar do Ω: com `c = 1` a view é confiada tanto quanto o prior, e é daí que vem a alavancagem. |

**Questão de desenho aberta, não decidida:** o teto corta a carteira inteira ou
só o TILT da view, deixando a perna de mercado intacta? Hoje corta tudo, e é a
explicação mais provável de a carteira perder do comprar-e-segurar SPY.

**Medida em 2026-08-07 (sessão 5) — a suspeita se confirma, e é quase tudo**
(`Dump/analises/Backtest_v1.md`, seção "Onde o teto corta"; `run_backtest(...,
teto_no_tilt=)`). Comparando a **Σ|w| medido igual**, que é a única comparação
honesta entre os dois escopos:

| Σ\|w\| medida | teto na carteira | teto só no tilt | diferença |
|---|---|---|---|
| 1,74 | −15,14 pp | −0,94 pp | **+14,19 pp** |
| 2,48 | −15,92 pp | −1,91 pp | **+14,02 pp** |

A parcela de tilt sai de **−11,84% para +0,35%**: no corte de carteira ela
misturava o tilt da view com o pedaço da perna de SPY que o corte tirou. Ou
seja, **o buraco de ~14 pp contra o SPY era o escopo do teto, não a view** — a
view 2.2 sozinha fica perto de zero na janela. Segue perdendo do SPY nos dois
escopos, mas por −0,94 pp em vez de −14,39 pp.

**Isto mede, não decide.** O escopo continua sendo decisão do grupo, e a ordem
da Lia (c → medir Σ|w| → decidir teto) não muda: o número acima só diz que a
pergunta do escopo tem consequência de duas casas decimais, então vale decidir
junto com o nível.

**Passo (2) da ordem da Lia pré-executado — varredura do `c`** (mesma sessão;
`Dump/analises/Curva_c.md`, `scripts/curva_c.py`, `run_backtest(..., incerteza=)`).
O `c` dela não existe ainda, então entrou como GRADE de valores constantes —
varre e reporta, não escolhe. Três resultados:

1. **O `c` encolhe a alavancagem menos do que parece.** Com Ω = (1/c)·diag(P·τΣ·Pᵀ),
   o tilt escala como **c/(1+c)**, não como `c`: perto de `c = 1` metade do peso
   já vem do prior, e apertar rende pouco. Medido, de `c = 1` a `c = 0,01` a
   Σ|w| pedida mediana cai 40× (195 → 4,8).
2. **Mesmo no `c` mais apertado da grade sobra alavancagem para cortar.** A Σ|w|
   pedida nunca cabe em 1, e o teto morde em 74% dos pregões em TODA a grade —
   por isso o excesso quase não se move (−14,39 → −14,12 pp no escopo de
   carteira). Nesta janela e com esta view, **o `c` não substitui o limitador de
   tamanho.** Isso não contradiz a Lia (o `c` de fato só tira peso, e a ordem
   dela segue certa); refina: os dois convivem, o teto não é só remendo.
3. **Correção de registro:** o "Σ|w| mediana 24, máx 264" acima subestima. Sem
   teto o backtest morre no primeiro dia de ruína, então aquela estatística só
   cobria os pregões até lá. Medida na carteira PEDIDA (que existe todo dia,
   por não depender de trajetória), a mediana é **195** e o máximo **34.481** na
   janela inteira. A conclusão que o número sustentava fica mais forte, não mais
   fraca.

**Posição da Lia (resposta de 2026-08-07), registrada — não fecha nada:** ela
pede para **não** fechar o teto antes de o `c` entrar, porque hoje o teto está
fazendo o trabalho do Ω. Argumento dela: a régua é produto de fatores em (0,1]
na convenção de confiança, logo `c ≥ 1` sempre e o módulo dela **só tira peso,
nunca adiciona** — parte da alavancagem cai por construção quando o `c` chegar,
e calibrar o teto antes é ajustar remendo contra buraco que vai mudar de
tamanho. Ordem que ela propõe: (1) entra o `c`; (2) mede-se Σ|w| de novo; (3)
só então se decide se ainda precisa de teto e se ele corta a carteira toda ou
só o tilt. **O Felipe concordou e leva assim para a reunião; a decisão segue do
grupo.** Ela também corrige o alvo: **δ = 3,0 não é parâmetro livre, é
observável** (medido no nosso SPY), então não é ele que precisa fechar junto com
a escala do `c` — é o teto.

**Remedição de 2026-08-07 (sessão 8), com as DUAS views ligadas — muda a
leitura do passo (2)** (`Dump/analises/Curva_c.md`). A varredura anterior rodou
com a 2.2 sozinha e concluiu que "o `c` não muda o resultado, o teto morde
antes". Com a 2.3 ligada **isso deixou de valer**: ao longo da mesma grade o
excesso se move até **5,01 pp**, e no escopo de tilt ele **troca de sinal**
(+2,62 pp em `c = 1` → −0,44 pp em `c = 0,01`, com máximo de +4,57 pp em
`c = 0,25`). O resto da leitura antiga continua de pé: a Σ|w| pedida nunca cabe
em 1 (mediana 199 em `c = 1`, ainda 4,9 em `c = 0,01`) e a ruína do irrestrito só
some com `c ≤ 0,02` — **algum** limitador segue obrigatório.

**Consequência, e é argumento a favor do protocolo dela, não contra:** o nível do
`c` não é ajuste fino, é escolha de resultado. Uma tabela em que o excesso tem
máximo interior é exatamente o que tenta o olho a "escolher o `c` que dá o melhor
número". Registrado como medição — **nenhum `c` desta tabela é proposta**.

**Segunda posição da Lia (`RESPOSTA3`, 2026-08-07) — protocolo anti-overfit,
registrado, NÃO fechado (é do grupo):** com o excesso agora positivo (+2,68 pp),
um `c` global alto passa a ser **custo** e não conserto — e ela levanta o risco
de processo de eu e ela alternarmos ajustes olhando o resultado ("ela calibra o
`c`, o grupo mexe o teto vendo o número, ela recalibra vendo o número"), que
vira overfit em dois passos sem nenhum dos lados perceber. Proposta dela:

1. a **forma** do `c` sai do teste de monotonicidade (erro realizado da
   probabilidade) e **não é revisitada por resultado de backtest**;
2. o **nível** global é escolhido **uma única vez**, na conversa de risco, junto
   com o teto;
3. se o resultado depois desagradar, mexe-se no **teto**, não na régua.

**O Felipe concorda e leva assim para a reunião.** Ela também registra que o
número do escopo (teto no tilt +2,68 pp × teto de carteira −7,91 pp na mesma
alavancagem de 1,90) responde a "questão de desenho aberta" acima com medição,
não com opinião — mas **a escolha continua do grupo**.

### 10a. Data de corte da régua do `c` e plano B pré-registrado 🟢 (fechada pelo dono, 2026-08-07 — sessão 9)

**O que fecha:** se a régua do `c` da Lia não chegar até **13/08** (entrega em
17/08), o v1 é entregue com **`c = 1`** (fallback neutro do `omega_fallback`) e
**teto no tilt**, no nível **1** — o mais conservador da grade `{1, 2, 3, 5}` já
registrada, que é também o escopo de referência de todas as varreduras desde
05/08.

**O que NÃO fecha:** o nível e o escopo do teto continuam sendo decisão do grupo,
e a ordem da Lia (c → medir Σ|w| → decidir teto) segue valendo até 13/08. Isto é
um **default de prazo**, não uma escolha metodológica adiantada.

**Por que pré-registrar em vez de resolver no dia 15:** o único jeito de escolher
o nível "pela regra e não pelo resultado" é escolhê-lo **antes** de ver o
resultado da configuração que vai ser entregue. A regra usada aqui é
explicitamente independente do backtest — *o ponto mais conservador da grade* —,
e é verificável: qualquer um confere que 1 é o menor de `{1, 2, 3, 5}` sem abrir
o `Backtest_v1.md`. Deixar para o dia 15 significaria escolher o teto com a
tabela de excesso na tela, que é exatamente o overfit em dois passos do
protocolo anti-overfit desta seção.

**Cadeia que isto destrava:** `G5 do Paulo` → `régua do c da Lia` → `nível e
escopo do teto`. Dois dos três elos estão fora deste branch; o plano B existe
para que o atraso de um elo alheio não vire decisão apressada no último dia.

---

## 11. Sessão de 2026-08-07 (sessão 5) — view B fora do v1 🟢 (provisória)

Fechada pelo Felipe no mesmo regime das seções 9 e 10 (**provisória, o grupo
revisa**). Espec da view preservada em
`Dump/analises/Informações_uteis/views/view_B_trajetoria_fed.md` — sai do v1, não
do projeto.

**Fato novo que motivou a decisão (levantado nesta sessão):** a B estava
registrada como "bloqueada, esperando dado", o que não descrevia a situação. Das
duas pernas:

- **A perna do poly EXISTE e já foi entregue.** `M3_fed_trajectory_*` no dado do
  Paulo: 9 faixas ("nenhum corte" a "8+ cortes em 2025"), ~690 leituras por
  faixa, de 2024-12-29 a 2025-12-10. Ninguém tinha percebido porque a view nunca
  chegou a ser montada.
- **A perna do mercado NÃO existe de graça, e isso já estava medido.** O F6 do
  Paulo testou todas as sintaxes do contrato de dezembro no yfinance (`ZQZ25`,
  `ZQZ25.CME`, `ZQ=Z25`, `ZQZ2025`, `ZQF26`, …) — todas vazias. Só o contínuo
  `ZQ=F` funciona, e ele é o contrato da frente, que não serve para um alvo de
  data fixa. As alternativas são pagas (CME DataMine, Nasdaq Data Link,
  Barchart); o FRED não tem o contrato.

**Por que sai do v1 em vez de virar mais um pedido:**

1. **Duplica a 2.3.** Por desenho (item 4 da espec) o β e o P são os MESMOS da
   2.3 — muda só a surpresa. A própria espec já listava "dupla exposição com a
   2.3" como pendência.
2. **Cobre metade da janela.** O M3 é só de 2025: contra a janela do backtest
   (2025-02-10 a 2026-08-06) sobram ~210 dos 374 pregões.
3. **A view irmã está travada por dado grátis.** A 2.3 espera o `DFF` (G8), um
   CSV de uma coluna já cobrado no FOLLOWUP4. Comprar dado para a B enquanto a
   2.3 espera um arquivo grátis inverte a prioridade.

**Condições de reabertura (qualquer uma):** aparecer fonte gratuita do ZQ de
dezembro, **ou** o grupo aprovar um benchmark substituto.

**Substituto mapeado, NÃO decidido — é decisão metodológica, do grupo:** extrair
o forward do mês de dezembro da curva de bills do FRED (dois pontos
interpolados). **Tem precedente direto:** a seção 9 já aceitou trocar o ZQ por
`ΔDTB3` na surpresa de juros, e a 2.3 vai rodar com `DTB3 − DFF`. Fica registrado
como opção, com a ressalva de que um forward de 1 mês tirado de dois vértices
interpolados é ruidoso e ninguém mediu esse ruído.

**Consequência operacional imediata:** **o Paulo pode parar de procurar o ZQ.** A
caça aparece em três pedidos diferentes (F6, FOLLOWUP2, FOLLOWUP3) e agora não
tem consumidor no v1.

---

## 12 (branch `Felipe`). Sessão de 2026-08-07 (sessão 6) — `E_FF` da view 2.3 sem o ZQ 🟢 (provisória)

> ⚠️ O número 12 já existe no branch `Paulo` com outro conteúdo — ver o aviso
> de numeração no topo.

Fechada pelo Felipe em sessão, mesmo regime das seções 9/10 (**provisória, o
grupo revisa**). Medições em `Dump/analises/Backtest_v1.md`.

**Contexto que mudou tudo:** a perna do poly da 2.3 **não** é o binário de
−50 bps do `clob_exploracao` — é a **PMF completa de decisão por reunião** do
`data/polymarket_fed_reunioes.parquet` (18 reuniões, 2024-04 a 2026-06, 4–5
faixas que particionam o desfecho). Medido nos dois:

| | binário de −50bp | PMF completa |
|---|---|---|
| dias com as duas pernas | 88 | 531 |
| variância da surpresa vinda do poly | 4,6% | **53%** |
| `corr(surpresa, −e_ff)` | 0,982 | 0,138 |
| sinal da surpresa | positivo em 100% dos dias | positivo em 83% |

Com o binário a 2.3 seria um proxy do spread de bills com rótulo de Polymarket.
Com a PMF é view de verdade.

| Item | Decisão | Por que precisa de revisão do grupo |
|---|---|---|
| **`E_FF` da 2.3** | **`DTB3 − DFF`, com a surpresa DEMEANADA por janela expansiva** (mesma construção da D7.4 da 2.2) | A espec (item 2) diz que `E_FF` nunca degrada e sai do ZQ. Não há ZQ grátis (F6). O substituto tem horizonte de ~3 meses contra uma reunião, e a demeanagem trata o viés de nível **sem** consertar o descasamento em si. |
| **PMF degenerada** | soma crua `< 0,9` → **view desativada no dia** (cascata), `SOMA_MINIMA` em `view_2_3_fed.py` | Piso escolhido sobre o medido (ver correção abaixo), não sobre teoria. O piso **não morde nenhum dia** — nem na janela do v1, nem no histórico completo. |

**⚠️ Correção de medição (2026-08-07, sessão 8) — o número que sustentava a
linha acima estava errado em dois pontos.** O registro original dizia "27 de 801
dias ruins, 24 com soma < 0,5, todos fora da janela do v1". Remedido no parquet:

| | registrado antes | medido |
|---|---|---|
| dias degenerados (leitura crua, sem carry) | 27 | **25** — o 27 é outra coisa: dias com alguma faixa faltando |
| desses, com soma < 0,5 | 24 | 24 ✔ |
| onde caem | "fora da janela do v1" | **dentro**: 30/10/2025 a 21/04/2026 |
| após `carry_missing` (o que a view lê) | — | **0 de 801**, somas entre 0,953 e 1,143 |

**Por que o piso mesmo assim não morde:** não é o recorte da janela, é o
tratamento — a view nunca vê a linha crua, e depois do `carry_missing` nenhum
dia do histórico inteiro chega ao piso. A frase antiga ("a faixa estreita é
propriedade do recorte") fica sem efeito.

**Fato novo, relevante para a régua da Lia:** os 25 dias degenerados são
**100% linhas incompletas** (mediana de 3 faixas ausentes de 4) — não existe um
único livro completo somando abaixo de 0,9. Ou seja, a soma baixa mede buraco,
não desencontro entre books. Comunicado a ela em
`Dump/trocas/RESPOSTA4_Lia_correcao_801_dias.md`, porque ela havia escolhido
calibrar sobre a história completa **por causa desses dias**. O que fazer com
isso é da régua dela; aqui fica só a medição.

**Compromisso de interface com o Ω da Lia (`RESPOSTA3`, 2026-08-07) — escrito
dos dois lados, a pedido dela:** o piso de 0,9 e o `score_coerencia` dela
(`−|soma − 1|`) **não** são dois cortes na mesma coisa, porque os regimes são
**disjuntos** — soma crua < 0,9 mata a view na minha cascata (ela nem chega ao
Ω, não existe `c` para ela); soma ≥ 0,9 é território só do score dela. A
assimetria é a favor: meu corte é só por baixo, o dela é bilateral (a soma de
1,32 medida no mercado de cortes do Fed passa inteira pela cascata e só o score
dela pega).

O compromisso que mantém isso verdadeiro: **o meu piso não vira rampa** (está
comentado em `view_2_3_fed.py::SOMA_MINIMA`) e **o único portão binário da régua
dela continua sendo o volume**. No dia em que qualquer um dos dois lados mudar,
isso vira dupla contagem — e o teste de monotonicidade dela **não pegaria**, por
os dois ingredientes se moverem juntos.

**Ressalva dela, registrada:** com a soma da 2.3 entre 0,969 e 1,013 na janela do
v1, o ingrediente de coerência tem pouca variação; se ele reprovar no teste de
monotonicidade, pode ser **falta de poder discriminante**, não sinal errado — ela
vai reportar a distinção em vez de deixar o relatório concluir que "o desarranjo
não prevê erro".

**Opções descartadas (registradas para a ata):** (A) usar cru — mantém viés de
+4,89 bps e a view fica do mesmo lado em 83% dos dias; (C) escalar a âncora por
`dias_até_reunião/91` — assume proporcionalidade que ninguém mediu; (D) pedir o
`DTB4WK` ao Paulo — casa melhor o horizonte, custa uma rodada e não elimina o
prêmio de prazo; (E) deixar a 2.3 fora do v1 como a B — joga fora 531 dias de
view que o dado sustenta.

**⚠️ Ressalva medida, para a reunião não ler o número torto:** a demeanagem
**não equilibrou** o sinal dentro da janela do backtest — inverteu o lado. No
levantamento completo (2024-04 → 2026-06, 533 dias) a surpresa líquida fica
45%/55%; dentro do backtest (2025-02 → 2026-06, média expansiva começando na
primeira data da janela) fica **22% positiva / 78% negativa**, porque a média
carrega o regime de 2024–25.

### 12a. Semeadura da média expansiva da 2.3 🟢 (fechada pelo dono, 2026-08-07 — sessão 8)

Era o "refinamento mapeado, não decidido" do parágrafo acima. **Fechada aqui, sem
ir à reunião, por instrução do dono** (com o v1 virando a entrega final, o
refinamento não tem versão seguinte para onde ser empurrado).

**O que é:** a lista que alimenta a média expansiva da 2.3 entra pré-preenchida
com os pregões **anteriores** ao início da janela (`MontadorV1.semear_2_3`).
Antes ela nascia vazia: o primeiro dia demeanava por 0,0 — viés inteiro do proxy
passando cru — e os primeiros meses usavam um zero estimado com meia dúzia de
pontos. Não é lookahead: tudo que entra é estritamente anterior ao primeiro dia
negociado, e a média segue expansiva dali em diante.

**Medido (206 pregões de semente, 2024-04 a 2025-02):**

| | sem semente | com semente |
|---|---|---|
| sinal líquido na janela (325 dias) | 22% pos / 78% neg | **34% pos / 66% neg** |
| média da surpresa líquida | −2,56 bps | −1,81 bps |
| excesso × SPY, `tilt ≤ 1` | +2,68 pp | **+2,62 pp** |
| excesso × SPY, `tilt ≤ 3` | +10,56 pp | **+13,70 pp** |

**Honestidade sobre o alcance:** a semente **melhora e não conserta**. O sinal não
volta aos 45%/55% do levantamento completo porque, dentro da janela, a surpresa
genuinamente pende para o lado negativo — o resíduo é regime, não artefato do
zero. No teto de referência (`tilt ≤ 1`) o resultado fica praticamente igual; o
ganho aparece nos tetos frouxos.

**A 2.2 não foi semeada** — não há o que semear: a janela começa na primeira PMF
de CPI (2025-02-08), então não existe pregão anterior a ela com dado da view.

### 12b. Piso de eventos de FOMC para o β 🟢 (fechada pelo dono, 2026-08-07 — sessão 8)

Estava "aberto de propósito". **Decisão: sem piso adicional no v1 — vale o mínimo
algébrico do `estimate_betas` (2).**

**Por que fechar assim, e não com um número:** na janela do v1 o β foi estimado
com **25 a 35 eventos** todos os dias (`n_eventos_beta`). Qualquer piso abaixo de
25 **não desativa um único pregão** — escolher 10 ou 20 seria inventar um
threshold sem medição e sem consequência, contra a regra 6 do `CLAUDE.md`.

**O critério, para quem retomar:** o piso só passa a morder com dado novo que
comece com poucas reuniões, ou ao reaproveitar o template de event-study em view
ou ativo de histórico curto. Aí ele se decide medindo a **curva de estabilidade**
— β estimado com os primeiros *n* eventos contra o β final — e o piso é onde a
diferença deixa de virar o sinal de `P`. Fica registrado como limitação do
relatório, não como pendência.

### 12c. Camada tática fora do v1 🟢 (fechada pelo dono, 2026-08-07 — sessão 8)

**Decisão: o v1 entrega com a camada tática DESLIGADA.** Os três overlays
(prêmio de anúncios 1.3, drift pós-FOMC, gap de fim de semana) ficam no
repositório, implementados e testados, com os orçamentos em `None`.

**Por que não é adiamento:** com o v1 virando a entrega, "decidir depois" não
existe mais — ou liga agora, ou não entra. Ligar exige um `orcamento` (fração do
patrimônio), que é parâmetro do modelo.

**Medido antes de decidir** (`Dump/analises/Curva_orcamento.md`,
`scripts/curva_orcamento.py`, teto no tilt = 1):

| família | Δ vs. desligada |
|---|---|
| só prêmio | −0,34 a −0,03 pp |
| só drift | +0,08 a +0,80 pp |
| prêmio + drift | +0,05 a +0,45 pp |

**O que a varredura mostrou, e é o motivo de não ligar:** o Δ é **monótono no
orçamento** dentro de cada família — cada overlay é um deslocamento de peso fixo
vezes o orçamento, então a grade **não tem ótimo interior**. A melhor linha é
sempre a da ponta, e a ponta é onde a varredura parou. Uma tabela assim não
seleciona orçamento; escolher a linha de cima seria calibrar tamanho contra o
resultado de 374 pregões, que é o overfit em dois passos do protocolo da seção
10 — agora sem rodada seguinte para desmentir.

**Fica no relatório como sensibilidade**, não como configuração entregue.

**Depende do Paulo (categoria 3):** a regra "vale o mercado da **próxima**
reunião" é a **opção (a) da Decisão 9 do branch `Paulo`** (overlap: 82/82 pares
de eventos consecutivos se sobrepõem). Fechei só para o **consumo da 2.3**; a
decisão do dataset continua dele.

**Efeito medido no backtest** (374 pregões, escopo do teto no tilt, teto 1):
a 2.3 fica ativa em **325 dias (87%)**, as duas views convivem em **240 dias
(64%)**, e o excesso contra o SPY sai de **−0,94 pp** (só a 2.2, alavancagem
medida 1,74) para **+2,68 pp** (alavancagem 1,90). Na mesma alavancagem medida
de 1,90, o teto de carteira dá −7,91 pp e o teto no tilt dá +2,68 pp.

---

## 13 (branch `Felipe`). Sessão de 2026-08-07 (sessão 9) — banda de não-negociação fora do v1 🟢

> ⚠️ Numeração paralela por branch — ver o aviso no topo. Cite como "D13 do
> `Felipe`".

**Decisão: o v1 entrega sem banda (`banda=None`) — a carteira negocia todo `Δw`
que o modelo pede.** Fechada pelo dono em sessão, com medição antes (mesmo
regime da 12c). Implementação (`backtest.no_trade_band`) e testes ficam no
repositório; a varredura vai ao relatório como sensibilidade.

**O que a banda é:** filtro de execução — `Δw` de um ativo abaixo da banda não é
executado, e o `Δw` grande passa inteiro. Era a saída **pré-registrada no D8**
para o caso de o giro do H = 1 dia ser ruído: a pesquisa que fechou o D8 aponta
"negociar contra si mesmo" como o mecanismo que mata estratégia diária, e a nossa
tem **36% do giro desfeito em 1–2 pregões**.

**Medido antes de decidir** (`Dump/analises/Curva_banda.md`,
`scripts/curva_banda.py`, teto no tilt = 1, 374 pregões):

| banda | giro diário | desfeito em 1–2 pregões | pernas paradas | breakeven | excesso × SPY |
|---|---|---|---|---|---|
| 0 (v1) | 0,242 | 0,363 | 1% | 35,89 bps | +2,62 pp |
| 0,10% | 0,241 | 0,363 | 55% | 36,01 bps | +2,61 pp |
| 1,00% | 0,235 | 0,357 | 82% | 36,99 bps | +2,68 pp |
| 5,00% | 0,220 | 0,354 | 90% | 38,48 bps | +1,70 pp |

**O que decidiu, e não foi o excesso:**

1. **O ruído não está nas pernas pequenas.** A banda mais fina já impede 55% dos
   pares (dia × ativo) de negociar e corta **0,4%** do giro. Não existe cauda de
   trade miúdo a filtrar — quase todo o giro está em poucas pernas grandes, que
   a banda deixa passar por construção. Para cortar giro de verdade ela teria de
   bloquear trade grande, e aí não é filtro de ruído, é deixar de seguir o modelo.
2. **A reversão quase não se move** (0,363 → 0,354). O remédio não morde o
   mecanismo que o motivou.
3. **O custo não é o que aperta:** breakeven de **35,89 bps por lado contra os
   2 bps premissados — 18× de folga**. O custo teria de subir uma ordem de
   grandeza para virar o sinal.

**Armadilha registrada:** o excesso tem **máximo interior** (1,00%, +2,68 pp).
Com a reversão parada, essa oscilação não tem mecanismo por trás — escolher a
banda por ela seria o overfit em dois passos do protocolo da seção 10, agora sem
rodada seguinte para desmentir.

**Consequência de registro:** com isto some a última pendência de código do
`Felipe` para a entrega. O que resta no caminho crítico é de terceiros (`G5 do
Paulo` → régua do `c` da Lia → teto do grupo, com o corte de 13/08 da seção 10a)
e o merge dos três branches, que não é feito daqui.

---

## 14 (branch `Felipe`). Reabertura de escopo — views novas e retorno da camada tática 🟡

> ⚠️ Numeração paralela por branch — ver o aviso no topo. Cite como "D14 do
> `Felipe`".

**Registro, não decisão.** Direção dada pelo dono em **2026-08-08**, ao revisar o
dossiê de limitações:

> "Duas views para uma estratégia inteira não é nem perto do suficiente. Na
> próxima sessão iremos criar novas views que fazem sentido para a estratégia e
> depois tentar REATIVAR a camada tática com novas estratégias."

**O fato que motivou:** das oito views desenhadas, **duas estão ativas** (2.2
inflação e 2.3 Fed) — verificável em `scripts/backtest_v1.py:395`. As outras seis
saíram por medição (seção 9/D2–D2c e seção 11), e a camada tática saiu pela 12c.

**O que esta direção toca — nada aqui está fechado nem reaberto ainda:**

| Decisão | Status hoje | O que a direção de 08/08 propõe |
|---|---|---|
| seção 9 (views fora: 2.4, 3.1, C, E, G) | 🟢 provisória | não desfazer os cortes — **desenhar views novas** |
| seção 11 (view B fora) | 🟢 provisória | reabre só sob as condições já registradas lá (fonte grátis do ZQ ou benchmark substituto aprovado) |
| seção 12c (camada tática desligada) | 🟢 | **tentar reativar** com estratégias novas |

**Trade-offs a levar para a próxima sessão, medidos e já registrados neste
arquivo — não são objeção, são o que a sessão vai ter de responder:**

1. **Calendário.** Entrega em **17/08**; a régua do `c` corta em **13/08** (10a).
   View nova precisa de mercado no Polymarket, benchmark de mercado e β estimado —
   as três coisas que travaram a B, a C, a E e a G.
2. **Dependência do Paulo.** Mercado que não está no `data/` é pedido novo
   (categoria 3). O histórico: a E morreu com 13 dias de cobertura e a G com 3.
3. **A barreira que derrubou quatro views é do dado, não do desenho.** A
   informação do Polymarket **aterrissa no gap de abertura**, que não é
   negociável — mesmo padrão na eleição 2024, na recessão 2025, no Irã 2026 e na
   tática de fim de semana. Uma view nova sobre mercado de evento provavelmente
   encontra a mesma parede; convém desenhar **medindo isso primeiro**.
4. **A tática não saiu por efeito fraco, saiu por não ter como escolher o
   tamanho** (12c): o Δ é monótono no orçamento, sem ótimo interior. Reativar
   exige uma **âncora para o `orcamento` que não venha do resultado do backtest**
   — caso contrário reabre exatamente o overfit em dois passos do protocolo da
   seção 10 (5.5 do dossiê), agora sem rodada seguinte para desmentir.

**Insumo pronto:** `Dump/trocas/DOSSIE_limitacoes_v1.md` (seções 1 e 2) traz o
motivo medido de cada corte, para a sessão nova não repetir desenho já reprovado.

**Nada fecha aqui.** Se as views novas entrarem, elas são decisão metodológica e
seguem o regime das seções 9/10 (provisórias, revisão do grupo).

### 14a. Direção da sessão seguinte, dada pelo dono em 2026-08-09 (fim da sessão 16)

> "O desafio não precisa de um resultado positivo, mas uma apresentação e
> estratégias que fazem sentido." · "Na próxima sessão vamos tentar adicionar
> mais umas views."

**Continua a seção 14, não a substitui.** A metade "views novas" segue aberta; o
que muda é o critério declarado — **fazer sentido vale mais que medir positivo**.
Isso é consistente com o que já está registrado (nenhuma view foi cortada por
excesso negativo no backtest — 17e) e deve orientar o desenho das próximas.

**Três insumos desta sessão para a próxima não repetir desenho já reprovado:**

1. **A pergunta "a view prevê?" tem teste, e ele é VETO.** Rodá-lo ANTES de
   construir custa minutos e teria matado a transversal antes das 400 linhas — é
   a mesma lição de ordem que o gate da D17 aplicou à camada tática. Depende de
   promover o script (pendência no fim da 15g).
2. **Número acumulado não é resultado sem a conta de atribuição.** A 15h mostrou
   uma view "de +3,89 pp" que era **um pregão**. A coluna "sem os 3 maiores" e o
   acerto de sinal passam a ser obrigatórias em qualquer view nova.
3. **As três inversões da família de inflação têm UMA causa medida, e ela é
   achado de apresentação.** A transversal (15f), a sleeve de CPI (16b) e o
   candidato C2a (17b) saíram invertidos pelo mesmo motivo, corroborado por outro
   caminho no `Convergencia_2_2.md`: **o TIP é dominado por DURAÇÃO, não por
   inflação** (β +1,6 ao juro de 10 anos contra +10,7 do SPY no canal risk-on).
   Três desenhos independentes reproduzindo o mesmo achado sobre o instrumento
   vale mais no relatório do que qualquer um deles teria valido funcionando.

**Ressalva de prior, levantada pelo dono e registrada:** de quatro desenhos que
saíram invertidos, **um tinha causa banal e nossa** (a base do M3, ver 15g). Isso
justifica **auditar o encanamento** dos outros antes de tratá-los como tese
morta — mas os outros três têm mecanismo medido e corroborado, o que a B não
tinha. Auditoria de encanamento **não é** reabrir decisão, e o precedente da D2b
segue: achar bug é uma coisa, inverter sinal porque o dado pediu é outra.

---

## 15 (branch `Felipe`). Duas views novas — CANDIDATAS, construídas e não ligadas 🟡

> ⚠️ Numeração paralela por branch — ver o aviso no topo. Cite como "D15 do
> `Felipe`".

**Registro, não decisão.** Resposta à direção da seção 14, sessão de
**2026-08-08**. As duas estão **implementadas, testadas e FORA do backtest** —
nenhuma foi empilhada, nenhum número de entrega mudou. O que segue é o que o
grupo precisa decidir antes de qualquer uma entrar.

| | View CPI transversal | View de incerteza de anúncio |
|---|---|---|
| Módulo | `src/view_cpi_transversal.py` | `src/view_incerteza_anuncio.py` |
| Testes | `tests/test_view_cpi_transversal.py` (8) | `tests/test_view_incerteza_anuncio.py` (8) |
| Dado novo? | **nenhum** | **nenhum** |
| Sinal | a divergência da 2.2 (E_poly[CPI] − breakeven) | entropia da PMF na véspera |
| P | seção cruzada dos 9 (`P_from_betas`, P[SPY] = 0) | **direcional**: 2 no SPY |
| Q | (ΣP·β) × divergência_líquida / dias_até_divulgação | (ΣP·β) × incerteza_líquida |

### 15a. As duas views leem sinal que já está em uso — e isso é do grupo 🔴

A **transversal** usa a MESMA divergência da 2.2. Empilhar as duas conta a mesma
informação duas vezes no BL, que foi um dos três motivos de tirar a view B
(seção 11). Não é o mesmo caso da B (lá o P também era o mesmo; aqui o P é
diferente), mas é correlação de view que o Ω precisa enxergar.

**Medido em 08/08 e é o achado que decide a conversa:** as duas tomam posições
**opostas no TIP**. A 2.2 fica comprada; a transversal fica vendida
(P[TIP] = −0,29 na amostra completa) porque, relativo ao mercado, o TIP responde
muito mais ao juro de 10 anos (β +1,6 contra +10,7 do SPY) do que ao componente
de inflação — o mesmo achado do `Dump/analises/Convergencia_2_2.md`, por outro
caminho. O β diário é dominado pelo canal risk-on (XLE +20,4; XLF +15,2;
TLT −11,2), então o P que sai é "cíclicos e energia contra duração".

**Três saídas, nenhuma escolhida aqui:** (a) só a 2.2; (b) só a transversal;
(c) as duas, com Ω que reconheça a correlação.

### 15b. A view de incerteza é a PRIMEIRA direcional do projeto 🔴

Todas as views estruturais são neutras em mercado por construção (`P_from_betas`
crava P[SPY] = 0 exato). O prêmio de Savor-Wilson é prêmio de MERCADO, e
expressá-lo com P[SPY] = 0 é exatamente o que impediu a view 3.1 de dizer o que
tinha a dizer (D2b). Por isso o P dela é direcional.

**O que não muda:** Σ|P| = 2 (decisão 4) e a identidade Q = P·E[r].
**O que muda e é do grupo:** com ΣP ≠ 0 a view mexe na exposição direcional, e a
obrigação 5a de `views_common.py` (centragem se troca em TODAS as views juntas)
precisa ser lida antes de empilhar esta com as neutras.

### 15c. A ESCALA da incerteza muda o resultado, e não há default honesto 🔴

Medido nos 32 anúncios (7 FOMC + 13 CPI + 12 payrolls), β do SPY — nenhuma das
duas escalas usa threshold:

| escala | β_SPY | t |
|---|---|---|
| entropia crua demeanada por família | +0,48 %/unidade | **+0,32** |
| percentil da entropia dentro da família | +1,75 %/unidade | **+1,96** |

A entropia crua **linear não sustenta a premissa**: o t cai de +2,27 (contraste
de grupos, como a premissa foi medida em `Dump/analises/Premio_condicional.md`)
para +0,32. O percentil dentro da família é a versão contínua do MESMO contraste
(a mediana é o percentil dicotomizado) e recupera o sinal sem cravar corte.
`build_view` aceita as duas e grava qual rodou em `diagnostics["escala"]` — qual
entra é decisão do grupo.

### 15d. O que a view de incerteza resolve da 12c

A 12c desligou a tática do prêmio de anúncios porque ligar exigia um `orcamento`
sem âncora, e o Δ era **monótono no orçamento** (sem ótimo interior: a grade
devolvia a pergunta em vez de selecionar parâmetro). Como **view**, quem
dimensiona é o BL (τ, Ω, Σ) — o parâmetro sem âncora deixa de existir. A
premissa, que a 12c registrou como APROVADA, é reaproveitada inteira.
**Isto não reabre a 12c**: a tática segue desligada e os overlays seguem com
`orcamento = None`. É outro caminho para a mesma premissa.

### 15f. A transversal REPROVOU no teste de sinal 🟢 (medido 2026-08-08)

Medido depois de construída, a pedido do dono, em 276 pregões (fev/2025 a
jul/2026), β expansivo e divergência de média expansiva — sem lookahead:

| elo da tese | medido |
|---|---|
| a divergência move o breakeven até a divulgação | b +0,0039, **t +2,11** ✅ |
| coef. preditivo de cada ativo acompanha o β contemporâneo | corr = **+0,06** 🛑 |
| a carteira P rende na direção do Q | b −0,048, **t −3,02**, acerto **35%** 🛑 |

**O primeiro elo existe, o segundo não.** O β diário ao Δbreakeven é dominado pelo
canal risk-on e não se transporta para retorno futuro condicionado ao sinal de
inflação. É erro de desenho, não de parâmetro.

**Recomendação (do Felipe, decisão do grupo):** a transversal **não entra**. Com
isso a 15a fica sem objeto por ora — a decisão "só a 2.2 / só a transversal / as
duas" resolve-se em "só a 2.2" enquanto não houver desenho novo.

**Não inverter**, apesar de o inverso ser significante: precedente fechado na D2b,
que recusou redesenhar a 3.1 na direção que o dado pedia (sinal contrário à
própria tese, um ano de amostra). Inverter é ajustar sinal à amostra.

**⚠️ CONTROLE — e ele muda como este teste deve ser citado.** Rodei o MESMO teste
nas duas views que estão na entrega:

| view | t | acerto de sinal |
|---|---|---|
| 2.2 (entrega) | +0,44 | 57% |
| **2.3 (entrega, carrega o backtest)** | **+0,26** | 51% / 56% |
| transversal | **−3,02** | 35% |

**Nenhuma view do v1 passa.** A 2.3, que leva o excesso de −0,94 pp para +2,68 pp,
dá t +0,26. Portanto o teste **não é certificado de utilidade** — ele não captura
o que faz uma view render dentro do BL, onde o Q interage com Σ, w_mkt e o teto do
tilt. Ele funciona como **veto**: pega sinal invertido. É só nisso que a
transversal se separa — as incumbentes são indistinguíveis de zero, ela é
significativamente ao contrário. A recomendação de não ligar vale por isso, e
**não** por ela ter ficado abaixo de uma régua que as outras cumprem.

**Consequência que o grupo precisa ver, e que não é sobre a transversal:** nenhuma
view do v1 prevê linearmente o retorno da própria carteira P. O +2,68 pp do
backtest vem da interação com Σ, w_mkt e o teto — não de o Q estar certo. Isso é
observação para o relatório; não mexo na 2.2 nem na 2.3, que são decisões
registradas.

### 15g. Candidata a 4ª view — a B com β PRÓPRIO 🟡 (medida, não decidida)

O dono pediu uma **quarta** view (2.2 + 2.3 + incerteza + 1). Levantadas todas as
candidatas, a única viável no calendário é a **view B (trajetória do Fed)
reformulada**. O que mudou desde o corte da seção 11:

**A objeção de duplicação era do DESENHO, não da view — e agora está medida.** A
espec da B manda **reusar os β da 2.3** (item 3), o que faz o P sair *literalmente
idêntico*: empilhar as duas põe **duas linhas iguais** no P do BL, que é pior que
correlação (as duas viram uma só, ponderada pelo Ω). Mas o β não precisa ser
reusado. Estimando-o contra **outro vértice da curva**, o P muda de verdade —
medido em 37 reuniões:

| β estimado contra | P resultante |
|---|---|
| ΔDTB3 (curto — o da 2.3) | long TLT +0,61 · TIP +0,36 · XLU +0,58 |
| ΔDGS10 (longo — proxy do vértice de trajetória) | long XLE +0,91 · XLF +0,30 · **short TLT −0,39** |

**Ângulo entre os dois P: 95,6°** (corr −0,34) — praticamente ortogonais. Com β
próprio, a B ocupa **dimensão nova** no BL e a objeção principal da seção 11 cai.

**Cobertura, o segundo motivo do corte:** o M3 (`will-N-fed-rate-cuts-happen-in-2025`)
vai de 2024-12-30 a 2025-12-10 e cobre **237 dos 374 pregões (63%)** da janela,
com soma das faixas média 1,007 (min 0,882). Não há mercado de trajetória de 2026
no `data/`. 63% é comparável à convivência atual das duas views (64%) — limitação
a declarar, não impedimento.

**O que falta de dado: UMA série do FRED, o `DGS1`** (1 ano — o vértice certo para
uma pergunta de fim de ano). Pedido como **G10a**, o item de TOPO do G10 (é uma
série só, minutos de trabalho). Sem ele não dá para especificar a view: o DTB3 (3 meses) é
curto demais e o DGS10 (10 anos) é longo demais para a pergunta.

**🛑 AVISO, e é o motivo de isto NÃO estar fechado:** rodei o teste de sinal na
versão PROXY (DGS10 nos dois lados, 179 dias) e ela saiu **invertida** — t −1,79
em 1 dia, **t −2,68** em 5 dias, acerto 48%. Mesma classe da transversal. O proxy é
sabidamente errado (benchmark de 10 anos para pergunta de 1 ano, então a
"surpresa" carrega prêmio de prazo), mas **é o segundo desenho seguido a sair
invertido**, e isso é padrão, não azar.

**Estado: CONSTRUÍDA em 2026-08-08, por instrução do dono** —
`src/view_B_trajetoria_propria.py` + `tests/test_view_B_trajetoria_propria.py`
(8 testes). O módulo **não depende do `DGS1`**: o benchmark e os β entram como
argumento, então o que ficou pendente é a MEDIÇÃO, não o código. Ele delega
cascata, E_poly e P ao `view_B_trajetoria_fed` (uma implementação só, para as
duas versões não divergirem em silêncio) e acrescenta três coisas: piso de soma
herdado da 2.3, demeanagem expansiva e `vertice` obrigatório nos diagnostics.

**Sequência que falta, e ela não é negociável por pressa:** chegou o `DGS1`
(G10a) → refazer o teste de sinal no vértice certo → **só então** empilhar. Se
sair invertido de novo, **não entra e não se inverte** (precedente D2b). O custo
dessa ordem é ~1 dia; o custo de pular a medição é uma view invertida na entrega
final.

**✅ RODADO em 2026-08-09 (sessão 16), a pedido do dono — a B NÃO sai invertida
no vértice certo, e o motivo da inversão registrada acima era NOSSO.** Medição
por ora só no chat e no `LOG.md`, sem artefato em `Dump/analises/` (o dono
delimitou o escopo a "fale o resultado aqui") — ver a pendência de
reprodutibilidade no fim deste bloco.

O teste foi RECONSTRUÍDO: era ad-hoc na sessão 12 e não sobrou script. A
convenção saiu do **controle**, não de palpite — com `r_P` começando em **D+1** a
**2.3 reproduz exatamente** o registrado em 15f (t +0,26, acerto 51%/56%). A 2.2
dá t +0,57 / 53% contra +0,44 / 57% registrados, e a diferença tem causa
conhecida: a correção do calendário do CPI (sessão 15) mexeu no dado dela e não
no da 2.3.

| vértice | base da grade de baldes | h = 1 | h = 5 |
|---|---|---|---|
| **DGS1 (certo)** | **fim de 2024** | **t +0,33 · 51%** | **t +0,65 · 53%** |
| DGS1 | taxa de hoje | t −0,25 · 50% | t −0,62 · 48% |
| DGS10 (proxy) | fim de 2024 | t −0,05 · 46% | t +0,57 · 50% |
| DGS10 (proxy) | taxa de hoje | t −1,10 · 45% | **t −1,85 · 46%** |

**A inversão era da BASE, não do vértice.** Consertar só a base leva −1,85 →
+0,57; consertar só o vértice leva −1,85 → −0,62. A última linha é a
reconstrução mais próxima do que esta seção registrou (t −2,68, 179 dias):
**reproduz a classe e o sinal, não o número** — a diferença de dias (210 × 179)
diz que a medição da sessão 12 tinha outro filtro, então **a atribuição é
direcional, não exata**.

**⚠️ Isto precisa da desconfiança do grupo, e é o próprio Felipe que pede:** uma
premissa que EU declarei sozinho (15h — a base da grade é a taxa do fim de 2024)
é o que desfaz um veredito negativo já registrado. Por isso a corroboração foi
buscada FORA do resultado, no nosso próprio dado: em **2025-12-10**, última
leitura do M3, o mercado põe **p = 0,97 no balde "3 cortes"**, e foram
exatamente **3** os cortes entregues em 2025 (set/out/dez, lidos no DFF). Se o
mercado contasse "cortes a partir de hoje", depois do corte daquele mesmo dia a
massa estaria em 0 ou 1, não em 3. **Verificável sem abrir o backtest.**

**O que isto muda e o que NÃO muda:** pela régua da própria 15g ("a régua para
esta view é *não sair invertida*, não *passar*"), a B **passa o veto** e sai da
lista de reprovadas. Não entra na de aprovadas: o teste é veto e não
certificado (15f), a B fica indistinguível de zero como as incumbentes
(2.2 +0,57 · 2.3 +0,26 · B +0,33), e **no backtest ela mede −1,38 pp** (15h).
**A entrada continua sendo decisão do grupo.**

**Ressalva menor, registrada:** a base usa o `DFF` (taxa EFETIVA), ~4 bps abaixo
do meio da banda de então. É viés de nível constante, absorvido pela demeanagem
expansiva — mas está aqui para ninguém redescobrir depois.

**Pendência de reprodutibilidade (minha, não do grupo):** o script do teste
vive no scratchpad e **não está no repositório** — a medição acima não é
reproduzível a partir do branch. Promovê-lo a `scripts/teste_sinal.py` (com a
2.2 e a 2.3 como controle embutido, no molde do `gate_sleeves.py`) é candidato a
primeiro movimento da sessão seguinte.

### 15e. Dependência do Paulo — um item bloqueia, dois não

`Dump/trocas/PEDIDO_G10_Paulo.md` (08/08, reescrito no fim da
sessão quando a quarta view entrou no escopo), três itens em ordem de prioridade:

- **G10a — `DGS1` do FRED.** Uma série. É o único insumo que falta para a quarta
  view (15g) existir, e **o único item BLOQUEANTE** do pedido.

- **G10b — rótulo dos baldes de payrolls.** Os 234 JSONs do G9 trazem só preço; o
  nome do arquivo tem o token, não o slug do desfecho. Sem rótulo não existe
  `E_poly[payrolls]`, e payrolls fica limitado à entropia (que não usa rótulo e
  por isso já roda). **Não bloqueia nenhuma das duas views.**
- **G10c — calendário oficial do CPI via API do FRED.** O
  `cpi_release_dates.csv` atual tem 15 datas derivadas das REGRAS dos mercados do
  Polymarket. Destravaria a variante event-study do β da transversal. Melhoria,
  não pré-requisito.

**Nada fecha aqui.** Se qualquer das duas entrar, é decisão metodológica sob o
regime das seções 9/10 (provisória, revisão do grupo), e o backtest só as empilha
depois de 15a, 15b e 15c fecharem.

### 15h. As duas views MEDIDAS no backtest — o ganho é UM PREGÃO 🟡 (medido 2026-08-09)

**Registro, não decisão.** A pedido do dono, as duas candidatas sem veredito
negativo (**15b incerteza** e **15g B com β próprio**) foram empilhadas no
`MontadorV1` e medidas. `views_novas=()` continua o default e **a entrega não
mudou** — `Backtest_v1.md` sai byte a byte idêntico. Medição em
`Dump/analises/Views_novas.md` (`scripts/views_novas.py`, teto no tilt = 1,
γ = 1,0, 374 pregões).

| configuração | dias com a view | excesso × SPY | Δ vs. v1 | Σ dos Δ diários | **sem os 3 maiores** | acerto de sinal |
|---|---|---|---|---|---|---|
| v1 entregue (2.2 + 2.3) | — | **+4,07 pp** | — | — | — | — |
| + incerteza (entropia crua) | 27 | +7,96 pp | **+3,89 pp** | +2,74 pp | **−0,54 pp** | 48% (13/27) |
| + incerteza (percentil) | 27 | +6,39 pp | **+2,32 pp** | +1,61 pp | **−0,09 pp** | 48% (13/27) |
| + B com β próprio (DGS1) | 210 | +2,70 pp | **−1,38 pp** | −0,96 pp | +2,93 pp | 49% (102/210) |
| + as duas (entropia crua) | 27 · 210 | +6,24 pp | +2,17 pp | +1,52 pp | +2,51 pp | 49% (109/222) |
| + as duas (percentil) | 27 · 210 | +4,88 pp | +0,81 pp | +0,50 pp | +0,73 pp | 47% (105/222) |

**O achado, e ele desmonta o número que parecia bom:** o Δ da view de incerteza é
**um único pregão — 2025-04-10**, o choque tarifário (SPY −4,38%, a view vendida
em mercado). Sozinho ele vale **+3,21 pp** dos +2,74 pp de soma diária; tirando os
três extremos o Δ vira **−0,54 pp**. E o acerto de sinal nos 27 dias de anúncio é
**48%** — cara ou coroa. Vale nas DUAS escalas da 15c, então a 15c não é o que
separa: a view não tem sinal, tem um dia.

**A medição da premissa já sabia disso e ninguém tinha ligado os pontos:**
`Premio_condicional.md` identifica 2025-04-10 como o extremo do grupo "incerto",
e a checagem de robustez de lá mostra a média do grupo caindo ao tirá-lo. O que
era ressalva de uma medição virou **o resultado inteiro** de um backtest.

**A B mede NEGATIVO (−1,38 pp)** e concentrada do mesmo jeito, com o sinal
trocado: sem os três extremos o Δ vira **+2,93 pp**. Acerto de sinal 49% em 210
dias. O P dela no fim da janela é **long XLE +1,04 · XLF +0,29 contra XLP −0,20 ·
XLU −0,19**, com TLT ≈ 0 — ortogonal ao da 2.3, como a 15g previu; o problema não
é duplicação, é que a view não prevê.

**🛑 Pendência de protocolo que continua de pé:** a 15g registra a ordem `DGS1
chegou → refazer o teste de sinal no vértice certo → só então empilhar`. Esta
rodada fez a última etapa **sem a do meio**, por instrução do dono, e para medir.
O **teste de sinal no `DGS1` segue não rodado**, e o precedente da D2b vale igual:
se sair invertido, não entra e **não se inverte**.

**Premissa declarada nesta rodada, e ela não estava escrita em lugar nenhum:** o
M3 pergunta quantos cortes acontecem **dentro de 2025**, então a taxa de fim de
ano de um balde é `taxa do FIM DE 2024 − 25bp × N`, não `taxa de hoje − 25bp × N`
— a leitura antiga contaria em dobro os cortes já entregues no ano (50 bps de
erro de nível em nov/2025). A espec da B só dizia "taxa_atual"
(`backtest_v1.M3_INICIO_DO_ANO`). É leitura da REGRA do mercado, não escolha de
parâmetro, mas fica declarada para quem revisar poder discordar.

**Nada fecha aqui.** 15a, 15b, 15c e 15g continuam abertas e a recomendação
implícita da tabela é do grupo, não minha.

---

## 16 (branch `Felipe`). Camada tática RECONSTRUÍDA — duas sleeves, medidas e REPROVADAS 🟡

> ⚠️ Numeração paralela por branch — ver o aviso no topo. Cite como "D16 do
> `Felipe`".

**Registro, não decisão.** Resposta à segunda metade da direção da seção 14
("reativar a camada tática com estratégias novas"), sessão de **2026-08-08**. As
duas sleeves estão **implementadas, testadas e FORA do backtest** (`tatica=()`
por default) — a entrega da 12c não mudou de número (+2,62 pp, conferido).

**Isto NÃO reabre a 12c.** Os três overlays antigos (`tatica_premio_anuncios`,
`tatica_drift_pos_fomc`, `tatica_gap_fds`) estão intocados, com `orcamento =
None`. O que entrou é um template novo ao lado deles.

### 16a. O que a 12c barrou tem conserto, e ele funcionou

A 12c desligou a camada porque o Δ era **monótono no orçamento** — a grade não
tinha ótimo interior e escolher a linha de cima era calibrar contra o resultado.
O conserto: **matar o parâmetro**, do mesmo jeito que a 15d matou o da tática de
prêmio ao virar view.

    dw = inv(δ·Σ) @ (direção × μ)        (`bl_optimizer.optimal_weights`)

- δ = 3,0 é **observável** (D7, medido no nosso SPY) e Σ é a amostral da D8;
- `μ` é MEDIDO por event-study expansivo (`tatica_drift_anuncio.estimate_drift_mu`),
  mesmo padrão do β das views e mesma proibição de lookahead;
- `μ` entra **encolhido pela própria dispersão**, com o fator ancorado na mesma
  convenção do Ω (`τ·Σ_ii / (τ·Σ_ii + se²)`) — sem isso um μ de 17 eventos
  entraria com confiança infinita, que é dar Ω = 0 a uma view.

**Nenhum parâmetro novo entrou.** Esta parte do desenho **sobreviveu ao teste** e
fica disponível para qualquer sleeve futura: é ela que permitiu medir sem
calibrar nada contra o resultado.

### 16b. As duas sleeves REPROVARAM — e a do FOMC morre por um achado sobre o dado 🛑

Medido em `Dump/analises/Tatica_reconstruida.md`
(`scripts/tatica_reconstruida.py`, 374 pregões, teto no tilt = 1):

| configuração | dias | excesso | Δ vs. desligada | P&L da sleeve sozinha |
|---|---|---|---|---|
| desligada (v1, 12c) | 0 | +2,62 pp | — | — |
| só drift FOMC (poly) | 158 | −3,06 pp | **−5,68 pp** | **−35,23 pp** |
| só drift CPI | 150 | +0,39 pp | **−2,23 pp** | **−5,31 pp** |
| as duas | 260 | −4,18 pp | −6,80 pp | −40,55 pp |

**A coluna que decide é a última**, e ela foi medida de propósito para separar
"a sleeve erra" de "a sleeve rouba o teto das views": é `Σ dw·r` no dw PEDIDO,
antes de qualquer corte. Negativa nas duas — **as sleeves perdem por conta
própria**, o teto não é o culpado.

**Sleeve do FOMC — o motivo é do dado, e é resultado a reportar:** a surpresa
(decisão realizada − `E_poly` da véspera) tem **mediana de 0,52 bps** em 17
reuniões, máximo 5,34. **O Polymarket acerta a decisão do Fed quase na mosca.**
Tomar direção pelo SINAL de um resíduo de 1 bp é condicionar em ruído de
discretização da própria PMF, e nenhum ajuste de tamanho conserta. É o oposto do
problema da 12c: lá faltava âncora para o tamanho, aqui falta sinal para a
direção.

**Sleeve do CPI:** a surpresa (Δ breakeven no dia, 6 positivas × 6 negativas) é
balanceada, mas o μ diz que depois de surpresa inflacionária o **TLT (nominal)
anda mais que o TIP (indexado)** — contrário à premissa que justifica o livro.
Mesma classe de inversão da transversal (15f) e da B em proxy (15g). **Terceiro
desenho seguido a sair invertido**, e pelo precedente da D2b **não se inverte**.

**Recomendação (do Felipe, decisão do grupo): a camada tática NÃO entra.** A 12c
fica de pé pelo mesmo resultado, agora por motivo mais forte — antes era "não sei
escolher o tamanho", agora é "medi o tamanho pela regra e as sleeves perdem".

### 16c. O que foi construído e fica no repositório

| | |
|---|---|
| Módulo | `src/tatica_drift_anuncio.py` (template das duas sleeves) |
| Testes | `tests/test_tatica_drift_anuncio.py` (11) |
| Medição | `scripts/tatica_reconstruida.py` → `Dump/analises/Tatica_reconstruida.md` |
| Dado novo? | **nenhum** — DFF, T10YIE e a PMF de FOMC já estavam no `data/` |
| Ligado? | **não** — `MontadorV1(tatica=())` por default |

**Insumo novo derivado, e ele serve a quem quiser retomar:**
`backtest_v1.decisoes_realizadas_fomc` lê no DFF a Δtaxa **decidida** em cada
reunião (0 ou −25 bps na janela, valores redondos). Não existia no projeto — a
2.3 usa `DTB3 − DFF` como *expectativa*, nunca a decisão realizada.

**Premissa declarada, única não-mecânica das duas sleeves:** a decisão do FOMC é
lida no DFF com janela para a frente. **Não é lookahead de preço** — a decisão é
pública às 14h ET do dia D e a sleeve só abre no close de D; o DFF é o
instrumento de leitura de um fato já público (a taxa efetiva só migra para o
novo alvo no dia seguinte). Está escrito no docstring de
`MontadorV1._surpresa_fomc_poly`.

**Nada fecha aqui.** Se o grupo quiser ligar mesmo assim, é decisão metodológica
sob o regime das seções 9/10.

---

## 17 (branch `Felipe`). Gate de sleeves — quatro candidatos triados e REPROVADOS antes de virar código 🟡

> ⚠️ Numeração paralela por branch — ver o aviso no topo. Cite como "D17 do
> `Felipe`".

**Registro, não decisão.** Sessão de **2026-08-08**, resposta ao pedido de
reconstruir a camada tática com o dado que já temos. **Nenhum módulo foi
escrito** — nenhum candidato passou na triagem. `MontadorV1(tatica=())` continua
o default e a entrega do v1 (+2,62 pp) não mudou (conferido, ver 17d).

### 17a. O que esta rodada corrige da D16 é a ORDEM, não o desenho

A D16 gastou 400+ linhas de módulo e 11 testes em duas sleeves que morreram por
motivo **de dado** — e os dois motivos cabiam numa tabela rodada ANTES do código.
Esta rodada mede primeiro: `scripts/gate_sleeves.py` →
`Dump/analises/Gate_sleeves.md`.

**O gate não tem corte numérico cravado** (cravar um seria threshold sem medição,
CLAUDE.md §6). No lugar do corte, ele carrega o **próprio grupo de controle**: as
duas sleeves reprovadas da D16 entram na mesma tabela, e o gate só é confiável se
reproduzi-las. Reproduz — `SPY +4,91 · TLT +1,37` (FOMC) e `TIP +0,21 · TLT
+1,31` (CPI), idênticos a `Tatica_reconstruida.md`.

| | o que mede |
|---|---|
| **G0** | pregões da janela em que o sinal existe |
| **G1** | mediana \|sinal\| ÷ Δ que UM tick de 1 centavo produz no sinal |
| **G2** | sinal de μ (`estimate_drift_mu` da D16, sem alterar) vs. o **declarado a priori** |
| **G3** | correlação com o sinal que as views 2.2, 2.3 e a candidata 15b já leem |

G4 (P&L da sleeve sozinha) ficou fora **de propósito**: exige backtest, backtest
exige o módulo, e o módulo é o que o gate se recusa a escrever antes da linha
passar.

### 17b. O achado, e ele mata uma FAMÍLIA inteira 🛑

**A revisão diária da crença do Polymarket anda MENOS que um tick.**

| candidato | G0 dias | G1 razão / tick | G2 | G3 maior \|corr\| |
|---|---|---|---|---|
| C1a revisão do M3 (nº de cortes) | 209 | **0,5×** | ❌ SPY −4,20 | −0,16 |
| C1b revisão da reunião (bps) | 334 | **0,2×** | ❌ SPY −2,75 · TLT −3,44 | −0,24 (div. 2.3) |
| C2a cauda da PMF de CPI | 289 | 19,5× | ❌ SPY +0,45 · TLT −1,31 | **−0,68 (entropia 15b)** |
| C2b cauda da PMF de reunião | 334 | 1,2× | ❌ TLT −0,87 | +0,58 (entropia 15b) |

**C1a e C1b abaixo de 1×**: o Δ típico de um pregão é menor que o deslocamento
que um centavo num único balde produz. É a versão FORTE do achado da D16 — lá o
poly acertava a decisão do Fed; aqui o próprio repreçamento diário dele vive
abaixo da granularidade do preço. **Qualquer sleeve que leia Δ de PMF de um dia
para o outro está condicionando em ruído de discretização.** Isso vale para
qualquer desenho futuro da família, não só para estes dois.

**C2a é o único com dispersão de verdade e morre nos outros dois critérios:** μ
invertido nos dois ativos do livro (contra a premissa declarada "SPY cai, TLT
sobe", e pela D2b não se inverte) e ρ = −0,68 com a entropia — massa de cauda e
entropia são o mesmo sinal com dois nomes, então ligar C2a com a view 15b seria a
dupla contagem da 15a. **Ressalva contra o próprio candidato:** parte do 19,5× é
degrau de grade (a média expansiva atravessa a troca de mercado e a grade do CPI
vai de 3 a 9 baldes); não muda o veredito, que é do G2 e do G3.

### 17c. Premissas declaradas ANTES de medir 🔴

São **categoria 3** (metodologia) e ficam registradas como declaradas, **não
fechadas** — o valor delas é terem sido escritas antes do event-study, que é o
que faz do G2 um teste em vez de racionalização. Sem isso, "a literatura não fixa
o sinal" (docstring de `tatica_drift_anuncio`) vira licença para aceitar qualquer
resultado medido.

- **C1a/C1b** — crença anda para mais afrouxamento → **SPY e TLT sobem**. Âncora:
  Bernanke-Kuttner, com **7 de 7** sinais já medidos nestes mesmos ativos em
  `Dump/analises/Surpresa_fomc_sem_ZQ.md`.
- **C2a/C2b** — mais massa nas pontas → prêmio de risco sobe → **SPY cai, TLT
  sobe** (fuga para qualidade). Livro **direcional** (ΣP ≠ 0), como a 15b.

### 17d. O que fica no repositório

| | |
|---|---|
| Script | `scripts/gate_sleeves.py` |
| Testes | `tests/test_gate_sleeves.py` (10) |
| Medição | `Dump/analises/Gate_sleeves.md` |
| Módulo novo em `src/`? | **nenhum** |
| Dado novo? | **nenhum** — M3, PMF de reunião, PMF de CPI e FRED já estavam no `data/` |
| Entrega mudou? | **não** — `tatica_reconstruida.py` devolve os mesmos +2,62 / −5,68 / −2,23 pp da D16 |

**Descartes por medição já registrada, feitos na triagem sem custar código:**
gap de fim de semana (seção 9), prêmio de anúncios como overlay (12c → virou a
view 15b), colapso de entropia pós-anúncio (mesma variável da 15b, mutuamente
exclusiva com ela), payrolls (bloqueado no `G10b` do Paulo — falta o realizado).

**O que isto NÃO diz:** que a camada tática é inviável. Diz que, no dado que
temos, os sinais de Polymarket que sobraram ou **não têm tamanho** (revisão
diária, abaixo do tick) ou **já pertencem a uma view** (cauda ≈ entropia). A
âncora de tamanho da D16 (`inv(δΣ)·μ` encolhido) segue de pé e sem uso — **o que
falta é sinal, não dimensionamento.**

### 17e. Inventário de cortes e condições de reabertura

`Dump/analises/Retomada_tatica.md` (escrito a pedido do dono, mesma sessão)
consolida as **11 views** e os **12 desenhos táticos** com o motivo de cada corte
e **o que teria de mudar** para reabrir. **Não decide nada** — a coluna de
reabertura lista condição, não recomendação.

Dois pontos de lá que interessam a esta decisão:

- **O experimento que nunca foi feito.** A D16 trocou DUAS coisas ao mesmo tempo:
  a âncora de tamanho (orçamento → `inv(δΣ)·μ`) **e** a fonte da surpresa (ΔDTB3
  → poly). A surpresa antiga **nunca rodou com a âncora nova**, e o ΔDTB3 tem
  dispersão onde o poly não tinha (σ 3,3 bps, 3 de 36 reuniões acima de 5 bps).
  É **uma linha no `gate_sleeves.py`**, não um módulo. Ressalva contra a própria
  ideia: a mediana COM SINAL do ΔDTB3 é +0,0 bps e a do valor absoluto não está
  medida — pode morrer na primeira linha.
- **Bloqueio de terceiro.** O `etf_open_daily.parquet` está em outra base de
  ajuste que o `etf_prices_daily.parquet` (`Premissa_taticas.md`). Enquanto
  durar, **nenhuma tática mede o retorno do PRÓPRIO dia do evento** — que é
  exatamente onde o achado transversal do projeto diz que a informação aterrissa.
  Conserto é um pull dos dois no mesmo dia: **módulo do Paulo**.

**Nada fecha aqui.** A recomendação da D16 (a camada tática não entra) fica de pé
com um motivo a mais, e a entrada continua sendo decisão do grupo.

---

## 18 (branch `Felipe`). Busca por views novas — régua do poly declarada e três candidatas triadas 🟡

> ⚠️ Numeração paralela por branch — ver o aviso no topo. Cite como "D18 do
> `Felipe`".

**Registro, não decisão.** Sessão de **2026-08-09**, a pedido do dono: duas frentes
de busca por views novas (arqueologia do repositório + literatura clássica),
limitadas a 3 propostas cada. **Nenhuma linha de código foi escrita.** A entrega do
v1 não foi tocada. O handoff detalhado das candidatas está em `leaveoff.md`.

### 18a. Régua declarada pelo dono nesta sessão 🟡 — precisa de ratificação do grupo

> **View que não lê o Polymarket não entra nem em discussão.**

Declarada verbatim pelo Felipe em 2026-08-09, ao ver as 6 propostas. **Não está
fechada como 🟢 porque não é decisão de um módulo só** — ela define o que conta como
view admissível no modelo, o que é premissa compartilhada (CLAUDE.md §1, categoria
3). Fica registrada como posição do dono da integração, **pendente de ratificação em
reunião**.

**Consequência medida, e é grande:** das 6 propostas geradas, **4 caem por esta
régua** — inclusive as duas mais baratas de implementar e a de melhor esperança
medida. Sobram 3, que são o conjunto inteiro admissível. Não é escolha de 3 entre 6.

**Trade-off para a reunião:** a régua protege a tese do desafio (BL *alimentado por
probabilidades do Polymarket*) ao custo de barrar sinais clássicos baratos que
melhorariam o backtest. As duas coisas são reais. **Quem decide é o grupo.**

### 18b. O que a régua barrou (inventariado para não ser redescoberto)

| proposta | fonte | por que caiu |
|---|---|---|
| Drift pós-FOMC (ΔDTB3) virado **view** | interna | não lê o poly. **Ressalva:** é a única tática do projeto que mediu **positivo** (+0,08 a +0,80 pp, D16), e o parâmetro que a matou (`orcamento` sem âncora) **deixa de existir** ao virar view — quem dimensiona passa a ser o BL. A célula `ΔDTB3 × inv(δΣ)·μ` **nunca foi rodada** |
| Ciclo FOMC semanas pares/ímpares (Cieslak, Morse & Vissing-Jorgensen 2019) | externa | não lê o poly; e a semana 0 se sobrepõe ao `drift_pos_fomc` **já ativo** |
| Reversão de curto prazo 5d (Lehmann 1990; Jegadeesh 1990) | externa | não lê o poly. Era a única cujo horizonte natural bate com **H = 1 dia** |
| Momentum setorial 12−1 (Moskowitz & Grinblatt 1999) | externa | não lê o poly; e descasamento de horizonte (paper é holding mensal, ~20 indústrias) |

**Se a reunião derrubar a régua 18a, o primeiro item volta na frente dos outros três**
— e custa uma linha no `gate_sleeves.py` para saber se vive (a mediana do |ΔDTB3|
nunca foi medida; se ficar perto do tick de 1 bp do FRED, morre no G1).

### 18c. As três candidatas admitidas — nenhuma aprovada

Detalhe completo em `leaveoff.md`. Resumo do status:

| candidata | estado | próximo passo | bloqueio |
|---|---|---|---|
| **C geopolítica, 2º episódio (Irã jun/2025)** | medição não rodada | uma linha no dict de `scripts/janela_negociavel.py:45-58` | nenhum — mas re-rodar no dado atual (o artefato não foi re-gerado pós-sessão 15) |
| **Transversal do CPI com β ortogonalizado** (ressuscita a 15f) | conserto proposto, não testado | teste de sinal **antes** do módulo | nenhum formal; risco técnico alto (ver abaixo) |
| **3.1 recessão com P direcional** | 🛑 **bloqueada** | reunião | **D2b** — ver 18d |

**Sobre a transversal:** a causa da morte está medida e corroborada por três
caminhos independentes (TIP dominado por **duração**, não por inflação). Mas o elo
que falhou **não foi o β — foi o transporte** do β contemporâneo para retorno futuro
(corr +0,06). Ortogonalizar ataca a causa declarada **sem garantia** de que o
transporte apareça. Ordem obrigatória (lição da 14a/D17): **medir antes de escrever
módulo.**

### 18d. Decisão que a 3.1 direcional exige do grupo 🛑

A 3.1 é o único caso do projeto com **sinal significante que a view não expressa**:
no par defensivo−cíclico t −0,46 a −1,05, mas **SPY +0,59% em 10 pregões, |t| > 2**.
O P neutro em mercado (`P[SPY] = 0`) apaga exatamente o que existe.

**O problema não é técnico, é de tese:** o coeficiente direcional medido é
**positivo**, e a tese original da view prevê **negativo**. Entrar como desenhada
perde; **inverter é o que a D2b proibiu explicitamente**.

**Pergunta para a reunião:** o grupo re-declara a tese a priori como **"prêmio de
medo pago"** (o mercado remunera quem carrega risco quando o medo sobe) — que é tese
diferente e defensável — ou mantém a 3.1 cortada?

Duas ressalvas para quem for decidir: (i) re-declarar tese **depois** de ver o sinal
é exatamente o vício que a D2b existe para barrar, então a declaração precisa ser
explícita e datada; (ii) **não há segundo mercado de recessão**, logo não existe o
teste fora da amostra que tornou o veredito da 2.4 confiável.

**Nada fecha aqui.** Nenhuma das três candidatas está aprovada, e a régua 18a
aguarda ratificação.

---

## 19 (branch `Felipe`). As três candidatas da D18 — MONTADAS e MEDIDAS 🟡

> ⚠️ Numeração paralela por branch — ver o aviso no topo. Cite como "D19 do
> `Felipe`".

**Registro, não decisão.** Sessão de **2026-08-09** (sessão 18), a pedido do
dono: montar e medir as três candidatas do `leaveoff.md`, **sem decidir o
destino de nenhuma**. A entrega do v1 não mudou — `Backtest_v1.md` sai byte a
byte idêntico e nenhuma candidata foi empilhada. Suíte inteira: 240 testes
passando.

**O que ficou no repositório:** `scripts/teste_sinal.py` (+ 5 testes) — promove
ao branch o teste que vivia no scratchpad e era pendência de reprodutibilidade
registrada no fim da 15g; `scripts/view_3_1_direcional.py`;
`view_3_1_recessao.build_view_direcional` (+ 3 testes); uma linha no dicionário
de `scripts/janela_negociavel.py`. Artefatos:
`Dump/analises/Teste_sinal.md` e `Dump/analises/Recessao_direcional.md`, mais o
`Janela_negociavel.md` re-gerado.

### 19a. Candidata 1 (view C, 2º episódio Irã jun/2025) — o veredito de 2026 NÃO se reproduz 🟡

Uma linha no dicionário de `scripts/janela_negociavel.py`, como a D18c previa.
Os 55 pregões do mercado de jun/2025 (2025-04-02 a 2025-06-20) nunca tinham
passado pelo teste de tradabilidade. Medido no XLE, que é o ativo da view:

| episódio | obs | gap (não negociável) | janela negociável | razão oc/cc | mediana dos 9 ativos |
|---|---|---|---|---|---|
| Irã 2026 (o que decidiu) | 27 | **+0,0606 · t +3,18** | −0,0183 · t −0,67 | **−44%** | +41% |
| Irã jun/2025 (fora da amostra) | 55 | +0,0578 · t +1,39 | +0,0478 · t +0,82 | **+46%** | **+83%** |

**A sensibilidade replica; o veredito não.** O coeficiente do gap sai
praticamente igual nos dois episódios (+0,0606 × +0,0578) — o mercado do poly
move o XLE com a mesma magnitude nas duas crises, o que é evidência real e vai
ao relatório. Mas as duas conclusões que sustentaram o corte caem no segundo
episódio: (i) nada é significante ali (t +1,39 no gap, com o DOBRO de
observações), e (ii) o efeito **não** morre na janela negociável — sobra 46% em
vez de −44%.

**Como ler isto, e as duas leituras são legítimas:** (a) o corte da C foi
decidido sobre 27 observações de um episódio e o segundo não o corrobora, logo a
evidência contra ela é mais fraca do que o registro sugere; (b) o segundo
episódio também não produz sinal significante, logo a C continua sem base para
entrar. **Nenhuma das duas é escolhida aqui.**

**Nota de encanamento (não é a candidata):** o `Janela_negociavel.md` publicado
não reproduzia o dado atual — o mercado de recessão ganhou 15 observações
(227 → 242) no re-pull da sessão 15 e vários coeficientes andaram na terceira
casa. Os números do Irã 2026 reproduzem **exatos**. O artefato foi re-gerado.

### 19b. Candidata 2 (transversal com β ortogonalizado) — REPROVADA, e o módulo não foi tocado 🛑

Ordem obrigatória da 14a/D17 cumprida: **o teste rodou antes do módulo**. O β
foi estimado contra o Δbreakeven residualizado do canal risk-on (retorno do SPY
e ΔDGS10), como a D18c propôs. `estimate_betas_breakeven` continua intacto.

**Controle embutido reproduz** (é o que autoriza ler o resto da tabela):

| view | h = 1 | h = 5 | h = divulgação | registrado antes |
|---|---|---|---|---|
| 2.2 (entrega) | t +0,57 · 53% | t +0,85 · 50% | t +0,50 · 58% | t +0,57 / 53% (15g) ✔ |
| 2.3 (entrega) | t +0,26 · 51% | t +0,23 · 56% | — | t +0,26 · 51%/56% (15f) ✔ |
| transversal (β cru) | t −1,08 · 49% | t −0,86 · 43% | **t −2,72 · 36%** | t −3,02 / 35% (15f) ✔ |
| **transversal (β ⊥ risk-on)** | t −0,90 · 49% | **t −2,36 · 47%** | t −1,12 · 37% | — |

**A ortogonalização conserta a causa declarada — e a view continua não
funcionando.** O P deixa de ser "cíclicos e energia contra duração" e vira o que
a tese sempre disse que era:

| variante | TIP | TLT | XLE |
|---|---|---|---|
| β cru | **−0,29** | −0,70 | +0,31 |
| β ⊥ risk-on | **+0,67** | −0,02 | +0,84 |

Ou seja: o diagnóstico das três medições convergentes (TIP dominado por duração,
15a/16b/17b) estava **certo**, e tirar duração e risk-on do regressor faz a view
ficar comprada em TIP, como a lógica de inflação pede. Mas o elo que falhou na
15f era o **transporte**, não o β — e ele piora: a corr entre coeficiente
preditivo e β contemporâneo vai de −0,48 para **−0,84** no horizonte da
divulgação, e o t de h = 5 passa a ser significativamente **contra** (−2,36).
Acerto de sinal em 37–49% em toda a tabela.

**Recomendação (do Felipe, decisão do grupo): a transversal continua fora, e a
15f não precisa ser reaberta.** Pela D2b não se inverte. **Custo desta rodada:
zero linha de módulo** — é a segunda vez que a ordem "medir antes de escrever"
paga (a primeira foi a D17), e isso é insumo de relatório sobre processo.

### 19c. Candidata 3 (3.1 com P direcional) — construída, medida, e o bloqueio MUDA DE NATUREZA 🛑

Construída a pedido do dono, **para medir**: `build_view_direcional` reusa o
`directional_P` da 15b (P[SPY] = 2, Σ|P| = 2, ΣP ≠ 0). **A entrada continua
bloqueada** — nada foi empilhado, nada foi decidido.

**O achado, e ele antecede a pergunta da D18d:** o coeficiente em que a
re-declaração de tese se apoiaria **troca de sinal dentro da própria amostra**.
SPY em h = 10, discordância `z(p_poly) − z(−spread)` padronizada de forma
EXPANSIVA (sem o z in sample que o `Nivel_divergencia_3_1.md` declarou como
ressalva):

| recorte | pregões | período | coef SPY (h = 10) | t |
|---|---|---|---|---|
| amostra inteira | 186 | 2025-04-04 a 2025-12-31 | **+0,40%** | +3,22 |
| 1ª metade | 93 | 2025-04-04 a 2025-08-18 | **+0,97%** | +6,52 |
| 2ª metade | 93 | 2025-08-19 a 2025-12-31 | **−0,35%** | −2,27 |

**As duas metades são significantes e apontam para lados opostos.** Não há
segundo mercado de recessão (a própria D18d registra isso), então não existe o
teste fora da amostra que tornou o veredito da 2.4 confiável — e agora sabemos
que não existe nem *dentro* da amostra.

**Consequência para a D18d, e ela é de agenda:** a pergunta registrada era "o
grupo re-declara a tese como *prêmio de medo pago*?". Medido, essa pergunta fica
**sem base empírica em qualquer das duas direções** — não porque a tese seja
falsa, mas porque o sinal que a sustentaria não é estável. A D18d pode ser
respondida sem discutir tese, o que **evita** o vício que a D2b existe para
barrar (re-declarar tese depois de ver o sinal).

**O que a medição confirma da premissa:** o P direcional de fato **captura o que
o P neutro apaga** — as duas montagens dão números diferentes nos mesmos dias, e
o desenho funciona. O problema não é a expressão da view; é o sinal.

**Ressalva honesta:** nos 126 pregões em que o β expansivo existe (2025-07-02 em
diante), **as duas** montagens medem negativo — mas esse recorte é
essencialmente a 2ª metade da tabela acima, então ele não é evidência
independente, é a mesma metade com outro nome. Está dito no artefato.

**Nada fecha aqui.** As três candidatas seguem sem destino; a régua 18a segue
pendente de ratificação.

---

**Próximo passo:** voltar para a Decisão 1.
