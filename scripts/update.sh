#!/usr/bin/env bash
# update.sh — full state regeneration: fetch -> process -> index -> learn.
# Each step is idempotent and safe to re-run.
# Offline/sample mode: FETCH_SAMPLE=1 bash scripts/update.sh
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PYTHON="${PYTHON:-python}"
ARGS=(all)
if [ "${FETCH_SAMPLE:-0}" = "1" ]; then
  ARGS+=(--offline)
fi
"$PYTHON" scripts/update_steps.py "${ARGS[@]}"