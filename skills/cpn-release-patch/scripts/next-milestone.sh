#!/usr/bin/env bash
# Usage: scripts/next-milestone.sh BASE_TAG
# Print the next patch milestone for a base tag, e.g. v9.24.4 -> 9.24.5.
# Pure derivation — no network. The hotfix/<milestone> branch name derives
# from this value.
set -euo pipefail

if [[ $# -ne 1 || -z $1 ]]; then
  echo "Error: BASE_TAG is required." >&2
  echo "Usage: scripts/next-milestone.sh v9.24.4" >&2
  exit 2
fi

BASE_TAG=$1
BASE=${BASE_TAG#v}
if [[ $BASE != *.*.* || $BASE == *.*.*.* ]]; then
  echo "Error: '$BASE_TAG' is not a vMAJOR.MINOR.PATCH tag (e.g. v9.24.4)." >&2
  exit 2
fi
IFS=. read -r MAJ MIN PAT <<<"$BASE"
if [[ ! $MAJ =~ ^[0-9]+$ || ! $MIN =~ ^[0-9]+$ || ! $PAT =~ ^[0-9]+$ ]]; then
  echo "Error: '$BASE_TAG' is not a vMAJOR.MINOR.PATCH tag (e.g. v9.24.4)." >&2
  exit 2
fi
echo "$MAJ.$MIN.$((PAT + 1))"
