"""Gera os SVGs do relatório a partir das séries medidas.

Nenhum número é digitado à mão: a curva vem de `dados/curva_diaria_regua_nivel1.csv`
(reprodução do backtest de entrega, já versionada) e a dispersão do `c` vem do CSV
da régua. Paleta validada em dark pelo validador do skill de dataviz.

Caminhos derivados do próprio arquivo: roda a partir do repositório, sem depender
do diretório de trabalho `X:` em que o backtest foi remontado.
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# --- parâmetros de identidade -------------------------------------------------
AMBAR = "#C9820C"        # Kairós — validado (OKLCH L 0.60, dark band)
AZUL = "#3D8FC4"         # benchmark SPY — validado, ΔE 21.7 protan vs âmbar
AMBAR_VIVO = "#F5A623"   # acento de identidade; nunca codifica série
TINTA = "#E8EDF2"
TINTA2 = "#9BAEC0"
GRID = "#24384B"
VERMELHO = "#C2544D"     # status: reprovado

BASE = Path(__file__).resolve().parent
DADOS = BASE / "dados"
SAIDA = BASE / "svg"
SAIDA.mkdir(exist_ok=True)

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Segoe UI", "DejaVu Sans"],
    "svg.fonttype": "path",
    "text.color": TINTA,
    "axes.labelcolor": TINTA2,
    "xtick.color": TINTA2,
    "ytick.color": TINTA2,
    "axes.edgecolor": GRID,
    "figure.facecolor": "none",
    "axes.facecolor": "none",
    "savefig.facecolor": "none",
})

pct = FuncFormatter(lambda v, _: f"{v * 100:.0f}%")


def limpar(ax, eixo_y=True):
    """Grid recessivo, sem moldura — as marcas carregam a leitura."""
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    ax.spines["left"].set_color(GRID)
    ax.spines["bottom"].set_color(GRID)
    if eixo_y:
        ax.grid(axis="y", color=GRID, linewidth=0.6, alpha=0.55)
    ax.set_axisbelow(True)
    ax.tick_params(length=0, labelsize=9)


# =============================================================================
# 1. Curva acumulada + drawdown
# =============================================================================
# Entrega com a régua do Ω acoplada no nível 1 (decisão 6q, 13/08/2026).
curva = pd.read_csv(DADOS / "curva_diaria_regua_nivel1.csv",
                    parse_dates=["data"]).set_index("data")

fig, (ax, ax2) = plt.subplots(
    2, 1, figsize=(7.6, 4.0), sharex=True,
    gridspec_kw={"height_ratios": [2.6, 1.0], "hspace": 0.18})

ax.plot(curva.index, curva["acum_spy"], color=AZUL, linewidth=2.0)
ax.plot(curva.index, curva["acum_estrategia"], color=AMBAR, linewidth=2.0)
ax.axhline(0, color=GRID, linewidth=1.0)
ax.yaxis.set_major_formatter(pct)
limpar(ax)

# Rótulos diretos no fim da linha — dispensam caixa de legenda (2 séries).
fim = curva.index[-1]
ax.annotate(f"KAIRÓS  +{curva['acum_estrategia'].iloc[-1] * 100:.1f}%",
            xy=(fim, curva["acum_estrategia"].iloc[-1]),
            xytext=(8, 4), textcoords="offset points",
            color=AMBAR, fontsize=10, fontweight="bold", va="center")
ax.annotate(f"SPY  +{curva['acum_spy'].iloc[-1] * 100:.1f}%",
            xy=(fim, curva["acum_spy"].iloc[-1]),
            xytext=(8, -6), textcoords="offset points",
            color=AZUL, fontsize=10, va="center")
ax.set_ylabel("retorno acumulado, líquido de custo", fontsize=8.5, color=TINTA2)

ax2.fill_between(curva.index, curva["dd_spy"], 0, color=AZUL, alpha=0.30, linewidth=0)
ax2.plot(curva.index, curva["dd_estrategia"], color=AMBAR, linewidth=1.4)
ax2.yaxis.set_major_formatter(pct)
ax2.set_ylabel("drawdown", fontsize=8.5, color=TINTA2)
limpar(ax2)

fig.autofmt_xdate(rotation=0, ha="center")
ax2.tick_params(labelsize=8.5)
fig.subplots_adjust(left=0.09, right=0.80, top=0.97, bottom=0.10)
fig.savefig(SAIDA / "curva.svg", format="svg", transparent=True)
plt.close(fig)
print("curva.svg  ok")


# =============================================================================
# 2. Os quatro ingredientes do Ω — faixa de Spearman por view
# =============================================================================
# ⚠️ SEM CONSUMIDOR desde a reestruturação da página 3 (2026-08-16), junto com o
# `regua.svg` abaixo. A página passou a desenhar o placar em HTML: numa coluna de
# 3,7 in este SVG cairia para ~4,5 pt de tipo, menos da metade da menor fonte do
# relatório. Os dois seguem sendo gerados de propósito — as faixas e a dispersão
# do `c` são as mesmas, e reinserir o gráfico é devolver o `{{PLACEHOLDER}}` ao
# template.
# Faixas medidas na §5 do RELATORIO_omega.md (todas as combinações testadas).
ingredientes = [
    ("Estabilidade\nda distribuição", (-0.40, -0.40), (-0.47, -0.47), "entra"),
    ("Coerência\ndo livro", (-0.18, -0.15), (-0.32, -0.23), "entra"),
    ("Volume\nnegociado", (-0.10, 0.19), (-0.11, 0.14), "vira veto"),
    ("Proximidade\ndo evento", (0.07, 0.22), (0.11, 0.37), "reprovado"),
]

# Achatado (2,9 -> 2,05 in) na reestruturação da página 3: o gráfico divide a
# coluna com o bloco da régua, e o que ele precisa mostrar é a POSIÇÃO das
# faixas em relação ao zero — altura sobrando só empurrava conteúdo para fora.
fig, ax = plt.subplots(figsize=(7.0, 2.05))
alturas = np.arange(len(ingredientes))[::-1]
desloc = 0.17

# A cor segue a VIEW e nunca o veredito — o status vai no rótulo de texto.
for y, (nome, f23, f22, veredito) in zip(alturas, ingredientes):
    for faixa, cor, rotulo in ((f23, AZUL, "2.3 Fed"), (f22, AMBAR, "2.2 CPI")):
        dy = desloc if rotulo == "2.3 Fed" else -desloc
        lo, hi = min(faixa), max(faixa)
        if abs(hi - lo) < 1e-9:                    # ponto: marcador de 8px
            ax.plot([lo], [y + dy], "o", color=cor, markersize=8, zorder=3,
                    label=rotulo if y == alturas[0] else None)
        else:
            ax.plot([lo, hi], [y + dy, y + dy], color=cor, linewidth=5,
                    solid_capstyle="round", zorder=3,
                    label=rotulo if y == alturas[0] else None)

ax.axvline(0, color=TINTA2, linewidth=1.0, alpha=0.7)
ax.set_yticks(alturas)
ax.set_yticklabels([n for n, *_ in ingredientes], fontsize=8.5, color=TINTA)
ax.set_xlim(-0.55, 0.62)
ax.set_xlabel("correlação de Spearman entre confiança e erro futuro da probabilidade",
              fontsize=8.5)
limpar(ax, eixo_y=False)
ax.grid(axis="x", color=GRID, linewidth=0.6, alpha=0.5)

for y, (_, _, _, veredito) in zip(alturas, ingredientes):
    cor = {"entra": AMBAR_VIVO, "vira veto": TINTA2, "reprovado": VERMELHO}[veredito]
    ax.text(0.60, y, veredito.upper(), fontsize=8, color=cor,
            fontweight="bold", va="center", ha="right")

ax.text(-0.53, alturas[0] + 0.80, "← mais negativo = confiança prevê erro menor",
        fontsize=8, color=TINTA2, style="italic")
leg = ax.legend(loc="lower left", bbox_to_anchor=(0.60, 1.00), ncol=2,
                frameon=False, fontsize=8.5, handlelength=1.2,
                columnspacing=1.4, handletextpad=0.5)
for t in leg.get_texts():
    t.set_color(TINTA2)
fig.subplots_adjust(left=0.22, right=0.98, top=0.83, bottom=0.26)
fig.savefig(SAIDA / "ingredientes.svg", format="svg", transparent=True)
plt.close(fig)
print("ingredientes.svg  ok")


# =============================================================================
# 3. Quanto a régua morde, por view
# =============================================================================
reg = pd.read_csv(BASE.parent.parent / "lia" / "c_por_decisao.csv")
ativas = reg[reg["ativa"] & reg["c_nivel1"].notna()]

rotulos = {"2.3_fed": "2.3  Fed", "2.2_inflacao": "2.2  CPI",
           "B_trajetoria_propria": "B  trajetória", "incerteza_anuncio": "15b  incerteza"}
ordem = ["2.3_fed", "2.2_inflacao", "B_trajetoria_propria", "incerteza_anuncio"]

fig, ax = plt.subplots(figsize=(7.0, 2.2))
for i, view in enumerate(ordem):
    s = ativas.loc[ativas["view"] == view, "c_nivel1"]
    y = len(ordem) - 1 - i
    p50, p95 = s.median(), s.quantile(0.95)
    ax.plot([p50, p95], [y, y], color=AMBAR, linewidth=5,
            solid_capstyle="round", alpha=0.55, zorder=2)
    ax.plot([p50], [y], "o", color=AMBAR, markersize=9, zorder=3)
    ax.plot([p95], [y], "o", color=AMBAR_VIVO, markersize=9, zorder=3)
    ax.text(p95 + 0.03, y, f"p95 {p95:.2f}", fontsize=8.5, color=TINTA2, va="center")
    ax.text(p50 - 0.03, y, f"{p50:.2f}", fontsize=8.5, color=TINTA,
            va="center", ha="right", fontweight="bold")

ax.axvline(1.0, color=TINTA2, linewidth=1.0, alpha=0.8)
ax.set_ylim(-0.6, 3.9)
ax.text(1.01, 3.55, "c = 1: confiança do BL clássico",
        fontsize=8, color=TINTA2, style="italic", va="center")
ax.set_yticks(range(len(ordem)))
ax.set_yticklabels([rotulos[v] for v in reversed(ordem)], fontsize=9, color=TINTA)
ax.set_xlim(0.93, 1.85)
ax.set_xlabel("multiplicador de incerteza c (nível 1) — mediana e p95 das decisões ativas",
              fontsize=8.5)
limpar(ax, eixo_y=False)
ax.grid(axis="x", color=GRID, linewidth=0.6, alpha=0.5)
fig.subplots_adjust(left=0.17, right=0.98, top=0.88, bottom=0.26)
fig.savefig(SAIDA / "regua.svg", format="svg", transparent=True)
plt.close(fig)
print("regua.svg  ok")

print()
print("--- números para o texto ---")
print("acum estrategia :", f"{curva['acum_estrategia'].iloc[-1]:.4f}")
print("acum spy        :", f"{curva['acum_spy'].iloc[-1]:.4f}")
print("dd estrategia   :", f"{curva['dd_estrategia'].min():.4f}")
print("dd spy          :", f"{curva['dd_spy'].min():.4f}")
print("dias com view   :", int((curva['n_views'] > 0).sum()), "de", len(curva))
print("dias com tatica :", int((curva['n_taticas'] > 0).sum()))
print("alavancagem med :", f"{curva['alavancagem'].mean():.4f}")
print("c mediano 2.2   :", f"{ativas.loc[ativas['view'] == '2.2_inflacao', 'c_nivel1'].median():.4f}")
print("c mediano 2.3   :", f"{ativas.loc[ativas['view'] == '2.3_fed', 'c_nivel1'].median():.4f}")
print("decisoes vetadas:", int((~reg['ativa']).sum()), "de", len(reg))
