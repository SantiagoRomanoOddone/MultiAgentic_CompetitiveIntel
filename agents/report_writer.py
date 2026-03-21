from datetime import datetime
from rich.console import Console

from .base import get_client, MODEL

SYSTEM_PROMPT = """You are a business writer specializing in competitive intelligence reports for executives.
Lead with insights. Be direct, specific, and opinionated. Write clean professional Markdown."""


class ReportWriterAgent:
    def __init__(self):
        self.client = get_client()
        self.console = Console()

    def write_report(self, your_company: str, market: str, competitors: list[str],
                     competitor_profiles: dict[str, str], analysis: str, signals: str,
                     competitor_scores: list[dict]) -> str:

        scores_section = ""
        if competitor_scores:
            scores_section = "\n## Competitor Score Matrix\n"
            scores_section += "| Company | Product | Momentum | Pricing | Brand | Threat |\n"
            scores_section += "|---------|---------|----------|---------|-------|--------|\n"
            for s in competitor_scores:
                scores_section += (
                    f"| {s.get('company')} | {s.get('product_strength')}/10 "
                    f"| {s.get('market_momentum')}/10 | {s.get('pricing_aggression')}/10 "
                    f"| {s.get('brand_strength')}/10 | {s.get('threat_level', '').upper()} |\n"
                )

        profiles_summary = "\n".join(
            f"- **{company}**: {profile[:300].strip()}..." for company, profile in competitor_profiles.items()
        )

        full_report = ""
        print("\n  ✍️  Streaming report...\n" + "─" * 70)

        stream = self.client.chat.completions.create(
            model=MODEL,
            max_tokens=4000,
            stream=True,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Write a competitive intelligence report for **{your_company}** — {datetime.now().strftime('%B %d, %Y')}.\n"
                        f"**Market**: {market} | **Competitors**: {', '.join(competitors)}\n\n"
                        f"## Strategic Analysis\n{analysis}\n\n"
                        f"## Signals\n{signals}\n\n"
                        f"{scores_section}\n"
                        f"## Competitor Summaries\n{profiles_summary}\n\n"
                        f"Sections: Executive Summary, Market Landscape, Competitor Profiles, "
                        f"Competitive Dynamics, Signals & Early Warnings, Strategic Recommendations, Monitoring Dashboard."
                    ),
                },
            ],
        )

        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                full_report += delta
                print(delta, end="", flush=True)

        print("\n" + "─" * 70)
        return full_report
