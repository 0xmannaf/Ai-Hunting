#!/usr/bin/env python3
"""Tests for learning_engine session hooks: shapes, bounds, SQLite persistence.

Offline-only: uses temporary SQLite DBs under tmp_path, no network, no live
targets. The documented public API is:
  before_recon(target, techs), during_testing(signals),
  after_finding(target, endpoint, vulnerability_class, signals,
                validation_state, source_provenance),
  before_summary(findings), after_triage(finding_id, feedback_type, notes,
                                         provenance)
"""

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from learning_engine import engine as le  # noqa: E402
from learning_engine.core.storage import Database  # noqa: E402


def _fresh_engine(tmp: Path) -> le.LearningEngine:
    eng = le.LearningEngine(root=tmp)
    eng.init_db()
    return eng


def _close_engine(eng: le.LearningEngine) -> None:
    if eng.db is not None:
        eng.db.close()
        eng.db = None


class _EngineTestCase(unittest.TestCase):
    """Hermetic engine tests: each test gets a fresh temp workspace."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="le_test_"))
        self.eng = _fresh_engine(self.tmp)

    def tearDown(self):
        _close_engine(self.eng)
        shutil.rmtree(self.tmp, ignore_errors=True)


class TestSessionHooksShapes(_EngineTestCase):
    def test_all_five_documented_hooks_exist(self):
        for hook in ("before_recon", "during_testing", "after_finding",
                     "before_summary", "after_triage"):
            self.assertTrue(callable(getattr(self.eng, hook)), f"missing hook {hook}")

    def test_before_recon_shape(self):
        out = self.eng.before_recon("example.com", techs=["react", "node"])
        self.assertEqual(out["target"], "example.com")
        self.assertEqual(out["techs"], ["react", "node"])
        self.assertIsInstance(out["relevant_lessons"], list)
        self.assertIsInstance(out["suggested_classes"], list)
        self.assertIs(out["ok"], True)

    def test_before_recon_default_techs(self):
        out = self.eng.before_recon("example.com")
        self.assertEqual(out["techs"], [])

    def test_during_testing_shape_and_bound(self):
        for signals in ({}, {"reflection": True, "auth_bypass": True},
                        {"noise": 999, "rce": True}):
            out = self.eng.during_testing(signals)
            self.assertIn("score", out)
            self.assertGreaterEqual(out["score"], 0.0)
            self.assertLessEqual(out["score"], 1.0)

    def test_during_testing_none(self):
        out = self.eng.during_testing(None)
        self.assertGreaterEqual(out["score"], 0.0)

    def test_after_finding_shape_and_persist(self):
        doc = self.eng.after_finding(
            target="example.com", endpoint="/api/invoices/42",
            vulnerability_class="idor", signals={"object_reference_guessable": True},
            validation_state="confirmed", source_provenance="test:acct-a",
        )
        self.assertIn("finding_id", doc)
        self.assertEqual(doc["status"], "new")
        self.assertAlmostEqual(doc["confidence"], 0.7, places=2)
        rows = self.eng.recall("invoice idor", limit=5)
        self.assertTrue(any(r.get("vuln_class") == "idor" for r in rows))

    def test_after_finding_state_mapping(self):
        for state, expect in (("observation", 0.10), ("lead", 0.25),
                              ("high_confidence_lead", 0.50), ("confirmed", 0.70),
                              ("validated", 0.90), ("reportable", 0.95)):
            doc = self.eng.after_finding(
                target="t", endpoint="e", vulnerability_class="xss",
                validation_state=state,
            )
            self.assertAlmostEqual(doc["confidence"], expect, places=2, msg=state)

    def test_before_summary_ranks(self):
        findings = [
            {"severity": "medium", "confidence": 0.9, "score": 0.4, "title": "m"},
            {"severity": "critical", "confidence": 0.5, "score": 0.3, "title": "c"},
            {"severity": "low", "confidence": 1.0, "score": 0.9, "title": "l"},
        ]
        out = self.eng.before_summary(findings)
        self.assertEqual(out["count"], 3)
        self.assertEqual(out["ranked"][0]["title"], "c")
        self.assertEqual(out["ranked"][2]["title"], "l")
        self.assertEqual(findings[0]["title"], "m")  # input not mutated

    def test_before_summary_empty_and_none(self):
        self.assertEqual(self.eng.before_summary([])["count"], 0)
        self.assertEqual(self.eng.before_summary(None)["count"], 0)

    def test_after_triage_shape_and_persist(self):
        doc = self.eng.after_finding(
            target="t", endpoint="e", vulnerability_class="sqli",
            validation_state="lead",
        )
        out = self.eng.after_triage(
            finding_id=doc["finding_id"], feedback_type="false_positive",
            notes="time lag explained by WAF", provenance="triage:test",
        )
        self.assertEqual(out["finding_id"], doc["finding_id"])
        self.assertEqual(out["verdict"], "false_positive")
        verdict = le.latest_verdict(self.eng._db(), doc["finding_id"])
        self.assertEqual(verdict["verdict"], "false_positive")

    def test_after_triage_feedback_mapping(self):
        mapping = {"accepted": "confirmed", "duplicate": "unverified",
                   "false_positive": "false_positive", "informational": "unverified",
                   "unknown_type": "unverified"}
        for fb, expect in mapping.items():
            doc = self.eng.after_finding(target="t", endpoint="e",
                                         vulnerability_class="xss",
                                         validation_state="confirmed")
            out = self.eng.after_triage(finding_id=doc["finding_id"],
                                        feedback_type=fb)
            self.assertEqual(out["verdict"], expect, msg=fb)


class TestPersistence(_EngineTestCase):
    def test_findings_and_triage_persist_to_sqlite(self):
        db_path = self.eng.db_path
        self.assertTrue(db_path.exists())

        docs = []
        for cls in ("xss", "idor", "ssrf"):
            docs.append(self.eng.record_finding(
                target="example.com", vuln_class=cls, title=f"finding {cls}",
                severity="high", confidence=0.9,
                signals={cls: True},
            ))
        self.eng.record_triage(finding_id=docs[0]["finding_id"],
                               verdict="confirmed", reason="ok")
        self.eng.record_triage(finding_id=docs[1]["finding_id"],
                               verdict="false_positive", reason="benign")

        db = Database(db_path)
        try:
            n_findings = db.one("SELECT count(*) AS n FROM findings")["n"]
            n_triage = db.one("SELECT count(*) AS n FROM triage")["n"]
        finally:
            db.close()
        self.assertEqual(n_findings, 3)
        self.assertEqual(n_triage, 2)

    def test_retrieval_returns_seeded_entries(self):
        self.eng.record_finding(
            target="example.com", vuln_class="ssrf", title="pdf logoUrl fetch",
            severity="high", confidence=0.9,
            signals={"ssrf_metadata": True},
            source="writeups/metadata/f-sample-ssrf.json",
        )
        results = self.eng.recall("pdf ssrf", limit=5)
        self.assertTrue(results)
        kinds = {r["kind"] for r in results}
        self.assertTrue(kinds & {"finding", "lesson"})

    def test_distill_aggregates_classes(self):
        self.eng.record_finding(target="a.com", vuln_class="xss", title="x1",
                                severity="medium", confidence=0.8,
                                signals={"reflection": True})
        self.eng.record_finding(target="b.com", vuln_class="xss", title="x2",
                                severity="high", confidence=0.9,
                                signals={"reflection": True, "no_output_encoding": True})
        out = self.eng.distill(min_support=2)
        classes = {c["vuln_class"]: c for c in out["classes"]}
        self.assertIn("xss", classes)
        self.assertEqual(classes["xss"]["count"], 2)
        self.assertIn("reflection", classes["xss"]["top_signals"])


class TestScoringWeights(unittest.TestCase):
    def test_weights_loaded_from_signals_json(self):
        signals_path = ROOT / "learning_engine/scoring/signals.json"
        data = json.loads(signals_path.read_text(encoding="utf-8"))
        self.assertIn("weights", data)
        self.assertIn("policy", data)
        for w in data["weights"].values():
            self.assertLessEqual(w, 0.50)

    def test_score_never_exceeds_ceiling(self):
        tmp = Path(tempfile.mkdtemp(prefix="le_score_"))
        eng = _fresh_engine(tmp)
        try:
            heavy = {k: True for k in
                     ("rce", "auth_bypass", "sql_injection", "pii_exposure",
                      "ssrf_metadata", "unrestricted_upload",
                      "privilege_escalation", "default_credentials",
                      "object_reference_guessable", "jwt_alg_none")}
            out = eng.score(heavy)
            self.assertLessEqual(out["score"], 1.0)
            self.assertGreaterEqual(out["score"], 0.0)
        finally:
            _close_engine(eng)
            shutil.rmtree(tmp, ignore_errors=True)

    def test_auto_escalation_boosts_matched_weight(self):
        from learning_engine.scoring.engine import BOOSTS, weight_for
        base = weight_for("auth_bypass")
        tmp = Path(tempfile.mkdtemp(prefix="le_boost_"))
        eng = _fresh_engine(tmp)
        try:
            boosted = eng.score({"auth_bypass": True})["matched"]["auth_bypass"]
            self.assertGreater(boosted, base)
            self.assertAlmostEqual(boosted, base * (1 + BOOSTS["auth_bypass"]), places=4)
            self.assertLessEqual(eng.score({"auth_bypass": True})["score"], 1.0)
        finally:
            _close_engine(eng)
            shutil.rmtree(tmp, ignore_errors=True)


class TestAnalyticsApis(_EngineTestCase):
    def _seed(self):
        docs = []
        for i in range(3):
            docs.append(self.eng.record_finding(
                target="example.com", vuln_class="ssrf",
                title=f"ssrf {i}", severity="high", confidence=0.9,
                signals={"ssrf_metadata": True, "chainable": True}))
        self.eng.record_finding(
            target="example.com", vuln_class="xss", title="xss 1",
            severity="medium", confidence=0.7, signals={"reflection": True})
        self.eng.record_triage(finding_id=docs[0]["finding_id"],
                               verdict="confirmed", reason="ok")
        self.eng.record_triage(finding_id=docs[1]["finding_id"],
                               verdict="unverified", reason="duplicate")
        self.eng.record_triage(finding_id=docs[2]["finding_id"],
                               verdict="false_positive", reason="benign")

    def test_get_statistics(self):
        self._seed()
        stats = self.eng.get_statistics()
        self.assertEqual(stats["findings"], 4)
        self.assertEqual(stats["triage"], 3)

    def test_get_tuning(self):
        tuning = self.eng.get_tuning()
        self.assertIn("weights", tuning)
        self.assertIn("policy", tuning)
        self.assertIn("rce", tuning["weights"])

    def test_get_heatmap(self):
        self._seed()
        heat = self.eng.get_heatmap()
        self.assertIn("ssrf", heat)
        self.assertEqual(heat["ssrf"]["ssrf_metadata"], 3)

    def test_get_chains(self):
        self._seed()
        chains = self.eng.get_chains()
        self.assertTrue(any(c["vuln_class"] == "ssrf" for c in chains["chain_candidates"]))
        self.assertTrue(any(p["signal"] == "ssrf_metadata" for p in chains["fp_patterns"]))

    def test_rebuild_graph(self):
        self._seed()
        graph = self.eng.rebuild_graph()
        self.assertIn("nodes", graph)
        self.assertIn("edges", graph)

    def test_analytics_helpers(self):
        self._seed()
        surfaces = self.eng.analytics.highest_signal_surfaces(limit=5)
        self.assertEqual(surfaces[0]["vuln_class"], "ssrf")
        dups = self.eng.analytics.duplicate_heavy_patterns(min_occurrences=1)
        self.assertTrue(any(d["signal"] == "ssrf_metadata" for d in dups))
        summary = self.eng.analytics.target_summary("example.com")
        self.assertEqual(summary["total_findings"], 4)
        self.assertEqual(summary["target"], "example.com")


if __name__ == "__main__":
    unittest.main(verbosity=2)