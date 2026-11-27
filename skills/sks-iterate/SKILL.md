---
name: sks-iterate
description:
  "Use when running a board-driven work loop: pull the next card, apply the
  coordination ladder, and stop only when done or blocked, or to raise a
  question or a finding that may derive work."
version: 0.2.0
author: Automata
license: Apache-2.0
metadata:
  hermes:
    tags:
      - workflow
      - loop
      - board
    related_skills:
      - sks-plan
      - sks-project
      - sks-delegate
      - sks-async
      - sks-investigate
      - sks-dev
      - sks-release
      - sks-context
platforms:
  - linux
  - macos
  - windows
---

# Iterate

Board-driven work loop: read the board (`sks-project`), pull the next card,
run it through the coordination ladder, close the iteration with a status
block, repeat. `sks-iterate` owns only what no existing skill owns — the
loop, its stop conditions, and the per-card ladder application. The unit
lifecycle is `sks-dev`'s; the board is `sks-project`'s; neither is restated
here.

Entry gate: `sks-plan` ran to done — the loop consumes a planned, boarded
milestone. An empty board or an unplanned backlog routes back to `sks-plan`,
never into improvised card pulls. An approved plan whose issue, triage fields
and board card were never materialized is NOT done: apply those writes before
the first pull. Pulling an unboarded card turns a planning decision into an
improvised card.

## Plan lookup

Before working an item, read the `sks-plan` that produced it and use its unit
table and dates. The plan owns Start date and Target date; never replace them
with a guess. If no plan exists, say so and route the item back to `sks-plan`
before proceeding.

## Invoked with no target while a card is in flight

`/sks-iterate` with no argument names no card. When the session already holds
an in-flight unit, do not pull a fresh one and do not invent one: name the
card that is open, read the board to confirm it is the rightmost active one,
and continue it. Read the board before continuing — an in-flight card whose
column another session moved is no longer the pull. Report the card id in the
status block so the loop is visibly bound to the board, not to the chat.

## A bare number is an unresolved reference

"continue N" / "land N" / "what about N" names a number, not a repo or a
type. Resolve it across the whole candidate space before reporting anything:

```bash
gh api repos/<o>/<r>/issues/<N> --jq '{title,state,pull_request}'
gh pr list --repo <o>/<r> --state all --search '<N> in:title,body'
git ls-remote --heads https://github.com/<o>/<r>.git | grep <N>   # branch names
```

- `gh pr view <N>` 404s on an issue, and `gh issue view <N>` on a PR — the
  per-type commands hide half the space. The unified `issues/<N>` endpoint
  returns both (`pull_request` is non-null for a PR).
- Numbers are per-repo and collide across them: the same number is a merged
  PR in one repo, an open epic in another, and a closed request in a third.
  Enumerate every org repo the user works in, under every `gh` identity in
  use, before concluding a number does not resolve.
- An epic is a parent issue with sub-issues; its real work is the children
  and their linked PRs. Read the sub-issue tree and each child's linked PRs —
  the in-flight unit is usually a child's open PR, not the parent.
- Name the resolved target back to the user before acting on it: repo,
  number, type, title, state. A wrong-repo resolution costs a full round
  trip, and the user's correction is the only signal it was wrong.

## When to Use

- "Keep working the board" / "take the next cards" — run the loop.
- One card is done and the session should continue to the next.
- Not for a single unit — that is `sks-dev` straight, no loop.

## The loop

1. **Pull.** Read the board (`sks-project`). Take the next card from the
   rightmost active column — the board is the tactical plan; this skill
   never picks work another way.
2. **Route.** Defect cards go through `sks-investigate` first (root cause +
   proposal in issue comments settles the ledger; the investigation emits
   its own summary block). Every card then takes the ladder: one card →
   `sks-delegate`; independent cards run together → `sks-async`. The gate
   is on the ISSUE, not in private state: a card routes to the ladder only
   after its acceptance ledger is settled in the issue's comments. A defect
   card also needs its root cause and fix decision there. A defect PR opened
   ahead of that record inverts the order (`sks-issue-refine` settles the
   ledger, then `sks-dev`).
3. **Run.** The unit itself is `sks-dev`'s lifecycle, end to end — this
   skill never re-derives it. Milestone-scoped units: `sks-milestone`.
