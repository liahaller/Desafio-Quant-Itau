"""Separação organizacional do dataset Polymarket Fed/FOMC (passo de preparação).

Divide data/polymarket_fed_probabilities.parquet (que permanece intocado) em:
- data/polymarket_fed_reunioes.parquet — só mercados de resultado direto de
  reunião do FOMC (padrão "no change / decrease / increase ... after [Mês]
  [Ano] meeting?" e variações de fraseado equivalentes);
- data/polymarket_fed_outros.parquet — todo o resto (Fed Chair, dissidência,
  derivative, sequências, cortes até data, etc.), guardado para uso futuro.

Casos ambíguos (ex.: "Fed rate cut by [Mês] meeting?") NÃO são decididos aqui:
vão temporariamente para "outros", sinalizados no log, aguardando decisão
humana.

Gera também data/log_separacao_mercados.txt com a classificação completa.

Uso:
    python src/data_pipeline/separar_mercados_fed.py
"""

import re
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
INPUT_PATH = REPO_ROOT / "data" / "polymarket_fed_probabilities.parquet"
REUNIOES_PATH = REPO_ROOT / "data" / "polymarket_fed_reunioes.parquet"
OUTROS_PATH = REPO_ROOT / "data" / "polymarket_fed_outros.parquet"
LOG_PATH = REPO_ROOT / "data" / "log_separacao_mercados.txt"

# Núcleo de reunião: resultado direto de uma reunião do FOMC.
# Ex.: "No change in Fed interest rates after December 2024 meeting?"
#      "Fed decreases interest rates by 25 bps after July 2025 meeting?"
#      "Will the Fed increase interest rates by 25+ bps after the March 2026 meeting?"
RE_NO_CHANGE = re.compile(
    r"^(will there be )?no change in fed interest rates after (the )?[\w ]+ meeting\?$"
)
RE_CHANGE = re.compile(
    r"^(will the fed |fed )(decreases?|increases?|raises?) interest rates "
    r"by \d+\+? ?bps after (the )?[\w ]+ meeting\?$"
)

# Casos ambíguos — mencionam "meeting" mas não seguem o padrão dos 4 outcomes.
# Não decidir aqui: vão temporariamente para "outros", sinalizados no log.
AMBIGUOUS_PATTERNS = [
    re.compile(r"^fed rate cut by [\w ]+ meeting\?$"),
    re.compile(r"^fed cuts rates by [\w ]+ meeting\?$"),
    re.compile(r"^will the fed change rates to another level after [\w ]+ meeting\?$"),
]


def is_reuniao(question: str) -> bool:
    """True se o mercado é resultado direto de reunião do FOMC (padrão central)."""
    q = question.lower().strip()
    return bool(RE_NO_CHANGE.match(q) or RE_CHANGE.match(q))


def is_ambiguous(question: str) -> bool:
    """True se o mercado menciona reunião mas não segue o padrão dos 4 outcomes."""
    q = question.lower().strip()
    return any(p.match(q) for p in AMBIGUOUS_PATTERNS)


def categorize_other(question: str) -> str:
    """Categoria descritiva (só para o log) dos mercados fora do núcleo."""
    q = question.lower()
    if "fed derivative" in q or "odds >" in q or "favored" in q:
        return "Derivative / odds sobre probabilidades"
    if "fomc decision result in" in q:
        return "Dissidência de votos (combo resultado x dissidências)"
    if "dissent" in q:
        return "Dissidência de votos"
    if re.search(r"cut.pause|pause.cut|cut.cut|pause.pause|decide differently", q):
        return "Sequências multi-reunião"
    if re.search(r"rate cuts? happen in", q) or re.search(r"cut interest rates \d+\+? ?time", q):
        return "Contagem anual de cortes"
    if any(
        k in q
        for k in (
            "fed chair",
            "chair of the federal reserve",
            "powell",
            "warsh",
            "lisa cook",
            "governor",
            "nominate",
        )
    ):
        return "Fed Chair / pessoas específicas"
    if re.match(r"^fed rate cut by ", q):
        return "Corte até data (sem 'meeting' explícito)"
    if "emergency" in q or re.search(r"rate (cut|hike) in \d{4}", q):
        return "Horizonte anual / emergência"
    return "Outros (sem categoria específica)"


def main() -> int:
    df = pd.read_parquet(INPUT_PATH)
    markets = sorted(df["mercado"].unique())

    reunioes = [m for m in markets if is_reuniao(m)]
    ambiguous = [m for m in markets if not is_reuniao(m) and is_ambiguous(m)]
    others = [m for m in markets if not is_reuniao(m) and not is_ambiguous(m)]

    df_reunioes = df[df["mercado"].isin(reunioes)]
    # Ambíguos vão TEMPORARIAMENTE para "outros" (sinalizados no log) até
    # decisão humana — assim reunioes + outros continuam particionando o
    # dataset original sem perda.
    df_outros = df[df["mercado"].isin(others + ambiguous)]

    assert len(df_reunioes) + len(df_outros) == len(df), "partição perdeu linhas"

    df_reunioes.to_parquet(REUNIOES_PATH, index=False)
    df_outros.to_parquet(OUTROS_PATH, index=False)

    by_category: dict[str, list[str]] = {}
    for m in others:
        by_category.setdefault(categorize_other(m), []).append(m)

    lines = []
    lines.append("LOG DE SEPARAÇÃO — mercados Fed/FOMC do Polymarket")
    lines.append("Passo de organização (não é decisão metodológica fechada).")
    lines.append(f"Gerado por: src/data_pipeline/separar_mercados_fed.py")
    lines.append(f"Original (intocado): {INPUT_PATH.name} — {len(df)} linhas, {len(markets)} mercados únicos")
    lines.append("")
    lines.append("=" * 70)
    lines.append("RESUMO")
    lines.append("=" * 70)
    lines.append(f"Mercados únicos no núcleo de reunião ('reunioes'): {len(reunioes)}")
    lines.append(f"Mercados únicos fora do núcleo ('outros'):         {len(others)}")
    lines.append(f"CASOS AMBÍGUOS (temporariamente em 'outros'):      {len(ambiguous)}")
    lines.append(f"Linhas: reunioes={len(df_reunioes)} | outros={len(df_outros)} | original={len(df)}")
    lines.append("")
    lines.append("=" * 70)
    lines.append(f"REUNIOES — {len(reunioes)} mercados (→ {REUNIOES_PATH.name})")
    lines.append("=" * 70)
    for m in reunioes:
        lines.append(f"  {m}")
    lines.append("")
    lines.append("=" * 70)
    lines.append("CASOS AMBÍGUOS — decidir depois")
    lines.append("(mencionam 'meeting' mas não seguem o padrão dos 4 outcomes;")
    lines.append(f" colocados TEMPORARIAMENTE em {OUTROS_PATH.name} — NÃO é decisão)")
    lines.append("=" * 70)
    for m in ambiguous:
        lines.append(f"  {m}")
    lines.append("")
    lines.append("=" * 70)
    lines.append(f"OUTROS — {len(others)} mercados por categoria (→ {OUTROS_PATH.name})")
    lines.append("=" * 70)
    for cat in sorted(by_category):
        lines.append(f"\n[{cat}] — {len(by_category[cat])} mercados")
        for m in by_category[cat]:
            lines.append(f"  {m}")

    LOG_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"reunioes: {len(reunioes)} mercados, {len(df_reunioes)} linhas → {REUNIOES_PATH}")
    print(f"outros:   {len(others)} mercados (+{len(ambiguous)} ambíguos), {len(df_outros)} linhas → {OUTROS_PATH}")
    print(f"log:      {LOG_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
