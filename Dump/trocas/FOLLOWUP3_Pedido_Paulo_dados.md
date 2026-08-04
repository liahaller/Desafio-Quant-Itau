# FOLLOW-UP 3 — um item só: `G7`, base de ajuste dos dois parquets de ETF

> **Para o Claude do Paulo:** o follow-up 2 fechou o que faltava. Conferi **arquivo por arquivo** contra o
> `origin/Paulo` (@ `a9be92b`) e **tudo bate**: G1 (51.129 linhas, 9 tickers, 2003-12-05 → 2026-07-08, merge com o
> close sem sobra dos dois lados, zero abertura ausente), G2 (6.152 / 16.848 / 18.934 linhas, 253 / 719 / 799
> vazios, cabeçalho `observation_date,<ID>`, nenhum `"."`), G3 (soma Yes+No = 1,0000 nos dois mercados), G4
> (5 arquivos de jan/2026 presentes) e G6 (a linha crua de dez/2025 está lá; a correção de ano é minha e já roda
> no tratamento). **Nada disso precisa ser refeito.**
>
> Apareceu **uma coisa só**, e ela só dá para ver cruzando os dois arquivos de preço — por isso não caiu em
> nenhuma conferência anterior. É rápida de resolver e não muda nada do que já foi entregue.
>
> Regras de sempre: **você levanta e reporta, não decide nada**; campo não medido vai como `?`; dado cru não se
> normaliza. **Push com hash** no fim.

---

## G7 — `etf_open_daily.parquet` e `etf_prices_daily.parquet` não estão na mesma base de ajuste

**O que eu medi** (mediana de `abertura/fechamento − 1`, por ticker, nos 5.681 pregões):

| SPY | **TIP** | **TLT** | XLE | XLF | XLK | XLP | XLU | XLV |
|---|---|---|---|---|---|---|---|---|
| −0,06% | **−1,15%** | **−0,41%** | −0,05% | −0,04% | −0,06% | −0,04% | −0,04% | −0,03% |

Se os dois arquivos estivessem no mesmo ajuste, a linha inteira ficaria no ruído intradiário (± 0,1%), como
ficam os outros sete. **TIP e TLT não ficam — e são exatamente os dois ETFs de distribuição MENSAL.**

**O degrau tem data.** A razão `abertura/fechamento` do TIP fica em **0,9878** de 2003 até ~**2026-06-01** e vai a
**1,0000** de junho/2026 em diante. Isso é a assinatura de um ex-dividendo que entrou no ajuste de **um** dos dois
arquivos: o `auto_adjust=True` reescala **toda a história anterior à data-ex**, então quem baixou depois pegou um
fator a mais.

**A causa é o intervalo entre os dois downloads**, que está no próprio git:

```
etf_prices_daily.parquet  ->  commit 48cb12e, 2026-07-09
etf_open_daily.parquet    ->  commit 7ea4e86, 2026-08-02
```

**Por que isso importa:** as três táticas da camada tática usam a janela `abertura(D) → fechamento(D)`. Com os
arquivos como estão, essa janela ganha **+1,15% (TIP) e +0,40% (TLT) de retorno FABRICADO por dia** em toda a
amostra anterior a junho/2026 — com o espelho negativo no overnight. É alfa que não existe, no par de renda fixa
que mais pesa nas views de juros. Fechamento contra fechamento **não** é afetado, e as correlações também não
(o deslocamento é constante); o estrago é nas médias de qualquer janela que misture os dois arquivos.

**Não é erro de método:** você fez o G1 exatamente como pedi (`auto_adjust=True`, mesma base declarada do close).
O que ninguém previu é que "mesma base" depende também de **quando** cada arquivo foi baixado.

### O que fazer

Re-gerar **os dois** — abertura e fechamento — no **mesmo `yf.download`**, numa execução só. O caminho mais
seguro é pedir as duas colunas de uma vez (`Open` e `Close` do mesmo retorno, `auto_adjust=True`) e salvar as
duas a partir desse mesmo objeto: aí não existe janela entre pulls onde um dividendo possa entrar.

Se preferir manter dois arquivos irmãos em vez de um com duas colunas, tanto faz — **desde que saiam do mesmo
pull**. A escolha de formato é sua; a de fonte e universo não muda nada (segue yfinance, mesmos 9, mesma janela).

Duas coisas que ajudam a não repetir isso:
1. **Gravar a data/hora do download** no `data/README.md` (ou numa coluna de metadado), para qualquer um
   conseguir ver se dois arquivos são comparáveis sem ter que medir a razão.
2. Se o re-pull esticar a janela além de 2026-07-08, tudo bem — só **diga até onde foi**, porque o meu
   alinhamento com o poly usa o grid de datas do close.

### O que reportar

```
=== G7 — BASE DE AJUSTE ===
Arquivos gerados:            <caminhos>  (um pull só? SIM / NÃO)
Data/hora do download:       <timestamp>
Chamada usada:               <linha do yfinance, com auto_adjust>
Nº de linhas / tickers:      <n> / <lista>
Janela:                      <primeira data> → <última data>
Mediana de abertura/fechamento − 1, por ticker:
  SPY <v>  TIP <v>  TLT <v>  XLE <v>  XLF <v>  XLK <v>  XLP <v>  XLU <v>  XLV <v>
  (esperado depois do conserto: todos dentro de ± 0,1%; TIP e TLT são o teste)
Mudou algum fechamento em relação ao arquivo antigo?  SIM / NÃO — <onde e quanto>
```

O último campo importa: se o re-pull trouxer um fator de ajuste novo, a série de **fechamento** também muda de
nível, e as medições que já rodei em cima dela (perfil de defasagem k, sensibilidade) precisam ser refeitas.
Um `NÃO` me poupa isso; um `SIM` com o tamanho do deslocamento também serve.

---

## O que continua parado (sem ação sua por enquanto)

- **G5 (série de volume no tempo):** segue esperando a spec do Ω com a Lia — `Dump/trocas/Pergunta_Lia_omega_volume.md`.
- **G6 (CPI 2022–2024):** condicional à reunião, como combinado.
- *(Detalhe sem ação: no G3, os slots de 12h com os dois lados no M4 dão 715, não 716 — um slot tem só um lado.
  Não muda a conclusão de que o No é redundante.)*

---

## Formato da devolução

O bloco `=== G7 — BASE DE AJUSTE ===` preenchido, mais:

```
## Bloqueios
<o que não deu, com o motivo>

## Commit
<hash + branch do push>
```

E como sempre: **um `?` honesto é útil; um número inventado contamina uma decisão metodológica.**
