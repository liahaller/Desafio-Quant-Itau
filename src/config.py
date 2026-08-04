"""Parâmetros de configuração do v1 (CLAUDE.md §5: nada espalhado no código).

Cada valor aqui é **decisão registrada**, fechada na maratona de 2026-08-04
(ver `LOG.md`, sessão 2) e **marcada para revisão do grupo** — são provisórias,
tomadas pelo Felipe com autorização do grupo para não travar a entrega.

Nada aqui é chute: o que não veio de medição veio de regra derivada do dado.
Onde a origem é uma medição, o arquivo de análise está citado na linha.
"""

from poly_preprocessing import FL_GAMMA_V1, OPEN_BUCKET_SHIFT  # noqa: F401

# --- Universo ---------------------------------------------------------------
# Decisão 1 (fechada em reunião): setores + classes de ativo, EUA, yfinance.
# A ORDEM define o alinhamento de todos os arrays (P, Q, w, Σ).
ASSETS = ("SPY", "TIP", "TLT", "XLE", "XLF", "XLK", "XLP", "XLU", "XLV")
MARKET_ASSET = "SPY"

# --- Rebalanceamento --------------------------------------------------------
# D1: H = 1 dia. Σ e π já são diários (conversão zero), as views de evento
# entregam em 1 dia, e o poly tem 2 pontos/dia — é o mais fino que o dado
# suporta sem lookahead.
H_DIAS = 1

# --- Black-Litterman --------------------------------------------------------
# D7: δ MEDIDO no nosso SPY com DTB3 como taxa livre de risco — excesso médio
# de 10,48% a.a. sobre variância, história inteira (22 anos). Janelas curtas
# dão 3,4 a 4,9, infladas pelo bull recente; 3,0 é o valor conservador.
DELTA = 3.0

# D7: τ = 1/T, T = janela de estimação do Σ. E o Ω tem de vir ancorado em
# diag(P·τΣ·Pᵀ) — assim o valor absoluto de τ SAI da conta e sobra a confiança
# relativa, que é o que o módulo da Lia mede. Ver `omega_fallback`.
SIGMA_JANELA_PREGOES = 504  # 2 anos de pregão
TAU = 1.0 / SIGMA_JANELA_PREGOES

# --- Views ativas no v1 -----------------------------------------------------
# D2/D2b/D2c: as poly-defasadas saíram (2.4 reprovou fora da amostra no
# mercado da Câmara 2026; C tem 27+45 obs; E tem 13 dias; G tem 3). A 3.1 saiu
# porque o sinal que existe é direcional e o P dela é neutro em mercado.
VIEWS_ATIVAS = ("2.2_inflacao", "2.3_fed", "B_trajetoria_fed")

# --- Camada tática ----------------------------------------------------------
# D3: entra redesenhada. A de prêmio só dispara em anúncio INCERTO (a âncora
# de Savor-Wilson é compensação por risco de evento); a de gap de fim de semana
# ficou de fora (D3b: só tem efeito com o sinal invertido).
TATICAS_ATIVAS = ("premio_anuncios", "drift_pos_fomc")
# Limiar de entropia da PMF acima do qual o anúncio conta como incerto.
# None = mediana de janela EXPANSIVA (sem lookahead) — é o default, e é regra,
# não parâmetro. Ver `Dump/analises/Premio_condicional.md`.
ENTROPIA_LIMIAR = None
# D3/2.3: a janela do livro de RF do drift vai até a véspera do FOMC seguinte.
# Os 50 dias da literatura são truncados em 47 de 47 intervalos do calendário.
DRIFT_JANELA_ACOES = 15
DRIFT_JANELA_RF = None  # None = até a véspera do próximo FOMC

# --- Custo de transação -----------------------------------------------------
# D8: 2 bps por lado sobre o giro, com Δw contra o peso DERIVADO (pós-drift do
# dia), não contra o alvo anterior. Premissa conservadora: o spread cotado
# desses 9 ETFs é de 1 a 2 bps CHEIOS (meio-spread 0,5 a 1,0), e o all-in
# medido do SPY em ordem de US$ 25 M é 0,30 bp.
CUSTO_BPS_POR_LADO = 2.0
CUSTO_VARREDURA_BPS = (0.0, 2.0, 5.0, 10.0)
# Parcelas que existem porque os pesos são irrestritos (decisão 8). Zero é
# cenário declarado, não omissão: não há número publicado para estes 9 tickers.
FINANCIAMENTO_SPREAD_BPS_ANO = 0.0
ALUGUEL_BPS_ANO = 0.0

# --- Robustez a reportar ----------------------------------------------------
# D5: sem correção de favorite-longshot no v1 (γ = 1,0), com o resultado
# reportado também nestes γ.
FL_GAMMA_VARREDURA = (1.0, 1.1, 1.25)

PREGOES_POR_ANO = 252
