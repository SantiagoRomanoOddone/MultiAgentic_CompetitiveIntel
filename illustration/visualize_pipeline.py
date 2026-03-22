#!/usr/bin/env python3
"""
Pipeline Visualization
======================
Rebuilds our Sales Lead Qualification pipeline using agent_framework's
native Workflow primitives, then generates visual diagrams showing how
the agents interact with each other.

Outputs:
    illustration/pipeline.mermaid   — Mermaid flowchart (paste into any Mermaid renderer)
    illustration/pipeline.dot       — Graphviz DOT source
    illustration/pipeline.png       — Rendered PNG (requires graphviz CLI)

No LLM calls are made — this is purely structural.
"""

import asyncio
import sys
from dataclasses import dataclass
from pathlib import Path
from typing_extensions import Never

from agent_framework import (
    Case,
    Default,
    Executor,
    WorkflowBuilder,
    WorkflowContext,
    WorkflowViz,
    handler,
)


# ── Data models (mirrors models.py) ─────────────────────────────────

@dataclass
class LeadData:
    name: str
    company: str
    title: str
    email: str
    industry: str = ""


@dataclass
class ResearchResult:
    lead: LeadData
    research: str = ""


@dataclass
class QualificationResult:
    lead: LeadData
    research: str
    score: int = 0
    category: str = ""
    reasoning: str = ""


@dataclass
class OutreachResult:
    lead: LeadData
    subject: str = ""
    body: str = ""
    score: int = 0
    category: str = ""


# ── Executor nodes (one per pipeline stage) ──────────────────────────

class Researcher(Executor):
    """Gathers intel on a lead: company info, pain points, relevance."""

    @handler
    async def process(self, lead: LeadData, ctx: WorkflowContext[ResearchResult]) -> None:
        # In production this calls the LLM via Agent — here we just pass through
        result = ResearchResult(lead=lead, research="(research placeholder)")
        await ctx.send_message(result)


class Qualifier(Executor):
    """Scores the lead 1-10 and categorises as hot / warm / cold."""

    @handler
    async def process(self, data: ResearchResult, ctx: WorkflowContext[QualificationResult]) -> None:
        result = QualificationResult(
            lead=data.lead,
            research=data.research,
            score=7,
            category="warm",
            reasoning="(qualification placeholder)",
        )
        await ctx.send_message(result)


class Outreach(Executor):
    """Drafts a personalised cold email for qualified leads."""

    @handler
    async def process(self, data: QualificationResult, ctx: WorkflowContext[OutreachResult]) -> None:
        result = OutreachResult(
            lead=data.lead,
            subject="(subject placeholder)",
            body="(body placeholder)",
            score=data.score,
            category=data.category,
        )
        await ctx.send_message(result)


class HumanReview(Executor):
    """Human-in-the-loop: approve, reject, or edit the draft."""

    @handler
    async def process(self, data: OutreachResult, ctx: WorkflowContext[Never, OutreachResult]) -> None:
        # Terminal node — yields final output
        await ctx.yield_output(data)


class AutoSkip(Executor):
    """Auto-skips leads that scored below the qualification threshold."""

    @handler
    async def process(self, data: QualificationResult, ctx: WorkflowContext[Never, str]) -> None:
        await ctx.yield_output(f"Skipped: {data.lead.name} (score {data.score})")


# ── Build the workflow ───────────────────────────────────────────────

QUALIFY_THRESHOLD = 5


def build_pipeline_workflow():
    researcher = Researcher(id="Researcher")
    qualifier = Qualifier(id="Qualifier")
    outreach = Outreach(id="Outreach")
    human_review = HumanReview(id="Human Review")
    auto_skip = AutoSkip(id="Auto-Skip")

    workflow = (
        WorkflowBuilder(
            start_executor=researcher,
            name="Sales Lead Qualification Pipeline",
            description="Multi-agent pipeline: research → qualify → route → outreach → human review",
        )
        # Researcher feeds into Qualifier
        .add_edge(researcher, qualifier)
        # Qualifier routes based on score
        .add_switch_case_edge_group(
            qualifier,
            [
                Case(
                    condition=lambda result: result.score >= QUALIFY_THRESHOLD,
                    target=outreach,
                ),
                Default(target=auto_skip),
            ],
        )
        # Qualified leads go to human review
        .add_edge(outreach, human_review)
        .build()
    )
    return workflow


