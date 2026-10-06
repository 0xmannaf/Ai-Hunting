---
title: "SSRF via PDF generator URL parameter"
source: "sample-corpus (synthetic case study)"
date: 2026-01-15
tags: [ssrf, server-side, pdf, url-input]
---

A PDF export feature accepts a `logoUrl` parameter and fetches it server-side.
Submitting `logoUrl=http://127.0.0.1:8080/admin` returned the internal admin
page inside the rendered PDF, proving the fetch is server-side and not
restricted to public hosts. Redirect chains to internal addresses were also
followed, and the cloud metadata endpoint was reachable when the SSRF was
chained through an open redirect on the same origin.

- Entry point: `POST /api/export/pdf` with `logoUrl`.
- Trust boundary crossed: public-URL allowlist → internal network + metadata.
- Proof method: render output embedded the internal response body.
- FP trap: some PDF fetchers render placeholder text for failed fetches — a
  missing image is NOT proof; the internal page content must appear.
- Chain opportunity: metadata endpoint → cloud credentials; internal admin →
  privileged actions.