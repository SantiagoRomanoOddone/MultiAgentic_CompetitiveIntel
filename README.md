# Competitive Intelligence Platform

> An AI-powered multi-agent system that automatically researches competitors, analyzes market dynamics, detects strategic signals, and generates executive-ready intelligence reports.

---

## The Problem 

Every business — from a 10-person startup to a Fortune 500 company — needs to track competitors. But today, competitive intelligence is:

- **Slow**: A typical analyst spends 5–10 hours per week manually researching competitors
- **Expensive**: Dedicated CI platforms (Crayon, Klue, Kompyte) cost $1,000–$5,000/month — out of reach for most SMBs
- **Reactive**: By the time a competitor move is noticed and analyzed, the window to respond has often passed
- **Inconsistent**: Analysis quality depends entirely on who wrote it and how much time they had

**The opportunity**: LLMs can do 80% of the research work in minutes, not hours. A multi-agent system can produce a structured, analyst-quality competitive report in under 3 minutes — and do it automatically, on a schedule, for any market.

**Business model**: $299–$999/month SaaS targeting SMBs (50–500 employees). Each report would cost ~$0.30–$0.80 in API calls. At $299/month for weekly reports, the gross margin is >90%.

**Why it has startup potential**:
- Recurring need (competitive intelligence never "finishes")
- Clear ROI (saves 5+ hours/week per analyst at ~$50/hr = $13,000+/year saved)
- No-code interface makes it accessible to non-technical users
- The reports can trigger Slack alerts, CRM updates, or sales enablement workflows

---

## How It Works: Multi-Agent Architecture

The system uses four specialized AI agents, each with a distinct role. They run sequentially, each building on the previous agent's output.

```
User Input (your company + competitors + market)
        │
        ▼
┌─────────────────────┐
│   Orchestrator      │  ← Pure Python. No AI. Just workflow logic.
│   (orchestrator.py) │    Knows which agents to call and in what order.
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Research Agent     │  ← Specialization: Information gathering
│  (researcher.py)    │    Creates detailed profiles for each competitor.
│                     │    In production: calls web search, Crunchbase,
│                     │    LinkedIn APIs, review sites (G2, Capterra).
└──────┬──────────────┘
       │  competitor profiles (structured markdown)
       ▼
┌─────────────────────┐
│  Analysis Agent     │  ← Specialization: Strategic synthesis
│  (analyst.py)       │    Uses TOOL USE to score each competitor on
│                     │    key dimensions (product, momentum, threat level).
│                     │    Then writes a full strategic analysis.
└──────┬──────────────┘
       │  analysis + structured scores from tool calls
       ▼
┌─────────────────────┐
│  Signal Detector    │  ← Specialization: Early warning intelligence
│  (signal_detector.py)│   Identifies leading indicators: hiring surges,
│                     │    pricing changes, product pivots, market moves.
│                     │    Flags URGENT signals requiring fast action.
└──────┬──────────────┘
       │  prioritized signals with recommended responses
       ▼
┌─────────────────────┐
│  Report Writer      │  ← Specialization: Executive communication
│  (report_writer.py) │    Compiles all outputs into a polished Markdown
│                     │    report. Uses STREAMING to display in real-time.
│                     │    Written for C-suite audience: opinionated,
│                     │    direct, scannable in 5 minutes.
└──────┬──────────────┘
       │
       ▼
  📄 intel_[company]_[date].md  (saved to disk)
```

### Why Multiple Agents?

Each agent has a **different job, different system prompt, and different optimization target**:

| Agent | Optimizes for | Key trait |
|-------|--------------|-----------|
| Researcher | Breadth + factual accuracy | Just the facts, no spin |
| Analyst | Depth + strategic insight | Opinionated, analytical |
| Signal Detector | Timeliness + actionability | Proactive, urgent |
| Report Writer | Clarity + scannability | Executive-ready, decisive |

Combining all of this into a single prompt would produce mediocre results in all dimensions. Specialized agents produce excellent results in each dimension.

### Demonstrated Patterns

This codebase demonstrates three key multi-agent patterns:

1. **Sequential Pipeline** (Orchestrator → agents in order)
2. **Tool Use in Agents** (Analysis Agent calls `score_competitor` tool)
3. **Streaming Output** (Report Writer streams to console in real-time)

---

## Agent Roles in Detail

### 🔍 Research Agent (`agents/researcher.py`)
Creates detailed competitor profiles covering: company snapshot, products, pricing, target customers, strengths, weaknesses, recent moves, and go-to-market approach.

**Production extension**: Add tool use to call live APIs — web search, Crunchbase funding data, LinkedIn job postings, G2 reviews, pricing pages.

