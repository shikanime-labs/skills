---
name: cpn-release-patch
description:
  "Use when backporting the commits between two release tags onto a hotfix
  branch in <org>/<repo>: find the patch milestone and duplicate
  those commits onto the tag with jj."
version: 0.4.0
author: Automata
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
      - sks-dev
      - sks-pr
      - sks-commit
      - sks-context
---

# Release Patch

Backport the gap between two release tags onto a `hotfix/<milestone>` branch so
release-please opens the patch release PR. The authoritative backport set is the
**target patch milestone's own merged PRs** — NOT a `BASE_TAG..main` diff. The
commits are duplicated onto `BASE_TAG` with `jj`, and the branch is pushed to
`origin`.

The repo is **jj-backed** (`.jj/` present; never `git commit`). Tags are
lightweight git tags exported via jj colocation; release-please consumes the
branch name, not a tag — see Verification.

## Available scripts

Run from the skill directory; each validates its args and exits non-zero with a
message on bad input.

- `scripts/next-milestone.py BASE_TAG` → next patch milestone
  (`vX.Y.Z` → `X.Y.Z+1`).
- `scripts/milestone-number.py REPO MILESTONE_TITLE` → milestone number, or
  exit 1 when absent/closed.
- `scripts/fetch-backport-set.py REPO MILE_NUM [OUTFILE]` → ordered
  merge-commit SHAs of the milestone's merged PRs (default
  `/tmp/sks_ms_ids.txt`).
- `scripts/verify-backport.py BASE_TAG TIP EXPECTED_COUNT` → count /
  conflict / tree-parity check, exit 0 when clean.

## When to Use

"Backport vX.Y.Z to vX.Y.Z+1", "duplicate the diff of main onto the vX.Y.Z tag
as a hotfix", "make a patch hotfix branch from vX.Y.Z", or any request to take
the commits between a tag and `main` and land them on a `hotfix/<x.y.z>`
branch for release-please to cut.

## Inputs

- `BASE_TAG` (required): a published tag, e.g. `vX.Y.Z`. The patch milestone is
  derived from it (see Step 1), the hotfix branch is named after that milestone,
  and the duplicated commits are placed on top of `BASE_TAG`.

Always confirm `BASE_TAG` with the user if ambiguous; never assume `main` is the
base.

## Procedure

### 0. Preconditions

```bash
jj status                       # .jj/ present, no surprise working-copy churn
gh api repos/<org>/<repo> --jq .viewerPermission   # need write/admin
git rev-parse -q --verify BASE_TAG   # tag must exist; replace BASE_TAG
jj git fetch                    # sync remote tags + bookmarks
```

For `<org>/<repo>` values (checkouts, identity, review policy) read
`references/cloud-pi-native.md` when operating in the target org.

If `BASE_TAG` is missing or you lack write: report `BLOCKED: <requirement> —
<evidence> — <recovery>`, do not proceed.

### 1. Resolve the patch milestone from the base tag

`vX.Y.Z` → next patch milestone is `X.Y.Z+1`. Derive mechanically, do not
guess:

```bash
NEXT=$(scripts/next-milestone.py "$BASE_TAG")
MILE_NUM=$(scripts/milestone-number.py <org>/<repo> "$NEXT")
```

If the milestone is absent or already closed, the script exits non-zero —
surface it before pushing; a duplicate patch branch would collide with an
already-cut release.

### 2. Get the EXACT backport set from the milestone (authoritative)

