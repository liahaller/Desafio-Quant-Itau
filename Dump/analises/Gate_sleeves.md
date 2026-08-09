# Gate de sleeves — o que passa na triagem ANTES de virar código

> Gerado por `scripts/gate_sleeves.py`. **Mede; não decide.** Nenhum critério tem corte cravado — cravar um seria escolher threshold sem medição. No lugar do corte, as duas sleeves REPROVADAS da D16 entram na mesma tabela como **grupo de controle**: a linha de um candidato se lê contra o que um sinal comprovadamente morto mede.

- janela do backtest: **2025-02-10 a 2026-08-06** (374 pregões), δ e Σ os mesmos do v1 (D7/D8)
- **G1** = mediana |sinal| ÷ Δ que UM tick de 1 centavo produz no sinal (no FRED, 1 bp). Perto de 1× o sinal É o ruído de discretização
- **G2** = μ do `tatica_drift_anuncio.estimate_drift_mu` (linha de base subtraída, encolhido pela dispersão) contra o sinal DECLARADO a priori
- **G3** = correlação com o sinal que as views já leem

**G4 (P&L da sleeve sozinha) não está aqui de propósito:** exige backtest, backtest exige o módulo, e o módulo é exatamente o que este gate se recusa a escrever antes de a linha passar.

**Convenção de janela:** o sinal do dia D é o slot pré-abertura de D e o retorno medido é o do pregão SEGUINTE — mesma convenção da D16 (a sleeve abre no close de D). Medir o retorno do próprio D exigiria o preço de abertura, e os dois parquets estão em bases de ajuste diferentes (`Premissa_taticas.md`) — conserto é do módulo do Paulo.

| candidato                     |   G0 dias | G0 janela               | G1 mediana \|sinal\|   | G1 razão / tick   | G2 μ (bps/dia)              | G2 bate?   | G3 maior \|corr\|           |
|:------------------------------|----------:|:------------------------|:-----------------------|:------------------|:----------------------------|:-----------|:----------------------------|
| C1a revisão M3 (nº de cortes) |       209 | 2025-02-11 → 2025-12-10 | 0.04565 cortes         | 0.5×              | SPY -4.20 ❌ · TLT +0.03 ✅ | ❌         | -0.17 (entropia CPI (15b))  |
| C1b revisão da reunião (bps)  |       334 | 2025-02-11 → 2026-06-17 | 0.2493 bps             | 0.2×              | SPY -2.75 ❌ · TLT -3.44 ❌ | ❌         | -0.24 (divergência da 2.3)  |
| C2a cauda da PMF de CPI       |       286 | 2025-02-11 → 2026-07-29 | 0.2007 prob.           | 20.1×             | SPY -0.14 ✅ · TLT -1.56 ❌ | ❌         | -0.69 (entropia CPI (15b))  |
| C2b cauda da PMF de reunião   |       334 | 2025-02-11 → 2026-06-17 | 0.01164 prob.          | 1.2×              | SPY -2.96 ✅ · TLT -0.87 ❌ | ❌         | +0.58 (entropia FOMC (15b)) |
| controle D16 · drift FOMC 🛑  |        17 | 2024-05-01 → 2026-06-17 | 0.5242 bps             | 0.5×              | SPY +4.91 ❌ · TLT +1.37 ❌ | ❌         | +0.72 (divergência da 2.3)  |
| controle D16 · drift CPI 🛑   |        13 | 2025-03-12 → 2026-07-14 | 1 bps                  | 1.0×              | TIP +0.29 ✅ · TLT +1.91 ❌ | ❌         | +0.50 (divergência da 2.2)  |

## Correlações do G3, uma a uma

