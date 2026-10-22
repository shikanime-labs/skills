---
name: sks-context
description:
  "Use when working in a target org's repos: the ecosystem map, environment
  facts, and shared assumptions every workflow skill builds on."
version: 0.1.0
author: Automata
license: Apache-2.0
metadata:
  hermes:
    tags:
      - environment
      - conventions
      - catalog
    related_skills:
      - sks-dev
      - sks-delegate
      - sks-commit
      - sks-land
      - sks-pr
platforms:
  - linux
  - macos
  - windows
---

# Skills Context

The shared context for the workflow skill family: one doctrine, the
environment assumptions every skill builds on, and how the family fits
together. Every sibling skill assumes this model; read it before working in
any target-org repo, and when sibling skills seem to conflict with each
other.

## When to Use

- Starting work in any target-org repo, before picking a workflow skill.
- Unsure which sibling skill owns a concern — the family table routes it.
- Sibling skills appear to conflict — this doctrine arbitrates.

## One doctrine

The lifecycle is **discussion → issue → issue comments → PR**:

- The issue body is the problem statement; acceptance criteria are a
  command-decidable tasklist — the gate ledger.
- Issue comments carry findings and evidence; the PR proves the ledger
  N-of-N.
- The PR↔issue link is Development metadata added at triage, never a body
  line.
- Landing is `gh pr merge --squash` in dependency order; a direct push to
  `main` needs explicit user authorization.

The working stance behind every unit: prefer the long-term solution, fix the
root cause, never land a tactical patch that accrues debt. There is no hard
SLA — correctness and durability outrank turnaround time, so take the time to
do it properly.

Skill bodies are org-neutral; org-specific conventions load on demand from
per-skill `references/<org>.md` files. Read `references/shikanime.md` for
the shikanime org: identity, checkout layout, remote split, protected
repos, commit trailers, toolchain.

## Environment assumptions

Every family skill assumes, without restating:

- Work runs as an agent account with org membership. Probe before work:
  `gh api user --jq .login` and
  `gh api repos/<org>/<repo> --jq .permissions.push`.
- Trunk is `main@origin` and may be protected by rulesets — the classic
  branch-protection endpoint reads ruleset-backed repos as unprotected.
- Every implementation unit runs in a fresh jj workspace pinned to
  `main@origin`; the cloned checkout is a read-only reference surface.
- Commits carry a plain-English imperative title, the org co-author
  trailer, and any repo-mandated sign-off; `sks-commit` owns the shape.
- Claims — pushed, landed, merged — are proven against real command output
  before reporting; success lines prove nothing.
- Unmet assumptions surface as `BLOCKED: <req> — <evidence> — <recovery>`,
  never as a silent scope change.

## How the family fits

| Concern                    | Skill                                             |
| -------------------------- | ------------------------------------------------- |
| Pre-issue convergence      | `sks-discussion`                                  |
| Issues and the gate ledger | `sks-issue`, `sks-issue-refine`, `sks-issue-triage` |
| Isolation for every unit   | `sks-delegate`                                    |
| Commits                    | `sks-commit`                                      |
| Review                     | `sks-pr-review`                                   |
| PRs                        | `sks-pr`, `sks-pr-ready`, `sks-pr-triage`         |
| Landing                    | `sks-land`                                        |
| Fan-out and swarm          | `sks-async`, `sks-swarm`                          |
| Board state                | `sks-project`                                     |
| End-of-loop block          | `sks-tldr`                                        |

The coordination ladder is one-way and takes the minimum rung that fits:
`sks-delegate` — one unit; `sks-async` — N parallel units, one repo;
`sks-swarm` — units needing different machines or capabilities.

## Procedure

1. Read the org reference for the org in play — for shikanime repos,
   `references/shikanime.md`.
2. Run the assumption probes above before any unit; report unmet ones as
   blockers.
3. Route the work through the family table; when a sibling skill's
   instructions contradict this doctrine, the doctrine wins and the
   conflict is filed as an upstream issue.

## Pitfalls

- Citing a sibling skill's `references/<org>.md` as an org-neutral fact —
  those files are org-specific by convention.
- Treating an unprobed assumption as true: an expired gh token or missing
  push right invalidates every downstream step, so probe first.
- Inventing org facts the reference file does not carry; probe the live
  repo instead and update the reference with what the probes return.

## Verification

```bash
gh api user --jq .login
gh api repos/<org>/<repo> --jq .permissions.push
test -d .jj && jj log -r 'main@origin' -n 1 --no-graph -T 'commit_id.short()'
```

## See also

- `sks-dev` — the full dev loop this context underpins.
- `sks-delegate` — the isolation entry every unit passes through.
- `sks-commit` / `sks-land` — the commit and landing shapes.
