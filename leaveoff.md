# Leave-off — sessão de 2026-08-04 (sessão 2, Felipe)

Ponto de retomada para a próxima sessão. **Leia também** a entrada
`## 2026-08-04 (sessão 2) — Felipe` do `LOG.md`, que traz os números de cada
decisão; este arquivo é o resumo operacional.

---

## Contexto que mudou o modo de trabalhar

O grupo **liberou o Felipe a fechar sozinho** as decisões que estavam travadas
em reunião, por causa da proximidade da entrega. Todas as decisões desta sessão
são **provisórias e marcadas para revisão do grupo** — a instrução do dono foi
"vamos construindo com elas, depois o grupo volta e olha com mais calma".

**Princípio dado pelo dono, que vale para as próximas sessões:**
> Cortar view é ruim. É melhor fazer algo mais complexo para manter a view do
> que simplesmente tirá-la.

Na prática: antes de recomendar tirar qualquer view, esgotar os redesenhos
(reestimar β na janela negociável, virar contemporânea com a natureza
declarada, trocar o benchmark por um termômetro externo) e dizer qual foi
tentado.

---

## Estado do v1 depois da maratona

| | |
|---|---|
| **Views ativas** | 2.2 inflação · 2.3 Fed · B trajetória do Fed |
| **Views fora** | 2.4 eleitoral · 3.1 recessão · C geopolítica · E tarifas · G fiscal |
| **Táticas ativas** | prêmio de anúncio condicionado à incerteza · drift pós-FOMC |
| **Tática fora** | gap de fim de semana |
| **Parâmetros** | H = 1 dia · δ = 3,0 · τ = 1/504 · balde aberto = meia largura · faixa faltante = carrega · sem FL (γ = 1,0) · custo 2 bps/lado |
| **Fonte de juros** | DTB3 do FRED (o ZQ não tem fonte grátis) |
| **Suíte** | 134 testes verdes |
| **Branch** | `Felipe`, worktree limpa, **23 commits à frente do `origin/Felipe`** — ⚠️ **push bloqueado por permissão**, ver seção 5 |

---

## O que foi decidido (13 decisões)

Todas em `LOG.md` com o número que sustenta cada uma. Resumo:

- **D1** H = 1 dia.
- **D2** views poly-defasadas fora (só ~23% do efeito sobrevive na janela negociável).
- **D2b** 3.1 fora — o sinal que existe é **direcional** e o P dela é neutro em mercado por construção.
- **D2c** redesenho tentado nas quatro; 2.4 **reprovou fora da amostra** no mercado da Câmara 2026; C tem o mecanismo (XLE r = +0,54 no gap) mas não na janela negociável; E e G têm 13 e 3 dias de dado.
- **D3** camada tática **entra redesenhada** — o prêmio de anúncio aparece quando se condiciona à incerteza da PMF (+0,383% vs −0,704%, t de Welch +2,10).
- **D3b** gap de fim de semana fora (condicionar achou significância, mas com sinal de reversão).
- **D4** balde aberto = ponto médio extrapolado; faixa faltante = carrega a última leitura e renormaliza.
- **D5** sem correção de favorite-longshot no v1, com γ ∈ {1,0; 1,1; 1,25} como robustez.
- **D6** ZQ substituído por ΔDTB3 (36 reuniões, 7/7 sinais coerentes com Bernanke-Kuttner).
- **D7** δ = 3,0 (medido no nosso SPY) e τ = 1/T, com o Ω ancorado em `diag(P·τΣ·Pᵀ)`.
- **D8** custo 2 bps/lado + financiamento + aluguel declarados; a métrica do relatório é o **custo de breakeven**.
- **D9** divergência demeanada e horizonte = pregões até a divulgação do CPI.
- **D10** quatro limitações declaradas; 5.3 (petróleo) virou munição do D2c; payrolls virou D3c.

---

## O que foi implementado

| Arquivo | O que é |
|---|---|
| `src/config.py` | **novo** — todos os parâmetros decididos num lugar só (I1) |
| `src/market_inputs.py` | **novo** — Σ amostral, `w_mkt` do prior CAPM, duration empírica, Ω de fallback (I3/I4) |
| `src/poly_preprocessing.py` | destravado: `favorite_longshot`, `favorite_longshot_pmf`, `carry_missing`, `bucket_values_with_open` (I2) |
| `src/view_2_2_inflacao.py` | P casado em duration, divergência demeanada, Q dividido pelos dias até a divulgação (I3b + D9) |
| `scripts/janela_negociavel.py` | **novo** — quanto do lag 0 sobra na janela negociável |
| `scripts/premio_condicional.py` | **novo** — prêmio de anúncio por entropia da PMF |
| `scripts/surpresa_fomc.py` | **novo** — ΔDTB3 como substituto do ZQ |
| `scripts/convergencia_2_2.py` | **novo** — horizonte de convergência da 2.2 |
| `scripts/nivel_divergencia_3_1.py` | **novo** — sinal de nível da 3.1 |
| `scripts/gap_fds_condicionado.py` | **novo** — gap de fds condicionado |
| `Dump/analises/*.md` | 6 relatórios novos, um por script |
| `Dump/trocas/FOLLOWUP3_...md` | ganhou o **G8** (série `DFF` do FRED) |

Duas decisões de módulo tomadas sozinho (categoria 2 do CLAUDE.md §1), com o
motivo registrado no código:

