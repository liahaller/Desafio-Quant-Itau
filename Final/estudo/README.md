# Como o estudo do Polymarket foi feito — documentação para quem for refazer ou mudar

> Escrito para outra sessão do Claude Code (ou outro membro) conseguir entender,
> reproduzir e alterar o estudo sem ler o histórico inteiro. Leia junto com o
> `CLAUDE.md` (regras do repo), a **D32** do `Decisoes_pendentes.md` (escopo
> fechado pelo dono) e a entrada da **sessão 46** do `LOG.md`.

## 1. O que é, em três linhas

Estudo estatístico do Polymarket como fonte de sinal, para o slide 16 da final.
Três perguntas: **Q1** o preço é uma probabilidade calibrada e como a acurácia
evolui até a resolução; **Q2** ele acrescenta informação ao mercado tradicional
(FOMC × proxy do futuro de fed funds); **Q3** é aplicável à carteira (event-study
do dia do anúncio, negativos já medidos, martingale do preço). **Mede; não
decide** — nada em `src/`, no backtest ou em parâmetro da estratégia muda.

## 2. Mapa de arquivos

| papel | arquivo | observação |
|---|---|---|
| **o script** (tudo sai dele) | `scripts/estudo_polymarket.py` | `python scripts/estudo_polymarket.py` mede e grava tudo (~1–2 min, bootstrap); `--demo` = 12 asserts sintéticos; `--tema claro` inverte a paleta das figuras do paper |
| tabelas | `Uteis/dados/estudo/*.csv` (16) | uma por métrica; `observacoes.csv` é a amostra longa (mercado × h) |
| tabelas em markdown | `Uteis/analises/Metricas_estudo.md` | fonte dos números do paper e do guia |
| figuras do paper | `Uteis/graficos/estudo_1..6.{png,svg}` | paleta do relatório (`graficos_p4.PALETAS`) |
| figuras do slide 16 | `Uteis/graficos/estudo_s0_calibracao`, `estudo_s2_mae` | paleta viva do deck, fonte maior, sem barras de erro |
| paper curto | `Final/estudo/Estudo_polymarket.md` | resumo · literatura · dados · método · resultados · limitações · referências |
| guia de fala | `Final/estudo/Guia_slide16.md` | gráfico a gráfico, sem jargão; perguntas da banca |
| slides | `scripts/slides_final_pptx.py` (`dados_estudo`, `s16_estudo`, `sA1_horizonte`, `sA2_poly_vs_ff`, `sA3_aplicabilidade`) → `Final/Slides_novos.pptx` (slides 18–21 do arquivo) | os números do slide são lidos dos CSV, nunca digitados |
| plano aprovado | `~/.claude/plans/para-final-uma-ideia-witty-snowflake.md` (fora do repo) | as escolhas pré-registradas estão copiadas na D32 |

Ordem de regeneração: `estudo_polymarket.py` → `slides_final_pptx.py` (o deck
lê os CSV e os PNG; se o pptx estiver aberto no PowerPoint, o `save` falha com
`PermissionError` — fechar antes).

## 3. Dados de entrada (tudo em `data/`, congelado, pipeline do Paulo)

| família | arquivo | como vira amostra |
|---|---|---|
| FOMC | `data/polymarket_fed_reunioes.parquet` | `poly_loader.load_fomc_pmf` → uma PMF (slots × faixas) por reunião; faixas ordenadas por Δtaxa; pontas abertas marcadas |
| CPI | `data/raw/clob_exploracao/CPI_<slug>_*.json` | `premio_condicional.prefixos_cpi` casa release → prefixo de arquivo (slug vem da coluna `fonte` do `cpi_release_dates.csv`); `poly_loader.load_pmf` monta a PMF; `bucket_value` lê o valor da faixa do slug |
| Payrolls | `data/raw/clob_exploracao/G9_payrolls_*.json` | `pmfs_payrolls` usa `PAYROLL_FAMILIAS` (só EUA: NFP e desemprego). **Sem rótulo de faixa e sem `PAYEMS`/`UNRATE` no repo → sem resolução (y)** |
| resolução FOMC | `data/raw/fred_DFF.csv` + `fomc_dates.csv` | `backtest_v1.decisoes_realizadas_fomc` (média de 5 leituras depois − 3 antes, em bps), arredondado a 25 |
| resolução CPI | `data/raw/fred_CPIAUCSL.csv` + `cpi_release_dates.csv` | `gate_pead.mom_realizado` (MoM em p.p., arredondado a 1 casa como o BLS publica); `load_cpi_releases` corrige os erros de calendário do shutdown |
| benchmark FOMC | `fred_DTB3.csv`, `fred_DFF.csv` | `E_FF = (DTB3 − DFF) × 100` bps — o proxy da estratégia (D12) |
| ETFs | `data/etf_prices_daily.parquet` | `market_loader.load_etf_prices` + `taticas_common.close_to_close_returns` |
| volume | coluna `volume` do parquet (lifetime, por mercado) | só FOMC tem |

