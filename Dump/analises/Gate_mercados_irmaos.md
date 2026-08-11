# Mercados irmãos — o mecanismo se repete no segundo mercado?

> Gerado por `scripts/gate_mercados_irmaos.py`. **Mede; não decide.** Nenhum corte cravado e **nenhuma premissa nova** — mercados, livros e grades vêm dos artefatos anteriores.

- janela do backtest: **2025-02-10 a 2026-08-06** (374 pregões)
- **μ CRU**, sem alinhar a premissa: alinhar embutiria a resposta, porque as premissas dos irmãos partidários já são espelhadas por declaração. O que se compara é para que lado cada ativo andou
- os livros testados são os **declarados dos dois irmãos**, aplicados aos dois mercados. Inventar um livro comum seria declarar premissa nova no meio de um teste de reprodução

## A relação exigida por cada par, declarada antes de medir

- **partidário** — M5 Trump 2024 ↔ M9 Câmara, relação **espelho**: um "SIM" em cada mercado significa o partido oposto — se o mecanismo for partidário, o μ inverte. **É o teste exato que derrubou a view 2.4**.
- **geopolítico** — M7 ação militar Irã (jun/2025) ↔ M7 ataque ao Irã (fev/2026), relação **igual**: os dois perguntam a mesma coisa, então o μ tem de repetir o sinal. **É o teste que derrubou a view C na D23f**.

