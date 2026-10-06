---
description: Normal bug bounty scan triage
agent: build
---

# Autonomous Scan

Target or notes:
$ARGUMENTS

Conservative, exploit-first triage of scans and leads against an authorized
target.

## Mandates

- Follow `AGENTS.md` + `prioritization.md`.
- Use all relevant skills from `runtime/registry.json`; start with master
  rules + learning-engine hooks.
- Exploit-first scan policy: scan output is a lead generator, not the
  deliverable. After scope lock and the first usable endpoint, test
  immediately.

## Required startup

1. Read `agent-briefing.md`; load master rules + learning-engine hooks.
2. Verify `python scripts/skill_registry.py check` passes.
3. Run `python scripts/runtime_preflight.py --target "<target>" --scenario
   "<surface>" --mode scan --workspace "testing/<root>/<sub>"
   --ensure-session`; stop if blocked.
4. Resolve `python scripts/skill_registry.py resolve --scenario "<surface>"
   --mode scan --paths-only` and load every returned skill.
5. After fingerprinting, call `engine.before_recon(target, technologies)` and
   record the plan in `notes/`.

## Workflow

1. **Learn first:** `memory/report-lessons.md`, `memory/patterns.md`,
   `memory/methodology.md`, `memory/targets/<vuln>.md` for the classes at hand.
2. **Prior history:** check `testing/` — "we had checked this target before";
   reuse prior `scans/`, `wordlists/`, `urls/`, `subdomains/` artifacts.
3. **Triage provided scan results first** (scanner output, fuzz results):
   response-diff, filter against `memory/FALSE_POSITIVE_DB.md` (signature-hash
   before any promotion).
4. **Exact-host boundary:** stay on the supplied target; sub-subdomain
   permutations inside the hostname only.
5. **Conservative approach:** no brute force, no credential attacks, no
   destructive payloads, no third-party data access, no aggressive volume.
   Prefer `wordlist/` project lists over SecLists.
6. Test the highest-priority lead immediately (one safe variant), then expand
   per the bypass ladder. Record every variant in the tested-variant ledger.

## Output (notes/)

- Target + scope; recon + fingerprint; scan/fuzzing plan with the wordlists
  used; prioritized findings; FP filtering notes; safe validation steps;
  evidence needed; recommended next commands.