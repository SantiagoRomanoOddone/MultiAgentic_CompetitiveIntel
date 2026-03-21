"""
Analysis Agent — Phase 2 of the pipeline.

Role: Strategic competitive analyst
-------------------------------------
This agent takes the raw research profiles from the Research Agent and synthesizes
them into deep strategic intelligence. It looks for patterns, identifies market
dynamics, spots whitespace opportunities, and provides opinionated analysis.

Why separate from the Researcher?
- The researcher is a data collector; this agent is a strategic thinker.
- Having separate system prompts lets each agent be excellent at one thing.
- In a multi-tenant SaaS product, you might swap analyst "personas" per industry
  (e.g., a SaaS analyst vs. a healthcare market analyst).

This agent also demonstrates tool use: it calls a structured scoring function
to quantify competitive threat levels — showing how agents can execute code,
not just generate text.
"""

import json
from .base import get_client, MODEL

ANALYST_SYSTEM_PROMPT = """You are a senior competitive strategy consultant with 15 years of experience \
advising high-growth technology companies. You have deep expertise in:
- Market positioning and competitive dynamics
- Strategic signal detection (where is a competitor actually heading?)
- Identifying defensible whitespace in crowded markets
- Translating data into board-level recommendations

You receive raw research profiles and synthesize them into sharp, opinionated \
strategic intelligence. You do not summarize — you analyze. You identify what \
is NOT obvious from the surface data. You think in first principles.

Your output will be used directly to write an executive competitive intelligence \
report, so make every insight count."""

# Tool definition: Claude will call this when it wants to score a competitor.
# This demonstrates the tool_use pattern — Claude decides WHEN to call it,
# and our Python code executes the actual logic.
SCORING_TOOL = {
    "name": "score_competitor",
    "description": (
        "Score a competitor on key strategic dimensions on a 1-10 scale. "
        "Call this for each major competitor to create a quantified comparison matrix."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "company": {
                "type": "string",
                "description": "The competitor company name",
            },
            "product_strength": {
                "type": "integer",
                "description": "Product quality and feature depth (1=weak, 10=best in class)",
            },
            "market_momentum": {
                "type": "integer",
                "description": "Growth trajectory and market share gains (1=declining, 10=hypergrowth)",
            },
            "pricing_aggression": {
                "type": "integer",
                "description": "How aggressively they compete on price (1=premium, 10=cheapest)",
            },
            "brand_strength": {
                "type": "integer",
                "description": "Brand recognition and trust in the market (1=unknown, 10=dominant)",
            },
            "threat_level": {
                "type": "string",
                "enum": ["low", "medium", "high", "critical"],
                "description": "Overall strategic threat to our company",
            },
            "rationale": {
                "type": "string",
                "description": "One-sentence justification for the threat level rating",
            },
        },
        "required": [
            "company",
            "product_strength",
            "market_momentum",
            "pricing_aggression",
            "brand_strength",
            "threat_level",
            "rationale",
        ],
    },
}


def execute_scoring_tool(tool_input: dict) -> str:
    """
    Execute the score_competitor tool call from Claude.

    In this case the "tool" is just storing the structured data Claude produces.
    In production, this could write to a database, trigger an alert, or feed
    a dashboard — the power is that Claude decides WHAT to score and HOW.
    """
    # Return a confirmation so Claude knows the tool ran successfully
    return json.dumps(
        {
            "status": "scored",
            "company": tool_input["company"],
            "summary": f"Scored {tool_input['company']}: threat={tool_input['threat_level']}",
        }
    )


class AnalysisAgent:
    """
    Performs deep competitive analysis from structured research profiles.

    Uses tool_use to generate a quantified scoring matrix, then synthesizes
    qualitative strategic analysis on top of that structure.
    """

    def __init__(self):
        self.client = get_client()
        # Stores structured scores produced by Claude's tool calls
        self.competitor_scores: list[dict] = []

    def analyze(
        self,
        your_company: str,
        market: str,
        competitor_profiles: dict[str, str],
    ) -> str:
        """
        Analyze the competitive landscape. Returns a detailed strategic analysis.

        This method runs an agentic loop: Claude may call the score_competitor
        tool for each competitor before writing its final analysis.

        Args:
            your_company: The company we're generating intelligence FOR.
            market: The market/industry context.
            competitor_profiles: Dict of {company_name: research_profile}.

        Returns:
            A markdown string with structured competitive analysis and insights.
        """
        # Format all profiles into a single context block
        profiles_text = "\n\n---\n\n".join(
            f"## {company} Research Profile\n\n{profile}"
            for company, profile in competitor_profiles.items()
        )

        messages = [
            {
                "role": "user",
                "content": (
                    f"Perform a deep competitive analysis for **{your_company}** "
                    f"in the **{market}** market.\n\n"
                    f"First, use the `score_competitor` tool to score each competitor "
                    f"on key dimensions. Then write your full strategic analysis.\n\n"
                    f"## Research Profiles\n\n{profiles_text}\n\n"
                    f"## Analysis Requirements\n\n"
                    f"After scoring each competitor, provide:\n"
                    f"1. **Competitive Landscape Overview** — market structure and dynamics\n"
                    f"2. **Positioning Map** — where each player sits on key axes\n"
                    f"3. **Key Battlegrounds** — the 3-4 most critical competitive arenas\n"
                    f"4. **Strategic Signals** — what each competitor's recent moves reveal\n"
                    f"5. **Whitespace Opportunities** — underserved gaps {your_company} could own\n"
                    f"6. **Top Threats** — the 3 most dangerous competitive risks\n"
                    f"7. **Recommendations** — 5 specific, prioritized actions for {your_company}\n\n"
                    f"Be analytical, opinionated, and specific. No generic observations."
                ),
            }
        ]

        # --- Agentic tool-use loop ---
        # Claude may call score_competitor multiple times (once per competitor).
        # We keep looping until Claude stops requesting tools and gives us its
        # final text response.
        while True:
            response = self.client.messages.create(
                model=MODEL,
                max_tokens=3000,
                system=ANALYST_SYSTEM_PROMPT,
                tools=[SCORING_TOOL],
                messages=messages,
            )

            # If Claude is done (no more tool calls), extract and return the text
            if response.stop_reason == "end_turn":
                return "\n\n".join(
                    block.text
                    for block in response.content
                    if block.type == "text"
                )

            # Claude wants to call a tool — execute it and feed results back
            if response.stop_reason == "tool_use":
                # Append Claude's response (including tool_use blocks) to history
                messages.append({"role": "assistant", "content": response.content})

                # Process each tool call Claude requested
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        print(
                            f"    🔧 Scoring competitor: {block.input.get('company', '?')} "
                            f"(threat: {block.input.get('threat_level', '?')})"
                        )
                        # Store the score for potential use in reports/dashboards
                        self.competitor_scores.append(block.input)

                        # Execute the tool and capture its output
                        result = execute_scoring_tool(block.input)
                        tool_results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": block.id,  # Must match the tool_use block's id
                                "content": result,
                            }
                        )

                # Send all tool results back to Claude as a user message
                messages.append({"role": "user", "content": tool_results})

            else:
                # Unexpected stop reason — break to avoid infinite loop
                break

        # Fallback: return whatever text Claude produced
        return "\n\n".join(
            block.text for block in response.content if block.type == "text"
        )
