---
id: learning-engine-integration
name: learning-engine-integration
description: load and use the persistent learning engine for adaptive hunting, signal scoring, memory retrieval, and triage feedback ingestion across hunts
phase: recon
severity: info
aliases: [learning-engine, learning-hooks, learning-engine-integration]
tags: [foundation, learning, hooks, boot]
---

# Learning Engine Integration — Adaptive Learning Skill

Loads the persistent learning engine into the agent workflow. Loaded SECOND in
every session (right after master-bugbounty-rules), before any recon. Provides
pre-hunt intelligence, real-time signal scoring, finding persistence,
post-triage learning, similar-case retrieval, and exploitability ranking. 100%
consistent with `AGENTS.md`, `agent-briefing.md`, and the `learning_engine/`
package.

## 1. Purpose

This skill is loaded automatically before every hunt and provides pre-hunt
intelligence, real-time signal scoring, finding persistence, post-triage
learning, report-lesson retrieval, and exploitability ranking.

## 2. Prerequisites

- The engine lives at `learning_engine/` — pure Python, no external
  dependencies.
- Initialize once at agent start:

```python
from learning_engine import LearningEngine
engine = LearningEngine()
```

## 3. Integration Points

1. **Before Recon — Load Intelligence:**
   - Call: `engine.before_recon(target, technologies)`
   - When: after scope parse, before any recon tool runs.
   - Why: retrieves target profile, similar targets, historically successful
     signals; read the plan and prioritize high-value surfaces first.
   - Use: `plan = engine.before_recon(target, techs)` — hunt
     `plan["suggested_classes"]` first.
   - ALSO: read `memory/report-lessons.md` before opening processed write-ups —
     the index is for retrieval only, the lesson file is the hunter's distilled
     memory.

2. **During Testing — Score Signals:**
   - Call: `engine.during_testing(signals)`
   - When: every time a new signal is discovered (endpoint, JS leak, header,
     etc.).
   - Why: scores each signal by historical outcomes.
   - Use: high scores → deep test; low → note and move on.

3. **After Finding — Persist Memory:**
   - Call: `engine.after_finding(target=..., endpoint=...,
     vulnerability_class=..., signals=..., validation_state=...,
     source_provenance=...)`
   - When: after documenting a finding in `notes/`.
   - Why: saves to learning memory and updates the target profile.
   - Use: ALWAYS call after every finding, even low-confidence observations.

3.5. **On Strong Lead — Expand Similar Cases:**
   - Search local write-up + memory sources for highly similar patterns when a
     lead looks credible enough for confirmation or impact expansion.
   - Start from `memory/report-lessons.md`, then search `writeups/index.md` by
     vuln class, mechanism, affected feature, and trust boundary.
   - Read matching processed write-ups only after the lesson pass, before
     deciding reportability or final severity.

3.75. **During /update — Learn From Reports:**
   - Convert collected reports into `memory/report-lessons.md` plus
     methodology, patterns, and target checklists; learn reusable hunting
     judgment, not merely accumulate searchable documents.
   - Extract: entry point, trust boundary, precondition, bypass, proof method,
     false-positive trap, chain opportunity, matching skills, and how the
     lesson changes future priority.

4. **After Triage — Learn from Feedback:**
   - Call: `engine.after_triage(finding_id, feedback_type, notes, provenance)`
   - When: the program responds (accepted, duplicate, informative,
     false_positive).
   - Why: atomically moves the finding, records feedback provenance,
     recalibrates outcomes; reinforce successful patterns, penalize noisy
     ones.
   - Use: never use session-level outcomes as feedback.

5. **Before Summary — Rank by Exploitability:**
   - Call: `engine.before_summary(findings)`
   - When: before structured-summary-reporting.
   - Why: ranks by historical exploitability, accept rate, chain value.
   - Use: present highest-value findings first.

## 4. Signal Registry

The engine tracks these signal types by default; weights are configurable in
`learning_engine/scoring/signals.json` (canonical). Bands reflect the current
weighted set (score = sum of matched weights, clamped to [0, 1]):

