---
name: sks-async
description:
  Use when splitting multi-unit work into parallel, isolated jj workspaces
  (depth-tree fan-out) and landing as independent plain `gh pr` merges.
version: 0.1.1
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - jj
      - workspaces
      - parallel
      - stacked-prs
      - gh-stack
      - delegation
      - github
      - shikanime-labs
      - shikanime-studio
    related_skills:
      - cpn-async
      - cpn-commit
      - cpn-dev-workflow
      - sks-dev-workflow
      - sks-pr
platforms:
  - linux
  - macos
  - windows
---

# Shikanime Org Parallel Streams

Decompose a multi-unit change into parallel, isolated streams; land each as an
independent PR or stacked chain. Distills unlazy depth-tree delegation fan-out
onto jj's commit DAG as plain `gh pr` merges. Core splitting component of
`sks-dev-workflow`.

## When to Use

- Several units, some independent.
- Parallel agents (delegate_task fan-out) must not share a working copy.
- Shape: B needs A → depth (stack); C needs A AND B → join.

## Procedure

1. **Tree before work** — decompose vs issue ledger; record tree in plan/`todo`
   with leaf gates fixed BEFORE fan-out (contracts before delegation).
2. **Fan out** — ALWAYS a NEW jj workspace; never an existing one (default is
   for trunk observation). One workspace per unit, rooted at trunk; name
   `<repo-name>.<unit>` (repo-global, dot-qualified):

   ```bash
   jj workspace add ../<repo-name>.<unit> --name <repo-name>.<unit>
   ```

   New workspace's working copy is a child of `@`; for depth > 1 root with
   `jj new <parent>`.
3. **Work each stream** in its dir; commit per `sks-commit` — every commit
   carries the trailer:

   ```bash
   jj describe -m "<subject>" -m "Co-authored-by: Automata <automata@shikanime.studio>"
   ```

4. **Land** (push to `origin`, PRs with `--head <org>:<branch>`; see
   `sks-dev-workflow`):
   - Independent unit → own bookmark + standalone PR (or single-member stack).

- Dependent chain → one bookmark per link. Example:

```bash
jj bookmark set <next> -r <next>
gh pr create --repo <org>/<repo> --base main --head "<org>:<next>" \
  --title "<subject>" \
  --body "$(cat <<'EOF'
## What
<brief bullet scope of this chain link>

## Why
<linked issue: why now>

## References

Related: <issue URL>
EOF
)"
```

- PR↔issue linkage per `sks-pr`: `Related: <issue URL>` by default.
- Before opening each PR, run the `sks-pr` step 2b duplicate/stack check — an
  existing open PR covering the unit means push to it or stack on it, never a
  second PR for the same change.

5. **Verify bottom-up** — each leaf's checks run IN its workspace; dispatcher
   re-runs them (subagent self-reports aren't evidence). Retire with
   `jj workspace forget <name>`; refresh idle with `jj workspace update-stale`.

## Fan-out via delegate_task

Each child: workspace path, unit gates, commit shape (plain English + Automata
co-author trailer). Parent re-verifies every gate via `terminal` in each
workspace before reporting done. Dispatch `delegate_task(tasks=[])`: **one task
per leaf**, `goal` carries the contract; never bundle two leaves (defeats
isolation). Skeleton: `references/sks-async-delegate.md`.

## Verification

```bash
jj workspace list && jj log -r 'all()' --limit 20   # tree shape on screen
gh pr list --repo <org>/<repo> --state open          # PRs exist per leaf
```

DAG matches planned tree; every leaf has a PR linked to its issue; every gate
has in-workspace evidence.

## See also

- `sks-dev-workflow` — parent; run its assumption-validation gate BEFORE
  fan-out.
- `sks-commit` / `sks-pr` — commit shape (co-author trailer) and PR linkage.
- `cpn-dev-workflow` — same fan-out for console module migrations.
- Model, pitfalls, dispatch skeleton: `references/sks-async-delegate.md`.
