---
name: sks-plan
description:
  "Use when planning a milestone from a goal: converge direction, decompose
  into dependency-ordered units, fill the milestone with triaged, boarded
  issues ready for sks-iterate."
version: 0.1.0
author: Automata
license: Apache-2.0
metadata:
  hermes:
    tags:
      - workflow
      - planning
      - milestone
    related_skills:
      - sks-discussion
      - sks-issue
      - sks-issue-triage
      - sks-milestone
      - sks-project
      - sks-iterate
      - sks-dev
      - sks-summary
      - sks-context
platforms:
  - linux
  - macos
  - windows
---

# Milestone Planning

Strategy plane above the execution loop: turn a goal into a milestone ready
to iterate — a filled milestone plus a dependency-ordered set of triaged,
boarded issues whose acceptance ledgers seed the work. The plane stack:
this skill (strategy) > `sks-iterate` (execution loop) > `sks-milestone`
(release readiness) > `sks-issue` (problem statement) > `sks-pr` (the how,
what, why of the solution) > `sks-dev` (local mechanics) > `sks-commit`
(atomic change); `sks-project` is the board where the works of teams are
organized. Every artifact this plan emits is written by the skill that
owns its plane; the loop that consumes the result is `sks-iterate`.

## When to Use

- "Plan the <goal> milestone" / a goal too large for one unit — decompose
  and fill the milestone.
- An RFC just converged (`sks-discussion`) and its direction needs units.
- Not for a single unit — that is `sks-dev` straight, no planning plane.
- Not for minting the nixpkgs-release milestone plane across repos — that
  is `sks-milestone`; this skill fills a milestone with units, that one
  owns the release calendar.

## Procedure

1. **Converge the goal.** Unconverged direction goes to `sks-discussion`
   first; units cut before the direction settles are rework. Converged
   means the RFC closed or the user stated the goal as fact.
2. **Decompose into units.** One unit is one issue's worth of work,
   complete in a single `sks-dev` pass. For each unit name its
   dependencies and mark the independent ones — they form the fan-out
   groups the loop will route together.
3. **Cut the set.** Drop every unit not required to reach the goal;
   speculative units are re-planned when they become real. Present the
   table — unit, depends on, fan-out group — and wait for approval before
   writing anything: opening issues is a gated batch (`sks-bulk` shape).
4. **Fill the milestone.** Attach the milestone the user names when one
   exists; otherwise create one titled after the goal — in every repo
   holding units when the set spans repos:

   ```bash
   # payload.json: {"title": "<goal>", "state": "open",
   #                "description": "<one-line goal>"} — no due_on
   gh api repos/<org>/<repo>/milestones --input payload.json
   gh api repos/<org>/<repo>/milestones --jq '.[].title'   # read back
   ```

   No `due_on` unless a real deadline exists: a due date is a commitment,
   never invented to fill the field (rule owned by `sks-milestone`).
5. **Open and triage every issue** (`sks-issue` then `sks-issue-triage`):
   body is the problem statement, the acceptance ledger already seeded
   command-decidable; dependencies recorded as issue relationships at
   triage, never only in the plan prose. This step owns the milestone
   assignment: triage never sets one, so every unit lands on the
   milestone here (or in step 4 when the issue already exists).
6. **Board the set** (`sks-project`): every card Status `Ready` on the
   family board — the board is what `sks-iterate` reads; no board, no
   loop.
7. **Close the planning loop** with the report block (`sks-summary`) and
   hand execution to `sks-iterate`.

## Pitfalls

- **Do not restate the children.** Issue shape, triage fields, board
  moves, and the loop itself are owned by their skills; a wrapper that
  re-teaches them drifts the day a child changes.
- **Ledger seeded thin.** An issue landing without command-decidable items
  defers its convergence into the loop — the expensive place to settle it.
- **Dependency order lost.** An order stated only in the plan report is
  gone next session; triage writes it onto the issues as relationships.
- **Planning an unconverged goal.** The RFC gate is cheaper than re-cutting
  the unit set after direction shifts.
- **Inventing a due date.** The milestone carries a date only when a real
  deadline exists; an empty field is honest.

## Verification

```bash
gh api repos/<org>/<repo>/milestones --jq '.[].title'   # milestone exists
gh issue list -R <org>/<repo> --json number,milestone \
  --jq '.[] | select(.milestone.title == "<goal>") | .number'
gh project item-list <board> --owner <board-owner> --limit 200 --format json \
  --jq '.items[] | select(.status == "Ready") | .content.number'
```

Done when every approved unit is an open, triaged issue on the milestone,
boarded `Ready`, dependencies sit on the issues, and the report block
names the hand-off to `sks-iterate`.

## See also

- `sks-discussion` — convergence gate before decomposition.
- `sks-issue` / `sks-issue-triage` — the artifacts this plan emits.
- `sks-milestone` — release readiness; owns due-date discipline and the
  nixpkgs-release plane.
- `sks-project` — the board the plan loads.
- `sks-iterate` — the loop that consumes the plan.
- `sks-dev` — the unit lifecycle each card runs.
- `sks-summary` — the report block that closes the planning loop.
