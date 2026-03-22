from dataclasses import dataclass


@dataclass
class Lead:
    name: str
    company: str
    title: str
    email: str
    industry: str = ""


@dataclass
class ResearchedLead(Lead):
    research: str = ""


@dataclass
class QualifiedLead(ResearchedLead):
    score: int = 0        # 1–10
    category: str = ""    # hot / warm / cold
    reasoning: str = ""


@dataclass
class OutreachDraft(QualifiedLead):
    subject: str = ""
    body: str = ""
