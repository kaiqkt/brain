#!/bin/bash
# Git pre-push hook — runs vault lint + reindex before every push.
#
# Lint failure blocks the push. Reindex regenerates index.md; if it changed,
# the push proceeds with a warning (commit the update next time).
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
echo "[vault] reindex"
python3 .claude/scripts/reindex.py

if ! git diff --quiet -- index.md; then
  echo
  echo "[vault] index.md regenerated — push proceeds, but commit the update:" >&2
  echo "        git add index.md && git commit -m 'chore: reindex' && git push" >&2
fi

exit 0
