# Authentication Bypass — per-class checklist

> Companion to `skills/auth-bypass.md` and the registry. Filled from confirmed
> findings and FPs; keep it current.

## Checklist

1. Map the auth flow: login, session issuance, password reset, MFA, session fix.
2. Test reset flows: host header poisoning, token predictability, token in URL.
3. Test session: cookie flags, session fixation, concurrent session handling.
4. Test rate limiting / credential stuffing defenses (non-destructively).
5. Test MFA: bypass via API path, missing enforcement on sensitive actions.
6. Test default/weak credentials only with explicit approval.

## Confirmed payloads / observations

_(none yet)_

## False-positive patterns

_(none yet — see memory/FALSE_POSITIVE_DB.md)_

## Evidence requirements

- Full auth flow captured: request chain proving the bypass and the protected
  action it enables.