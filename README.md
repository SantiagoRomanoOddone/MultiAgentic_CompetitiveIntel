# MultiAgentic CompetitiveIntel

A multi-agent price intelligence pipeline for CPG brands in Latin America — powered by **Microsoft `agent-framework`** and **Azure OpenAI**, with a **control layer** and **RL feedback loop** that learns from human decisions over time.

---

## What it does

Given a stream of price events (from the Argentine SEPA dataset or VTEX APIs), the pipeline runs 3 AI agents in sequence, with a rules-based control layer and a lightweight reinforcement learning loop:

```
[sample_events.json]   ← SEPA daily price data / VTEX API
        │
        ▼
  DataFetcherAgent      # Enriches the raw price event with competitive context
        │
        ▼
  AnalystAgent          # Scores urgency (1–10) and classifies the alert type
        │
        ▼
  Control Layer         # Auto-skip low-urgency / escalate high-urgency alerts
        │
        ▼
  RecommenderAgent      # Recommends action + drafts message for brand manager
        │
        ▼
  Human Review (CLI)    # Approve / reject / edit — every decision feeds the RL loop
        │
        ▼
  RL Feedback Store     # Adjusts skip threshold based on approval patterns
```

---

## Data source

**SEPA** (Sistema Electrónico de Publicidad de Precios Argentinos) — the Argentine government requires all large supermarket chains to report prices daily.

| Stat | Value |
|---|---|
| Supermarket branches | 3,600 |
| Price records per day | ~12 million |
| Chains covered | Carrefour, DIA, Jumbo, Walmart, Coto, and more |
| License | Creative Commons Attribution 4.0 |
| Update frequency | Daily |
| Source | [datos.produccion.gob.ar/dataset/sepa-precios](https://datos.produccion.gob.ar/dataset/sepa-precios) |

For non-SEPA chains, the pipeline can query the **VTEX public catalog API** (used by most LatAm supermarkets) directly by EAN barcode — no authentication required.

---

## Tech stack

| Layer | Library |
|---|---|
| Agent framework | [`agent-framework-core`](https://github.com/microsoft/agent-framework) by Microsoft |
| LLM backend | Azure OpenAI (Chat Completions) via `AzureOpenAIChatClient` |
| Data models | Python dataclasses (`models.py`) |
| Control layer | Rules engine (`control_layer.py`) |
| RL feedback | Human-in-the-loop feedback store (`rl_feedback.py`) |
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
# Fill in your Azure OpenAI values

# 3. Run
python main.py
```

### `.env` variables

```env
OPEN_AI_ENDPOINT=https://<your-resource>.openai.azure.com
OPEN_AI_KEY=<your-api-key>
CHAT_MODEL=<your-deployment-name>   # e.g. gpt-4o
```

---

## Project structure

```
├── main.py                      # Entry point
├── pipeline.py                  # Orchestrates agents + control layer + RL
├── models.py                    # PriceEvent → AnalyzedEvent → ScoredAlert → ActionRecommendation
├── control_layer.py             # Rules engine: auto-skip / escalate / priority routing
├── rl_feedback.py               # RL feedback store: logs decisions, tunes skip threshold
├── human_loop.py                # CLI for reviewing and approving recommendations
├── sample_events.json           # Example price events (Argentine CPG data)
├── rl_feedback.json             # Auto-generated: persisted human feedback history
├── requirements.txt
└── intel_agents/
    ├── base.py                  # AzureOpenAIChatClient setup
    ├── response_utils.py        # Response parsing utilities
    ├── fetcher.py               # DataFetcherAgent — competitive context
    ├── analyst.py               # AnalystAgent — urgency scoring + alert classification
    └── recommender.py           # RecommenderAgent — action + message drafting
```

---

## Data flow

```
PriceEvent  (ean, product_name, brand, chain, list_price, promo_price, previous_price)
  └─> AnalyzedEvent   (+ context: competitive intelligence brief)
        └─> ScoredAlert    (+ urgency_score 1–10, alert_type, reasoning)
              └─> ActionRecommendation   (+ action, message)
```

**Alert types:** `price_increase` / `price_drop` / `promotion_start` / `competitor_move` / `srp_violation`

**Actions:** `reprice` / `notify_account_manager` / `escalate` / `monitor`

---

## Control layer

`control_layer.py` applies routing rules before human review:

| Condition | Routing |
|---|---|
| `urgency_score < skip_threshold` | Auto-skipped (logged, no human review) |
| `urgency_score >= 8` | Escalated flag — priority human review |
| Competitor drop > 15% | Always escalated regardless of score |

The `skip_threshold` starts at 4 and is tuned dynamically by the RL feedback loop.

---

## Reinforcement learning loop

Every human decision (approve / reject) is logged in `rl_feedback.json` with the alert type and urgency score. On the next run, `rl_feedback.compute_threshold()` scans the history and returns the lowest urgency score with >= 50% approval rate — which becomes the new skip threshold.

```
Run 1:  threshold = 4  (default, no history)
Run 5:  threshold = 5  (humans rejected too many score-4 alerts)
Run 20: threshold = 3  (humans approved most score-3 alerts after tuning prompts)
```

This is RLHF-lite: no neural network, same core principle — human signal drives policy.

---

## Validation context

This pipeline is a **validation prototype** for a competitive intelligence product targeting brand managers at mid-sized CPG companies in Argentina. The core hypothesis:

> Brand managers making weekly pricing decisions in a high-inflation environment have no systematic way to know if price increases are being applied correctly across chains, or when competitors move. They find out from their sales rep, days later.

The SEPA dataset makes this buildable today — 12M daily price records, free, legal, public.
