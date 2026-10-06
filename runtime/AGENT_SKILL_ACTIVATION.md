# AGENT_SKILL_ACTIVATION — Per-Agent Skill Loading Contract

- **Version:** 1.0
- **Last Updated:** 2026-10-01
- **Purpose:** how every agent (orchestrator + 5 sub-agents) activates skills
  before work. Consistent with `runtime/registry.json` (authoritative),
  `runtime/opencode/ORCHESTRATION.md`, and `AGENTS.md` §4.

## Contract

1. Before ANY test, answer: "What skills does this surface trigger?" → run
   `python scripts/skill_registry.py resolve --scenario "<surface>" --mode test
   --paths-only`.
2. Load EVERY returned skill from `skills/<skill>.md` or
   `.agents/skills/<skill>/SKILL.md`.
3. Sub-agents MUST additionally load ALL skills registered to their role in
   `runtime/registry.json` → `agents[<id>].skills`.
4. A sub-agent may not begin until its skill gate is loaded, or the deferral
   is recorded in `memory/CONTEXT_LEDGER.md` with the reason.
5. Foundation order is fixed: master-bugbounty-rules FIRST,
   learning-engine-integration SECOND.
6. No payload before the gate passes. Never bulk-load skills at boot — load on
   demand as surfaces trigger them.

## Deferral format (`memory/CONTEXT_LEDGER.md`)

`| <timestamp> | <session> | <target> | defer | <surface> | <skill(s)> | <reason> | — |`