# leaveoff — as três candidatas foram medidas; a próxima sessão discute o CRITÉRIO

**Escrito em:** 2026-08-09 (sessão 18, Felipe) · **Para:** a sessão que vier depois.
**Substitui** o handoff da sessão 17, cujas três candidatas já foram montadas e
medidas nesta sessão. O registro formal está na **D19** do `Decisoes_pendentes.md`;
o que aconteceu está no `LOG.md` (sessão 18).

⚠️ **Nada aqui está decidido.** As três candidatas seguem **sem destino**, por
instrução explícita do dono. O que segue é medição e recomendação.

---

## Direção dada pelo dono para a próxima sessão

> "Na próxima sessão teremos uma discussão mais ampla sobre **como decidir quais
> views entram ou não**."

Ou seja: a próxima sessão **não é para montar mais uma view**. É para fechar o
critério de admissão — hoje ele existe espalhado em precedentes (D2b, o teste de
sinal da 15f, a régua do poly da 18a) e nunca foi escrito como regra única. Os
insumos para essa conversa estão no fim deste arquivo.

---

## O que aconteceu com cada candidata — versão leiga

**Candidata 1 — petróleo e crise no Irã.**
A ideia: quando o Polymarket aumenta a chance de ataque ao Irã, comprar energia
(XLE). Testei numa **segunda crise** (jun/2025) que estava parada no disco e
nunca tinha sido medida. O mercado de apostas **de fato mexe o XLE, com a mesma
força nas duas crises** — isso é verdade e é bom.
**Motivo principal de ficar fora: com 55 dias de teste, o efeito não é
distinguível de sorte.** Descobrimos que o motivo antigo do corte estava errado,
mas não achamos motivo novo para ligar.

**Candidata 2 — inflação na seção cruzada.**
A ideia: o Polymarket discorda do mercado sobre inflação → comprar quem ganha com
inflação, vender quem perde. A view estava escolhendo os ativos errados (comprava
petróleo e bancos em vez de títulos indexados). Consertei isso — e o conserto
**funcionou**: ela passou a comprar TIP, como deveria.
**Motivo principal de ficar fora: o problema nunca foi a escolha dos ativos, era
o sinal.** Saber quem reage à inflação *hoje* não diz quem vai subir *amanhã*.
Consertamos a peça errada — e depois do conserto ela ficou **pior**, não melhor.

**Candidata 3 — recessão.**
A ideia: Polymarket vê mais risco de recessão que a curva de juros → apostar na
direção do mercado inteiro. Construí e medi; o efeito existe no papel.
**Motivo principal de ficar fora: o sinal se inverte no meio da própria
amostra.** Na primeira metade de 2025 o mercado **subia** quando o medo
aumentava; na segunda metade **caía** — as duas metades com significância
estatística. É moeda jogada duas vezes, não estratégia. E só existe um mercado de
recessão, então não há como desempatar.

**Em uma frase:** nenhuma das três ficou fora por ser mal desenhada — as três
ficaram fora porque **o sinal não existe de forma estável**: a 1 é fraca demais,
a 2 não se transporta para o futuro, a 3 troca de lado no meio do caminho.

---

## Os números, para quem for conferir

### Candidata 1 — view C, 2º episódio (`Dump/analises/Janela_negociavel.md`)

| episódio | obs | gap (não negociável) | janela negociável | razão oc/cc |
|---|---|---|---|---|
| Irã 2026 (o que decidiu o corte) | 27 | **+0,0606 · t +3,18** | −0,0183 · t −0,67 | **−44%** |
| Irã jun/2025 (fora da amostra) | 55 | +0,0578 · t +1,39 | +0,0478 · t +0,82 | **+46%** |

A sensibilidade replica (+0,0606 × +0,0578, duas crises independentes); o veredito
não. **Consequência que passa do escopo da candidata:** o relatório não pode mais
citar "a informação do poly morre no gap de abertura" como achado transversal sem
ressalva — no segundo episódio 46% do efeito sobrevive na janela negociável.

### Candidata 2 — transversal ortogonalizada (`Dump/analises/Teste_sinal.md`)

| variante | TIP | TLT | XLE | transporte (corr) | t (h = 5) |
|---|---|---|---|---|---|
| β cru | **−0,29** | −0,70 | +0,31 | −0,48 | −0,86 |
| β ⊥ risk-on | **+0,67** | −0,02 | +0,84 | **−0,84** | **−2,36** |

