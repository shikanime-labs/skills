---
name: sks-issue-workflow
description:
  "Use when you need the single entry point for the issue side:
  create, refine, and triage the issue before any PR."
version: 0.2.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - github
      - issues
      - workflow
    related_skills:
      - sks-issue
      - sks-issue-refine
      - sks-issue-triage
platforms:
  - linux
  - macos
  - windows
---

# Issue Workflow

Thin orchestrator over `sks-issue` → `sks-issue-refine` → `sks-issue-triage`.
When operating in cloud-pi-native/console, read
`references/cloud-pi-native.md` for the org overrides of each step.

## When to Use

- "Open and set up an issue on <repo>".
- "Take this problem through to a triaged issue".
- "Run the issue side: create an issue and triage it."
- "Derive the PR" — after refinement converges on a statable problem.
- "Set up the full issue workflow before implementation."

## Procedure

1. **Create** — Load `sks-issue`. Body = problem statement + `- [ ]` gate ledger
   (command-decidable acceptance criteria); findings go in comments, not the
   body. Result: issue `#N`.
2. **Refine** — Load `sks-issue-refine`; iterate the problem _inside the issue_
   until acceptance criteria converge. Update the body's tasklist only when
   criteria change. Skip only if already converged at creation (rare).
3. **Triage** — Load `sks-issue-triage`; apply labels, assignee, milestone,
   project now. Only empty/determinable fields — **never invent a label the repo
   lacks**. Then set the card's board Status to `Ready` (`sks-project`);
   `Backlog` only with a parked rationale.

## Verification

Complete when body is a stable problem statement with a converged `- [ ]` ledger
and triage metadata is set. Triage set = labels non-empty, assignee present,
a project card with Status set and custom Fields populated where the board
has them (Priority/Size etc. — `gh project item-list` shows them; `item-edit`
to fix) — verify, don't assume. Verify:

```bash
gh issue view <N> --repo <org>/<repo> \
  --json number,title,labels,assignees,milestone,projectItems
```

## Gate

```bash
gh issue view <N> --repo <org>/<repo> \
  --json number,title,labels,assignees,milestone,projectItems \
  # body + ledger + triage set
```

Gate fails if `labels` is empty, `assignees` is `[]`, or the board card is
missing or its Fields unset — the authoritative check is
`gh project item-list <board> --owner <owner> --format json` filtered to the
issue number (shows Status + custom Fields). `milestone` may be null when
the repo genuinely lacks a value — but null must be a seen decision, not an
unread field.

## See also

- `sks-issue` — create step.
- `sks-issue-refine` — in-issue convergence loop.
- `sks-issue-triage` — metadata step run immediately after creation.
