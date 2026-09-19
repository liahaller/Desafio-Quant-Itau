# Decisões do projeto — dossiê da entrega (código CONGELADO)

**Estado: semifinal. O código não muda mais.** Este arquivo deixou de ser fila de
trabalho e passou a ser o registro do que a estratégia **é** e do porquê de cada
escolha — o material de defesa na arguição.

**Overhaul de 2026-09-06 (sessão 39):** saiu tudo que não pode mais ser feito —
pendência de código, pedido a outro membro, condição de reabertura, "próxima
sessão", re-geração de artefato e pergunta para reunião que não acontece mais.
O motivo não é limpeza: ler como pendência o que já está entregue **já produziu
descrição errada da carteira** (ver D30). Nada foi reaberto e nenhuma decisão
mudou de estado — o histórico integral está no git.

Status: 🟢 fechada (é o que está no código) · 🟡 medida sem fechar (limitação
declarada) · 🔴 aberta — e o que resta aberto é **narrativa**, não modelagem.

## Estado congelado da entrega — a fonte da verdade

Vale esta tabela, e não o texto de nenhuma seção histórica abaixo. Verificável
em `scripts/backtest_v1.py` e no cabeçalho do `Dump/analises/Backtest_v1.md`.

| o que | valor entregue | onde está no código | decisão |
|---|---|---|---|
| views ativas | **quatro** — 2.2 inflação · 2.3 Fed · 15b incerteza · 15g B própria | `VIEWS_V1 = ("incerteza", "B")` | D23 |
| **camada tática** | **LIGADA** — sleeves **M4 recessão** (bloco k = 3, 5, 10) e **M9 Câmara** (k = 20), livro `+XLP −XLK` hedgeado | `carregar(..., sleeves=True)` | **D28.13** |
| camada tática ANTIGA (prêmio 1.3, drift pós-FOMC, gap de fds) | **desligada** | `tatica=()`, orçamentos `None` | D12c |
| régua do Ω (Lia) | **ligada**, nível 1 | `--regua` · `--regua-nivel 1` | D29 (o nível é a 6q dela) |
| teto de alavancagem | varredura {1, 2, 3, 5}; **referência = 1, no tilt** | `--tetos`, `teto_no_tilt` | D10a |
| banda de não-negociação | **sem banda** (`banda=None`) | — | D13 |
| custo | 2 bps por lado sobre o giro contra o peso derivado | `CUSTO_BPS_POR_LADO` | D8 · D9 |
| γ favorite-longshot | 1,0 (robustez em {1; 1,1; 1,25}) | `FL_GAMMA_V1` | D9 |
| **número da entrega** | **+33,2% líquido × +30,1% do SPY** (+3,04 pp), 374 pregões, breakeven 22,9 bps/lado | `Backtest_v1.md`, coluna `tilt ≤ 1` | D29 |

⚠️ **As seções abaixo descrevem o estado da data delas.** Onde uma delas disser
que a camada tática não entra (D12c, D16, D17, D26, D27), leia o banner de
supersessão: **a D28 reabriu a camada e a D28.13 a ligou na entrega.**

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

## 5. Definição operacional de "surpresa" (PEAD, 1.1) 🟢 (fechada pelo dono, 2026-08-11 — sessão 27)
Fórmula da surpresa. `1 − prob_atribuída`? Contínua ou por threshold?

**Decisão:** **`surpresa = resolução − probabilidade precificada na véspera`, CONTÍNUA
(sem threshold).** Fechada pelo dono em 2026-08-11, junto com o pacote da **D28**.

- **Contínua e não por faixa:** um threshold seria um parâmetro livre novo,
  escolhido sem medição — exatamente o que a regra 6 do `CLAUDE.md` barra. A
  forma contínua não introduz número nenhum.
- **"Véspera" é o slot pré-abertura do dia anterior à resolução**, que é o
  último dado conhecido antes do evento. Não é escolha de janela: é o que o
  dado tem (a série do poly termina na véspera — medido no `Gate_PEAD.md`).
- **Não é definição nova:** é o **placeholder declarado** que o `Gate_PEAD.md`
  já usou e que o `Candidatos_taticos.md` carrega por escrito. O que muda é o
  status — deixa de ser placeholder e passa a ser a definição do projeto, o que
  torna a medição do `Gate_PEAD.md` válida em vez de provisória.

**O que ela destravou, e o desfecho:** a **1.1 PEAD** fora do Fed foi medida com
o `CPIAUCSL` (item 8 da D28) e **REPROVOU** (D28.c). A definição deixou de ser
gargalo e virou resultado.

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
> **Nada foi decidido agora — só recolocado.**

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
| Camada tática | ~~entra: prêmio de anúncio + drift pós-FOMC~~ — **SUPERADO**: desligada na D12c, e o que entrou na entrega é a **v2** (sleeves M4/M9, D28.13) |
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

**Como isto terminou, e é o que a entrega mostra:** o grupo **nunca escolheu um
teto**. A entrega reporta a **grade inteira** {1, 2, 3, 5} nos dois escopos e cita
**1 no tilt** como referência (10a). Reportar a varredura em vez de cravar a
linha de melhor número é a saída registrada — não é pendência esquecida.

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

**O que sobrou disto na entrega:** o corte de 13/08 não precisou ser acionado —
a régua da Lia chegou e entrou (D29). O que ficou desta seção é o **teto de
referência 1, no tilt**: é o escopo de todas as varreduras do projeto e a coluna
que o relatório e a apresentação citam.

---

## 11. Sessão de 2026-08-07 (sessão 5) — view B fora do v1 🟢 (provisória)

> ⚠️ **SUPERADA em 2026-08-10 (D23).** A B **voltou e está na entrega**, como
> **15g**, com β próprio contra o ΔDGS1. O que esta seção barrou foi o *desenho*
> que reusava os β da 2.3 (P literalmente idêntico), não a view.

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

**Como terminou:** a B voltou por um terceiro caminho, que não estava nesta
lista — β próprio contra o ΔDGS1, medido na 15g e ligado na D23. O ZQ nunca
apareceu de graça e deixou de ter consumidor.

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

Fica registrado como limitação do relatório.

### 12c. Camada tática fora do v1 🟢 (fechada pelo dono, 2026-08-07 — sessão 8)

> ⚠️ **SUPERADA pela D28 (2026-08-11).** A camada tática foi **reaberta** e a
> **v2 está LIGADA na entrega** (D28.13 — sleeves M4/M9). O que continua
> desligado é exatamente o que esta seção desligou: os três overlays antigos
> (prêmio 1.3, drift pós-FOMC, gap de fim de semana), com `orcamento = None`.

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
`Felipe` para a entrega do v1 de duas views.

---

## 15 (branch `Felipe`). Duas views novas — CANDIDATAS, construídas e não ligadas 🟡

> ⚠️ Numeração paralela por branch — ver o aviso no topo. Cite como "D15 do
> `Felipe`".

**Registro, não decisão.** Resposta à direção da seção 14, sessão de
**2026-08-08**. As duas estão **implementadas, testadas e FORA do backtest** —
nenhuma foi empilhada, nenhum número de entrega mudou. O que segue é o que o
grupo precisa decidir antes de qualquer uma entrar.

> **Atualização de 2026-08-10 (sessão 23) — as três subdecisões desta seção
> FECHARAM por instrução do dono, nenhuma foi à reunião:** **15a** dupla leitura
> aceita · **15b** P direcional aceito · **15c** escala = entropia crua. Com
> isso a **15g não tem mais bloqueio de decisão** e a **15b tem só o item 4 da
> D22** (medição do dono do módulo, não decisão). A **transversal desta tabela
> continua fora** pela 15f/19b — nada aqui a reabre.

| | View CPI transversal | View de incerteza de anúncio |
|---|---|---|
| Módulo | `src/view_cpi_transversal.py` | `src/view_incerteza_anuncio.py` |
| Testes | `tests/test_view_cpi_transversal.py` (8) | `tests/test_view_incerteza_anuncio.py` (8) |
| Dado novo? | **nenhum** | **nenhum** |
| Sinal | a divergência da 2.2 (E_poly[CPI] − breakeven) | entropia da PMF na véspera |
| P | seção cruzada dos 9 (`P_from_betas`, P[SPY] = 0) | **direcional**: 2 no SPY |
| Q | (ΣP·β) × divergência_líquida / dias_até_divulgação | (ΣP·β) × incerteza_líquida |

### 15a. As duas views leem sinal que já está em uso 🟢 (FECHADA pelo dono, 2026-08-10 — sessão 23)

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

**DECISÃO (dono, 2026-08-10 — instrução explícita, não vai à reunião): a dupla
LEITURA é aceita.** Duas views podem ler a mesma fonte do Polymarket desde que
ocupem dimensão nova no P — que é exatamente o item 4 da D22, já medido para a
15g (**ângulo 95,6°** contra a 2.3, corr −0,34).

**O que isto libera:** a **15g** (B com β próprio) deixa de travar aqui. Era o
único bloqueio dela — a objeção "lê a PMF de reunião que a 2.3 já lê" fica
respondida pelo princípio, não caso a caso.

**O que isto NÃO faz — e é o ponto de não confundir:** dupla leitura ≠ dupla
contagem. O que continua proibido é **P colinear**, e quem barra isso é o item 4
da D22, não esta seção. Em particular:

- a **transversal continua fora**, por reprovar no teste de sinal (15f, e a
  variante ortogonalizada na 19b) — nada disto se reabre por esta decisão;
- a **B original** (seção 11) continua morta: lá o P era *literalmente idêntico*
  ao da 2.3, que é o caso que o item 4 barra;
- as duas views que ainda não têm o ângulo medido (**15b** e **C**) não passam
  a estar liberadas — a medição segue obrigatória.

**Consequência para o Ω, registrada:** com duas views lendo a mesma fonte, a
correlação entre elas existe mesmo com P ortogonal. O Ω da Lia é diagonal por
construção (`diag(P·τΣ·Pᵀ)`), logo **não a enxerga**. Não é bug — é limitação a
declarar no relatório, junto com a das quatro views.

### 15b. A view de incerteza é a PRIMEIRA direcional do projeto 🟢 (FECHADA pelo dono, 2026-08-10 — sessão 23)

Todas as views estruturais são neutras em mercado por construção (`P_from_betas`
crava P[SPY] = 0 exato). O prêmio de Savor-Wilson é prêmio de MERCADO, e
expressá-lo com P[SPY] = 0 é exatamente o que impediu a view 3.1 de dizer o que
tinha a dizer (D2b). Por isso o P dela é direcional.

**O que não muda:** Σ|P| = 2 (decisão 4) e a identidade Q = P·E[r].
**O que muda e é do grupo:** com ΣP ≠ 0 a view mexe na exposição direcional, e a
obrigação 5a de `views_common.py` (centragem se troca em TODAS as views juntas)
precisa ser lida antes de empilhar esta com as neutras.

**DECISÃO (dono, 2026-08-10 — instrução explícita, não vai à reunião): o P
direcional é ACEITO.** Uma view do modelo pode apostar na direção do mercado
(`P[SPY] = +2`, ΣP ≠ 0), e não só no preço relativo entre ativos. O motivo é o da
própria seção: o prêmio de Savor-Wilson **é** prêmio de mercado, e a alternativa
neutra não é uma versão mais conservadora da view — é a view esvaziada, o mesmo
que matou a 3.1 (D2b).

**O que o projeto passa a assumir, e precisa estar no relatório:**

1. **O tilt deixa de ser neutro em mercado** nos 27 pregões de anúncio, onde a
   carteira ganha exposição direcional por decisão do modelo. Não é efeito
   colateral: é o conteúdo da view.

   ⚠️ **CORREÇÃO da própria linha acima, medida em 2026-08-10 poucas horas depois
   de ela ser escrita** (`Dump/analises/Ortogonalidade.md`): a premissa de que o
   tilt *era* neutro antes da 15b **é falsa**. As views ditas neutras carregam
   ΣP mediano de **+0,96 (2.2) · +1,74 (2.3) · +1,24 (15g)** — `P[SPY] = 0` é
   exato, mas o resto do vetor é líquido COMPRADO nos outros 8 ativos. A 15b
   não introduz direcional no modelo: ela **declara** o que já existia sem
   rótulo. Ver a obrigação 5a abaixo, que deixa de ser formalidade.
2. **A exposição direcional passa a ter dono.** Antes ela vinha inteira da perna
   de mercado (`w_mkt`); agora uma view a move. Quem dimensiona continua sendo o
   BL (τ, Ω, Σ) — não há parâmetro de tamanho novo.

**Obrigação 5a — MEDIDA no mesmo dia, e o resultado é maior que esta decisão.**
O `P_from_betas` crava `P[market_asset] = 0` exato, mas **os outros 8 pesos não
precisam somar zero**. Medido (`Dump/analises/Ortogonalidade.md`):

| view | ΣP mediano | Σ\|P\| | leitura |
|---|---|---|---|
| 2.2 inflação | **+0,961** | 2,00 | ≈ +1,48 comprado × −0,52 vendido |
| 2.3 Fed | **+1,736** | 2,00 | ≈ +1,87 comprado × −0,13 vendido |
| 15g B própria | **+1,241** | 2,00 | ≈ +1,62 comprado × −0,38 vendido |
| 15b incerteza | +2,000 | 2,00 | direcional por desenho |

**As views ditas neutras nunca foram neutras.** `P[SPY] = 0` significa "a view não
toma posição no SPY" e **nunca** significou "a view não tem exposição
direcional": o vetor é líquido COMPRADO nos outros 8 ativos, que têm β próprio ao
mercado. A exposição direcional agregada da carteira tem mediana **+2,94** nos
pregões sem a 15b e **+4,27** nos 27 com ela.

**DECISÃO (dono, 2026-08-10): o componente direcional é ACEITO como
intencional — não se re-centra nada.** Saída (a) das três mapeadas; as outras
eram (b) re-centrar todas as views juntas e (c) manter como limitação sem
declará-la. A regra do docstring fica satisfeita pelo caminho de cima: o
direcional passa a ser **declarado**, e por isso a cláusula "se não for
intencional, troque a centragem de TODAS as views juntas" não dispara.

