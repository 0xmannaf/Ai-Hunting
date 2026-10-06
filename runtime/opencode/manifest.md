# OpenCode Runtime Manifest

- **Runtime:** OpenCode — Practical 4-Phase Interleaved Flow
- **Last Updated:** 2026-10-01
- **Purpose:** define what OpenCode provides, requires, and governs. The
  authoritative machine-readable source is `runtime/registry.json`; generated
  snapshots (agent tables, skill categories) are reference views only —
  **registry.json wins on any conflict**.

## 1. Header

| Field | Value |
|-------|-------|
| Title | OpenCode Runtime Manifest |
| Runtime | OpenCode — Practical 4-Phase Interleaved Flow |
| Last Updated | 2026-10-01 |
| Purpose | Define what OpenCode provides, requires, and governs |
| Canonical source | `runtime/registry.json` (authoritative, machine-readable) |
| Compatibility | This file + `ORCHESTRATION.md` + `loader.md` are reference views |

## 2. Runtime Profile

| Aspect | Value |
|--------|-------|
| Architecture | Multi-Agent: Orchestrator + 5 collection sub-agents; orchestrator does ALL exploitation + validation |
| Workflow | Exploit-first orchestrator: BOOT → resolve skills → immediate exploit loop with bounded dorking/recon/JS/fuzzing/understanding → validate → REPORT |
| Context strategy | Orchestrator loads foundations + `ORCHESTRATION.md`; sub-agents get fresh isolated context per spawn |
| Skill activation | Every agent resolves the scenario via `scripts/skill_registry.py` and loads every returned active skill path |
| Sub-agent types | dorking-agent, recon-agent, js-agent, fuzzing-agent, understand-agent |
| Phase coverage | BOOT (<5 min) → DISPATCH (parallel sub-agents) → SYNTHESIS → EXPLOIT (orchestrator direct) → REPORT (gated) |
| Parameter testing | Orchestrator, comprehensive all vectors |
| Memory model | Orchestrator maintains `CONTEXT_LEDGER.md`, sub-agent summaries, variant ledger; sub-agents stateless |
| Scope model | Locked at start; scope-enforcer gate loaded before any expansion; sub-agents inherit scope constraints |
| Learning | Orchestrator calls the learning engine; sub-agents do not persist learning |
| Reporting | Gated — no auto-reports |
| Parallelism | Max 3 concurrent sub-agents (recon → dorking → understand → js → fuzzing waves) |

## 3. What OpenCode Provides (shared knowledge — read-only reference)

| Resource | Location | Role |
|----------|----------|------|
| Canonical skill registry | `runtime/registry.json` | All skills indexed by attack surface, load order, autonomous directives — ALL agents use it as truth |
| Signal prioritization | `prioritization.md` | P1-P4, chain analysis, when to stop; reference only — flow defined in `ORCHESTRATION.md` + `AGENTS.md` |
| Foundation rules | `skills/master-bugbounty-rules.md` | Load FIRST |
| Learning engine skill | `.agents/skills/learning-engine-integration/SKILL.md` | Load SECOND |
| Session briefing | `agent-briefing.md` | Read first, every session |
| Memory base | `memory/` (`methodology.md`, `patterns.md`, `report-lessons.md`, `targets/`) | Learned knowledge |
| Evidence repository | `writeups/` (`index.md`, `processed/`, `raw/` via /update) | Corpus |
| Skill library | `skills/` + `.agents/skills/` | One file per skill, loaded on demand, never duplicated locally |
| Learning engine | `learning_engine/` | Python module, 5 hooks |
| Multi-agent config | `ORCHESTRATION.md` + `agents/` directory (5 briefing files) | Orchestration |
| Runtime config | `loader.md` + `manifest.md` (this file) | Boot + contract |

## 4. What OpenCode Requires at Startup

### Files that MUST exist

