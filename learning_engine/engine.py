"""engine.py — public API of the learning engine (5 hooks).

Hooks:
  1. record_finding(...)  — ingest a finding
  2. record_triage(...)   — ingest a triage verdict (incl. false positives)
  3. recall(query, ...)   — retrieve relevant lessons/findings
  4. distill(...)         — aggregate analytics into lessons + patterns
  5. score(signals)       — bounded signal scoring

Session lifecycle hooks (documented public API, used by the briefing):
  before_recon(target, techs)         — recon context + recalled lessons
  during_testing(signals)             — bounded signal score for live testing
  after_finding(target, endpoint, vulnerability_class, signals,
                validation_state, source_provenance) — persist a finding
  before_summary(findings)            — rank findings for the summary
  after_triage(finding_id, feedback_type, notes, provenance) — persist triage

Module-level helpers mirror the hooks using a default engine rooted at the
workspace root, so pipelines can do:

    from learning_engine import engine
    engine.record_finding(target=..., vuln_class=..., title=...)
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from .analytics.patterns import (
    duplicate_heavy_patterns,
    fp_pattern_candidates,
    highest_signal_surfaces,
    per_class_stats,
    signal_heatmap,
    target_summary,
)
from .core.config import Config, DEFAULT_RECALL_LIMIT, get_config
from .core.storage import Database
from .graph.builder import build_graph
from .ingestion.finding import normalize_finding, persist_finding
from .ingestion.triage import latest_verdict, persist_triage
from .retrieval.search import search_findings, search_lessons
from .scoring.engine import score as _score


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class LearningEngine:
    """SQLite-backed memory with five public hooks."""

    def __init__(self, root: str | Path | None = None) -> None:
        self.config: Config = Config(root=root) if root else get_config()
        self.db_path = self.config.db_path
        self.db: Database | None = None

    def init_db(self) -> Database:
        self.db = Database(self.db_path)
        self.db.init_schema()
        return self.db

    def _db(self) -> Database:
        if self.db is None:
            self.init_db()
        return self.db

    # ---- Hook 1: ingest a finding -------------------------------------
    def record_finding(
        self,
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
        doc = normalize_finding(
            target=target,
            vuln_class=vuln_class,
            title=title,
            severity=severity,
            confidence=confidence,
            evidence=evidence,
            signals=signals,
            source=source,
            finding_id=finding_id,
        )
        return persist_finding(self._db(), doc)

    # ---- Hook 2: ingest a triage verdict ------------------------------
    def record_triage(
        self,
        *,
        finding_id: str,
        verdict: str,
        reason: str | None = None,
        reviewer: str | None = None,
    ) -> dict:
        return persist_triage(
            self._db(), finding_id=finding_id, verdict=verdict,
            reason=reason, reviewer=reviewer,
        )

    # ---- Hook 3: recall ------------------------------------------------
    def recall(
        self,
        query: str,
        limit: int = DEFAULT_RECALL_LIMIT,
        vuln_class: str | None = None,
        include_lessons: bool = True,
        include_findings: bool = True,
    ) -> list[dict]:
        db = self._db()
        out: list[dict] = []
        if include_lessons:
            for r in search_lessons(db, query, limit, vuln_class):
                out.append({"kind": "lesson", **r})
        if include_findings:
            for r in search_findings(db, query, limit, vuln_class):
                out.append({"kind": "finding", **r})
        return out[:limit]

    # ---- Hook 4: distill -----------------------------------------------
    def distill(self, min_support: int = 2) -> dict:
        db = self._db()
        classes = per_class_stats(db)
        fp_patterns = fp_pattern_candidates(db, min_occurrences=max(1, min_support))
        out_classes: list[dict] = []
        for c in classes:
            lesson = (
                f"On {c['vuln_class']}: {c['confirmed']} confirmed / "
                f"{c['count']} total (fp_rate {c['fp_rate']:.0%}), "
                f"top signals: {', '.join(c['top_signals'][:3]) or 'none'}"
            )
            out_classes.append({**c, "lessons": [lesson]})
        return {
            "summary": {
                "classes": len(out_classes),
                "findings": sum(c["count"] for c in out_classes),
                "fp_patterns": len(fp_patterns),
                "generated_at": _now(),
            },
            "classes": out_classes,
            "fp_patterns": fp_patterns,
        }

    # ---- Hook 5: bounded signal scoring --------------------------------
    def score(self, signals: dict | None) -> dict:
        return _score(signals)

    # ---- Session lifecycle hooks (documented public API) ----------------

    # Mapping of finding-state machine -> confidence for validation_state input.
    STATE_CONFIDENCE = {
        "observation": 0.10,
        "lead": 0.25,
        "high_confidence_lead": 0.50,
        "confirmed": 0.70,
        "validated": 0.90,
        "reportable": 0.95,
    }

    # Mapping of triage feedback_type -> verdict for after_triage.
    FEEDBACK_VERDICTS = {
        "accepted": "confirmed",
        "duplicate": "unverified",
        "false_positive": "false_positive",
        "informational": "unverified",
        "n/a": "unverified",
    }

    def before_recon(self, target: str, techs: list[str] | None = None) -> dict:
        """Call before recon. Returns context: recalled lessons for the stack.

        Shapes: in  target: str, techs: list[str]
                out {"target": str, "techs": list[str], "relevant_lessons": [dict],
                     "suggested_classes": [str], "ok": True}
        """
        techs = techs or []
        query = " ".join(techs) or target
        lessons = self.recall(query, limit=5, include_findings=False)
        classes = sorted({r.get("vuln_class") for r in lessons if r.get("vuln_class")})
        return {
            "target": target,
            "techs": techs,
            "relevant_lessons": lessons,
            "suggested_classes": classes,
            "ok": True,
        }

    def during_testing(self, signals: dict | None) -> dict:
        """Call to score live signals during testing. Bounded score in [0, 1].

        Shapes: in  signals: dict
                out dict with "score" (float 0-1) plus weight breakdown.
        """
        return _score(signals)

    def after_finding(
        self,
        target: str,
        endpoint: str,
        vulnerability_class: str,
        signals: dict | None = None,
        validation_state: str = "observation",
        source_provenance: str | None = None,
    ) -> dict:
        """Call after a finding passes its gates. Persists to SQLite.

        Shapes: in  target: str, endpoint: str, vulnerability_class: str,
                    signals: dict, validation_state: str, source_provenance: str
                out record_finding doc dict (with "finding_id", "status").
        """
        confidence = self.STATE_CONFIDENCE.get(validation_state.lower(), 0.5)
        return self.record_finding(
            target=target,
            vuln_class=vulnerability_class,
            title=f"{vulnerability_class} @ {endpoint}",
            confidence=confidence,
            signals=signals,
            source=source_provenance or f"session:{target}",
        )

    def before_summary(self, findings: list[dict] | None) -> dict:
        """Call before writing a summary. Ranks findings by severity, then
        confidence, then score. Never mutates the input list.

        Shapes: in  findings: list[dict]
                out {"ranked": [dict], "count": int}
        """
        findings = list(findings or [])
        rank = {"critical": 5, "high": 4, "medium": 3, "low": 2, "info": 1,
                "informational": 1}
        ranked = sorted(
            findings,
            key=lambda f: (
                rank.get(str(f.get("severity", "medium")).lower(), 3),
                float(f.get("confidence", 0.0)),
                float(f.get("score", 0.0)),
            ),
            reverse=True,
        )
        return {"ranked": ranked, "count": len(ranked)}

    def after_triage(
        self,
        finding_id: str,
        feedback_type: str,
        notes: str | None = None,
        provenance: str | None = None,
    ) -> dict:
        """Call after triage feedback (accepted/duplicate/false_positive).
        Persists a triage verdict.

        Shapes: in  finding_id: str, feedback_type: str, notes: str, provenance: str
                out record_triage doc dict (with "verdict", "finding_id").
        """
        verdict = self.FEEDBACK_VERDICTS.get(feedback_type.lower(), "unverified")
        return self.record_triage(
            finding_id=finding_id,
            verdict=verdict,
            reason=notes,
            reviewer=provenance or "session",
        )

    # ---- Convenience ----------------------------------------------------
    def stats(self) -> dict:
        db = self._db()
        return {
            "findings": db.one("SELECT count(*) AS n FROM findings")["n"],
            "triage": db.one("SELECT count(*) AS n FROM triage")["n"],
            "lessons": db.one("SELECT count(*) AS n FROM lessons")["n"],
            "patterns": db.one("SELECT count(*) AS n FROM patterns")["n"],
            "schema_version": db.one("SELECT value FROM meta WHERE key = 'schema_version'")["value"],
        }

    def export_graph(self) -> dict:
        return build_graph(self._db())

    # ---- Analytics convenience -------------------------------------------

    def get_statistics(self) -> dict:
        """Alias of stats(): counts per table + schema version."""
        return self.stats()

    def get_tuning(self) -> dict:
        """Signal weights + policy (learning_engine/scoring/signals.json)."""
        from .scoring.engine import load_policy, load_weights  # noqa: PLC0415
        return {"weights": load_weights(), "policy": load_policy()}

    def get_heatmap(self) -> dict:
        """Per-class signal occurrence counts."""
        return signal_heatmap(self._db())

    def get_chains(self) -> dict:
        """Chain candidates: classes with 2+ findings + FP patterns."""
        db = self._db()
        classes = [
            {k: c[k] for k in ("vuln_class", "count", "fp_rate", "top_signals")}
            for c in per_class_stats(db) if c["count"] >= 2
        ]
        return {
            "chain_candidates": classes,
            "fp_patterns": fp_pattern_candidates(db, min_occurrences=1),
        }

    def rebuild_graph(self) -> dict:
        """Alias of export_graph()."""
        return self.export_graph()

    @property
    def analytics(self):
        """Analytics helpers bound to this engine's database."""
        from types import SimpleNamespace  # noqa: PLC0415
        return SimpleNamespace(
            highest_signal_surfaces=lambda limit=10: highest_signal_surfaces(self._db(), limit=limit),
            duplicate_heavy_patterns=lambda min_occurrences=2: duplicate_heavy_patterns(self._db(), min_occurrences=min_occurrences),
            target_summary=lambda target: target_summary(self._db(), target),
        )


