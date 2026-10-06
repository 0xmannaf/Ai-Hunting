---
description: Write a Bugcrowd-ready report from confirmed bug evidence
agent: build
---

# Autonomous Report

Target or notes:
$ARGUMENTS

Render a Bugcrowd-ready report from CONFIRMED, evidence-backed findings only.

## Mandates

- Follow `AGENTS.md` + `prioritization.md`.
- Use: master-bugbounty-rules, false-positive-filter,
  evidence-validation-and-severity-calibration, evidence-hygiene,
  request-response-analyzer, report-writer; bugcrowd-reporting or
  redteam-report-template when applicable.

## Before writing

1. Resolve `python scripts/skill_registry.py resolve --scenario
   "validated report <finding class>" --mode report --paths-only`; load every
   returned skill.
2. Run the COMPLETE FP gate from `AGENTS.md` (10-question checklist, verbatim).
3. Only REPORTABLE-state findings with raw evidence may be rendered. Anything
   less -> "Not ready to report".

## Rules

- Only write if enough evidence exists. If weak, output a **"Not ready to
  report"** section listing the missing proof + the safest next validation
  step.
- Read `memory/report-lessons.md` + the closest `memory/targets/<vuln>.md`
  checklist before final severity wording.
- Never claim data breach / ATO / RCE / admin / cross-tenant unless the
  evidence proves it. Downgrade when unsure (`prioritization.md` P1-P4).

## Artifact path rule

- Reports under `testing/<root-domain>/reports/` or
  `testing/<root-domain>/<subdomain>/reports/`; supporting files in
  `evidence/`, `requests/`, `responses/`, `screenshots/`. Never project root.

## Output structure

- Title; affected asset; severity with justification; impact statement
  ("As an attacker, I can ..."); reproduction steps (raw requests); evidence
  paths; remediation; limitations; triager notes.