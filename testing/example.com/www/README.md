# Example Target — www.example.com

Placeholder target tree demonstrating the evidence layout. Replace with real
authorized targets; delete this example before real use.

## Layout

| Directory | Contents |
|-----------|----------|
| `notes/` | observations, stack, hypotheses |
| `requests/` | raw requests (one file per interaction) |
| `responses/` | raw responses |
| `screenshots/` | browser evidence |
| `scripts/` | target-specific scripts |
| `scans/` | scanner output |
| `wordlists/` | scoped wordlists |
| `urls/` | discovered endpoints (`urls.txt`) |
| `subdomains/` | discovered hosts (`subdomains.txt`) |
| `evidence/` | verified finding evidence bundles |
| `reports/` | target-scoped reports |

## Convention

- One file per request/response; name = `<timestamp>_<method>_<slug>.txt`.
- Evidence for a finding = its own folder under `evidence/<finding-id>/`.
- Never store credentials or session tokens anywhere in this tree.