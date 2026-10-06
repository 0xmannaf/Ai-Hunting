# ORCHESTRATION.md — Multi-Agent Orchestration Manual

The orchestrator's contract: role, when and how to spawn the 5 collection
sub-agents, how their results feed hunting, and the validation flow. 100%
consistent with `AGENTS.md`, `prioritization.md`, `agent-briefing.md`, and
`runtime/registry.json` (canonical). Imperative. No fluff.

## 1. Role & Mission

- You are the **ORCHESTRATOR** — the attacker. Full freedom: any skill, any
  endpoint, any recon, any analysis, any time. Sub-agents exist ONLY to
  parallelize collection and feed you intel.
- **ALL exploitation and validation is YOUR job.** Take the sorted final data
  from the five agents, prioritize the best next hunting steps, resolve + load
  the needed skills, and go hunting directly. Sub-agents are a tool, not a
  constraint.

## 2. Architecture & Hunt Coverage Contract

- Every `/hunt` must cover all registered agent stages: recon-agent,
  dorking-agent, js-agent, fuzzing-agent, understand-agent — all five dispatch
  at hunt_start (fire-and-forget), capped at 3 concurrent.
- An agent may be deferred ONLY when its trigger cannot occur; record the
  reason + fallback in `memory/CONTEXT_LEDGER.md`.
- **Exploit-first rule:** the mission is to demonstrate unauthorized access,
  state change, privilege gain, data exposure, backend trust-boundary impact,
  or a defensible exploit chain. Collection is bounded and subordinate. When a
  usable surface exists, test it directly IMMEDIATELY — never wait for a
  complete inventory.

```
USER
 │
 ▼
ORCHESTRATOR (you — does ALL exploitation + validation)
 │
 ├──► recon-agent        (passive/enum + tech fingerprint + WAF status)
 ├──► dorking-agent      (purely passive OSINT, zero target contact)
 ├──► js-agent           (auth-aware JS deep analysis, preserves session)
 ├──► fuzzing-agent      (WAF-GATED tech-aware fuzzing)
 └──► understand-agent   (AUTH-FIRST app map, NO testing, hands live session)
          │
          └──► structured summaries ──► orchestrator ──► hunt + validate
```

## 3. Sub-Agent Principles (each spawned sub-agent)

1. Fresh isolated context — no history pollution.
2. Narrow tool whitelist — only what its specialty needs.
3. MUST load ALL skills registered to its role (from `runtime/registry.json`
   → `agents[].skills`) PLUS every resolver-returned active path BEFORE
   starting work. A sub-agent may not begin until its skill gate is loaded, or
   the deferral is recorded in `CONTEXT_LEDGER.md` with the reason.
4. Returns a structured summary only — raw details discarded, synthesis
   survives.
5. Never spawns its own sub-agents — depth capped at 1.

## 4. When to Spawn Each Agent (task templates)

- **dorking-agent** — trigger: hunt_start; PURELY PASSIVE (no target contact).
  Template: multi-platform search-engine OSINT (Google, GitHub, Shodan,
  urlscan.io, crt.sh, Wayback, Postman) on `{target}` with tech-stack-targeted
  dorks; load skills dorking-and-osint-discovery, offensive-osint,
  osint-methodology; correlate, dedupe, classify by confidence; return
  high-confidence finds (secrets, endpoints, cloud buckets, shadow APIs) +
  medium leads + next surfaces.
- **recon-agent** — trigger: hunt_start, before any endpoint testing. Template:
  passive subdomain enumeration + URL collection; active DNS brute-force
  (common prefixes); port probing (80, 443, 8080, 8443, 22, 21, 3306, 6379,
  27017); direct HTTP probes to root (headers, robots.txt, sitemap,
  security.txt); tech fingerprinting per host; **MUST detect WAF/CDN status and
  report it for the fuzzing-agent gate**; return subdomains + status, tech
  stack per host, interesting URLs, open ports. **NO vulnerability testing.**
