"""
Orchestrator — The conductor of the multi-agent pipeline.

Role: Workflow coordinator
---------------------------
The orchestrator knows about all agents and decides:
  1. Which agents to invoke, in what order
  2. How to pass outputs from one agent as inputs to the next
  3. How to handle errors gracefully without losing completed work
  4. When the pipeline is complete

This is a "sequential workflow" orchestrator — agents run one after another,
each building on the previous agent's output. This is appropriate here because:
  - Phase 2 (Analysis) NEEDS Phase 1 (Research) to be complete first
  - Phase 3 (Signals) NEEDS Phase 2 (Analysis) to reason from
  - The Report Writer NEEDS all previous outputs

An alternative pattern is "parallel orchestration" where independent agents
run concurrently. For example, in a larger system you might parallelize the
per-competitor research calls (each company can be researched independently).

The orchestrator does NOT do any AI work itself — it's pure Python logic.
Keeping orchestration separate from intelligence makes the system easier to
test, debug, and modify.
"""

from datetime import datetime
from pathlib import Path

from .researcher import ResearchAgent
from .analyst import AnalysisAgent
from .signal_detector import SignalDetectorAgent
from .report_writer import ReportWriterAgent


class Orchestrator:
    """
    Coordinates the full competitive intelligence pipeline.

    Pipeline:
        [User Input]
            ↓
        ResearchAgent      → Competitor profiles (structured markdown)
            ↓
        AnalysisAgent      → Strategic analysis + scoring (tool use)
            ↓
        SignalDetectorAgent → Prioritized signals and early warnings
            ↓
        ReportWriterAgent  → Executive report (streamed to console)
            ↓
        [Markdown file saved to disk]
    """

    def __init__(self):
        self.researcher = ResearchAgent()
        self.analyst = AnalysisAgent()
        self.signal_detector = SignalDetectorAgent()
        self.report_writer = ReportWriterAgent()

    def run(
        self,
        your_company: str,
        competitors: list[str],
        market: str,
        output_dir: Path = Path("."),
    ) -> Path:
        """
        Execute the full competitive intelligence pipeline and save the report.

        Args:
            your_company: Company the report is generated FOR.
            competitors: List of competitor names to analyze.
            market: Market/industry context string.
            output_dir: Directory where the report file will be saved.

        Returns:
            Path to the saved report file.
        """
        started_at = datetime.now()

        print(f"\n{'═' * 60}")
        print(f"  🔍 Competitive Intelligence Platform")
        print(f"{'═' * 60}")
        print(f"  Company:     {your_company}")
        print(f"  Market:      {market}")
        print(f"  Competitors: {', '.join(competitors)}")
        print(f"  Started:     {started_at.strftime('%H:%M:%S')}")
        print(f"{'═' * 60}\n")

        # ── Phase 1: Research ──────────────────────────────────────────────
        print("📚 Phase 1 / 4 — Research")
        print("  Gathering competitor profiles...")
        competitor_profiles = self.researcher.research_all(competitors, market)
        print(f"  ✅ Profiled {len(competitor_profiles)} companies.\n")

        # ── Phase 2: Analysis ──────────────────────────────────────────────
        print("🔬 Phase 2 / 4 — Strategic Analysis")
        print("  Running competitive analysis (with tool use for scoring)...")
        analysis = self.analyst.analyze(your_company, market, competitor_profiles)
        print(f"  ✅ Analysis complete.\n")

        # ── Phase 3: Signal Detection ──────────────────────────────────────
        print("⚡ Phase 3 / 4 — Signal Detection")
        print("  Scanning for strategic signals and early warnings...")
        signals = self.signal_detector.detect_signals(
            your_company, market, competitor_profiles, analysis
        )
        print(f"  ✅ Signals identified.\n")

        # ── Phase 4: Report Writing ────────────────────────────────────────
        print("📄 Phase 4 / 4 — Report Writing")
        report_markdown = self.report_writer.write_report(
            your_company=your_company,
            market=market,
            competitors=competitors,
            competitor_profiles=competitor_profiles,
            analysis=analysis,
            signals=signals,
            competitor_scores=self.analyst.competitor_scores,
        )

        # ── Save Report ────────────────────────────────────────────────────
        safe_name = your_company.lower().replace(" ", "_").replace("/", "-")
        timestamp = started_at.strftime("%Y%m%d_%H%M")
        filename = f"intel_{safe_name}_{timestamp}.md"
        output_path = output_dir / filename

        # Prepend a YAML frontmatter header for easy parsing/indexing
        frontmatter = (
            f"---\n"
            f"title: Competitive Intelligence Report\n"
            f"company: {your_company}\n"
            f"market: {market}\n"
            f"competitors: [{', '.join(competitors)}]\n"
            f"generated: {started_at.isoformat()}\n"
            f"duration_seconds: {(datetime.now() - started_at).seconds}\n"
            f"---\n\n"
        )

        output_path.write_text(frontmatter + report_markdown, encoding="utf-8")

        elapsed = (datetime.now() - started_at).seconds
        print(f"\n{'═' * 60}")
        print(f"  ✅ Pipeline complete in {elapsed}s")
        print(f"  📁 Report saved: {output_path}")
        print(f"{'═' * 60}\n")

        return output_path
