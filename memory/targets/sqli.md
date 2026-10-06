# SQL Injection (SQLi) — per-class checklist

> Companion to `skills/sqli.md` and the registry. Filled from confirmed findings
> and FPs; keep it current.

## Checklist

1. Find parameters hitting DB-backed features: search, filters, sort, ids, login.
2. Test with a benign marker and single-quote probe; watch for error deltas.
3. Classify: boolean-based, error-based, UNION, time-based, blind.
4. Confirm extraction or boolean oracle with two distinct conditions.
5. Note DB type from error signatures or version functions.
6. Check secondary injections: order-by, group-by, JSON query params.

## Confirmed payloads / observations

_(none yet)_

## False-positive patterns

_(none yet — see memory/FALSE_POSITIVE_DB.md)_

## Evidence requirements

- Baseline request/response pair vs injected pair (same endpoint).
- For blind: timing deltas or boolean oracle outputs, two runs.
- For UNION: the extracted data itself (no full dump; a single row suffices).