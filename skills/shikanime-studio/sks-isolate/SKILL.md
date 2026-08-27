---
name: sks-isolate
description:
  Use when isolating one unit of shikanime work in a fresh jj workspace so
  concurrent editors / WIP never get folded in — bookmarks and pushes are scoped
  to that single workspace.
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - jj
      - workspace
      - isolation
      - shikanime-labs
      - shikanime-studio
    related_skills:
      - sks-dev-workflow
      - sks-async
      - sks-commit
      - sks-pr-workflow
      - sks-gc
platforms:
  - linux
  - macos
  - windows
---

# Shikanime Org Work Isolation

Open a fresh `jj` workspace for ONE unit of work so an in-flight working folder
(full of other editors' WIP you must not touch) never folds your change into the
wrong commit. This is the single-stream primitive behind `sks-async`'s per-unit
fan-out and the isolation lane of `sks-dev-workflow`.

## When to Use

- "Work on X in isolation / a clean workspace."
- The checkout you're in has concurrent uncommitted WIP you must not lose or
  mix.
- One unit only — for N parallel units, use `sks-async`.

## Procedure

1. **Snapshot any WIP you must preserve** (outside the isolation dir), then open
   the workspace off a clean rev:

   ```bash
   cd ~/Source/Repos/github.com/<orga>/<repo>
   mkdir -p /tmp/wip-isolate
   for f in <WIP files>; do
     cp "$f" "/tmp/wip-isolate/$(echo "$f" | tr '/' '__')"
   done
   jj workspace add ../<repo>-<unit> -r 'main@origin' && cd ../<repo>-<unit>
   ```

   `<unit>` is a short slug for this work (`fix`, `feat-x`). Prefer this over
   `jj restore`/`jj split` to peel subsets — those can drop the sibling WIP.

2. **Copy in ONLY your change files**, then commit per `sks-commit`:

   ```bash
   jj add <change files>
   jj describe -m "<subject>" -m "Co-authored-by: Automata
   <automata@shikanime.studio>"
   ```

3. **Bookmark + push** (jj does not auto-track — `track` is mandatory):

   ```bash
   jj bookmark create <branch> -r @
   jj bookmark track <branch> --remote=origin
   jj git push --remote origin -b <branch>
   ```

4. **Hand off to `sks-pr-workflow`** to open the PR (`--head <org>:<branch>`,
   base `main`, `Related:` full issue URL; run its step 2b duplicate/stack check
   first — skip the PR if one already exists, stack if yours must sit on top).
   Do NOT merge here.

## Pitfalls

- `jj workspace add` without `-r` parents the new workspace on the current `@`
  (possibly dirty) — always pin `-r 'main@origin'`. Only override with an
  explicit `-r '<other-base>@origin'` when stacking on a non-trunk base; never
  inherit the local `main` (it can be stale).
- Forgetting `jj bookmark track` makes `jj git push` reject the bookmark.
- The new dir (`../<repo>-<unit>`) is a SIBLING of the repo root, not inside it;
  `sks-gc` reclaims it after landing.
- Don't `rm -rf` the isolation dir while it holds uncommitted work — that is WIP
  loss. Retire via `sks-gc`.

## Verification

```bash
jj workspace list                       # new <repo>-<unit> present, clean
jj status && jj log -r @ -T 'bookmarks'
gh pr view <N> --repo <org>/<repo> --json state,headRefName   # after PR step
```

## See also

- `sks-dev-workflow` — full loop; this skill is its isolation lane.
- `sks-async` — fan-out; each stream uses this same workspace recipe.
- `sks-pr-workflow` — open the PR from the pushed bookmark.
- `sks-gc` — reclaim the workspace/bookmark once landed.
