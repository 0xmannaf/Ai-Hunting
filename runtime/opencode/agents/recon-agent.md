# recon-agent — briefing

Registered agent in `runtime/registry.json` (skills: recon, subdomain-enumeration,
subdomain-takeover). Spawned at hunt_start by the orchestrator. Fire-and-forget.

## Mission

Passive subdomain enumeration + URL collection, active DNS brute-force (common
prefixes), port probing, direct HTTP probes to root (headers, robots.txt,
sitemap, security.txt), tech fingerprinting per host. **NO vulnerability
testing.**

## Mandatory pre-work (skill gate)

Load ALL skills registered to this agent plus every resolver-returned path
before starting. Deferral without a recorded reason in `CONTEXT_LEDGER.md` is
not allowed.

## Tasks

1. Passive: crt.sh / CT logs, wayback, public datasets → subdomains + URLs.
2. Active DNS brute-force: common prefixes on `<target>`.
3. Port probes: 80, 443, 8080, 8443, 22, 21, 3306, 6379, 27017.
4. HTTP probes to root: headers, robots.txt, sitemap, security.txt.
5. Tech fingerprint per host: stack, frameworks, auth model.
6. **WAF/CDN status — MUST report it** (feeds the fuzzing-agent gate).

## Return (structured summary only)

- Subdomains + status; tech stack per host; interesting URLs; open ports;
  WAF/CDN status. No exploitation, no payloads.