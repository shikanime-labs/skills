# jj recovery recipes (shikanime checkouts)

Verified patterns for the jj-managed checkouts under
`~/Source/Repos/<host>/<orga>/<repo>`. The checked-out git working copy is
jj-controlled: git `main`/`HEAD` refs can lag `origin/main`, and a foreign WIP
commit may already sit under `@`.

## Committed directly to protected `main`

`manifests` `main` is ruleset-protected (see Branch discipline) — direct push is
rejected. If a commit lands on local `main` before branching, move it to a
branch and reset `main` to `origin/main`:

```bash
git branch <branch> HEAD                 # snapshot the stray commit
git reset --hard origin/main             # local main back to trunk
jj bookmark create <branch> -r <branch>  # jj auto-imports the git branch
jj bookmark track <branch> --remote=origin
jj git push --remote origin --bookmark <branch>
# open PR --head <org>:<branch>; land via gh pr merge --squash --admin
```

Never `git push origin main` — protected. Land through the PR.

## Stray edit landed on a foreign WIP commit

If `@` already sits on someone else's (or a prior session's) WIP commit, an edit
you make gets entangled with their work. Extract ONLY your edit without
orphaning theirs:

```bash
# revert your edit back to the WIP parent
jj restore --to @ --from @- <file>
# fresh isolated change off main@origin (PIN the hash)
jj new -m "<your subject>" <fixed-main-hash>
# re-apply your edit in the clean WC, then commit/branch/push as normal
```

Pin the parent to a fixed `main@origin` hash so a background `jj git fetch`
can't clobber the working copy (see "Stale working-copy clobber" in SKILL.md).
The WIP parent (e.g. `88e3e876`) stays intact on its bookmark.

## `jj describe -F` does not exist

`jj describe -F <file>` errors with a bare "Usage:" in jj 0.44 — there is no
`-F` (file) flag. The file-based form is `jj describe --stdin < <file>` (reads
the message from stdin; multi-line bodies with trailers are safer via a file,
same reason gh `--body-file` beats inline `--body`). Verified 2026-09-04.
Also: passing `-r @` before `--stdin` works, but bare `jj describe --stdin`
(default rev `@`) is sufficient in a single-change workspace.

## `jj checkout` does not exist

