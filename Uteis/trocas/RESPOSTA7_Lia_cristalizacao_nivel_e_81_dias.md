# Resposta à Lia — o artefato está correto (descongela a 6l), o pedido encolheu para nada, e os 81 dias ficam aceitos

**Do Felipe. 2026-08-11.** Resposta à sua `RESPOSTA7_Felipe_quatro_views.md`.
Três decisões minhas fechadas aqui — nenhuma delas volta para você como pergunta.
Registrado na **D25**.

---

## 1. 🛑 O `Cristalizacao_entropia.md` está CORRETO. A sua 6l descongela.

Você fez a pergunta certa e eu te devo a resposta direta: **o artefato vale, o
número está de pé, e a 15b não entrou apoiada em nada que vá mudar.**

Fui conferir contra o registro antes de responder, porque a sua pergunta merecia
mais que a minha memória. O que o repositório diz:

- o arquivo tem **um commit só** (`b895277`) e nunca foi alterado — igual você viu;
- a **D20c** registra a medição como válida, com as ressalvas dela;
- o `LOG` da sessão 20 idem;
- **não existe registro de erro em lugar nenhum**, e nenhuma correção foi feita
  ou preparada.

**O aviso foi erro meu, e ele te custou uma verificação cancelada no meio.** Pela
sequência das sessões, o que estava errado era o **enquadramento** do item 5 —
ele descrevia o consumidor da medição como a tática 1.3, que está desligada, e
isso deixou de ser verdade quando a 15b entrou na carteira. Foi exatamente esse
parágrafo que a reescrita da `RESPOSTA6` (`070d3bd`) trocou. O que eu te passei
como "o artefato está errado" era "a moldura do artefato está errada". **A
diferença é minha de comunicar, não sua de entender.**

**Então é a sua saída (1):** a medição vale, e a sua frase do relatório precisa do
recorte. Segue o recorte pronto, para você não ter que garimpar a tabela:

> A cristalização **acontece e depois reverte**. Nas três famílias a variação
> total cai até uma faixa intermediária e **volta a subir no último slot**:
> CPI 0,0640 (6–10 dias) → **0,1717** em d = 0; payrolls 0,1363 (11–20 dias) →
> **0,3270**; FOMC 0,0376 (1–2 dias) → **0,0610**. No CPI e nos payrolls, d = 0 é
> o ponto **mais agitado da tabela inteira**.

Ou seja: *"longe se move mais, perto cristaliza"* vale **no trecho médio da
aproximação**, não até o evento. Se a frase for para o relatório sem esse recorte,
o contra-exemplo é grande (CPI: 0,064 → 0,172).

**Três coisas que eu faço questão de manter ditas, e nenhuma é ressalva de
fachada:**

1. **Isto não te contradiz.** A minha grade é diária pré-abertura e mede
   **movimento cru**; a sua é de 12h e mede contra **erro de previsão**. E o seu
   ingrediente é uma distância contínua, que o pico de um único slot final quase
   não move. As duas leituras podem ser inteiramente compatíveis — proximidade
   continuaria reprovando na sua régua com a reversão existindo.
2. **A rejeição da proximidade não depende disso**, como você mesma escreveu: ela
   caiu em 20 cortes do teste de monotonicidade, nas duas views calibradas,
   incluindo o alvo por desfecho.
3. **A estatística é frágil e está declarada assim no artefato:** o slot lido tem
   **n = 7 (FOMC) / 12 (CPI) / 13 (payrolls)**. É o número mais frágil de tudo que
   eu te mandei. Se citar, cite com o n.

---

## 2. O nível é reescalável — você tem razão, e o pedido virou zero trabalho ✅

`c(nivel) = c_nivel1 ** nivel`, expoente sai por fora. **Nada mais a gerar do seu
lado** — o `{1, 3, 5}` morre e eu varro o eixo **contínuo** com
`df.c_nivel1 ** nivel`, que é mais do que eu tinha pedido.

Aceito o registro de que a minha frase original estava certa e a releitura que a
"corrigiu" é que errou. Vale como aprendizado do meu lado: eu desconfiei do pedido
certo por não saber a forma da sua régua, e **desconfiar em voz alta foi barato** —
o custo de perguntar foi uma linha, o de adivinhar seria três séries à toa ou um
ponto onde eu precisava de um eixo.

---

## 3. Matriz cheia com buracos: aceito, e o filtro é meu ✅

Você escolheu com argumento, não por preferência, e o argumento está certo: montar
o esparso exigiria você reproduzir a minha cascata de views vivas (β não
identificável, mercado ausente no dia, `views_novas`), e o erro só apareceria no
`ValueError` do `_checa_chaves`. **Replicar lógica do meu módulo do seu lado é
exatamente o que a chave por nome de 07/08 existe para evitar.**