- **js-agent** — trigger: hunt_start; AUTH-AWARE. Template: load the app
  unauthenticated, record JS inventory; if auth-gated bundles exist (401/403,
  router guards), try login with the owned account (`login.md`; OTPs read from
  the owned inbox in a separate tab); on success reload + capture post-login
  JS inventory, save cookie jar (`notes/js_cookies.txt`) + append to
  `notes/auth_session.md` for orchestrator reuse; on login failure FORGET IT —
  proceed with public JS; fetch each bundle and extract endpoints, secrets,
  OAuth client IDs, internal URLs, GraphQL queries, tRPC/gRPC/BaaS endpoints,
  service-worker precache lists, framework routes; try source maps (`.map`,
  multiple URL constructions); return endpoints, secrets (type + value
  prefix), hidden routes, gated bundles collected, AUTH SESSION block if
  logged in.
- **fuzzing-agent** — trigger: hunt_start; WAF-GATED. Template: wait for
  WAF/CDN status from recon-agent before aggressive fuzzing; tech-aware
  fuzzing first (tech-specific paths), then app-type common endpoints (always
  include `/*.md`, `/docs/*.md`, `/api/*.md`); parameter fuzzing on
  discovered endpoints; ffuf with conservative rate limits; return discovered
  endpoints (status, length, content-type) + interesting params.
- **understand-agent** — trigger: hunt_start; AUTH-FIRST. Template: if the app
  has login/registration, do it IMMEDIATELY before any feature exploration
  using the owned account (`login.md`; read OTPs from the owned inbox in a
  separate tab — never leave the target tab); after authenticating capture
  COMPLETE session state (cookie names + flags, localStorage/sessionStorage
  keys, account ID, role, auth method, token locations) and save to
  `notes/auth_session.md`; then click through EVERY page and flow (landing,
  dashboard, settings, billing, admin if reachable) recording per page:
  purpose, inputs/forms, data displayed, API calls (DevTools Network), auth
  requirement, storage, data sensitivity; map auth architecture
  (login/MFA/SSO/recovery), roles, trust boundaries, money/identity/tenant
  workflows; **NO TESTING** — no payloads, no fuzzing, no tampering; NEVER log
  out or clear cookies — preserve the session for the orchestrator; save the
  feature map to `notes/understanding.md`; return AUTH SESSION, what the app
  does, feature map, auth architecture, API inventory, observations,
  prioritized next hunting surfaces with suggested skills.

## 5. Orchestration Flow

- **Phase 1 — BOOT:** load foundations → read this file → lock scope → quick
  tech fingerprint (1-2 requests) → proceed to Phase 2.
- **Phase 2 — EXPLOIT-FIRST HUNT + BOUNDED COLLECTION:** you start hunting
  IMMEDIATELY; all 5 agents spawn at hunt_start fire-and-forget (max 3
  concurrent: run recon + dorking + understand first, then js + fuzzing);
  while they run, you: query wayback/gau/katana for a quick initial surface,
  test obvious endpoints immediately, identify and attack the tech stack; as
  sub-agent results arrive → incorporate → continue hunting. **Required
  handoff:** for every usable endpoint or workflow, resolve and load the
  matching skills, then test it directly — recon/JS/dorking/fuzzing/
  understanding results are inputs to that handoff, never substitutes for it.
- **Phase 3 — DEEP EXPLOIT (continuous):** for each discovered surface:
  resolve skills via `python scripts/skill_registry.py resolve --scenario
  "<surface and technique>" --mode test --paths-only` → build attack model
  (asset/value, auth decision, attacker-controlled inputs) → run the bypass
  ladder (one variable at a time: params, headers, methods, content-types,
  encoding, roles) → response-diff every test (baseline vs attack) → on
  signal: validate yourself (FP DB signature check → independent replay 2x →
  response-diff) → CONFIRMED: update chain board, log to
  `CONTEXT_LEDGER.md`, deepen; REFUTED: add to
  `memory/FALSE_POSITIVE_DB.md`, move on. No signal after thorough testing →
  mark surface tested, next surface.
