# Banco de Ideias — Polymarket como dado alternativo (consolidado)

Consolidação dos dois arquivos (*Dump da reunião* + *Estudo fundamentalistas*). As ideias de IA foram removidas conforme pedido.

**Como ler:**
- ⭐ = ideia que você marcou como boa.
- *Sua avaliação* = sua nota original do arquivo.
- Nas ideias fundamentalistas, a explicação é **a sua versão** (não a acadêmica longa); a base acadêmica fica só como âncora de uma linha.
- As ideias do mercado comum foram resumidas de forma curta.
- *Nota de sobreposição* = onde a ideia se conecta/se distingue de outra.

---

## 1. Estratégias fundamentalistas (âncora acadêmica)

### 1.1 Drift pós-evento (PEAD) ⭐
**Base:** análogo ao PEAD de Bernard & Thomas (1989); underreaction (Barberis, Shleifer & Vishny, 1998).
**Ideia:** surpresas demoram alguns dias para serem ajustadas no preço. Dá pra descobrir quando algo é surpresa comparando a previsão do poly com o que aconteceu — se o poly dá 30% de algo acontecer e aquilo acontece, você sabe que vai ter drift e pode se posicionar nas ações relacionadas. O poly vira o seu medidor padronizado de surpresa para qualquer tipo de evento.
*Sua avaliação:* ideia bem interessante e robusta.
*Nota de sobreposição:* parecida com a Event-driven (3.2), mas distinta — aqui você opera **depois** da resolução; lá, **antes**.

### 1.2 Momentum em crenças ⭐
**Base:** Time-Series Momentum (Moskowitz, Ooi & Pedersen, 2012); sticky expectations (Coibion & Gorodnichenko, 2015).
**Ideia:** leitura de momentum no Polymarket. Sabendo que uma previsão vem subindo nas últimas semanas, ela provavelmente vai continuar subindo. Ao perceber uma tendência de alta ou queda numa previsão macro, você altera sua posição.
*Sua avaliação:* cria sinais direcionais para ajuste do portfólio — cada previsão analisada gera um sinal que ajusta a posição; ajuda a escolher setores específicos e a **controlar o beta do portfólio**.
*Nota de sobreposição:* tema macro em comum com o Índice de sentimento (3.1), mas o sinal é diferente — aqui é a **tendência** da probabilidade, lá é a **divergência de nível** entre poly e mercado.

### 1.3 Prêmio de risco de anúncios macro ⭐ (com ressalva)
**Base:** Savor & Wilson (2013); pre-FOMC drift de Lucca & Moench (2015).
**Ideia:** quando há anúncios macroeconômicos, espera-se volatilidade. Nesses dias, a maior parte do dinheiro é feita por quem compra ações e se expõe ao risco da vol. A ideia é usar a bet do poly que prevê o anúncio: quando o poly está incerto (não sabe o que vai acontecer), você se expõe às ações (vol); quando está certo, não.
*Sua avaliação:* esperado que no longo prazo seja positivo, mas com possibilidade de perdas grandes.

---

## 2. Black-Litterman — arquitetura + views

As três views abaixo são os insumos concretos que alimentam a arquitetura complexa (2.1).

### 2.1 Arquitetura complexa: portfólio condicionado a cenários precificados pelo Polymarket
**Conceito:** o Polymarket dá, em tempo real, uma distribuição de probabilidades sobre estados futuros do mundo. Em vez de assumir retornos estáticos, o portfólio se reposiciona conforme essas probabilidades mudam. É um **Black-Litterman onde as views vêm do Polymarket** em vez de analistas.
- **Camada 1 — Extração de estados macro:** agregar mercados do poly num vetor de cenários (corte de juros, recessão, geopolítica, eleições); limpar ruído de mercados ilíquidos e corrigir favorite-longshot bias.
- **Camada 2 — Mapeamento cenário → ativos:** estimar sensibilidade histórica de S&P, Treasuries, dólar, setores e ações a cada estado do mundo (regressões condicionais / análise de eventos). Gera matriz de retornos condicionais.
- **Camada 3 — Construção do portfólio:** otimizador combina camadas 1 e 2 — retorno esperado = soma dos retornos condicionais ponderados pelas probabilidades do poly.
- **Camada 4 — Overlay de risco:** usar a dispersão/oscilação das probabilidades perto de eventos agendados como termômetro; reduzir exposição ou comprar proteção quando a incerteza sobe.
- **Sinal tático — velocidade de ajuste:** além do nível, usar a *derivada* das probabilidades; quando o poly se move rápido e o mercado tradicional ainda não reagiu, posições táticas de curto prazo por cima da alocação estrutural.

Vantagem modular: se um módulo não funcionar empiricamente, descarta sem derrubar o projeto.

