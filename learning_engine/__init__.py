"""learning_engine — SQLite-backed memory: findings, triage, lessons, patterns.

Public API (see engine.py):
    record_finding, record_triage, recall, distill, score
"""

from .engine import LearningEngine  # noqa: F401

__all__ = ["LearningEngine"]
__version__ = "1.0.0"