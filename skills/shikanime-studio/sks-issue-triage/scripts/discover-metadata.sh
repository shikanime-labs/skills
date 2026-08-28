#!/usr/bin/env bash
# Usage: scripts/discover-metadata.sh REPO
# Discover every triage-relevant metadata value a repo offers: labels,
# milestones, projects, assignees, issue types, and custom fields. This is the
# source of truth — triage must only set values that exist here. Structured
# output, one section per metadata class.
set -euo pipefail

if [[ $# -ne 1 || -z "$1" ]]; then
  echo "Error: REPO (OWNER/REPO) is required." >&2
  echo "Usage: scripts/discover-metadata.sh shikanime-labs/skills" >&2
  exit 2
fi

REPO=$1
OWNER=${REPO%/*}

echo "== labels =="
gh label list --repo "$REPO" --limit 200 --json name,description \
  --jq '.[] | "\(.name)\t\(.description // "")"'

echo "== milestones (open) =="
gh api --paginate "repos/$REPO/milestones?state=open" \
  --jq '.[] | "\(.number)\t\(.title)"'

echo "== projects (owner) =="
gh project list --owner "$OWNER" --format json \
  --jq '.[] | "\(.number)\t\(.title)"' 2>/dev/null \
  || echo "no accessible projects (needs project scope)"

echo "== assignees =="
gh api --paginate "repos/$REPO/assignees" --jq '.[].login'

echo "== issue types (enabled) =="
gh api --paginate "repos/$REPO/issue-types" \
  --jq '.[] | select(.is_enabled) | .name'

echo "== custom fields =="
FIELDS=$(gh api --paginate "repos/$REPO/fields" --jq '.[].name' 2>/dev/null) || FIELDS=""
if [[ -z "$FIELDS" ]]; then
  echo "no repo-level fields"
else
  echo "$FIELDS"
fi
