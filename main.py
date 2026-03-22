#!/usr/bin/env python3
"""
Sales Lead Qualification Pipeline
==================================
Multi-agent system that researches, qualifies, and drafts outreach
for B2B sales leads — with human-in-the-loop approval before sending.

Usage:
    python main.py                          # runs sample_leads.json
    python main.py --leads my_leads.json    # custom leads file
"""

import argparse
import json
import os
import sys
from pathlib import Path

from models import Lead
from pipeline import Pipeline


def load_leads(path: Path) -> list[Lead]:
    data = json.loads(path.read_text())
    return [Lead(**item) for item in data]


def check_env() -> None:
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\nError: ANTHROPIC_API_KEY is not set.")
        print("  export ANTHROPIC_API_KEY=sk-ant-...")
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Sales Lead Qualification Pipeline")
    parser.add_argument(
        "--leads",
        type=Path,
        default=Path("sample_leads.json"),
        help="JSON file with lead objects (default: sample_leads.json)",
    )
    args = parser.parse_args()

    check_env()

    if not args.leads.exists():
        print(f"\nError: leads file not found — {args.leads}")
        sys.exit(1)

    leads = load_leads(args.leads)

    print(f"\n{'═' * 55}")
    print(f"  Sales Lead Qualification Pipeline")
    print(f"  {len(leads)} leads loaded")
    print(f"{'═' * 55}")

    try:
        approved = Pipeline().run(leads)
    except KeyboardInterrupt:
        print("\n\nInterrupted.")
        sys.exit(0)

    print(f"\n{'═' * 55}")
    print(f"  Result: {len(approved)}/{len(leads)} leads approved")
    for draft in approved:
        print(f"    • {draft.name} @ {draft.company}  ({draft.score}/10 {draft.category})")
    print(f"{'═' * 55}\n")


if __name__ == "__main__":
    main()
