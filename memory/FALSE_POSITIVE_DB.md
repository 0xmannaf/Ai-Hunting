# False Positive Database (FP DB)

Every false positive observed, with its trigger pattern and signature hash, so
the hunting loop stops repeating it. Check this file BEFORE testing a class and
BEFORE promoting any observation beyond LEAD.

## Signature-hash format

Compute before every OBSERVATION -> LEAD promotion:

```
SHA256(status:body-length:body-substring)[:8]
```

- `status`  = HTTP status code of the attack response (e.g. 200, 403).
- `body-length` = length of the attack response body.
- `body-substring` = a stable 64-char substring from the middle of the attack
  response body (skip timestamps/tokens/CSRF rot).

An attack response whose signature-hash matches a row below is a **known FP**:
auto-downgrade to INFORMATIONAL, increment the row hit-count, and stop. On a
miss, run the FP filter; if it is an FP, append a new row (pattern, class,
benign explanation, confuser, date, hash) — the DB never shrinks.

Example:

```
$ printf '200:4128:{"status":"ok","error":null}' | sha256sum | cut -c1-8
```

## Format

| Pattern | Class | Benign explanation | Confuser that triggered it | Date | Signature-hash (8) | Hits |
|---------|-------|--------------------|-----------------------------|------|--------------------|------|
| `id=<n>` sequential → "IDOR" | idor | resource ids are public by design (no auth boundary) | same response shape for two ids | 2026-01-01 | — | 0 |

## Active FP patterns

_(none recorded yet)_

## Findings Strength Verification checklist

Run AFTER a finding is CONFIRMED and BEFORE any report. Reportable only if ALL
pass:

1. **Real impact** — the attacker gains specific data, access, privilege, or
   state; state it concretely ("As an attacker, I can ...").
2. **Exploitability** — complete step-by-step chain, demonstrated end-to-end.
3. **Leverageability** — usable from a real attacker position; chains into
   ATO / RCE / cross-tenant / admin / money / data.
4. **Proof quality** — raw reproducible HTTP request/response pair proving a
   server-side effect (screenshots support only).
5. **Cross-context** — shown with 2+ accounts/roles/tenants where applicable.
6. **FP check** — signature-hash computed and checked against this DB; response
   diff (baseline vs attack) shows a real signal, not noise.

ANY "NO" → downgrade to LEAD/OBSERVATION. Never report.

## Rules

- An FP entry is only added after the validator confirms the benign explanation.
- Before reporting a candidate, grep this file for its trigger pattern and its
  signature-hash.
- The learning engine stores FPs too; `scripts/update_steps.py learn` surfaces
  co-occurring signals as `fp_patterns`.