| File | Purpose | Location |
|------|---------|----------|
| Session briefing | current knowledge state | `agent-briefing.md` |
| Canonical registry | skills/routes/agents/commands | `runtime/registry.json` |
| Signal engine | P1-P4 framework | `prioritization.md` |
| Foundation skill | master rules (load first) | `skills/master-bugbounty-rules.md` |
| Foundation skill | learning hooks (load second) | `.agents/skills/learning-engine-integration/SKILL.md` |
| Skill library | attack-surface playbooks | `skills/` + `.agents/skills/` |
| Memory base | lessons/patterns/methodology | `memory/` |
| Learning engine | Python module + SQLite | `learning_engine/` |
| Evidence repository | writeup corpus | `writeups/` |
| Target trees | hunt artifacts | `testing/` |

### Workspace requirements

- `testing/<root-domain>/` structure with standard subfolders: `notes`,
  `requests`, `responses`, `screenshots`, `scripts`, `scans`, `wordlists`,
  `urls`, `subdomains`, `evidence`, `reports`.
- Chrome for app exploration; terminal for local tools (ffuf, httpx, katana,
  nuclei, subfinder, amass — verify availability at boot).
- Optional: user-provided Burp Collaborator domain. Never curl/access it
  directly — embed in payloads only.

## 5. Agent Definitions

### Orchestrator (main agent)

- Full tool access, full freedom; performs ALL exploitation and validation
  directly.
- Consumes the sorted final data from the five agents, prioritizes next
  steps, resolves + loads skills, hunts, validates against the FP gate.
- Responsibility: decompose collection into the 5 parallel sub-agents;
  exploit everything yourself.
- Tools: full (read, write, glob, grep, web_search, bash, sessions_spawn,
  chrome browser + devtools MCP).
- Loaded at boot: `agent-briefing.md`, `AGENTS.md`, `ORCHESTRATION.md`,
  master-bugbounty-rules, learning-engine-integration.

### Sub-agent registry (canonical source: `runtime/registry.json`)

| Agent ID | Role | Tool whitelist | Max spawns/session | Context |
|----------|------|----------------|--------------------|---------|
| dorking-agent | Passive OSINT, zero target contact | read, glob, grep, web_search, bash (public sources only) | 2 | isolated |
| recon-agent | Passive + active recon: subdomains, URLs, tech fingerprint, DNS brute-force, port probes, HTTP probes, WAF/CDN detection | read, glob, grep, web_search, bash (subfinder, amass, httpx, katana, waybackurls, gau, curl, Test-NetConnection) | 2 | isolated |
| js-agent | JS bundle + source map analysis, AUTH-AWARE | read, glob, grep, web_search, bash (curl, python), chrome MCP | 4 | isolated |
| fuzzing-agent | Tech-aware endpoint/param fuzzing, WAF-gated | read, write, glob, bash (ffuf, curl, httpx) | 6 | isolated |
| understand-agent | AUTH-FIRST browse + click; maps app; delivers session to `notes/auth_session.md`; NO testing | read, glob, grep, web_search, bash (safe GET only), chrome MCP | 2 | isolated |

### Spawning rules

- `sessions_spawn(task, agentId, context="isolated", toolsAllow=[...])`.
- Never `context="fork"`; never omit `agentId`; `toolsAllow` must match the
  whitelist exactly.
- Max 3 concurrent. 3 consecutive failures → document + handle directly.
- Timeout: 5 min default; 10 min for recon-agent and understand-agent.

### Sub-agent briefings

- `runtime/opencode/agents/{type}-agent.md` loaded on spawn — define identity,
  tool whitelist, procedure, output format, quality rules.

## 6. Workflow Execution Model

Every hunt follows this orchestrated dispatch sequence:

1. **BOOT (<5 min):** read `agent-briefing.md` → read `ORCHESTRATION.md` →
   load foundations → lock scope, quick fingerprint, check workspace history →
   session bootstrap → READY TO DISPATCH.
