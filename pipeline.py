from intel_agents.fetcher import DataFetcherAgent
from intel_agents.analyst import AnalystAgent
from intel_agents.recommender import RecommenderAgent
from control_layer import ControlLayer
from human_loop import human_review
from rl_feedback import log_decision, compute_threshold, approval_rate_summary
from models import PriceEvent, ActionRecommendation


class Pipeline:
    def __init__(self):
        self.fetcher = DataFetcherAgent()
        self.analyst = AnalystAgent()
        self.recommender = RecommenderAgent()
        # Threshold is learned from past human decisions via RL feedback
        threshold = compute_threshold()
        self.control = ControlLayer(skip_threshold=threshold)
        print(f"  [RL]  Learned skip threshold: {threshold}  (auto-skip urgency < {threshold})")

    def run(self, events: list[PriceEvent]) -> list[ActionRecommendation]:
        approved = []

        for i, event in enumerate(events, 1):
            print(f"\n{'─' * 60}")
            print(f"  Event {i}/{len(events)}: {event.product_name} @ {event.chain}")
            print(f"{'─' * 60}")

            print("  [FETCHER]     Enriching with competitive context...", end=" ", flush=True)
            analyzed = self.fetcher.run(event)
            print("done")

            print("  [ANALYST]     Scoring urgency...", end=" ", flush=True)
            alert = self.analyst.run(analyzed)
            priority = self.control.priority(alert)
            print(
                f"done  →  {alert.urgency_score}/10  [{alert.alert_type}]  ({priority.upper()})"
            )
            print(f"              {alert.reasoning}")

            if self.control.should_auto_skip(alert):
                print("  → Auto-skipped by control layer (urgency below learned threshold)")
                log_decision(alert.alert_type, alert.urgency_score, approved=False)
                continue

            if self.control.should_escalate(alert):
                print("  ⚠  Escalated — flagged for priority review")

            print("  [RECOMMENDER] Drafting action...", end=" ", flush=True)
            recommendation = self.recommender.run(alert)
            print("done")

            result = human_review(recommendation)
            log_decision(alert.alert_type, alert.urgency_score, approved=result is not None)
            if result:
                approved.append(result)

        summary = approval_rate_summary()
        if summary:
            print(f"\n  [RL] Approval rates by type: {summary}")

        return approved
