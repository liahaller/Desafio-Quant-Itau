# Templates de reestilização — seis propostas, do atual ao challenge

**Estado (2026-09-18):** só o **T6** fica na pasta; T1–T5 foram descartados
pelo dono. As tabelas abaixo ficam como registro da comparação; os cinco
podem ser regerados com `python scripts/templates_reestilizar.py --todos`.

Cada `T*.pptx` tem UM slide de exemplo com o mesmo conteúdo (título, três
caixas ligadas por setas, texto, fórmula nativa do PowerPoint, gráfico nativo,
caixa de conclusão, rodapé/navegação). Só o estilo muda — a comparação é de
estilo. Os `T*.png` são o render de cada um pelo PowerPoint. Gerador:
`scripts/templates_reestilizar.py`. Dados do exemplo são ilustrativos.

Referências (na mesma pasta): **Polaris** (Insper, AB InBev — cinza-claro,
grafite + amarelo, aba lateral de seção, nav inferior), **Wolves of Quatá**
(Insper, Fleury — branco + navy, índice lateral, círculos numerados),
**Waterloo** (Rotman 2026, vencedor — branco, barras pretas, acento vermelho,
"Seção | Título", nav inferior com seção ativa, caixas tracejadas).

## O gradiente

| | template | fundo | referência | o que muda em relação ao deck atual |
|---|---|---|---|---|
| T1 | **Kairós sóbrio** | escuro (navy chapado) | o próprio deck, sem enfeites | sai o fundo radial, os halos, o glow, o número fantasma e os cards em degradê; cards retos com borda de 1 pt; kickers deixam o Consolas. Mesma fonte (Bahnschrift), mesmo dourado, mesmo cabeçalho e rodapé. |
| T2 | **Kairós claro** | claro (branco) | T1 invertido | tudo do T1 em fundo branco: dourado escurecido para ler no claro, painéis cinza-claro, texto grafite. Estrutura idêntica. |
| T3 | **Terminal** | escuro (grafite) | Waterloo em fundo escuro | formato research: "Seção \| Título" com régua, marca à direita, barra de navegação inferior com a seção ativa sublinhada, círculos numerados nas caixas, conclusão em caixa tracejada. Fonte Segoe UI; dourado único como acento. |
| T4 | **Consultoria** | claro (cinza F2F2F2) | Polaris | aba lateral grafite com a seção, título grande + subtítulo cinza, painéis brancos com barra dourada no topo, conclusão em painel grafite com texto branco, nav inferior em caixa alta. |
| T5 | **Research** | claro (branco) | Waterloo | barras pretas de rótulo nas caixas, acento vermelho, setas em bloco cinza, caixa tracejada, nav inferior com seção ativa em vermelho. O mais próximo do deck vencedor. |
| T6 | **Terminal Polymarket** | escuro (grafite) | T3 com o azul do Polymarket | o T3 idêntico (linhas, bordas e texto secundário cinza), com a série de mercado do gráfico em azul Polymarket escurecido (2A4BC4) no lugar do cinza; dourado segue como acento. Fora da ordem do gradiente — é uma variante de cor do T3. |

## Esforço de refatoração (slide a slide)

O deck da final tem 34 slides; a maior parte sai dos geradores
(`draft_semis_pptx.py`, `slides_3a6_pptx.py`, `slide8_pesquisa_pptx.py`,
`slides_apendice_pptx.py`, `slides_final_pptx.py`) e o resto foi editado à
mão no PowerPoint. Os gráficos são PNG de matplotlib com a paleta `SLIDE`.

| | esforço | o que precisa ser feito | o que se aproveita |
|---|---|---|---|
| T1 | **baixo** | trocar `moldura()` e a primitiva de card nos geradores (fundo chapado, sem efeitos, cantos retos, kicker sem mono) e regerar; nos slides manuais, apagar halos e número fantasma e retirar o degradê dos cards. | todos os layouts, todos os gráficos (fundo escuro igual), todos os textos e tamanhos. |
| T2 | **médio** | tudo do T1 + inverter a paleta (texto/fundo/painéis) nos geradores e **regerar todos os gráficos** com fundo claro; nos slides manuais, recolorir texto e cards à mão. | layouts, tamanhos de fonte, posições. |
| T3 | **médio-alto** | cabeçalho e rodapé novos (Seção \| Título, régua, nav inferior), cards e kickers redesenhados, círculos numerados; a troca de fonte (Bahnschrift condensada → Segoe UI, mais larga) muda quebras de linha: **cada slide precisa de conferência**; gráficos regerados na paleta cinza + dourado. | fundo escuro (gráficos só mudam de paleta), estrutura de coluna dos slides. |
| T4 | **alto** | tudo do T2 + aba lateral, painéis brancos com barra, cada slide ganha um subtítulo, conclusão em painel grafite; layouts redesenhados slide a slide para o formato "título + subtítulo + painéis". | o conteúdo e os dados dos gráficos. |
| T5 | **alto** | paleta nova (preto + vermelho) em todos os gráficos, barras pretas de rótulo, tabelas com cabeçalho preto, nav inferior; o formato é mais denso — alguns slides pedem tabela ou linha de fonte que hoje não têm. | o conteúdo e os dados dos gráficos. |
| T6 | **médio-alto** | igual ao T3 (mesma estrutura); só a paleta dos gráficos muda para azul + dourado, que é a do deck atual — os PNG de matplotlib precisam de menos retoque do que no T3. | tudo o que o T3 aproveita, mais a paleta dos gráficos atuais. |

Regra de bolso: T1 é uma tarde de gerador; T2 e T3 são um dia (regerar
gráficos e conferir cada slide); T4 e T5 são reconstrução do deck (dois ou
três dias, com os slides manuais refeitos).

## Notas técnicas

- A **fórmula é equação nativa** (OMML dentro de `mc:AlternateContent`):
  editável em Inserir → Equação; leitores antigos veem o texto do fallback.
- O **gráfico é nativo** (colunas agrupadas): dados e cores editáveis no
  PowerPoint. Os gráficos do deck real são PNG de matplotlib; para o deck
  final, manter matplotlib e só trocar a paleta é o caminho barato.
- Fontes: Bahnschrift (T1, T2) e Segoe UI (T3–T5) vêm com o Windows 10+;
  Cambria Math na equação.
