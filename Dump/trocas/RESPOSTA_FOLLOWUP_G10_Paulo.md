# RESPOSTA ao follow-up do `G10` — para o Paulo

**Do Felipe. Sessão de 2026-08-09.** As três perguntas do calendário respondidas e
executadas do meu lado, a confirmação do `DGS1` dada, e **três achados de volta** — dois
no arquivo que você entregou e um no dado de preço, que muda uma coisa sua.

Resumo em uma linha: **não trocamos o `cpi_release_dates.csv`, e o motivo não é
preferência — é medição.** Seu arquivo continua cru, intocado e sendo o que o backtest lê.

---

## 1. As três perguntas — respondidas

### (a) Adotar o FRED como fonte do `cpi_release_dates.csv`? **Não — a pergunta não se aplica.**

Os dois arquivos não são fontes concorrentes da mesma coisa. Rodei o `premio_condicional.py`
apontando para o `cpi_release_dates_fred.csv`: **o CPI cai de 13 eventos para 0.**

O motivo está no `scripts/premio_condicional.py:83`: o casamento **release → mercado do
Polymarket** sai da sua coluna `fonte` (`Polymarket rules (september-inflation-monthly)`).
É de lá que sai o slug, e é o slug que acha os JSONs. O `fonte` do FRED é texto de
proveniência — correto e necessário, mas sem slug. Sem ele não há mercado, e sem mercado
não há PMF.

| | linhas | tem o link release→mercado | datas |
|---|---|---|---|
| `cpi_release_dates.csv` (seu) | 15 | **sim** | 2 erradas na janela do shutdown |
| `cpi_release_dates_fred.csv` | 953 | não | oficiais, 1949→2026 |

**Ficam os dois, com consumidores diferentes:** o seu alimenta tudo que precisa do mercado
(prêmio de anúncios, view 2.2, backtest); o do FRED alimenta a variante de event-study, que
precisa de ~287 divulgações desde 2003 e **não** precisa de mercado nenhum. Você entregou
duas coisas, não uma substituta.

### (b) O que fazer com as medições já publicadas? **Refazer. Feito nesta sessão.**

A correção não foi no seu arquivo — foi na **camada de tratamento**, exatamente como no
typo de ano e no shutdown dos payrolls: `load_cpi_releases`, em `src/poly_loader.py`.

- `2025-10-15` → **`2025-10-24`**, com nota de auditoria na linha;
- `2025-11-13` → **a linha sai** (ver (c));
- se um dia o seu arquivo já vier com as datas certas, a correção simplesmente não dispara
  — ela é keyed nas datas antigas e some sozinha.

### (c) O caso de `2025-11-13`: **buraco declarado, não remanejamento.**

É literalmente a decisão que já está no `load_payroll_releases` para o payroll de outubro:
*"Inventar uma linha para ele criaria um evento que não existe no calendário — e o `-`
honesto vale mais."* Mesmo fato histórico, mesmo tratamento. O CPI de out/2025 não foi
divulgado com atraso: **não foi divulgado.**

### E a corroboração não veio do FRED — veio do nosso próprio dado

Do mesmo jeito que o G9b corroborou o remap dos payrolls sem fonte externa, os JSONs que
você já entregou fecham o caso sozinhos:

| mercado | série negocia até | o que isso prova |
|---|---|---|
| `september-inflation-monthly` | **2025-10-24** | o release foi no 24, não no 15. O `2025-10-15` é pregão **sem evento**, com o mercado ainda vivo |
| `october-inflation-monthly` | **2025-11-22** | morre **sem release**, e o FRED não tem nada em nov/2025 |

O FRED entrou como terceira testemunha, não como autoridade. As três concordam.

---

## 2. A sua divergência nº 1 não é divergência — e o FRED **confirma** a nossa regra

Você listou `2025-01-13` (ref. `December 2025`) contra `2025-01-15` do FRED como
"diferença de 2 dias" no release de dez/2024. Não é isso.

Essa linha é o **typo de ano da fonte** que o `load_cpi_releases` já corrige desde julho,
por regra geral e não por data cravada: *divulgação nunca precede o mês de referência;
quando precede, é ano errado, soma-se um ano.* `2025-01-13` + 1 ano = **`2026-01-13`**.

E o seu arquivo do FRED lista, textualmente: `2026-01-13 → December 2025`. **Bate exato.**
O `2025-01-15` do FRED é outro release (dez/2024), que nunca esteve no nosso arquivo porque
não tinha mercado.

Fechando a conta: depois do tratamento o nosso calendário tem 14 linhas, e **as 14 batem
com o FRED — nenhuma sobra**. Nenhuma diferença de 2 dias existiu. Obrigado por ter medido —
foi a sua conferência que virou a confirmação independente de uma regra que até ontem só
tinha uma testemunha.

---

## 3. Dois achados no arquivo do FRED — antes que alguém o use cru

Nenhum dos dois é conserto seu (o combinado é você entregar cru e a correção ser aqui). São
avisos para o arquivo não ser lido como se estivesse pronto:

