---
name: sks-issue-refine
description:
  Use when iterating a problem to convergence inside its GitHub issue via
  research and comments before deriving the PR.
version: 0.1.1
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - github
      - issues
      - research
      - problem-framing
      - workflow
      - shikanime-labs
      - shikanime-studio
    related_skills:
      - sks-issue
      - sks-issue-workflow
      - sks-issue-triage
      - sks-investigate
platforms:
  - linux
  - macos
  - windows
---

# Shikanime Issue Refinement

The issue IS the problem statement. `sks-issue` opens it (body = problem
statement + `- [ ]` gate ledger + References); findings belong in comments. This
skill is the **iteration loop**: resolve an existing issue's open questions via
research + candidate solutions until the problem statement and acceptance
criteria converge (wayfinder's fog cycle on the thread).

## When to Use

- Issue exists (`sks-issue`) but the problem is still foggy.
- NOT for opening/RFC/edge — `sks-issue`/`sks-discussion`; open once it
  converges into a statable problem.
- NOT for implementation (`sks-pr`/branch phase). Refine writes comments, never
  product code.

## Model: the issue comment thread is the iteration space

- **Destination** — the converged problem statement the body should hold.
- **Fog of war** — questions you can state but not answer; research until
  precise, then resolve.
- **Frontier** — open resolvable questions; clear one at a time.
- **Four question kinds** (only `research` fans out; `grilling` is strictly
  serial with the human):

  | Kind        | Mode   | Use when                                                      | Resolved by                                                    |
  | ----------- | ------ | ------------------------------------------------------------- | -------------------------------------------------------------- |
  | `research`  | AFK    | A fact outside the working dir blocks a decision.             | A `delegate_task` agent; findings posted as a comment.         |
  | `prototype` | HITL   | "How should this look/behave" — talk can't settle it.         | A cheap artifact (linked); **selection stays with the human**. |
  | `grilling`  | HITL   | The default — settleable by talking it through.               | Precise one-at-a-time questions, _why_ attached.               |
  | `task`      | Either | No decision, but manual work (access, data shape) blocks one. | A precise checklist — never product code.                      |

## Procedure

1. **Load** — `gh issue view <N>`; read body + comments. If the problem can't
   yet be stated, route to `sks-discussion`.
2. **Enumerate the fog** — one line per open question in your in-agent
   scratchpad (never post raw).
3. **Classify** each question into one of the four kinds.
4. **Resolve AFK in parallel** — `research` fans out via `delegate_task` (one
   child per independent fact; isolate on `research/<name>` per `sks-async` if
   it touches the repo; read-only, never edits product code — see
   `references/delegate-research.md`). `grilling`/`prototype` engage the human
   serially — one question, wait, next.
5. **Post findings as comments** — each resolution is a `gh issue comment`:
   finding + candidate solution(s) + official References. These NEVER go in the
   body (body stays the stable problem statement); durable References move into
   the body via `gh issue edit`.
6. **Convergence test** — stop when: no item reads "build the X"; fog clears;
   body is a clean problem statement + decidable `- [ ]` ledger.
7. **Hand off** — route to `sks-pr`/branch phase (`sks-dev-workflow` phase 3+).
   Never carry implementation into this loop.

## Pitfalls

- Writing product code — `task` only unblocks a decision, never delivers
  a slice of the destination.
- Fog as a ticket — "investigate X" with no precise question isn't a question;
  research it, then phrase the real one.
- Parallel grilling — serial only; two threads ask the same thing in different
  words. Only `research` fans out.
- Prototype self-selection — agent builds variants and picks one → broken
  ticket; the human chooses, the agent links artifacts.
- Editing the body with findings — findings stay in comments; only durable
  References may move into the body.
- Leaking the thinking — fog drafts, classification, status chatter stay
  in-agent; the thread gets only the resolved comment.
  Interim comments deletable once converged.
- English only — no French; do not carry cpn templates in.

## Verification

```bash
gh issue view <N> --repo <org>/<repo> --json number,title,comments
```

Every open question has a resolution comment; body holds a problem statement +
References only; convergence passes before `sks-pr` handoff.

## References

- `references/wayfinder-distillation.md` — wayfinder distillation (four kinds,
  plan-don't-build, failure modes).
- `references/delegate-research.md` — `delegate_task` fan-out snippet +
  read-only/report contract.

## See also

- `sks-issue` — opens the iterated issue.
- `sks-discussion` — RFC/edge; use before problem is statable.
- `sks-pr` — solver; links back via `Related:`.
- `sks-async` — isolation for parallel `research` fan-out.
- `sks-issue-triage` — assign metadata once converged.
- `sks-investigate` — defect root-cause research; use it when the issue is a
  diagnosed bug needing its cause, not a foggy problem needing framing.