### Três achados de dado que definem o desenho (não são escolhas)

1. **A série de todo mercado termina no slot das 12:00 UTC do dia do anúncio**
   — antes das 14:00 ET do FOMC e das 08:30 ET (12:30 UTC) do CPI. O último
   preço ainda é expectativa. **Nunca use o preço terminal como resolução**; a
   resolução vem do FRED.
2. **Payrolls não resolve** com o que está no repo (ver tabela). Entra só em
   Σp (overround) e martingale. Se alguém trouxer `PAYEMS`/`UNRATE` e o slug
   das faixas, a família entra na Q1 pelo mesmo caminho do CPI (`amostra_cpi`
   é o molde).
3. **A reunião de 29/10/2025 não tem o slot da véspera** (12:00 UTC) no
   parquet — fica fora de h = 0 pela regra, e o parquet segue até 31/10 com
   zeros. Por isso a data do evento vem do calendário oficial (`fomc_dates.csv`,
   última data ≤ fim da série), nunca do fim da série.

## 4. Como a amostra é montada (`amostra_fomc`, `amostra_cpi`, `_linhas`)

- **Unidade:** (contrato, h). Para cada evento e cada h em `HORIZONTES`
  (0, 1, 2, 3, 5, 10, 15, 20, 30, 45, 60 dias corridos), o preço é a linha da
  PMF no slot pré-abertura (`daily_preopen`, 12:00 UTC) do dia `evento − h`,
  depois de `carry_missing` (faixa sem leitura herda a última — D4/6.1).
- **Linha inválida** (`leitura`): sem slot, alguma faixa NaN, ou Σp < `SOMA_MINIMA`
  (0,5 — linha em que os buckets já morreram; medido no CPI de mar/2026). A
  falta é contada em `cobertura_h.csv` com o motivo (`sem slot` / `degenerada`).
- **y** (`vencedor`): faixa cujo valor nominal bate o realizado; ponta aberta
  vence se o realizado passa dela (FOMC: `abertos` vem do título "50+"; CPI:
  as duas pontas são abertas pelas regras do mercado). Exatamente uma faixa
  vence, senão levanta erro.
- **`valor`** (para E_poly e RPS): valores com ponta aberta resolvida a meia
  largura para fora (`bucket_values_with_open`, D1.2). O acerto **modal**
  compara pelo vetor `y`, não pelo valor (a ponta −50+ resolve com −50, não com
  o −62,5 da D1.2 — foi um bug pego na verificação).
- **Dependência:** faixas da mesma PMF somam ~1 → **cluster = evento** em todo
  IC (`bootstrap_por_cluster`, B = 2.000, semente fixa) e em todo EP
  (`ols_cluster`).
- Saída: `observacoes.csv` (familia, evento, mercado, bucket, K, h, p, y, valor,
  volume) + `diarias` (dict evento → (PMF diária, valores, realizado[, y])),
  que a Q2/Q3 reusam.

## 5. O que cada bloco calcula

**Funções puras (seção 2 do script)** — todas em numpy/scipy (statsmodels não
está instalado): `brier`, `logloss`, `brier_uniforme` (1/K por faixa =
baseline do BSS), `murphy` (confiabilidade − resolução + incerteza; a
identidade fecha contra o Brier do previsor *binado*), `curva`,
`bootstrap_por_cluster`, `ols_cluster` (Liang–Zeger), `regressao_calibracao`
(y = a + b·p, Wald de (0,1)), `gamma_otimo` (γ que minimiza o Brier com a
`favorite_longshot` binária), `rps` (normalizado por K−1), `newey_west`
(Bartlett), `diebold_mariano` (sobre |erro|, correção HLN, p da t(n−1)),
`acf_pooled`, `variance_ratio` (Lo–MacKinlay, janelas sobrepostas).

**Q1 (`q1`)** → `brier_horizonte` (por família/h e pooled, com IC), `murphy`
(pooled 10 bins; h=0, h=20, FOMC, CPI com 5 bins; inclui a regressão e o γ),
`calibracao_bins` (curva com IC por bin), `extremos` (p < 0,10 e p > 0,90),
`rps` (por evento/h vs uniforme e persistência = faixa do evento anterior),
`overround` (Σp por família/h), `volume` (tercis, FOMC).

