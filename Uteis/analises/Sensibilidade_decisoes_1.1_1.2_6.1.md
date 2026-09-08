# Sensibilidade das decisões 1.1, 1.2 e 6.1

> Gerado por `scripts/sensibilidade_reuniao.py` sobre o dado cru do `origin/Paulo`. Nenhuma regra é escolhida aqui — o script varre as opções e mede quanto cada uma move o número.

**Unidade:** pontos percentuais da variação **mensal** do CPI (é o que os mercados entregues precificam; o M3 sai em nº de cortes). Como `Q = duration × (E_poly − breakeven)`, o breakeven cancela na diferença entre regras: **dispersão em Q = dispersão em pp × duration**.

**Como ler.** `Δ` é quanto a mediana de E_poly anda quando se varre aquela decisão com as outras duas fixas no cenário de referência (ponta = ponto médio, faixa faltante = renormalizar, sem correção FL). `σ` é o desvio-padrão do próprio E_poly **ao longo do tempo** — é o tamanho do sinal que a view lê. A coluna que decide é a última: **Δ/σ**. Perto de zero, a regra é irrelevante e a reunião fecha em dois minutos; perto de 1, a escolha da regra vale tanto quanto a informação do mercado.

## CPI — mercados mensais

| Mercado | buckets | slots | E_poly ref | σ(E_poly) | Δ balde aberto | Δ faixa faltante | Δ FL | maior Δ/σ |
|---|---|---|---|---|---|---|---|---|
| CPI_april-inflation-us-monthly | 9 | 63 | 0.5797 | 0.1258 | 0.0006 | 0.0132 | 0.0079 | 0.10 |
| CPI_august-inflation-monthly | 5 | 60 | 0.3366 | 0.0149 | 0.0343 | 0.0000 | 0.0069 | 2.30 |
| CPI_december-inflation-monthly | 3 | 4 | 0.3816 | 0.0151 | 0.0123 | 0.0000 | 0.0013 | 0.81 |
| CPI_december-inflation-us-monthly | 5 | 78 | 0.2714 | 0.0256 | 0.0035 | 0.0000 | 0.0030 | 0.14 |
| CPI_february-inflation-monthly | 5 | 66 | 0.3241 | 0.0219 | 0.0053 | 0.0000 | 0.0004 | 0.24 |
| CPI_january-inflation-monthly | 4 | 56 | 0.2949 | 0.0213 | 0.0179 | 0.0000 | 0.0016 | 0.84 |
| CPI_july-inflation-monthly | 6 | 56 | 0.2529 | 0.0148 | 0.0001 | 0.0000 | 0.0016 | 0.11 |
| CPI_july-inflation-us-monthly-20260714151042 | 9 | 29 | 0.0666 | 0.0865 | 0.0589 | 0.0016 | 0.0234 | 0.68 |
| CPI_june-inflation-monthly | 5 | 68 | 0.2418 | 0.0124 | 0.0102 | 0.0000 | 0.0005 | 0.82 |
| CPI_june-inflation-us-monthly-20260610151033 | 9 | 68 | 0.0761 | 0.0826 | 0.0927 | 0.0000 | 0.0176 | 1.12 |
| CPI_march-inflation-monthly | 5 | 58 | 0.1169 | 0.0329 | 0.0655 | 0.0000 | 0.0196 | 1.99 |
| CPI_march-inflation-us-monthly | 6 | 60 | 0.6960 | 0.1160 | 0.0378 | 0.1264 | 0.0149 | 1.09 |
| CPI_may-inflation-monthly | 5 | 58 | 0.1890 | 0.0194 | 0.0008 | 0.0000 | 0.0025 | 0.13 |
| CPI_may-inflation-us-monthly | 9 | 57 | 0.5114 | 0.0274 | 0.0007 | 0.0000 | 0.0017 | 0.06 |
| CPI_november-inflation-monthly | 5 | 122 | 0.3000 | 0.0085 | 0.0001 | 0.0000 | 0.0000 | 0.02 |
| CPI_october-inflation-monthly | 5 | 45 | 0.2498 | 0.0267 | 0.0079 | 0.0000 | 0.0028 | 0.30 |
| CPI_september-inflation-monthly | 5 | 86 | 0.3891 | 0.0157 | 0.0168 | 0.0000 | 0.0032 | 1.07 |
| M1_cpi_monthly | 6 | 56 | 0.2529 | 0.0148 | 0.0001 | 0.0000 | 0.0016 | 0.11 |
| M3_fed_trajectory | 9 | 691 | 2.6444 | 0.4921 | 0.0484 | 0.1837 | 0.1424 | 0.37 |

