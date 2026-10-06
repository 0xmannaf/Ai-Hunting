---
description: OSINT/dorking pass over search engines
agent: build
---

# Autonomous Dorking

Target or notes:
$ARGUMENTS

Search-engine OSINT for exposed assets, docs, and leaked info. Purely passive.

## Queries to try (adjust per target)

- `site:<root>` and `site:*.root` (subdomains)
- `site:<root> filetype:pdf|docx|xlsx|env|json`
- `site:<root> inurl:admin|api|dev|staging|swagger`
- `"<root>" "api_key"|"password"|"internal"` (leaks — note only, never exfiltrate)
- `site:github.com "<root>"` (repo/secret leaks)
- `site:pastebin.com "<root>"`

## Output

- `testing/<root>/notes/dorking.md`: findings, each with URL + snippet reason.
- Leaks: log the location and type; do NOT download or store credential content
  in evidence. Report the existence.

## Rules

- Respect search-engine rate limits; no scraping tools without approval.
- Anything found is still subject to the scope gate before testing.