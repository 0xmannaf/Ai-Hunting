"""Validation and normalization of learning-engine payloads."""

from __future__ import annotations

import re

from .config import SEVERITIES, VERDICTS

_ID_RE = re.compile(r"[^a-z0-9_.-]+")
_FINDING_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_.-]*$")


def normalize_target(target: str) -> str:
    t = str(target or "").strip().lower()
    if not t:
        raise ValueError("target must be non-empty")
    return t.rstrip("/")


def normalize_vuln_class(vuln_class: str) -> str:
    v = str(vuln_class or "").strip().lower()
    if not v:
        raise ValueError("vuln_class must be non-empty")
    return _ID_RE.sub("-", v).strip("-")


def normalize_finding_id(finding_id: str) -> str:
    f = str(finding_id or "").strip().lower()
    if not _FINDING_ID_RE.match(f):
        raise ValueError(
            f"invalid finding_id {f!r}: lowercase letters, digits, '.', '_', '-' only"
        )
    return f


def validate_severity(severity: str) -> str:
    s = str(severity or "").strip().lower()
    if s not in SEVERITIES:
        raise ValueError(f"severity must be one of {SEVERITIES}, got {s!r}")
    return s


def validate_confidence(confidence: float) -> float:
    c = float(confidence)
    if not (0.0 <= c <= 1.0):
        raise ValueError(f"confidence must be within [0, 1], got {c}")
    return c


def validate_verdict(verdict: str) -> str:
    v = str(verdict or "").strip().lower()
    if v not in VERDICTS:
        raise ValueError(f"verdict must be one of {VERDICTS}, got {v!r}")
    return v


def validate_signals(signals: dict | None) -> dict:
    if not signals:
        return {}
    if not isinstance(signals, dict):
        raise TypeError("signals must be a dict of signal key -> truthy value")
    out: dict = {}
    for key, value in signals.items():
        k = str(key).strip().lower()
        if not k:
            continue
        if isinstance(value, (int, float, bool, str)):
            out[k] = value
    return out