| candidato                     |   eventos no μ |   corr divergência da 2.2 |   corr divergência da 2.3 |   corr entropia CPI (15b) |   corr entropia FOMC (15b) |
|:------------------------------|---------------:|--------------------------:|--------------------------:|--------------------------:|---------------------------:|
| C1a revisão M3 (nº de cortes) |            209 |                      0.08 |                     -0.05 |                     -0.17 |                       0.11 |
| C1b revisão da reunião (bps)  |            324 |                     -0.02 |                     -0.24 |                     -0.04 |                       0.08 |
| C2a cauda da PMF de CPI       |            286 |                      0.02 |                      0.06 |                     -0.69 |                      -0.02 |
| C2b cauda da PMF de reunião   |            334 |                     -0.16 |                     -0.02 |                     -0.01 |                       0.58 |
| controle D16 · drift FOMC 🛑  |             17 |                     -0.06 |                      0.72 |                      0.44 |                       0.67 |
| controle D16 · drift CPI 🛑   |             11 |                      0.5  |                      0.14 |                     -0.1  |                      -0.48 |

## Premissa declarada ANTES de medir

Declarar por escrito antes do event-study é o que faz do G2 um teste em vez de racionalização — sem isso, "a literatura não fixa o sinal" vira licença para aceitar qualquer resultado.

- **C1a revisão M3 (nº de cortes)** — crença anda para mais afrouxamento → SPY e TLT sobem
- **C1b revisão da reunião (bps)** — idem, com o sinal invertido porque E_poly é Δtaxa (afrouxar = cair)
- **C2a cauda da PMF de CPI** — mais massa nas pontas → prêmio de risco sobe → SPY cai, TLT sobe
- **C2b cauda da PMF de reunião** — idem, na família do Fed
- **controle D16 · drift FOMC 🛑** — Bernanke-Kuttner: surpresa de ALTA → SPY e TLT caem
- **controle D16 · drift CPI 🛑** — surpresa inflacionária → o indexado (TIP) bate o nominal (TLT)

## Leitura

**O gate está calibrado — o controle reproduz a D16 número a número.** As duas sleeves reprovadas saem com `SPY +4.91 ❌ · TLT +1.37 ❌` e `TIP +0.29 ✅ · TLT +1.91 ❌`, que são os mesmos μ de `Tatica_reconstruida.md`. Se o controle não reproduzisse, o errado seria o gate, não os candidatos.

**O achado desta rodada é do G1, e mata uma FAMÍLIA inteira de uma vez: a revisão diária da crença do poly anda MENOS que um tick.** C1a revisão M3 (nº de cortes) mede 0.5× e C1b revisão da reunião (bps) mede 0.2× — abaixo de 1×, ou seja, o Δ típico de um pregão é menor que o deslocamento que UM centavo num único balde produz. É a versão forte do achado da D16: lá o poly acertava a decisão do Fed; aqui o próprio repreçamento diário dele vive abaixo da granularidade do preço. **Qualquer sleeve que leia Δ de PMF de um dia para o outro está condicionando em ruído de discretização** — e isso se descobriu com um script, não com um módulo.

**O único sinal com dispersão de verdade é a cauda do CPI (20.1×), e ela morre nos outros dois critérios.** No G2 o μ sai invertido em 1 dos 2 ativos do livro (`SPY -0.14 ✅ · TLT -1.56 ❌`, contra a premissa declarada "SPY cai, TLT sobe"), e pela D2b não se inverte. No G3 ela correlaciona -0.69 (entropia CPI (15b)) — massa de cauda e entropia são o mesmo sinal com dois nomes, então ligar esta sleeve com a view 15b seria a dupla contagem da 15a.

> ⚠️ **Ressalva no G1 da cauda, contra o próprio candidato:** a média expansiva atravessa a troca de mercado, e a grade do CPI muda de 3 a 9 baldes entre meses — parte do 20.1× é degrau de grade, não sinal. A 15b demeana POR FAMÍLIA e normaliza a entropia por log(nº de baldes) justamente por isso. Não muda o veredito: a linha já morre no G2 e no G3, que não dependem da escala do sinal.

**Nenhum candidato passa nos três critérios** (0 de 4 com G2 ✅). Pelo protocolo desta rodada, **nenhum módulo é escrito** — o gate custou um script e evitou o segundo par de sleeves natimortas.

**O que isto NÃO diz:** que a camada tática é inviável. Diz que, no dado que temos, os sinais de Polymarket que sobraram ou não têm tamanho (revisão diária, abaixo do tick) ou já pertencem a uma view (cauda ≈ entropia). A âncora de tamanho da D16 segue de pé e sem uso — o que falta é sinal, não dimensionamento.

