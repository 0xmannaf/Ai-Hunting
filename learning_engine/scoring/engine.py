"""Bounded signal scoring engine.

score(signals) sums the weights of present signals, clamped to [0, 1].
Weights live in signals.json (max 0.50 per signal; sum of weights may exceed 1
but the result is bounded by score_ceiling).
"""

from __future__ import annotations

import json
from pathlib import Path

from ..core.config import MAX_SIGNAL_WEIGHT

SIGNALS_PATH = Path(__file__).resolve().parent / "signals.json"


def load_weights() -> dict[str, float]:
    doc = json.loads(SIGNALS_PATH.read_text(encoding="utf-8"))
    return {str(k).lower(): float(v) for k, v in doc["weights"].items()}


def load_policy() -> dict:
    doc = json.loads(SIGNALS_PATH.read_text(encoding="utf-8"))
    return doc["policy"]


def score(signals: dict | None) -> dict:
    """Bounded scoring of a signal dict.

    Returns {score, matched, weights}. score is clamped to [0, 1].
    Auto-escalation: signals with an entry in BOOSTS get matched weight
    multiplied by (1 + boost) before clamping (bounded by the ceiling).
    """
    weights = load_weights()
    policy = load_policy()
    ceiling = float(policy.get("score_ceiling", 1.0))
    floor = float(policy.get("score_floor", 0.0))
    max_w = float(policy.get("max_signal_weight", MAX_SIGNAL_WEIGHT))

    signals = {str(k).strip().lower(): v for k, v in (signals or {}).items() if v}

    matched: dict[str, float] = {}
    total = 0.0
    for key in signals:
        w = weights.get(key, 0.0)
        if w > 0:
            boosted = min(w, max_w) * (1 + BOOSTS.get(key, 0.0))
            matched[key] = round(min(boosted, ceiling), 4)
            total += matched[key]

    bounded = max(floor, min(ceiling, total))
    return {"score": round(bounded, 4), "matched": matched, "weights": weights}


# Auto-escalation boosts applied to matched weights (before ceiling clamp).
BOOSTS = {
    "cross_tenant": 0.30,
    "admin_bypass": 0.30,
    "state_changing": 0.20,
    "sensitive_data": 0.20,
    "auth_bypass": 0.30,
    "chainable": 0.20,
    "payment_impact": 0.30,
}


def weight_for(signal: str) -> float:
    """Weight of a single signal key (0.0 if unknown)."""
    return load_weights().get(str(signal).strip().lower(), 0.0)