### 🔬 Analysis Agent (`agents/analyst.py`)
Synthesizes research into strategic intelligence. Uses **tool use** to score each competitor on four dimensions (product strength, market momentum, pricing aggression, brand strength) before writing its full analysis.

The tool use pattern here shows how Claude can produce **structured data** (JSON scores) alongside **unstructured text** (narrative analysis) — powerful for feeding downstream dashboards or databases.

### ⚡ Signal Detector (`agents/signal_detector.py`)
Identifies leading indicators across four categories:
- 🔴 **Immediate Threats** — moves requiring response NOW
- 🟡 **Watch List** — trends to monitor monthly
- 🟢 **Opportunities** — competitor gaps to exploit
- ⚡ **Market Inflection Points** — forces reshaping the landscape

### 📄 Report Writer (`agents/report_writer.py`)
Compiles all outputs into an executive report using **streaming** so users see content appear in real-time rather than waiting 30+ seconds. Structured as 8 sections optimized for C-suite reading patterns.

---

## Quickstart

### 1. Prerequisites

- Python 3.10+
- An Anthropic API key ([get one here](https://console.anthropic.com))

### 2. Install

```bash
cd test1
pip install -r requirements.txt
```

### 3. Configure

```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 4. Run

**Quick demo** (no input required):
```bash
python main.py --demo
```

**Interactive mode**:
```bash
python main.py
```

**Command-line mode** (great for automation):
```bash
python main.py \
  --company "Slack" \
  --competitors "Microsoft Teams,Zoom,Discord" \
  --market "business communication and collaboration"
```

The report is saved as `intel_[company]_[timestamp].md` in the current directory.

---

## Example Output Structure

Each report contains:

1. **Executive Summary** — 5 bullets an exec needs to read
2. **Market Landscape** — Structure, dynamics, maturity stage
3. **Competitor Profiles** — Positioning, strengths, weaknesses, threat rating
4. **Competitive Dynamics** — Who's winning, key battlegrounds, positioning map
5. **Signals & Early Warnings** — Prioritized alerts with recommended actions
6. **Strategic Recommendations** — 5 prioritized actions with rationale and timing
7. **Monitoring Dashboard** — What to watch weekly/monthly

---

## Estimated Cost per Report

| Competitors | Approximate API cost |
|-------------|---------------------|
| 2–3          | ~$0.30–0.50         |
| 4–5          | ~$0.50–0.80         |
| 6–8          | ~$0.80–1.20         |

*(Using Claude Sonnet 4.6 pricing. Input/output token counts vary by report depth.)*

---

## Extending This System

This prototype is intentionally simple to be easy to understand. Here's how a production version would extend it:

### Add Live Data Sources
```python
# In researcher.py, add tools for live data:
WEB_SEARCH_TOOL = {"type": "web_search_20260209", "name": "web_search"}
# Claude will automatically search the web for current data
```

### Run Research in Parallel
```python
# In orchestrator.py, use asyncio for concurrent research:
import asyncio
profiles = await asyncio.gather(*[
    researcher.research_company_async(company, market)
    for company in competitors
])
```

### Add a Scheduling Layer
```python
# Run weekly reports automatically:
# Use a cron job, Celery task, or cloud scheduler to call:
orchestrator.run(company, competitors, market)
# Then email or Slack the report
```

### Output to Multiple Formats
```python
# Convert the markdown report to PDF, DOCX, or HTML
# Add charts from the competitor scores data
# Post sections directly to Slack or Notion
```

### Build a Web UI
```python
# Wrap the orchestrator in a FastAPI endpoint:
@app.post("/analyze")
async def analyze(request: AnalysisRequest):
    return orchestrator.run(request.company, request.competitors, request.market)
```

---

## Project Structure

```
test1/
├── main.py                    # CLI entry point
├── requirements.txt           # Dependencies
├── .env.example               # API key template
├── README.md                  # This file
└── agents/
    ├── __init__.py
    ├── base.py                # Shared client + model config
    ├── orchestrator.py        # Workflow coordinator
    ├── researcher.py          # Research Agent
    ├── analyst.py             # Analysis Agent (with tool use)
    ├── signal_detector.py     # Signal Detection Agent
    └── report_writer.py       # Report Writer (with streaming)
```

---

## Why Claude for This?

- **Broad knowledge**: Claude has deep knowledge of thousands of companies, markets, and business models — ideal for the research phase
- **Strategic reasoning**: Claude excels at synthesis, pattern recognition, and strategic analysis — the core of what makes CI valuable
- **Tool use**: The ability to call structured functions (like our `score_competitor` tool) lets agents produce machine-readable data alongside text
- **Instruction following**: Complex multi-section reports come out well-structured on the first try
- **Streaming**: Long reports stream smoothly, making the UX feel responsive even for 4,000-token outputs

---

*Built with the [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python) and Claude Sonnet 4.6.*
