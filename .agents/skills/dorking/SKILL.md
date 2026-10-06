---
id: dorking
name: Google Dorking & OSINT
phase: recon
severity: info
aliases: [google-dorking, osint, search-dorking, googling]
tags: [recon, osint, search]
---

# Google Dorking & OSINT

## When to use
Use during recon to find exposed files, login portals, error pages, and leaked credentials indexed by search engines. Trigger when the target has a public web presence and scope allows passive collection. Also useful for finding forgotten panels, directory listings, and paste/code leaks.

## Quick checks
1. Search the apex domain: `site:example.com`.
2. Hunt config/secret files: `site:example.com ext:env OR ext:yml OR ext:json`.
3. Find admin panels: `site:example.com inurl:admin OR inurl:login`.
4. Look for directory listings: `site:example.com intitle:"index of"`.
5. Search code leaks: GitHub `org:example`, GitLab, grep.app, Pastebin.
6. Check the Wayback Machine and urlscan.io for historical endpoints.

## Payloads / test cases
- `site:example.com ext:sql OR ext:bak OR ext:log`
- `site:example.com intitle:"index of" "parent directory"`
- `site:example.com inurl:api | inurl:swagger | inurl:graphql`
- `site:example.com "not for public" OR "internal use only"`
- `"example.com" site:pastebin.com OR site:ghostbin.com`
- `site:example.com -www` to surface non-www hosts.

## Detection & confirmation
1. Open the indexed result directly and confirm the live resource still exists.
2. Record the exact URL, HTTP status, and a snippet of exposed content.
3. For credentials found, validate minimally (never log in to third-party accounts) and report via program channel.
4. For files, download a copy into evidence (no mass scraping).
5. Cross-check that the finding is in scope and not a third-party mirror.

## Escalation
Exposed credentials or secrets -> P1/P2 depending on privilege; directory listing with sensitive files -> P2; stale docs/login pages -> P3 (see prioritization.md).

## Evidence to capture
- Screenshot of the search query and results page.
- Direct URL of the exposed resource plus HTTP response headers.
- Saved copy of the exposed file (redact secrets in report body).
- Timestamp and search engine used.
- Notes on whether the resource is still live.

## Common false positives
- Cached/indexed pages that are already removed (404 live).
- Third-party mirrors or scrapers republishing public data.
- Example/sample files intentionally public.
- Old JS bundles with no live endpoints.

## Related skills
- [[recon]]
- [[subdomain-enumeration]]
- [[api-testing]]
- [[auth-bypass]]
