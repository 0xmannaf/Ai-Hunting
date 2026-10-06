#!/usr/bin/env python3
"""update_steps.py — the real, testable learning pipeline.

Steps (each idempotent, safe to re-run, offline-capable):

  fetch    pull new write-ups from configured sources into writeups/raw/
           (offline/sample mode: seed local sample corpus, never network)
  process  convert writeups/raw/*.md -> structured entries in writeups/processed/
           (also parses testing/<root>/<sub>/requests/*.txt -> notes/, legacy)
  index    rebuild writeups/index.md from writeups/processed/
           (also refreshes per-target testing/*/index.md, legacy)
  learn    ingest CONFIRMED metadata -> learning engine -> distill ->
           regenerate memory/report-lessons.md, refresh memory/patterns.md and
           memory/methodology.md, and REGENERATE agent-briefing.md
           (header date, knowledge-base count from index.md, biases from lessons)
  all      fetch -> process -> index -> learn

CLI:  python scripts/update_steps.py <step> [--offline] [--root DIR]
      python scripts/update_steps.py all [--offline] [--root DIR]

Functions accept an explicit `root` so tests run against temporary workspaces.
No step requires network access except `fetch` in online mode (FETCH_FEEDS).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SAMPLE_FEEDS_DIR = "writeups/feeds/sample"
RAW_DIR = "writeups/raw"
PROCESSED_DIR = "writeups/processed"
METADATA_DIR = "writeups/metadata"
INDEX_PATH = "writeups/index.md"
LESSONS_PATH = "memory/report-lessons.md"
PATTERNS_PATH = "memory/patterns.md"
METHODOLOGY_PATH = "memory/methodology.md"
BRIEFING_PATH = "agent-briefing.md"

PROCESSED_FIELDS = [
    "title", "source", "date", "entry point", "precondition", "trust boundary",
    "bypass", "proof method", "fp trap", "chain opportunity", "tags",
]

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


# ---------------------------------------------------------------------------
# fetch
# ---------------------------------------------------------------------------

def step_fetch(root: Path, offline: bool = False) -> dict:
    """Pull write-ups into writeups/raw/. Idempotent: skips existing names."""
    raw = root / RAW_DIR
    raw.mkdir(parents=True, exist_ok=True)
    sample = root / SAMPLE_FEEDS_DIR
    copied = 0

    if offline:
        if sample.is_dir():
            for src in sorted(sample.glob("*.md")):
                dst = raw / src.name
                if not dst.exists():
                    shutil.copy2(src, dst)
                    copied += 1
        return {"mode": "offline/sample", "copied": copied, "fetched": []}

    feeds = os.environ.get("FETCH_FEEDS", "").split()
    if not feeds:
        return {"mode": "no feeds configured", "copied": 0, "fetched": []}

    fetched: list[str] = []
    for url in feeds:
        name = Path(url.rstrip("/")).name or f"feed-{len(fetched)}.md"
        dst = raw / name
        if dst.exists():
            continue
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:  # noqa: S310
                data = resp.read()
            dst.write_bytes(data)
            fetched.append(url)
        except Exception as exc:  # noqa: BLE001
            print(f"[fetch] warning: failed {url} ({exc}); continuing")
    return {"mode": "online", "copied": copied, "fetched": fetched}


# ---------------------------------------------------------------------------
# process
# ---------------------------------------------------------------------------

def _parse_frontmatter(text: str) -> tuple[dict, str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    fm: dict = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            fm[key.strip().lower()] = value.strip().strip('"').strip("'")
    tags = fm.get("tags", "")
    if isinstance(tags, str):
        fm["tags"] = [t.strip() for t in tags.strip("[]").split(",") if t.strip()]
    return fm, text[m.end():]


def _derive(fm: dict, body: str, path: Path) -> dict:
    title = fm.get("title") or (re.match(r"^#\s+(.+)$", body, re.M) or [None, path.stem])[1]
    date = fm.get("date") or _now()
    return {
        "title": title,
        "source": fm.get("source", "local"),
        "date": date,
        "entry point": fm.get("entry point", "see body"),
        "precondition": fm.get("precondition", "see body"),
        "trust boundary": fm.get("trust boundary", "see body"),
        "bypass": fm.get("bypass", "see body"),
        "proof method": fm.get("proof method", "see body"),
        "fp trap": fm.get("fp trap", "see body"),
        "chain opportunity": fm.get("chain opportunity", "see body"),
        "tags": fm.get("tags", []),
    }


def _processed_entry(entry: dict) -> str:
    lines = [f"# {entry['title']}", "", f"- source: `{entry['source']}`", f"- date: {entry['date']}", ""]
    for field in PROCESSED_FIELDS:
        if field == "title":
            continue
        value = entry.get(field, "—")
        if field == "tags":
            value = ", ".join(entry.get("tags", [])) or "—"
        lines.append(f"**{field}:** {value}")
    lines += ["", "---"]
    return "\n".join(lines) + "\n"


def step_process(root: Path) -> dict:
    """writeups/raw/*.md -> structured entries in writeups/processed/. Idempotent."""
    raw = root / RAW_DIR
    processed = root / PROCESSED_DIR
    raw.mkdir(parents=True, exist_ok=True)
    processed.mkdir(parents=True, exist_ok=True)

    written = 0
    for src in sorted(raw.glob("*.md")):
        slug = src.stem
        dst = processed / f"{slug}.md"
        if dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
            continue
        text = src.read_text(encoding="utf-8")
        fm, body = _parse_frontmatter(text)
        entry = _derive(fm, body, src)
        dst.write_text(_processed_entry(entry), encoding="utf-8")
        written += 1

    # Legacy: testing/<root>/<sub>/requests/*.txt -> notes/*.md (read-only over evidence).
    parsed_legacy = 0
    for req in sorted((root / "testing").glob("*/*/requests/*.txt")):
        sub = req.parent.parent
        out = sub / "notes" / f"{req.stem}.md"
        if out.exists():
            continue
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            f"# Parsed request: {req.stem}\n\nSource: `{req}`\n\n## Raw\n```http\n"
            f"{req.read_text(encoding='utf-8')}\n```\n",
            encoding="utf-8",
        )
        parsed_legacy += 1
    return {"written": written, "legacy_parsed": parsed_legacy}


# ---------------------------------------------------------------------------
# index
# ---------------------------------------------------------------------------

def step_index(root: Path) -> dict:
    """Rebuild writeups/index.md from processed/. Idempotent by construction."""
    processed = root / PROCESSED_DIR
    processed.mkdir(parents=True, exist_ok=True)

    entries: list[dict] = []
    for f in sorted(processed.glob("*.md")):
        text = f.read_text(encoding="utf-8")
        title = (re.match(r"^#\s+(.+)$", text, re.M) or [None, f.stem])[1].strip()
        date = (re.search(r"^- date: (.+)$", text, re.M) or [None, "—"])[1].strip()
        tags = (re.search(r"^\*\*tags:\*\* (.+)$", text, re.M) or [None, "—"])[1].strip()
        entries.append({"slug": f.stem, "title": title, "date": date, "tags": tags})

    lines = [
        "# Writeups Index",
        "",
        f"> AUTO-GENERATED by scripts/update_steps.py (step index). Count: {len(entries)}.",
        "",
        f"- **Knowledge base:** {len(entries)} processed write-ups",
        "",
        "| # | Slug | Title | Date | Tags |",
        "|---|------|-------|------|------|",
    ]
    for i, e in enumerate(entries, 1):
        lines.append(f"| {i} | `{e['slug']}` | {e['title']} | {e['date']} | {e['tags']} |")
    lines.append("")
    (root / INDEX_PATH).write_text("\n".join(lines), encoding="utf-8")

    # Legacy: per-target testing/*/index.md refresh.
    targets = 0
    for target in sorted((root / "testing").glob("*/")):
        if not target.is_dir():
            continue
        idx = [f"# Index: {target.name}", ""]
        for sub in sorted(target.glob("*/")):
            if not sub.is_dir():
                continue
            idx.append(f"## {sub.name}")
            for kind in ("notes", "requests", "responses", "screenshots", "scripts",
                         "scans", "urls", "subdomains", "evidence", "reports"):
                d = sub / kind
                if d.is_dir():
                    n = len(list(d.glob("*")))
                    idx.append(f"- {kind}/: {n} files")
            for kind in ("urls", "subdomains"):
                lst = sub / f"{kind}.txt"
                if lst.exists():
                    idx.append(f"- {kind}.txt: {len(lst.read_text(encoding='utf-8').splitlines())} entries")
            idx.append("")
        (target / "index.md").write_text("\n".join(idx), encoding="utf-8")
        targets += 1
    return {"indexed": len(entries), "targets_refreshed": targets}


