import asyncio
import json

from agent_framework import Agent

from lead_agents.base import get_client
from lead_agents.response_utils import extract_text
from models import ResearchedLead, QualifiedLead


_INSTRUCTIONS = (
    "You are a B2B lead qualification specialist. "
    "Score leads based on seniority, decision-making power, and fit for a sales automation product. "
    "Scoring: 8–10 = hot (decision maker, clear pain point), "
    "5–7 = warm (influencer or partial fit), 1–4 = cold (low seniority or poor fit). "
    "Respond ONLY with valid JSON: "
    '{"score": <int 1-10>, "category": "<hot|warm|cold>", "reasoning": "<one sentence>"}'
)


class QualifierAgent:
    def __init__(self):
        self._agent = Agent(get_client(), _INSTRUCTIONS)

    def run(self, lead: ResearchedLead) -> QualifiedLead:
        response = asyncio.run(
            self._agent.run(
                f"Lead: {lead.name}, {lead.title} at {lead.company} ({lead.industry})\n"
                f"Research:\n{lead.research}"
            )
        )
        raw = extract_text(response)
        if not raw:
            raise ValueError(f"Qualifier got empty response. Response object: {response!r}")
        data = json.loads(raw)
        return QualifiedLead(
            **{
                **lead.__dict__,
                "score": int(data["score"]),
                "category": data["category"],
                "reasoning": data["reasoning"],
            }
        )
