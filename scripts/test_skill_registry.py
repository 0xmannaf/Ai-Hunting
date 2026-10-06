#!/usr/bin/env python3
"""Tests for scripts/skill_registry.py — deterministic resolver + registry integrity."""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts import skill_registry as sr  # noqa: E402


class TestRegistryIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = sr._load_registry()

    def test_registry_parses(self):
        self.assertIsInstance(self.registry, dict)
        self.assertEqual(self.registry["version"], "1.0.0")

    def test_check_passes(self):
        problems = sr.check(self.registry)
        self.assertEqual(problems, [], f"registry problems: {problems}")

    def test_skill_count_within_budget(self):
        n = len(self.registry["skills"])
        self.assertGreaterEqual(n, 10)
        self.assertLessEqual(n, 20)

    def test_all_aliases_bidirectional(self):
        for alias, sid in self.registry["aliases"].items():
            self.assertIn(sid, self.registry["skills"])
            self.assertIn(alias, self.registry["skills"][sid]["aliases"])

    def test_phases_and_severities_valid(self):
        for sid, meta in self.registry["skills"].items():
            self.assertIn(meta["phase"], ("recon", "exploit"))
            self.assertIn(meta["severity"], ("info", "low", "medium", "high", "critical"))

    def test_routes_reference_known_skills(self):
        known = set(self.registry["skills"])
        for route, sids in self.registry["routes"].items():
            self.assertTrue(sids, f"route {route} empty")
            for sid in sids:
                self.assertIn(sid, known, f"route {route} -> unknown {sid}")

    def test_every_skill_reachable_by_some_route(self):
        known = set(self.registry["skills"])
        reached = {s for sids in self.registry["routes"].values() for s in sids}
        self.assertEqual(known, reached)


class TestResolve(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = sr._load_registry()

    def test_exact_route(self):
        self.assertEqual(sr.resolve(self.registry, "web"), self.registry["routes"]["web"])

    def test_case_insensitive(self):
        self.assertEqual(sr.resolve(self.registry, "WEB"), self.registry["routes"]["web"])

    def test_alias_resolves_to_route(self):
        result = sr.resolve(self.registry, "osint")
        self.assertIn("dorking", result)

    def test_fuzzy_tokens(self):
        result = sr.resolve(self.registry, "sql injection")
        self.assertIn("sqli", result)

    def test_unknown_scenario_empty(self):
        self.assertEqual(sr.resolve(self.registry, "zzz-not-a-scenario"), [])

    def test_deterministic(self):
        a = sr.resolve(self.registry, "api")
        b = sr.resolve(self.registry, "api")
        self.assertEqual(a, b)

    def test_full_route_covers_all_skills(self):
        full = sr.resolve(self.registry, "full")
        self.assertEqual(set(full), set(self.registry["skills"]))


class TestResolveWithOptions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = sr._load_registry()

    def test_foundation_skills_always_included(self):
        foundation = self.registry["routes"]["start"]
        for scenario in ("web", "api", "auth", "upload"):
            sids = sr.resolve_with_options(self.registry, scenario, with_foundation=True)
            self.assertTrue(set(foundation).issubset(set(sids)),
                            f"foundation missing for {scenario}: {set(foundation) - set(sids)}")
            self.assertEqual(sids[:len(foundation)], foundation)

    def test_mode_all_default(self):
        self.assertEqual(
            sr.resolve_with_options(self.registry, "web"),
            sr.resolve(self.registry, "web"),
        )

    def test_mode_recon_filters_phase(self):
        sids = sr.resolve_with_options(self.registry, "full", mode="recon")
        self.assertTrue(sids)
        for sid in sids:
            self.assertEqual(self.registry["skills"][sid]["phase"], "recon")

    def test_mode_test_keeps_exploit_only(self):
        sids = sr.resolve_with_options(self.registry, "full", mode="test")
        self.assertTrue(sids)
        for sid in sids:
            self.assertEqual(self.registry["skills"][sid]["phase"], "exploit")
        for sid in self.registry["routes"]["start"]:
            self.assertNotIn(sid, sids)

    def test_paths_only_resolves_to_existing_files(self):
        for scenario in ("web", "api", "graphql", "jwt", "file-upload"):
            paths = [
                ROOT / self.registry["skills"][sid]["file"]
                for sid in sr.resolve_with_options(self.registry, scenario, mode="test")
            ]
            self.assertTrue(paths, f"no skills for {scenario}")
            for p in paths:
                self.assertTrue(p.exists(), f"missing skill file: {p}")


class TestResolveCli(unittest.TestCase):
    def test_cli_paths_only_outputs_existing_files(self):
        from scripts.skill_registry import main as sr_main
        from io import StringIO
        import contextlib
        buf = StringIO()
        with contextlib.redirect_stdout(buf):
            code = sr_main(["resolve", "api", "--mode", "test", "--paths-only"])
        self.assertEqual(code, 0)
        for line in buf.getvalue().splitlines():
            self.assertTrue(Path(line.strip()).exists(), f"path does not exist: {line}")

    def test_cli_unknown_scenario_degrades_gracefully(self):
        from scripts.skill_registry import main as sr_main
        from io import StringIO
        import contextlib
        err = StringIO()
        with contextlib.redirect_stderr(err):
            code = sr_main(["resolve", "zzz-not-a-scenario", "--paths-only"])
        self.assertEqual(code, 2)
        self.assertIn("no skills", err.getvalue())

    def test_cli_foundation_flag(self):
        from scripts.skill_registry import main as sr_main
        from io import StringIO
        import contextlib
        buf = StringIO()
        with contextlib.redirect_stdout(buf):
            code = sr_main(["resolve", "web", "--with-foundation", "--paths-only"])
        self.assertEqual(code, 0)
        lines = buf.getvalue().splitlines()
        foundation = sr._load_registry()["routes"]["start"]
        for sid in foundation:
            self.assertTrue(any(Path(l).name == f"{sid}.md" for l in lines))


class TestGenerate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = sr._load_registry()

    def test_generate_writes_runtime_copies(self):
        written = sr.generate(self.registry)
        self.assertEqual(len(written), len(self.registry["skills"]))
        for dst in written:
            self.assertTrue(dst.exists())
        problems = sr.check(self.registry)
        self.assertEqual(problems, [])

    def test_runtime_copy_matches_source(self):
        for sid, meta in self.registry["skills"].items():
            src = ROOT / meta["file"]
            dst = sr.SKILLS_RUNTIME / sid / "SKILL.md"
            self.assertEqual(dst.read_text(encoding="utf-8"),
                             src.read_text(encoding="utf-8"))


class TestFrontmatter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = sr._load_registry()

    def test_skill_frontmatter_matches_registry(self):
        for sid, meta in self.registry["skills"].items():
            text = (ROOT / meta["file"]).read_text(encoding="utf-8")
            self.assertTrue(text.startswith("---"), f"{sid}: missing frontmatter")
            fm = text.split("---", 2)[1]
            for field, want in (("id", sid), ("phase", meta["phase"]),
                                ("severity", meta["severity"])):
                self.assertIn(f"{field}: {want}", fm, f"{sid}: frontmatter {field} mismatch")
            self.assertIn(f"name: {meta['name']}", fm, f"{sid}: frontmatter name mismatch")


if __name__ == "__main__":
    unittest.main(verbosity=2)