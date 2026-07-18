# Development Workflow

The strict development workflow this repo encodes, as one skill: `dev-workflow`.
Every feature is drafted as a GitHub issue to validate the task _before_ it is
built; `docs/agents/` holds the durable substrate so maintainers, humans, and
other agents share one map.

Two forces run through the whole pipeline:

- **The pipeline** (Matt Pocock's engineering skills): idea → spec → tickets →
  triage → implement → review. Nothing is built until it exists as a validated
  issue on the tracker.
- **The ladder** (Ponytail): an always-on laziness guard on every coding step —
  write only what the task needs, never cut validation/security/accessibility.

All phases live in `skills/dev-workflow/SKILL.md` as numbered sections you jump
between.

## The main flow: idea → ship

1. **Sharpen the idea.** Discuss it against the codebase. Sharpen terminology
   into `CONTEXT.md`, record decisions as ADRs (`docs/agents/domain.md`).
2. **§ Spec** — turn the conversation into a spec (Problem / Solution / User
   Stories / Implementation Decisions) and **publish it as a GitHub issue**
   labelled `ready-for-agent`. This is the validation gate: no spec issue, no
   build.
3. **§ Tickets** — break the spec into tracer-bullet tickets (vertical slices,
   each demoable, each sized for one context window), published as sub-issues
   with blocking edges.
4. **§ Triage** — move issues through the state machine
   (`needs-triage → needs-info → ready-for-agent → ready-for-human → wontfix`).
5. **§ Implement** — build a `ready-for-agent` ticket. Drive test-driven
   development at pre-agreed seams, stay on the Ponytail ladder throughout,
   close with § Review before committing.
6. **§ Review** — two-axis review (Standards + Spec) of the diff against a fixed
   point, in parallel sub-agents. The over-engineering pass is a focused
   sub-mode of the Standards axis.

For a single-session change, skip 3 and go spec → implement in one context.

## Always-on: the Ponytail ladder

On **any** coding step, stop at the first rung that holds:

1. Does this need to exist? (YAGNI) → no: skip it
2. Already in this codebase? → reuse it
3. Stdlib does it? → use it
4. Native platform feature? → use it
5. Installed dependency? → use it
6. One line? → one line
7. Only then: the minimum that works

Lazy about the solution, never about reading the code first. Never cut
trust-boundary validation, data-loss handling, security, or accessibility. §
Debt tracks the deferrals marked with `ponytail:` comments.

## Setup

Run **§ Setup** once per repo before first use. It discovers the git remote,
existing labels, and docs layout, confirms with you, and writes
`docs/agents/{issue-tracker,domain,workflow}.md`. The pipeline reads those files
instead of guessing.

## The substrate

- `docs/agents/issue-tracker.md` — where work lives, auth, label vocabulary, how
  to create issues and blocking edges.
- `docs/agents/domain.md` — glossary + ADR layout and consumer rules.
- `docs/agents/workflow.md` — this file.
