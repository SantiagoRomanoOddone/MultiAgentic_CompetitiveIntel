# Competitive Intelligence Platform

A multi-agent system that researches competitors, analyzes market dynamics, detects strategic signals, and generates intelligence reports — in minutes instead of hours.

---

## Architecture

```
[company + competitors + market]
        │
        ▼
   Orchestrator          # Sequential pipeline coordinator. No AI — pure workflow logic.
        │
        ▼
   Research Agent        # Builds a structured profile for each competitor
        │
        ▼
   Analysis Agent        # Strategic synthesis + scores competitors via tool use
        │
        ▼
   Signal Detector       # Flags threats, opportunities, and market inflection points
        │
        ▼
   Report Writer         # Compiles everything into a streamed executive report
        │
        ▼
  intel_[company]_[date].md
```

**Patterns demonstrated:** sequential pipeline, tool use for structured output, streaming.

---

## Quickstart

**Prerequisites:** Python 3.10+, [Anthropic API key](https://console.anthropic.com)

```bash
# 1. Install
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env

# 3. Run
python main.py --demo

# Or with your own inputs
python main.py \
  --company "Slack" \
  --competitors "Microsoft Teams,Zoom,Discord" \
  --market "business communication"
```

The report is saved as `intel_[company]_[timestamp].md`.

---

## Structure

```
├── main.py                  # CLI entry point
├── requirements.txt
├── .env.example
└── agents/
    ├── base.py              # Shared client + model config
    ├── orchestrator.py      # Pipeline coordinator
    ├── researcher.py        # Research Agent
    ├── analyst.py           # Analysis Agent (tool use)
    ├── signal_detector.py   # Signal Detection Agent
    └── report_writer.py     # Report Writer (streaming)
```

---

*Built with the [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python) and Claude Sonnet 4.6.*
