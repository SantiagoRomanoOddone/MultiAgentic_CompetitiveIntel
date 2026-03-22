import asyncio
import json

from agent_framework import Agent

from lead_agents.base import get_client
from models import Lead, ResearchedLead


_INSTRUCTIONS = (
    "You are a B2B lead researcher. "
    "Given a lead's name, title, company, and industry, write a concise research brief. "
    "Cover: what the company does, their likely pain points, and why this lead is relevant. "
    "Respond ONLY with valid JSON: "
    '{"research": "• point 1\\n• point 2\\n• point 3"}'
)


class ResearcherAgent:
    def __init__(self):
        self._agent = Agent(get_client(), _INSTRUCTIONS)

    def run(self, lead: Lead) -> ResearchedLead:
        response = asyncio.run(
            self._agent.run(
                f"{lead.name} — {lead.title} at {lead.company} ({lead.industry})"
            )
        )
        data = json.loads(response.text)
        return ResearchedLead(**{**lead.__dict__, "research": data["research"]})
