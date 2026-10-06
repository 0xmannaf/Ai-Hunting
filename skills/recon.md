---
id: recon
name: Reconnaissance
phase: recon
severity: info
aliases: [recon, reconnaissance, enum, enumeration, asset-discovery]
tags: [recon, osint, assets]
---

# Reconnaissance

## When to use
Use at the start of every engagement once the root domain or organization is in scope. Triggers when scope lists only a primary domain, app name, or IP range and the full asset surface is unknown. Also re-run when a new acquisition, product, or region appears in bug-bounty program updates.

## Quick checks
1. Resolve the root domain and note A/AAAA, MX, NS, and TXT records (`dig +short`, `nslookup`).
2. Fetch `robots.txt`, `sitemap.xml`, and `security.txt` for paths, hosts, and contact metadata.
3. Check certificate transparency logs (crt.sh, Censys) for hostnames on the apex certificate.
4. Query ASN and netblock ownership (whois, BGP.he.net) to bound IP space.
5. Look for public code/CI leaks: GitHub org, GitLab, Pastebin, Postman public workspaces.
6. Fingerprint the edge: CDN, WAF, server headers (`curl -I`), favicon hash (Shodan `http.favicon.hash`).

## Payloads / test cases
- `dig any <domain>`, `dig axfr @ns1.<domain> <domain>` (zone transfer, non-destructive read).
- `curl -s https://crt.sh/?q=%25.<domain>&output=json` to enumerate CT entries.
- `amass enum -passive -d <domain>` and `subfinder -d <domain> -all` for passive host discovery.
- `nmap -sV -Pn --top-ports 1000 <ip>` for a light service fingerprint.
- `curl -I https://<host>` to capture server, CDN, and framework headers.
- Shodan/Censys queries: `ssl:"<domain>"`, `org:"<Org Name>"`, `http.title:"<app>"`.

## Detection & confirmation
1. Cross-reference at least two independent sources (CT log + DNS resolution) before treating a host as live.
2. Confirm liveness with an HTTP response, not just a DNS record; dangling records are a separate skill.
3. Record status codes, titles, and server headers per host in a table.
4. Tag each asset with environment (prod/staging/dev) and tech stack.
5. Feed confirmed hosts into subdomain-enumeration and port/service follow-up skills.

## Escalation
Informational on its own; findings that expose auth bypass, takeover, or injection routes escalate via the specific skill (see prioritization.md).

## Evidence to capture
- Raw DNS output (`dig any`, `dig axfr`) per domain.
- `crt.sh` JSON export and subfinder/amass output files.
- `curl -I` headers for each live host.
- Screenshot of Shodan/Censys result pages used.
- Scope notes: in-scope vs out-of-scope asset table.

## Common false positives
- Wildcard DNS (`*.domain`) resolving every random label to a parked edge.
- CT entries for hosts that never served production traffic or are expired.
- Shared CDN IPs making unrelated sites appear owned by the target.
- MX/TXT records for third-party mail providers misread as in-scope hosts.

## Related skills
- [[subdomain-enumeration]]
- [[dorking]]
- [[subdomain-takeover]]
- [[api-testing]]
