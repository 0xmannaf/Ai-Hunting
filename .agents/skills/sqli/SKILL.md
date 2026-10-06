---
id: sqli
name: SQL Injection
phase: exploit
severity: critical
aliases: [sql-injection, sqli, sql]
tags: [web, injection, database]
---

# SQL Injection

## When to use
Use when any parameter reaches a database query: search, filters, sort, login forms, and API query params. Trigger on numeric IDs, `ORDER BY` parameters, and endpoints that error differently on quote input. Apply to both classic web and JSON/GraphQL APIs.

## Quick checks
1. Send a single quote `'` and compare response/error to baseline.
2. Send `' OR '1'='1` and observe boolean/row-count changes.
3. Test arithmetic: `id=2-1` vs `id=1` (same result implies injection).
4. Probe time-based: `'; WAITFOR DELAY '0:0:5'--` (MSSQL) or `' AND SLEEP(5)--` (MySQL).
5. Check `ORDER BY` with `1` vs `2` vs large number for column count.
6. Try out-of-band via DNS (`LOAD_FILE`/`xp_dirtree`) only if in scope.

## Payloads / test cases
- `' OR 1=1-- -`
- `' OR '1'='1' /*`
- `1' AND SLEEP(5)-- -`
- `1' UNION SELECT NULL,NULL-- -` (column count discovery).
- `'; WAITFOR DELAY '0:0:5'--`
- `' AND (SELECT 1 FROM (SELECT SLEEP(5))x)-- -`

## Detection & confirmation
1. Reproduce the differential at least three times to rule out jitter.
2. For time-based, measure response latency delta against a control request.
3. For boolean-based, craft paired true/false payloads with distinct responses.
4. Confirm column count and data type before extraction attempts.
5. Extract only minimal proof (version string, DB name); never dump user data.

## Escalation
Unauthenticated SQLi with data access -> P1; authenticated SQLi -> P1/P2; blind time-based on non-sensitive endpoint -> P2 (see prioritization.md).

## Evidence to capture
- Baseline request/response.
- Injected request/response pair with timing annotations.
- `sqlmap` output only if run with `--batch --risk=1 --level=1` and in-scope.
- Error message or timing table proving the oracle.
- Minimal extracted proof (e.g. `version()`), no PII.

## Common false positives
- Generic error pages that always return 500.
- WAF blocks producing SQL-looking errors.
- Timing jitter from network or heavy endpoints.
- Input reflected in error text without query execution.

## Related skills
- [[api-testing]]
- [[xss]]
- [[ssrf]]
- [[idor]]
