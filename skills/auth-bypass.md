---
id: auth-bypass
name: Authentication Bypass
phase: exploit
severity: critical
aliases: [auth-bypass, authentication-bypass, login-bypass, authz-bypass]
tags: [auth, web, access-control]
---

# Authentication Bypass

## When to use
Use on login, registration, password reset, MFA, and token-validation flows. Trigger when JWTs, session cookies, or API keys are present, or when admin panels are reachable. Also apply to forced-browsing of authenticated routes and password-reset logic flaws.

## Quick checks
1. Inspect JWT: decode header/payload, test `alg:none` and algorithm confusion.
2. Check if signature is verified by tampering a claim (e.g. `"role":"admin"`).
3. Test login response manipulation: `{"success":false}` -> `{"success":true}`.
4. Try default/weak creds on admin panels (`admin:admin`, `admin:password`).
5. Test password reset: host header injection, token reuse, predictable tokens.
6. Bypass path checks: `/admin`, `/admin/`, `/admin..;/`, `/%2e/admin`.

## Payloads / test cases
- JWT `alg:none`: header `{"alg":"none","typ":"JWT"}`, empty signature.
- HS256 confusion: sign with public key as HMAC secret.
- `{"sub":"admin","role":"admin"}` with original signature (verify if enforced).
- `X-Forwarded-For: 127.0.0.1`, `X-Original-URL: /admin` header bypasses.
- Path tricks: `/admin/..;/`, `//admin`, `/./admin`, `/admin%20`.
- Reset token brute: short numeric tokens or tokens derived from timestamp.

## Detection & confirmation
1. Prove access to a protected resource that returns sensitive data or admin actions.
2. Capture the exact tampered token/header and the successful response.
3. Confirm the server accepted the forged credential (not cached page).
4. For reset flaws, demonstrate receiving another user's token in your inbox.
5. Verify the bypass is reproducible across sessions and browsers.

## Escalation
Unauthenticated admin access or account takeover -> P1; MFA bypass on privileged account -> P1; weak reset on low-priv user -> P2 (see prioritization.md).

## Evidence to capture
- Original and tampered tokens (redact secrets).
- Request/response showing protected resource access.
- Admin panel screenshot with the bypassed session.
- Reset email/token proof with headers.
- Timestamped reproduction steps.

## Common false positives
- Pages that look admin-only but are public marketing routes.
- Client-side role checks only (server still enforces).
- Cached authenticated pages served to anonymous users.
- Tokens valid because of a legitimate long-lived session, not a bypass.

## Related skills
- [[idor]]
- [[api-testing]]
- [[sqli]]
- [[xss]]
