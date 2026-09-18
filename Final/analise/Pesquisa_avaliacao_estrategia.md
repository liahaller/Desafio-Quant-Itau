# Como se avalia uma estratégia quantitativa — a pesquisa e o que ela pede do Kairós

> Sessão 48 (2026-09-18), Felipe. Insumo dos slides 14 (resultados), 15 (análise crítica) e
> A9 (estatística do backtest). Os números citados saem de `scripts/analise_backtest.py` →
> `Uteis/analises/Analise_backtest.md`; nenhum foi digitado à mão aqui sem estar lá.

## 1. O que a literatura exige

| Fonte | O que pede | Onde entra no Kairós |
|---|---|---|
| Lo (2002), *The Statistics of Sharpe Ratios*, FAJ 58(4) — [CFA](https://rpc.cfainstitute.org/research/financial-analysts-journal/2002/the-statistics-of-sharpe-ratios) | O Sharpe é uma estimativa com erro-padrão √((1 + SR²/2)/T); autocorrelação muda a anualização | IC do Sharpe (iid); ACF(1) da série (−0,07: anualizar por √252 é aceitável) |
| Bailey & López de Prado (2012), *The Sharpe Ratio Efficient Frontier* — [PDF](https://www.davidhbailey.com/dhbpapers/sharpe-frontier.pdf) | **PSR**: P(SR > SR*) dado T, assimetria e curtose; **MinTRL**: track record mínimo para um nível de confiança | PSR(0) = 0,93; MinTRL(95 %) = 457 pregões > 374 |
| Bailey & López de Prado (2014), *The Deflated Sharpe Ratio*, JPM 40(5) — [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551) | **DSR**: deflacionar o Sharpe pelo Sharpe que N tentativas de ruído já produziriam (E[max SR] cresce com N e com a variância V das tentativas) | Grade N × V — N do registro do projeto (18 configurações · 31 hipóteses · +200 células da D27), V medido e V de tentativas independentes |
| Bailey, Borwein, López de Prado & Zhu (2014), *Pseudo-Mathematics and Financial Charlatanism*, AMS Notices — [PDF](https://www.ams.org/notices/201405/rnoti-p458.pdf) | MinBTL: com N configurações e backtest curto, um Sharpe in-sample alto é quase garantido mesmo sem valor OOS | Motiva reportar N; a linha "V de tentativas independentes" do DSR é esse cenário |
| Harvey & Liu (2015), *Backtesting*, JPM 42(1) — [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2345489); Harvey, Liu & Zhu (2016), *…and the Cross-Section of Expected Returns*, RFS 29(1) — [OUP](https://academic.oup.com/rfs/article/29/1/5/1843824) | Haircut do Sharpe por testes múltiplos; **t > 3** como régua para achado novo, não t > 2 | O t do alpha (0,6) é comparado à régua de 3, não à de 2 |
| Ledoit & Wolf (2008), *Robust performance hypothesis testing with the Sharpe ratio*, JEF 15 — [PDF](http://www.ledoit.net/jef_2008pdf.pdf) | Testar diferença de Sharpe por bootstrap de série temporal (Jobson–Korkie falha com caudas pesadas e dependência) | IC95 de SR_K − SR_SPY por bootstrap estacionário: [−0,42; 0,63] |
| Politis & Romano (1994), *The Stationary Bootstrap*, JASA 89 | Reamostrar blocos de comprimento geométrico preserva a dependência local | Motor de todos os IC (bloco médio 10 pregões, B = 2 000, semente fixa) |
| Grinold & Kahn (2000), *Active Portfolio Management* | IR = IC · √breadth; tracking error; o poder de um teste depende do nº de apostas independentes | IR 0,30, TE 5,1 %; breadth baixa (≈ 30 eventos macro em 18 meses) explica o IC largo |
| López de Prado (2018), *Advances in Financial Machine Learning*, cap. 14 *Backtest Statistics* — [Wiley](https://www.wiley.com/en-us/Advances+in+Financial+Machine+Learning-p-9781119482086) | Lista canônica do que reportar: hit ratio, ganho/perda médios, HHI de concentração, drawdown e **time under water**, giro, custo, PSR/DSR | Tear-sheet do apêndice A9 |
| Arnott, Harvey & Markowitz (2019), *A Backtesting Protocol in the Era of Machine Learning*, JFDS 1(1) — [PDF](https://people.duke.edu/~charvey/Research/Published_Papers/P138_A_backtesting_protocol.pdf) | Protocolo de 7 pontos (abaixo) | Esqueleto do slide 15 |
| Luo et al. (2014), Deutsche Bank, *Seven Sins of Quantitative Investing* — [PDF](https://hudsonthames.org/wp-content/uploads/2022/01/DB-201409-Seven_Sins_of_Quantitative_Investing.pdf) | Sobrevivência · look-ahead · storytelling · data-snooping · giro/custo · outliers · assimetria/short | Checklist de vieses (§3) |
| Novy-Marx & Velikov (2016), *A Taxonomy of Anomalies and Their Trading Costs*, RFS 29(1) — [OUP](https://academic.oup.com/rfs/article-abstract/29/1/104/1844518) | Estratégias de giro mensal > 50 % raramente sobrevivem ao custo real; buy/hold spread é a mitigação mais eficaz | Giro de 0,40/dia é altíssimo nessa escala; o que salva é o breakeven de 22,9 bps × 2 pagos, e a banda (D13) foi testada e não morde |
| pyfolio (Quantopian) — [tears.py](https://github.com/quantopian/pyfolio/blob/master/pyfolio/tears.py) | Prática institucional: rolling Sharpe/beta, tabela de drawdowns, retornos mensais, regimes | Gráficos do A9 (rolling IR, mensal) e a tabela dos 3 maiores drawdowns |

**Regra que sai daqui:** todo número aparece com T, intervalo de confiança e a régua contra a qual
foi julgado; a análise crítica segue um protocolo publicado, não uma lista de opinião.

## 2. Protocolo Arnott–Harvey–Markowitz × Kairós (scorecard do slide 15)

| # | Ponto do protocolo | O que o Kairós tem | Nota |
|---|---|---|---|
| 1 | **Motivação econômica** — hipótese antes do teste, mecanismo plausível | Hipótese escrita em julho (Decisões §1–4) antes de qualquer backtest; o sinal é calibrado (Brier 0,043) e o β vem de event-study, não de ajuste ao retorno | ✔ |
| 2 | **Testes múltiplos** — registrar tudo que foi tentado, corrigir | 31 hipóteses registradas, 7 entraram; grade de tetos/γ/bandas gravada; **DSR reportado em grade**. Mas as ~200 células da busca tática (D27) não têm correção | ◐ |
| 3 | **Dados e amostra** — sem sobrevivência, sem lookahead, transformações pré-fixadas | Universo fixo de 9 ETFs (sem sobrevivência), preços ajustados, "último fechamento estritamente anterior", semente da média fora da janela (206 pregões) | ✔ |
| 4 | **Validação cruzada / OOS** — o único OOS de verdade é o tempo | **Não há OOS**: uma janela, um regime (alta do S&P). MinTRL 457 > 374 | ✕ |
| 5 | **Dinâmica do modelo** — resiliência a mudança de regime, sem ajuste ad hoc | Parâmetros fixados uma vez em reunião (10a; protocolo anti-overfit §10); mas o excesso está na 1ª metade (+3,3 pp) e some na 2ª (−0,6 pp) | ◐ |
| 6 | **Complexidade** — poucos parâmetros, interpretável | 4 views, BL fechado, δ e τ medidos; Ω diagonal — não vê a correlação entre views (ρ 0,67 entre 15g e 2.2) | ◐ |
| 7 | **Cultura** — rigor acima de resultado | Critério de admissão = acertar a probabilidade, nunca render mais; LOG de 145 erros da IA; 2 views entregues com hit 49 % porque o mecanismo passou | ✔ |

## 3. Os sete pecados (Luo et al.) × Kairós

| Pecado | Status | Evidência |
|---|---|---|
| Sobrevivência | fechado | universo de 9 ETFs fixo desde julho; nenhum saiu |
| Look-ahead | fechado | toda leitura usa o slot pré-abertura e o último fechamento anterior; o lookahead de um dia no E_FF foi pego pelo controle do s4 (sessão 46) |
| Storytelling | fechado | a tese (nível do Polymarket, não Δp) foi escrita antes; o Δp foi testado e reprovado (Teste_sinal) |
| Data-snooping | **aberto** | ~200 células da D27 sem correção; DSR na linha "independentes" cai a 0,08 com N = 231 |
| Giro e custo | medido | 0,40/dia, 42 % desfeito em 1–2 pregões; breakeven 22,9 bps × 2 pagos; banda testada (D13) |
| Outliers | **aberto** | os 3 maiores dias do tilt = 3,5 dos 5,2 pp; sem eles 1,7 pp (mas sem os 3 piores, 9,7 pp — a cauda é dos dois lados) |
| Assimetria / short | parcial | as views vendem TLT/XLK via P; custo de aluguel não modelado além do declarado na D8 |

## 4. Como ler cada número (para a fala)

- **+3,0 pp, IC95 [−13; +21], P(> 0) = 64 %.** O número é positivo em todas as leituras, mas com 374 pregões o bootstrap aceita tanto −13 quanto +21. Dizer "batemos o SPY" sem o intervalo é a frase que a literatura proíbe.
- **Sharpe 1,18 [−0,2; 3,0].** Erro-padrão de 0,8 em 1,5 ano — regra de bolso de Lo: SE ≈ 1/√anos.
- **t do alpha 0,6 contra a régua de 3.** Harvey–Liu: com o data-mining acumulado da área, um achado novo precisa de t > 3. Não estamos perto — e não fingimos estar.
- **PSR 0,93 e MinTRL 457.** A probabilidade de o Sharpe verdadeiro ser positivo é 93 %; para fechar 95 % faltam ~80 pregões (4 meses). É o argumento para "o próximo semestre é o OOS pré-registrado".
- **DSR em grade.** Com a variância medida nas configurações (correlacionadas) o DSR fica em 0,84–0,88; se as tentativas fossem independentes, 0,08–0,33. A verdade está entre — e é por isso que a régua de admissão do projeto nunca foi "render mais".
- **Metades e regime.** O excesso está na 1ª metade e nos dias de queda do SPY (+6,2 bps/dia, hit 52 %); nos dias de alta a carteira perde do índice (−3,9 bps/dia). Beta 0,95 com ΣP comprado: a carteira anda com o mercado, e o tilt ganha quando o mercado cai.
- **HHI 0,01.** O resultado não é um dia só — mas os 3 maiores dias carregam 2/3 do tilt, e os 3 piores tiram 4,5 pp. Cauda dos dois lados, curtose 26.
- **Time under water 87 pregões**, igual ao SPY: o drawdown de abril/2025 é o do mercado.

## 5. O que a pesquisa pede e NÃO foi feito (fica declarado, não escondido)

- Walk-forward / OOS: impossível com o código congelado e 18 meses de Polymarket macro; o desenho honesto é **pré-registrar o próximo semestre** como OOS antes de vê-lo.
- Correção das ~200 comparações da busca tática (D27): não há Sharpe por célula gravado; entra só pelo N da grade do DSR.
- Regressão de fatores (Fama–French) para o alpha: universo de 9 ETFs e 18 meses não sustentam 3–5 fatores com poder; o alpha é contra o SPY, como a convenção do projeto.
- Custo real de execução (Novy-Marx–Velikov): 2 bps é premissa; o breakeven de 22,9 bps é a folga declarada, não uma medição de custo.