2. **DISPATCH ALL COLLECTION AGENTS** at hunt_start (max 3 concurrent: recon +
   dorking + understand first, then js + fuzzing): recon-agent (passive +
   active recon + WAF/CDN detection), dorking-agent (passive OSINT),
   understand-agent (AUTH-FIRST, delivers live session — no re-login),
   js-agent (AUTH-AWARE), fuzzing-agent (WAF-GATED). Do NOT wait — start
   exploiting immediately; as results arrive update `CONTEXT_LEDGER.md` and
   incorporate.
3. **EXPLOIT ORCHESTRATOR DIRECT (continuous):** per surface resolve + load
   skills (`python scripts/skill_registry.py resolve --mode test
   --paths-only`) → attack model → baseline → bypass ladder (params, headers,
   methods, content-type, encoding, roles) → response-diff every test →
   update `CONTEXT_LEDGER.md`; prioritize with the understand-agent feature
   map (money, identity, tenant, admin, data first).
4. **VALIDATE ORCHESTRATOR DIRECT:** for each HIGH-CONFIDENCE+ finding: FP DB
   signature check → independent replay 2x → response-diff → HARD FP GATE from
   `AGENTS.md`; CONFIRMED → chain board + evidence path; REFUTED → add to
   `memory/FALSE_POSITIVE_DB.md`.
5. **REPORT (gated):** collect CONFIRMED → FP filter + evidence validation →
   rank by exploitability → structured summary in notes → no PoCs/reports
   until asked.

### Key discipline requirements

| Discipline | Requirement |
|------------|-------------|
| Multi-agent | Orchestrator full freedom; every hunt covers all 5 stages; direct work never replaces handoff records |
| Exploitation | Only the orchestrator |
| Validation | Only the orchestrator |
| Startup | Foundations + `ORCHESTRATION.md` < 5 min; everything else on demand |
| Sub-agent context | Always isolated |
| Tool whitelists | Narrow per role |
| Scope | Locked; expansion only for chains/shared vulns |
| Context budget | 25% headroom; never store sub-agent contexts |
| Finding pipeline | OBSERVATION → LEAD → HIGH-CONF → CONFIRMED → VALIDATED → REPORTABLE |
| No-progress | 5 same-pattern results → change surface |
| Circuit breaker | 5x 403/429 → 60s backoff → stop surface |
| Sub-agent failures | 3 → document, handle directly once, then skip |
| Parallelism | Max 3; never two on one endpoint |
| Memory | Orchestrator keeps ledger + summaries + variant ledger |
| Bypass strategy | 3-5 families on promising leads |
| Evidence | Raw HTTP from own evidence files |
| Reporting | Gated |
| Browser | Reuse window; new tab default |

## 7. Skill Activation Manifest

- OpenCode automatically activates all applicable skills per discovered
  surface.
- **Mandatory load order:** 1) master-bugbounty-rules, 2)
  learning-engine-integration, 3) all other skills per category as triggered.
- Compatibility trigger map — **canonical source = `runtime/registry.json`;
  always run the resolver** (`python scripts/skill_registry.py resolve
  --scenario "<surface>" --mode test --paths-only`):

| Category | Registry skills |
|----------|-----------------|
| Recon/Discovery | recon, subdomain-enumeration, subdomain-takeover, dorking |
| APIs | api-testing, graphql |
| Parameters | no dedicated skill in registry — resolve via api-testing |
| Auth | auth-bypass, jwt, oauth |
| Authz | idor |
| Client | xss, csrf |
| Blind/OOB | ssrf (callback/OOB-capable) |
| Realtime | no dedicated skill in registry — race-condition covers concurrency |
| Infrastructure | no dedicated skill in registry — subdomain-takeover is closest |
| Injection/Parsing | sqli, ssti, lfi, xss, file-upload |
| Cloud/Mobile/AI | no dedicated skill in registry |
| Web3 | no dedicated skill in registry |
| Workflow/Chain | business-logic, race-condition, open-redirect, csrf, file-upload |
| Foundation | master-bugbounty-rules, learning-engine-integration (boot layer, outside the 20-skill registry budget) |
| Reporting | no registry skill — `report.md` command + §9 standards govern |

