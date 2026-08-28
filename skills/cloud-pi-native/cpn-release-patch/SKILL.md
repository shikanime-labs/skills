---
name: cpn-release-patch
description:
  "Use when backporting the commits between two release tags onto a hotfix
  branch in cloud-pi-native/console: find the patch milestone and duplicate
  those commits onto the tag with jj."
version: 0.3.1
author: Hermes Agent
license: Apache-2.0
platforms:
  - linux
  - macos
  - windows
metadata:
  hermes:
    tags:
      - cloud-pi-native
      - console
      - jj
      - release-please
      - hotfix
      - backport
    related_skills:
      - cpn-dev-workflow
      - cpn-pr
      - cpn-commit
---

# CPN Release Patch (tag → hotfix branch)

Backport the gap between two release tags onto a `hotfix/<milestone>` branch so
release-please opens the patch release PR. The authoritative backport set is the
**target patch milestone's own merged PRs** — NOT a `BASE_TAG..main` diff. The
commits are duplicated onto `BASE_TAG` with `jj`, and the branch is pushed to
`origin`.

The repo is **jj-backed** (`.jj/` present; never `git commit`). Tags are
lightweight git tags exported via jj colocation; release-please consumes the
branch name, not a tag — see Verification.

## When to Use

"Backport v9.24.4 to v9.24.5", "duplicate the diff of main onto the v9.24.4 tag
as a hotfix", "make a patch hotfix branch from v9.24.4", or any request to take
the commits between a tag and `main` and land them on a `hotfix/<x.y.z>`
branch for release-please to cut.

## Inputs

- `BASE_TAG` (required): a published tag, e.g. `v9.24.4`. The patch milestone is
  derived from it (see Step 1), the hotfix branch is named after that milestone,
  and the duplicated commits are placed on top of `BASE_TAG`.

Always confirm `BASE_TAG` with the user if ambiguous; never assume `main` is the
base.

## Procedure

### 0. Preconditions (verify, block if unmet)

```bash
jj status                       # .jj/ present, no surprise working-copy churn
gh api repos/cloud-pi-native/console --jq .viewerPermission   # need write/admin
git rev-parse -q --verify BASE_TAG   # tag must exist; replace BASE_TAG
jj git fetch                    # sync remote tags + bookmarks
```

If `BASE_TAG` is missing or you lack write: report `BLOCKED: <requirement> —
<evidence> — <recovery>`, do not proceed.

### 1. Resolve the patch milestone from the base tag

`v9.24.4` → next patch milestone is `9.24.5`. Derive mechanically, do not guess:

```bash
BASE=${BASE_TAG#v}                       # 9.24.4
IFS=. read -r MAJ MIN PAT <<< "$BASE"
NEXT="$MAJ.$MIN.$((PAT + 1))"            # 9.24.5  -> the hotfix/<milestone> name
```

Cross-check the milestone actually exists on the repo and capture its number
(needed for the commit set in Step 2):

```bash
MILE_NUM=$(gh api repos/cloud-pi-native/console/milestones --jq \
  '.[] | select(.title == "'\''$NEXT'\''") | .number')
echo "milestone $NEXT -> #$MILE_NUM"
```

If the milestone is absent or already closed, surface it before pushing — a
duplicate patch branch would collide with an already-cut release.

### 2. Get the EXACT backport set from the milestone (authoritative)

The milestone's merged PRs ARE the backport set. Do **not** derive it from a
`BASE_TAG..main` patch-id diff — that over-counts, because `main` carries the
*next* minor's dev commits (`9.25.0` prerelease work) whose patch-ids are not on
the tag either, so they leak in. For `v9.24.4` the milestone had **16** commits;
a `v9.24.4..main` patch-id diff returned **35** (16 in-milestone + 19 from
`9.25.0` dev). The milestone is the precise source of truth.

```bash
# milestone's closed PRs: merged commit SHA + merged date, oldest first
URL="repos/cloud-pi-native/console/issues?milestone=$MILE_NUM&state=closed&per_page=100"
gh api "$URL" \
  --jq '.[] | select(.pull_request) |
    "\\(.pull_request.merged_at) \\(.pull_request.merge_commit_sha)"' \
  | sort | awk '{print $2}' > /tmp/cpn_ms_ids.txt

wc -l /tmp/cpn_ms_ids.txt   # expect the milestone size (16 for v9.24.5)
```

`/tmp/cpn_ms_ids.txt` is now the ordered (oldest→newest) list of the exact
commits to duplicate. Order matters: `jj duplicate` replays them in argument
order, and each must parent onto the previous so the chain re-roots cleanly on
the tag.