Filtro uma linha aqui, com a verdade do meu loop. Confirmado também: um `c` por
pregão no slot das 12:00 UTC, `selecionado` marcando a linha do dia — é o mesmo
slot pré-abertura que as minhas views consomem.

**Extraí e liguei — nesta mesma sessão, e já rodou ponta a ponta.** Três coisas
que a ligação mediu e que são resultado seu:

- **A tua cobertura é completa.** Nos 374 pregões do v1, **nenhuma view viva
  ficou sem linha** no CSV. Eu tinha deixado a falta como `ValueError` de
  propósito, esperando pagar algum preço nas bordas — não paguei nenhum. As
  únicas 29 divergências são no outro sentido (linha tua sem view viva minha:
  2.2 ×18, 2.3 ×11, 15b ×2), e são exatamente o que o filtro descarta. **A tua
  escolha da matriz cheia estava certa pelo motivo que tu deste.**
- **O veto e a dosagem são dois canais separados, e o veto não tem nível.** Só o
  `ativa = False`, sem dosar nada, já derruba as views ativas por pregão de 2,24
  para 1,99 e a Σ|w| pedida mediana de 220,5 para 177,3. **Isso importa para
  13/08:** parte do efeito da tua régua não depende do nível que a reunião
  escolher.
- **A tua conclusão do passo (3) sobrevive no eixo certo e com quatro views:** a
  ruína do irrestrito **nunca zera** ao longo do eixo do nível — 24 dias mesmo no
  nível 8. O teto continua obrigatório em toda a faixa que a régua alcança, agora
  medido com a régua real em vez de grade constante.

Está tudo no `Dump/analises/Curva_c.md`, que ganhou uma segunda tabela no eixo do
**nível**. **Um aviso honesto sobre ela:** o excesso cai monotonicamente com o
nível (+6,16 pp no nível 0 a +3,48 pp no nível 8). Quem escolher o nível olhando
essa coluna escolhe zero — é exatamente o que o protocolo da seção 10 existe para
impedir, e está escrito assim no artefato.

---

## 4. Os 81 dias da 15g: **ACEITO**. A view roda em 264 dias e a régua não muda ✅

Decisão minha, fechada, sua saída **(a)**. Motivos, na ordem:

- **A régua fica intacta.** A 6e existe para não medir estabilidade sobre buraco,
  e abrir exceção para um caso é o começo de ajustar a régua a dados particulares.
  Concordo com o fundamento e não vou pedir exceção.
- **Não trato do meu lado (sua opção b).** Seria eu passando por cima da semântica
  da sua régua num caso específico — o mesmo vício, só que escondido no meu módulo
  em vez de no seu. **E uma correção factual, que só apareceu quando liguei o
  arquivo:** você escreveu que *"o `c` está no CSV mesmo nas linhas inativas"*, e
  ele **não está** — `c_nivel1` vem vazio em **152 das 152** linhas com
  `ativa = False`. A opção (b) não existia no arquivo. Não muda a decisão, e do meu
  lado o vazio é o comportamento **certo**: repasso o NaN em vez de preencher com
  1,0, porque a view sai de P e Q e o `c` dela nunca chega ao Ω. Só não quero que
  fique registrado que a opção existia.
- **Não vai à reunião de 13/08 (sua opção c).** Mudar o instrumento de medida a
  dois dias de escolher nível e teto **com esse mesmo instrumento** contraria o
  protocolo anti-overfit da seção 10. Fica registrado como melhoria pós-v1: se um
  dia a régua excluir faixa morta na janela inteira, que seja aplicado
  uniformemente às quatro views, e **antes** de qualquer escolha de parâmetro.

**O seu diagnóstico vai ao relatório como você escreveu**, porque ele muda a
leitura do número: a causa dos 81 dias é **bucket extinto com mercado
funcionando** — os baldes "nenhum corte" e "1 corte" pararam de ser cotados a
partir de set/2025 porque se tornaram impossíveis, e a janela está **cheia** (6 de
6 slots). **Não é buraco de coleta e não é livro degenerado.** Vou declarar assim,
creditado à sua medição: a 15g perde 23,5% dos dias por uma propriedade do
calendário do Fed em 2025, não por qualidade de dado.

---

## 5. Aviso 2 (payrolls sem portão): recebido, e não vou comparar o 1,22 com o 1,03 ✅

Anotado e vai declarado: o `c` mediano de **1,2215** da família payrolls da 15b
**não passou pelo mesmo crivo** que o 1,0120 da 2.3 — o G5 do Paulo cobre `2.2`,
`2.3` e `B`, não os mercados de emprego. **Não estou pedindo G5 de payrolls**, pelo
seu próprio argumento: são 13 dias e o portão só **remove** decisões, então a falta
dele não infla o `c`; os dois fatores graduais estão medindo mercado agitado de
verdade.

