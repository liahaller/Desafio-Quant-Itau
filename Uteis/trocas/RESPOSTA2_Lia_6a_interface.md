# Para a Lia — verificação do lookahead feita, dict implementado, e uma notícia que muda seu dimensionamento

Oi, Lia. Resposta ao seu retorno de 2026-08-07 (decisão 6a + interface). Ordem: a **verificação que
você pediu** (feita, com a evidência), o **dict implementado** (está no ar, com uma ressalva de
nome), o que **não muda** do meu lado no 6a, e duas **notícias** que chegaram junto com a sua
resposta e mexem no seu item 4.

Aceitei os três pontos. O pedido de interface estava certo e o dp fica com você.

---

## 1. Verificação do `idade_ultimo_ponto_h = 0.0`: **não há lookahead**

Você pediu para eu confirmar se o último ponto da `serie_janela` é o slot **fechado antes** do
timestamp de decisão ou o slot que **contém** esse timestamp. A pergunta tem uma terceira resposta,
que é a que vale aqui: **o ponto não é um slot, é um instante.**

A série do `/prices-history` com `fidelity=720` não entrega agregado de 12h — entrega o **midpoint
amostrado no instante `t`**, com a grade caindo em 00:00 e 12:00 UTC e deriva medida de **3 a 9
segundos** (auditoria de 2026-07-30; que a série é o midpoint, e não o último trade, foi **medido**
pelo Paulo em dois mercados vivos no F-follow-up — antes disso era inferência nossa, e estava
errada).

Então o ponto das 12:00 UTC do dia D carrega preço formado **até** as 12:00 UTC, não depois. E a
execução do dia D é na abertura de Nova York — 13:30 UTC no horário de verão, 14:30 fora dele.

```
12:00 UTC  ── leitura que a view usa (07:00/08:00 em NY)
13:30 UTC  ── abertura, execução
```

`idade_ultimo_ponto_h = 0.0` quer dizer "o snapshot do próprio slot de decisão", que está **1,5 a 2,5
horas antes** da execução. A meia-fatia de lookahead que você descreveu existiria se a série fosse
agregado do intervalo; como é snapshot instantâneo, não existe. Nada a corrigir, e a estabilidade
que você mede não está inflada por esse caminho.

(O slot das 00:00 UTC também é pré-abertura, 12h mais velho. Ele está na `serie_janela` — nenhum
ponto foi descartado.)

---

## 2. Dict por nome: implementado, com **uma ressalva de chave**

Aceito, e já está no branch `Felipe`. Você tinha razão no diagnóstico: posicional não levanta
exceção, produz carteira plausível e errada. Eu não mantive a versão de vetor — deixar as duas
manteria a armadilha viva.

```python
# src/bl_integration.py
aplicar_veto(view_results, ativa, incerteza=None)
#   ativa     : dict[str, bool]
#   incerteza : dict[str, float] | None
#   -> (view_results com os vetados virados None, incerteza como VETOR já na
#      ordem de stack_views, reduzido aos sobreviventes)
```

**⚠️ A chave é o identificador longo, não o apelido curto.** No seu exemplo você escreveu
`{'2.2': 1.8, '2.3': 3.1, 'B': 1.2}`. A chave que a função casa é exatamente a string de
`diagnostics["view"]`, que é o que os módulos das views já emitem hoje:

| View | Chave |
|---|---|
| 2.2 inflação | `"2.2_inflacao"` |
| 2.3 Fed | `"2.3_fed"` |
| B trajetória | `"B_trajetoria_fed"` |

Não inventei um nome novo nem renomeei os seus: é o campo que você já recebe no `diagnostics` de
cada view, então a chave sai do mesmo lugar que o resto do bloco. Se preferir o apelido curto, eu
troco — mas aí trocamos nos dois lados de uma vez, não só na sua chamada.

**Chave que não casa é `ValueError`, não default:** falta, sobra ou nome errado levantam, com a lista
do que faltou e do que sobrou. `incerteza` é validado com o mesmo rigor de `ativa` (mandar `ativa`
completo e `incerteza` pela metade também levanta). As views desativadas pela cascata **não entram
nos dicts** — elas nem chegam a existir do seu lado.

Testes: `tests/test_bl_integration.py`, 9 verdes, incluindo os três casos de chave torta.

**Achado colateral, para você não confiar no número errado:** ao mexer nos testes descobri que o
bloco `if __name__ == "__main__"` desse arquivo estava no MEIO dele — os 4 testes definidos depois
nunca rodavam pelo comando padrão (`pytest` pegava, o script não). Dois outros arquivos de teste
chamavam nome antigo de função e morriam em `NameError`. Corrigido; a suíte inteira roda de novo.

---

## 3. Decisão 6a: nada muda do meu lado

Confirmado — **`dp_variacao_janela` continua saindo `NaN` de propósito e eu não vou preencher.** A
`serie_janela` continua crua e o `soma_faixas` continua cru e separado, que é o que deixa você
renormalizar antes de colapsar sem que o desarranjo do livro entre duas vezes. Seu argumento de que
a régua multiplicativa puniria a mesma coisa duas vezes fecha, e o teste de monotonicidade de fato
não pegaria (os dois ingredientes se moveriam juntos).

Sobre a ressalva da candidata **b**: registrada, e ela é mais forte do que parece — o balde aberto
(ponto médio extrapolado, meia largura) é uma das provisórias da seção 9 que o grupo revisa **em
bloco**, não uma pendência solta. Se **b** ganhar, a recalibração não é hipótese, é agendada.

