# Antigravity Manifest

Command-execution manifests for the hunting runtime.

## Execution context

Every skill playbook's "Quick checks" and "Payloads" sections are executed under
this manifest. Skills never execute arbitrary user text; they execute the
payloads listed in their own playbook file.

## Safety flags

| Flag | Meaning | Default |
|------|---------|---------|
| `--scope=<root>` | restrict all requests to this root domain | required |
| `--dry-run` | print commands, execute nothing | off |
| `--no-evidence` | skip evidence capture (discouraged) | off |
| `--throttle=<ms>` | min delay between requests | 500 ms |

## Environment

- `HUNT_ROOT` = workspace root (`hunting-new/`)
- `TARGET_ROOT` = current root domain under `testing/`
- `EVIDENCE_DIR` = `testing/<root>/<sub>/evidence/`
- `LOGS_DIR` = `logs/runs/`

## Pipeline scripts (entry points)

| Script | Purpose |
|--------|---------|
| `scripts/update.sh` | full state regeneration |
| `scripts/fetch.sh` | fetch remote feeds (writeups/feeds) |
| `scripts/process.sh` | batch-parse raw artifacts into structured notes |
| `scripts/index.sh` | index evidence/urls into target trees |
| `scripts/learn.sh` | ingest + distill lessons |
| `scripts/skill_registry.py` | resolve/check/generate registry state |
| `scripts/runtime_preflight.py` | boot gate + session bootstrap |

## Extending

New executors must be added here AND in `runtime/opencode/manifest.md` (agents)
and pass `scripts/test_runtime_contract.py`.