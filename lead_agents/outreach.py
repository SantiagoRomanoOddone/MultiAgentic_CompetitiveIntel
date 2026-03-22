from pydantic import BaseModel
from agents import Agent, Runner

import lead_agents.base  # noqa: F401 — triggers Azure OpenAI setup
from lead_agents.base import MODEL
from models import QualifiedLead, OutreachDraft


class _Output(BaseModel):
    subject: str
    body: str


_agent = Agent(
    name="Outreach",
    instructions=(
        "You are a B2B outreach specialist. "
        "Write a short, personalized cold email based on the lead's role and research context. "
        "Be concise (3–4 sentences + CTA), specific, and avoid generic language. "
        "Return subject and body as plain text (no markdown)."
    ),
    output_type=_Output,
    model=MODEL,
)


class OutreachAgent:
    def run(self, lead: QualifiedLead) -> OutreachDraft:
        result = Runner.run_sync(
            _agent,
            f"Lead: {lead.name}, {lead.title} at {lead.company} ({lead.industry})\n"
            f"Score: {lead.score}/10 ({lead.category})\n"
            f"Research:\n{lead.research}",
        )
        out = result.final_output
        return OutreachDraft(**{**lead.__dict__, "subject": out.subject, "body": out.body})
