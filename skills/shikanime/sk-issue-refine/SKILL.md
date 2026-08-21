---
name: sk-issue-refine
description:
  "Iterate a problem to convergence inside its GitHub issue via research +
  comments. Extracted from sk-issue's comment-iteration convention and
  wayfinder's research/fog loop."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      [
        GitHub,
        Issues,
        research,
        problem-framing,
        shikanime-labs,
        shikanime-studio,
      ]
---

# Shikanime Issue Refinement

The issue IS the problem statement. `sk-issue` opens it (body = problem
statement + `- [ ]` gate ledger + References) and states that findings belong in
comments. This skill is the **iteration loop extracted from that convention** —
working _inside_ an existing issue to resolve its open questions through
research and candidate solutions posted as comments, until the problem statement
and acceptance criteria converge and are ready to be solved. Distills
wayfinder's research/grilling/fog-of-war cycle onto the issue's comment thread.

## When to Use

- An issue already exists (`sk-issue`) but its problem is still foggy: open
  questions, missing evidence, several candidate approaches untested.
- "Research this before we build", "what are our options for <X>", "iterate on
  issue #N".
- NOT for opening the issue — that is `sk-issue`. NOT for RFC / open questions /
  edge exploration — that is `sk-discussion`; once a discussion converges into a
  statable problem, open the issue (`sk-issue`) and iterate within it here.
- NOT for implementation — that is `sk-pr` / the branch phase. Refine writes
  comments, never product code.

## Model: the issue comment thread is the iteration space

- **Destination** — the converged problem statement the issue body should hold.
  Named when the issue is opened; refine measures every question against it.
- **Fog of war** — open questions about the problem you can _state_ but not yet
  _answer_. The test: can you phrase the question precisely now? Then resolve
  it. If you only feel uncertainty, research it until it sharpens.
- **Frontier** — the open, resolvable questions. Resolve one at a time; each
  resolution clears fog ahead and graduates whatever is now specifiable.
- **Four question kinds** (only `research` fans out; `grilling` is strictly
  serial with the human):

  | Kind        | Mode   | Use when                                                                                 | Resolved by                                                                   |
  | ----------- | ------ | ---------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
  | `research`  | AFK    | A fact _outside_ the working dir blocks a decision (docs, API behavior, upstream state). | A `delegate_task` research agent; findings posted as a comment.               |
  | `prototype` | HITL   | "How should this look/behave" — talking cannot settle it.                                | A cheap artifact (linked from a comment); **selection stays with the human**. |
  | `grilling`  | HITL   | The default — settleable by talking it through.                                          | Precise one-at-a-time questions, _why_ attached.                              |
  | `task`      | Either | No decision, but manual work (access, data shape) blocks one.                            | A precise checklist — never product code.                                     |

## Procedure

1. **Load the issue** — `gh issue view <N>`; read the body (problem statement +
   ledger) and existing comments. If the problem cannot yet be stated, stop and
   route to `sk-discussion` instead.
2. **Enumerate the fog** — list every open question as a one-line comment on the
   issue. Each must read as a _question_, never "build the X".
3. **Classify** each question into one of the four kinds.
4. **Resolve AFK work in parallel** — for `research` items, fan out via
   `delegate_task` (one child per independent fact; isolate on a
   `research/<name>` branch per `sk-async` if it touches the repo). Research
   ONLY reads and reports; it never edits product code. For `grilling`/
   `prototype`, engage the human serially — one question, wait, then next.
5. **Post findings as comments** — each resolution goes in a `gh issue comment`:
   the finding, the candidate solution(s), and any official References (docs,
   linked issues/PRs, commits, specs). Candidate solutions and references NEVER
   go in the body (body stays a stable problem statement per `sk-issue`); if a
   reference is durable, add it to the body's **References** section via
   `gh issue edit`.
6. **Convergence test** — stop iterating when:
   - No open item reads "build the X" (those belong downstream of the issue).
   - The fog clears: remaining items are all answerable.
   - The body is a clean problem statement + decidable `- [ ]` ledger.
7. **Hand off to the solver** — the issue is now ready to be solved: route to
   `sk-pr` / the branch-implement phase (`sk-dev-workflow` phase 3+). Never
   carry implementation into this loop.

## Pitfalls

- **Writing product code in the issue** — the most-reported failure. `task`
  earns its place only by _unblocking_ a decision, never by delivering a slice
  of the destination. Builds stay in their own sessions.
- **Fog disguised as a ticket** — "we should investigate X" with no precise
  question is not a question; research it first, then phrase the real one.
- **Parallel grilling** — two grilling threads get asked the same question in
  different words (no shared context). Grilling is serial; only `research` fans
  out.
- **Prototype self-selection** — an agent building three UI variants and picking
  one has broken the ticket. The human chooses; the agent links artifacts.
- **Editing the body with findings** — findings belong in comments; the body is
  the stable problem statement. Only the durable References section may move
  into the body.
- **English only** — no French; do not carry cpn templates in.

## Verification

```bash
gh issue view <N> --repo <org>/<repo> --json number,title,comments
```

Every open question has a resolution comment; the body carries a problem
statement + References only (no candidate solutions inline); the convergence
test passes before handoff to `sk-pr`.

## References

- `references/wayfinder-distillation.md` — condensed wayfinder source (four
  question kinds, plan-don't-build discipline, documented failure modes) this
  skill is distilled from.

## See also

- `sk-issue` — opens the issue this skill iterates within (problem statement +
  gate ledger + References; findings as comments).
- `sk-discussion` — RFC / open-question / edge-exploration surface; use it
  before the problem can be stated, then open the issue this skill iterates.
- `sk-pr` — the solver; links back via `Related:` without auto-close.
- `sk-async` — isolation model for parallel `research` fan-out.
- `sk-issue-triage` — assign metadata (labels, assignee, milestone, project)
  once converged.
