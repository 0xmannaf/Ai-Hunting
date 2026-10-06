---
id: race-condition
name: Race Conditions / TOCTOU
phase: exploit
severity: high
aliases: [race-condition, toctou, concurrency, race]
tags: [web, api, concurrency]
---

# Race Conditions / TOCTOU

## When to use
Endpoints enforce single-use or limited operations: coupon redeem, gift card, withdrawal, transfer, vote, invite accept.
Recon signal: rate-limited actions (OTP, password reset), check-then-act sequences, or balance and credit updates.
Any flow where two requests can interleave between a read and a write is a candidate.

## Quick checks
1. List single-use or quota-limited actions and their tokens or identifiers.
2. Send 20-50 parallel requests with the same coupon/token/OTP.
3. Test rate limits by firing many attempts inside one connection window.
4. Use HTTP/2 single-packet attack (Burp "Send group in parallel" or h2.race) for true simultaneity.
5. Probe TOCTOU on unique constraints: duplicate username or email registration.
6. Check withdrawal/transfer with two concurrent sessions and a tight balance.

## Payloads / test cases
- Parallel POST /redeem with the same coupon code (20-50 threads).
- Same password-reset or OTP token submitted concurrently many times.
- Two concurrent POST /transfer from the same balance to overdraw.
- Parallel POST /register with the same email to bypass uniqueness.
- Race a "verify email" token against a "change email" request.
- Last-byte sync or single-packet: hold the final byte, then release all requests together.

## Detection & confirmation
1. Establish baseline: sequentially, the second request fails with "already used".
2. Run the parallel batch and count successes (for example, coupon applied 5 times).
3. Verify server-side state change: balance, credits, or inventory before and after.
4. For OTP/reset, show multiple accepted attempts inside the validity window.
5. Capture response timestamps showing the requests overlapped.

## Escalation
Double-spend, duplicate withdrawal, or balance overdraw -> P1; OTP/reset limit bypass -> P1/P2; duplicate non-financial action -> P3 (see prioritization.md).

## Evidence to capture
- Raw parallel requests (HAR or Turbo Intruder log) with timestamps.
- Responses showing multiple successes from a single-use token.
- Before/after balance, credits, or order state screenshots.
- Baseline sequential failure for contrast.
- Tool configuration (thread count, HTTP/2, single-packet).

## Common false positives
- Database row locks serialize writes so only the first request succeeds.
- Client-side dedupe hides duplicates while the server correctly rejects them.
- Network retries create duplicate requests that are idempotent by design.
- Responses served from cache, masking the real server behavior.

## Related skills
- [[business-logic]]
- [[csrf]]
- [[jwt]]
