# Premissa do G1 — horizonte × família

> Gerado por `scripts/premissa_g1.py`. **Mede; não decide.** Nenhum corte cravado, mesma regra do `Gate_sleeves.md`.

O gate da D17 mediu o G1 num ponto só do espaço — **Δ de 1 pregão, família do Fed** — e a leitura virou regra geral: *"qualquer sleeve que leia Δ de PMF de um dia para o outro está condicionando em ruído de discretização"*. Esta tabela testa as duas premissas embutidas nessa generalização: que o resultado não depende do **horizonte** (as colunas) nem da **família de mercado** (as linhas).

- **razão** = mediana |Δ do sinal em k pregões| ÷ Δ que UM tick de 1 centavo produz no sinal. Abaixo de 1× o sinal É o ruído de discretização do preço.
- **binário**: o sinal é a própria probabilidade, então o tick é o centavo — não há grade de balde para escalar.
- séries reindexadas em dias úteis antes do `diff`, para que `k` signifique pregões e não leituras (o dado tem buracos de 24/36/48h).

⚠️ **G1 é condição NECESSÁRIA, não suficiente.** Passar do tick diz que o sinal existe acima da granularidade do preço — não que ele prevê retorno (G2) nem que sobrevive ao custo de segurar k pregões de exposição (G4).

| mercado                                 | família                |   dias | janela            | tick no sinal   | k=1   | k=2   | k=3   | k=5   | k=10   | k=20   |
|:----------------------------------------|:-----------------------|-------:|:------------------|:----------------|:------|:------|:------|:------|:-------|:-------|
| C1a M3 trajetória do Fed (nº de cortes) | Fed · controle D17     |    210 | 2025-02 → 2025-12 | 0.085 cortes    | 0.5×  | 0.9×  | 1.2×  | 1.7×  | 2.9×   | 3.7×   |
| C1b reunião do FOMC (E_poly em bps)     | Fed · controle D17     |    335 | 2025-02 → 2026-06 | 1 bps           | 0.2×  | 0.4×  | 0.5×  | 0.9×  | 1.6×   | 2.4×   |
| CPI mensal (E_poly)                     | CPI                    |    287 | 2025-02 → 2026-07 | 5e-05 frac./mês | 1.1×  | 1.8×  | 2.3×  | 3.1×  | 6.2×   | 12.1×  |
| M4 recessão EUA 2025                    | binário (nunca medido) |    255 | 2025-01 → 2025-12 | 0.01 prob.      | 0.7×  | 1.0×  | 1.0×  | 2.0×  | 2.5×   | 5.5×   |
| M5 Trump 2024                           | binário (nunca medido) |    219 | 2024-01 → 2024-11 | 0.01 prob.      | 0.5×  | 1.0×  | 1.2×  | 2.0×  | 3.0×   | 5.0×   |
| M6 tarifas China                        | binário (nunca medido) |      9 | 2025-04 → 2025-04 | 0.01 prob.      | 3.5×  | 5.0×  | 12.8× | 44.0× | —      | —      |
| M7 ação militar Irã (jun/2025)          | binário (nunca medido) |     59 | 2025-04 → 2025-06 | 0.01 prob.      | 1.2×  | 2.5×  | 3.3×  | 4.8×  | 5.5×   | 9.0×   |
| M7 ataque ao Irã (fev/2026)             | binário (nunca medido) |     29 | 2026-01 → 2026-02 | 0.01 prob.      | 4.0×  | 6.0×  | 7.7×  | 10.5× | 11.0×  | 26.0×  |
| M8 reconciliação fiscal                 | binário (nunca medido) |      3 | 2025-07 → 2025-07 | 0.01 prob.      | 33.0× | 66.0× | —     | —     | —      | —      |
| M9 Câmara                               | binário (nunca medido) |    253 | 2025-07 → 2026-07 | 0.01 prob.      | 0.0×  | 0.5×  | 1.0×  | 1.0×  | 1.0×   | 3.0×   |

