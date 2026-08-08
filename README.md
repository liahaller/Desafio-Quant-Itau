# Desafio-Quant-Itau

Black-Litterman alimentado por probabilidades do Polymarket. Este é o branch
**`Felipe`**: otimizador BL, bridge probabilidade→Q, views e loop de backtest.

## Como reproduzir (leia primeiro)

⚠️ **Nenhum branch roda sozinho.** O código está no `Felipe`, o `data/` está no
`Paulo` e o Ω reativo está no `Lia`. O `data/` **não é versionado aqui** — ele
entra por cópia e fica no `.git/info/exclude` local, para não sujar o branch nem
duplicar dado que tem dono. A entrega final exige o merge dos três, que não é
feito por este branch.

```sh
# 1. dado do Paulo, sem merge e sem sujar o working tree
git fetch origin Paulo
git archive origin/Paulo data | tar -x
echo "data/" >> .git/info/exclude     # só uma vez, é local

# 2. suíte (183 testes, ~3 s) — roda sem o data/, é tudo sintético
python -m pytest tests/ -q

# 3. os quatro artefatos do relatório, nesta ordem
python scripts/backtest_v1.py    --raiz .   # -> Dump/analises/Backtest_v1.md
python scripts/curva_c.py        --raiz .   # -> Dump/analises/Curva_c.md
python scripts/curva_orcamento.py --raiz .  # -> Dump/analises/Curva_orcamento.md
python scripts/curva_banda.py    --raiz .   # -> Dump/analises/Curva_banda.md
```

Os quatro escrevem em `Dump/analises/` e são independentes — cada um recarrega o
dado do zero. O `--raiz` é o diretório que contém `data/`, e não precisa ser o
repositório: `--raiz /caminho/do/branch/paulo` roda contra a cópia dele sem
copiar nada.

**Ambientes medidos:** os quatro artefatos saem **byte a byte iguais** nos dois
abaixo — inclusive atravessando a major do pandas.

| | Python | numpy | pandas | scipy | pyarrow |
|---|---|---|---|---|---|
| 07/08 | 3.11.2 | 2.3.4 | 2.3.3 | 1.16.3 | 25.0.0 |
| 08/08 | 3.11.3 | 2.3.3 | **3.0.4** | 1.16.2 | 25.0.0 |

Não há `requirements.txt` porque não há dependência fixada — se os números
divergirem, comece conferindo a versão do pandas (a leitura de PMF depende de
`groupby`/`reindex`). Suíte: 183 verdes nos dois.

## O que cada coisa é

| Caminho | O que é |
|---|---|
| `src/bl_optimizer.py` | reverse optimization, posterior He & Litterman, pesos |
| `src/bl_integration.py` | empilha as views ativas e devolve o `w` do dia |
| `src/backtest.py` | motor do loop: composição, custo, giro, teto, banda |
| `src/view_2_2_inflacao.py`, `src/view_2_3_fed.py` | as duas views ativas do v1 |
| `src/poly_loader.py`, `src/poly_preprocessing.py` | leitura e tratamento da PMF |
| `scripts/backtest_v1.py` | o backtest do v1 ponta a ponta (plumbing de dado) |
| `scripts/curva_*.py` | varreduras de parâmetro — **medem e reportam, não escolhem** |
| `Decisoes_pendentes.md` | fonte da verdade do que está decidido e do que não está |
| `LOG.md` | ata por sessão |

Parâmetro do modelo (τ, δ, teto, γ, banda, orçamento) **não se escolhe olhando
resultado de backtest** — o protocolo está na seção 10 do `Decisoes_pendentes.md`.
Por isso as varreduras existem: elas reportam a grade inteira e nenhuma linha
delas é proposta.
