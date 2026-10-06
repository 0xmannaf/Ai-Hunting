---
id: xss
name: Cross-Site Scripting (XSS)
phase: exploit
severity: high
aliases: [xss, cross-site-scripting, reflected-xss, stored-xss, dom-xss]
tags: [web, browser, client-side, javascript]
---

# Cross-Site Scripting (XSS)

## When to use
Use whenever user-controlled input is reflected or stored and rendered in HTML, attributes, or JavaScript. Trigger on search boxes, profile fields, comments, URL fragments, and error pages. Check both server-rendered and DOM sinks (`innerHTML`, `document.write`, `eval`).

## Quick checks
1. Send a unique marker (`xss<canary>123`) and grep the response for it.
2. Identify context: HTML body, attribute, `<script>`, URL, or CSS.
3. Test angle brackets and quotes: `<b>`, `"`, `'`, backtick.
4. For DOM XSS, inspect `location.hash`/`search` handling in JS sources.
5. Check if input is stored: submit, then reload the page as another user.
6. Review CSP header; note inline vs nonce-based policy.

## Payloads / test cases
- `<script>alert(document.domain)</script>`
- `"><img src=x onerror=alert(document.domain)>`
- `'><svg onload=alert(document.domain)>`
- `javascript:alert(document.domain)` in an href.
- DOM: `#<img src=x onerror=alert(1)>` when written via `innerHTML`.
- Attribute break: `" autofocus onfocus=alert(document.domain) x="`.

## Detection & confirmation
1. Confirm the marker survives unencoded in the exact context.
2. Use `alert(document.domain)` or a unique `console.log` rather than `alert(1)` to prove execution context.
3. For stored XSS, re-fetch the page from a separate session/browser and confirm execution.
4. Capture the full HTTP request that injects and the response that renders.
5. Verify impact (cookie access, CSRF token theft) without exfiltrating real data.

## Escalation
Stored XSS on admin/privileged page -> P1; stored on user-facing page -> P2; reflected behind auth -> P3; self-XSS only -> informational (see prioritization.md).

## Evidence to capture
- Raw inject request and rendering response.
- Screenshot/console output showing `alert(document.domain)`.
- Browser console stack or DOM snippet showing the sink.
- Second-session proof for stored XSS.
- CSP header captured for context.

## Common false positives
- Reflection inside JSON that is never rendered as HTML.
- Output encoded in a context that blocks execution (e.g. `textContent`).
- Self-XSS requiring the victim to paste the payload manually.
- WAF blocking reflected payloads while logging them (no execution).

## Related skills
- [[api-testing]]
- [[sqli]]
- [[auth-bypass]]
- [[idor]]
