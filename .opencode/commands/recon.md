---
description: Exploit-first scope-safe bug bounty discovery and attack-surface prioritization
agent: build
---

# Autonomous Recon

Target or notes:
$ARGUMENTS

Exploit-first, scope-safe discovery. Recon is a bounded input, never the
mission.

## Mandates

- Follow `AGENTS.md` + `prioritization.md`.
- Minimum-viable recon to find an authorized high-value surface, then enter the
  exploit loop immediately. Never build an inventory without testing.
- Scope-safe: no brute force, no DoS, no credential abuse, no destructive
  actions, no third-party data.

## Artifact path rule + scope lock

- Artifacts under `testing/<root-domain>/<subdomain>/` standard folders; never
  project root.
- Exact-host first; no `*.<root>` traversal without approval; others are
  passive context only.

## Required context

1. Read `agent-briefing.md` + `memory/report-lessons.md` + `memory/patterns.md`
   + `memory/methodology.md`; check `testing/` for prior history.
2. Verify `python scripts/skill_registry.py check` passes.
3. Run `python scripts/runtime_preflight.py --target "<target>" --scenario
   "<surface>" --mode recon --workspace "testing/<root>/<sub>"
   --ensure-session`; stop if blocked.
4. Resolve `python scripts/skill_registry.py resolve --scenario "<surface>"
   --mode recon --paths-only` and load every returned skill.
5. After fingerprinting, call `engine.before_recon(target, technologies)` and
   record the resulting plan in `notes/`.

## Recon skill stack (load before starting)

master-bugbounty-rules, learning-engine-integration, recon-workflow,
tech-fingerprint, endpoint-triage, fuzzing, dorking-and-osint-discovery,
offensive-osint, osint-methodology, js-deep-analysis, js-secret-and-api-review,
business-context-analysis, exploit-chain-analysis, evidence-hygiene,
structured-summary-reporting.

## Workflow

1. **Passive recon:** wayback, certificate-transparency logs, subdomains.
   Record into `subdomains/`, `urls/`.
2. **Tech fingerprint:** stack, WAF/CDN presence, auth model.
3. **Pick the highest-value surface** and TEST IT IMMEDIATELY — one safe
   controlled variant, recorded in the tested-variant ledger.
4. **Expand exploit paths** with JS deep analysis + tech-aware fuzzing.
5. Whenever discovery hits a bug class: run the resolver, load every matching
   skill, test before collecting more.

## Output (notes/)

- Target + scope assumptions; fingerprint; prioritized surfaces; safe
  validation steps performed; evidence needed; recommended next commands.