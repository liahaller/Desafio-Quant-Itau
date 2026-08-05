# Leave-off — sessão de 2026-08-05 (sessão 3, Felipe)

Ponto de retomada para a próxima sessão. **Leia também** a entrada
`## 2026-08-05 (sessão 3) — Felipe` do `LOG.md`, que traz os números; este
arquivo é o resumo operacional.

---

## O que mudou nesta sessão

1. **O push destravou** — a maratona inteira chegou ao repo compartilhado.
2. **Os dois recados que faltavam foram escritos** (nenhum dos três enviado).
3. **O I5 está pronto e rodando no dado real** — a entrega final existe.

O princípio do dono continua valendo:

> Cortar view é ruim. É melhor fazer algo mais complexo para manter a view do
> que simplesmente tirá-la.

---

## Estado do v1

| | |
|---|---|
| **Views que RODAM hoje** | **só a 2.2 inflação** |
| **Views bloqueadas por dado** | 2.3 (falta `DFF`/G8) · B (precisa do ZQ de dezembro, sem fonte e **sem pedido a ninguém**) |
| **Camada tática** | desligada — faltam os orçamentos (parâmetro de reunião) |
| **Parâmetros** | H = 1 dia · δ = 3,0 · τ = 1/504 · duration da 2.2 = **medida, 8,31–8,38** · teto Σ\|w\| varrido em {1,2,3,5} · custo 2 bps/lado |
| **Suíte** | 158 testes verdes |
| **Branch** | `Felipe`, sincronizada com `origin/Felipe` ✅ · conta `gh` = `menusoids-p` |

---

## O resultado do backtest

353 pregões (2025-02-10 → 2026-07-08), só a 2.2 ativa (74% dos dias):

| | Σ\|w\| ≤ 1 | ≤ 2 | ≤ 3 | ≤ 5 |
|---|---|---|---|---|
| retorno líquido | +8,6% | +7,4% | +6,1% | +3,5% |
| sharpe | 0,71 | 0,59 | 0,47 | 0,26 |
| giro diário médio | 0,22 | 0,36 | 0,50 | 0,78 |
| giro desfeito em 1–2 pregões | 33% | 32% | 32% | 32% |
| custo de breakeven | 13,3 bps | 8,1 | 5,8 | 3,6 |

**Benchmark (comprar e segurar SPY): +26,2% — a carteira perde por 17,6 pp.**

**O custo não é o culpado:** o bruto já é +10,3% e o breakeven é 6,7× a
premissa. A explicação mais provável é mecânica — o teto escala todas as pontas
junto, inclusive a de SPY do prior, e a view tira orçamento do SPY numa janela
em que o SPY fez +26%.

---

## O que falta — em ordem

### 1. Esperar as respostas — os três recados FORAM ENVIADOS em 05/08 ✅
- **`FOLLOWUP3`** ao Paulo — G7 (base de ajuste) + G8 (`DFF`).
- **`PEDIDO_G9_payrolls_Paulo.md`** ao Paulo — calendário + mercados.
- **Régua do Ω à Lia** — seção 4 do `Pergunta_Lia_omega_volume.md`.

Nada a despachar. A próxima sessão trabalha no que **não** depende deles
(item 2 abaixo) e integra as respostas conforme chegarem.

**O que cada resposta muda no backtest:**

| resposta | efeito |
|---|---|
| **G8 / `DFF`** | destrava a **view 2.3** — o backtest deixa de rodar com uma view só |
| **Ω da Lia** | mexe **direto na alavancagem**: `c > 1` encolhe o tilt e dispensaria o teto |
| **G7** | **nada aqui** — este backtest é fechamento contra fechamento; o G7 só contamina `abertura→fechamento` (janela das táticas) |
| **G9 / payrolls** | nada enquanto a camada tática estiver desligada |

### 2. A questão de desenho que o backtest abriu
**O teto corta a carteira inteira ou só o TILT da view, deixando a perna de
mercado intacta?** Hoje corta tudo, e é a explicação mais provável da
underperformance. Registrada na seção 10 do `Decisoes_pendentes.md`, **não
decidida**. É o primeiro item a testar na próxima sessão — é uma linha de código
e pode mudar o resultado inteiro.

### 3. Ligar a camada tática
O script já está ligado nos orçamentos: passar `--orcamento-premio`,
`--orcamento-drift-acoes`, `--orcamento-drift-rf` liga sem tocar em código. Os
valores são **parâmetro de reunião** — não foram inventados.

### 4. Revisão do grupo
Seção 9 (13 decisões, prioridade D7 τ/δ) + **seção 10 nova** (duration medida e
teto de alavancagem — o teto encosta no módulo de risco da Lia).

---

## Como rodar

O dado do Paulo vive no branch `Paulo`, não neste:

```
git archive origin/Paulo data/ | tar -x -C <dir temporario>
python scripts/backtest_v1.py --raiz <dir temporario>
```

Roda em ~30 s e escreve `Dump/analises/Backtest_v1.md`.

---

## Armadilhas que a próxima sessão precisa saber

- **Sem teto, o backtest vai à ruína.** Σ|w| mediana 24, máximo 264. Não é bug:
  o I3b casou a duration do par TIP/TLT para cancelar o movimento de juros, e
  `w ∝ Δμ/(δσ²)` numa direção de variância pequena explode por construção.
  Qualquer mexida no P da 2.2 precisa olhar esse número.
- **`None` de view tem dois significados diferentes.** Cascata (não havia
  mercado) e insumo que não chegou (2.3 e B) não são a mesma coisa — o script
  declara as segundas em vez de deixá-las cair silenciosamente em `None`.
- **A informação do Polymarket aterrissa no gap de abertura.** Continua valendo:
  qualquer tese nova que dependa de "a bolsa demora a absorver" tem de ser
  testada em `abertura → fechamento`.
- **O arquivo `M9_midterms_2022_will-the-democratic-party*` é o mercado da
  Câmara 2026**, não de 2022 — o único teste fora da amostra que o projeto tem.
- **`gh auth login --web` trava sem terminal interativo.** Se a credencial
  desandar de novo, o caminho que funcionou foi o **device flow por curl** (o
  dono autoriza o código no browser), não o comando interativo.
