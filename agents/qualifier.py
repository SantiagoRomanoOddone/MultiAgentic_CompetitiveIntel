from .base import BaseAgent
from models import ResearchedLead, QualifiedLead


SYSTEM = """You are a B2B lead qualification specialist.
Score leads based on their seniority, decision-making power, and fit for a sales automation product.

Scoring:
  8–10 → hot   (decision maker, clear pain point, high urgency)
  5–7  → warm  (influencer or partial fit)
  1–4  → cold  (low seniority or poor fit)

Respond ONLY with valid JSON:
{"score": <int 1-10>, "category": "<hot|warm|cold>", "reasoning": "<one sentence>"}"""


class QualifierAgent(BaseAgent):
    def run(self, lead: ResearchedLead) -> QualifiedLead:
        data = self._call(
            system=SYSTEM,
            user=(
                f"Lead: {lead.name}, {lead.title} at {lead.company} ({lead.industry})\n"
                f"Research:\n{lead.research}"
            ),
        )
        return QualifiedLead(
            **{
                **lead.__dict__,
                "score": int(data["score"]),
                "category": data["category"],
                "reasoning": data["reasoning"],
            }
        )
