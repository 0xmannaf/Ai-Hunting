---
id: graphql
name: GraphQL Testing
phase: exploit
severity: high
aliases: [graphql, gql, graphql-api]
tags: [api, graphql]
---

# GraphQL Testing

## When to use
The target exposes /graphql, /api/graphql, /v1/graphql, /gql, or a single endpoint taking a query parameter.
Recon signal: GraphQL-style errors, "Cannot query field", Apollo or GraphiQL assets, or __typename in responses.
Mobile and SPA backends commonly hide rich schemas behind one endpoint.

## Quick checks
1. Run introspection: {"query":"{__schema{types{name}}}"}.
2. Compare GET vs POST and Content-Type application/json vs application/graphql.
3. Trigger field suggestions with a typo ("Did you mean ...") when introspection is off.
4. Test query batching and alias-based brute force in one request.
5. Probe depth/cost limits with a deeply nested query.
6. Test per-field authorization by requesting other users' nodes by ID.

## Payloads / test cases
- {"query":"{__schema{queryType{name} types{name fields{name}}}}"}
- {"query":"{ usr { id } }"} to trigger a "Did you mean user" suggestion.
- Batching: [{"query":"mutation{login(user:\"a\",pass:\"1\")}"},{"query":"mutation{login(user:\"a\",pass:\"2\")}"}]
- Alias brute force: {a0:login(pass:"1") a1:login(pass:"2") a2:login(pass:"3")}
- IDOR: {"query":"{ user(id:2){ email role } }"}
- Deep nesting: {"query":"{ user { friends { friends { friends { name } } } } }"}

## Detection & confirmation
1. Complete introspection and save the schema for analysis.
2. Identify sensitive queries and mutations (admin, delete, role, payment).
3. Test unauthorized field or mutation access with a low-privilege token.
4. Confirm IDOR or data exposure with a response diff between IDs.
5. For brute force, show multiple login attempts accepted within a single request.

## Escalation
Introspection plus unauthenticated sensitive mutation -> P1; IDOR or PII exposure -> P2; introspection alone with no sensitive fields -> P4 (see prioritization.md).

## Evidence to capture
- Introspection response or saved schema file.
- Raw GraphQL request and response for each finding.
- Token used and privilege level.
- Screenshot of leaked data or unauthorized mutation result.
- Batch/alias request showing multiple attempts.

## Common false positives
- Introspection disabled but field suggestions still leak type names (report as informational).
- Depth or cost limits block the query with a generic error.
- Schema is public by design for a public API.
- Aliasing or batching rate-limited server-side, so brute force fails.

## Related skills
- [[jwt]]
- [[business-logic]]
- [[csrf]]
