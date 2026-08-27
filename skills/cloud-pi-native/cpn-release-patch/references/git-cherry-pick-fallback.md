# Git Cherry-Pick Fallback for CPN Release Patches

When `jj duplicate --onto @` fails due to stale jj state, an empty working copy,
or any jj error, use this git-based procedure to build the hotfix chain.

## Why this exists

`jj duplicate` can fail when the jj working copy is in an unexpected state
(e.g., a prior `jj bookmark set` moved the internal ref, or the working copy is
an old empty scaffold). The git approach is a known-good escape hatch that always
produces a clean chain.

## Procedure

```bash
# 1. Create a fresh git branch rooted on BASE_TAG
git checkout -B hotfix/$NEXT BASE_TAG

# 2. Cherry-pick each milestone commit in order (oldest first)
#    IDs are in /tmp/cpn_ms_ids.txt, one SHA per line
IDS=($(cat /tmp/cpn_ms_ids.txt))
for c in "${IDS[@]}"; do
  git cherry-pick "$c"
done

# 3. Verify commit count matches milestone size
COMMITS=$(git rev-list --count BASE_TAG..hotfix/$NEXT)
expected=$(wc -l < /tmp/cpn_ms_ids.txt)
echo "$COMMITS commits (expected $expected)"

# 4. Push (force-with-lease replaces the remote bookmark)
git push --force-with-lease origin hotfix/$NEXT
```

## Key constraints

- `git checkout -B` creates or resets the local branch — no stale state possible.
- `git cherry-pick` is sequential: each commit parents the previous, preserving
  the milestone's ordered history.
- `git push --force-with-lease` is safe against concurrent pushes (the lease
  detects if someone else moved the branch).
- After this, the git ref `hotfix/$NEXT` IS the canonical branch. Do NOT run
  `jj bookmark set` — the jj internal bookmark will sync on next `jj git fetch`.

## jj bookmark cleanup (after git cherry-pick)

If you already ran `jj bookmark set` before the git push and want to sync jj
to the updated git ref:

```bash
# The jj working copy may be on the old (empty) scaffold. Abandon it.
# If jj abandons nothing, the working copy is already at the right state.
jj abandon <old_chain_root>  2>/dev/null; true

# Sync jj with the updated git ref
jj git fetch
jj bookmark set hotfix/$NEXT

# Verify the bookmark matches the git HEAD
jj log -r 'hotfix/$NEXT' --no-graph -T 'change_id ++ " " ++ description.first_line() ++ "\n"'
```

If the working copy is on an empty scaffold after `jj git fetch`, create a new
working copy on the tag and build the chain via git (the fallback procedure),
then abandon the scaffold.
