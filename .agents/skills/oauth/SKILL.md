---
id: oauth
name: OAuth / OIDC Attacks
phase: exploit
severity: high
aliases: [oauth, oauth2, oidc, sso, openid-connect]
tags: [auth, sso, oauth]
---

# OAuth / OIDC Attacks

## When to use
The target exposes "Login with ..." social SSO, /oauth/authorize, /oauth/token, /callback, or OIDC discovery.
Recon signal: client_id, redirect_uri, scope, state, code, or id_token parameters in URLs and requests.
Account linking, invite flows, and mobile deep links that complete OAuth are prime targets.

## Quick checks
1. Fetch /.well-known/openid-configuration to map endpoints and supported flows.
2. Tamper redirect_uri with external domains, path suffixes, and userinfo tricks.
3. Remove or replay the state parameter to test login CSRF and code swapping.
4. Request elevated scopes (admin, write) and inspect the issued token.
5. Check PKCE: strip code_challenge or send plain instead of S256.
6. Look for code or token leakage via Referer, fragment, and logs.

## Payloads / test cases
- redirect_uri=https://evil.tld
- redirect_uri=https://legit.tld.evil.tld
- redirect_uri=https://legit.tld%2f@evil.tld
- redirect_uri=https://legit.tld/../../evil (and //evil.tld variants)
- Missing state: complete the flow without state and observe acceptance.
- Code replay: exchange the same authorization code twice.
- response_type=token or id_token when code is expected (flow confusion).
- scope=openid profile email admin (scope inflation).

## Detection & confirmation
1. Intercept /oauth/authorize, change redirect_uri, and read the 302 Location header.
2. Host a listener on the attacker origin and confirm the code or token arrives there.
3. For missing state, prove login CSRF: the victim's browser links the attacker's identity.
4. Exchange a stolen code at /oauth/token and show access to the victim's resources.
5. Compare responses for tampered scope versus baseline to confirm granted privileges.

## Escalation
Redirect_uri or code theft leading to full account takeover -> P1; login CSRF or account-linking abuse -> P2; scope inflation without data access -> P3 (see prioritization.md).

## Evidence to capture
- Raw /authorize request and 302 response with the attacker Location.
- Callback server log showing the code or token received.
- Raw /token exchange request and response.
- Screenshot of the authenticated victim session or linked account.
- state, nonce, and PKCE values used and their validation behavior.

## Common false positives
- Exact-match redirect_uri validation rejects the payload but a generic error page resembles a redirect.
- The identity provider is third-party and out of scope for the program.
- Code appears in the URL but PKCE and state are enforced, preventing replay.
- Wildcard subdomain redirects explicitly allowed by design.

## Related skills
- [[jwt]]
- [[csrf]]
- [[open-redirect]]
