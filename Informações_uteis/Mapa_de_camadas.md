# Mapa de camadas — onde cada ideia entra

Como as ideias do banco se distribuem na arquitetura. Cada camada responde uma pergunta diferente.

## 1. Camada que monta o portfólio
**O que faz:** define os pesos estruturais da carteira. Cada ideia vira uma *view* no Black-Litterman (opinião direcional + confiança), e o otimizador junta tudo em pesos.

- **Índice de sentimento macro (3.1)** — agrega vários mercados num vetor de cenários; dá o *regime* macro de fundo.
- **View do Fed (2.3)** — juros → inclina entre setores sensíveis a duration (tech, real estate) e defensivos.
- **View de inflação (2.2)** — poly de CPI vs. TIPS → TIPS vs. nominais.
- **View eleitoral (2.4)** — setores ganhadores/perdedores por cenário político → tilt nas cestas.
- **Momentum em crenças (1.2)** — tendência de uma probabilidade macro → sinal direcional que ajusta beta e setor.

Container: **Arquitetura complexa (2.1)** — pega as views, aplica a confiança e cospe os pesos finais.

> Divisão de trabalho: 3.1 dá o cenário · 2.2 / 2.3 / 2.4 dão as apostas concretas · 1.2 dá a direção · 2.1 vira tudo em carteira.

## 2. Camada tática
**O que faz:** não mexe nos pesos estruturais — adiciona trades curtos e oportunistas *por cima* da carteira. As três exploram a mesma coisa: a defasagem entre o poly se mexer e o mercado reprecificar. A diferença é só o *momento* em que entram.

- **Velocidade de ajuste (derivada)** — age *durante* o movimento; gatilho = derivada da probabilidade.
- **Event-driven (3.2)** — age *antes* da resolução; gatilho = salto de nível (ex.: fusão 40% → 70%).
- **Drift pós-evento / PEAD (1.1)** — age *depois* da resolução; gatilho = tamanho da surpresa.

## 3. Camada de risco / dimensionamento
**O que faz:** decide *quanto* risco tomar, não onde alocar. Pode viver dentro do Ω reativo (a confiança que sobe e desce conforme a qualidade do sinal).

- **Prêmio de anúncio macro (1.3)** — dimensiona a exposição à vol em dias de anúncio conforme a (in)certeza do poly.
- **Vol proxy (3.3)** — usa a dispersão das probabilidades como termômetro de vol futura.

## 4. Camada de calibração (Ω)
**O que faz:** ajusta a *confiança* nas views, não a carteira. Limpa e pondera o sinal antes de ele virar peso.

- **Correção de favorite-longshot bias** — limpa as probabilidades antes de virarem view.
- **Anti-narrativa (3.5)** — filtro de qualidade: detecta mercados "contaminados" e derruba a confiança neles.

## Reserva / especulativa
- **Detector de info privilegiada (3.4)** — gera sinal próprio a partir de movimentos sem catalisador público; mais ousada, fica em reserva.

---

**Atenção:** a **cesta eleitoral (2.4)** é a única que vive nos dois lados — *view* estrutural (camada 1) **ou** pair trade tático (camada 2), dependendo do horizonte.
