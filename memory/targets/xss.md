# Cross-Site Scripting (XSS) — per-class checklist

> Companion to `skills/xss.md` and the registry. Filled from confirmed findings
> and FPs; keep it current.

## Checklist

1. Map all input reflections: query, path, headers (Referer, User-Agent, X-Forwarded-*),
   POST bodies, file names, JSON keys echoed in responses.
2. Determine context: HTML body, attribute, JS string, JS context, CSS, URL.
3. Test encoding: does the app HTML-encode, JS-escape, or pass through?
4. Confirm with a benign unique marker first; then a payload that executes.
5. Test storage: does the payload persist and render to other users (stored)?
6. DOM sinks: location, innerHTML, eval, document.write, postMessage handlers.

## Confirmed payloads / observations

_(none yet)_

## False-positive patterns

_(none yet — see memory/FALSE_POSITIVE_DB.md)_

## Evidence requirements

- Request with payload + response showing reflection/execution.
- Screenshot of execution (browser) for stored/reflected with interaction.
- DOM XSS: proof of sink reachable from an attacker-controlled source.