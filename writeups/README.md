# Writeups

Raw capture, processed reports, metadata, and external feeds.

| Directory | Purpose |
|-----------|---------|
| `raw/` | unprocessed captures, scan dumps, notes-to-be |
| `processed/` | final writeups (one per finding: `<slug>.md`) |
| `metadata/` | machine-readable finding records (`<finding-id>.json`) |
| `feeds/` | external feeds pulled by `scripts/fetch.sh` |

## Metadata schema (`metadata/<finding-id>.json`)

```json
{
  "finding_id": "f-abc123def456",
  "target": "example.com",
  "vuln_class": "xss",
  "title": "...",
  "severity": "high",
  "confidence": 0.9,
  "verdict": "CONFIRMED",
  "priority": "P2",
  "evidence": "testing/example.com/www/evidence/...",
  "signals": {"reflection": true},
  "reason": "...",
  "reviewer": "..."
}
```

`verdict` ∈ {CONFIRMED, FALSE_POSITIVE, UNVERIFIED}. Only CONFIRMED records are
ingested by `scripts/learn.sh`.