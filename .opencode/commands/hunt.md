---
description: Advanced autonomous bug bounty hunting with Chrome DevTools
agent: build
---

# Autonomous Browser Hunt

Target or notes:
$ARGUMENTS

**Mandate: Follow all workspace rules in `AGENTS.md` and `PRIORITIZATION.md`.**
**Browser mandate: ALWAYS use MCP (chrome-devtools-mcp) + Chrome DevTools together for every browser interaction. Never use one without the other.**

**Exploit-first mandate:** The objective is a reproducible, high-impact vulnerability. Recon, OSINT, JS analysis, and fuzzing are bounded support work. Once a usable surface exists, resolve its skills and test it immediately; do not wait for a complete inventory or spend the session collecting data without an exploit attempt.

## Step 0: Owned-Account Login — MANDATORY BEFORE EVERYTHING

**Do NOT start any recon, scope lock, fuzzing, or testing before the mail inbox is logged in.**

1. Read `login.md` at the workspace root — it contains the login credentials and the exact Chrome MCP login steps.
2. Open the mail inbox via Chrome MCP (chrome-devtools-mcp / chrome browser tools): navigate to the mail URL, click "Sign in", select the sign-in tab, type the email and password from `login.md`, click Next until the inbox loads.
3. Confirm the inbox is loaded before proceeding.
4. If already logged in from a previous session, verify the inbox is open; do not re-login unnecessarily.

**Email policy (applies to the whole hunt):**
- Use ONLY the owned account from `login.md`. Do NOT use temp-mail, guerrillamail, mohmal, or any other address.
- Use this inbox for ALL account registration, verification codes, OTPs, magic links, reset links, and email delivery.
- The agent HAS full access to this inbox — read codes/links directly from it, no need to ask the user.
- Window discipline: keep the target form/tab open; open the inbox in a separate tab to read the OTP/link, then return to the target tab.

## Hunt Start Contract

Before optional URL history, broad fuzzing, or other collection expands, the orchestrator must:

1. Select the highest-value usable endpoint, workflow, object, token, upload, URL fetcher, or role boundary from the supplied target, prior notes, or existing browser state.
2. Run the canonical skill resolver and load every returned skill.
3. Define the asset, authority decision, attacker-controlled input, and expected impact.
4. Capture a baseline and execute the first safe controlled exploit variant.
5. Record the result in the tested-variant ledger, then use recon and sub-agents to expand the active exploit path.

## Mandatory Sub-Agent Coverage

The hunt must cover every registered sub-agent in staged waves. Never wait for collection before exploiting, and never run two agents against the same endpoint. The runtime cap is three concurrent agents. **All exploitation and validation is done by the orchestrator directly — the five sub-agents collect only.**

- `recon-agent`: dispatch at hunt start for minimum-viable host, route, technology, and WAF/CDN detection.
- `dorking-agent`: dispatch at hunt start for scope-safe public-source discovery.
- `understand-agent`: dispatch at hunt start — AUTH-FIRST: logs in/registers with the owned account, clicks through the whole app, maps features/roles/auth/data flows, and delivers the live session credentials (notes/auth_session.md) so you never re-login (NO testing).
- `js-agent`: dispatch at hunt start for JS bundle and source map analysis. AUTH-AWARE: it logs in with the owned account when JS only appears after login (best-effort — proceeds with public JS if login is impossible) and hands the session to you.
- `fuzzing-agent`: dispatch at hunt start for tech-aware endpoint/parameter discovery (WAF-gated by recon-agent output).

For every spawn, completion, error, retry, or fallback, update `notes/CONTEXT_LEDGER.md` with the agent ID, task, target surface, loaded skills, result, evidence path, and next exploit action. The complete staged dispatch plan is authoritative in `runtime/registry.json` and is printed by `scripts/runtime_preflight.py`.

## Artifact Path Rule

Before creating any file or directory, derive the target workspace path from the supplied target:

- Root-domain work: `testing/<root-domain>/`
- Host/subdomain work: `testing/<root-domain>/<scope-folder>/`
- Standard target folders: `notes/`, `requests/`, `responses/`, `screenshots/`, `scripts/`, `scans/`, `wordlists/`, `urls/`, `subdomains/`, `evidence/`, and `reports/`

Never create target artifacts directly in the project root.

## Scope Lock

- Parse and print the active scope root, storage root, and enumeration boundary before recon.
- Treat an exact host as exact-host scope unless the user explicitly expands scope.
- For exact-host scope, keep the parent/root domain and sibling hosts out-of-scope by default; do not enumerate or fuzz `*.<root-domain>`.
- Stay on the supplied target first. Do not actively test another target, sibling host, root wildcard, or adjacent service until the supplied target is exhausted and the user approves expansion.
- Use outside targets only as passive context unless a very high-signal lead directly affects the supplied target; ask before active testing.
- Treat a wildcard as limited to that wildcard suffix.
- Store artifacts only in the derived target workspace path.
- Use the interleaved 4-phase practical flow: BOOT → SURFACE DISCOVERY ↔ EXPLOIT → REPORT. Recon and testing run together, not sequentially. Do not wait for full recon before testing.

## Required Startup

1. Read `agent-briefing.md` first.
2. Load `skills/master-bugbounty-rules.md` and `.agents/skills/learning-engine-integration/SKILL.md`.
3. **Load your runtime loader:** Load `runtime/opencode/loader.md` — **execute each BOOT step verbatim. Do not skip any step.**
4. Verify which local tools are available.
5. Run `python scripts/runtime_preflight.py --target "<exact target>" --scenario "<initial surface>" --mode hunt --workspace "testing/<root>/<subdomain>" --ensure-session`; stop if it reports `blocked`.
6. Before any bug-class test or sub-agent spawn, check the skill registry and load matching skills. Skills load on demand, not upfront.

