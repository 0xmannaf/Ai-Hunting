# Patterns

Recurring technical patterns observed across targets. Updated via learning engine
distill + human review. Each entry: pattern, where it appears, why it works, countercheck.

## How to use

- Before testing a class, check `memory/targets/<vuln>.md` for the checklist.
- If a pattern here matches your current target's stack, prioritize the related skill.

## Patterns

- **xss** (n=2, fp_rate=0%): top signals `reflection, no_output_encoding`.

## Signal co-occurrence notes

- High-FP signals (see `FALSE_POSITIVE_DB.md`) are listed there, not here.
- A signal is a pattern only after it appeared on 2+ distinct targets with
  confirmed outcomes.