**Consequência de relatório, e ela não é opcional:** a frase "as views são
neutras em mercado" **não pode ser dita** — nem sobre o v1 de duas views. A
descrição correta passa a ser: o P não toma posição no ativo de mercado, e a
carteira carrega exposição direcional líquida, declarada e medida.

**Correção de percurso registrada, porque ela é o próprio argumento:** a primeira
versão desta seção (escrita horas antes, na mesma sessão) dizia que "o tilt
deixa de ser neutro **com a 15b**". A medição desmentiu — a 15b não introduz o
direcional, ela **declara** o que já existia sem rótulo em três views. A
obrigação 5a estava no docstring desde o começo e nunca tinha sido executada.

### 15c. A ESCALA da incerteza muda o resultado, e não há default honesto 🟢 (FECHADA pelo dono, 2026-08-10 — sessão 23)

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

**DECISÃO (dono, 2026-08-10 — instrução explícita, não vai à reunião): entra a
ENTROPIA CRUA demeanada por família** (`escala="entropia"`), não o percentil.

**O custo da escolha, declarado para não ser redescoberto:** é a escala com o
**t mais fraco das duas** na medição da premissa (+0,32 contra +1,96). Pela D22
isso **não reprova** — sinal fraco não é impedimento, o que reprova é a tese ser
contrariada, e nenhuma das duas escalas inverte. Mas a frase "a entropia crua
linear não sustenta a premissa" acima **continua valendo** e vai ao relatório
como limitação da view, não como nota de rodapé.

**O que a escolha NÃO muda, e é o que tira o peso dela:** a 15h mediu as duas
escalas no backtest e o achado é o mesmo nas duas — o Δ é **um pregão**
(2025-04-10) e o acerto de sinal é 48% em ambas. A 15c nunca foi o que separava
a view de si mesma. Efeito prático da escolha no número entregue: **+3,89 pp
(crua) contra +2,32 pp (percentil)** de Δ sobre o v1 — e o de baixo é o que
sobrevive melhor à retirada dos extremos (−0,09 pp contra −0,54 pp), ou seja, a
escala escolhida é a de número maior e sobrevivência pior. Registrado aqui de
propósito: quem ler o +3,89 pp precisa achar esta linha.

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

### 15g. A 4ª view — a B com β PRÓPRIO 🟢 (medida em 08/08, ENTROU na entrega pela D23)

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
**Desfecho: a B ENTROU na entrega em 2026-08-10** (D23), depois de a 15a fechar e o item 4 da D22 ser medido (ângulo 87,5°).

**Ressalva menor, registrada:** a base usa o `DFF` (taxa EFETIVA), ~4 bps abaixo
do meio da banda de então. É viés de nível constante, absorvido pela demeanagem
expansiva — mas está aqui para ninguém redescobrir depois.

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

**Premissa declarada nesta rodada, e ela não estava escrita em lugar nenhum:** o
M3 pergunta quantos cortes acontecem **dentro de 2025**, então a taxa de fim de
ano de um balde é `taxa do FIM DE 2024 − 25bp × N`, não `taxa de hoje − 25bp × N`
— a leitura antiga contaria em dobro os cortes já entregues no ano (50 bps de
erro de nível em nov/2025). A espec da B só dizia "taxa_atual"
(`backtest_v1.M3_INICIO_DO_ANO`). É leitura da REGRA do mercado, não escolha de
parâmetro, mas fica declarada para quem revisar poder discordar.

**Fechadas depois:** 15a, 15b e 15c em 10/08, e as duas views **entraram na
entrega** pela D23. Esta tabela é o registro obrigatório de atribuição — está
aqui para o número da entrega não ser lido como desempenho das views novas.

---

## 16 (branch `Felipe`). Camada tática RECONSTRUÍDA — duas sleeves, medidas e REPROVADAS 🟡

> ⚠️ **A recomendação desta seção ("a camada tática não entra") foi SUPERADA
> pela D28.** As duas sleeves *desta* seção continuam fora e reprovadas; a
> camada que entrou na entrega é outra — transversal, M4/M9 (D28, D28.13). O
> que sobreviveu daqui é a **âncora de tamanho `inv(δΣ)·μ`** (16a), que é a que
> a camada v2 usa.

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

> ⚠️ **Registro histórico.** Os quatro candidatos daqui seguem reprovados, mas a
> generalização do G1 caiu na D26 e a camada foi reaberta na D28. O que
> sobrevive é o **protocolo**: medir antes de escrever módulo.

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

### 17c. Premissas declaradas ANTES de medir 🟡

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

## 18 (branch `Felipe`). Busca por views novas — régua do poly declarada e três candidatas triadas 🟡

> ⚠️ Numeração paralela por branch — ver o aviso no topo. Cite como "D18 do
> `Felipe`".

**Registro, não decisão.** Sessão de **2026-08-09**, a pedido do dono: duas frentes
de busca por views novas (arqueologia do repositório + literatura clássica),
limitadas a 3 propostas cada. **Nenhuma linha de código foi escrita.** A entrega do
v1 não foi tocada. O handoff detalhado das candidatas está em `leaveoff.md`.

### 18a. Régua do poly declarada pelo dono 🟢 (absorvida pela D22, item 1)

> **View que não lê o Polymarket não entra nem em discussão.**

Declarada verbatim pelo Felipe em 2026-08-09, ao ver as 6 propostas. **Não está
fechada como 🟢 porque não é decisão de um módulo só** — ela define o que conta como
view admissível no modelo, o que é premissa compartilhada (CLAUDE.md §1, categoria
3). **Absorvida pela D22 (item 1) em 2026-08-10** — deixou de ser posição
pendente e virou régua fechada.

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

**Medido depois (D21c):** o primeiro item reprova no G1 — mediana |ΔDTB3| = 1 bps,
exatamente 1,0× o tick de publicação do FRED. A régua 18a não custou a
oportunidade.

### 18c. As três candidatas admitidas — nenhuma aprovada

Detalhe completo em `leaveoff.md`. Resumo do status:

| candidata | estado | próximo passo | bloqueio |
|---|---|---|---|
| **C geopolítica, 2º episódio (Irã jun/2025)** | medição não rodada | uma linha no dict de `scripts/janela_negociavel.py:45-58` | nenhum — mas re-rodar no dado atual (o artefato não foi re-gerado pós-sessão 15) |
| **Transversal do CPI com β ortogonalizado** (ressuscita a 15f) | conserto proposto, não testado | teste de sinal **antes** do módulo | nenhum formal; risco técnico alto (ver abaixo) |
| **3.1 recessão com P direcional** | 🛑 **bloqueada** | reunião | **D2b** — ver 18d |

**Desfecho das três:** foram montadas e medidas na **D19** — nenhuma entrou. A
transversal ⊥ risk-on reprovou (19b), a 3.1 direcional tem coeficiente que troca
de sinal dentro da amostra (19c) e a **C** foi cortada na **23f**.

**Sobre a transversal:** a causa da morte está medida e corroborada por três
caminhos independentes (TIP dominado por **duração**, não por inflação). Mas o elo
que falhou **não foi o β — foi o transporte** do β contemporâneo para retorno futuro
(corr +0,06). Ortogonalizar ataca a causa declarada **sem garantia** de que o
transporte apareça. Ordem obrigatória (lição da 14a/D17): **medir antes de escrever
módulo.**

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

**Consequência:** a saída mapeada para a 3.1 era o grupo **re-declarar a tese**
como *prêmio de medo pago*. Medida, ela fica **sem base empírica em qualquer das
duas direções** — não porque a tese seja falsa, mas porque o sinal que a
sustentaria não é estável. A 3.1 fica fora sem precisar discutir tese, o que
**evita** o vício que a D2b existe para barrar.

**O que a medição confirma da premissa:** o P direcional de fato **captura o que
o P neutro apaga** — as duas montagens dão números diferentes nos mesmos dias, e
o desenho funciona. O problema não é a expressão da view; é o sinal.

**Ressalva honesta:** nos 126 pregões em que o β expansivo existe (2025-07-02 em
diante), **as duas** montagens medem negativo — mas esse recorte é
essencialmente a 2ª metade da tabela acima, então ele não é evidência
independente, é a mesma metade com outro nome. Está dito no artefato.

**Desfecho:** **nenhuma das três entrou.** A transversal ficou fora (19b), a 3.1
ficou fora (19c) e a C foi cortada na **23f**. A régua 18a virou o **item 1 da
D22**, fechada em 10/08.

---

## 20 (branch `Felipe`). A régua da Lia chegou — convenção, volume e eixo da escolha de 13/08 🟡

> ⚠️ Numeração paralela por branch — ver o aviso no topo. Cite como "D20 do
> `Felipe`".

**Registro, não decisão.** Sessão de **2026-08-10** (sessão 19), a partir da
`RESPOSTA5_Felipe_calendario_e_nivel.md` da Lia. A régua do `c` está fechada e
implementada do lado dela (`lia/omega.py`, 66 testes, 601 decisões da 2.2,
90,3% ativas). Deste lado nada de comportamento mudou: a suíte sai de 240 para
**244 testes** (os 4 novos são do script da 20c) e o `Backtest_v1.md` não foi
re-gerado.

### 20b. O eixo da escolha de 13/08 é o NÍVEL da régua, não o `c` das curvas 🟡

As duas convenções são recíprocas e as duas estão em uso:

- **eixo das curvas** (o `curva_c.py` daqui e o gráfico dela): `c ∈ (0,1]` é
  **confiança**, maior = mais peso;
- **eixo da entrega** (o que `omega_fallback` recebe): `c >= 1` é
  **multiplicador de incerteza**, maior = menos peso. `c_curva = 1/c_regua`.

Medido por ela nas 601 decisões da 2.2, traduzido para o eixo das curvas:

| nível | mediana | p95 | pior mercado |
|---|---|---|---|
| 1 | 0,953 | 0,805 | 0,362 |
| 3 | 0,865 | 0,521 | 0,047 |
| 5 | 0,785 | 0,338 | 0,006 |

**A régua vive no topo da curva:** com nível 1 ela ocupa `[0,36 · 1,0]`, e a
região onde a Σ|w| desaba (`c = 0,01`) exigiria nível ≈ 95 para a mediana — não
é escolha, é impossibilidade. Escolher "um `c`" na tabela do `Curva_c.md` é
portanto escolher um ponto que a régua não alcança.

Re-medido deste lado na faixa alcançável (`Dump/analises/Curva_c_faixa_regua.md`,
grade constante = LIMITE da régua, já que ela age por view):

| c (eixo da curva) | incerteza | Σ\|w\| pedida mediana | dias de ruína | excesso (teto no tilt) |
|---|---|---|---|---|
| 1,000 (hoje) | 1,00 | 192,0 | 35 | +4,07 pp |
| 0,953 (mediana, nível 1) | 1,05 | 187,3 | 34 | +4,18 pp |
| 0,785 (mediana, nível 5) | 1,27 | 168,7 | 27 | +4,63 pp |
| 0,362 (pior mercado, nível 1) | 2,76 | 102,0 | 16 | +5,82 pp |

Duas leituras, e as duas são insumo da reunião:

1. **O teto continua obrigatório em toda a faixa que a régua alcança.** Mesmo no
   extremo (todas as views tratadas como o pior mercado da amostra) sobram
   **16 dias de ruína** no irrestrito e Σ|w| mediana de **102**. A conclusão do
   passo (3) da Lia fica de pé agora medida no eixo certo, não por extrapolação.
2. **No centro a régua quase não move resultado** (+4,07 → +4,18 pp): o efeito
   dela está na **cauda**, e grade constante não consegue mostrá-lo. Para medir
   o efeito de verdade é preciso a série de `c` **por decisão**, que ela ofereceu
   mandar — pedido feito na resposta.

**Não fecha nada:** nível e teto saem juntos, uma vez só, pelo protocolo
anti-overfit da seção 10 — e não por iteração contra esta tabela.

**✅ A `RESPOSTA6` foi SEGURADA e depois ENVIADA, tudo em 2026-08-10 (sessão
23).** Ficou retida por decisão do dono até o conjunto de views fechar, foi
reescrita quando fechou (D23e) e o dono a enviou no fim da sessão.

**Por que a espera valeu:** o pedido nomeia as views uma a uma, e na versão
original nomeava só `"2.2_inflacao"` e `"2.3_fed"`. Enviada de manhã, ela teria
produzido uma série de `c` cobrindo **metade do modelo** — e o erro só apareceria
com o arquivo na mão, em cima do corte de 13/08. É o mesmo modo de falha que a
sessão 22 pegou no mesmo arquivo: **o que roda calado é o caro.**

**O que a reescrita acrescentou, além das quatro chaves:** o aviso de que a 15b é
direcional e de que as views ditas neutras nunca foram neutras (muda a descrição
da carteira na seção dela); a marcação de que os números da
`Curva_c_faixa_regua.md` são da carteira de duas views; a resolução de "e dia sem
view?" como **fato de interface** e não como pergunta (o `_checa_chaves` faz
casamento exato contra as views vivas do pregão); e a seção 9 com a assimetria da
**D24**, explicitamente marcada como coisa que não se responde agora.

**O risco que o dono aceitou ao segurar, e ele não se materializou:** o corte da
10a é **13/08**. Se o conjunto de views não tivesse fechado a tempo, valeria o
plano B pré-registrado (`c = 1`, teto no tilt, nível 1). Fechou no mesmo dia.

### 20c. Cristalização perto do evento — o achado (b) dela, medido contra a tática 1.3 🟡

A Lia passou como insumo: a proximidade do evento reprovou de novo na régua
dela, com folga maior no alvo por desfecho (+0,29 a +0,72), e o sinal é "longe
do evento o mercado se move mais; perto, ele cristaliza". Isso toca a 1.3
porque o sinal dela é a **entropia da PMF no slot pré-abertura do próprio dia do
anúncio** — dentro da janela onde a cristalização estaria agindo.