| par         | relação   | livro              | lookback   | n A / n B   | μ cru A/B (bps/dia)                       | reproduz?   |
|:------------|:----------|:-------------------|:-----------|:------------|:------------------------------------------|:------------|
| partidário  | espelho   | direcional SPY/TLT | k = 1      | 136 / 98    | SPY -2.12/+2.82 ✅ · TLT +0.12/+2.96 ❌   | ❌          |
| partidário  | espelho   | direcional SPY/TLT | k = 2      | 163 / 126   | SPY -2.94/-0.02 ❌ · TLT -0.34/+1.47 ✅   | ❌          |
| partidário  | espelho   | direcional SPY/TLT | k = 3      | 179 / 147   | SPY -2.18/+2.67 ✅ · TLT -0.20/+0.70 ✅   | ✅          |
| partidário  | espelho   | direcional SPY/TLT | k = 5      | 193 / 164   | SPY -0.42/+3.59 ✅ · TLT +0.82/+1.53 ❌   | ❌          |
| partidário  | espelho   | direcional SPY/TLT | k = 10     | 194 / 194   | SPY -0.60/+1.43 ✅ · TLT +0.94/+0.11 ❌   | ❌          |
| partidário  | espelho   | direcional SPY/TLT | k = 20     | 192 / 204   | SPY +1.55/-0.40 ✅ · TLT +0.09/-1.12 ✅   | ✅          |
| partidário  | espelho   | setorial +XLF −XLP | k = 1      | 136 / 98    | XLF +0.04/+3.96 ❌ · XLP -1.54/+1.19 ✅   | ❌          |
| partidário  | espelho   | setorial +XLF −XLP | k = 2      | 163 / 126   | XLF -2.74/+3.84 ✅ · XLP -1.66/+0.26 ✅   | ✅          |
| partidário  | espelho   | setorial +XLF −XLP | k = 3      | 179 / 147   | XLF -1.04/+4.68 ✅ · XLP +0.08/-0.64 ✅   | ✅          |
| partidário  | espelho   | setorial +XLF −XLP | k = 5      | 193 / 164   | XLF -0.87/+6.45 ✅ · XLP +0.35/-0.62 ✅   | ✅          |
| partidário  | espelho   | setorial +XLF −XLP | k = 10     | 194 / 194   | XLF -0.59/+4.04 ✅ · XLP +1.71/+0.80 ❌   | ❌          |
| partidário  | espelho   | setorial +XLF −XLP | k = 20     | 192 / 204   | XLF +1.35/+2.73 ❌ · XLP -0.45/+2.31 ✅   | ❌          |
| partidário  | espelho   | neutro +XLF −XLP⊥  | k = 1      | 136 / 98    | XLF⊥ +2.11/+0.77 ❌ · XLP⊥ -0.14/+0.29 ✅ | ❌          |
| partidário  | espelho   | neutro +XLF −XLP⊥  | k = 2      | 163 / 126   | XLF⊥ +0.62/+2.58 ❌ · XLP⊥ +0.19/+0.26 ❌ | ❌          |
| partidário  | espelho   | neutro +XLF −XLP⊥  | k = 3      | 179 / 147   | XLF⊥ +1.22/+1.34 ❌ · XLP⊥ +1.37/-1.48 ✅ | ❌          |
| partidário  | espelho   | neutro +XLF −XLP⊥  | k = 5      | 193 / 164   | XLF⊥ -0.30/+1.91 ✅ · XLP⊥ +0.58/-1.68 ✅ | ✅          |
| partidário  | espelho   | neutro +XLF −XLP⊥  | k = 10     | 194 / 194   | XLF⊥ +0.10/+1.96 ❌ · XLP⊥ +2.10/+0.26 ❌ | ❌          |
| partidário  | espelho   | neutro +XLF −XLP⊥  | k = 20     | 192 / 204   | XLF⊥ -0.36/+2.54 ✅ · XLP⊥ -1.39/+2.23 ✅ | ✅          |
| partidário  | espelho   | setorial +XLP −XLK | k = 1      | 136 / 98    | XLP -1.54/+1.19 ✅ · XLK -3.09/+0.71 ✅   | ✅          |
| partidário  | espelho   | setorial +XLP −XLK | k = 2      | 163 / 126   | XLP -1.66/+0.26 ✅ · XLK -3.23/-1.44 ❌   | ❌          |
| partidário  | espelho   | setorial +XLP −XLK | k = 3      | 179 / 147   | XLP +0.08/-0.64 ✅ · XLK -3.20/+2.53 ✅   | ✅          |
| partidário  | espelho   | setorial +XLP −XLK | k = 5      | 193 / 164   | XLP +0.35/-0.62 ✅ · XLK +0.21/+1.81 ❌   | ❌          |
| partidário  | espelho   | setorial +XLP −XLK | k = 10     | 194 / 194   | XLP +1.71/+0.80 ❌ · XLK -1.41/-0.93 ❌   | ❌          |
| partidário  | espelho   | setorial +XLP −XLK | k = 20     | 192 / 204   | XLP -0.45/+2.31 ✅ · XLK +1.49/-3.79 ✅   | ✅          |
| partidário  | espelho   | neutro +XLP −XLK⊥  | k = 1      | 136 / 98    | XLP⊥ -0.14/+0.29 ✅ · XLK⊥ -1.10/-1.08 ❌ | ❌          |
| partidário  | espelho   | neutro +XLP −XLK⊥  | k = 2      | 163 / 126   | XLP⊥ +0.19/+0.26 ❌ · XLK⊥ -0.56/-1.09 ❌ | ❌          |
| partidário  | espelho   | neutro +XLP −XLK⊥  | k = 3      | 179 / 147   | XLP⊥ +1.37/-1.48 ✅ · XLK⊥ -1.08/+0.21 ✅ | ✅          |
| partidário  | espelho   | neutro +XLP −XLK⊥  | k = 5      | 193 / 164   | XLP⊥ +0.58/-1.68 ✅ · XLK⊥ +0.54/-0.73 ✅ | ✅          |
| partidário  | espelho   | neutro +XLP −XLK⊥  | k = 10     | 194 / 194   | XLP⊥ +2.10/+0.26 ❌ · XLK⊥ -0.78/-1.51 ❌ | ❌          |
| partidário  | espelho   | neutro +XLP −XLK⊥  | k = 20     | 192 / 204   | XLP⊥ -1.39/+2.23 ✅ · XLK⊥ +0.08/-2.62 ✅ | ✅          |
| geopolítico | igual     | direcional SPY/TLT | k = 1      | 50 / 28     | XLE +0.88/-1.41 ❌ · SPY +0.14/+3.09 ✅   | ❌          |
| geopolítico | igual     | direcional SPY/TLT | k = 2      | 52 / 27     | XLE +0.74/+0.11 ✅ · SPY +0.29/+3.33 ✅   | ✅          |
| geopolítico | igual     | direcional SPY/TLT | k = 3      | 53 / 24     | XLE -1.72/-0.69 ✅ · SPY -1.17/+1.17 ❌   | ❌          |
| geopolítico | igual     | direcional SPY/TLT | k = 5      | 54 / 23     | XLE -0.75/-1.96 ✅ · SPY -0.15/+0.78 ❌   | ❌          |
| geopolítico | igual     | direcional SPY/TLT | k = 10     | 47 / 18     | XLE -1.09/-0.69 ✅ · SPY +0.22/+0.39 ✅   | ✅          |
| geopolítico | igual     | direcional SPY/TLT | k = 20     | 39 / 9      | XLE -0.59/-2.41 ✅ · SPY -2.25/-0.05 ✅   | ✅          |
| geopolítico | igual     | setorial +XLE −XLK | k = 1      | 50 / 28     | XLE +0.88/-1.41 ❌ · XLK +0.24/+3.51 ✅   | ❌          |
| geopolítico | igual     | setorial +XLE −XLK | k = 2      | 52 / 27     | XLE +0.74/+0.11 ✅ · XLK +0.61/+4.19 ✅   | ✅          |
| geopolítico | igual     | setorial +XLE −XLK | k = 3      | 53 / 24     | XLE -1.72/-0.69 ✅ · XLK -2.39/+1.87 ❌   | ❌          |
| geopolítico | igual     | setorial +XLE −XLK | k = 5      | 54 / 23     | XLE -0.75/-1.96 ✅ · XLK -0.24/+1.00 ❌   | ❌          |
| geopolítico | igual     | setorial +XLE −XLK | k = 10     | 47 / 18     | XLE -1.09/-0.69 ✅ · XLK -0.16/+0.59 ❌   | ❌          |
| geopolítico | igual     | setorial +XLE −XLK | k = 20     | 39 / 9      | XLE -0.59/-2.41 ✅ · XLK -4.92/+0.15 ❌   | ❌          |
| geopolítico | igual     | neutro +XLE −XLK⊥  | k = 1      | 50 / 28     | XLE⊥ +1.83/-2.86 ❌ · XLK⊥ +0.04/+1.16 ✅ | ❌          |
| geopolítico | igual     | neutro +XLE −XLK⊥  | k = 2      | 52 / 27     | XLE⊥ +0.57/-1.39 ❌ · XLK⊥ +0.45/+1.50 ✅ | ❌          |
| geopolítico | igual     | neutro +XLE −XLK⊥  | k = 3      | 53 / 24     | XLE⊥ +1.19/-1.21 ❌ · XLK⊥ -1.42/+0.83 ❌ | ❌          |
| geopolítico | igual     | neutro +XLE −XLK⊥  | k = 5      | 54 / 23     | XLE⊥ -0.82/-2.11 ✅ · XLK⊥ +0.02/+0.39 ✅ | ✅          |
| geopolítico | igual     | neutro +XLE −XLK⊥  | k = 10     | 47 / 18     | XLE⊥ -1.58/-1.02 ✅ · XLK⊥ -0.95/+0.29 ❌ | ❌          |
| geopolítico | igual     | neutro +XLE −XLK⊥  | k = 20     | 39 / 9      | XLE⊥ +2.01/-1.23 ❌ · XLK⊥ -2.54/+0.18 ❌ | ❌          |