## Qual decisão move mais o número

| Decisão | Δ mediano | Δ máximo | Δ/σ no pior caso | mercado do pior caso |
|---|---|---|---|---|
| 1.2 balde aberto | 0.0102 | 0.0927 | 1.12 | CPI_june-inflation-us-monthly-20260610151033433 |
| 6.1 faixa faltante | 0.0000 | 0.1837 | 0.37 | M3_fed_trajectory |
| 1.1 favorite-longshot | 0.0028 | 0.1424 | 0.29 | M3_fed_trajectory |

## Binário em p baixa (view 3.1) — onde o FL morde mais

| gamma | p mediana | p no 1º decil | p máxima |
|---|---|---|---|
| 1.0 | 0.2050 | 0.0297 | 0.6550 |
| 1.1 | 0.1838 | 0.0211 | 0.6693 |
| 1.25 | 0.1552 | 0.0126 | 0.6903 |

## Leitura (fatos, não recomendação)

1. **A decisão 1.2 (balde aberto) é a que move o número na PMF**, não a 1.1. Em 4 dos 19 mercados a escolha da ponta desloca E_poly MAIS do que o próprio E_poly varia no tempo (Δ/σ > 1). Nos meses de grade nova de 2026 (9 buckets), Δ chega a 0.093 pp contra σ de ~0,08 pp — a regra vale tanto quanto a informação do mercado.
2. **A 1.1 (favorite-longshot) quase não mexe na PMF de CPI** (Δ/σ ≤ 0,3 em todos os mercados de CPI, dentro da faixa de γ testada) — mas é decisiva no BINÁRIO em p baixa, que é onde a view 3.1 vive: a mediana do mercado de recessão cai de 0,205 para 0,155 e o 1º decil cai de 0,030 para 0,013, mais da metade. Ou seja: 1.1 e 1.2 travam views DIFERENTES, e podem ser decididas separadamente.
3. **A 6.1 (faixa faltante) é irrelevante em 2025 e material em 2026:** Δ = 0 em todos os meses de grade estável e 0,126 pp em mar/2026 (só 24 dos 60 slots têm todos os buckets) e 0,184 corte no M3. A decisão só precisa cobrir os meses de grade nova — e precisa incluir o caso 'faixa some e volta', que a redação atual da 6.1 não cobre.

> **Ressalva de método.** A curva de FL é uma família de UM parâmetro (`p^γ` normalizado, γ ∈ {1,0; 1,1; 1,25}) escolhida só para dar escala ao efeito; não é a correção da decisão 1.1 nem uma calibração. Se a reunião escolher uma curva com forma diferente, os Δ da coluna FL mudam — os das outras duas colunas, não.

> **Achado de unidade, para a pauta.** A espec da 2.2 foi escrita supondo CPI **anual** (buckets 3,7% / 3,8% / ≤3,6%), mas o Paulo mediu (Nota A) que os mercados entregues são de variação **mensal** do CPI-U (0,0% a 0,5%). Do jeito que a fórmula está, `E_poly − breakeven_10a` compara uma variação mensal (~0,3%) com um breakeven anual (~2,3%) e produz divergência negativa permanente de ~2 pp. **Não é bug do código — é premissa da view a reconciliar** (anualizar o E_poly, comparar com breakeven mensalizado, ou achar mercado de CPI anual).
