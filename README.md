# Competitive Intelligence Platform

Multi-agent system that researches competitors, scores strategic signals, and generates structured intelligence reports. Four specialized agents run sequentially, each building on the previous output.

---

## Architecture

```
User Input (company + competitors + market)
        │
        ▼
┌─────────────────────┐
│   Orchestrator      │  Pure Python. Workflow logic only.
│   (orchestrator.py) │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Research Agent     │  Builds structured competitor profiles.
│  (researcher.py)    │
└──────┬──────────────┘
       │  competitor profiles (structured markdown)
       ▼
┌─────────────────────┐
│  Analysis Agent     │  Scores competitors via tool use, writes
│  (analyst.py)       │  strategic analysis.
└──────┬──────────────┘
       │  scores + narrative analysis
       ▼
┌─────────────────────┐
│  Signal Detector    │  Identifies leading indicators: hiring
│  (signal_detector.py)│  surges, pricing changes, product pivots.
└──────┬──────────────┘
       │  prioritized signals
       ▼
┌─────────────────────┐
│  Report Writer      │  Compiles all outputs into a Markdown
│  (report_writer.py) │  report, streamed to console in real-time.
└──────┬──────────────┘
       │
       ▼
  intel_[company]_[date].md
```

**Patterns demonstrated**: sequential pipeline, tool use (structured JSON scores from `score_competitor`), streaming output.

---

## Quickstart

**Prerequisites**: Python 3.10+, Anthropic API key

```bash
cd test1
pip install -r requirements.txt
cp .env.example .env
# Add ANTHROPIC_API_KEY to .env
```

```bash
# Demo (no input required)
python main.py --demo

# Interactive
python main.py

# CLI
python main.py \
  --company "Slack" \
  --competitors "Microsoft Teams,Zoom,Discord" \
  --market "business communication and collaboration"
```

Output saved as `intel_[company]_[timestamp].md`.

---

## Project Structure

```
test1/
├── main.py                    # CLI entry point
├── requirements.txt
├── .env.example
└── agents/
    ├── base.py                # Shared client + model config
    ├── orchestrator.py        # Workflow coordinator
    ├── researcher.py          # Research Agent
    ├── analyst.py             # Analysis Agent (tool use)
    ├── signal_detector.py     # Signal Detection Agent
    └── report_writer.py       # Report Writer (streaming)
```

---

*Built with the [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python) and Claude Sonnet 4.6.*
