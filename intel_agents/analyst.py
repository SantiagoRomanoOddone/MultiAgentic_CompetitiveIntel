"""
AnalystAgent
============
Scores the business urgency of a price event and classifies its alert type.

Urgency scale (1–10):
  8–10  Urgent — immediate action likely needed
  5–7   Monitor — meaningful movement, worth reviewing
  1–4   Routine — minor fluctuation, low business impact

Alert types:
  price_increase     Own product price rose (pass-through of cost increase?)
  price_drop         Own product price fell below SRP (chain discounting unilaterally?)
  promotion_start    Active promo detected (promo_price < list_price)
  competitor_move    Competitor brand moved significantly in same category
  srp_violation      Price deviates materially from suggested retail price
"""

import asyncio
import json

from agent_framework import Agent

from intel_agents.base import get_client
from intel_agents.response_utils import extract_text
from models import AnalyzedEvent, ScoredAlert


_INSTRUCTIONS = (
    "You are a brand management analyst for CPG companies in Argentina. "
    "Evaluate price events and score their business urgency for a brand manager. "
    "Urgency 1-10: 8-10 = urgent action needed (large competitor drop, SRP violation, unilateral promo), "
    "5-7 = monitor closely (moderate change, routine promo), 1-4 = low impact (minor fluctuation). "
    "Alert types: price_increase / price_drop / promotion_start / competitor_move / srp_violation. "
    "Respond ONLY with valid JSON: "
    '{"urgency_score": <int 1-10>, "alert_type": "<type>", "reasoning": "<one sentence>"}'
)


class AnalystAgent:
    def __init__(self):
        self._agent = Agent(get_client(), _INSTRUCTIONS)

    def run(self, event: AnalyzedEvent) -> ScoredAlert:
        change_str = (
            f"{event.price_change_pct:+.1f}% vs previous"
            if event.price_change_pct is not None
            else "no prior price"
        )
        promo_str = (
            f"${event.promo_price:.0f} promo active"
            if event.is_on_promo
            else "no promotion"
        )
        response = asyncio.run(
            self._agent.run(
                f"Product: {event.product_name} ({event.brand})\n"
                f"Chain: {event.chain} | City: {event.city} | Date: {event.date}\n"
                f"Price: ${event.list_price:.0f} ({change_str}) | {promo_str}\n"
                f"Context:\n{event.context}"
            )
        )
        raw = extract_text(response)
        if not raw:
            raise ValueError(f"Analyst got empty response: {response!r}")
        data = json.loads(raw)
        return ScoredAlert(
            **{
                **event.__dict__,
                "urgency_score": int(data["urgency_score"]),
                "alert_type": data["alert_type"],
                "reasoning": data["reasoning"],
            }
        )
