"""
RL Feedback Store
=================
Lightweight reinforcement learning loop: every human approval/rejection
is logged and used to tune the control layer's skip threshold over time.

How it works:
  1. After each human decision, log_decision() stores the outcome.
  2. compute_threshold() scans historical decisions and returns the lowest
     urgency score that still achieves >= MIN_APPROVAL_RATE approval.
  3. The pipeline feeds this threshold into the ControlLayer on each run,
     so the system gets tighter or looser based on actual feedback.

This is RLHF-lite: no neural network, but the same core idea —
human signal drives policy adjustment.
"""

import json
from pathlib import Path
from typing import Optional

_STORE = Path("rl_feedback.json")
_DEFAULT_THRESHOLD = 4
_MIN_APPROVAL_RATE = 0.5
_MIN_SAMPLES_TO_LEARN = 10


def log_decision(alert_type: str, urgency_score: int, approved: bool) -> None:
    """Persist a human approval/rejection decision."""
    history = _load()
    history.append(
        {
            "alert_type": alert_type,
            "urgency_score": urgency_score,
            "approved": approved,
        }
    )
    _STORE.write_text(json.dumps(history, indent=2))


def compute_threshold() -> int:
    """
    Return the learned skip threshold based on historical feedback.

    Algorithm: find the lowest urgency score where humans approve >= 50%
    of the time. Alerts below this score are auto-skipped by the control layer.
    Falls back to the default threshold until MIN_SAMPLES_TO_LEARN decisions exist.
    """
    history = _load()
    if len(history) < _MIN_SAMPLES_TO_LEARN:
        return _DEFAULT_THRESHOLD

    score_buckets: dict[int, list[bool]] = {}
    for entry in history:
        s = entry["urgency_score"]
        score_buckets.setdefault(s, []).append(entry["approved"])

    for score in range(1, 11):
        decisions = score_buckets.get(score, [])
        if not decisions:
            continue
        if sum(decisions) / len(decisions) >= _MIN_APPROVAL_RATE:
            return score

    return _DEFAULT_THRESHOLD


def approval_rate_summary() -> dict[str, float]:
    """Approval rate per alert_type — useful for understanding model drift."""
    history = _load()
    buckets: dict[str, dict] = {}
    for entry in history:
        at = entry["alert_type"]
        buckets.setdefault(at, {"approved": 0, "total": 0})
        buckets[at]["total"] += 1
        if entry["approved"]:
            buckets[at]["approved"] += 1
    return {
        k: round(v["approved"] / v["total"], 2)
        for k, v in buckets.items()
        if v["total"] > 0
    }


def _load() -> list:
    if not _STORE.exists():
        return []
    return json.loads(_STORE.read_text())