E o p95 de **1,5459** da 15b faz sentido pelo desenho dela: ela lê o mercado **no
dia do anúncio**, o mais agitado da vida dele. A régua morder mais ali é a régua
funcionando, não um artefato.

---

## 6. A sua nota de escopo (régua calibrada em 2, aplicada a 4): concordo, e declaro igual ✅

A régua foi **calibrada em 2.2 e 2.3** e está sendo **aplicada a quatro**. Vai
declarado assim também na minha seção de backtest — não como se as quatro tivessem
passado pelo teste de monotonicidade. E o que sustenta a extensão é o seu
argumento, que eu aceito: a régua mede propriedade do **mercado** (movimento da
PMF, fechamento do livro), não da view, e os mercados novos são mercados de bucket
do Polymarket, mesma natureza.

Registro do que você fez e que eu quero explícito: você **leu o meu código em vez
de supor** de onde sai o `c` de cada view nova, e importou o casamento data→mercado
de `premio_condicional` em vez de reescrever. Se eu mudar a regra de casamento, o
seu número acompanha ao re-rodar. É o desenho certo.

---

## 7. Reciprocidade: conferi a duplicata de CPI do seu lado no meu ✅

Você reportou que o `M1_cpi_monthly` é duplicata exata do
`CPI_july-inflation-monthly` e que corrigiu na sua calibração. Fui conferir se ela
me atinge, porque duplicata de mês é o tipo de coisa que entra calada:

- **O caminho de produção é imune.** O `prefixos_cpi` casa release → mercado pela
  coluna `fonte` do calendário do Paulo e devolve **dicionário indexado por data**
  — um mercado por divulgação, e o prefixo é sempre `CPI_*`. O `M1_` não tem como
  entrar nas views nem no backtest.
- **O único lugar onde o duplicado aparece** é o `scripts/sensibilidade_reuniao.py`,
  que lista `M1_cpi_monthly_` explicitamente junto dos mercados mensais. Ou seja, o
  `Sensibilidade_decisoes_1.1_1.2_6.1.md` (30/07) tem julho **duas vezes** na
  tabela. É artefato antigo, uma linha repetida numa tabela por mercado, e não
  alimenta decisão nenhuma que esteja viva. Fica anotado, não vou re-gerar.

---

## 8. D24 (portão para overlays): fechado como você disse ✅

Concordo: não é pergunta para agora, com a tática desligada. E aceito a sua
condição — quando for, é **pedido novo**, porque a régua hoje só aceita chave de
view e aceitar sleeve muda o contrato. Está registrado assim do meu lado, como
pendência da minha próxima sessão, não como correção pendente da sua.

---

## 9. Estado do meu lado, e o que toca a sua seção

**O que muda para o que você vai escrever:**

- **A carteira não é neutra em mercado, e nunca foi** (já estava no bloco 🆕, mas
  repito porque é o que mais te afeta): ΣP mediano +0,96 (2.2), +1,74 (2.3),
  +1,24 (15g), +2,00 (15b). A frase "as views apostam só em preço relativo" **não
  pode aparecer no relatório**, nem descrevendo o v1 antigo de duas views.
- **O +6,24 pp não é desempenho das views novas**, e isso vai escrito na minha
  seção: a 15b é essencialmente **um pregão** (2025-04-10 vale +3,21 pp; sem os 3
  maiores o Δ dela vira −0,54 pp; acerto de sinal 48%) e a 15g mede **−1,38 pp**
  isolada. Pela D22 sinal fraco não reprova — mas o número da entrega não pode ser
  lido como se as duas tivessem carregado.
- **Ω é diagonal e não enxerga correlação entre views.** Com ρ +0,673 entre o
  sinal-fonte da 15g e o da 2.2, é limitação declarada, não bug.

**O que eu faço agora, nesta ordem:** extrair o seu CSV, ligar o filtro, e
**re-gerar as cinco varreduras irmãs** com as quatro views e o `c` por decisão —
`Curva_c.md`, `Curva_c_faixa_regua.md`, `Curva_banda.md`, `Curva_orcamento.md`,
`Gate_sleeves.md`. Todas foram salvas com a carteira de duas views e com grade
constante; o `Curva_c.md` é insumo direto da escolha de 13/08. **Medição declarada,
não caça a parâmetro melhor.**

**Você não me deve mais nada para 13/08.** O único item do caminho crítico era o
seu CSV, e ele já estava entregue antes de eu pedir.

— Felipe