# ---- Module-level defaults for pipelines --------------------------------

_engine: LearningEngine | None = None


def _default() -> LearningEngine:
    global _engine
    if _engine is None:
        _engine = LearningEngine()
        _engine.init_db()
    return _engine


def record_finding(**kwargs) -> dict:
    return _default().record_finding(**kwargs)


def record_triage(**kwargs) -> dict:
    return _default().record_triage(**kwargs)


def recall(**kwargs) -> list[dict]:
    return _default().recall(**kwargs)


def distill(min_support: int = 2) -> dict:
    return _default().distill(min_support=min_support)


def score(signals: dict | None = None) -> dict:
    return _default().score(signals)


def before_recon(target: str, techs: list[str] | None = None) -> dict:
    return _default().before_recon(target=target, techs=techs)


def during_testing(signals: dict | None = None) -> dict:
    return _default().during_testing(signals)


def after_finding(
    target: str,
    endpoint: str,
    vulnerability_class: str,
    signals: dict | None = None,
    validation_state: str = "observation",
    source_provenance: str | None = None,
) -> dict:
    return _default().after_finding(
        target=target, endpoint=endpoint, vulnerability_class=vulnerability_class,
        signals=signals, validation_state=validation_state,
        source_provenance=source_provenance,
    )


def before_summary(findings: list[dict] | None = None) -> dict:
    return _default().before_summary(findings)


def after_triage(
    finding_id: str,
    feedback_type: str,
    notes: str | None = None,
    provenance: str | None = None,
) -> dict:
    return _default().after_triage(
        finding_id=finding_id, feedback_type=feedback_type,
        notes=notes, provenance=provenance,
    )


def stats() -> dict:
    return _default().stats()