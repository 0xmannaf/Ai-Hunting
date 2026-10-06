# opencode Runtime Loader

Loads the opencode side of the hunting runtime: agents, commands, and MCP wiring.

## Load order

1. `opencode.json` — MCP servers (`chrome-devtools`) and tool policy.
2. `.opencode.json` — chrome-devtools-mcp browser/capture defaults.
3. `runtime/opencode/manifest.md` — agent + command manifest (this layer).
4. `runtime/opencode/agents/*.md` — agent definitions.
5. `runtime/registry.json` — canonical skill/route state (read-only here; edited
   via `scripts/skill_registry.py`).

## Contracts

- **Agents** in `agents/*.md` declare `skills` from `registry.json`; drift fails CI.
- **Commands** live in `.opencode/commands/*.md`; each maps to registry `commands`.
- **Boot gate**: run `python scripts/runtime_preflight.py` before any hunt session.
  Non-zero exit = do not proceed until fixed.
- **Scenario resolution**: `python scripts/skill_registry.py resolve <scenario>`.

## MCP notes

- Browser automation via chrome-devtools-mcp (`opencode.json`).
- Evidence from the browser session must be saved under
  `testing/<root-domain>/<subdomain>/evidence/` per skill playbooks.