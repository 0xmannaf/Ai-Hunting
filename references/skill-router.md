# Skill Router — Trigger Mapping & Discovery

- **Version:** 1.0
- **Last Updated:** 2026-10-01
- **Purpose:** route hunters to the correct skills based on the discovered
  attack surface.

> `runtime/registry.json` + `scripts/skill_registry.py` are **AUTHORITATIVE**;
> this table is a human-readable compatibility cross-check. Always use the
> resolver before testing so all matching skills load automatically:
> `python scripts/skill_registry.py resolve --scenario "<surface>" --mode test
> --paths-only`. Skill names match `runtime/registry.json` exactly.

## How to use

1. Find the surface in the left column.
2. Check the trigger surface description.
3. Load ALL skills in "Skills to Load".
4. Skip skills in "When NOT to Load" if the conditions apply.
5. Reference links for exact file paths: `skills/<skill>.md` (source) +
   `.agents/skills/<skill>/SKILL.md` (active runtime copy).

## Master registry table by attack surface

### FOUNDATION (always first)

| Attack Surface | Trigger Surface | Skills to Load | When NOT to Load | Key Patterns |
|----------------|-----------------|----------------|------------------|--------------|
| Every session | every hunt/scan/triage/report | master-bugbounty-rules, learning-engine-integration | NEVER — both load first, in order | boot layer, outside registry budget |

### Authentication & Identity

| Attack Surface | Trigger Surface | Skills to Load | When NOT to Load | Key Patterns |
|----------------|-----------------|----------------|------------------|--------------|
| login form | username/password form, API login, cookie issuance | auth-bypass, csrf | csrf when token-less pure API | credential stuffing is never allowed |
| magic link / passwordless | one-time URL login, token in email | auth-bypass, jwt | — | OTP from owned inbox only |
| registration | signup forms, invite codes | auth-bypass, csrf, business-logic | — | owned account only |
| OAuth/OIDC | SSO buttons, redirect flows, /authorize | oauth, jwt, open-redirect | open-redirect only if chaining | state/redirect_uri tampering |
| SAML | SAML endpoints, XML assertions | oauth (nearest), jwt | — | no dedicated SAML skill in registry |
| 2FA/TOTP | TOTP setup, MFA challenge | auth-bypass | — | brute force never allowed |
| SMS/email OTP | OTP verify endpoints | auth-bypass | — | owned inbox only |
| backup codes | recovery code flows | auth-bypass | — | never generate real codes at scale |
| WebAuthn/FIDO2 | authenticator registration | auth-bypass | — | — |
| reset link / reset code | forgot-password, reset endpoints | auth-bypass | — | owned account only; never third-party |
| security questions | answer-based recovery | auth-bypass | — | — |
| verification via old password | re-auth flows | auth-bypass | — | — |

### Authorization & Access Control

| Attack Surface | Trigger Surface | Skills to Load | When NOT to Load | Key Patterns |
|----------------|-----------------|----------------|------------------|--------------|
| user/object IDs | numeric/UUID ids in paths, bodies, headers | idor | — | cross-account swap with owned accounts |
| tenant/org ID | org/tenant params, subdomain-based tenancy | idor, auth-bypass | — | cross-tenant focus |
| resource paths | /api/../files, exports, attachments | idor, lfi | lfi only if file serving | — |
| filter/query params | list/filter/search endpoints | idor, business-logic | — | mass-assignment candidates |
| RBAC roles | role params, admin flags | auth-bypass, idor | — | vertical priv-esc |
| admin/support actions | admin panels, support tooling | auth-bypass, idor | — | hidden admin routes |
| feature gates | paid/enterprise features | business-logic | — | plan/quota abuse |

### API & GraphQL

| Attack Surface | Trigger Surface | Skills to Load | When NOT to Load | Key Patterns |
|----------------|-----------------|----------------|------------------|--------------|
| REST endpoints | JSON APIs, swagger/openapi | api-testing, idor | idor when no object refs | method/path differentials |
| JSON bodies | write endpoints, nested objects | api-testing, business-logic | — | mass assignment |
| GraphQL | /graphql, introspection, mutations | graphql, idor, auth-bypass | — | introspection + authz gaps |
| hidden methods | OPTIONS, PATCH, DELETE, overrides | api-testing | — | method override abuse |
| webhooks | callback endpoints, delivery retries | ssrf (nearest), business-logic | — | no dedicated webhook skill in registry |

### Client-Side & JS

