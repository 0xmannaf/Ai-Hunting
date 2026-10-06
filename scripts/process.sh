#!/usr/bin/env bash
# process.sh — convert writeups/raw/ -> structured entries in writeups/processed/
# (step: process). Also parses testing/<root>/<sub>/requests/*.txt -> notes/.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

"${PYTHON:-python}" scripts/update_steps.py process