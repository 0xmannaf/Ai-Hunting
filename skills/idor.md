---
id: idor
name: Insecure Direct Object Reference (BOLA)
phase: exploit
severity: high
aliases: [idor, bola, broken-object-level-authorization, object-reference, access-control]
tags: [web, api, authorization]
---

# Insecure Direct Object Reference (BOLA)

## When to use
Use when endpoints reference objects by ID (`/user/123`, `?invoice_id=`, UUIDs) and authorization is checked per request. Trigger when two accounts exist and API calls include numeric or guessable identifiers. Prioritize on APIs and export/download endpoints.

## Quick checks
1. Create two accounts (A and B) and capture each one's object IDs.
2. Request A's object while authenticated as B; compare status and body.
3. Swap numeric IDs sequentially (`1,2,3`) on read endpoints.
4. Try the object via alternate paths: `/api/users/1`, `/api/v1/users/1`, `/users/1.json`.
5. Remove or alter auth headers to test unauthenticated access.
6. Check exported files/receipts/PDFs served with predictable names.

## Payloads / test cases
- `GET /api/v1/users/1002` with B's token while 1002 belongs to A.
- `GET /api/invoices?id=5001` -> change to `5002`.
- `POST /api/orders/{"userId":1002}` with B's session.
- `DELETE /api/comments/1234` owned by another user.
- `GET /download?file=receipt_1002.pdf` (predictable filename).
- GraphQL: `{"query":"{ user(id:1002){ email } }"}`.

## Detection & confirmation
1. Capture the request as account A and as account B for the same object ID.
2. Confirm B receives A's data (200 + body) or performs a state change.
3. Verify the object truly belongs to A (email/name in response).
4. Reproduce twice with fresh tokens to rule out caching.
5. Test horizontal (same role) and vertical (lower role -> higher) cases.

## Escalation
Cross-tenant read/write of sensitive data -> P1; same-tenant IDOR or non-sensitive metadata -> P2/P3 (see prioritization.md).

## Evidence to capture
- Paired requests: A's legitimate call and B's unauthorized call.
- Responses showing object ownership (redacted PII).
- Token/account mapping table (A vs B, roles).
- Timestamps and endpoint list tested.
- Screenshot of the unauthorized resource rendered.

## Common false positives
- IDs that are per-session and not globally guessable.
- Endpoints that return 403 but with a generic body misread as success.
- Public objects (shared/published) legitimately accessible.
- Caching returning another user's page erroneously (cache poisoning, not IDOR).

## Related skills
- [[api-testing]]
- [[auth-bypass]]
- [[xss]]
- [[sqli]]
