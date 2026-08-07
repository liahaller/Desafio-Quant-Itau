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

**Próximo passo:** voltar para a Decisão 1.
