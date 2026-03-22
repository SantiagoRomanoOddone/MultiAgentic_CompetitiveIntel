# Sales Lead Qualification Pipeline

A multi-agent system that takes raw sales leads and automatically researches, qualifies, and drafts personalized outreach — powered by **Microsoft `agent-framework`** and **Azure OpenAI**.

---

## What it does

Given a list of leads (name, title, company, industry), the pipeline runs 3 AI agents in sequence:

```
[sample_leads.json]
        │
        ▼
  Researcher Agent       # Writes a research brief: what the company does, pain points, relevance
        │
        ▼
  Qualifier Agent        # Scores the lead 1–10 and labels it hot / warm / cold
        │
        ▼
  Outreach Agent         # Drafts a personalized cold email (subject + body)
        │
        ▼
  Human Review (CLI)     # You approve, skip, or edit each lead before final export
        │
        ▼
  [console output / export]
```

---

## Tech stack

| Layer | Library |
|---|---|
| Agent framework | [`agent-framework-core`](https://github.com/microsoft/agent-framework) by Microsoft |
| LLM backend | Azure OpenAI (Chat Completions) via `AzureOpenAIChatClient` |
| Data models | Pydantic (`models.py`) |
| Auth | API key (`OPEN_AI_KEY` in `.env`) |

---

## Quickstart

**Prerequisites:** Python 3.10+, Azure OpenAI deployment

```bash
# 1. Install
pip install agent-framework-core --pre
pip install rich python-dotenv

# 2. Configure
cp .env.example .env
# Fill in your Azure OpenAI values (see below)

# 3. Run
python main.py
```

### `.env` variables

```env
OPEN_AI_ENDPOINT=https://<your-resource>.openai.azure.com
OPEN_AI_KEY=<your-api-key>
CHAT_MODEL=<your-deployment-name>        # e.g. gpt-4o
```

---

## Project structure

```
├── main.py                  # Entry point — runs the full pipeline
├── pipeline.py              # Orchestrates the 3 agents in sequence
├── models.py                # Pydantic models: Lead → ResearchedLead → QualifiedLead → OutreachDraft
├── human_loop.py            # CLI for reviewing and approving leads
├── sample_leads.json        # Example input leads
├── requirements.txt
└── lead_agents/
    ├── base.py              # AzureOpenAIChatClient setup (reads from .env)
    ├── researcher.py        # Researcher Agent
    ├── qualifier.py         # Qualifier Agent
    └── outreach.py          # Outreach Agent
```

---

## Data flow

Each agent receives a Pydantic model and returns an enriched version:

```
Lead
  └─> ResearchedLead   (+ research: str)
        └─> QualifiedLead   (+ score: int, category: hot|warm|cold, reasoning: str)
              └─> OutreachDraft   (+ subject: str, body: str)
```

---

## How agents work

Each agent in `lead_agents/` follows the same pattern:

```python
from agent_framework import Agent
from agent_framework.azure import AzureOpenAIChatClient

client = AzureOpenAIChatClient(endpoint=..., api_key=..., deployment_name=...)
agent = Agent(client, instructions="...")
response = asyncio.run(agent.run(message))
data = json.loads(response.text)   # agents are prompted to return JSON
```

---

## Original version

The `master` branch contains the original **Competitive Intelligence Platform** (different pipeline, different purpose). This branch is a full rebuild.