## Leitura

**Partidário (M5 Trump 2024 ↔ M9 Câmara, relação espelho): 13 de 30 células reproduzem (43%), contra **25%** que sair-se-ia por acaso (livro de 2 pernas, exigindo acerto nas duas).** Onde reproduz: `direcional SPY/TLT` k = 3 · `direcional SPY/TLT` k = 20 · `setorial +XLF −XLP` k = 2 · `setorial +XLF −XLP` k = 3 · `setorial +XLF −XLP` k = 5 · `neutro +XLF −XLP⊥` k = 5 · `neutro +XLF −XLP⊥` k = 20 · `setorial +XLP −XLK` k = 1 · `setorial +XLP −XLK` k = 3 · `setorial +XLP −XLK` k = 20 · `neutro +XLP −XLK⊥` k = 3 · `neutro +XLP −XLK⊥` k = 5 · `neutro +XLP −XLK⊥` k = 20.

⚠️ **A taxa acima NÃO é um teste estatístico, e não deve ser lida como um.** As células não são independentes: os horizontes se sobrepõem (k = 3 e k = 5 leem quase os mesmos dias) e os livros compartilham perna. O `n` efetivo é muito menor que 30, então a distância entre 43% e 25% não sustenta significância. Ela serve para uma coisa só: dizer se a reprodução é **rara** ou **comum** neste par. O que decide candidata é o cruzamento célula a célula, logo abaixo.