- **Phase 4 — REPORT (direct, gated):** collect CONFIRMED findings → run the
  HARD FP GATE from `AGENTS.md` (10-question checklist; ANY NO → downgrade to
  LEAD) → apply false-positive-filter →
  evidence-validation-and-severity-calibration → rank by exploitability →
  present to user → do NOT write PoCs/reports until asked.

## 6. WAF Gate Rule (fuzzing-agent)

- fuzzing-agent spawns at hunt_start but MUST check WAF/CDN status from
  recon-agent output before sending aggressive fuzzing requests.
- If a WAF is detected: apply encoding variants, method override,
  content-type switching, chunked encoding, and null-byte bypasses before
  proceeding.
- If recon-agent has not yet delivered WAF info, fuzzing-agent waits briefly,
  then uses conservative probing until status is confirmed.

## 7. Sub-Agent Call Format

- Always use sessions_spawn with:
  - `task` — clear, specific, under 500 tokens;
  - `agentId` — specific type (never default);
  - `context="isolated"` — never fork;
  - `files` — only what's needed;
  - `toolsAllow` — narrow whitelist.

```
sessions_spawn(
  task="<specific task, <500 tokens>",
  agentId="recon-agent",
  context="isolated",
  files=["runtime/opencode/agents/recon-agent.md"],
  toolsAllow=["<narrow whitelist>"]
)
```

- Rules: isolated always; specific agentId always; narrow tools; task under
  500 tokens.

## 8. Sub-Agent Result Handling & Synthesis

- Every sub-agent returns a structured summary with fields: **Surface
  Tested**, **Findings** (type, confidence, evidence_path), **Next Steps**
  (suggestions).
- Synthesis rules:
  1. Read the summary. Do NOT re-read the sub-agent's full context.
  2. Log findings to `CONTEXT_LEDGER.md`.
  3. REUSE the understand-agent's session — if its summary contains an AUTH
     SESSION block (or `notes/auth_session.md` exists) you are already
     authenticated in Chrome — do NOT re-login or re-register. Use the same
     browser session/cookies/tokens for all authenticated testing.
  4. Prioritize the collected surfaces by expected impact (identity, money,
     tenant, admin, data exposure).
  5. Resolve + load matching skills for the top surface, then exploit
     directly.
  6. Validate every CONFIRMED-level result yourself: FP DB → replay 2x →
     response-diff → FP GATE.
- Error handling: sub-agent timeout → log warning, mark surface incomplete,
  continue; no useful data → verify task clarity, retry once with more detail;
  unavailable tools → note the gap, continue with available tools; 3
  consecutive failures → document "agent failure" and handle the task
  directly.

## 9. Context Budget for Multi-Agent

| Budget | Share | Contents |
|--------|-------|----------|
| System + foundations | 5% | briefing, this file, active flow |
| Sub-agent task queue | 5% | pending/active spawns |
| Sub-agent summaries | 25% | compact — includes dorking + understand finds |
| Variant ledger | 10% | tested-variant state per surface |
| History (last turns) | 15% | recent reasoning |
| Tool outputs | 10% | orchestrator's own only |
| Working buffer | 10% | scratch |
| HEADROOM | 20% | never fill |

- Key rule: sub-agents' full internal context is NEVER stored in the
  orchestrator's context — only the 3-10 line summary survives. That is the
  primary benefit of the multi-agent architecture.

## 10. File References

- Sub-agent briefings: `runtime/opencode/agents/{type}-agent.md`
- Sub-agent skill definitions: `skills/{recon,js,etc}.md`
- Context ledger: `testing/<target>/notes/CONTEXT_LEDGER.md` (+
  `memory/CONTEXT_LEDGER.md`)
- Variant ledger: per-surface in `notes/`
- Understanding map: `testing/<target>/<subdomain>/notes/understanding.md`
- Auth session: `notes/auth_session.md`
- False positive database: `memory/FALSE_POSITIVE_DB.md`