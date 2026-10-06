#!/usr/bin/env bash
# fetch.sh — pull external write-ups into writeups/raw/ (step: fetch).
# Online: FETCH_FEEDS="url1 url2" downloads each into writeups/raw/ (idempotent).
# Offline/sample: FETCH_SAMPLE=1 seeds the local sample corpus, never network.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PYTHON="${PYTHON:-python}"
ARGS=(fetch)
if [ "${FETCH_SAMPLE:-0}" = "1" ]; then
  ARGS+=(--offline)
fi
"$PYTHON" scripts/update_steps.py "${ARGS[@]}"