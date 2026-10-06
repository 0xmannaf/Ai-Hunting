---
title: "IDOR on invoice export endpoint"
source: "sample-corpus (synthetic case study)"
date: 2026-02-02
tags: [idor, authorization, export, invoices]
---

The invoice export endpoint `GET /api/invoices/{invoiceId}/export` returned any
invoice PDF when the numeric id was replaced with a victim's id, without any
ownership check. Response-diff between a valid owner request and the swapped-id
request was identical (same 200 + PDF bytes). Confirmed across two owned
accounts by exporting account A's invoice while authenticated as account B.

- Entry point: `GET /api/invoices/{id}/export`.
- Trust boundary crossed: object ownership → cross-user data exposure.
- Proof method: 2-account cross-context reproduction with raw HTTP pairs.
- FP trap: if ids are UUIDs and not enumerable, the finding downgrades to
  enumeration-only unless ids leak elsewhere (logs, shares, previous
  responses).
- Chain opportunity: leaked invoice ids from shared links → mass export.