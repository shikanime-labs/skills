---
name: sks-commit-resolve
description:
  "Use when a jj commit or pushed PR branch is conflicted against a moved
  trunk: collision verdicts, chain resolution order, squash traps — until the
  branch is pushable."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - jj
      - conflicts
      - rebase
      - pr
      - shikanime-labs
      - shikanime-studio
    related_skills:
      - sks-converge
      - sks-restack
      - sks-dev-workflow
      - sks-commit
      - sks-pr-resolve
platforms:
  - linux
  - macos
  - windows
---

# Shikanime Org Commit Conflict Resolution

Resolve a conflicted jj commit or pushed PR branch against a moved trunk
until the branch is pushable. `sks-converge` owns the repo-state mechanics
(the `conflicts()`/`divergent()` loop, the jj marker dialect, twin
convergence) — load it for those. This skill owns the decisions around that
loop: where in a chain to resolve, which side of a collision wins, and the
squash/abandon traps that turn a clean resolution into a silent regression
(trailer loss, stale commit ids, wrong-stack gates).

## When to Use

- GitHub shows the PR CONFLICTING, or a rebase onto moved `main` produced
  conflicts on a pushed branch.
- `jj git push` fails `Won't push commit ... since it has conflicts` or
  `Bookmark <name> is conflicted` on a commit you authored.
- You must pick a side in a collision: a sibling PR merged the same content,
  or main stripped a file your branch still carries.
- A resolution requires `jj squash` / `jj abandon` on a pushed commit.

## Prerequisites

- `jj git fetch --remote origin` FIRST — conflicts and divergence only
  become visible once the fetch imports the remote rewrite; resolving on a
  stale trunk wastes the work.
- Triage before resolving: `jj diff -r main@origin --stat` next to your own
  `jj diff --stat` shows which files collide and whether main already
  carries your content.

## Procedure A — resolve a conflicted chain

1. **Locate** the conflicted revisions with the `conflicts()` revset
   (`sks-converge` step A1); `jj resolve --list` only works on the
   working-copy commit.
2. **Resolve bottom-up.** A conflict born at the chain bottom propagates to
   every descendant: resolve it once there and the stack auto-resolves.
   Then RE-SCAN `conflicts()` after each parent — resolving a parent
   re-materializes its children's conflicts, so never trust the earlier
   list.
3. **Verify intent on every file both sides touched.** jj's auto-merge can
   silently duplicate or drop adjacent-insert lines (module registration
   lists, imports). Compare the old base→head diff against
   `main@origin..@` per file — file list and hunk shape.
4. **Address revisions by CHANGE ID after any rewrite.** A stale commit_id
   still resolves — silently to the hidden pre-rebase original — and reads
   old content as if the rebase regressed. Commit ids are only for git
   plumbing on commits you just printed.
5. **Torn `@` after `jj rebase -r`.** The working copy can keep the stale
   pre-rebase parent (old tree plus phantom deletions) while the rebased
   commit is fine — do not redo the edits. Recover: `jj new <rebased>`,
   `jj abandon` the stale empty `@`, `jj bookmark set <branch> -r
   <rebased> --allow-backwards`, then re-run gates. Gates run against the
   wrong stack prove nothing: confirm `@`'s ancestry includes the commit
   under test.

## Procedure B — collision verdicts

Decide per collided file BEFORE editing anything:

1. **A sibling PR merged the same content** → keep main's version
   byte-for-byte (`jj file show -r main@origin <file>` is the source of
   truth) and drop the branch copy. The resolved commit becomes `(empty)`:
   `jj abandon` it and `jj bookmark set <branch> -r <parent>
   --allow-backwards`. The PR dropping a commit is correct.
2. **Main's version is OLDER than yours** (main stripped the file back) →
   KEEP YOURS. Read both versions; if main's is an ancestor of yours, yours
   is correct — do not let the rebase silently revert your work.
3. **Main landed content you were also adding** → drop your duplicate
   (`jj restore --from main@origin <file>`) rather than keeping both.
4. **An upstream edit collided with a line-targeted insertion** → audit the
   WHOLE block for duplicated keys (a key can sit mid-block, not only after
   a `- name:` line) and diff before/after to prove zero new breakage.

## Procedure C — squash and abandon traps during resolution

- **Always `--from A --into B`.** Positional args to `jj squash` are
  treated as paths (`No matching entries for paths`).
- **Direction:** `jj squash --from @` folds the child into the parent and
  keeps the PARENT's description and bookmark — the normal fold when a fix
  lands on a pushed commit. `--from @- --into @` inverts it (pulls the
  parent's change into the child).
- **`-m` replaces the target's ENTIRE message** — body, `Co-authored-by`,
  `Signed-off-by` all lost. Fold without `-m`
  (`--use-destination-message` keeps the parent's description), then
  re-describe if wording must change:
  `jj describe -r <rev> --stdin < msg.txt`. Verify trailers after every
  squash touching a pushed or signed commit.
- **Headless:** `JJ_EDITOR=true jj squash ...` — without a TTY the editor
  (`hx`) panics; the command aborts atomically before any tree change, so
  check state with `jj log`/`jj diff` and redo with explicit flags.
- **Abandon by COMMIT ID**, not change-id offset — offsets renumber between
  operations; commit ids are stable. After abandoning, never reference the
  dead commit again (naming it resurrects it and re-diverges the change).
- Fold the resolution INTO the conflicted commit — a separate "fix
  conflicts" child on a PR branch ships noise and a misleading diff.

## Push gate

```bash
jj log -r 'conflicts()' --no-graph    # empty
jj log -r 'divergent()' --no-graph    # empty
jj git push --remote origin -b <branch>
```

`[move sideways from X to Y]` is the expected output for a rewritten pushed
branch, not an error. On this host push with `--config
signing.behavior=drop --config git.sign-on-push=false` (GitHub squash-merge
re-signs server-side). Never bypass the gate — `Won't push ... conflicts`
is it working. After the push, verify the remote ref actually moved
(`gh api repos/<org>/<repo>/git/ref/heads/<branch>`): a success line is not
evidence, and a silently regressed ref carrying an old commit has been
observed after clean pushes.

## Pitfalls

- Resolving bottom-up is necessary but not sufficient: re-scan
  `conflicts()` after every parent resolution.
- A stale commit_id resolves silently to the hidden original — use change
  ids after every rewrite.
- `jj squash -m` trailer loss is silent; landing then fails gitlint/DCO or
  loses the Automata credit.
- Gates captured before the final rewrite describe a superseded tree —
  re-run lint/build on the resolved tip before pushing.
- "references unexpectedly moved (stale info)" on push can mean origin
  deleted the branch while main re-landed your parent's content as an
  identical squash: diff the old parent against the main tip — if empty,
  rebase only the genuinely-new commits and plain-push (no force).

## Verification

```bash
jj log -r 'conflicts()' --no-graph         # empty
jj log -r 'divergent()' --no-graph         # empty
jj diff --from main@origin --to @ --stat   # exactly the intended scope
gh api repos/<org>/<repo>/git/ref/heads/<branch> --jq .object.sha
# must equal `jj log -r @ --no-graph -T commit_id`
```

## See also

- `sks-converge` — the state loop (marker dialect, `:ours`/`:theirs`,
  divergent twins) this skill builds on.
- `sks-restack` — the rebase step that produces most of these conflicts.
- `sks-dev-workflow` — landing gates; push discipline.
- `sks-commit` — the commit envelope whose trailers these traps threaten.
- `sks-gc` — reclaim empty revs and workspaces after landing.