1. **`w_mkt` = 100% SPY (prior CAPM).** Não há dado de tamanho dos ETFs, e peso
   igual entre SPY e sete setores dele contaria a bolsa duas vezes. Benefício
   colateral: o benchmark do backtest vira comprar e segurar SPY.
2. **Durations medidas, não copiadas da ficha do emissor** — TIP 5,09 anos e
   TLT 14,53, estimadas contra a variação do DGS10.

---

## O que falta — em ordem

### 1. `I5` — loop de backtest / rebalanceamento (**é a entrega final**)
Andar nas datas, montar as views ativas, chamar `bl_weights_from_views`,
aplicar custo e produzir a série de retorno. **Tudo de que ele depende já está
pronto** (config, Σ, `w_mkt`, Ω de fallback, views com horizonte declarado).

Duas checagens **obrigatórias**, vindas da pesquisa do D8:
- reportar o **giro diário médio** na mesma tabela do resultado;
- decompor **quanto do giro é reversão de posição em 1–2 dias** — é o mecanismo
  que destruiu a estratégia GTAA diária citada na pesquisa;
- teste unitário do motor de custo (ir de `w = 0` a `w = 1` num ativo tem de
  cobrar exatamente `c`).

**O D1 fica sob revisão condicional:** se o giro for alto e o custo de breakeven
baixo, a saída **não** é abandonar H = 1 dia — é banda de não-negociação, que a
pesquisa aponta como a mitigação simples mais eficaz.

### 2. Três recados prontos, nenhum enviado
- **`FOLLOWUP3` ao Paulo** — G7 (base de ajuste dos parquets) + G8 (`DFF`).
- **Pedido de payrolls ao Paulo** (`D3c`) — calendário + mercados, mesmo
  procedimento do G4. Aumenta a amostra da tática de prêmio, que hoje roda com
  19 eventos.
- **Régua do Ω para a Lia** — o Ω precisa vir como **multiplicador de
  confiança** sobre `diag(P·τΣ·Pᵀ)`, não como variância absoluta. É interface,
  não metodologia dela. Anexar ao `Dump/trocas/Pergunta_Lia_omega_volume.md`.

### 3. Pendências de dado
- **`I6`** — quando o G7 chegar, rerodar `market_loader.adjustment_gap` e
  revalidar qualquer janela `abertura → fechamento` de TIP e TLT. Nenhuma
  medição desta sessão depende disso (as janelas medidas terminam antes do
  degrau de ~2026-06-01, e deslocamento constante não move covariância).
- **`e_ff_bps` da view 2.3** fica incompleto até o `DFF` chegar. O β já roda.

### 4. Revisão do grupo
Item de revisão aberto na lista de tarefas, **prioridade D7 (τ e δ)**, que
encosta no módulo de risco da Lia. Depois: D2 (corte das defasadas), D3
(entrada da camada tática), D6 (DTB3 no lugar do ZQ).

### 5. ⚠️ O PUSH ESTÁ BLOQUEADO — resolver antes de qualquer coisa

`git push origin Felipe` falha com **403**:

```
remote: Permission to liahaller/Desafio-Quant-Itau.git denied to Gruppy-FelipeM
```

**Causa:** o repositório é da Lia (`liahaller/Desafio-Quant-Itau`); o `git` local
está com o usuário `menusoids-p` / felipe.menusier@gmail.com, mas a credencial
que o push usa é a conta **`Gruppy-FelipeM`** (é a conta ativa do `gh auth`), e
essa conta **não tem permissão de escrita** no repo. Sessões anteriores
empurraram com credencial diferente, ou o acesso da `Gruppy-FelipeM` foi
removido.

**Saídas (escolha do dono — não mexer em credencial por conta própria):**
1. `gh auth switch` / `gh auth login` para a conta com acesso, e repetir o push.
2. Pedir à Lia acesso de escrita para `Gruppy-FelipeM`.
3. Empurrar pelo terminal próprio, se o Credential Manager estiver com a conta
   certa fora do Claude Code.

**Estado:** branch `Felipe` **23 commits à frente do `origin/Felipe`**, worktree
limpa. Nada se perdeu — está tudo commitado localmente. Mas **nada da maratona
chegou ao repositório compartilhado**: o Paulo e a Lia ainda não veem nenhuma
das decisões, nem o código novo.

*(Resolvido: `Decisoes_pendentes.md` recebeu as 13 decisões como seção 9, em
tabela, marcadas como provisórias.)*

---

## Armadilhas que a próxima sessão precisa saber

- **A informação do Polymarket aterrissa no gap de abertura.** Apareceu em
  todas as medições — tática de fim de semana, eleição 2024, recessão 2025,
  Irã 2026. Qualquer tese nova que dependa de "a bolsa demora a absorver"
  precisa ser testada na janela `abertura → fechamento`, não de fechamento a
  fechamento.
- **O arquivo `M9_midterms_2022_will-the-democratic-party*` é o mercado da
  Câmara 2026** (355 dias), não de 2022. Foi puxado por engano pelo Paulo e é o
  único teste fora da amostra que o projeto tem.
- **Medir a coisa certa e medir bem são falhas independentes.** O erro desta
  sessão foi classificar a 3.1 como view defasada e cortá-la medindo `Δp`
  quando o sinal dela é de nível. A conclusão sobreviveu; o fundamento não.
- **O dado do Paulo vive no branch `Paulo`, não neste.** Para rodar os scripts
  sem merge:
  ```
  git archive origin/Paulo data/ | tar -x -C <dir temporario>
  ```
  e apontar `--dados`, `--precos`, `--abertura` etc. para lá.
