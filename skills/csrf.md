---
id: csrf
name: Cross-Site Request Forgery
phase: exploit
severity: medium
aliases: [csrf, xsrf, cross-site-request-forgery]
tags: [web, client-side, session]
---

# Cross-Site Request Forgery

## When to use
State-changing endpoints (email/password change, transfer, delete, admin actions) rely on cookie sessions.
Recon signal: session cookies without SameSite, no CSRF token in forms or XHR, or tokens not tied to the session.
Any action reachable by a simple HTML form without custom headers is a candidate.

## Quick checks
1. Inspect Set-Cookie for SameSite, Secure, and HttpOnly attributes.
2. Search forms and JS for csrf, _token, or X-CSRF-Token parameters and headers.
3. Replay a state-changing request in Burp with the token removed and with Origin/Referer stripped.
4. Test token binding: reuse a token from another session or after logout.
5. Test method override (_method=POST/PUT) and text/plain form tricks against JSON endpoints.
6. Check GET-based state changes (confirm=1, action=delete) that need no form.

## Payloads / test cases
- Auto-submit form: <form action="https://target.tld/email/change" method="POST"><input name="email" value="attacker@evil.tld"></form><script>document.forms[0].submit()</script>
- Image GET: <img src="https://target.tld/account/delete?confirm=1">
- JSON via form: <form enctype="text/plain" action="https://target.tld/api/update" method="POST"><input name='{"role":"admin","x":"' value='"}'> (text/plain avoids preflight)
- Strip Origin and Referer headers entirely and resend the request.
- Swap Content-Type from application/json to application/x-www-form-urlencoded.

## Detection & confirmation
1. Host the PoC HTML on an attacker origin and open it while logged in as the victim.
2. Verify the server state changed (profile email, role, balance) after the victim visits.
3. Repeat in Burp with the CSRF token removed; show the server still accepts the request.
4. Test whether a token from a different session is accepted (broken binding).
5. Capture both the forged request and the resulting state change as proof.

## Escalation
CSRF on password/email change or funds transfer -> P1 (account takeover); CSRF on privilege change -> P1/P2; low-impact state change with SameSite bypass -> P3 (see prioritization.md).

## Evidence to capture
- PoC HTML file and the attacker hosting URL or data URI.
- Raw forged request and server response.
- Before/after account state screenshots.
- Set-Cookie header showing SameSite attributes.
- Token presence or absence in the original request.

## Common false positives
- SameSite=Lax blocks cross-site POST in the browser even though curl succeeds (test in a real browser).
- Endpoint is idempotent or performs no state change.
- CORS preflight blocks the JSON fetch, but a text/plain form still works (re-test both).
- Token is present but reflected only in the page; the server validates a separate header.

## Related skills
- [[oauth]]
- [[open-redirect]]
- [[business-logic]]
