import asyncio
import json

from agent_framework import Agent

from lead_agents.base import get_client
from models import QualifiedLead, OutreachDraft


_INSTRUCTIONS = (
    "You are a B2B outreach specialist. "
    "Write a short, personalized cold email based on the lead's role and research context. "
    "Be concise (3–4 sentences + CTA), specific, and avoid generic language. "
    "Respond ONLY with valid JSON: "
    '{"subject": "<email subject>", "body": "<email body — plain text, no markdown>"}'
)


class OutreachAgent:
    def __init__(self):
        self._agent = Agent(get_client(), _INSTRUCTIONS)

    def run(self, lead: QualifiedLead) -> OutreachDraft:
        response = asyncio.run(
            self._agent.run(
                f"Lead: {lead.name}, {lead.title} at {lead.company} ({lead.industry})\n"
                f"Score: {lead.score}/10 ({lead.category})\n"
                f"Research:\n{lead.research}"
            )
        )
        data = json.loads(response.text)
        return OutreachDraft(**{**lead.__dict__, "subject": data["subject"], "body": data["body"]})