def _knowledge_base_count(root: Path) -> int:
    text = (root / INDEX_PATH).read_text(encoding="utf-8", errors="replace")
    m = re.search(r"Knowledge base:\*\* (\d+) processed", text)
    return int(m.group(1)) if m else 0


# ---------------------------------------------------------------------------
# learn
# ---------------------------------------------------------------------------

def step_learn(root: Path) -> dict:
    """Ingest metadata -> distill -> memory files -> regenerate agent-briefing.md."""
    from learning_engine import engine  # noqa: PLC0415

    eng = engine.LearningEngine(root=root)
    eng.init_db()

    meta_dir = root / METADATA_DIR
    ingested = 0
    triaged = 0
    if meta_dir.is_dir():
        for f in sorted(meta_dir.glob("*.json")):
            doc = json.loads(f.read_text(encoding="utf-8"))
            if doc.get("verdict") == "CONFIRMED":
                if eng.record_finding(
                    target=doc.get("target", "unknown"),
                    vuln_class=doc.get("vuln_class", "unknown"),
                    title=doc.get("title", f.stem),
                    severity=doc.get("severity", "medium"),
                    confidence=float(doc.get("confidence", 0.8)),
                    evidence=doc.get("evidence"),
                    signals=doc.get("signals"),
                    source="writeups/metadata/" + f.name,
                    finding_id=doc.get("finding_id"),
                ).get("status") == "new":
                    ingested += 1
            elif doc.get("verdict") in ("FALSE_POSITIVE", "UNVERIFIED") and doc.get("finding_id"):
                eng.record_triage(
                    finding_id=doc["finding_id"],
                    verdict=doc["verdict"].lower(),
                    reason=doc.get("reason"),
                    reviewer=doc.get("reviewer", "pipeline"),
                )
                triaged += 1

    distill = eng.distill(min_support=1)
    _write_report_lessons(root, distill, ingested, triaged)
    _refresh_patterns(root, distill)
    _touch_methodology(root)
    _regenerate_briefing(root, distill)

    stats = eng.stats()
    if eng.db is not None:
        eng.db.close()
    return {
        "ingested": ingested,
        "triaged": triaged,
        "classes": len(distill.get("classes", [])),
        "findings_in_db": stats["findings"],
    }


