# Insecure Direct Object Reference (IDOR/BOLA) — per-class checklist

> Companion to `skills/idor.md` and the registry. Filled from confirmed findings
> and FPs; keep it current.

## Checklist

1. Enumerate object routes: /api/users/{id}, /orders/{id}, /files/{uuid}, etc.
2. Create a second account; cross-access objects with the other account's session.
3. Test both GET and state-changing methods (PUT/DELETE) on the same object.
4. Test id formats: sequential, GUID, base64-encoded id, hashed id.
5. Check list endpoints for missing filters (mass assignment of resources).
6. Verify authorization boundary: is the object owner-scoped or any-authenticated?

## Confirmed payloads / observations

_(none yet)_

## False-positive patterns

- Sequential ids returning identical shape for different users is NOT IDOR if the
  resource is public by design — confirm there is an authorization boundary.

## Evidence requirements

- Two requests from different accounts to the same object id (one denied path
  if exists, one successful cross-access), or documented absence of authz.