#!/usr/bin/env python3
"""Tests for the runtime contract: boot gate, registry/command/agent wiring,
learning engine hooks, and scoring bounds."""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts import runtime_preflight as pre  # noqa: E402
from scripts import skill_registry as sr  # noqa: E402


class TestPreflightGate(unittest.TestCase):
    def test_required_trees_exist(self):
        for rel in pre.REQUIRED_FILES:
            self.assertTrue((ROOT / rel).exists(), f"missing {rel}")
        for rel in pre.REQUIRED_DIRS:
            self.assertTrue((ROOT / rel).is_dir(), f"missing dir {rel}")

    def test_all_commands_exist(self):
        for cmd in pre.COMMANDS:
            self.assertTrue((ROOT / ".opencode" / "commands" / f"{cmd}.md").exists())

    def test_gate_passes(self):
        problems = pre.run_gate(quiet=True)
        self.assertEqual(problems, [], f"gate problems: {problems}")


class TestScopeIntake(unittest.TestCase):
    """Scope lock: ledger-scoped targets only; ambiguity and mismatches block."""

    def test_in_scope_target_allowed(self):
        allowed, reason = pre.scope_status("test.example.com")
        self.assertTrue(allowed, f"should be in scope: {reason}")

    def test_unknown_target_blocked(self):
        allowed, reason = pre.scope_status("not-in-ledger.example.org")
        self.assertFalse(allowed)
        self.assertIn("OUT OF SCOPE", reason)

    def test_out_of_scope_marker_blocked(self):
        rows = pre.load_scope_table()
        self.assertTrue(rows, "ledger scope table should have entries")
        for row in rows:
            if row["in_scope"].lower() not in ("in", "yes", "true", "1"):
                self.assertTrue(
                    pre.scope_status(row["target"])[0] is False,
                    f"{row['target']} marked out but allowed",
                )

    def test_ensure_session_creates_bootstrap(self):
        dst = pre.ensure_session(
            target="test.example.com", scenario="login form", mode="hunt",
            workspace="testing/test.example.com/www", quiet=True,
        )
        self.assertTrue(dst.exists(), f"bootstrap not created: {dst}")
        import json
        block = json.loads(dst.read_text(encoding="utf-8"))
        self.assertEqual(block["target"], "test.example.com")
        self.assertEqual(block["kind"], "session-bootstrap")
        note = ROOT / "testing/test.example.com/www/notes/bootstrap.md"
        self.assertTrue(note.exists(), "workspace bootstrap note missing")
        self.assertIn("test.example.com", note.read_text(encoding="utf-8"))

    def test_ensure_session_blocks_unknown_target(self):
        from io import StringIO
        import contextlib
        err = StringIO()
        with contextlib.redirect_stderr(err):
            code = pre.main(["--target", "example.org", "--scenario", "x",
                             "--mode", "hunt", "--ensure-session"])
        self.assertNotEqual(code, 0, "out-of-scope target must block")
        self.assertIn("BLOCKED", err.getvalue())

    def test_ensure_session_blocks_workspace_mismatch(self):
        from io import StringIO
        import contextlib
        err = StringIO()
        with contextlib.redirect_stderr(err):
            code = pre.main(["--target", "test.example.com", "--scenario", "x",
                             "--mode", "hunt",
                             "--workspace", "testing/other.example.com/www",
                             "--ensure-session"])
        self.assertNotEqual(code, 0)
        self.assertIn("workspace", err.getvalue().lower())

    def test_ensure_session_requires_target(self):
        from io import StringIO
        import contextlib
        err = StringIO()
        with contextlib.redirect_stderr(err):
            code = pre.main(["--scenario", "x", "--mode", "hunt", "--ensure-session"])
        self.assertNotEqual(code, 0)
        self.assertIn("--target", err.getvalue())


class TestRuntimeWiring(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = sr._load_registry()

    def test_agent_files_exist(self):
        for aid, meta in self.registry["agents"].items():
            self.assertTrue((ROOT / meta["file"]).exists(), f"agent {aid} file missing")

    def test_agent_skills_valid(self):
        known = set(self.registry["skills"])
        for aid, meta in self.registry["agents"].items():
            for sid in meta["skills"]:
                self.assertTrue(sid == "*" or sid in known, f"agent {aid}: bad skill {sid}")

    def test_command_files_and_routes(self):
        routes = self.registry["routes"]
        for cid, meta in self.registry["commands"].items():
            self.assertTrue((ROOT / meta["file"]).exists(), f"command {cid} file missing")
            for rid in meta["routes"]:
                self.assertIn(rid, routes, f"command {cid}: unknown route {rid}")

    def test_antigravity_manifest_lists_all_scripts(self):
        text = (ROOT / "runtime/antigravity/manifest.md").read_text(encoding="utf-8")
        for script in ("update.sh", "fetch.sh", "process.sh", "index.sh", "learn.sh",
                       "skill_registry.py", "runtime_preflight.py"):
            self.assertIn(script, text, f"manifest missing {script}")


class TestLearningEngineContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import shutil
        import tempfile
        from learning_engine import engine as le  # noqa: PLC0415
        cls._tmp = Path(tempfile.mkdtemp(prefix="le_contract_"))
        cls.le = le
        cls.eng = le.LearningEngine(root=cls._tmp)
        cls.eng.init_db()

    @classmethod
    def tearDownClass(cls):
        import shutil
        if cls.eng.db is not None:
            cls.eng.db.close()
        shutil.rmtree(cls._tmp, ignore_errors=True)

    def test_five_public_hooks_exist(self):
        for hook in ("record_finding", "record_triage", "recall", "distill", "score"):
            self.assertTrue(callable(getattr(self.eng, hook)), f"missing hook {hook}")

    def test_record_finding_roundtrip(self):
        doc = self.eng.record_finding(
            target="example.com", vuln_class="xss", title="test finding",
            severity="medium", confidence=0.9, evidence="req/1.txt",
            signals={"reflection": True, "no_encoding": True},
        )
        self.assertEqual(doc["status"], "new")
        results = self.eng.recall("xss reflection", limit=5)
        self.assertTrue(any(r.get("vuln_class") == "xss" for r in results))

    def test_record_triage(self):
        doc = self.eng.record_finding(
            target="example.com", vuln_class="sqli", title="triage target",
            severity="high", confidence=0.7,
        )
        verdict = self.eng.record_triage(
            finding_id=doc["finding_id"], verdict="false_positive",
            reason="time-based lag explained by WAF",
        )
        self.assertEqual(verdict["verdict"], "false_positive")

    def test_score_is_bounded(self):
        cases = [
            {},
            {"reflection": True, "auth_bypass": True, "rce": True, "pii": True},
            {"reflection": False, "noise": 999},
        ]
        for signals in cases:
            result = self.eng.score(signals)
            self.assertGreaterEqual(result["score"], 0.0)
            self.assertLessEqual(result["score"], 1.0)

    def test_distill_runs(self):
        out = self.eng.distill(min_support=1)
        self.assertIn("classes", out)
        self.assertIn("summary", out)

    def test_schema_version(self):
        from learning_engine.core.config import SCHEMA_VERSION  # noqa: PLC0415
        self.assertIsInstance(SCHEMA_VERSION, str)
        self.assertTrue(SCHEMA_VERSION.count(".") >= 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)