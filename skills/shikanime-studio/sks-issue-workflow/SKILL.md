---
name: sks-issue-workflow
description:
  "Use when you need the single entry point for the shikanime issue side:
  create, refine, and triage the issue before any PR."
version: 0.1.1
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - github
      - issues
      - shikanime-labs
      - shikanime-studio
      - workflow
    related_skills:
      - sks-issue
      - sks-issue-refine
      - sks-issue-triage
platforms:
  - linux
  - macos
---

# Shikanime Org Issue Workflow

Thin orchestrator over `sks-issue` → `sks-issue-refine` → `sks-issue-triage`.

## When to Use

- "Open and set up an issue on <repo>".
- "Take this problem through to a triaged issue".

## Procedure

1. **Create** — Load `sks-issue`. Body = problem statement + `- [ ]` gate ledger
   (command-decidable acceptance criteria); findings go in comments, not the
   body. Result: issue `#N`.
2. **Refine** — Load `sks-issue-refine`; iterate the problem _inside the issue_
   until acceptance criteria converge. Update the body's tasklist only when
   criteria change. Skip only if already converged at creation (rare).
3. **Triage** — Load `sks-issue-triage`; apply labels, assignee, milestone,
   project now. Only empty/determinable fields — **never invent a label the repo
   lacks**.

## Gate

Complete when body is a stable problem statement with a converged `- [ ]` ledger
and triage metadata is set. Verify:

```bash
gh issue view <N> --repo <org>/<repo> --json number,title,labels
```

## See also

- `sks-issue` — create step.
- `sks-issue-refine` — in-issue convergence loop.
- `sks-issue-triage` — metadata step run immediately after creation.
