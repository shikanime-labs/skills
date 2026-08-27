# jj Colocation Escape Hatch for CPN Release Patches

When `jj duplicate --onto @` fails due to stale colocation state, an empty
working copy, or any jj error that blocks the duplicate path.

## Why this exists

`jj duplicate` can fail when the jj working copy is in an unexpected state:
a prior `jj bookmark set` moved the internal ref, or the working copy is
on an old empty scaffold. The recovery below tries jj-native steps first.
Only if all jj approaches fail do we drop to git as a true last resort
(`git cherry-pick` is *always* reliable — it is the escape hatch of last
resort, used here solely because it has no dependency on jj colocation state).

## Procedure

### Step 1: Diagnose the failure

```bash
# Check current working copy state
jj status
# Is @ an empty scaffold?
jj log -r @ --no-graph -T 'commit_id ++ " " ++ description.first_line()'
# Is the bookmark stale?
jj log -r 'hotfix/$NEXT' --no-graph -T 'commit_id ++ " " ++ description.first_line()' 2>&1
```

### Step 2: Try jj-native recovery (preferred)

If the working copy is on an empty scaffold or stale state:

```bash
# Abandon the broken working copy content
jj abandon @ 2>/dev/null; true

# Move to the tag directly — no scaffold
jj goto BASE_TAG

# Verify @ is the tag
jj log -r @ --no-graph -T 'commit_id ++ " " ++ description.first_line()'

# Now duplicate the milestone set
IDS=($(cat /tmp/cpn_ms_ids.txt))
# jj dup each SHA in order (oldest first), onto @
for c in "${IDS[@]}"; do
  jj dup "$c" --onto @
done

# Set the bookmark to the new chain tip
TIP=$(jj log -r 'heads(@)' --no-graph -T commit_id | head -1)
jj bookmark set hotfix/$NEXT -r "$TIP"
```

### Step 3: Last resort — git cherry-pick (if jj duplicate still fails)

If jj-native recovery above does not produce a clean chain (e.g., `jj dup`
errors on a specific commit, or colocation is irrecoverably broken):

```bash
# 1. Create a fresh git branch rooted on BASE_TAG (no stale state possible)
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

### Step 4: Sync jj after git cherry-pick

```bash
# Abandon any stale jj working copy
jj abandon <old_chain_root> 2>/dev/null; true

# Sync jj with the updated git ref
jj git fetch
jj bookmark set hotfix/$NEXT

# Verify the bookmark matches the git HEAD
jj log -r 'hotfix/$NEXT' --no-graph -T 'change_id ++ " " ++ description.first_line() ++ "\n"'
```

## Key constraints

- **`git checkout -B` creates or resets the local branch** — no stale state
  possible. Use only as a last resort.
- **`git cherry-pick` is sequential**: each commit parents the previous,
  preserving the milestone's ordered history.
- **`git push --force-with-lease`** is safe against concurrent pushes (the
  lease detects if someone else moved the branch).
- After git recovery, the git ref `hotfix/$NEXT` IS the canonical branch. Do
  NOT run `jj bookmark set` before the git push or it will leave the git ref
  pointing at the old (possibly empty) commit.
- Prefer `jj dup` / `jj goto` / `jj abandon` whenever possible — git is the
  escape hatch, not the default path.