4. **Close the iteration.** One status block per iteration: card taken,
   unit outcome, evidence links (PR, issue). Park BLOCKED cards with the
   rationale on the card, not in prose.
5. **Stop or repeat.** Stop when a stop condition fires (below). Otherwise
   pull again without asking for permission.

## Stop conditions

Three conditions end the loop — any one of them:

- **Rightmost active column empty.** The board holds no more actionable
  cards.
- **BLOCKED card parked with rationale.** The next card is blocked; park it
  (`sks-project`) with the blocker on the card and stop.
- **Iteration budget exhausted.** The user-set card count (or time budget)
  is spent; report where the loop stands.

Two conditions suspend the loop instead of ending it. Each stops the loop to
ask, with the evidence gathered so far and the card it holds:

- **A decision only the user can make.** Ask it as one question.
- **A finding that may derive work beyond its card.** A review finding or an
  investigation that exposes a defect in a sibling skill, card or plan is
  neither absorbed into the current unit nor filed unasked: report the
  finding, its evidence and the work it may derive, then ask whether to
  derive it. A steer the user asked for is not a finding: it is already
  decided.

Do not stop for anything a read of the board, the plan, or the issue ledger
can settle: resolve it and continue. A check-in that needs no answer is not
a stop condition.

## Stacked work mid-loop

A follow-up that depends on a card already in flight is a new unit on a
stacked branch, not an addition to the open PR: branch from the approved
commit and open a stacked PR (`sks-dev`). The loop does not wait for the
parent to merge before starting it. It continues down the board, and lands
the stack top first when every link passes its gates (`sks-land`).

## Milestone end

When the loop empties a release milestone's board: close its milestone
(`sks-milestone`) and hand the release cut to `sks-release` — RC first when
main is ahead but validation is unproven. The loop does not cut releases
itself.

## Pitfalls

- **Re-read the plan's writes before applying them.** A plan whose boarding,
  triage fields and dependency edges were already landed is a no-op: verify
  with targeted reads, report it as already applied, and start the loop
  instead of replaying mutations. Replaying a plan into an already-boarded
  set duplicates writes and can trigger the project board's bulk-mutation gate.
- **Do not re-derive the lifecycle.** The phase table lives in `sks-dev`;
  restating it here is the wrapper-skill defect the fold precedent rejects.
- **A parent card whose open criteria already live as sub-issues is an
  investigation-only iteration.** Record the split in its comments, reset its
  Status to the phase its ledger supports, then pull the children — opening
  work on the parent duplicates planned units and strands the children.
- **A blocked card is parked, never skipped silently.** Skipping loses the
  blocker; parking records it where the next session finds it. When the board
  has no BLOCKED column, post the blocker as an issue comment with the failing
  command and its output, keep the card in its current phase, and stop — never
  mint a new option on someone else's board.
- **A mid-loop steer that changes the product is a new unit.** File it,
  develop it on a stacked branch, and keep any already-approved PR head
  pinned; appending a new feature to an approved PR silently revokes the
  approval. The status block then names the new card.
- **A stop that is really a question wastes the round trip.** Ask once,
  with the evidence and the card it holds, then wait. Do not re-ask, and
  do not keep working past an unanswered question that gates the next card.
- **One status block per iteration, not per phase** — mid-loop chatter is
  noise; the block closes the iteration.

## Verification

```bash
# per iteration: the card moved and the evidence exists
gh issue view <N> -R <org>/<repo> --json state,comments -q '.state'
gh pr view <PR> -R <org>/<repo> --json state,url -q '"\(.state) \(.url)"'
```

Done when: every pulled card is landed, parked BLOCKED with rationale,
carried as a stacked unit, or the budget expired with the standing report
stating which.

## See also

- `sks-project` — the board this loop reads.
- `sks-plan` — the strategy plane upstream of this loop; an empty board
  with an unconverged backlog routes back there.
- `sks-dev` — the unit lifecycle each card runs, and the owner of the
  stacked-branch rule.
- `sks-land` — landing a stack, top link first.
- `sks-delegate` / `sks-async` — the ladder rungs.
- `sks-investigate` — defect routing before the ladder.
- `sks-milestone` / `sks-release` — milestone close and the release cut at
  milestone end.
