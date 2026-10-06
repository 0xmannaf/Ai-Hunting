# AGENT_INIT_TEMPLATE — Agent Definition Template

- **Version:** 1.0
- **Last Updated:** 2026-10-01
- **Purpose:** canonical structure for every agent definition file under
  `runtime/opencode/agents/*.md`. Sub-agents are briefed by instantiating this
  template.

## Template

```
# <agent-id> — briefing

Registered agent in `runtime/registry.json` (skills: <registry skills>).
Spawned at hunt_start by the orchestrator. Fire-and-forget.

## Identity
- Role: <one-line role>
- Tool whitelist: <narrow list>
- Max spawns/session: <n>
- Timeout: <default 5 min; 10 min for recon-agent/understand-agent>
- Context: isolated (never fork)

## Skill gate (mandatory pre-work)
Load ALL skills registered to this agent plus every resolver-returned path
before starting. Deferral without a reason in `memory/CONTEXT_LEDGER.md` is
not allowed.

## Procedure
<numbered steps; task template from `runtime/opencode/ORCHESTRATION.md` §4>

## Output format (structured summary only)
- Surface Tested
- Findings (type, confidence, evidence_path)
- Next Steps (suggestions)
```

## Rules

- Never spawn sub-agents (depth capped at 1).
- Return summaries only — raw details discarded, synthesis survives.
- No exploitation, no payloads — collection only, unless the role is the
  orchestrator.