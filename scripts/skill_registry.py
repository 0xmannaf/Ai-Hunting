#!/usr/bin/env python3
"""skill_registry.py — deterministic scenario -> skills resolver.

Subcommands:
  check      validate registry consistency (skills exist, aliases resolve,
             routes reference known skills, runtime copies in sync)
  resolve    <scenario> -> ordered list of skill ids + playbook paths
  generate   write .agents/skills/<id>/SKILL.md from skills/<id>.md
  list       dump registry (skills / aliases / routes / agents / commands)

Exit codes: 0 ok, 1 check failure, 2 usage/parse error, 3 missing files.
No side effects beyond `generate`.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = ROOT / "runtime" / "registry.json"
SKILLS_SOURCE = ROOT / "skills"
SKILLS_RUNTIME = ROOT / ".agents" / "skills"

TOKEN_RE = re.compile(r"[a-z0-9]+")


def _load_registry() -> dict:
    if not REGISTRY_PATH.exists():
        sys.exit(f"registry not found: {REGISTRY_PATH}")
    try:
        return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        sys.exit(f"registry is not valid JSON: {exc}")


def _skill_file(registry: dict, skill_id: str) -> Path:
    return ROOT / registry["skills"][skill_id]["file"]


def _tokens(*values: str) -> set[str]:
    return {t for v in values if v for t in TOKEN_RE.findall(v.lower())}


def check(registry: dict) -> list[str]:
    """Return list of problems (empty = healthy)."""
    problems: list[str] = []
    skills = registry.get("skills", {})
    aliases = registry.get("aliases", {})
    routes = registry.get("routes", {})
    agents = registry.get("agents", {})
    commands = registry.get("commands", {})

    if not skills:
        problems.append("registry has no skills")

    for sid, meta in skills.items():
        f = ROOT / meta.get("file", "")
        if not f.exists():
            problems.append(f"skill '{sid}': file missing -> {f}")
        for field in ("name", "phase", "severity", "aliases"):
            if field not in meta:
                problems.append(f"skill '{sid}': missing field '{field}'")
        for alias in meta.get("aliases", []):
            if aliases.get(alias) != sid:
                problems.append(f"skill '{sid}': alias '{alias}' not mapped to it in aliases")

    for alias, sid in aliases.items():
        if sid not in skills:
            problems.append(f"alias '{alias}' -> unknown skill '{sid}'")
        elif alias not in skills[sid].get("aliases", []):
            problems.append(f"alias '{alias}' not declared in skill '{sid}' aliases")

    for route, sids in routes.items():
        if not sids:
            problems.append(f"route '{route}' is empty")
        for sid in sids:
            if sid not in skills:
                problems.append(f"route '{route}' -> unknown skill '{sid}'")

    for aid, meta in agents.items():
        f = ROOT / meta.get("file", "")
        if not f.exists():
            problems.append(f"agent '{aid}': file missing -> {f}")
        for sid in meta.get("skills", []):
            if sid != "*" and sid not in skills:
                problems.append(f"agent '{aid}': unknown skill '{sid}'")

    for cid, meta in commands.items():
        f = ROOT / meta.get("file", "")
        if not f.exists():
            problems.append(f"command '{cid}': file missing -> {f}")
        for rid in meta.get("routes", []):
            if rid not in routes:
                problems.append(f"command '{cid}': unknown route '{rid}'")

    for sid in skills:
        runtime_copy = SKILLS_RUNTIME / sid / "SKILL.md"
        source = _skill_file(registry, sid)
        if not runtime_copy.exists():
            problems.append(f"runtime copy missing: {runtime_copy} (run 'generate')")
        elif runtime_copy.read_text(encoding="utf-8") != source.read_text(encoding="utf-8"):
            problems.append(f"runtime copy out of sync: {runtime_copy} (run 'generate')")

    return problems


def resolve(registry: dict, scenario: str) -> list[str]:
    """Ordered skill ids for a scenario. Exact route -> alias -> fuzzy tokens."""
    scenario = scenario.strip().lower()
    routes = registry.get("routes", {})
    skills = registry.get("skills", {})

    if scenario in routes:
        return list(routes[scenario])

    if scenario in registry.get("aliases", {}):
        sid = registry["aliases"][scenario]
        for route, sids in routes.items():
            if sid in sids:
                return list(sids)
        return [sid]

    q = _tokens(scenario)
    if not q:
        return []
    best: list[tuple[int, str]] = []
    for sid, meta in skills.items():
        score = len(q & _tokens(sid, meta["name"], *meta.get("tags", [])))
        if score:
            best.append((score, sid))
    best.sort(key=lambda t: (-t[0], t[1]))
    return [sid for _, sid in best]


def resolve_with_options(
    registry: dict,
    scenario: str,
    mode: str = "all",
    with_foundation: bool = False,
) -> list[str]:
    """Resolve with the skill-gate options used by the hunt flow.

    mode: 'recon' keeps recon-phase skills only; 'test'/'hunt' keeps
          exploit-phase skills only; 'all' keeps everything.
    with_foundation: prepend the foundation skills (route 'start'), deduped.
    """
    skills = registry.get("skills", {})
    sids = resolve(registry, scenario)
    if mode in ("recon", "test", "hunt"):
        wanted = "recon" if mode == "recon" else "exploit"
        sids = [sid for sid in sids if skills.get(sid, {}).get("phase") == wanted]
    if with_foundation:
        foundation = list(registry.get("routes", {}).get("start", []))
        sids = foundation + [sid for sid in sids if sid not in foundation]
    return sids


def generate(registry: dict, skill_ids: list[str] | None = None) -> list[Path]:
    """Copy skill sources to .agents/skills/<id>/SKILL.md. Returns written paths."""
    skills = registry["skills"]
    ids = skill_ids or list(skills)
    missing = [sid for sid in ids if sid not in skills]
    if missing:
        sys.exit(f"unknown skill ids: {', '.join(missing)}")
    written: list[Path] = []
    for sid in ids:
        src = _skill_file(registry, sid)
        if not src.exists():
            sys.exit(f"source missing for skill '{sid}': {src}")
        dst = SKILLS_RUNTIME / sid / "SKILL.md"
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        written.append(dst)
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Deterministic scenario -> skills resolver")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("check", help="validate registry consistency")
    p_resolve = sub.add_parser("resolve", help="resolve a scenario to skill ids")
    p_resolve.add_argument("scenario", nargs="?", help="scenario (positional or --scenario)")
    p_resolve.add_argument("--scenario", dest="scenario_flag", help="scenario as a flag (alias)")
    p_resolve.add_argument("--mode", choices=["all", "recon", "test", "hunt",
                                              "update", "report"],
                           default="all",
                           help="phase filter (test/hunt -> exploit phase; "
                                "update/report -> all phases)")
    p_resolve.add_argument("--paths-only", action="store_true",
                           help="print only the resolved playbook file paths")
    p_resolve.add_argument("--with-foundation", action="store_true",
                           help="prepend foundation skills (route 'start')")
    p_gen = sub.add_parser("generate", help="write .agents/skills runtime copies")
    p_gen.add_argument("--skills", nargs="*", default=None)
    p_list = sub.add_parser("list", help="dump registry")
    p_list.add_argument("--section", choices=["skills", "aliases", "routes", "agents", "commands"])

    args = parser.parse_args(argv)
    registry = _load_registry()

    if args.cmd == "check":
        problems = check(registry)
        for p in problems:
            print(f"[FAIL] {p}")
        print(f"checked: {len(registry.get('skills', {}))} skills, "
              f"{len(registry.get('routes', {}))} routes, "
              f"{len(registry.get('aliases', {}))} aliases")
        return 1 if problems else 0

    if args.cmd == "resolve":
        scenario = args.scenario or args.scenario_flag
        if not scenario:
            print("resolve: missing scenario", file=sys.stderr)
            return 2
        sids = resolve_with_options(
            registry, scenario, mode=args.mode, with_foundation=args.with_foundation,
        )
        if not sids:
            print(f"resolve: no skills for scenario '{scenario}'", file=sys.stderr)
            return 2
        for sid in sids:
            path = ROOT / registry["skills"][sid]["file"]
            print(path if args.paths_only else f"{sid}\t{path}")
        return 0

    if args.cmd == "generate":
        for dst in generate(registry, args.skills):
            print(f"[gen] {dst}")
        return 0

    if args.cmd == "list":
        section = args.section
        if section is None:
            print(json.dumps(registry, indent=2, ensure_ascii=False))
            return 0
        data = registry.get(section, {})
        for key in sorted(data):
            print(f"{key}\t{json.dumps(data[key], ensure_ascii=False)}")
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())