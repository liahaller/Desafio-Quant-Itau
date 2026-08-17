# Relatório final — KAIROS

`KAIROS.pdf` é o entregável: 5 páginas, 16:9 (960 × 540 pt), anônimo.
Renome-ar para `[chave de envio].pdf` na hora de enviar.

## Como regerar

```
cd fonte
python regerar_graficos_p4.py  # redesenha os 3 gráficos da página 4 pelo gerador do autor
python importar_graficos.py    # recorta os da página 5 e a arte, dos PDFs recebidos
python montar.py             # injeta imagem e SVGs no template, gera o PDF e valida
python montar_pptx.py        # reconstrói a página 3 como slide de PowerPoint editável
```

O `montar.py` valida sozinho contra o edital: número de páginas (≤ 5), proporção
16:9 exata, contagem de palavras e ausência de qualquer identificador de autor,
equipe ou instituição.

## As cinco páginas num fonte só (16/08/2026)

As páginas 1, 2, 4 e 5 chegaram como **PDFs prontos**, cada uma com o estilo de
quem a fez: `kairos_p1.pdf` e `kairos_p2_final.pdf` em Calibri sobre fundo em
degradê, `KAIROSv2_p4_p5.pdf` em Segoe UI sobre preto. Elas foram **remontadas no
`template.html`** com o CSS da página 3 — mesma paleta, mesma família, mesmo
cabeçalho, mesmos padrões de título, bloco e nota. O texto é o que o autor
escreveu, palavra por palavra; o que mudou foi a moldura.

Duas alterações combinadas, e só elas: a numeração `01 / 05` virou `01`, e
`KAIRÓS` virou **`KAIROS`** nas páginas 4 e 5 (o nome sem acento é decisão de
16/08 e já valia nas outras três). O `montar.py` confere isso a cada geração,
comparando os caracteres de cada página com os do PDF de origem — se alguém
mexer no texto de uma página alheia, a checagem acusa.

Os **três gráficos da página 4** não são recorte: a legenda da curva dizia
`Kairós` e trocar a letra dentro da imagem não dá. O `regerar_graficos_p4.py`
extrai o `origin/Felipe` para um diretório fora do repositório, troca o rótulo na
**cópia** do `scripts/graficos_p4.py` e roda o gerador ali — o módulo alheio não
é tocado, e a saída vem melhor que o recorte: 300 dpi com fundo transparente,
desenhada sobre os mesmos CSV do autor. As métricas que ele imprime de brinde
conferem com a tabela da página, número a número.

ℹ️ A palavra **`Kairós` com acento continua na página 1**, em "Kairós, no grego,
é o instante oportuno": ali é a palavra grega sendo explicada, não a marca.

As páginas 4 e 5 usam a variante `.slide.densa` do CSS: mesma identidade, margens
menores. Sem isso, o conteúdo entregue nelas só caberia em corpo de 5,5 pt.

O `montar_pptx.py` refaz a **página 3 em PowerPoint** (`KAIROS_pagina3.pptx`):
um slide de 960 × 540 pt em que texto, filetes, cartões, tabelas e barras são
formas nativas e editáveis — só o diagrama das duas camadas entra como imagem,
gerada do `arquitetura.svg` pelo mesmo Chrome. As posições são as medidas no
`KAIROS.pdf`, e ao final ele compara os caracteres do slide com os da página 3 do
PDF: se alguém mudar o texto do relatório e não o slide, a checagem acusa.
⚠️ Roda **depois** do `montar.py`, que é quem produz o PDF de referência.

## O que gera o quê

| Arquivo | Papel |
|---|---|
| `template.html` | as 5 páginas, com `{{PLACEHOLDERS}}` para imagem e gráficos |
| `montar.py` | injeta, chama o Chrome headless (`--print-to-pdf`) e valida |
| `montar_pptx.py` | a página 3 em `KAIROS_pagina3.pptx`, para apresentar |
| `importar_graficos.py` | recorta os 6 gráficos das páginas 4 e 5 do PDF recebido |
| `importado/*.png` | esses recortes, já com o fundo do relatório |
| `pipeline.svg` | diagrama da página 2, desenhado à mão |
| `arquitetura.svg` | diagrama das duas camadas (página 3), desenhado à mão |
| `svg/*.svg` | os três gráficos, gerados por `graficos.py` |
| `dados/curva_diaria_regua_nivel1.csv` | série diária da carteira de entrega |
| `kairos_datauri.txt` | a arte do robô já em base64 (a que veio na página 1) |

⚠️ **Dois dos três SVGs estão sem consumidor** desde a reestruturação da página 3
(16/08/2026): `ingredientes.svg` e `regua.svg`. A página passou a desenhar o
placar dos ingredientes em HTML — na coluna de 3,7 in o SVG do matplotlib cairia
para ~4,5 pt de tipo, metade da menor fonte do relatório. Os dois seguem sendo
gerados; reinserir qualquer um é devolver o `{{PLACEHOLDER}}` ao template.

## Dependência externa dos gráficos

`extrair_serie.py` **não roda direto neste branch**: ele reexecuta o backtest de
entrega importando `src/` e `scripts/backtest_v1.py` do branch `Felipe` com o
`data/` do branch `Paulo`, ambos extraídos para um diretório de trabalho fora do
repositório. A série resultante já está versionada em `dados/`, então
`graficos.py` e `montar.py` rodam **direto do repositório** (caminhos derivados do
próprio arquivo desde 16/08/2026 — antes apontavam para o drive de trabalho `X:`).

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
