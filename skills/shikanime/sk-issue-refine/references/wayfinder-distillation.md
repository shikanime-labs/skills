# wayfinder → sk-issue-refine distillation

Condensed from aihero.dev/skills-wayfinder (Matt Pocock). This skill is the
problem-iteration half of that flow, re-skinned onto shikanime's issue-first
chain. Kept here so future edits don't have to re-read upstream.

## Core rule: plan, don't do

Every unit holds a question whose resolution is a **decision**, not a slice of a
build to execute. The map is finished when nothing is left to decide; then it
hands off — it does NOT carry on into code.

- A `task` ticket is the only type that _does_ rather than decides, and it earns
  its place only by **unblocking a decision**, never by delivering a piece of
  the destination.
- An agent that starts writing product code inside the map has broken the skill.

## Four decision-ticket types (→ question kinds in the parent SKILL.md)

| wayfinder type | shikanime kind | Mode   | Resolved by                                           |
| -------------- | -------------- | ------ | ----------------------------------------------------- |
| `grilling`     | `grilling`     | HITL   | Talking it through (default).                         |
| `prototype`    | `prototype`    | HITL   | A built artifact; **selection stays with the human**. |
| `research`     | `research`     | AFK    | A research subagent, fired at charting time.          |
| `task`         | `task`         | Either | Manual work that unblocks a decision.                 |

`research` is the only type that fans out (one subagent per fact, parallel).
HITL types are serial with the human.

## Documented failure modes (→ Pitfalls in parent)

- **Agent writes "this map carries execution" into its own Notes, then reads it
  back as a licence to build on a live server.** No hard in-skill stop; guard by
  keeping implementation in its own sessions.
- **Over-planning**: charting 27 tickets, later ones rest on assumptions the
  earlier ones invalidated (waterfall trap). Mitigate: scope to one bounded
  epic, not the whole product; prototype aggressively to flush uncertainty
  before implementation depends on it.
- **Parallel grilling collision**: two grilling threads get asked the same
  question in different words because they share no context. One-at-a-time is
  the safer default.
- **Prototype self-selection**: an agent builds three UI variants, picks one,
  closes the ticket. The selection is the human's; the skill must say so loudly.
- **Editing the body with findings**: the body is a stable problem statement;
  findings belong in comments. (shikanime enforces this via `sk-issue`.)
- **Fog disguised as a ticket**: "investigate X" with no precise question is not
  a question — research it first, then phrase the real one.

## "It's working if" (acceptance lens for the refine loop)

- The destination is written down before any work.
- Every open item reads as a question; anything reading "build the X" is
  mis-typed or belongs downstream.
- A session resolves one item, posts the answer as a comment, and stops.
- "Not yet specified" shrinks over time; a patch of fog that graduates into a
  ticket disappears from the fog section, not both places.
- The loop hands off toward a spec/PR, never a pull request of its own.