## Leitura

**A premissa do horizonte NÃO se sustenta como regra geral.** C1a M3 trajetória do Fed (nº de cortes) cruza 1× em k = 3 · C1b reunião do FOMC (E_poly em bps) cruza 1× em k = 10. O tick é fixo e o sinal acumula, então o veredito do gate vale para o k que o gate mediu — não para a série. Isso separa a *velocidade de ajuste* (derivada, k = 1) da *1.2 momentum* (tendência, k grande): são leituras da mesma série em pontos diferentes desta curva, e só a primeira está medida como morta.

**A premissa da família NÃO se sustenta — mas o que a derruba não é "não-Fed", é NOTÍCIA.** Passam de 1× já em k = 1: **M6 tarifas China** 3.5× em 9 dias · **M7 ação militar Irã (jun/2025)** 1.2× em 59 dias · **M7 ataque ao Irã (fev/2026)** 4.0× em 29 dias · **M8 reconciliação fiscal** 33.0× em 3 dias. São mercados de evento discreto (geopolítica, tarifa, votação), que reprecificam quando chega notícia. Já os binários de pergunta permanente ficam junto do Fed, abaixo do tick: **M4 recessão EUA 2025** 0.7× em 255 dias · **M5 Trump 2024** 0.5× em 219 dias · **M9 Câmara** 0.0× em 253 dias. O corte não é a família do mercado, é se existe fluxo de notícia a que o preço responda. **Nenhuma sleeve do projeto jamais leu nenhum destes** — as 13 tentativas leram Fed ou CPI.

Binários que cruzam 1× em algum horizonte da grade: **M4 recessão EUA 2025** (k = 2, máximo em k = 20) · **M5 Trump 2024** (k = 2, máximo em k = 20) · **M6 tarifas China** (k = 1, máximo em k = 5) · **M7 ação militar Irã (jun/2025)** (k = 1, máximo em k = 20) · **M7 ataque ao Irã (fev/2026)** (k = 1, máximo em k = 20) · **M8 reconciliação fiscal** (k = 1, máximo em k = 2) · **M9 Câmara** (k = 3, máximo em k = 20).

### Cobertura × dispersão — as duas andam em direções opostas

Quem passa o tick em k = 1, e com quanta cobertura: **CPI mensal (E_poly)** 1.1× em 287 dias · **M6 tarifas China** 3.5× em 9 dias · **M7 ação militar Irã (jun/2025)** 1.2× em 59 dias · **M7 ataque ao Irã (fev/2026)** 4.0× em 29 dias · **M8 reconciliação fiscal** 33.0× em 3 dias. O de maior cobertura entre eles é **CPI mensal (E_poly)** (287 dias), contra 335 dias do mercado mais longo da tabela (C1b reunião do FOMC (E_poly em bps)). **Sleeve precisa das duas:** G0 sem G1 é condicionar em ruído de discretização (foi o que matou C1a e C1b), e G1 sem G0 não tem quantos dias para virar carteira — um mercado de 9 pregões não sustenta overlay, por mais que se mexa.

> ⚠️ **O E_poly do CPI já tem dono.** A divergência da view 2.2 é construída dessa mesma série (`gate_sleeves.py`, referências do G3), então a linha do CPI aqui não é candidata livre: qualquer sleeve sobre ela cai no G3 antes de chegar ao G4. Ela está na tabela como régua de escala, não como vaga aberta.

**Sem série utilizável** (entregues vazios ou sem leitura na grade): M9 Senado.

**O que isto NÃO diz:** que existe sleeve. Diz em que ponto do espaço (horizonte × família) o sinal do poly sai de dentro do tick — que é a primeira condição, e a única que custa um script. O G2 (μ contra premissa declarada) e o G3 (duplicação com as views vivas) continuam por rodar, e a âncora de tamanho da D16 continua de pé e sem uso.

