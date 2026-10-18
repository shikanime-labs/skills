---
name: sks-iterate
description:
  "Use when running a board-driven work loop across cards: pull the next card,
  apply the coordination ladder per card, stop on empty column, BLOCKED
  parking, or budget exhaustion."
version: 0.1.0
author: Automata
license: Apache-2.0
metadata:
  hermes:
    tags:
      - workflow
      - loop
      - board
    related_skills:
      - sks-project
      - sks-delegate
      - sks-async
      - sks-investigate
      - sks-dev
      - sks-release
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
   `sks-delegate`; independent cards run together → `sks-async`.
3. **Run.** The unit itself is `sks-dev`'s lifecycle, end to end — this
   skill never re-derives it. Milestone-scoped units: `sks-milestone`.
4. **Close the iteration.** One status block per iteration: card taken,
   unit outcome, evidence links (PR, issue). Park BLOCKED cards with the
   rationale on the card, not in prose.
5. **Stop or repeat.** Stop when a stop condition fires (below). Otherwise
   pull again.

## Stop conditions

Exactly three — any one ends the loop:

- **Rightmost active column empty.** The board holds no more actionable
  cards.
- **BLOCKED card parked with rationale.** The next card is blocked; park it
  (`sks-project`) with the blocker on the card and stop.
- **Iteration budget exhausted.** The user-set card count (or time budget)
  is spent; report where the loop stands.

## Milestone end

When the loop empties a release milestone's board: close its milestone
(`sks-milestone`) and hand the release cut to `sks-release` — RC first when
main is ahead but validation is unproven. The loop does not cut releases
itself.

## Pitfalls

- **Do not re-derive the lifecycle.** The phase table lives in `sks-dev`;
  restating it here is the wrapper-skill defect the fold precedent rejects.
- **A blocked card is parked, never skipped silently.** Skipping loses the
  blocker; parking records it where the next session finds it.
- **One status block per iteration, not per phase** — mid-loop chatter is
  noise; the block closes the iteration.

## Verification

```bash
# per iteration: the card moved and the evidence exists
gh issue view <N> -R <org>/<repo> --json state,comments -q '.state'
gh pr view <PR> -R <org>/<repo> --json state,url -q '"\(.state) \(.url)"'
```

Done when: every pulled card is landed, parked BLOCKED with rationale, or
the budget expired with the standing report stating which.

## See also

- `sks-project` — the board this loop reads.
- `sks-dev` — the unit lifecycle each card runs.
- `sks-delegate` / `sks-async` — the ladder rungs.
- `sks-investigate` — defect routing before the ladder.
- `sks-milestone` / `sks-release` — milestone close and the release cut at
  milestone end.
