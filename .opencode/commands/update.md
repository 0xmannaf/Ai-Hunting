---
description: Full intelligence update - fetch, process, index, and learn from write-ups
agent: build
---

# Autonomous Intelligence Update

Target or notes:
$ARGUMENTS

Full intelligence pipeline: fetch -> process -> index -> learn -> briefing.
Safe, idempotent, re-runnable.

## Mandates

- Read `agent-briefing.md`; load master rules + learning-engine hooks.
- Verify `python scripts/skill_registry.py check` passes.
- Run `python scripts/runtime_preflight.py --mode update --ensure-session`
  (no target needed; stop if blocked).
- Resolve `python scripts/skill_registry.py resolve --scenario
  "write-up intelligence update" --mode update --paths-only`; load every
  returned skill.

## Pipeline (run `scripts/update.sh` or equivalent autonomously)

1. **a. fetch** — new write-ups from the configured public sources into
   `writeups/raw/`, organized by source:
   `writeups/raw/github/`, `hackerone/`, `medium/`, `yeswehack/`, `bugboard/`,
   `projectzero/`, `vickieli/`, `nahamsec/`, `cobalt/`, `cloudflare/`, etc.
   Save as `writeups/raw/[source]/[topic]_[timestamp].md`.
2. **b. process** — raw -> structured files under `writeups/processed/` with
   triple-layer dedup: exact URL, normalized title, content hash
   (SHA256 of first 300 chars).
3. **c. index** — rebuild `writeups/index.md` as a TABLE: Title, Vuln Type,
   Target, Source.
4. **d. learn** — extract lessons into `memory/report-lessons.md`.
5. **e. update** `memory/methodology.md` and `memory/patterns.md`.
6. **f. generate/refresh** `memory/targets/<vuln>.md` checklists ONLY for
   vulnerability types appearing 3+ times.
7. **g. briefing** — update timestamp + knowledge count in
   `agent-briefing.md`. Static sections PRESERVED, never overwritten.

## After the pipeline

1. Run the learning-engine audit in report-only mode:
   `python learning_engine/scripts/audit_learning_engine.py --report-only`
   (if present).
2. Re-read `agent-briefing.md`.
3. Record the update summary in the session `notes/`.

## Output (session notes)

- Fetch status + sources queried; per-source new write-ups; processing status
  (new/skipped/errors); index total; memory files updated; top categories;
  briefing timestamp confirmation.