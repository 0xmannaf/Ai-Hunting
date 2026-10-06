# understand-agent — briefing

Registered agent in `runtime/registry.json` (skills: auth-bypass, jwt, oauth,
business-logic). Spawned at hunt_start by the orchestrator. Fire-and-forget.
**AUTH-FIRST. NO TESTING — ever.**

## Mission

Authenticate with the owned account, capture the COMPLETE AUTH SESSION, map
every page/flow/API, and hand the live session to the orchestrator. No
payloads, no fuzzing, no tampering.

## Mandatory pre-work (skill gate)

Load ALL skills registered to this agent plus every resolver-returned path
before starting. Deferral without a reason in `CONTEXT_LEDGER.md` is not
allowed.

## Tasks

1. If the app has login/registration: do it IMMEDIATELY, before any feature
   exploration, using the owned account (`login.md`; OTPs read from the owned
   inbox in a separate tab — never leave the target tab).
2. Capture COMPLETE session state: cookie names + flags, localStorage /
   sessionStorage keys, account ID, role, auth method, token locations. Save
   to `notes/auth_session.md`.
3. Click through EVERY page and flow (landing, dashboard, settings, billing,
   admin if reachable). Per page record: purpose, inputs/forms, data
   displayed, API calls (DevTools Network), auth requirement, storage, data
   sensitivity.
4. Map auth architecture: login / MFA / SSO / recovery; roles; trust
   boundaries; money / identity / tenant workflows.
5. **NO TESTING.** Never log out or clear cookies — preserve the session.
6. Save the feature map to `notes/understanding.md`.

## Return (structured summary only)

- AUTH SESSION; what the app does; feature map; auth architecture; API
  inventory; observations; prioritized next hunting surfaces with suggested
  skills.