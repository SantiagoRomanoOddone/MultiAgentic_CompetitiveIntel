#!/usr/bin/env python3
"""
Price Intelligence Pipeline
===========================
Multi-agent system that ingests price events from the Argentine SEPA dataset,
enriches them with competitive context, scores business urgency, applies a
control layer (auto-skip / escalate), recommends actions, and collects human
feedback — which feeds a lightweight RL loop to tune thresholds over time.

Data source: SEPA (Sistema Electrónico de Publicidad de Precios Argentinos)
             12M daily price records from 3,600 supermarket branches.
             Public dataset — datos.produccion.gob.ar/dataset/sepa-precios

Usage:
    python main.py                            # runs sample_events.json
    python main.py --events my_events.json    # custom events file
"""

import argparse
import json
import os
import sys
from pathlib import Path

from models import PriceEvent
from pipeline import Pipeline


def load_events(path: Path) -> list[PriceEvent]:
    data = json.loads(path.read_text())
    return [PriceEvent(**item) for item in data]


def check_env() -> None:
    missing = [v for v in ("OPEN_AI_ENDPOINT", "OPEN_AI_KEY", "CHAT_MODEL") if not os.getenv(v)]
    if missing:
        print(f"\nError: missing environment variables: {', '.join(missing)}")
        print("  Copy .env.example to .env and fill in the values.")
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Price Intelligence Pipeline")
    parser.add_argument(
        "--events",
        type=Path,
        default=Path("sample_events.json"),
        help="JSON file with price event objects (default: sample_events.json)",
    )
    args = parser.parse_args()

    check_env()

    if not args.events.exists():
        print(f"\nError: events file not found — {args.events}")
        sys.exit(1)

    events = load_events(args.events)

    print(f"\n{'═' * 60}")
    print(f"  Price Intelligence Pipeline")
    print(f"  {len(events)} price events loaded from SEPA")
    print(f"{'═' * 60}")

    try:
        approved = Pipeline().run(events)
    except KeyboardInterrupt:
        print("\n\nInterrupted.")
        sys.exit(0)

    print(f"\n{'═' * 60}")
    print(f"  Result: {len(approved)}/{len(events)} alerts approved")
    for rec in approved:
        print(f"    • {rec.product_name} @ {rec.chain}  ({rec.urgency_score}/10  → {rec.action})")
    print(f"{'═' * 60}\n")


if __name__ == "__main__":
    main()
