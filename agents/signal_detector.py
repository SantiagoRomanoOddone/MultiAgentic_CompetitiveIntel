from .base import get_client, MODEL

SYSTEM_PROMPT = """You are an expert at detecting strategic signals from competitive intelligence data.
A signal is a leading indicator — something that hints at where a competitor is heading BEFORE it's obvious.

Signal categories:
- 🔴 THREAT: moves that could directly hurt your client
- 🟡 WATCH: trends worth monitoring
- 🟢 OPPORTUNITY: competitor weaknesses to exploit
- ⚡ URGENT: requires action in the next 30-60 days

Format output as structured markdown with clear signal cards."""


class SignalDetectorAgent:
    def __init__(self):
        self.client = get_client()

    def detect_signals(self, your_company: str, market: str, competitor_profiles: dict[str, str], analysis: str) -> str:
        condensed = "\n\n".join(
            f"### {company}\n{profile[:600]}..." for company, profile in competitor_profiles.items()
        )

        response = self.client.chat.completions.create(
            model=MODEL,
            max_tokens=2000,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Identify strategic signals for **{your_company}** in **{market}**.\n\n"
                        f"## Competitor Profiles\n{condensed}\n\n"
                        f"## Strategic Analysis\n{analysis}\n\n"
                        f"Identify 6-10 signals across: Immediate Threats, Watch List, Opportunities, Market Inflection Points.\n"
                        f"For each: what, evidence, implication, recommended action, timeframe."
                    ),
                },
            ],
        )
        return response.choices[0].message.content
