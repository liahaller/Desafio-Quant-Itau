# Candidatos táticos — desenhos nunca medidos

Este arquivo lista **apenas os desenhos da camada tática em estado CANDIDATO**:
os que saíram do escopo na decisão 10 **sem uma única medição**. Táticas com
certidão de óbito medida (gap de fim de semana, sleeves da D16/D17, drift
pós-FOMC) ficam no `Dump/analises/Retomada_tatica.md`.

Views estruturais candidatas ficam no `Candidatos.md`. **São camadas diferentes:**
uma view entra em P/Q do Black-Litterman; uma tática é overlay por cima dos pesos
já otimizados. Um candidato tático não compete com uma view candidata.

**Nada aqui está decidido.** A coluna "o que falta" lista condição, não
recomendação.

## Régua de admissão em vigor — **D22, fechada pelo dono em 2026-08-10**

A mesma régua das views estruturais vale aqui:

1. **Lê o Polymarket** — o sinal vem de preço/PMF de mercado do poly.
2. **Atua na bolsa** — se expressa em ETFs do universo decidido (D1).
3. **Teoria não desprovada por teste** — nenhuma medição contradiz a tese.
4. **Ortogonal ao que já está dentro** — ângulo alto entre os sinais, sem ρ alto
   no sinal-fonte.

**Sinal fraco não é impedimento.** O que reprova é a tese ser contrariada pelo
dado (precedente D2b, "não se inverte").

**As quatro passam os itens 1–3 por vacuidade** — nunca foram medidas, logo nada
as desprovou. O **item 4 não está medido em nenhuma das quatro**, e aqui ele é
mais mordaz que nas views: as quatro leem a mesma série de probabilidade em
janelas diferentes (resolução · salto · derivada · tendência), então a chance de
duas delas serem a mesma coisa com outro nome é alta — foi exatamente assim que
a C2a morreu (ρ −0,68 com a entropia da 15b). Isso não é aprovação: é a constatação de que o corte delas foi de
**escopo**, não de evidência. O que as separa de virar candidatas de fato são as
três condições de camada abaixo, todas já registradas e nenhuma delas nova:

- **Escopo (decisão 10).** As três saíram em reunião. Reabri-las é reabrir
  escopo, não rodar script — decisão do grupo.
- **Tamanho com âncora (12c).** A camada tática inteira foi desligada porque o
  dimensionamento era parâmetro livre (Δ monótono no orçamento, sem ótimo
  interior). O mesmo problema pega as três: nenhuma tem âncora de tamanho.
- **Sinal acima do tick da fonte (G1, D17).** O gate reprovou 4 candidatos a
  custo zero de código. É o primeiro teste a rodar em qualquer uma das três.

## O bloqueio de terceiro CAIU — e o registro estava desatualizado

A D17e e o `Retomada_tatica.md` registram que o `etf_open_daily.parquet` está em
outra base de ajuste que o `etf_prices_daily.parquet` (TIP e TLT com +1,15% e
+0,40% fabricados por dia), e que por isso **nenhuma tática mede o retorno do
próprio dia do evento**.

**Isso não vale mais.** O `Premissa_taticas.md` foi re-gerado em **2026-08-09**
(sessão 18) e a conferência passa — mediana de `abertura/fechamento − 1` por
ticker, todos dentro de ± 0,1%:

| SPY | TIP | TLT | XLE | XLF | XLK | XLP | XLU | XLV |
|---|---|---|---|---|---|---|---|---|
| −0,059% | +0,000% | −0,023% | −0,046% | −0,038% | −0,064% | −0,042% | −0,034% | −0,027% |

Texto do próprio arquivo: o deslocamento *"não está mais no dado — os dois
arquivos vieram no mesmo ajuste"*, e *"as janelas intradiárias valem para todos
os tickers, **inclusive no dia do próprio evento**"*.

**Consequência:** não há pedido ao Paulo aqui, e as quatro táticas podem ser
medidas no dia do evento assim que a decisão 10 reabrir. O bloqueio que sobra é
todo interno: escopo, âncora de tamanho e gate G1.

---

## 1.1 — PEAD (pós-resolução)