# ── Generate diagrams ────────────────────────────────────────────────

def main():
    output_dir = Path(__file__).parent

    workflow = build_pipeline_workflow()
    viz = WorkflowViz(workflow)

    # 1. Mermaid
    mermaid_text = viz.to_mermaid()
    mermaid_path = output_dir / "pipeline.mermaid"
    mermaid_path.write_text(mermaid_text, encoding="utf-8")
    print(f"  Mermaid → {mermaid_path}")

    # 2. DOT
    dot_text = viz.to_digraph()
    dot_path = output_dir / "pipeline.dot"
    dot_path.write_text(dot_text, encoding="utf-8")
    print(f"  DOT     → {dot_path}")

    # 3. PNG
    try:
        png_path = viz.export(format="png", filename=str(output_dir / "pipeline"))
        print(f"  PNG     → {png_path}")
    except ImportError as e:
        print(f"  PNG     — skipped ({e})")

    # 4. Annotated DOT with edge labels and descriptions
    annotated_dot = _build_annotated_dot()
    annotated_dot_path = output_dir / "pipeline_annotated.dot"
    annotated_dot_path.write_text(annotated_dot, encoding="utf-8")
    print(f"  DOT*    → {annotated_dot_path}")

    try:
        import graphviz as gv

        src = gv.Source(annotated_dot)
        base = str(output_dir / "pipeline_annotated")
        src.render(base, format="png", cleanup=True)
        print(f"  PNG*    → {base}.png")
    except Exception as e:
        print(f"  PNG*    — skipped ({e})")

    # 5. Print the Mermaid to stdout for quick preview
    print(f"\n{'─' * 55}")
    print("  Mermaid Diagram (paste into https://mermaid.live)")
    print(f"{'─' * 55}")
    print(mermaid_text)
    print()


def _build_annotated_dot() -> str:
    """Hand-crafted DOT with edge labels showing the routing logic."""
    return '''\
// Sales Lead Qualification Pipeline — annotated version
// Generated from agent_framework WorkflowViz, then enriched with edge labels
// Render: dot -Tpng pipeline_annotated.dot -o pipeline_annotated.png

digraph Workflow {
  rankdir=TD;
  fontname="Helvetica";
  node [shape=box, style="filled,rounded", fontname="Helvetica", fontsize=12];
  edge [color="#333333", arrowhead=vee, fontname="Helvetica", fontsize=10];

  // Nodes
  "Researcher"   [fillcolor="#90EE90", label="Researcher\\n(Start)\\n\\nGathers intel on the lead:\\ncompany, pain points, relevance"];
  "Qualifier"    [fillcolor="#87CEEB", label="Qualifier\\n\\nScores 1\\u201310\\nhot / warm / cold"];
  "Outreach"     [fillcolor="#87CEEB", label="Outreach\\n\\nDrafts personalised\\ncold email"];
  "Auto-Skip"    [fillcolor="#FFB6C1", label="Auto-Skip\\n\\nScore < 5\\nLead discarded"];
  "Human Review" [fillcolor="#DDA0DD", label="Human Review\\n\\nApprove / Reject / Edit\\n(human-in-the-loop)"];

  // Edges
  "Researcher" -> "Qualifier"    [label="  research brief  "];
  "Qualifier"  -> "Outreach"     [label="  score >= 5  ", color="#228B22", fontcolor="#228B22"];
  "Qualifier"  -> "Auto-Skip"    [label="  score < 5  ", color="#DC143C", fontcolor="#DC143C", style=dashed];
  "Outreach"   -> "Human Review" [label="  email draft  "];
}
'''


if __name__ == "__main__":
    main()
