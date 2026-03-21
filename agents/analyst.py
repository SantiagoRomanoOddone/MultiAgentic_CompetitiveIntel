import json
from .base import get_client, MODEL

SYSTEM_PROMPT = """You are a senior competitive strategy consultant.
You receive raw research profiles and synthesize them into sharp, opinionated strategic intelligence.
You do not summarize — you analyze. Identify what is NOT obvious from the surface data."""

SCORING_TOOL = {
    "type": "function",
    "function": {
        "name": "score_competitor",
        "description": "Score a competitor on key strategic dimensions (1-10). Call for each competitor.",
        "parameters": {
            "type": "object",
            "properties": {
                "company": {"type": "string"},
                "product_strength": {"type": "integer", "description": "1=weak, 10=best in class"},
                "market_momentum": {"type": "integer", "description": "1=declining, 10=hypergrowth"},
                "pricing_aggression": {"type": "integer", "description": "1=premium, 10=cheapest"},
                "brand_strength": {"type": "integer", "description": "1=unknown, 10=dominant"},
                "threat_level": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
                "rationale": {"type": "string"},
            },
            "required": ["company", "product_strength", "market_momentum", "pricing_aggression", "brand_strength", "threat_level", "rationale"],
        },
    },
}


class AnalysisAgent:
    def __init__(self):
        self.client = get_client()
        self.competitor_scores: list[dict] = []

    def analyze(self, your_company: str, market: str, competitor_profiles: dict[str, str]) -> str:
        profiles_text = "\n\n---\n\n".join(
            f"## {company}\n\n{profile}" for company, profile in competitor_profiles.items()
        )

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Perform a deep competitive analysis for **{your_company}** in **{market}**.\n\n"
                    f"First, use `score_competitor` for each competitor. Then write your full analysis covering:\n"
                    f"1. Competitive Landscape Overview\n"
                    f"2. Positioning Map\n"
                    f"3. Key Battlegrounds\n"
                    f"4. Strategic Signals\n"
                    f"5. Whitespace Opportunities\n"
                    f"6. Top Threats\n"
                    f"7. Recommendations\n\n"
                    f"## Research Profiles\n\n{profiles_text}"
                ),
            },
        ]

        while True:
            response = self.client.chat.completions.create(
                model=MODEL,
                max_tokens=3000,
                messages=messages,
                tools=[SCORING_TOOL],
                tool_choice="auto",
            )

            choice = response.choices[0]

            if choice.finish_reason == "stop":
                return choice.message.content

            if choice.finish_reason == "tool_calls":
                messages.append(choice.message)

                for call in choice.message.tool_calls:
                    args = json.loads(call.function.arguments)
                    print(f"    🔧 Scoring: {args.get('company')} (threat: {args.get('threat_level')})")
                    self.competitor_scores.append(args)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": json.dumps({"status": "scored", "company": args.get("company")}),
                    })
            else:
                break

        return choice.message.content or ""
