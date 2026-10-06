# Surface Notes 01 — www.dell.com homepage + auth + support

## Stack fingerprint
- Akamai CDN + Bot Manager (`bm_s`, `akavpau_*`, `_abck` cookies) + WAF (blocks payloads with 403 Access Denied + edgesuite ref)
- F5 BIG-IP ASM cookies behind Akamai (`TS01173a82`, `TS01515ac7`, `TS01b893f4` etc.)
- Cloud Foundry (PCF): `X-Vcap-Request-Id`, `diagnostics-url: https://diagnostics.a2.pcf.dell.com/traces/<traceid>` (host NOT publicly resolvable)
- Dellcore CMS (`Dellcore-Version 2.9.x`, `X-Upstream: https://campaign-web-md-PROD`, `unified-masthead-md-PROD`)
- Dynatrace RUM (Server-Timing dtSInfo, x-dt-tracestate), Adobe Target (stt.dell.com mbox), mPulse, OneTrust, Ensighten TMS (nexus.dell.com), VCR collector (collector.vcr.dell.com), Akamai EUM (trial-eum-clientnsv4-s.akamaihd.net)
- Suspicious 3rd-party: `www.mczbf.com/tags/11306/tag.js` (unknown tag network), `d41.co` (D&B), cnnx.link, 6sc.co, taboola, adnxs

## OIDC / Identity (/di/, /dci/, DWA)
- Discovery: `https://www.dell.com/di/.well-known/openid-configuration` (200, public)
  - issuer: https://www.dell.com/di
  - authorization_endpoint: /di/v3/fp/oidc/authorize; token_endpoint: /di/v3/fp/oidc/token; userinfo: /di/v3/fp/oidc/userinfo; jwks: /di/v3/fp/v3/keys/public
  - registration_endpoint: `https://di-portal.di.pcf.dell.com/home` (internal CF host — NOT publicly resolvable)
  - grants: authorization_code, **SessionManaged**, **refresh_token**, **token_exchange**
  - scopes: openid profile email address phone **dellprofile adprofile sfdc groups** offline
  - response_types: code, id_token, code id_token (implicit enabled); response_modes: query, form_post
  - revocation auth: client_secret_basic/post/jwt + **none**
  - service_documentation: `https://confluence.dell.com/display/DCP/...` (internal Confluence — NOT publicly resolvable)
- Flow: `/di/v3/fp/session/authorize?client_id=cf7b2e54-...&redirect_uri=...` → 302 → `/di/idp/dwa/authorize` (login page) → id_token → `/dci/fp/session/authorize` → session
- **redirect_uri validation (DWA authorize):** external (https://evil.example.com, @-trick, suffix-trick, http, evil.dell.com sub) → REJECTED 302 `Error?errorCode=400`. BUT `https://www.dell.com//evil.example.com` and `https://www.dell.com/\evil.example.com` → 200 login page (accepted as path variant). Browser normalizes host stays dell.com → low direct impact; needs owned account to test token-time redirect. OBSERVATION.
- **Scope inflation:** authorize with `openid profile email address phone dellprofile adprofile sfdc groups offline` for client_id 657d850a → login page rendered (NOT rejected). Real claim-level impact needs owned account + token inspection. OBSERVATION → possible LEAD w/ account.

## Header leaks (informational)
- `di_verbos: WebModule | 4.23.8.8 | https://dellidentity-corp dell com/di/api/settings | cf7b2e54-...` (internal IdP settings URL, client_id)
- `resolvedurl: cart-bridge-service-stable.upa.us.dell.com`, `upstreamname: cart-bridge-green`, `upstreamcontextname: context-as-proxy-stable.upa.us.dell.com`, `nginx-rule`, `layer: green`
- `X-Upstream: https://campaign-web-md-PROD`

## Support surface (www.dell.com/support/*)
- `/support/productsmfe/en-us/homedashboard?appname=home&detectpc=true&registereddevices=true&version=5.0`
- `/support/guidedpath/guidedPath/getva?appname=Home&tagOrSerialNumber=&newVA=true...` (service-tag→VA)
- `/support/search/api/supportsearchapi/unathuser/us/en`
- `/support/productsmfe/en-us/api/catalog/autosuggest`
- `/support/mastheadux/accountinfo/authstatus` (204 unauth)
- `/support/intelligent-web/en-us/genesyschat/getsettings`
- `/support/onlineapi/no-result-found/ifd.log.html?methodName=&sessionId=&msg=` → 200 "success", NO reflection; WAF 403 on payloads → log sink only, no XSS
- `/csbapi/en-us/cart/item`
- API probing after payloads → Akamai 403 bucket; WAF gate = respect backoff

## Cart/user APIs
- `getusercontext` (shopapi/masthead/v2): unauth JSON w/ roleName Buyer, customerSetId STUSA11000386, segment CNSR — no sensitive data unauth
- `purchase/api/cart-bridge-context/v3/cart/en-us`: `{"activeQuotes":[],"activeCarts":[],"count":0}` — unauth empty

## Tested-variant ledger (auth surface)
| Surface | Skill | Variant | Result | Reason | Next |
|---|---|---|---|---|---|
| /di/idp/dwa/authorize redirect_uri | oauth | evil/at/suffix/sub/http | blocked (302 errorCode=400) | validation OK | token-time w/ account |
| /di/idp/dwa/authorize redirect_uri | oauth | //path / \backslash | accepted (200 login) | path variants allowed; host stays dell.com | verify post-login redirect target w/ owned account |
| /di/idp/dwa/authorize scope | oauth | +dellprofile+adprofile+sfdc+groups+offline | accepted (200 login) | scope not rejected at authorize | inspect id_token claims w/ account |
| ifd.log.html | xss | script/img/attr payloads | blocked (403) + no reflection | WAF + server-side log sink | none — not XSS |

## Chain board
- Scope-inflation-accepted (OBS) → owned account → id_token claim inspection → data exposure (adprofile/sfdc)? needs account
- redirect_uri path-variant (OBS) → owned account → post-login redirect target → token leak? needs account
- Header internal host leaks → all non-resolvable publicly → informational only