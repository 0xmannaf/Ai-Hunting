# Methodology

The operating methodology for hunts. Conservative, evidence-first, learning-driven.

## 1. Preparation

1. Read `AGENTS.md` and `prioritization.md`.
2. Verify target scope in `memory/CONTEXT_LEDGER.md` (binary in/out).
3. Run `python scripts/runtime_preflight.py --bootstrap`.
4. Resolve skills: `python scripts/skill_registry.py resolve <scenario>`.

## 2. Recon (passive -> active)

1. Passive: certificate transparency, DNS history, search dorking, public datasets.
2. Active (throttled): subdomain enumeration, port/service discovery, robots/sitemap.
3. Record: subdomains, URLs, tech stack, WAF presence, auth surface.
4. Artifacts -> `testing/<root>/<sub>/subdomains/`, `urls/`, `notes/`.

## 3. Surface mapping ("understand")

1. Map entry points: login, API docs, upload, search, download, redirect handlers.
2. Identify auth model: session, JWT, OAuth, API keys; where tokens live.
3. Note input classes: reflection, storage, server-side fetch, file access, templates.

## 4. Hunting

1. One hypothesis at a time; skill playbook guides payloads.
2. Non-destructive payloads first (AGENTS.md rule 4).
3. Capture every meaningful request/response as evidence immediately.
4. Stop at first confirmation; hand to validator.

## 5. Verification

1. Independent reproduction from clean state.
2. Score per prioritization rubric; confidence >= 0.8 for P1/P2.
3. FPs -> `FALSE_POSITIVE_DB.md` with trigger pattern.

## 6. Learning

1. Ingest findings + triage into learning engine (`scripts/learn.sh`).
2. Distill lessons -> `report-lessons.md`.
3. Update `patterns.md` when a signal repeats across targets.
4. Update `targets/<vuln>.md` checklists with new payloads/observations.

## 7. Reporting

1. Draft writeup in `writeups/processed/` (reporter agent).
2. Evidence references relative to `testing/`.
3. P1/P2 -> human review; P3/P4 -> weekly batch.

## Principles

- Evidence over assertion; nothing fabricated; empty sections are honest.
- Scope is binary; ambiguous = out.
- Rate-limit everything; respect the target.
- Every FP is a lesson, not a failure.

> Last pipeline run: 2026-10-01 (update_steps learn)
