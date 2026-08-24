# CPN PR — Squash, author/sign, verify, and pitfalls (reference detail)

Loaded lazily from `cpn-pr` SKILL.md. Covers finalizing a PR's commit and the
gotchas that recur when squashing / rebase / force-pushing.

## Squash + author/sign a finalized PR commit

When the branch has multiple fixup commits, **squash to one commit before the
user validates**.

### A. Squash into one commit

If both commits are adjacent and the second sits directly on the first:

```bash
# folds the child (reconcile fix) into its parent (per-project email fix)
jj squash -r <second> --message "fix(server-nestjs): <conventional subject>"
```

If non-adjacent or `jj squash` reports a conflict (both touch the same files),
recreate the squashed commit:

```bash
jj log -r '<squashed>' --no-graph \
  -T 'parents.first().commit_id'   # parent of the 2-commit chain
jj new "$BASE"              # empty wc on the base
jj restore --from <squashed>   # pull the full combined diff into the wc
jj describe -m "<conventional subject>"   # set message, no editor
jj commit --config 'user.name=...' --config 'user.email=...' -m "<same subject>"
# move the bookmark to the new commit
jj bookmark set hotfix/<branch> -r @- --allow-backwards
```

### B. Fix author + sign

- jj signs new commits automatically when `signing.behavior = own`. The recreate
  form above reliably **sets the author** (pass `--config user.name/user.email`
  to `jj commit`) **and** gets a fresh signature in one shot.
- Author/committer must match the `Signed-off-by` / `Change-Id` trailers already
  on the commit. When they diverge, align before pushing — ask the user which
  identity owns the commit.
- Git shows `U` (unverified) for the SSH signature **locally** only because no
  `allowedSignersFile` is configured; GitHub verifies the SSH key. Treat the
  `gpgsig -----BEGIN SSH SIGNATURE-----` header as "signed" — don't re-sign to
  clear a local `U`.

### C. Verify the squashed content

**`jj cat` is unreliable in this repo** — it intermittently returns truncated or
empty output. Verify via `jj file show` and cross-check counts:

```bash
ROOT=$(jj root)
jj file show -r <commit> <path> | grep -c "it('should"      # test count
# AI-marker sweep
jj file show -r <commit> <path> | grep -l "ponytail"        # per-file
# signature present
jj log -r <commit> --no-graph -T 'if(signature, "signed", "UNSIGNED")'
# author check
jj log -r <commit> --no-graph -T 'author.name() ++ " <" ++ author.email() ++ ">\n"'
```

If `jj file show` returns suspiciously short output, re-run it — truncation is
intermittent. Trust `jj log`/`jj diff` for graph and wc state; re-verify any
file-content assertion that looks truncated.

### C2. Squash-message hygiene (avoid jj-artifact leakage)

Squashing can auto-concatenate commit descriptions, leaking jj internals and
duplicate/self trailers into the merged commit (same risk as `sks-commit`):

- Strip jj internals before finalizing: no `*` bullet lines (jj's per-commit
  description separator), no `---------` separators (jj description-join
  markers), no stray `Change-Id:` lines from unrelated prior commits.
- One subject + one coherent body + exactly the trailers the repo wants:
  `Co-authored-by: Automata <automata@shikanime.studio>` (always, per operator),
  plus any `Signed-off-by` / `Change-Id` already legitimately on the history —
  never duplicate, never self-co-author.
- When landing via `gh pr merge --squash`, ALWAYS pass the final message
  explicitly with `-m` (subject) and `-m` (body + trailers). Never rely on
  GitHub auto-concatenation of branch commit messages.

### D. Git-based squash / split / force-push (doc repos are plain git, not jj)

These git patterns bit us and were recovered:

- **Squash to one commit**:
  `git reset --soft <base> && git add -A && git commit -m "doc: <subject>"`.
  `<base>` = `origin/main` is ONLY correct if cut from the CURRENT main.