def _write_report_lessons(root: Path, distill: dict, ingested: int, triaged: int) -> None:
    lines = [
        "# Report Lessons (distilled)",
        "",
        "> AUTO-GENERATED by scripts/update_steps.py (step learn) via learning_engine.distill().",
        "> Do not edit by hand.",
        "",
        f"- Findings ingested this run: {ingested}",
        f"- Triage records this run: {triaged}",
        f"- Vuln classes with signal: {len(distill.get('classes', []))}",
        "",
    ]
    for c in distill.get("classes", []):
        lines.append(f"## {c['vuln_class']} (n={c['count']}, fp_rate={c['fp_rate']:.0%})")
        for k in c.get("top_signals", [])[:5]:
            lines.append(f"- signal: {k}")
        for lesson in c.get("lessons", [])[:3]:
            lines.append(f"- lesson: {lesson}")
        lines.append("")
    (root / LESSONS_PATH).write_text("\n".join(lines), encoding="utf-8")


def _refresh_patterns(root: Path, distill: dict) -> None:
    path = root / PATTERNS_PATH
    if not path.exists():
        return
    lines = ["# Patterns", "",
             "Recurring technical patterns observed across targets. Updated via learning engine",
             "distill + human review. Each entry: pattern, where it appears, why it works, countercheck.",
             "",
             "## How to use",
             "",
             "- Before testing a class, check `memory/targets/<vuln>.md` for the checklist.",
             "- If a pattern here matches your current target's stack, prioritize the related skill.",
             "",
             "## Patterns", ""]
    seen = 0
    for c in distill.get("classes", []):
        if c["count"] < 2:
            continue
        signals = ", ".join(c.get("top_signals", [])[:3]) or "none"
        lines.append(f"- **{c['vuln_class']}** (n={c['count']}, fp_rate={c['fp_rate']:.0%}): "
                     f"top signals `{signals}`.")
        seen += 1
    if not seen:
        lines.append("_(none yet — patterns appear after 2+ confirmed findings in a class)_")
    lines += ["", "## Signal co-occurrence notes",
              "", "- High-FP signals (see `FALSE_POSITIVE_DB.md`) are listed there, not here.",
              "- A signal is a pattern only after it appeared on 2+ distinct targets with",
              "  confirmed outcomes.", ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def _touch_methodology(root: Path) -> None:
    path = root / METHODOLOGY_PATH
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    marker = "> Last pipeline run:"
    text = re.sub(rf"{re.escape(marker)}.*", f"{marker} {_now()} (update_steps learn)", text)
    if marker not in text:
        text = text.rstrip() + f"\n\n{marker} {_now()} (update_steps learn)\n"
    path.write_text(text, encoding="utf-8")


def _biases_from_lessons(root: Path) -> list[str]:
    path = root / LESSONS_PATH
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    biases: list[str] = []
    for m in re.finditer(r"^## (\w+) \(n=(\d+), fp_rate=([\d.]+)%\)", text, re.M):
        biases.append(f"On {m.group(1)}: {m.group(2)} finding(s) in corpus "
                      f"(fp_rate {m.group(3)}%) — see report-lessons.md.")
    if not biases:
        biases.append("No distilled lessons yet — run the /update pipeline with CONFIRMED "
                      "metadata to build biases.")
    return biases


def _regenerate_briefing(root: Path, distill: dict) -> None:
    path = root / BRIEFING_PATH
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    count = _knowledge_base_count(root)
    text = re.sub(r"- \*\*Last updated:\*\* .*", f"- **Last updated:** {_now()}", text, count=1)
    text = re.sub(r"- \*\*Knowledge base:\*\* .*",
                  f"- **Knowledge base:** {count} processed write-ups (from writeups/index.md)",
                  text, count=1)
    biases = _biases_from_lessons(root)
    body = ["_(Regenerated by /update — learned biases from report-lessons.md + patterns.md)_"]
    body += [f"{i}. {b}" for i, b in enumerate(biases, 1)]
    block = "\n".join(body) + "\n"
    text = re.sub(
        r"(## 3\. Knowledge State \(Current Learned Biases\)\n)(.*?)(\n## 4\.)",
        lambda m: m.group(1) + "\n" + block + m.group(3),
        text, count=1, flags=re.DOTALL,
    )
    path.write_text(text, encoding="utf-8")


# ---------------------------------------------------------------------------
# pipeline
# ---------------------------------------------------------------------------

def run_all(root: Path, offline: bool = False) -> dict:
    results = {
        "fetch": step_fetch(root, offline=offline),
        "process": step_process(root),
        "index": step_index(root),
        "learn": step_learn(root),
    }
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Learning pipeline steps (idempotent)")
    parser.add_argument("step", choices=["fetch", "process", "index", "learn", "all"])
    parser.add_argument("--offline", action="store_true", help="fetch: sample/offline mode")
    parser.add_argument("--root", default=str(ROOT), help="workspace root (default: repo root)")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    if args.step == "all":
        results = run_all(root, offline=args.offline)
        for step, res in results.items():
            print(f"[update:{step}] {json.dumps(res, sort_keys=True)}")
        print("[update] done")
        return 0

    func = {"fetch": step_fetch, "process": step_process, "index": step_index, "learn": step_learn}[args.step]
    res = func(root) if args.step != "fetch" else func(root, offline=args.offline)
    print(f"[{args.step}] {json.dumps(res, sort_keys=True)}")
    print(f"[{args.step}] done")
    return 0


if __name__ == "__main__":
    sys.exit(main())