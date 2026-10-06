---
title: "JWT algorithm confusion via public key as HMAC secret"
source: "sample-corpus (synthetic case study)"
date: 2026-03-05
tags: [jwt, authentication, signature-bypass]
---

The API accepted RS256-issued JWTs but the verification library did not pin the
algorithm. A token re-signed with HS256 using the RSA public key (downloaded
from `/jwks`) as the HMAC secret was accepted, allowing arbitrary claims
(`"role":"admin"`). The forgeable token gave access to admin-only routes.

- Entry point: `Authorization: Bearer <jwt>` on `/api/admin/*`.
- Trust boundary crossed: signature trust → claim forgery → privilege
  escalation.
- Proof method: forged HS256 token accepted with raw 200 response; baseline
  RS256 token for comparison.
- FP trap: some libraries validate alg via a header allowlist — verify the
  rejected response body differs, and that the same token is rejected after
  rotation.
- Chain opportunity: forged token → admin API → mass data access.