| Attack Surface | Trigger Surface | Skills to Load | When NOT to Load | Key Patterns |
|----------------|-----------------|----------------|------------------|--------------|
| JS bundles | scripts, bundled apps | api-testing (nearest) | — | js-agent owns collection; deep-analyze immediately |
| source maps | .map files | api-testing (nearest) | — | secrets/hidden routes |
| client routes | SPA routing, feature flags | api-testing (nearest) | — | undocumented endpoints |
| forms / reflected content | search, error echoes | xss, csrf | csrf when no state change | reflection ≠ finding |
| markdown / rich text | previews, editors, admin render | xss | — | server-side storage proof required |
| postMessage | cross-origin messaging | xss | — | origin checks |

### Injection & Parsing

| Attack Surface | Trigger Surface | Skills to Load | When NOT to Load | Key Patterns |
|----------------|-----------------|----------------|------------------|--------------|
| SQL | query params, login, search | sqli | — | low-impact probes only |
| XSS sinks | innerHTML, eval, template refs | xss | — | server-side effect required |
| SSTI | templates, mail/PDF rendering, 404 pages | ssti | — | per-engine payloads |
| SSRF / URL fetchers | URL params, imports, PDF/screenshot | ssrf | — | OOB canary first; Collaborator discipline |
| XXE / XML | XML bodies, uploads, SOAP | ssrf (nearest) | — | no dedicated XXE skill in registry |
| file uploads | upload/import endpoints | file-upload, lfi | lfi when no file read-back | webshell never; PoC only on request |
| path traversal | download/serve params | lfi | — | encoding families |
| command injection | shell-consuming params | sqli (nearest, partial) | — | no dedicated skill in registry; resolver first |

### Infrastructure & Perimeter

| Attack Surface | Trigger Surface | Skills to Load | When NOT to Load | Key Patterns |
|----------------|-----------------|----------------|------------------|--------------|
| CORS | cross-origin responses | idor (nearest) | — | browser PoC required for claim |
| cache | CDN, cache headers | open-redirect (nearest) | — | cache poisoning chains |
| host headers | Host/Forwarded manipulation | open-redirect (nearest) | — | password-reset poisoning |
| CDN/WAF | 403/429 patterns | recon (nearest) | — | bypass ladder before concluding |
| subdomains | DNS, takeover indicators | subdomain-enumeration, subdomain-takeover | — | dangling CNAMEs |
| appliances | VPN/vCenter/SharePoint | recon (nearest) | — | fingerprint → known CVEs (informational) |
| NTLM | auth headers | auth-bypass (nearest) | — | relay ≠ in-scope without approval |

### Stateful & Realtime

| Attack Surface | Trigger Surface | Skills to Load | When NOT to Load | Key Patterns |
|----------------|-----------------|----------------|------------------|--------------|
| WebSockets | ws:// channels, live updates | race-condition (nearest) | — | no dedicated websocket skill in registry |
| race conditions | one-time actions, coupons, approvals | race-condition, business-logic | — | safe racing only |
| one-time actions | token single-use, replay | race-condition, business-logic | — | — |
| payments | checkout, credits, subscriptions | business-logic | — | never alter real balances |

### Cloud/Mobile/AI/Web3

| Attack Surface | Trigger Surface | Skills to Load | When NOT to Load | Key Patterns |
|----------------|-----------------|----------------|------------------|--------------|
| buckets | S3/GCS URLs, signed links | api-testing (nearest) | — | no dedicated skill in registry |
| IAM | cloud creds in JS/configs | api-testing (nearest) | — | metadata only on explicit approval |
| LLM/AI | chat endpoints, prompt flows | business-logic (nearest) | — | no dedicated skill in registry |
| APK/mobile | app bundles | api-testing (nearest) | — | — |
| smart contracts | Web3 surfaces | none in registry | — | out of current registry budget |

### Workflow & Chain

| Attack Surface | Trigger Surface | Skills to Load | When NOT to Load | Key Patterns |
|----------------|-----------------|----------------|------------------|--------------|
| business logic | billing, trials, approvals, invites | business-logic, race-condition | race-condition when no concurrency | state-transition abuse |
| exploit chains | any two+ linked signals | all matching skills for the chain | — | chain board required |

### Validation & Reporting

| Attack Surface | Trigger Surface | Skills to Load | When NOT to Load | Key Patterns |
|----------------|-----------------|----------------|------------------|--------------|
| response analysis | any test result | none in registry | — | response-diff: `references/VERIFICATION_CHECKLIST.md` |
| FP filtering | any lead | none in registry | — | `memory/FALSE_POSITIVE_DB.md` + AGENTS.md FP gate |
| severity | any confirmed | none in registry | — | `prioritization.md` P1-P4 |
| summary/report | session end / user request | none in registry | — | `.opencode/commands/report.md`; report only when asked |

> Rule: for any surface not listed, run the resolver — fuzzy matching covers
> the long tail. No payload before the skill gate passes.