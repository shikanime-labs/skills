---
name: sks-delegate
description:
  Use when isolating one unit of work in a fresh jj workspace — the mandatory
  entry to implementation for every unit, so concurrent WIP never folds in
  and bookmarks/pushes stay scoped.
version: 0.3.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - jj
      - workspace
      - isolation
    related_skills:
      - sks-dev
      - sks-async
      - sks-commit
      - sks-pr-workflow
      - sks-gc
platforms:
  - linux
  - macos
  - windows
---

# Stack Isolation

Open a fresh `jj` workspace for ONE unit of work. This is **mandatory for every
implementation unit** — not only when WIP is present — so an in-flight working
folder (full of other editors' WIP you must not touch) never folds your change
into the wrong commit, and so the working surface is always isolated and
reproducible. This is the single-stream primitive behind `sks-async`'s per-unit
fan-out and the isolation lane of `sks-dev`.

For shikanime-org specifics (repo layout, co-author trailer), read
`references/shikanime.md` when operating in a shikanime org. For
cloud-pi-native specifics (console checkout path, the default reviewer, French
artifacts, `Refs #N`), read `references/cloud-pi-native.md` when working in
the cloud-pi-native/console repository.

## Mandatory

Every implementation unit runs in a fresh `jj` workspace created by this skill —
never in the cloned checkout. `sks-dev` inherits this requirement; the
checkout is a read-only reference surface. A unit that skips `sks-delegate`
has not entered the dev loop.

## When to Use

- Every implementation unit of the target org — even on a clean checkout. This
  is not an
  isolation escape hatch for WIP; it is the default working surface (Phase 3 of
  `sks-dev`). The cloned checkout is never where edits are made.
- A checkout holding concurrent uncommitted WIP you must not lose or mix.
- One unit only — for N parallel units, use `sks-async`.

## Procedure

1. **Snapshot any WIP you must preserve** (outside the isolation dir), then open
   the workspace off a clean rev:

   ```bash
   cd <repo checkout>   # org path layout per references/shikanime.md
   mkdir -p /tmp/wip-isolate
   for f in <WIP files>; do
     cp "$f" "/tmp/wip-isolate/$(echo "$f" | tr '/' '__')"
   done
   jj workspace add ../<repo>.<unit> -r 'main@origin' && cd ../<repo>.<unit>
   ```

   `<unit>` is a short slug for this work (`fix`, `feat-x`). Prefer this over
   `jj restore`/`jj split` to peel subsets — those can drop the sibling WIP.

2. **Copy in ONLY your change files**, then commit per `sks-commit` (org
   co-author trailer — value per `references/shikanime.md`):

   ```bash
   jj add <change files>
   jj describe -m "<subject>" -m "<co-author trailer>"
   ```

   Isolation created = the unit is being worked: set the issue's board card
   to `In progress` (`sks-project`) right after this step.

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
  (possibly dirty) — always pin `-r 'main@origin'` so the workspace forks from
  the remote tip, never stale local main.
- Forgetting `jj bookmark track` makes `jj git push` reject the bookmark.
- The new dir (`../<repo>.<unit>`) is a SIBLING of the repo root, not inside it;
  `sks-gc` reclaims it after landing.
- Don't `rm -rf` the isolation dir while it holds uncommitted work — that is WIP
  loss. Retire via `sks-gc`.
- `gh pr create` failing with "a pull request already exists" on your head
  bookmark is not an error to work around: your push already stacked onto that
  PR. Verify `gh pr view <branch> --json headRefOid` equals local `@`, then
  document the delta in a PR comment instead of opening a duplicate.
- `git show`/`git ls-remote <remote>` fail in jj workspaces (git CLI does not
  see jj remotes or the shared store). Use `jj file show -r <commit> <path>`
  for file content and `git ls-remote <repo-url>` for push verification.
- Unit targeting an in-flight PR (not a fresh branch): pin the workspace to
  the PR's bookmark (`jj workspace add ../<repo>.<unit> -r <pr-branch>`),
  commit on top, then `jj bookmark move <pr-branch> --to @-` + push — a
  fast-forward ride on the existing PR; never open a duplicate PR. Read
  target files at the PR head (they may diverge from main).
- Validate GitHub issue-form YAML with the repo's own toolchain instead of
  hunting for a Python yaml module: `node -e` + `require.resolve('js-yaml',
  { paths: ['./node_modules/.pnpm/node_modules'] })` in a pnpm monorepo.

## Verification

```bash
jj workspace list                       # new <repo>.<unit> present, clean
jj status && jj log -r @ -T 'bookmarks'
gh pr view <N> --repo <org>/<repo> --json state,headRefName   # after PR step
```

## See also

- `sks-dev` — full loop; this skill is its stack isolation lane.
- `sks-async` — fan-out; each stream uses this same workspace recipe.
- `sks-adversarial` — disposable sandbox; composes this skill + `sks-async`.
- `sks-investigate` — root-cause discipline; use before isolating a fix.
- `sks-pr-workflow` — open the PR from the pushed bookmark.
- `sks-gc` — reclaim the workspace/bookmark once landed.
