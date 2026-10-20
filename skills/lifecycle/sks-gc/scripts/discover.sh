#!/usr/bin/env bash
# Usage: scripts/discover.sh [REPO_DIR]
# Discover GC candidates in a shikanime jj repo: dangling bookmarks (not on
# trunk, no open PR) and skill-created workspaces (<repo>.<unit> or
# <repo>-fix), with the dirty working-copy guard. Dry-run only — never forgets
# or removes. Default REPO_DIR is the cwd; run from the repo root.
set -euo pipefail

REPO_DIR=${1:-$(pwd)}
cd "$REPO_DIR"

if [[ ! -d .jj ]]; then
  echo "Error: $REPO_DIR has no .jj/ — run from a jj repo root." >&2
  exit 2
fi

# protected names: trunk + any bookmark with an open PR
TRUNK='main trunk master'
OPEN_PRS=$(gh pr list --state open --limit 200 --json headRefName \
  --jq '.[].headRefName')

echo "== dangling bookmarks (not trunk, no open PR) =="
# jj 0.43: default `bookmark list` lines carry "name: changeid desc" plus
# indented @origin continuation lines — template the name alone and dedupe.
# `trunk()` resolves the configured trunk (main/trunk/master) so the revset
# works on repos whose trunk is not named main.
jj bookmark list -r 'bookmarks() & ~::trunk()' --color never \
  -T 'name ++ "\n"' |
  sort -u | while read -r bm; do
  case " $TRUNK " in
  *" $bm "*) continue ;;
  esac
  if echo "$OPEN_PRS" | grep -qx "$bm"; then
    continue
  fi
  echo "$bm"
done

echo "== skill workspaces (<repo>.<unit> or <repo>.fix) =="
# jj 0.43: default `workspace list` has no path column — template it explicitly
REPO_NAME=$(basename "$PWD")
jj workspace list --color never -T 'name ++ "\t" ++ root ++ "\n"' |
  while IFS=$'\t' read -r name path; do
    [[ $name == "$REPO_NAME".* ]] ||
      continue
    # canonical repo-named workspace is never a candidate
    if jj -R "$path" status --color never 2>/dev/null |
      grep -q 'has no changes'; then
      echo "CLEAN $name $path"
    else
      echo "DIRTY $name $path   # skip: uncommitted changes (data loss)"
    fi
  done
