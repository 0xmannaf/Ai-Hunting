---
id: open-redirect
name: Open Redirect
phase: exploit
severity: low
aliases: [open-redirect, url-redirect, redirect]
tags: [web, client-side, phishing]
---

# Open Redirect

## When to use
Requests contain redirect targets: ?next=, ?url=, ?redirect=, ?return=, ?continue=, ?dest=, ?u=, ?r=.
Recon signal: login/logout, SSO callbacks, unsubscribe, share, and "leaving site" interstitial pages.
Client-side JS sinks such as window.location = param or location.href assignment also qualify.

## Quick checks
1. Replace the parameter value with https://evil.tld and inspect the Location header or JS sink.
2. Test protocol-relative //evil.tld and backslash variants /\evil.tld.
3. Test authority confusion: https://target.tld@evil.tld and https://target.tld.evil.tld.
4. Test encoding bypasses: %2f%2f, https:evil.tld, and double-encoded values.
5. Test CRLF injection %0d%0a into the Location header.
6. Confirm whether the redirect fires pre-auth (unauthenticated) or only post-login.

## Payloads / test cases
- ?next=https://evil.tld
- ?next=//evil.tld
- ?next=/\evil.tld
- ?next=https://target.tld@evil.tld
- ?next=https://target.tld.evil.tld
- ?next=%2f%2fevil.tld
- ?next=javascript:alert(document.domain) (client-side sink)
- ?next=https://target.tld%0d%0aSet-Cookie:x=1 (CRLF)

## Detection & confirmation
1. Send the payload and capture the 302/301 Location header pointing off-origin.
2. Follow the redirect in a browser and confirm the final origin is attacker-controlled.
3. For JS sinks, show execution via the console or an alert screenshot.
4. Verify the redirect works without authentication if applicable.
5. Document the exact parameter, encoding, and response status.

## Escalation
Open redirect chained to OAuth code/token theft -> P1; trusted-domain phishing vector -> P3; standalone cosmetic redirect -> P4/low (see prioritization.md).

## Evidence to capture
- Raw request and 302 response with the Location header highlighted.
- Browser screenshot of the attacker landing page.
- Console output or alert for JS-based redirects.
- Parameter name and exact encoding used.
- Note on authentication requirement (pre/post login).

## Common false positives
- Redirect stays on the same domain or only allows relative paths.
- An interstitial "you are leaving" warning page intercepts the redirect.
- Allowlist rejects the payload but the error page echoes the URL.
- Redirect occurs only after authentication, reducing phishing value.

## Related skills
- [[oauth]]
- [[csrf]]
- [[jwt]]
