#!/usr/bin/env python3
"""
Competitive Intelligence Platform
==================================
A multi-agent AI system that automatically researches competitors,
analyzes market dynamics, detects strategic signals, and generates
executive-ready intelligence reports.

Run interactively:
    python main.py

Run with arguments (no prompts):
    python main.py --company "Notion" \
                   --competitors "Confluence,Coda,Obsidian" \
                   --market "collaborative workspace software"

Run the built-in demo:
    python main.py --demo
"""

import sys
import argparse
import os
from pathlib import Path

from agents.orchestrator import Orchestrator


# ── Demo configuration ──────────────────────────────────────────────────────
# A ready-to-run example that works out of the box.
# Swap these values to analyze any company/market you like.
DEMO_CONFIG = {
    "your_company": "Notion",
    "competitors": ["Confluence", "Coda", "Obsidian"],
    "market": "collaborative workspace and knowledge management software",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="AI-powered competitive intelligence platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--company", type=str, help="Your company name")
    parser.add_argument(
        "--competitors",
        type=str,
        help="Comma-separated competitor names (e.g. 'Salesforce,HubSpot')",
    )
    parser.add_argument("--market", type=str, help="Market or industry context")
    parser.add_argument(
        "--demo",
        action="store_true",
        help=f"Run with demo values ({DEMO_CONFIG['your_company']} vs "
             f"{', '.join(DEMO_CONFIG['competitors'])})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("."),
        help="Directory to save the report (default: current directory)",
    )
    return parser.parse_args()


def get_input_interactive() -> tuple[str, list[str], str]:
    """Prompt the user for inputs interactively."""
    print("\nEnter the details for your competitive analysis.")
    print("(Press Enter to use demo values)\n")

    company = input("  Your company name: ").strip()
    if not company:
        print("\n  Using demo values...\n")
        return (
            DEMO_CONFIG["your_company"],
            DEMO_CONFIG["competitors"],
            DEMO_CONFIG["market"],
        )

    competitors_raw = input("  Competitors (comma-separated): ").strip()
    competitors = [c.strip() for c in competitors_raw.split(",") if c.strip()]

    market = input("  Market / industry: ").strip()

    if not competitors:
        print("\n❌ Please provide at least one competitor name.")
        sys.exit(1)

    if not market:
        market = f"{company}'s market"

    return company, competitors, market


def check_api_key() -> None:
    """Verify the API key is configured before we start making calls."""
    if not os.getenv("OPEN_AI_KEY") or not os.getenv("OPEN_AI_ENDPOINT") or not os.getenv("CHAT_MODEL"):
        print("\n❌ Missing Azure credentials.\n")
        print("   1. Copy .env.example to .env")
        print("   2. Fill in OPEN_AI_ENDPOINT, OPEN_AI_KEY, CHAT_MODEL\n")
        sys.exit(1)


def main() -> None:
    args = parse_args()

    # Verify API key first — fail fast before any user prompts
    check_api_key()

    # Determine input values from args, demo mode, or interactive prompts
    if args.demo:
        your_company = DEMO_CONFIG["your_company"]
        competitors = DEMO_CONFIG["competitors"]
        market = DEMO_CONFIG["market"]
        print(f"\n🎯 Demo mode: analyzing {your_company} vs {', '.join(competitors)}")
    elif args.company and args.competitors:
        your_company = args.company
        competitors = [c.strip() for c in args.competitors.split(",") if c.strip()]
        market = args.market or f"{your_company}'s market"
    else:
        your_company, competitors, market = get_input_interactive()

    # Validate inputs
    if not competitors:
        print("❌ Please provide at least one competitor.")
        sys.exit(1)

    # Ensure output directory exists
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Run the multi-agent pipeline
    orchestrator = Orchestrator()
    try:
        report_path = orchestrator.run(
            your_company=your_company,
            competitors=competitors,
            market=market,
            output_dir=args.output_dir,
        )
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user. Partial report may not be saved.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        raise

    print(f"✨ Open your report: {report_path.resolve()}\n")


if __name__ == "__main__":
    main()
