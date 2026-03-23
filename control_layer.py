"""
Control Layer
=============
Rules engine that decides how each alert is routed before human review.

Thresholds are seeded from RL feedback (rl_feedback.compute_threshold())
and refined over time as humans approve/reject recommendations.

Routing logic:
  urgency < skip_threshold      → auto-skip (log only, no human review)
  urgency >= escalate_threshold → escalate flag set (still goes to human)
  large competitor drop         → always escalated regardless of score
"""

from models import ScoredAlert

_DEFAULT_SKIP_THRESHOLD = 4
_DEFAULT_ESCALATE_THRESHOLD = 8
_LARGE_DROP_PCT = 15.0


class ControlLayer:
    def __init__(
        self,
        skip_threshold: int = _DEFAULT_SKIP_THRESHOLD,
        escalate_threshold: int = _DEFAULT_ESCALATE_THRESHOLD,
    ):
        self.skip_threshold = skip_threshold
        self.escalate_threshold = escalate_threshold

    def should_auto_skip(self, alert: ScoredAlert) -> bool:
        return alert.urgency_score < self.skip_threshold

    def should_escalate(self, alert: ScoredAlert) -> bool:
        if alert.urgency_score >= self.escalate_threshold:
            return True
        # Large competitor price drop is always escalated regardless of score
        change = alert.price_change_pct
        if (
            alert.alert_type == "competitor_move"
            and change is not None
            and change <= -_LARGE_DROP_PCT
        ):
            return True
        return False

    def priority(self, alert: ScoredAlert) -> str:
        if alert.urgency_score >= self.escalate_threshold:
            return "urgent"
        if alert.urgency_score >= 5:
            return "normal"
        return "low"
