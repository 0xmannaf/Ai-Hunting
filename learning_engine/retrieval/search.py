"""Retrieval: full-text search over findings and lessons (FTS5 with LIKE fallback)."""

from __future__ import annotations

from ..core.config import DEFAULT_RECALL_LIMIT
from ..core.storage import Database


def _fts_available(db: Database) -> bool:
    try:
        db.execute("SELECT count(*) FROM findings_fts")
        return True
    except Exception:  # noqa: BLE001
        return False


def _rank(query: str, row: dict) -> int:
    """Simple deterministic rank: match in title/target > vuln_class > lesson."""
    q = query.lower()
    score = 0
    for field in ("title", "lesson", "target", "vuln_class"):
        if q in str(row.get(field, "")).lower():
            score += 4 if field in ("title", "lesson") else 2
    return -score


def _tokens(query: str) -> list[str]:
    return [t for t in query.lower().replace("/", " ").split() if t]


def _multi_like_rows(db: Database, sql_from: str, fields: tuple[str, ...], query: str) -> list[dict]:
    """AND across query tokens: every token must appear in some indexed field."""
    tokens = _tokens(query)
    if not tokens:
        return []
    clauses, params = [], []
    for token in tokens:
        like = f"%{token}%"
        clauses.append("(" + " OR ".join(f"{f} LIKE ?" for f in fields) + ")")
        params += [like] * len(fields)
    return db.rows(f"SELECT * FROM {sql_from} WHERE {' AND '.join(clauses)}", params)


def search_findings(
    db: Database, query: str, limit: int = DEFAULT_RECALL_LIMIT, vuln_class: str | None = None
) -> list[dict]:
    query = str(query or "").strip()
    if not query:
        return []
    rows: list[dict] = []
    if _fts_available(db):
        fts_query = " AND ".join(f'"{t}"' for t in _tokens(query)) or query
        sql = (
            "SELECT f.*, bm25(findings_fts) AS rank FROM findings_fts "
            "JOIN findings f ON f.id = findings_fts.rowid WHERE findings_fts MATCH ?"
        )
        try:
            rows = db.rows(sql, (fts_query,))
        except Exception:  # noqa: BLE001
            rows = []
    if not rows:
        rows = _multi_like_rows(db, "findings", ("title", "target", "vuln_class", "signals"), query)
    if vuln_class:
        rows = [r for r in rows if r.get("vuln_class") == vuln_class]
    rows.sort(key=lambda r: _rank(query, r))
    return rows[:limit]


def search_lessons(
    db: Database, query: str, limit: int = DEFAULT_RECALL_LIMIT, vuln_class: str | None = None
) -> list[dict]:
    query = str(query or "").strip()
    if not query:
        return []
    rows: list[dict] = []
    if _fts_available(db):
        fts_query = " AND ".join(f'"{t}"' for t in _tokens(query)) or query
        sql = (
            "SELECT l.* FROM lessons_fts JOIN lessons l ON l.id = lessons_fts.rowid "
            "WHERE lessons_fts MATCH ?"
        )
        try:
            rows = db.rows(sql, (fts_query,))
        except Exception:  # noqa: BLE001
            rows = []
    if not rows:
        rows = _multi_like_rows(db, "lessons", ("lesson", "vuln_class"), query)
    if vuln_class:
        rows = [r for r in rows if r.get("vuln_class") == vuln_class]
    rows.sort(key=lambda r: _rank(query, r))
    return rows[:limit]