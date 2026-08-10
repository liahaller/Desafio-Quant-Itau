# Candidatos — views construídas e não decididas

Este arquivo lista **apenas as views em estado CANDIDATA**: montadas, medidas e
sem destino. Views aceitas, rejeitadas, adiadas e mortas por dado ficam no
`Decisoes_pendentes.md` e no `Dump/analises/Retomada_tatica.md`.

**Nada aqui está decidido.** A coluna "o que falta" lista condição, não
recomendação.

> # 🟢 ARQUIVO ZERADO — não há nenhuma view em estado candidato
>
> **2026-08-10 (sessão 23), por decisão do dono: o conjunto de views está
> FECHADO em quatro — 2.2 · 2.3 · 15b · 15g.**
>
> - A **15b** e a **15g** saíram daqui porque **entraram**: cumpriram os quatro
>   itens da D22 e as três decisões humanas que as travavam fecharam (D15a dupla
>   leitura · D15b P direcional · D15c entropia crua · D22e item 4 medido). A
>   entrega passou de +4,07 pp para **+6,24 pp**. Registro na **D23**.
> - A **C** saiu porque **não entra** (D23f). Ela passou os quatro itens da
>   D22 — o corte não é da régua. O que a matou foi a premissa: o critério
>   pré-registrado para fixar o `k` foi executado pela primeira vez e **não
>   identifica k** (corr +0,08 entre os dois episódios do Irã), e o único lag em
>   que os episódios concordam é o **lag 0** — o gap de abertura, que a view não
>   pode usar por construção. Em paralelo, a **D4.1** bloqueia todo k ≥ 2 no
>   empilhamento, e o único k permitido (1) é o que inverte entre episódios.
>
> **Este arquivo não é lixo: é o registro de que a busca por views terminou.**
> Se uma view nova for proposta, ela volta a ser preenchido — com a régua da D22
> e com os dois precedentes de ρ abertos na D22e.

## Régua de admissão em vigor — **D22, fechada pelo dono em 2026-08-10**

Quatro exigências, todas necessárias:

1. **Lê o Polymarket** — o sinal da view vem de preço/PMF de mercado do poly.
2. **Atua na bolsa** — a view se expressa em ETFs do universo decidido (D1).
3. **Teoria não desprovada por teste** — nenhuma medição contradiz a tese
   declarada da view.
4. **Ortogonal ao que já está dentro** — ângulo alto entre o P dela e o das views
   ativas, sem ρ alto no sinal-fonte.

**Sinal fraco não é impedimento.** |t| baixo, acerto de sinal perto de 50% e Δ
negativo no backtest **não** reprovam uma candidata. O que reprova é a tese ser
contrariada pelo dado — o precedente D2b ("não se inverte") continua valendo,
agora como conteúdo do item 3.

A D22 **não vai à reunião**: foi fechada por instrução explícita do dono. Ela
absorve a régua 18a (item 1) e formaliza o critério de dupla exposição (item 4),
que até então era precedente solto.

---

## Resumo — nenhuma candidata

| View | 1 poly | 2 bolsa | 3 tese | 4 ortogonal | Destino |
|---|---|---|---|---|---|
| **15b** incerteza | ✅ | ✅ SPY | ✅ t +0,06 | ✅ ρ ≤ 0,19 | **ENTROU** (D23) |
| **15g** B β próprio | ✅ | ✅ XLE/XLF | ✅ t +0,33 | ✅ 87,5° · ρ +0,673 | **ENTROU** (D23) |
| **C** geopolítica | ✅ | ✅ XLE | ✅ nenhum k inverte | ✅ 88,7°–160,9° | **FORA** (D23f) |

**Repare que a C passa os quatro itens da régua e mesmo assim não entra.** Isso
não é contradição: a D22 diz quem *pode* entrar, não quem *deve*. O que barrou a
C está fora da régua — o parâmetro central dela (o `k`) não tem critério que o
fixe, e a D4.1 bloqueia os valores que o teste de sinal favorece.

**Dois precedentes abertos na D22e, para quem propuser view nova:**

1. **O ângulo não testa view direcional.** Contra o P de `P_from_betas` (que
   crava P[SPY] = 0 exato) o produto interno é zero por construção: qualquer
   view direcional dá 90,0° com qualquer view neutra, em qualquer amostra. Para
   essas, o item 4 se decide **só pelo ρ**.
2. **A barra do "ρ alto" está acima de 0,827.** Dois casos julgados como não
   reprovando na mesma sessão (15g +0,673 em 168 dias; C +0,827 em 25). Se um
   terceiro aparecer, vale dizer que o item 4 opera só pelo ângulo na prática,
   em vez de manter um critério que nunca barrou ninguém.
