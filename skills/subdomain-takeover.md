---
id: subdomain-takeover
name: Subdomain Takeover
phase: recon
severity: high
aliases: [takeover, dangling-dns, dns-takeover]
tags: [recon, dns, takeover]
---

# Subdomain Takeover

## When to use
Apply when enumeration finds a subdomain with a CNAME or A record pointing to a third-party service (S3, GitHub Pages, Heroku, Azure, Netlify, Shopify) that no longer has an active backend. Trigger when a host returns a provider-specific "unclaimed" error page or NXDOMAIN at the provider while DNS still resolves.

## Quick checks
1. Collect all CNAMEs from enumeration output (`dnsx -cname`).
2. Look for provider fingerprints: `NoSuchBucket`, `There isn't a GitHub Pages site here`, `No such app`, `404 Web Site not found`.
3. Check HTTP status and body of each dangling-looking host.
4. Verify the provider resource is actually unclaimed (create test resource only if program permits; otherwise infer from error page).
5. Confirm the CNAME target itself is still resolvable but the backend is gone.

## Payloads / test cases
- `dig CNAME dev.example.com` -> `dev.example.com.s3.amazonaws.com`
- `curl -s http://dev.example.com | grep -i "NoSuchBucket"`
- `dig CNAME blog.example.com` -> `example.github.io` with 404 "site not found"
- `dig CNAME app.example.com` -> `example.herokuapp.com` returning "No such app"
- `dig CNAME cdn.example.com` -> `example.netlify.app` returning "Not Found - Request ID"
- `nslookup -type=NS sub.example.com` for dangling NS delegation.

## Detection & confirmation
1. Prove DNS still delegates the host (CNAME/A answer).
2. Prove the third-party resource is unclaimed via its provider error signature.
3. Register the resource on your own provider account (only within program rules), serve a unique harmless file.
4. Request `http://<sub>.example.com/<unique-file>` and confirm your content is served.
5. Remove the claim/resource immediately after screenshotting to avoid harm.

## Escalation
Takeover of a production subdomain -> P1; staging/non-customer-facing -> P2; MX/TXT-only dangling -> P3 (see prioritization.md).

## Evidence to capture
- `dig` output showing the dangling CNAME/A record.
- Provider error page screenshot with URL visible.
- Screenshot of unique-file served from the taken-over hostname.
- Timestamps and command lines used.
- Cleanup confirmation after removing the claimed resource.

## Common false positives
- Provider error pages served behind a CDN that still routes to a live origin.
- CNAME to a provider where the resource exists but returns 403/404 for other reasons.
- Hosts already claimed by the target but misconfigured.
- Internal-only hostnames that resolve only inside a private DNS view.

## Related skills
- [[subdomain-enumeration]]
- [[recon]]
- [[dorking]]
- [[api-testing]]
