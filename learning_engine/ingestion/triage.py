"""Triage ingestion: record verdicts against findings."""

from __future__ import annotations

from datetime import datetime, timezone

from ..core.storage import Database
from ..core.validation import normalize_finding_id, validate_verdict


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def persist_triage(
    db: Database,
    *,
    finding_id: str,
    verdict: str,
    reason: str | None = None,
    reviewer: str | None = None,
) -> dict:
    fid = normalize_finding_id(finding_id)
    v = validate_verdict(verdict)

    existing = db.one("SELECT finding_id FROM findings WHERE finding_id = ?", (fid,))
    if not existing:
        raise ValueError(f"unknown finding_id: {fid} (ingest the finding first)")

    db.execute(
        """
        INSERT INTO triage (finding_id, verdict, reason, reviewer, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (fid, v, reason, reviewer, _now()),
    )
    db.commit()
    return {"finding_id": fid, "verdict": v, "reason": reason, "reviewer": reviewer}


def latest_verdict(db: Database, finding_id: str) -> dict | None:
    return db.one(
        """
        SELECT verdict, reason, reviewer, created_at
        FROM triage WHERE finding_id = ?
        ORDER BY id DESC LIMIT 1
        """,
        (finding_id,),
    )