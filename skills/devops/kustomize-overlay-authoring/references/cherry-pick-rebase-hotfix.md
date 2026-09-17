# Escaping a corrupted rebase via cherry-pick

Observed 2026-09-01 during rebase of `realign-tailscale-hostnames` onto
`origin/main`. 18 commits, 18 conflicted files. `.git/rebase-merge/git-rebase-todo`
got corrupted — all `drop` lines concatenated into one, leaving `pick` lines
orphaned. `git rebase --continue` failed with "fatal: expected label onto/reset onto".

## Root cause

Editing `.git/rebase-merge/git-rebase-todo` in Python via heredoc
(`python3 -c '...'`) silently corrupted multi-line file contents when the
search/replace pattern matched and replaced within a single string
passed to `sh -c` heredoc — the resulting file had all `drop` lines merged into
a single line, dropping newlines. The file looked valid to `git rebase` but
contained only two lines (both were continuation lines) where it needed many.

Reproduced: replacing the `drop` lines in the rebase-todo file inside the
`git-rebase-todo` file's quoted heredoc produced a corrupted file because the
search pattern itself was embedded in the same quoted context.

## Recovery

1. `git rebase --abort` — exits cleanly to the pre-rebase state (HEAD = `fb02f70ef`).
2. `git stash` — shelves any uncommitted working-tree changes.
3. `git checkout main && git checkout -B realign-tailscale-hostnames origin/main` —
   resets to `origin/main` with a clean HEAD, erasing the rebase state entirely.
4. Cherry-pick each commit individually: `git cherry-pick <sha>`.
   - When conflicts arise: resolve inline (`sed`/`patch` for conflict markers,
     `git add` resolved files), then `git cherry-pick --continue`.
   - For files needing merge-conflict resolution across commits (e.g.
     `envoyproxy.yaml` appearing in 3 successive commits): `sed` may fail on
     heredoc content (`<<<<<<<` in proxy config fields). Use Python `re` module
     via `execute_code` instead.
   - Some commits carry "soft" changes that land cleanly (no conflicts) — they
     become trivial fast-forwards.
5. After cherry-picking all commits, verify with `git diff origin/main --stat`:
   the diff shows only the intended files. Any commit whose changes are already
   in `origin/main` (non-authorial commits carried along) disappears from the
   diff. Those shas should be noted for future branch operations.
6. `git push --force-with-lease origin realign-tailscale-hostnames`.

## Result

8 commits cherry-picked cleanly. 6 commits from the original branch
dropped (non-tailscale changes: lldap web UI consolidation, flux-operator
UI gateway docs, treefmt). Result: 264 files changed (34 files per cherry-
pick commit), zero merge conflicts, zero `taila659a.ts.net` references.

## Key differences from interactive rebase

| Aspect | rebase | cherry-pick hotfix |
|--------|--------|-------------------|
| Conflict state | All files in one batch | One file at a time |
| `git status` output | 30+ files, many U/M/UU | 2-5 files |
| Abort cost | High — re-read whole conflict set | `git rebase --abort` (1 command) |
| Commit visibility | Rewritten shas, squashed commits | Original shas preserved |
| Drop handling | Manual `.git/rebase-todo` edits | Implicit — if a commit has no diff, it vanishes from `git diff` |

## Gotchas

- **`git cherry-pick --skip` does not exist.** Unlike rebase, there is no skip
  command. When a conflict cannot be resolved, `git cherry-pick --continue`
  always fails. Options: (a) resolve inline and continue, (b) abort and
  re-apply later, or (c) use `git commit --amend` to fix the current
  cherry-pick's commit content, then resume the chain.
- **Force push is `git push --force-with-lease`, not `--force`.** `--force-with-lease`
  refuses if someone else pushed to the branch since the last fetch. Use
  `git fetch origin && git push --force-with-lease` to refresh the lease.
  `--force` can clobber a collaborator's changes.
- **Working tree must be clean before `git checkout -B`.** Any uncommitted
  changes are lost. Stash them first. `git stash && git checkout -B <branch> origin/main`.
