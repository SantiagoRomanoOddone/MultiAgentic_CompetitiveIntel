from .base import BaseAgent
from models import QualifiedLead, OutreachDraft


SYSTEM = """You are a B2B outreach specialist.
Write a short, personalized cold email based on the lead's role and research.
The email must be concise (3–4 sentences + CTA), specific, and not generic.

Respond ONLY with valid JSON:
{"subject": "<email subject>", "body": "<email body — plain text, no markdown>"}"""


class OutreachAgent(BaseAgent):
    def run(self, lead: QualifiedLead) -> OutreachDraft:
        data = self._call(
            system=SYSTEM,
            user=(
                f"Lead: {lead.name}, {lead.title} at {lead.company} ({lead.industry})\n"
                f"Score: {lead.score}/10 ({lead.category})\n"
                f"Research:\n{lead.research}"
            ),
            max_tokens=512,
        )
        return OutreachDraft(
            **{**lead.__dict__, "subject": data["subject"], "body": data["body"]}
        )