**Geopolítico (M7 ação militar Irã (jun/2025) ↔ M7 ataque ao Irã (fev/2026), relação igual): 5 de 18 células reproduzem (28%), contra **25%** que sair-se-ia por acaso (livro de 2 pernas, exigindo acerto nas duas).** Onde reproduz: `direcional SPY/TLT` k = 2 · `direcional SPY/TLT` k = 10 · `direcional SPY/TLT` k = 20 · `setorial +XLE −XLK` k = 2 · `neutro +XLE −XLK⊥` k = 5.

⚠️ **A taxa acima NÃO é um teste estatístico, e não deve ser lida como um.** As células não são independentes: os horizontes se sobrepõem (k = 3 e k = 5 leem quase os mesmos dias) e os livros compartilham perna. O `n` efetivo é muito menor que 18, então a distância entre 28% e 25% não sustenta significância. Ela serve para uma coisa só: dizer se a reprodução é **rara** ou **comum** neste par. O que decide candidata é o cruzamento célula a célula, logo abaixo.

⚠️ **Isso é praticamente o acaso.** A taxa de reprodução não se separa do que moeda jogada produziria, então este par **não** confirma o mecanismo — as células que reproduzem são compatíveis com sorte, e as que não reproduzem não são surpresa.

### O cruzamento que decide o nível 2

A pergunta não é *"o par reproduz em alguma célula?"* — é **se a célula exata que sobreviveu ao corte da amostra é uma das que reproduzem**. Uma célula que passa no corte mas reprova no irmão está medindo o mercado, não o mecanismo.

- **M9 Câmara** · `neutro +XLP −XLK⊥` · k = 20 — **✅** · μ cru A/B: XLP⊥ -1.39/+2.23 ✅ · XLK⊥ +0.08/-2.62 ✅. **A célula viva reproduz no mercado irmão** — é a evidência mais forte disponível para uma célula deste nível.
- **M7 ação militar Irã (jun/2025)** · `neutro +XLE −XLK⊥` · k = 20 — **❌** · μ cru A/B: XLE⊥ +2.01/-1.23 ❌ · XLK⊥ -2.54/+0.18 ❌. **A célula viva NÃO reproduz no irmão:** ela sobrevive ao corte dentro do próprio mercado e falha quando o mercado muda. É o padrão que matou a view irmã.
- **M5 Trump 2024** · `neutro +XLF −XLP⊥` · k = 1 — **❌** · μ cru A/B: XLF⊥ +2.11/+0.77 ❌ · XLP⊥ -0.14/+0.29 ✅. **A célula viva NÃO reproduz no irmão:** ela sobrevive ao corte dentro do próprio mercado e falha quando o mercado muda. É o padrão que matou a view irmã.

⚠️ **Sobre o M5 Trump:** a célula viva dele é o corte `q0.00` do gatilho de SALTO, que **não existe nesta grade de lookbacks** — `q0.00` é "todo dia com Δp ≠ 0", cujo vizinho mais próximo é k = 1, e é essa a linha lida acima. A correspondência é aproximada, e está dita para não ser lida como exata.

### Os mercados que NÃO têm irmão

A ausência deste teste **não é aprovação** — é limite do dado, e precisa estar visível ao lado de qualquer veredito positivo nesses mercados.

- **M4 recessão EUA 2025** — não existe segundo mercado de recessão no dado (registrado na própria D18d). Este teste **nunca** vai ser aplicável a ele.
- **CPI mensal (E_poly)** — família com mercado único por mês, sem par contemporâneo.
- **C1a M3 trajetória do Fed (nº de cortes)** — mercado único.
- **C1b reunião do FOMC (E_poly em bps)** — mercado único.
- **M6 tarifas China** — mercado único, e 8 pregões.
- **M8 reconciliação fiscal** — mercado único, e 2 pregões.

⚠️ **O caso que importa é o M4 recessão.** É a única célula que passou todos os critérios da maratona, e é justamente a que **nunca** poderá ser confirmada por mercado irmão. Ela vai depender para sempre de duas coisas: o corte em metades (que passa, inclusive em três horizontes contíguos no livro neutro) e a **explicação da contradição com a D19c**, que mediu inversão dentro da amostra neste mesmo mercado com a montagem da view 3.1.

**O que isto NÃO diz:** nada sobre P&L, e nada sobre os mercados sem irmão. Reprovar aqui é evidência forte contra o mecanismo; passar aqui seria evidência forte a favor — a ausência do teste não é nem uma coisa nem outra.

