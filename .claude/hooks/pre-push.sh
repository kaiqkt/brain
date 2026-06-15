#!/bin/bash
# Git pre-push hook — runs vault lint + index coverage check before every push.
#
# Lint failure blocks the push.
# Reindex is informational — reports notes missing from or stale in index.md.
# index.md is AI-maintained; update it manually when the check reports drift.
#
# Install:
#   cd brain && ln -sf ../../.claude/hooks/pre-push.sh .git/hooks/pre-push

set -u

VAULT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || {
  echo "[pre-push] not a git repo — skipping vault checks"
  exit 0
}

cd "$VAULT_ROOT"

echo "[vault] lint"
if ! python3 .claude/scripts/lint.py; then
  echo
  echo "[vault] lint failed — push blocked. Fix findings and re-push." >&2
  exit 1
fi

echo
echo "[vault] index coverage"
python3 .claude/scripts/reindex.py

exit 0
