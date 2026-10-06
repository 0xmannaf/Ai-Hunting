# Wordlists

Scoped payload wordlists. Small, targeted, deduplicated. Never download
multi-GB generic lists here — keep them outside the repo and reference them.

## Categories

- `ids.txt` — object-id patterns for IDOR enumeration (sequential ranges, GUIDs)
- `paths.txt` — common admin/dev/debug paths (per-target curated)
- `fuzz.txt` — parameter/header names for behavior probing
- `traversal.txt` — path traversal payloads (see skills/lfi.md)
- `subdomains.txt` — small top-1000 subdomain wordlist (curated per target)

## Rules

- Lists are per-target scoped when possible (`testing/<root>/<sub>/wordlists/`).
- Payload lists must be non-destructive by default.
- Before adding a payload, check `memory/FALSE_POSITIVE_DB.md` for known noise.