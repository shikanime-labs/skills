---
name: sks-gc
description:
  Use when reclaiming resources leaked by shikanime jj workflows: dangling
  bookmarks, skill-created jj workspaces, and leftover working-copy dirs from
  sks-async/sks-dev-workflow.
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - jj
      - gc
      - cleanup
      - workspaces
      - bookmarks
      - shikanime-labs
      - shikanime-studio
    related_skills:
      - sks-async
      - sks-dev-workflow
      - sks-land
platforms:
  - linux
  - macos
  - windows
---

# Shikanime Org Workspace Garbage Collection

Reclaim resources leaked by the parallel/migration skills: `jj` bookmarks with
no open PR and not on `main`, `jj` workspaces the skills created
(`<repo>.<unit>`, `<repo>-fix`), and the sibling working-copy directories they
leave on disk. Destructive — always dry-run first.

## When to Use

- After a finished or stalled `sks-async` fan-out or `sks-dev-workflow`
  isolation pass: workspaces and bookmarks pile up.
- "Clean up my dangling branches / orphan jj workspaces."
- Periodic hygiene on a repo worked across many parallel streams.

## Hard rules (do not skip)

- **Dry-run first.** Print every candidate; never `forget`/`rm` on the same
  pass that discovers it. Require an explicit apply step after review.
- **Never drop `main` / `trunk` / `master`** or a bookmark with an OPEN PR.
- **Never forget a workspace with uncommitted changes.** Skip it and report —
  losing WIP is data loss.
- Operate in the repo root (`~/Source/Repos/.../<repo>`); the canonical
  workspace (named after the repo, no unit suffix) is NEVER a candidate.

## Procedure

1. **Baseline.**
   ```bash
   cd ~/Source/Repos/github.com/<orga>/<repo>
   jj workspace list                          # name | path | revision
   jj bookmark list                           # local + remote-tracking
   gh pr list --state open --json number,headRefName   # protected branches
   ```

2. **Identify dangling bookmarks** — reachable from nowhere on trunk and with no
   open PR:
   ```bash
   # candidates: bookmarks NOT ancestors of main
   jj bookmark list -r 'bookmarks() & ~::main'
   ```
   Drop any name in the `gh pr list` set and any trunk name. Remaining =
   dangling.

3. **Identify skill workspaces** — those the skills created, named
   `<repo>.<unit>` (dot-qualified) or `<repo>-fix`:
   ```bash
   jj workspace list --color never \
     | awk -F'\t' '$1 ~ /\./ || $1 ~ /-fix/ {print $1, $2}'
   ```
   Exclude the bare repo-name workspace. Guard each candidate against dirty WIP:
   ```bash
   jj -R <path> status --color never | grep -q 'has no changes' \
     || echo "SKIP $name (dirty working copy)"
   ```

4. **Prune remote-tracking bookmarks no longer on origin** (safe, built-in):
   ```bash
   jj git fetch --prune --remote origin
   ```

5. **Apply** (only after review) — forget dangling bookmarks and clean
   workspaces:
   ```bash
   jj bookmark forget <dangling...>
   jj workspace forget <name...>       # already confirmed clean
   rm -rf <path>                        # ONLY the sibling dir from step 3
   ```

6. **Verify.**
   ```bash
   jj workspace list && jj bookmark list
   gh pr list --state open
   ```

## What "resources from other skills" covers

- `sks-async` → one `jj workspace add ../<repo>.<unit>` per stream, a bookmark
  per link, and `gh stack` branches on `origin`.
- `sks-dev-workflow` → `jj workspace add ../<repo>-fix` isolation dirs and
  `/tmp/wip*` scratch copies (the latter are manual — list, but never auto-`rm`
  without asking).
- `gh stack` chains → branch bookmarks on `origin`; cleared by forgetting the
  bookmark plus `jj git fetch --prune` (step 4).

## Pitfalls

- `jj workspace forget` does NOT delete the on-disk directory — `rm -rf` it
  yourself after confirming it is the sibling skill dir, never the repo root.
- A dirty workspace skipped by the guard means real WIP; surface it, do not
  force.
- Remote-tracking bookmarks (`origin/...`) need `--prune` (step 4), not
  `bookmark forget`, to clear.
- The canonical workspace (bare repo name, no dot/`-fix`) is never a candidate;
  don't fold the trunk working copy into GC.

## See also

- `sks-async` — the fan-out that creates the workspaces/bookmarks this skill
  reclaims.
- `sks-dev-workflow` — isolation workspace pattern
  (`../<repo>-fix`).
- `sks-land` — lands PRs (this skill only reclaims after landing, never merges).
