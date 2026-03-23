"""
DataFetcherAgent
================
Enriches a raw price event with competitive context.

In production this agent would also call the SEPA API or VTEX endpoints
to pull cross-chain comparisons for the same EAN. For now it reasons
from the event data and its knowledge of the LatAm CPG market.
"""

import asyncio
import json

from agent_framework import Agent

from intel_agents.base import get_client
from intel_agents.response_utils import extract_text
from models import PriceEvent, AnalyzedEvent


_INSTRUCTIONS = (
    "You are a competitive intelligence analyst for CPG brands in Latin America. "
    "Given a price event from the Argentine SEPA dataset, write a concise competitive context. "
    "Cover: what this price movement likely signals, how it compares to category norms in Argentina, "
    "and any relevant competitive dynamics between major chains (Carrefour, DIA, Jumbo, Walmart, Coto). "
    "Be concise — 3 bullet points max. "
    "Respond ONLY with valid JSON: "
    '{"context": "• insight 1\\n• insight 2\\n• insight 3"}'
)


class DataFetcherAgent:
    def __init__(self):
        self._agent = Agent(get_client(), _INSTRUCTIONS)

    def run(self, event: PriceEvent) -> AnalyzedEvent:
        change_str = (
            f"{event.price_change_pct:+.1f}% vs previous price"
            if event.price_change_pct is not None
            else "no prior price on record"
        )
        promo_str = (
            f"promo price ${event.promo_price:.0f} ({((event.list_price - event.promo_price) / event.list_price * 100):.0f}% off)"
            if event.is_on_promo
            else "no active promotion"
        )
        response = asyncio.run(
            self._agent.run(
                f"Product: {event.product_name} (EAN {event.ean})\n"
                f"Brand: {event.brand} | Chain: {event.chain} | City: {event.city}\n"
                f"Date: {event.date}\n"
                f"Current list price: ${event.list_price:.0f} ({change_str})\n"
                f"Promotion: {promo_str}"
            )
        )
        data = json.loads(extract_text(response))
        return AnalyzedEvent(**{**event.__dict__, "context": data["context"]})