O módulo `src/view_cpi_transversal.py` **não foi tocado** — o teste rodou antes,
como a D17 mandou, e custou zero linha.

### Candidata 3 — 3.1 direcional (`Dump/analises/Recessao_direcional.md`)

SPY em h = 10, discordância padronizada de forma expansiva:

| recorte | pregões | período | coef SPY | t |
|---|---|---|---|---|
| amostra inteira | 186 | 04/25 a 12/25 | **+0,40%** | +3,22 |
| 1ª metade | 93 | 04/25 a 08/25 | **+0,97%** | +6,52 |
| 2ª metade | 93 | 08/25 a 12/25 | **−0,35%** | −2,27 |

**Isto antecede a pergunta da D18d.** A decisão pendente era "o grupo re-declara
a tese como *prêmio de medo pago*?". Medido, a pergunta fica **sem base empírica
em nenhuma das duas direções** — e responder assim evita o vício que a D2b existe
para barrar (re-declarar tese depois de ver o sinal).

---

## O que ficou no repositório

| | |
|---|---|
| `scripts/teste_sinal.py` (+ 5 testes) | paga a pendência de reprodutibilidade da 15g; 2.2 e 2.3 como **controle embutido**, e o controle reproduz |
| `scripts/view_3_1_direcional.py` | medição da candidata 3, com a tabela de estabilidade |
| `view_3_1_recessao.build_view_direcional` (+ 3 testes) | construída para MEDIR; **não ligada** |
| uma linha em `scripts/janela_negociavel.py` | o mercado do Irã jun/2025 no dicionário |
| Artefatos | `Teste_sinal.md`, `Recessao_direcional.md`, `Janela_negociavel.md` re-gerado |

**Entrega intocada:** `Backtest_v1.md` byte a byte idêntico (**+4,07 pp**), 240
testes passando, `views_novas=()` e `tatica=()` seguem o default.

---

## Insumos para a discussão de critério da próxima sessão

O critério de admissão hoje **não existe escrito** — existem quatro precedentes
soltos, e a conversa é sobre transformá-los (ou não) em regra:

1. **D2b — não se inverte.** Sinal contrário à tese não vira view invertida.
   Aplicado 4 vezes; é o precedente mais firme que temos.
2. **Régua do poly (D18a, 🟡 pendente de ratificação).** "View que não lê o
   Polymarket não entra." Barrou 4 propostas boas, inclusive a **única tática que
   mediu positivo** (drift pós-FOMC via ΔDTB3, inventariada na D18b).
3. **Teste de sinal — é VETO, não certificado (15f).** Nenhuma view do v1 passa:
   a 2.3, que carrega o backtest, dá t +0,26. Ele pega sinal **invertido**, não
   mede utilidade. Usá-lo como nota de corte reprovaria a entrega.
4. **Atribuição obrigatória (15h).** "Sem os 3 maiores" e acerto de sinal, sempre
   — foi assim que uma view "de +3,89 pp" virou **um pregão**.

**As perguntas que a sessão precisa responder, e nenhuma é minha:**

- O critério é **estabilidade** (o sinal se repete em subamostras / segundo
  episódio) ou **significância** (|t| na amostra inteira)? As três candidatas
  desta sessão passariam ou reprovariam em ordens diferentes conforme a escolha.
- A régua do poly (18a) é ratificada? Se cair, o drift pós-FOMC volta na frente
  de tudo — e custa **uma linha** no `gate_sleeves.py` para saber se vive.
- "Fazer sentido vale mais que medir positivo" (14a) continua valendo? Se sim, a
  candidata 1 é o caso-teste: mecanismo replicado em duas crises, sem
  significância em nenhuma.

**O que NÃO reabrir** (medido e morto, inventário completo em
`Dump/analises/Retomada_tatica.md`): 2.4 eleitoral · E tarifas e G fiscal
(amostra pura) · 15b incerteza (o ganho é um pregão) · 15g B com β próprio ·
sleeves de revisão do poly (abaixo de um tick) · C2a cauda do CPI (dupla contagem
com a 15b) · gap de fim de semana · **e agora as três desta sessão**, salvo se o
critério novo mudar a régua.
