---
description: Map application behavior and attack surface before testing
agent: build
---

# Autonomous Understand

Target or notes:
$ARGUMENTS

Behavioral mapping pass. No payloads — read and record.

## Steps

1. Load the page and enumerate links, forms, and endpoints
   (`requests/`, `notes/`).
2. Identify auth model: session cookies, JWT, OAuth, API keys; where tokens live.
3. Map input classes:
   - reflected inputs (query, headers, body fields)
   - stored inputs (profile, uploads, comments)
   - server-side fetch (URL params, webhooks, proxies)
   - file access (download, include, template params)
4. Note framework/stack from headers, JS bundles, error pages.
5. Write `testing/<root>/<sub>/notes/understand.md`:
   - endpoint table (method, params, auth required?)
   - input class table -> candidate skills

## Output contract

| Input class | Candidate skills |
|-------------|------------------|
| reflection | xss, ssti, open-redirect |
| object ids | idor |
| server-side fetch | ssrf |
| file params | lfi, file-upload |
| auth flows | auth-bypass, jwt, oauth |