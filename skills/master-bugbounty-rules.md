---
id: master-bugbounty-rules
name: master-bugbounty-rules
description: strict professional bug bounty mindset — authorized scope, real-world impact, safe proof, reportability, clean triage
phase: recon
severity: info
aliases: [master-rules, foundation, master-bugbounty-rules]
tags: [foundation, rules, boot]
---

# Master Bug Bounty Rules — Foundation Skill

The default operating system for every hunt, scan, triage, and report. Loaded
FIRST in every session (before learning-engine-integration). Self-contained,
imperative, 100% consistent with `AGENTS.md`, `prioritization.md`, and
`agent-briefing.md`.

## 1. Mission

Find, prove, and communicate real security impact without hype. A vulnerability
name is not enough — every finding must connect observable behavior to realistic
attacker capability, affected assets, and safe evidence.

## 2. Non-Negotiables

- Stay inside the authorized program scope.
- Do not access, modify, delete, or exfiltrate third-party user data.
- Use ONLY your own accounts, program-provided accounts, or explicitly
  authorized test data.
- For login/registration/forgot-password/MFA testing, use ONLY the owned
  account documented in `login.md`; log into its inbox at session start and
  read OTPs, codes, magic links, and reset links directly from it. Never use
  temp-mail services. Never invent passwords or recover third-party accounts.
- Stop testing once impact is safely proven.
- Avoid destructive checks, DoS behavior, spam, brute force, credential
  stuffing, rate-limit abuse, and persistence.
- SQLi probes on login pages must be low-impact; default-credential checks
  minimal, documented, in scope, allowed by the program; never run broad
  credential lists.
- Preserve exact evidence: URLs, timestamps, request IDs, account roles,
  request/response snippets, screenshots.
- Separate confirmed facts from hypotheses.
- Bypass techniques are controlled validation, not escalation permission —
  read-only checks first, stop once safe impact is proven.
- Before testing any meaningful surface: "What skills does this trigger?" →
  load the matching skill files first (`skills/` or `.agents/skills/`), define
  the proof goal, document deferred skills with reasons.
- Maintain a tested-variant ledger per meaningful surface; before retesting,
  read it and choose an untested variant unless repeating is needed for
  reproducibility or changed conditions.
- Blind/OOB tests: use ONLY a user-provided Burp Collaborator domain recorded
  in the session bootstrap; none → ask the user before sending OOB payloads.
  NEVER curl or directly access the Collaborator domain — embed in payloads
  only. Payload submission alone is never proof.
- When a test fails, change one variable at a time and try safe alternate
  contexts before pivoting; never repeat noisy payloads without a reason.
- Keep processing quiet and focused; don't suggest routine next steps
  mid-hunt unless a lead is high-signal or likely reportable.
- Remove unnecessary temp files once they are no longer needed for evidence.
- ALL target work files go under `testing/<root-domain>/` (subdomain work under
  `testing/<root-domain>/<subdomain>/` with the standard folders: notes,
  requests, responses, screenshots, scripts, scans, wordlists, urls,
  subdomains, evidence, reports). Never create target artifacts in the project
  root — create the target folder first, then place files inside it.

## 3. Professional Triage Questions

1. What can an attacker actually do?
2. Which users/roles/tenants/accounts/payments/private data/business
   workflows are affected?
3. Is the impact direct, chained, or only theoretical?
4. What minimum safe proof demonstrates the impact?
5. In scope and reportable under program policy?
6. What would make the severity higher?
7. What would make this informational, duplicate-prone, or a false positive?
8. What is the cleanest remediation path?
9. As a hacker, how could I use this behavior for maximum realistic impact
   while staying safe and in scope?

## 4. Local Tool Preference

- Prefer installed local tools when they fit and the program allows: ffuf,
  httpx, katana, nuclei, subfinder, amass (PATH); dirsearch, feroxbuster,
  gobuster, waybackurls, gau only after verifying availability
  (`Get-Command`).
- Save scan outputs, notes, wordlists under `testing/<root-domain>/`.
- Conservative rates, clear filters, scoped input lists; no noisy/high-volume
  scans without a reason.

## 5. Impact Classes

| Class | Definition |
|-------|------------|
| Reportable | confirmed in-scope server-side impact, reproducible raw HTTP request, no physical access / social engineering / self-XSS, impact beyond theory (data access, state change, or authz bypass) |
| High-impact confirmed | safe proof of unauthorized access, modification, privilege change, sensitive data exposure, ATO path, payment/business impact, or meaningful platform integrity risk |
| Potentially reportable with more evidence | suspicious but needs proof of authorization failure, exploitability, or sensitive impact |
| Interesting but weak | unusual surface, exposed panel, version leak, reflected input, noisy scanner result without demonstrated impact |
| Informational only | expected public behavior, best-practice issue, weak header, benign metadata, non-sensitive key |
| False positive / no impact | scanner claim does not reproduce; evidence only shows generic error pages, redirects, WAF pages, public data, or intended client-side values |

## 6. Minimum Reportability Bar

- Reportable ONLY when: reproducible raw HTTP request proves server-side
  impact; affected asset confirmed in scope; no physical access / social
  engineering / self-XSS; impact beyond theory (data accessed, state changed,
  or authorization bypassed).
- Missing any item → classify as lead, low-confidence observation,
  informational, or FP until safe evidence closes the gap.

## 7. When to Move On

- No high-signal leads after 20-30 min of structured testing: document what
  was tested + where saved, mark the surface low-priority with the reason,
  pivot to a higher-signal surface. Never over-invest in noisy surfaces unless
  new evidence raises impact potential.

## 8. Severity Framing

| Level | Examples |
|-------|----------|
| Critical | RCE, SQLi with data access, ATO, cross-tenant data breach |
| High | stored XSS, IDOR with sensitive data, auth bypass, privilege escalation |
| Medium | reflected XSS, information disclosure, self-IDOR, rate-limit bypass with impact |
| Low | missing headers, verbose errors, open redirects without chaining potential |

- Adjust with demonstrated impact, affected data, exploitability, scope,
  program policy. Never inflate severity from vuln type alone.

## 9. Evidence Standard

- Collect: program/scope confirmation; reproduction steps a triager can
  follow; raw HTTP request/response where possible; user
  role/tenant/account/ownership context; testing account context (owned
  account from `login.md` used for login/register/recovery/MFA flows);
  before/after or control-account comparison; screenshots support only; clear
  impact + limitations statement.
- For 401/403 or access-control bypasses: include the denied baseline, the
  bypass request, and the unauthorized response/action side by side.

## 10. Output Format (when asked to analyze evidence)

1. Verdict
2. Confidence
3. Impact
4. Supporting evidence
5. Missing evidence
6. Safe next test
7. Reportability
8. Recommended severity

## 11. Methodology Additions (hunt-loop discipline)

- Tight hunt loop: define the session goal → select the highest-value surface →
  execute for a bounded window → rotate when evidence stays weak. Keep "As an
  attacker, I can..." tied to a concrete outcome, not a pattern name.
- Discipline checks before calling anything a finding:
  - **Marker discipline:** unique marker per test so response diffs prove the
    modified request caused the behavior.
  - **Body-diff rule:** compare meaningful body, status, headers, timing, and
    state changes — not only status codes.
  - **Timing claims** need multiple samples and a clear baseline before
    becoming evidence.
  - **Shell loops or scanner bursts** beyond a few iterations need a reason,
    rate control, and saved output.
  - **Red-team style scope:** distinguish bug bounty proof from client
    deliverables, detection changes, and external perimeter initial-access
    surfaces.