**Q2 (`q2`, só FOMC)** → `fomc_previsoes` (por reunião/h: E_poly = `pmf_mean`,
modal, E_FF, E_FF corrigido) e `fomc_vs_ff` (MAE/RMSE/viés/acerto modal/DM por
h, cru e corrigido), `encompassing` (h = 0 e 20, EP HC1), `leadlag_ccf`
(corr(Δpoly_t, Δff_{t+k}), k = −3…3, pooled nos 60 dias úteis antes de cada
reunião), `leadlag_granger` (dois sentidos, NW).
- **E_FF é lido estritamente antes da data da leitura** (`ultimo_antes`): o
  H.15 sai depois do fechamento; às 08:00 ET só se conhece o DTB3 da véspera.
  Mesma regra do backtest. (A primeira versão lia o do próprio dia — lookahead
  de um fechamento, pego pelo controle do item 8.)
- **E_FF corrigido** = E_FF + média expansiva dos erros das reuniões
  *anteriores* no mesmo h (D12a) — sem lookahead; a primeira reunião fica NaN.
- **Lead-lag:** Δpoly_t cobre [08:00 ET t−1, 08:00 ET t]; Δff_t cobre
  [16:00 ET t−1, 16:00 ET t]. Só k ∈ {−1, 0} se sobrepõem; k = +1 e k = −2 são
  o teste limpo. Na regressão (B) o regressor `d_ff_l0` é contemporâneo e
  posterior à leitura — é controle, não evidência.

**Q3 (`q3`)** → `event_study` (R², β, t por ETF; FOMC com surpresa poly / FF
cru / FF corrigido / Kuttner = ΔDTB3 do dia; CPI com poly / naive = mês
anterior; **unidades**: CPI em p.p. dos dois lados — os valores de faixa aqui
NÃO são divididos por 100 como no `pmf_diaria` do backtest) e `martingale`
(ACF(1), ACF(2), VR(2), VR(5) pooled por família, IC por evento com B = 500;
coluna `interior` = só preços em (0,02; 0,98)). O negativo de pré-anúncio **não
é re-rodado**: é transcrito de `Uteis/analises/Teste_sinal.md`.

**Síntese (`sintese`)** monta as seis células do placar a partir das tabelas;
`fig_sintese` desenha. Os slides recomputam as mesmas células em
`slides_final_pptx.dados_estudo` lendo os CSV.

## 6. Escolhas pré-registradas (D32) — o que NÃO mudar sem registrar

Grade `HORIZONTES`; `HORIZONTES_HEROI = (0, 20)`; bins 10 pooled / 5 por
recorte; baseline do BSS = uniforme sobre faixas vivas; γ só medido (a D9 fixa
1,0); `VR_Q = (2, 5)`; `NW_LAGS = 5`; `DIAS_LEADLAG = 60`; `B_BOOT = 2000`,
`SEMENTE = 20260917`; filtros de dado `SOMA_MINIMA = 0.5` e `INTERIOR = (0.02, 0.98)`;
`REFERENCIAS` (Kalshi 0,087 / 0,045; Dune 0,058) são números publicados, não
medidos aqui. Mudar qualquer um é decisão de categoria 2 no mínimo (regra 1 do
`CLAUDE.md`): apresentar ao dono e registrar.

## 7. Verificação — o que tem de passar antes de gravar

1. `python scripts/estudo_polymarket.py --demo` — 12 asserts sintéticos
   (calibrado → confiabilidade ≈ 0 e slope ≈ 1; constante 0,5 → Brier 0,25;
   RPS 0/1; γ ótimo = 1 em dado calibrado; VR ≈ 1 e ACF ≈ 0 em ruído; DM com
   sinal e p certos; NW recupera β; `vencedor` com ponta aberta; bootstrap
   contém a estimativa).
2. **Controle real** contra `Uteis/dados/s4_comparacao.csv` (artefato do slide
   4, gerado pelo backtest): na véspera de 17/09/2025 (h = 1 do evento
   2025-09-17) `fomc_previsoes.csv` tem de dar **E_poly −26,90 e E_FF −42**;
   em h = 2, −27,38 e −39. Se o E_poly bater e o E_FF não, é o `ultimo_antes`.
3. `python scripts/slides_final_pptx.py --demo` — confere que os indicadores
   saem do CSV com a forma esperada e que o placar é ✔✔✔ ✕✕✕.
