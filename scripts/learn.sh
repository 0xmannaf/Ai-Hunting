#!/usr/bin/env bash
# learn.sh — ingest CONFIRMED metadata -> learning engine -> distill -> memory
# files + regenerate agent-briefing.md (step: learn).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

"${PYTHON:-python}" scripts/update_steps.py learn