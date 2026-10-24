---
name: sks-converge
description:
  Use when jj conflicts, divergent changes, or red required GitHub Actions
  checks block a pushed head — resolve each until the head is green and
  pushable.
version: 0.3.0
author: Automata
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
      - sks-context
platforms:
  - linux
  - macos
  - windows
---

# jj + CI Convergence

Resolve the three states that block a pushed head of the target org after
the tree moves (rebase, restack, remote rewrite) or the push lands:
**conflicted revisions**, **divergent changes**, and **red required GitHub
Actions checks**. Reusable standalone — `sks-restack` hands off here after
its rebase; any skill may call this loop directly. Exit condition: green and
pushable, i.e. `conflicts()` and `divergent()` empty, bookmarks
unconflicted, and required checks green on the pushed head.

For org specifics, read `references/shikanime.md` when operating in
shikanime repos.

## When to Use

- Any `jj log -r 'conflicts()'` output after moving revisions.
- `jj log` shows a change ID twice (`ab12cdef/0`, `ab12cdef/1`, tagged
  `(divergent)`), or a bookmark renders `feat??` / `(conflicted)` after a
  fetch.
- `jj git push` fails `Won't push commit ... since it has conflicts` or
  `Error: Bookmark <name> is conflicted`.
- `gh pr checks <n>` (or the merge box) shows a red **required** check on
  the pushed head — converge the head back to green before landing.
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

## Procedure C — red required GitHub Actions checks

1. **Detect.** A push that succeeds can still leave the PR blocked — a red
   required check is a convergence gate exactly like a jj conflict:

   ```bash
   gh pr checks <n> -R <org>/<repo>            # fail = blocker
   gh api repos/<org>/<repo>/commits/<head-sha>/check-runs \
     --jq '.check_runs[] | select(.conclusion=="failure") | .name'
   ```

   `gh pr checks` exit codes: 0 = all pass, 1 = failing (or no checks),
   8 = pending. Non-required red checks do not block landing — converge
   the required set only.

2. **Classify.** Fetch the failing job's log and read the first failing
   step (`gh run view <run> --job <job-id> --log`, or the per-job API in
   `sks-cichecks`) — never fix from the check name alone:

   - **Transient/flake** (network hiccup, runner boot, download timeout,
     timestamp/ordering test) → re-run just that job:
     `gh run rerun <run> -R <org>/<repo> --failed`.
   - **Code-caused** (the failure names your diff: a touched file, a
     changed schema, a lint rule your edit breaks) → fix at the root cause
     in the workspace, amend (`jj describe -m "<same subject>"` re-signs
     and re-points the bookmark), re-push, and wait for the new head's
     checks — the fix lands as the same change, never a tactical patch
     that accrues debt.
   - **Pre-existing/infra** (fails on `main` too, or a non-200/403/
     action-syntax error untouched by your diff) → do not change PR code;
     surface as `BLOCKED: required check <name> — failing on main —
     <recovery>` and let `sks-cichecks` own classification evidence.

   Bounded re-run policy: at most one automatic `--failed` re-run; a
   second identical failure is evidence of a real fault, not a flake —
   trace it.

3. **Re-verify on the CURRENT head.** Re-running mutates nothing locally;
   a fix + re-push moves the head, which invalidates every earlier check
   run — re-query, never reuse the previous verdict. A green re-run of a
   job the head has since moved past proves nothing.

4. **Hand depth to `sks-cichecks`.** This procedure converges the loop;
   per-job log fetching, `needs`-graph root-cause tracing, and
   landability verification are owned there — load it when step 2's
   classification is not obvious from the first failing step.

## Push gate (all procedures)

```bash
jj log -r 'conflicts()' --no-graph    # empty
jj log -r 'divergent()' --no-graph    # empty
jj git push --remote origin -b <branch>
gh pr checks <n> -R <org>/<repo>      # exit 0 — required checks green
```

Where the org's host setup requires it, push with the org's push-signing
overrides — read `references/shikanime.md` when operating in shikanime
repos for the exact flags; the host re-signs server-side on squash-merge.
A red required check on the pushed head is a gate doing its job — converge
it (Procedure C), never `--admin` past it unasked.

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
  `Bookmark <name> is conflicted` mean converge more; never bypass. Same
  for a red required check: it is Procedure C input, not a merge blocker
  to `--admin` past.
- **A green check run can be stale.** Checks attach to a head SHA; after
  any fix + re-push (or a `main` advance that ejects a queued PR), only
  runs on the current `headRefOid` count. Re-query on the head you are
  about to land, never reuse the previous verdict.
- **Re-run churn.** `gh run rerun --failed` re-runs only failed jobs but
  re-allocates the same run ID — an unbounded loop of re-runs hides a real
  fault behind runner luck. One re-run; the second identical failure gets
  traced (Procedure C step 2).
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
gh pr checks <n> -R <org>/<repo>     # exit 0 — green on the pushed head
```

## See also

- `sks-restack` — the rebase step that precedes this skill.
- `sks-cichecks` — per-job log tracing, `needs`-graph root-cause
  classification, and landability verification for red CI (Procedure C's
  depth owner).
- `sks-dev` — landing gates; never force-push stack branches; watch is not
  merge.
- `sks-delegate` — mandatory fresh-workspace isolation for every
  implementation unit.
- `sks-gc` — reclaim empty revs and stale workspaces afterwards.