### 2.2 View de inflação — breakevens sintéticos (TIPS vs nominais) ⭐
**Base:** decomposição de juros nominais em expectativa + prêmio de risco (Fisher; literatura de breakeven).
**Ideia:** igual à de eleição, mas sem precisar mapear cestas: olhando os títulos de proteção (TIPS) você quantifica o que o mercado prevê de inflação. Quando há diferença entre isso e os mercados de inflação do poly, você aposta no do poly (assumindo que ele é mais rápido), comprando ou shorteando os títulos de proteção.
*Sua avaliação:* legal.

### 2.3 View de política monetária — curva de probabilidades do Fed
**Base:** Bernanke & Kuttner (2005); efeito assimétrico de surpresas de juros em setores duration-sensitive.
**Ideia:** você compara o que o Polymarket diz e o que o Fed Funds futures diz. Quando o poly diverge do Fed Funds, você aposta no que o poly está dizendo (teoria de que ele está mais certo) e compra as ações que se beneficiam dessa previsão. Monta a carteira com base no Fed Funds.
*Sua avaliação:* o poly tem que estar certo; carteira montada com base no Fed Funds.
*Nota de sobreposição:* mesmo tema "poly vs preço de mercado" do Índice de sentimento macro (3.1); aqui é a versão BL formalizada por setor.

### 2.4 View eleitoral e regulatória — cestas de exposição política
**Base:** policy uncertainty (Pástor & Veronesi, 2012, 2013); election portfolios.
**Ideia:** eleições afetam setores de formas diferentes. Você mapeia quais ações se beneficiam de cada candidato e olha o spread de valor (a "cesta" melhor é a do candidato que o mercado espera). Se o spread da cesta diz 50% mas o poly diz 70% de o candidato ganhar, você aposta na cesta dele porque o mercado ainda está atrasado, e aposta contra a cesta oposta.
*Sua avaliação:* você aposta em duas coisas — que a precificação está ligada à expectativa de resultado e que o poly é mais rápido que o mercado. Dificuldade: montar as cestas.

> **Detalhe que vale ouro na apresentação:** a maior crítica prática ao Black-Litterman é que as views e a matriz Ω são subjetivas. Aqui, *todas* as views vêm de probabilidades negociadas com dinheiro real, e *toda* a matriz de confiança vem de métricas objetivas (volume, liquidez, estabilidade, convergência entre fontes). O elo mais frágil e subjetivo do BL vira o mais sistemático.

---

## 3. Ideias para mercado comum (menos desenvolvidas)

### 3.1 Índice de sentimento macro implícito ⭐
Agregar probabilidades de vários mercados do poly (Fed, CPI, recessão, geopolítica) num índice único de expectativa macro. Operar as divergências entre esse índice e o que está precificado em juros/bolsa, posicionando em S&P, Treasuries ou ativos BR sensíveis ao ciclo americano.
*Sua avaliação:* legal.

### 3.2 Event-driven trading em ações expostas a eventos binários
Mapear mercados do poly ligados a empresas específicas (regulação, antitruste, fusões, eleições, decisões judiciais). Quando a probabilidade salta bruscamente, gerar sinal de compra/venda na ação antes de o mercado precificar. Ex: merger arb quando a prob de aprovação sobe de 40% para 70%.
*Nota de sobreposição:* ver PEAD (1.1) — distinção é antes (aqui) vs depois (lá) da resolução.

### 3.3 Polymarket como proxy de volatilidade de eventos agendados
Usar a dispersão e a velocidade das probabilidades do poly antes de eventos com data marcada como estimador de vol futura. Comparar com a vol implícita em opções (VIX, single stocks); montar straddles long/short quando há descasamento.
*Nota de sobreposição:* mesma lógica de incerteza usada na Camada 4 da arquitetura (2.1), mas aqui como estratégia direta de vol em vez de gestão de risco.

### 3.4 (Maluca) Detector de informação privilegiada / antecipação de notícias
Anomaly detection em alta frequência em todos os mercados do poly, cruzando com NLP de notícias. Movimento brusco **sem catalisador público** = sinal de informação ainda não pública; mapear automaticamente os ativos afetados e posicionar antes da imprensa. Discussão ética endereçável: opera sobre informação pública on-chain.

### 3.5 (Maluca) Carteira anti-narrativa
Inverter a lógica: identificar quando o poly está **sistematicamente errado** e operar contra. Hipótese: em eventos de forte carga emocional/política, o mercado herda o viés demográfico dos participantes. Classificar mercados "confiáveis" vs "contaminados por narrativa" (engajamento em redes, polarização, perfil dos traders, divergência vs casas de apostas e polls) e fazer fade nos contaminados. Combina com o modelo principal como filtro de qualidade de sinal.

---

## Decisões em aberto (do arquivo original)
- Estratégia complexa vs. estratégia simples.
- Atua no mercado normal.
- *(Uso de IA: removido deste arquivo conforme pedido.)*
