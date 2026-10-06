"""Finding ingestion: normalize + persist findings."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from ..core.storage import Database
from ..core.validation import (
    normalize_finding_id,
    normalize_target,
    normalize_vuln_class,
    validate_confidence,
    validate_severity,
    validate_signals,
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def new_finding_id() -> str:
    return f"f-{uuid.uuid4().hex[:12]}"


def normalize_finding(
    *,
    target: str,
    vuln_class: str,
    title: str,
    severity: str = "medium",
    confidence: float = 0.5,
    evidence: str | None = None,
    signals: dict | None = None,
    source: str | None = None,
    finding_id: str | None = None,
) -> dict:
    doc = {
        "finding_id": normalize_finding_id(finding_id or new_finding_id()),
        "target": normalize_target(target),
        "vuln_class": normalize_vuln_class(vuln_class),
        "title": str(title).strip() or "untitled finding",
        "severity": validate_severity(severity),
        "confidence": validate_confidence(confidence),
        "evidence": evidence,
        "signals": validate_signals(signals),
        "source": source,
        "created_at": _now(),
    }
    return doc


def persist_finding(db: Database, doc: dict) -> dict:
    row = db.one("SELECT finding_id FROM findings WHERE finding_id = ?", (doc["finding_id"],))
    if row:
        return {**doc, "status": "existing"}
    db.execute(
        """
        INSERT INTO findings
            (finding_id, target, vuln_class, title, severity, confidence,
             evidence, signals, source, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            doc["finding_id"],
            doc["target"],
            doc["vuln_class"],
            doc["title"],
            doc["severity"],
            doc["confidence"],
            doc["evidence"],
            json.dumps(doc["signals"]),
            doc["source"],
            doc["created_at"],
        ),
    )
    db.commit()
    return {**doc, "status": "new"}