---
name: to-tickets
description:
  "Break a spec, plan, or conversation into tracer-bullet tickets, each
  declaring its blocking edges, published as GitHub sub-issues."
version: 1.0.0
author: Operator 21O (derived from MIT-licensed engineering workflow references)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [workflow, tickets, issues, planning, decomposition]
    related_skills: [to-spec, triage, implement, ask]
---

<!-- markdownlint-disable MD013 MD033 -->

# To Tickets

Break a plan, spec, or the current conversation into a set of **tickets** —
tracer-bullet vertical slices, each declaring the tickets that **block** it —
and publish them to the tracker.

The tracker and label vocabulary come from `docs/agents/issue-tracker.md`; run
`bootstrap` if missing. Titles and bodies use the glossary in
`docs/agents/domain.md`.

## Process

### 1. Gather context

Work from the conversation. If the user passes a reference (spec path, issue
number/URL), fetch its full body and comments. If a **meta issue** already
exists for this work (the strategic spec/PRD), fetch it — the tactical tickets
you create will set their parent to it.

### 2. Explore the codebase (optional)

If not already done, explore to understand current state. Look for
**prefactoring** opportunities: "make the change easy, then make the easy
change."

### 3. Draft vertical slices

<vertical-slice-rules>

- Each slice cuts a narrow but COMPLETE path through every layer (schema, API,
  UI, tests) — vertical, NOT a horizontal slice of one layer.
- A completed slice is demoable or verifiable on its own.
- Each slice fits in a single fresh context window.
- Each slice stays on the minimalism ladder (`docs/agents/workflow.md`): no
  speculative abstractions, no scaffolding "for later", the minimum seam that
  proves the path.

</vertical-slice-rules>

Give each ticket its **blocking edges** — the tickets that must complete before
it can start. A ticket with no blockers can start immediately.

**Wide refactors are the exception.** A mechanical change whose blast radius
fans across the whole codebase can't be a single tracer bullet. Sequence it
**expand–contract**: first expand (add the new form beside the old so nothing
breaks), then migrate call sites in batches sized by blast radius (per package /
directory), each batch a ticket blocked by the expand, keeping CI green; a final
contract ticket removes the old form once all batches land.

### 4. Publish

Create one issue per ticket via the GitHub MCP (`GitHub_issue_write`,
`GitHub_sub_issue_write`) or `gh`. Model blocking edges as native sub-issues, or
a `Blocked by: #N` line in the body. **If a meta issue exists for this work, set
each ticket's parent to it** (`gh issue create ... --parent <meta>`) so the
tactical tickets roll up under the strategic epic. Apply the `ready-for-agent`
label to tickets with no unresolved blockers. Hand back the ticket URLs and the
blocking graph.

### 5. Hand off to delivery

Each ticket becomes one branch and one PR; the blocking graph is the stack order
(a PR's base is the branch of the ticket that blocks it). Note the issue number
and branch name per ticket so `implement` opens an atomic PR that links it.

## Boundaries

Produces tickets and their edges. Does not implement them (that's `implement`).
