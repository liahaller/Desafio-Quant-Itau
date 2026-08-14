# Felipe — o nível fechou em 1, e falta acoplar a régua na entrega

**13/08/2026 · Lia.** Curto: a decisão que a reunião de hoje esperava está tomada
do meu lado, e sobra **uma linha** no teu módulo. Não toquei em nada teu.

---

## 1. A decisão

**`nível = 1`** — registrada como **6q** no `Decisoes_pendentes.md` (branch `Lia`),
fechada por mim. Era o último parâmetro livre do Ω.

O fundamento está inteiro no registro; o resumo é que **nenhum dos três eixos usa
retorno de carteira**:

1. **Nível 0 contradiz o resultado do próprio módulo.** Com expoente zero os dois
   ingredientes que *passaram* no teste de monotonicidade param de operar e sobra
   só o veto — que é o ingrediente *reprovado* como score e rebaixado a portão.
2. **Níveis altos concentram poder onde a régua não foi validada.** Ela foi
   calibrada em 2.2 e 2.3 e aplicada a quatro views. No nível 5 a régua corta
   ≥50% da confiança em **33% das decisões da 15b** contra **0,1% da 2.3** — ou
   seja, subir o nível morde quase só as views sem evidência (e a família de
   payrolls da 15b nem tem veto de liquidez).
3. **Subir o nível não compra controle de tamanho.** Os dias de ruína **nunca
   zeram** (24 no nível 8 contra 33 sem régua). Quem limita tamanho é o teto, não
   a régua — confirmado agora com a camada ligada.

⚠️ **Declarado no registro para não parecer post-hoc:** o nível 1 é também quase o
topo da coluna de excesso. O raciocínio não consultou essa coluna em momento
nenhum, mas a coincidência existe e está escrita lá.

---

## 2. O que falta do teu lado — uma linha

O `run_backtest` **já expõe** `regua=` e o `market_inputs.regua_por_decisao` já
faz o trabalho. O que não acontece é o `scripts/backtest_v1.py` passar o
parâmetro: o `main` chama `run_backtest` na **linha 973** sem `regua=`, então a
**entrega roda com Ω sem a minha régua**.

```python
# scripts/backtest_v1.py — no topo, junto dos outros imports de market_inputs
from market_inputs import regua_por_decisao

# no main, antes do laço dos tetos
regua = regua_por_decisao(args.raiz / "data/lia/c_por_decisao.csv", nivel=1)

# e na chamada da linha 973
resultado = run_backtest(..., teto_no_tilt=no_tilt, regua=regua)
```

O CSV é o mesmo já publicado — nada novo a gerar:

```
git show origin/Lia:lia/c_por_decisao.csv > data/lia/c_por_decisao.csv
```

**É decisão tua se e como acoplar** (inclusive se vira flag em vez de fixo). Só
não dá para ficar como está: enquanto não acoplar, o teu `Backtest_v1.md` e o
relatório final descrevem carteiras diferentes.

---

## 3. O que muda no número da entrega

Medido por fora, chamando o **mesmo** `run_backtest` com `regua=` (teto 1 no
tilt, camada ligada, γ = 1):

| | sem régua | com régua (nível 1) |
|---|---|---|
| excesso × SPY | +4,08 pp | **+3,04 pp** |
| retorno líquido | +34,20% | **+33,16%** |
| sharpe | 1,2136 | **1,1815** |
| Σ\|w\| média | 1,9438 | **1,9146** |
| giro diário | 0,3201 | **0,3963** |
| breakeven | 28,47 bps | **22,87 bps** |
| views/dia | 2,24 | **1,99** |

Antes disso eu reproduzi o teu `Backtest_v1.md` **dígito a dígito** sem régua
(sharpe 1,2136 · breakeven 28,4727 · excesso +4,08 pp), então a diferença acima é
a régua e nada mais.

---

## 4. Dois artefatos teus que ficaram desatualizados

**Não estou pedindo re-geração** — é chamada tua. Só registrando o que medi:

**(a) `Curva_c.md` — a grade de nível.** A tua própria D28.13 já o listava como
invalidado pela entrada da camada. Re-gerei com a entrega atual e o excesso cai
~3 pp em toda a linha:

| nível | Σ\|w\| pedida mediana | dias de ruína | excesso (tilt ≤ 1) |
|---|---|---|---|
| sem régua | 221,8 | 33 | +4,08 pp |
| 0 (só veto) | 177,5 | 31 | +3,17 pp |
| **1** | 174,5 | 28 | **+3,04 pp** |
| 3 | 162,6 | 27 | +2,60 pp |
| 5 | 147,8 | 26 | +1,88 pp |
| 8 | 130,5 | 24 | +0,49 pp |

Vale reparar: **o veto sozinho faz o corte pesado** (221,8 → 177,5 na Σ|w| pedida,
antes de qualquer dosagem), e todo o eixo restante tira só mais 26%.

**(b) `Camada_tatica_v2.md` — o custo da camada.** O `−2,16 pp` tem as duas pontas
**sem régua**. Medido na configuração da entrega (as duas pontas com régua nível 1):

| | sem régua | com régua nível 1 |
|---|---|---|
| excesso sem camada | +6,24 pp | +5,98 pp |
| excesso com camada | +4,08 pp | +3,04 pp |
| **Δ da camada** | **−2,16 pp** | **−2,94 pp** |

A régua encolhe o tilt das views e a camada disputa o mesmo orçamento de risco,
então cortar de um lado aumenta o peso relativo do outro. **Isto não reabre a
D28.13** — a decisão de entregar com a camada ligada é tua e não foi tomada por
este número. Fica só o registro de que ele mudou.

---

## 5. O que continua pendente, e é teu ou do grupo

- 🔴 **Acoplar a régua** (seção 2) — teu.
- 🟡 **O nível fica condicionado ao teto.** Pelo §9 do `RELATORIO_omega.md` a
  ordem é: entra o `c`, mede-se a Σ|w| resultante, e só então se decide o teto
  (**D12, do grupo**). Se o teto se mover, a conta do nível se refaz — e eu
  reabro a 6q.

---

## 6. Como reproduzir o que está aqui

Nada disso rodou no teu branch nem alterou arquivo teu. Montei um diretório de
trabalho fora do repositório com o teu código e o `data/` do Paulo, e os scripts
que usei estão em `relatorio/fonte/` no meu branch:

| script | o que mede |
|---|---|
| `extrair_serie_regua.py` | a entrega com `regua=` no nível 1 |
| `gamma_regua.py` | varredura de γ com a régua ligada (+3,04 a +3,89 pp) |
| `delta_camada.py` | as duas pontas da camada na mesma configuração |

A grade de nível saiu do teu `scripts/curva_c.py` sem modificação, com
`--regua lia/c_por_decisao.csv --niveis 0 1 2 3 5 8 --teto 1.0`.
