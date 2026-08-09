# Aviso à Lia — números republicados (calendário do CPI corrigido)

**Do Felipe. 2026-08-09.** Não é pedido nem decisão: é aviso de que **números que você pode
já ter citado no relatório mudaram**. Nada do seu módulo precisa ser refeito.

## O que aconteceu, em três linhas

O G10c do Paulo trouxe o calendário oficial do CPI (FRED) e ele expôs **duas datas erradas**
no calendário que usávamos, as duas na janela do shutdown de 2025:

- o CPI de set/2025 saiu em **24/10**, não em 15/10 (atraso do shutdown);
- o CPI de out/2025 **nunca foi publicado** — o `2025-11-13` era um **evento fantasma**.

Corrigido na nossa camada de tratamento (`load_cpi_releases`), não no arquivo do Paulo, que
segue cru. Depois do tratamento o calendário bate 14/14 com o FRED.

## O que mudou nos números que te interessam

| número | publicado | agora |
|---|---|---|
| prêmio de anúncios — t de Welch | +2,27 | **+2,12** |
| prêmio — eventos | 32 | **31** |
| backtest v1 — excesso × SPY (`tilt ≤ 1`) | +2,62 pp | **+4,07 pp** |
| Σ\|w\| pedida — mediana em `c = 1` | 198,7 | **192,0** |

**Nenhum veredito mudou de sinal.** O gate segue reprovando os 4 candidatos, as duas sleeves
da D16 seguem reprovadas, o prêmio segue positivo.

## Na SUA régua do `c` — a conclusão fica de pé, a sensibilidade cresce

Re-rodei o `curva_c.py` (ele passa pelo backtest, então dependia do calendário).
`Dump/analises/Curva_c.md` está atualizado. O que mudou:

- **A conclusão do passo (3) continua valendo, e igual:** o `c` **não** substitui o
  limitador de tamanho. Mesmo em `c = 0,01` a Σ|w| pedida ainda tem mediana **4,8** — acima
  do teto de 1. Os dois têm de conviver.
- **O `c` pesa MAIS do que estava publicado:** no teto de 1 ele move o resultado em até
  **6,34 pp** (era 5,01 pp). Sua escolha de nível decide mais resultado, não menos.
- **O ponto de troca de sinal andou:** no escopo `no tilt` o excesso ficava negativo já em
  `c = 0,02` (−0,03 pp); agora só vira em `c = 0,01` (−0,11 pp).

Isso **não** muda nada do seu módulo, nem a interface, nem o que você tem a entregar. O
nível do `c` segue sendo sua decisão e segue pendente, com o corte de 13/08 de pé.

## Uma coisa que talvez valha um parágrafo no relatório (sua chamada, é seu módulo)

Duas linhas de calendário mexeram o resultado-título do v1 em **+1,45 pp**. O mecanismo não
é "dois pregões trocaram de lado": com o release fantasma no arquivo, a view 2.2 lia o
mercado errado como vigente por **dois meses** (meados de out a meados de dez/2025).

O número novo é o certo — mas a **sensibilidade** é achado por si só, e é honesto: numa
janela curta como a nossa, erro de calendário vale mais que boa parte das escolhas de
modelo. Se for para a seção de limitações/robustez, o argumento que ele sustenta é
"calendário oficial em tudo que for medido", não "o resultado melhorou".

## Arquivos regenerados (é de onde tirar número daqui pra frente)

`Backtest_v1.md` · `Curva_c.md` · `Curva_banda.md` · `Curva_orcamento.md` ·
`Premio_condicional.md` · `Convergencia_2_2.md` · `Premissa_taticas.md` ·
`Tatica_reconstruida.md` · `Gate_sleeves.md`

Detalhe completo na sessão 15 do `LOG.md`; a resposta ao Paulo está em
`Dump/trocas/RESPOSTA_FOLLOWUP_G10_Paulo.md`.

— Felipe
