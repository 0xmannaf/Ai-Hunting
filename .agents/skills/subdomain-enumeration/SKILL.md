---
id: subdomain-enumeration
name: Subdomain Enumeration
phase: recon
severity: info
aliases: [subdomains, subdomain-enum, dns-enum, dns-recon]
tags: [recon, dns, subdomains]
---

# Subdomain Enumeration

## When to use
Run after initial recon when the apex domain is known and the goal is to expand the attack surface. Trigger when scope says "*.example.com" or when a wildcard TLS certificate reveals many hosts. Essential before testing for takeover, staging exposures, or forgotten admin panels.

## Quick checks
1. Passive sources first: crt.sh, subfinder, amass passive, SecurityTrails.
2. Brute-force with a curated wordlist (SecLists `subdomains-top1million-5000.txt`).
3. DNS resolution with a fast resolver and wildcard filtering (`dnsx`, `massdns`, `shuffledns`).
4. Check for wildcard records: resolve several random labels (`dig random123.<domain>`).
5. HTTP probe live hosts for status, title, and redirect (`httpx -sc -title -td`).
6. Permute discovered names (alterations: dev-, -stg, -api, numbers).

## Payloads / test cases
- `subfinder -d example.com -all -o subs.txt`
- `amass enum -passive -d example.com -o amass.txt`
- `curl -s "https://crt.sh/?q=%25.example.com&output=json" | jq -r '.[].name_value' | sort -u`
- `shuffledns -d example.com -w wordlist.txt -r resolvers.txt -o brute.txt`
- `dnsx -l subs.txt -a -resp -o resolved.txt`
- `httpx -l resolved.txt -ports 80,443,8080,8443 -sc -title -tech-detect -o live.txt`

## Detection & confirmation
1. Merge all sources, deduplicate, and remove wildcard-resolved noise.
2. Confirm each candidate resolves to a real A/AAAA/CNAME record.
3. Probe over HTTP/HTTPS and record status code, title, server, and redirect chain.
4. Classify hosts: prod, staging, dev, admin, api, legacy, third-party.
5. Verify scope membership before any active testing; drop out-of-scope hosts.

## Escalation
Informational by itself; live staging/admin hosts found here feed takeover (P2-P1) and auth-bypass/injection testing (see prioritization.md).

## Evidence to capture
- Raw output of each enumeration tool with command line used.
- Deduplicated resolved host list.
- `httpx` output table (status, title, tech).
- Wildcard detection notes (test label + response).
- Screenshots of interesting hosts (admin, staging, login).

## Common false positives
- Wildcard DNS answers for non-existent labels.
- CDN anycast records that resolve but serve a generic error page.
- Parked/for-sale domains pointing at the target's name.
- Stale CT entries for decommissioned hosts.

## Related skills
- [[recon]]
- [[subdomain-takeover]]
- [[dorking]]
- [[api-testing]]
