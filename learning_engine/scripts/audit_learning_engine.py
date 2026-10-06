#!/usr/bin/env python3
"""audit_learning_engine.py — health audit of the learning engine DB.

Checks (exit 1 on any failure):
  1. DB initializes and schema version matches code SCHEMA_VERSION
  2. table row counts reported
  3. no triage rows pointing at unknown findings (FK orphans)
  4. signal weights are bounded (0 < w <= 0.50) and non-empty
  5. FTS tables present (fallback search still works if absent)
  6. findings sanity: severity/confidence in valid ranges

Usage:
  python learning_engine/scripts/audit_learning_engine.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from learning_engine.core.config import SEVERITIES, SCHEMA_VERSION  # noqa: E402
from learning_engine.core.storage import Database  # noqa: E402
from learning_engine.scoring.engine import load_weights  # noqa: E402


def audit() -> int:
    problems: list[str] = []
    db = Database(ROOT / "learning_engine" / "memory" / "learning.db")
    db.init_schema()

    version = db.one("SELECT value FROM meta WHERE key = 'schema_version'")
    if not version or version["value"] != SCHEMA_VERSION:
        problems.append(f"schema version mismatch: db={version} code={SCHEMA_VERSION}")

    stats = {t: db.one(f"SELECT count(*) AS n FROM {t}")["n"]
             for t in ("findings", "triage", "lessons", "patterns", "signals_meta")}
    print(f"[audit] rows: {json.dumps(stats)}")

    orphans = db.rows(
        "SELECT t.finding_id, t.verdict FROM triage t "
        "LEFT JOIN findings f ON f.finding_id = t.finding_id WHERE f.finding_id IS NULL"
    )
    for o in orphans:
        problems.append(f"triage orphan: finding_id={o['finding_id']}")

    weights = load_weights()
    if not weights:
        problems.append("signal weights are empty")
    for key, w in weights.items():
        if not (0.0 < w <= 0.50):
            problems.append(f"signal weight out of bounds: {key}={w}")

    try:
        db.execute("SELECT count(*) FROM findings_fts")
        print("[audit] fts5: available")
    except Exception:  # noqa: BLE001
        print("[audit] fts5: unavailable (LIKE fallback will be used)")

    for f in db.rows("SELECT severity, confidence FROM findings"):
        if f["severity"] not in SEVERITIES:
            problems.append(f"bad severity: {f['severity']}")
        if not (0.0 <= float(f["confidence"]) <= 1.0):
            problems.append(f"bad confidence: {f['confidence']}")

    if problems:
        for p in problems:
            print(f"[FAIL] {p}", file=sys.stderr)
        print(f"audit FAILED: {len(problems)} problem(s)", file=sys.stderr)
        return 1
    print("audit OK")
    return 0


if __name__ == "__main__":
    sys.exit(audit())