---
name: sks-split
description:
  "Use when one jj commit or in-flight stack has grown multiple
  responsibilities and must be split into parallel sibling units or a
  parent/child stack, decided per unit pair by dependency."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - jj
      - split
      - stacked-prs
      - single-responsibility
      - shikanime-labs
      - shikanime-studio
    related_skills:
      - sks-delegate
      - sks-async
      - sks-commit
      - sks-pr
      - sks-restack
platforms:
  - linux
  - macos
  - windows
---

# Split

Decide and execute the split of one oversized commit or in-flight stack into
units with a single responsibility each, as parallel siblings or a
parent/child stack. This skill owns the decision and the jj mechanics;
`sks-delegate` owns unit isolation and `sks-async` owns fan-out after the
shape is settled.

## When to Use

- One commit (or dirty working copy) mixes two or more responsibilities.
- An in-flight chain turns out partially independent: some links build on
  earlier ones, some do not.
- Review feedback demands a change land as separate PRs.

Not for: choosing units before any work exists (`sks-async`), moving a whole
existing stack onto a moved base (`sks-restack`), or isolating one unit you
already know is single (`sks-delegate`).

## Procedure

1. **Enumerate responsibilities.** Read the dirty change or chain
   (`jj diff -r @ --stat`, `jj log -r 'main@origin..@'`) and list each
   responsibility as a unit: its files, and what it is for. A unit that
   exists only to serve another unit is not a unit.

2. **Dependency-test every pair.** For each unit pair A/B ask: does B's diff
   compile or make sense without A's files? Map the answer to a shape:

   | Relation                                         | Shape              |
   | ------------------------------------------------ | ------------------ |
   | B edits files or contracts A introduces          | parent/child stack |
   | A and B touch disjoint files, no shared contract | parallel siblings  |
   | One responsibility only, or inseparable hunks    | no split           |

   Inseparable means interleaved hunks in the same file that belong to both
   concerns; splitting those needs interactive `jj split`, which requires a
   TTY — surface that as a manual step instead of failing silently.

3. **Split each mixed commit, non-interactively.** `jj split` without `-m`
   opens the diff editor and fails in a non-TTY session. Selected paths stay
   in the ORIGINAL change; the remainder lands in a NEW child commit:

   ```bash
   # parent/child stack: A first, remainder (B) as the child
   jj split -m "<unit A subject>" <A's files>
   jj describe -m "<unit B subject>"        # describes the new child @

   # parallel siblings: A and B both parented on the split point
   jj split --parallel -m "<unit A subject>" <A's files>
   jj describe -m "<unit B subject>"
   ```

   After a `--parallel` split both siblings are ancestors of `@`; give each
   its own bookmark and land as independent PRs.

4. **Break a wrongly stacked chain.** When an already-committed chain holds
   independent links, make them siblings with explicit change ids:

   ```bash
   jj log -r 'main@origin..@' --no-graph \
     -T 'change_id.short() ++ " " ++ description.first_line() ++ "\n"'
   jj parallelize <change-id-A> <change-id-B>
   ```

   Pass change ids from the log, never a description-range revset:
   `description("x")::description("y")` can resolve empty and `parallelize`
   then reports "Nothing changed" with exit 0 — a silent no-op.

5. **Bookmark per unit, push, land.** One bookmark per unit; each unit gets
   its own PR per `sks-pr`. Siblings land in any order; a stack
   lands base first (`sks-land`). Commit descriptions follow `sks-commit`.

## Pitfalls

- `jj split <paths>` without `-m` opens the diff editor; in a non-TTY it
  fails with "Failed to edit description" and leaves a temp file behind.
  Always pass `-m`.
- `jj file list -r <rev>` shows the cumulative tree, not the commit's own
  contribution — verify splits with `jj diff -r <rev> --stat`.
- Template revsets like `description("x")` silently match nothing when the
  description differs; resolve change ids from `jj log` first.
- A pushed bookmark is immutable — split BEFORE pushing, or follow the
  rebase-into-fresh-commit recovery in `sks-dev`'s landing procedure.
- Splitting one dirty change twice: the second `jj split` operates on the
  remainder child, not the original — re-run `jj diff -r @ --stat` before
  each split.

## Verification

```bash
jj log -r 'main@origin..@' --no-graph \
  -T 'change_id.short() ++ " [" ++ description.first_line() ++ "]\n"'
jj diff -r <each-unit> --stat   # one responsibility per commit, no overlap
```

Done when: every commit in the range holds exactly one responsibility, the
dependency shape matches the table, and each unit has its own bookmark.

## See also

- `sks-delegate` — isolate one already-single unit.
- `sks-async` — fan-out once units and contracts are settled.
- `sks-restack` — move an existing stack onto a moved base.
- `sks-land` — landing order for stacked PRs.