**O que é:** age **depois** da resolução do mercado do Polymarket; gatilho =
**tamanho da surpresa**. Explora a defasagem entre o movimento do poly e a
reprecificação do mercado tradicional, no momento em que a incerteza já colapsou.

**Status:** 🟡 candidata tática — cortada na decisão 10 por escopo, **nunca
medida**. A decisão 5 (definição operacional de "surpresa") foi fechada "sem
objeto" quando a camada caiu.

**Régua:**
- Lê o poly ✅ — a surpresa é a diferença entre a resolução e a probabilidade
  precificada na véspera.
- Atua na bolsa ✅ — ETFs do universo.
- Teoria não desprovada ✅ — por vacuidade: nunca testada.

**O que falta para entrar:**
1. **Reabrir a decisão 10** — decisão do grupo.
2. **Reabrir a decisão 5**, que define o que é "surpresa" operacionalmente. Sem
   ela não há sinal para construir.
3. **Rodar o gate G1** — o sinal é maior que o tick da fonte? Uma linha em
   `gate_sleeves.py`, se houver como montar o sinal com o dado do `data/`.
4. **Âncora de tamanho** que sobreviva ao teste da 12c.
5. **Espec canônica perdida:** a descrição completa da 1.1 vivia em
   `Ideias_consolidadas.md`, que **foi deletado do repositório**. Sobra só o
   resumo de uma linha no mapa de camadas.

---

## 3.2 — Event-driven (pré-resolução)

**O que é:** age **antes** da resolução; gatilho = **salto de nível** da
probabilidade. Compra a reprecificação enquanto o mercado tradicional ainda não
absorveu o salto do poly.

**Status:** 🟡 candidata tática — cortada na decisão 10 por escopo, **nunca
medida**. Registro adjacente: eventos político-regulatórios firm-specific
pertenciam a esta camada e caíram junto quando a 2.4 fechou como view estrutural.

**Régua:**
- Lê o poly ✅ — o gatilho **é** o salto da probabilidade.
- Atua na bolsa ✅ — ETFs do universo.
- Teoria não desprovada ✅ — por vacuidade: nunca testada.

**O que falta para entrar:**
1. **Reabrir a decisão 10** — decisão do grupo.
2. **Definir o limiar de "salto"** — é threshold, e threshold sem âncora é
   exatamente o que a 12c e a D13 mataram duas vezes. Precisa vir de decisão
   registrada, não de grade.
3. **Rodar o gate G1.**
4. **Testar contra o achado transversal:** o efeito de salto do poly é justamente
   o caso em que "aterrissa no gap de abertura" é mais provável — foi assim que
   a 2.4, a C, a E e o gap de fim de semana caíram. Este teste vem antes de
   escrever módulo.
5. **Espec canônica perdida** (`Ideias_consolidadas.md` deletado).

---

## Velocidade de ajuste

**O que é:** age **durante** o movimento; gatilho = **derivada da
probabilidade**. Diferente das outras duas por não depender de um evento
datado — lê a taxa de variação do sinal, não o nível nem a resolução.

**Status:** 🟡 candidata tática — cortada na decisão 10 por escopo, **nunca
medida**. É a única das três cuja descrição **só existe no mapa de camadas** —
nunca teve arquivo próprio.

**Régua:**
- Lê o poly ✅ — a derivada é da probabilidade do poly.
- Atua na bolsa ✅ — ETFs do universo.
- Teoria não desprovada ✅ — por vacuidade: nunca testada.

**O que falta para entrar:**
1. **Reabrir a decisão 10** — decisão do grupo.
2. **Escrever a espec** — não há arquivo, só uma linha no mapa. É a única das
   três que precisa ser especificada antes de poder ser medida.
3. **Rodar o gate G1**, com uma ressalva de desenho: derivada de probabilidade é
   diferença diária de preço de mercado fino. O risco de o sinal ficar **abaixo
   do tick** é o mais alto das três — foi assim que a C1a (0,5×) e a C1b (0,2×)
   morreram, e as duas eram exatamente "revisão diária" do poly.
4. **Âncora de tamanho** (12c).

---

## 1.2 — Momentum em crenças

**O que é:** gatilho = **tendência da probabilidade** (não o salto, não a
derivada instantânea, não a resolução — a direção sustentada do sinal do poly ao
longo de vários pregões).

