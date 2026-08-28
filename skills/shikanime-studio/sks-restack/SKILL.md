---
name: sks-restack
description:
  Use when rebasing a shikanime jj stack onto moved main leaves conflicts —
  restack, then resolve each conflicted revision with edit/resolve until
  pushable.
version: 0.2.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - jj
      - rebase
      - conflicts
      - restack
      - shikanime-labs
      - shikanime-studio
    related_skills:
      - sks-converge
      - sks-dev-workflow
      - sks-stack
      - sks-async
      - sks-gc
platforms:
  - linux
  - macos
  - windows
---

# Shikanime Org jj Restack + Conflict Resolution

Rebase a jj stack (bookmarked commits above `main`) onto a moved trunk, then
resolve every conflict the move produced. `jj restack` in these environments is
an alias — `jj config get aliases` shows
`restack = ["rebase", "--onto", "trunk()", "--source",
"roots(trunk()..) & mutable()", "--simplify-parents"]`
— so it rebases all mutable roots onto trunk. Where the alias is undefined,
the scoped equivalent is `jj rebase -b <branch> --onto main@origin` per
bookmark. This skill covers the full loop: restack → resolve → push.

## When to Use

- Trunk moved (squash-landed PR, cascading rebase) and your stack must follow:
  "restack and resolve the conflicts".
- "Rebase my jj stack onto main and fix the conflicts."
- Post-restack `jj git push` fails `Won't push commit ... since it has
  conflicts` — come here before improvising.
- Multi-link stacks: resolve bottom-up so each fix's parent stays stable.

## Prerequisites

- jj repo (`.jj/`); the stack's bookmarks exist (`jj bookmark list`).
- Trunk is current: `jj git fetch --remote origin` first, or you restack onto
  a stale `main@origin`.

## Procedure

1. **Baseline.**

   ```bash
   cd ~/Source/Repos/github.com/<orga>/<repo>
   jj git fetch --remote origin
   jj bookmark list && jj log -r 'trunk()..mutable()' --limit 15
   ```

   Completion: bookmark set known; every stack rev visible.

2. **Restack.** Alias when defined, else scoped per bookmark:

   ```bash
   jj config get aliases | grep -q restack \
     && jj restack \
     || jj rebase -b <branch> --onto main@origin
   ```

   Rebase auto-moves bookmarks — confirm with `jj bookmark list` after.
   Completion: no "skipped" lines for your revs.

3. **Converge via `sks-converge`.** Resolving conflicts (and any divergence
   the fetch reveals) is that skill's reusable loop: locate with
   `conflicts()` / `divergent()`, resolve per revision, repoint bookmarks.
   Load `sks-converge` and follow it; do not re-derive resolution here.

4. **Return to your working copy** if `sks-converge` moved `@` (its Procedure
   A step 3): `jj edit <original @ change-id>`.

5. **Push gate.** `sks-converge` exits pushable; re-assert here:

   ```bash
   jj log -r 'conflicts()' --no-graph   # MUST print nothing
   jj git push --remote origin -b <branch>
   ```

   A restacked bookmark already on origin is rewritten non-FF: the push output
   reads `[move sideways from <old> to <new>]` — expected shape, not an error.
   On this host push with
   `--config signing.behavior=drop --config git.sign-on-push=false` (key in no
   agent); GitHub squash-merge re-signs server-side.

6. **Hand off.** Rewritten stack PRs land via `sks-land` / `sks-pr-workflow`;
   leftover `(empty)` revs and stale workspaces are `sks-gc` territory.

## Pitfalls

- **Marker dialect, `jj resolve --list` limits, `jj edit` re-parenting** —
  all resolution mechanics live in `sks-converge`; load it rather than
  improvising.
- **Push rejects conflicts.** `Won't push commit ... since it has conflicts`
  is the gate doing its job; resolve, never bypass.
- **`[move sideways from X to Y]`** on push = bookmark moved non-FF by the
  restack; expected for an already-pushed branch.
- **Stale trunk.** Restacking without `jj git fetch` rebases onto old
  `main@origin` — wasted resolution work.
- **Shared working copy.** The alias's `roots(trunk()..) & mutable()` restacks
  every mutable root, including other sessions' WIP; with concurrent editors,
  prefer the scoped `jj rebase -b <branch> --onto main@origin`.

## Verification

```bash
jj log -r 'conflicts()' --no-graph           # empty
jj status                                    # @ restored, no stray M files
jj bookmark list                             # bookmark on the rewritten rev
jj git push --remote origin -b <branch>      # accepted, no conflict rejection
```

## See also

- `sks-converge` — the reusable conflict/divergence resolution loop this
  skill hands off to after the rebase.
- `sks-dev-workflow` — the landing gates this feeds; never force-push stack
  branches.
- `sks-stack` — isolate before resolving when the main checkout is crowded.
- `sks-async` — multi-link stacks whose streams each need this loop.
- `sks-gc` — reclaim empty revs and stale isolation workspaces afterwards.
