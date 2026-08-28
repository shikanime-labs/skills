#!/usr/bin/env bash
# Usage: scripts/fetch-backport-set.sh REPO MILE_NUM [OUTFILE]
# Print (or write to OUTFILE, default /tmp/cpn_ms_ids.txt) the ordered
# (oldest->newest) merge commit SHAs of a milestone's merged PRs. One SHA per
# line. The milestone is the authoritative backport set — NOT a BASE_TAG..main
# diff (that over-counts next-minor dev commits).
set -euo pipefail

if [[ $# -lt 2 || -z "$1" || -z "$2" ]]; then
  echo "Error: REPO and MILE_NUM are required." >&2
  echo "Usage: scripts/fetch-backport-set.sh cloud-pi-native/console 42" >&2
  exit 2
fi

REPO=$1
MILE_NUM=$2
OUT=${3:-/tmp/cpn_ms_ids.txt}
PRS="$OUT.prs"

# Phase 1: the milestone's PR numbers, oldest merged first. The issues endpoint
# honors the milestone filter but returns null merge_commit_sha.
gh api --paginate \
  "repos/$REPO/issues?milestone=$MILE_NUM&state=closed&per_page=100" \
  --jq '.[] | select(.pull_request and .pull_request.merged_at != null)
    | "\(.pull_request.merged_at) \(.number)"' \
  | sort | awk '{print $2}' >"$PRS"

# Phase 2: merge_commit_sha per PR (only the pulls endpoint returns it).
: >"$OUT"
while read -r pr; do
  [[ -n "$pr" ]] || continue
  gh api "repos/$REPO/pulls/$pr" --jq '.merge_commit_sha' >>"$OUT"
done <"$PRS"
rm -f "$PRS"

echo "wrote $(wc -l <"$OUT" | tr -d ' ') commits to $OUT" >&2
