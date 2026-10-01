---
name: sks-converge
description:
  Use when jj conflicts or divergent changes block a jj repo after a
  tree move — resolve conflicted revisions and divergent twins until pushable.
version: 0.2.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - jj
      - conflicts
      - divergence
      - recovery
    related_skills:
      - sks-restack
      - sks-dev
      - sks-delegate
      - sks-gc
platforms:
  - linux
  - macos
  - windows
---

# jj Convergence

Resolve the two states that block a jj repo of the target org after the
tree moves (rebase, restack, remote rewrite): **conflicted revisions** and
**divergent changes**. Reusable standalone — `sks-restack` hands off
here after its rebase; any skill may call this loop directly. Exit condition:
pushable, i.e. `conflicts()` and `divergent()` empty and bookmarks
unconflicted.

For org specifics, read `references/shikanime.md` when operating in
shikanime repos.

## When to Use

- Any `jj log -r 'conflicts()'` output after moving revisions.
- `jj log` shows a change ID twice (`ab12cdef/0`, `ab12cdef/1`, tagged
  `(divergent)`), or a bookmark renders `feat??` / `(conflicted)` after a
  fetch.
- `jj git push` fails `Won't push commit ... since it has conflicts` or
  `Error: Bookmark <name> is conflicted`.
- Another checkout rewrote a commit you also rewrote (stacked agents,
  two machines).

## Prerequisites

- jj repo; `jj git fetch --remote origin` FIRST — divergence only becomes
  visible after the fetch imports the remote rewrite.

## Procedure A — conflicted revisions

1. **Locate.**

   ```bash
   jj log -r 'conflicts()' --no-graph \
     -T 'change_id.short() ++ " | " ++ description.first_line() ++ "\n"'
   ```

   Empty output = no conflicts; go to Procedure B. `jj resolve --list` only
   works on the working-copy commit — on other revs it errors
   `No conflicts found at this revision`; use the revset.

2. **Resolve oldest-first, re-scanning between revisions** (resolving a
   parent re-materializes its children's conflicts — never trust the earlier
   list).

   1. `jj edit <change-id>` — checks the rev out.

   2. Read the conflict. jj's own marker dialect, NOT git's:

      ```text
      <<<<<<< conflict 1 of 1
      %%%%%%% diff from: <base> (parents of rebased revision)
      \\\\\\\\\        to: <dest> (rebase destination)
      -old line
      +dest line
      +++++++ <rev> (rebased revision)
      your line
      >>>>>>> conflict 1 of 1 ends
      ```

      Side map: `%%%%%%% diff from:` block = the **destination** side (moved
      trunk); `+++++++ <rev>` block = the **rebased revision** (your change).
      Outside the markers = shared context.

   3. Hand-merge (keep context, combine both intents, delete every marker
      line) or whole-side pick:

      ```bash
      jj resolve --tool :ours <file>    # destination side (moved trunk)
      jj resolve --tool :theirs <file>  # your rebased change
      ```

   4. Saving the file auto-snapshots into the checked-out rev; the
      `(conflict)` tag disappears. `jj squash` only if you resolved in a
      child rev.

   5. Re-scan `conflicts()` → next rev.

3. **Restore `@`.** `jj edit` moved the working copy —
   `jj edit <original @ change-id>` before anything else snapshots into a
   stack rev.

## Procedure B — divergent changes

1. **Locate.**

   ```bash
   jj log -r 'divergent()' --no-graph \
     -T 'change_id.short() ++ " | " ++ description.first_line() ++ "\n"'
   ```

   A divergent change = one change ID on 2+ commits (`id/0`, `id/1`), shown
   tagged `(divergent)` in `jj log`. Bookmark display turns `name??` and
   `jj bookmark list` shows `(conflicted)` with `@origin (ahead by N, behind
   by N)`.

2. **Pick the surviving twin.** Default = YOUR local rewrite (the remote twin
   is usually a stale push or another agent's duplicate). Diff them first:

   ```bash
   jj diff --from <id>/0 --to <id>/1
   ```

3. **Converge** — abandon the losing twin, then repoint the bookmark. Both
   steps are required; abandoning alone leaves the bookmark conflicted and
   push rejected:

   ```bash
   jj abandon <id>/0                        # losing twin
   jj bookmark set <branch> -r <id>/1       # winner — offset form REQUIRED
   jj git push --remote origin -b <branch>  # reads [move sideways ...]
   ```

   Bare `<id>` (no `/N`) errors `Change ID ... is divergent` on a divergent
   change — always address twins by offset.

4. **Verify.**

   ```bash
   jj log -r 'divergent()' --no-graph    # empty
   jj bookmark list                       # no (conflicted), no name??
   ```

## Push gate (both procedures)

```bash
jj log -r 'conflicts()' --no-graph    # empty
jj log -r 'divergent()' --no-graph    # empty
jj git push --remote origin -b <branch>
```

Where the org's host setup requires it, push with the org's push-signing
overrides — read `references/shikanime.md` when operating in shikanime
repos for the exact flags; the host re-signs server-side on squash-merge.

## Pitfalls

- **Resurrection by reference.** After abandoning a twin, ANY command that
  references it (`jj new <a> <b>` merge of both twins, `jj show <id>/0`)
  makes it reachable again and re-diverges the change. Abandon, then never
  name it again.
- **Offset is mandatory.** `jj bookmark set <name> -r <id>` on a divergent
  change fails; use `<id>/1`. This also bites `jj describe -r <id>`.
- **Hidden ≠ gone.** `jj abandon` hides the twin; `jj bookmark list` may keep
  showing it `(hidden)` under the conflicted entry until the bookmark is
  repointed and pushed.
- **`jj resolve --list` on non-head revs errors** — the `conflicts()` revset
  is the locator.
- **Marker dialect.** Parsing git-style `<<<<<<<` only mangles the file; the
  real sides live under `%%%%%%%` / `+++++++`.
- **Push rejection is the gate.** `Won't push ... conflicts` /
  `Bookmark <name> is conflicted` mean converge more; never bypass.
- **Twin churn is the failure mode of hand-resolving on the wrong rev.**
  Resolving in a non-child `@` (or a merge of the twins) makes `jj squash`
  fork parallel resolved copies — change ids end up divergent with CONFLICT
  twins, and every `jj abandon` of the working copy re-seeds a new merge
  child. Guard rails: (1) always `jj edit` INTO the conflicted change before
  editing files; (2) `jj squash --from @ --into <rev>` only when `<rev>` is
  `@-` (the parent) or `@` itself; (3) after any abandon, never reference the
  abandoned id again — find survivors via description search
  (`jj log -r 'description("...")'`), not by old ids. `jj new <hidden-twin>
  -d <other>` creates a MERGE, not a revival — use `jj rebase -s` instead.

## Verification

```bash
jj log -r 'conflicts()' --no-graph   # empty
jj log -r 'divergent()' --no-graph   # empty
jj bookmark list                     # unconflicted
jj status                            # @ restored
```

## See also

- `sks-restack` — the rebase step that precedes this skill.
- `sks-dev` — landing gates; never force-push stack branches.
- `sks-delegate` — mandatory fresh-workspace isolation for every
  implementation unit.
- `sks-gc` — reclaim empty revs and stale workspaces afterwards.
