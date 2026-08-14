# Relatório final — KAIRÓS

`KAIROS.pdf` é o entregável: 5 páginas, 16:9 (960 × 540 pt), anônimo.
Renome-ar para `[chave de envio].pdf` na hora de enviar.

## Como regerar

```
cd fonte
python montar.py       # injeta imagem e SVGs no template, gera o PDF e valida
```

O `montar.py` valida sozinho contra o edital: número de páginas (≤ 5), proporção
16:9 exata, contagem de palavras e ausência de qualquer identificador de autor,
equipe ou instituição.

## O que gera o quê

| Arquivo | Papel |
|---|---|
| `template.html` | as 5 páginas, com `{{PLACEHOLDERS}}` para imagem e gráficos |
| `montar.py` | injeta, chama o Chrome headless (`--print-to-pdf`) e valida |
| `pipeline.svg` | diagrama da página 2, desenhado à mão |
| `svg/*.svg` | os três gráficos, gerados por `graficos.py` |
| `dados/curva_diaria.csv` | série diária da carteira de entrega |
| `kairos_datauri.txt` | a arte do robô já em base64 |

## Dependência externa dos gráficos

`extrair_serie.py` **não roda direto neste branch**: ele reexecuta o backtest de
entrega importando `src/` e `scripts/backtest_v1.py` do branch `Felipe` com o
`data/` do branch `Paulo`, ambos extraídos para um diretório de trabalho fora do
repositório. A série resultante já está versionada em `dados/curva_diaria.csv`,
então `graficos.py` e `montar.py` rodam sem essa etapa.

A rodada de 12/08/2026 reproduziu os números do `Dump/analises/Backtest_v1.md`
dígito a dígito (Sharpe 1,2136 · breakeven 28,4727 · excesso +4,08 pp).

## Configuração retratada

Teto de risco **1 no tilt** (D10a), camada tática **ligada** (D28.13), quatro
views, γ = 1, e a régua do Ω **acoplada no nível 1** (decisão 6q, 13/08/2026).

⚠️ **O `scripts/backtest_v1.py` do branch `Felipe` ainda não passa `regua=`** — é
módulo dele e não foi tocado. Os números deste relatório vêm de
`fonte/extrair_serie_regua.py`, que chama o mesmo `run_backtest` passando a régua
pelo parâmetro que ele já expõe. Enquanto a entrega oficial não acoplar a régua,
os dois números divergem:

| | sem régua | com régua (nível 1) |
|---|---|---|
| retorno líquido | +34,2% | **+33,2%** |
| excesso × SPY | +4,08 pp | **+3,04 pp** |
| Sharpe | 1,21 | **1,18** |
| views/dia | 2,24 | **1,99** |