Medido em `scripts/cristalizacao_entropia.py` (+ 4 testes) →
`Dump/analises/Cristalizacao_entropia.md`, nas três famílias de anúncio:

| família | variação total: mínimo | variação em d = 0 | desvio da entropia: 6–10 dias → d = 0 |
|---|---|---|---|
| FOMC | 0,0376 (1–2 dias) | **0,0610** | 0,274 → **0,305** |
| CPI | 0,0640 (6–10 dias) | **0,1717** | 0,205 → 0,202 |
| Payrolls | 0,1363 (11–20 dias) | **0,3270** | 0,043 → **0,098** |

**A cristalização é real, mas não é monótona — ela reverte no último slot, que é
justamente o que a sleeve lê.** Nas três famílias o mínimo de variação cai numa
faixa intermediária e d = 0 volta a ser alto (no CPI e nos payrolls, o mais alto
da tabela). E o número que decide o desenho — a **dispersão do sinal entre
anúncios em d = 0** — não colapsa: é igual (CPI) ou maior (FOMC, payrolls) que a
das faixas distantes. Ou seja: **o achado dela não invalida a modulação da 1.3**;
`dw = orcamento · sinal` continua diferenciando anúncio de anúncio.

**Ressalvas, que são do registro e não da conversa:** (i) o slot lido tem n = 7
(FOMC), 12 (CPI) e 13 (payrolls) — o desvio em d = 0 é a estatística mais frágil
da tabela; (ii) a grade aqui é diária pré-abertura, a dela é de 12h, e a medida
dela é contra erro de previsão, não movimento cru — as duas leituras não são o
mesmo teste e a divergência de forma pode ser só isso. **Observação devolvida a
ela na resposta; nada do módulo dela foi tocado.**

**Desfecho:** a 1.3 **nunca entrou como overlay** — o prêmio de anúncio virou a
**view 15b** (D23) —, e a camada que entrou na entrega é a **v2** (D28). O
`orcamento` foi abandonado de vez: item 9 da D28, tamanho pela âncora
`inv(δΣ)·μ`, zero parâmetro livre.

---

## 21 (branch `Felipe`). Régua ligada, teste de sinal completo e o experimento pendente da D18b 🟡

> ⚠️ Numeração paralela por branch — ver o aviso no topo. Cite como "D21 do
> `Felipe`".

**Registro, não decisão.** Sessão de **2026-08-10** (sessão 20). Três frentes de
execução e **nada fechado** — nenhuma view entrou, nenhuma sleeve entrou, nenhum
parâmetro foi escolhido. A entrega segue intacta: `Backtest_v1.md` re-gerado e
**byte a byte idêntico**, suíte de **244 → 248 testes**.

### 21a. A régua da Lia entra POR DECISÃO no loop — encanamento, não escolha

O `aplicar_veto` existia desde 07/08 e **nunca tinha sido chamado**: o
`run_backtest` só aceitava `incerteza` ESCALAR, que aplica o mesmo `c` a todas as
views. Isso é o LIMITE da régua, nunca a régua — e a 20b registra que o efeito
dela é de **cauda**, que grade constante não consegue medir por construção.

Agora `run_backtest(regua=callable(data) -> (ativa, incerteza))` roteia pelo
`aplicar_veto`: veto tira a view de P e Q antes do `stack_views`, e o vetor sai
alinhado à ordem que o `omega_fallback` exige. `regua` e `incerteza` são
mutuamente exclusivos (a grade sobrescreveria a régua em silêncio).

**Não muda nada da entrega** — `regua=None` é o default e o caminho do v1 não
passa por lá. O que muda é que, quando a **série de `c` por decisão** chegar (o
pedido do item 2 da `RESPOSTA6`), medir o efeito real é rodar o backtest, não
escrever módulo. Era o único item de código no caminho crítico do corte de 13/08.

### 21b. O teste de sinal ficou completo — e a pendência de protocolo da 15h está paga 🟢

O `scripts/teste_sinal.py` cobria 4 linhas; agora cobre 6 —
entraram a **15b (incerteza)** e a **B com β próprio (15g)**, que tinham sido
medidas no BACKTEST (15h) e nunca no teste de veto. Entrou também a coluna
`h = 0` (o próprio pregão de D, que é o que o backtest ganha e o **único**
horizonte da 15b, cujo Q é o close-to-close do dia do anúncio).

**O controle reproduz, o que autoriza ler o resto** (`Dump/analises/Teste_sinal.md`):

| view | n | h = 0 | h = 1 | h = 5 | registrado antes |
|---|---|---|---|---|---|
| 2.2 (entrega) | 274 | t +0,29 · 50% | t +0,57 · 53% | t +0,85 · 50% | t +0,57 / 53% ✔ |
| 2.3 (entrega) | 325 | t +0,59 · 50% | t +0,26 · 51% | t +0,23 · 56% | t +0,26 · 51%/56% ✔ |
| **incerteza (15b)** | **27** | **t +0,06 · 44%** | t −0,17 · 41% | t +0,93 · 41% | — |
| **B com β próprio (15g)** | **210** | t +0,05 · 51% | **t +0,33 · 51%** | **t +0,65 · 53%** | t +0,33 · 51% / +0,65 · 53% ✔ |

**O que isto fecha:** a 15h registrou como pendência de protocolo que "o teste de
sinal no `DGS1` segue não rodado" — a medição da sessão 16 existia só no chat e
no `LOG.md`. Agora ela roda **a partir do branch** e sai idêntica. A B **passa o
veto** (não sai invertida), como a 15g já dizia; continua sem entrar, porque o
teste é veto e não certificado (15f) e ela mede −1,38 pp no backtest (15h).

**A 15b é indistinguível de zero no horizonte que é o dela** (t +0,06, acerto
44% em 27 anúncios) — coerente com o achado da 15h de que o Δ dela era **um
pregão**. Duas medições independentes agora dizem o mesmo.

**Achado lateral, contra a candidata já reprovada:** a transversal ⊥ risk-on dá
**t −2,02 no `h = 0`**, significativamente ao contrário também no horizonte que o
backtest ganha. Reforça a 19b; não muda o veredito.

### 21c. O experimento pendente da D17e/D18b rodou — e morre no G1 🟢 (medido)

O item registrado como "**uma linha no `gate_sleeves.py`**": a D16 trocou de uma
vez a âncora de tamanho (orçamento → `inv(δΣ)·μ`) **e** a fonte da surpresa
(ΔDTB3 → poly), então a fonte ANTIGA nunca rodou com a âncora nova. Rodou
(`Dump/analises/Gate_sleeves.md`, linha `C3`):

| | medido |
|---|---|
| G0 | 37 reuniões, 2022-01-26 → 2026-07-29 (janela maior que as outras linhas — o ΔDTB3 existe desde 2022) |
| **G1** | mediana \|ΔDTB3\| = **1 bps** = **1,0×** o tick de publicação do FRED |
| **G2** | μ `SPY +0,55 ❌ · TLT +0,97 ❌` — invertido contra a Bernanke-Kuttner que o controle declara igual |
| G3 | −0,56 com a entropia de FOMC (15b) |

**A ressalva que a D17e levantou contra a própria ideia se confirmou:** o sinal
tem o tamanho do tick da fonte. **Consequência de agenda, e é o motivo de ter
rodado antes da reunião:** a D18b registra que "se a régua 18a cair, este item
volta na frente dos outros três". **Medido, ele não volta** — reprova pelos
mesmos critérios que reprovaram os candidatos que leem o poly. A 18a foi absorvida pela **D22 (item 1)** no dia seguinte, e esta medição
mostra que ela não custou a oportunidade.

## 22 (branch `Felipe`). Régua de admissão de views 🟢 (FECHADA pelo dono, 2026-08-10 — sessão 21)

**Instrução do dono, verbatim:** "a view precisa apenas ler o polymarket, atuar na
bolsa e não ter sua teoria desprovada por testes" + "coloque a ortogonalidade como
parte da régua" + "pode registrar como D22 FECHADA. não será discutida".

**Não vai à reunião.** Fechada por instrução explícita, sem ratificação do grupo.

### 22a. A régua — quatro itens, todos necessários

Uma view entra na estratégia se, e só se, cumpre os quatro:

1. **Lê o Polymarket.** O sinal da view vem de preço ou PMF de mercado do poly.
2. **Atua na bolsa.** A view se expressa em ETFs do universo decidido (D1).
3. **Teoria não desprovada por teste.** Nenhuma medição contradiz a tese
   declarada da view.
4. **Ortogonal ao que já está dentro.** A view ocupa dimensão nova: ângulo alto
   entre o P dela e o das views ativas, sem ρ alto no sinal-fonte.

**Sinal fraco NÃO é impedimento.** |t| baixo, acerto de sinal perto de 50% e Δ
negativo no backtest **não reprovam** uma view. O que reprova é a tese ser
contrariada pelo dado — o precedente D2b ("não se inverte") segue valendo, agora
como conteúdo do item 3.

### 22b. O que a D22 muda no que já estava registrado

