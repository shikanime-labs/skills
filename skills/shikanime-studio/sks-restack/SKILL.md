---
name: sks-restack
description:
  Use when rebasing a shikanime jj stack onto moved main leaves conflicts —
  restack, then resolve each conflicted revision with edit/resolve until
  pushable.
version: 0.1.0
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

3. **Locate conflicts.**

   ```bash
   jj log -r 'conflicts()' --no-graph \
     -T 'change_id.short() ++ " | " ++ description.first_line() ++ "\n"'
   ```

   Empty output = no conflicts; jump to step 6. Note `jj resolve --list` only
   works on the working-copy commit — on other revs it errors
   `No conflicts found at this revision`; use the revset instead.

4. **Resolve each conflicted rev, oldest first.** Resolving a parent
   re-materializes its children's conflicts — re-run the locator between every
   rev, never trust the earlier list.

   1. Check out the rev:

      ```bash
      jj edit <change-id>
      ```

   2. Read the conflict. jj materializes it in the working-copy file in its
      own marker dialect — NOT classic git `<<<<<<<`/`>>>>>>>` markers:

      ```text
      alpha
      <<<<<<< conflict 1 of 1
      %%%%%%% diff from: rsmunysv "trunk base" (parents of rebased revision)
      \\\\\\\\\        to: ynvnqypp "trunk move" (rebase destination)
      -beta
      +BETA-trunk
      +++++++ ruunpwut "stack change" (rebased revision)
      BETA-stack
      >>>>>>> conflict 1 of 1 ends
      gamma
      ```

      Side map:

      - `%%%%%%% diff from:` block = the **destination** side — how moved
        trunk changed the file relative to the base.
      - `+++++++ <rev>` block = the **rebased revision** — your stack's own
        change, verbatim.
      - Lines outside the markers are shared context.

      Hand-merge when both changes must survive: keep the file's context,
      combine both intents, delete every marker line.

   3. For whole-side picks, skip hand-merging — the built-in tools map
      `:ours` = side #1 (destination, moved trunk) and `:theirs` = side #2
      (rebased rev, your change):

      ```bash
      jj resolve --tool :ours <file>    # keep the moved-trunk version
      jj resolve --tool :theirs <file>  # keep your stack's version
      ```

   4. Snapshot. Saving the file auto-snapshots into the checked-out rev:
      `jj status` shows `M <file>` under the resolved rev and the `(conflict)`
      tag disappears. `jj squash` is only needed when you resolved in a child
      of the conflicted rev instead of editing it directly.

   5. Re-scan: `jj log -r 'conflicts()' --no-graph` → resolve the next rev.

5. **Return to your working copy.** `jj edit` moved `@`; restore it before
   anything else snapshots into the stack rev:

   ```bash
   jj edit <original @ change-id>
   ```

6. **Push gate — zero conflicts.** `jj git push` hard-rejects conflicted
   commits (`Error: Won't push commit <id> since it has conflicts`), so the
   check is mandatory, not ceremony:

   ```bash
   jj log -r 'conflicts()' --no-graph   # MUST print nothing
   jj git push --remote origin -b <branch>
   ```

   A restacked bookmark already on origin is rewritten non-FF: the push output
   reads `[move sideways from <old> to <new>]` — expected shape, not an error.
   On this host push with
   `--config signing.behavior=drop --config git.sign-on-push=false` (key in no
   agent); GitHub squash-merge re-signs server-side.

7. **Hand off.** Rewritten stack PRs land via `sks-land` / `sks-pr-workflow`;
   leftover `(empty)` revs and stale workspaces are `sks-gc` territory.

## Pitfalls

- **Marker dialect.** jj writes `%%%%%%% diff from:` / `+++++++` markers; an
  agent parsing the classic `<<<<<<<` shape mangles the file. Always
  `read_file` the conflicted file before editing.
- **`jj resolve --list` on non-head revs errors** `No conflicts found at this
  revision`; the `conflicts()` revset is the reliable locator.
- **`jj edit` re-parents `@`.** Forgetting step 5 snapshots your next edit
  into a stack rev.
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

- `sks-dev-workflow` — the landing gates this feeds; never force-push stack
  branches.
- `sks-stack` — isolate before resolving when the main checkout is crowded.
- `sks-async` — multi-link stacks whose streams each need this loop.
- `sks-gc` — reclaim empty revs and stale isolation workspaces afterwards.