4. Sanidade (não assert): Brier FOMC h = 0 ≈ 0,007, pooled ≈ 0,043; Σp FOMC
   ≈ 1,00; `cobertura_h.csv` com FOMC 17 em h = 0 (a reunião de 29/10/2025) e
   CPI 0 além de h = 30.
5. Render dos slides pelo PowerPoint (COM): `--render <pasta>`; olhar os PNG.

## 8. Receitas de mudança

- **Trocar horizontes / bins / B:** só as constantes do topo; tudo se
  propaga. Registrar (item 6).
- **Adicionar uma família com resolução** (ex.: payrolls com `UNRATE`): copiar
  `amostra_cpi` — carregar a PMF, obter `valores` (precisa de rótulo de faixa
  no nome do arquivo ou de um mapa), calcular `y` com `vencedor`, chamar
  `_linhas`. Adicionar no `medir` (`pd.concat`) e na `cobertura`. As figuras
  usam `cores[familia]` — incluir a cor nova em `fig_brier`.
- **Trocar o benchmark do FOMC** (ex.: contrato ZQ de verdade): em `q2`, a
  série `e_ff` é a única entrada; manter a leitura estritamente anterior e a
  correção expansiva (ou justificar tirar).
- **Adicionar benchmark para o CPI** (ex.: Cleveland Fed nowcast): hoje só há
  `naive_mes_anterior` no event-study; um "Q2 do CPI" seria um clone de `q2`
  com `diarias_cpi` e a série do nowcast — dado novo é pipeline do Paulo.
- **Mudar o slide 16:** `s16_estudo` em `slides_final_pptx.py`; as duas
  figuras são `fig_slide_calibracao` e `fig_slide_mae` (paleta `SLIDE`). Os
  números vêm de `dados_estudo`. Layout em polegadas; margens `L = 0.80`,
  `R = 12.53`; rodapé em `PE = 7.167`.
- **Mudar figuras do paper:** `fig_*` na seção 6; `salvar` grava PNG 300 dpi +
  SVG com fundo transparente (o slide é que pinta).
- **Tema claro** (relatório em fundo branco): `--tema claro` — só afeta as
  figuras do paper, não as do slide.

## 9. Armadilhas que já morderam (não repetir)

- `carry_missing` mora em `poly_preprocessing`, não em `poly_loader`.
- A identidade de Murphy só fecha contra o Brier do previsor binado.
- Acerto modal compara `y[argmax p]`, não `valor[argmax p] == realizado`.
- CPI: `valor` está em p.p.; não multiplicar por 100 no event-study.
- E_FF: `ultimo_antes(serie, data)` é **estritamente** anterior.
- Bins vazios no bootstrap da curva geram `All-NaN slice` — suprimido dentro
  de `bootstrap_por_cluster`, é esperado.
- Heredoc do bash quebra com `'''` dentro; patches grandes vão por arquivo.
- `Final/Slides_novos.pptx` aberto no PowerPoint bloqueia o `save`.
- A afirmação "o mercado de juros errou set/2024" é falsa (o proxy também
  apontava −50 na véspera); o certo é "52 % × 47 %, e a moda acertou".

## 10. O que ficou fora (e por quê)

- Pull amplo de todas as categorias do Polymarket (estilo Kalshi 2 M): é dado
  novo → pipeline do Paulo; o dono optou por profundidade macro (D32).
- Benchmarks externos (Cleveland Fed nowcast, ZQ, PAYEMS/UNRATE): não estão
  no repo; o dono pediu zero pedidos de dado nesta rodada.
- Lead-lag intradiário: a grade é de 12 h; não dá para ver quem se move
  primeiro dentro do pregão.

## 11. Resultado, para conferir depois de qualquer mudança

Brier pooled h = 0 **0,043** [0,022; 0,067], BSS 0,73; calibração h = 0
b = 1,04 (p = 0,15), pooled b = 1,08 (p < 0,001); p < 0,10 → 0,0 % em 908 obs;
γ ótimo 1,20 pooled; FOMC h = 0: MAE 0,9 × 8,9 (cru) × 4,8 (corrigido) bps,
DM p < 0,001 / 0,002, modal 17/17; encompassing h = 0: 1,14 (t 19,0) e −0,06
(t −1,05); CCF k = +1 0,02, k = −2 −0,03; event-study FOMC R² médio poly 0,08,
FF corr. 0,19, Kuttner 0,06; VR(5) FOMC 0,78 [0,71; 0,86], CPI 0,72, payrolls
0,43. Se algo mudar sem mudança de dado ou de escolha, algo quebrou.