Detalhe seu de pares adjacentes: sem objeção, e obrigado por registrar o "não normalizo pela
distância temporal" — é o tipo de escolha que ninguém consegue reconstruir depois.

---

## 4. Notícia 1: o `DFF` chegou e **a 2.3 está rodando** — k = 2 é a maioria da janela

O Paulo entregou o G8 hoje. Conferi contra o `origin/Paulo`: 26.334 linhas, **zero** campo vazio,
1954-07-01 → 2026-08-05. A 2.3 foi ligada na mesma sessão e o backtest já roda com as duas views.

**O que isso muda no seu item 2 (calibrar *entre* views):**

- **A 2.3 fica ativa em 325 dos 374 pregões (87%)**, e as duas views convivem em **240 dias (64%)**.
  Ou seja: k = 2 é o caso comum, não a exceção. A sua régua vai ser exercitada entre mercados
  diferentes na maior parte da amostra, e o seu item 3 (`c` e teto viram a mesma alavanca com k = 1)
  passa a valer só na minoria dos dias.
- A perna do poly da 2.3 é a **PMF completa de decisão por reunião** (`polymarket_fed_reunioes.parquet`,
  18 reuniões, 4–5 faixas). Então o `soma_faixas` da 2.3 chega até você com grade de verdade, não
  binário: na janela do backtest ele fica em **0,969 a 1,013**.
- Fechei duas decisões provisórias que te tocam de lado (seção 12 do `Decisoes_pendentes.md`, branch
  `Felipe`): `E_FF = DTB3 − DFF` com a surpresa **demeanada** por janela expansiva, e **PMF com soma
  crua < 0,9 desativa a view no dia** — na janela do v1 esse piso não mordeu nenhum dia, mas é o
  ponto em que a minha cascata e o seu portão de qualidade se encostam. Se a sua régua for punir
  soma ruim por outro caminho, me diga: dois cortes na mesma coisa é o erro que você mesma apontou
  no 6a.

## 5. Notícia 2: o G5 chegou, e a pergunta que sobrou é sua

`data/raw/g5_volume_no_tempo.csv` + `g5_volume_cobertura.csv`, 121 mercados, 12.928 slots, os dois
medidores (`notional_usd` e `n_trades`) no mesmo varrimento. O `t_cobertura_min` está lá, por
mercado.

O Paulo aplicou a sua spec ao pé da letra e **sinalizou um caso que ela não separa**: dos 424 slots
`NaN`, **346 são truncamento do cap** (o caso que o `t_cobertura_min` existe para proteger) mas
**78 são "pré-primeiro-trade" em 19 mercados que não foram truncados** — a série de preço já tinha
ponto (midpoint semeado na criação), só não houve trade nenhum ainda. Esses dariam para ler como
`0` legítimo. É decisão sua, e ele diz que é uma linha no script dele.

Vale notar que os dois casos significam coisas diferentes para o seu portão: truncamento é
**ignorância nossa** (o dado existe, a API não entrega), pré-primeiro-trade é **fato do mercado**
(ninguém negociou). Se o portão de volume trata `NaN` e `0` igual, a distinção não importa; se
trata diferente, importa muito.

**Aviso de encanamento:** ele registrou isso como "Decisão 12" no branch `Paulo`, e hoje o 12 do
branch `Felipe` é o `E_FF` da 2.3. A numeração diverge **a partir da 8** nos três branches (levantei
e escrevi a tabela no topo do `Decisoes_pendentes.md`). Quando citar número de decisão, diga também
de qual branch — "D12 do `Paulo`", não "D12".

---

## 6. Sobre o seu parágrafo de honestidade (+15,7% × +30,1%)

Concordo com o mecanismo — `c ≥ 1` só encolhe, e no limite a carteira vira o benchmark. Só reancoro
o número, porque ele mudou depois que você escreveu:

Aquele buraco de ~14 pp contra o SPY era **escopo do teto**, não a view. Medindo com o teto cortando
só o tilt (e pareando pela alavancagem realmente carregada), a parcela de tilt saía de **−11,84%
para +0,35%** e o excesso contra o SPY, de −14,39 pp para **−0,94 pp**.

Com a 2.3 ligada, hoje: **+2,68 pp** de excesso (teto no tilt = 1, alavancagem medida 1,90) — a
carteira passou a bater o comprar-e-segurar SPY. Na mesma alavancagem medida de 1,90, o teto de
carteira dá −7,91 pp e o teto no tilt +2,68 pp.

Então o número que você viu (+15,7% × +30,1%) já está duas medições atrás. O que continua valendo é
o mecanismo que você escreveu: `c ≥ 1` só encolhe, e um `c` agressivo vai comer esse +2,68 pp em
direção ao benchmark. Só que agora ele encolhe um resultado positivo, não um negativo — o que muda
a leitura de um `c` alto de "conserto" para "custo". Melhor você saber isso antes de calibrar.

---

## Encaixe atual, sem ambiguidade

```python
# src/bl_integration.py
aplicar_veto(view_results, ativa, incerteza=None)
#   ativa/incerteza: dict chaveado por diagnostics["view"] ("2.2_inflacao", "2.3_fed", ...)
#   devolve (view_results, incerteza_vetor) já alinhados para o omega_fallback

# src/market_inputs.py
omega_fallback(P, sigma, tau, incerteza=None)   # incerteza: (k,) float, >= 1
```

`incerteza=None` segue devolvendo `diag(P·τΣ·Pᵀ)` puro — He-Litterman, teto de confiança. É o que
roda hoje, e o backtest não para enquanto sua régua não chega.
