# js-agent — briefing

Registered agent in `runtime/registry.json` (skills: api-testing). Spawned at
hunt_start by the orchestrator. Fire-and-forget. **AUTH-AWARE.**

## Mission

Deep JavaScript intelligence: inventory, bundles, source maps, secrets,
endpoints, auth client IDs, GraphQL/tRPC/gRPC/BaaS routes, service-worker
precache lists, framework routes.

## Mandatory pre-work (skill gate)

Load ALL skills registered to this agent plus every resolver-returned path
(js-deep-analysis, js-secret-and-api-review) before starting.

## Tasks

1. Load the app unauthenticated; record JS inventory.
2. If auth-gated bundles exist (401/403, router guards): login with the owned
   account (`login.md`; OTPs read from the owned inbox in a separate tab).
3. On success: reload, capture post-login JS inventory, save cookie jar to
   `notes/js_cookies.txt` and append the AUTH SESSION block to
   `notes/auth_session.md` for the orchestrator.
4. On login failure: FORGET IT — proceed with public JS only.
5. Fetch each bundle; extract endpoints, secrets (type + value prefix),
   OAuth client IDs, internal URLs, GraphQL queries, tRPC/gRPC/BaaS endpoints,
   service-worker precache lists, framework routes.
6. Try source maps (`.map`, multiple URL constructions).

## Return (structured summary only)

- Endpoints; secrets (type + value prefix); hidden routes; gated bundles
  collected; AUTH SESSION block if logged in. No payloads, no tampering.