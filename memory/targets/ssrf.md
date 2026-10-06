# Server-Side Request Forgery (SSRF) — per-class checklist

> Companion to `skills/ssrf.md` and the registry. Filled from confirmed findings
> and FPs; keep it current.

## Checklist

1. Find server-side fetch surfaces: URL inputs, webhooks, image proxies,
   PDF generators, SSO/redirect handlers, feed importers.
2. Test with a canary domain first (DNS/HTTP log) — non-destructive.
3. Confirm internal reachability: 169.254.169.254 (cloud metadata) only as a
   demonstration, minimal and scoped.
4. Check redirect-follow behavior (SSRF via open redirect chains).
5. Check protocol schemes: file://, gopher://, dict:// (as applicable).

## Confirmed payloads / observations

_(none yet)_

## False-positive patterns

_(none yet — see memory/FALSE_POSITIVE_DB.md)_

## Evidence requirements

- Request showing the URL parameter + response differing between canary and
  internal address (or canary hit log).
- Never capture metadata secrets into evidence; note the exposure only.