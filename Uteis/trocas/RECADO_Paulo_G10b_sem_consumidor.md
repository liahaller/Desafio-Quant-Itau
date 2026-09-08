# Recado ao Paulo — o G10b ficou sem consumidor, e o motivo é meu, não seu

**Do Felipe. 2026-08-11.** Não é pedido nem correção: é aviso, para você não
reservar trabalho em cima de uma coisa que parou. Nada a fazer do seu lado.

---

## 1. O G10b está certo e não vai ser usado no v1

Os 182 rótulos casaram 182/182 com os JSONs, o `groupItemTitle` veio cru e o
nome de campo verdadeiro foi reportado em vez de forçado. **Entrega correta.**

O que mudou foi a premissa do pedido, do meu lado e depois dele: pedi o G10b
porque ele *"destrava payrolls como família de view"*. Em 10/08 o dono fechou o
conjunto de views em **quatro** (2.2 · 2.3 · 15b incerteza · 15g B própria) e
declarou o conjunto **encerrado** (D23e) — não há mais candidata, e payrolls não
entrou.

E há uma segunda razão, técnica, que vale você saber porque ela contraria o que
eu escrevi no pedido: **a única view que hoje lê os mercados de payrolls não usa
valor de balde.** A 15b lê a **entropia normalizada da PMF**, que é invariante à
ordem das colunas e à renormalização — por isso ela funciona com os JSONs do G9b
mesmo sem rótulo. Rótulo de balde só seria necessário para uma view que
calculasse `E_poly` em número (como a 2.2 faz no CPI), e essa view não existe.

**Conclusão:** o `payrolls_bucket_labels.csv` fica no `origin/Paulo`, correto e
parado. Se o conjunto de views reabrir depois do v1, ele já está pronto — o
trabalho não se perde, só não tem consumidor agora.

**O que eu deveria ter feito diferente:** conferir se o consumidor do dado
existia antes de pedir o dado. O pedido dizia para que era, o que foi certo; o
que faltou foi checar se aquele "para que" dependia de uma decisão que ainda não
tinha sido tomada. Fica registrado como aprendizado meu.

---

## 2. O G10a, ao contrário, entrou em produção

O `fred_DGS1.csv` é o vértice da **15g**, que é uma das quatro views da entrega:
os β saem por event-study expansivo contra o **ΔDGS1** nos dias de FOMC, e a
view roda em **210 pregões**. Sem o G10a ela não existiria — era o item que você
marcou como "faça este se fizer um só", e estava certo.

Registrado também no README deste branch: quem for reproduzir o `Backtest_v1.md`
precisa extrair o `data/` do `origin/Paulo` **incluindo o `fred_DGS1.csv`**, ou
o `load_fred` estoura. Falha alto, nunca calada.

---

## 3. O aviso de re-puxada funcionou — mantenha

A linha sobre os dois parquets de ETF re-puxados em **06/08/2026** (`87721ae`,
janela até `2026-08-06`, 4519 pregões) é exatamente o que eu precisava: é a base
sob o `Backtest_v1.md` de hoje. **Mantém a convenção** de avisar toda re-puxada
numa linha do doc de resposta — sem ela, um número de artefato muda sem que
ninguém saiba por quê.

---

## 4. Os dois avisos do `cpi_release_dates_fred.csv` estão registrados

Os 18 fevereiros de fatores sazonais (`release_id=10` compartilhado) e o
`mes_referencia` derivado quebrando na janela do shutdown estão anotados como
filtro **nosso**, não conserto seu. O calendário oficial não substituiu o seu
arquivo, como fechado: os dois ficam, com consumidores diferentes, e a correção
das duas divergências reais do shutdown já vive no `load_cpi_releases`.

---

**Nada pendente com você.** Os três itens do G10 estão entregues e aceitos, e
você não trava nada no caminho de 13/08.

— Felipe
