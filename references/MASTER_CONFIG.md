# Master Config — Complete Agent System Overview

- **Version:** 1.0
- **Last Updated:** 2026-10-01
- **Purpose:** complete overview of the agent system. Load ONLY when debugging
  the architecture — `references/CONFIG_INDEX.md` is the lightweight runtime
  map.

## System architecture

### Configuration files in load order

| # | File | When | Role |
|---|------|------|------|
| 1 | `agent-briefing.md` | every session, first | current knowledge state |
| 2 | `AGENTS.md` | boot | constitution — highest authority |
| 3 | `prioritization.md` | boot | signal engine P1-P4 |
| 4 | `runtime/AGENT_SKILL_ACTIVATION.md` | on demand | per-agent skill loading contract |
| 5 | `runtime/AGENT_INIT_TEMPLATE.md` | on demand | agent definition template |
| 6 | `references/VERIFICATION_CHECKLIST.md` | boot + pre-report | audit & readiness gate |
| 7 | `references/skill-router.md` | per surface | trigger → skills cross-check |

### Skill sources

| Source | Role |
|--------|------|
| `skills/<skill>.md` | source mirrors (canonical text) |
| `.agents/skills/<skill>/SKILL.md` | active runtime copies (generated, checked by CI) |
| master-bugbounty-rules + learning-engine-integration | foundation pair — load first, every hunt, mandatory |

### Working directory tree

- `testing/<root-domain>/` — per-target root
- `testing/<root-domain>/<subdomain>/` — 11 standard artifact folders: `notes`,
  `requests`, `responses`, `screenshots`, `scripts`, `scans`, `wordlists`,
  `urls`, `subdomains`, `evidence`, `reports`.
- Never create target artifacts in the project root.

## Execution flow

| Phase | Window | Steps |
|-------|--------|-------|
| 1 — BOOT | <5 min | briefing → foundations (master-bugbounty-rules, learning-engine-integration) → scope lock → quick fingerprint → prior-history check → session bootstrap → READY |
| 2 — DISCOVERY↔EXPLOIT | interleaved | passive recon + JS deep analysis + tech-aware fuzzing feeding direct testing; skill trigger → attack model → test |
| 3 — DEEP EXPLOIT | continuous | bypass ladder (one variable at a time) → response-diff every test → FP-DB check → replay 2x |
| 4 — REPORT | gated by user | FP gate (AGENTS.md 10-question) → FP filter → severity calibration → rank → present |

## When to debug structure

This file is the overview. Load it ONLY when debugging the architecture —
configuration load order, skill sources, or execution phases. For day-to-day
hunting use `agent-briefing.md` + `references/CONFIG_INDEX.md` +
`runtime/opencode/loader.md`.