- **Absorve a régua 18a.** O item 1 **é** a 18a ("view que não lê o Polymarket
  não entra"). A 18a deixa de estar 🟡 pendente de ratificação: seu conteúdo
  entra fechado aqui. As quatro propostas que ela barrou (drift ΔDTB3 como view,
  reversão 5d, momentum setorial 12−1, ciclo FOMC) **seguem barradas**, agora
  pelo item 1 da D22.
- **Formaliza o critério de dupla exposição.** Era o precedente mais aplicado do
  projeto sem nunca ter sido escrito como regra — derrubou F (×C), H (×2.3×B), a
  B original (P idêntico ao da 2.3) e a C2a (ρ −0,68 com a entropia da 15b), e é
  o único motivo pelo qual a **15g sobreviveu** (ângulo 95,6° com a 2.3). Com o
  item 4, F e H **continuam mortas** — sem ele, voltariam à mesa, porque passam
  os itens 1, 2 e 3.
- **Não revoga o teste de sinal como VETO (15f).** Ele continua sendo a forma de
  medir o item 3: reprova quem sai significativamente **invertido**, não quem sai
  fraco. Nenhuma view do v1 "passa" nele (a 2.3 dá t +0,26), e isso é esperado.
- **Não revoga a atribuição obrigatória (15h).** "Sem os 3 maiores" e acerto de
  sinal continuam obrigatórios — não como nota de corte, mas para o número do
  backtest não ser lido como desempenho da view.

### 22c. Efeito imediato nas candidatas

Aplicada às candidatas de `Candidatos.md`:

| View | 1 poly | 2 bolsa | 3 tese | 4 ortogonal | Situação |
|---|---|---|---|---|---|
| **15g** B com β próprio | ✅ | ✅ | ✅ t +0,33 | ✅ **95,6° medido** | ~~trava na D15a~~ → **D15a fechada em 10/08: sem bloqueio** |
| **15b** incerteza | ✅ | ✅ | ✅ t +0,06 | ⬜ **não medido** | ~~D15b/D15c~~ → **fechadas em 10/08; resta só o item 4** |
| **C** geopolítica | ✅ | ✅ | ✅ | ⬜ **não medido** | trava na janela negociável **+ item 4** |

O item 4 **cria trabalho novo**: a 15b e a C nunca tiveram o ângulo do P delas
medido contra o das views ativas. Para a 15b isso é especialmente relevante — ela
é direcional (P[SPY] = 2) e a C2a já mostrou ρ −0,68 entre a entropia dela e
outro sinal do projeto. É medição, não decisão: entra na fila do dono do módulo.

**A 3.1 direcional segue fora** — falha o item 3 (β troca de sinal dentro da
amostra, +0,97% na 1ª metade e −0,35% na 2ª, ambos significantes). Removida do
`Candidatos.md` por instrução do dono nesta sessão.

### 22e. O item 4 medido nas duas candidatas — e o que conta como "ρ alto" 🟢 (FECHADA pelo dono, 2026-08-10 — sessão 23)

Medição em `Dump/analises/Ortogonalidade.md` (`scripts/ortogonalidade.py`, 374
pregões, escala da 15b = entropia crua).

**Achado de método, e ele muda como o item 4 deve ser aplicado daqui em diante:**
o ângulo **não testa view direcional**. O P da 15b é `[SPY = 2, 0…]` e o das
neutras sai de `P_from_betas`, que crava `P[SPY] = 0` EXATO — o produto interno é
zero **por construção**, então o ângulo dá 90,000° contra qualquer view neutra,
em qualquer amostra. Para uma view direcional o item 4 se decide **inteiro no
ρ**. Quem reaplicar a régua precisa saber disto, ou vai ler um 90° como
aprovação forte quando ele é tautologia.

| par | ângulo mediano | ρ Pearson | ρ Spearman | dias |
|---|---|---|---|---|
| 2.2 × 2.3 (as duas da entrega) | 77,9° | −0,197 | −0,380 | 239 |
| 2.2 × **15g** | 87,5° | **+0,673** | **+0,765** | 168 |
| 2.3 × **15g** | 70,9° | −0,462 | −0,520 | 203 |
| 2.2 × **15b** | 90,0° (tautológico) | −0,132 | −0,269 | 13 |
| 2.3 × **15b** | 90,0° (tautológico) | +0,193 | +0,284 | 19 |
| 15g × **15b** | 90,0° (tautológico) | −0,091 | −0,043 | 15 |

**DECISÃO (dono, 2026-08-10): ρ +0,673 NÃO reprova. A 15g cumpre o item 4 e
entra.**

**Consequência que precisa estar escrita, porque é o que um leitor vai cobrar:**
com isto a barra do "ρ alto" da D22 passa a estar **acima de 0,673** — não por
um número escolhido, mas por precedente, do mesmo jeito que a D2b virou regra a
partir de um caso. Nenhum threshold foi cravado (seria parâmetro sem medição,
CLAUDE.md §6); o que existe é um caso julgado. Quem for aplicar a régua a uma
view futura compara com este precedente, não com uma constante.

**O que sustenta a decisão, para a ata:** expectativa de inflação e trajetória do
Fed são economicamente ligadas — o ρ é **real, não artefato de encanamento**. E o
que o item 4 existe para impedir é **dupla contagem no BL**, que se dá pelo P:
nesse eixo a 15g está a 87,5° da 2.2. Duas views podem ler sinais correlacionados
e ainda assim pedir posições diferentes.

**Limitação que fica de pé:** o Ω é diagonal (`diag(P·τΣ·Pᵀ)`), logo **não
enxerga** essa correlação. Vale para o relatório junto com a mesma ressalva da
D15a.

**Ressalva de amostra na 15b, registrada:** os ρ dela saem de **13 a 19 pregões**
de sobreposição — ela só vive em 27 dias de anúncio. Passa como medido; não é
número robusto, e está aqui para ninguém citá-lo como se fosse.

**Segunda aplicação, no mesmo dia — a view C (candidata).** Medida com o mesmo
script, contra as quatro ativas:

| C contra | ângulo mediano (k = 3) | ρ Pearson (k = 3) | dias |
|---|---|---|---|
| 2.2 inflação | 88,7° | **+0,827** (spearman +0,674) | **25** |
| 2.3 Fed | 108,6° | +0,107 | 62 |
| 15g B própria | 116,5° | +0,241 | 46 |
| 15b incerteza | 90,0° (tautológico) | −0,827 | **4 — sem valor** |

**DECISÃO (dono, 2026-08-10): o ρ da C com a 2.2 NÃO reprova — mesmo critério
já aplicado à 15g.** O mecanismo é o mesmo tipo: escalada no Irã → petróleo →
expectativa de inflação, que é o sinal da 2.2. Correlação real de fonte, com P a
88,7° — não é dupla contagem no BL.

**O que isto acumula, e precisa estar visível:** a barra do "ρ alto" da D22 sobe
de novo, agora para **acima de 0,827** — e desta vez sobre **25 dias**, contra os
168 da 15g. Dois precedentes na mesma sessão, na mesma direção. Se um terceiro
caso aparecer, o item 4 estará operando **só pelo ângulo** na prática, e vale
dizer isso em vez de manter um critério que nunca barrou ninguém.

### 22d. Alcance

A D22 é régua de **views estruturais** (linha de P/Q do Black-Litterman). A
camada tática (overlay sobre os pesos) usa os mesmos quatro itens em
`Candidatos_taticos.md`, mas soma as condições de camada já registradas e não
revogadas aqui: escopo (decisão 10), tamanho com âncora (12c) e sinal acima do
tick da fonte (G1, D17).

---

## 23 (branch `Felipe`). A estratégia passa a ter QUATRO views 🟢 (fechada pelo dono, 2026-08-10 — sessão 23)

> ⚠️ Numeração paralela por branch — ver o aviso no topo. Cite como "D23 do
> `Felipe`".

**O que fechou:** a 15b (incerteza de anúncio) e a 15g (B com β próprio) saíram
de candidatas e entraram na entrega. `scripts/backtest_v1.py::VIEWS_V1` deixou de
ser `()`. Nenhuma das duas foi ligada por resultado — as quatro exigências da D22
foram verificadas uma a uma, e as três decisões humanas que travavam foram
fechadas por instrução explícita do dono, sem ir à reunião.

**Cadeia de decisão, para a ata:** D15a (dupla leitura aceita) · D15b (P
direcional aceito) · D15c (entropia crua) · D22e (item 4 medido; ρ +0,673 não
reprova) · obrigação 5a (direcional declarado intencional, não se re-centra).

### 23a. As quatro views e a régua da D22

| view | 1 poly | 2 bolsa | 3 tese (teste de sinal) | 4 ortogonal | dias |
|---|---|---|---|---|---|
| **2.2 inflação** | ✅ PMF de CPI | ✅ TIP/TLT | t +0,29 (h=0) · 50% | — (incumbente) | 274 |
| **2.3 Fed** | ✅ PMF de reunião | ✅ 9 ativos | t +0,59 (h=0) · 50% | — (incumbente) | 325 |
| **15b incerteza** | ✅ entropia da PMF | ✅ SPY | t +0,06 (h=0) · 44% | ✅ ρ ≤ 0,19 | **27** |
| **15g B própria** | ✅ PMF do M3 | ✅ XLE/XLF vs. XLP/XLU | t +0,33 (h=1) · 51% | ✅ 87,5° · ρ +0,673 | **210** |

**Nenhuma das quatro "passa" no teste de sinal, e isso é esperado** — a 15f
estabeleceu que ele é **veto e não certificado**: reprova quem sai
significativamente invertido, não quem sai fraco. As quatro são indistinguíveis
de zero; nenhuma sai invertida.

### 23b. Registros obrigatórios da D22 — atribuição e concentração 🛑

A D22 exige que "sem os 3 maiores" e o acerto de sinal estejam escritos **antes**
de a view entrar, não depois. Fonte: `Dump/analises/Views_novas.md`
(`scripts/views_novas.py`), teto no tilt = 1, γ = 1,0, 374 pregões. A base é o
**v1 anterior de duas views** (+4,07 pp).

| view | Δ vs. v1 anterior | Σ dos Δ diários | **sem os 3 maiores** | acerto de sinal |
|---|---|---|---|---|
| **15b** (entropia crua) | +3,89 pp | +2,74 pp | **−0,54 pp** | **48%** (13/27) |
| **15g** (β próprio, DGS1) | **−1,38 pp** | −0,96 pp | +2,93 pp | **49%** (102/210) |
| **as duas juntas** | +2,17 pp | +1,52 pp | +2,51 pp | 49% (109/222) |

**O que estes números dizem, e é o oposto de "as views funcionam":**

- **A 15b é um pregão.** O Δ dela vem de **2025-04-10** (choque tarifário, SPY
  −4,38%), que sozinho vale +3,21 pp. Tirados os três extremos, o Δ **vira
  negativo**. O acerto de sinal em 27 anúncios é 48% — cara ou coroa. Duas
  medições independentes dizem o mesmo: o teste de sinal dá t +0,06 no horizonte
  que é o dela.
- **A 15g mede NEGATIVO** no backtest (−1,38 pp), e concentrada do mesmo jeito
  com o sinal trocado. Acerto 49% em 210 dias.
- **Pela D22 nada disso reprova** (sinal fraco não é impedimento). Está aqui para
  que o **+6,24 pp da entrega não seja lido como desempenho das views novas.**

**Limitação de cobertura, declarada:** a 15b vive em **27 de 374 pregões** (só
dia de anúncio, por desenho) e a 15g em **210** (o M3 acaba em 2025-12-10 e não
há mercado de trajetória de 2026 no `data/`).

### 23c. O que mudou no número da entrega

Escopo de referência (teto no tilt = 1), `Dump/analises/Backtest_v1.md`:

| | v1 anterior (2 views) | **entrega (4 views)** |
|---|---|---|
| excesso × SPY | +4,07 pp | **+6,24 pp** |
| retorno líquido | +34,2% | **+36,4%** |
| sharpe | 1,19 | **1,27** |
| Σ\|w\| média | 1,93 | 1,94 |
| custo de breakeven | 35,9 bps/lado | **34,5 bps/lado** |
| views ativas por dia | — | 2,24 |

O sinal do resultado **não depende do γ** na varredura de robustez (+6,24 a
+6,96 pp em γ ∈ {1; 1,1; 1,25}).

### 23d. Três consequências que a entrada cria, e nenhuma é opcional

1. **🛑 A carteira não é neutra em mercado — e nunca foi.** ΣP mediano de +0,96
   (2.2), +1,74 (2.3), +1,24 (15g), +2,00 (15b). A frase "as views apostam só em
   preço relativo" **não pode aparecer no relatório**, nem descrevendo o v1 de
   duas views. Medição e decisão na 15b/obrigação 5a.
2. **O Ω é diagonal e não enxerga correlação entre views.** Com a 15g e a 2.2 a
   ρ +0,673 no sinal-fonte, isso deixa de ser hipotético. Limitação de relatório
   (D15a, D22e), não bug.
3. **🛑 Limitação declarada — nem toda varredura irmã foi re-gerada.** As
   páginas de varredura leem o default do `carregar`, mas alguns `.md` salvos
   são de configurações antigas (o pior é o `Curva_orcamento.md`, que ainda
   anuncia a camada desligada pela 12c). **A carteira entregue é a do
   `Backtest_v1.md` e só ela** — número de página de varredura não descreve a
   entrega.

### 23f. A view C foi medida até o fim — e trava em decisão ANTERIOR a ela 🟡

**Registro, não decisão.** Medida na mesma sessão, a pedido do dono, na ordem
que a D14a manda (veto antes de código de produção).

**Item 3 (tese não desprovada) — PASSA.** `Dump/analises/Teste_sinal.md`,
grade k ∈ {1…5}, controle reproduzindo:

| k | n | h = 0 | h = 1 |
|---|---|---|---|
| 1 | 72 | t −0,43 · 44% | t −0,68 · 53% |
| 2 | 68 | t −0,75 · 53% | t −0,50 · 53% |
| 3 | 64 | t +1,29 · 55% | **t +1,44 · 56%** |
| 4 | 60 | t +0,41 · 47% | t +0,10 · 53% |
| 5 | 56 | t +0,56 · 55% | t −0,62 · 45% |

Nenhum k sai invertido com significância. Pela D22 isso **não reprova**.

**Item 4 (ortogonalidade) — PASSA, com o ρ liberado pelo dono** (ver 22e):
ângulo de 88,7° a 160,9° contra as quatro ativas; ρ +0,827 com a 2.2 julgado
como não reprovando.

**🛑 O k NÃO tem critério que o fixe — e o teste que existia para isso foi
executado e deu negativo.** `Dump/analises/Absorcao_C.md`
(`scripts/absorcao_C.py`): a espec 2.4 item 6 pré-registrou "*o perfil decide*",
isto é, o k é onde a resposta acumulada assenta. Medido nos dois episódios
separados:

| lag k | fração da resposta acumulada (XLE) — jun/2025 | 2026 |
|---|---|---|
| 0 | −0,66 | −0,43 |
| 1 | −0,83 | +0,20 |
| 2 | −0,29 | +0,84 |
| 3 | **+0,97** | +0,03 |
| 4 | −1,03 | +0,97 |
| 5 | −0,23 | +1,03 |

**corr entre as duas curvas: +0,08.** A resposta acumulada oscila com amplitude
maior que o próprio nível e os dois episódios não concordam sobre onde o efeito
chega. **O perfil não identifica k** — que era o terceiro dos três desfechos
mapeados antes de medir, e é resultado, não falha da medição.

**Achado que corrobora o corte original da C por um quarto caminho:** o **lag 0
é positivo nos dois episódios** (+0,0606 e +0,0313) e é o único lag em que os
dois concordam em sinal. Tudo depois disso é ruído. O lag 0 é exatamente o **gap
de abertura**, que não é negociável — e `lagged_poly_view` **recusa k < 1** por
construção ("sem defasagem não há tese"). Ou seja: o único lag com sinal coerente
é o que a view estruturalmente não pode usar. É o mesmo padrão já medido na
eleição 2024, na recessão 2025 e na tática de fim de semana (D14, item 3).

**🛑 E há um bloqueio ANTERIOR ao k, que nunca tinha mordido: a DECISAO-4.1.**
`Dump/analises/View_C_backtest.md` (`scripts/view_C_backtest.py`):

| k | backtest empilhado com as 4 views |
|---|---|
| 1 | roda — **Δ −6,40 pp** contra a entrega |
| 2 a 5 | **bloqueado** pelo `stack_views` |

O `stack_views` recusa empilhar views com `horizonte_q_dias` diferentes — guarda
que FALHA ALTO de propósito (`src/bl_integration.py`). O Q da C é **acumulado em
k dias**; o das outras quatro é de **1 dia**. Somar os dois é somar km/h com km.
**A C só convive com as outras em k = 1**, e para qualquer k ≥ 2 a entrada dela
exige fechar a D4.1 — decisão de metodologia, aberta desde o começo do projeto e
que só agora encontrou um consumidor.

**O nó, e ele é fechado:** o único k que a D4.1 permite (k = 1) é o único k que
**inverte entre os episódios** — t +2,13 em jun/2025 contra t −1,60 em 2026 — e o
que mede **−6,40 pp** no backtest, com acerto de sinal de 40%. Os k que o teste
de sinal favorece (k = 3) são os que a D4.1 bloqueia.

**DECISÃO (dono, 2026-08-10 — sessão 23): saída (c). A view C fica FORA, e as
três medições vão ao relatório como resultado.** As alternativas descartadas
ficam na ata: (a) fechar a D4.1 e medir a C em k ≥ 2 — mexeria no empilhamento
de TODAS as views a seis dias da entrega; (b) entrar em k = 1 — o único k
permitido é o que o próprio dado contradiz.

**Por que este corte é diferente do de 04/08, e é o ponto que vai ao relatório:**
o corte original disse "o efeito aterrissa no gap" a partir de **um** episódio,
com 27 observações, e a D19a o enfraqueceu ao medir um segundo episódio que não
o reproduzia. Agora o mesmo veredito volta por um **caminho independente** — a
curva de absorção, que não olha janela negociável nenhuma — e com os dois
episódios concordando exatamente no lag 0. **A C não é cortada por número ruim:
é cortada porque a premissa de que existe atraso a explorar foi testada pela
primeira vez e não se sustenta.**

**O que a C entrega ao relatório sem entrar na carteira:**

1. **O poly move o XLE, e move igual nos dois episódios** (+0,0606 e +0,0313 no
   lag 0; coeficiente de gap +0,0606 × +0,0578 na D19a). A fonte tem conteúdo.
2. **O efeito inteiro chega enquanto a bolsa está fechada.** Quarta medição
   independente do mesmo padrão — eleição 2024, recessão 2025, Irã e tática de
   fim de semana (D14 item 3). Deixa de ser observação e vira **achado sobre o
   limite da fonte de dados**.
3. **A D4.1 ganhou um consumidor e um caso concreto.** Ela estava aberta desde o
   começo do projeto sem nunca morder; agora existe um exemplo medido do que ela
   impede e por quê. Vai ao relatório como limitação conhecida do desenho, não
   como pendência esquecida.

**A D4.1 NÃO é fechada aqui.** Continua aberta; o que muda é que deixa de estar
no caminho crítico da entrega, já que nenhuma view do v1 tem `horizonte_q_dias`
diferente de 1.

### 23e. O conjunto de views está FECHADO 🟢 (dono, 2026-08-10)

**A estratégia entrega com QUATRO views: 2.2 · 2.3 · 15b · 15g.** Com a decisão
da 23f (a C fica fora), **não há candidata restante** — o `Candidatos.md` fica
sem nenhuma view em estado candidato pela primeira vez desde que foi criado.

---

## 25 (branch `Felipe`). Resposta à `RESPOSTA7` da Lia — três fechamentos 🟢 (fechadas pelo dono, 2026-08-11)

> Contexto: a Lia respondeu ao pedido da `RESPOSTA6` em
> `RESPOSTA7_Felipe_quatro_views.md`. A resposta devolveu duas decisões e uma
> pergunta bloqueante. Fechadas todas em `Dump/trocas/RESPOSTA7_Lia_cristalizacao_nivel_e_81_dias.md`,
> **enviada pelo dono em 2026-08-11** (o `RECADO_Paulo_G10b_sem_consumidor.md` saiu junto).

### 25a. Os 81 dias inativos da 15g — ACEITOS 🟢 (fechada pelo dono, 2026-08-11)

A régua da Lia desativa a `B_trajetoria_propria` em **81 de 345 dias (23,5%)**,
todos entre 20/09 e 10/12/2025, todos com motivo `sem_par_adjacente`.

**A causa não é qualidade de dado, e isso muda a leitura do número.** A partir de
set/2025 os baldes "nenhum corte" e "1 corte" pararam de ser cotados (141 e 84
slots sem leitura) porque se tornaram **impossíveis** — o Fed já cortara mais que
isso em 2025. Toda linha da janela passa a ter ao menos uma faixa sem leitura, e a
regra 6e (slot com faixa ausente não entra no cálculo de variação) mata o par. A
janela está **cheia** (6 de 6 slots): **bucket extinto com mercado funcionando**,
não buraco de coleta e não livro degenerado.

**Decisão: opção (a) — aceitar.** A 15g roda em **264 dias em vez de 345** e a
causa vai declarada no relatório, creditada à medição da Lia.

**As duas rejeitadas, e o motivo de cada uma:**

- **(b) tratar do lado do Felipe** (o `c` está no CSV mesmo nas linhas inativas):
  seria passar por cima da semântica da régua num caso específico — o mesmo vício
  que a 6e existe para evitar, só que escondido no meu módulo em vez de no dela.
- **(c) levar à reunião de 13/08** (a régua passaria a excluir faixa morta na
  janela inteira, uniformemente nas quatro views): mudar o instrumento de medida a
  dois dias de escolher **nível e teto com esse mesmo instrumento** contraria o
  protocolo anti-overfit da seção 10. **Fica registrada como melhoria pós-v1** —
  se for feita, que seja uniforme nas quatro views e **antes** de qualquer escolha
  de parâmetro.

**A régua da Lia não muda.** Nenhum pedido foi feito ao módulo dela.

### 25d. Duas declarações de relatório que a resposta dela obriga

1. **A régua foi calibrada em 2.2 e 2.3 e está sendo aplicada a QUATRO.** Vai
   declarado assim nas duas seções — não como se as quatro tivessem passado pelo
   teste de monotonicidade. O que sustenta a extensão: a régua mede propriedade do
   **mercado** (movimento da PMF, fechamento do livro), não da view.
2. **O `c` mediano de 1,2215 da família payrolls da 15b não é comparável** ao
   1,0120 da 2.3: o G5 do Paulo cobre `2.2`, `2.3` e `B`, não os mercados de
   emprego. **G5 de payrolls NÃO foi pedido** — são 13 dias e o portão só *remove*
   decisões, então a falta dele não infla o `c`.

### 25f. A régua entrou em produção — e o veto é um canal separado do nível 🟢 (medido)

`market_inputs.regua_por_decisao` lê o CSV dela e devolve o `callable(data,
nomes)` do loop; o `run_backtest` passou a informar as **views vivas do pregão**
à régua (antes ela só recebia a data, e sem a lista o filtro seria adivinhação).
O `bl_integration.nomes_ativos` virou público para as duas pontas usarem a mesma
lista. **Nada da entrega muda:** sem régua o backtest sai no `+6,24 pp` idêntico.

**Cobertura conferida antes de confiar:** nos 374 pregões, **nenhuma view viva
ficou sem linha** no CSV; as 29 divergências são todas no outro sentido (linha
sem view viva) e o filtro as descarta. A falta continua sendo `ValueError`.

**O achado que separa dois efeitos** (`Dump/analises/Curva_c.md`, tabela nova no
eixo do nível):

| nível | views/dia | Σ\|w\| pedida mediana | dias de ruína | excesso (tilt ≤ 1) |
|---|---|---|---|---|
| sem régua | 2,24 | 220,5 | 33 | +6,24 pp |
| **0 (só veto)** | **1,99** | **177,3** | 31 | +6,16 pp |
| 1 | 1,99 | 174,3 | 28 | +5,98 pp |
| 5 | 1,99 | 146,6 | 26 | +4,74 pp |
| 8 | 1,99 | 130,3 | 24 | +3,48 pp |

1. **O veto não tem nível.** O `ativa = False` sozinho já tira 0,25 view/dia e
   21% da Σ|w| pedida, antes de qualquer dosagem. A reunião de 13/08 escolhe
   **parte** do efeito da régua, não o efeito.
2. **A conclusão do passo (3) da Lia sobrevive no eixo certo e com quatro
   views:** a ruína do irrestrito **nunca zera** (24 dias no nível 8). O teto é
   obrigatório em toda a faixa alcançável — agora medido com a régua real, não
   com grade constante.
3. **🛑 O excesso cai monotonicamente com o nível.** Escolher o nível olhando
   essa coluna escolheria **zero**. É exatamente o que o protocolo anti-overfit
   da seção 10 existe para impedir, e está declarado assim no artefato.

**Correção factual devolvida à Lia:** o `c` **não** está no CSV nas linhas
inativas — `c_nivel1` é vazio em **152/152**. A opção (b) dos 81 dias (que ela
ofereceu como "usar o `c` das linhas inativas sob tua responsabilidade") não
existia no arquivo. Não muda a 25a. Do lado do Felipe o NaN é **repassado**, não
preenchido com 1,0: a view sai de P e Q e o `c` dela nunca chega ao Ω.

### 25g. Bug de registro pego na re-geração: as views estavam HARDCODED 🛑

O cabeçalho do `Curva_c.md` dizia `views ativas: **2.2 e 2.3** (a B fora do v1
pela decisão 11)` — texto fixo no `curva_c.py`, escrito quando eram duas views e
**sobrevivente à D23**. A primeira re-geração desta sessão saiu descrevendo uma
carteira que não era a medida. Agora a lista é **derivada da rodada**
(`res.diagnostics`), como já era o `n_views`.

**Mesmo modo de falha da D17e** (bloqueio do `etf_open_daily` propagado sem abrir
a fonte) e da linha da 15h ("já medido" que era metade): **registro que envelhece
não levanta exceção**. A régua que fica: campo que descreve a rodada sai da
rodada, nunca do texto.

Segundo caso na mesma sessão, e vale registrar junto: o `--regua` do `curva_c.py`
tinha caminho relativo fixo, então rodar contra a cópia do Paulo (`--raiz
/outro`) faria a tabela do nível — o insumo de 13/08 — **sumir calada**. O
default passou a seguir o `--raiz`; só `--regua ""` desliga, e desliga explícito.

## 26 (branch `Felipe`). A generalização do G1 da D17 caiu — e a camada tática reprova por MOTIVO NOVO 🟢 (registro, 2026-08-11 — sessão 25)

> ⚠️ **SUPERADA no mesmo dia, pela D27/D28 (sessão 27).** O caminho que esta
> seção declara esgotado é o de **ler o repreçamento diário do poly**; o que
> abriu a camada foi outro eixo (livro transversal neutro + incremento), medido
> na D27 e admitido na D28.

> ⚠️ Numeração paralela por branch — ver o aviso no topo. Cite como "D26 do
> `Felipe`".

**Registro, não decisão.** Nada aqui fecha e nada aqui reabre escopo — a
reabertura da camada continua sendo decisão de grupo. O que muda é **o motivo**
pelo qual ela não entra, e o motivo importa porque determina o que se tenta
depois. Conclusões completas em `Conclusoes.md`.

**O que estava escrito e não se sustenta.** O `Gate_sleeves.md` generaliza o
achado da D17 assim: *"qualquer sleeve que leia Δ de PMF de um dia para o outro
está condicionando em ruído de discretização"*. A frase vale para o `k` que a
D17 mediu, **não para a série** — o tick é fixo e o erro de discretização no
incremento fica preso em ~1 tick por mais que `k` cresça, enquanto o movimento
verdadeiro acumula (`Premissa_G1.md`):

| | k=1 | k=3 | k=10 | k=20 |
|---|---|---|---|---|
| M3 trajetória do Fed | 0,5× | **1,2×** | 2,9× | 3,7× |
| C1b reunião do FOMC | 0,2× | 0,5× | **1,6×** | 2,4× |

**O veredito da D17 sobrevive; a justificativa muda.** Acumular resolve o
problema de **tamanho** e não produz **previsão** (`Gate_M3_acumulado.md`): o M3
acumulado reprova no G2 em todos os seis lookbacks da grade, com a premissa
herdada da D17 palavra por palavra. E o **G3 degrada exatamente onde o G1
melhora** (−0,19 em k=1 → −0,42 em k=20, contra a entropia da 15b), o que fecha
a janela pelos dois lados.

**Duas candidatas nunca medidas passam a ter evidência CONTRA** (`Premissa_tendencia.md`):
variance ratio do M3 entre 0,97 e 1,18 e nenhuma autocorrelação ex-ante com
|t| ≥ 2. A *1.2 momentum* e a *velocidade de ajuste* leem o movimento da crença
para prever o próximo movimento da crença, e esse encadeamento não existe. Pela
régua D22 isso é **tese contrariada pelo dado**, não sinal fraco — a diferença
que o `Candidatos_taticos.md` registra como decisiva. **Não estou marcando as
duas como reprovadas:** quem move candidato de estado é o dono.

**O que NÃO foi tocado, e é o que sobra:** a **1.1 PEAD** lê a *resolução*, não
o Δ diário — nenhuma medida desta sessão diz coisa alguma sobre ela. Ela segue
travada pela **decisão 5** (definição operacional de "surpresa"), que está 🔴
aberta e vazia desde que foi fechada "sem objeto" em 2026-07-09. **É o gargalo
número um da reativação, e é humano.** A **3.2 event-driven** também segue não
medida, e o teste que falta é de uma linha: quanto do movimento sobra do
fechamento do dia do salto em diante.

**Correção de um achado meu, dentro da própria sessão:** li o crescimento da
mediana como "mais rápido que √k, logo tendência". Era artefato — em k=1 a
maioria dos dias tem variação zero, o que prende a mediana. O variance ratio diz
1. Fica registrado porque a leitura errada chegou a ser comunicada ao dono antes
de ser medida.

**Nada em `src/` foi tocado.** O `referencias_g3` saiu de dentro do `main` do
`gate_sleeves.py` para poder ser reusado; o artefato `Gate_sleeves.md` foi
re-gerado e conferido por hash — **idêntico**.

**O que aconteceu com as três saídas listadas aqui:** a **(a)** foi feita — a
decisão 5 fechou e a 1.1 fora do Fed foi medida com o `CPIAUCSL` e **reprovou**
(D28.c); a **(b)** foi medida e a 3.2 morreu sem sinal (D27); a **(c)** foi
recusada. A camada acabou entrando por um quarto caminho, o livro transversal
neutro (D27/D28).

---

## 27 (branch `Felipe`). Maratona de medição da camada tática — 4 candidatos testados, 2 células vivas 🟢 (registro, 2026-08-11 — sessão 26)

> ✅ **Desfecho:** as duas células vivas (M4 recessão, M9 Câmara) foram
> **ADMITIDAS na D28** e estão **LIGADAS na entrega** (D28.13). As ressalvas
> abaixo — comparações múltiplas sem correção, M9 como célula única — seguem de
> pé e vão declaradas no relatório.

> ⚠️ Numeração paralela por branch — ver o aviso no topo. Cite como "D27 do
> `Felipe`".

**Registro, não decisão.** Nada aqui fecha, nada reabre escopo e **nenhum
candidato foi movido de estado** — quem move é o dono. Por instrução dele a
sessão implementou e testou um a um os candidatos válidos, só para ver quem
passa. Seis scripts, seis artefatos, **nenhum módulo em `src/`** (protocolo da
D17). Suíte: **259 → 289 testes**. Detalhe completo em `Candidatos_taticos.md`.

**As quatro candidatas medidas, e a causa de morte de cada uma:**

| candidato | causa | número |
|---|---|---|
| **1.1 PEAD** · Fed | SEM SINAL | surpresa mediana **0,52 bps** contra tick de 1 bp; e o `h = 15` sai `SPY +4.91 ❌ · TLT +1.37 ❌`, **dígito por dígito** o controle da D16 |
| **1.1 PEAD** · CPI/binários | DADO | a série do poly **termina na véspera** da resolução; sem valor resolvido não há surpresa. Binários: 1 evento por mercado |
| **3.2 event-driven** | SEM SINAL | resíduo pós-gap de **mediana −1%**, 4 de 8 mercados na direção declarada |
| **notícia** | DADO | 2, 8, 28 e 58 pregões nos mercados que se mexem |
| **transversal** | — | eixo confirmado (ver abaixo), sem gatilho próprio |

**1. A 1.1 no Fed não é candidata nunca medida — É a sleeve da D16.** A
reprodução é exata, não aproximada, e isso deixou de ser argumento e virou
medida (`Gate_PEAD.md`). O que continua intocado é a 1.1 **fora** do Fed, e o
que impede é G0 + a **decisão 5**, que segue 🔴 aberta. A definição usada aqui
(*resolução − probabilidade da véspera*) entrou como **placeholder declarado** e
**não fecha a decisão 5**.

**2. O eixo do INSTRUMENTO existe, e sobrevive à neutralização de beta.**
Mesmo sinal, mesma grade, trocando só o livro: **8 pares passam só com livro
setorial, 0 só com o direcional** (`Gate_transversal.md`). Metade dos livros
declarados, porém, era **beta disfarçado** (`+XLF −XLP` +0,59 · `+XLP −XLK`
−0,56 · `+XLF −XLU` +0,48). Com as pernas hedgeadas contra o SPY por β expansivo
defasado, a maior |corr| cai para **0,17** e o placar **sobe para 14 × 0**
(`Gate_transversal_neutro.md`). A vantagem do livro **não era** alavancagem
direcional disfarçada.

**3. Um modo de falha novo entrou no repertório da camada, e derrubou a
maioria: INSTÁVEL.** Não é invenção desta sessão — é o corte da amostra em duas
metades que a **D19c** usou para derrubar a 3.1 direcional. **Das 10 aprovações
de G2 da maratona, 8 morrem nele.** Formalizá-lo como quinto item da D22 é
decisão do dono; **não estou tratando como se já fosse**.

**4. O teste entre mercados IRMÃOS liquidou o resto** (`Gate_mercados_irmaos.md`).
Partir a amostra usa o mesmo mercado, ano e regime; o teste forte é se o
mecanismo se repete num segundo mercado — foi assim que a 2.4 morreu. Relação
declarada antes de medir (partidário = **espelho**, geopolítico = **igual**), μ
**cru** e não alinhado:

- **M7 Irã k = 20 — ❌**, não reproduz no segundo episódio. Mesmo padrão da view
  C (D23f), agora medido na camada tática.
- **M5 Trump — ❌**. (Ressalva: a célula viva dele é corte de salto `q0.00`, que
  não existe na grade de lookbacks; leu-se k = 1, correspondência aproximada.)
- **M9 Câmara k = 20 — ✅.**

**As duas células que sobraram, e nenhuma pode entrar:**

| célula | o que passou | o que falta |
|---|---|---|
| **M4 recessão** — direcional k = 5 · setorial neutro **k = 3, 5, 10** | G0 249 · G1 2,0× · G2 ✅ · G3 −0,20 · corte da amostra ✅, em **três horizontes contíguos** | 🛑 **a contradição com a D19c**, no mesmo mercado. E **nunca** terá teste de irmão: não existe segundo mercado de recessão (D18d) |
| **M9 Câmara** — setorial neutro k = 20 | tudo acima **+ reprodução em mercado irmão** — única do projeto | 🛑 tensão com a **2.4**: ressuscitar como *overlay* um mecanismo cortado como *view* é decisão de grupo. E é **célula única**, não bloco |

⚠️ **Contra as duas, e precisa estar visível:** elas saíram de uma seleção de
~200 células (mercado × horizonte × livro) em seis artefatos. **Nenhum teste
rodado corrige para comparações múltiplas.** O M4 tem proteção parcial (três
horizontes contíguos — garimpo tende a produzir célula isolada); o **M9 não
tem**, e é o mais exposto.

⚠️ **A taxa de reprodução por par NÃO é teste estatístico** (43% partidário, 28%
geopolítico, contra 25% de acaso): as células não são independentes — horizontes
vizinhos leem quase os mesmos dias e os livros compartilham perna. Está dito no
artefato para ninguém citar como significância.

**O G4 (P&L da sleeve sozinha) continua sem ser rodado para NADA.** Tudo acima é
critério de admissão — responde *"o sinal existe e aponta certo?"*, nunca *"isso
ganha dinheiro?"*. O G4 é o primeiro que exige módulo, e por protocolo vem
depois das duas pendências acima.

**Os três portões que esta seção listava como fechados foram todos resolvidos na
D28, na sessão seguinte:** a reabertura de escopo (item 1), o portão de qualidade
do poly valendo também para overlay (item 2 — era a antiga D24) e a 12c, com o
tamanho pela âncora `inv(δΣ)·μ` e **sem `orcamento`** (item 9).

**Correção de registro feita nesta sessão:** o `Conclusoes.md` rotulava uma
premissa morta como *"o poly está atrasado"*, o que se lê como o contrário do
que a tese diz. O rótulo virou *"o poly ajusta em rampa"* — a medição (VR ≈ 1) é
sobre o repreçamento ser gradual ou instantâneo, e ele é instantâneo.

**Decisão do dono na sessão seguinte:** as duas foram avaliadas e admitidas —
ver a **D28**.

---

## 28 (branch `Felipe`). A camada tática é REABERTA e as candidatas são admitidas por uma régua nova 🟢 (fechadas pelo dono, 2026-08-11 — sessão 27)

> ⚠️ Numeração paralela por branch — ver o aviso no topo. Cite como "D28 do
> `Felipe`".

**Doze decisões, todas fechadas pelo dono em sessão**, por instrução explícita
("aceito todas as recomendações"). Elas não vão à reunião: com o v1 virando a
entrega, não existe versão seguinte para onde empurrar. Seguem o regime das
seções 9/10 — **provisórias, o grupo revisa**.

### 28.0. A régua do dono, e ela precede as doze 🟢

Declarada por ele nesta sessão, ao recusar que eu rejeitasse candidata sem que
ele entendesse o motivo:

> "Para mim não é problema que ela esteja no prejuízo, desde que a estratégia
> não seja desprovada, leia o polymarket e não tenha overfit ou variável não
> teórica estou aceitando."

**Quatro itens, todos necessários:** (1) a tese não pode estar contrariada pelo
dado; (2) o sinal vem do Polymarket; (3) nenhum parâmetro escolhido olhando o
resultado; (4) toda variável declarada pelo mecanismo, antes de medir.

**O que esta régua NÃO contém, e é deliberado: resultado.** Excesso negativo não
reprova. Isso é consistente com o que já estava registrado — a **14a** ("fazer
sentido vale mais que medir positivo") e o fato de **nenhuma view do projeto ter
sido cortada por excesso negativo** (17e). O que ela muda é o alcance: passa a
valer também para a camada tática, onde o **G4** vinha sendo tratado como
portão implícito.

**Efeito imediato no placar da D27:** o inventário de "2 células vivas" era
contra a régua antiga. Contra esta, **três candidatas** ficam de pé (M4, M9,
1.1 fora do Fed), e **três estão desprovadas de verdade** — 1.1 no Fed, 3.2
event-driven, 1.2 momentum e velocidade de ajuste foram medidas e a tese caiu.
A **transversal não é candidata**: é o *livro* que a M4 e a M9 usam.

### 28.1 a 28.12 — as doze

| # | decisão | motivo registrado |
|---|---|---|
| **1** | **A camada tática está REABERTA.** | O ponteiro da "decisão 10" aponta para o vazio desde a reorganização do arquivo (levantado na sessão 25). O dono declara a reabertura e admite candidata a candidata pela 28.0. |
| **2** | **D24 fechada: o portão de qualidade VALE para overlay**, adaptado a binário — leitura ausente no slot pré-abertura desativa o dia. | Estava 🔴 desde a sessão 25. Sem isso uma sleeve passaria livre pelo veto que mata a view equivalente, que é a assimetria que a própria D24 existe para nomear. |
| **3** | **M4: o `k` é o BLOCO k = 3, 5, 10, com peso igual.** | Declarar antes é o único jeito de não escolher o horizonte pela tabela. O bloco não seleciona nada: é exatamente o conjunto que sobrevive ao corte da amostra, e é contíguo. |
| **4** | **Livro HEDGEADO (`⊥`)**, β expansivo defasado, semeado em 60 pregões. | É o que foi medido (`Gate_transversal_neutro.md`) e o que sustenta a tese: com o índice removido das duas pernas a maior \|corr\| com o SPY cai de 0,59 para 0,17 e o placar sobe de 8×0 para 14×0. O livro cru mediria alavancagem direcional disfarçada. |
| **5** | **A M9 pode entrar como overlay**, condicionada a a objeção da 2.4 não sobreviver ao livro neutro. | A 2.4 morreu com o mecanismo partidário no livro **direcional**. É a mesma estrutura que a D19c tinha contra a M4 e que a **28.a** abaixo resolveu a favor. Se a objeção sobreviver ao livro neutro, a M9 cai. |
| **6** | **Comparações múltiplas: aceitas e DECLARADAS no relatório.** | ~200 células em seis artefatos, nenhuma correção. A régua 28.0 não exige significância; esconder a exposição é que violaria o item (3). M4 tem defesa parcial (bloco contíguo); a M9 não tem. |
| **7** | **Decisão 5 fechada** — surpresa = `resolução − prob. da véspera`, contínua. | Ver a seção 5, reescrita. Destrava a 1.1. |
| **8** | **Autorizado UM csv do FRED** (`CPIAUCSL`) com o valor realizado. | Sem valor resolvido não existe surpresa, e o `data/` só tem as **datas** de release. É uma coluna no formato dos `fred_*.csv` que o repositório já lê — ordem de grandeza diferente de um pull novo de mercados, que foi recusado no mesmo fôlego. ⚠️ **Encosta no módulo do Paulo** (pipeline de dados): fica registrado como exceção autorizada pelo dono, não como precedente. |
| **9** | **Tamanho pela âncora `inv(δΣ)·μ` da D16. NÃO se reintroduz `orcamento`.** | Zero parâmetro livre. A falta disso é o que matou a **12c**: o Δ era monótono no orçamento, sem ótimo interior, então a grade não selecionava tamanho. |
| **10** | **O tilt tático entra DENTRO do teto** (Σ\|w\| ≤ 1 no tilt). | Não cria parâmetro novo e mantém o escopo de referência de todas as varreduras desde 05/08. |
| **11** | **Sleeves que compartilham livro têm os μ SOMADOS antes do `inv(δΣ)`.** | A M4 e a M9 usam o **mesmo** livro (`+XLP −XLK`). Somadas como posições independentes, virariam dupla contagem da mesma perna. |
| **12** | **O G4 é RELATÓRIO, não portão.** | Ele nunca rodou para nada. Pela 28.0 o resultado não reprova, e usá-lo como portão reintroduziria a escolha por resultado — o overfit em dois passos do protocolo da seção 10, agora sem rodada seguinte para desmentir. |

### 28.a. A contradição com a D19c está RESOLVIDA — e por um eixo que ninguém tinha proposto 🟢 (medido, 2026-08-11)

Era o **primeiro item da sessão por decisão do dono** e travava a candidata mais
forte. Medido em `Dump/analises/Gate_recessao_2x2.md`
(`scripts/gate_recessao_2x2.py`, 7 testes; suíte **289 → 296**). Nenhum módulo
em `src/`; livros, premissas e partição importados **por referência**.

**O problema:** a D19c mediu que o coeficiente da view 3.1 no M4 troca de sinal
dentro da amostra; a D27 mediu que a sleeve no MESMO mercado sobrevive ao mesmo
corte. As amostras se sobrepõem quase inteiras (2025-01/04 a 2025-12), então
"é outro período" não era saída.

**Conserto no próprio teste, antes de qualquer leitura:** em h = 10 o critério
"trocou de sinal" marca **13 das 14 células** — com janelas sobrepostas e
n ≈ 200, girar é barato. Passou a valer o critério **literal da D19c** (*as duas
metades significantes e opostas*, \|t\| > 2), que marca **3 de 14**.

| | livro: SPY direcional | livro: spread neutro |
|---|---|---|
| **nível** (discordância) | 🛑 gira — **a D19c, reproduzida** | 🛑 **gira também** |
| **incremento** (Δp k = 3, 5, 10) | não gira | não gira — **a sleeve** |

Marginais na régua forte: **nível 3 de 6 · incremento 0 de 8**; por livro, 1 de
7 e 2 de 7. **Nenhuma das duas explicações que eu havia pré-registrado se
sustenta:** o giro não se concentra num livro (cai "é o canal de direção") e não
alcança sinal de incremento nenhum (cai "o mercado M4 é instável").

**O eixo é a TRANSFORMAÇÃO do sinal.** O NÍVEL da crença tem relação instável
com os retornos; o INCREMENTO não. O mecanismo é banal e verificável: um nível
que sobe e desce com o medo de recessão ao longo de 2025 fica correlacionado com
o que o mercado fez em cada regime, e o coeficiente ajustado vira afirmação
sobre o regime. Diferenciar remove isso por construção. Corroborado por dois
controles: o giro vem da perna `z(poly)` e **nunca** da perna `z(−spread)`, e a
correlação entre as duas séries de `p` é **+1,000**, o que exclui a construção
do `p` como explicação.

**Consequência:** a D19c **deixa de ser objeção** à sleeve M4. O que sobra dela
é uma **limitação a declarar**: neste mercado, qualquer view que leia NÍVEL está
medindo regime.

⚠️ **Limitação nova, que saiu junto e não é pequena:** em k = 3, 5 e 10 a sleeve
**reprova a premissa em h = 10** na amostra inteira. Ela é estável, mas a
vantagem que o G2 mede vive na janela de **1 pregão** e não se estende a dez.
**Estabilidade não é alcance** — e é a segunda coisa que o G4 vai medir.

⚠️ **Refactor verificado, não confiado:** `componentes_expansivos` saiu de dentro
do `divergencia_expansiva` (`view_3_1_direcional.py`) para as duas parcelas do
`z` serem medíveis sozinhas. O `Recessao_direcional.md` foi re-gerado e conferido
**por hash — idêntico** (`04cfda9835cba307`).

### 28.b. A M9 passa pelo mesmo 2×2, e some a condição do item 5 🟢 (medido, 2026-08-11)

`Dump/analises/Gate_2x2_M9.md`, mesmo script parametrizado por mercado. A
objeção da 2.4 (o mecanismo partidário não reproduz fora da amostra) foi medida
**no livro neutro**, que é o da sleeve:

| | SPY direcional | spread neutro |
|---|---|---|
| **nível** `z(p)` | 🛑 gira (forte) | 🛑 gira (forte) |
| **incremento** Δp k = 20 | não gira | **não gira** — G2 ✅✅ nas duas metades |

Marginais: **nível 2 de 2 · incremento 0 de 2**, nos dois livros — o mesmo eixo
da 28.a, achado por medição independente. **A condição do item 5 está cumprida.**

**E a M9 tem o que a M4 nunca terá:** a célula viva dela (`neutro +XLP −XLK⊥`,
k = 20) **reproduz em mercado irmão** (`Gate_mercados_irmaos.md`: `XLP⊥
−1,39/+2,23 ✅ · XLK⊥ +0,08/−2,62 ✅`), com k = 3 e k = 5 reproduzindo no mesmo
livro. É a única célula do projeto com fora-da-amostra de verdade.

### 28.c. A 1.1 fora do Fed foi destravada e REPROVOU 🟢 (medido, 2026-08-11)

O item 8 autorizou o `CPIAUCSL`; com ele o G0 do CPI abriu — **12 divulgações
pareadas**. O bloqueio nunca foi a série do poly terminar na véspera (a véspera
é o lado que a surpresa usa), era o valor realizado.

| | medido |
|---|---|
| G1 | **0,6×** — mediana da \|surpresa\| **0,06 p.p.** contra grade de 0,1 p.p. |
| G2 | **nenhuma** das 5 janelas passa; o TIP anda contra a premissa em todas |
| G3 | **+0,58** com a divergência da 2.2, que uma view VIVA já lê |

**Pela régua 28.0 isto é tese contrariada pelo dado**, não prejuízo: a 1.1 sai
do estoque. Custou um CSV de uma coluna descobrir, contra a estimativa anterior
de "pedido ao Paulo". Três registros que haviam envelhecido no `gate_pead.py`
foram corrigidos junto (decisão 5 "aberta", CPI ❌ no G0, "falta pedir ao Paulo").

### 28.13. A entrega vai com a camada LIGADA 🟢 (fechada pelo dono, 2026-08-11)

**Decisão do dono, com o número na mesa.** O `carregar` passa a ter
`sleeves=True` por default — mesma lógica do `VIEWS_V1`: é o default do módulo
que define "o v1" para as varreduras irmãs, e cravar a decisão só no `main`
faria a entrega e as varreduras medirem carteiras diferentes em silêncio.

**Medido antes de decidir** (`Dump/analises/Camada_tatica_v2.md`, teto no tilt):

| teto | excesso × SPY sem | com | Δ |
|---|---|---|---|
| **1** (referência) | +6,24 pp | **+4,08 pp** | **−2,16 pp** |
| 2 | +8,51 pp | +3,29 pp | −5,22 pp |
| 3 | +13,22 pp | +5,06 pp | −8,16 pp |
| 5 | +16,03 pp | +16,85 pp | +0,82 pp |

**O achado da rodada, e ele não é o Δ:** a camada é **positiva sozinha** (G4:
**+42,6 pp** em 327 pregões, acerto de sinal 54%, e **+64 pp** sem os 3 maiores
dias em \|valor\| — não é um punhado de pregões) e **negativa quando somada**.
Não há contradição: com o teto no tilt, o corte reescala o tilt das views e o da
camada **juntos**, então entrar não é somar — é **dividir um orçamento fixo de
risco**. Ela pede Σ\|dw\| mediano de **2,54** contra um teto de **1** para o
tilt inteiro, e nesta janela não rende mais por unidade de Σ\|w\| do que o tilt
que desloca.

⚠️ **O Δ não é monótono no teto** (−2,16 · −5,22 · −8,16 · +0,82): não se lê nem
como "a camada perde" nem como "ela só disputa espaço". **Nenhuma linha da grade
é proposta** — ler o teto 5 como recomendação seria escolher configuração pelo
resultado, que é o que a régua 28.0 barra. O teto de referência continua sendo
**1**, pela 10a.

⚠️ **O G4 é bruto de custo e sem teto** — mede o `dw` pedido, não uma carteira
executável. O custo aparece na entrega: breakeven de **28,5 bps por lado** contra
os 2 bps premissados (era 34,5 sem a camada), ainda **14× de folga**.

**Limitação declarada — artefatos de carteira anterior.** `Curva_c.md`,
`Curva_banda.md`, `Curva_orcamento.md`, `Teste_sinal.md`, `View_C_backtest.md` e
`Ortogonalidade.md` foram gerados antes desta decisão; parte foi re-gerada
depois, parte não. **Não citar número deles como sendo a entrega** — a entrega é
o `Backtest_v1.md`, que já saiu com a camada ligada.

#### Errata da 28.13 — os números foram re-medidos com a régua (2026-08-14, sessão 30)

**A decisão NÃO é reaberta.** Ela foi tomada por mecanismo (régua 28.0), não por
este número; o que muda é o tamanho do custo, não o sinal dele. Medido com a
régua da Lia ligada nas DUAS pontas (nível 1, 6q — a configuração da entrega
desde hoje):

| teto | excesso sem a camada | com | Δ (era) |
|---|---|---|---|
| **1** (referência) | +5,98 pp | **+3,04 pp** | **−2,94 pp** (era −2,16) |
| 2 | +6,51 pp | −0,24 pp | −6,75 pp (era −5,22) |
| 3 | +7,22 pp | −1,68 pp | −8,90 pp (era −8,16) |
| 5 | +4,17 pp | +7,99 pp | +3,82 pp (era +0,82) |

O custo cresce porque a régua encolhe o tilt das views e a camada disputa o
mesmo orçamento de risco: cortar de um lado aumenta o peso relativo do outro.
**O resto da leitura sobrevive inteiro** — o Δ continua não-monótono, o pior
ponto continua no teto 3, e o G4 (**+42,6 pp**, acerto 54%) não muda um dígito,
porque a régua dosa o Ω das views e não toca o `dw` da camada. O breakeven da
entrega com a camada passa de 28,5 para **22,9 bps por lado** — 11× a premissa
de 2 bps, ainda longe de o custo decidir o resultado.

Chegou pela Lia (`PEDIDO_Felipe_acoplar_regua.md`, branch dela) e foi
**reproduzido aqui** re-rodando o `camada_tatica_v2.py` com `--regua`.

---

## 29 (branch `Felipe`). A régua do Ω entrou na ENTREGA 🟢 (fechada pelo dono, 2026-08-14 — sessão 30)

**O buraco.** O encanamento estava pronto dos dois lados desde 11/08 — a
`market_inputs.regua_por_decisao` (D21a) e o parâmetro `regua` do `run_backtest`
— mas o `main` do `scripts/backtest_v1.py` nunca passou o parâmetro. Resultado:
a **entrega rodava sem a régua** enquanto o relatório final da Lia já saía com
ela, e os dois documentos descreviam carteiras diferentes. Quem apontou foi a
Lia, em `PEDIDO_Felipe_acoplar_regua.md`.

**O que ficou.** `--regua` (caminho do CSV, default seguindo o `--raiz`, `""`
desliga) e `--regua-nivel` (default **1**) em cinco scripts:
`backtest_v1.py`, `camada_tatica_v2.py`, `curva_banda.py`, `curva_orcamento.py`
e `view_C_backtest.py`. O default do caminho segue o `--raiz` pelo mesmo motivo
do `curva_c.py`: com o CSV num relativo fixo, rodar contra a cópia do Paulo
desligaria a régua **calado**.

⚠️ **O nível 1 não é escolha deste branch** — é a **6q da Lia**, fechada por ela
em 13/08. Aqui ele é default de flag, não decisão; mudou lá, muda aqui.

**O que mudou no número da entrega** (teto no tilt = 1, camada ligada, γ = 1):

| | sem régua | com régua nível 1 |
|---|---|---|
| excesso × SPY | +4,08 pp | **+3,04 pp** |
| retorno líquido | +34,20% | **+33,16%** |
| sharpe | 1,2136 | **1,1815** |
| Σ\|w\| média | 1,9438 | **1,9146** |
| giro diário | 0,3201 | **0,3963** |
| breakeven | 28,47 bps | **22,87 bps** |
| views/dia | 2,24 | **1,99** |

Bateu **dígito a dígito** com o que a Lia mediu por fora, o que fecha a
checagem cruzada: o mesmo `run_backtest` chamado de dois lugares dá o mesmo
número.

**A régua encolhe e agita ao mesmo tempo**, e as duas coisas puxam o breakeven
em direções opostas: a Σ|w| cai (1,944 → 1,915) mas o giro **sobe** 24% (0,320 →
0,396), porque o `c` muda de pregão para pregão e o tamanho do tilt muda junto.
O que sobra é breakeven menor (28,5 → 22,9 bps), ainda 11× a premissa de 2 bps.
As views/dia caindo de 2,24 para 1,99 são o **veto de liquidez** dela, que é
canal separado do nível (D25f) e continua agindo mesmo em `--regua-nivel 0`.

**O que isto deixa declarado (não é pendência — é limitação):**

- **O teto nunca foi cravado num número, e isso é escolha.** A ordem era: entra
  o `c` → mede-se a Σ|w| → decide-se o teto. Os dois primeiros passos estão
  feitos e medidos; o terceiro nunca foi fechado, então a **entrega reporta a
  grade {1, 2, 3, 5}** e cita **1 no tilt** como referência (10a), em vez de
  escolher a linha de melhor número.
- `Teste_sinal.md` e `Ortogonalidade.md` são anteriores à entrada da camada
  (28.13) — nenhum dos dois passa pelo `run_backtest`. Valem para o que medem
  (sinal das views, ângulo entre P), não como descrição da carteira.

---

---

## 30 (branch `Felipe`). O slide 6 da semi × o que o backtest realmente rodou 🔴 (registro, 2026-09-06 — sessões 38 e 39)

**A única decisão aberta do arquivo, e ela é de NARRATIVA — não de modelagem.**
O código está congelado; o que a reunião decide aqui é o que os slides contam.

**Correção de fato, feita na sessão 39 (lida no código, não no registro).** A
versão anterior desta seção afirmava que a camada tática não entrou no backtest
e que os números do slide 9 eram medidos **sem** ela. **As duas afirmações estão
erradas**, e o erro nasceu de citar a D12c/D16 (camada *antiga*) como se
descrevessem o estado atual:

| verificação | resultado |
|---|---|
| `scripts/backtest_v1.py::carregar` | `sleeves=True` por **default** — o `main` não desliga |
| `Dump/dados/backtest_diario.csv` | `n_taticas = 1` em **327 dos 374 pregões**, em todos os 8 cenários |
| cabeçalho do `Backtest_v1.md` | "camada tática v2 (sleeves da D28): **LIGADA** — os números desta tabela **já incluem** o overlay" |
| slide 9 (+33,2% × +30,1%) | é a coluna `tilt ≤ 1` desse relatório, ou seja **+3,04 pp COM a camada** (a errata da 28.13 mede +5,98 pp sem ela) |

**O que continua desligado**, e é a origem da confusão: a camada tática
**antiga** — prêmio de anúncios 1.3, drift pós-FOMC, gap de fim de semana
(`tatica=()`, D12c/D16). A que roda é a **v2**, admitida na D28: sleeves M4
recessão e M9 Câmara, livro `+XLP −XLK` hedgeado.

**O conflito que SOBRA para a reunião alinhar** (o slide 6 não é o problema —
ele está certo; os outros dois é que não acompanharam):

| onde | o que diz | está certo? |
|---|---|---|
| slide 6 (`Semis.txt`) | camada tática ativa, exemplo de abril/2025 | ✅ a camada está ativa |
| slide 8 (`Semis.txt`) | "5 candidatos passaram pelo gate, **nenhum entrou**" | ❌ **duas entraram** (M4 e M9, D28) |
| slide 9 / backtest | +33,2% × +30,1% "sem camada tática" | ✅ o número; ❌ o rótulo — é **com** camada |
| roteiro das quartas | "em abril de 2025 a carteira caiu **mais fundo** que o índice" | ⚠️ é sobre a carteira inteira; o slide 6 fala do ganho **da sleeve** naquele dia — as duas podem ser verdade ao mesmo tempo, mas ditas assim se contradizem no palco |

**Duas coisas a decidir, e nenhuma mexe em código:**

1. **Alinhar 8 e 9 ao 6** — o slide 8 passa a dizer "5 candidatos medidos, **2
   entraram**" e o 9 rotula o número como *com* camada tática. É a saída que bate
   com o que está entregue.
2. **Como contar abril/2025 sem se contradizer:** a sleeve ganhou no dia, e a
   carteira caiu mais que o índice no episódio. Dizer as duas, nessa ordem, é
   defensável; dizer só a primeira é o que a banca cruza com o roteiro das
   quartas.

**Ressalva a levar junto**, porque a banca pode perguntar: a camada é **positiva
sozinha** (+42,6 pp no G4) e **custa −2,94 pp** quando somada no teto de
referência, porque divide um orçamento fixo de risco com o tilt das views
(D28.13 e sua errata). Isso está medido e declarado — não é surpresa a ser
descoberta no palco.

### 30.a. Mais duas linhas do slide 8 que não batem (achado na sessão 42, ao montá-lo)

Nenhuma fecha nada — entram na mesma pauta da reunião, que é de narrativa:

| onde | o que diz | está certo? |
|---|---|---|
| slide 8 (`Semis.txt`) | "39 mercados coletados, 9 usados" | ⚠️ o **9 usados** bate (D5, `poly_preprocessing.py`); os **39 coletados** não aparecem em artefato nenhum do repositório — `data/raw/clob_exploracao` tem 366 arquivos e o dataset do Fed tem 76 mercados de desfecho. Ou alguém tem a fonte, ou o número sai do palco. |
| slide 8 (`Semis.txt`) | "8 configurações testadas, tilt ≤ 1 **escolhido pelo Sharpe**" | ❌ a grade ({1, 2, 3, 5} × dois escopos = 8) está certa, mas o nível **1** foi escolhido **pela regra e antes de ver o resultado** (10a). Dizer "pelo Sharpe" contradiz a régua que o próprio slide 8 defende — é o pior lugar do deck para essa frase. |

**O que o `Semis/Slide_8.pptx` faz enquanto a reunião não decide:** conta o funil
pelo que está **medido** — 13 candidatas → 1 entrou (o placar da p. 4 do
relatório), grade de 8 configurações com o nível escolhido pela regra, e sem o
"39". A tupla `GRUPOS` do `scripts/slide8_pesquisa_pptx.py` está marcada com
`# TODO(DECISAO-30)`: se a reunião fechar outra contagem, muda ali e só ali.


## 31 (branch `Felipe`). Formato da apresentação da semifinal: HTML, PPTX ou híbrido 🔴 (registro, 2026-09-06 — sessão 40)

**Por que é decisão de time e não minha:** os slides 1, 2 e 7–10 não são meus, e
Paulo e Lia sobem no palco com o mesmo deck. Trocar o formato de um pedaço muda o
que todo mundo entrega.

**O que já está resolvido:** o guia da semifinal (regra 2) libera o formato —
*"pode ser feita no formato que preferirem (PowerPoint, PDF, HTML, etc.),
compartilhando a tela"*. Não há restrição do Itaú. São 6 minutos com hard stop,
por Teams.

**O que motivou:** o `Semis.txt` pede, para os slides 3–6, um diagrama que
atravessa as quatro páginas revelando nós. Em PPTX cada acendimento vira um slide
duplicado — os 4 slides lógicos viram 12 a 15 físicos, com as posições
sincronizadas à mão. O Morph por nome (`!!q`) do `slides_3a6_pptx.py` é a solução
certa dentro do PPTX, mas para de escalar exatamente aí. Em HTML é uma classe por
estado.

**Estado atual (feito, não decidido):** os slides 3–6 foram refeitos em
`Semis/slides_3a6/index.html` por instrução direta do dono. O resto segue em
PPTX.

| opção | a favor | contra |
|---|---|---|
| **A. Híbrido** (3–6 em HTML, resto PPTX) | é o estado de hoje; nenhum retrabalho | trocar de janela no meio de uma apresentação de 6 min com hard stop |
| **B. Deck inteiro em HTML** | uma janela só; ganha o modo apresentador (notas + cronômetro por bloco), que ajuda no hard stop | refazer 6 slides que não são meus |
| **C. Voltar 3–6 para PPTX** | uma janela só, sem retrabalho de terceiros | perde o reveal progressivo que o `Semis.txt` pede — é o motivo de ter saído do PPTX |

**Ressalva de palco (vale para A e B):** no modo apresentador do guizang,
compartilhar a **janela** do público, nunca a tela inteira — senão a banca vê as
notas.

## 32 (branch `Felipe`). Estudo estatístico do Polymarket para a final — escopo e escolhas pré-registradas 🟢 (fechada pelo dono, 2026-09-17 — sessão 46)

**O que é:** o slide 16 do planejamento da final ("análise estatística do valor
do Polymarket como fonte de dados") virou um estudo formal —
`Final/estudo/Estudo_polymarket.md`, `scripts/estudo_polymarket.py`,
`Uteis/analises/Metricas_estudo.md`, figuras `Uteis/graficos/estudo_*` e os
slides 16 + A1 + A2 em `Final/Slides_novos.pptx`. **Mede; não decide** — nada
em `src/`, no backtest ou em parâmetro da estratégia muda por causa dele.

**Fechado pelo dono na sessão (quatro escolhas de escopo):**
1. **Amostra = só o dado macro já no repo** (FOMC · CPI · payrolls). Estudos
   amplos (Kalshi Research 2026, Dune/McCullough) entram como referência
   externa; **nenhum pedido de dado ao Paulo**. Um pull amplo de todas as
   categorias ficou fora — se voltar, é pipeline do Paulo.
2. **Formato = paper curto + slide 16 + 2 slides de apêndice + um script.**
3. **Os achados negativos entram** (Δp não antecipa retorno — `Teste_sinal.md`;
   preço do poly reverte em 12 h): o valor está no NÍVEL, não no movimento,
   que é o argumento para usar o Polymarket via Black-Litterman.
4. **Escolhas metodológicas pré-registradas no plano, aprovadas junto com ele**
   (regra 1: valores não se assumem sozinhos): grade de horizontes
   h ∈ {0, 1, 2, 3, 5, 10, 15, 20, 30, 45, 60} dias corridos; bins de calibração
   10 (pooled) / 5 (por recorte); baseline do skill = PMF uniforme sobre os
   buckets vivos; h-herói = 0 e 20; γ favorito-azarão só **medido** (D9 segue
   com 1,0); VR(2), VR(5); Diebold–Mariano e Newey–West em numpy; cluster =
   evento em todo IC e EP; B = 2.000.

**Dois achados de DADO que mudaram o desenho (medidos, não escolhidos):**
- a série de todo mercado termina no slot das 12:00 UTC do dia do anúncio —
  **o preço terminal não é a resolução**. FOMC resolve pelo `DFF`
  (`decisoes_realizadas_fomc`), CPI pelo `CPIAUCSL` (`mom_realizado`);
- **payrolls não tem resolução no repo** (arquivos do G9 sem rótulo de faixa;
  `PAYEMS`/`UNRATE` não estão no `data/`). Entram só em Σp e martingale. Com o
  dado, entram na Q1 pelo mesmo script — é pedido ao Paulo **se** o time quiser.

**Filtros de dado declarados (não são threshold de estratégia):** linha de PMF
com Σp < 0,5 é leitura degenerada (buckets mortos — CPI de mar/2026) e sai;
coluna de robustez do martingale usa só preços em (0,02; 0,98).

**Resultado (números em `Metricas_estudo.md`):** Brier pooled na véspera 0,043
[0,022; 0,067], BSS 0,73; `b` da calibração 1,04 (p = 0,15) na véspera e 1,08
(p < 0,001) no pooled — viés favorito-azarão (p < 10 ¢ nunca resolveu Yes, n =
908; γ ótimo 1,1–1,2 = a faixa de robustez da D9); FOMC na véspera: MAE 0,9 bps
× 4,8 do proxy corrigido (DM p = 0,002), acerto modal 17/17, futuro não
acrescenta em encompassing; lead-lag ≈ 0 fora da sobreposição de janela;
event-study do dia: surpresa-poly R² médio 0,08 (quase não sobra surpresa);
VR(5) < 1 em todas as famílias.

**Uma correção pega na verificação (registro):** a primeira versão lia o
`DTB3 − DFF` do próprio dia da leitura — lookahead de um fechamento frente ao
slot pré-abertura. Corrigida para "último fechamento estritamente anterior",
a mesma regra do backtest; o controle com o `s4_comparacao.csv` (E_poly −26,90
e E_FF −42 na véspera de 17/09/2025) fecha exato.

## 33 (branch `Felipe`). Análise estatística do backtest para a final — escolhas pré-registradas 🟢 (fechada pelo dono, 2026-09-18 — sessão 48)

**O que é:** os slides 28 (Backtest e resultados) e 30 (Análise crítica) do
`Final/fianl.pptx` mostravam o placar sem inferência — nenhum número com
intervalo, nenhum teste contra o benchmark, nenhuma correção por nº de
tentativas. Pesquisa de como a literatura julga uma estratégia
(`Final/analise/Pesquisa_avaliacao_estrategia.md`: Lo 2002; Bailey–López de
Prado 2012/2014; Ledoit–Wolf 2008; Politis–Romano 1994; Harvey–Liu 2015;
López de Prado 2018 cap. 14; Arnott–Harvey–Markowitz 2019; Luo et al. 2014;
Novy-Marx–Velikov 2016) → `scripts/analise_backtest.py` →
`Uteis/analises/Analise_backtest.md` + `Uteis/dados/analise_backtest/*.csv` +
`Uteis/graficos/ab_*` → slides **14, 15 e A9** em `Final/Slides_novos.pptx`.
**Mede; não decide** — o código da estratégia segue congelado; o script lê só
o `backtest_diario.csv` (cenário `tilt ≤ 1`) e as grades já gravadas.

**Fechado pelo dono na sessão (três escolhas de escopo):**
1. **A incerteza vai no slide de resultados**, não só nas notas: o +3,0 pp
   aparece com IC95 e P(> 0), o Sharpe com IC95, o alpha com o t e a régua.
2. Os slides nascem em `Slides_novos.pptx` (padrão das sessões 45–46); o dono
   cola no `fianl.pptx`.
3. Um slide de apêndice (A9) com a tear-sheet completa.

**Escolhas metodológicas pré-registradas no plano, aprovadas junto com ele
(regra 1: valores não se assumem sozinhos):** série `tilt ≤ 1`, 374 pregões,
taxa livre zero (convenção do projeto); bootstrap estacionário de
Politis–Romano com bloco médio 10 pregões, B = 2 000, semente 20260918, os
MESMOS índices para Kairós e SPY; Newey–West 5 lags; metades por contagem de
pregões (187/187); regime = sinal do retorno do SPY no dia; rolling de 63
pregões; SR* = 0; nível 95 %; **N do DSR em grade, não escolhido** —
{18 configurações com Sharpe gravado · 31 hipóteses do LOG · 231 = + ~200
células da D27} × {V medido nas configurações (correlacionadas, subestima) ·
V de tentativas independentes (SE² de Lo, cota superior)}.

**Resultado (números em `Analise_backtest.md`):** excesso +3,04 pp, IC95
[−12,9; +20,6], P(> 0) = 64 %; Sharpe 1,18 [−0,23; 3,04]; ΔSharpe
[−0,42; 0,63], P(> 0) = 66 %; alpha +2,6 % a.a. com t = 0,62 (régua de
Harvey–Liu: 3); PSR(0) = 93 %; **MinTRL(95 %) = 457 > 374 pregões**; DSR
0,84–0,88 com V medido, 0,08–0,33 com V independente; excesso na 1ª metade
(+3,3 pp) e negativo na 2ª (−0,6 pp); nos dias de queda do SPY +6,2 bps/dia
(hit 52 %), nos de alta −3,9 bps/dia; hit do tilt 50 %, HHI 0,01, os 3
maiores dias = 3,5 dos 5,2 pp; TuW 87 pregões (= SPY); 11 de 19 meses.
**Leitura fechada com o dono:** o número é positivo em todas as leituras, mas
18 meses não separam habilidade de sorte — o que sustenta a estratégia é o
mecanismo medido fora do resultado, e é isso que os slides dizem.

**Forma dos slides, fechada pelo dono na 2ª rodada:** o 14 replica o slide 28
do `fianl.pptx` com um único tile a mais (P(excesso > 0) = 64 %, IC95, MinTRL);
o 15 tem três números com leitura qualitativa (457 · +6,2 bps · 3 de 7) e uma
linha "faríamos diferente" — o scorecard inteiro fica no
`Pesquisa_avaliacao_estrategia.md` §2 e nas notas.

**Scorecard do protocolo (resumido no slide 15 como "3 de 7"), registrado:** ✔ motivação econômica ·
◐ testes múltiplos (DSR reportado; D27 sem correção) · ✔ dados/amostra ·
✕ validação fora da amostra (não há OOS; o próximo semestre é o OOS
pré-registrado) · ◐ dinâmica (parâmetros fixos, mas excesso só na 1ª
metade) · ◐ complexidade (Ω diagonal) · ✔ cultura.

**O que a pesquisa pede e NÃO foi feito (declarado no `Pesquisa_avaliacao_estrategia.md` §5):**
walk-forward, correção célula a célula da D27, regressão de fatores, custo real
de execução.

## 34 (branch `Felipe`). Estilo do deck da final — seis templates para o grupo escolher 🟡 (aberta, 2026-09-18 — sessão 49)

**O que é:** o grupo achou o estilo atual do `Final/fianl.pptx` "bonitinho,
pouco sério" e pediu propostas baseadas em decks de challenges financeiros
reais (Polaris/Insper, Wolves of Quatá/Insper, Waterloo/Rotman 2026, em
`Final/Reestilizar/`). Seis templates de um slide cada, mesmo conteúdo,
em gradiente do atual ao challenge — `Final/Reestilizar/T1…T5` (`.pptx` +
`.png`), esforço e trade-offs em `Final/Reestilizar/README_templates.md`.

**Opções:** T1 Kairós sóbrio (escuro, esforço baixo) · T2 Kairós claro
(claro, médio) · T3 Terminal (escuro, formato research, médio-alto) ·
T4 Consultoria (claro Polaris, alto) · T5 Research (claro Waterloo, alto) ·
T6 Terminal Polymarket (T3 com a série de mercado do gráfico em azul, médio-alto).

**Trade-off central:** quanto mais perto do challenge, mais o deck precisa
ser reconstruído (34 slides, gráficos regerados, slides manuais refeitos) —
T1/T2 trocam paleta nos geradores; T4/T5 são um deck novo. A escolha é do
grupo (afeta o entregável de todos). **Não fechar sem reunião.**

**2026-09-18, mesma sessão:** o dono descartou T1–T5 (arquivos apagados;
regeráveis com `--todos`) e manteve só o **T6** na pasta — candidato único,
confirmação em reunião.
**Aplicado:** `Final/FINAL_T6.pptx` = o deck inteiro no T6 (`scripts/final_t6_pptx.py`),
para o grupo avaliar lado a lado com o `FINAL.pptx`.
**2026-09-19 (sessão 50):** o dono achou a composição do T6 "pouco profissional"
(cards com borda em todo lugar). `Final/FINAL_T7.pptx` = o deck RECOMPOSTO no
estilo T6 com a composição dos decks de challenge — colunas com rótulo + régua,
números soltos, círculos numerados, uma caixa por slide (`scripts/final_t7_pptx.py`,
32 slides; o 16 vazio saiu). Três candidatos para a reunião: `FINAL` · `FINAL_T6` · `FINAL_T7`.
