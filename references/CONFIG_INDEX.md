# Config Index — Lightweight Runtime Map

- **Version:** 1.0
- **Last Updated:** 2026-10-01
- **Purpose:** one-glance runtime map. Keep SHORT. Full detail:
  `references/MASTER_CONFIG.md`.

## Runtime load order

1. `agent-briefing.md` (first, every session)
2. `AGENTS.md` + `prioritization.md` (constitution + signal engine)
3. `runtime/opencode/loader.md` → `runtime/opencode/ORCHESTRATION.md` →
   `runtime/opencode/manifest.md` → `runtime/opencode/agents/*.md`
4. `runtime/AGENT_SKILL_ACTIVATION.md` / `runtime/AGENT_INIT_TEMPLATE.md` (on demand)
5. `references/VERIFICATION_CHECKLIST.md` (boot + pre-report)

## Active skill sources

- `skills/<skill>.md` — source mirrors
- `.agents/skills/<skill>/SKILL.md` — active runtime copies
- master-bugbounty-rules + learning-engine-integration — foundation, every hunt

## Knowledge sources

- `memory/report-lessons.md` — read FIRST (distilled memory)
- `memory/patterns.md`, `memory/methodology.md`, `memory/targets/` — guide per
  class
- `writeups/index.md` — retrieval only, never a lesson source
- `learning_engine/` — 5 hooks + SQLite memory

## Command/agent entry points

- `.opencode/commands/*.md` — hunt, scan, recon, dorking, understand, update,
  report, mindmap
- `scripts/update_steps.py` (+ `update.sh`) — intelligence pipeline
- `scripts/runtime_preflight.py` — boot gate + session bootstrap
- `scripts/skill_registry.py` — resolver/check/generate
- `.opencode.json` — chrome-devtools-mcp browser config

## Guardrails (one-liners)

- Scope: exact-host only; ambiguity = out.
- Stickiness: stay until surfaces tested or documented not-applicable.
- Skill gate: no payload before the resolver + skill load.

## Target workspace rule

- ALL artifacts under `testing/<root-domain>/<subdomain>/` (11 standard
  folders). Never project root.

## Current status

- [X] Ready for supervised autonomous hunting
- [ ] Needs boot audit (run `references/VERIFICATION_CHECKLIST.md`)