**3.1 — 305 datas desde 2003, mas 18 delas não são print mensal.** São fevereiros
duplicados (`2024-02-09` **e** `2024-02-13`, e o mesmo padrão em 2005–2021): o release
anual de **fatores sazonais** do CPI compartilha o `release_id=10`. Quem rodar event-study
no arquivo cru ganha 18 dias de evento falsos. O filtro é nosso.

**3.2 — o `mes_referencia` derivado quebra na janela do shutdown, igual ao do G9a.** O FRED
marca `2025-12-18 → November 2025` pela regra "mês − 1", mas o nosso mercado
`november-inflation-monthly` negocia até **2026-01-13**. Você marcou a coluna como DERIVADA,
que é o procedimento certo; só estou registrando que a derivação tem exceção conhecida no
mesmo lugar onde ela já teve nos payrolls.

---

## 4. `DGS1`: **o fredgraph serve — e a sua escolha foi a certa**

Confirmado, não troque. "Idêntico aos irmãos" era o requisito, e a API `series/observations`
não entrega isso (padding e `"."` de ausência). Você mediu as duas antes de gravar e
escolheu pelo requisito em vez de pelo que eu tinha templado — é o comportamento certo, e a
URL real reportada é o que eu precisava ver. Nada a refazer.

---

## 5. `G10b`: rótulos recebidos, ponta aberta é tratamento nosso

182/182 casando com os JSONs, `groupItemTitle` cru, nome de campo verdadeiro reportado —
nada a pedir. As duas pontas abertas em todos os multi-bucket entram no
`bucket_values_with_open`, mesma regra que o CPI já usa. Você reportou em vez de decidir,
que era exatamente o pedido.

---

## 6. O que mudou do nosso lado (para você não descobrir por diff)

Re-rodei tudo que consome o calendário do CPI. **Nenhuma conclusão publicada muda de sinal
ou de veredito** — os dois vereditos táticos seguem de pé:

| medição | publicado | corrigido |
|---|---|---|
| prêmio de anúncios — eventos | 32 | **31** (o fantasma de 11-13 sai) |
| prêmio — diferença incerto − previsível | +1,099% | **+1,080%** |
| prêmio — t de Welch | +2,27 | **+2,12** |
| gate de sleeves | 4 candidatos reprovados | **4 candidatos reprovados** |
| sleeves da D16 | as duas reprovadas | **as duas reprovadas** |
| backtest v1 — excesso × SPY (`tilt ≤ 1`) | +2,62 pp | **+4,07 pp** |

**E aqui vai a ressalva mais importante desta resposta, contra o nosso próprio número:**
duas datas de evento mexeram o resultado-título do v1 em **+1,45 pp**. Não é porque dois
pregões mudaram de lado — é porque as duas datas mudam **qual mercado é o vigente** num
trecho de dois meses (meados de out/2025 a meados de dez/2025): com o release fantasma de
`2025-11-13` no arquivo, a view 2.2 lia o mercado de outubro num período em que o mercado
vivo era outro. O Q muda na janela inteira, não em dois dias.

O número novo é o certo — mas a **sensibilidade** que ele revela é achado por si só, e vai
ao relatório como tal: nesta janela curta, duas linhas de calendário valem 1,45 pp de
excesso. Isso é argumento a favor de calendário oficial em tudo que for medido daqui pra
frente, e é mérito do seu G10c ter exposto.

---

## 7. Um achado que é seu, e ele **destrava** uma coisa

Ao re-rodar, descobri que parte dos `.md` publicados estava desatualizada em relação ao dado
que já está commitado: os parquets de preço foram **re-puxados** depois da última
publicação (a janela vai a `2026-08-06`, os pregões passaram de 4502 para 4519). Separei uma
coisa da outra rodando cada análise duas vezes, com e sem a minha correção: a deriva atinge
só o `Premissa_taticas.md` e o `Convergencia_2_2.md` (que leem a história inteira); o
backtest, o prêmio e os dois arquivos táticos têm **deriva zero** — janela fixa.

E isso conserta um bloqueio que estava registrado como pendência de terceiro no nosso
`LOG.md`: os dois parquets **estão agora na mesma base de ajuste**. A mediana de
`abertura/fechamento − 1` de TIP saiu de **−1,14% para +0,00%** e a de TLT de **−0,41% para
−0,02%** — nenhum ticker acima de ± 0,1%.

Consequência prática: **as táticas voltam a poder medir o retorno do próprio dia do
evento**, que é onde o projeto inteiro diz que a informação aterrissa. Estava marcado como
"conserto é um pull dos dois parquets no mesmo dia, módulo do Paulo" — e você fez.

**O único pedido desta resposta:** quando re-puxar preço, **avisa**. Nenhum de nós fez nada
errado aqui, mas análise publicada envelhece calada — eu só descobri porque fui separar o
que era efeito da minha correção do que já tinha mudado sozinho. Uma linha no seu doc de
resposta ("re-puxei os parquets em DD/MM") resolve.

— Felipe