**Status:** 🟡 candidata tática — **nasceu como view estrutural** e foi
reclassificada para esta camada em 2026-07-10, por não ter âncora de magnitude
que o template estrutural exige (o Q não sai de β × preço observável). Caiu com a
camada na decisão 10, **sem nenhuma medição**.

**Régua:**
- Lê o poly ✅ — a tendência **é** da probabilidade do poly.
- Atua na bolsa ✅ — ETFs do universo.
- Teoria não desprovada ✅ — por vacuidade: nunca testada.

**O que falta para entrar:**
1. **Reabrir a decisão 10** — decisão do grupo.
2. **Definir a janela da tendência** — quantos pregões fazem uma "tendência".
   É parâmetro livre, da mesma família que matou a 12c e a D13; precisa vir de
   decisão registrada, não de grade.
3. **Rodar o gate G1**, com a mesma ressalva da velocidade de ajuste: tendência
   de probabilidade é agregado de diferenças diárias de um mercado fino. A C1a
   (0,5× o tick) e a C1b (0,2×) morreram medindo exatamente revisão diária do
   poly — agregar em janela ajuda, mas não é garantia.
4. **Separar da velocidade de ajuste** — as duas leem variação da probabilidade
   em horizontes diferentes (tendência × derivada). Se as duas forem medidas,
   vale o teste de ortogonalidade que salvou a 15g e matou a C2a: ângulo entre
   os sinais antes de admitir as duas.
5. **Âncora de tamanho** (12c).
6. **Espec canônica perdida:** a descrição completa da 1.2 vivia em
   `Ideias_consolidadas.md`, **deletado do repositório**.

**Nota de camada:** o motivo de ela ter saído das views estruturais (Q sem
âncora) **não é sinal fraco** — é ausência de magnitude construível. A régua do
dono perdoa |t| baixo; não perdoa Q inventado. Por isso ela volta aqui, e não no
`Candidatos.md`.

---

## Resumo

| Tática | Momento | Gatilho | 1 poly | 2 bolsa | 3 tese | 4 ortogonal | Bloqueio principal |
|---|---|---|---|---|---|---|---|
| **1.1** PEAD | depois da resolução | tamanho da surpresa | ✅ | ✅ | ✅ (vacuidade) | ⬜ | decisão 10 + decisão 5 sem objeto |
| **3.2** event-driven | antes da resolução | salto de nível | ✅ | ✅ | ✅ (vacuidade) | ⬜ | decisão 10 + limiar sem âncora |
| **velocidade** | durante o movimento | derivada da prob. | ✅ | ✅ | ✅ (vacuidade) | ⬜ | decisão 10 + espec inexistente |
| **1.2** momentum | ao longo do movimento | tendência da prob. | ✅ | ✅ | ✅ (vacuidade) | ⬜ | decisão 10 + janela sem âncora |

**Ordem de custo para descobrir se vivem:** 1.1 e 3.2 têm espec resumida e podem
ir direto ao gate G1 assim que a decisão 10 reabrir. A velocidade de ajuste e a
1.2 precisam de espec antes — e são as duas com maior risco de morrer no G1, pelo
precedente da C1a/C1b (as duas leem revisão diária do poly).

**As quatro compartilham o mesmo teto:** mesmo passando no gate, a 12c continua
de pé — a camada tática foi desligada por tamanho sem âncora, e nenhuma das
quatro resolve isso por si só.

**As quatro se dividem por horizonte do gatilho** — resolução (1.1), salto
(3.2), derivada (velocidade), tendência (1.2). São quatro leituras da mesma
série de probabilidade em janelas diferentes: se mais de uma sobreviver ao gate,
o teste de ortogonalidade entre elas vem antes de admitir as duas.

---

## Fora deste arquivo

- **1.3 prêmio de anúncios** e **drift pós-FOMC (T1+T3)** são táticas **medidas**
  e desligadas pela 12c — não são candidatas por vacuidade. Ficam na D12c e no
  `Retomada_tatica.md`. Nota registrada: o drift foi a **única tática do projeto
  que mediu positivo** (+0,08 a +0,80 pp).
