"""
Research Agent — Phase 1 of the pipeline.

Role: Information gathering specialist
--------------------------------------
This agent is responsible for creating detailed, structured profiles of each
competitor. It focuses on breadth and factual accuracy, capturing everything
strategically relevant: business model, products, pricing, strengths, weaknesses,
and recent signals.

Why a dedicated agent for this?
- Separating research from analysis keeps each agent focused on one job.
- The researcher is "just the facts"; the analyst does the interpretation.
- In production, this agent would also use web search tools to pull live data.
"""

from .base import get_client, MODEL

# The system prompt shapes how Claude behaves throughout the entire conversation.
# A well-written system prompt is the most important part of any agent.
RESEARCHER_SYSTEM_PROMPT = """You are an expert competitive intelligence researcher with deep knowledge \
of technology markets, business strategy, and company histories.

Your job is to produce detailed, accurate research profiles for companies based \
on your knowledge. These profiles will be consumed by a strategic analyst, so \
prioritize information that is strategically relevant.

For each company, cover:
1. Company snapshot (founded, HQ, size, total funding, key investors)
2. Core products/services and primary value proposition
3. Target customer segments (who pays them, and why)
4. Pricing model and approximate price points (if publicly known)
5. Key differentiators and competitive strengths
6. Known weaknesses, limitations, or customer complaints
7. Recent developments, pivots, or strategic moves
8. Go-to-market approach (sales-led, product-led, channel, etc.)

Be specific and factual. Use concise markdown formatting."""


class ResearchAgent:
    """
    Gathers structured research profiles for each company in the competitive set.

    In a production system, this agent would use tool_use to call live data
    sources: web search APIs, Crunchbase, LinkedIn job postings, pricing pages,
    and review sites like G2 or Capterra. For this prototype, it draws on
    Claude's broad knowledge of publicly known company information.
    """

    def __init__(self):
        self.client = get_client()

    def research_company(self, company_name: str, market: str) -> str:
        """
        Research a single company and return a structured markdown profile.

        Args:
            company_name: The company to research (e.g., "Salesforce")
            market: Market context to focus the research (e.g., "CRM software")

        Returns:
            A structured markdown string with the company's competitive profile.
        """
        response = self.client.messages.create(
            model=MODEL,
            max_tokens=1500,
            system=RESEARCHER_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Create a competitive intelligence research profile for:\n\n"
                        f"**Company**: {company_name}\n"
                        f"**Market Context**: {market}\n\n"
                        f"Produce a thorough, structured profile. Focus on information "
                        f"a strategic analyst would find most valuable for competitive "
                        f"positioning decisions."
                    ),
                }
            ],
        )
        return response.content[0].text

    def research_all(self, companies: list[str], market: str) -> dict[str, str]:
        """
        Research a list of companies and return a dict of {company: profile}.

        In production, this would fan out across companies concurrently using
        asyncio.gather() to reduce total latency. Sequential for simplicity here.
        """
        profiles: dict[str, str] = {}
        for company in companies:
            print(f"    📊 Researching {company}...")
            profiles[company] = self.research_company(company, market)
        return profiles
