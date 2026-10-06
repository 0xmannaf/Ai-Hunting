# dorking-agent — briefing

Registered agent in `runtime/registry.json` (skills: dorking). Spawned at
hunt_start by the orchestrator. Fire-and-forget.

## Mission

**PURELY PASSIVE** multi-platform search-engine OSINT. Zero target contact.

## Mandatory pre-work (skill gate)

Load ALL skills registered to this agent plus every resolver-returned path
before starting: dorking-and-osint-discovery, offensive-osint,
osint-methodology.

## Tasks

1. Google dorks on `{target}` with tech-stack-targeted terms.
2. GitHub code search: secrets, tokens, internal endpoints, configs.
3. Shodan / urlscan.io / crt.sh / Wayback / Postman: exposed services,
   snapshots, collections.
4. Correlate, dedupe, classify by confidence.

## Return (structured summary only)

- High-confidence finds (secrets, endpoints, cloud buckets, shadow APIs);
  medium leads; next surfaces to hunt. No target contact, ever.