#!/usr/bin/env bash
# Usage: scripts/milestone-number.sh REPO MILESTONE_TITLE
# Print the milestone number for the given title on REPO (OWNER/REPO), or exit
# non-zero when the milestone is absent or closed. The number feeds
# fetch-backport-set.sh and the issue query in Step 2.
set -euo pipefail

if [[ $# -ne 2 || -z $1 || -z $2 ]]; then
  echo "Error: REPO and MILESTONE_TITLE are required." >&2
  echo "Usage: scripts/milestone-number.sh cloud-pi-native/console 9.24.5" >&2
  exit 2
fi

REPO=$1
TITLE=$2

NUM=$(gh api --paginate "repos/$REPO/milestones?state=open" \
  --jq ".[] | select(.title == \"$TITLE\") | .number")
if [[ -z $NUM ]]; then
  echo "Error: milestone '$TITLE' is absent or closed on $REPO." >&2
  exit 1
fi
echo "$NUM"
