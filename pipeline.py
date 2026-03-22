from lead_agents.researcher import ResearcherAgent
from lead_agents.qualifier import QualifierAgent
from lead_agents.outreach import OutreachAgent
from human_loop import human_review
from models import Lead, OutreachDraft


QUALIFY_THRESHOLD = 5  # Leads below this score are auto-skipped


class Pipeline:
    def __init__(self):
        self.researcher = ResearcherAgent()
        self.qualifier = QualifierAgent()
        self.outreach = OutreachAgent()

    def run(self, leads: list[Lead]) -> list[OutreachDraft]:
        approved = []

        for i, lead in enumerate(leads, 1):
            print(f"\n{'─' * 55}")
            print(f"  Lead {i}/{len(leads)}: {lead.name} @ {lead.company}")
            print(f"{'─' * 55}")

            print("  [RESEARCHER]  Gathering intel...", end=" ", flush=True)
            researched = self.researcher.run(lead)
            print("done")

            print("  [QUALIFIER]   Scoring lead...", end=" ", flush=True)
            qualified = self.qualifier.run(researched)
            category_label = {"hot": "HOT", "warm": "WARM", "cold": "COLD"}.get(
                qualified.category, qualified.category.upper()
            )
            print(f"done  →  {qualified.score}/10 {category_label}")
            print(f"              {qualified.reasoning}")

            if qualified.score < QUALIFY_THRESHOLD:
                print("  → Auto-skipped (score below threshold)")
                continue

            print("  [OUTREACH]    Drafting email...", end=" ", flush=True)
            draft = self.outreach.run(qualified)
            print("done")

            result = human_review(draft)
            if result:
                approved.append(result)

        return approved
