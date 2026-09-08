#!/usr/bin/env bash
# Usage: scripts/verify-backport.sh BASE_TAG TIP EXPECTED_COUNT
# Verify a rebuilt hotfix chain: exact commit count, zero conflict markers,
# and a tree that reconstructs main's source (release-please files may
# differ). Exit 0 when clean; exit 1 and print what failed otherwise.
set -euo pipefail

if [[ $# -ne 3 || -z $1 || -z $2 || -z $3 ]]; then
  echo "Error: BASE_TAG TIP EXPECTED_COUNT are required." >&2
  echo "Usage: scripts/verify-backport.sh v9.24.4 <tip> 16" >&2
  exit 2
fi

BASE_TAG=$1
TIP=$2
EXPECTED=$3
RANGE="$BASE_TAG..$TIP"

COUNT=$(jj log -r "$RANGE" --no-graph -T 'commit_id' | grep -c . || true)
CONFLICTS=$(jj log -r "$RANGE" --no-graph \
  -T 'if(conflict, description.first_line(), "")' | grep -c . || true)

FAIL=0
if [[ $COUNT != "$EXPECTED" ]]; then
  echo "FAIL: chain has $COUNT commits, expected $EXPECTED" >&2
  FAIL=1
fi
if [[ $CONFLICTS != "0" ]]; then
  echo "FAIL: $CONFLICTS conflict markers in $RANGE" >&2
  FAIL=1
fi

# tree reconstructs main's source (release-please files may differ)
DIFF=$(git diff --name-only "$TIP" main | grep -vE \
  'package\.json|CHANGELOG\.md|\.release-please-manifest\.json' || true)
if [[ -n $DIFF ]]; then
  echo "FAIL: tree differs from main: $DIFF" >&2
  FAIL=1
fi

if [[ $FAIL == "0" ]]; then
  echo "OK: $COUNT commits, no conflicts, tree matches main"
fi
exit "$FAIL"