- **`origin/main` may have advanced** since the branch was cut:
  `git reset --soft origin/main` stages spurious REVERTS of unrelated main
  commits. Find the TRUE base first:

```bash
git merge-base --is-ancestor \
  $(git rev-parse <oldest-pr-commit>^) origin/main
```

→ if NO, the branch predates current main; use
`git rebase --onto origin/main <true-base> <branch>` instead of reset-soft.

- **Recover before pushing**: if you staged wrong state,
  `git reset --hard <last-good-sha>` immediately — before any push.
- **Force-push with lease**: `--force-with-lease` alone rejects with "stale
  info" when the local tracking ref is stale. Pin it:
  `git fetch origin <branch>` then

```bash
git push --force-with-lease=refs/heads/<branch>:<known-remote-sha> \
  origin <branch>
```

Get `<known-remote-sha>` from `git ls-remote origin refs/heads/<branch>`.

- **Verify after force-push**: `gh pr view ... --json commits` lags (eventual
  consistency). Confirm the branch tip with
  `git ls-remote origin refs/heads/<branch>` — it must equal your local HEAD.
- **Split a stacked branch into 2 PRs**: cut each slice with
  `git rebase --onto origin/main <slice-base> <temp-branch>`, then resolve
  cross-file overlaps by `git rm` the file already covered by the earlier PR.
  Amend the later PR's message to drop the now-absent file.
- **SSH-sign check**: local `%G?` = `N` is a missing `allowedSignersFile` trust
  gap, NOT an unsigned commit. Confirm with
  `git cat-file -p <commit> | grep -c '^gpgsig'` (expect 1).

## Pitfalls

- Non-conventional PR title → Release Please bumps the wrong version (where
  configured).
- Assuming console rules apply everywhere → false enforcement (e.g. forcing
  conventional commits where there's no commitlint).
- Non-conventional commit on a commitlint repo → `commit-msg` hook rejects
  locally.
- Pushing to `main` → branch protection rejects; use a feature/`hotfix/*`
  branch.
- Pre-push Husky runs tests on repos that have it; an untested push fails before
  GitHub.
- Self-merge may be blocked; a separate review is mandatory where protected.
- Always open PRs against `cloud-pi-native/*` directly: push to `origin` and
  open with `--head cloud-pi-native:<branch>`.
- PR with no linked issue violates the issue-first norm.
- **Verify the linked issue actually matches the PR's code change.** A PR's
  `Issues liées` can point at an unrelated issue (e.g. PR #2403 "use project
  owner email for sonarqube user creation" linked to #2400, a Vault secret bug).
  Search the code (`jj file annotate`, `jj show <commit>`) and the commit for
  the actual intent, and link the _correct_ issue (or create one).
- **Doc repos REQUIRE a `doc:` commit prefix** — the table's old "documentation
  prefers plain-English no prefix" note was wrong. `documentation` and
  `documentation-interne-socle` require `doc:`-prefixed subjects; only the PR
  _title_ is conventional everywhere.
- **`reset --soft origin/main` after main advanced** stages spurious reverts.
  Find the true base — parent of the oldest PR commit — and use
  `git rebase --onto origin/main <true-base> <branch>` instead.
- **`--force-with-lease` "stale info"** → local tracking ref is stale.
  `git fetch origin <branch>` then pin:

```bash
git push --force-with-lease=refs/heads/<branch>:<known-remote-sha> \
  origin <branch>
```

(sha from `git ls-remote`).

- **`gh pr view --json commits` lags after force-push** (eventual consistency).
  Verify the branch tip with `git ls-remote origin refs/heads/<branch>` — it
  must equal your local HEAD.
- **Duplicate issues**: when a PR links a newer issue that duplicates an older
  one, relink the PR to the OLDER canonical issue (`gh pr edit ... --body-file`)
  and close the newer with
  `gh issue close <dup> --reason duplicate --comment "Doublon de #<canon>"`.