The milestone's merged PRs ARE the backport set. Do **not** derive it from a
`BASE_TAG..main` patch-id diff — that over-counts, because `main` carries the
next minor's dev commits (`<next-minor>` prerelease work) whose patch-ids are
not on the tag either, so they leak in. In one observed case the milestone
had **16** commits while a `BASE_TAG..main` patch-id diff returned **35**
(16 in-milestone + 19 from the next minor's dev). The milestone is the
precise source of truth.

```bash
scripts/fetch-backport-set.py <org>/<repo> "$MILE_NUM"
wc -l /tmp/sks_ms_ids.txt   # expect the milestone size
```

`/tmp/sks_ms_ids.txt` is the ordered (oldest→newest) list of the exact commits
to duplicate. Order matters: `jj duplicate` replays them in argument order, and
each must parent onto the previous so the chain re-roots cleanly on the tag.

Optional sanity check (not the selector): confirm none are already an ancestor
of `BASE_TAG` — a hit makes `jj duplicate` produce a harmless no-op commit:

```bash
while read c; do git merge-base --is-ancestor "$c" BASE_TAG && \
  echo "already-on-tag: $c"; done < /tmp/sks_ms_ids.txt
```

### 3. Rebuild the chain directly on the tag (NO empty scaffold)

Critical: do **not** `jj new BASE_TAG -m "..."`. That creates an *empty* commit
as a child of the tag; when you duplicate `--onto @` it stays an ancestor of the
tip, shows up in `BASE_TAG..hotfix/$NEXT`, and blocks the push ("Won't push
commit … has no description"). Point the working copy at the tag itself so the
duplicated chain's root parent is the tag, with no scaffold:

```bash
jj goto BASE_TAG                 # @ becomes the tag commit (no new empty commit)
IDS=$(tr '\n' ' ' < /tmp/sks_ms_ids.txt)
jj duplicate $IDS --onto @       # duplicated commits are children of @ (= BASE_TAG)
TIP=$(jj log -r 'heads(@)' --no-graph -T commit_id | head -1)   # newest duplicate
```

`heads(@)` after the duplicate is exactly the tip — no empty commit to drop.
If you already used `jj new BASE_TAG -m`, recover by rebasing the chain root
onto the tag and abandoning the empty commit:

```bash
ROOT=$(jj log -r '(<empty_commit_id>::)' --no-graph -T 'commit_id' | tail -1)
jj rebase -r "$ROOT" -d BASE_TAG
jj abandon <empty_commit_id>
```

### 4. Verify the backport is complete and clean

```bash
scripts/verify-backport.py "$BASE_TAG" "$TIP" \
  "$(wc -l < /tmp/sks_ms_ids.txt)"
```

The script checks exact commit count (milestone size, no scaffold), zero
conflict markers in `BASE_TAG..$TIP`, and a tree that reconstructs
`main`'s source (release-please files may differ). Also compare chain subjects
against the milestone PR titles — zero extras (no next-minor commits).

### 5. Create the hotfix bookmark and push

Path A — jj `duplicate` (preferred):

```bash
jj bookmark set hotfix/$NEXT -r "$TIP"
jj git push --bookmark hotfix/$NEXT --remote origin
```

Path B — jj colocation escape hatch (when `jj duplicate` fails): see
`references/jj-colocation-escape-hatch.md` for jj-native recovery and a
last-resort `git cherry-pick` fallback.

If the push fails with `unexpectedly moved on the remote` / `stale info`, clear
the stale remote-tracking bookmark, re-point, and push:

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

## Pitfalls

The backport chain's failure modes - milestone-vs-range sourcing,
null SHAs from the issues API, empty scaffold bases, jj colocation
escapes, stale remote-tracking, tree-diff verification - are
catalogued in `references/backport-pitfalls.md`. Read it before the
first duplicate, not after the first blocked push.

## Verification

Release-please specifics for the target repo — when operating in
cloud-pi-native/console, read `references/cloud-pi-native.md` for the
repo's exact config.

- `release-please-config.json`: `release-type: node`, single package `.`;
  next version comes from `.release-please-manifest.json`.
- The release workflow on a `hotfix/*` branch uses
  `versioning-strategy: always-bump-patch`, so the manifest version bumps
  to the patch — the milestone `NEXT` derived in Step 1. The branch name
  `hotfix/<x.y.z>` is the only trigger; no tag needed.
- Therefore: name the branch `hotfix/$NEXT`, push it, let release-please
  open the release PR. Do not hand-cut `v$NEXT`.

## See also

- `sks-dev` — the org repo's contribution workflow, jj conventions,
  PR rules.
- `sks-pr` — open the release PR if release-please does not auto-open.
- `sks-commit` — commit message shape (conventional, SSH-signed).
- `references/jj-colocation-escape-hatch.md` — jj-native recovery and a
  last-resort `git cherry-pick` escape hatch when `jj duplicate` fails.
