---
id: api-testing
name: API Testing
phase: exploit
severity: high
aliases: [api, rest, rest-api, swagger, openapi, web-api]
tags: [api, web, json]
---

# API Testing

## When to use
Use when recon reveals `/api`, `/v1`, `/graphql`, Swagger/OpenAPI docs, or mobile app traffic. Trigger when the app is SPA/mobile heavy and UI hides endpoints. Apply before generic web testing so object-level and auth flaws are caught early.

## Quick checks
1. Fetch `/swagger.json`, `/openapi.json`, `/api-docs`, `/graphql` (introspection query).
2. Enumerate versions: `/v1/`, `/v2/`, `/v3/` and compare auth requirements.
3. Check HTTP methods with `OPTIONS` and try `PUT`/`DELETE`/`PATCH` on read endpoints.
4. Compare unauthenticated vs authenticated responses for the same endpoint.
5. Inspect JSON error messages for stack traces, field names, and internal IDs.
6. Test content types: send `application/xml` or form data where JSON is expected.

## Payloads / test cases
- GraphQL introspection: `{"query":"{__schema{types{name}}}"}`.
- Method swap: `POST /api/user/1` -> `DELETE /api/user/1`.
- Mass assignment: `{"username":"u","role":"admin","isAdmin":true}`.
- Content-type confusion: `Content-Type: application/x-www-form-urlencoded` against a JSON endpoint.
- Version downgrade: call `/v1/users` when `/v2/users` enforces stricter auth.
- Parameter pollution: `?id=1&id=2` and `{"id":1,"id":2}`.

## Detection & confirmation
1. Capture the baseline request/response with full headers and body.
2. Replay with a modified parameter and diff the response (status, length, fields).
3. Confirm the change is server-side (persisted via a follow-up GET), not just echo.
4. Test with a second account to prove cross-tenant impact (BOLA).
5. Save both requests to evidence and note exact endpoint and parameter.

## Escalation
Unauthenticated admin API access or mass data exposure -> P1; authenticated BOLA/privilege escalation -> P1/P2; verbose errors/versioning only -> P3 (see prioritization.md).

## Evidence to capture
- Raw request and response pairs (headers + body).
- Swagger/OpenAPI spec download.
- Diff output showing parameter effect.
- Second-account proof for authorization bugs.
- Endpoint inventory with auth status.

## Common false positives
- Responses that echo input without server-side effect.
- API gateways returning generic 200 for unknown routes.
- Versioned endpoints that are actually aliases to the same handler.
- Rate-limit or WAF blocks misread as authorization failures.

## Related skills
- [[idor]]
- [[auth-bypass]]
- [[ssrf]]
- [[sqli]]
