from pydantic import BaseModel
from agents import Agent, Runner

import lead_agents.base  # noqa: F401 — triggers Azure OpenAI setup
from lead_agents.base import MODEL
from models import Lead, ResearchedLead


class _Output(BaseModel):
    research: str


_agent = Agent(
    name="Researcher",
    instructions=(
        "You are a B2B lead researcher. "
        "Given a lead's name, title, company, and industry, write a concise research brief. "
        "Cover: what the company does, their likely pain points, and why this lead is relevant. "
        "Return 3–4 bullet points."
    ),
    output_type=_Output,
    model=MODEL,
)


class ResearcherAgent:
    def run(self, lead: Lead) -> ResearchedLead:
        result = Runner.run_sync(
            _agent,
            f"{lead.name} — {lead.title} at {lead.company} ({lead.industry})",
        )
        return ResearchedLead(**{**lead.__dict__, "research": result.final_output.research})
