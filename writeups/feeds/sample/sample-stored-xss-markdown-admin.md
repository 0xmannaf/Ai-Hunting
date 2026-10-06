---
title: "Stored XSS through markdown preview rendered in admin context"
source: "sample-corpus (synthetic case study)"
date: 2026-02-20
tags: [xss, stored, markdown, admin-context]
---

A project description field accepts markdown that is rendered server-side into
an HTML preview without output encoding for raw HTML blocks. A payload using an
HTML block (`<img src=x onerror=...>`) executed when an admin viewed the
preview. Because the admin panel rendered the same field unsanitized, the XSS
executed in the admin session — a stored, admin-context XSS chain to account
takeover.

- Entry point: `PATCH /api/projects/{id}` description field + admin preview.
- Trust boundary crossed: user content → admin session.
- Proof method: stored payload, admin-context execution captured in raw
  request/response pair; browser PoC only as support.
- FP trap: many previews sanitize on the client but not the server — always
  re-submit the raw payload via HTTP, never via the UI, to prove server-side
  storage/rendering.
- Chain opportunity: admin XSS → session theft → ATO of admin.