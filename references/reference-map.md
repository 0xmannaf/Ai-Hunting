# Reference Map — Cross-File Dependencies & Routing

- **Version:** 1.0
- **Last Updated:** 2026-10-01
- **Purpose:** every file's purpose, who references it, and what it points to.
  Every reference must resolve to an existing path.

## Reference conventions

| Notation | Meaning |
|----------|---------|
| `../FILE.md` | project root (`../` = up one from `references/`) |
| `FILE.md` | same directory |
| `../` alone | up one level |

## File cross-reference matrix

| File | Purpose | Referenced BY | References TO |
|------|---------|---------------|---------------|
| `agent-briefing.md` | session knowledge state | every command, loader, VERIFICATION_CHECKLIST | `AGENTS.md`, `prioritization.md`, `memory/*`, `writeups/*` |
| `AGENTS.md` | constitution | all skills, commands, ORCHESTRATION | `prioritization.md`, `memory/*`, `testing/*`, `runtime/registry.json` |
| `prioritization.md` | signal engine P1-P4 | AGENTS.md, report command, VERIFICATION_CHECKLIST | `AGENTS.md`, `runtime/registry.json`, `memory/*` |
| `runtime/opencode/ORCHESTRATION.md` | multi-agent manual | loader, manifest, AGENTS.md | `runtime/opencode/agents/*.md`, `scripts/skill_registry.py`, `memory/*` |
| `runtime/opencode/loader.md` | boot load order | agent-briefing, manifest | `opencode.json`, `.opencode.json`, `runtime/opencode/manifest.md`, `runtime/opencode/agents/*.md`, `runtime/registry.json` |
| `runtime/opencode/manifest.md` | runtime profile + agents | loader, ORCHESTRATION | `runtime/registry.json`, `runtime/opencode/ORCHESTRATION.md`, `skills/*`, `learning_engine/` |
| `references/skill-router.md` | trigger → skills | VERIFICATION_CHECKLIST, hunt command | `runtime/registry.json`, `skills/*`, `.agents/skills/*` |
| `runtime/registry.json` | canonical registry | ALL agents, resolver, CI | `skills/*`, `.agents/skills/*`, `runtime/opencode/agents/*.md`, `.opencode/commands/*.md` |
| `scripts/skill_registry.py` | resolver/check/generate | every command, ORCHESTRATION, CI | `runtime/registry.json`, `skills/*`, `.agents/skills/*` |
| `scripts/runtime_preflight.py` | boot gate + bootstrap | every command, CI | `AGENTS.md`, `memory/CONTEXT_LEDGER.md`, `logs/sessions/` |
| `skills/master-bugbounty-rules.md` | foundation rules | manifest, every session boot | `AGENTS.md`, `prioritization.md` |
| `skills/learning-engine-integration.md` | learning hooks | manifest, every session boot | `learning_engine/`, `memory/*` |
| `memory/*` | lessons/patterns/methodology/FP DB/ledger/targets | AGENTS.md, commands, engine | `writeups/*`, `testing/*` |
| `writeups/*` | corpus (raw/processed/index) | /update pipeline, learn step | `memory/*`, `agent-briefing.md` |
| `.opencode/commands/*.md` | command contracts | registry `commands`, users | `AGENTS.md`, `prioritization.md`, `scripts/*`, `runtime/*` |
| `learning_engine/` | 5 hooks + SQLite | learning-engine-integration skill, learn step | `learning_engine/scoring/signals.json`, `learning_engine/memory/learning.db` |
| `runtime/AGENT_SKILL_ACTIVATION.md` | per-agent skill activation | MASTER_CONFIG, ORCHESTRATION | `runtime/registry.json` |
| `runtime/AGENT_INIT_TEMPLATE.md` | agent definition template | MASTER_CONFIG, ORCHESTRATION | `runtime/opencode/agents/*.md` |
| `references/VERIFICATION_CHECKLIST.md` | audit & readiness | boot, pre-report | `skills/*`, `scripts/*`, `memory/*` |
| `references/MASTER_CONFIG.md` | system overview (debug only) | CONFIG_INDEX | `references/*`, `runtime/*`, `testing/*` |
| `references/CONFIG_INDEX.md` | lightweight runtime map | every session | `references/MASTER_CONFIG.md` |
| `references/ownership-map.md` | file governance | anyone editing files | all shared/runtime/target paths |
| `references/reference-map.md` | dependency matrix | link-check runs | every file above |

## Dependency note

- **Hub:** the resolver (`scripts/skill_registry.py`) and the registry
  (`runtime/registry.json`) are the hub of the system — every agent and
  command resolves through them.
- **Link check:** every reference above must resolve to an existing path.
  Run a link check (grep each `references/*.md` for `*.md`/`*.json`/`*.py`
  tokens and test existence) and report any broken references found before
  booting a session.