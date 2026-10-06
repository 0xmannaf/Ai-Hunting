---
id: business-logic
name: Business Logic Flaws
phase: exploit
severity: high
aliases: [business-logic, logic-bug, workflow-abuse, logic-flaw]
tags: [web, api, logic]
---

# Business Logic Flaws

## When to use
Applications implement multi-step workflows: checkout, payment, refund, approval, subscription, referral, KYC.
Recon signal: client-supplied prices, quantities, roles, or state flags; steps that can be reordered or skipped.
Anything where the server trusts a value the client controls is worth mapping.

## Quick checks
1. Map the intended workflow and list every state transition and parameter.
2. Tamper with price, quantity (negative, zero, huge), and currency fields.
3. Call a later step directly, skipping required earlier steps.
4. Replay the final confirmation step or reorder requests.
5. Tamper with role or privilege fields (role=admin, isAdmin=true, plan=enterprise).
6. Test coupon stacking, expired coupons, and refund-after-use.

## Payloads / test cases
- quantity=-1 (credit instead of charge)
- price=0.01 or price=0 in the cart/order request
- currency=USD -> currency=JPY or a weaker currency at checkout
- Skip payment: POST /order/complete without calling /payment/confirm
- Apply the same coupon twice or reuse an expired code
- role=admin or user_id=<other user> in a profile update
- amount=-100 on transfer/withdraw
- Trial reset by re-registering with a plus-aliased email

## Detection & confirmation
1. Reproduce the tampered flow end-to-end and verify the resulting state (order paid, balance changed).
2. Show the server accepted an out-of-order or undervalued request that the UI would prevent.
3. Quantify impact: goods or services obtained free/cheap, or privilege gained.
4. Compare normal-flow responses with tampered-flow responses to isolate the flaw.
5. Document each step request and response in the chain.

## Escalation
Free purchase, unauthorized withdrawal, or privilege escalation -> P1; discount abuse or trial reset with monetary value -> P2/P3; cosmetic logic inconsistency -> P4 (see prioritization.md).

## Evidence to capture
- Full request chain from step 1 to the final step.
- Tampered parameter values and server responses.
- Resulting order, invoice, or balance screenshot.
- Role/privilege change proof (before/after).
- Note on which client-side check was bypassed.

## Common false positives
- Client-side validation blocks the UI but the server recomputes price or role safely.
- Test/staging discount codes intended for the environment.
- Refunds or payouts gated by manual review, so no real impact.
- UI hides a field but the API validates it against server state.

## Related skills
- [[race-condition]]
- [[csrf]]
- [[graphql]]
