from .base import get_client, MODEL

SYSTEM_PROMPT = """You are an expert competitive intelligence researcher.
For each company, cover:
1. Company snapshot (founded, HQ, size, funding)
2. Core products and value proposition
3. Target customer segments
4. Pricing model and price points
5. Key strengths and differentiators
6. Known weaknesses or complaints
7. Recent developments or strategic moves
8. Go-to-market approach

Be specific and factual. Use concise markdown formatting."""


class ResearchAgent:
    def __init__(self):
        self.client = get_client()

    def research_company(self, company_name: str, market: str) -> str:
        response = self.client.chat.completions.create(
            model=MODEL,
            max_tokens=1500,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Create a competitive intelligence profile for:\n\n"
                        f"**Company**: {company_name}\n"
                        f"**Market**: {market}"
                    ),
                },
            ],
        )
        return response.choices[0].message.content

    def research_all(self, companies: list[str], market: str) -> dict[str, str]:
        profiles: dict[str, str] = {}
        for company in companies:
            print(f"    📊 Researching {company}...")
            profiles[company] = self.research_company(company, market)
        return profiles
