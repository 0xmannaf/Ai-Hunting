# Recon Pass 01 — dell.com

- Session bootstrap: `logs/sessions/20261001T141158Z.json` (scope locked 2026-10-01, master-authorized `/hunt dell.com`)
- Started: 2026-10-01T14:11Z

## Edge / WAF fingerprint (www.dell.com, GET /)

- Akamai CDN + **Akamai Bot Manager** (`bm_s`, `akavpau_maintenance_vp` cookies, `akavpau_maintenance_vp` = maintenance vp token). WAF gate active.
- `X-Akamai-Transformed`, `Akamai-Cache-Status: Hit from child`; HSTS `max-age=86400; preload`; `X-Content-Type-Options: nosniff`; Referrer-Policy strict-origin-when-cross-origin.
- Backend: `X-Upstream: https://campaign-web-md-PROD` (leaks internal upstream name); `Dellcore-Version: 2.9.11-beta.3+b7b365cd...`; `X-Vcap-Request-Id` (Cloud Foundry); Dynatrace (Server-Timing dtSInfo, x-dt-tracestate).
- `Set-Cookie akGD` geolocation cookie (country=EG region); domain `.dell.com`.
- Link headers: /cdn/assets/shop/styles/*.css, /cdn/assets/tnt/adobebundle/shop/bundle_toggle.min.js (Adobe Target/TNT), /dds/assets/fonts (DDS = Dell Design System).

## DNS

- A: 143.166.30.172, 143.166.136.12 (Dell ASN)
- NS: ns{1-4}{ak,ns}.dell.com (Akamai + Dell NS)
- MX: Proofpoint (pphosted.com) — SPF include pphosted
- TXT: verification records for atlassian, cisco, fastly, mongodb, openai, anthropic, adobe-idp (Adobe Identity!), salesforce (00D0b...), quickbase, smartsheet, dynatrace, onetrust, google, apple, work-accounts (Okta Work Account? "work-accounts-domain-verification" = Okta), paloaltonetworks, miro, liveramp, flexera, cloudhealth, e2ma, autodesk, qqmail
- CT-based host discovery: pending (crt.sh)

## robots.txt / security.txt signals

- `/csbapi/*` + `/csbapi/` disallowed — API surface
- `/di/idp/dwa/`, `/dci/idp/dwa/` — IdP endpoints (Dell Identity + Dell Cloud Identity?), DWA = lightweight login?
- `/buyer/` — buyer portal
- `*/api/` globally disallowed
- `/quote/` — quote workflow
- `/support/*` — support portal, `/support/kbdoc/*`
- security.txt: Bugcrowd programs — applications https://bugcrowd.com/dell-com, products https://bugcrowd.com/dell-product; PSIRT key; VRP policy page

## Notes

- No Collaborator domain provided → NO OOB/blind tests this session.
- No owned Dell accounts → auth flows = read-only understanding only.
- Akamai Bot Manager will likely challenge aggressive fuzzing; use browser session (real UA + JS) for page-level work; keep request rates low.