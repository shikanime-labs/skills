# Push a patch on a branch — safe minimal-split procedure

When asked to "push a patch on a branch," split unrelated edits FIRST — and
PROVE the split is minimal before pushing. The console tree is jj-backed (not
raw git) and often holds multiple unrelated in-flight working-tree changes. The
observed failure: splitting via `git apply` of a saved fix patch left the fix
commit polluted with unrelated WIP (a 2-file fix shipped as 7 files to PR #2526)
because the saved patch was diffed against a tree that already had the fix mixed
in. The only safe sequence rebuilds the fix from a clean `main` and verifies its
file set before publishing:

1. Save the user's FULL in-flight WIP so nothing is lost:
   `jj diff > /tmp/wip.patch` (capture any untracked files separately).
2. Reset the working copy to a clean `main` (disk now matches `main`, all WIP
   off disk): `jj restore --from main --to @`.
3. Create an empty child of `main` for the fix: `jj new main -m "fix(...)"`.
4. Apply ONLY the intended change by hand-editing the target file(s) with
   `patch`/`write_file` — do NOT `git apply` a mixed patch. Touch only the files
   the fix needs.
5. **VERIFY THE COMMIT IS MINIMAL before any push:** `jj commit -m "fix(...)"`,
   then `jj diff -r <commit> --stat` — the file list must be EXACTLY the
   intended files, and `jj diff -r <commit> | grep -cE "unrelated-token"` must
   be 0. If extra files leaked in, the split failed; do not push. This check
   would have caught the 7-file leak that reached PR #2526 in one session.
6. Re-point the bookmark to the clean commit:
   `jj bookmark set fix/<topic> -r <commit>` (if the target is an ANCESTOR of
   the bookmark's current position, jj refuses as "backwards" — add
   `--allow-backwards`; the working copy and WIP are untouched).
7. Push only to origin: `jj git push --bookmark fix/<topic> --remote origin`.
8. Restore the user's WIP to the working tree:
   `jj restore --from <saved-wip> --to @` (or apply `/tmp/wip.patch` by hand
   with `patch`/`write_file`). If the fix and WIP touched the SAME file(s), the
   full patch won't apply (it was diffed against the pre-fix baseline) — split
   it to exclude the fix's files: drop the affected hunks whose path matches the
   fix's files with a small `python3` regex and apply the rest. Never bundle
   unrelated work into one PR. After any raw file write outside jj, jj's
   snapshot lags until you `touch` the file — `jj squash` then reports "Nothing
   changed" and `jj diff` shows nothing. Full recovery:
   `references/jj-snapshot-pitfalls.md`.