- **High value (weight 0.20-0.30):** rce, auth_bypass, sql_injection,
  pii_exposure, ssrf_metadata, unrestricted_upload, privilege_escalation.
- **Medium value (weight 0.10-0.15):** default_credentials,
  object_reference_guessable, jwt_alg_none, no_authorization_check,
  reflection, no_output_encoding, template_math_evaluated, file_read_confirm.
- **Low value (weight 0.01-0.05):** csrf_token_missing, cors_reflects_origin,
  no_rate_limit, verbose_error, missing_security_headers.

Unknown signals are ignored by scoring (weight 0.0) — add new keys to
`signals.json`, never ad hoc.

## 5. Scoring Auto-Escalation

The engine automatically boosts scores (multiplier applied to matched weight
before the ceiling clamp, `scoring/engine.py` `BOOSTS`): cross_tenant +30%,
admin_bypass +30%, state_changing +20%, sensitive_data +20%, auth_bypass +30%,
chainable +20%, payment_impact +30%. Score remains bounded to [0, 1].

## 6. Memory Buckets

| Bucket | Purpose | Learning effect |
|--------|---------|-----------------|
| heuristics/ | validated signal patterns only | outcome-calibrated tracking |
| pending finding state | initial storage for observations | traceability only, never trains heuristics |
| accepted/ | confirmed findings | signal reinforced from triage evidence |
| duplicates/ | duplicate findings | signal penalized, pattern refined |
| informative/ | informational findings | signal weight may reduce |
| false_positive/ | false positives | signal penalized, pattern downgraded |
| chains/ | chain opportunities | chain frequency tracked |
| target_profiles/ | per-target data | technology/surface/bug class accumulation |

## 7. Analytics

Available after hunts:

```python
engine.get_statistics()                                  # counts per table
engine.get_tuning()                                      # weights + policy
engine.get_heatmap()                                     # class x signal counts
engine.get_chains()                                      # chain candidates + FP patterns
engine.rebuild_graph()                                   # JSON graph (targets/classes/signals)
engine.analytics.highest_signal_surfaces(limit=10)       # top vuln-class surfaces
engine.analytics.duplicate_heavy_patterns()              # duplicate-heavy signal patterns
engine.analytics.target_summary(target)                  # per-target profile
```

## 8. Quick Reference

```python
from learning_engine import LearningEngine
engine = LearningEngine()                 # initialize once at agent start

plan = engine.before_recon(target, techs) # -> suggested classes, recalled lessons
score = engine.during_testing(signals)    # -> {"score": 0-1, "matched": {...}}

f = engine.after_finding(target=target, vulnerability_class="xss",
                         signals={"reflection": True},
                         validation_state="confirmed",
                         source_provenance="session:hunt")
engine.after_triage(f["finding_id"], "accepted" | "duplicate" |
                    "informative" | "false_positive",
                    provenance={"source": "program_triage", "actor": "tester"})
ranked = engine.before_summary(all_findings)  # -> {"ranked": [...], "count": n}

# analytics anytime
engine.get_heatmap(); engine.analytics.target_summary(target)
```

## 9. File Locations

- Engine code: `learning_engine/`
- Skill file: `.agents/skills/learning-engine-integration/SKILL.md` (runtime
  copy of this file)
- Signal config: `learning_engine/scoring/signals.json`
- Memory source of truth: `learning_engine/memory/learning.db`
- Legacy JSON and `.bak` folders (if present): migration/recovery artifacts
  only — never read as truth.
- Audit: `python learning_engine/scripts/audit_learning_engine.py --report-only`
- Schemas: `learning_engine/schemas/*.json`
- Docs: `learning_engine/docs/*.md`

## 10. Testing Requirement

After writing this skill, verify the engine contract: run
`python learning_engine/scripts/audit_learning_engine.py --report-only` and the
learning-engine test suite (`py -m pytest scripts/test_learning_engine.py -q`).
Confirm all 5 hooks accept and return the documented shapes and that signal
scoring is bounded. Report pass/fail.