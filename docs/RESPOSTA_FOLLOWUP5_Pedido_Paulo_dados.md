# RESPOSTA — FOLLOW-UP 5 · `G5` — slot pré-primeiro-trade: aplicada a régua da Lia (Decisão 12 do `Paulo`)

> A resposta da dona da régua chegou no FOLLOWUP5: **separar os dois casos** no
> `NaN`/`0` do G5. Apliquei exatamente isso — **uma condição** no
> `scripts/g5_volume_no_tempo.py` —, re-rodei (cache local, sem nova chamada de
> API) e conferi linha a linha. Nada mais foi tocado: mesmo escopo, mesmo grid de
> 12h, mesmo `t_cobertura_min` por mercado.

---

## O que a Lia decidiu (FOLLOWUP5) e o que eu fiz

| Caso | Slots | Antes (F4) | Agora (F5) | Por quê (palavra dela) |
|---|---|---|---|---|
| Truncamento do cap de 20k | **346** | `NaN` | `NaN` | Ignorância nossa — o dado existe, a API não entrega. Propaga como "sem dado", não veta. |
| Pré-primeiro-trade (19 mercados não capados) | **78** | `NaN` | **`0`** | Fato do mercado — ninguém negociou. É `0` legítimo e **veta** o portão de volume dela. |

`NaN` e `0` deixaram de ser intercambiáveis na série: `NaN` agora aparece
**só** quando houve truncamento; `0` é sempre volume genuinamente zero.

---

## A mudança no código (a "uma linha" que ela previu)

A régua antiga marcava `NaN` para **todo** slot antes do `t_cobertura_min`. A nova
condiciona o `NaN` a o mercado ter batido no cap:

```python
# antes
if cov_slot is None or s < cov_slot:
    ...  # NaN

# agora
if res["bateu_cap"] and (cov_slot is None or s < cov_slot):
    ...  # NaN só se o mercado foi truncado
# else: mercado não capado antes do 1º trade cai aqui e vira 0 legítimo
```

Para um mercado **não** capado, o `t_cobertura_min` é o 1º trade **real** (a API
alcançou a vida inteira); os slots anteriores caem no `else` e recebem
`agg.get(s) = (0.0, 0)` → `0`. Para um mercado **capado**, os slots anteriores
continuam `NaN`. Também atualizei a docstring e os rótulos do report para
descreverem a régua dos dois casos (comentário, não muda dado).

`t_cobertura_min` por mercado: **inalterado** — o `g5_volume_cobertura.csv` não
mudou (nem entrou no `git status`). Escopo, grid de 12h, `notional_usd` e
`n_trades` positivos: **idênticos**.

---

## Prova numérica (re-rodado e conferido contra o CSV)

```
=== G5 — VOLUME NO TEMPO (após régua da Lia / FOLLOWUP5) ===
Nº de linhas:   12928   (inalterado)
Nº de mercados: 121     (2.2=111 · 2.3=1 · B=9, inalterado)
Janela:         2024-12-30 00:00 → 2026-07-29 12:00 (UTC, inalterada)
Mercados que bateram no cap de 20k: 3  (M2_fomc, M3 4-cuts, M3 5-cuts — inalterado)
Slots com volume 0 legítimo:  2481   (era 2403; +78 pré-1º-trade)
Slots NaN (só truncamento):   346    (era 424; −78)
```

| Contagem | F4 (antes) | F5 (agora) | Δ |
|---|---:|---:|---:|
| `NaN` (campos vazios) | 424 | **346** | −78 |
| `0` (`n_trades=0`) | 2 403 | **2 481** | +78 |
| positivos (`n_trades>0`) | 10 101 | 10 101 | 0 |
| **total de linhas** | 12 928 | 12 928 | 0 |

Checagens que rodei:
- **`NaN` em mercado não capado = 0** — todo `NaN` restante está num dos 3
  mercados capados. Os 346 são exatamente os do truncamento (os 2 M3 capados:
  4-cuts=309, 5-cuts=37; o M2 capou mas seu `t_cobertura_min` cai antes do 1º
  slot da série, então já contribuía com 0 `NaN`).
- **+78 exatos** migraram de `NaN`→`0`, nos mesmos **19** mercados não capados do
  breakdown do F4. Nenhum positivo virou `0` nem vice-versa.

---

## O que isso destrava (contexto que ela deu)

A série de preço do Polymarket é **midpoint**, não último trade — então nunca
fica vazia por falta de negociação. Midpoint parado num mercado ilíquido leria
como **estabilidade perfeita** na régua dela; sem o portão de volume, o mercado
mais ilíquido ganharia confiança **máxima** (inversão de sinal). Os 78 slots
pré-trade são o midpoint semeado na criação do book — o caso puro que o portão
existe para vetar; tratá-los como `NaN` deixaria passar exatamente esse exemplo.
Por isso `0`.

Registro também, para a fila: a Lia **revogou** o "entrego o `c` sem portão de
volume se o G5 atrasar" (05/08) — sem volume a estabilidade não é interpretável.
Com isso o **G5 deixou de ser um dos quatro insumos e virou pré-condição** de um
deles. Com esta entrega, este era **o único item da régua dela ainda bloqueado**
— e está resolvido. Nada do lado dela dependia do valor (o backtest roda com
`incerteza=None`).

---

## Encanamento (registrado, não é ação)

Anotado o aviso da numeração: as decisões divergem **a partir da 8** entre os três
branches — o "12" **do `Paulo`** é este G5; o "12" do `Felipe` é o `E_FF` da 2.3.
Adoto a convenção da Lia e do Felipe: citar sempre o branch — **"D12 do `Paulo`"**,
nunca "D12". Esquema definitivo fica para a reunião.

---

## Estado da Decisão 12 (`Paulo`)

A régua é da Lia e ela respondeu por escrito no FOLLOWUP5; a implementação está
feita e conferida. Marquei a **Decisão 12 do `Paulo` como 🟢 fechada** no
`Decisoes_pendentes.md`, atribuindo a decisão à Lia (FOLLOWUP5) e registrando a
troca no script. Não fechei nada por conta própria — só transcrevi a decisão da
dona da régua. Se preferir manter aberta até a reunião, é só dizer que reverto.

## Bloqueios

- **Nenhum.** O único item da régua da Lia que dependia do G5 está entregue.
- **Cache:** re-rodei com o `data/raw/g5_cache/` local (git-ignored) — **zero**
  chamada nova de API; só a régua de `NaN`/`0` mudou.

## Arquivos alterados

- `scripts/g5_volume_no_tempo.py` — condição do `NaN` (só truncamento) + docstring/rótulos.
- `data/raw/g5_volume_no_tempo.csv` — 78 slots `NaN`→`0` (346 `NaN` de truncamento mantidos).
- `data/raw/g5_volume_cobertura.csv` — **sem alteração** (`t_cobertura_min` intacto).
- `Decisoes_pendentes.md` — Decisão 12 do `Paulo` fechada (resposta da Lia).

## Commit

- **Branch:** `Paulo` · base `a4d1d18`.
- **Hash:** `08decf6` (entrega FOLLOWUP5 no branch `Paulo`).