## Practical Hunting Flow (Parallel Phases)

**You hunt from second 1. Never wait for recon.** Sub-agents run in the background. You start exploiting immediately with what you have.

### Phase 1: BOOT (< 5 minutes)
- Lock scope, fingerprint tech stack, check prior history, load foundations
- Load `runtime/opencode/loader.md` and `runtime/opencode/ORCHESTRATION.md`
- Create session bootstrap note
- **READY TO HUNT** — spawn all 5 collection agents at hunt_start (recon, dorking, understand, js, fuzzing — fire-and-forget), start hunting immediately

### Phase 2: HUNT + Parallel Sub-Agents (continuous, never stops)

```
YOU (hunt immediately):                     SUB-AGENTS (background):
─────────────────────                       ────────────────────────
• Initial surface grab (wayback, gau)       • recon-agent runs
• Test obvious endpoints (login, api,       • dorking-agent runs
  admin, graphql) right now                 • understand-agent maps the app
• As you find things → test them            • js-agent runs
• Sub-agent results arrive mid-hunt → read  • fuzzing-agent runs (WAF-gated)
  → incorporate → keep hunting
```

**Key rules:**
- You NEVER wait for a sub-agent. Fire-and-forget every spawn.
- Start with the first controlled exploit attempt from the supplied target or prior notes; use wayback, gau, katana, and similar collection only in parallel or when discovery blocks the next exploit path.
- Test everything you find immediately — don't save it for "after recon"
- When recon-agent finishes: read summary, update targets, keep hunting
- When understand-agent finishes: read its AUTH SESSION block — you are authenticated in Chrome, do NOT re-login/re-register; use its feature map to prioritize which surfaces to attack first (money, identity, tenant, admin, data)
- When js-agent finishes: add endpoints/secrets to your attack list; if it logged in, reuse its session (notes/auth_session.md / js_cookies.txt) — no re-login needed; keep hunting
- When fuzzing-agent finishes: add discovered paths/params, keep hunting
- Sub-agent results are MID-HUNT INTEL FEEDS, not gates

### Phase 3: DEEP EXPLOIT (same as Phase 2 — you never stopped)

You've been hunting since Phase 2. This phase is the same loop — deepen as more intel arrives:

1. **Skill trigger** — Load matching skills for the surface's tech + vuln class
2. **Attack model** — asset/value, auth boundary, attacker controls, expected proof
3. **Test** — bypass ladder (params, headers, methods, content-type, encoding, roles)
4. **Response-diff** every test — baseline vs attack response
5. **If signal found:** chain board → validate it yourself (FP DB signature check → replay 2x → response-diff)
6. **If no signal after thorough testing (all bypass families):** mark low-yield, next surface
7. **Take your time — exploitation is the main goal.** Don't rush. Spend 30-60+ min per high-value surface. Exhaust all bypass families, encode variants, role switches, and workflow states before moving on.

### Phase 4: REPORT (gated by user)
- Every finding must pass YOUR validation (FP DB → replay 2x → response-diff) + the HARD FP GATE from AGENTS.md before it is reported
- Apply false-positive filter + evidence validation on CONFIRMED findings only
- Rank findings by exploitability
- Leave structured summary, tested surfaces, open leads, sub-agent status
- Do NOT write PoCs or formal reports — wait for explicit user instruction

**Note:** If stalled on a surface, change one variable and retry. If still stalled, document and return to surface discovery from a new angle. The hunt loop is perpetual — you don't exit Phase 2/3 until you've exhausted every surface or the session ends.

## Systematic Fuzzing Order

When fuzzing for hidden endpoints, parameters, or functionality, follow this exact priority:
1. **Technology-Aware Common Words FIRST:** Generate candidates from the target's identified technologies. See `tech-fingerprint` output → fuzzing strategy. **AI/LLM apps: always fuzz for `/llms.txt`, `/llms.md`, `/ai-plugin.json`, `/*.md`, `/docs/*.md`, `/api/*.md`.**
2. **Common Endpoint Patterns by App Type:** If tech-aware yields nothing, try common patterns for the app type (API → `/users`, `/admin`, `/health`; CMS → common CMS paths; SPA → JS routes). **For ALL types, fuzz for exposed `.md` files: `/*.md`, `/docs/*.md`, `/api/*.md`, `/backend/*.md`, `/swagger.md`.**
3. **Existing Wordlists LAST:** Only use SecLists/Assetnote/project wordlists when the first two priorities are exhausted.

## Exact-Host Fuzzing Boundary

If the target is a full hostname, exhaust that host first. Only after documenting primary-scope exhaustion may you generate tightly related hostname permutations inside the original hierarchy. For `documentsmanagement-stage.np.dmm.business.comcast.com`, valid first-pass patterns are `documentsmanagement-FUZZ.np.dmm.business.comcast.com`, `documentsmanagement-stage.FUZZ.dmm.business.comcast.com`, and `documentsmanagement-stage.np.FUZZ.business.comcast.com`. Do not fuzz `FUZZ.business.comcast.com` or broad `*.business.comcast.com` without explicit approval or a documented active exploit-chain requirement.

## Output Structure

1. Scope and assumptions
2. Loaded and deferred skills
3. Safe exploit tests performed (starting before broad collection)
4. Evidence captured
5. Confirmed findings and unproven leads separated by impact gate
6. Recon sources, assets, services, endpoints, and technologies used to expand exploit paths
7. JavaScript findings and workflow map
8. Attack surface map and prioritized hypotheses
9. Chain board, tested variants, failed approaches, pivots, and next best steps