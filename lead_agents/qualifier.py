from pydantic import BaseModel
from agents import Agent, Runner
from typing import Literal

import lead_agents.base  # noqa: F401 — triggers Azure OpenAI setup
from lead_agents.base import MODEL
from models import ResearchedLead, QualifiedLead


class _Output(BaseModel):
    score: int
    category: Literal["hot", "warm", "cold"]
    reasoning: str


_agent = Agent(
    name="Qualifier",
    instructions=(
        "You are a B2B lead qualification specialist. "
        "Score leads based on seniority, decision-making power, and fit for a sales automation product.\n"
        "Scoring: 8–10 = hot (decision maker, clear pain point), "
        "5–7 = warm (influencer or partial fit), 1–4 = cold (low seniority or poor fit). "
        "Return score (int), category (hot|warm|cold), and a one-sentence reasoning."
    ),
    output_type=_Output,
    model=MODEL,
)


class QualifierAgent:
    def run(self, lead: ResearchedLead) -> QualifiedLead:
        result = Runner.run_sync(
            _agent,
            f"Lead: {lead.name}, {lead.title} at {lead.company} ({lead.industry})\n"
            f"Research:\n{lead.research}",
        )
        out = result.final_output
        return QualifiedLead(
            **{**lead.__dict__, "score": out.score, "category": out.category, "reasoning": out.reasoning}
        )
