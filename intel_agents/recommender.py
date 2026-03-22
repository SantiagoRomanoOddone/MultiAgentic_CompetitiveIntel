"""
RecommenderAgent
================
Given a scored alert, recommends the appropriate action and drafts
a short message for the brand manager.

Actions:
  reprice                 Adjust your SRP or negotiate with the chain
  notify_account_manager  Flag to the chain account manager immediately
  escalate                Escalate to commercial director / leadership
  monitor                 Log and watch — no immediate action needed
"""

import asyncio
import json

from agent_framework import Agent

from intel_agents.base import get_client
from intel_agents.response_utils import extract_text
from models import ScoredAlert, ActionRecommendation


_INSTRUCTIONS = (
    "You are a brand strategy advisor for CPG companies in Argentina. "
    "Given a scored price alert, recommend the right action and write a short message "
    "for the brand manager — direct, specific, no fluff (2-3 sentences max). "
    "Actions: reprice / notify_account_manager / escalate / monitor. "
    "Respond ONLY with valid JSON: "
    '{"action": "<action>", "message": "<message text>"}'
)


class RecommenderAgent:
    def __init__(self):
        self._agent = Agent(get_client(), _INSTRUCTIONS)

    def run(self, alert: ScoredAlert) -> ActionRecommendation:
        change_str = (
            f"{alert.price_change_pct:+.1f}% vs previous"
            if alert.price_change_pct is not None
            else "no prior price on record"
        )
        response = asyncio.run(
            self._agent.run(
                f"Product: {alert.product_name} ({alert.brand})\n"
                f"Chain: {alert.chain} | City: {alert.city} | Date: {alert.date}\n"
                f"Urgency: {alert.urgency_score}/10 | Type: {alert.alert_type}\n"
                f"Price: ${alert.list_price:.0f} ({change_str})"
                + (f" | Promo: ${alert.promo_price:.0f}" if alert.is_on_promo else "")
                + f"\nReasoning: {alert.reasoning}\n"
                f"Context:\n{alert.context}"
            )
        )
        data = json.loads(extract_text(response))
        return ActionRecommendation(
            **{**alert.__dict__, "action": data["action"], "message": data["message"]}
        )
