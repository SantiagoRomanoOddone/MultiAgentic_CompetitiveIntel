"""
Signal Detection Agent — Phase 3 of the pipeline.

Role: Early warning system
---------------------------
This agent scans competitor research and analysis for "signals" — leading
indicators of strategic moves before they become obvious. It's the difference
between reactive intelligence (knowing what happened) and proactive intelligence
(knowing what's about to happen).

Common signals it detects:
- Hiring surges in specific departments → product direction hints
- Pricing changes → competitive pressure or new segment targeting
- Acquisition rumors / partnerships → strategic pivots
- Geographic expansion → market share plays
- Open-source releases → developer ecosystem strategy
- Feature deprecations → product focus shifts

In a production product, this agent would also monitor:
- LinkedIn job postings (via scraping or API)
- App store review sentiment trends
- GitHub commit activity
- Patent filings
- Press releases and SEC filings
"""

from .base import get_client, MODEL

SIGNAL_DETECTOR_SYSTEM_PROMPT = """You are an expert at detecting strategic signals from competitive intelligence data.

A "signal" is a leading indicator — something in the data that hints at where a \
competitor is heading BEFORE it becomes obvious to the market. Signals are more \
valuable than confirmed facts because they give companies time to respond.

You think like a detective: you look for inconsistencies, unexpected moves, \
resource allocation patterns, and what is conspicuously absent from a competitor's \
strategy.

Signal categories to identify:
- 🔴 THREAT signals: moves that could directly hurt your client
- 🟡 WATCH signals: trends worth monitoring but not yet dangerous
- 🟢 OPPORTUNITY signals: competitor weaknesses or gaps you could exploit
- ⚡ URGENT signals: things requiring action in the next 30-60 days

Format your output as structured markdown with clear signal cards."""


class SignalDetectorAgent:
    """
    Identifies strategic signals and early warning indicators from competitive data.

    This agent reads like an intelligence analyst: it looks for the "tells"
    in competitor behavior that most people miss.
    """

    def __init__(self):
        self.client = get_client()

    def detect_signals(
        self,
        your_company: str,
        market: str,
        competitor_profiles: dict[str, str],
        analysis: str,
    ) -> str:
        """
        Scan research and analysis for actionable competitive signals.

        Args:
            your_company: Company we're generating intelligence for.
            market: Market/industry context.
            competitor_profiles: Raw research profiles per competitor.
            analysis: The strategic analysis from the AnalysisAgent.

        Returns:
            Structured markdown with prioritized signals and recommended responses.
        """
        competitors = list(competitor_profiles.keys())

        # Condense profiles to save tokens — we want key facts, not full profiles
        condensed_profiles = "\n\n".join(
            f"### {company}\n{profile[:600]}..."
            for company, profile in competitor_profiles.items()
        )

        response = self.client.messages.create(
            model=MODEL,
            max_tokens=2000,
            system=SIGNAL_DETECTOR_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Analyze competitive data for **{your_company}** in the "
                        f"**{market}** market and identify strategic signals.\n\n"
                        f"**Competitors**: {', '.join(competitors)}\n\n"
                        f"## Competitor Profiles (condensed)\n{condensed_profiles}\n\n"
                        f"## Strategic Analysis\n{analysis}\n\n"
                        f"## Task\n\n"
                        f"Identify 6-10 high-value signals across these categories:\n"
                        f"1. **Immediate Threats** (🔴) — competitor moves that demand a response NOW\n"
                        f"2. **Strategic Watch List** (🟡) — trends to monitor monthly\n"
                        f"3. **Exploitable Opportunities** (🟢) — gaps or weaknesses to capitalize on\n"
                        f"4. **Market Inflection Points** (⚡) — forces reshaping the competitive landscape\n\n"
                        f"For each signal:\n"
                        f"- **What**: Describe the signal clearly\n"
                        f"- **Evidence**: What data points suggest this?\n"
                        f"- **Implication**: What does this mean for {your_company}?\n"
                        f"- **Recommended Action**: 1-2 specific steps to respond\n"
                        f"- **Timeframe**: When should {your_company} act?\n\n"
                        f"Prioritize signals that are non-obvious, actionable, and time-sensitive."
                    ),
                }
            ],
        )

        return response.content[0].text
