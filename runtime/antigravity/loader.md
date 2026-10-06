# Antigravity Runtime Loader

Antigravity is the command-execution layer of the hunting runtime: it runs the
scripted portions of skills (curl, python one-liners, playwright captures, node
scans) with strict gates.

## Load order

1. `runtime/antigravity/manifest.md` — executor manifests (this layer).
2. `runtime/registry.json` — routes/commands for execution context.
3. `scripts/` — canonical pipeline scripts (never reimplemented ad hoc).

## Gate contract (all executions)

- Target must be in `memory/CONTEXT_LEDGER.md` scope: `in`.
- Command must be read-only/non-destructive unless explicitly approved.
- Requests are throttled and batched (see `scripts/process.sh` policies).
- Evidence of every execution lands under `testing/<root>/<sub>/requests/`.

## Executors

| Executor | Use for | Gate |
|----------|---------|------|
| `bash` | curl/httpx-style probes, pipelines | scope + throttle |
| `python` | learning engine, parsing, analysis | read-only by default |
| `node` | playwright capture (`scripts/playwright_capture.js`) | local only |
| `chrome-devtools` | live browser verification | evidence capture required |

## Failure policy

- Non-zero exit = halt that skill step, log to `logs/runs/`, do not guess a fix.
- Rate-limit/429/blocked responses are logged as WAF signal, not as findings.