This jj version has no `jj checkout` subcommand (errors "unrecognized
subcommand 'checkout'"). To move the working copy back onto a bookmark/branch,
use git:

```bash
# switches the underlying git branch; jj re-imports it
git checkout <bookmark>
```

`jj add` is also absent — use `jj file track` for new files only; tracked files
need no staging (see the SKILL.md note).

## `git ls-files` reflects the stale checked-out tree

In a jj checkout the git index tracks the *checked-out* commit, which can lag
`origin/main` after a reset/fetch. A removal merged upstream can still appear in
`git ls-files`, giving a false "not removed" reading. Verify against the merged
commit tree instead:

```bash
git fetch origin
git reset --hard origin/main            # resync the local checkout first
git ls-tree -r --name-only <merge-commit> | grep -i <path> || echo "absent in tree"
git diff --stat <merge-commit>^ <merge-commit>
```

Trust the merged-tree view, not `git ls-files`, when proving a deletion landed.

## Rebase an open PR onto moved main (single recipe, verified on #2048 → #2049)

```bash
jj git fetch --remote origin
jj rebase -d main@origin -r @          # -r @ works: @ is the change, not the bookmark
# resolve conflicts (jj status lists 2-sided conflict paths; edit files directly)
jj restore --from main@origin --to @ <files whose main version should win outright>
# rewrites + re-points bookmark; commit-msg hook re-runs
jj describe -m "<same description>"
jj git push --remote origin -b <branch>   # "move sideways" — no force needed
# headRefOid must equal `jj log -r @ -T commit_id`
gh pr view <n> --json state,headRefOid,mergeable
```

Collision triage before resolving: `jj diff -r <new-main> --stat` vs your own
diff. If main landed content you were ALSO adding, DROP your duplicate
(`jj restore --from main@origin` on that file) rather than keeping both.
Stale-version collision: when main's version of your file is OLDER than
yours (main STRIPPED it back), KEEP YOURS — verify by reading both versions;
if main's is an ancestor of yours, yours is correct.

## Squash into an already-pushed `@` is refused — the edits are already there

`jj squash -r @` fails with "would rewrite N immutable commits" once `@` is
a published bookmark — even when the working-copy changes are not yet
committed. The working-copy edits already live on `@`; no fold needed:

```bash
jj diff -r @ --stat          # confirms the new edits are already part of @
jj sign -r @                 # rebase/describe rewrites drop signatures
jj bookmark set <branch> -r @
jj git push --remote origin -b <branch>
```

## Stale working-copy clobber under a moving bookmark

When the workspace parent is a moving bookmark (`main@origin`), a background
`jj git fetch` advancing it makes every MUTATING op (`jj commit`, `jj
snapshot`, `jj file track`) auto-update-stale the WC and re-materialize
tracked files from the new parent — discarding OS-level edits made between
calls. The read-only `jj workspace update-stale` does the same on itself.

Escape that WORKED: PIN to a fixed hash, edit AFTER the pin, and commit in
the SAME shell call as the edit:

```bash
# PIN — a fixed-hash parent has no bookmark to follow
jj new <current-main@origin-tip-hash>
# ... write the files, then in ONE call:
jj commit -m "..."
```

- Do NOT use `jj workspace add -r <hash>` as the fix — it pollutes the new
  WC (phantom "Added 904 files") and still reverts.
- Do NOT interleave `jj git fetch` / `jj new` / `update-stale` between
  writing a file and committing — one reconcile wipes uncommitted edits.
- `jj commit` leaves `@` as an EMPTY child; the real commit is `@-`'s
  parent. Verify with `jj diff --stat -r <commit-id>` (not `-r @`).
- After ANY `update-stale`, re-read the key edited files before
  describing/committing — `jj status` "no changes" can mean REVERTED, not
  clean. Treat `update-stale` as a barrier: finish all edits first, or run
  it only on a clean WC.

## Mine a reverted diff before discarding it

A landed revert does not mean the reverted work was worthless. Triage each
reverted hunk: generic (kernel modules, services, image packaging) vs
host-specific (SOPS, tailscale, openssh, per-machine TPM/LUKS), then
backport the generic parts into the shared module (`modules/...`) — but
HARD-CODE the fixed config rather than exposing `mkOption` extension
points. Verified on `containerdisk.nix`: the user stripped every speculative
option (`kernelModules`, `extraPackages`, `usb.enable`, `machineInfo.enable`,
`cloudInit.enable`) in favor of inlined constants; the module kept only
`name` + `settings` passthrough. Opinionated template beats configurable
library. Before re-implementing a reverted service, check what NixOS already
provides natively (`disk-image.nix` ships `boot.growPartition`; timesyncd is
on by default). Verify the backport: `nix build .#packages.<system>.<name>
--dry-run` must eval the full graph with zero errors; parse + `treefmt` the
module before pushing.

## Workspace dir vanishes mid-task (disk-full purge) — commit survives

The host disk can hit 100% mid-session and macOS (or cleanup sweeps) purge
whole workspace directories (`~/Source/Repos/manifests-<unit>` gone; hit
TWICE in one session 2026-09-03). Do not panic — the jj repo store is shared:
the commit (by change-id) lives in the main checkout's `.jj`, so nothing
authored+described is lost. Recovery (verified):

```bash
cd <main-checkout>                          # the surviving jj repo
jj log -r '<change-id-prefix>'              # confirm the commit survived
jj workspace forget <name> 2>/dev/null      # drop the stale workspace entry
jj workspace add <same-or-new-path> -r <change-id>   # re-materialize the tree
```

Then continue work in the recreated dir. Gotchas:

- Any `/tmp` scratch (decrypted plaintext, `.sops.yaml`, encrypt scripts) is
  GONE — keep decrypted artifacts under `/tmp` only transiently and expect to
  re-derive them from the committed encrypted file (decrypt again).
- Divergence: if you re-`jj squash`ed into the change from a lost copy earlier,
  the change-id may be divergent (`rusxlqky/0`, `/1`). Resolve with
  `jj bookmark set <b> -r <change>/<N> --allow-backwards` then
  `jj abandon <other-N>`; always re-verify the surviving commit's content
  (`jj file show -r <change> <file> | decrypt ...`) before pushing.
- After recreation, the git mirror may be stale: `jj git export` before any
  direct `git -C <main>/.git push` (see SKILL.md silent-push no-op section).
- Prevention: watch `df -h /` when jobs write big caches; prune
  `~/.cache/{pnpm,uv}` (`pnpm store prune`, `uv cache prune`) — freed 3G+
  in-session. Never clean `/private/tmp/<sibling-*>` dirs (other agents' WIP).
- The credential-helper gotcha after nix GC: if git pushes fail with
  "could not read Username", the pinned `gh` store path was garbage-collected;
  pass `-c credential.helper="$(command -v gh) auth git-credential"` and
  re-export jj state first (`jj git export`).

## Verifying push landing inside an isolation workspace (no `.git`)

`git ls-remote origin` fails in a `jj workspace add` sibling ("'origin' does
not appear to be a git repository" — the workspace carries no git remote
wiring), and `gh` fails there too ("not a git repository"). Two verified
alternatives:

```bash
jj git push --remote origin --bookmark <branch> --dry-run
# "Bookmark <branch>@origin already matches <branch>" + "Nothing changed." → landed
# must equal `jj log -r @ -T commit_id`
gh api repos/<org>/<repo>/branches/<branch> --jq .commit.sha
```

"move sideways from X to Y" in the real push output is the affirmative
signal; "Nothing changed" on the dry-run means the remote already matches —
do not retry the push.

## jj version quirks (this build)

- `jj workspace add` takes NO `--git` flag — git-backed by default in a
  colocated repo. Plain `jj workspace add -r main@origin <dir>` works. A
  workspace added from OUTSIDE the repo needs `jj -R <repo-path> workspace
  add <dest>`; run follow-up commands from INSIDE the new workspace dir.
- `jj git fetch` takes NO positional remote arg — `jj git fetch origin`
  errors `unexpected argument 'origin'`. Use plain `jj git fetch`.
- `jj bookmark forget <name>@origin` errors `Invalid string expression`. To
  drop a deleted remote bookmark, just run `jj git fetch` — it reports
  `bookmark: <name>@origin [deleted] untracked` and cleans it up.
- `jj add` does not exist — edited files already tracked in the parent are
  auto-included in the working-copy commit; only NEW untracked files need
  `jj file track <path>`. (Where a skill says `jj add`, ignore it.)
- `jj describe -F <file>` does not exist — use `jj describe --stdin <
  <file>` for multi-line bodies with trailers.
- `jj checkout` does not exist — `git checkout <bookmark>` instead; jj
  re-imports the moved git branch.
- Resolve a commit by short change-id prefix directly:
  `jj log -r '<prefix>'`. Grep `jj log -T` if the exact rev does not resolve.
- `committer()` does not exist in the template language — use `author.*`
  fields, or `git log -1 --format='%cn <%ce>'` from the original checkout.
