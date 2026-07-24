"""Script de exploração — top mercados Polymarket por volume.

Uso:
    python scripts/explorar_mercados_polymarket.py

Salva: data/polymarket_top_mercados.json
"""

import json
import time
from pathlib import Path

import requests

OUTPUT = Path(__file__).resolve().parents[1] / "data" / "polymarket_top_mercados.json"
GAMMA_URL = "https://gamma-api.polymarket.com"


def fetch_top(n: int = 100) -> list[dict]:
    resp = requests.get(
        f"{GAMMA_URL}/markets",
        params={"order": "volume", "ascending": "false", "limit": n, "closed": "false"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def main():
    print("Buscando top 100 mercados por volume...")
    markets = fetch_top(100)
    print(f"Retornados: {len(markets)}")

    resumo = []
    for i, m in enumerate(markets, 1):
        vol = float(m.get("volume") or 0)
        entry = {
            "rank": i,
            "volume": vol,
            "question": m.get("question", m.get("slug", "")),
            "slug": m.get("slug", ""),
            "category": m.get("category", ""),
            "tags": [t.get("label", "") for t in (m.get("tags") or [])],
            "end_date": m.get("endDate", ""),
            "condition_id": m.get("conditionId", ""),
        }
        resumo.append(entry)
        print(f"{i:3d}. vol=${vol:>12,.0f}  {entry['question'][:80]}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(resumo, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSalvo em: {OUTPUT}")


if __name__ == "__main__":
    main()
