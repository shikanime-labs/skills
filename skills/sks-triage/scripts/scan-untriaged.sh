#!/usr/bin/env bash
# Usage: scripts/scan-untriaged.sh OWNER/REPO
# List open issues and PRs whose triage metadata is incomplete, computed
# against what the repo or its org actually supports. One paginated call per
# repo. Output: TSV number, kind, missing classes.
set -euo pipefail

if [[ $# -ne 1 || -z $1 ]]; then
  echo "Error: REPO (OWNER/REPO) is required." >&2
  echo "Usage: scripts/scan-untriaged.sh shikanime-labs/skills" >&2
  exit 2
fi

REPO=$1
OWNER=${REPO%/*}

TYPES=$(gh api "repos/$REPO/issue-types" \
  --jq '[.[] | select(.is_enabled)] | length' 2>/dev/null || echo 0)
FIELDS=$(gh api "orgs/$OWNER/issue-fields" --jq 'length' 2>/dev/null || echo 0)
MILESTONES=$(gh api "repos/$REPO/milestones?state=open" \
  --jq 'length' 2>/dev/null || echo 0)

echo "# classes: type=$TYPES fields=$FIELDS milestones=$MILESTONES"

gh api --paginate "repos/$REPO/issues?state=open&per_page=100" --jq '.[] |
  [.number,
   (if .pull_request then "pr" else "issue" end),
   (.type.name // "-"),
   ([.labels[].name] | join(",")),
   ([.assignees[].login] | join(",")),
   (if ([.issue_field_values[].issue_field_name] | length) == 0 then "none"
    else [.issue_field_values[].issue_field_name] | join(",") end),
   (.milestone.title // "-")] | @tsv' |
  while IFS=$'\t' read -r n kind type labels assignees fields milestone; do
    gaps=""
    if [[ $kind == issue && $TYPES -gt 0 && $type == "-" ]]; then
      gaps+="type,"
    fi
    if [[ -z $labels ]]; then
      gaps+="labels,"
    fi
    if [[ -z $assignees ]]; then
      gaps+="assignee,"
    fi
    if [[ $MILESTONES -gt 0 && $milestone == "-" ]]; then
      gaps+="milestone,"
    fi
    if [[ $kind == issue && $FIELDS -gt 0 && $fields == "none" ]]; then
      gaps+="fields,"
    fi
    if [[ -n $gaps ]]; then
      printf '%s\t%s\t%s\n' "$n" "$kind" "${gaps%,}"
    fi
  done