Optional sanity check (not the selector): confirm none of these commits are
already an ancestor of `BASE_TAG` — if any are, `jj duplicate` will simply
produce an empty/no-op commit for it, which is harmless but worth noting:

```bash
while read c; do git merge-base --is-ancestor "$c" BASE_TAG && \
  echo "already-on-tag: $c"; done < /tmp/cpn_ms_ids.txt
```

### 3. Rebuild the chain directly on the tag (NO empty scaffold)

Critical: do **not** `jj new BASE_TAG -m "..."`. That creates an *empty* commit
as a child of the tag, and when you duplicate `--onto @` the empty commit stays
an ancestor of the tip — it then appears in `BASE_TAG..hotfix/$NEXT` and blocks
the push ("Won't push commit … has no description"). Instead, point the working
copy at the tag itself and duplicate onto it; the duplicated chain's root parent
is the tag, with no scaffold:

```bash
jj goto BASE_TAG                 # @ becomes the tag commit (no new empty commit)
IDS=$(tr '\n' ' ' < /tmp/cpn_ms_ids.txt)
jj duplicate $IDS --onto @       # duplicated commits are children of @ (= BASE_TAG)
TIP=$(jj log -r 'heads(@)' --no-graph -T commit_id | head -1)   # newest duplicate
```

`heads(@)` after the duplicate is exactly the tip of the new chain — no empty
commit to drop. If you ever did use `jj new BASE_TAG -m`, recover by rebasing the
chain root onto the tag and abandoning the empty commit:

```bash
# WRONG: jj rebase -r root(<empty>::)  -> use the explicit root SHA instead
# CORRECT recovery:
ROOT=$(jj log -r '(<empty_commit_id>::)' --no-graph \
  -T 'commit_id' | tail -1)  # oldest child of empty
jj rebase -r "$ROOT" -d BASE_TAG
jj abandon <empty_commit_id>
```

### 4. Verify the backport is complete and clean

```bash
# exactly the milestone size, no empty/scaffold commit
jj log -r "BASE_TAG..hotfix/$NEXT" --no-graph -T 'commit_id' |
  grep -c .   # = lines in /tmp/cpn_ms_ids.txt
# no conflict markers anywhere in the chain
jj log -r "BASE_TAG..hotfix/$NEXT" --no-graph \
  -T 'if(conflict, description.first_line(), "")' | grep -c .   # must be 0
# tree reconstructs main's source (release-please files may differ) — optional
# but recommended
git diff --name-only "$TIP" main | grep -vE \
  'package\.json|CHANGELOG\.md|\.release-please-manifest\.json'
# empty output above = trees identical; backport complete
```

Also confirm the milestone set is fully present (subjects) and nothing extra
leaked — compare `BASE_TAG..hotfix/$NEXT` subjects against the milestone PR
titles; there must be zero extras (no `9.25.0` commits).

### 5. Create the hotfix bookmark and push

**Two paths depending on how the chain was built.**

Path A —jj `duplicate` (preferred when it works):

```bash
jj bookmark set hotfix/$NEXT -r "$TIP"
jj git push --bookmark hotfix/$NEXT --remote origin
```

Path B —jj colocation escape hatch (when `jj duplicate` fails):
See `references/jj-colocation-escape-hatch.md` for jj-native recovery
(abandon stale scaffold, `jj goto BASE_TAG`, `jj dup --onto @`) and a
last-resort `git cherry-pick` fallback when jj colocation state is
irrecoverable. The git escape hatch is `git push --force-with-lease origin
hotfix/$NEXT` after building the chain via git.

If the push fails with `unexpectedly moved on the remote` / `stale info`, the
local jj has a stale remote-tracking bookmark (e.g. from a prior force-push of
this branch). Clear it, then re-point and push:

```bash
jj git fetch                                          # clears stale remote-tracking
jj bookmark set hotfix/$NEXT -r "$TIP" --allow-backwards   # resolves any conflict
jj git push --bookmark hotfix/$NEXT --remote origin
```

`hotfix/$NEXT` is the branch release-please watches (see Verification). Do not
create a `v$NEXT` tag — release-please cuts it from the branch.

### 6. Report

Return the pushed branch (`hotfix/$NEXT`), the duplicate commit count, and the
commit range (`BASE_TAG..hotfix/$NEXT`). Tell the user release-please will open
a `chore: Release v$NEXT` PR against `hotfix/$NEXT` with `always-bump-patch`.

## Verification (release-please mechanics — why this works)

- `release-please-config.json`: `release-type: node`, single package `.` =
  `console`; next version comes from `.release-please-manifest.json` (currently
  `9.24.4`).
