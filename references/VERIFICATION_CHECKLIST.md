# Verification Checklist — Audit & Readiness

- **Version:** 1.0
- **Last Updated:** 2026-10-01
- **Purpose:** boot-time and pre-report readiness gate. Run the checklist
  before any hunt and before any report.

## Skill coverage

- [ ] `skills/` mirrors exist for every skill in `runtime/registry.json`
- [ ] `.agents/skills/` active runtime folders exist for every registered skill
- [ ] master-bugbounty-rules loads FIRST every session
- [ ] learning-engine-integration loads SECOND every session
- [ ] resolver (`scripts/skill_registry.py resolve --scenario "<surface>" --mode
      test --paths-only`) returns existing files before every test
- [ ] deferred skills recorded with reasons in `memory/CONTEXT_LEDGER.md`

## Startup & hunting rules

- [ ] `agent-briefing.md` read FIRST (non-negotiable)
- [ ] `AGENTS.md` defines the workflow — constitution wins on conflict
- [ ] 4-phase interleaved flow: BOOT → DISCOVERY↔EXPLOIT → DEEP EXPLOIT →
      REPORT (gated)
- [ ] exact-host scope locked; no `*.<root>` fuzzing without approval
- [ ] target stickiness: stay until surfaces tested or documented not-applicable
- [ ] prior-data check in `testing/` before fresh recon
- [ ] session bootstrap created via
      `scripts/runtime_preflight.py --target ... --ensure-session`
- [ ] per-target `testing/<root-domain>/<subdomain>/MINDMAP.md` maintained
- [ ] every discovered JS file deep-analyzed immediately (auth/API bundles
      first)
- [ ] skill gates enforced before any payload

## Learning & update pipeline

- [ ] `memory/report-lessons.md` read BEFORE processed write-ups
- [ ] `memory/patterns.md`, `memory/methodology.md`, `memory/targets/` guide
      each test class
- [ ] `writeups/index.md` is retrieval only — never a lesson source
- [ ] raw → processed → index → learn flow via `scripts/update_steps.py`
- [ ] `/update` rebuilds `agent-briefing.md` (date, knowledge count, biases)
- [ ] learning-engine hooks called every hunt
      (`before_recon`, `during_testing`, `after_finding`, `before_summary`,
      `after_triage`)

## Validation & reporting

- [ ] scanner output treated as LEADS, never findings
- [ ] FP filter + evidence validation + evidence hygiene applied BEFORE
      severity assignment
- [ ] response-diff (baseline vs attack) for every claimed signal
- [ ] FP-DB signature-hash check before any promotion beyond LEAD
- [ ] structured summaries in `notes/` — no auto-reports
- [ ] report skills/commands used ONLY when the user requests a report
- [ ] minimum reportability bar met: raw HTTP proof + real impact +
      representative contexts

---

## Current Status

```
[ ] NOT READY — fix the unchecked items above before proceeding
[X] Ready for supervised autonomous hunting
```

> Readiness requires ALL skill-coverage and startup boxes checked. Validation
> boxes are per-report gates, not boot gates.