#!/usr/bin/env bash
# index.sh — rebuild writeups/index.md from writeups/processed/ (step: index).
# Also refreshes per-target testing/*/index.md.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

"${PYTHON:-python}" scripts/update_steps.py index