- `.github/workflows/job-release-please.yml`: when run on a `hotfix/*` branch it
  uses `versioning-strategy: always-bump-patch`, so the manifest `9.24.4`
  becomes `9.24.5` — the milestone `NEXT` derived in Step 1. The branch name
  `hotfix/<x.y.z>` is the only trigger; no tag needed.
- Therefore: name the branch `hotfix/$NEXT`, push it, let release-please open
  the release PR. Do not hand-cut `v$NEXT`.

## Pitfalls

- **The backport set is the MILESTONE, not `BASE_TAG..main`.** A `v9.24.4..main`
  patch-id diff returns 35 commits for `v9.24.4`: 16 in the `9.24.5` milestone +
  19 from `9.25.0` dev work whose patch-ids are also absent from the tag.
  Duplicating all 35 leaks `9.25.0` features into the hotfix. Always source the
  set from the milestone's merged PRs (Step 2).
- **NEVER `jj new BASE_TAG -m "..."` as the duplicate base.** It creates an empty
  commit that becomes a permanent ancestor of the tip, shows up in
  `BASE_TAG..hotfix/$NEXT`, and blocks `jj git push` ("Won't push commit …
  has no description"). Use `jj goto BASE_TAG` (Step 3) so the chain roots
  directly on the tag with no scaffold. If you already made the empty commit:
  `jj rebase -r <chain_root> -d BASE_TAG && jj abandon <empty_commit_id>`.
- **`jj duplicate --onto @` fails with colocation state** (e.g., a prior
  `jj bookmark set` moved the internal ref, leaving jj's working copy on a stale
  scaffold). Try jj-native recovery first: `jj abandon @`, `jj goto BASE_TAG`,
  then `jj duplicate --onto @`. If jj colocation state is irrecoverable, fall
  back to `git cherry-pick` (see `references/jj-colocation-escape-hatch.md`).
  The git escape hatch is `git checkout -B hotfix/$NEXT BASE_TAG`, cherry-pick
  each SHA sequentially, then `git push --force-with-lease origin
  hotfix/$NEXT`. After that, sync jj with `jj git fetch` then
  `jj bookmark set hotfix/$NEXT` — never `jj bookmark set` before the git push
  or it will leave the git ref pointing at the old (possibly empty) commit.
- **Tip revset**: after `duplicate --onto @`, bookmark `heads(@)`, never a
  manually guessed commit. `heads(@)` is the newest duplicate.
- **Stale remote-tracking blocks push**: after any prior force-push of
  `hotfix/$NEXT`, local jj believes the remote is at the old SHA. `jj git fetch`
  clears it; then `jj bookmark set … --allow-backwards` + push.
- **`A..B` in jj = set difference**, not git's "exclusive range with merge
  base". `BASE_TAG..main` names the commits, but content overlap / next-minor
  leakage makes it wrong as a backport source — hence the milestone in Step 2.
- **Tag is not an ancestor of main**: expected for CPN release tags (they carry
  hotfix-only commits). Do not try to branch from `main`; branch from the tag.
- **Verify by tree, not count**: after duplicate, `git diff --name-only <tip>
  main` should show only `package.json` / `CHANGELOG.md` /
  `.release-please-manifest.json`. Any other differing file means a milestone
  commit was missed or mis-ordered — re-run Step 2, do not push.
- **No `jj git tag` in 0.43**: tags are git objects synced through colocation.
  Create branches with `jj bookmark create`/`set`, not tags.
- **`jj op undo` does not exist** in this jj version — to roll back a dry run or
  a bad duplicate, `jj abandon '<revset>'` or `jj op restore --to <op-id>`
  (`jj op log` to find it). Restoring to the pre-duplicate checkpoint and
  rebuilding from Step 3 is the safe reset path.
- **Conflict during duplicate**: rare with the milestone set (commits are
  independent fixes). If one appears, resolve in the working copy, `jj squash`,
  continue. Do not re-scope the set.
- **Branch already exists on origin** (`hotfix/$NEXT`): the patch was already
  started. `jj git fetch`, rebase your duplicate onto the existing bookmark, and
  push — do not force a second branch.

## See also

- `cpn-dev-workflow` — console contribution workflow, jj conventions, PR rules.
- `cpn-pr` — open the release PR if release-please does not auto-open.
- `cpn-commit` — commit message shape (conventional, SSH-signed).
- `references/jj-colocation-escape-hatch.md` — jj-native recovery and a
  last-resort `git cherry-pick` escape hatch when `jj duplicate` fails
  (stale state, empty working copy, irrecoverable colocation).
