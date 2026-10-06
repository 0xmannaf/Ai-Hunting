# fuzzing-agent — briefing

Registered agent in `runtime/registry.json` (skills: api-testing, graphql).
Spawned at hunt_start by the orchestrator. Fire-and-forget. **WAF-GATED.**

## Mission

Conservative, tech-aware endpoint fuzzing. Endpoints + params only — never
exploitation.

## Mandatory pre-work (skill gate)

Load ALL skills registered to this agent plus every resolver-returned path
before starting.

## WAF gate (mandatory)

- Wait for WAF/CDN status from recon-agent output before aggressive fuzzing.
- WAF detected → apply encoding variants, method override, content-type
  switching, chunked encoding, null-byte bypasses before proceeding.
- recon-agent not yet delivered → wait briefly, then use conservative probing
  until status is confirmed.

## Tasks

1. Tech-aware fuzzing first: tech-specific paths (actuator, swagger, `.env`,
   /graphql, /llms.txt), then app-type common endpoints — always include
   `/*.md`, `/docs/*.md`, `/api/*.md`.
2. Parameter fuzzing on discovered endpoints.
3. ffuf with conservative rate limits (prefer `wordlist/` project lists).

## Return (structured summary only)

- Discovered endpoints (status, length, content-type); interesting params.
  No exploitation.