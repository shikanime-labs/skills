# jj / git interop pitfalls (cloud-pi-native console)

The console repo is **jj-backed**. Raw `git` commands (git apply, git checkout,
git diff) drive the working tree, but jj owns the commit graph. Mixing them
produces snapshot desync that looks like lost or phantom edits. This file is the
proven recovery sequence from a session that rebuilt two PR-2529 commits after a
tangled jj/git state.

## Symptoms you will see

- `git apply <patch>` writes files, but `jj diff` shows nothing until you
  `touch` the files. jj's file monitor missed the change.
- `jj squash --into @` prints `Nothing changed.` yet `jj diff -r @` now shows
  the content. The message lies; the re-snapshot succeeded.
- `jj squash` (no `--into`) fails: `Commit d55564f6 is immutable` — it tried to
  fold into the parent (`main`), which is immutable.
- `jj squash`/`jj split` without `--config ui.editor=cat` launches `hx` and
  panics: `thread 'main' panicked ... reader source not set` (editor step).
- `jj diff -r A -r B` is **invalid syntax** in this jj version (errors). Use
  `jj diff -r A` (one-sided, vs parent) or `jj log -p -r A`.
- `jj bookmark move <name> -t @` fails: `The target ... is not a descendant`
  when the move is sideways (sibling commits).
- `jj git push --bookmark <name>` refuses:
  `Refusing to create new remote bookmark <name>@origin` — the name already
  exists on the remote (`origin`).

## Recovery sequence (proven)

1. Apply or revert via raw git:
   - apply fix: `git apply /tmp/fix.patch`
   - revert unrelated file: `git checkout main -- <paths>`
   - capture unrelated edits first: `git diff main -- <paths> > /tmp/x.patch`
2. **Force jj re-snapshot**: `touch <changed-files>` (this is the key step jj
   skips after raw git writes).
3. Fold into a child you own: `jj squash --into @ --config ui.editor=cat`. Use
   `jj new main -m "fix(...)"` first if `@` is not an empty child of main.
4. **Verify with `jj diff -r @`** (grep for a known token). Do NOT trust the
   squash stdout message.
5. Bookmark + push:
   - sideways move: `jj bookmark set <name> -r @ --allow-backwards`
   - push to the org remote (`origin`):
     `jj git push --bookmark <name> --remote origin`. If `<name>@origin` already
     exists, re-point it first (`jj bookmark move <name> -t @`) so the push
     updates the existing remote bookmark instead of conflicting.

## Splitting two fixes out of one working tree

Goal: fix A and fix B as sibling children of `main` (jj diamond), each its own
PR/bookmark.

1. `git diff main -- <unrelated-paths> > /tmp/unrelated.patch` (preserve user's
   other in-flight edits — do NOT bundle them into the PR).
2. `git checkout main -- <unrelated-paths>` to clear them from the tree.
3. For each fix: `jj new main -m "fix(...)"` → `git apply /tmp/<fix>.patch` →
   `touch <files>` → `jj squash --into @ --config ui.editor=cat` → verify
   `jj diff -r @`.
4. `jj bookmark set fix/<topic> -r @` per commit.
5. `jj git push --bookmark fix/<topic> --remote origin` for each.
6. Restore user's unrelated edits: `git apply /tmp/unrelated.patch`.

## Verification idiom

After any jj operation on this repo, confirm content with `jj diff -r <rev>`
(count a known token), not `git diff` alone and never the squash message. The
working-tree `git diff main` can lag jj's snapshot by one operation.
