# Backport Pitfalls

The failure modes of the cpn release-patch backport chain, observed
live. Read before running the procedure; the body carries the steps.

## Pitfalls

- **The backport set is the MILESTONE, not `BASE_TAG..main`.** A
  `BASE_TAG..main` patch-id diff over-counts: in the observed case it
  returned 35 commits — 16 in the patch milestone + 19 from the next
  minor's dev work whose patch-ids are also absent from the tag.
  Duplicating all 35 leaks next-minor features into the hotfix. Always
  source the set from the milestone's merged PRs (Step 2).
- **The issues API hides merge_commit_sha.** `repos/R/issues?milestone=N`
  returns `pull_request.merge_commit_sha: null`; only the pulls endpoint
  (`repos/R/pulls/<n>`) exposes the real SHA. `fetch-backport-set.py` fetches
  PR numbers from issues, then SHAs from pulls — never write `null` SHAs into
  the duplicate list.
- **NEVER `jj new BASE_TAG -m "..."` as the duplicate base.** It creates an
  empty commit that becomes a permanent ancestor of the tip, shows up in
  `BASE_TAG..hotfix/$NEXT`, and blocks `jj git push` ("Won't push commit … has
  no description"). Use `jj goto BASE_TAG` (Step 3) so the chain roots directly
  on the tag with no scaffold. Recovery:
  `jj rebase -r <chain_root> -d BASE_TAG && jj abandon <empty_commit_id>`.
- **`jj duplicate --onto @` fails with colocation state** (e.g. a prior
  `jj bookmark set` moved the internal ref, leaving jj's working copy on a
  stale scaffold). Try `jj abandon @`, `jj goto BASE_TAG`, then
  `jj duplicate --onto @`. If jj colocation is irrecoverable, fall back to
  `git cherry-pick` (see `references/jj-colocation-escape-hatch.md`); sync jj
  with `jj git fetch` then `jj bookmark set hotfix/$NEXT` after the git push —
  never `jj bookmark set` before it, or the git ref points at the old (possibly
  empty) commit.
- **Tip revset**: after `duplicate --onto @`, bookmark `heads(@)`, never a
  manually guessed commit.
- **Stale remote-tracking blocks push**: after any prior force-push of
  `hotfix/$NEXT`, local jj believes the remote is at the old SHA. `jj git fetch`
  clears it; then `jj bookmark set … --allow-backwards` + push.
- **`A..B` in jj = set difference**, not git's "exclusive range with merge
  base". `BASE_TAG..main` names the commits, but content overlap / next-minor
  leakage makes it wrong as a backport source — hence the milestone in Step 2.
- **Tag is not an ancestor of the default branch**: expected for release
  tags (they carry hotfix-only commits). Do not try to branch from the
  default branch; branch from the tag.
- **Verify by tree, not count**: after duplicate, `git diff --name-only <tip>`
  against the default branch should show only `package.json` /
  `CHANGELOG.md` / `.release-please-manifest.json`. Any other differing
  file means a milestone commit was missed or mis-ordered — re-run Step 2,
  do not push.
- **No `jj git tag` in 0.43**: tags are git objects synced through colocation.
  Create branches with `jj bookmark create`/`set`, not tags.
- **`jj op undo` does not exist** in this jj version — to roll back a dry run
  or a bad duplicate, `jj abandon '<revset>'` or
  `jj op restore --to <op-id>`
  (`jj op log` to find it). Restoring to the pre-duplicate checkpoint and
  rebuilding from Step 3 is the safe reset path.
- **Conflict during duplicate**: rare with the milestone set (commits are
  independent fixes). If one appears, resolve in the working copy, `jj squash`,
  continue. Do not re-scope the set.
- **Branch already exists on origin** (`hotfix/$NEXT`): the patch was already
  started. `jj git fetch`, rebase your duplicate onto the existing bookmark, and
  push — do not force a second branch.
