# Learning Engine — Package Doc

SQLite-backed memory for the hunting runtime. Pure Python, no external
dependencies. Canonical DB: `learning_engine/memory/learning.db` (WAL mode).

## Public API

- `from learning_engine import LearningEngine`
- `engine = LearningEngine()` — root defaults to the workspace root; pass
  `root=` for isolated workspaces (tests).

### Session hooks (documented, used by skills)

| Hook | Signature |
|------|-----------|
| `before_recon` | `(target, techs)` → plan + recalled lessons |
| `during_testing` | `(signals)` → bounded score 0-1 |
| `after_finding` | `(target, endpoint, vulnerability_class, signals, validation_state, source_provenance)` → persisted doc |
| `before_summary` | `(findings)` → ranked list |
| `after_triage` | `(finding_id, feedback_type, notes, provenance)` → verdict persisted |

### Core

- `record_finding(...)`, `record_triage(...)`, `recall(query, ...)`,
  `distill(min_support)`, `score(signals)`, `stats()`, `export_graph()`.

### Analytics

- `get_statistics()`, `get_tuning()`, `get_heatmap()`, `get_chains()`,
  `rebuild_graph()`, `engine.analytics.highest_signal_surfaces(limit=10)`,
  `engine.analytics.duplicate_heavy_patterns()`,
  `engine.analytics.target_summary(target)`.

## Scoring

Weights + policy in `learning_engine/scoring/signals.json`; score clamped to
[0, 1]; auto-escalation boosts in `scoring/engine.py` (`BOOSTS`).

## Storage

Tables: findings, triage, lessons, patterns, meta (see `core/storage.py`).
Schemas: `learning_engine/schemas/*.json`.

## Audit

`python learning_engine/scripts/audit_learning_engine.py --report-only`