## 8. Memory & Learning Model

- **Continuous context:** maintain every URL/endpoint/param tested, all
  payloads/variants/bypass families, success indicators, FPs, dead ends,
  findings with proof level + chains, active/deferred hypotheses — in
  `notes/` + `memory/CONTEXT_LEDGER.md`.
- **Learning engine hooks** (`learning_engine/`, 5 hooks):
  - `before_recon(target, techs)`
  - `during_testing(signals)`
  - `after_finding(target, endpoint, vulnerability_class, signals,
    validation_state, source_provenance)`
  - `before_summary(findings)`
  - `after_triage(finding_id, feedback_type, notes, provenance)` — never
    session-level outcomes.
- **Knowledge priority order:** `memory/targets/<vuln>.md` →
  `memory/report-lessons.md` → `memory/patterns.md` → `memory/methodology.md`
  → `writeups/processed/` (5-7 best matches) → base training.

## 9. Reporting & Evidence Standards

- **Minimum Reportability Bar:** reproducible raw HTTP proving server-side
  impact; no physical access / social engineering / self-XSS; real-world
  impact demonstrated; tested across representative contexts.
- **Evidence checklist:** scope confirmation; exact URL/endpoint/method/
  timestamp; raw baseline + modified request/response; account/role/tenant/
  ownership context; before/after state for writes; screenshots support only;
  impact statement + limitations + safe reproduction; FP reasoning when weak.
- Reports land in `testing/<root>/<sub>/reports/`; never project root.

## 10. When Hunt Ends

- **If finding:** update the learning engine (`after_finding` +
  `after_triage`), preserve evidence, wait for user instruction on PoC/report.
- **If no finding:** leave structured summary, tested-surfaces list,
  tested-variant ledger with full parameter coverage, open leads, deferred
  follow-ups, all discovered URLs with attack models in `notes/`.
- **Always:** update target notes; call the learning engine to ingest the
  session outcome (`before_summary` → `after_triage`).

## 11. Differences from Antigravity CLI Runtime

| Aspect | OpenCode (`runtime/opencode/`) | Antigravity CLI (`runtime/antigravity/`) |
|--------|-------------------------------|-------------------------------------------|
| Architecture | Multi-agent (orchestrator + 5 sub-agents) | Single-agent |
| Phases | Exploit-first dispatch | 4 interleaved phases |
| Preload | Foundations + `ORCHESTRATION.md` | Foundations only |
| Skill activation | Orchestrator: any skill, any time | Triggered as needed |
| Memory model | Comprehensive ledger | Lightweight P1/P2 |
| Parameter testing | Systematic, all vectors | High-signal only |
| Finding validation | FP DB + replay 2x + response-diff + FP GATE | Self-validated |
| Time per surface | 10-15 min exhaust bypass families | 10-15 max, skip P4 |
| Primary guide | `ORCHESTRATION.md` + `AGENTS.md` | `prioritization.md` |

## 12. Next Steps

1. **Startup:** execute `loader.md` → load foundations + `ORCHESTRATION.md` →
   spawn all 5 collection agents.
2. **Hunting:** exploit immediately; bounded feeds; max 3 concurrent.
3. **Spawning:** `sessions_spawn` with `context="isolated"`; never fork.
4. **Synthesis:** summaries only; prioritize; update `CONTEXT_LEDGER.md`.
5. **Validation:** every HIGH-CONFIDENCE+ finding → FP DB → replay 2x →
   response-diff → FP GATE.
6. **Reporting:** collect CONFIRMED, FP filter, rank, present — no
   auto-reports.

OpenCode runtime is now initialized.