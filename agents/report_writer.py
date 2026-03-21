"""
Report Writer Agent — Final phase of the pipeline.

Role: Executive communication specialist
-----------------------------------------
This agent takes all the outputs from the previous agents (research profiles,
strategic analysis, competitive signals) and compiles them into a polished,
executive-ready report.

Key design decisions:
- Uses STREAMING: the report is long, and streaming shows progress in real-time
  rather than making the user wait 30+ seconds for a single response.
- Writes for a C-suite audience: direct, decisive, no corporate jargon.
- The report format is opinionated: "so what?" comes before "what happened?"
- Includes both narrative sections and scannable bullet points.

In a production SaaS product, this agent would also:
- Output to PDF, DOCX, or a custom web format
- Personalize tone based on the user's industry/preferences
- Add company logos, charts, and formatted tables
- Send the report via email or Slack webhook
"""

from datetime import datetime
from rich.console import Console
from rich.markdown import Markdown

from .base import get_client, MODEL

WRITER_SYSTEM_PROMPT = """You are a world-class business writer specializing in competitive intelligence \
reports for Fortune 500 executives and high-growth startup CEOs.

Your reports are famous for:
- **Directness**: You lead with the insight, not the background
- **Specificity**: Every claim is tied to evidence; no vague generalizations
- **Opinionated takes**: You tell readers what to THINK, not just what to KNOW
- **Scannability**: Executives read in 5 minutes; your structure enables that
- **Actionability**: Every section ends with clear implications or next steps

You write in clean, professional Markdown. Your voice is confident, analytical, \
and slightly urgent — because competitive intelligence without urgency is just trivia."""


class ReportWriterAgent:
    """
    Compiles all agent outputs into a polished executive competitive intelligence report.

    Uses streaming to display the report in real-time as it's generated,
    then returns the complete text for saving to disk.
    """

    def __init__(self):
        self.client = get_client()
        self.console = Console()  # Rich console for formatted terminal output

    def write_report(
        self,
        your_company: str,
        market: str,
        competitors: list[str],
        competitor_profiles: dict[str, str],
        analysis: str,
        signals: str,
        competitor_scores: list[dict],
    ) -> str:
        """
        Generate the final executive report using streaming.

        Args:
            your_company: Company the report is written FOR.
            market: The market/industry context.
            competitors: List of competitor names (for the header).
            competitor_profiles: Raw research profiles.
            analysis: Strategic analysis from AnalysisAgent.
            signals: Signal detection output from SignalDetectorAgent.
            competitor_scores: Structured scores from the analyst's tool calls.

        Returns:
            The full report as a markdown string.
        """
        # Format the scores table if we have structured data from tool calls
        scores_section = ""
        if competitor_scores:
            scores_section = "\n## Competitor Score Matrix (from analysis)\n"
            scores_section += "| Company | Product | Momentum | Pricing | Brand | Threat |\n"
            scores_section += "|---------|---------|----------|---------|-------|--------|\n"
            for s in competitor_scores:
                scores_section += (
                    f"| {s.get('company', '?')} "
                    f"| {s.get('product_strength', '?')}/10 "
                    f"| {s.get('market_momentum', '?')}/10 "
                    f"| {s.get('pricing_aggression', '?')}/10 "
                    f"| {s.get('brand_strength', '?')}/10 "
                    f"| {s.get('threat_level', '?').upper()} |\n"
                )

        # Condense profiles for context (the writer needs key facts, not full profiles)
        profiles_summary = "\n".join(
            f"- **{company}**: {profile[:300].strip()}..."
            for company, profile in competitor_profiles.items()
        )

        full_report = ""

        print("\n  ✍️  Streaming report to console...\n")
        print("─" * 70)

        # Use streaming so the user sees output in real-time
        with self.client.messages.stream(
            model=MODEL,
            max_tokens=4000,
            system=WRITER_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Write a complete competitive intelligence report for "
                        f"**{your_company}** dated {datetime.now().strftime('%B %d, %Y')}.\n\n"
                        f"**Market**: {market}\n"
                        f"**Competitors Analyzed**: {', '.join(competitors)}\n\n"
                        f"## Strategic Analysis (primary source)\n{analysis}\n\n"
                        f"## Strategic Signals\n{signals}\n\n"
                        f"{scores_section}\n"
                        f"## Competitor Summaries (reference)\n{profiles_summary}\n\n"
                        f"## Report Format\n\n"
                        f"Write a professional Markdown report with exactly these sections:\n\n"
                        f"1. **# Competitive Intelligence Report: {market.title()}**\n"
                        f"   - Subtitle, date, prepared for {your_company}\n\n"
                        f"2. **## Executive Summary** (5 bullet points MAX — the 5 things "
                        f"   an executive must know)\n\n"
                        f"3. **## Market Landscape** (150 words: structure, dynamics, "
                        f"   maturity stage)\n\n"
                        f"4. **## Competitor Profiles** (one subsection per competitor: "
                        f"   positioning, strengths, weaknesses, threat rating)\n\n"
                        f"5. **## Competitive Dynamics** (positioning map description, "
                        f"   key battlegrounds, who's winning and why)\n\n"
                        f"6. **## Signals & Early Warnings** (incorporate the signal analysis, "
                        f"   formatted as alert cards)\n\n"
                        f"7. **## Strategic Recommendations for {your_company}** "
                        f"   (5 recommendations, prioritized, each with: what, why, by when)\n\n"
                        f"8. **## Monitoring Dashboard** (what to watch weekly/monthly, "
                        f"   key metrics and triggers)\n\n"
                        f"Make it executive-ready. Lead with insights. Be opinionated. "
                        f"Every section should make the reader smarter about their competitive position."
                    ),
                }
            ],
        ) as stream:
            for text in stream.text_stream:
                full_report += text
                print(text, end="", flush=True)

        print("\n" + "─" * 70)

        return full_report
