import json
import anthropic


MODEL = "claude-opus-4-6"


class BaseAgent:
    def __init__(self):
        self.client = anthropic.Anthropic()
        self.model = MODEL

    def _call(self, system: str, user: str, max_tokens: int = 1024) -> dict:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        text = response.content[0].text.strip()
        # Strip markdown code fences if present
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        return json.loads(text)
