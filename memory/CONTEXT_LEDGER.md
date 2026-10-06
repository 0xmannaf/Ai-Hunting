# Context Ledger

Append-only record of scope, sessions, hypotheses, and decisions. The
authoritative answer to "what are we allowed to test and what happened when".
Read it at session start; append after every surface / test / pivot / finding.

## Scope (authoritative)

Pipe-delimited table. A target is testable ONLY when `In scope?` = `in`.
Ambiguity = out. Out-of-scope observations are logged as `noted, out of scope` —
never tested.

| Target (root domain) | In scope? | Boundaries / notes | Authorized by | Date |
|----------------------|-----------|--------------------|---------------|------|
| test.example.com | in | local validation sandbox only; no production traffic; synthetic corpus | master | 2026-10-01 |
| dell.com | in | master-commanded `/hunt dell.com`; passive-first recon + fingerprint; no OOB (no Collaborator domain); no FUZZ.dell.com without approval; auth flows only via owned accounts (none yet) | master | 2026-10-01 |
| pentest-ground.com | in | master-commanded `/hunt https://pentest-ground.com:81/`; exact-host scope = pentest-ground.com:81 only; no OOB (no Collaborator domain provided); no FUZZ.pentest-ground.com without approval; no destructive/DoS; training-style target presumed | master | 2026-10-01 |

## Sessions

Pipe-delimited, ~3-5 lines per meaningful action:

| timestamp | session | target | action | surface | result | evidence path |
|-----------|---------|--------|--------|---------|--------|---------------|
| 2026-01-01T00:00:00Z | bootstrap | — | workspace bootstrap | — | created registry, skills, learning engine, pipelines | — |
| 2026-10-01T13:50:00Z | update | — | pipeline build | learning process | update_steps.py created; corpus seeded (4 sample writeups); 5 session hooks added; tests 73 passed | writeups/raw, writeups/processed, scripts/test_*.py |
| 2026-10-01T13:55:57Z | update | — | offline pipeline run | writeups+memory | fetch=0 process=4 index=4 learn=4; idempotent on rerun | writeups/index.md, memory/report-lessons.md, agent-briefing.md |
| 2026-10-01T13:56:53Z | session | test.example.com | scope intake | login form | bootstrap created; scope locked | logs/sessions/20261001T135653Z.json, testing/test.example.com/www/notes/bootstrap.md |
| 2026-10-01T14:11:58Z | session | dell.com | hunt boot | homepage | scope intake recorded (master /hunt); preflight OK; Akamai+BotManager+F5 ASM fingerprint | testing/dell.com/www/notes/recon-01.md |
| 2026-10-01T14:13-14:30Z | session | dell.com/www | surface discovery+test | homepage/auth/support | OIDC discovery public; redirect_uri path-variants accepted (external rejected); elevated scopes accepted at authorize (client 657d850a); internal hosts in metadata not resolvable; header leaks informational; ifd.log.html no XSS; 5x403 → backoff | testing/dell.com/www/notes/surface-01-homepage-auth.md |
| 2026-10-01T14:30Z | session | dell.com/www | backoff | WAF gate | 60s circuit break after Akamai 403 bucket; resume with passive/browser-native requests only | — |
| 2026-10-01T14:43Z | session | pentest-ground.com:81 | hunt boot | scope intake | master /hunt https://pentest-ground.com:81/; preflight OK after ledger scope entry; GuardianLeaks Flask lab (Pentest-Tools), nginx 1.31.6, no WAF | logs/sessions/20261001T144317Z.json |
| 2026-10-01T14:44-14:50Z | session | pentest-ground.com:81 | surface discovery | root/app | 5 agents dispatched; endpoints: /console (werkzeug debugger, SECRET leak, PIN-gated), /create (reference=SSRF), /search (query), /dashboard→/login, /top_secret; /app/app.py source obtained via traceback leak | testing/pentest-ground.com/pentest-ground.com/notes/findings.md |
| 2026-10-01T14:46-14:55Z | session | pentest-ground.com:81 | exploit+validate | search/login/post/create/dashboard | RCE via eval(query) PROVEN (file write+readback); SQLi x3 (post/<id> readable UNION, search error-based, create); SECRET_KEY "your secret key" → session forgery → admin dashboard (id=2); hardcoded basic auth bonnie:Bonni3 → /top_secret; 2nd-order SQLi→stored XSS via email (textarea breakout); login parameterized (no bypass); artifacts cleaned up | testing/pentest-ground.com/pentest-ground.com/evidence/ (pending), responses/*.html |
| 2026-10-01T14:55Z | session | pentest-ground.com:81 | learning ingest | findings | engine after_finding called for RCE/SQLi/session-forgery/XSS/creds; notes+ledger updated; target restored (admin email, /static files removed) | — |

- Bootstrap by runtime_preflight. No production targets yet.
- Decision: 20 skill playbooks; registry is canonical; memory files derived
  where marked AUTO-GENERATED.

## Hypotheses

| # | Hypothesis | Target | Status | Outcome |
|---|------------|--------|--------|---------|
| _(none)_ | | | | |

## Decisions

| # | Decision | Rationale | Date |
|---|----------|-----------|------|
| _(none)_ | | | |

## Out-of-scope observations

| Observed | Target | Disposition |
|----------|--------|-------------|
| _(none)_ | | |2026-10-01|recon-agent|pentest-ground.com:81|boot: tech fingerprint nginx/1.31.6, CORS *, SessionID cookie; 8 root files 404; WAF/CDN none; pages all 200; DNS 178.79.134.182|summary returned to orchestrator
dorking-agent|pentest-ground.com|passive OSINT done: services map (6 apps), X-Auth-Token, Wayback /documents + /private-dev surfaces, GitHub examples|high-confidence|2026-10-01
| 2026-10-01T14:45Z | hunt | pentest-ground.com | understand-agent mapping (NO testing) | home/login/blog/contact/post | Flask+nginx:81; SessionID cookie NO HttpOnly/Secure/SameSite (value 'encrypted-session-id'); CORS *; leaked routes /create /search; anon Edit links /1/edit /2/edit; contact form blind-SQLi TODO comment + hidden rick.astley@youtube.com; no owned account -> login flow documented only | testing/pentest-ground.com/pentest-ground.com/notes/understanding.md |
