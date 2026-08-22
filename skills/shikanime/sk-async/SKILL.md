---
name: sk-async
description: "jj workspace fan-out + stacked PRs for parallel work."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      [
        jj,
        workspaces,
        parallel,
        stacked-prs,
        gh-stack,
        delegation,
        github,
        shikanime-labs,
        shikanime-studio,
      ]
---

# Shikanime Org Parallel Streams

Split a multi-unit change into parallel, isolated streams that cannot conflict,
then land each as an independent PR or a stacked chain. Distills the unlazy
depth-tree delegation fan-out (decompose → dispatch parallel leaves → verify
bottom-up) onto jj's native commit DAG plus `gh stack`. This is the core
splitting component of `sk-dev-workflow` (and `cpn-dev-workflow`).

## When to Use

- A change decomposes into several units and some are independent.
- Parallel agents (delegate_task fan-out) must not share a working copy.
- Units carry dependencies: B needs A's code → depth (a stack); C needs A AND B
  → a join (merge commit).

## Model: the work is a DAG, jj is the executor

- **Fan-out** — multiple children of one trunk commit = parallel independent
  units. jj natively allows N children of any commit.
- **Depth** — a child of a child = a dependent unit; each root-to-leaf chain is
  a STACK (`gh stack`), each link its own PR.
- **Join** — a child with multiple parents (`jj new <a> <b>`) = a unit depending
  on several parallel units; it lands after them.
- **Isolation** — each stream works in its OWN jj workspace: separate working
  copy and working-copy commit, same repo and graph. No working-copy contention,
  no interleaved edits — conflictual work is avoided by construction, not by
  coordination.
- **Independence test** (decomposition rule): a unit is independent iff its file
  set is disjoint from its siblings' and it imports none of their NEW code.
  Otherwise it is a dependent unit (depth) or a join (merge).

## Procedure

1. **Tree before work** — decompose against the issue ledger; write the tree
   (trunk, units, edges) into the plan/`todo` with gates fixed per leaf BEFORE
   any fan-out (contracts before delegation).
2. **Fan out** — ALWAYS start work in a NEW jj workspace; never work directly in
   an existing one (the default workspace is reserved for trunk observation).
   One workspace per parallel unit, rooted at the trunk; name workspaces
   `<repo-name>.<unit>` (workspace names are repo-global, dot- qualification
   prevents collisions across repos):

   ```bash
   jj workspace add ../<repo-name>.<unit> --name <repo-name>.<unit>
   ```

   A new workspace's working-copy commit is a child of the current `@`; for
   depth > 1, root the stream inside it with `jj new <parent>`.
3. **Work each stream** in its own workspace directory; commit per `sk-commit` —
   every commit carries the trailer:

   ```bash
   jj describe -m "<subject>" -m "Co-authored-by: Automata
   <automata@shikanime.studio>"
   ```

   commit; jj merges automatically).
4. **Land** (fork-first — branches push to the fork remote, PRs open with
   `--head <login>:<branch>`; see `sk-dev-workflow`):
   - Independent unit → own bookmark + standalone PR (or single-member stack).
   - Dependent chain → one bookmark per link, then:

     ```bash
     gh stack init <base> && gh stack add <next> && gh stack submit --auto --open
     ```

   - PR↔issue linkage per `sk-pr`: `Related: <issue URL>` by default — no
     auto-close keywords.
5. **Verify bottom-up** — each leaf's checks run IN its own workspace; the
   dispatcher re-runs them itself (subagent self-reports are not evidence).
   Retire finished streams: `jj workspace forget <name>`; refresh a fallen-
   behind workspace with `jj workspace update-stale`.

## Fan-out via delegate_task

Give each child agent: its workspace path, its unit's gates, the commit shape
(plain English + Automata co-author trailer). The parent re-verifies every gate
via `terminal` inside each workspace before reporting done.

## Pitfalls

- **Pseudo-independent units** (overlapping file sets) → merge conflicts at
  join; fix the decomposition, not the conflict.
- **Workspaces share the repo** — bookmarks and the commit graph are GLOBAL: one
  bookmark per unit, never two streams on one bookmark.
- **Fan-out before contracts** — spawning children without fixed gates
  reproduces the prose-enforcement failure the gates exist to prevent.
- `gh stack` = GitHub public-preview; fine for internal shikanime use (see
  `sk-dev-workflow`).
- Forgetting `jj workspace update-stale` on a workspace left idle while the
  trunk advanced — it does not auto-advance.

## Verification

```bash
jj workspace list && jj log -r 'all()' --limit 20   # tree shape on screen
gh stack view && gh pr list --state open             # chains + PRs exist
```

The rendered DAG matches the planned tree; every leaf has a PR linked to its
issue without auto-close; every gate has in-workspace evidence.

## See also

- `sk-dev-workflow` — parent workflow; run its assumption-validation gate BEFORE
  fanning out.
- `sk-commit` / `sk-pr` — commit shape (co-author trailer) and PR linkage.
- `cpn-dev-workflow` — same fan-out applied to console module migrations.
