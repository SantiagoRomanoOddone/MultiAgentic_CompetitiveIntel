from .base import BaseAgent
from models import Lead, ResearchedLead


SYSTEM = """You are a B2B lead researcher.
Given a lead's name, title, company, and industry, write a concise research brief.
Cover: what the company does, their likely pain points, and why this lead is relevant.

Respond ONLY with valid JSON:
{"research": "• point 1\\n• point 2\\n• point 3"}"""


class ResearcherAgent(BaseAgent):
    def run(self, lead: Lead) -> ResearchedLead:
        data = self._call(
            system=SYSTEM,
            user=f"{lead.name} — {lead.title} at {lead.company} ({lead.industry})",
        )
        return ResearchedLead(**{**lead.__dict__, "research": data["research"]})
